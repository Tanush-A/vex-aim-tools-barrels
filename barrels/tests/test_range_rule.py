"""The range experiment's rule R2 and its range bookkeeping (``experiments/2026-11-24_adaptive_range/run.py``): the
pure parts, on made-up conditions (no image is opened)."""
import importlib.util
import sys
from pathlib import Path

import pytest

from barrels import hsrel as hr

EXP = Path(__file__).resolve().parents[1] / "experiments"


@pytest.fixture(scope="module")
def rr():
    spec = importlib.util.spec_from_file_location("range_exp_under_test", EXP / "2026-11-24_adaptive_range" / "run.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["range_exp_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


FIXED = {"orange_h_lo": 3, "orange_h_hi": 13, "orange_s_lo": 140, "blue_h_lo": 103, "blue_h_hi": 119, "blue_s_lo": 113}
F_HOME = {f: 0.0 for f in hr.FEATURES}


def make(conds):
    """conds: {key: (place, {threshold: (lo, hi)}, {feature: value})} -> (cond, CR) as run.py builds them."""
    cond, cr = {}, {}
    for k, (place, ranges, feats) in conds.items():
        cond[k] = {"place": place, "feat": {f: feats.get(f, 0.0) for f in hr.FEATURES}, "class": hr.ORDINARY}
        cr[k] = {t: (*ranges.get(t, (FIXED[t] - 5, FIXED[t] + 5)), False) for t in hr.THRESHOLDS}
    return cond, {"det": cr}


def test_r2_keeps_a_threshold_fixed_when_the_fixed_value_is_in_every_range(rr):
    cond, CR = make({"a": ("p1", {}, {}), "b": ("p2", {}, {})})
    terms, info = rr.fit_r2(["a", "b"], cond, CR, FIXED, F_HOME)
    assert terms == [] and all(i["why"].startswith("fixed inside") for i in info.values())


def test_r2_adapts_on_the_primary_feature_only_when_that_beats_fixed(rr):
    # blue S floor: place p1 (feature +10) needs 150-170, place p2 (feature -10) needs 60-90: a line through home fits both
    cond, CR = make({"a": ("p1", {"blue_s_lo": (150, 170)}, {"blue_s_p90": 10.0}),
                     "b": ("p2", {"blue_s_lo": (60, 90)}, {"blue_s_p90": -10.0})})
    terms, info = rr.fit_r2(["a", "b"], cond, CR, FIXED, F_HOME)
    assert [t.threshold for t in terms] == ["blue_s_lo"] and terms[0].feature == "blue_s_p90"
    t = terms[0]
    assert 150 <= FIXED["blue_s_lo"] + t.delta(10.0) <= 170 and 60 <= FIXED["blue_s_lo"] + t.delta(-10.0) <= 90
    assert info["blue_s_lo"]["hits"] == 2 and info["blue_s_lo"]["hits_fixed"] == 0
    # both places need the SAME shift but the feature points opposite ways: no line through home does better than fixed
    cond, CR = make({"a": ("p1", {"blue_s_lo": (150, 170)}, {"blue_s_p90": 10.0}),
                     "b": ("p2", {"blue_s_lo": (150, 170)}, {"blue_s_p90": -10.0})})
    terms, info = rr.fit_r2(["a", "b"], cond, CR, FIXED, F_HOME)
    assert terms and info["blue_s_lo"]["hits"] == 1                      # one of the two is the best a line can do: kept (beats 0)
    cond, CR = make({"a": ("p1", {"blue_s_lo": (150, 170)}, {"blue_s_p90": 0.0})})
    terms, info = rr.fit_r2(["a"], cond, CR, FIXED, F_HOME)
    assert terms == [] and info["blue_s_lo"]["why"].startswith("no line")    # the frame looks like home: nothing to move by


def test_place_rate_weights_places_equally(rr):
    rows = [{"place": "p1", "x": True}, {"place": "p1", "x": False}, {"place": "p1", "x": False}, {"place": "p2", "x": True}]
    rate, all_hit, n = rr.place_rate(rows, "x")
    assert rate == pytest.approx((1 / 3 + 1) / 2) and all_hit == 1 and n == 2
