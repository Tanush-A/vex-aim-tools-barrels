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


# ---------------------------------------------------------------- v2 rule (EVAL.md 2026-11-02)

def test_v2_bottom_edge_tolerance():
    gt = [bx(O, 100, 200, 60, 60)]                              # tol = max(3, 0.1 * 60) = 6 px
    far = [bx(O, 100, 200, 60, 70)]                             # IoU 6/7 but the bottom is 10 px too low
    r = ed.evaluate_frame("x", far, gt, rule="v2")
    assert r.rule == "v2" and r.tp[O] == 0 and r.fp[O] == 1 and r.fn[O] == 1 and r.matches == []
    assert r.unmatched_gt == [0] and r.unmatched_pred == [0]
    assert ed.evaluate_frame("x", far, gt).tp[O] == 1           # v1: IoU alone decides
    near = [bx(O, 100, 200, 60, 65)]                            # 5 px low: inside the tolerance
    r2 = ed.evaluate_frame("x", near, gt, rule="v2")
    assert r2.tp[O] == 1 and r2.fp[O] == 0 and r2.fn[O] == 0
    m = r2.matches[0]
    assert m.bottom_row_err_px == 5 and m.bottom_err_frac == pytest.approx(5 / 60) and m.gt_flags == () and not m.bottom_estimated
    assert ed.evaluate_frame("x", [bx(O, 100, 200, 60, 66)], gt, rule="v2").tp[O] == 1     # exactly 6 px: inclusive
    assert ed.evaluate_frame("x", [bx(O, 100, 194, 60, 60)], gt, rule="v2").tp[O] == 1     # 6 px too high, same rule
    with pytest.raises(ValueError):
        ed.evaluate_frame("x", near, gt, rule="v3")


def test_v2_three_px_floor_on_small_boxes():
    gt = [bx(B, 10, 10, 20, 20)]                                # 10 % = 2 px, so the 3 px floor applies
    assert ed.bottom_tol_px(gt[0]) == 3 and ed.bottom_tol_px(bx(O, 0, 0, 60, 150)) == 15
    assert ed.evaluate_frame("x", [bx(B, 10, 10, 20, 23)], gt, rule="v2").tp[B] == 1      # 3 px low (IoU 20/23)
    r = ed.evaluate_frame("x", [bx(B, 10, 10, 20, 24)], gt, rule="v2")                      # 4 px low (IoU 20/24 ≥ 0.5)
    assert r.tp[B] == 0 and r.fp[B] == 1 and r.fn[B] == 1


def test_v2_matching_is_highest_iou_first():
    gts = [bx(O, 100, 200, 60, 60)]
    preds = [bx(O, 102, 200, 60, 60, conf=0.6), bx(O, 110, 200, 60, 60, conf=0.9)]       # IoU 0.94 vs 0.71, both eligible
    v1 = ed.evaluate_frame("x", preds, gts); v2 = ed.evaluate_frame("x", preds, gts, rule="v2")
    assert v1.matches[0].pred_idx == 1                          # v1: the more confident prediction wins
    assert v2.matches[0].pred_idx == 0 and v2.tp[O] == 1 and v2.fp[O] == 1 and v2.unmatched_pred == [1]
    iou = lambda p, g: ed.box_iou(p.bbox, g.bbox)  # noqa: E731
    assert ed.match_best_first(preds, gts, iou, 0.5) == ed.match_best_first(preds, gts, iou, 0.5) == [(0, 0, pytest.approx(58 * 60 / (7200 - 58 * 60)))]
    assert ed.match_best_first(preds, gts, iou, 0.5, eligible=lambda p, g: False) == []


def test_v2_every_gt_counts_no_ignores():
    gts = [bx(O, 100, 200, 60, 60, flags=["occluded", "bottom_estimated"])]
    miss = ed.evaluate_frame("x", [], gts, rule="v2")
    assert miss.fn[O] == 1 and miss.n_ignored[O] == 0 and not miss.negative and miss.count_err == -1
    assert ed.evaluate_frame("x", [], gts).fn[O] == 0            # v1 ignores the occluded barrel
    hit = ed.evaluate_frame("x", [bx(O, 100, 200, 60, 60)], gts, rule="v2")
    assert hit.tp[O] == 1 and hit.n_ignored[O] == 0 and hit.matches[0].bottom_estimated and hit.matches[0].gt_flags == ("bottom_estimated", "occluded")
    trunc = [bx(B, 0, 300, 40, 80, flags=["truncated"])]
    assert ed.evaluate_frame("x", [], trunc, rule="v2").fn[B] == 1 and ed.evaluate_frame("x", [], trunc).fn[B] == 0


def test_v2_clean_negative_disqualifies_unclean_counts():
    false = [bx(B, 10, 300, 20, 20)]
    gts = [bx(O, 100, 200, 60, 60)]
    pos = ed.evaluate_frame("4A8B_window_light_core_01", list(gts), gts, rule="v2")
    clean = ed.evaluate_frame("4A8B_window_light_neg_01", false, [], rule="v2", clean=True)
    dirty = ed.evaluate_frame("DAVE_office_speckle_neg_02", false, [], rule="v2", clean=False)
    assert clean.negative and clean.clean and clean.fp[B] == 1 and dirty.negative and not dirty.clean and dirty.fp[B] == 1
    sc = ed.score([pos, clean], {pos.name: "core", clean.name: "neg"})
    assert sc["rule"] == "v2" and sc["disqualified"] and sc["neg_false_detections"] == 1 and sc["neg_clean_false_detections"] == 1
    sd = ed.score([pos, dirty], {pos.name: "core", dirty.name: "neg"})
    assert not sd["disqualified"] and sd["neg_false_detections"] == 1 and sd["neg_clean_false_detections"] == 0
    assert sd["F1_o"] == 1.0 and sd["P_b"] == 0.0 and sd["F1_b"] == 0.0 and sd["primary"] == 0.5   # the false box still costs
    a = ed.aggregate([pos, clean, dirty])["ALL"]
    assert a.n_negative == 2 and a.n_clean_negative == 1 and a.neg_false_detections == 2 and a.neg_clean_false_detections == 1
    # v1 never looks at clean: any false detection on a negative frame disqualifies
    dirty_v1 = ed.evaluate_frame(dirty.name, false, [], clean=False)
    assert ed.score([dirty_v1], {})["disqualified"] and ed.score([dirty_v1], {})["rule"] == "v1"
    with pytest.raises(ValueError):
        ed.score([pos, dirty_v1], {})                           # mixed rules


def test_count_error_per_frame_and_aggregate():
    gts = [bx(O, 100, 200, 60, 60), bx(B, 300, 200, 60, 60)]
    r = ed.evaluate_frame("x", [bx(O, 100, 200, 60, 60), bx(O, 400, 100, 30, 30), bx(B, 300, 200, 60, 60)], gts, rule="v2")
    r2 = ed.evaluate_frame("y", [], gts, rule="v2")
    assert r.count_err == 1 and r2.count_err == -2
    a = ed.aggregate([r, r2])["ALL"]
    assert a.count_errs == [1, -2]
    sc = ed.score([r, r2], {})
    assert sc["count_err_mean"] == -0.5 and sc["count_err_mean_abs"] == 1.5


def test_v2_bottom_error_split_by_bottom_estimated():
    gts = [bx(O, 100, 200, 60, 60), bx(B, 300, 200, 60, 60, flags=["bottom_estimated", "occluded"])]
    preds = [bx(O, 100, 200, 60, 62), bx(B, 300, 200, 60, 56)]      # +2 px (seen), −4 px (estimated)
    r = ed.evaluate_frame("4A8B_window_light_occl_01", preds, gts, rule="v2")
    assert r.tp == {O: 1, B: 1}
    a = ed.aggregate([r])["ALL"]
    assert a.bottom_by_case["seen"]["px"] == [2] and a.bottom_by_case["estimated"]["px"] == [-4]
    assert a.bottom_by_case["seen"]["frac"] == [pytest.approx(2 / 60)] and a.bottom_by_case["estimated"]["frac"] == [pytest.approx(-4 / 60)]
    assert sorted(a.bottom_errs) == [-4, 2] and len(a.bottom_fracs) == 2
    sc = ed.score([r], {r.name: "occl"})
    assert sc["bottom_err_seen_median_px"] == 2 and sc["bottom_err_est_median_px"] == 4 and sc["bottom_err_frac_median"] == pytest.approx(3 / 60)


def test_v2_aggregate_keys_and_summary(tmp_path):
    gts = [bx(O, 100, 200, 60, 60)]
    r1 = ed.evaluate_frame("4A8B_window_light_touch_01", list(gts), gts, rule="v2")
    r2 = ed.evaluate_frame("4A8B_window_light_core_02", [], gts, rule="v2")
    r3 = ed.evaluate_frame("4A8B_lamp_wood_touch_01", list(gts), gts, rule="v2")
    assert r1.condition() == "window_light" and r1.scene() == "touch" and r1.aggregate_keys() == ("window_light", "scene:touch", "ALL")
    aggs = ed.aggregate([r1, r2, r3])
    assert list(aggs) == ["ALL", "lamp_wood", "window_light", "scene:core", "scene:touch"]
    assert aggs["scene:touch"].n_frames == 2 and aggs["window_light"].n_frames == 2 and aggs["ALL"].n_frames == 3
    assert aggs["scene:touch"].prf(O) == (1.0, 1.0, 1.0) and aggs["scene:core"].prf(O)[1] == 0.0
    md, csv_s, csv_i = ed.write_results([r1, r2, r3], tmp_path / "v2", title="t")
    text = md.read_text()
    assert "Rule **v2**" in text and "| scene:touch |" in text and "| window_light |" in text and "| ALL |" in text
    head = csv_s.read_text().splitlines()
    assert head[0].startswith("condition,n_frames,n_neg,neg_false_detections,orange_n_gt") and "bottom_est_median_px" in head[0] and head[1].endswith(",v2")
    assert csv_i.read_text().splitlines()[0].endswith("color_confusions,scene,clean,count_err")
    assert "bottom_err_frac,gt_flags" in (tmp_path / "v2" / "per_barrel.csv").read_text().splitlines()[0]


def test_v1_rule_explicit_equals_default_and_keys_unchanged(tmp_path):
    gts = [bx(O, 100, 200, 60, 60, flags=["occluded"]), bx(B, 300, 200, 60, 60)]
    preds = [bx(O, 100, 200, 60, 70), bx(B, 300, 200, 60, 60, conf=0.5), bx(B, 302, 200, 60, 60, conf=0.9)]
    d = ed.evaluate_frame("4A8B_window_light_core_01", preds, gts)
    e = ed.evaluate_frame("4A8B_window_light_core_01", preds, gts, rule="v1")
    assert repr(d) == repr(e) and d.rule == "v1" and d.clean and d.count_err == 1    # repr: nan fields compare unequal
    assert d.n_ignored[O] == 1 and d.tp == {O: 0, B: 1} and d.fp == {O: 0, B: 1} and d.matches[1].pred_idx == 2    # confidence order, occluded ignored
    assert d.condition() == "window_light_core" and d.aggregate_keys() == ("window_light_core", "ALL")
    assert list(ed.aggregate([d])) == ["ALL", "window_light_core"]
    md, _, _ = ed.write_results([d], tmp_path / "v1", title="t")
    assert "Rule **v1**" in md.read_text() and ed.score([d], {})["rule"] == "v1"
