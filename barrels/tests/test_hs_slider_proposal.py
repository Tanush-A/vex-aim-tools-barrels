"""The slider tool's proposal (2026-11-24): where the sliders start on a frame with no saved label (Claude's proposal
file, else the computed proposal, else the adopted values), the bands, what the saved label records, the render grid,
and the label / proposal files in ``io``. Synthetic frames in a temporary folder."""
import importlib.util
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from barrels import hslabel as hl, io

_spec = importlib.util.spec_from_file_location("hs_slider_tool_p", Path(__file__).resolve().parents[1] / "tools" / "hs_slider.py")
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)

A, B, T = "4A8B_sun_white_core_01", "4A8B_sun_white_occl_01", "4A8B_sun_white_clutter_01"
SPLITS = {"train": [A, B], "dev": [], "test": [T], "measured": []}
ADOPTED = {"orange": {"h_lo": 3, "h_hi": 13, "s_lo": 140}, "blue": {"h_lo": 103, "h_hi": 119, "s_lo": 113}}
CLAUDE = {"orange": {"h_lo": 0, "h_hi": 15, "s_lo": 150}, "blue": {"h_lo": 100, "h_hi": 120, "s_lo": 120}}


def _image() -> np.ndarray:
    hsv = np.zeros((480, 640, 3), np.uint8)
    hsv[..., 2] = 128
    hsv[200:300, 100:170] = (8, 220, 220)               # an orange "barrel"
    hsv[240:250, 100:170] = (110, 220, 200)             # its blue stripe
    hsv[200:300, 300:370] = (110, 220, 200)             # a blue one
    hsv[240:250, 300:370] = (8, 220, 220)
    hsv[350:400, 450:600] = (10, 90, 200)               # orange-ish clutter of low saturation
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


@pytest.fixture
def dirs(tmp_path):
    raw, labels = tmp_path / "raw", tmp_path / "labels"
    raw.mkdir(); labels.mkdir()
    for stem in (A, B):
        cv2.imwrite(str(raw / f"{stem}.png"), _image())
    io.save_boxes(A, {"image_sha1": "", "barrels": [{"color": "orange", "bbox": [100, 200, 170, 300]},
                                                     {"color": "blue", "bbox": [300, 200, 370, 300]}]}, labels_dir=labels)
    return raw, labels


def _session(dirs, stems=(A, B), **kw):
    kw = {"propose": True, "background": False, **kw}
    return tool.Session(list(stems), SPLITS, hl.adopted_model(), dirs[0], dirs[1], git="testhash", **kw)


def test_a_frame_with_boxes_and_no_label_starts_at_the_computed_proposal_with_bands(dirs):
    s = _session(dirs)
    assert s.start == "computed" and s.proposal == s.thr and not s.dirty
    assert set(s.ranges) == set(tool.hx.THRESHOLDS)
    for t, (lo, hi) in s.ranges.items():
        assert lo <= hx_flat(s.thr)[t] <= hi or t.endswith(("h_lo", "h_hi"))   # the start values sit in their bands (hue: the anchor may be kept)
    # the floor sits above the clutter's saturation and at or below the barrel's
    assert 90 < s.thr["orange"]["s_lo"] <= 220
    assert "computed proposal" in s.status()[0]
    view = s.render()
    assert (view[480:, :] == tool.BAND).all(axis=2).any()                          # a band is drawn


def hx_flat(thr):
    return tool.hx.flat(thr)


def test_accepting_the_proposal_records_it_and_moving_a_slider_is_recorded(dirs):
    s = _session(dirs)
    s.on_key(ord("w"))
    d = json.loads(io.hs_path(A, dirs[1]).read_text())
    assert d["proposed"] is True and d["proposed_by"] == "computed" and d["moved"] is False
    assert d["proposal"] == {k: d[k] for k in ("orange", "blue")}
    assert set(d["ranges"]) == {"orange", "blue"} and len(d["ranges"]["orange"]["s_lo"]) == 2
    io.load_hs(A, dirs[1], check_image=False)                                       # it reads back
    s.on_key(ord("3")); s.on_key(ord("]")); s.on_key(ord("w"))                      # move a slider, save again
    d = json.loads(io.hs_path(A, dirs[1]).read_text())
    assert d["proposed_by"] == "computed" and d["moved"] is True


def test_claude_proposal_file_comes_first_and_its_reasoning_is_shown(dirs):
    io.save_hs_proposed(A, CLAUDE, "barrels saturated; clutter below S 100", dirs[1])
    s = _session(dirs)
    assert s.start == "claude" and s.thr == CLAUDE and "clutter below S 100" in s.msg
    assert s.ranges is not None                                                     # bands around Claude's numbers
    s.on_key(ord("w"))
    d = io.load_hs(A, dirs[1], check_image=False)
    assert d["proposed_by"] == "claude" and d["moved"] is False and d["proposal"] == CLAUDE


def test_a_saved_label_wins_and_a_frame_without_boxes_starts_adopted(dirs):
    io.save_hs_proposed(A, CLAUDE, "x", dirs[1])
    s = _session(dirs)
    s.on_key(ord("1")); s.on_key(ord("-")); s.on_key(ord("w"))
    s2 = _session(dirs)
    assert s2.start == "saved label" and s2.thr != CLAUDE and s2.prov["proposed_by"] == "claude"
    s2.on_key(ord("n"))                                                             # B: no boxes, no proposal file
    assert s2.stem == B and s2.start == "adopted" and s2.thr == ADOPTED and s2.ranges is None
    s2.on_key(ord("w"))
    d = io.load_hs(B, dirs[1], check_image=False)
    assert d["proposed"] is False and d["proposed_by"] is None and d["ranges"] is None


def test_no_propose_and_a_late_proposal_after_a_slider_moved(dirs):
    s = _session(dirs, propose=False)
    assert s.start == "adopted" and s.thr == ADOPTED and s.ranges is None
    s = _session(dirs, background=True)
    s.guide_key = None                                       # hold the result back, move a slider, then deliver it
    s.on_key(ord("3")); s.on_key(ord("]"))
    s.guide_key = (A, None)
    while not s._guides.get(s.guide_key):
        pass
    s.poll()
    assert s.start == "adopted" and s.dirty and s.ranges is not None and "not applied" in s.msg


def test_a_test_frame_is_still_refused(dirs):
    with pytest.raises(hl.RefusedFrame):
        _session(dirs, stems=(T,))


def test_parse_try_and_the_render_grid(dirs):
    assert tool.parse_try("o:-1,6,167;b:102,121,79", ADOPTED) == {"orange": {"h_lo": -1, "h_hi": 6, "s_lo": 167}, "blue": {"h_lo": 102, "h_hi": 121, "s_lo": 79}}
    assert tool.parse_try("b:100,120,90", ADOPTED)["orange"] == ADOPTED["orange"]
    for bad in ("x:1,2,3", "o:1,2", "o:13,3,140", "o:a,b,c"):
        with pytest.raises(ValueError):
            tool.parse_try(bad, ADOPTED)
    s = _session(dirs, propose=False)
    pic = tool.render_grid(s.img, s.truth, s.base, [("adopted", ADOPTED), ("claude", CLAUDE)], cols=3)
    assert pic.shape == (480 + 44, 3 * 640, 3)
    pic = tool.render_grid(s.img, s.truth, s.base, [("a", ADOPTED)] * 3, cols=3)
    assert pic.shape == (2 * (480 + 44), 3 * 640, 3)
    assert tool.resolve_try("adopted", s)[1] == ADOPTED and tool.resolve_try("computed", s)[0] == "computed"


def test_io_label_provenance_and_proposal_files(tmp_path):
    base = {"orange": ADOPTED["orange"], "blue": ADOPTED["blue"], "v_min": 40, "horizon_row": 50, "base_model": "eb863d84", "boxes_drawn": 2}
    p = io.save_hs(A, base, tmp_path)
    assert "proposed" not in json.loads(p.read_text())                                # a plain label is written as before
    io.save_hs(A, {**base, "proposed_by": "claude", "moved": True, "proposal": CLAUDE, "ranges": {"orange": {"s_lo": [100, 180]}}}, tmp_path)
    d = io.load_hs(A, tmp_path, check_image=False)
    assert d["proposed"] is True and d["ranges"]["orange"]["s_lo"] == [100, 180]
    for bad in ({"proposed_by": "robot"}, {"moved": "yes"}, {"ranges": {"orange": {"s_lo": [180, 100]}}}, {"ranges": {"green": {}}},
                {"proposal": {"orange": {"h_lo": 1}}}, {"proposed": 1}):
        with pytest.raises(ValueError):
            io.validate_hs({**base, **bad})
    io.save_hs_proposed(A, CLAUDE, "why", tmp_path)
    q = io.load_hs_proposed(A, tmp_path)
    assert q["reasoning"] == "why" and hl.copy_thresholds(q) == CLAUDE and q["by"] == "claude"
    assert io.hs_proposed_path(A, tmp_path).name == f"{A}_hs_proposed.json"
    assert not io.hs_path(A, tmp_path).name.endswith("_proposed.json")
    io.hs_proposed_path(B, tmp_path).write_text(json.dumps({"version": 1, "stem": A, **CLAUDE}))
    with pytest.raises(ValueError):
        io.load_hs_proposed(B, tmp_path)                                               # another frame's proposal
