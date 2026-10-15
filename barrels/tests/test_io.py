import numpy as np
import pytest

from barrels import io


def test_mask_roundtrip(tmp_path):
    mask = np.zeros((8, 10), np.uint8)
    mask[1, 1] = io.ORANGE
    mask[2, 2] = io.BLUE
    mask[3, 3] = io.IGNORE
    p = io.save_mask(tmp_path / "sub" / "x_mask.png", mask)
    back = io.load_mask(p)
    assert back.dtype == np.uint8 and back.shape == mask.shape
    assert (back == mask).all()


def test_save_mask_rejects_bad_values(tmp_path):
    bad = np.full((4, 4), 7, np.uint8)
    with pytest.raises(ValueError):
        io.save_mask(tmp_path / "bad_mask.png", bad)
    with pytest.raises(ValueError):
        io.validate_mask(np.zeros((4, 4), np.int32))


def test_load_mask_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        io.load_mask(tmp_path / "nope.png")


def test_paths_follow_convention(tmp_path):
    img = tmp_path / "4A8B_bounce_black_core_01.png"
    assert io.mask_path(img, tmp_path).name == "4A8B_bounce_black_core_01_mask.png"
    assert io.strokes_path(img, tmp_path).name == "4A8B_bounce_black_core_01_strokes.png"


def test_list_images_skips_side_files(tmp_path):
    for n in ("b_01.png", "a_01.png", "a_01_mask.png", "a_01_strokes.png", "notes.txt"):
        (tmp_path / n).write_bytes(b"")
    assert [p.name for p in io.list_images(tmp_path)] == ["a_01.png", "b_01.png"]


def test_parse_name():
    d = io.parse_name("4A8B_upmid_wood_topstripe_02")
    assert d == {"robot": "4A8B", "light": "upmid", "surface": "wood", "scene": "topstripe", "nn": "02"}
    with pytest.raises(ValueError):
        io.parse_name("robot_snap3")
