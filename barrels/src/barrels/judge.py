"""The standard pass rule for experiments, as a tool (2026-11-26, TODO M3).

Every earlier experiment wrote its own pass rule, and they were stricter than the noise: one barrel is about 0.03 of
a condition's score, the rules allowed 0.02, and hand-set thresholds that found 70 more barrels failed. This module
is the one rule. A color-step idea, a detector idea and a whole new pipeline are judged the same way.

**What is judged.** A *detector* is any function ``detect_frame(stem, frame) -> list[Barrel]``: the frame's name and
its pixels in (``pipeline.Frame``; ``frame.rgb`` is the picture, which may not be written to), boxes out. A baseline
and a candidate are both run on the **ordinary train conditions** (``data/conditions.json``; today 17 conditions at 8
places). Extreme and unlisted conditions are run and printed, never judged. Test frames are refused before any image
is opened.

**How it is counted.** ``counting.py``: every physical placement once (the share of its lights in which it is
found), a box on a barrel that fails the strict rule once, boxes that are not on their barrel once per arrangement.
"Found" is always the strict v2 rule of ``docs/EVAL.md``.

**The verdict** (``decide``; the clauses in plain words are in ``docs/EVAL.md``, "The standard pass rule"). The
margins are measured, not chosen: each is the largest change that a change which means nothing (one hue unit, three
saturation units, two brightness units on the fixed color model) produced at that level
(``experiments/2026-11-26_noise_floor``, stored in ``results/baseline/margins.json``).

- FAIL when the candidate is worse than the baseline by more than the margin in any of: found over all ordinary
  places; found at any single place; boxes that are not on their barrel; boxes on empty frames (any new box on a
  *clean* empty frame fails).
- PASS when nothing fails and found over all ordinary places is up by more than the margin (or boxes that are not on
  their barrel are down by more than the margin while found is not lower).
- NO CLEAR DIFFERENCE otherwise.

**A candidate with fitted numbers** is judged leave one place out: the caller gives ``fit(train_stems, held_place)
-> detector``; for each place it is called with the frames of the other places and the detector it returns is run on
the held-out place only. The verdict then rests on held-out results alone.

In the order the data flows: ``train_frames`` (which frames) -> ``load_truth`` (labels and placements) ->
``run_many`` (each detector on each frame -> a ``Run``: its boxes and their states) -> ``compare`` (two runs -> a
``Judgement``: the tables, every barrel that changed, the verdict) -> ``format_judgement`` / ``write``. ``judge`` does
it all in one call; ``tools/judge.py`` is the command.
"""
from __future__ import annotations

import csv
import dataclasses
import datetime as dt
import importlib.util
import json
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import conditions as cnd
from . import counting as ct
from . import report as rp
from . import splits as splits_mod
from .detect_types import COLOR_NAMES, Barrel
from .io import PKG_ROOT

Detector = Callable[[str, object], list]        # detect_frame(stem, frame) -> list[Barrel]
MARGINS_PATH = PKG_ROOT / "results" / "baseline" / "margins.json"
PASS, FAIL, NO_CLEAR = "PASS", "FAIL", "NO CLEAR DIFFERENCE"
BETTER, WORSE, WITHIN = "BETTER", "WORSE", "within the noise"
EPS = 1e-9                                      # shares are fractions (1/3, 1/5): a tie is a tie


# ---------------------------------------------------------------- 1. which frames

def train_frames(labels_dir=None, splits: dict | None = None) -> dict[str, list[str]]:
    """Every train frame with a box label, by the class of its condition: ``{"ordinary": [...], "extreme": [...],
    "excluded": [...], "unlisted": [...]}``. Dave's frames and the geometry-only scenes are left out. Raises
    ``report.TestFrameError`` if a test frame got in."""
    splits = splits if splits is not None else splits_mod.load_splits()
    sel = rp.select_frames(rp.labeled_stems(labels_dir), splits, split="train")
    out: dict[str, list[str]] = {cnd.ORDINARY: [], cnd.EXTREME: [], cnd.EXCLUDED: [], cnd.UNLISTED: []}
    for key, stems in sel.sets.items():
        if rp.is_indicative(key):
            continue
        for s in stems:
            out[cnd.info(ct.condition_of(s)).klass].append(s)
    require_train([s for v in out.values() for s in v], splits)
    return out


def require_train(stems, splits: dict | None = None) -> None:
    """Raise unless every stem is a train frame: ``report.TestFrameError`` for a test frame, ValueError for a frame
    of any other split or of none. Called before anything is opened."""
    splits = splits if splits is not None else splits_mod.load_splits()
    rp.refuse_test_frames(stems, splits)
    train = set(splits.get("train", []))
    bad = sorted(s for s in set(stems) if s not in train)
    if bad:
        raise ValueError(f"{len(bad)} frame(s) are not train frames ({', '.join(bad[:3])}{', ...' if len(bad) > 3 else ''}): "
                         "the judge runs on train frames only")


def load_frame(stem: str, splits: dict | None = None):
    """The ``pipeline.Frame`` of a TRAIN frame, its arrays read-only (no step may change a pixel). The safe way for
    a ``fit`` function to read its training frames: any other frame is refused."""
    from . import io, pipeline as pl
    require_train([stem], splits)
    path = io.find_image(stem)
    if path is None:
        raise FileNotFoundError(f"no image for {stem} in {io.RAW_DIR}")
    frame = pl.Frame.from_image(io.load_image(path))
    for a in (frame.bgr, frame.rgb, frame.sat, frame.val):
        a.setflags(write=False)
    return frame


@dataclass
class Truth:
    """The labels of a set of frames: the true barrels, the ``clean`` flag, and which box is which placement."""
    gts: dict[str, list]
    clean: dict[str, bool]
    placements: ct.Placements


def load_truth(stems, labels_dir=None) -> Truth:
    gts, clean = ct.load_gts(stems, labels_dir)
    return Truth(gts, clean, ct.build_placements(gts))


# ---------------------------------------------------------------- 2. detectors

def model_detector(model=None, det_overrides: dict | None = None, cam=None, describe: str = "") -> Detector:
    """A color model plus the rule detector as a ``detect_frame``. ``model``: None (the adopted model, what runs
    today), a results ``config.json`` path, or a ``pipeline.Model``. ``det_overrides``: the ``DetConfig`` fields
    changed from the default."""
    from . import detector as det, geometry as geo, pipeline as pl, worldmap_bridge as wb
    cam = cam or geo.AIM_4A8B6118_BOXFIT
    path = None
    if model is None:
        model = wb.DEFAULT_MODEL
    if not isinstance(model, pl.Model):
        path = Path(model)
        model = wb.BarrelDetectorHook.load(path, cam=cam).model
    cfg = dataclasses.replace(det.DetConfig(), **(det_overrides or {}))

    def detect_frame(stem: str, frame) -> list:
        return det.detect(pl.segment(frame, model)[0], cfg, cam)
    ov = ", ".join(f"{k}={v}" for k, v in (det_overrides or {}).items()) or "defaults"
    detect_frame.describe = describe or f"{f'{path.parent.name}/{path.name}' if path else 'a pipeline.Model'}; DetConfig {ov}"
    return detect_frame


def fixed_detector() -> Detector:
    """What runs today: the adopted color model and ``DetConfig()``."""
    return model_detector(describe="today's default (the adopted color model, DetConfig defaults)")


def leave_one_place_out(fit: Callable, train_stems: list[str], describe: str = "") -> Detector:
    """A candidate with fitted numbers, as one ``detect_frame``. ``fit(stems, held_place) -> detect_frame`` is called
    once per place, with the ordinary train frames of every OTHER place, the first time a frame of that place comes
    up; what it returns is used for that place only. So no frame is ever scored by something fitted on its own
    place. (A report-only frame at a place of its own is scored by a fit on all the ordinary frames.)"""
    fitted: dict[str, Detector] = {}

    def detect_frame(stem: str, frame) -> list:
        place = ct.place_of(stem)
        if place not in fitted:
            d = fit([s for s in train_stems if ct.place_of(s) != place], place)
            if not callable(d):
                raise TypeError(f"fit(stems, {place!r}) must return a detect_frame(stem, frame) function, got {type(d).__name__}")
            fitted[place] = d
        return fitted[place](stem, frame)
    detect_frame.describe = describe or "fitted leave one place out"
    detect_frame.fitted = fitted
    return detect_frame


def load_callable(spec: str) -> Callable:
    """``path/to/file.py:name`` -> that function (the file's folder is put on the import path, as a script's is)."""
    path, _, name = spec.rpartition(":")
    if not path or not name:
        raise ValueError(f"expected FILE.py:FUNCTION, got {spec!r}")
    p = Path(path).resolve()
    if not p.exists():
        raise ValueError(f"no such file: {path}")
    sys.path.insert(0, str(p.parent))
    mod_spec = importlib.util.spec_from_file_location(f"judge_candidate_{p.stem}", p)
    mod = importlib.util.module_from_spec(mod_spec)
    sys.modules[mod_spec.name] = mod
    mod_spec.loader.exec_module(mod)
    if not callable(getattr(mod, name, None)):
        raise ValueError(f"{path} has no function {name!r}")
    return getattr(mod, name)


# ---------------------------------------------------------------- 3. detectors on frames

@dataclass
class Run:
    """One detector on a set of frames: its boxes and, per frame, the state of every barrel and box."""
    name: str
    describe: str = ""
    boxes: dict[str, list] = field(default_factory=dict)
    counts: dict[str, ct.FrameCount] = field(default_factory=dict)
    seconds: float = 0.0


def run_many(detectors: dict[str, Detector], stems, truth: Truth, splits: dict | None = None) -> dict[str, Run]:
    """Every detector on every frame. Each image is read once, handed to each detector in turn and dropped. Refuses
    anything but train frames before the first image is opened."""
    stems = list(stems)
    require_train(stems, splits)
    runs = {n: Run(n, getattr(d, "describe", "") or n) for n, d in detectors.items()}
    for s in stems:
        frame = load_frame(s, splits)
        for n, d in detectors.items():
            t0 = time.perf_counter()
            preds = list(d(s, frame))
            runs[n].seconds += time.perf_counter() - t0
            bad = [p for p in preds if not isinstance(p, Barrel)]
            if bad:
                raise TypeError(f"{n}: detect_frame must return detect_types.Barrel objects, got {type(bad[0]).__name__} on {s}")
            runs[n].boxes[s] = preds
            runs[n].counts[s] = ct.classify_frame(s, preds, truth.gts[s], truth.clean[s])
    return runs


# ---------------------------------------------------------------- 4. the margins and the verdict

@dataclass(frozen=True)
class Margins:
    """How much each count may move before it is called a difference. Units: placements for found; boxes counted
    once per arrangement for the rest. Measured by ``experiments/2026-11-26_noise_floor/run.py``. A margin per
    direction: the fixed model was picked for scoring well, so a change that means nothing loses far more than it
    gains, and a gain is compared with the largest such gain, a loss with the largest such loss."""
    found_gain: float               # found over the ordinary conditions: up by MORE than this = better
    found_loss: float               # ... down by more than this = worse
    extra_rise: float               # boxes that are not on their barrel: up by more than this = worse
    extra_fall: float               # ... down by more than this = better
    cluttered_empty: float          # boxes on empty frames that hold clutter: up by more than this = worse
    place: dict = field(default_factory=dict)       # place -> found at that place: down by more than this = worse
    place_default: float = 1.0      # a place that was not measured
    clean_empty: float = 0.0        # boxes on clean empty frames: none
    source: str = ""

    def for_place(self, place: str) -> float:
        return float(self.place.get(place, self.place_default))


def load_margins(path: Path | str = MARGINS_PATH) -> Margins:
    """The margins the noise-floor experiment wrote. Raises FileNotFoundError with the command that makes them."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"no margins at {path}: run  python barrels/experiments/2026-11-26_noise_floor/run.py")
    d = json.loads(path.read_text())
    j = d.get("judge")
    if d.get("version") != 1 or not isinstance(j, dict):
        raise ValueError(f"{path}: expected version 1 with a 'judge' block")
    return margins_from_dict(j, f"{path.name}, made {d.get('made', '?')} at git {d.get('git', '?')}")


def margins_from_dict(j: dict, source: str = "") -> Margins:
    """The ``judge`` block of margins.json (or the same block as first registered) as ``Margins``."""
    return Margins(float(j["found_gain"]), float(j["found_loss"]), float(j["extra_rise"]), float(j["extra_fall"]), float(j["cluttered_empty"]),
                   {k: float(v) for k, v in j.get("place", {}).items()}, float(j.get("place_default", 1.0)), float(j.get("clean_empty", 0.0)), source)


@dataclass
class Clause:
    key: str            # found | place | extra | empty
    state: str          # BETTER | WORSE | within the noise
    text: str


@dataclass
class Verdict:
    result: str         # PASS | FAIL | NO CLEAR DIFFERENCE
    clauses: list[Clause]
    reason: str

    def state(self, key: str) -> str:
        return next(c.state for c in self.clauses if c.key == key)


def _state(delta: float, up: float, down: float, higher_is_better: bool = True) -> str:
    """BETTER / WORSE when ``delta`` is above ``up`` or below ``-down``, by more than a rounding error."""
    if delta > up + EPS:
        return BETTER if higher_is_better else WORSE
    if delta < -(down + EPS):
        return WORSE if higher_is_better else BETTER
    return WITHIN


def decide(base: ct.Tally, cand: ct.Tally, places: dict[str, tuple[ct.Tally, ct.Tally]], m: Margins) -> Verdict:
    """The written clauses, on the tallies of the ordinary conditions (``base`` / ``cand`` over all of them,
    ``places``: place -> (baseline, candidate)). Numbers in, verdict out; nothing else is looked at.

    1. found: found (strict, per placement) over all places up by more than ``m.found_gain`` -> BETTER; down by more
       than ``m.found_loss`` -> WORSE.
    2. place: found at one place down by more than that place's margin -> WORSE.
    3. extra: boxes not on their barrel (per arrangement) up by more than ``m.extra_rise`` -> WORSE; down by more
       than ``m.extra_fall`` -> BETTER.
    4. empty: more boxes on clean empty frames than the baseline (``m.clean_empty`` = 0), or boxes on empty frames
       with clutter up by more than ``m.cluttered_empty`` -> WORSE.
    FAIL if any clause is WORSE. Else PASS if found is BETTER, or extra is BETTER and found is not lower. Else NO
    CLEAR DIFFERENCE."""
    d_found = cand.found_w - base.found_w
    found = Clause("found", _state(d_found, m.found_gain, m.found_loss),
                   f"found, the ordinary conditions together: {base.found_w:.1f} -> {cand.found_w:.1f} of {base.placements} placements "
                   f"({d_found:+.1f}; counted per frame {base.found} -> {cand.found} of {base.barrels}). Better above +{m.found_gain:.1f}, "
                   f"worse below -{m.found_loss:.1f}.")
    moved, worse = [], []
    for p, (b, c) in places.items():
        d = c.found_w - b.found_w
        if abs(d) > EPS:
            bad = d < -(m.for_place(p) + EPS)
            unmeasured = "" if p in m.place else ", not measured at this place: re-run the noise floor"
            moved.append(f"{p} {d:+.1f} of {b.placements} (margin {m.for_place(p):.1f}{unmeasured}{', WORSE' if bad else ''})")
            if bad:
                worse.append(p)
    place = Clause("place", WORSE if worse else WITHIN,
                   "found, place by place: " + ("; ".join(moved) if moved else "no place moved") + ".")
    d_extra = cand.extra_w - base.extra_w
    extra = Clause("extra", _state(d_extra, m.extra_rise, m.extra_fall, higher_is_better=False),
                   f"boxes that are not on their barrel: {base.extra_w:.1f} -> {cand.extra_w:.1f} counted once per arrangement ({d_extra:+.1f}; "
                   f"per frame: on nothing {base.nothing} -> {cand.nothing}, second box {base.second} -> {cand.second}, wrong color "
                   f"{base.wrong} -> {cand.wrong}). Worse above +{m.extra_rise:.1f}, better below -{m.extra_fall:.1f}.")
    d_clean = cand.clean_empty - base.clean_empty
    d_clut = cand.cluttered_empty_w - base.cluttered_empty_w
    empty_bad = d_clean > m.clean_empty + EPS or d_clut > m.cluttered_empty + EPS
    empty = Clause("empty", WORSE if empty_bad else WITHIN,
                   f"boxes on empty frames: on clean ones {base.clean_empty} -> {cand.clean_empty} (margin {m.clean_empty:g}: none is allowed); on "
                   f"ones with clutter {base.cluttered_empty_w:.1f} -> {cand.cluttered_empty_w:.1f} per arrangement (margin {m.cluttered_empty:.1f}).")
    clauses = [found, place, extra, empty]
    bad = [c.key for c in clauses if c.state == WORSE]
    names = {"found": "found over all places", "place": "found at " + ", ".join(worse), "extra": "boxes that are not on their barrel",
             "empty": "boxes on empty frames"}
    if bad:
        return Verdict(FAIL, clauses, "worse than the baseline by more than the noise in: " + "; ".join(names[k] for k in bad) + ".")
    if found.state == BETTER:
        return Verdict(PASS, clauses, "found is up by more than the noise, and nothing is worse by more than the noise.")
    if extra.state == BETTER and d_found >= -EPS:
        return Verdict(PASS, clauses, "boxes that are not on their barrel are down by more than the noise, found is not lower, and nothing is "
                                      "worse by more than the noise.")
    return Verdict(NO_CLEAR, clauses, "no count moved by more than a change that means nothing moves it.")


# ---------------------------------------------------------------- 5. two runs -> the judgement

@dataclass
class Change:
    """One true barrel whose state differs between the two runs."""
    stem: str
    index: int              # its place in the label file's list (0-based)
    color: str
    bbox: tuple
    before: str             # found | off | missed
    after: str
    judged: bool = True     # False: a report-only (extreme / unlisted) frame

    @property
    def kind(self) -> str:
        """gained (now a strict hit), lost (was a strict hit), or other (box off <-> missed)."""
        return "gained" if self.after == ct.FOUND else "lost" if self.before == ct.FOUND else "other"


@dataclass
class Judgement:
    baseline: Run
    candidate: Run
    frames: dict[str, list[str]]
    truth: Truth
    total: tuple                    # (baseline Tally, candidate Tally) over the ordinary conditions
    places: dict                    # place -> (baseline Tally, candidate Tally)
    conditions: dict                # condition -> (baseline, candidate), ordinary
    report_only: dict               # condition -> (baseline, candidate), extreme / unlisted
    changes: list[Change]
    box_changes: list[dict]         # frames whose boxes-not-on-their-barrel differ
    verdict: Verdict
    margins: Margins
    lopo: bool = False
    git: str = ""
    made: str = ""

    @property
    def result(self) -> str:
        return self.verdict.result


def compare(baseline: Run, candidate: Run, frames: dict[str, list[str]], truth: Truth, margins: Margins | None = None,
            lopo: bool = False) -> Judgement:
    """Two runs on the same frames -> the tables, every barrel and box that changed, and the verdict. ``frames`` as
    ``train_frames`` gives them: the verdict uses ``frames["ordinary"]`` only; extreme and unlisted frames that both
    runs cover are tabulated as report only."""
    from . import cv as bcv
    margins = margins or load_margins()
    ordinary = list(frames.get(cnd.ORDINARY, []))
    for r in (baseline, candidate):
        missing = [s for s in ordinary if s not in r.counts]
        if missing:
            raise ValueError(f"the run {r.name!r} has no result for {len(missing)} ordinary frame(s) ({missing[0]}, ...)")
    extra = [s for k in (cnd.EXTREME, cnd.UNLISTED) for s in frames.get(k, []) if s in baseline.counts and s in candidate.counts]

    def pair(stems: list[str]) -> tuple:
        return ct.tally(baseline.counts, stems, truth.placements), ct.tally(candidate.counts, stems, truth.placements)
    total = pair(ordinary)
    places = {p: pair(ss) for p, ss in ct.group_stems(ordinary, "place").items()}
    conditions = {c: pair(ss) for c, ss in ct.group_stems(ordinary, "condition").items()}
    report_only = {c: pair(ss) for c, ss in ct.group_stems(extra, "condition").items()}
    changes, box_changes = [], []
    for judged, stems in ((True, ordinary), (False, extra)):
        for s in stems:
            b, c = baseline.counts[s], candidate.counts[s]
            for i, (x, y) in enumerate(zip(b.gt, c.gt)):
                if x != y:
                    g = truth.gts[s][i]
                    changes.append(Change(s, i, COLOR_NAMES[g.color], tuple(g.bbox), x, y, judged))
            nb = {k: b.n_box(k) for k in ct.EXTRA_STATES}
            nc = {k: c.n_box(k) for k in ct.EXTRA_STATES}
            if nb != nc:
                box_changes.append({"stem": s, "judged": judged, "empty": b.negative, "clean": b.clean, "before": nb, "after": nc,
                                    "boxes_after": [(COLOR_NAMES[p.color], tuple(int(v) for v in p.bbox)) for p, st in zip(candidate.boxes[s], c.boxes)
                                                    if st in ct.EXTRA_STATES]})
    return Judgement(baseline, candidate, frames, truth, total, places, conditions, report_only, changes, box_changes,
                     decide(total[0], total[1], places, margins), margins, lopo, bcv.git_hash(), dt.date.today().isoformat())


def judge(candidate: Detector | None = None, baseline: Detector | None = None, *, fit: Callable | None = None,
          name: str = "candidate", base_name: str = "baseline", report_only: bool = True, margins: Margins | None = None,
          out_dir: Path | str | None = None, frames: dict | None = None, truth: Truth | None = None,
          splits: dict | None = None) -> Judgement:
    """Everything in one call.

    ``candidate``: a ``detect_frame(stem, frame) -> list[Barrel]``. ``baseline``: the same; None = what runs today
    (``fixed_detector()``). ``fit``: instead of ``candidate``, for anything with fitted numbers:
    ``fit(train_stems, held_place) -> detect_frame``, judged leave one place out. ``report_only=False`` skips the
    extreme conditions (faster). ``out_dir``: also write judge.md, judge.json and changes.csv there. ``frames``,
    ``truth``, ``splits``: given by a caller that has them already (several judgements in one script; the tests);
    by default the committed train frames, their labels and ``data/splits.json``."""
    if (candidate is None) == (fit is None):
        raise ValueError("give exactly one of candidate (a detect_frame) and fit (a function that returns one per held-out place)")
    frames = frames or train_frames(splits=splits)
    stems = frames[cnd.ORDINARY] + ((frames[cnd.EXTREME] + frames[cnd.UNLISTED]) if report_only else [])
    truth = truth or load_truth(stems)
    if fit is not None:
        candidate = leave_one_place_out(fit, frames[cnd.ORDINARY], getattr(fit, "describe", "") or f"{name}: fitted leave one place out")
    runs = run_many({base_name: baseline or fixed_detector(), name: candidate}, stems, truth, splits)
    j = compare(runs[base_name], runs[name], frames, truth, margins, lopo=fit is not None)
    if out_dir is not None:
        write(j, out_dir)
    return j


# ---------------------------------------------------------------- 6. the judgement as text and files

def _rows(d: dict, total: tuple | None = None, total_name: str = "") -> list[ct.TableRow]:
    rows = [ct.TableRow(k, list(v)) for k, v in d.items()]
    if total is not None:
        rows.append(ct.TableRow(total_name, list(total), "total"))
    return rows


def _box(c: Change) -> str:
    return f"{c.stem} #{c.index + 1} {c.color} at {list(c.bbox)}: {c.before} -> {c.after}"


def format_judgement(j: Judgement, markdown: bool = False) -> str:
    """The whole judgement as plain text (or markdown): what was run, the tables, every barrel that changed, the
    clauses with their margins, and the verdict as the last line."""
    arms = [j.baseline.name, j.candidate.name]
    b, c = j.total
    n_ord = len(j.frames[cnd.ORDINARY])

    def table(rows, title):
        t = ct.format_table(rows, arms, markdown, title if markdown else "")
        return ([] if markdown else [title]) + [t, ""]

    def para(text: str) -> list[str]:
        return [text] if markdown else textwrap.wrap(text, width=150, subsequent_indent="    ")
    out = [("# " if markdown else "") + f"JUDGE: {j.candidate.name} against {j.baseline.name}", ""]
    out += para(f"baseline  = {j.baseline.describe}")
    out += para(f"candidate = {j.candidate.describe}")
    out += para(f"Frames: {n_ord} ordinary train frames, {len(j.conditions)} conditions at {len(j.places)} places: {b.placements} placements "
                f"(physical barrels) in {b.arrangements} arrangements, {b.barrels} barrels when every light is counted. Test frames never opened. "
                f"git {j.git}, {j.made}; {j.baseline.seconds + j.candidate.seconds:.0f} s in the detectors.")
    if j.lopo:
        out += para("LEAVE ONE PLACE OUT: every place was scored by a candidate fitted on the other places only; the verdict rests on held-out results.")
    out.append("")
    out += table(_rows(j.places, j.total, "all ordinary places"), "BY PLACE (the verdict is computed on these)")
    out += table(_rows(j.conditions), "BY CONDITION (one light each)")
    if j.report_only:
        out += table(_rows(j.report_only), "REPORT ONLY (extreme or unlisted conditions; never judged)")
    out += [("- " if markdown else "") + x for x in para(ct.LEGEND)] + [""]
    judged = [x for x in j.changes if x.judged]
    gained, lost, other = ([x for x in judged if x.kind == k] for k in ("gained", "lost", "other"))
    out.append(("## " if markdown else "") + f"BARRELS THAT CHANGED on the ordinary conditions: {len(gained)} gained, {len(lost)} lost"
               + (f", {len(other)} moved between 'box off' and 'missed'" if other else "") + " (counted per frame)")
    for head, items in (("gained", gained), ("lost", lost), ("other", other)):
        out += [f"  {'+' if head == 'gained' else '-' if head == 'lost' else '~'} {_box(x)}" for x in items]
    rest = [x for x in j.changes if not x.judged]
    if rest:
        out.append(f"  report only: {sum(x.kind == 'gained' for x in rest)} gained, {sum(x.kind == 'lost' for x in rest)} lost on the extreme conditions (judge.json lists them)")
    bx = [x for x in j.box_changes if x["judged"]]
    out += ["", ("## " if markdown else "") + f"BOXES NOT ON THEIR BARREL that changed: {len(bx)} frame(s)"]
    for x in bx:
        kind = "" if not x["empty"] else " [empty frame, clean]" if x["clean"] else " [empty frame with clutter]"
        diff = ", ".join(f"{k.replace('_', ' ')} {x['before'][k]} -> {x['after'][k]}" for k in ct.EXTRA_STATES if x["before"][k] != x["after"][k])
        out.append(f"  {x['stem']}{kind}: {diff}" + (f"; now {x['boxes_after']}" if x["boxes_after"] else ""))
    out += ["", ("## " if markdown else "") + f"THE CLAUSES (margins: {j.margins.source or 'given by the caller'})"]
    for cl in j.verdict.clauses:
        lines = para(f"[{cl.state}] {cl.text}")
        out += [("- " if markdown else "  ") + lines[0]] + ["  " + x for x in lines[1:]]
    out += ["", f"VERDICT: {j.verdict.result}. {j.verdict.reason}"]
    return "\n".join(out)


def to_json(j: Judgement) -> dict:
    def pairs(d: dict) -> dict:
        return {k: {"baseline": v[0].to_dict(), "candidate": v[1].to_dict()} for k, v in d.items()}
    return {"verdict": j.verdict.result, "reason": j.verdict.reason,
            "clauses": [dataclasses.asdict(c) for c in j.verdict.clauses],
            "margins": dataclasses.asdict(j.margins), "lopo": j.lopo, "git": j.git, "made": j.made,
            "baseline": {"name": j.baseline.name, "describe": j.baseline.describe, "seconds": round(j.baseline.seconds, 1)},
            "candidate": {"name": j.candidate.name, "describe": j.candidate.describe, "seconds": round(j.candidate.seconds, 1)},
            "frames": {k: len(v) for k, v in j.frames.items()},
            "total": {"baseline": j.total[0].to_dict(), "candidate": j.total[1].to_dict()},
            "places": pairs(j.places), "conditions": pairs(j.conditions), "report_only": pairs(j.report_only),
            "changes": [dataclasses.asdict(c) | {"kind": c.kind} for c in j.changes], "box_changes": j.box_changes}


def write(j: Judgement, out_dir: Path | str) -> Path:
    """judge.md (the text, tables in a code block), judge.json (every number) and changes.csv (one line per barrel
    that changed) in ``out_dir``."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "judge.md").write_text(f"# Judge: {j.candidate.name} against {j.baseline.name}: {j.verdict.result}\n\n```\n{format_judgement(j)}\n```\n")
    (out_dir / "judge.json").write_text(json.dumps(to_json(j), indent=1, default=str) + "\n")
    with (out_dir / "changes.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stem", "barrel", "color", "bbox", "before", "after", "kind", "place", "condition", "judged"])
        for c in j.changes:
            w.writerow([c.stem, c.index + 1, c.color, " ".join(map(str, c.bbox)), c.before, c.after, c.kind, ct.place_of(c.stem), ct.condition_of(c.stem), int(c.judged)])
    return out_dir
