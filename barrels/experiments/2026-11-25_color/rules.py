"""Candidate color rules of the 2026-11-25 work, as mask functions (frame in, class mask out), for the exploration
and the pre-registered test. Each builds on ``pipeline`` (the adopted gates and tie rule); none changes a pixel.

- ``fixed``: the adopted model eb863d84 (orange 3..13 S>=140, blue 103..119 S>=113).
- ``const(six)``: other fixed numbers (a re-centred constant).
- ``hyst(loose, radius)``: hysteresis. A pixel is a barrel color when it passes the adopted (strict) box, or when it
  passes a wider (loose) box AND lies within ``radius`` px of a pixel that passed the strict box of the same color.
  The strict pixels are the seeds: the loose box only grows paint around something already barrel-colored, so a
  table or a wall that falls in the loose box but has no strict pixel nearby stays unpainted.
- ``peak(...)``: the orange hue sector placed at the frame's own orange peak (the 2026-11-16 lead).
"""
from __future__ import annotations

import cv2
import numpy as np

from barrels import boxfit as bf
from barrels import hslabel as hl
from barrels import hsrange as hx
from barrels import pipeline as pl
from barrels.io import BLUE, ORANGE, OTHER

FIXED = {"orange_h_lo": 3, "orange_h_hi": 13, "orange_s_lo": 140, "blue_h_lo": 103, "blue_h_hi": 119, "blue_s_lo": 113}
_BASE = None


def base() -> pl.Model:
    global _BASE
    if _BASE is None:
        _BASE = hl.adopted_model()
    return _BASE


def boxes_of(six: dict) -> dict:
    return hl.model_from_thresholds(base(), hx.nested(six)).boxes


def tie(frame: pl.Frame, cand: dict) -> np.ndarray:
    """The adopted tie rule (R > B -> orange) and the mask, as ``pipeline.segment``."""
    both = cand[ORANGE] & cand[BLUE]
    if both.any():
        ow = frame.rgb[..., 0] > frame.rgb[..., 2]
        cand[ORANGE] = cand[ORANGE] & (~both | ow)
        cand[BLUE] = cand[BLUE] & (~both | ~ow)
    m = np.full(frame.shape, OTHER, np.uint8)
    m[cand[ORANGE]] = ORANGE
    m[cand[BLUE]] = BLUE
    return m


def gate(frame: pl.Frame, v_min: int = 40, horizon: int = 50) -> np.ndarray:
    k = frame.val >= v_min
    k[:horizon] = False
    return k


def in_six(frame: pl.Frame, six: dict, keep: np.ndarray) -> dict:
    bx = boxes_of(six)
    return {c: keep & bf.in_box(frame.hs(pl.HUE_SHIFT[c]), bx[c]) for c in (ORANGE, BLUE)}


def fixed(frame: pl.Frame) -> np.ndarray:
    return pl.segment(frame, base())[0]


def const(frame: pl.Frame, six: dict, v_min: int = 40) -> np.ndarray:
    return tie(frame, in_six(frame, six, gate(frame, v_min)))


def hyst(frame: pl.Frame, loose: dict, radius: int, strict: dict = FIXED, v_min: int = 40, loose_v_min: int | None = None) -> np.ndarray:
    keep = gate(frame, v_min)
    s = in_six(frame, strict, keep)
    lkeep = keep if loose_v_min is None else gate(frame, loose_v_min)
    lo = in_six(frame, loose, lkeep)
    cand = {}
    for c in (ORANGE, BLUE):
        if radius <= 0:
            near = s[c]
        else:
            k = 2 * radius + 1
            near = cv2.dilate(s[c].astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))) > 0
        cand[c] = s[c] | (lo[c] & near)
    return tie(frame, cand)


def orange_peak(frame: pl.Frame, s_min: int = 150, window=(-10, 30), min_px: int = 200) -> float | None:
    keep = gate(frame)
    hs = frame.hs(30)
    h = hs[..., 0][keep].astype(int) - 30
    s = hs[..., 1][keep]
    m = (s >= s_min) & (h >= window[0]) & (h <= window[1])
    if m.sum() < min_px:
        return None
    cnt = np.bincount(h[m] - window[0], minlength=window[1] - window[0] + 1).astype(float)
    cnt = np.convolve(cnt, [1, 2, 3, 2, 1], "same")
    return float(window[0] + int(np.argmax(cnt)))


def peak(frame: pl.Frame, below: int = 5, above: int = 5, ref: float = 8.0, max_shift: int = 10) -> np.ndarray:
    p = orange_peak(frame)
    six = dict(FIXED)
    if p is not None:
        d = int(np.clip(round(p - ref), -max_shift, max_shift))
        six["orange_h_lo"], six["orange_h_hi"] = FIXED["orange_h_lo"] + d, FIXED["orange_h_hi"] + d
    return const(frame, six)


def warmth(frame: pl.Frame, v_min: int = 40, horizon: int = 50) -> float:
    """How yellow the whole frame is: the median over the gated pixels (rows from 50, V >= 40) of (R - B) / (R + G + B).
    0 for a neutral (gray / white-table) scene, about 0.4 under the warm lamp on the bathroom floor."""
    k = gate(frame, v_min, horizon)
    rgb = frame.rgb[k].astype(np.float32)
    if len(rgb) == 0:
        return 0.0
    return float(np.median((rgb[:, 0] - rgb[:, 2]) / (rgb.sum(1) + 1.0)))


def light_warmth(frame: pl.Frame, top: float = 5.0, v_max: int = 256) -> float:
    """The color of the LIGHT, white-patch style: the median of (R - B) / (R + G + B) over the brightest ``top`` % of
    the whole frame's pixels (the brightest things in a scene are mostly white or pale surfaces and highlights, which
    take the light's color). ``v_max``: leave out pixels this bright or brighter (clipped). 0 = neutral light."""
    rgb = frame.rgb.reshape(-1, 3).astype(np.float32)
    v = rgb.max(1)
    ok = v < v_max
    if ok.sum() < 100:
        ok = np.ones(len(v), bool)
    thr = np.percentile(v[ok], 100 - top)
    sel = ok & (v >= thr)
    x = rgb[sel]
    return float(np.median((x[:, 0] - x[:, 2]) / (x.sum(1) + 1.0)))


def blue_top(frame: pl.Frame, n: int = 300, h=(92, 128), s_min: int = 20) -> float:
    """The frame's strongest blue: the S of its n-th most saturated pixel with hue in h (gated); 0 with fewer."""
    k = gate(frame)
    hs = frame.hs(0)
    H, S = hs[..., 0][k], hs[..., 1][k]
    s = S[(H >= h[0]) & (H <= h[1]) & (S >= s_min)]
    if len(s) < n:
        return 0.0
    return float(np.partition(s, len(s) - n)[len(s) - n])


def ramp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    """y0 at x <= x0, y1 at x >= x1, a straight line between."""
    if x <= x0:
        return y0
    if x >= x1:
        return y1
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def combo(frame: pl.Frame, orange: str = "fixed", blue: str = "fixed", o_loose=(-6, 22, 140), radius: int = 8,
          o_const=(-3, 16, 140), w0: float = 0.08, w1: float = 0.25, s_warm: int = 40, h_warm: int | None = None,
          k_top: float = 0.5, erode: int = 0) -> np.ndarray:
    """Orange part: "fixed" | "const" (o_const) | "hyst" (strict = adopted, loose = o_loose within ``radius``).
    Blue part: "fixed" | "warm": the blue S floor goes from 113 down to ``s_warm`` as the frame's warmth goes from w0
    to w1 (and, with ``h_warm``, the blue hue low end from 103 down to h_warm the same way)."""
    keep = gate(frame)
    six = dict(FIXED)
    if orange == "const":
        six["orange_h_lo"], six["orange_h_hi"], six["orange_s_lo"] = o_const
    if blue in ("warm", "light"):
        w = warmth(frame) if blue == "warm" else light_warmth(frame)
        six["blue_s_lo"] = int(round(ramp(w, w0, w1, FIXED["blue_s_lo"], s_warm)))
        if h_warm is not None:
            six["blue_h_lo"] = int(round(ramp(w, w0, w1, FIXED["blue_h_lo"], h_warm)))
    if blue == "rel":       # warm frame: the floor follows the frame's own strongest blue (k x its 300th most saturated blue px)
        w = warmth(frame)
        if w >= w0:
            top = blue_top(frame)
            floor = int(round(min(FIXED["blue_s_lo"], max(s_warm, k_top * top))))
            six["blue_s_lo"] = floor
            if h_warm is not None:
                frac = (FIXED["blue_s_lo"] - floor) / max(1, FIXED["blue_s_lo"] - s_warm)
                six["blue_h_lo"] = int(round(FIXED["blue_h_lo"] - frac * (FIXED["blue_h_lo"] - h_warm)))
    cand = in_six(frame, six, keep)
    if orange == "hyst":
        loose = {**six, "orange_h_lo": o_loose[0], "orange_h_hi": o_loose[1], "orange_s_lo": o_loose[2]}
        lo = in_six(frame, loose, keep)
        k = 2 * radius + 1
        seed = cand[ORANGE].astype(np.uint8)
        if erode:
            seed = cv2.erode(seed, np.ones((2 * erode + 1, 2 * erode + 1), np.uint8))
        near = cv2.dilate(seed, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))) > 0
        cand[ORANGE] = cand[ORANGE] | (lo[ORANGE] & near)
    return tie(frame, cand)
