"""The judged candidates of the peaks experiment (PREREG.md): this frame's color ranges set from a peak of its own
histogram, falling back to the fixed ranges when no confident peak exists.

    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-27_peaks/candidates.py:fit_P1

Each candidate is a ``fit(train_stems, held_place) -> detect_frame``: the setting (one row of ``GRID``) is chosen on
the training places by ``choose`` and the detector with it is run on the held-out place only.

    P0  F0_naive peaks (every gated pixel)                       -- the known failure, for comparison
    P1  F6_pair_small peaks (stripe pattern + barrel-sized region) -- the primary candidate
    P2  F5_pair peaks (stripe pattern only)
    P3  F1_sat peaks (saturation-weighted, no structure)
    P5  P1's frame ranges as the first pass of the self-calibration (selfcal AB, its own defaults), then selfcal
    S0  report only: selfcal AB with its defaults on the fixed ranges (the comparison for P5; no fitted number)

How one setting turns the found peaks into ranges (``frame_boxes``), per color, starting from the fixed range
[lo, hi] (orange 3-13 S >= 140, blue 103-119 S >= 113):

- the peak is used only when it exists, the finder kept at least ``n_min`` pixels of that color, and the peak's hue
  lies within ``cap`` hue units of the fixed range (lo - cap <= hue <= hi + cap). Otherwise the fixed range stays.
- ``shift``: the range is moved so its middle sits on the peak, its half-width the fixed one plus ``pad``.
  ``union``: the hull of the fixed range and that moved range (the range only widens).
- blue only, ``s_follow``: when the blue peak is used, the blue saturation floor becomes 0.6 x the peak's saturation,
  never under 60 and never above the fixed floor. Orange's floor is never moved (orange keeps its saturation).
"""
from __future__ import annotations

import dataclasses
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import peaks as pk  # noqa: E402

from barrels import boxfit as bf  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
MODEL = hl.adopted_model()
DET = det.DetConfig()
FIXED = {c: (MODEL.boxes[c].lo[0] - pl.HUE_SHIFT[c], MODEL.boxes[c].hi[0] - pl.HUE_SHIFT[c], MODEL.boxes[c].lo[1]) for c in (ORANGE, BLUE)}
S_FOLLOW, S_FLOOR_MIN = 0.6, 60.0

# the grid, the most careful setting first (a tie keeps the earlier one)
KEYS = ("cap", "n_min", "pad", "s_follow", "mode")
GRID = [dict(zip(KEYS, v)) for v in itertools.product((4, 8), (200, 50), (0, 2), (False, True), ("union", "shift"))]
FINDER = {"P0": "F0_naive", "P1": "F6_pair_small", "P2": "F5_pair", "P3": "F1_sat", "P5": "F6_pair_small"}

_peaks: dict = {}       # stem -> find_all result
_fixed: dict = {}       # stem -> boxes of the fixed model
_runs: dict = {}        # (stem, thresholds tuple, selfcal?) -> boxes
_gts: dict = {}
CHOSEN: dict = {}       # (cand, held place) -> {"setting": ..., "table": [...]}
INFO: dict = {}         # (cand, stem) -> the thresholds used


def frame_thresholds(found: dict, s: dict) -> tuple:
    """(orange lo, hi, s_lo, blue lo, hi, s_lo) for one frame from one finder's peaks and one setting."""
    out = []
    for c in (ORANGE, BLUE):
        lo, hi, s_lo = FIXED[c]
        p = found.get(c)
        if p is not None and p.n_sel >= s["n_min"] and lo - s["cap"] <= p.hue <= hi + s["cap"]:
            half = (hi - lo) / 2 + s["pad"]
            nlo, nhi = p.hue - half, p.hue + half
            if s["mode"] == "union":
                nlo, nhi = min(lo, nlo), max(hi, nhi)
            ns = s_lo
            if c == BLUE and s["s_follow"]:
                ns = float(min(s_lo, max(S_FLOOR_MIN, S_FOLLOW * p.s)))
            lo, hi, s_lo = nlo, nhi, ns
        out += [float(lo), float(hi), float(s_lo)]
    return tuple(out)


def model_of(th: tuple) -> pl.Model:
    boxes = dict(MODEL.boxes)
    for i, c in enumerate((ORANGE, BLUE)):
        lo, hi, s_lo = th[3 * i:3 * i + 3]
        sh = pl.HUE_SHIFT[c]
        boxes[c] = bf.Box((lo + sh, s_lo), (hi + sh, 255.0))
    return dataclasses.replace(MODEL, boxes=boxes)


FIXED_TH = tuple(x for c in (ORANGE, BLUE) for x in FIXED[c])


def peaks_of(stem, frame):
    if stem not in _peaks:
        _peaks[stem] = pk.find_all(frame.bgr)
    return _peaks[stem]


_sc = None


def selfcal_run(model, frame):
    global _sc
    import selfcal_copy as sc
    return sc.SelfCal(model, sc.SelfCalConfig(), CAM).run(frame).boxes


def boxes_for(stem, frame, th: tuple, selfcal: bool = False):
    key = (stem, th, selfcal)
    if key not in _runs:
        if th == FIXED_TH and not selfcal:
            if stem not in _fixed:
                _fixed[stem] = det.detect(pl.segment(frame, MODEL)[0], DET, CAM)
            _runs[key] = _fixed[stem]
        elif selfcal:
            _runs[key] = selfcal_run(model_of(th), frame)
        else:
            _runs[key] = det.detect(pl.segment(frame, model_of(th))[0], DET, CAM)
    return _runs[key]


def run_cand(cand: str, s: dict | None, stem: str, frame) -> list:
    if s is None:
        th = FIXED_TH
    else:
        th = frame_thresholds(peaks_of(stem, frame)[FINDER[cand]], s)
    INFO[(cand, stem)] = th
    return boxes_for(stem, frame, th, selfcal=(cand == "P5"))


def gts(stem):
    if stem not in _gts:
        g, clean = ct.load_gts([stem])
        _gts[stem] = (g[stem], clean[stem])
    return _gts[stem]


def tally(boxes_of, stems, placements):
    counts = {s: ct.classify_frame(s, boxes_of(s), gts(s)[0], gts(s)[1]) for s in stems}
    return ct.tally(counts, stems, placements)


def choose(cand: str, train_stems: list[str]):
    """The setting for one fold, from the training places only (P5 uses P1's choice: it is P1's ranges plus selfcal).

    Every setting and the fixed detector are counted on the training frames as the judge counts. A setting is out if,
    against the fixed detector on those frames, it would fail one of the judge's clauses other than "found better":
    boxes that are not on their barrel up by more than 1.85, any more box on a clean empty frame, boxes on cluttered
    empty frames up by more than 1.0, or found at one training place down by more than that place's margin. Of the
    rest the one that finds the most placements wins; a tie keeps the earlier (more careful) one. If none is left
    or none finds more than the fixed detector, the fold uses the fixed ranges (None)."""
    m = jg.load_margins()
    prepare(cand, train_stems)
    placements = ct.build_placements({st: gts(st)[0] for st in train_stems})
    by_place: dict = {}
    for st in train_stems:
        by_place.setdefault(ct.place_of(st), []).append(st)

    def boxes_of_setting(s):
        return lambda st: _runs[(st, FIXED_TH if s is None else frame_thresholds(_peaks[st][FINDER[cand]], s), cand == "P5")]

    base_f = boxes_of_setting(None)
    base = tally(base_f, train_stems, placements)
    base_pl = {p: tally(base_f, ss, placements).found_w for p, ss in by_place.items()}
    best, table = None, []
    for s in GRID:
        f = boxes_of_setting(s)
        t = tally(f, train_stems, placements)
        drops = {p: base_pl[p] - tally(f, ss, placements).found_w for p, ss in by_place.items()}
        ok = (t.extra_w - base.extra_w <= m.extra_rise + jg.EPS and t.clean_empty - base.clean_empty <= m.clean_empty + jg.EPS
              and t.cluttered_empty_w - base.cluttered_empty_w <= m.cluttered_empty + jg.EPS
              and all(d <= m.for_place(p) + jg.EPS for p, d in drops.items()))
        table.append({**s, "found_w": round(t.found_w, 2), "extra_w": round(t.extra_w, 2), "clean_empty": t.clean_empty,
                      "cluttered_empty_w": round(t.cluttered_empty_w, 2), "worst_place_drop": round(max(drops.values()), 2),
                      "allowed": bool(ok)})
        if ok and t.found_w > base.found_w + jg.EPS and (best is None or t.found_w > best[1] + jg.EPS):
            best = (s, t.found_w)
    table.append({"fixed": True, "found_w": round(base.found_w, 2), "extra_w": round(base.extra_w, 2),
                  "clean_empty": base.clean_empty, "cluttered_empty_w": round(base.cluttered_empty_w, 2)})
    return (best[0] if best else None), table


def prepare(cand: str, stems) -> None:
    """Every setting of the grid (and the fixed ranges) on every frame, each image read once and dropped."""
    for st in stems:
        need = st not in _peaks or (st, FIXED_TH, False) not in _runs
        if not need:
            ths = {frame_thresholds(_peaks[st][FINDER[cand]], s) for s in GRID}
            need = any((st, th, cand == "P5") not in _runs for th in ths)
        if not need:
            continue
        fr = jg.load_frame(st)
        peaks_of(st, fr)
        boxes_for(st, fr, FIXED_TH)
        for s in GRID:
            boxes_for(st, fr, frame_thresholds(_peaks[st][FINDER[cand]], s), selfcal=(cand == "P5"))


def make_fit(cand: str):
    def fit(train_stems: list[str], held_place: str):
        src = "P1" if cand == "P5" else cand
        if (src, held_place) not in CHOSEN:
            s, table = choose(src, list(train_stems))
            CHOSEN[(src, held_place)] = {"setting": s, "table": table}
        s = CHOSEN[(src, held_place)]["setting"]
        if cand == "P5":
            CHOSEN[(cand, held_place)] = {"setting": s, "table": "P1's"}

        def detect(stem: str, frame) -> list:
            if cand == "P5":
                th = FIXED_TH if s is None else frame_thresholds(peaks_of(stem, frame)[FINDER[cand]], s)
                INFO[(cand, stem)] = th
                return boxes_for(stem, frame, th, selfcal=True)
            return run_cand(cand, s, stem, frame)
        detect.describe = f"{cand} with {s}, picked without {held_place}"
        return detect
    fit.describe = f"peaks {cand} ({FINDER[cand]}): {len(GRID)} settings, one picked per fold on the other places"
    fit.__name__ = f"fit_{cand}"
    return fit


fit_P0 = make_fit("P0")
fit_P1 = make_fit("P1")
fit_P2 = make_fit("P2")
fit_P3 = make_fit("P3")
fit_P5 = make_fit("P5")


def detect_S0(stem: str, frame) -> list:
    """Report only: selfcal AB with its own defaults on the fixed ranges."""
    return boxes_for(stem, frame, FIXED_TH, selfcal=True)


detect_S0.describe = "selfcal AB (wip/exp-selfcal 690ae91, its defaults) on the fixed ranges"


def detect_P1_with(setting: dict):
    """P1 with one fixed setting (no fold): an importable callable for the best candidate."""
    def detect_frame(stem: str, frame) -> list:
        return run_cand("P1", setting, stem, frame)
    detect_frame.describe = f"P1 with {setting}"
    return detect_frame
