"""Is there a relation between a frame's own hue x saturation histogram and the right thresholds? (TODO F,
2026-11-18.) An analysis helper like ``hshist``: nothing here feeds ``pipeline`` or ``detector``.

How the data flows (the script is ``experiments/2026-11-18_hs_relation/run.py``, the plan its PREREG.md):

1. ``group_conditions``  train stems -> conditions. A condition is one table under one light, the
   ``{light}_{surface}`` part of the frame name; each is ``ordinary``, ``extreme`` (parked: the orange wood table
   under a lamp, the black table with its glare) or ``excluded`` (lamp brightness 1). The condition, not the
   frame, is the unit of evidence: frames of one condition share the light.
2. ``gated_hist`` / ``frame_features``  the features, from the frame alone (no label): the H x S histogram of
   the pixels below the horizon row with V >= 40, and nine numbers read off it (``FEATURES``). Two of them
   compare the frame with a ``Reference`` (the pooled home histogram).
3. ``thresholds_of`` / ``model_from_thresholds`` / ``load_hs_label``  the six thresholds (``THRESHOLDS``) as a
   flat dict in real OpenCV hue (orange's low end may be negative: -3 = 177), to and from a ``pipeline.Model``
   and from a slider label file.
4. ``spearman`` / ``perm_pvalue`` / ``holm``  is there a relation: rank correlation, its permutation p-value
   (every permutation when n <= 8), and the Holm correction over a family of pairs.
5. ``loco`` / ``loco_optimistic``  does it predict: leave one condition out, fit a line (or a plane on two
   features) on the others, predict the one left out. The feature is chosen **inside** the loop, by a second
   leave-one-out over the training conditions only (``select_features``); choosing it on all conditions first
   (``loco_optimistic``) lets the held-out condition vote for its own predictor, and reads too good.
"""
from __future__ import annotations

import itertools
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import boxfit as bf
from . import hshist as hh
from . import pipeline as pl
from .io import BLUE, ORANGE, parse_name

THRESHOLDS = ("orange_h_lo", "orange_h_hi", "orange_s_lo", "blue_h_lo", "blue_h_hi", "blue_s_lo")
COLOR_OF = {"orange": ORANGE, "blue": BLUE}

# ---- features (pre-registered 2026-11-18; the reason for each is in PREREG.md)
FEATURES = ("v_mean", "s_median", "s_share100", "blue_peak_h", "blue_s_p90", "orange_peak_h", "orange_s_p90",
            "ref_hue_shift", "ref_s_scale")
WINDOWS = {"blue": (85, 125), "orange": (-10, 30)}      # wide hue windows, real OpenCV hue, both ends included
S_COLOR = 40            # a pixel under this saturation has no usable hue: left out of the windows and of the alignment
S_HIGH = 100            # ``s_share100``
MIN_WINDOW_PX = 200     # fewer pixels than this in a window (or in the alignment) -> the feature is nan for the frame
SHIFT_MAX = 20          # the hue offset against the reference is searched in -20 .. +20
S_QUANTILES = tuple(range(10, 100, 10))
# the pairs with a physical reason, tested as their own small family (12 pairs)
PRIMARY = {"orange_h_lo": ("orange_peak_h", "ref_hue_shift"), "orange_h_hi": ("orange_peak_h", "ref_hue_shift"),
           "orange_s_lo": ("orange_s_p90", "ref_s_scale"),
           "blue_h_lo": ("blue_peak_h", "ref_hue_shift"), "blue_h_hi": ("blue_peak_h", "ref_hue_shift"),
           "blue_s_lo": ("blue_s_p90", "ref_s_scale")}

# ---- conditions
ORDINARY, EXTREME, EXCLUDED = "ordinary", "extreme", "excluded"
EXTREME_KEYS = ("window_black",)        # the black table under window light: glare (parked 2026-11-18)
REF_CONDITION = "window_light"          # home, white table: the frames the adopted model was fit on
_DIM_LAMP = re.compile(r"^lamp[a-z]+1$")


def condition_key(stem: str) -> str:
    """``{light}_{surface}`` of a frame name."""
    t = parse_name(stem)
    return f"{t['light']}_{t['surface']}"


def classify(key: str) -> str:
    """ordinary / extreme / excluded for a condition key. Lamp brightness 1 is excluded everywhere; a lamp on the
    (orange) wood table and the keys in ``EXTREME_KEYS`` are extreme; anything else, so every new condition, is
    ordinary until it is listed here."""
    light, surface = key.split("_")
    if _DIM_LAMP.match(light):
        return EXCLUDED
    if (light.startswith("lamp") and surface == "wood") or key in EXTREME_KEYS:
        return EXTREME
    return ORDINARY


def group_conditions(stems, test=()) -> dict[str, dict]:
    """{key: {"class": ..., "stems": [...]}}, ordinary conditions first, then extreme, then excluded, each
    alphabetical. Raises ValueError when a stem is a test frame: nothing downstream may see one."""
    bad = sorted(set(stems) & set(test))
    if bad:
        raise ValueError(f"{len(bad)} test frame(s) among the stems ({', '.join(bad[:3])}): test frames are never opened here")
    out: dict[str, dict] = {}
    for s in sorted(set(stems)):
        k = condition_key(s)
        out.setdefault(k, {"class": classify(k), "stems": []})["stems"].append(s)
    order = (ORDINARY, EXTREME, EXCLUDED)
    return {k: out[k] for k in sorted(out, key=lambda k: (order.index(out[k]["class"]), k))}


# ---------------------------------------------------------------- features from the frame alone

def gated_hist(bgr: np.ndarray, horizon_row: int = 50, v_min: int = 40) -> tuple[np.ndarray, float]:
    """(counts [180 rolled hue, 128 S bins], mean V) of the pixels below ``horizon_row`` with V >= ``v_min``:
    the pixels the color model may label. No label is used."""
    h, s, v = hh.planes(bgr)
    sel = v >= v_min
    sel[: max(0, horizon_row)] = False
    hist = hh.fine_hist(h, s, v, sel).sum(2)
    return hist, (float(v[sel].mean()) if sel.any() else float("nan"))


_S_CENTERS = np.arange(hh.NS) * 2.0 + 1


def _hue_profile(hist: np.ndarray) -> np.ndarray | None:
    """The hue distribution of the colored pixels (S >= S_COLOR), smoothed over +-2 around the circle, sum 1."""
    m = hist[:, S_COLOR // 2:].sum(1).astype(float)
    if m.sum() < MIN_WINDOW_PX:
        return None
    m = sum(np.roll(m, k) for k in range(-2, 3))
    return m / m.sum()


def _s_quantiles(hist: np.ndarray) -> np.ndarray | None:
    c = hist[:, S_COLOR // 2:].sum(0)
    if c.sum() < MIN_WINDOW_PX:
        return None
    return np.array(hh.wpct(c, _S_CENTERS[S_COLOR // 2:], S_QUANTILES))


@dataclass
class Reference:
    """What a frame is aligned against: the pooled histogram of the reference condition (home)."""
    hue_profile: np.ndarray
    s_quantiles: np.ndarray

    @classmethod
    def from_hists(cls, hists) -> "Reference":
        tot = np.sum(list(hists), axis=0)
        hp, sq = _hue_profile(tot), _s_quantiles(tot)
        if hp is None or sq is None:
            raise ValueError("the reference frames hold too few colored pixels")
        return cls(hp, sq)


def hue_shift(profile: np.ndarray, ref: np.ndarray) -> float:
    """The whole-histogram hue offset d (in -SHIFT_MAX .. SHIFT_MAX) for which the reference profile moved by d
    correlates best with the frame's: positive = the frame's hues sit above the reference's. Ties go to the
    smaller |d|."""
    best, best_d = -np.inf, 0
    for d in sorted(range(-SHIFT_MAX, SHIFT_MAX + 1), key=abs):
        r = float(np.corrcoef(np.roll(ref, d), profile)[0, 1])
        if r > best + 1e-12:
            best, best_d = r, d
    return float(best_d)


def window_stats(hist: np.ndarray, lo: int, hi: int) -> tuple[float, float]:
    """(peak hue, 90th percentile of S) of the pixels with hue in lo..hi (real OpenCV hue) and S >= S_COLOR;
    (nan, nan) when the window holds fewer than MIN_WINDOW_PX pixels."""
    w = hist[lo + hh.ROLL: hi + hh.ROLL + 1, S_COLOR // 2:]
    if w.sum() < MIN_WINDOW_PX:
        return float("nan"), float("nan")
    m = np.convolve(w.sum(1).astype(float), [1, 2, 3, 2, 1], "same")      # smoothed with a peaked kernel: a lone spike stays where it is
    return float(lo + int(np.argmax(m))), hh.wpct(w.sum(0), _S_CENTERS[S_COLOR // 2:], (90,))[0]


def frame_features(hist: np.ndarray, v_mean: float, ref: Reference | None) -> dict[str, float]:
    """The nine pre-registered features of one frame (``FEATURES``), from ``gated_hist`` output. With
    ``ref=None`` the two that compare the frame with the reference (``ref_*``) are nan: what the adaptive
    color rule (``adaptive.py``) uses, so that the pipeline needs nothing but the frame."""
    n = hist.sum()
    nan = float("nan")
    f = {k: nan for k in FEATURES}
    if n == 0:
        return f
    f["v_mean"] = v_mean
    f["s_median"] = hh.wpct(hist.sum(0), _S_CENTERS, (50,))[0]
    f["s_share100"] = float(hist[:, S_HIGH // 2:].sum() / n)
    for name, (lo, hi) in WINDOWS.items():
        f[f"{name}_peak_h"], f[f"{name}_s_p90"] = window_stats(hist, lo, hi)
    if ref is None:
        return f
    hp, sq = _hue_profile(hist), _s_quantiles(hist)
    if hp is not None:
        f["ref_hue_shift"] = hue_shift(hp, ref.hue_profile)
    if sq is not None:
        f["ref_s_scale"] = float(np.median(sq / ref.s_quantiles))
    return f


# ---------------------------------------------------------------- the six thresholds

def thresholds_of(model: pl.Model) -> dict[str, float]:
    """The six thresholds of an hs model, real OpenCV hue."""
    out = {}
    for name, c in COLOR_OF.items():
        b = model.boxes[c]
        out[f"{name}_h_lo"] = float(b.lo[0] - pl.HUE_SHIFT[c])
        out[f"{name}_h_hi"] = float(b.hi[0] - pl.HUE_SHIFT[c])
        out[f"{name}_s_lo"] = float(b.lo[1])
    return out


def model_from_thresholds(base: pl.Model, th: dict[str, float]) -> tuple[pl.Model, list[str]]:
    """``base`` with the two class boxes replaced by the six thresholds (as the ceiling check does). A color whose
    numbers are missing, not finite or not a range (h_lo >= h_hi) keeps the base box; those colors are returned.
    S floors are clipped to 0..255, hues to the range the model can represent."""
    import dataclasses
    boxes, kept = dict(base.boxes), []
    for name, c in COLOR_OF.items():
        v = [th.get(f"{name}_{k}", float("nan")) for k in ("h_lo", "h_hi", "s_lo")]
        if not all(np.isfinite(v)):
            kept.append(name); continue
        sh = pl.HUE_SHIFT[c]
        h_lo, h_hi = (float(np.clip(x, -sh, 179 - sh)) for x in v[:2])
        if h_lo >= h_hi:
            kept.append(name); continue
        boxes[c] = bf.Box((h_lo + sh, float(np.clip(v[2], 0, 255))), (h_hi + sh, 255.0))
    return dataclasses.replace(base, boxes=boxes), kept


def load_hs_label(path: Path | str) -> dict[str, float]:
    """A slider label ``<stem>_hs.json`` (version 1) as the flat six-threshold dict. Local reader: the loader
    ``io.load_hs`` is on the slider-tool branch; switch to it at merge."""
    d = json.loads(Path(path).read_text())
    if d.get("version") != 1:
        raise ValueError(f"{path}: hs label version {d.get('version')!r}, expected 1")
    out = {}
    for name in COLOR_OF:
        for k in ("h_lo", "h_hi", "s_lo"):
            out[f"{name}_{k}"] = float(d[name][k])
    return out


# ---------------------------------------------------------------- is there a relation

def rankdata(x) -> np.ndarray:
    """Ranks 1..n, ties get the mean of their ranks."""
    x = np.asarray(x, float)
    order = np.argsort(x, kind="stable")
    ranks = np.empty(len(x))
    ranks[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    return ranks


def _corr_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pearson correlation of every row of ``a`` [m, n] with ``b`` [n]."""
    a = a - a.mean(1, keepdims=True)
    b = b - b.mean()
    den = np.sqrt((a * a).sum(1) * (b * b).sum())
    with np.errstate(invalid="ignore", divide="ignore"):
        return (a @ b) / den


def spearman(x, y) -> float:
    """Spearman rank correlation; nan with fewer than 3 points or when either side is constant."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(_corr_rows(rankdata(x)[None], rankdata(y))[0])


def perm_pvalue(x, y, n_perm: int = 20000, seed: int = 0, exact_max: int = 8) -> dict:
    """Two-sided permutation p-value of the Spearman correlation: the share of re-pairings of x with y whose
    |rho| is at least the observed one. n <= ``exact_max``: every one of the n! permutations (so the smallest
    possible p is 2 / n!: 0.33 at n = 3, 0.083 at n = 4, 0.017 at n = 5). Larger n: ``n_perm`` random
    permutations, p = (1 + hits) / (1 + n_perm). Returns rho, p, n, perms, exact."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    rho = spearman(x, y)
    if rho != rho:
        return {"rho": rho, "p": float("nan"), "n": n, "perms": 0, "exact": False}
    rx, ry = rankdata(x), rankdata(y)
    if n <= exact_max:
        perms = np.array(list(itertools.permutations(ry)))
        r = _corr_rows(perms, rx)
        return {"rho": rho, "p": float((np.abs(r) >= abs(rho) - 1e-12).mean()), "n": n, "perms": len(perms), "exact": True}
    rng = np.random.default_rng(seed)
    perms = rng.permuted(np.tile(ry, (n_perm, 1)), axis=1)
    hits = int((np.abs(_corr_rows(perms, rx)) >= abs(rho) - 1e-12).sum())
    return {"rho": rho, "p": (1 + hits) / (1 + n_perm), "n": n, "perms": n_perm, "exact": False}


def holm(pvals) -> np.ndarray:
    """Holm's step-down correction over a family of p-values; nan entries are not part of the family."""
    p = np.asarray(pvals, float)
    out = np.full(p.shape, np.nan)
    idx = np.flatnonzero(np.isfinite(p))
    m = len(idx)
    run = 0.0
    for rank, i in enumerate(idx[np.argsort(p[idx], kind="stable")]):
        run = max(run, min(1.0, (m - rank) * p[i]))
        out[i] = run
    return out


# ---------------------------------------------------------------- does it predict

def fit_predict(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
    """Least-squares line / plane with an intercept, fit on the training rows, evaluated on ``x_test`` [m, k].
    When the fit is not determined (too few rows, or the columns do not span) the answer is the training mean."""
    x_train, x_test = np.atleast_2d(x_train), np.atleast_2d(x_test)
    a = np.column_stack([np.ones(len(x_train)), x_train])
    if len(x_train) < a.shape[1] or np.linalg.matrix_rank(a) < a.shape[1]:
        return np.full(len(x_test), float(np.mean(y_train)))
    coef = np.linalg.lstsq(a, y_train, rcond=None)[0]
    return np.column_stack([np.ones(len(x_test)), x_test]) @ coef


def _held_sets(n: int, groups) -> list[np.ndarray]:
    """The rows held out together: one row at a time (``groups`` None), or every row of one group (leave one
    group out; a group = a place, all conditions that share a table and a room)."""
    if groups is None:
        return [np.arange(n) == i for i in range(n)]
    g = np.asarray(groups, object)
    return [g == v for v in dict.fromkeys(g.tolist())]


def n_groups(n: int, groups) -> int:
    return n if groups is None else len(set(np.asarray(groups, object).tolist()))


def loo_error(x: np.ndarray, y: np.ndarray, feats: tuple[int, ...], groups=None) -> float:
    """Mean |error| of leave-one-out predictions with the given feature columns. With ``groups``: leave one
    group out, every row of the held-out group predicted from the other groups; the mean is over rows."""
    n = len(y)
    err = []
    for held in _held_sets(n, groups):
        tr = ~held
        err.extend(np.abs(fit_predict(x[tr][:, feats], y[tr], x[held][:, feats]) - y[held]).tolist())
    return float(np.mean(err))


def select_features(x: np.ndarray, y: np.ndarray, max_features: int = 1, usable=None, groups=None) -> tuple[int, ...] | None:
    """The feature set (one column, or up to ``max_features``) with the smallest leave-one-out error **over
    these rows only** (leave one group out when ``groups`` is given). A column is a candidate when it is finite
    and not constant here (and listed in ``usable`` when given); a set of k columns needs at least k + 2 rows
    (groups), so every inner fit has a determined line. A pair is taken only when its error is below the best
    single column's. None when there is no candidate."""
    n, m = x.shape
    ng = n_groups(n, groups)
    cols = [j for j in (range(m) if usable is None else usable) if np.isfinite(x[:, j]).all() and np.ptp(x[:, j]) > 0]
    best, best_err = None, np.inf
    for k in range(1, max_features + 1):
        if ng < k + 2:
            break
        for feats in itertools.combinations(cols, k):
            e = loo_error(x, y, feats, groups)
            if e < best_err - 1e-12:
                best, best_err = feats, e
    return best


def loco(x: np.ndarray, y: np.ndarray, max_features: int = 1, groups=None) -> list[dict]:
    """Leave one condition out, nested (``groups`` given: leave one GROUP out, e.g. one place, nested the same
    way). For each held-out set: choose the feature(s) on the other rows only (``select_features``, by the same
    kind of hold-out), fit on the other rows, predict the held-out rows. A column that is nan for a held-out row
    is not a candidate for it. With no candidate (too few conditions / places) the prediction falls back to the
    mean of the others and ``fallback`` is True. Returns one dict per row: pred, feats, fallback."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(y)
    out: list[dict | None] = [None] * n
    g_arr = None if groups is None else np.asarray(groups, object)
    for held in _held_sets(n, groups):
        tr = ~held
        g_tr = None if g_arr is None else g_arr[tr]
        for i in np.flatnonzero(held):
            usable = [j for j in range(x.shape[1]) if np.isfinite(x[i, j])]
            feats = select_features(x[tr], y[tr], max_features, usable, g_tr) if tr.sum() else None
            if feats is None:
                out[i] = {"pred": float(np.mean(y[tr])) if tr.sum() else float("nan"), "feats": (), "fallback": True}
            else:
                out[i] = {"pred": float(fit_predict(x[tr][:, feats], y[tr], x[i:i + 1][:, feats])[0]), "feats": feats, "fallback": False}
    return out


def loco_optimistic(x: np.ndarray, y: np.ndarray, max_features: int = 1, groups=None) -> tuple[list[float], tuple[int, ...]]:
    """The WRONG way, kept to show the size of the mistake: the feature is chosen once on all conditions, then
    each is predicted leave-one-out (one group out with ``groups``). The held-out rows helped choose their own
    predictor."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    feats = select_features(x, y, max_features, groups=groups)
    n = len(y)
    out = [float("nan")] * n
    for held in _held_sets(n, groups):
        tr = ~held
        for i in np.flatnonzero(held):
            if feats is None:
                out[i] = float(np.mean(y[tr])) if tr.sum() else float("nan")
            else:
                out[i] = float(fit_predict(x[tr][:, feats], y[tr], x[i:i + 1][:, feats])[0])
    return out, (feats or ())
