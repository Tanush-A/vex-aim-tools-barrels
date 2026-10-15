"""Semi-automatic label growing: hand strokes -> full per-pixel mask.

Stroke values (what the label tool paints):
    0 unlabeled   1 orange   2 blue   3 table/background   4 glare/uncertain

``grow`` seeds a marker-based watershed (cv2.watershed) with the strokes, so every
pixel gets the class of the nearest seed in gradient terms, then maps stroke classes
to mask values (docs/DATA.md) and burns the strokes back in as hard overrides.
"""
from __future__ import annotations

import cv2
import numpy as np

from .io import BLUE, IGNORE, ORANGE, OTHER

STROKE_UNLABELED, STROKE_ORANGE, STROKE_BLUE, STROKE_BG, STROKE_IGNORE = 0, 1, 2, 3, 4
STROKE_VALUES = (STROKE_UNLABELED, STROKE_ORANGE, STROKE_BLUE, STROKE_BG, STROKE_IGNORE)
STROKE_NAMES = {0: "eraser", 1: "orange", 2: "blue", 3: "background", 4: "ignore"}
STROKE_TO_MASK = {STROKE_ORANGE: ORANGE, STROKE_BLUE: BLUE, STROKE_BG: OTHER, STROKE_IGNORE: IGNORE}


def strokes_to_mask(strokes: np.ndarray) -> np.ndarray:
    """Map stroke classes to mask values; unlabeled pixels become OTHER."""
    mask = np.full(strokes.shape, OTHER, np.uint8)
    for sv, mv in STROKE_TO_MASK.items():
        mask[strokes == sv] = mv
    return mask


def burn_strokes(mask: np.ndarray, strokes: np.ndarray) -> np.ndarray:
    """Return a copy of ``mask`` with every stroked pixel forced to its stroke class."""
    out = mask.copy()
    for sv, mv in STROKE_TO_MASK.items():
        out[strokes == sv] = mv
    return out


def _fill_boundaries(markers: np.ndarray, max_iter: int = 8) -> np.ndarray:
    """Replace watershed boundary pixels (-1) with the majority class of their 3x3 neighbours."""
    lab = markers.copy()
    lab[lab < 0] = 0
    kernel = np.ones((3, 3), np.float32)
    for _ in range(max_iter):
        holes = lab == 0
        if not holes.any():
            break
        best = np.zeros(lab.shape, np.int32)
        best_count = np.zeros(lab.shape, np.float32)
        for c in np.unique(lab[lab > 0]):
            count = cv2.filter2D((lab == c).astype(np.float32), -1, kernel, borderType=cv2.BORDER_CONSTANT)
            better = count > best_count
            best[better] = c
            best_count[better] = count[better]
        lab[holes] = best[holes]
    return lab


def grow(image_bgr: np.ndarray, strokes: np.ndarray, auto_bg_rows: int = 10, blur: int = 3) -> np.ndarray:
    """Grow sparse strokes into a full mask.

    auto_bg_rows: the top N rows are seeded as background where unstroked (rows above
        the horizon can never be barrel — constraints.md; 10 is safely inside the
        conservative ~25-row band).
    blur: Gaussian kernel size applied before watershed (0 = none); smooths texture
        so the flood follows object edges, not wood grain.
    Returns a mask in docs/DATA.md values. Stroked pixels always keep their stroke class.
    """
    if image_bgr.shape[:2] != strokes.shape:
        raise ValueError(f"image {image_bgr.shape[:2]} and strokes {strokes.shape} differ in size")
    markers = strokes.astype(np.int32)
    if auto_bg_rows > 0:
        top = markers[:auto_bg_rows]
        top[top == STROKE_UNLABELED] = STROKE_BG
    if not (markers > 0).any():
        return np.full(strokes.shape, OTHER, np.uint8)
    img = image_bgr
    if blur and blur > 1:
        k = blur if blur % 2 else blur + 1
        img = cv2.GaussianBlur(image_bgr, (k, k), 0)
    cv2.watershed(np.ascontiguousarray(img), markers)  # in place; -1 marks boundaries
    labels = _fill_boundaries(markers)
    mask = np.full(strokes.shape, OTHER, np.uint8)
    for sv, mv in STROKE_TO_MASK.items():
        mask[labels == sv] = mv
    return burn_strokes(mask, strokes)
