"""Measure the damage real segmentation has, in the units of ``degrade.py`` (2026-11-19).

``degrade.py`` damages a good mask by stated amounts (a pale patch w x W wide, a break in the stripe, edges eaten by
e pixels, a share of pixels dropped, specks on the table). This module goes the other way: given a mask and what
it should have been, it reads those amounts back, so that a real segmentation can be put on the same scale. Used by
``experiments/2026-11-19_damage_realism``; nothing here is part of the detector, the color model or the eval.

Three instruments:

``measure_barrel(truth, pred, box, color)``   needs a hand-made mask. Per barrel (W wide, H tall, its hand-drawn box):
    lost             share of the barrel's hand-mask pixels that are not painted their color (body and stripe);
    edge_outer_px,   how many pixels the edges are eaten: the pixels of the hand mask are sorted into rings by their
    edge_seam_px     depth from the outline (outer) or from the body / stripe seam (seam); the lost share of rings
                     1, 2, 3, over what the inside loses anyway, added up (an erosion by e px gives e);
    dropout          the lost share deeper than 3 px, holes left out;
    top_hole_*       the largest hole on the upper body (above the stripe): width / W, height / H, where its centre is;
    stripe_hole_w    the widest hole across the stripe, / W;
    stripe_pieces,   the stripe read column by column: in how many pieces it is, how many breaks between pieces,
    stripe_breaks,   the widest break / W, the unpainted columns at its two ends / W, and how thick the painted
    stripe_break_w,  stripe is against the hand-made one;
    stripe_end_gap, stripe_thickness
    spill            pixels painted a barrel color within 4 px of the box where the hand mask has nothing, / the
                     barrel's area (reflections; the simulation has no such damage).
    A hole is a connected group of lost pixels that survives a 3 x 3 opening (so it holds a 3 x 3 block), counted
    only deeper than the rings that are eaten outright.

``measure_box(pred, box, color)``   needs only the hand-drawn box. Coverage of the box core, the stripe across the
    box width, holes in the core. The same quantities as above in spirit; the numbers are comparable between
    masks measured with THIS instrument (a hand mask gives its zero point), not with ``measure_barrel``.

``specks(pred, boxes, truth)``   areas of the groups of barrel-colored pixels off the barrels.
"""
from __future__ import annotations

import cv2
import numpy as np

from .io import BLUE, ORANGE

RINGS = 3              # edge rings read (depth 1, 2, 3 px)
RING_EATEN = 0.5       # a ring that lost this share counts as eaten outright (holes are looked for deeper)
RING_MIN_PX = 5        # ... if it has at least this many pixels
INSIDE_MIN_PX = 30     # the dropout needs this many pixels deeper than the rings
PAD = 4                # specks and spill: this many px around a box belong to the barrel (degrade.SPECK_PAD)
SPECK_MAX = 20         # a group under this many px is a speck (the detector drops blobs under 20 px); else a blob
CORE = (0.2, 0.1)      # the box core of measure_box: this share of W off each side, of H off top and bottom
_K3 = np.ones((3, 3), np.uint8)
NAN = float("nan")


def other_color(color: int) -> int:
    return BLUE if color == ORANGE else ORANGE


def column_runs(painted: np.ndarray, W: float) -> dict:
    """A stripe read column by column. ``painted``: one bool per column, left to right. Pieces = runs of painted
    columns; breaks = the unpainted runs between two pieces; ``break_w`` the widest break, ``end_gap`` the
    unpainted columns before the first and after the last piece, ``span`` first to last painted column; all / W."""
    painted = np.asarray(painted, bool)
    idx = np.flatnonzero(painted)
    if len(idx) == 0:
        return {"pieces": 0, "breaks": 0, "break_w": NAN, "end_gap": len(painted) / W, "span": 0.0}
    inner = painted[idx[0]:idx[-1] + 1]
    edges = np.flatnonzero(np.diff(np.concatenate(([1], inner.astype(np.int8), [1]))))      # starts and ends of the unpainted runs
    gaps = edges[1::2] - edges[0::2]
    return {"pieces": len(gaps) + 1, "breaks": len(gaps), "break_w": float(gaps.max()) / W if len(gaps) else 0.0,
            "end_gap": (len(painted) - len(inner)) / W, "span": len(inner) / W}


def _depth(region: np.ndarray) -> np.ndarray:
    """Chessboard distance of every pixel of ``region`` to the nearest pixel outside it (1 = on its edge; what a
    3 x 3 erosion removes in that many rounds). The array's border counts as outside."""
    return cv2.distanceTransform(np.pad(region.astype(np.uint8), 1), cv2.DIST_C, 3)[1:-1, 1:-1]


def _dist_to(target: np.ndarray) -> np.ndarray:
    """Chessboard distance of every pixel to the nearest pixel of ``target`` (inf when there is none)."""
    if not target.any():
        return np.full(target.shape, np.inf, np.float32)
    return cv2.distanceTransform((~target).astype(np.uint8), cv2.DIST_C, 3)


def hole_components(lost: np.ndarray) -> list[np.ndarray]:
    """The holes of a lost-pixel map: its connected groups after a 3 x 3 opening, largest first."""
    opened = cv2.morphologyEx(np.pad(lost.astype(np.uint8), 1), cv2.MORPH_OPEN, _K3)[1:-1, 1:-1]
    n, lab, stats, _ = cv2.connectedComponentsWithStats(opened, connectivity=8)
    order = sorted(range(1, n), key=lambda i: -stats[i, cv2.CC_STAT_AREA])
    return [lab == i for i in order]


def _extent(m: np.ndarray) -> tuple[int, int, float, float]:
    ys, xs = np.nonzero(m)
    return int(np.ptp(xs)) + 1, int(np.ptp(ys)) + 1, float(xs.mean()), float(ys.mean())


def measure_barrel(truth: np.ndarray, pred: np.ndarray, box: tuple[int, int, int, int], color: int) -> dict:
    """The damage of one barrel of ``pred`` against the hand mask ``truth`` inside its hand-drawn ``box``
    (x0, y0, x1, y1, half-open); ``color`` is the body color. See the module docstring for the fields."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    oc = other_color(color)
    t, p = truth[y0:y1, x0:x1], pred[y0:y1, x0:x1]
    body, stripe = t == color, t == oc
    own = body | stripe
    n = int(own.sum())
    out = {"W": W, "H": H, "px": n, "body_px": int(body.sum()), "stripe_px": int(stripe.sum())}
    if n == 0:
        return out
    lost = (body & (p != color)) | (stripe & (p != oc))
    out["lost"] = float(lost.sum()) / n
    out["body_lost"] = float((body & lost).sum()) / max(1, int(body.sum()))
    out["stripe_lost"] = float((stripe & lost).sum()) / int(stripe.sum()) if stripe.any() else NAN
    out["wrong_color"] = float(((body & (p == oc)) | (stripe & (p == color))).sum()) / n

    d_out = _depth(own)
    d_seam = np.where(body, _dist_to(stripe), np.where(stripe, _dist_to(body), np.inf))
    depth = np.minimum(d_out, d_seam)
    seam = own & (d_seam < d_out)

    def share(sel):
        return float((lost & sel).sum()) / int(sel.sum()) if sel.sum() else NAN

    eaten = 0                                                    # rings lost outright, from the edge inward
    for k in range(1, RINGS + 1):
        ring = own & (depth == k)
        if ring.sum() >= RING_MIN_PX and share(ring) >= RING_EATEN and eaten == k - 1:
            eaten = k
    holes = hole_components(lost & (depth > eaten))
    in_hole = np.zeros(own.shape, bool)
    for hmask in holes:
        in_hole |= hmask
    rest = own & ~in_hole
    inside = rest & (depth > RINGS)
    out["dropout"] = share(inside) if inside.sum() >= INSIDE_MIN_PX else NAN
    floor = 0.0 if np.isnan(out["dropout"]) else out["dropout"]
    for name, sel in (("outer", rest & ~seam), ("seam", rest & seam)):
        tot, any_ring = 0.0, False
        for k in range(1, RINGS + 1):
            s = share(sel & (depth == k))
            out[f"ring{k}_{name}"] = s
            if not np.isnan(s):
                any_ring = True
                tot += max(0.0, (s - floor) / (1 - floor)) if floor < 1 else 0.0
        out[f"edge_{name}_px"] = tot if any_ring else NAN

    rows = np.flatnonzero(stripe.any(1))
    s_top, s_bot = (int(rows.min()), int(rows.max())) if len(rows) else (H // 2, H // 2)
    out.update({"holes": len(holes), "hole_area": float(in_hole.sum()) / n,
                "top_hole_w": 0.0, "top_hole_h": 0.0, "top_hole_cx": NAN, "top_hole_cy": NAN, "top_hole_area": 0.0,
                "low_hole_w": 0.0, "low_hole_h": 0.0, "stripe_hole_w": 0.0, "stripe_hole_h": 0.0})
    for hmask in holes:                                          # largest first
        w, h, cx, cy = _extent(hmask)
        where = "top" if cy < s_top else ("low" if cy > s_bot else "")
        if where == "top" and out["top_hole_w"] == 0.0:
            out.update({"top_hole_w": w / W, "top_hole_h": h / H, "top_hole_cx": (cx + 0.5) / W, "top_hole_cy": (cy + 0.5) / H,
                        "top_hole_area": float(hmask.sum()) / (W * H)})
        if where == "low" and out["low_hole_w"] == 0.0:
            out.update({"low_hole_w": w / W, "low_hole_h": h / H})
        if (hmask & stripe).any():
            sw, _, _, _ = _extent(hmask & stripe)
            if sw / W > out["stripe_hole_w"]:
                out.update({"stripe_hole_w": sw / W, "stripe_hole_h": h / H})

    if stripe.any():
        cols = np.flatnonzero(stripe.any(0))
        kept = stripe & (p == oc)
        runs = column_runs(kept.any(0)[cols], W)
        out.update({"stripe_pieces": runs["pieces"], "stripe_breaks": runs["breaks"], "stripe_break_w": runs["break_w"],
                    "stripe_end_gap": runs["end_gap"], "stripe_span": runs["span"]})
        have = kept.any(0)
        out["stripe_thickness"] = float(np.median(kept.sum(0)[have] / stripe.sum(0)[have])) if have.any() else 0.0

    X0, Y0, X1, Y1 = max(0, x0 - PAD), max(0, y0 - PAD), min(truth.shape[1], x1 + PAD), min(truth.shape[0], y1 + PAD)
    tt, pp = truth[Y0:Y1, X0:X1], pred[Y0:Y1, X0:X1]
    out["spill"] = float(((tt == 0) & np.isin(pp, (ORANGE, BLUE))).sum()) / n
    return out


def measure_box(pred: np.ndarray, box: tuple[int, int, int, int], color: int) -> dict:
    """What can be read without a hand mask, inside a hand-drawn box of a barrel with body color ``color``:

    core_cov        share of the box core (the box less 0.2 W each side and 0.1 H top and bottom) painted either
                    barrel color;
    upper_cov       share of the core's rows 0.1 H to 0.3 H painted the body color;
    stripe_*        the stripe color in the middle half of the box's rows, column by column over the full width:
                    pieces, breaks, widest break / W, first-to-last span / W;
    top_hole_w, _h  the largest unpainted hole (3 x 3 opening) of the core whose centre is above 0.4 H, / W, / H;
    mid_hole_w      the widest unpainted hole of the core reaching the rows 0.4 H to 0.6 H, / W.
    The core is at most 0.6 W wide and 0.8 H tall, so no hole reads larger than that."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    oc = other_color(color)
    p = pred[y0:y1, x0:x1]
    cx0, cx1 = int(round(CORE[0] * W)), int(round((1 - CORE[0]) * W))
    cy0, cy1 = int(round(CORE[1] * H)), int(round((1 - CORE[1]) * H))
    core = p[cy0:cy1, cx0:cx1]
    out = {"W": W, "H": H}
    if core.size == 0:
        return out
    paint = np.isin(core, (ORANGE, BLUE))
    out["core_cov"] = float(paint.mean())
    up = p[cy0:max(cy0 + 1, int(round(0.3 * H))), cx0:cx1]
    out["upper_cov"] = float((up == color).mean())
    band = p[int(round(0.25 * H)):int(round(0.75 * H))] == oc
    runs = column_runs(band.any(0), W)
    out.update({"stripe_pieces": runs["pieces"], "stripe_breaks": runs["breaks"], "stripe_break_w": runs["break_w"], "stripe_span": runs["span"]})
    out.update({"top_hole_w": 0.0, "top_hole_h": 0.0, "mid_hole_w": 0.0})
    m0, m1 = 0.4 * H - cy0, 0.6 * H - cy0
    for hmask in hole_components(~paint):
        w, h, _, cy = _extent(hmask)
        if cy < m0 and out["top_hole_w"] == 0.0:
            out.update({"top_hole_w": w / W, "top_hole_h": h / H})
        ys = np.flatnonzero(hmask.any(1))
        if ys.max() >= m0 and ys.min() < m1:
            out["mid_hole_w"] = max(out["mid_hole_w"], w / W)
    return out


def specks(pred: np.ndarray, boxes: list[tuple[int, int, int, int]], truth: np.ndarray | None = None) -> list[int]:
    """Areas (px, largest first) of the connected groups of barrel-colored pixels of ``pred`` that are more than
    ``PAD`` px outside every box of ``boxes`` (and, with a hand mask, where it says "other")."""
    free = np.isin(pred, (ORANGE, BLUE))
    if truth is not None:
        free &= truth == 0
    for x0, y0, x1, y1 in boxes:
        free[max(0, y0 - PAD):max(0, y1 + PAD), max(0, x0 - PAD):max(0, x1 + PAD)] = False
    n, _, stats, _ = cv2.connectedComponentsWithStats(free.astype(np.uint8), connectivity=8)
    return sorted((int(stats[i, cv2.CC_STAT_AREA]) for i in range(1, n)), reverse=True)


def speck_counts(areas: list[int]) -> dict:
    """``specks`` in three numbers: groups under ``SPECK_MAX`` px, groups of that size or more, the largest."""
    return {"specks": sum(a < SPECK_MAX for a in areas), "blobs": sum(a >= SPECK_MAX for a in areas),
            "speck_px": sum(a for a in areas if a < SPECK_MAX), "largest": max(areas, default=0)}
