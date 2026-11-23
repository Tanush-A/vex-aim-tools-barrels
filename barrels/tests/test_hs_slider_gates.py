"""The slider tool's gate sliders and wider blue hue (2026-11-25): the V gate and the horizon row are settable,
saved in the label's ``v_min`` / ``horizon_row``, and a label saved before keeps its meaning."""
import importlib.util
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from barrels import hslabel as hl, io, pipeline as pl
from barrels.io import BLUE, ORANGE

_spec = importlib.util.spec_from_file_location("hs_slider_tool_g", Path(__file__).resolve().parents[1] / "tools" / "hs_slider.py")
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)

A, B = "4A8B_sun_white_core_01", "4A8B_sun_white_occl_01"
SPLITS = {"train": [A, B], "dev": [], "test": [], "measured": []}
ADOPTED = {"orange": {"h_lo": 3, "h_hi": 13, "s_lo": 140}, "blue": {"h_lo": 103, "h_hi": 119, "s_lo": 113}}
DARK_ORANGE = (slice(200, 260), slice(100, 150))       # V = 30: under today's V gate of 40
OLIVE = (slice(200, 260), slice(300, 350))             # a "blue" painted under a warm lamp: hue 40, S 60
HIGH = (slice(20, 40), slice(500, 560))                # a bright orange patch above row 50


def _image() -> np.ndarray:
    hsv = np.zeros((480, 640, 3), np.uint8)
    hsv[..., 2] = 128
    hsv[DARK_ORANGE] = (8, 220, 30)
    hsv[OLIVE] = (40, 60, 90)
    hsv[HIGH] = (8, 220, 220)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


@pytest.fixture
def dirs(tmp_path):
    raw, labels = tmp_path / "raw", tmp_path / "labels"
    raw.mkdir(); labels.mkdir()
    for stem in (A, B):
        cv2.imwrite(str(raw / f"{stem}.png"), _image())
    return raw, labels


def _session(dirs, stems=(A, B)):
    return tool.Session(list(stems), SPLITS, hl.adopted_model(), dirs[0], dirs[1], git="testhash", propose=False)


def test_eight_sliders_blue_reaches_the_whole_circle_and_each_value_has_its_pixel():
    assert len(tool.SLIDERS) == 8 and tool.SLIDERS[3][3:] == (0, 179) and tool.SLIDERS[4][3:] == (0, 179)
    assert [s[:2] for s in tool.SLIDERS[6:]] == [("gate", "v_min"), ("gate", "horizon_row")]
    ys = set()
    for i, (_, _, _, lo, hi) in enumerate(tool.SLIDERS):
        x0, x1, yc = tool.track(i, 640, 480)
        assert 0 <= x0 < x1 <= 1280 and 480 < yc < 480 + tool.PANEL_H
        ys.add((x0 // 640, yc))
        for v in range(lo, hi + 1):
            assert tool.x_to_value(tool.value_to_x(v, lo, hi, x0, x1), lo, hi, x0, x1) == v
    assert len(ys) == 8                                          # no two sliders share a place
    assert tool.LIMITS["blue_h_lo"] == (0, 179) and tool.LIMITS["orange_h_lo"] == (-30, 60) and "v_min" not in tool.LIMITS


def test_gates_start_at_todays_values_and_move_the_segmentation(dirs):
    s = _session(dirs)
    assert s.gates == {"v_min": 40, "horizon_row": 50} and not s.dirty
    mask, _ = s.result()
    assert not (mask[DARK_ORANGE] == ORANGE).any() and not (mask[HIGH] == ORANGE).any()
    s.on_key(ord("7"))
    for _ in range(3):
        s.on_key(ord("["))                                       # V gate 40 -> 25
    assert s.gates["v_min"] == 25 and s.dirty
    assert (s.result()[0][DARK_ORANGE] == ORANGE).all()          # the dark orange now passes
    s.on_key(ord("8"))
    s.set_value(7, 0)
    assert (s.result()[0][HIGH] == ORANGE).all()                 # rows above 50 are painted with the horizon at 0
    s.set_value(6, 999)
    assert s.gates["v_min"] == 150                               # kept inside the slider
    s.on_key(ord("r"))
    assert s.gates == {"v_min": 40, "horizon_row": 50} and s.thr == ADOPTED and not s.dirty
    s.set_value(6, 10); s.on_key(ord("u"))
    assert s.gates["v_min"] == 40 and not s.dirty
    assert "V >= 40, rows >= 50" in s.status()[1]
    assert s.render().shape == (480 + tool.PANEL_H, 1280, 3)


def test_blue_hue_below_60_paints_the_washed_out_blue(dirs):
    s = _session(dirs)
    assert not (s.result()[0][OLIVE] == BLUE).any()
    s.set_value(3, 30); s.set_value(5, 40)                       # blue hue 30..119, S >= 40
    assert s.thr["blue"]["h_lo"] == 30 and (s.result()[0][OLIVE] == BLUE).all()


def test_saved_gates_round_trip_and_copy_to_the_next_frame(dirs):
    s = _session(dirs)
    s.set_value(6, 20); s.set_value(7, 30)
    s.on_key(ord("w"))
    meta = io.load_hs(A, dirs[1], raw_dir=dirs[0])
    assert (meta["v_min"], meta["horizon_row"]) == (20, 30) and hl.gates_of(hl.adopted_model(), meta) == {"v_min": 20, "horizon_row": 30}
    assert "V >= 20, rows >= 30" in s.msg
    again = _session(dirs)
    assert again.gates == {"v_min": 20, "horizon_row": 30} and not again.dirty and again.msg == ""   # no "set against" warning
    again.on_key(ord("n"))
    assert again.gates == {"v_min": 40, "horizon_row": 50}
    again.on_key(ord("c"))
    assert again.gates == {"v_min": 20, "horizon_row": 30} and again.dirty


def test_a_label_saved_before_the_gate_sliders_means_what_it_meant(dirs):
    old = {"version": 1, "stem": A, "image_sha1": "", "orange": {"h_lo": 3, "h_hi": 13, "s_lo": 140},
           "blue": {"h_lo": 103, "h_hi": 119, "s_lo": 113}, "v_min": 40, "horizon_row": 50, "base_model": "eb863d84",
           "detector_git": "x", "boxes_drawn": 0, "reviewed": True, "note": ""}
    (dirs[1] / f"{A}_hs.json").write_text(json.dumps(old))
    s = _session(dirs)
    assert s.has_label and s.gates == {"v_min": 40, "horizon_row": 50} and not s.dirty
    base = hl.adopted_model()
    m_old = hl.model_from_thresholds(base, ADOPTED)
    m_new = hl.model_from_thresholds(base, ADOPTED, hl.gates_of(base, old))
    assert m_old.cfg == m_new.cfg == base.cfg


def test_model_from_thresholds_gates_and_their_checks():
    base = hl.adopted_model()
    m = hl.model_from_thresholds(base, ADOPTED, {"v_min": 25})
    assert m.cfg.v_min == 25 and m.cfg.horizon_row == base.cfg.horizon_row and base.cfg.v_min == 40
    assert m.cfg.short_hash() != base.cfg.short_hash()
    for bad in ({"v_min": -1}, {"v_min": 300}, {"horizon_row": 900}, {"tie": "orange"}, {"v_min": 2.5}):
        with pytest.raises(ValueError):
            hl.model_from_thresholds(base, ADOPTED, bad)
    assert hl.gates_of(base) == {"v_min": 40, "horizon_row": 50}
    lm = hl.label_meta("x", "", ADOPTED, base, 0, "g", gates={"v_min": 30})
    assert (lm["v_min"], lm["horizon_row"]) == (30, 50)
    assert (hl.label_meta("x", "", ADOPTED, base, 0, "g")["v_min"]) == 40


def test_parse_try_reads_gate_parts_and_the_grid_uses_them(dirs):
    thr = tool.parse_try("b:30,119,40;v:25;z:0", ADOPTED)
    assert thr["gates"] == {"v_min": 25, "horizon_row": 0} and thr["blue"] == {"h_lo": 30, "h_hi": 119, "s_lo": 40}
    assert "gates" not in tool.parse_try("o:1,2,3", ADOPTED)
    with pytest.raises(ValueError):
        tool.parse_try("v:abc", ADOPTED)
    img = _image()
    plain = tool.grid_tile(img, None, hl.adopted_model(), ADOPTED, "a", None)
    gated = tool.grid_tile(img, None, hl.adopted_model(), thr, "g", None)
    assert plain.shape == gated.shape and not np.array_equal(plain, gated)
    assert tool.gates_text({"v_min": 40}, {"v_min": 40, "horizon_row": 50}) == ""
    assert tool.gates_text({"v_min": 30}, {"v_min": 40, "horizon_row": 50}) == "   V >= 30, rows >= 50"
