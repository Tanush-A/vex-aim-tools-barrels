import cv2
import numpy as np

from barrels import io
from barrels import labeling as lab


def synthetic_scene():
    """120x160 BGR: dark table, gray wall on top, an orange disc left, a blue disc right."""
    img = np.zeros((120, 160, 3), np.uint8)
    img[:] = (30, 30, 30)            # table
    img[:40] = (150, 150, 150)       # wall
    cv2.circle(img, (45, 80), 22, (0, 128, 255), -1)   # orange (BGR)
    cv2.circle(img, (115, 80), 22, (255, 100, 0), -1)  # blue
    truth = np.full(img.shape[:2], io.OTHER, np.uint8)
    cv2.circle(truth, (45, 80), 22, io.ORANGE, -1)
    cv2.circle(truth, (115, 80), 22, io.BLUE, -1)
    return img, truth


def test_grow_recovers_discs_from_sparse_strokes():
    img, truth = synthetic_scene()
    strokes = np.zeros(img.shape[:2], np.uint8)
    cv2.circle(strokes, (45, 80), 4, lab.STROKE_ORANGE, -1)
    cv2.circle(strokes, (115, 80), 4, lab.STROKE_BLUE, -1)
    cv2.line(strokes, (5, 110), (155, 110), lab.STROKE_BG, 2)   # table
    cv2.line(strokes, (5, 20), (155, 20), lab.STROKE_BG, 2)     # wall
    mask = lab.grow(img, strokes, auto_bg_rows=0)
    assert mask.dtype == np.uint8 and set(np.unique(mask)) <= set(io.MASK_VALUES)
    for cls in (io.ORANGE, io.BLUE):
        inter = ((mask == cls) & (truth == cls)).sum()
        union = ((mask == cls) | (truth == cls)).sum()
        assert inter / union > 0.9, f"class {cls} IoU {inter/union:.2f}"
    assert (mask[:40] == io.OTHER).all()


def test_auto_bg_rows_seed_background_only():
    img, _ = synthetic_scene()
    strokes = np.zeros(img.shape[:2], np.uint8)
    cv2.circle(strokes, (45, 80), 4, lab.STROKE_ORANGE, -1)
    mask = lab.grow(img, strokes, auto_bg_rows=10)
    assert (mask[:10] == io.OTHER).all()
    assert (mask == io.ORANGE).any()
    assert not (mask == io.BLUE).any()


def test_strokes_override_grown_mask():
    img, _ = synthetic_scene()
    strokes = np.zeros(img.shape[:2], np.uint8)
    cv2.circle(strokes, (45, 80), 4, lab.STROKE_ORANGE, -1)
    cv2.line(strokes, (5, 110), (155, 110), lab.STROKE_BG, 2)
    strokes[50:55, 40:50] = lab.STROKE_IGNORE   # inside the orange disc
    mask = lab.grow(img, strokes)
    assert (mask[50:55, 40:50] == io.IGNORE).all()
    assert (mask[strokes == lab.STROKE_BG] == io.OTHER).all()


def test_grow_with_no_strokes_is_all_other():
    img, _ = synthetic_scene()
    mask = lab.grow(img, np.zeros(img.shape[:2], np.uint8), auto_bg_rows=0)
    assert (mask == io.OTHER).all()


def test_fill_boundaries_leaves_no_holes():
    m = np.ones((5, 5), np.int32)
    m[:, 2] = -1
    m[:, 3:] = 2
    out = lab._fill_boundaries(m)
    assert (out > 0).all()
    assert (out[:, :2] == 1).all() and (out[:, 3:] == 2).all()


def test_strokes_to_mask_mapping():
    s = np.array([[0, 1, 2, 3, 4]], np.uint8)
    assert lab.strokes_to_mask(s).tolist() == [[io.OTHER, io.ORANGE, io.BLUE, io.OTHER, io.IGNORE]]
