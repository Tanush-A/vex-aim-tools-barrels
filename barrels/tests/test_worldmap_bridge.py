import json

import numpy as np

from barrels import detect_cc, detector as det, geometry as geo, io, pipeline as pl, viz, worldmap_bridge as wb
from barrels.detect_types import Barrel
from test_labeling import synthetic_scene


def test_items_have_exactly_what_worldmap_reads_and_status_not_mutated():
    b = [Barrel(color=io.ORANGE, bbox=(100, 200, 160, 262)), Barrel(color=io.BLUE, bbox=(300, 100, 340, 150), confidence=0.5)]
    items = wb.barrels_to_aivision_items(b)
    assert [i["id"] for i in items] == ["barrels-0", "barrels-1"]
    assert items[0] == {"type_str": "aiobj", "name": "OrangeBarrel", "originx": 50, "originy": 100, "width": 30, "height": 31, "score": 1.0, "id": "barrels-0"}
    status = {"aivision": {"objects": {"items": [{"name": "vendor"}]}}, "other": 1}
    new = wb.with_items(status, items)
    assert new["aivision"]["objects"]["items"] == items and new["other"] == 1
    assert status["aivision"]["objects"]["items"] == [{"name": "vendor"}]
    assert wb.with_items(None, items)["aivision"]["objects"]["items"] == items


def test_draw_boxes_marks_the_right_pixels():
    img = np.zeros((480, 640, 3), np.uint8)
    out = wb.draw_boxes(img, [Barrel(color=io.ORANGE, bbox=(100, 200, 160, 262))])
    assert out.shape == img.shape and (img == 0).all()
    assert out[200:262, 100:160].any() and not out[300:, :].any()


def test_hook_runs_on_a_synthetic_scene(tmp_path):
    img, truth = synthetic_scene()
    frame = pl.Frame.from_image(img)
    cfg = pl.Config(horizon_row=10, bg_rows=(0, 10), table_rows=20, v_min=20)
    model = pl.fit([frame], [truth], cfg)
    conf = tmp_path / "config.json"
    json.dump({"model": model.to_dict()}, conf.open("w"))
    hook = wb.BarrelDetectorHook.load(conf, cam=geo.NOMINAL, detector=detect_cc.detect, det_cfg=detect_cc.CCConfig())   # the CC floor: the 120x160 scene has no stripes
    assert hook.model.cfg == cfg and hook.model.boxes[io.ORANGE] == model.boxes[io.ORANGE]
    rgb = np.ascontiguousarray(img[..., ::-1])
    barrels = hook.on_image(rgb)
    assert len(barrels) == 2 and {b.color for b in barrels} == {io.ORANGE, io.BLUE}
    assert all(b.ground_xy_mm is not None for b in barrels)
    assert hook.annotate(rgb, barrels).shape == rgb.shape


def test_default_hook_is_the_detector_as_it_stands():
    hook = wb.BarrelDetectorHook.default()
    assert hook.detector is det.detect and isinstance(hook.det_cfg, det.DetConfig) and hook.det_cfg.require_stripe
    assert hook.cam == geo.AIM_4A8B6118_BOXFIT and hook.model.cfg.short_hash() == "afd85483"


def test_view_on_a_real_frame_matches_the_photo_path():
    """The live path (RGB in, RGB out) must give exactly the boxes and pixels tools/detect_image.py gives."""
    bgr = io.load_image(io.RAW_DIR / "4A8B_window_light_touch_02.png")
    rgb = np.ascontiguousarray(bgr[..., ::-1])
    hook = wb.BarrelDetectorHook.default()
    barrels = hook.on_image(rgb)
    assert len(barrels) == 3 and [b.color for b in barrels] == [io.ORANGE, io.BLUE, io.ORANGE]   # orange-blue-orange, left to right
    mask, _ = pl.segment(pl.Frame.from_image(bgr), hook.model)
    assert (hook.last_mask == mask).all()
    for mode in wb.VIEWS:
        out = hook.view(rgb, mode)
        assert out.shape == rgb.shape and out.dtype == np.uint8 and out.flags["C_CONTIGUOUS"]
    boxes = hook.view(rgb, "boxes")
    assert (boxes[..., ::-1] == det.draw(bgr, barrels)).all()           # same pixels as the photo path, just RGB
    x0, y0, x1, y1 = barrels[0].bbox
    assert tuple(boxes[y0, x0]) == (255, 255, 0)                        # yellow in RGB = an orange barrel's box
    assert (hook.view(rgb, "seg")[..., ::-1] == viz.overlay(bgr, mask)).all()
    try:
        hook.view(rgb, "nope")
    except ValueError:
        pass
    else:
        raise AssertionError("bad mode accepted")
