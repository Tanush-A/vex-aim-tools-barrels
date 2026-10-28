import json

import numpy as np

from barrels import geometry as geo, io, pipeline as pl, worldmap_bridge as wb
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
    hook = wb.BarrelDetectorHook.load(conf, cam=geo.NOMINAL)
    assert hook.model.cfg == cfg and hook.model.boxes[io.ORANGE] == model.boxes[io.ORANGE]
    rgb = np.ascontiguousarray(img[..., ::-1])
    barrels = hook.on_image(rgb)
    assert len(barrels) == 2 and {b.color for b in barrels} == {io.ORANGE, io.BLUE}
    assert all(b.ground_xy_mm is not None for b in barrels)
    assert hook.annotate(rgb, barrels).shape == rgb.shape
