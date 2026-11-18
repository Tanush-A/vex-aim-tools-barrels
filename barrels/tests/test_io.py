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
    for n in ("a_01.png", "a_01_inst.png", "a_01_mask.png", "a_01_pred.png", "a_01_overlay.png", "a_01_orange.png", "a_01_blue.png"):
        (tmp_path / n).write_bytes(b"")
    assert [p.name for p in io.list_images(tmp_path)] == ["a_01.png"]


# ---------------------------------------------------------------- box labels (v2)

def _box(id, color, bbox, flags=()):
    return {"id": id, "color": color, "bbox": list(bbox), "flags": list(flags), "note": ""}


def test_boxes_round_trip_sorts_renumbers_and_derives_negative(tmp_path):
    meta = {"image_sha1": "abc", "reviewed": True, "clean": False,
            "barrels": [_box(7, "blue", (300, 100, 360, 170), ["occluded", "bottom_estimated"]), _box(2, "orange", (10, 20, 50, 60))]}
    p = io.save_boxes("4A8B_window_light_core_01", meta, labels_dir=tmp_path)
    assert p.name == "4A8B_window_light_core_01_boxes.json" and p == io.boxes_path("4A8B_window_light_core_01", tmp_path)
    back = io.load_boxes("4A8B_window_light_core_01", labels_dir=tmp_path, raw_dir=tmp_path)   # no image there -> sha not checked
    assert back["version"] == io.BOXES_JSON_VERSION and back["stem"] == "4A8B_window_light_core_01"
    assert back["negative"] is False and back["clean"] is False and back["reviewed"] is True and back["image_sha1"] == "abc"
    assert [b["id"] for b in back["barrels"]] == [1, 2]                      # renumbered left to right
    assert back["barrels"][0]["bbox"] == [10, 20, 50, 60] and back["barrels"][0]["color"] == "orange"
    assert back["barrels"][1]["flags"] == ["occluded", "bottom_estimated"]   # BOX_FLAGS order
    neg = io.save_boxes("x_neg_01", {"barrels": []}, labels_dir=tmp_path)
    assert neg.name == "x_neg_01_boxes.json" and io.load_boxes("x_neg_01", labels_dir=tmp_path, raw_dir=tmp_path)["negative"] is True
    with pytest.raises(FileNotFoundError):
        io.load_boxes("nope", labels_dir=tmp_path)


def test_validate_boxes_rejects_bad_content():
    ok = {"barrels": [_box(1, "orange", (0, 0, 640, 480))]}
    io.validate_boxes(ok)
    for bad in (
        {"barrels": [_box(1, "orange", (10, 10, 10, 20))]},            # empty
        {"barrels": [_box(1, "orange", (-1, 0, 20, 20))]},             # outside
        {"barrels": [_box(1, "orange", (0, 0, 641, 20))]},             # outside
        {"barrels": [_box(1, "orange", (0, 0, 20.5, 20))]},            # not ints
        {"barrels": [_box(1, "red", (0, 0, 20, 20))]},                 # color
        {"barrels": [_box(1, "blue", (0, 0, 20, 20), ["top_only"])]},  # not a box flag
        {"barrels": [_box(1, "blue", (0, 0, 20, 20)), _box(1, "blue", (30, 30, 40, 40))]},   # duplicate id
        {"negative": True, "barrels": [_box(1, "blue", (0, 0, 20, 20))]},                   # negative with barrels
        {"negative": False, "barrels": []},
        {"nothing": 1},
    ):
        with pytest.raises(ValueError):
            io.validate_boxes(bad)


def test_load_boxes_detects_changed_image(tmp_path):
    img = np.zeros((480, 640, 3), np.uint8)
    cv2.imwrite(str(tmp_path / "a_01.png"), img)
    io.save_boxes("a_01", {"image_sha1": io.file_sha1(tmp_path / "a_01.png"), "barrels": []}, labels_dir=tmp_path)
    io.load_boxes("a_01", labels_dir=tmp_path, raw_dir=tmp_path)
    img[0, 0] = 255; cv2.imwrite(str(tmp_path / "a_01.png"), img)
    with pytest.raises(ValueError, match="stale"):
        io.load_boxes("a_01", labels_dir=tmp_path, raw_dir=tmp_path)
    io.load_boxes("a_01", labels_dir=tmp_path, raw_dir=tmp_path, check_image=False)


def test_boxes_from_instances_maps_flags_and_truncation():
    imeta = {"stem": "4A8B_window_light_top_01", "barrels": [
        {"id": 1, "color": "orange", "flags": ["top_only"], "bbox": [100, 300, 500, 480]},
        {"id": 2, "color": "blue", "flags": ["occluded", "no_stripe"], "bbox": [10, 20, 40, 50]},
        {"id": 3, "color": "blue", "flags": [], "bbox": [0, 100, 30, 150]}]}
    meta = io.boxes_from_instances(imeta, image_sha1="s")
    assert meta["reviewed"] is False and meta["source"] == "from_inst" and meta["negative"] is False and meta["clean"] is True
    by_id = {b["id"]: b for b in meta["barrels"]}
    assert by_id[1]["flags"] == ["truncated"]                       # top_only -> truncated (also touches the frame)
    assert by_id[2]["flags"] == ["no_stripe", "occluded"]           # sorted set
    assert by_id[3]["flags"] == ["truncated"]                       # touches x = 0
    empty = io.boxes_from_instances({"stem": "n", "barrels": []}, "s")
    assert empty["negative"] is True and empty["barrels"] == []
    assert io.touches_frame((0, 10, 20, 30)) and io.touches_frame((10, 10, 640, 30)) and not io.touches_frame((1, 1, 639, 479))


def test_list_images_skips_boxes_side_files(tmp_path):
    for n in ("a_01.png", "a_01_boxes.png"):
        (tmp_path / n).write_bytes(b"")
    assert [p.name for p in io.list_images(tmp_path)] == ["a_01.png"]
    assert io.find_image("a_01", tmp_path) == tmp_path / "a_01.png" and io.find_image("zz", tmp_path) is None


# ---------------------------------------------------------------- hand-set color thresholds (<stem>_hs.json)

def _hs_meta(**kw) -> dict:
    meta = {"image_sha1": "", "orange": {"h_lo": -3, "h_hi": 13, "s_lo": 140}, "blue": {"h_lo": 103, "h_hi": 119, "s_lo": 113},
            "v_min": 40, "horizon_row": 50, "base_model": "eb863d84", "detector_git": "abc1234", "boxes_drawn": 3, "reviewed": True}
    return meta | kw


def test_hs_round_trip_writes_the_schema_in_order_and_leaves_no_temp_file(tmp_path):
    import json
    p = io.save_hs("4A8B_window_light_core_01", _hs_meta(), labels_dir=tmp_path / "sub")
    assert p.name == "4A8B_window_light_core_01_hs.json" and p == io.hs_path("4A8B_window_light_core_01.png", tmp_path / "sub")
    assert [x.name for x in (tmp_path / "sub").iterdir()] == [p.name] and p.read_text().endswith("}\n")
    raw = json.loads(p.read_text())
    assert raw == {"version": 1, "stem": "4A8B_window_light_core_01", "image_sha1": "",
                   "orange": {"h_lo": -3, "h_hi": 13, "s_lo": 140}, "blue": {"h_lo": 103, "h_hi": 119, "s_lo": 113},
                   "hue_units": "opencv 0-179; h_lo may be negative across the red wrap (-3 = 177)", "v_min": 40, "horizon_row": 50,
                   "base_model": "eb863d84", "detector_git": "abc1234", "boxes_drawn": 3,
                   "criterion": "as much barrel painted as needed to detect it, as little else as possible", "reviewed": True, "note": ""}
    assert list(raw)[:5] == ["version", "stem", "image_sha1", "orange", "blue"]
    assert io.load_hs("4A8B_window_light_core_01", labels_dir=tmp_path / "sub", raw_dir=tmp_path) == raw     # no image there -> sha not checked
    io.save_hs("4A8B_window_light_core_01", raw | {"note": "again", "boxes_drawn": 4}, labels_dir=tmp_path / "sub")   # a loaded label saves back
    assert io.load_hs("4A8B_window_light_core_01", labels_dir=tmp_path / "sub", raw_dir=tmp_path)["note"] == "again"
    with pytest.raises(FileNotFoundError):
        io.load_hs("nope", labels_dir=tmp_path)


def test_validate_hs_rejects_bad_content(tmp_path):
    io.validate_hs(_hs_meta())
    io.validate_hs(_hs_meta(horizon_row=None))
    for bad in (_hs_meta(orange={"h_lo": 13, "h_hi": 3, "s_lo": 140}), _hs_meta(orange={"h_lo": -31, "h_hi": 3, "s_lo": 140}),
                _hs_meta(blue={"h_lo": -1, "h_hi": 119, "s_lo": 113}), _hs_meta(blue={"h_lo": 103, "h_hi": 180, "s_lo": 113}),
                _hs_meta(blue={"h_lo": 103, "h_hi": 119, "s_lo": 256}), _hs_meta(blue={"h_lo": 103.5, "h_hi": 119, "s_lo": 113}),
                _hs_meta(blue={"h_lo": 103, "h_hi": 119}), _hs_meta(v_min="40"), _hs_meta(horizon_row=50.0), _hs_meta(base_model=""),
                _hs_meta(boxes_drawn=-1), _hs_meta(boxes_drawn=True), _hs_meta(reviewed="yes"), _hs_meta(note=3),
                {k: v for k, v in _hs_meta().items() if k != "orange"}, {k: v for k, v in _hs_meta().items() if k != "horizon_row"}):
        with pytest.raises(ValueError):
            io.validate_hs(bad)
        with pytest.raises(ValueError):
            io.save_hs("a_01", bad, labels_dir=tmp_path)
    assert not list(tmp_path.iterdir())                                           # a refused label writes nothing


def test_load_hs_detects_a_changed_image_another_frames_label_and_garbage(tmp_path):
    cv2.imwrite(str(tmp_path / "a_01.png"), np.zeros((4, 4, 3), np.uint8))
    io.save_hs("a_01", _hs_meta(image_sha1=io.file_sha1(tmp_path / "a_01.png")), labels_dir=tmp_path)
    io.load_hs("a_01", labels_dir=tmp_path, raw_dir=tmp_path)
    cv2.imwrite(str(tmp_path / "a_01.png"), np.ones((4, 4, 3), np.uint8))
    with pytest.raises(ValueError, match="stale"):
        io.load_hs("a_01", labels_dir=tmp_path, raw_dir=tmp_path)
    io.load_hs("a_01", labels_dir=tmp_path, raw_dir=tmp_path, check_image=False)
    io.hs_path("b_01", tmp_path).write_text(io.hs_path("a_01", tmp_path).read_text())        # a copied file keeps the other stem
    with pytest.raises(ValueError, match="a_01"):
        io.load_hs("b_01", labels_dir=tmp_path, check_image=False)
    io.hs_path("c_01", tmp_path).write_text("{not json")
    with pytest.raises(ValueError):
        io.load_hs("c_01", labels_dir=tmp_path)
    io.hs_path("d_01", tmp_path).write_text('{"version": 2, "stem": "d_01"}')
    with pytest.raises(ValueError, match="version"):
        io.load_hs("d_01", labels_dir=tmp_path)


def test_list_images_never_lists_hs_side_files(tmp_path):
    for n in ("a_01.png", "a_01_hs.png", "a_01_hs.json", "a_01_hs.json.tmp"):
        (tmp_path / n).write_bytes(b"")
    assert [p.name for p in io.list_images(tmp_path)] == ["a_01.png"]
