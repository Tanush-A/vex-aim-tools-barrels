"""Data-level checks on the committed labels: every instance file agrees with its class mask, every box
label file is well-formed and was drawn on the committed image."""
import json

import pytest

from barrels import instances as ins, io

STEMS = [p.stem for p in io.list_images() if io.inst_json_path(p).exists()] if io.RAW_DIR.exists() else []
BOX_STEMS = [p.stem for p in io.list_images() if io.boxes_path(p).exists()] if io.RAW_DIR.exists() else []


@pytest.mark.parametrize("stem", STEMS)
def test_instances_consistent_with_masks(stem):
    inst, meta = io.load_instances(stem)              # raises if the cache or the mask sha1 is stale
    mask = io.load_mask(io.LABELS_DIR / f"{stem}_mask.png")
    cc = ins.check_consistency(mask, inst)
    assert cc["outside_mask_px"] == 0
    assert cc["unassigned_class_px"] <= meta.get("dropped_px", 0)
    assert meta["barrels"] and all(b["color"] in ("orange", "blue") for b in meta["barrels"]) or (not meta["barrels"] and not cc["ids"])
    json.dumps(meta)                                   # serialisable


def test_all_window_light_frames_have_instances():
    missing = [p.stem for p in io.list_images() if "window_light" in p.name and not io.inst_json_path(p).exists()]
    assert missing == []


@pytest.mark.parametrize("stem", BOX_STEMS)
def test_box_labels_valid_and_match_image(stem):
    meta = io.load_boxes(stem)                         # validates; raises if the image changed since
    assert meta["stem"] == stem and meta["image_sha1"] == io.file_sha1(io.find_image(stem))
    scene = io.parse_name(stem)["scene"]
    if scene == "neg":
        assert meta["negative"] and not meta["barrels"]
    elif scene not in ("calib", "ruler", "horizon", "held"):      # held: a barrel in the kicker may be left unboxed (Tanush, 2026-11-08)
        assert meta["barrels"], "a positive frame with no boxes"


def test_all_window_light_frames_have_boxes():
    missing = [p.stem for p in io.list_images() if "window_light" in p.name and not io.boxes_path(p).exists()]
    assert missing == []
