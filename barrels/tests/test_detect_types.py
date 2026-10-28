import numpy as np
import pytest

from barrels import detect_types as dt, geometry as geo, io


def test_barrel_basics_and_spec_round_trip():
    b = dt.Barrel(color=io.ORANGE, bbox=(100, 200, 160, 262), confidence=0.9)
    assert b.width == 60 and b.height == 62 and b.bottom_row == 261 and b.bottom_mid == (130.0, 262.0)
    spec = b.to_aivision_spec(id="barrels-0")
    assert spec == {"type_str": "aiobj", "name": "OrangeBarrel", "originx": 50, "originy": 100, "width": 30, "height": 31, "score": 0.9, "id": "barrels-0"}
    back = dt.Barrel.from_aivision_spec(spec)
    assert back.bbox == (100, 200, 160, 262) and back.color == io.ORANGE and back.source == "aivision"
    assert dt.Barrel(color=io.BLUE, bbox=(0, 0, 3, 3)).to_aivision_spec()["name"] == "BlueBarrel"
    assert dt.Barrel.from_dict(b.to_dict()) == b
    with pytest.raises(ValueError):
        dt.Barrel(color=io.ORANGE, bbox=(10, 10, 10, 20))
    with pytest.raises(ValueError):
        dt.Barrel(color=io.ORANGE, bbox=(0, 0, 1, 1), flags=frozenset({"bogus"}))


def test_from_instance_mask_and_ground():
    inst = np.zeros((40, 60), np.uint8); inst[10:30, 20:45] = 3
    mask = np.zeros((40, 60), np.uint8); mask[10:30, 20:45] = io.BLUE; mask[18:22, 20:45] = io.ORANGE
    b = dt.Barrel.from_instance_mask(inst, mask, 3, cam=geo.NOMINAL)
    assert b.bbox == (20, 10, 45, 30) and b.color == io.BLUE and b.area == 500 and b.source == "gt"
    assert b.ground_xy_mm is not None
    x_expected, y_expected = geo.NOMINAL.barrel_axis_xy(32.5, 30.0)
    assert b.ground_xy_mm == pytest.approx((x_expected, y_expected))
    with pytest.raises(ValueError):
        dt.Barrel.from_instance_mask(inst, mask, 7)
    # with_ground at 11 mm reproduces worldmap's offset
    b11 = b.with_ground(geo.WORLDMAP_CURRENT, radius_mm=11.0)
    assert b11.ground_xy_mm == pytest.approx(geo.WORLDMAP_CURRENT.barrel_axis_xy(32.5, 30.0, 11.0))


def test_barrels_from_instances_uses_json_then_mask():
    inst = np.zeros((40, 60), np.uint8); inst[5:15, 5:15] = 1; inst[20:35, 30:50] = 2
    mask = np.full((40, 60), io.OTHER, np.uint8); mask[5:15, 5:15] = io.ORANGE; mask[20:35, 30:50] = io.BLUE
    meta = {"barrels": [{"id": 1, "color": "orange", "flags": ["truncated"], "ground_xy_mm": [100.0, -5.0]}, {"id": 2}]}
    out = dt.barrels_from_instances(inst, meta, mask)
    assert [b.color for b in out] == [io.ORANGE, io.BLUE]
    assert out[0].flags == {"truncated"} and out[0].ground_xy_mm == (100.0, -5.0) and out[1].ground_xy_mm is None
    with pytest.raises(ValueError):
        dt.barrels_from_instances(inst, meta)      # id 2 has no color and no mask
    out2 = dt.barrels_from_instances(inst, meta, mask, cam=geo.NOMINAL)
    assert out2[1].ground_xy_mm is not None and out2[0].ground_xy_mm == (100.0, -5.0)


def test_attach_measured_truth_convention():
    import importlib.util, pathlib
    spec = importlib.util.spec_from_file_location("attach_measured", pathlib.Path(__file__).resolve().parents[1] / "tools" / "attach_measured.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    assert mod.truth_xy(100.0, -60.0) == (139.0, -60.0)      # d + 30 (front edge) + 9 (base radius)
