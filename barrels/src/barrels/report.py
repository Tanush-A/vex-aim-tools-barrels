"""One table for "what is better where" (TODO step 6, 2026-11-11): data set x scenario rows, a candidate and a
baseline side by side, and the difference. Presentation only — every number comes from ``eval_det`` under the
v2 rule of docs/EVAL.md (``evaluate_frame(rule="v2")`` for the matching, ``score`` for the headline); nothing
here changes what a hit is.

The data flows in five steps, each one function:

1. ``select_frames``  which frames: every stem with a box label, grouped into data sets by
   ``{robot}_{light}_{surface}`` (HOME, CAMPUS, DAVE, and any new session with no code change). Train frames
   only; test frames are refused (``TestFrameError``) unless the caller says ``split="test"`` explicitly.
2. ``run_arm``        one arm (= a color-model file + a DetConfig) on those frames: segment, detect, score each
   frame with ``eval_det.evaluate_frame``. The home frames are scored leave-one-scene-out (the color model is
   re-fit without the scene being scored), exactly as the published home number is; every other set uses the
   model file as it is.
3. ``summarize``      a list of scored frames -> one ``Cell``: found / missed / false, median width ratio,
   median |bottom error|, and (for a whole data set) the headline score and the disqualifier.
4. ``build_rows``     the rows: per data set one row per scenario and a subtotal, candidate next to baseline,
   and ``delta`` = candidate - baseline.
5. ``format_text`` / ``format_markdown`` / ``write_csv`` / ``to_json``  the same rows, four ways.

``make_report`` chains 1-4; ``tools/report.py`` is the command; ``tests/conftest.py`` prints the same table at
the end of a test run.
"""
from __future__ import annotations

import csv
import dataclasses
import json
import math
import textwrap
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import eval_det as ed
from . import splits as splits_mod
from .io import LABELS_DIR, PKG_ROOT, parse_name

GEOMETRY_SCENES = splits_mod.UNASSIGNED_SCENES          # calib / ruler / horizon: geometry only, never scored
SET_ALIASES = {"4A8B_window_light": "HOME", "4A8B_campus_light": "CAMPUS"}     # short names of the sets we talk about
INDICATIVE_ROBOTS = ("DAVE",)       # Dave's frames: his boxes group touching barrels -> indicative; they are in no split
FIT_SET = "4A8B_window_light"       # the frames the color model is fit on -> scored leave-one-scene-out
ALL_KEY = "ALL"
COLUMNS = ("found", "missed", "false", "width", "bottom")          # per arm, in table order
SCORE_COLUMNS = ("score", "neg_false", "clean_neg_false")


class TestFrameError(ValueError):
    """A held-out test frame was about to be scored without the explicit ``split="test"``."""
    __test__ = False        # not a pytest class


# ---------------------------------------------------------------- 1. which frames

def set_key(stem: str) -> str:
    """``{robot}_{light}_{surface}`` of a stem — the data set it belongs to."""
    t = parse_name(stem)
    return f"{t['robot']}_{t['light']}_{t['surface']}"


def is_indicative(key: str) -> bool:
    return key.split("_")[0] in INDICATIVE_ROBOTS


def set_label(key: str, all_keys: list[str] | tuple[str, ...] = ()) -> str:
    """The name shown in the table: HOME / CAMPUS, ``DAVE*`` (``*`` = indicative; the full key when Dave has
    more than one labeled set), else the key itself, so a new session names itself."""
    if key in SET_ALIASES:
        return SET_ALIASES[key]
    if is_indicative(key):
        robot = key.split("_")[0]
        alone = sum(1 for k in all_keys if k.split("_")[0] == robot) <= 1
        return (robot if alone else key) + "*"
    return key


def set_order(keys) -> list[str]:
    """HOME, CAMPUS, then new sessions alphabetically, indicative sets last."""
    first = list(SET_ALIASES)
    return sorted(keys, key=lambda k: (is_indicative(k), first.index(k) if k in first else len(first), k))


def labeled_stems(labels_dir: Path | str | None = None) -> list[str]:
    """Every stem that has a ``<stem>_boxes.json`` (file names only; nothing is opened)."""
    return sorted(p.name[:-len("_boxes.json")] for p in Path(labels_dir or LABELS_DIR).glob("*_boxes.json"))


@dataclass
class Selection:
    sets: dict[str, list[str]]                                  # set key -> stems, in ``set_order``
    skipped: dict[str, list[str]] = field(default_factory=dict)  # reason -> stems left out
    split: str = "train"

    @property
    def stems(self) -> list[str]:
        return [s for v in self.sets.values() for s in v]


def select_frames(stems: list[str], splits: dict[str, list[str]], split: str = "train",
                  only_sets: list[str] | None = None) -> Selection:
    """Group the labeled stems into data sets and keep the ones of ``split``.

    ``split="train"`` (the default): frames in the train split, plus the frames of an indicative set (Dave's),
    which are in no split. ``split="test"``: the test frames and nothing else — the caller has to ask for it.
    Left out and listed under ``skipped``: test frames (when not asked for), geometry-only scenes, names that
    do not follow the convention, and labeled frames that are in no split yet (assign them with
    ``tools/make_splits.py`` first — an unassigned frame might still become a test frame)."""
    if split not in ("train", "test"):
        raise ValueError(f"split must be 'train' or 'test', got {split!r}")
    in_split = {s: name for name, v in splits.items() for s in v}
    groups: dict[str, list[str]] = {}
    skipped: dict[str, list[str]] = {}
    for stem in sorted(set(stems)):
        try:
            tags = parse_name(stem)
        except ValueError:
            skipped.setdefault("name not {robot}_{light}_{surface}_{scene}_{nn}", []).append(stem); continue
        key = set_key(stem)
        if tags["scene"] in GEOMETRY_SCENES:
            skipped.setdefault("geometry-only scene", []).append(stem); continue
        where = in_split.get(stem)
        if split == "test":
            keep = where == "test"
            reason = "not a test frame"
        elif where == "test":
            keep, reason = False, "test frame (held out)"
        elif where == "train" or (where is None and is_indicative(key)):
            keep, reason = True, ""
        else:
            keep, reason = False, ("in no split yet (run tools/make_splits.py)" if where is None else f"split {where}")
        if not keep:
            skipped.setdefault(reason, []).append(stem); continue
        groups.setdefault(key, []).append(stem)
    if only_sets:
        want = {x.upper() for x in only_sets}
        labels = {k: set_label(k, list(groups)) for k in groups}
        groups = {k: v for k, v in groups.items() if k.upper() in want or labels[k].rstrip("*").upper() in want}
    return Selection({k: groups[k] for k in set_order(groups)}, skipped, split)


def refuse_test_frames(stems, splits: dict[str, list[str]], allow_test: bool = False) -> None:
    """Raise ``TestFrameError`` when any stem is a test frame and ``allow_test`` was not given. Called before
    any image is opened, so a slip anywhere upstream cannot look at the held-out frames."""
    if allow_test:
        return
    bad = sorted(set(stems) & set(splits.get("test", [])))
    if bad:
        raise TestFrameError(f"{len(bad)} test frame(s) would be scored ({', '.join(bad[:3])}{', ...' if len(bad) > 3 else ''}); "
                             f"the test split is looked at only when planned (EVAL.md) — pass --split test explicitly")


# ---------------------------------------------------------------- 2. one arm on the frames

@dataclass(frozen=True)
class Arm:
    """One side of the comparison: a color-model file (a results ``config.json`` with a fitted ``model``) and
    the detector settings (``det_overrides`` are the DetConfig fields changed from the default)."""
    name: str
    model_path: Path
    det_overrides: dict = field(default_factory=dict)

    def det_config(self):
        from . import detector as det
        return dataclasses.replace(det.DetConfig(), **self.det_overrides)

    def describe(self) -> str:
        ov = ", ".join(f"{k}={v}" for k, v in self.det_overrides.items()) or "defaults"
        p = Path(self.model_path)
        return f"{p.parent.name}/{p.name}; DetConfig {ov}"


def parse_det_overrides(items: list[str] | None) -> dict:
    """``["body_width=0", "cover_rows=false"]`` -> ``{"body_width": 0.0, "cover_rows": False}``. Each value is
    converted to the type of that DetConfig field's default; an unknown field or a bad value raises ValueError."""
    from . import detector as det
    defaults = det.DetConfig().to_dict()
    out = {}
    for item in items or []:
        for part in item.split(","):
            if not part.strip():
                continue
            if "=" not in part:
                raise ValueError(f"DetConfig override must be field=value, got {part!r}")
            k, v = (x.strip() for x in part.split("=", 1))
            if k not in defaults:
                raise ValueError(f"DetConfig has no field {k!r} (fields: {', '.join(defaults)})")
            d = defaults[k]
            if isinstance(d, bool):
                if v.lower() not in ("1", "0", "true", "false", "on", "off", "yes", "no"):
                    raise ValueError(f"{k} is a switch: use true/false, got {v!r}")
                out[k] = v.lower() in ("1", "true", "on", "yes")
            elif isinstance(d, int):
                out[k] = int(v)
            elif isinstance(d, float):
                out[k] = float(v)
            else:
                out[k] = v
    return out


def default_arms() -> tuple[Arm, Arm]:
    """(candidate, baseline) when nothing is said: what runs today, and the v1 front end with the same detector."""
    from . import worldmap_bridge as wb
    return Arm("candidate", wb.DEFAULT_MODEL), Arm("baseline", wb.V1_MODEL)


class FrameCache:
    """Images are read once and shared by both arms (``pipeline.Frame`` per stem; the home masks for the re-fit)."""

    def __init__(self):
        self._frames: dict = {}
        self._masks: dict = {}

    def frame(self, stem: str):
        from . import io, pipeline as pl
        if stem not in self._frames:
            path = io.find_image(stem)
            if path is None:
                raise FileNotFoundError(f"no image for {stem} in {io.RAW_DIR}")
            self._frames[stem] = pl.Frame.from_image(io.load_image(path))
        return self._frames[stem]

    def mask(self, stem: str):
        from . import io
        if stem not in self._masks:
            self._masks[stem] = io.load_mask(io.mask_path(stem))
        return self._masks[stem]


def score_frame(stem: str, mask, det_cfg, cam) -> ed.DetImageResult:
    """Class mask -> boxes -> scored against the box label under the v2 rule (the same three lines every
    experiment script uses)."""
    from . import detect_types as dtp, detector as det, io
    label = io.load_boxes(stem)
    gts = [b.with_ground(cam) for b in dtp.barrels_from_boxes(label)]
    preds = det.detect(mask, det_cfg, cam)
    return ed.evaluate_frame(stem, preds, gts, cam, rule="v2", clean=label.get("clean", True))


def run_arm(arm: Arm, selection: Selection, splits: dict[str, list[str]], cam=None, home_protocol: str = "loso",
            cache: FrameCache | None = None) -> dict[str, ed.DetImageResult]:
    """stem -> scored frame for one arm.

    ``home_protocol="loso"`` (default): the frames of ``FIT_SET`` (home) are the ones the color model was fit
    on, so each home scene is segmented by a model re-fit (same ``Config``) on the other home scenes — the
    protocol behind the published home number. ``"fixed"``: the model file as it is on the home frames too
    (what the robot runs; optimistic for a model that learned from those very frames)."""
    from . import cv as bcv, geometry as geo, pipeline as pl, worldmap_bridge as wb
    if home_protocol not in ("loso", "fixed"):
        raise ValueError(f"home_protocol must be 'loso' or 'fixed', got {home_protocol!r}")
    refuse_test_frames(selection.stems, splits, allow_test=selection.split == "test")
    cam = cam or geo.AIM_4A8B6118_BOXFIT
    cache = cache or FrameCache()
    model = wb.BarrelDetectorHook.load(arm.model_path, cam=cam).model
    dcfg = arm.det_config()
    out: dict[str, ed.DetImageResult] = {}
    for key, stems in selection.sets.items():
        if key == FIT_SET and home_protocol == "loso" and selection.split == "train":
            scenes = {s: parse_name(s)["scene"] for s in stems}
            for fold in bcv.loso_folds(stems, scenes):
                m = pl.fit([cache.frame(s) for s in fold.train], [cache.mask(s) for s in fold.train], model.cfg)
                for s in fold.held_out:
                    out[s] = score_frame(s, pl.segment(cache.frame(s), m)[0], dcfg, cam)
        else:
            for s in stems:
                out[s] = score_frame(s, pl.segment(cache.frame(s), model)[0], dcfg, cam)
    return out


# ---------------------------------------------------------------- 3. scored frames -> one cell

@dataclass
class Cell:
    """The numbers of one arm for one row."""
    frames: int = 0
    barrels: int = 0            # true barrels
    found: int = 0              # true barrels matched by a box (v2 rule)
    missed: int = 0             # true barrels with no box
    false: int = 0              # boxes that match no barrel (negative frames included)
    width: float = math.nan     # median box width / true width over the found barrels
    bottom: float = math.nan    # median |bottom-edge error| in px over the found barrels
    score: float = math.nan     # mean of the orange and blue F1 (eval_det.score "primary")
    neg_false: int = 0          # false boxes on negative frames
    clean_neg_false: int = 0    # ... on clean negative frames
    disqualified: bool = False  # a false box on a clean negative frame (EVAL.md rule 4)

    def to_dict(self) -> dict:
        return {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in dataclasses.asdict(self).items()}


def summarize(results: list[ed.DetImageResult]) -> Cell:
    """Pool scored frames into one Cell. Counts are sums over frames and both colors; the two medians are over
    the matched pairs; score and disqualifier come from ``eval_det.score`` unchanged."""
    if not results:
        return Cell()
    c = Cell(frames=len(results))
    widths, bottoms = [], []
    for r in results:
        c.barrels += sum(r.n_gt.values())
        c.found += sum(r.tp.values()); c.missed += sum(r.fn.values()); c.false += sum(r.fp.values())
        for m in r.matches:
            widths.append(m.width_ratio); bottoms.append(abs(m.bottom_row_err_px))
    widths = [x for x in widths if math.isfinite(x)]
    c.width = float(np.median(widths)) if widths else math.nan
    c.bottom = float(np.median(bottoms)) if bottoms else math.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)      # a row with no barrels has no F1: its score is nan, quietly
        s = ed.score(results, {}, out_scope=(), rule="v2")
    c.score = s["primary"]
    c.neg_false = s["neg_false_detections"]; c.clean_neg_false = s["neg_clean_false_detections"]
    c.disqualified = bool(s["disqualified"])
    return c


def delta(cand: Cell, base: Cell) -> dict:
    """candidate - baseline for every table column (None where either side has no number)."""
    out = {}
    for k in COLUMNS + SCORE_COLUMNS:
        a, b = getattr(cand, k), getattr(base, k)
        out[k] = None if (isinstance(a, float) and math.isnan(a)) or (isinstance(b, float) and math.isnan(b)) else a - b
    return out


# ---------------------------------------------------------------- 4. the rows

@dataclass
class Row:
    set_key: str            # e.g. 4A8B_campus_light, or ALL
    label: str              # HOME / CAMPUS / DAVE* / the key
    scene: str              # the scenario tag; "" on a subtotal row
    kind: str               # "scene" | "subtotal" | "total"
    cand: Cell
    base: Cell
    indicative: bool = False

    @property
    def delta(self) -> dict:
        return delta(self.cand, self.base)

    def to_dict(self) -> dict:
        return {"set": self.set_key, "label": self.label, "scene": self.scene, "kind": self.kind, "indicative": self.indicative,
                "candidate": self.cand.to_dict(), "baseline": self.base.to_dict(), "delta": self.delta}


def build_rows(sets: dict[str, list[str]], cand: dict[str, ed.DetImageResult], base: dict[str, ed.DetImageResult]) -> list[Row]:
    """Per data set: one row per scenario tag (alphabetical), then the set's subtotal (which carries the
    headline score). Last, one ALL row over the sets that are not indicative (counts only meaningful there)."""
    rows: list[Row] = []
    keys = list(sets)
    for key in keys:
        label, ind = set_label(key, keys), is_indicative(key)
        by_scene: dict[str, list[str]] = {}
        for s in sets[key]:
            by_scene.setdefault(parse_name(s)["scene"], []).append(s)
        for scene in sorted(by_scene):
            st = by_scene[scene]
            rows.append(Row(key, label, scene, "scene", summarize([cand[s] for s in st]), summarize([base[s] for s in st]), ind))
        rows.append(Row(key, label, "", "subtotal", summarize([cand[s] for s in sets[key]]), summarize([base[s] for s in sets[key]]), ind))
    real = [s for k in keys if not is_indicative(k) for s in sets[k]]
    if sum(1 for k in keys if not is_indicative(k)) > 1:
        rows.append(Row(ALL_KEY, ALL_KEY, "", "total", summarize([cand[s] for s in real]), summarize([base[s] for s in real]), False))
    return rows


@dataclass
class Report:
    rows: list[Row]
    candidate: Arm
    baseline: Arm
    selection: Selection
    home_protocol: str = "loso"
    git: str = ""
    seconds: float = math.nan

    def subtotal(self, label_or_key: str) -> Row:
        for r in self.rows:
            if r.kind != "scene" and label_or_key in (r.set_key, r.label, r.label.rstrip("*")):
                return r
        raise KeyError(label_or_key)


def make_report(candidate: Arm | None = None, baseline: Arm | None = None, split: str = "train",
                only_sets: list[str] | None = None, home_protocol: str = "loso", cam=None,
                labels_dir: Path | str | None = None, splits: dict[str, list[str]] | None = None) -> Report:
    """Steps 1-4 in one call: select the frames, run both arms, build the rows."""
    import time
    from . import cv as bcv
    t0 = time.time()
    dc, db = default_arms()
    candidate, baseline = candidate or dc, baseline or db
    splits = splits if splits is not None else splits_mod.load_splits()
    sel = select_frames(labeled_stems(labels_dir), splits, split=split, only_sets=only_sets)
    cache = FrameCache()
    cres = run_arm(candidate, sel, splits, cam=cam, home_protocol=home_protocol, cache=cache)
    bres = run_arm(baseline, sel, splits, cam=cam, home_protocol=home_protocol, cache=cache)
    return Report(build_rows(sel.sets, cres, bres), candidate, baseline, sel, home_protocol, bcv.git_hash(), time.time() - t0)


# ---------------------------------------------------------------- 5. the same rows, four ways

def _num(x, fmt: str, signed: bool = False) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    if signed:
        text = f"{x:+{fmt}}"
        return "." if float(text) == 0 else text        # a change too small to print is no change
    return f"{x:{fmt}}"


_FMT = {"found": "d", "missed": "d", "false": "d", "width": ".2f", "bottom": ".1f", "score": ".2f", "neg_false": "d", "clean_neg_false": "d"}
_HEAD = {"found": "found", "missed": "miss", "false": "false", "width": "width", "bottom": "bot"}
_W = {"found": 5, "missed": 4, "false": 5, "width": 5, "bottom": 5}


def _cells(row: Row) -> dict:
    """Every printed field of a row as a string (shared by the text, markdown and CSV writers)."""
    d = row.delta
    out = {"name": (f"{row.label} all" if row.kind != "scene" else f"  {row.scene}"), "frames": str(row.cand.frames), "barrels": str(row.cand.barrels)}
    for k in COLUMNS:
        out[f"c_{k}"] = _num(getattr(row.cand, k), _FMT[k]); out[f"b_{k}"] = _num(getattr(row.base, k), _FMT[k])
        out[f"d_{k}"] = _num(d[k], _FMT[k], signed=True)
    if row.kind == "scene":
        out.update(c_score="", b_score="", d_score="", flags="")
    elif row.kind == "total":       # counts only: a score pooled over different sets is not a number anyone has agreed on
        out.update(c_score="", b_score="", d_score="", flags=f"{row.cand.neg_false}/{row.base.neg_false}")
    else:
        out["c_score"] = _num(row.cand.score, ".2f"); out["b_score"] = _num(row.base.score, ".2f"); out["d_score"] = _num(d["score"], ".2f", signed=True)
        dq = "".join(n for n, c in (("c", row.cand), ("b", row.base)) if c.disqualified)
        out["flags"] = f"{row.cand.neg_false}/{row.base.neg_false}" + (f" DQ:{dq}" if dq else "")
    return out


def footer_lines(rep: Report) -> list[str]:
    sel = rep.selection
    n = {k: len(v) for k, v in sel.sets.items()}
    keys = list(sel.sets)
    lines = [f"candidate = {rep.candidate.describe()}",
             f"baseline  = {rep.baseline.describe()}",
             f"delta = candidate - baseline ('.' = no change). Frames: {sel.split} split only"
             + (", test frames never opened" if sel.split == "train" else " (a PLANNED test look)") + "; "
             + ", ".join(f"{set_label(k, keys)} {n[k]}" for k in keys) + f". git {rep.git}; {rep.seconds:.1f} s.",
             "Rule: EVAL.md v2, as eval_det implements it — a box is right when same color, IoU >= 0.5 and bottom edge within max(3 px, 10 % of the true height).",
             "found / miss = true barrels with / without a right box; false = boxes that match no barrel; width = median box width / true width over the found;",
             "bot = median |bottom-edge error| in px over the found; score = mean of the orange and blue F1 (pooled over the set's frames), on the set rows only.",
             "negF c/b = false boxes on empty (negative) frames, candidate/baseline; DQ:c / DQ:b = that arm drew a box on a CLEAN empty frame, which disqualifies it."]
    if FIT_SET in sel.sets and sel.split == "train":
        if rep.home_protocol == "loso":
            lines.append("HOME is scored leave-one-scene-out: the color model is fit on these frames, so each scene is segmented by a model re-fit without it "
                         "(the published home number). Other sets use the model file as it is.")
            lines.append("The ALL row adds up the counts of the sets that are not indicative; it has no score (no agreed headline pools different sets).")
        else:
            lines.append("HOME is scored with the model file as it is (--home-protocol fixed): the model was fit on these very frames, so this is NOT the "
                         "published leave-one-scene-out home number.")
    if any(is_indicative(k) for k in keys):
        lines.append("* indicative only: Dave's boxes group touching barrels, and his frames are in no split.")
    for reason, stems in sel.skipped.items():
        if reason.startswith(("in no split", "name not")):
            lines.append(f"left out, {reason}: {len(stems)} frame(s) ({', '.join(stems[:4])}{', ...' if len(stems) > 4 else ''})")
    return lines


def format_text(rep: Report) -> str:
    """Fixed-width plain text, under 140 columns."""
    name_w = max([len("set/scenario")] + [len(_cells(r)["name"]) for r in rep.rows])
    arm_w = sum(_W.values()) + len(_W) - 1

    def arm_block(c: dict, p: str) -> str:
        return " ".join(f"{c[f'{p}_{k}']:>{_W[k]}}" for k in COLUMNS)

    head_arm = " ".join(f"{_HEAD[k]:>{_W[k]}}" for k in COLUMNS)
    top = (f"{'':{name_w}} {'':>3} {'':>4} | {'CANDIDATE':^{arm_w}} | {'BASELINE':^{arm_w}} | {'DELTA (cand - base)':^{arm_w}} | {'score':^15} | negF")
    hdr = (f"{'set/scenario':{name_w}} {'frm':>3} {'brls':>4} | {head_arm} | {head_arm} | {head_arm} | {'cand':>4} {'base':>4} {'delta':>5} | c/b")
    rule = "-" * len(hdr)
    out = [top, hdr, rule]
    for r in rep.rows:
        c = _cells(r)
        if r.kind == "total":
            out.append(rule)
        line = (f"{c['name']:{name_w}} {c['frames']:>3} {c['barrels']:>4} | {arm_block(c, 'c')} | {arm_block(c, 'b')} | {arm_block(c, 'd')} | "
                f"{c['c_score']:>4} {c['b_score']:>4} {c['d_score']:>5} | {c['flags']}")
        out.append(line.rstrip())
        if r.kind == "subtotal":
            out.append("")
    while out and out[-1] == "":
        out.pop()
    out.append(rule)
    for line in footer_lines(rep):
        out += textwrap.wrap(line, width=120, subsequent_indent="    ")
    return "\n".join(out)


def format_markdown(rep: Report, title: str = "Eval report") -> str:
    cols = ["set / scenario", "frames", "barrels"] + [f"{a} {_HEAD[k]}" for a in ("cand", "base", "Δ") for k in COLUMNS] + ["score cand", "score base", "score Δ", "negF c/b"]
    lines = [f"# {title}", "", "| " + " | ".join(cols) + " |", "|---|" + "---:|" * (len(cols) - 1)]
    for r in rep.rows:
        c = _cells(r)
        vals = [c["name"].strip(), c["frames"], c["barrels"]] + [c[f"{p}_{k}"] for p in "cbd" for k in COLUMNS] + [c["c_score"], c["b_score"], c["d_score"], c["flags"]]
        if r.kind != "scene":
            vals = [f"**{v}**" if v else v for v in vals]
        lines.append("| " + " | ".join(vals) + " |")
    lines += [""] + [f"- {x}" for x in footer_lines(rep)] + [""]
    return "\n".join(lines)


def write_csv(rep: Report, path: Path | str) -> Path:
    """One line per table row, plain numbers (empty = no number)."""
    path = Path(path)
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["set", "label", "scene", "kind", "indicative", "frames", "barrels"]
                   + [f"{a}_{k}" for a in ("cand", "base", "delta") for k in COLUMNS + SCORE_COLUMNS] + ["cand_disqualified", "base_disqualified"])
        for r in rep.rows:
            d = r.delta

            def v(x):
                return "" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{x:.4f}" if isinstance(x, float) else x)
            w.writerow([r.set_key, r.label, r.scene, r.kind, int(r.indicative), r.cand.frames, r.cand.barrels]
                       + [v(getattr(r.cand, k)) for k in COLUMNS + SCORE_COLUMNS] + [v(getattr(r.base, k)) for k in COLUMNS + SCORE_COLUMNS]
                       + [v(d[k]) for k in COLUMNS + SCORE_COLUMNS] + [int(r.cand.disqualified), int(r.base.disqualified)])
    return path


def to_json(rep: Report) -> dict:
    def arm(a: Arm) -> dict:
        mp = Path(a.model_path)
        d = {"name": a.name, "model_path": str(mp.relative_to(PKG_ROOT)) if mp.is_relative_to(PKG_ROOT) else str(mp),
             "det_overrides": a.det_overrides, "det": a.det_config().to_dict()}
        try:
            d["model_config_hash"] = json.load(Path(a.model_path).open()).get("config_hash")
        except (OSError, ValueError):
            d["model_config_hash"] = None
        return d
    return {"git": rep.git, "rule": "v2", "split": rep.selection.split, "home_protocol": rep.home_protocol, "seconds": round(rep.seconds, 2),
            "candidate": arm(rep.candidate), "baseline": arm(rep.baseline),
            "sets": {k: {"label": set_label(k, list(rep.selection.sets)), "indicative": is_indicative(k), "stems": v} for k, v in rep.selection.sets.items()},
            "skipped": rep.selection.skipped, "rows": [r.to_dict() for r in rep.rows]}


def write_all(rep: Report, out_dir: Path | str, title: str = "Eval report") -> Path:
    """report.md (the table as printed, then the same as a markdown table), report.csv, report.json in ``out_dir``."""
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    md = format_markdown(rep, title).split("\n")
    (out_dir / "report.md").write_text("\n".join(md[:2] + ["```", format_text(rep), "```", ""] + md[2:]))
    write_csv(rep, out_dir / "report.csv")
    (out_dir / "report.json").write_text(json.dumps(to_json(rep), indent=1) + "\n")
    return out_dir
