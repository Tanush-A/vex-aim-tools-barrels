import json
import math

import cv2
import numpy as np
import pytest

from barrels import boxfit as bf, hsrel as hr, pipeline as pl
from barrels.io import BLUE, ORANGE


# ---------------------------------------------------------------- conditions

def test_classify_and_condition_key():
    assert hr.condition_key("4A8B_window_light_core_01") == "window_light"
    assert hr.classify("window_light") == hr.ORDINARY and hr.classify("campus_light") == hr.ORDINARY
    assert hr.classify("overhead_darkwood") == hr.ORDINARY          # a new table is ordinary until listed
    assert hr.classify("window_black") == hr.EXTREME
    assert hr.classify("lampwarm6_wood") == hr.EXTREME and hr.classify("lampcool3_wood") == hr.EXTREME
    for k in ("lampwarm1_wood", "lampmid1_wood", "lampcool1_wood"):
        assert hr.classify(k) == hr.EXCLUDED


def test_group_conditions_orders_and_refuses_test_frames():
    stems = ["4A8B_lampwarm1_wood_core_01", "4A8B_window_black_core_01", "4A8B_window_light_core_02", "4A8B_window_light_core_01",
             "4A8B_campus_light_neg_01", "4A8B_lampmid3_wood_core_01"]
    g = hr.group_conditions(stems)
    assert list(g) == ["campus_light", "window_light", "lampmid3_wood", "window_black", "lampwarm1_wood"]
    assert g["window_light"] == {"class": hr.ORDINARY, "stems": ["4A8B_window_light_core_01", "4A8B_window_light_core_02"]}
    assert g["lampwarm1_wood"]["class"] == hr.EXCLUDED
    with pytest.raises(ValueError, match="test frame"):
        hr.group_conditions(stems, test=["4A8B_campus_light_neg_01"])


# ---------------------------------------------------------------- correlation, permutation p, Holm

def test_rankdata_ties_and_spearman():
    assert list(hr.rankdata([10, 30, 20, 30])) == [1, 3.5, 2, 3.5]
    assert hr.spearman([1, 2, 3, 4], [1, 4, 9, 100]) == pytest.approx(1.0)
    assert hr.spearman([1, 2, 3, 4], [9, 7, 5, -3]) == pytest.approx(-1.0)
    assert hr.spearman([1, 2, 3, 4, 5], [2, 1, 4, 3, 5]) == pytest.approx(0.8)     # 1 - 6 * 4 / (5 * 24)
    assert math.isnan(hr.spearman([1, 2], [1, 2])) and math.isnan(hr.spearman([1, 2, 3], [5, 5, 5]))


def test_perm_pvalue_exact_small_n():
    for n in (3, 4, 5):
        r = hr.perm_pvalue(np.arange(n), np.arange(n) ** 3)
        assert r["exact"] and r["perms"] == math.factorial(n) and r["n"] == n
        assert r["rho"] == pytest.approx(1.0) and r["p"] == pytest.approx(2 / math.factorial(n))      # the identity and the reversal
    r = hr.perm_pvalue([1, 2, 3, 4, 5], [2, 1, 4, 3, 5])
    a = hr.perm_pvalue([1, 2, 3, 4, 5], [-2, -1, -4, -3, -5])
    assert r["p"] == pytest.approx(a["p"]) and a["rho"] == pytest.approx(-0.8)      # two-sided
    assert 2 / 120 < r["p"] < 0.2
    assert math.isnan(hr.perm_pvalue([1, 2], [3, 4])["p"])


def test_perm_pvalue_monte_carlo_large_n():
    x = np.arange(12.0)
    r = hr.perm_pvalue(x, x * 2 + 1, n_perm=2000, seed=0)
    assert not r["exact"] and r["perms"] == 2000 and r["p"] == pytest.approx(1 / 2001)
    assert hr.perm_pvalue(x, x * 2 + 1, n_perm=2000, seed=0) == r                   # the seed fixes it
    rng = np.random.default_rng(1)
    ps = [hr.perm_pvalue(rng.normal(size=12), rng.normal(size=12), n_perm=500, seed=3)["p"] for _ in range(40)]
    assert 0.3 < np.mean(ps) < 0.7                                                  # unrelated data: p spread over 0..1


def test_holm():
    assert list(hr.holm([0.01, 0.04, 0.03])) == pytest.approx([0.03, 0.06, 0.06])
    out = hr.holm([0.5, float("nan"), 0.001])
    assert out[0] == pytest.approx(0.5) and math.isnan(out[1]) and out[2] == pytest.approx(0.002)
    assert list(hr.holm([0.9, 0.8])) == pytest.approx([1.0, 1.0])


# ---------------------------------------------------------------- prediction, leave one condition out

def test_fit_predict_line_and_fallback_to_mean():
    x = np.array([[0.0], [1.0], [2.0]])
    y = np.array([1.0, 3.0, 5.0])
    assert hr.fit_predict(x, y, np.array([[10.0]]))[0] == pytest.approx(21.0)
    assert hr.fit_predict(x[:1], y[:1], np.array([[10.0]]))[0] == pytest.approx(1.0)              # one point: the mean
    assert hr.fit_predict(np.ones((3, 1)), y, np.array([[10.0]]))[0] == pytest.approx(3.0)        # constant column: the mean


def test_select_features_picks_the_informative_column():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(8, 3))
    y = 3 * x[:, 1] + 2
    assert hr.select_features(x, y, 1) == (1,)
    assert hr.select_features(x, y, 2) == (1,)                       # a pair must beat the single column: it cannot
    y2 = x[:, 0] - 2 * x[:, 2]
    assert hr.select_features(x, y2, 2) == (0, 2)
    assert hr.select_features(x, y2, 1, usable=[1]) == (1,)          # only the listed columns are candidates
    assert hr.select_features(x[:2], y[:2], 1) is None               # too few rows for a leave-one-out fit
    x[:, 1] = np.nan
    assert hr.select_features(x, y, 1) in ((0,), (2,))               # a column with a missing value is not a candidate


def test_loco_recovers_a_line_and_falls_back_when_n_is_small():
    rng = np.random.default_rng(0)
    x = np.column_stack([np.arange(6.0), rng.normal(size=6)])
    y = 2 * x[:, 0] + 1
    out = hr.loco(x, y, 1)
    assert [o["feats"] for o in out] == [(0,)] * 6 and not any(o["fallback"] for o in out)
    assert [o["pred"] for o in out] == pytest.approx(list(y))
    small = hr.loco(x[:3], y[:3], 1)                                 # 2 training conditions: no nested choice possible
    assert all(o["fallback"] and o["feats"] == () for o in small)
    assert [o["pred"] for o in small] == pytest.approx([4.0, 3.0, 2.0])      # the mean of the other two
    two = hr.loco(x[:2], y[:2], 1)
    assert [o["pred"] for o in two] == pytest.approx([3.0, 1.0])
    x[0, 0] = np.nan                                                 # the held-out row lacks the good feature
    out = hr.loco(x, y, 1)
    assert out[0]["feats"] == (1,)


def test_leave_one_group_out_holds_out_every_row_of_a_place_together():
    # three places; place "a" has three near-copies of one point that sits OFF the line of the others
    x = np.array([[0.0], [0.1], [0.2], [5.0], [6.0], [7.0], [8.0]])
    y = np.array([10.0, 10.0, 10.0, 5.0, 6.0, 7.0, 8.0])
    g = ["a", "a", "a", "b", "b", "c", "c"]
    # leave one condition out: each "a" row is predicted with its two copies still in, so the line bends toward them
    loco_err = hr.loo_error(x, y, (0,))
    lopo_err = hr.loo_error(x, y, (0,), groups=g)
    assert lopo_err > loco_err                                       # holding out the whole place is the harder test
    held = hr._held_sets(len(y), g)
    assert held[0].tolist() == [True, True, True, False, False, False, False]
    assert hr.n_groups(7, g) == 3 and hr.n_groups(7, None) == 7


def test_nested_selection_needs_enough_places_not_enough_rows():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(6, 2))
    y = 2 * x[:, 0]
    assert hr.select_features(x, y, 1) == (0,)                       # six rows: a choice is possible
    assert hr.select_features(x, y, 1, groups=["a", "a", "a", "b", "b", "b"]) is None   # two places: it is not
    out = hr.loco(x, y, 1, groups=["a", "a", "a", "b", "b", "b"])
    assert all(o["fallback"] for o in out)                           # one training place: the mean of the other place
    assert out[0]["pred"] == pytest.approx(float(np.mean(y[3:])))
    three = hr.loco(x, y, 1, groups=["a", "a", "b", "b", "c", "c"])  # three places: two left inside, still no choice
    assert all(o["fallback"] for o in three)
    x8 = rng.normal(size=(8, 2))
    y8 = 2 * x8[:, 0]
    ok = hr.loco(x8, y8, 1, groups=["a", "a", "b", "b", "c", "c", "d", "d"])   # four places: three left inside
    assert all(not o["fallback"] and o["feats"] == (0,) for o in ok)
    assert [o["pred"] for o in ok] == pytest.approx(list(y8))


def test_optimistic_with_groups_runs():
    x = np.column_stack([np.arange(6.0), np.zeros(6)])
    y = 3 * x[:, 0]
    preds, feats = hr.loco_optimistic(x, y, 1, groups=["a", "a", "b", "b", "c", "c"])
    assert feats == (0,) and preds == pytest.approx(list(y))


def test_choosing_the_feature_outside_the_loop_is_optimistic():
    """Pure noise: no feature predicts y. Choosing the feature on all conditions first still finds one that
    'works'; the nested choice does not, and is no better than the mean of the others."""
    rng = np.random.default_rng(0)
    opt_err, nested_err, mean_err = [], [], []
    for _ in range(20):
        x, y = rng.normal(size=(8, 30)), rng.normal(size=8)
        opt, feats = hr.loco_optimistic(x, y, 1)
        assert len(feats) == 1
        opt_err.append(np.mean(np.abs(np.array(opt) - y)))
        nested_err.append(np.mean([abs(o["pred"] - t) for o, t in zip(hr.loco(x, y, 1), y)]))
        mean_err.append(np.mean([abs(np.delete(y, i).mean() - y[i]) for i in range(8)]))
    assert np.mean(opt_err) < 0.75 * np.mean(mean_err)
    assert np.mean(nested_err) > np.mean(mean_err)


# ---------------------------------------------------------------- thresholds <-> model, slider labels

def _base() -> pl.Model:
    return pl.Model(cfg=pl.Config(color_model="hs"), boxes={ORANGE: bf.Box((33.0, 140.0), (43.0, 255.0)), BLUE: bf.Box((103.0, 113.0), (119.0, 255.0))})


def test_thresholds_round_trip_and_bad_ranges_keep_the_base_box():
    base = _base()
    th = hr.thresholds_of(base)
    assert th == {"orange_h_lo": 3, "orange_h_hi": 13, "orange_s_lo": 140, "blue_h_lo": 103, "blue_h_hi": 119, "blue_s_lo": 113}
    assert tuple(th) == hr.THRESHOLDS
    m, kept = hr.model_from_thresholds(base, th)
    assert kept == [] and m.boxes == base.boxes
    m, kept = hr.model_from_thresholds(base, th | {"orange_h_lo": -3, "blue_s_lo": 300})
    assert kept == [] and m.boxes[ORANGE].lo == (27.0, 140.0) and m.boxes[BLUE].lo == (103.0, 255.0)      # -3 = 177; S clipped
    m, kept = hr.model_from_thresholds(base, th | {"orange_h_lo": 20, "blue_h_hi": float("nan")})
    assert kept == ["orange", "blue"] and m.boxes == base.boxes
    assert base.boxes[ORANGE].lo == (33.0, 140.0)                    # the base model is never changed


def test_load_hs_label(tmp_path):
    p = tmp_path / "x_hs.json"
    d = {"version": 1, "stem": "x", "orange": {"h_lo": -3, "h_hi": 12, "s_lo": 120}, "blue": {"h_lo": 98, "h_hi": 118, "s_lo": 90},
         "hue_units": "opencv 0-179; h_lo may be negative across the red wrap (-3 = 177)", "v_min": 40, "horizon_row": 50}
    p.write_text(json.dumps(d))
    assert hr.load_hs_label(p) == {"orange_h_lo": -3, "orange_h_hi": 12, "orange_s_lo": 120, "blue_h_lo": 98, "blue_h_hi": 118, "blue_s_lo": 90}
    p.write_text(json.dumps(d | {"version": 2}))
    with pytest.raises(ValueError, match="version"):
        hr.load_hs_label(p)


# ---------------------------------------------------------------- features

def _scene(d_hue: int = 0, s_scale: float = 1.0) -> np.ndarray:
    """Gray table, one blue and one orange patch, a green one; a saturated red block above the horizon."""
    hsv = np.zeros((120, 160, 3), np.uint8)
    hsv[..., 1], hsv[..., 2] = 10, 180
    for (y0, y1, x0, x1), (h, s) in {(60, 90, 10, 50): (110, 200), (60, 90, 60, 100): (8, 220), (95, 115, 10, 150): (60, 120)}.items():
        hsv[y0:y1, x0:x1, 0] = (h + d_hue) % 180
        hsv[y0:y1, x0:x1, 1] = int(s * s_scale)
    hsv[0:40, :, 0], hsv[0:40, :, 1] = 0, 255
    hsv[100:115, 150:160, 2] = 20                                    # too dark: gated out
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def test_gated_hist_counts_only_pixels_below_the_horizon_and_bright_enough():
    hist, v_mean = hr.gated_hist(_scene(), horizon_row=50, v_min=40)
    assert hist.shape == (180, 128) and hist.sum() == 70 * 160 - 15 * 10
    assert v_mean == pytest.approx(180, abs=2)
    assert hist[(0 + 30) % 180, 120:].sum() == 0                     # the red block above the horizon is not counted


def test_frame_features_read_the_scene():
    hist, v = hr.gated_hist(_scene())
    ref = hr.Reference.from_hists([hist])
    f = hr.frame_features(hist, v, ref)
    assert tuple(f) == hr.FEATURES
    assert f["blue_peak_h"] == pytest.approx(110, abs=1) and f["orange_peak_h"] == pytest.approx(8, abs=1)
    assert f["blue_s_p90"] == pytest.approx(200, abs=3) and f["orange_s_p90"] == pytest.approx(220, abs=3)
    assert f["s_median"] < 20 and 0.3 < f["s_share100"] < 0.6
    assert f["ref_hue_shift"] == 0 and f["ref_s_scale"] == pytest.approx(1.0)
    hist2, v2 = hr.gated_hist(_scene(d_hue=6, s_scale=0.6))
    g = hr.frame_features(hist2, v2, ref)
    assert g["ref_hue_shift"] == pytest.approx(6, abs=1) and g["ref_s_scale"] == pytest.approx(0.6, abs=0.05)
    assert g["blue_peak_h"] == pytest.approx(116, abs=1)


def test_window_features_are_missing_without_enough_pixels():
    hsv = np.zeros((120, 160, 3), np.uint8)
    hsv[..., 1], hsv[..., 2] = 10, 180
    hsv[60:70, 10:20] = (110, 200, 180)                              # 100 blue pixels: under MIN_WINDOW_PX
    hist, v = hr.gated_hist(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    ref = hr.Reference.from_hists([hr.gated_hist(_scene())[0]])
    f = hr.frame_features(hist, v, ref)
    assert math.isnan(f["blue_peak_h"]) and math.isnan(f["orange_s_p90"]) and math.isnan(f["ref_hue_shift"])
    assert f["v_mean"] == pytest.approx(180, abs=2)
