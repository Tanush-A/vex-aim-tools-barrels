"""Peak finders for the barrels' colors in one frame's own histogram (experiment 2026-11-27_peaks).

Nothing that runs by default imports this. Per frame only; no pixel is changed; no label is read here.

Hue is "rolled" (+30, as in ``hshist``) so orange (about 3-13) is contiguous; ``real = rolled - 30``.
The 2-D histogram is hue (1 unit) x saturation (16 bins of 16), smoothed a little; a peak is a local maximum.

Finders (each returns, per color, the largest local peak in that color's hue region among the pixels it keeps):

    F0_naive       every gated pixel (rows >= 50, V >= 40)
    F1_sat         the same, each pixel weighted by (S/255)^3: saturated pixels count far more
    F2_rows        only rows below the horizon row (76): where a barrel can be
    F3_small       only pixels in connected regions of barrel-plausible size for their bottom row, found window by
                   window (an 8-unit hue window slid 2 units at a time), so a big uniform region (floor, wall) drops
    F4_logrb       1-D peaks of log((R+8)/(B+8)) instead of hue (its own units)
    F5_pair        only pixels of one broad color that are part of a stripe pattern with the other broad color:
                   a stripe pixel has body color above AND below it (each within 2 stripe heights, same column);
                   a body pixel is within 2 stripe heights above or below such a stripe pixel
    F6_pair_small  F5 and F3 together
    F7_pair_sat    F5, weighted as F1
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from barrels import geometry as geo
from barrels.io import BLUE, ORANGE

ROLL = 30
GATE_ROW = 50
HORIZON = 76
V_MIN = 40
S_BIN = 16
NSB = 256 // S_BIN
CAM = geo.AIM_4A8B6118_BOXFIT
# hue regions searched for each color (rolled hue): real orange -12..32, real blue 80..140
REGION = {ORANGE: (18, 63), BLUE: (80, 141)}
S_MIN_PEAK = 40                     # peaks are searched at S >= this (the gray mass is below)
BROAD_S = {ORANGE: 60, BLUE: 40}    # the broad color windows of F3 / F5
NAMES = {ORANGE: "orange", BLUE: "blue"}


def planes(bgr):
    hsv = cv2.cvtColor(np.ascontiguousarray(bgr), cv2.COLOR_BGR2HSV).astype(np.int32)
    return (hsv[..., 0] + ROLL) % 180, hsv[..., 1], hsv[..., 2]


def gate(shape, row0=GATE_ROW):
    g = np.zeros(shape, bool)
    g[row0:] = True
    return g


def hist2d(h, s, sel, weight=None):
    idx = h[sel] * NSB + (s[sel] // S_BIN)
    w = None if weight is None else weight[sel].astype(np.float64)
    return np.bincount(idx, weights=w, minlength=180 * NSB).reshape(180, NSB).astype(np.float64)


def smooth(hist):
    return cv2.GaussianBlur(hist.astype(np.float32), (3, 5), sigmaX=0.7, sigmaY=1.0,
                            borderType=cv2.BORDER_REFLECT).astype(np.float64)


def local_peaks(hs, region, s_min=S_MIN_PEAK):
    """Local maxima (>= all 8 neighbours, > 0) of a smoothed hist inside ``region`` (rolled hue), S >= s_min.
    Returns [(height, hue_rolled, s_center)], tallest first."""
    lo, hi = region
    sb0 = s_min // S_BIN
    sub = hs[lo - 1:hi + 1]
    pad = np.pad(sub, ((0, 0), (1, 1)), constant_values=-1)
    out = []
    for i in range(1, sub.shape[0] - 1):
        for j in range(sb0, NSB):
            val = sub[i, j]
            if val <= 1e-9:
                continue
            if val >= pad[i - 1:i + 2, j:j + 3].max():
                out.append((float(val), lo - 1 + i, j * S_BIN + S_BIN / 2))
    out.sort(key=lambda t: -t[0])
    return out


@dataclass
class Peak:
    hue: float        # real OpenCV hue (may be negative: -3 = 177)
    s: float
    height: float     # smoothed count (or weight)
    n_sel: int        # pixels the finder kept in the color's hue region (S >= S_MIN_PEAK)
    second: float     # height of the second peak / height of this one (0 if none)
    peaks: list       # every local peak [(height, real hue, s)], tallest first


def peak_of(h, s, sel, c, weight=None):
    hs = smooth(hist2d(h, s, sel, weight))
    pk = local_peaks(hs, REGION[c])
    if not pk:
        return None
    lo, hi = REGION[c]
    n = int((sel & (h >= lo) & (h < hi) & (s >= S_MIN_PEAK)).sum())
    return Peak(pk[0][1] - ROLL, pk[0][2], pk[0][0], n, pk[1][0] / pk[0][0] if len(pk) > 1 else 0.0,
                [(a, b - ROLL, cc) for a, b, cc in pk])


def broad(h, s, v, c, row0=GATE_ROW):
    lo, hi = REGION[c]
    m = (h >= lo) & (h < hi) & (s >= BROAD_S[c]) & (v >= V_MIN)
    m[:row0] = False
    return m


# ---- geometry per row: expected barrel width / height for a barrel whose bottom is at that row; stripe height
#      for a stripe whose middle is at that row

_ROWGEO: dict = {}


def row_geo(H=480):
    if H in _ROWGEO:
        return _ROWGEO[H]
    W, Hh, St = np.zeros(H), np.zeros(H), np.zeros(H)
    for r in range(H):
        if r > CAM.horizon_row() + 1:
            try:
                W[r] = CAM.expected_barrel_width_px(bottom_row=r)
                Hh[r] = CAM.expected_barrel_height_px(bottom_row=r)
            except Exception:
                pass
            try:
                b = CAM.bottom_row_from_stripe_row(r)
                d = CAM.d_axis_from_bottom_row(b)
                br = CAM.barrel_rows(d)
                St[r] = abs(br.stripe_bottom - br.stripe_top)
            except Exception:
                pass
    for arr in (W, Hh, St):
        good = np.nonzero(np.isfinite(arr) & (arr > 0))[0]
        if len(good):
            arr[good[-1]:] = arr[good[-1]]
        arr[~np.isfinite(arr)] = 0
    _ROWGEO[H] = (W, Hh, St)
    return _ROWGEO[H]


def stripe_h_at(row, H=480):
    St = row_geo(H)[2]
    return max(3.0, float(St[int(np.clip(row, 0, H - 1))]))


def small_regions(h, s, v, c, width=8, step=2, row0=GATE_ROW, wmax=1.6, hmax=1.3, amin=12):
    """Pixels of color region ``c`` that lie in a connected region of barrel-plausible size in at least one narrow
    hue window. Size test at the region's bottom row: bbox width <= wmax * W and height <= hmax * H."""
    W, Hh, _ = row_geo(h.shape[0])
    lo, hi = REGION[c]
    base = (s >= BROAD_S[c]) & (v >= V_MIN)
    base[:row0] = False
    out = np.zeros(h.shape, bool)
    for a in range(lo, hi - width + 1, step):
        m = base & (h >= a) & (h < a + width)
        if m.sum() < amin:
            continue
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
        x, y, w, hh, area = st[:, 0], st[:, 1], st[:, 2], st[:, 3], st[:, 4]
        bot = np.minimum(y + hh - 1, h.shape[0] - 1)
        ok = (area >= amin) & (bot > HORIZON + 1) & (W[bot] > 0) & (w <= wmax * W[bot]) & (hh <= hmax * Hh[bot])
        ok[0] = False
        out |= ok[lab]
    return out


def _near(m, kmul, up: bool | None, band=32):
    """True where m holds within k rows above (up=True), below (up=False) or either (None), same column;
    k = kmul stripe heights at that row (taken per band of rows)."""
    H = m.shape[0]
    out = np.zeros_like(m)
    for r0 in range(0, H, band):
        r1 = min(H, r0 + band)
        k = max(1, int(round(kmul * stripe_h_at((r0 + r1) // 2, H))))
        acc = np.zeros((r1 - r0, m.shape[1]), bool)
        dirs = (-1,) if up is True else (1,) if up is False else (-1, 1)
        for sgn in dirs:
            for d in range(1, k + 1):
                src0, src1 = r0 + sgn * d, r1 + sgn * d
                lo_, hi_ = max(0, src0), min(H, src1)
                if hi_ > lo_:
                    acc[lo_ - src0:hi_ - src0] |= m[lo_:hi_]
        out[r0:r1] = acc
    return out


def pair_masks(h, s, v, kmul=2.0, row0=GATE_ROW):
    """{c: pixels of broad color c that are part of a stripe pattern with the other broad color}."""
    O, B = broad(h, s, v, ORANGE, row0), broad(h, s, v, BLUE, row0)
    out = {ORANGE: np.zeros_like(O), BLUE: np.zeros_like(O)}
    for body, stripe, cb, cs in ((O, B, ORANGE, BLUE), (B, O, BLUE, ORANGE)):
        sand = stripe & _near(body, kmul, True) & _near(body, kmul, False)
        out[cs] |= sand
        out[cb] |= body & _near(sand, kmul, None)
    return out


def logrb(bgr):
    b = bgr[..., 0].astype(np.float32)
    r = bgr[..., 2].astype(np.float32)
    return np.log((r + 8) / (b + 8))


LRB_BINS = np.linspace(-3, 3, 121)


def lrb_peak(L, sel, c):
    hist, _ = np.histogram(L[sel], bins=LRB_BINS)
    hs = cv2.GaussianBlur(hist.astype(np.float32).reshape(1, -1), (5, 1), 1.0).ravel()
    centers = (LRB_BINS[1:] + LRB_BINS[:-1]) / 2
    ok = centers > 0.3 if c == ORANGE else centers < -0.3
    best = None
    for i in range(1, len(hs) - 1):
        if ok[i] and hs[i] > 0 and hs[i] >= hs[i - 1] and hs[i] >= hs[i + 1]:
            if best is None or hs[i] > hs[best]:
                best = i
    return None if best is None else float(centers[best])


FINDERS = ("F0_naive", "F1_sat", "F2_rows", "F3_small", "F5_pair", "F6_pair_small", "F7_pair_sat")


def selections(bgr):
    """(h, s, v, {finder: (selection mask per color, weight or None)}) for one frame."""
    h, s, v = planes(bgr)
    g = gate(h.shape) & (v >= V_MIN)
    w_sat = (s / 255.0) ** 3
    rows = g.copy()
    rows[:HORIZON + 1] = False
    pm = pair_masks(h, s, v)
    sel = {}
    for c in (ORANGE, BLUE):
        sm = small_regions(h, s, v, c)
        sel.setdefault("F0_naive", {})[c] = (g, None)
        sel.setdefault("F1_sat", {})[c] = (g, w_sat)
        sel.setdefault("F2_rows", {})[c] = (rows, None)
        sel.setdefault("F3_small", {})[c] = (g & sm, None)
        sel.setdefault("F5_pair", {})[c] = (g & pm[c], None)
        sel.setdefault("F6_pair_small", {})[c] = (g & pm[c] & sm, None)
        sel.setdefault("F7_pair_sat", {})[c] = (g & pm[c], w_sat)
    return h, s, v, sel


def find_all(bgr) -> dict:
    """{finder: {color: Peak | None}}, plus 'F4_logrb': {color: float | None}, for one frame."""
    h, s, v, sel = selections(bgr)
    out = {f: {c: peak_of(h, s, m, c, w) for c, (m, w) in d.items()} for f, d in sel.items()}
    g = gate(h.shape) & (v >= V_MIN) & (s >= S_MIN_PEAK)
    L = logrb(bgr)
    out["F4_logrb"] = {c: lrb_peak(L, g, c) for c in (ORANGE, BLUE)}
    return out
