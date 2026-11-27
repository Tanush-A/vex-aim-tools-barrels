"""The never-regress check, with a margin (2026-11-26; the first, zero-tolerance version was 2026-11-18).

The principle (Tanush, 2026-11-26: "a general principle, not a strict rule"): a change may not make the protected
sets worse **by more than a change that means nothing moves them**. The first version failed when any single
scenario row of home or campus lost one barrel or gained one false box. That is tighter than the noise: moving one
hue edge of the color model by one unit moves these counts by a barrel here and there
(``experiments/2026-11-26_noise_floor``). This version:

- judges a protected set on its **totals**, not on its single rows;
- counts as ``counting.py`` does: found = strict hits (the v2 rule), every physical placement once; a box on its
  barrel that fails the strict rule is not a false box; the boxes that are not on their barrel are counted once per
  arrangement;
- fails a protected set only when its found is lower than the stored baseline's **by more than the set's margin**,
  or its boxes-not-on-their-barrel higher by more than the margin. The margins are the largest change a one-step
  neighbour of the color model produced in that set, at least one whole unit (``results/baseline/margins.json``);
- still **lists every barrel and every box that changed**, in every set, pass or fail, so a person sees it;
- keeps one hard line: a new box on a *clean* empty frame fails it, in any set. Boxes on empty frames that hold
  clutter get a margin like everything else.

In the order the data flows:

1. ``snapshot``   a ``report.Report`` -> one line per frame of its candidate arm: the state of every true barrel
   (found / box off / missed), of every box, and which placement each barrel is. ``save_baseline`` writes it to
   ``results/baseline/baseline.json`` (committed; one frame per line, so a change is a one-line diff).
2. ``load_protected``   the protected sets, ``results/baseline/protected.json``: each a name and the data sets
   (``{robot}_{light}_{surface}``) it is made of, so the glass table under five lights is one protected set.
   ``load_margins``: the margins.
3. ``compare``    stored baseline against this run -> one ``SetChange`` per protected set, one per other data set
   (for information), and the empty frames.
4. ``GateResult.passed``, and ``GateResult.lower``: anything lower at all, which is what ``--save-baseline`` looks
   at, so the stored reference never drifts down unnoticed.
5. ``format_gate``   plain text, ending in RESULT: PASS or RESULT: FAIL.

The command is ``python barrels/tools/report.py --gate`` (and ``--save-baseline``).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import counting as ct
from .io import PKG_ROOT

BASELINE_DIR = PKG_ROOT / "results" / "baseline"
BASELINE_PATH = BASELINE_DIR / "baseline.json"        # the stored run (written by --save-baseline, committed)
PROTECTED_PATH = BASELINE_DIR / "protected.json"      # the protected sets
MARGINS_PATH = BASELINE_DIR / "margins.json"          # the measured noise (written by experiments/2026-11-26_noise_floor/run.py)
VERSION = 2
FRAME_KEYS = ("stem", "set", "arr", "pl", "gt", "boxes", "clean")
FLOOR = 1.0             # no margin is below one whole unit: one barrel flipping is the smallest thing that can happen
EPS = 1e-9
SAME, BETTER, LOWER, WORSE, NEW, GONE, CHANGED = "same", "better", "lower, within the margin", "WORSE", "new", "gone", "cannot be compared"
ABSENT = "no frames"        # a protected set with no frame in the baseline or in this run: nothing to check yet
ALIASES = {"HOME": "4A8B_window_light", "CAMPUS": "4A8B_campus_light"}        # the names the eval table prints


# ---------------------------------------------------------------- 1. the run, one line per frame

def snapshot(rep, made: str = "") -> dict:
    """The candidate arm of a report as plain data: for every frame its data set, its arrangement, which placement
    each true barrel is, and the states (``counting.FrameCount.to_dict``: one letter per barrel and per box)."""
    from . import report as rp
    if rep.cand_counts is None or rep.placements is None:
        raise ValueError("no per-frame counts to store: " + (rep.placement_error or "the report was not made by make_report"))
    arm = rp.to_json(rep)["candidate"]
    frames = []
    for key, stems in rep.selection.sets.items():
        for s in stems:
            fc = rep.cand_counts[s]
            frames.append({"stem": s, "set": key, "arr": "/".join(rep.placements.arrangement[s]),
                           "pl": [rep.placements.key[(s, i)][-1] for i in range(len(fc.gt))]} | {k: v for k, v in fc.to_dict().items() if k != "stem"})
    return {"version": VERSION, "made": made, "git": rep.git, "arm": rep.candidate.describe(),
            "model_config_hash": arm.get("model_config_hash"), "det": arm.get("det"),
            "split": rep.selection.split, "home_protocol": rep.home_protocol, "frames": frames}


def validate(snap: dict) -> None:
    if not isinstance(snap, dict) or snap.get("version") != VERSION:
        got = snap.get("version") if isinstance(snap, dict) else snap
        raise ValueError(f"baseline version must be {VERSION}, got {got!r}" + (" (a baseline from before 2026-11-26: save a new one with "
                         "python barrels/tools/report.py --save-baseline)" if got == 1 else ""))
    if not isinstance(snap.get("frames"), list):
        raise ValueError("baseline needs a 'frames' list")
    for r in snap["frames"]:
        missing = [k for k in FRAME_KEYS if k not in r]
        if missing:
            raise ValueError(f"baseline frame {r!r} lacks {missing}")
        if len(r["pl"]) != len(r["gt"]):
            raise ValueError(f"baseline frame {r['stem']}: {len(r['gt'])} barrels but {len(r['pl'])} placements")


def save_baseline(snap: dict, path: Path | str = BASELINE_PATH) -> Path:
    """Write the snapshot, one frame per line so a change shows up as a one-line diff in git."""
    validate(snap)
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    head = {k: v for k, v in snap.items() if k != "frames"}
    text = json.dumps(head, indent=1)[:-2] + ',\n "frames": [\n' + ",\n".join("  " + json.dumps(r) for r in snap["frames"]) + "\n ]\n}\n"
    path.write_text(text)
    return path


def load_baseline(path: Path | str = BASELINE_PATH) -> dict:
    snap = json.loads(Path(path).read_text())
    validate(snap)
    return snap


# ---------------------------------------------------------------- 2. what is protected, and by how much

@dataclass(frozen=True)
class Group:
    """One protected set: a name and the data sets (``{robot}_{light}_{surface}``) it is made of."""
    name: str
    sets: tuple[str, ...]


DEFAULT_PROTECTED = (Group("HOME", (ALIASES["HOME"],)), Group("CAMPUS", (ALIASES["CAMPUS"],)))      # used when protected.json is missing


def load_protected(path: Path | str = PROTECTED_PATH) -> tuple[Group, ...]:
    """The protected sets. The file holds ``{"protected": [{"name": ..., "sets": [...]}, ...]}``; a plain name in
    the list (``"HOME"``, or a full set key) is a set of its own. ``DEFAULT_PROTECTED`` when the file is missing."""
    path = Path(path)
    if not path.exists():
        return DEFAULT_PROTECTED
    items = json.loads(path.read_text()).get("protected")
    if not (isinstance(items, list) and items):
        raise ValueError(f"{path} must hold {{\"protected\": [...]}} with at least one set")
    out = []
    for it in items:
        if isinstance(it, str) and it:
            out.append(Group(it, (ALIASES.get(it.upper(), it),)))
        elif isinstance(it, dict) and it.get("name") and isinstance(it.get("sets"), list) and it["sets"] and all(isinstance(s, str) and s for s in it["sets"]):
            out.append(Group(it["name"], tuple(ALIASES.get(s.upper(), s) for s in it["sets"])))
        else:
            raise ValueError(f"{path}: a protected set is a name or {{\"name\": ..., \"sets\": [set keys]}}, got {it!r}")
    if len({g.name for g in out}) != len(out):
        raise ValueError(f"{path}: two protected sets have the same name")
    return tuple(out)


@dataclass(frozen=True)
class Margins:
    """Per protected set: how far found may drop (placements) and boxes-not-on-their-barrel may rise (per
    arrangement) before the check fails. ``cluttered_empty``: the same for boxes on empty frames with clutter, all
    sets together. ``clean_empty`` is 0: the hard line."""
    groups: dict = field(default_factory=dict)          # name -> {"found": x, "extra": y}
    cluttered_empty: float = FLOOR
    clean_empty: float = 0.0
    source: str = "no margins file: one whole unit everywhere"

    def of(self, name: str) -> tuple[float, float]:
        g = self.groups.get(name, {})
        return float(g.get("found", FLOOR)), float(g.get("extra", FLOOR))


def load_margins(path: Path | str = MARGINS_PATH) -> Margins:
    """The gate's margins from ``margins.json`` (its ``gate`` block). A missing file gives the floor, one whole unit
    for every set, and says so in ``source``."""
    path = Path(path)
    if not path.exists():
        return Margins()
    d = json.loads(path.read_text())
    g = d.get("gate")
    if d.get("version") != 1 or not isinstance(g, dict):
        raise ValueError(f"{path}: expected version 1 with a 'gate' block")
    return Margins({k: {"found": float(v["found"]), "extra": float(v["extra"])} for k, v in g.get("groups", {}).items()},
                   float(g.get("cluttered_empty", FLOOR)), float(g.get("clean_empty", 0.0)),
                   f"{path.name}, made {d.get('made', '?')} at git {d.get('git', '?')}")


# ---------------------------------------------------------------- 3. baseline against this run

def _unpack(snap: dict) -> tuple[dict, ct.Placements, dict]:
    """(stem -> FrameCount, the placements, set key -> stems) of a snapshot."""
    counts, pl, sets = {}, ct.Placements(), {}
    for r in snap["frames"]:
        fc = ct.FrameCount.from_dict(r)
        counts[fc.stem] = fc
        arr = tuple(r["arr"].split("/"))
        pl.arrangement[fc.stem] = arr
        for i, k in enumerate(r["pl"]):
            pl.key[(fc.stem, i)] = arr + (k,)
        sets.setdefault(r["set"], []).append(fc.stem)
    return counts, pl, sets


@dataclass
class SetChange:
    """One set (a protected one, or any other data set) in the baseline and in this run."""
    name: str
    sets: tuple[str, ...]
    protected: bool
    status: str                     # same | better | lower, within the margin | WORSE | new | gone | cannot be compared
    base: ct.Tally | None
    cand: ct.Tally | None
    margin: tuple[float, float] = (FLOOR, FLOOR)        # (found, boxes not on their barrel); used for a protected set
    barrels: list = field(default_factory=list)         # every barrel whose state changed: "stem #n: found -> missed"
    boxes: list = field(default_factory=list)           # every frame whose boxes-not-on-their-barrel changed
    why: str = ""                   # for "cannot be compared"

    @property
    def fails(self) -> bool:
        return self.protected and self.status in (WORSE, GONE, CHANGED)

    @property
    def is_lower(self) -> bool:
        """Lower than the baseline at all (also inside the margin), or not comparable."""
        return self.status in (LOWER, WORSE, GONE, CHANGED)

    def describe(self) -> str:
        b, c = self.base, self.cand
        if self.status == ABSENT:
            return "no frames in the baseline or in this run"
        if self.status == NEW:
            return f"found {c.found_w:.1f} of {c.placements} placements ({c.found} of {c.barrels} per frame); boxes not on their barrel {c.extra}"
        if self.status == GONE:
            return f"was found {b.found_w:.1f} of {b.placements}; not in this run"
        if self.status == CHANGED:
            return f"its frames or labels changed since the baseline ({self.why}): cannot be compared"
        d, e = c.found_w - b.found_w, c.extra_w - b.extra_w
        text = (f"found {b.found_w:.1f} -> {c.found_w:.1f} of {c.placements} placements" + (f" ({d:+.1f})" if abs(d) > EPS else "")
                + f" [per frame {b.found} -> {c.found} of {c.barrels}]; boxes not on their barrel {b.extra_w:.1f} -> {c.extra_w:.1f}"
                + (f" ({e:+.1f})" if abs(e) > EPS else ""))
        if self.protected:
            text += f"; margins {self.margin[0]:.1f} / {self.margin[1]:.1f}"
        return text + f": {self.status}"


def _set_change(name: str, keys: tuple, protected: bool, base, cand, margin: tuple[float, float]) -> SetChange:
    (bc, bp, bs), (cc, cp, cs) = base, cand
    b_stems = [s for k in keys for s in bs.get(k, [])]
    c_stems = [s for k in keys for s in cs.get(k, [])]
    tb = ct.tally(bc, b_stems, bp) if b_stems else None
    tc = ct.tally(cc, c_stems, cp) if c_stems else None
    if not b_stems or not c_stems:
        return SetChange(name, keys, protected, NEW if c_stems else GONE if b_stems else ABSENT, tb, tc, margin)
    why = ""
    if set(b_stems) != set(c_stems):
        why = f"{len(b_stems)} frames -> {len(c_stems)} frames"
    else:
        diff = [s for s in c_stems if len(bc[s].gt) != len(cc[s].gt) or [bp.key[(s, i)] for i in range(len(bc[s].gt))] != [cp.key[(s, i)] for i in range(len(cc[s].gt))]]
        if diff:
            why = f"the labels of {len(diff)} frame(s) changed, {diff[0]} first"
    if why:
        return SetChange(name, keys, protected, CHANGED, tb, tc, margin, why=why)
    barrels, boxes = [], []
    for s in c_stems:
        barrels += [f"{s} #{i + 1}: {x} -> {y}" for i, (x, y) in enumerate(zip(bc[s].gt, cc[s].gt)) if x != y]
        nb, nc = [bc[s].n_box(k) for k in ct.EXTRA_STATES], [cc[s].n_box(k) for k in ct.EXTRA_STATES]
        if nb != nc:
            boxes.append(f"{s}: " + ", ".join(f"{k.replace('_', ' ')} {x} -> {y}" for k, x, y in zip(ct.EXTRA_STATES, nb, nc) if x != y))
    d, e = tc.found_w - tb.found_w, tc.extra_w - tb.extra_w
    if d < -(margin[0] + EPS) or e > margin[1] + EPS:
        status = WORSE
    elif d < -EPS or e > EPS:
        status = LOWER
    elif d > EPS or e < -EPS:
        status = BETTER
    else:
        status = SAME
    return SetChange(name, keys, protected, status, tb, tc, margin, barrels, boxes)


@dataclass
class GateResult:
    groups: list[SetChange]                 # the protected sets: these decide
    others: list[SetChange]                 # every other data set: shown only
    clean_empty: list[str]                  # clean empty frames with more boxes than in the baseline: each fails
    cluttered: tuple[float, float]          # boxes on empty frames with clutter, per arrangement: (baseline, this run)
    cluttered_frames: list[str]             # the frames behind a change of that number
    margins: Margins
    baseline: dict                          # the stored snapshot's header (made, git, arm)
    current: dict
    notes: list[str] = field(default_factory=list)

    @property
    def cluttered_fails(self) -> bool:
        return self.cluttered[1] - self.cluttered[0] > self.margins.cluttered_empty + EPS

    @property
    def failures(self) -> list[SetChange]:
        return [g for g in self.groups if g.fails]

    @property
    def passed(self) -> bool:
        return not self.failures and not self.clean_empty and not self.cluttered_fails

    @property
    def lower(self) -> list[str]:
        """Everything that is lower than the baseline at all, inside a margin or not. ``--save-baseline`` refuses to
        store such a run without ``--force``, so the reference cannot slide down one margin at a time."""
        out = [g.name for g in self.groups if g.is_lower] + self.clean_empty
        if self.cluttered[1] - self.cluttered[0] > EPS:
            out.append("boxes on empty frames with clutter")
        return out


def compare(baseline: dict, current: dict, protected=DEFAULT_PROTECTED, margins: Margins | None = None) -> GateResult:
    """Stored baseline against this run. Each protected set is judged on its totals against its margin
    (``SetChange``); every other data set is compared the same way for information; a clean empty frame with more
    boxes than in the baseline fails outright; boxes on empty frames with clutter may rise by their margin."""
    validate(baseline); validate(current)
    margins = margins or Margins()
    base, cand = _unpack(baseline), _unpack(current)
    groups = [_set_change(g.name, g.sets, True, base, cand, margins.of(g.name)) for g in protected]
    taken = {k for g in protected for k in g.sets}
    keys = [k for k in cand[2] if k not in taken] + [k for k in base[2] if k not in taken and k not in cand[2]]
    others = [_set_change(k, (k,), False, base, cand, (FLOOR, FLOOR)) for k in keys]
    clean, clut_frames = [], []
    for s, fc in cand[0].items():
        if not fc.negative:
            continue
        before, now = (len(base[0][s].boxes) if s in base[0] else 0), len(fc.boxes)       # a frame the baseline has not seen counts from 0
        if fc.clean and now > before:
            clean.append(f"{s}: {before} -> {now} box(es)")
        elif not fc.clean and now != before:
            clut_frames.append(f"{s}: {before} -> {now} box(es)")
    cluttered = (ct.tally(base[0], list(base[0]), base[1]).cluttered_empty_w, ct.tally(cand[0], list(cand[0]), cand[1]).cluttered_empty_w)
    head = lambda s: {k: v for k, v in s.items() if k != "frames"}  # noqa: E731
    res = GateResult(groups, others, clean, cluttered, clut_frames, margins, head(baseline), head(current))
    for g in groups:
        if g.status == NEW:
            res.notes.append(f"{g.name} is on the protected list but has no frames in the stored baseline: it is not protected until a new baseline is saved.")
        if g.status == ABSENT:
            res.notes.append(f"{g.name} is on the protected list but has no frames in the baseline or in this run.")
    return res


# ---------------------------------------------------------------- 5. plain text

def format_gate(res: GateResult, title: str = "NEVER-REGRESS CHECK") -> str:
    names = ", ".join(g.name for g in res.groups)
    out = [title,
           f"this run : {res.current.get('arm', '?')}; git {res.current.get('git', '?')}",
           f"baseline : saved {res.baseline.get('made', '?')} from git {res.baseline.get('git', '?')} ({res.baseline.get('arm', '?')})",
           f"Protected sets: {names}. A protected set fails when its found (strict rule, each placement once) is lower than the baseline's by",
           "more than its margin, or its boxes that are not on their barrel are higher by more than its margin. A new box on a clean empty",
           "frame fails in any set. Every barrel and box that changed is listed below, whether or not anything fails.",
           f"Margins (found / boxes): {res.margins.source}.", ""]

    def block(g: SetChange, tag: str) -> None:
        out.append(f"  {g.name}  {g.describe()}  [{tag}]")
        out.extend(f"      barrel  {x}" for x in g.barrels)
        out.extend(f"      boxes   {x}" for x in g.boxes)

    out.append("PROTECTED SETS, baseline -> this run")
    for g in res.groups:
        block(g, "protected")
    out += ["", "EMPTY FRAMES (every set)"]
    out.append("  clean empty frames with a new box: " + ("none" if not res.clean_empty else f"{len(res.clean_empty)} frame(s): FAILS"))
    out.extend(f"      {x}" for x in res.clean_empty)
    b, c = res.cluttered
    out.append(f"  boxes on empty frames with clutter, once per arrangement: {b:.1f} -> {c:.1f} (margin {res.margins.cluttered_empty:.1f})"
               + (": WORSE" if res.cluttered_fails else ""))
    out.extend(f"      {x}" for x in res.cluttered_frames)
    moved = [g for g in res.others if g.status not in (SAME, NEW)]
    new = [g for g in res.others if g.status == NEW]
    same = [g for g in res.others if g.status == SAME]
    out += ["", "OTHER SETS, for information only (they cannot fail the check)"]
    for g in moved:
        block(g, "information only")
    if same:
        out.append(f"  unchanged: {len(same)} set(s) ({', '.join(g.name for g in same)})")
    for g in new:
        block(g, "information only, new")
    out += [""] + [f"Note: {n}" for n in res.notes]
    if res.passed:
        low = res.lower
        out.append("RESULT: PASS. No protected set is worse than the baseline by more than its margin, and no clean empty frame gained a box."
                   + (f" Lower inside the margin: {', '.join(low)}; read the lists above." if low else ""))
    else:
        why = []
        worse = [g.name for g in res.failures if g.status == WORSE]
        cannot = [g.name for g in res.failures if g.status in (CHANGED, GONE)]
        if worse:
            why.append(f"{len(worse)} protected set(s) worse by more than the margin ({', '.join(worse)})")
        if res.clean_empty:
            why.append(f"a new box on a clean empty frame in {len(res.clean_empty)} frame(s) ({', '.join(x.split(':')[0] for x in res.clean_empty)})")
        if res.cluttered_fails:
            why.append("boxes on empty frames with clutter up by more than the margin")
        if cannot:
            why.append(f"{len(cannot)} protected set(s) cannot be compared ({', '.join(cannot)})")
        out.append("RESULT: FAIL. " + "; ".join(why) + ". This change must not become the default as it is.")
    return "\n".join(out)
