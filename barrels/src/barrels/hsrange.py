"""The feasible RANGE of each of the six hs thresholds on one frame, judged against the hand-drawn boxes
(2026-11-24 range experiment; the plan: ``experiments/2026-11-24_adaptive_range/PREREG.md``). Also the slider
tool's computed proposal. An analysis / labeling helper like ``hsrel``: nothing here feeds ``pipeline`` or
``detector``; it only calls them.

Why ranges: a frame does not have one right threshold. Tanush's slider value is one point inside a run of values
that work equally well (2026-11-23), so the target of any prediction is the run, not the point.

How it works, in order:

1. ``FrameEval``  one frame, its hand-drawn boxes and the adopted model. ``evaluate(T)`` segments the frame with the
   six numbers T (``pipeline.segment``, the adopted gates), runs today's detector and scores its boxes against HIS
   boxes (v2 rule): which of his barrels are found, how many false boxes, and two pixel counts per color: the share
   of the CORES of his boxes of that color painted (a core is the box minus 15 % at each side: the corners hold
   table), and the pixels painted OUTSIDE his boxes (each padded by 4 px).
2. ``works``  is a setting as good as the anchor (his values)? Detector version: every barrel found at the anchor is
   still found, no more false boxes, and the outside paint grows by at most max(150 px, 10 %). Pixel version: the
   core share drops by at most 5 points, same outside clause.
3. ``sweep``  one threshold at a time, the others at the anchor: step away from the anchor until a value stops
   working; the range is the run of working values around the anchor, each end with the reason it stopped.
4. ``joint_check``  the box made of the six ranges, tried with all six moved at once (its corners and random points
   inside), shrunk toward the anchor until it holds.
5. ``net_optimum`` / ``propose``  the slider tool's computed proposal from the frame and the boxes alone: the setting
   that paints the most barrel pixels minus outside pixels (Tanush's rule: stop where the paint outside climbs
   faster than the paint on the barrels), then the middle of the detector ranges around it.
"""
from __future__ import annotations

import hashlib
import itertools
import math
from dataclasses import dataclass, field

import numpy as np

from . import detect_types as dtp
from . import detector as det
from . import eval_det as ed
from . import geometry as geo
from . import hslabel as hl
from . import hsrel as hr
from . import pipeline as pl
from .io import BLUE, ORANGE

THRESHOLDS = hr.THRESHOLDS
CLASS_NAMES = ("orange", "blue")
CLASS_ID = {"orange": ORANGE, "blue": BLUE}
# the slider tool's limits (tools/hs_slider.py SLIDERS): a sweep that reaches one marks the end "open"
LIMITS = {"orange_h_lo": (-30, 60), "orange_h_hi": (-30, 60), "orange_s_lo": (0, 255),
          "blue_h_lo": (60, 150), "blue_h_hi": (60, 150), "blue_s_lo": (0, 255)}
STEPS = {t: (2 if t.endswith("s_lo") else 1) for t in THRESHOLDS}      # PREREG: 1 hue unit, 2 S units
PARTNER = {"orange_h_lo": "orange_h_hi", "orange_h_hi": "orange_h_lo", "blue_h_lo": "blue_h_hi", "blue_h_hi": "blue_h_lo"}
CORE_FRAC = 0.15        # the core: the box minus this share of its width at each side and of its height at top and bottom
PAD = 4                 # the boxes are padded by this many px before "outside" starts
OUT_MIN_PX = 150        # outside paint may grow by max(OUT_MIN_PX, OUT_REL * the anchor's)
OUT_REL = 0.10
CORE_DROP = 0.05        # pixel version: the core share may drop by this much
DET, PIX = "det", "pix"
OPEN, OTHER_END = "open", "other end"
LOST, FALSE, OUTSIDE, CORE, EMPTY = "barrel lost", "false box", "outside paint", "core paint", "empty sector"
SHRINKS = (1.0, 0.75, 0.5, 0.25)
JOINT_RANDOM, JOINT_MIN_SHARE = 64, 0.9
NET_WEIGHTS = (1.0, 0.5, 0.25, 0.1)     # the proposal tries the net optimum with these weights on outside paint


# ---------------------------------------------------------------- six numbers: flat <-> nested

def flat(thr: dict) -> dict[str, int]:
    """{'orange': {'h_lo': ..}, 'blue': {..}} -> {'orange_h_lo': .., ...}; a flat dict is returned as a copy."""
    if "orange_h_lo" in thr:
        return {t: int(thr[t]) for t in THRESHOLDS}
    return {f"{c}_{k}": int(thr[c][k]) for c in CLASS_NAMES for k in ("h_lo", "h_hi", "s_lo")}


def nested(thr: dict) -> dict:
    """The inverse of ``flat`` (the form ``hslabel`` and the label files use)."""
    f = flat(thr)
    return {c: {k: f[f"{c}_{k}"] for k in ("h_lo", "h_hi", "s_lo")} for c in CLASS_NAMES}


def key(thr: dict) -> tuple:
    f = flat(thr)
    return tuple(f[t] for t in THRESHOLDS)


def valid(thr: dict) -> bool:
    f = flat(thr)
    return all(f[f"{c}_h_lo"] <= f[f"{c}_h_hi"] for c in CLASS_NAMES)


# ---------------------------------------------------------------- 1. one frame

@dataclass(frozen=True)
class Outcome:
    found: frozenset            # indices of his boxes matched by a detector box (v2)
    n_false: int                # detector boxes matching none of his
    core: dict                  # class name -> share of the cores of his boxes of that color painted that color (nan: no such box)
    out: dict                   # class name -> pixels painted that color outside his (padded) boxes
    n_boxes: int = 0            # detector boxes drawn
    empty: bool = False         # the setting has an empty hue sector: it cannot be run


def regions(shape, boxes, row0: int, core_frac: float = CORE_FRAC, pad: int = PAD) -> tuple[dict, np.ndarray, np.ndarray]:
    """(core mask per class name, all-cores mask, outside mask) for his boxes, rows >= ``row0`` only."""
    h, w = shape[:2]
    core = {c: np.zeros((h, w), bool) for c in CLASS_NAMES}
    near = np.zeros((h, w), bool)
    for b in boxes:
        x0, y0, x1, y1 = (int(v) for v in b["bbox"])
        dx, dy = int(round(core_frac * (x1 - x0))), int(round(core_frac * (y1 - y0)))
        if b["color"] in core:
            core[b["color"]][max(0, y0 + dy):max(0, y1 - dy), max(0, x0 + dx):max(0, x1 - dx)] = True
        near[max(0, y0 - pad):min(h, y1 + pad), max(0, x0 - pad):min(w, x1 + pad)] = True
    outside = ~near
    for m in (*core.values(), outside):
        m[:max(0, row0)] = False
    return core, core["orange"] | core["blue"], outside


class FrameEval:
    """One frame with his boxes: ``evaluate(T)`` -> ``Outcome``. Results are cached per setting, the detector per
    distinct mask. ``label`` is a box label dict (``io.load_boxes``): its ``barrels`` and ``clean``."""

    def __init__(self, bgr: np.ndarray, label: dict, base: pl.Model, det_cfg=None, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
                 stem: str = "frame"):
        self.frame, self.base, self.cam, self.stem = pl.Frame.from_image(bgr), base, cam, stem
        self.det_cfg = det_cfg or det.DetConfig()
        self.boxes = list(label.get("barrels", []))
        self.clean = bool(label.get("clean", True))
        self.row0 = base.cfg.horizon_row or 0
        self.core, self.cores, self.outside = regions(bgr.shape, self.boxes, self.row0)
        self.gts = [b.with_ground(cam) for b in dtp.barrels_from_boxes({"barrels": self.boxes})]
        self._cache: dict[tuple, Outcome] = {}
        self._det: dict[bytes, tuple] = {}
        self.calls = 0

    def mask(self, thr: dict) -> np.ndarray:
        return pl.segment(self.frame, hl.model_from_thresholds(self.base, nested(thr)))[0]

    def evaluate(self, thr: dict, detect: bool = True) -> Outcome:
        k = (key(thr), detect)
        if k in self._cache:
            return self._cache[k]
        if not valid(thr):
            o = Outcome(frozenset(), 10 ** 6, {c: float("nan") for c in CLASS_NAMES}, {c: 10 ** 9 for c in CLASS_NAMES}, 0, True)
            self._cache[k] = o
            return o
        m = self.mask(thr)
        core = {c: (float((m[self.core[c]] == CLASS_ID[c]).mean()) if self.core[c].any() else float("nan")) for c in CLASS_NAMES}
        out = {c: int((m[self.outside] == CLASS_ID[c]).sum()) for c in CLASS_NAMES}
        found, n_false, n_boxes = frozenset(), 0, 0
        if detect:
            h = hashlib.blake2b(m.tobytes(), digest_size=16).digest()
            if h not in self._det:
                self.calls += 1
                preds = det.detect(m, self.det_cfg, self.cam)
                r = ed.evaluate_frame(self.stem, preds, self.gts, self.cam, rule="v2", clean=self.clean)
                self._det[h] = (frozenset(mm.gt_idx for mm in r.matches), int(sum(r.fp.values())), len(preds))
            found, n_false, n_boxes = self._det[h]
        o = Outcome(found, n_false, core, out, n_boxes)
        self._cache[k] = o
        return o


# ---------------------------------------------------------------- 2. does a setting work

def out_margin(ref_out: int) -> float:
    return max(OUT_MIN_PX, OUT_REL * ref_out)


def works(o: Outcome, ref: Outcome, kind: str = DET) -> str | None:
    """None when ``o`` is as good as the anchor's ``ref`` (PREREG part 1), else the first reason it is not."""
    if o.empty:
        return EMPTY
    if kind == DET:
        if not o.found >= ref.found:
            return LOST
        if o.n_false > ref.n_false:
            return FALSE
    else:
        for c in CLASS_NAMES:
            if math.isfinite(ref.core[c]) and o.core[c] < ref.core[c] - CORE_DROP:
                return CORE
    for c in CLASS_NAMES:
        if o.out[c] > ref.out[c] + out_margin(ref.out[c]):
            return OUTSIDE
    return None


# ---------------------------------------------------------------- 3. one threshold at a time

@dataclass
class Range:
    lo: int
    hi: int
    lo_why: str
    hi_why: str
    anchor: int

    @property
    def width(self) -> int:
        return self.hi - self.lo

    def contains(self, v: float) -> bool:
        return self.lo <= v <= self.hi

    def as_list(self) -> list[int]:
        return [int(self.lo), int(self.hi)]


def _walk(fe: FrameEval, anchor: dict, t: str, d: int, ref: Outcome, kind: str, step: int, coarse: int) -> tuple[int, str]:
    """From the anchor, step in direction d until a value fails; (last working value, why it stopped). With
    ``coarse`` > 1: jump by coarse * step until a failure, then go on from the last good value by step (faster;
    may skip a lone failing value between jumps)."""
    lim_lo, lim_hi = LIMITS[t]
    detect = kind == DET
    v = anchor[t]
    for st in ((coarse * step, step) if coarse > 1 else (step,)):
        while True:
            nv = v + d * st
            stop = None
            if d < 0 and nv < lim_lo:
                nv, stop = (lim_lo, None) if v > lim_lo else (v, OPEN)
            if d > 0 and nv > lim_hi:
                nv, stop = (lim_hi, None) if v < lim_hi else (v, OPEN)
            if stop is None and t in PARTNER:
                other = anchor[PARTNER[t]]
                if t.endswith("h_lo") and d > 0 and nv > other:
                    nv, stop = (other, None) if v < other else (v, OTHER_END)
                if t.endswith("h_hi") and d < 0 and nv < other:
                    nv, stop = (other, None) if v > other else (v, OTHER_END)
            if stop is not None:
                if st == step:
                    return v, stop
                break
            why = works(fe.evaluate({**anchor, t: nv}, detect), ref, kind)
            if why:
                if st == step:
                    return v, why
                break
            v = nv
    return v, OPEN      # not reached


def sweep(fe: FrameEval, anchor: dict, kind: str = DET, thresholds=THRESHOLDS, coarse: int = 1, steps: dict | None = None) -> dict[str, Range]:
    """The range of each threshold, one at a time, the others at the anchor (PREREG part 1)."""
    anchor = flat(anchor)
    ref = fe.evaluate(anchor, kind == DET)
    steps = steps or STEPS
    out = {}
    for t in thresholds:
        lo, lw = _walk(fe, anchor, t, -1, ref, kind, steps[t], coarse)
        hi, hw = _walk(fe, anchor, t, +1, ref, kind, steps[t], coarse)
        out[t] = Range(lo, hi, lw, hw, anchor[t])
    return out


# ---------------------------------------------------------------- 4. all six at once

def shrink(anchor: dict, ranges: dict[str, Range], s: float) -> dict[str, tuple[int, int]]:
    """Each range pulled toward the anchor by factor s (1 = as is, 0 = the anchor alone), whole numbers inside."""
    a = flat(anchor)
    return {t: (a[t] - int(math.floor(s * (a[t] - r.lo) + 1e-9)), a[t] + int(math.floor(s * (r.hi - a[t]) + 1e-9))) for t, r in ranges.items()}


def box_points(bounds: dict[str, tuple[int, int]], n_random: int = JOINT_RANDOM, seed: int = 0) -> tuple[list[dict], list[dict]]:
    """(the distinct corners, ``n_random`` uniform integer points) of a box of six ranges."""
    ts = list(bounds)
    corners = [dict(zip(ts, c)) for c in sorted(set(itertools.product(*[bounds[t] for t in ts])))]
    rng = np.random.default_rng(seed)
    rand = [{t: int(rng.integers(bounds[t][0], bounds[t][1] + 1)) for t in ts} for _ in range(n_random)]
    return corners, rand


@dataclass
class Joint:
    corner_share: float          # at s = 1
    random_share: float          # at s = 1
    confirmed: float             # the largest s whose box holds (all corners, >= 90 % random); 0 = the anchor alone
    tried: dict = field(default_factory=dict)       # s -> (corners working, corners, random working, random)


def joint_check(fe: FrameEval, anchor: dict, ranges: dict[str, Range], kind: str = DET, n_random: int = JOINT_RANDOM, seed: int = 0) -> Joint:
    anchor = flat(anchor)
    ref = fe.evaluate(anchor, kind == DET)
    ok = lambda p: works(fe.evaluate(p, kind == DET), ref, kind) is None  # noqa: E731
    j = Joint(float("nan"), float("nan"), 0.0)
    for s in SHRINKS:
        corners, rand = box_points(shrink(anchor, ranges, s), n_random, seed)
        if s == SHRINKS[0]:
            c_ok, r_ok = sum(map(ok, corners)), sum(map(ok, rand))
            j.corner_share, j.random_share = c_ok / len(corners), r_ok / len(rand)
        else:
            c_ok = 0
            for p in corners:                 # stop at the first failing corner: the box does not hold
                if not ok(p):
                    break
                c_ok += 1
            r_ok = sum(map(ok, rand)) if c_ok == len(corners) else 0
        j.tried[s] = (c_ok, len(corners), r_ok, len(rand))
        if c_ok == len(corners) and r_ok >= JOINT_MIN_SHARE * len(rand):
            j.confirmed = s
            break
    return j


# ---------------------------------------------------------------- 5. the computed proposal (slider tool)

def _hist(hs: np.ndarray, sel: np.ndarray) -> np.ndarray:
    h = hs[..., 0][sel].astype(int)
    s = hs[..., 1][sel].astype(int)
    out = np.zeros((180, 256), np.int64)
    np.add.at(out, (h, s), 1)
    return out


def _best_run(v: np.ndarray) -> tuple[float, int, int]:
    """Maximum-sum contiguous run of ``v``: (sum, first, last); an empty-gain row gives (0, -1, -1)."""
    best, cur, start, bi, bj = 0.0, 0.0, 0, -1, -1
    for i, x in enumerate(v):
        if cur <= 0:
            cur, start = x, i
        else:
            cur += x
        if cur > best:
            best, bi, bj = cur, start, i
    return best, bi, bj


def net_optimum(fe: FrameEval, adopted: dict, w_out: float = 1.0) -> dict[str, int]:
    """Per color the hue sector and S floor that maximise (pixels painted inside the cores of his boxes) minus
    ``w_out`` x (pixels painted outside his padded boxes), searched exactly over the slider ranges (the gates as
    the adopted model's). Cores of both colors count, so the other color's stripe counts for its color. A color
    with nothing to gain keeps the adopted values."""
    keep = (fe.frame.val >= fe.base.cfg.v_min)
    keep[:fe.row0] = False
    out = flat(adopted)
    for c in CLASS_NAMES:
        shift = pl.HUE_SHIFT[CLASS_ID[c]]
        hs = fe.frame.hs(shift)
        hin, hout = _hist(hs, keep & fe.cores), _hist(hs, keep & fe.outside)
        cum = lambda a: np.cumsum(a[:, ::-1], axis=1)[:, ::-1]  # noqa: E731  [h, s] = pixels with S >= s
        net = cum(hin) - w_out * cum(hout)
        lo, hi = LIMITS[f"{c}_h_lo"][0] + shift, LIMITS[f"{c}_h_hi"][1] + shift
        best = (0.0, None)
        for s in range(255, -1, -1):          # from the top: a tie keeps the higher floor (paints less)
            g, i, j = _best_run(net[lo:hi + 1, s])
            if g > best[0] + 1e-9:
                best = (g, (lo + i - shift, lo + j - shift, s))
        if best[1] is not None:
            out[f"{c}_h_lo"], out[f"{c}_h_hi"], out[f"{c}_s_lo"] = (int(x) for x in best[1])
    return out


@dataclass
class Proposal:
    thresholds: dict             # flat six numbers: where the sliders start
    anchor: dict                 # the setting the ranges were computed around
    ranges: dict                 # threshold -> Range (detector version)
    source: str                  # "middle of the ranges" | "net optimum" | "adopted"
    found: int = 0               # his barrels the detector finds with ``thresholds``
    n_boxes: int = 0             # his boxes on the frame


def propose(fe: FrameEval, adopted: dict, coarse: int = 4) -> Proposal:
    """The computed proposal for a frame with his boxes: anchor = among the net-pixel optima (outside weights
    ``NET_WEIGHTS``) and the adopted values, the one that finds the most of his barrels, then the fewest false
    boxes; ranges around the anchor (detector version, coarse-then-fine); proposal = the middle of each range, kept
    only when all six together work against the anchor, else the anchor. Uses the frame and his boxes only."""
    adopted = flat(adopted)
    cands = [(f"net optimum (outside weight {w:g})", net_optimum(fe, adopted, w)) for w in NET_WEIGHTS] + [("adopted", adopted)]
    # the most of his barrels found, then the fewest false boxes; ties keep the earlier (more careful) candidate
    src, anchor = max(cands, key=lambda c: (len(fe.evaluate(c[1]).found), -fe.evaluate(c[1]).n_false, -cands.index(c)))
    ranges = sweep(fe, anchor, DET, coarse=coarse)
    # the middle of a range that ran into a slider's end (or the other end of its sector) says nothing: there the anchor
    # (the net optimum, tight on the barrels) stays
    mid = {t: (anchor[t] if {r.lo_why, r.hi_why} & {OPEN, OTHER_END} else int(round((r.lo + r.hi) / 2))) for t, r in ranges.items()}
    for c in CLASS_NAMES:
        if mid[f"{c}_h_lo"] > mid[f"{c}_h_hi"]:
            mid[f"{c}_h_lo"], mid[f"{c}_h_hi"] = anchor[f"{c}_h_lo"], anchor[f"{c}_h_hi"]
    ref = fe.evaluate(anchor)
    if works(fe.evaluate(mid), ref, DET) is None:
        chosen, src = mid, "middle of the ranges"
    else:
        chosen, src = anchor, src + " (the middle did not work)"
    return Proposal(chosen, anchor, ranges, src, len(fe.evaluate(chosen).found), len(fe.boxes))


def ranges_dict(ranges: dict[str, Range]) -> dict:
    """{'orange': {'h_lo': [lo, hi], ...}, 'blue': {...}}: the form stored in a label's ``ranges``."""
    return {c: {k: ranges[f"{c}_{k}"].as_list() for k in ("h_lo", "h_hi", "s_lo") if f"{c}_{k}" in ranges} for c in CLASS_NAMES}


# ---------------------------------------------------------------- analysis helpers (part 2 and the rule R2)

def intersect(ranges: list[tuple[float, float]]) -> tuple[float, float, bool]:
    """(lo, hi, empty): the intersection of the ranges; when it is empty, the median of the lower ends to the median
    of the upper ends, flagged."""
    lo, hi = max(r[0] for r in ranges), min(r[1] for r in ranges)
    if lo <= hi:
        return float(lo), float(hi), False
    return float(np.median([r[0] for r in ranges])), float(np.median([r[1] for r in ranges])), True


def interval_slope(x, ranges, fixed: float, f_ref: float, max_delta: float, weights=None) -> tuple[float, float]:
    """(b, hits) for the line ``fixed + b (x - f_ref)``, clipped to +-max_delta: b puts the most rows inside their
    ranges (weighted); ties broken by weighted least squares to the range midpoints. Rows with a missing x are left
    out; b = 0 is always a candidate. Candidates: every b where a row's prediction meets a range end, the midpoints
    between neighbours, and 0."""
    x = np.asarray(x, float)
    w = np.ones(len(x)) if weights is None else np.asarray(weights, float)
    rows = [(xi - f_ref, r, wi) for xi, r, wi in zip(x, ranges, w) if np.isfinite(xi)]

    def pred(b, dx):
        return fixed + float(np.clip(b * dx, -max_delta, max_delta))

    def score(b):
        hits = sum(wi for dx, r, wi in rows if r[0] <= pred(b, dx) <= r[1])
        sq = sum(wi * (pred(b, dx) - (r[0] + r[1]) / 2) ** 2 for dx, r, wi in rows)
        return hits, sq

    cands = {0.0}
    for dx, r, _ in rows:
        if abs(dx) > 1e-12:
            cands |= {(r[0] - fixed) / dx, (r[1] - fixed) / dx}
    cs = sorted(cands)
    cands |= {(a + b) / 2 for a, b in zip(cs, cs[1:])}
    best = max(sorted(cands, key=abs), key=lambda b: (round(score(b)[0], 9), -score(b)[1]))
    return float(best), float(score(best)[0])


def hits_at(x, ranges, fixed: float, f_ref: float, b: float, max_delta: float = math.inf, weights=None) -> float:
    """Weighted number of rows whose prediction ``fixed + clip(b (x - f_ref))`` lies in their range (a missing x
    predicts ``fixed``)."""
    w = np.ones(len(ranges)) if weights is None else np.asarray(weights, float)
    tot = 0.0
    for xi, r, wi in zip(x, ranges, w):
        p = fixed + (float(np.clip(b * (xi - f_ref), -max_delta, max_delta)) if np.isfinite(xi) else 0.0)
        tot += wi * (r[0] <= p <= r[1])
    return float(tot)


# ---------------------------------------------------------------- one labelled frame, start to end (the experiment's worker)

def analyse_frame(stem: str, anchor: dict | None = None, labels_dir=None, raw_dir=None, joint: bool = True) -> dict:
    """Ranges (detector and pixel versions) and the joint check of one frame, anchored at its slider label (or at
    ``anchor``), as plain data. The CALLER checks that the stem is a train frame before calling this."""
    import cv2

    from . import io
    cv2.setNumThreads(1)
    base = hl.adopted_model()
    bgr = io.load_image(io.find_image(stem, raw_dir))
    fe = FrameEval(bgr, io.load_boxes(stem, labels_dir, check_image=False), base, stem=stem)
    meta = None
    if anchor is None:
        meta = io.load_hs(stem, labels_dir, check_image=False)
        anchor = meta
    a = flat(anchor)
    ref = fe.evaluate(a)
    out = {"stem": stem, "anchor": a, "n_boxes": len(fe.boxes), "found": len(ref.found), "false": ref.n_false,
           "core": ref.core, "out": ref.out, "proposed": bool(meta.get("proposed")) if meta else False,
           "moved": meta.get("moved") if meta else None, "proposed_by": meta.get("proposed_by") if meta else None}
    det_ranges = None
    for kind in (DET, PIX):
        r = sweep(fe, a, kind)
        out[kind] = {t: [x.lo, x.hi, x.lo_why, x.hi_why] for t, x in r.items()}
        if kind == DET:
            det_ranges = r
    if joint:
        j = joint_check(fe, a, det_ranges)
        out["joint"] = {"corner_share": j.corner_share, "random_share": j.random_share, "confirmed": j.confirmed,
                        "tried": {str(k): list(v) for k, v in j.tried.items()}}
        out["confirmed"] = {t: list(v) for t, v in shrink(a, det_ranges, j.confirmed).items()}
    out["detector_calls"] = fe.calls
    return out
