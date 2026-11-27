"""The experiment 2026-11-27_occl_photo (DetConfig.side_photo): off by default, and the cut line's measurements."""
import dataclasses

import numpy as np
import pytest

from barrels import detector as det
from barrels.io import BLUE, ORANGE


def _photo_with_edge(col: int, rows=(0, 480), dark_left: bool = True) -> np.ndarray:
    img = np.full((480, 640, 3), 200, np.uint8)
    if dark_left:
        img[rows[0]:rows[1], :col] = 30
    else:
        img[rows[0]:rows[1], col:] = 30
    return img


def _barrel_mask(x0=100, x1=125, top=120, bottom=170) -> np.ndarray:
    m = np.zeros((480, 640), np.uint8)
    m[top:bottom, x0:x1] = ORANGE
    m[140:148, x0:x1] = BLUE
    return m


def test_default_is_off_and_validated():
    assert det.DetConfig().side_photo == "off"
    with pytest.raises(ValueError):
        det.DetConfig(side_photo="maybe")


def test_photo_changes_nothing_when_off():
    m = _barrel_mask()
    photo = _photo_with_edge(100)
    assert det.detect(m, det.DetConfig(), photo=photo) == det.detect(m, det.DetConfig())


def test_photo_steps_finds_the_edge():
    g = det.photo_steps(_photo_with_edge(100))
    assert g.shape == (480, 640)
    assert abs(int(np.argmax(g[200, 50:150])) + 50 - 100) <= 2
    assert g[200, 300] == 0


def test_cut_line_runs_on_above_a_front_edge():
    m = _barrel_mask()
    steps = det.photo_steps(_photo_with_edge(100))
    up = det.cut_line_in_band(steps, m, "L", 100, 120, 170, 50.0, 50.0, 144.0, "up")
    assert up["frac"] >= 0.9 and abs(up["lean"]) < 0.1 and up["cross"] == 0.0 and abs(up["touch"]) <= 1.5
    # the free right end: no edge in the photo there
    right = det.cut_line_in_band(steps, m, "R", 125, 120, 170, 50.0, 50.0, 144.0, "up")
    assert right["frac"] == 0.0


def test_cut_line_crossed_by_the_barrel_is_an_edge_behind():
    m = _barrel_mask(x0=95)                                         # the barrel runs 5 px past the edge: the edge is behind it
    steps = det.photo_steps(_photo_with_edge(100))
    up = det.cut_line_in_band(steps, m, "L", 95, 120, 170, 50.0, 50.0, 144.0, "up")
    assert up["cross"] > 0.5
