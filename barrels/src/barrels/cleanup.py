"""Mask cleanup stages (v1.5): small-blob removal, morphological opening, hole filling.
All default-off in pipeline.Config, applied after the class decision; they never change pixel
values, only which pixels carry a class.
"""
from __future__ import annotations

import cv2
import numpy as np

from .io import BLUE, ORANGE, OTHER

CLASSES = (ORANGE, BLUE)


def remove_small_blobs(mask: np.ndarray, min_px: int, classes=CLASSES) -> np.ndarray:
    """Per class, 8-connected components smaller than min_px become OTHER."""
    if min_px <= 0:
        return mask
    out = mask.copy()
    for c in classes:
        n, lab, st, _ = cv2.connectedComponentsWithStats((mask == c).astype(np.uint8), connectivity=8)
        small = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] < min_px]
        if small:
            out[np.isin(lab, small)] = OTHER
    return out


def open_mask(mask: np.ndarray, k: int, classes=CLASSES) -> np.ndarray:
    """Per-class binary opening with a k×k kernel (k odd, ≥ 3); removes thin bridges and specks."""
    if k < 3:
        return mask
    k = k if k % 2 else k + 1
    kern = np.ones((k, k), np.uint8)
    out = mask.copy()
    for c in classes:
        sel = (mask == c).astype(np.uint8)
        opened = cv2.morphologyEx(sel, cv2.MORPH_OPEN, kern) > 0
        out[(sel > 0) & ~opened] = OTHER
    return out


def fill_holes(mask: np.ndarray, classes=CLASSES) -> np.ndarray:
    """Per class, OTHER regions fully enclosed by that class (not touching the image border and
    not containing another class) take the class."""
    out = mask.copy()
    h, w = mask.shape
    for c in classes:
        sel = (mask == c).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats((1 - sel).astype(np.uint8), connectivity=4)
        for i in range(1, n):
            x, y, bw, bh, _ = st[i]
            if x == 0 or y == 0 or x + bw == w or y + bh == h:
                continue                                            # touches the border: not a hole
            region = lab == i
            if (mask[region] != OTHER).any():
                continue                                            # contains another class
            out[region] = c
    return out


def apply(mask: np.ndarray, cfg) -> np.ndarray:
    """Apply the cleanup stages in cfg order: open -> remove small blobs -> fill holes."""
    out = mask
    if getattr(cfg, "open_px", 0):
        out = open_mask(out, cfg.open_px)
    if getattr(cfg, "min_blob_px", 0):
        out = remove_small_blobs(out, cfg.min_blob_px)
    if getattr(cfg, "fill_holes", False):
        out = fill_holes(out)
    return out
