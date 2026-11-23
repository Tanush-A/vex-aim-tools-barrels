"""The adaptive color rule (adaptive.py, pipeline.Config.hs_adapt): off by default, moves thresholds per frame
along a line on one histogram number of that frame, never touches a pixel, keeps no state."""
import dataclasses
import json

import cv2
import numpy as np
import pytest

from barrels import adaptive as ad, boxfit as bf, pipeline as pl, worldmap_bridge as wb
from barrels.io import BLUE, ORANGE


def hs_model(hs_adapt=()) -> pl.Model:
    """The adopted six numbers (orange 3..13 S>=140, blue 103..119 S>=113) as an hs model."""
    cfg = pl.Config(color_model="hs", hs_adapt=hs_adapt)
    boxes = {ORANGE: bf.Box((3.0 + 30, 140.0), (13.0 + 30, 255.0)), BLUE: bf.Box((103.0, 113.0), (119.0, 255.0))}
    return pl.Model(cfg=cfg, boxes=boxes)


def image_with_blue_patch(s: int = 150, h: int = 110, v: int = 200) -> np.ndarray:
    hsv = np.zeros((480, 640, 3), np.uint8)
    hsv[..., 2] = 160                                   # a gray table: S = 0
    hsv[300:400, 200:300] = (h, s, v)                   # one blue patch, 10 000 px
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


BLUE_TERM = ("blue_s_lo", "blue_s_p90", 1.0, 100.0, 60.0)


def test_off_by_default_and_the_adopted_hash_is_unchanged():
    assert pl.Config().hs_adapt == ()
    assert wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL).model.cfg.short_hash() == "eb863d84"
    on = pl.Config(color_model="hs", hs_adapt=(BLUE_TERM,))
    assert on.short_hash() != pl.Config(color_model="hs").short_hash()


def test_config_round_trips_through_json():
    cfg = pl.Config(color_model="hs", hs_adapt=ad.as_config_value([BLUE_TERM]))
    back = pl.Config.from_dict(json.loads(json.dumps(cfg.to_dict())))
    assert back == cfg and back.short_hash() == cfg.short_hash()
    assert pl.Config.from_dict(json.loads(json.dumps(pl.Config().to_dict()))).hs_adapt == ()


def test_term_checks_and_delta():
    t = ad.Term(*BLUE_TERM)
    assert t.delta(130.0) == pytest.approx(30.0)
    assert t.delta(400.0) == pytest.approx(60.0)        # clipped to max_delta
    assert t.delta(-400.0) == pytest.approx(-60.0)
    assert t.delta(float("nan")) == 0.0 and t.delta(None) == 0.0      # no reading: the fixed value
    with pytest.raises(ValueError):
        ad.Term("blue_s_hi", "blue_s_p90", 1, 0, 1)    # not a threshold of the model
    with pytest.raises(ValueError):
        ad.Term("blue_s_lo", "ref_s_scale", 1, 0, 1)   # needs a reference histogram: not readable from the frame alone


def test_the_rule_moves_the_floor_by_the_frames_own_histogram():
    img = image_with_blue_patch(s=150)
    fixed = hs_model()
    f = ad.frame_feature_values(img, 50, 40)
    assert f["blue_s_p90"] == pytest.approx(151, abs=2)          # S histogram bins are 2 wide
    m_fixed, _ = pl.segment(pl.Frame.from_image(img), fixed)
    assert (m_fixed == BLUE).sum() == 10000                       # S 150 >= 113: painted
    on = hs_model(ad.as_config_value([BLUE_TERM]))
    th = ad.frame_thresholds(pl.Frame.from_image(img), on)
    assert th["blue_s_lo"] == pytest.approx(113 + 51, abs=2)      # floor + 1 * (151 - 100)
    m_on, info = pl.segment(pl.Frame.from_image(img), on)
    assert (m_on == BLUE).sum() == 0                              # S 150 < 164: not painted
    assert info["adapt"]["moves"]["blue_s_lo"] == pytest.approx(51, abs=2)
    # a duller blue frame reads a lower p90: its floor comes DOWN with the same rule
    dull = image_with_blue_patch(s=70)
    th2 = ad.frame_thresholds(pl.Frame.from_image(dull), on)
    assert th2["blue_s_lo"] == pytest.approx(113 - 29, abs=2)
    steep = hs_model(ad.as_config_value([("blue_s_lo", "blue_s_p90", 2.0, 100.0, 60.0)]))     # floor 113 + 2 * (71 - 100) = 55
    assert (pl.segment(pl.Frame.from_image(dull), steep)[0] == BLUE).sum() == 10000
    assert (pl.segment(pl.Frame.from_image(dull), fixed)[0] == BLUE).sum() == 0


def test_no_reading_keeps_the_fixed_value_and_pixels_are_never_changed():
    img = image_with_blue_patch(s=150)
    img[300:400, 200:300] = 160                                   # no blue left: the window has no reading
    keep = img.copy()
    on = hs_model(ad.as_config_value([BLUE_TERM]))
    assert ad.frame_thresholds(pl.Frame.from_image(img), on)["blue_s_lo"] == pytest.approx(113)
    pl.segment(pl.Frame.from_image(img), on)
    assert np.array_equal(img, keep)                              # never an image correction


def test_nothing_is_carried_between_frames():
    a, b = image_with_blue_patch(s=150), image_with_blue_patch(s=70)
    on = hs_model(ad.as_config_value([BLUE_TERM]))
    first = pl.segment(pl.Frame.from_image(a), on)[0]
    pl.segment(pl.Frame.from_image(b), on)
    again = pl.segment(pl.Frame.from_image(a), on)[0]
    assert np.array_equal(first, again)


def test_an_empty_hue_range_keeps_the_models_box():
    img = image_with_blue_patch(s=150)
    on = hs_model(ad.as_config_value([("orange_h_hi", "blue_s_p90", -1.0, 100.0, 50.0)]))   # hi pushed below lo
    boxes, info = ad.adapted_boxes(pl.Frame.from_image(img), on)
    assert boxes[ORANGE] is on.boxes[ORANGE] and ORANGE in info["kept"]


def test_a_refit_model_adapts_around_its_own_numbers():
    on = hs_model(ad.as_config_value([BLUE_TERM]))
    moved = dataclasses.replace(on, boxes={**on.boxes, BLUE: bf.Box((103.0, 90.0), (119.0, 255.0))})
    th = ad.frame_thresholds(pl.Frame.from_image(image_with_blue_patch(s=150)), moved)
    assert th["blue_s_lo"] == pytest.approx(90 + 51, abs=2)


def test_fit_slope_through_the_home_point_and_place_weights():
    x = np.array([110.0, 120.0, 130.0])
    assert ad.fit_slope(x, 113 + 2 * (x - 100), 113, 100) == pytest.approx(2.0)
    assert ad.fit_slope([100.0, 100.0], [50.0, 200.0], 113, 100) == 0.0      # nothing off the home point
    assert ad.fit_slope([np.nan, 110.0], [0.0, 123.0], 113, 100) == pytest.approx(1.0)   # a missing reading is left out
    w = ad.place_weights(["ott", "ott", "ott", "ott", "pale"])
    assert w.tolist() == pytest.approx([0.25] * 4 + [1.0])
    # four copies of one place do not outvote another place
    xs = np.array([110.0, 110.0, 110.0, 110.0, 90.0])
    ys = np.array([123.0, 123.0, 123.0, 123.0, 113 + 10])               # ott wants b=+1, pale wants b=-1
    assert ad.fit_slope(xs, ys, 113, 100, w) == pytest.approx(0.0)
    assert ad.fit_slope(xs, ys, 113, 100) > 0.5                          # unweighted: the four copies win
