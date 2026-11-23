"""Candidate measures of "does the seen part bulge OUTWARD or INWARD at this end" (census only; nothing here is the
detector). The detector's version, once chosen, lives in ``detector.py`` and the census checks that it agrees.

The seen part of a barrel at one end of its seen columns, read exactly as ``own_close`` reads it (``_end_closure``):
for every column, the top row t(x) = the first body pixel walking down from the predicted top less the edge tolerance
to the stripe (the stripe's top row when there is none), and the bottom row b(x) = the last body pixel from the stripe
down to the predicted bottom plus the tolerance (the stripe's bottom row when there is none). The region seen is the
set of rows t(x)..b(x) in each column.

Measures, at one end, over the ``zone`` x W columns nearest it (at least 3), all in barrel heights H (signed:
positive = the boundary bulges OUTWARD, the region is convex there; negative = it bulges INWARD, concave):

  ``chord_top``   mean over the zone of (the straight chord from the end column's top to the zone's inner column's
                  top) minus t(x). Positive when the top runs above the chord (a rounded corner: flat, then falling
                  away at the very end); negative when it sags below (a round thing in front cut into it).
  ``chord_bot``   the same for the bottom, mirrored: b(x) minus the chord.
  ``chord``       the mean of the two.
  ``chord_min``   the smaller of the two.
  ``hull``        1 - (area of the region in the zone) / (area of its convex hull), unsigned (0 = convex).
  ``side``        the outermost column of the region in each row between the zone's highest top and lowest bottom,
                  minus the chord from the top row's outermost column to the bottom row's; mean, in barrel WIDTHS,
                  positive outward (the middle rows reach further out than the top and bottom rows).
"""
from __future__ import annotations

import math

import cv2
import numpy as np

from barrels import detector as det


def profiles(mask: np.ndarray, s, rows, sx0: int, sx1: int, cfg) -> tuple[np.ndarray, np.ndarray]:
    """t(x), b(x) for the columns sx0..sx1, as ``detector._end_closure`` reads them (b = the row after the last body pixel)."""
    h = mask.shape[0]
    H = rows.bottom - rows.top
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
    x0, y0, x1, y1 = s.bbox
    lim_top, lim_bot = max(0, int(rows.top - tol)), min(h, int(rows.bottom + tol) + 1)
    t, b = [], []
    for x in range(sx0, sx1):
        up = np.flatnonzero(mask[lim_top:y0, x] == s.body)
        dn = np.flatnonzero(mask[y1:lim_bot, x] == s.body)
        t.append(float((lim_top + up[0]) if len(up) else y0))
        b.append(float((y1 + dn[-1] + 1) if len(dn) else y1))
    return np.array(t), np.array(b)


def _chord_dev(v: np.ndarray) -> float:
    """mean of (chord from v[0] to v[-1]) - v over the samples."""
    n = len(v)
    chord = v[0] + (v[-1] - v[0]) * np.arange(n) / (n - 1)
    return float(np.mean(chord - v))


def end_measures(t: np.ndarray, b: np.ndarray, left: bool, W: float, H: float, zone: float) -> dict:
    n = max(3, int(round(zone * W)))
    if len(t) < 3:
        return {k: math.nan for k in ("chord_top", "chord_bot", "chord", "chord_min", "hull", "side")}
    n = min(n, len(t))
    tt, bb = (t[:n], b[:n]) if left else (t[::-1][:n], b[::-1][:n])          # index 0 = the end column, inward from there
    ct = _chord_dev(tt) / H                 # chord - t > 0: the top runs above the chord (outward)
    cb = -_chord_dev(bb) / H                # b - chord > 0: the bottom runs below the chord (outward)
    # the region in the zone as column intervals; i = distance from the end in columns
    pts = []
    area = 0.0
    for i in range(n):
        if bb[i] > tt[i]:
            pts += [(i, tt[i]), (i + 1, tt[i]), (i, bb[i]), (i + 1, bb[i])]
            area += bb[i] - tt[i]
    hull = math.nan
    if len(pts) >= 3 and area > 0:
        ha = cv2.contourArea(cv2.convexHull(np.array(pts, np.float32)))
        hull = 1.0 - area / ha if ha > 0 else math.nan
    # side profile: for each row, the outermost column (smallest i) whose interval holds the row
    r0, r1 = int(math.floor(tt.min())), int(math.ceil(bb.max()))
    e = []
    for r in range(r0, r1):
        inside = np.flatnonzero((tt <= r) & (r < bb))
        e.append(float(inside.min()) if len(inside) else math.nan)
    e = np.array(e)
    side = math.nan
    ok = ~np.isnan(e)
    if ok.sum() >= 3:
        ys = np.flatnonzero(ok)
        ev = e[ok]
        chord = ev[0] + (ev[-1] - ev[0]) * (ys - ys[0]) / max(1, ys[-1] - ys[0])
        side = float(np.mean(chord - ev)) / W            # outward = smaller i than the chord
    return {"chord_top": ct, "chord_bot": cb, "chord": (ct + cb) / 2, "chord_min": min(ct, cb), "hull": hull, "side": side}


def closure(t: np.ndarray, b: np.ndarray, left: bool, rows, W: float, H: float) -> float:
    """``own_close``'s closure of this end (det.CLOSE_ZONE x W, at least 2 columns), in barrel heights."""
    n = max(2, int(round(det.CLOSE_ZONE * W)))
    tt, bb = (t[:n], b[:n]) if left else (t[::-1][:n], b[::-1][:n])
    return min(float(np.mean(tt - rows.top)), float(np.mean(rows.bottom - bb))) / H
