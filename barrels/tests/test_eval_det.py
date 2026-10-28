import math

import pytest

from barrels import eval_det as ed, geometry as geo, io
from barrels.detect_types import Barrel

O, B = io.ORANGE, io.BLUE


def bx(color, x0, y0, w, h, conf=1.0, flags=(), ground=None):
    return Barrel(color=color, bbox=(x0, y0, x0 + w, y0 + h), confidence=conf, flags=frozenset(flags), ground_xy_mm=ground)


def test_box_iou():
    assert ed.box_iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert ed.box_iou((0, 0, 10, 10), (5, 0, 15, 10)) == pytest.approx(1 / 3)
    assert ed.box_iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_perfect_and_shifted():
    gts = [bx(O, 100, 200, 60, 60), bx(B, 300, 200, 60, 60)]
    r = ed.evaluate_frame("4A8B_window_light_core_01", list(gts), gts, geo.NOMINAL)
    assert r.tp == {O: 1, B: 1} and r.fp == {O: 0, B: 0} and r.fn == {O: 0, B: 0} and not r.negative
    assert all(m.iou == 1.0 and m.bottom_row_err_px == 0 and m.ground_err_proj_mm == 0 for m in r.matches)
    shifted = [bx(O, 130, 200, 60, 60), bx(B, 300, 200, 60, 60)]      # orange shifted by half its width: IoU 1/3
    r2 = ed.evaluate_frame("x", shifted, gts, geo.NOMINAL)
    assert r2.tp == {O: 0, B: 1} and r2.fp == {O: 1, B: 0} and r2.fn == {O: 1, B: 0}
    assert r2.tp_loose[O] == 0 or r2.tp_loose[O] == 1          # depends on how far 30 px is on the ground at that row
    assert r2.condition() == "?_?_?"


def test_two_preds_one_gt_and_wrong_color():
    gts = [bx(O, 100, 200, 60, 60)]
    preds = [bx(O, 102, 200, 60, 60, conf=0.6), bx(O, 100, 202, 60, 60, conf=0.9)]
    r = ed.evaluate_frame("x", preds, gts)
    assert r.tp[O] == 1 and r.fp[O] == 1 and r.fn[O] == 0
    assert r.matches[0].pred_idx == 1                           # the higher-confidence prediction wins
    rc = ed.evaluate_frame("x", [bx(B, 100, 200, 60, 60)], gts)
    assert rc.tp == {O: 0, B: 0} and rc.fp[B] == 1 and rc.fn[O] == 1 and rc.color_confusions == 1


def test_ignore_flags_both_ways():
    gts = [bx(O, 100, 200, 60, 60, flags=["occluded"])]
    hit = ed.evaluate_frame("x", [bx(O, 100, 200, 60, 60)], gts)
    assert hit.tp[O] == 0 and hit.fp[O] == 0 and hit.fn[O] == 0 and hit.n_ignored[O] == 1
    miss = ed.evaluate_frame("x", [], gts)
    assert miss.fn[O] == 0 and miss.n_ignored[O] == 1 and not miss.negative


def test_bottom_row_sign_and_ground_errors():
    gt = bx(O, 300, 200, 60, 60, ground=(150.0, 0.0))
    pred = bx(O, 300, 200, 60, 70)                               # bottom 10 px lower
    r = ed.evaluate_frame("x", [pred], [gt], geo.NOMINAL)
    m = r.matches[0]
    assert m.bottom_row_err_px == 10 and m.bottom_mid_err_px == 10
    px, py = geo.NOMINAL.barrel_axis_xy(*pred.bottom_mid); gx, gy = geo.NOMINAL.barrel_axis_xy(*gt.bottom_mid)
    assert m.ground_err_proj_mm == pytest.approx(math.hypot(px - gx, py - gy))
    assert m.range_err_mm == pytest.approx(px - gx) and m.range_err_mm < 0      # lower in the image = closer
    assert m.ground_err_mm == pytest.approx(math.hypot(px - 150.0, py - 0.0))


def test_negative_frame_aggregate_write_and_score(tmp_path):
    neg = ed.evaluate_frame("4A8B_window_light_neg_01", [bx(B, 10, 300, 20, 20)], [], geo.NOMINAL)
    assert neg.negative and neg.fp[B] == 1
    gts = [bx(O, 100, 200, 60, 60), bx(B, 300, 200, 60, 60)]
    pos = ed.evaluate_frame("4A8B_window_light_core_01", [bx(O, 100, 200, 60, 60)], gts, geo.NOMINAL)
    top = ed.evaluate_frame("4A8B_window_light_top_01", [], [bx(O, 100, 300, 300, 180, flags=["top_only"])], geo.NOMINAL)
    aggs = ed.aggregate([neg, pos, top])
    assert list(aggs)[0] == "ALL" and set(aggs) == {"ALL", "window_light_neg", "window_light_core", "window_light_top"}
    a = aggs["ALL"]
    assert a.n_negative == 1 and a.neg_false_detections == 1
    assert a.prf(O) == (1.0, 1.0, 1.0) and a.prf(B)[1] == 0.0 and a.counts[O]["ign"] == 1
    md, csv_s, csv_i = ed.write_results([neg, pos, top], tmp_path / "run", title="t")
    assert md.exists() and csv_s.exists() and csv_i.exists() and (tmp_path / "run" / "per_barrel.csv").exists()
    assert "| ALL |" in md.read_text() and csv_s.read_text().startswith("condition,n_frames,n_neg,neg_false_detections,orange_n_gt")
    sc = ed.score([neg, pos, top], {neg.name: "neg", pos.name: "core", top.name: "top"})
    assert sc["disqualified"] and sc["F1_o"] == 1.0 and sc["F1_b"] == 0.0 and sc["primary"] == 0.5
    sc2 = ed.score([pos], {pos.name: "core"})
    assert not sc2["disqualified"] and sc2["neg_false_detections"] == 0


def test_greedy_matching_is_deterministic():
    gts = [bx(O, 0, 0, 10, 10), bx(O, 20, 0, 10, 10)]
    preds = [bx(O, 1, 0, 10, 10), bx(O, 21, 0, 10, 10)]
    a = ed.match_greedy(preds, gts, lambda p, g: ed.box_iou(p.bbox, g.bbox), 0.5)
    b = ed.match_greedy(preds, gts, lambda p, g: ed.box_iou(p.bbox, g.bbox), 0.5)
    assert a == b and sorted((p, g) for p, g, _ in a) == [(0, 0), (1, 1)]
    assert ed.match_greedy([], gts, lambda p, g: 1.0, 0.5) == []
