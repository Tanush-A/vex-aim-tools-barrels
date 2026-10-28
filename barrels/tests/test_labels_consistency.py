"""Data-level checks on the committed labels: every instance file agrees with its class mask."""
import json

import pytest

from barrels import instances as ins, io

STEMS = [p.stem for p in io.list_images() if io.inst_json_path(p).exists()] if io.RAW_DIR.exists() else []


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
