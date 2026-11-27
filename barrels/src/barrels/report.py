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

The vendor arm (2026-11-18). An arm can also be the robot's built-in detector: ``vendor_arm()`` takes its boxes from
the files ``data/vendor/<stem>_vendor.json`` saved with each frame instead of running the color model and the
detector, and they are scored by the same ``evaluate_frame(rule="v2")`` against the same labels. When either arm is
the vendor, BOTH arms are scored only on the frames the vendor was measured on (``vendor_coverage``): a frame with
no vendor file, or with ``available: false``, is left out and counted in the footer, never scored as "the vendor
saw nothing". Two looser counts (``loose_counts``: found by overlap alone, found by position) are reported next to
the strict ones, because the vendor may not draw its boxes the way our labels are drawn; they never enter the
score. The never-regress check that reads this table is ``gate.py``.
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
VENDOR = "vendor"                   # the kind of an arm whose boxes are read from data/vendor/ instead of being detected
LOOSE_KEYS = ("found_iou", "false_iou", "found_center", "false_center")       # the two looser counts (reporting only)
CENTER_TOL_WIDTHS = 0.5             # "in the same place": the two box centers at most this many true-box widths apart


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
    the detector settings (``det_overrides`` are the DetConfig fields changed from the default). ``kind="vendor"``
    (``vendor_arm``) is the robot's built-in detector instead: no model, no DetConfig, its boxes are read from
    the saved ``data/vendor/<stem>_vendor.json`` files."""
    name: str
    model_path: Path | None
    det_overrides: dict = field(default_factory=dict)
    kind: str = "detector"          # "detector" | VENDOR

    @property
    def is_vendor(self) -> bool:
        return self.kind == VENDOR

    def det_config(self):
        from . import detector as det
        return dataclasses.replace(det.DetConfig(), **self.det_overrides)

    def describe(self) -> str:
        if self.is_vendor:
            return "the robot's built-in detector (vendor), its boxes as saved with each frame in data/vendor/<stem>_vendor.json"
        ov = ", ".join(f"{k}={v}" for k, v in self.det_overrides.items()) or "defaults"
        p = Path(self.model_path)
        return f"{p.parent.name}/{p.name}; DetConfig {ov}"


def vendor_arm(name: str = "baseline") -> Arm:
    """The robot's built-in detector as an arm (candidate or baseline)."""
    return Arm(name, None, {}, VENDOR)


# DetConfig's on/off switches until the detector was collapsed (2026-11-26): named here only so that an old command line gets a
# clear answer. The detector with its switches is at the git tag COLLAPSE_TAG.
REMOVED_DET_SWITCHES = ("require_stripe", "stripe_mode", "dark_stripe", "cover_rows", "occl_body_side", "stripe_join", "cap_behind",
                        "side_hidden", "seam_height", "cap_seen_bottom", "slice_box", "cover_unpinned", "stripe_two", "edge_check",
                        "cap_same", "half_stripe", "half_thin", "post_pair", "stripe_wide", "slice_behind", "cap_low", "pin_outline",
                        "pin_thin", "stripe_bridge", "thin_frame", "own_close", "thin_span", "closeup_side", "closeup_stripe",
                        "verify_front", "verify_readings")
ZERO_MEANT_OFF = ("body_min", "body_width", "height_max")      # numbers whose value 0 switched their check off until then
COLLAPSE_TAG = "pre-collapse-2026-11-26"


def parse_det_overrides(items: list[str] | None) -> dict:
    """``["body_width=1.1", "stripe_merge=1.5,min_area_px=30"]`` -> ``{"body_width": 1.1, "stripe_merge": 1.5, "min_area_px": 30}``.
    Each value is converted to the type of that DetConfig field's default; an unknown field or a bad value raises ValueError.
    DetConfig holds numbers only. A switch that was removed in the collapse, or a 0 that used to mean "this check off", raises
    ValueError with a message that names the tag where the old detector is."""
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
            if k in REMOVED_DET_SWITCHES:
                raise ValueError(f"{k} was an on/off switch of the detector and no longer exists: since the collapse of 2026-11-26 every "
                                 f"rule always runs, and only the numbers can be overridden ({', '.join(defaults)}). The detector with "
                                 f"its switches is at the git tag {COLLAPSE_TAG}.")
            if k not in defaults:
                raise ValueError(f"DetConfig has no field {k!r} (fields: {', '.join(defaults)})")
            d = defaults[k]
            if isinstance(d, int):
                out[k] = int(v)
            elif isinstance(d, float):
                out[k] = float(v)
            else:
                out[k] = v
            if k in ZERO_MEANT_OFF and out[k] == 0:
                raise ValueError(f"{k}=0 used to switch that check off. Since the collapse of 2026-11-26 the check always runs, and 0 is "
                                 f"not a size it can use. The detector with its switches is at the git tag {COLLAPSE_TAG}.")
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


def box_center(b) -> tuple[float, float]:
    x0, y0, x1, y1 = b.bbox
    return (x0 + x1) / 2, (y0 + y1) / 2


def loose_counts(preds: list, gts: list) -> dict[str, int]:
    """Two looser ways of counting one frame's boxes, next to the v2 rule and never instead of it:

    * ``found_iou`` / ``false_iou``: same color and IoU >= 0.5; the bottom edge is not checked.
    * ``found_center`` / ``false_center``: same color and the two box centers at most half the TRUE box's width
      apart (``CENTER_TOL_WIDTHS``), nearest pair first. This one does not depend on how tight a box is or on
      whether it covers the whole barrel: it only asks "is there a box of the right color on this barrel".

    Each true barrel and each box is used at most once (``eval_det.match_best_first``); ``false_*`` are the boxes
    left over. Made for the vendor comparison, whose boxes may follow another convention than our labels."""
    def dist(p, g) -> float:
        (px, py), (gx, gy) = box_center(p), box_center(g)
        return math.hypot(px - gx, py - gy)
    by_iou = ed.match_best_first(preds, gts, lambda p, g: ed.box_iou(p.bbox, g.bbox), ed.IOU_THR)
    by_center = ed.match_best_first(preds, gts, lambda p, g: 1.0 / (1.0 + dist(p, g)), 0.0,
                                    eligible=lambda p, g: dist(p, g) <= CENTER_TOL_WIDTHS * g.width)
    return {"found_iou": len(by_iou), "false_iou": len(preds) - len(by_iou),
            "found_center": len(by_center), "false_center": len(preds) - len(by_center)}


def score_boxes(stem: str, preds: list, cam, loose: dict | None = None, labels_dir: Path | str | None = None) -> ed.DetImageResult:
    """Boxes (ours or the vendor's) scored against the frame's box label under the v2 rule. With ``loose`` (a
    dict), the frame's ``loose_counts`` are also put into it under the stem."""
    from . import detect_types as dtp, io
    label = io.load_boxes(stem, labels_dir)
    gts = [b.with_ground(cam) for b in dtp.barrels_from_boxes(label)]
    if loose is not None:
        loose[stem] = loose_counts(preds, gts)
    return ed.evaluate_frame(stem, preds, gts, cam, rule="v2", clean=label.get("clean", True))


def score_frame(stem: str, mask, det_cfg, cam, loose: dict | None = None, labels_dir: Path | str | None = None) -> ed.DetImageResult:
    """Class mask -> boxes -> scored against the box label under the v2 rule (the same three lines every
    experiment script uses)."""
    from . import detector as det
    return score_boxes(stem, det.detect(mask, det_cfg, cam), cam, loose, labels_dir)


@dataclass
class VendorCoverage:
    """Which of the selected frames the vendor detector was measured on, and what was set aside."""
    measured: dict[str, list[str]] = field(default_factory=dict)    # set key -> stems with a usable vendor record
    total: dict[str, int] = field(default_factory=dict)             # set key -> frames selected, with or without one
    barrels: dict[str, list] = field(default_factory=dict)          # stem -> the vendor's barrels (each file is read once)
    no_file: list[str] = field(default_factory=list)                # frames with no <stem>_vendor.json
    not_measured: list[str] = field(default_factory=list)           # frames whose file says available: false
    unreadable: dict[str, str] = field(default_factory=dict)        # stem -> why its file could not be used
    other_objects: int = 0                                          # vendor objects that are not barrels (ball, robot, tag)
    no_box: int = 0                                                 # vendor barrel objects without a usable box

    @property
    def stems(self) -> set[str]:
        return set(self.barrels)

    def to_dict(self) -> dict:
        return {"frames_with_vendor": {k: len(v) for k, v in self.measured.items()}, "frames_selected": dict(self.total),
                "stems": {k: list(v) for k, v in self.measured.items()}, "no_file": list(self.no_file),
                "not_measured": list(self.not_measured), "unreadable": dict(self.unreadable),
                "other_objects_ignored": self.other_objects, "barrels_without_box_ignored": self.no_box}


def vendor_coverage(selection: Selection, splits: dict[str, list[str]], vendor_dir: Path | str | None = None) -> VendorCoverage:
    """Read the vendor file of every selected frame once and sort the frames: measured (the file is there and says
    ``available: true``; an empty object list is a measurement: the vendor saw nothing), no file, not measured
    (``available: false``), unreadable. Only the two barrel classes are kept as boxes (``io.vendor_barrels``); other
    objects are counted. Test frames are refused first, before any vendor file is opened."""
    from . import io
    refuse_test_frames(selection.stems, splits, allow_test=selection.split == "test")
    cov = VendorCoverage()
    for key, stems in selection.sets.items():
        cov.total[key], cov.measured[key] = len(stems), []
        for s in stems:
            try:
                meta = io.load_vendor(s, vendor_dir)
            except FileNotFoundError:
                cov.no_file.append(s); continue
            except ValueError as e:             # bad JSON or a record that breaks the schema
                cov.unreadable[s] = str(e); continue
            if not meta["available"]:           # "not measured" is not "saw nothing"
                cov.not_measured.append(s); continue
            barrels, counts = io.vendor_barrels(meta)
            cov.barrels[s] = barrels
            cov.other_objects += counts["other"]; cov.no_box += counts["no_box"]
            cov.measured[key].append(s)
    return cov


def run_arm(arm: Arm, selection: Selection, splits: dict[str, list[str]], cam=None, home_protocol: str = "loso",
            cache: FrameCache | None = None, only: set[str] | None = None, loose: dict | None = None,
            vendor: VendorCoverage | None = None, labels_dir: Path | str | None = None,
            vendor_dir: Path | str | None = None) -> dict[str, ed.DetImageResult]:
    """stem -> scored frame for one arm.

    ``home_protocol="loso"`` (default): the frames of ``FIT_SET`` (home) are the ones the color model was fit
    on, so each home scene is segmented by a model re-fit (same ``Config``) on the other home scenes — the
    protocol behind the published home number. ``"fixed"``: the model file as it is on the home frames too
    (what the robot runs; optimistic for a model that learned from those very frames).

    ``only``: score just these stems (the vendor comparison: the frames that have a vendor file). The home re-fit
    still learns from every other home scene in ``selection``, so a frame's score does not depend on ``only``.
    ``loose``: a dict that receives stem -> ``loose_counts``. A vendor arm opens no image: it scores the boxes
    in ``vendor`` (``vendor_coverage``, computed here when not given)."""
    from . import geometry as geo
    if home_protocol not in ("loso", "fixed"):
        raise ValueError(f"home_protocol must be 'loso' or 'fixed', got {home_protocol!r}")
    refuse_test_frames(selection.stems, splits, allow_test=selection.split == "test")
    cam = cam or geo.AIM_4A8B6118_BOXFIT
    out: dict[str, ed.DetImageResult] = {}
    if arm.is_vendor:
        vendor = vendor or vendor_coverage(selection, splits, vendor_dir)
        for s in selection.stems:
            if s in vendor.barrels and (only is None or s in only):
                out[s] = score_boxes(s, vendor.barrels[s], cam, loose, labels_dir)
        return out
    from . import cv as bcv, pipeline as pl, worldmap_bridge as wb
    cache = cache or FrameCache()
    model = wb.BarrelDetectorHook.load(arm.model_path, cam=cam).model
    dcfg = arm.det_config()
    for key, stems in selection.sets.items():
        if key == FIT_SET and home_protocol == "loso" and selection.split == "train":
            scenes = {s: parse_name(s)["scene"] for s in stems}
            for fold in bcv.loso_folds(stems, scenes):
                held = [s for s in fold.held_out if only is None or s in only]
                if not held:
                    continue
                m = pl.fit([cache.frame(s) for s in fold.train], [cache.mask(s) for s in fold.train], model.cfg)
                for s in held:
                    out[s] = score_frame(s, pl.segment(cache.frame(s), m)[0], dcfg, cam, loose, labels_dir)
        else:
            for s in stems:
                if only is None or s in only:
                    out[s] = score_frame(s, pl.segment(cache.frame(s), model)[0], dcfg, cam, loose, labels_dir)
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
    loose: dict | None = None   # the looser counts (LOOSE_KEYS) summed over the frames; None when not asked for

    def to_dict(self) -> dict:
        d = {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in dataclasses.asdict(self).items()}
        if d["loose"] is None:
            del d["loose"]          # a report without the looser counts is written exactly as before they existed
        return d


def summarize(results: list[ed.DetImageResult], loose: list[dict] | None = None) -> Cell:
    """Pool scored frames into one Cell. Counts are sums over frames and both colors; the two medians are over
    the matched pairs; score and disqualifier come from ``eval_det.score`` unchanged. ``loose`` (the frames'
    ``loose_counts``, same order) is summed into ``Cell.loose``."""
    if not results:
        return Cell()
    c = Cell(frames=len(results))
    if loose is not None:
        c.loose = {k: sum(x[k] for x in loose) for k in LOOSE_KEYS}
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


def build_rows(sets: dict[str, list[str]], cand: dict[str, ed.DetImageResult], base: dict[str, ed.DetImageResult],
               cand_loose: dict | None = None, base_loose: dict | None = None) -> list[Row]:
    """Per data set: one row per scenario tag (alphabetical), then the set's subtotal (which carries the
    headline score). Last, one ALL row over the sets that are not indicative (counts only meaningful there).
    ``cand_loose`` / ``base_loose`` (stem -> ``loose_counts``) add the looser counts to every cell."""
    rows: list[Row] = []
    keys = list(sets)

    def cell(res: dict, loose: dict | None, stems: list[str]) -> Cell:
        return summarize([res[s] for s in stems], None if loose is None else [loose[s] for s in stems])
    for key in keys:
        label, ind = set_label(key, keys), is_indicative(key)
        by_scene: dict[str, list[str]] = {}
        for s in sets[key]:
            by_scene.setdefault(parse_name(s)["scene"], []).append(s)
        for scene in sorted(by_scene):
            st = by_scene[scene]
            rows.append(Row(key, label, scene, "scene", cell(cand, cand_loose, st), cell(base, base_loose, st), ind))
        rows.append(Row(key, label, "", "subtotal", cell(cand, cand_loose, sets[key]), cell(base, base_loose, sets[key]), ind))
    real = [s for k in keys if not is_indicative(k) for s in sets[k]]
    if sum(1 for k in keys if not is_indicative(k)) > 1:
        rows.append(Row(ALL_KEY, ALL_KEY, "", "total", cell(cand, cand_loose, real), cell(base, base_loose, real), False))
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
    vendor: VendorCoverage | None = None    # set when an arm is the vendor: the rows hold only the frames it was measured on
    loose: bool = False                     # the looser counts are in the cells and are printed

    def subtotal(self, label_or_key: str) -> Row:
        for r in self.rows:
            if r.kind != "scene" and label_or_key in (r.set_key, r.label, r.label.rstrip("*")):
                return r
        raise KeyError(label_or_key)


def make_report(candidate: Arm | None = None, baseline: Arm | None = None, split: str = "train",
                only_sets: list[str] | None = None, home_protocol: str = "loso", cam=None,
                labels_dir: Path | str | None = None, splits: dict[str, list[str]] | None = None,
                loose: bool = False, vendor_dir: Path | str | None = None) -> Report:
    """Steps 1-4 in one call: select the frames, run both arms, build the rows.

    When either arm is the vendor, the frames it was measured on are found first (``vendor_coverage``) and both
    arms are scored on those frames only; the looser counts are then always on. ``loose=True`` adds them to any
    other comparison. Passing the same ``Arm`` object as candidate and baseline runs it once (the gate does)."""
    import time
    from . import cv as bcv
    t0 = time.time()
    dc, db = default_arms()
    candidate, baseline = candidate or dc, baseline or db
    splits = splits if splits is not None else splits_mod.load_splits()
    sel = select_frames(labeled_stems(labels_dir), splits, split=split, only_sets=only_sets)
    vendor = vendor_coverage(sel, splits, vendor_dir) if (candidate.is_vendor or baseline.is_vendor) else None
    only = None if vendor is None else vendor.stems
    loose = bool(loose or vendor is not None)
    cache = FrameCache()

    def run(arm: Arm) -> tuple[dict, dict | None]:
        counts: dict | None = {} if loose else None
        return run_arm(arm, sel, splits, cam=cam, home_protocol=home_protocol, cache=cache, only=only, loose=counts,
                       vendor=vendor, labels_dir=labels_dir), counts

    cres, cloose = run(candidate)
    bres, bloose = (cres, cloose) if baseline is candidate else run(baseline)
    shown = sel if vendor is None else Selection({k: v for k, v in vendor.measured.items() if v}, sel.skipped, sel.split)
    return Report(build_rows(shown.sets, cres, bres, cloose, bloose), candidate, baseline, shown, home_protocol,
                  bcv.git_hash(), time.time() - t0, vendor, loose)


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


def _some(stems, n: int = 4) -> str:
    stems = list(stems)
    return ", ".join(stems[:n]) + (", ..." if len(stems) > n else "")


def vendor_lines(rep: Report) -> list[str]:
    """Footer lines of a vendor comparison: how many frames of each set have a vendor file, what was left out
    and why, what was ignored, and the caveat about the vendor's box convention. Empty for any other report."""
    v = rep.vendor
    if v is None:
        return []
    keys = list(v.total)
    n_with = sum(len(x) for x in v.measured.values())
    lines = ["VENDOR COMPARISON: both arms are scored on the frames that have a vendor file, and only on those ("
             + f"{n_with} of {sum(v.total.values())} frames): "
             + ", ".join(f"{set_label(k, keys)} {len(v.measured[k])} of {v.total[k]}" for k in keys) + "."]
    left = [f"{len(v.no_file)} with no vendor file"]
    if v.not_measured:
        left.append(f"{len(v.not_measured)} not measured ('available: false' in the file; this is not 'the vendor saw nothing'): {_some(v.not_measured)}")
    if v.unreadable:
        left.append(f"{len(v.unreadable)} with a vendor file that could not be read: {_some(v.unreadable)}")
    lines.append("Left out, for both arms: " + "; ".join(left) + ".")
    lines.append(f"Vendor objects that are not barrels (ball, robot, tag) are ignored: {v.other_objects}. "
                 f"Vendor barrels without a usable box, ignored: {v.no_box}.")
    lines.append("Caveat: the vendor may not draw its boxes the way our labels are drawn (how tight, whether the whole barrel is covered), "
                 "so the v2 rule may be harsh on it. Read the looser counts below next to the strict ones; the score is the strict one.")
    return lines


def loose_lines(rep: Report) -> list[str]:
    """The small second table: per set, strict found next to the two looser counts, candidate/baseline."""
    rows = [r for r in rep.rows if r.kind != "scene" and r.cand.loose is not None and r.base.loose is not None]
    if not (rep.loose and rows):
        return []

    def pair(a, b) -> str:
        return f"{a}/{b}"

    name_w = max([len("set")] + [len(f"{r.label} all") for r in rows])
    head = f"{'set':{name_w}} {'brls':>4} | {'strict c/b':>10} | {'overlap c/b':>11} {'false c/b':>9} | {'place c/b':>9} {'false c/b':>9}"
    out = ["", "LOOSER COUNTS per set, candidate/baseline (reporting only: the table and the score above are the v2 rule, unchanged)",
           head, "-" * len(head)]
    for r in rows:
        c, b = r.cand.loose, r.base.loose
        name = f"{r.label} all"
        out.append(f"{name:{name_w}} {r.cand.barrels:>4} | {pair(r.cand.found, r.base.found):>10} | "
                   f"{pair(c['found_iou'], b['found_iou']):>11} {pair(c['false_iou'], b['false_iou']):>9} | "
                   f"{pair(c['found_center'], b['found_center']):>9} {pair(c['false_center'], b['false_center']):>9}")
    out.append("-" * len(head))
    out += textwrap.wrap("strict = barrels found under the v2 rule (the table above). overlap = same color and IoU >= 0.5, the bottom edge not "
                         "checked. place = same color and the two box centers at most half the true box's width apart (it does not depend "
                         "on how tight a box is). false = boxes left without a barrel under that count.", width=120, subsequent_indent="    ")
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
    lines += vendor_lines(rep)
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
    out += loose_lines(rep)
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
    if rep.loose:
        lines += ["## Looser counts (reporting only; candidate / baseline)", "",
                  "| set / scenario | barrels | strict found | overlap found | overlap false | place found | place false |", "|---|" + "---:|" * 6]
        for r in rep.rows:
            c, b = r.cand.loose, r.base.loose
            if c is None or b is None:
                continue
            vals = [_cells(r)["name"].strip(), str(r.cand.barrels), f"{r.cand.found} / {r.base.found}"] + [f"{c[k]} / {b[k]}" for k in LOOSE_KEYS]
            lines.append("| " + " | ".join(f"**{v}**" if r.kind != "scene" else v for v in vals) + " |")
        lines += ["", "- strict = the v2 rule. overlap = same color and IoU >= 0.5, bottom edge not checked. place = same color and box centers "
                  "at most half the true box's width apart. false = boxes left without a barrel under that count.", ""]
    return "\n".join(lines)


def write_csv(rep: Report, path: Path | str) -> Path:
    """One line per table row, plain numbers (empty = no number)."""
    path = Path(path)
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["set", "label", "scene", "kind", "indicative", "frames", "barrels"]
                   + [f"{a}_{k}" for a in ("cand", "base", "delta") for k in COLUMNS + SCORE_COLUMNS] + ["cand_disqualified", "base_disqualified"]
                   + ([f"{a}_{k}" for a in ("cand", "base") for k in LOOSE_KEYS] if rep.loose else []))
        for r in rep.rows:
            d = r.delta

            def v(x):
                return "" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{x:.4f}" if isinstance(x, float) else x)
            w.writerow([r.set_key, r.label, r.scene, r.kind, int(r.indicative), r.cand.frames, r.cand.barrels]
                       + [v(getattr(r.cand, k)) for k in COLUMNS + SCORE_COLUMNS] + [v(getattr(r.base, k)) for k in COLUMNS + SCORE_COLUMNS]
                       + [v(d[k]) for k in COLUMNS + SCORE_COLUMNS] + [int(r.cand.disqualified), int(r.base.disqualified)]
                       + ([v((cell.loose or {}).get(k)) for cell in (r.cand, r.base) for k in LOOSE_KEYS] if rep.loose else []))
    return path


def to_json(rep: Report) -> dict:
    def arm(a: Arm) -> dict:
        if a.is_vendor:
            return {"name": a.name, "kind": VENDOR, "source": "data/vendor/<stem>_vendor.json"}
        mp = Path(a.model_path)
        d = {"name": a.name, "model_path": str(mp.relative_to(PKG_ROOT)) if mp.is_relative_to(PKG_ROOT) else str(mp),
             "det_overrides": a.det_overrides, "det": a.det_config().to_dict()}
        try:
            d["model_config_hash"] = json.load(Path(a.model_path).open()).get("config_hash")
        except (OSError, ValueError):
            d["model_config_hash"] = None
        return d
    out = {"git": rep.git, "rule": "v2", "split": rep.selection.split, "home_protocol": rep.home_protocol, "seconds": round(rep.seconds, 2),
           "candidate": arm(rep.candidate), "baseline": arm(rep.baseline),
           "sets": {k: {"label": set_label(k, list(rep.selection.sets)), "indicative": is_indicative(k), "stems": v} for k, v in rep.selection.sets.items()},
           "skipped": rep.selection.skipped, "rows": [r.to_dict() for r in rep.rows]}
    if rep.loose:           # each cell then carries "loose": {found_iou, false_iou, found_center, false_center}
        out["loose"] = {"found_iou / false_iou": "same color and IoU >= 0.5, bottom edge not checked",
                        "found_center / false_center": f"same color and box centers at most {CENTER_TOL_WIDTHS} of the true box's width apart"}
    if rep.vendor is not None:
        out["vendor"] = rep.vendor.to_dict()
    return out


def write_all(rep: Report, out_dir: Path | str, title: str = "Eval report") -> Path:
    """report.md (the table as printed, then the same as a markdown table), report.csv, report.json in ``out_dir``."""
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    md = format_markdown(rep, title).split("\n")
    (out_dir / "report.md").write_text("\n".join(md[:2] + ["```", format_text(rep), "```", ""] + md[2:]))
    write_csv(rep, out_dir / "report.csv")
    (out_dir / "report.json").write_text(json.dumps(to_json(rep), indent=1) + "\n")
    return out_dir
