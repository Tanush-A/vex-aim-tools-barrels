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
    assert hook.cam == geo.AIM_4A8B6118_BOXFIT and hook.model.cfg.short_hash() == "eb863d84" and hook.model.cfg.color_model == "hs"


def test_barrels_model_env_var_swaps_the_default_front_end(monkeypatch):
    monkeypatch.setenv(wb.MODEL_ENV, str(wb.V1_MODEL))
    hook = wb.BarrelDetectorHook.default()
    assert hook.model.cfg.color_model == "rgb_box" and hook.model.cfg.short_hash() == "afd85483"
    monkeypatch.delenv(wb.MODEL_ENV)
    assert wb.BarrelDetectorHook.default().model.cfg.short_hash() == "eb863d84"


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
    seg = hook.view(rgb, "seg")                                         # seg: non-barrel pixels dimmed, barrel pixels as they were
    is_class = mask > 0
    assert is_class.any() and (seg[is_class] == rgb[is_class]).all()
    assert (seg[~is_class] == wb.seg_views(rgb, mask)[0][~is_class]).all() and seg[~is_class].mean() < 0.4 * rgb[~is_class].mean()
    only = hook.seg_only()                                              # the second window: class colors on black, RGB
    assert only.shape == rgb.shape and only.dtype == np.uint8 and only.flags["C_CONTIGUOUS"]
    assert (only[mask == io.ORANGE] == (255, 128, 0)).all() and (only[mask == io.BLUE] == (0, 100, 255)).all()
    assert not only[~is_class].any()
    both = hook.view(rgb, "both")                                       # both: the dimmed frame with the boxes on it
    assert tuple(both[y0, x0]) == (255, 255, 0) and (both[0, 0] == seg[0, 0]).all()
    try:
        hook.view(rgb, "nope")
    except ValueError:
        pass
    else:
        raise AssertionError("bad mode accepted")


def test_render_draws_the_barrels_it_is_given_and_raw_ones_in_white():
    hook = wb.BarrelDetectorHook.default()
    bgr = io.load_image(io.RAW_DIR / "4A8B_window_light_touch_02.png")
    rgb = np.ascontiguousarray(bgr[..., ::-1])
    barrels = hook.on_image(rgb)
    assert (hook.render(rgb, barrels, "boxes") == hook.view(rgb, "boxes")).all()      # view = on_image + render
    given = [Barrel(color=io.BLUE, bbox=(10, 10, 50, 60))]
    out = hook.render(rgb, given, "boxes")
    assert tuple(out[10, 10]) == (0, 255, 0) and tuple(out[10, 49]) == (0, 255, 0)     # green = blue barrel, where we said
    for b in barrels:                                                                  # this frame's own boxes are not drawn
        x0, y0, _, _ = b.bbox
        assert tuple(out[y0, x0]) == tuple(rgb[y0, x0])
    out = hook.render(rgb, given, "boxes", raw=barrels)
    for b in barrels:
        x0, y0, _, _ = b.bbox
        assert tuple(out[y0, x0]) == (255, 255, 255)                                   # ... unless asked for, in white
    seg = hook.render(rgb, given, "seg")
    assert (seg == wb.seg_views(rgb, hook.last_mask)[0]).all()                         # seg: the dimmed frame only, no boxes
    try:
        hook.render(rgb, given, "nope")
        assert False, "bad mode accepted"
    except ValueError:
        pass


def test_seg_views_dims_what_is_not_a_barrel_color_and_keeps_only_the_segmented_pixels():
    image = np.full((4, 6, 3), 200, np.uint8)
    image[..., 0] = 100                                   # every pixel (100, 200, 200)
    image[3, 5] = (255, 255, 255)
    mask = np.zeros((4, 6), np.uint8)
    mask[0, :2] = io.ORANGE
    mask[1, 2:4] = io.BLUE
    mask[2, 0] = io.IGNORE                                # anything that is not orange/blue counts as "not a barrel color"
    before = image.copy()
    dimmed, only = wb.seg_views(image, mask, dim=0.5)
    assert (image == before).all()                        # the input is not touched
    for out in (dimmed, only):
        assert out.shape == image.shape and out.dtype == np.uint8 and out.flags["C_CONTIGUOUS"]
    is_class = (mask == io.ORANGE) | (mask == io.BLUE)
    assert (dimmed[is_class] == image[is_class]).all()    # barrel-colored pixels at full brightness
    assert (dimmed[~is_class][:-1] == (50, 100, 100)).all() and tuple(dimmed[3, 5]) == (128, 128, 128)   # the rest halved (rounded)
    assert tuple(dimmed[2, 0]) == (50, 100, 100)
    assert (only[is_class] == image[is_class]).all() and not only[~is_class].any()    # original colors on black
    _, colored = wb.seg_views(image, mask, colors={io.ORANGE: (1, 2, 3), io.BLUE: (4, 5, 6)})
    assert (colored[mask == io.ORANGE] == (1, 2, 3)).all() and (colored[mask == io.BLUE] == (4, 5, 6)).all()
    assert not colored[~is_class].any()                   # class colors on black
    default_dim, _ = wb.seg_views(image, mask)
    assert tuple(default_dim[3, 0]) == (30, 60, 60) and wb.SEG_DIM == 0.3
    empty_dim, empty_only = wb.seg_views(image, np.zeros((4, 6), np.uint8))           # no barrel pixels: all dim, all black
    assert empty_dim.max() == 77 and not empty_only.any()
    try:
        wb.seg_views(image, np.zeros((5, 6), np.uint8))
    except ValueError:
        pass
    else:
        raise AssertionError("size mismatch accepted")


def test_seg_only_is_none_before_the_first_frame():
    assert wb.BarrelDetectorHook.default().seg_only() is None
