"""The light's warmth and the blue box that follows it (lightcolor.py, pipeline.Config.hs_light; off by default)."""
import cv2
import numpy as np
import pytest

from barrels import boxfit as bf
from barrels import lightcolor as lc
from barrels import pipeline as pl
from barrels import worldmap_bridge as wb
from barrels.io import BLUE, ORANGE

BOXES = {ORANGE: bf.Box((33.0, 140.0), (43.0, 255.0)), BLUE: bf.Box((103.0, 113.0), (119.0, 255.0))}
P = (0.10, 0.25, 40.0, 92.0)


def _frame(light=(1.0, 1.0, 1.0), patch_hsv=(105, 60, 110)) -> np.ndarray:
    """A gray-white table lit by ``light`` (R, G, B gains), a bright white patch, and a blue-ish patch (BGR out)."""
    rgb = np.full((480, 640, 3), 150.0)
    rgb[400:480, :] = 245.0                                       # bright pale surface: the white patch
    rgb *= np.array(light)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    bgr = rgb[..., ::-1].copy()
    hsv = np.zeros((40, 40, 3), np.uint8); hsv[:] = patch_hsv
    bgr[200:240, 300:340] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr


def test_light_warmth_reads_the_brightest_pixels():
    assert abs(lc.light_warmth(_frame()[..., ::-1])) < 0.01
    warm = lc.light_warmth(_frame((1.0, 0.75, 0.35))[..., ::-1])
    cool = lc.light_warmth(_frame((0.85, 0.95, 1.0))[..., ::-1])
    assert warm > 0.25 and cool < 0
    rgb = np.full((100, 100, 3), 120, np.uint8); rgb[:, :, 2] = 60      # a yellow table ...
    rgb[:8] = 250                                                       # ... with a white strip, the brightest 8 %
    assert lc.light_warmth(rgb) < 0.01                                  # a warm TABLE under white light reads neutral
    assert lc.light_warmth(np.zeros((0, 3))) == 0.0


def test_share_and_validate():
    assert lc.share(0.05, 0.1, 0.25) == 0 and lc.share(0.4, 0.1, 0.25) == 1 and lc.share(0.175, 0.1, 0.25) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        lc.share(0.2, 0.3, 0.3)
    for bad in ((0.2, 0.1, 40, 92), (0.1, 0.2, 40), ("a", 0.2, 40, 92), (0.1, 0.2, 300, 92), (0.1, 0.2, 40, 200), (0.1, np.nan, 40, 92)):
        with pytest.raises(ValueError):
            lc.validate(bad)
    assert lc.validate([0.1, 0.25, 40, 92]) == P + (0, 5.0)
    assert lc.validate((0.1, 0.25, 40, 92, 50, 20)) == P + (50, 20.0)
    for bad in ((0.1, 0.25, 40, 92, 50), (0.1, 0.25, 40, 92, 50.5, 20), (0.1, 0.25, 40, 92, 50, 0)):
        with pytest.raises(ValueError):
            lc.validate(bad)


def test_warm_blue_boxes_moves_only_the_blue_lower_corner_and_only_down():
    neutral = _frame()[..., ::-1]
    out, info = lc.warm_blue_boxes(neutral, BOXES, P)
    assert out[BLUE] == BOXES[BLUE] and out[ORANGE] == BOXES[ORANGE] and info["share"] == 0
    warm = _frame((1.0, 0.75, 0.35))[..., ::-1]
    out, info = lc.warm_blue_boxes(warm, BOXES, P)
    assert info["share"] == 1 and out[BLUE].lo == (92.0, 40.0) and out[BLUE].hi == BOXES[BLUE].hi and out[ORANGE] == BOXES[ORANGE]
    low = {**BOXES, BLUE: bf.Box((90.0, 30.0), (119.0, 255.0))}       # already below the targets: left as it is
    assert lc.warm_blue_boxes(warm, low, P)[0][BLUE] == low[BLUE]
    half = lc.warm_blue_boxes(warm, BOXES, (info["warmth"] - 0.1, info["warmth"] + 0.1, 40, 92))[0][BLUE]
    assert half.lo == pytest.approx((97.5, 76.5))


def test_config_default_off_and_the_adopted_hash_unchanged():
    assert pl.Config().hs_light == ()
    m = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL).model
    assert m.cfg.short_hash() == "eb863d84" and m.cfg.hs_light == ()
    on = pl.Config.from_dict({**m.cfg.to_dict(), "hs_light": [0.1, 0.25, 40, 92]})
    assert on.hs_light == P and on.short_hash() != "eb863d84"
    assert pl.Config.from_dict(on.to_dict()) == on


def test_segment_paints_the_washed_out_blue_only_under_a_warm_light():
    m = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL).model
    import dataclasses
    on = dataclasses.replace(m, cfg=dataclasses.replace(m.cfg, hs_light=P))
    for light, want in (((1.0, 1.0, 1.0), False), ((1.0, 0.75, 0.35), True)):
        f = pl.Frame.from_image(_frame(light))
        mask_off, _ = pl.segment(f, m)
        mask_on, info = pl.segment(f, on)
        patch = (slice(200, 240), slice(300, 340))
        assert not (mask_off[patch] == BLUE).any()                     # S 60 < 113: the adopted model never paints it
        assert (mask_on[patch] == BLUE).all() == want
        assert "light" in info and ("light" not in pl.segment(f, m)[1])
        assert (mask_on[:200] == mask_off[:200]).all()                  # nothing else moves on this frame


def test_band_reading_ignores_what_is_below_the_horizon_gate():
    """Round 2: the light read from rows 0-49 only; a warm-looking table and close barrels below row 50 do not count."""
    rgb = np.full((480, 640, 3), 200, np.uint8)
    rgb[50:] = (230, 120, 30)                                       # orange things fill everything below row 50
    out, info = lc.warm_blue_boxes(rgb, BOXES, P + (50, 20))
    assert abs(info["warmth"]) < 0.01 and out[BLUE] == BOXES[BLUE]
    out, info = lc.warm_blue_boxes(rgb, BOXES, P)                    # the whole-frame reading is fooled
    assert info["warmth"] > 0.25 and out[BLUE].lo == (92.0, 40.0)
