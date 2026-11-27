"""The stage-11 variants of addendum 3 (plan: PREREG.md). A post-filter on the ten stages' boxes (``Found``); nothing
here is in the detector. Each variant is a set of (reading, number) choices:

- ``solid``: None, or ("closed", t): the adopted reading (``detector.paint_readings``, closed 3 x 3) under t; or
  ("raw", t): solidity without the closing (round 1, the experiment's) under t.
- ``raw_speckle_edge_ok``: with ("raw", t), a box that touches the frame edge is not asked.
- ``label``: None, or (reading, stripe, body, exclude): reading "col" = the adopted one (column median, body in the
  stripe's columns); "row" = round 1 (rows of the stripe's box, body over the whole box). ``exclude``: pixels inside
  a nearer box (another box of the list whose bottom edge is strictly lower; any color) are left out of both
  readings; a box with nothing left to read is not asked.

Every box of the list is asked; a reading that cannot be made never drops a box."""
from __future__ import annotations

import math

import cv2
import numpy as np

from barrels import detector as det
from barrels.io import BLUE, ORANGE

VARIANTS = {
    "none": {},
    "V0_adopted": {"solid": ("closed", 0.40), "label": ("col", 1.5, 0.6, False)},
    "V1_fusion_mild": {"solid": ("raw", 0.35), "label": ("row", 1.5, 0.6, False)},
    "V2_row_label_excl": {"solid": ("closed", 0.40), "label": ("row", 1.5, 0.6, True)},
    "V3_col_label_125_excl": {"solid": ("closed", 0.40), "label": ("col", 1.25, 0.6, True)},
    "V4_raw_speckle_025": {"solid": ("closed", 0.40), "raw": ("raw", 0.25), "label": ("col", 1.5, 0.6, False)},
    "V5_V2_plus_V4": {"solid": ("closed", 0.40), "raw": ("raw", 0.25), "label": ("row", 1.5, 0.6, True)},
}


def _at(f, cam):
    return det._at(f.stripe, cam) if f.stripe is not None else det.BarrelAt.from_top_row(cam, f.barrel.bbox[1])


def raw_solid(f, mask) -> float:
    x0, y0, x1, y1 = f.barrel.bbox
    box = mask[y0:y1, x0:x1]
    colored = (box == ORANGE) | (box == BLUE)
    if not box.size or not colored.any():
        return math.nan
    er = cv2.erode(colored.astype(np.uint8), np.ones((3, 3), np.uint8), borderType=cv2.BORDER_REPLICATE)
    return float(er.sum()) / float(colored.sum())


def covered(f, found, shape) -> np.ndarray:
    """Pixels of the frame inside a nearer box (bottom strictly lower), as bool."""
    cov = np.zeros(shape, bool)
    for g in found:
        if g is f or g.barrel.bbox[3] <= f.barrel.bbox[3]:
            continue
        a0, b0, a1, b1 = g.barrel.bbox
        cov[b0:b1, a0:a1] = True
    return cov


def label_readings(f, found, mask, cam, reading: str, exclude: bool):
    """(stripe height over a stripe height, body share), nan when not readable."""
    at = _at(f, cam)
    if at is None or f.stripe is None:
        return math.nan, math.nan
    b = f.barrel
    x0, y0, x1, y1 = b.bbox
    other = det._other(b.color)
    cov = covered(f, found, mask.shape) if exclude else np.zeros(mask.shape, bool)
    sx0, s_top, sx1, s_bot = f.stripe.bbox
    st = (mask[s_top:s_bot, sx0:sx1] == other) & ~cov[s_top:s_bot, sx0:sx1]
    sh = math.nan
    if reading == "row":
        rows = np.flatnonzero(st.any(axis=1))
        if rows.size:
            sh = float(np.percentile(rows, 90) - np.percentile(rows, 10) + 1) / at.Hs
        c0, c1 = 0, x1 - x0
    else:
        spans = [np.percentile(r, 90) - np.percentile(r, 10) + 1 for r in (np.flatnonzero(c) for c in st.T) if r.size]
        if spans:
            sh = float(np.median(spans)) / at.Hs
        c0, c1 = (max(sx0, x0) - x0, min(sx1, x1) - x0) if min(sx1, x1) > max(sx0, x0) else (0, x1 - x0)
    keep = np.ones(y1 - y0, bool)
    keep[max(0, s_top - y0):max(0, min(y1, s_bot) - y0)] = False
    box = mask[y0:y1, x0:x1][keep][:, c0:c1]
    ok = ~cov[y0:y1, x0:x1][keep][:, c0:c1]
    body = float((box[ok] == b.color).mean()) if ok.any() else math.nan
    return sh, body


def apply(found: list, mask: np.ndarray, cam, spec: dict) -> list:
    """The boxes of ``found`` that the variant keeps (``Found`` objects, same order)."""
    if not spec:
        return list(found)
    H, W = mask.shape
    out = []
    for f in found:
        at = _at(f, cam)
        if at is None:
            out.append(f)
            continue
        x0, y0, x1, y1 = f.barrel.bbox
        drop = False
        s = spec.get("solid")
        if s and s[0] == "closed":
            r = det.paint_readings(f, mask, cam, det.DetConfig())
            drop |= r is not None and r[0] < s[1]
        rw = spec.get("raw")
        if rw and not drop and not (x0 == 0 or y0 == 0 or x1 == W or y1 == H):
            drop |= raw_solid(f, mask) < rw[1]
        if s and s[0] == "raw" and not drop:
            drop |= raw_solid(f, mask) < s[1]
        lb = spec.get("label")
        if lb and not drop:
            sh, body = label_readings(f, found, mask, cam, lb[0], lb[3])
            drop |= sh > lb[1] and body < lb[2]
        if not drop:
            out.append(f)
    return out
