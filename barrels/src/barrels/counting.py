"""Counting what was physically shot, and counting a misplaced box once (2026-11-26, TODO M1).

Two things the one table (``report.py``) got wrong, and nothing else. The v2 rule of ``docs/EVAL.md`` is untouched:
it is kept, reported beside the new counts, and called **strict** here.

1. **Placements, not lamp settings.** One arrangement of barrels shot under five lamp settings used to count as
   five times as many barrels. Three words, all read off the frame name and ``data/conditions.json``:

   - a *place* is a table in a room (``conditions.info(...).place``);
   - an *arrangement* is one scene at one place: the frames ``{scene}_{nn}`` of that place, one per light;
   - a *placement* is one barrel in one arrangement. It is the same physical barrel in every light.

   A placement counts once. Shot under several lights, it counts the **share of its lights in which it is found**
   (found under 3 of 5 lights = 0.6). ``Tally.found_w`` is the sum of those shares; ``Tally.placements`` is what
   it is out of. Boxes that are not on their barrel are weighted the same way (a tin boxed under each of five
   lights is one tin): each such box counts 1 / (the lights of its arrangement).

2. **A misplaced box counts once.** Under the strict rule a box that sits on a real barrel of the right color but
   fails the rule (usually its bottom edge) is charged twice: the barrel is a miss and the box is a false box. The
   second accounting (``classify_frame``) gives every true barrel one of three states and every box one of five:

   - barrel: ``found`` (a strict hit) / ``off`` (found, box off: a same-color box is on it but fails strict) /
     ``missed``;
   - box: ``found`` or ``off`` (it is the one box on its barrel) / ``wrong_color`` (on a barrel of the other
     color) / ``second`` (on a barrel of its color that already has a box) / ``nothing``.

   **On a barrel** has one definition (``is_on``): at least half of the smaller of the two boxes lies inside the
   other. A box drawn around the visible half of a hidden barrel is on it; so is a box a little too big, or one
   whose bottom edge is 10 px off; a box beside the barrel is not. Every pair that passes the overlap clause of the
   strict rule (IoU >= 0.5) passes this test, so the states are nested: strict hit, then on the barrel, then not.

   The strict hits are taken first and are exactly ``eval_det.evaluate_frame(rule="v2")``'s, so ``found`` here is
   the strict count, always. Boxes on empty frames are ``nothing`` and are also counted on their own
   (``Tally.empty``; on *clean* empty frames ``Tally.clean_empty``).

In the order the data flows: ``classify_frame`` (one frame's boxes against its labels -> a ``FrameCount``);
``build_placements`` (which label box is which placement, from the labels of all lights of an arrangement);
``tally`` (frames -> one ``Tally``: raw counts and placement-weighted counts); ``group_stems`` (frames by condition
or by place); ``format_table`` (the rows as text or markdown). Nothing here opens an image.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from . import conditions as cond
from . import eval_det as ed
from .io import parse_name

FOUND, OFF, MISSED = "found", "off", "missed"                    # a true barrel's state
WRONG, SECOND, NOTHING = "wrong_color", "second", "nothing"      # a box that is not the one box on its barrel
GT_STATES = (FOUND, OFF, MISSED)
BOX_STATES = (FOUND, OFF, WRONG, SECOND, NOTHING)
EXTRA_STATES = (WRONG, SECOND, NOTHING)
ON_SHARE = 0.5              # "on a barrel": this share of the smaller box lies inside the other
_CODE = {FOUND: "F", OFF: "O", MISSED: "M", WRONG: "W", SECOND: "S", NOTHING: "N"}
_STATE = {v: k for k, v in _CODE.items()}


# ---------------------------------------------------------------- 1. one frame: a misplaced box counts once

def on_share(a: tuple, b: tuple) -> float:
    """The share of the smaller of two boxes that lies inside the other: intersection area / the smaller area."""
    ax0, ay0, ax1, ay1 = a; bx0, by0, bx1, by1 = b
    iw = max(0, min(ax1, bx1) - max(ax0, bx0)); ih = max(0, min(ay1, by1) - max(ay0, by0))
    small = min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0))
    return iw * ih / small if small > 0 else 0.0


def is_on(p, g) -> bool:
    """A box is on a barrel when at least half (``ON_SHARE``) of the smaller of the two boxes lies inside the other.
    Color is not looked at here."""
    return on_share(p.bbox, g.bbox) >= ON_SHARE


@dataclass(frozen=True)
class FrameCount:
    """One frame under the second accounting: a state per true barrel (label order) and a state per box (the
    detector's order). ``assumed``: nothing was measured, the states are an assumption (the vendor on a white table)."""
    stem: str
    gt: tuple[str, ...]
    boxes: tuple[str, ...]
    clean: bool = True              # the label's flag; matters on an empty frame only
    assumed: bool = False

    @property
    def negative(self) -> bool:
        return not self.gt

    def n_gt(self, state: str) -> int:
        return sum(1 for s in self.gt if s == state)

    def n_box(self, *states: str) -> int:
        return sum(1 for s in self.boxes if s in states)

    @property
    def extra(self) -> int:
        """Boxes that are not the one box on their barrel: wrong color, a second box, on nothing."""
        return self.n_box(*EXTRA_STATES)

    def to_dict(self) -> dict:
        """Compact: one letter per barrel and per box (F found, O off, M missed, W wrong color, S second, N nothing)."""
        d = {"stem": self.stem, "gt": "".join(_CODE[s] for s in self.gt), "boxes": "".join(_CODE[s] for s in self.boxes), "clean": self.clean}
        if self.assumed:
            d["assumed"] = True
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FrameCount":
        try:
            return cls(d["stem"], tuple(_STATE[c] for c in d["gt"]), tuple(_STATE[c] for c in d["boxes"]), bool(d.get("clean", True)),
                       bool(d.get("assumed", False)))
        except (KeyError, TypeError) as e:
            raise ValueError(f"bad frame count {d!r}: {e}") from None


def classify_frame(stem: str, preds: list, gts: list, clean: bool = True, on=is_on) -> FrameCount:
    """One frame's boxes against its true barrels -> a state for each. (``on``: the test for "this box is on this
    barrel"; ``is_on`` everywhere, another one only to show how much the counts depend on it.)

    1. The strict hits, exactly as the v2 rule takes them (same color, IoU >= 0.5, bottom edge within tolerance,
       highest IoU first): barrel ``found``, box ``found``.
    2. Among what is left: a box of the same color that is on the barrel (``is_on``), highest IoU first, each barrel
       and each box once: barrel ``off`` (found, box off), box ``off``.
    3. Every box still left: if it is on some barrel, the one it overlaps most decides: the box's own color ->
       ``second`` (that barrel has its box already), the other color -> ``wrong_color``. On no barrel -> ``nothing``.
    Barrels still left are ``missed``."""
    def iou(p, g) -> float:
        return ed.box_iou(p.bbox, g.bbox)
    gt = [MISSED] * len(gts)
    box: list[str | None] = [None] * len(preds)
    for pi, gi, _ in ed.match_best_first(preds, gts, iou, ed.IOU_THR, same_class=True, eligible=ed.bottom_within_tol):
        gt[gi], box[pi] = FOUND, FOUND
    rest_p = [i for i, s in enumerate(box) if s is None]
    rest_g = [i for i, s in enumerate(gt) if s == MISSED]
    for a, b, _ in ed.match_best_first([preds[i] for i in rest_p], [gts[i] for i in rest_g], iou, 0.0, same_class=True, eligible=on):
        gt[rest_g[b]], box[rest_p[a]] = OFF, OFF
    for i, p in enumerate(preds):
        if box[i] is not None:
            continue
        sits = [(iou(p, g), g.color == p.color, -gi) for gi, g in enumerate(gts) if on(p, g)]
        box[i] = NOTHING if not sits else (SECOND if max(sits)[1] else WRONG)
    return FrameCount(stem, tuple(gt), tuple(box), bool(clean))


def assumed_perfect(stem: str, n_barrels: int, clean: bool = True) -> FrameCount:
    """The frame as it counts when an arm is ASSUMED to find every barrel and to draw nothing else (the vendor on a
    white table under window or overhead light, Tanush 2026-11-26). Marked ``assumed``; never a measurement."""
    return FrameCount(stem, (FOUND,) * n_barrels, (FOUND,) * n_barrels, bool(clean), assumed=True)


# ---------------------------------------------------------------- 2. which barrel is which placement

def condition_of(stem: str) -> str:
    """``{light}_{surface}`` of a frame name: the condition (one table under one light)."""
    t = parse_name(stem)
    return f"{t['light']}_{t['surface']}"


def place_of(stem: str, table: dict | None = None) -> str:
    """The place (table and room) a frame was shot at, from ``data/conditions.json``."""
    return cond.info(condition_of(stem), table).place


def arrangement_of(stem: str, table: dict | None = None) -> tuple[str, str, str, str]:
    """(robot, place, scene, nn): one scene at one place. The frames of one arrangement differ only in the light."""
    t = parse_name(stem)
    return (t["robot"], place_of(stem, table), t["scene"], t["nn"])


class ArrangementMismatch(ValueError):
    """Two frames that are one arrangement under two lights do not hold the same barrels."""


@dataclass
class Placements:
    """Which label box is which physical barrel. ``key[(stem, i)]`` = the placement of true barrel ``i`` of ``stem``:
    its arrangement plus a number inside it; the same key in every light of the arrangement."""
    key: dict[tuple[str, int], tuple] = field(default_factory=dict)
    arrangement: dict[str, tuple] = field(default_factory=dict)         # stem -> arrangement

    def count(self, stems) -> tuple[int, int]:
        """(placements, arrangements) among these frames."""
        stems = set(stems)
        return len({k for (s, _), k in self.key.items() if s in stems}), len({self.arrangement[s] for s in stems})


def build_placements(gts: dict[str, list], table: dict | None = None) -> Placements:
    """``gts``: stem -> the true barrels of that frame (``detect_types.barrels_from_boxes``).

    The frames are grouped by arrangement. The barrels of the first frame (by name) of an arrangement are numbered as
    they come; in every other light each barrel takes the number of the barrel of the same color it overlaps most
    in that first frame (the boxes of one arrangement are copies of each other, so the overlap is near 1). Raises
    ``ArrangementMismatch`` when two lights of one arrangement do not hold the same barrels: then either a label is
    wrong or the two frames are not one arrangement, and no count that leans on them would be right."""
    out = Placements()
    groups: dict[tuple, list[str]] = {}
    for s in sorted(gts):
        out.arrangement[s] = arrangement_of(s, table)
        groups.setdefault(out.arrangement[s], []).append(s)
    for arr, stems in groups.items():
        ref = stems[0]
        for i in range(len(gts[ref])):
            out.key[(ref, i)] = arr + (i,)
        for s in stems[1:]:
            pairs = ed.match_best_first(gts[s], gts[ref], lambda p, g: ed.box_iou(p.bbox, g.bbox), ed.IOU_THR, same_class=True)
            if len(gts[s]) != len(gts[ref]) or len(pairs) != len(gts[ref]):
                raise ArrangementMismatch(f"{s} and {ref} are one arrangement under two lights but do not hold the same barrels "
                                          f"({len(gts[s])} and {len(gts[ref])} boxes, {len(pairs)} of them in the same place with the same color): "
                                          f"fix the labels (tools/copy_boxes.py), or give one of the two frames another scene number")
            for si, ri, _ in pairs:
                out.key[(s, si)] = arr + (ri,)
    return out


def load_gts(stems, labels_dir=None) -> tuple[dict[str, list], dict[str, bool]]:
    """(stem -> true barrels, stem -> the label's ``clean`` flag) from the box labels. Opens label files only."""
    from . import detect_types as dtp, io
    gts, clean = {}, {}
    for s in stems:
        label = io.load_boxes(s, labels_dir, check_image=False)
        gts[s] = dtp.barrels_from_boxes(label)
        clean[s] = bool(label.get("clean", True))
    return gts, clean


# ---------------------------------------------------------------- 3. frames -> one tally

@dataclass
class Tally:
    """The counts of one arm over a group of frames. ``_w`` = each placement (or arrangement) once."""
    frames: int = 0
    conditions: int = 0             # lights: how many conditions the frames come from
    places: int = 0
    arrangements: int = 0
    placements: int = 0             # physical barrels: what found_w / off_w are out of
    barrels: int = 0                # label boxes: what found / off / missed are out of (a placement once per light)
    found: int = 0                  # strict hits (the v2 rule)
    off: int = 0                    # found, box off
    missed: int = 0
    found_w: float = 0.0            # sum over placements of the share of their lights with a strict hit
    off_w: float = 0.0
    boxes: int = 0                  # boxes drawn
    wrong: int = 0                  # on a barrel of the other color
    second: int = 0                 # a second box on a barrel
    nothing: int = 0                # on no barrel (boxes on empty frames included)
    extra_w: float = 0.0            # wrong + second + nothing, each box 1 / (lights of its arrangement)
    nothing_w: float = 0.0
    empty_frames: int = 0
    clean_empty_frames: int = 0
    empty: int = 0                  # boxes on empty frames
    clean_empty: int = 0            # ... on clean empty frames
    empty_w: float = 0.0
    cluttered_empty_w: float = 0.0  # boxes on empty frames that are not clean, per arrangement
    assumed_frames: int = 0         # frames in here that are an assumption, not a measurement

    @property
    def assumed(self) -> bool:
        """Every frame in here is an assumption."""
        return self.frames > 0 and self.assumed_frames == self.frames

    @property
    def extra(self) -> int:
        return self.wrong + self.second + self.nothing

    @property
    def strict_false(self) -> int:
        """The old "false": every box that is not a strict hit (a misplaced box included)."""
        return self.boxes - self.found

    @property
    def missed_w(self) -> float:
        return self.placements - self.found_w - self.off_w

    def to_dict(self) -> dict:
        d = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}
        d.update(extra=self.extra, strict_false=self.strict_false, missed_w=round(self.missed_w, 4), assumed=self.assumed)
        return d


def tally(counts: dict[str, FrameCount], stems, placements: Placements, table: dict | None = None) -> Tally:
    """Pool the frames ``stems`` of one arm. Raw counts are sums over frames. Weighted counts take every placement
    once: a placement that is in k of these frames adds (hits among the k) / k to ``found_w``; a box that is not on
    its barrel adds 1 / k where k is the number of these frames that show its arrangement."""
    stems = list(stems)
    t = Tally(frames=len(stems))
    if not stems:
        return t
    per_arr = Counter(placements.arrangement[s] for s in stems)
    t.arrangements = len(per_arr)
    t.conditions = len({condition_of(s) for s in stems})
    t.places = len({place_of(s, table) for s in stems})
    t.assumed_frames = sum(1 for s in stems if counts[s].assumed)
    states: dict[tuple, list[str]] = {}
    for s in stems:
        fc = counts[s]
        w = 1.0 / per_arr[placements.arrangement[s]]
        for i, st in enumerate(fc.gt):
            states.setdefault(placements.key[(s, i)], []).append(st)
        t.barrels += len(fc.gt)
        t.found += fc.n_gt(FOUND); t.off += fc.n_gt(OFF); t.missed += fc.n_gt(MISSED)
        t.boxes += len(fc.boxes)
        t.wrong += fc.n_box(WRONG); t.second += fc.n_box(SECOND); t.nothing += fc.n_box(NOTHING)
        t.extra_w += w * fc.extra; t.nothing_w += w * fc.n_box(NOTHING)
        if fc.negative:
            t.empty_frames += 1
            t.empty += len(fc.boxes); t.empty_w += w * len(fc.boxes)
            if fc.clean:
                t.clean_empty_frames += 1
                t.clean_empty += len(fc.boxes)
            else:
                t.cluttered_empty_w += w * len(fc.boxes)
    t.placements = len(states)
    for sts in states.values():
        t.found_w += sts.count(FOUND) / len(sts)
        t.off_w += sts.count(OFF) / len(sts)
    return t


def group_stems(stems, level: str, table: dict | None = None) -> dict[str, list[str]]:
    """The frames by ``"condition"`` or by ``"place"``, in the order each first comes."""
    if level not in ("condition", "place"):
        raise ValueError(f"level must be 'condition' or 'place', got {level!r}")
    out: dict[str, list[str]] = {}
    for s in stems:
        out.setdefault(condition_of(s) if level == "condition" else place_of(s, table), []).append(s)
    return out


# ---------------------------------------------------------------- 4. the rows as text

@dataclass
class TableRow:
    """One line of a counting table: a name and one ``Tally`` per arm (None = no number for that arm)."""
    name: str
    arms: list
    kind: str = "row"               # "row" | "total"


def _w(x: float) -> str:
    return f"{round(x, 1) + 0.0:.1f}"       # + 0.0: a rounding leftover of -0.0 prints as 0.0


def _arm_cells(t: Tally | None) -> list[str]:
    if t is None:
        return ["-"] * len(ARM_HEAD)
    if t.assumed:           # an assumption says "every barrel found" and nothing about its boxes
        return [f"{_w(t.found_w)}*", f"{t.found}*"] + ["-"] * (len(ARM_HEAD) - 2)
    star = "*" if t.assumed_frames else ""       # a total that holds assumed frames is marked too, never mixed in silently
    return [_w(t.found_w) + star, str(t.found) + star, f"{_w(t.off_w)} ({t.off})", f"{_w(t.missed_w)} ({t.missed})",
            str(t.wrong), str(t.second), str(t.nothing), str(t.empty)]


ARM_HEAD = ["found", "raw", "box off", "missed", "wrong", "2nd", "none", "empty"]
BASE_HEAD = ["", "lights", "frames", "brls", "plcm"]
LEGEND = ("found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it "
          "is found; raw = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails "
          "the strict rule, placements (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second "
          "box on a barrel, none = on no barrel, empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two "
          "boxes lies inside the other. plcm = placements (physical barrels), brls = label boxes (a placement once per light). "
          "* = ASSUMED, not measured (on a total: it holds assumed frames).")


def format_table(rows: list[TableRow], arm_names: list[str], markdown: bool = False, title: str = "") -> str:
    """The rows as fixed-width text, or as a markdown table; the columns are explained by ``LEGEND``."""
    n = len(ARM_HEAD)

    def base(r: TableRow) -> list[str]:
        t = next((a for a in r.arms if a is not None), Tally())
        return [r.name, str(t.conditions), str(t.frames), str(t.barrels), str(t.placements)]
    body = [base(r) + [c for a in r.arms for c in _arm_cells(a)] for r in rows]
    if markdown:
        head = ["place / condition", "lights", "frames", "barrels", "placements"] + [f"{a} {h}" for a in arm_names for h in ARM_HEAD]
        lines = ([f"### {title}", ""] if title else []) + ["| " + " | ".join(head) + " |", "|---|" + "---:|" * (len(head) - 1)]
        for r, cells in zip(rows, body):
            lines.append("| " + " | ".join(f"**{c}**" if r.kind == "total" else c for c in cells) + " |")
        return "\n".join(lines)
    widths = [max([len(BASE_HEAD[i])] + [len(b[i]) for b in body]) for i in range(5)]
    aw = [max([len(ARM_HEAD[j])] + [len(b[5 + k * n + j]) for b in body for k in range(len(arm_names))]) for j in range(n)]
    arm_w = sum(aw) + n - 1

    def line(cells: list[str]) -> str:
        left = f"{cells[0]:{widths[0]}} " + " ".join(f"{cells[i]:>{widths[i]}}" for i in range(1, 5))
        arms = [" ".join(f"{cells[5 + k * n + j]:>{aw[j]}}" for j in range(n)) for k in range(len(arm_names))]
        return (left + " | " + " | ".join(arms)).rstrip()
    top = (" " * (sum(widths) + 4) + " | " + " | ".join(f"{a.upper():^{arm_w}}" for a in arm_names)).rstrip()
    hdr = line(BASE_HEAD + ARM_HEAD * len(arm_names))
    rule = "-" * len(hdr)
    out = ([title] if title else []) + [top, hdr, rule]
    for r, cells in zip(rows, body):
        if r.kind == "total":
            out.append(rule)
        out.append(line(cells))
    out.append(rule)
    return "\n".join(out)
