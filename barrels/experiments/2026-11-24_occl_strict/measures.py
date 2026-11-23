"""The consistency facts of a real barrel, measured on each box the detector drew (census only; nothing here changes a box).

For every box: the EVIDENCE it was read from (the stripe, the cap piece, the band, the two slices, or the stripeless piece;
taken from the reason log), and these measures:

  front_box   share of the evidence box's area that lies inside the box of another drawn barrel standing NEARER (its
              bottom edge lower). A barrel cannot be seen through a nearer barrel: what lies inside the nearer one's
              outline is the nearer one's picture.
  front_sil   the same, with the nearer barrel's OUTLINE (rounded corners: the camera model's top and bottom lines for the
              distance its width gives) instead of its box. The logical version of front_box.
  front_px    the same as front_sil, counted on the evidence's barrel-colored pixels rather than its box area.
  own_top, own_bot
              the box's top (bottom) edge is a seen edge of this barrel: not inferred, and not against barrel color (barrel
              color, either one, in at least half of the box's columns in the 4 rows beyond it; edge_check's test).
  horizon     the body color joined to the evidence above it (the stripe step's walk, gaps of 3 rows) reaches the horizon row
              or above it. No barrel, near or far, reaches the horizon: the camera is higher than a barrel.
  below_horizon_bottom   the box's bottom row is below the horizon row (every barrel stands on the table).
"""
from __future__ import annotations

import math

import cv2
import numpy as np

from barrels import detector as det, geometry as geo
from barrels.io import BLUE, ORANGE

STAGE = {"barrel": "stripe", "cap": "cap", "pair": "post_pair", "slice": "slice", "half": "half_stripe", "piece": "piece"}


def evidence(log: list, b) -> tuple[str, tuple]:
    """(the stage that drew ``b``, the box of what it was read from)."""
    for e in reversed(log or []):
        if e.get("why") == "kept" and e.get("box") is not None and tuple(e["box"]) == tuple(b.bbox):
            ev = tuple(e["bbox"])
            if e.get("other") is not None:                        # post_pair: both slices
                o = tuple(e["other"])
                ev = (min(ev[0], o[0]), min(ev[1], o[1]), max(ev[2], o[2]), max(ev[3], o[3]))
            return STAGE.get(e["stage"], e["stage"]), ev
    return "piece", tuple(b.bbox)


def silhouette(F, cam: geo.CameraModel, shape) -> np.ndarray:
    """Bool mask of the outline of a barrel whose box is F.bbox: the box with the rounded corners the camera model gives
    at the distance its width says (scaled to the box's height)."""
    h, w = shape
    x0, y0, x1, y1 = F.bbox
    out = np.zeros(shape, bool)
    Wf = x1 - x0
    if Wf < 2 or y1 - y0 < 2:
        return out
    d = cam.f * geo.BARREL_BULGE_DIAMETER_MM / Wf
    try:
        ol = det.Outline.at(cam, d)
    except ValueError:
        out[y0:y1, x0:x1] = True
        return out
    scale = (y1 - y0) / max(1e-6, ol.bot_apex - ol.top_apex)
    cx = (x0 + x1) / 2
    for x in range(max(0, x0), min(w, x1)):
        u = (x + 0.5 - cx) / Wf
        t = y0 + scale * (float(ol.top(u)) - ol.top_apex)
        bt = y1 - scale * (ol.bot_apex - float(ol.bottom(u)))
        out[max(0, int(math.ceil(t))):min(h, int(math.floor(bt))), x] = True
    return out


def layout(F, cam: geo.CameraModel, shape) -> np.ndarray:
    """Per pixel, the color a barrel with box F.bbox shows there by its own layout (body, stripe, body): F.color in its body
    rows, the other color in its stripe rows (the stripe's rows by the camera model at the distance F's width gives, scaled to
    the box), 0 outside its outline; in the rows within half a stripe height of a seam, -1 (either color)."""
    out = np.zeros(shape, np.int8)
    sil = silhouette(F, cam, shape)
    x0, y0, x1, y1 = F.bbox
    d = cam.f * geo.BARREL_BULGE_DIAMETER_MM / max(1, x1 - x0)
    try:
        r = cam.barrel_rows(d)
    except ValueError:
        return out
    H = r.bottom - r.top
    s0 = y0 + (y1 - y0) * (r.stripe_top - r.top) / H
    s1 = y0 + (y1 - y0) * (r.stripe_bottom - r.top) / H
    m = (s1 - s0) / 2
    other = BLUE if F.color == ORANGE else ORANGE
    rows = np.arange(shape[0])[:, None] + 0.5
    lay = np.where((rows >= s0) & (rows < s1), other, F.color)
    seam = (np.abs(rows - s0) <= m) | (np.abs(rows - s1) <= m)
    lay = np.where(seam, -1, lay)
    out[sil] = np.broadcast_to(lay, shape)[sil]
    return out


def against(mask: np.ndarray, x0: int, x1: int, r0: int, r1: int) -> bool:
    h = mask.shape[0]
    band = mask[max(0, r0):max(0, min(h, r1)), max(0, x0):max(0, x1)]
    return band.size > 0 and float(np.isin(band, (ORANGE, BLUE)).any(axis=0).mean()) >= 0.5


def measure(mask: np.ndarray, found: list, log: list, cam: geo.CameraModel) -> list[dict]:
    h, w = mask.shape
    hz = cam.horizon_row()
    barrel = np.isin(mask, (ORANGE, BLUE))
    sil = {id(F): silhouette(F, cam, mask.shape) for F in found}
    lay = {id(F): layout(F, cam, mask.shape) for F in found}
    allbox = np.zeros(mask.shape, np.int16)
    for F in found:
        allbox[F.bbox[1]:F.bbox[3], F.bbox[0]:F.bbox[2]] += 1
    rows = []
    for b in found:
        stage, ev = evidence(log, b)
        ex0, ey0, ex1, ey1 = (max(0, ev[0]), max(0, ev[1]), min(w, ev[2]), min(h, ev[3]))
        area = max(1, (ex1 - ex0) * (ey1 - ey0))
        nearer = [F for F in found if F is not b and F.bbox[3] > b.bbox[3]]
        inbox = np.zeros(mask.shape, bool)
        insil = np.zeros(mask.shape, bool)
        explained = np.zeros(mask.shape, bool)
        for F in nearer:
            inbox[F.bbox[1]:F.bbox[3], F.bbox[0]:F.bbox[2]] = True
            insil |= sil[id(F)]
            L = lay[id(F)]
            explained |= (L == -1) | ((L > 0) & (L == mask))
        evpix = barrel[ey0:ey1, ex0:ex1]
        n_ev = int(evpix.sum())
        x0, y0, x1, y1 = b.bbox
        own_top = "top_inferred" not in b.flags and y0 > 0 and not against(mask, x0, x1, y0 - 4, y0)
        own_bot = "bottom_inferred" not in b.flags and y1 < h and not against(mask, x0, x1, y1, y1 + 4)
        top_walk, _ = det._body_extent(mask, b.color, ex0, ex1, ey0, ey1) if ex1 > ex0 and ey1 > ey0 else (ey0, ey1)
        # extent: the box's own color resuming beyond a SEEN top (bottom) within a stripe-height-and-a-half gap, beyond the
        # 3-row gap the body walk allows, in the evidence's columns, not inside another drawn box
        Hs = math.nan
        d = cam.f * geo.BARREL_BULGE_DIAMETER_MM / max(1, x1 - x0)
        try:
            r = cam.barrel_rows(cam.d_axis_from_bottom_row(y1) if y1 < h else d)
            Hs = r.stripe_bottom - r.stripe_top
        except ValueError:
            pass
        g = int(math.ceil(1.6 * Hs)) if math.isfinite(Hs) else 0
        own_box = np.zeros(mask.shape, bool); own_box[y0:y1, x0:x1] = True
        free = (mask == b.color) & ((allbox == 0) | ((allbox == 1) & own_box))
        def resumes(r0, r1):
            band = free[max(0, r0):max(0, min(h, r1)), ex0:ex1]
            return float(band.any(axis=0).mean()) if band.size else 0.0
        above = resumes(y0 - 4 - g, y0 - 4) if "top_inferred" not in b.flags and g else 0.0
        below = resumes(y1 + 4, y1 + 4 + g) if "bottom_inferred" not in b.flags and g else 0.0
        # side extent: the body color joined to the evidence (the stripe step's _body_span over the box's rows, the evidence rows
        # left out), with the columns of every OTHER drawn box of this color removed, in barrel widths W (W from the evidence's
        # row by the camera model for a stripe; the box's width otherwise)
        side = math.nan
        if ex1 > ex0 and y1 - y0 >= 2:
            g2 = det._stripe_geometry(cam, (ey0 + ey1) / 2) if stage in ("stripe", "slice", "post_pair") else None
            Wx = g2[1].width_px if g2 is not None else float(x1 - x0)
            others = tuple((F.bbox[0], F.bbox[2]) for F in found if F is not b and F.color == b.color)
            sp = det._body_span(mask, b.color, ex0, ex1, max(0, y0), min(h, y1), ey0, ey1, others)
            if sp is not None and Wx > 0:
                side = (max(sp[1], ex1) - min(sp[0], ex0)) / Wx
        # vertical extent: an inferred edge whose body runs on PAST it (taller than the barrel) rather than stopping short of it
        over_top = over_bot = 0
        if ex1 > ex0 and ey1 > ey0:
            tw, bw_ = det._body_extent(mask, b.color, ex0, ex1, ey0, ey1)
            over_top = int("top_inferred" in b.flags and tw < y0)
            over_bot = int("bottom_inferred" in b.flags and bw_ > y1)
        # the whole band: the connected region of the stripe color holding the evidence stripe (closed mask, 8-connected), without
        # the pixels inside any OTHER drawn box; its height (10th to 90th percentile of its rows) in expected stripe heights and its
        # width in barrel widths, both at the evidence's row
        band_h = band_w = math.nan
        if stage in ("stripe", "slice", "post_pair") and ex1 > ex0 and ey1 > ey0:
            g3 = det._stripe_geometry(cam, (ey0 + ey1) / 2)
            if g3 is not None:
                sc = BLUE if b.color == ORANGE else ORANGE
                cm = det._closed(mask == sc, det.DetConfig())
                n_, lab_ = cv2.connectedComponents(cm.astype(np.uint8), connectivity=8)
                ids = np.unique(lab_[ey0:ey1, ex0:ex1][(mask[ey0:ey1, ex0:ex1] == sc)])
                ids = ids[ids > 0]
                if len(ids):
                    reg = np.isin(lab_, ids)
                    for F in found:
                        if F is not b:
                            reg[F.bbox[1]:F.bbox[3], F.bbox[0]:F.bbox[2]] = False
                    ys, xs = np.nonzero(reg)
                    if len(ys):
                        Hs3 = g3[1].stripe_bottom - g3[1].stripe_top
                        band_h = (np.percentile(ys, 90) - np.percentile(ys, 10) + 1) / Hs3
                        band_w = (xs.max() - xs.min() + 1) / g3[1].width_px
        rows.append(dict(
            band_h=round(band_h, 3) if math.isfinite(band_h) else "", band_w=round(band_w, 3) if math.isfinite(band_w) else "",
            over_top=over_top, over_bot=over_bot,
            stage=stage, ev=ev, side=round(side, 3) if math.isfinite(side) else "",
            front_box=round(float(inbox[ey0:ey1, ex0:ex1].sum()) / area, 3),
            front_sil=round(float(insil[ey0:ey1, ex0:ex1].sum()) / area, 3),
            front_px=round(float((insil[ey0:ey1, ex0:ex1] & evpix).sum()) / max(1, n_ev), 3),
            front_lay=round(float((insil[ey0:ey1, ex0:ex1] & explained[ey0:ey1, ex0:ex1] & evpix).sum()) / max(1, n_ev), 3),
            own_top=int(own_top), own_bot=int(own_bot),
            horizon=int(top_walk <= hz),
            above=round(above, 3), below=round(below, 3),
            below_horizon_bottom=int(y1 > hz),
        ))
    return rows
