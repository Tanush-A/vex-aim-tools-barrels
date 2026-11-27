"""A color setting for one place, computed from ONE frame and its hand-drawn boxes: what a calibration shot gives
(2026-11-26, experiment ``experiments/2026-11-26_place_ceiling``; TODO C7 and the third idea of E6).

An analysis helper like ``hsrange``: NOTHING here is called by ``pipeline``, ``detector`` or the live code. No pixel
is changed: the frame is only read, and what comes out is six numbers (a hue range and a saturation floor per color)
for ``hslabel.model_from_thresholds``.

Why not ``hsrange.net_optimum`` as it is. It counts every pixel inside the cores of all boxes as "barrel" for both
colors, which is safe only while the blue slider cannot reach orange's hues. Since 2026-11-25 the blue slider runs
over the whole hue circle (under a warm lamp the blue paint reads hue 26 to 44), so here each color gets its own
pixels:

1. ``zones``  where in a box each color sits. Measured on the home masks (``explore/zone_geometry.py``): in the
   central half of the box width the barrel's own color fills 10-35 % and 70-95 % of the box height and the stripe
   (the other color) fills 50-60 %. The body zones are rows 12-35 % and 72-90 %, the stripe zone rows 50-60 %, both
   in the central half of the width. A box flagged occluded, truncated, held or no_stripe gives no zone (what is in
   it may be the thing in front). "Outside" is everything at least 4 px away from every box.
2. ``class_hists``  per color two (hue, S) histograms of the pixels past the two fixed gates (below the horizon row,
   V >= the brightness floor): its own zone pixels, and the pixels it must not paint (outside, plus the other
   color's zones).
3. ``net_rect`` / ``net_setting``  the hue range and S floor that paint the most zone pixels minus ``w_out`` x the
   pixels that must not be painted, searched exactly (Tanush's rule, as in ``hsrange.net_optimum``: stop where the
   paint outside climbs faster than the paint on the barrels). A color with nothing to gain keeps the adopted values.
4. ``mid_setting``  the slider tool's recipe (``hsrange.propose``) on top of it: among the net settings at four
   outside weights and the adopted values, the one with which today's detector finds the most of the frame's boxes;
   then, per threshold, the middle of the run of values that work as well on that frame (a setting in the middle of
   what works on the calibration frame has room on both sides for the next frame).

``pooled_net_setting`` is step 3 on the summed histograms of several frames (a ceiling for the computation: every
frame of a condition at once).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import hsrange as hx
from . import pipeline as pl
from .io import BLUE, ORANGE

CLASS_NAMES = ("orange", "blue")
CLASS_ID = {"orange": ORANGE, "blue": BLUE}
OTHER = {"orange": "blue", "blue": "orange"}
BODY_ROWS = ((0.12, 0.35), (0.72, 0.90))        # shares of the box height that hold the barrel's own color
STRIPE_ROWS = (0.50, 0.60)                      # ... that hold the stripe (the other color)
COLS = (0.25, 0.75)                             # the central half of the box width
PAD = 4                                         # "outside" starts this many px away from every box
SKIP_FLAGS = ("occluded", "truncated", "held", "no_stripe")
# the span each threshold may take: the slider tool's since 2026-11-25 (tools/hs_slider.py SLIDERS)
FULL_LIMITS = {"orange_h_lo": (-30, 60), "orange_h_hi": (-30, 60), "orange_s_lo": (0, 255),
               "blue_h_lo": (0, 179), "blue_h_hi": (0, 179), "blue_s_lo": (0, 255)}
NET_WEIGHTS = hx.NET_WEIGHTS                    # (1, 0.5, 0.25, 0.1): the outside weights the recipe tries


# ---------------------------------------------------------------- 1. where each color sits in a box

@dataclass
class Zones:
    pos: dict                   # class name -> bool mask: pixels that are that color (body zones of its barrels, stripe zones of the others)
    outside: np.ndarray         # bool mask: at least PAD px away from every box, from row0 down
    used: int                   # boxes that gave zones
    skipped: int                # boxes left out (flagged)


def _rows(y0: int, y1: int, lo: float, hi: float) -> tuple[int, int]:
    h = y1 - y0
    a, b = y0 + int(round(lo * h)), y0 + int(round(hi * h))
    return a, max(b, a + 1)


def zones(shape, boxes, row0: int = 0) -> Zones:
    """The zone masks of a frame of ``shape`` (h, w) for its box labels (``io.load_boxes(...)["barrels"]``: dicts with
    ``bbox`` [x0, y0, x1, y1] half-open, ``color``, ``flags``). Rows above ``row0`` (the horizon gate) are in no zone."""
    h, w = shape[:2]
    pos = {c: np.zeros((h, w), bool) for c in CLASS_NAMES}
    near = np.zeros((h, w), bool)
    used = skipped = 0
    for b in boxes:
        x0, y0, x1, y1 = (int(v) for v in b["bbox"])
        near[max(0, y0 - PAD):min(h, y1 + PAD), max(0, x0 - PAD):min(w, x1 + PAD)] = True
        if b["color"] not in pos or any(f in SKIP_FLAGS for f in (b.get("flags") or ())):
            skipped += 1
            continue
        used += 1
        bw = x1 - x0
        c0, c1 = x0 + int(round(COLS[0] * bw)), x0 + int(round(COLS[1] * bw))
        c1 = max(c1, c0 + 1)
        for lo, hi in BODY_ROWS:
            r0, r1 = _rows(y0, y1, lo, hi)
            pos[b["color"]][max(0, r0):max(0, r1), max(0, c0):max(0, c1)] = True
        r0, r1 = _rows(y0, y1, *STRIPE_ROWS)
        pos[OTHER[b["color"]]][max(0, r0):max(0, r1), max(0, c0):max(0, c1)] = True
    both = pos["orange"] & pos["blue"]              # two boxes overlap there: nobody's
    outside = ~near
    for m in (*pos.values(), outside):
        m[:max(0, row0)] = False
    for c in CLASS_NAMES:
        pos[c] &= ~both
    return Zones(pos, outside, used, skipped)


# ---------------------------------------------------------------- 2. the histograms

def _hist(hs: np.ndarray, sel: np.ndarray) -> np.ndarray:
    out = np.zeros((180, 256), np.int64)
    np.add.at(out, (hs[..., 0][sel].astype(int), hs[..., 1][sel].astype(int)), 1)
    return out


def class_hists(frame: pl.Frame, z: Zones, v_min: int) -> dict:
    """class name -> (hin, hout): (shifted hue, S) counts of that color's zone pixels and of the pixels it must not
    paint (outside every box, plus the other color's zones), among the pixels with V >= ``v_min``. The hue axis is
    shifted by ``pipeline.HUE_SHIFT`` (orange: +30), as the model's boxes are."""
    keep = np.asarray(frame.val) >= v_min
    out = {}
    for c in CLASS_NAMES:
        hs = frame.hs(pl.HUE_SHIFT[CLASS_ID[c]])
        out[c] = (_hist(hs, keep & z.pos[c]), _hist(hs, keep & (z.outside | z.pos[OTHER[c]])))
    return out


def frame_hists(frame: pl.Frame, boxes, base: pl.Model) -> dict:
    """``class_hists`` of a frame with the base model's two gates (horizon row, brightness floor)."""
    return class_hists(frame, zones(frame.shape, boxes, base.cfg.horizon_row or 0), int(base.cfg.v_min))


def add_hists(a: dict | None, b: dict) -> dict:
    """The sum of two ``class_hists`` results (``a`` may be None)."""
    if a is None:
        return {c: (b[c][0].copy(), b[c][1].copy()) for c in CLASS_NAMES}
    return {c: (a[c][0] + b[c][0], a[c][1] + b[c][1]) for c in CLASS_NAMES}


# ---------------------------------------------------------------- 3. the net setting

def net_rect(hin: np.ndarray, hout: np.ndarray, w_out: float = 1.0, lo: int = 0, hi: int = 179) -> tuple[int, int, int] | None:
    """(first hue index, last hue index, S floor) that maximise  sum(hin) - w_out * sum(hout)  over the rectangle
    hue in [first, last] (inside ``lo`` .. ``hi``), S >= floor; None when no rectangle gains anything. Exact. Floors
    are tried from 255 down and a tie keeps the higher floor (it paints less)."""
    cum = lambda a: np.cumsum(a[:, ::-1], axis=1)[:, ::-1]  # noqa: E731  [h, s] = pixels with S >= s
    net = cum(hin) - w_out * cum(hout)
    best_g, best = 0.0, None
    for s in range(255, -1, -1):
        g, i, j = hx._best_run(net[lo:hi + 1, s])
        if g > best_g + 1e-9:
            best_g, best = g, (lo + i, lo + j, s)
    return best


def net_from_hists(hists: dict, adopted: dict, w_out: float = 1.0, limits: dict | None = None) -> dict:
    """The six numbers (flat, as ``hsrange.flat``) from ``class_hists``; a color with nothing to gain keeps
    ``adopted``'s values. ``limits``: the span of each threshold (default ``FULL_LIMITS``)."""
    limits = limits or FULL_LIMITS
    out = hx.flat(adopted)
    for c in CLASS_NAMES:
        shift = pl.HUE_SHIFT[CLASS_ID[c]]
        lo, hi = limits[f"{c}_h_lo"][0] + shift, limits[f"{c}_h_hi"][1] + shift
        r = net_rect(hists[c][0], hists[c][1], w_out, max(0, lo), min(179, hi))
        if r is not None:
            out[f"{c}_h_lo"], out[f"{c}_h_hi"], out[f"{c}_s_lo"] = r[0] - shift, r[1] - shift, r[2]
    return out


def net_setting(frame: pl.Frame, boxes, base: pl.Model, adopted: dict, w_out: float = 1.0, limits: dict | None = None) -> dict:
    """The net setting of ONE frame and its boxes (no detector is run)."""
    return net_from_hists(frame_hists(frame, boxes, base), adopted, w_out, limits)


def pooled_net_setting(frames_and_boxes, base: pl.Model, adopted: dict, w_out: float = 1.0, limits: dict | None = None) -> dict:
    """The net setting of several frames at once: their histograms summed. ``frames_and_boxes``: (Frame, boxes) pairs."""
    total = None
    for frame, boxes in frames_and_boxes:
        total = add_hists(total, frame_hists(frame, boxes, base))
    if total is None:
        return hx.flat(adopted)
    return net_from_hists(total, adopted, w_out, limits)


# ---------------------------------------------------------------- 4. the middle of what works on the calibration frame

@dataclass
class MidSetting:
    thresholds: dict            # flat six numbers
    anchor: dict                # the setting the ranges were computed around
    source: str                 # which candidate became the anchor, and whether the middle was kept
    found: int                  # the frame's boxes today's detector finds with ``thresholds``
    n_boxes: int
    ranges: dict                # threshold -> (lo, hi)


def mid_setting(fe: hx.FrameEval, adopted: dict, limits: dict | None = None, coarse: int = 4) -> MidSetting:
    """``hsrange.propose`` with the net settings of this module and the full slider span. ``fe``: the calibration
    frame with its boxes (``hsrange.FrameEval``). Anchor = among the net settings (outside weights ``NET_WEIGHTS``)
    and the adopted values, the one that finds the most of the frame's boxes, then draws the fewest false boxes
    (ties keep the earlier, more careful one). Then each threshold's run of working values around the anchor
    (``hsrange.sweep``), and the middle of each run that did not hit an end of its span; all six middles together must
    work as well as the anchor, else the anchor stays."""
    limits = limits or FULL_LIMITS
    adopted = hx.flat(adopted)
    hists = frame_hists(fe.frame, fe.boxes, fe.base)
    cands = [(f"net setting (outside weight {w:g})", net_from_hists(hists, adopted, w, limits)) for w in NET_WEIGHTS] + [("adopted", adopted)]
    src, anchor = max(cands, key=lambda c: (len(fe.evaluate(c[1]).found), -fe.evaluate(c[1]).n_false, -cands.index(c)))
    ranges = hx.sweep(fe, anchor, hx.DET, coarse=coarse, limits=limits)
    mid = {t: (anchor[t] if {r.lo_why, r.hi_why} & {hx.OPEN, hx.OTHER_END} else int(round((r.lo + r.hi) / 2))) for t, r in ranges.items()}
    for c in CLASS_NAMES:
        if mid[f"{c}_h_lo"] > mid[f"{c}_h_hi"]:
            mid[f"{c}_h_lo"], mid[f"{c}_h_hi"] = anchor[f"{c}_h_lo"], anchor[f"{c}_h_hi"]
    if hx.works(fe.evaluate(mid), fe.evaluate(anchor), hx.DET) is None:
        chosen, src = mid, src + ", middle of the ranges"
    else:
        chosen, src = anchor, src + " (the middle did not work)"
    return MidSetting(chosen, anchor, src, len(fe.evaluate(chosen).found), len(fe.boxes), {t: (r.lo, r.hi) for t, r in ranges.items()})
