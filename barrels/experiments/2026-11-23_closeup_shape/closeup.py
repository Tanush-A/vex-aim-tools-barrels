"""Shared by the scripts of this experiment (TODO A9): paths, the arms, and the cues measured on a frame-bottom piece."""
from __future__ import annotations

import dataclasses
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
COMB = EXP / "2026-11-20_occl_combined"      # the battery (scorecard, eval table, damage levels, recordings), loaded by path
sys.path.insert(0, str(HERE.parents[1] / "src"))

from barrels import detector as det, geometry as geo  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-23_closeup_shape"
_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}
NEW = ("closeup_side", "closeup_stripe")   # this experiment's switches (PREREG.md); pinned off in START
START = det.DetConfig(**{k: False for k in NEW + ("verify_front", "verify_readings") if k in _FIELDS})      # origin/barrels e0d01e0, field by field (2026-11-24: occl_strict's switches pinned off too)
ARMS = {"start": START}
if set(NEW) <= _FIELDS:
    ARMS["side"] = dataclasses.replace(START, closeup_side=True)       # rule A
    ARMS["stripe"] = dataclasses.replace(START, closeup_stripe=True)   # rule B
    ARMS["shape"] = dataclasses.replace(START, closeup_side=True, closeup_stripe=True)   # A + B, the candidate default
ARMS["defaults"] = det.DetConfig()       # NOT pinned


def battery():
    """The combined experiment's ``common`` module with this experiment's arms in its arm table and its output folder."""
    sys.path.insert(0, str(COMB))
    import common as C  # noqa: E402  (the combined experiment's shared module)
    C.A.ARMS.update(ARMS)
    C.OUT = C.A.OUT = OUT
    C.RULE_ARMS = tuple(ARMS)
    return C


def cues(mask: np.ndarray, pixels: np.ndarray, box, color: int, cam: geo.CameraModel) -> dict:
    """The candidate cues of one frame-bottom piece (its pixels; box = x0, y0, x1, frame height)."""
    h, w = mask.shape
    x0, y0, x1, y1 = box
    other = BLUE if color == ORANGE else ORANGE
    sub = pixels[y0:y1, x0:x1]
    msub = mask[y0:y1, x0:x1]
    area = sub.sum()
    d = cam._d_axis_from_point_row(y0, geo.BARREL_HEIGHT_MM, +geo.BARREL_END_DIAMETER_MM / 2)
    W = cam.f * geo.BARREL_BULGE_DIAMETER_MM / d if d > 0 and math.isfinite(d) else math.inf
    try:
        rows = cam.barrel_rows(d) if d > 0 and math.isfinite(d) else None
    except ValueError:                    # the base would be at or behind the camera
        rows = None
    H = (rows.bottom - rows.top) if rows else math.inf
    cols = np.flatnonzero(sub.any(axis=0))
    tops = np.array([np.flatnonzero(sub[:, c])[0] for c in range(sub.shape[1]) if sub[:, c].any()], float)
    # row-wise fill: in each row, the share of the span between the first and the last piece pixel that is the body color
    fills = []
    for r in range(sub.shape[0]):
        xs = np.flatnonzero(sub[r])
        if len(xs) >= 2:
            fills.append((msub[r, xs[0]:xs[-1] + 1] == color).mean())
    seen_h = y1 - y0
    cut_l, cut_r = x0 == 0, x1 == w
    # the top: share of the columns whose top lies within one tenth of a barrel height of the top row (a flat lid edge
    # seen from above is an arc: its ends are lower by (top_end - top_apex) + the shoulder)
    flat = float((tops <= 0.1 * H).mean()) if len(tops) and math.isfinite(H) else math.nan
    # the upper body: a barrel whose top is at y0 shows its body color from y0 down to its stripe's top row (or the frame
    # bottom when the stripe is below the frame). reach = how much of that is seen (the piece's seen bottom row)
    seen_y1 = int(np.flatnonzero(pixels.any(axis=1)).max()) + 1
    try:
        st = cam.barrel_rows(d).stripe_top if d > 0 and math.isfinite(d) else math.inf
    except ValueError:
        st = math.inf
    upper = min(h, st) - y0
    # the top line at each end of the piece against the barrel's outline at the distance its top row gives, the end taken
    # as the barrel's own side (``detector._end_costs`` on the top line alone: shape only, median offset removed; barrel heights)
    cost_l = cost_r = math.nan
    if math.isfinite(W) and math.isfinite(H) and H > 0 and len(cols) >= 2:
        ol = det.Outline.at(cam, d)
        tl = np.full(x1 - x0, np.nan)
        for c in cols:
            tl[c] = y0 + np.flatnonzero(sub[:, c])[0]
        xs = np.arange(x0, x1) + 0.5

        def cost(left: bool) -> float:
            centre = x0 + W / 2 if left else x1 - W / 2
            near = (xs - x0 <= det.LID_HALF * W) if left else (x1 - xs <= det.LID_HALF * W)
            v = tl[near]; u = (xs[near] - centre) / W
            ok = ~np.isnan(v)
            if ok.sum() < 2:
                return math.inf
            r = v[ok] - ol.top(u[ok])
            return float(np.mean(np.abs(r - np.median(r)))) / H
        cost_l, cost_r = cost(True), cost(False)
    out = dict(
        cost_l=round(cost_l, 3), cost_r=round(cost_r, 3),
        st_pred=round(st, 1) if math.isfinite(st) else "below", upper=round(upper, 1),
        reach=round((seen_y1 - y0) / upper, 2) if upper > 0 else math.nan,
        # the pre-registered rule (PREREG.md): a piece the frame's side cuts must be seen down to min(h, stripe top) within
        # max(bottom_tol_min_px, bottom_tol x that height)
        rule_pass=int(not (cut_l or cut_r) or seen_y1 >= min(h, st) - max(det.DetConfig().bottom_tol_min_px, det.DetConfig().bottom_tol * upper)),
        Wtop=round(W, 1), ratio=round((x1 - x0) / W, 2) if math.isfinite(W) else math.nan,
        cut_l=int(cut_l), cut_r=int(cut_r), seen_h=seen_h, Hpred=round(H, 1),
        h_ratio=round(seen_h / H, 2) if math.isfinite(H) and H > 0 else math.nan,
        y0_below_horizon=round(y0 - cam.horizon_row(), 1),
        fill_box=round(float(area) / max(1, sub.size), 2),
        body=round(float((msub[sub] == color).mean()), 2), other=round(float((msub[sub] == other).mean()), 2),
        row_fill=round(float(np.median(fills)), 2) if fills else math.nan,
        row_fill_p10=round(float(np.percentile(fills, 10)), 2) if fills else math.nan,
        top_flat=round(flat, 2),
    )
    return out
