"""The adaptive color rule (2026-11-23, behind a switch; off by default; PREREG:
``experiments/2026-11-24_adaptive/PREREG.md``).

The hs color model has six numbers (per color a hue range and a saturation floor), fixed after one fit at home.
The adaptive rule moves some of them **per frame**, from that frame's own histogram, along a straight line
through the home point::

    threshold(frame) = fixed + b * (feature(frame) - f_home),   clipped to fixed +- max_delta

- ``fixed``: the model's own value (its fitted box), so a re-fit model (home leave-one-scene-out) adapts around
  its own numbers.
- ``feature``: one number read off the frame's hue x saturation histogram (the pixels below the horizon row with
  V >= v_min; ``hsrel.frame_features`` with no reference), e.g. ``blue_s_p90`` = how saturated the most
  saturated blue things in view are. A frame without a reading (fewer than 200 pixels in the window) keeps
  ``fixed`` for that threshold.
- ``f_home``: that feature's mean over the home train frames; at home the rule therefore gives the adopted model.
- ``b``: the only fitted number, fit on the slider labels (``fit_slope``: least squares through the home point,
  every place weighted equally).

What is never done: a pixel is never changed (no white balance, no image correction), and nothing is carried
from one frame to the next. The switch is ``pipeline.Config.hs_adapt``: a tuple of ``Term``s as plain tuples
``(threshold, feature, b, f_home, max_delta)``; empty = off (the default, and then the config hash is unchanged).
``pipeline.segment`` calls ``adapted_boxes`` when it is not empty.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import boxfit as bf
from . import hsrel as hr
from .io import BLUE, ORANGE

# threshold name -> (class, axis, end): axis 0 = shifted hue, 1 = S; end "lo" / "hi" of the box
SLOTS = {"orange_h_lo": (ORANGE, 0, "lo"), "orange_h_hi": (ORANGE, 0, "hi"), "orange_s_lo": (ORANGE, 1, "lo"),
         "blue_h_lo": (BLUE, 0, "lo"), "blue_h_hi": (BLUE, 0, "hi"), "blue_s_lo": (BLUE, 1, "lo")}
# features the rule may read: the ones that need nothing but the frame (no reference histogram)
FRAME_FEATURES = ("v_mean", "s_median", "s_share100", "blue_peak_h", "blue_s_p90", "orange_peak_h", "orange_s_p90")


@dataclass(frozen=True)
class Term:
    threshold: str      # one of SLOTS
    feature: str        # one of FRAME_FEATURES
    slope: float        # b
    f_ref: float        # f_home
    max_delta: float    # the threshold never moves further than this from the model's value

    def __post_init__(self):
        if self.threshold not in SLOTS:
            raise ValueError(f"unknown threshold {self.threshold!r} (one of {', '.join(SLOTS)})")
        if self.feature not in FRAME_FEATURES:
            raise ValueError(f"feature {self.feature!r} cannot be read from the frame alone (one of {', '.join(FRAME_FEATURES)})")
        if not (np.isfinite(self.slope) and np.isfinite(self.f_ref) and self.max_delta >= 0):
            raise ValueError(f"bad term {self!r}")

    def as_tuple(self) -> tuple:
        return (self.threshold, self.feature, float(self.slope), float(self.f_ref), float(self.max_delta))

    def delta(self, value: float) -> float:
        """How far this term moves its threshold for a frame whose feature reads ``value`` (0 without a reading)."""
        if value is None or not np.isfinite(value):
            return 0.0
        return float(np.clip(self.slope * (value - self.f_ref), -self.max_delta, self.max_delta))


def terms(spec) -> list[Term]:
    """``Config.hs_adapt`` (tuples or lists) -> Terms."""
    return [t if isinstance(t, Term) else Term(str(t[0]), str(t[1]), float(t[2]), float(t[3]), float(t[4])) for t in spec]


def as_config_value(ts) -> tuple:
    """Terms -> the plain tuple stored in ``Config.hs_adapt``."""
    return tuple(t.as_tuple() for t in terms(ts))


def frame_feature_values(bgr: np.ndarray, horizon_row: int | None, v_min: int) -> dict[str, float]:
    """The frame-only features of one image (``FRAME_FEATURES``), from its own histogram; no label used."""
    hist, v_mean = hr.gated_hist(bgr, horizon_row or 0, v_min)
    f = hr.frame_features(hist, v_mean, None)
    return {k: f[k] for k in FRAME_FEATURES}


def adapted_boxes(frame, model) -> tuple[dict[int, bf.Box], dict]:
    """The model's two class boxes moved by the rule for this frame. A color whose hue range comes out empty
    (lo >= hi) keeps the model's box. Returns (boxes, info: the feature values, each term's move, the colors
    kept)."""
    ts = terms(model.cfg.hs_adapt)
    feats = frame_feature_values(frame.bgr, model.cfg.horizon_row, model.cfg.v_min)
    lo = {c: list(model.boxes[c].lo) for c in model.boxes}
    hi = {c: list(model.boxes[c].hi) for c in model.boxes}
    moves = {}
    for t in ts:
        c, axis, end = SLOTS[t.threshold]
        d = t.delta(feats.get(t.feature))
        moves[t.threshold] = d
        (lo if end == "lo" else hi)[c][axis] += d
    boxes, kept = {}, []
    for c, b in model.boxes.items():
        new_lo, new_hi = lo[c], hi[c]
        new_lo[1] = float(np.clip(new_lo[1], 0, 255))
        if new_lo[0] >= new_hi[0] or new_lo[1] > new_hi[1]:
            boxes[c] = b
            kept.append(c)
        else:
            boxes[c] = bf.Box(tuple(new_lo), tuple(new_hi))
    return boxes, {"features": {t.feature: feats.get(t.feature) for t in ts}, "moves": moves, "kept": kept}


def frame_thresholds(frame, model) -> dict[str, float]:
    """The six thresholds (real OpenCV hue) the rule gives for this frame: for reports and the tests."""
    import dataclasses
    boxes, _ = adapted_boxes(frame, model)
    return hr.thresholds_of(dataclasses.replace(model, boxes=boxes))


# ---------------------------------------------------------------- the fit

def place_weights(places) -> np.ndarray:
    """One weight per row so that every place weighs 1 in total, however many conditions it has."""
    places = list(places)
    n = {p: places.count(p) for p in set(places)}
    return np.array([1.0 / n[p] for p in places])


def fit_slope(x, y, fixed: float, f_ref: float, weights=None) -> float:
    """b of the line ``y = fixed + b * (x - f_ref)`` by weighted least squares (the line goes through the home
    point by construction; only its slope is fit). Rows with a missing x or y are left out. 0 when no row has
    an x different from f_ref (nothing to fit: the rule is then the fixed model)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    w = np.ones(len(x)) if weights is None else np.asarray(weights, float)
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(w)
    dx, dy, w = x[ok] - f_ref, y[ok] - fixed, w[ok]
    den = float((w * dx * dx).sum())
    return 0.0 if den <= 1e-12 else float((w * dx * dy).sum() / den)
