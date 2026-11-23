"""hsrange: the range sweep, the joint check, the net-pixel optimum and the small fitting helpers (infrastructure:
the experiment's numbers mean nothing if these are wrong). Synthetic frames and a fake evaluator; no data files."""
import math

import cv2
import numpy as np
import pytest

from barrels import hslabel as hl, hsrange as hx

ADOPTED = {"orange_h_lo": 3, "orange_h_hi": 13, "orange_s_lo": 140, "blue_h_lo": 103, "blue_h_hi": 119, "blue_s_lo": 113}


def outcome(found=(0,), false=0, core=None, out=None):
    return hx.Outcome(frozenset(found), false, core or {"orange": 0.8, "blue": 0.8}, out or {"orange": 1000, "blue": 1000})


class Fake:
    """A stand-in for FrameEval: ``rule(thr) -> Outcome``."""

    def __init__(self, rule):
        self.rule, self.n = rule, 0

    def evaluate(self, thr, detect=True):
        self.n += 1
        if not hx.valid(thr):
            return hx.Outcome(frozenset(), 10 ** 6, {"orange": math.nan, "blue": math.nan}, {"orange": 10 ** 9, "blue": 10 ** 9}, 0, True)
        return self.rule(hx.flat(thr))


def s_rule(t):
    """Orange S floor: barrel lost above 150, outside paint climbs below 100; orange hue high: a false box above 20."""
    s = t["orange_s_lo"]
    found = (0,) if s <= 150 else ()
    out = 1000 + (0 if s >= 100 else 50 * (100 - s))
    return outcome(found, 1 if t["orange_h_hi"] > 20 else 0, out={"orange": out, "blue": 1000})


def test_flat_and_nested_round_trip():
    n = hx.nested(ADOPTED)
    assert n["orange"] == {"h_lo": 3, "h_hi": 13, "s_lo": 140}
    assert hx.flat(n) == ADOPTED and hx.flat(ADOPTED) == ADOPTED
    assert hx.valid(ADOPTED) and not hx.valid({**ADOPTED, "blue_h_lo": 120})


def test_regions_core_is_the_shrunk_box_and_outside_excludes_the_padded_box_and_the_sky():
    core, cores, outside = hx.regions((100, 100), [{"bbox": [20, 40, 40, 80], "color": "orange"}], row0=10)
    ys, xs = np.nonzero(core["orange"])
    assert (xs.min(), xs.max(), ys.min(), ys.max()) == (23, 36, 46, 73)        # 15 % of 20 = 3 px, of 40 = 6 px
    assert not core["blue"].any() and (cores == core["orange"]).all()
    assert not outside[:10].any() and not outside[36:84, 16:44].any() and outside[50, 50] and outside[35, 30]


def test_works_names_the_first_reason():
    ref = outcome((0, 1))
    assert hx.works(outcome((0, 1, 2)), ref) is None                           # finding more is fine
    assert hx.works(outcome((0,)), ref) == hx.LOST
    assert hx.works(outcome((0, 1), false=1), ref) == hx.FALSE
    assert hx.works(outcome((0, 1), out={"orange": 1100, "blue": 1000}), ref) is None     # +100 < max(150, 100)
    assert hx.works(outcome((0, 1), out={"orange": 1151, "blue": 1000}), ref) == hx.OUTSIDE
    assert hx.works(outcome((), core={"orange": 0.76, "blue": 0.8}), ref, hx.PIX) is None  # pixel version ignores the detector
    assert hx.works(outcome((), core={"orange": 0.74, "blue": 0.8}), ref, hx.PIX) == hx.CORE
    assert hx.works(outcome(core={"orange": 0.1, "blue": 0.8}), outcome(core={"orange": math.nan, "blue": 0.8}), hx.PIX) is None


def test_sweep_finds_the_run_around_the_anchor_and_why_each_end_stopped():
    r = hx.sweep(Fake(s_rule), ADOPTED)
    s = r["orange_s_lo"]
    # outside paint: 50 px per S unit below 100, margin 150 px -> 97 still works (+150), 96 fails; steps of 2 from 140 -> 98 is the last even value
    assert (s.lo, s.lo_why) == (98, hx.OUTSIDE)
    assert (s.hi, s.hi_why) == (150, hx.LOST)
    hh = r["orange_h_hi"]
    assert (hh.hi, hh.hi_why) == (20, hx.FALSE)
    assert (hh.lo, hh.lo_why) == (3, hx.OTHER_END)                             # down to the low end of the sector
    lo = r["orange_h_lo"]
    assert (lo.lo, lo.lo_why) == (-30, hx.OPEN) and (lo.hi, lo.hi_why) == (13, hx.OTHER_END)
    assert r["blue_s_lo"].lo == 0 and r["blue_s_lo"].hi == 255 and r["blue_s_lo"].hi_why == hx.OPEN


def test_coarse_sweep_agrees_with_the_fine_one_on_a_monotone_frame_with_fewer_calls():
    fine, coarse = Fake(s_rule), Fake(s_rule)
    a, b = hx.sweep(fine, ADOPTED), hx.sweep(coarse, ADOPTED, coarse=4)
    assert {t: (x.lo, x.hi) for t, x in a.items()} == {t: (x.lo, x.hi) for t, x in b.items()}
    assert coarse.n < fine.n


def test_shrink_and_box_points():
    r = {"orange_s_lo": hx.Range(100, 160, "", "", 140), "blue_s_lo": hx.Range(113, 113, "", "", 113)}
    a = {**ADOPTED}
    assert hx.shrink(a, r, 1.0) == {"orange_s_lo": (100, 160), "blue_s_lo": (113, 113)}
    assert hx.shrink(a, r, 0.5) == {"orange_s_lo": (120, 150), "blue_s_lo": (113, 113)}
    assert hx.shrink(a, r, 0.0)["orange_s_lo"] == (140, 140)
    corners, rand = hx.box_points({"orange_s_lo": (100, 160), "blue_s_lo": (113, 113)}, 10)
    assert len(corners) == 2 and len(rand) == 10 and all(100 <= p["orange_s_lo"] <= 160 for p in rand)


def test_joint_check_holds_when_everything_works_and_shrinks_when_corners_fail():
    always = Fake(lambda t: outcome())
    r = {t: hx.Range(ADOPTED[t] - 2, ADOPTED[t] + 2, "", "", ADOPTED[t]) for t in hx.THRESHOLDS}
    assert hx.joint_check(always, ADOPTED, r, n_random=8).confirmed == 1.0
    # a box whose hue ends can cross (low end above the high end) does not hold: an empty sector cannot be run
    r = hx.sweep(always, ADOPTED)
    j = hx.joint_check(always, ADOPTED, r, n_random=8)
    assert j.corner_share < 1 and j.confirmed < 1

    def corner_rule(t):           # fails only when both S floors are far below the anchor at once
        bad = t["orange_s_lo"] < 60 and t["blue_s_lo"] < 40
        return outcome(() if bad else (0,))
    f = Fake(corner_rule)
    r = {t: hx.Range(ADOPTED[t], ADOPTED[t], "", "", ADOPTED[t]) for t in hx.THRESHOLDS}
    r["orange_s_lo"] = hx.Range(0, 140, "", "", 140)
    r["blue_s_lo"] = hx.Range(0, 113, "", "", 113)
    j = hx.joint_check(f, ADOPTED, r, n_random=16)
    assert j.corner_share < 1 and 0 < j.confirmed < 1


def test_best_run():
    assert hx._best_run(np.array([-1, 2, 3, -10, 4.0])) == (5.0, 1, 2)
    assert hx._best_run(np.array([-1.0, -2.0]))[0] == 0


def synthetic_frame():
    """A gray table (S 0) with an orange-ish patch of low saturation (clutter, S 80) and an orange barrel (S 200)."""
    hsv = np.zeros((120, 160, 3), np.uint8)
    hsv[..., 2] = 200
    hsv[60:100, 20:50] = (10, 200, 200)          # the barrel
    hsv[60:100, 100:150] = (12, 80, 200)         # clutter: orange hue, low S
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR), {"barrels": [{"id": 1, "color": "orange", "bbox": [20, 60, 50, 100], "flags": []}], "clean": True}


def test_net_optimum_puts_the_floor_between_clutter_and_barrel_and_the_sector_on_the_barrel():
    bgr, label = synthetic_frame()
    fe = hx.FrameEval(bgr, label, hl.adopted_model())
    hs = fe.frame.hs(0)
    s_barrel, s_clutter = int(hs[80, 35, 1]), int(hs[80, 120, 1])
    p = hx.net_optimum(fe, ADOPTED)
    assert s_clutter < p["orange_s_lo"] <= s_barrel
    h = int(hs[80, 35, 0])
    assert p["orange_h_lo"] <= h <= p["orange_h_hi"]
    assert {k: p[k] for k in ("blue_h_lo", "blue_h_hi", "blue_s_lo")} == {k: ADOPTED[k] for k in ("blue_h_lo", "blue_h_hi", "blue_s_lo")}
    # with outside paint free the gain is the same at any floor up to the barrel's S: a tie keeps the higher floor
    assert hx.net_optimum(fe, ADOPTED, w_out=0.0)["orange_s_lo"] == s_barrel


def test_frame_eval_measures_core_paint_and_outside_paint():
    bgr, label = synthetic_frame()
    fe = hx.FrameEval(bgr, label, hl.adopted_model())
    hi = fe.evaluate({**ADOPTED, "orange_h_lo": 0, "orange_h_hi": 20, "orange_s_lo": 150}, detect=False)
    lo = fe.evaluate({**ADOPTED, "orange_h_lo": 0, "orange_h_hi": 20, "orange_s_lo": 50}, detect=False)
    assert hi.core["orange"] == pytest.approx(1.0) and hi.out["orange"] == 0
    assert lo.out["orange"] == 40 * 50 and math.isnan(lo.core["blue"])


def test_intersect_interval_slope_and_hits():
    assert hx.intersect([(0, 10), (5, 20)]) == (5.0, 10.0, False)
    assert hx.intersect([(0, 4), (6, 20)])[2] is True
    # fixed 10, home feature 0; two rows at x = 1 and 2 whose ranges hold 12-14 and 14-18: b = 2 hits both
    b, hits = hx.interval_slope([1, 2], [(12, 14), (14, 18)], 10, 0, math.inf)
    assert hits == 2 and 10 + b * 1 >= 12 and 10 + b * 2 >= 14 and 10 + b <= 14
    assert hx.hits_at([1, 2], [(12, 14), (14, 18)], 10, 0, 0.0) == 0
    assert hx.hits_at([1, float("nan")], [(9, 11), (9, 11)], 10, 0, 100.0, max_delta=1) == 2     # nan -> fixed (inside); x=1 -> clipped to 11, inside
    assert hx.hits_at([1], [(9, 10.5)], 10, 0, 100.0, max_delta=1) == 0
    # the fixed value already inside both: b = 0 keeps it (ties go to the smallest |b| with the best midpoint fit)
    b0, h0 = hx.interval_slope([1, -1], [(5, 15), (5, 15)], 10, 0, math.inf)
    assert h0 == 2 and b0 == 0


def test_ranges_dict_is_nested():
    r = {t: hx.Range(1, 2, "", "", 1) for t in hx.THRESHOLDS}
    assert hx.ranges_dict(r)["blue"]["s_lo"] == [1, 2]
