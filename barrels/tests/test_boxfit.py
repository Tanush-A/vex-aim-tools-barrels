import numpy as np
import pytest

from barrels import boxfit as bf


def test_fit_box_percentiles_and_in_box_inclusive():
    rng = np.random.default_rng(0)
    px = rng.integers(50, 151, (20000, 3))                # uniform cube [50,150]
    box = bf.fit_box(px, 1, 99)
    assert all(48 <= lo <= 53 for lo in box.lo) and all(147 <= hi <= 152 for hi in box.hi)
    assert bf.in_box(np.array(box.lo), box) and bf.in_box(np.array(box.hi), box)
    assert not bf.in_box(np.array(box.hi) + 1, box)
    img = np.zeros((4, 5, 3), np.int16); img[1, 2] = 100
    assert bf.in_box(img, box).sum() == 1
    with pytest.raises(ValueError):
        bf.fit_box(np.zeros((0, 3)))


def test_fullness_solid_vs_line():
    g = np.arange(0, 64)
    cube = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1).reshape(-1, 3)
    box = bf.Box((0, 0, 0), (63, 63, 63))
    assert bf.fullness(cube, box, voxel=8) == 1.0
    line = np.stack([g, g, g], 1)
    assert bf.fullness(line, box, voxel=8) == pytest.approx(8 / 512)
    assert bf.fullness(np.array([[200, 200, 200]]), box, 8) == 0.0


def test_pca_of_gray_line_is_linear_and_gray():
    t = np.linspace(0, 200, 500)
    px = np.stack([t, t, t], 1) + np.random.default_rng(0).normal(0, 0.5, (500, 3))
    p = bf.pca(px)
    assert p["var_fraction"][0] > 0.99 and p["linearity"] > 0.99 and p["cos_to_gray"] > 0.999


def test_sample_class_pixels_caps_and_respects_keep():
    rng = np.random.default_rng(1)
    img = rng.integers(0, 255, (30, 40, 3)).astype(np.int16)
    mask = np.zeros((30, 40), np.uint8); mask[:, :20] = 1
    keep = np.zeros((30, 40), bool); keep[:10] = True
    px = bf.sample_class_pixels(img, mask, 1, keep=keep)
    assert len(px) == 10 * 20
    capped = bf.sample_class_pixels(img, mask, 1, max_px=50, rng=np.random.default_rng(0))
    capped2 = bf.sample_class_pixels(img, mask, 1, max_px=50, rng=np.random.default_rng(0))
    assert len(capped) == 50 and (capped == capped2).all()


def test_box_helpers():
    a = bf.Box((0, 0, 0), (10, 10, 10)); b = bf.Box((5, 5, 5), (20, 20, 20)); c = bf.Box((11, 0, 0), (12, 1, 1))
    assert bf.box_overlap(a, b) == bf.Box((5, 5, 5), (10, 10, 10))
    assert bf.box_overlap(a, c) is None
    assert a.volume() == 11 ** 3
    s = a.shrink(0.2)
    assert s.lo == (1, 1, 1) and s.hi == (9, 9, 9)
    assert b.clip_to(a) == bf.Box((5, 5, 5), (10, 10, 10))
    assert bf.Box.from_dict(a.to_dict()) == bf.Box((0.0, 0.0, 0.0), (10.0, 10.0, 10.0))
