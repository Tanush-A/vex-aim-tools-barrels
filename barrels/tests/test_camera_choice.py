"""One place decides the camera (geometry.DEFAULT_CAMERA, 2026-11-19): the names, the number form, and that
the detector, the live hook and an arm of the eval table all take it from there."""
import inspect

import pytest

from barrels import detector as det
from barrels import geometry as g
from barrels import report as rp
from barrels import worldmap_bridge as wb


def test_named_cameras_and_the_old_constant_stays_what_it_was():
    assert g.camera("boxfit") is g.AIM_4A8B6118_BOXFIT and g.camera(" BoxFit ") is g.AIM_4A8B6118_BOXFIT
    assert g.camera("4a8b") is g.AIM_4A8B6118 and g.camera("nominal") is g.NOMINAL
    old = g.AIM_4A8B6118_BOXFIT                                   # the 2026-11-03 box fit: its numbers do not move
    assert (old.f, old.tilt_deg, old.height_mm, old.cy) == (400.0, 22.25, 43.47, 240.0)
    assert old.horizon_row() == pytest.approx(76.36, abs=0.01)
    assert g.camera(old) is old                                   # a CameraModel passes through


def test_camera_from_numbers():
    c = g.camera("f=400,tilt=20.4,height=40.2")
    assert (c.f, c.tilt_deg, c.height_mm, c.cy) == (400.0, 20.4, 40.2, 240.0)
    assert c.horizon_row() == pytest.approx(91.24, abs=0.01)
    assert g.camera("f=380, tilt_deg=21").height_mm == g.H_CAM_MM          # what is not given keeps the default
    for bad in ("ruler2", "f=400", "tilt=20", "f=400,tilt=20,zoom=2", "f=abc,tilt=20"):
        with pytest.raises(ValueError):
            g.camera(bad)


def test_default_camera_is_one_name_and_the_environment_can_replace_it(monkeypatch):
    monkeypatch.delenv(g.CAMERA_ENV, raising=False)
    assert g.default_camera() is g.CAMERAS[g.DEFAULT_CAMERA_NAME]
    monkeypatch.setenv(g.CAMERA_ENV, "boxfit")
    assert g.default_camera() is g.AIM_4A8B6118_BOXFIT
    monkeypatch.setenv(g.CAMERA_ENV, "f=390,tilt=21,height=41")
    assert g.default_camera() == g.CameraModel(f=390.0, tilt_deg=21.0, height_mm=41.0)


def test_every_default_points_at_the_same_camera():
    for fn in (det.detect, det.detect_step1):
        assert inspect.signature(fn).parameters["cam"].default is g.DEFAULT_CAMERA
    assert inspect.signature(wb.BarrelDetectorHook.load).parameters["cam"].default is g.DEFAULT_CAMERA
    assert inspect.signature(wb.BarrelDetectorHook.default).parameters["cam"].default is g.DEFAULT_CAMERA
    assert wb.BarrelDetectorHook.__dataclass_fields__["cam"].default is g.DEFAULT_CAMERA


def test_an_arm_can_carry_its_own_camera():
    a = rp.Arm("x", "results/a/config.json")
    assert a.cam is None and "camera" not in a.describe()                  # None = the camera that runs
    b = rp.Arm("y", "results/a/config.json", {}, cam=g.camera("f=400,tilt=20.4,height=40.2"))
    assert b.describe().endswith("camera f 400, tilt 20.4, height 40.2")
