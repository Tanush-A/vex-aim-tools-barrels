"""The readings of the light's color (lightread.py; the measuring kit of experiments/2026-11-26_light; nothing in the
detector imports it)."""
import ast
from pathlib import Path

import numpy as np
import pytest

from barrels import lightcolor as lc
from barrels import lightread as lr

SRC = Path(lr.__file__).resolve().parent


def scene(light=(1.0, 1.0, 1.0)) -> np.ndarray:
    """A gray table (150) with a white strip at the bottom (245) and a wall above the gate (200), lit by ``light``
    (R, G, B gains). RGB uint8, 480 x 640."""
    rgb = np.full((480, 640, 3), 150.0)
    rgb[:50] = 200.0
    rgb[400:] = 245.0
    return np.clip(rgb * np.array(light), 0, 255).astype(np.uint8)


WARM = (1.0, 0.75, 0.35)


def test_summarize_and_read():
    px = np.tile(np.array([[200.0, 100.0, 50.0]]), (300, 1))
    r = lr.summarize(px)
    assert r.ok and r.n == 300 and r.v_med == 200
    assert r.warmth == pytest.approx(150 / 351) and r.log_rg == pytest.approx(np.log(201 / 101)) and r.log_bg == pytest.approx(np.log(51 / 101))
    few = lr.summarize(px[:lr.MIN_PX - 1])
    assert not few.ok and few.n == lr.MIN_PX - 1 and np.isnan(few.warmth)
    rgb = scene()
    m = np.zeros(rgb.shape[:2], bool); m[:10] = True
    assert lr.read(rgb, m).n == 10 * 640 and lr.read(rgb, m).v_med == 200
    with pytest.raises(ValueError):
        lr.read(np.zeros((4, 4)), np.zeros((4, 4), bool))


def test_pixel_warmth_and_saturation():
    rgb = np.array([[[200, 100, 50], [0, 0, 0], [50, 100, 200], [80, 80, 80]]], np.uint8)
    w = lr.pixel_warmth(rgb)[0]
    assert w[0] == pytest.approx(150 / 351) and w[1] == 0 and w[2] == pytest.approx(-150 / 351) and w[3] == 0
    s = lr.hsv_s(rgb)[0]
    assert s[0] == pytest.approx(255 * 150 / 200) and s[1] == 0 and s[3] == 0


def test_whole_frame_is_the_existing_light_warmth():
    rng = np.random.default_rng(0)
    for light in ((1, 1, 1), WARM, (0.85, 0.95, 1.0)):
        rgb = np.clip(scene(light).astype(float) + rng.integers(-6, 7, (480, 640, 3)), 0, 255).astype(np.uint8)
        assert lr.whole_frame(rgb).warmth == pytest.approx(lc.light_warmth(rgb), abs=1e-6)
        assert lr.above_gate(rgb, 50, 20.0).warmth == pytest.approx(lc.light_warmth(rgb[:50], 20.0), abs=1e-6)


def test_every_reading_follows_the_light_on_a_plain_scene():
    neutral, warm = scene(), scene(WARM)
    for f in (lr.whole_frame, lr.above_gate, lr.near_strip, lr.gray_world, lr.max_rgb, lr.tiles, lr.least_colored):
        assert abs(f(neutral).warmth) < 0.01, f.__name__
        assert f(warm).warmth > 0.25, f.__name__
    assert abs(lr.neutral(neutral).warmth) < 0.01
    assert not lr.neutral(warm).ok                      # under a yellow lamp nothing is under a fixed S limit: it says nothing
    hi = lr.highlights(scene((0.96, 0.96, 0.96)))       # the white strip at 235: nearly clipped
    assert hi.ok and abs(hi.warmth) < 0.01
    assert not lr.highlights(np.full((100, 100, 3), 120, np.uint8)).ok


def test_masks_pick_the_pixels_they_say():
    rgb = scene()
    assert lr.whole_frame_mask(rgb)[400:].all() and not lr.whole_frame_mask(rgb)[:400].any()         # ties at the threshold are included
    assert lr.above_gate_mask(rgb)[:50].all() and not lr.above_gate_mask(rgb)[50:].any()
    assert lr.near_strip_mask(rgb, 80)[400:].all() and not lr.near_strip_mask(rgb, 80)[:400].any()
    assert not lr.gray_world_mask(rgb)[:50].any() and lr.gray_world_mask(rgb)[50:].all()
    dark = rgb.copy(); dark[100:200] = 10
    assert not lr.gray_world_mask(dark)[100:200].any()
    assert lr.rows_mask((10, 4), -3, 2).sum() == 8 and lr.rows_mask((10, 4), 8, 20).sum() == 8
    assert not lr.brightest_mask(rgb, 5.0, np.zeros(rgb.shape[:2], bool)).any()


def test_an_orange_thing_fools_the_whole_frame_and_not_the_others():
    rgb = scene((0.6, 0.6, 0.6))                         # a dim neutral scene: nothing is brighter than the barrel
    rgb[120:320, 200:440] = (250, 110, 30)               # a close orange barrel, the brightest thing in view
    assert lr.whole_frame(rgb).warmth > 0.4              # the white patch reads the barrel
    barrel = np.zeros(rgb.shape[:2], bool); barrel[120:320, 200:440] = True
    assert abs(lr.without_barrels(rgb, barrel).warmth) < 0.01
    assert abs(lr.above_gate(rgb).warmth) < 0.01
    assert abs(lr.tiles(rgb).warmth) < 0.01              # one tile is orange, the low quantile over the tiles is not
    edge = np.zeros(rgb.shape[:2], bool); edge[140:300, 220:420] = True     # a mask that misses a 20 px rim of the barrel ...
    assert lr.without_barrels(rgb, edge, margin=0).warmth > 0.4             # ... leaves the rim to be read
    assert abs(lr.without_barrels(rgb, edge, margin=20).warmth) < 0.01      # ... the margin takes it out


def test_grow():
    m = np.zeros((20, 20), bool); m[10, 10] = True
    assert lr.grow(m, 0).sum() == 1 and lr.grow(m, 2).sum() == 25 and lr.grow(m, 2)[8:13, 8:13].all()


def test_tiles_need_enough_bright_tiles():
    assert not lr.tiles(np.full((480, 640, 3), 30, np.uint8)).ok          # a dark frame: no tile votes
    rgb = np.full((480, 640, 3), 30, np.uint8)
    rgb[:120, :320] = 200                                                  # two bright tiles of sixteen
    assert len(lr.tile_votes(rgb)) == 2 and not lr.tiles(rgb).ok
    assert lr.tiles(rgb, min_tiles=2).ok
    assert lr.tiles_mask(rgb)[:120, :320].all() and not lr.tiles_mask(rgb)[120:].any()


def test_ramp():
    assert lr.ramp(0.05, 0.1, 0.2, 113, 40) == 113 and lr.ramp(0.3, 0.1, 0.2, 113, 40) == 40
    assert lr.ramp(0.15, 0.1, 0.2, 113, 40) == pytest.approx(76.5)
    assert lr.ramp(float("nan"), 0.1, 0.2, 113, 40) == 113                # a reading that says nothing moves nothing
    with pytest.raises(ValueError):
        lr.ramp(0.1, 0.2, 0.2, 1, 2)


def test_readings_never_write_to_the_frame():
    rgb = scene(WARM)
    rgb.setflags(write=False)
    before = rgb.copy()
    m = np.zeros(rgb.shape[:2], bool); m[100:150, 100:150] = True
    for f in (lr.whole_frame, lr.above_gate, lr.neutral, lr.least_colored, lr.highlights, lr.near_strip, lr.gray_world, lr.max_rgb, lr.tiles):
        f(rgb)
    lr.without_barrels(rgb, m)
    assert (rgb == before).all()


def test_nothing_that_runs_by_default_imports_lightread():
    """The readings are an experiment's kit: no other module of the package may import them."""
    for p in SRC.glob("*.py"):
        if p.name == "lightread.py":
            continue
        for node in ast.walk(ast.parse(p.read_text())):
            names = [a.name for a in node.names] if isinstance(node, (ast.Import, ast.ImportFrom)) else []
            mod = node.module or "" if isinstance(node, ast.ImportFrom) else ""
            assert "lightread" not in mod and not any("lightread" in n for n in names), f"{p.name} imports lightread"
