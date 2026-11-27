"""``detector.detect`` with what each box was drawn from kept (``Found``: its rule and its stripe), and the
measurements of part B on one box. Nothing here changes what the detector draws: ``found(mask)`` is the ten lines
of ``detector.detect`` and returns the same boxes in the same order (``check_same.py`` proves it on every input of
the proof harness).

The measurements of a box (``measure``), all read from the class mask (0 other, 1 orange, 2 blue) and the camera
model; ``at`` is the barrel the geometry expects at the box's own reading (its stripe's row; a box with no stripe:
its top row, as the caps and close-ups use):

- ``w_ratio``, ``h_ratio``: the box's width and height over W and H at that row.
- ``seen_w_ratio``: the widest run of barrel color (body or stripe) in the stripe's rows (or the box's middle
  third) over W.
- ``fill``: the share of the box's pixels that are barrel color (either color).
- ``body_fill``: the share of the box's pixels outside the stripe's rows that are body color.
- ``top_err``, ``bot_err``: where the body color's seen top and bottom are, minus where the row predicts them, in
  units of H (nan when the body does not show there).
- ``stripe_h_ratio``: the stripe's seen height (10th-90th percentile of its rows, as ``find_stripes``) over the
  predicted stripe height; ``stripe_over_body``: the stripe's seen height over the seen body height.
- ``up_share``, ``low_share``: the share of body color in the band above the stripe and in the band below it (each
  as tall as the row predicts, in the stripe's columns); ``bands_alike``: the smaller over the larger.
- ``bulge``: the body's width in the upper and lower quarter of the seen body, over its width at the stripe: a
  barrel is widest at its middle (about 0.85-0.95 at the ends seen from this camera); a box or a tin is not.
- ``aspect``: the seen barrel-colored part's width over its height, over W / H.
"""
from __future__ import annotations

import math

import numpy as np

from barrels import detector as det
from barrels import geometry as geo
from barrels.io import BLUE, ORANGE

CAM = geo.AIM_4A8B6118_BOXFIT


def found(mask: np.ndarray, cfg: det.DetConfig = det.DetConfig(), cam: geo.CameraModel = CAM) -> list[det.Found]:
    """The ten stages of ``detector.detect``, the same calls in the same order; the ``Found`` list, left to right."""
    log = None
    layers = det.sandwiches(mask, cam, cfg)
    pieces = det.find_pieces(mask, cam, cfg, log)
    stripes, leftover = det.find_stripes(mask, cam, cfg, log, layers)
    fs, unplaced, lost = det.boxes_from_stripes(stripes, mask, cam, cfg, log)
    fs = fs + det.closeup_pieces(pieces, fs, mask, cam, cfg, log)
    fs = det.drop_seen_through(fs, mask, cam, cfg, log)
    fs = fs + det.caps_behind(fs, lost, mask, cam, cfg, log)
    fs = fs + det.post_pairs(leftover + unplaced, fs, mask, cam, cfg, log)
    fs = det.half_stripes(fs, mask, cam, cfg, log, layers)
    fs = det.drop_seen_through(fs, mask, cam, cfg, log)
    fs = det.drop_single_reading(fs, mask, cam, cfg, log)
    return sorted(fs, key=lambda f: f.barrel.bbox[0])


def expected(f: det.Found, cam: geo.CameraModel = CAM) -> det.BarrelAt | None:
    """The barrel the geometry expects for this box: from its stripe's centre row; with no stripe, from its top row."""
    if f.stripe is not None:
        return det._at(f.stripe, cam)
    return det.BarrelAt.from_top_row(cam, f.barrel.bbox[1])


def _runs_max(row: np.ndarray) -> int:
    """The longest run of True in a 1-D bool array."""
    if not row.any():
        return 0
    d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
    s, e = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    return int((e - s).max())


def _span(cols: np.ndarray) -> float:
    """The width of a bool column profile: from its 5th to its 95th percentile column (nan if empty)."""
    x = np.flatnonzero(cols)
    if x.size < 2:
        return float("nan")
    return float(np.percentile(x, 95) - np.percentile(x, 5) + 1)


NAN = float("nan")


def measure(f: det.Found, mask: np.ndarray, cam: geo.CameraModel = CAM) -> dict:
    b = f.barrel
    x0, y0, x1, y1 = b.bbox
    H_img, W_img = mask.shape
    body = b.color
    other = BLUE if body == ORANGE else ORANGE
    at = expected(f, cam)
    out = {"rule": f.rule, "color": "orange" if body == ORANGE else "blue", "x0": x0, "y0": y0, "x1": x1, "y1": y1,
           "w": x1 - x0, "h": y1 - y0}
    if at is None:
        return out
    W, H, Hs = at.W, at.H, at.Hs
    out.update(W=round(W, 2), H=round(H, 2), Hs=round(Hs, 2), w_ratio=(x1 - x0) / W, h_ratio=(y1 - y0) / H)
    box = mask[y0:y1, x0:x1]
    colored = (box == ORANGE) | (box == BLUE)
    out["fill"] = float(colored.mean()) if box.size else NAN
    # the stripe's rows: the stripe the box was read from, else the rows the geometry predicts
    if f.stripe is not None:
        sx0, sy0, sx1, sy1 = f.stripe.bbox
        st = mask[sy0:sy1, sx0:sx1] == other
        rows = np.flatnonzero(st.any(axis=1)) + sy0
        if rows.size:
            r10, r90 = np.percentile(rows, 10), np.percentile(rows, 90)
            out["stripe_h"] = float(r90 - r10 + 1)
        s_top, s_bot = sy0, sy1
    else:
        s_top, s_bot = int(round(at.rows.stripe_top)), int(round(at.rows.stripe_bottom))
        sx0, sx1 = x0, x1
    out["stripe_h_ratio"] = out.get("stripe_h", NAN) / Hs
    # body outside the stripe rows, inside the box
    keep = np.ones(y1 - y0, bool)
    a, z = max(0, s_top - y0), max(0, min(y1, s_bot) - y0)
    keep[a:z] = False
    out["body_fill"] = float((box[keep] == body).mean()) if keep.any() else NAN
    # seen body extent in the stripe's columns, searched one H above and below the box
    cx0, cx1 = max(0, sx0), min(W_img, sx1)
    ya, yb = max(0, int(y0 - 0.3 * H)), min(H_img, int(y1 + 0.3 * H))
    colb = (mask[ya:yb, cx0:cx1] == body)
    prof = colb.mean(axis=1) if colb.size else np.zeros(0)
    seen = np.flatnonzero(prof >= 0.25) + ya
    if seen.size:
        out["seen_top"], out["seen_bot"] = int(seen.min()), int(seen.max()) + 1
        out["top_err"] = (seen.min() - at.top) / H
        out["bot_err"] = (seen.max() + 1 - at.bottom) / H
        seen_h = seen.max() + 1 - seen.min()
        out["stripe_over_body"] = out.get("stripe_h", NAN) / seen_h if seen_h else NAN
    else:
        out["top_err"] = out["bot_err"] = out["stripe_over_body"] = NAN
    # body bands above / below the stripe, each as tall as the row predicts
    up_h = max(1, int(round(at.rows.stripe_top - at.rows.top)))
    lo_h = max(1, int(round(at.rows.bottom - at.rows.stripe_bottom)))
    ub = mask[max(0, s_top - up_h):max(0, s_top), cx0:cx1]
    lb = mask[min(H_img, s_bot):min(H_img, s_bot + lo_h), cx0:cx1]
    up = float((ub == body).mean()) if ub.size else NAN
    lo = float((lb == body).mean()) if lb.size else NAN
    out["up_share"], out["low_share"] = up, lo
    out["bands_alike"] = (min(up, lo) / max(up, lo)) if (np.isfinite(up) and np.isfinite(lo) and max(up, lo) > 0) else NAN
    # widest run of barrel color in the stripe's rows
    band = mask[max(0, s_top):min(H_img, s_bot), max(0, int(x0 - 0.3 * W)):min(W_img, int(x1 + 0.3 * W))]
    bc = (band == ORANGE) | (band == BLUE)
    out["seen_w_ratio"] = (max((_runs_max(r) for r in bc), default=0) / W) if bc.size else NAN
    # bulge: body width at the upper and lower quarter of the seen body, over the width at the stripe
    if seen.size and (seen.max() - seen.min()) >= 6:
        t0, t1 = int(seen.min()), int(seen.max()) + 1
        q = max(1, (t1 - t0) // 4)
        xa, xb = max(0, int(x0 - 0.2 * W)), min(W_img, int(x1 + 0.2 * W))
        reg = mask[:, xa:xb]
        def width_at(r0, r1, color_ok):
            sub = reg[max(0, r0):min(H_img, r1)]
            ok = np.isin(sub, color_ok)
            if not ok.size:
                return NAN
            return float(np.median([_runs_max(r) for r in ok]))
        mid = width_at(s_top, s_bot, (ORANGE, BLUE))
        top_w = width_at(t0, t0 + q, (body,))
        bot_w = width_at(t1 - q, t1, (body,))
        out["bulge_top"] = top_w / mid if mid else NAN
        out["bulge_bot"] = bot_w / mid if mid else NAN
        # seen part: its width over its height, over W / H
        allc = (mask[t0:t1, xa:xb] == ORANGE) | (mask[t0:t1, xa:xb] == BLUE)
        sw = _span(allc.any(axis=0))
        out["aspect"] = (sw / (t1 - t0)) / (W / H) if np.isfinite(sw) else NAN
    else:
        out["bulge_top"] = out["bulge_bot"] = out["aspect"] = NAN
    # the stripe's width over W
    if f.stripe is not None:
        out["stripe_w_ratio"] = (f.stripe.bbox[2] - f.stripe.bbox[0]) / W
    # what is around the box: barrel color (either) in strips 0.25 W wide just left and right of the box, at the
    # box's rows, and in a strip 0.25 H tall just above it, over the box's columns
    anyc = (mask == ORANGE) | (mask == BLUE)
    sw_ = max(2, int(round(0.25 * W)))
    sh_ = max(2, int(round(0.25 * H)))
    left = anyc[y0:y1, max(0, x0 - sw_):x0]
    right = anyc[y0:y1, x1:min(W_img, x1 + sw_)]
    above = anyc[max(0, y0 - sh_):y0, x0:x1]
    lv = float(left.mean()) if left.size else NAN
    rv = float(right.mean()) if right.size else NAN
    out["ring_left"], out["ring_right"] = lv, rv
    out["ring_lr_min"] = min(lv, rv) if np.isfinite(lv) and np.isfinite(rv) else (lv if np.isfinite(lv) else rv)
    out["ring_top"] = float(above.mean()) if above.size else NAN
    # solidity: of the barrel-colored pixels in the box, the share whose 3 x 3 neighbourhood is all barrel color
    if box.size and colored.any():
        import cv2
        er = cv2.erode(colored.astype(np.uint8), np.ones((3, 3), np.uint8), borderType=cv2.BORDER_REPLICATE)
        out["solid"] = float(er.sum()) / float(colored.sum())
    return {k: (round(v, 4) if isinstance(v, float) and math.isfinite(v) else v) for k, v in out.items()}
