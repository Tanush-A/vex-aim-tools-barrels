import cv2
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


def test_instance_round_trip_and_staleness(tmp_path):
    inst = np.zeros((8, 10), np.uint8); inst[1:4, 1:5] = 1; inst[5:7, 6:9] = 2
    mask = np.zeros((8, 10), np.uint8); mask[1:4, 1:5] = io.ORANGE; mask[5:7, 6:9] = io.BLUE
    io.save_mask(tmp_path / "x_mask.png", mask)
    meta = {"mask_sha1": io.file_sha1(tmp_path / "x_mask.png"), "barrels": [{"id": 1, "color": "orange"}, {"id": 2, "color": "blue", "flags": ["occluded"]}]}
    png, js = io.save_instances("x", inst, meta, labels_dir=tmp_path)
    back, m = io.load_instances("x", labels_dir=tmp_path)
    assert (back == inst).all() and m["version"] == io.INSTANCE_JSON_VERSION and m["stem"] == "x"
    assert m["barrels"][0]["bbox"] == [1, 1, 5, 4] and m["barrels"][0]["area"] == 12 and m["barrels"][0]["color"] == "orange"
    assert m["barrels"][1]["flags"] == ["occluded"] and m["barrels"][1]["bottom_mid"] == [7.5, 7]
    recs = io.instance_records(inst, mask)
    assert recs[1]["px"] == {"orange": 0, "blue": 6, "ignore": 0}
    # stale cache: PNG edited after the JSON
    inst2 = inst.copy(); inst2[1:4, 1:6] = 1
    cv2.imwrite(str(png), inst2)
    with pytest.raises(ValueError, match="stale"):
        io.load_instances("x", labels_dir=tmp_path)
    # stale mask: class mask changed since
    io.save_instances("x", inst2, meta, labels_dir=tmp_path)
    mask[0, 0] = io.ORANGE; io.save_mask(tmp_path / "x_mask.png", mask)
    with pytest.raises(ValueError, match="changed"):
        io.load_instances("x", labels_dir=tmp_path)
    assert io.load_instances("x", labels_dir=tmp_path, check_mask=False)[0].shape == (8, 10)
    with pytest.raises(ValueError):
        io.validate_instances(np.full((2, 2), 255, np.uint8))
    with pytest.raises(FileNotFoundError):
        io.load_instances("nope", labels_dir=tmp_path)


def test_list_images_skips_inst_files(tmp_path):
    for n in ("a_01.png", "a_01_inst.png", "a_01_mask.png"):
        (tmp_path / n).write_bytes(b"")
    assert [p.name for p in io.list_images(tmp_path)] == ["a_01.png"]
