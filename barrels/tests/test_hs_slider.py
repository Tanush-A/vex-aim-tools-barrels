"""The slider tool without its window: ``tools/hs_slider.py``'s ``Session`` (state, keys, mouse, picture)."""
import importlib.util
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from barrels import hslabel as hl, io, pipeline as pl, splits as sp, viz
from barrels.io import BLUE, ORANGE

_spec = importlib.util.spec_from_file_location("hs_slider_tool", Path(__file__).resolve().parents[1] / "tools" / "hs_slider.py")
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)

A, B, T = "4A8B_sun_white_core_01", "4A8B_sun_white_occl_01", "4A8B_sun_white_clutter_01"
SPLITS = {"train": [A, B], "dev": [], "test": [T], "measured": []}
ADOPTED = {"orange": {"h_lo": 3, "h_hi": 13, "s_lo": 140}, "blue": {"h_lo": 103, "h_hi": 119, "s_lo": 113}}
ORANGE_BLOCK, BLUE_BLOCK = (slice(200, 260), slice(100, 150)), (slice(200, 260), slice(300, 350))


def _image() -> np.ndarray:
    hsv = np.zeros((480, 640, 3), np.uint8)
    hsv[..., 2] = 128                                   # gray
    hsv[ORANGE_BLOCK] = (8, 220, 220)
    hsv[BLUE_BLOCK] = (110, 220, 200)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


@pytest.fixture
def dirs(tmp_path):
    raw, labels = tmp_path / "raw", tmp_path / "labels"
    raw.mkdir(); labels.mkdir()
    for stem in (A, B):                                 # the test frame T has no image at all: it must never be asked for
        cv2.imwrite(str(raw / f"{stem}.png"), _image())
    return raw, labels


def _session(dirs, stems=(A, B), **kw):
    return tool.Session(list(stems), SPLITS, hl.adopted_model(), dirs[0], dirs[1], git="testhash", **kw)


def _click(s, i, value, scale=1.0):
    _, _, _, lo, hi = tool.SLIDERS[i]
    x0, x1, yc = tool.track(i, 640, 480)
    x = tool.value_to_x(value, lo, hi, x0, x1)
    s.on_mouse(cv2.EVENT_LBUTTONDOWN, x * scale, yc * scale)
    s.on_mouse(cv2.EVENT_LBUTTONUP, x * scale, yc * scale)


def test_every_slider_value_has_its_own_pixel():
    for i, (_, _, _, lo, hi) in enumerate(tool.SLIDERS):
        x0, x1, _ = tool.track(i, 640, 480)
        assert 0 <= x0 < x1 <= 1280
        for v in range(lo, hi + 1):
            assert tool.x_to_value(tool.value_to_x(v, lo, hi, x0, x1), lo, hi, x0, x1) == v
        assert tool.x_to_value(x0 - 50, lo, hi, x0, x1) == lo and tool.x_to_value(x1 + 50, lo, hi, x0, x1) == hi
    assert [s[3:] for s in tool.SLIDERS[:2]] == [(-30, 60), (-30, 60)]           # orange hue goes below 0


def test_starts_from_the_adopted_values_and_shows_raw_next_to_the_segmentation(dirs):
    s = _session(dirs)
    assert s.thr == ADOPTED and not s.dirty and not s.has_label
    view = s.render()
    assert view.shape == (480 + tool.PANEL_H, 1280, 3) and view.dtype == np.uint8
    img = _image()
    assert (view[:480, :640] == img).all()                                       # left: the raw frame, untouched
    right = view[:480, 640:]
    mask, barrels = s.result()
    want, _ = pl.segment(pl.Frame.from_image(img), hl.model_from_thresholds(hl.adopted_model(), ADOPTED))
    assert (mask == want).all() and (mask[ORANGE_BLOCK] == ORANGE).all() and (mask[BLUE_BLOCK] == BLUE).all()
    plain = tool.seg_picture(img, mask, barrels, None, False, False, "flat")
    assert tuple(plain[230, 125]) == viz.ORANGE_BGR and tuple(plain[230, 325]) == viz.BLUE_BGR
    assert tuple(plain[400, 500]) == tuple((img[400, 500].astype(np.float32) * 0.3 + 0.5).astype(np.uint8))     # dimmed, not recolored
    own = tool.seg_picture(img, mask, barrels, None, False, False, "own")
    assert (own[ORANGE_BLOCK] == img[ORANGE_BLOCK]).all()
    assert tuple(right[400, 500]) == tuple(plain[400, 500])
    assert s.status()[1].startswith("orange hue 3..13 S>=140   blue hue 103..119 S>=113")


def test_mouse_sets_a_slider_and_the_picture_follows(dirs):
    s = _session(dirs)
    _click(s, 2, 255)                                                             # orange S floor above the block's 220
    assert s.thr["orange"]["s_lo"] == 255 and s.sel == 2 and s.dirty and s.grab is None
    assert not (s.result()[0] == ORANGE).any() and (s.result()[0][BLUE_BLOCK] == BLUE).all()
    x0, x1, yc = tool.track(0, 640, 480)
    s.on_mouse(cv2.EVENT_LBUTTONDOWN, tool.value_to_x(-3, -30, 60, x0, x1), yc)
    assert s.thr["orange"]["h_lo"] == -3 and s.grab == 0
    s.on_mouse(cv2.EVENT_MOUSEMOVE, tool.value_to_x(-12, -30, 60, x0, x1), yc + 200)   # a drag may leave the row
    assert s.thr["orange"]["h_lo"] == -12
    s.on_mouse(cv2.EVENT_MOUSEMOVE, x1 + 300, yc)                                 # dragged past the high slider: stops at it
    assert s.thr["orange"]["h_lo"] == s.thr["orange"]["h_hi"] == 13
    s.on_mouse(cv2.EVENT_LBUTTONUP, 0, 0)
    s.on_mouse(cv2.EVENT_MOUSEMOVE, x0, yc)                                       # not dragging any more
    assert s.thr["orange"]["h_lo"] == 13
    s.on_mouse(cv2.EVENT_LBUTTONDOWN, 300, 200)                                   # a click on the picture changes nothing
    assert s.thr["orange"] == {"h_lo": 13, "h_hi": 13, "s_lo": 255}
    big = _session(dirs, scale=2.0)
    _click(big, 5, 77, scale=2.0)
    assert big.thr["blue"]["s_lo"] == 77 and big.render().shape == (2 * (480 + tool.PANEL_H), 2560, 3)


def test_keys_select_nudge_reset_and_undo(dirs):
    s = _session(dirs)
    for k in "1-":
        s.on_key(ord(k))
    assert s.thr["orange"]["h_lo"] == 2
    s.on_key(ord("["))
    assert s.thr["orange"]["h_lo"] == -3 and "(=177..13)" in s.status()[1]
    for k in "2[[[[":                                                             # hue high cannot go below hue low
        s.on_key(ord(k))
    assert s.thr["orange"]["h_hi"] == -3
    for k in "6=]":
        s.on_key(ord(k))
    assert s.thr["blue"]["s_lo"] == 119
    s.on_key(ord("r"))
    assert s.thr == ADOPTED and not s.dirty
    s.on_key(ord("4")); s.on_key(ord("="))
    s.on_key(ord("u"))
    assert s.thr == ADOPTED
    for k in "btm":
        s.on_key(ord(k))
    assert (s.show_boxes, s.show_truth, tool.PAINTS[s.paint]) == (False, True, "own") and "no hand-drawn boxes" in s.msg
    assert s.on_key(200) is True and s.thr == ADOPTED


def test_unsaved_changes_are_not_lost_silently(dirs):
    s = _session(dirs)
    assert s.on_key(ord("n")) and s.stem == B and s.on_key(ord("p")) and s.stem == A      # untouched: moves, writes nothing
    assert not list(dirs[1].iterdir())
    _click(s, 2, 100)
    assert s.on_key(ord("n")) and s.stem == A and "UNSAVED" in s.msg and "UNSAVED" in s.status()[2]
    assert s.on_key(ord("b")) and s.on_key(ord("n")) and s.stem == A                      # another key in between: asks again
    assert s.on_key(ord("p")) and s.stem == A                                             # a different leave key: asks again
    assert s.on_key(ord("q")) is True and s.on_key(27) is False                           # q then Esc = the same key twice
    assert s.on_key(ord("n")) and s.on_key(ord("n")) and s.stem == B                      # n twice: discarded
    assert not list(dirs[1].iterdir())
    s.on_key(ord("p"))
    assert s.thr == ADOPTED                                                               # the discarded change is gone
    assert _session(dirs).on_key(ord("q")) is False                                       # nothing changed: quits at once


def test_save_writes_the_label_and_the_next_session_starts_from_it(dirs):
    s = _session(dirs)
    _click(s, 0, -3)
    _click(s, 5, 90)
    s.on_key(ord("w"))
    assert not s.dirty and s.has_label and [p.name for p in dirs[1].iterdir()] == [f"{A}_hs.json"]
    meta = io.load_hs(A, dirs[1], raw_dir=dirs[0])                                        # passes the image sha check
    assert meta["orange"] == {"h_lo": -3, "h_hi": 13, "s_lo": 140} and meta["blue"] == {"h_lo": 103, "h_hi": 119, "s_lo": 90}
    assert meta["boxes_drawn"] == len(s.result()[1]) and meta["detector_git"] == "testhash" and meta["base_model"] == "eb863d84"
    assert (meta["v_min"], meta["horizon_row"], meta["reviewed"], meta["image_sha1"]) == (40, 50, True, io.file_sha1(dirs[0] / f"{A}.png"))
    assert s.on_key(ord("n")) and s.stem == B and s.thr == ADOPTED                        # saved: moves at once; B starts adopted
    s.on_key(ord("c"))                                                                    # copy the previous frame's saved thresholds
    assert s.thr["orange"]["h_lo"] == -3 and s.thr["blue"]["s_lo"] == 90 and s.dirty and A in s.msg
    again = _session(dirs)
    assert again.has_label and again.thr == hl.copy_thresholds(meta) and not again.dirty
    again.on_key(ord("r"))
    assert again.thr == ADOPTED and again.dirty                                           # reset on a labeled frame is a change
    again.on_key(ord("c"))
    assert "nothing to copy" in again.msg and again.thr == ADOPTED                        # the first frame has no previous one


def test_a_changed_image_or_a_broken_label_is_reported(dirs):
    s = _session(dirs)
    s.on_key(ord("w"))
    img = _image(); img[0, 0] = 9
    cv2.imwrite(str(dirs[0] / f"{A}.png"), img)
    assert "image changed" in _session(dirs).msg
    (dirs[1] / f"{A}_hs.json").write_text(json.dumps({"version": 1, "stem": A, "orange": {"h_lo": 20, "h_hi": 3, "s_lo": 1}}))
    broken = _session(dirs)
    assert "ignored" in broken.msg and broken.thr == ADOPTED and not broken.has_label


def test_truth_boxes_are_drawn_thin_white_when_asked(dirs):
    io.save_boxes(A, {"image_sha1": "", "barrels": [{"color": "orange", "bbox": [90, 190, 160, 270]}]}, labels_dir=dirs[1])
    s = _session(dirs)
    assert len(s.truth) == 1 and "truth boxes=1 (hidden)" in s.status()[0]
    off = s.render()[:480, 640:].copy()
    s.on_key(ord("t"))
    on = s.render()[:480, 640:]
    assert tuple(on[190, 120]) == (255, 255, 255) and tuple(off[190, 120]) != (255, 255, 255)
    assert (s.render()[:480, :640] == _image()).all()                                     # the raw side stays raw


def test_a_test_frame_is_refused_before_its_image_is_looked_for(dirs):
    with pytest.raises(hl.RefusedFrame):                 # T has no image: FileNotFoundError would mean the guard came too late
        _session(dirs, stems=(T,))
    s = _session(dirs, stems=(A, T))
    with pytest.raises(hl.RefusedFrame):
        s.on_key(ord("n"))
    with pytest.raises(hl.RefusedFrame):
        _session(dirs, stems=("4A8B_sun_white_calib_01",))
    with pytest.raises(hl.RefusedFrame):
        _session(dirs, stems=("4A8B_dim_gray_core_01",))


def test_parse_thresholds():
    assert tool.parse_thresholds("-3,13,140,103,119,113")["orange"] == {"h_lo": -3, "h_hi": 13, "s_lo": 140}
    for bad in ("1,2,3", "a,b,c,d,e,f", "13,3,140,103,119,113"):
        with pytest.raises(ValueError):
            tool.parse_thresholds(bad)


def test_command_line_lists_only_train_frames_and_selftest_writes_the_picture(tmp_path, capsys):
    splits = sp.load_splits()
    train = sorted(s for s in splits["train"] if hl.scene_matches(s, hl.DEFAULT_SCENES) and io.find_image(s))
    if not train or not splits["test"]:
        pytest.skip("no frames here")
    assert tool.main(["--list", "--scenes", "all", "--labels", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    listed = [line.split()[0] for line in out.splitlines() if line.startswith(("4A8B", "DAVE"))]
    assert listed and not set(listed) & set(splits["test"]) and set(listed) <= set(splits["train"])
    assert f"refused, {hl.REFUSE_TEST}: {len(splits['test'])} frame(s)" in out
    assert tool.main(["--list", "--scenes", "all", "--filter", sorted(splits["test"])[0], "--labels", str(tmp_path)]) == 0
    assert "\n0 frame(s)" in capsys.readouterr().out
    assert tool.main(["--scenes", "all", "--filter", sorted(splits["test"])[0], "--selftest", str(tmp_path / "t.png")]) == 1
    assert not (tmp_path / "t.png").exists()                                              # a test frame is never rendered
    png = tmp_path / "x.png"
    assert tool.main(["--filter", train[0], "--labels", str(tmp_path), "--selftest", str(png), "--thresholds=-3,13,140,103,119,113"]) == 0
    assert cv2.imread(str(png)).shape == (480 + tool.PANEL_H, 1280, 3)
    assert "orange hue -3..13 (=177..13) S>=140" in capsys.readouterr().out
    assert not list(tmp_path.glob("*_hs.json"))                                           # the selftest saves no label
