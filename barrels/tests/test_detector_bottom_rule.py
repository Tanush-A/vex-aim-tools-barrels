"""The experiment 2026-11-26_bottom, on synthetic barrels (its quality is judged by ``experiments/2026-11-26_bottom``):
which row is drawn for a seen bottom that agrees with the predicted one (``DetConfig.bottom_rule``, ``drawn_bottom``), and
which rows under a barrel count as seen (``DetConfig.bottom_rows``, ``rows_with_body``). Both are off by default, and
then every box is today's box (proved on 5435 masks by ``experiments/2026-11-26_collapse``; here on small cases)."""
from dataclasses import replace

import numpy as np
import pytest

from barrels import detector as det, eval_det as ed, io, report as rp
from barrels.detect_types import Barrel
from test_detector import CAM, _cap, paint_barrel
from test_detector_occl import _one_barrel

LOW, BOTH, PRED = (replace(det.DetConfig(), bottom_rule=r) for r in ("low", "both", "predicted"))
ROWS = replace(det.DetConfig(), bottom_rows=0.5)
D = 150                                                      # mm: a barrel about 74 px tall with this camera


def _barrel(extra_rows=0, cut_rows=0, tail=None):
    """An orange barrel 150 mm away. ``extra_rows``: that many rows of its color painted under it, as wide as the barrel
    (a shadow, a reflection). ``cut_rows``: that many rows of its lower body not painted. ``tail`` = (rows, columns): a
    narrow streak of its color under its middle. Returns (mask, the true box, the barrel's height)."""
    mask = np.zeros((480, 640), np.uint8)
    x0, top, x1, bottom = truth = paint_barrel(mask, D, 320)
    mask[bottom:bottom + extra_rows, x0:x1] = io.ORANGE
    if cut_rows:
        mask[bottom - cut_rows:bottom, x0:x1] = 0
    if tail:
        mask[bottom:bottom + tail[0], 320 - tail[1] // 2:320 + (tail[1] + 1) // 2] = io.ORANGE
    return mask, truth, bottom - top


def _one(mask, cfg):
    out = det.detect(mask, cfg, CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and out[0].source == "det2"
    return out[0]


def test_the_experiment_is_off_by_default_and_refuses_a_setting_it_does_not_know():
    cfg = det.DetConfig()
    assert cfg.bottom_rule == "" and cfg.bottom_rows == 0.0 and det.BOTTOM_RULES == ("", "low", "both", "predicted", "low_uncut")
    for bad in ({"bottom_rule": "lower"}, {"bottom_rule": "on"}, {"bottom_rows": 1.5}, {"bottom_rows": -0.1}):
        with pytest.raises(ValueError):
            replace(cfg, **bad)
    assert rp.parse_det_overrides(["bottom_rule=low,bottom_rows=0.5"]) == {"bottom_rule": "low", "bottom_rows": 0.5}


def test_the_rules_use_the_scorers_tolerance():
    """The detector does not import the scorer; its copy of the scorer's two numbers must stay equal to them."""
    assert (det.SCORER_BOTTOM_TOL, det.SCORER_BOTTOM_MIN_PX) == (ed.BOTTOM_TOL_FRAC, ed.BOTTOM_TOL_MIN_PX)


def test_drawn_bottom_rule_by_rule():
    """H = 50: the scorer's tolerance is 5 px. The predicted bottom is row 200."""
    for seen, today, low, both in ((204, 204, 204, 204), (205, 205, 205, 205),       # within the tolerance: the seen row, in every rule
                                   (206, 206, 200, 200),                             # 6 px below: "low" and "both" draw the predicted row
                                   (194, 194, 194, 200),                             # 6 px above: only "both" does
                                   (196, 196, 196, 196)):
        assert [det.drawn_bottom(seen, 200.0, 50.0, c) for c in (det.DetConfig(), LOW, BOTH, PRED)] == [today, low, both, 200]
    assert det.drawn_bottom(203, 200.0, 20.0, LOW) == 203 and det.drawn_bottom(204, 200.0, 20.0, LOW) == 200     # a small barrel: at least 3 px
    assert det.drawn_bottom(210, 200.4, 50.0, PRED) == 200


def test_low_uncut_is_low_except_for_a_stripe_the_frame_side_cuts():
    """Round 2. A barrel standing free: "low_uncut" does what "low" does. The same barrel with its left half outside the
    frame, shadow and all: the stripe touches the frame edge, its row is not trusted, and the seen bottom is drawn, as
    today; "low" draws the predicted row there."""
    uncut = replace(det.DetConfig(), bottom_rule="low_uncut")
    assert det.drawn_bottom(206, 200.0, 50.0, uncut) == 200 and det.drawn_bottom(206, 200.0, 50.0, uncut, reading_cut=True) == 206
    assert det.drawn_bottom(206, 200.0, 50.0, LOW, reading_cut=True) == 200
    mask, truth, _ = _barrel(extra_rows=9)
    assert _one(mask, uncut) == _one(mask, LOW)
    cut = np.zeros_like(mask)
    shift = (truth[0] + truth[2]) // 2
    cut[:, :640 - shift] = mask[:, shift:]                                           # the barrel's right half at the left frame edge
    today, low, unc = (det.detect(cut, c, CAM) for c in (det.DetConfig(), LOW, uncut))
    assert len(today) == 1 and today[0].bbox[0] == 0 and today[0].bbox[3] == truth[3] + 9
    assert unc == today and abs(low[0].bbox[3] - truth[3]) <= 1


def test_rows_with_body_counts_a_row_by_its_share_of_the_columns():
    sel = np.zeros((4, 10), bool)
    sel[0, :] = True; sel[1, :5] = True; sel[2, :4] = True
    assert det.rows_with_body(sel, 0.0).tolist() == [True, True, True, False]        # today: one pixel is enough
    assert det.rows_with_body(sel, 0.5).tolist() == [True, True, False, False]
    assert det.rows_with_body(sel[:, :0], 0.5).tolist() == [False] * 4               # no columns: no row


def test_a_shadow_under_a_barrel_is_followed_today_and_not_with_the_rules():
    """Nine rows of the body's color under a barrel 74 px tall: 12 % of its height. Today that is "a seen bottom that
    agrees" (15 %), and the box ends nine rows low: outside the scorer's 10 %. With each rule the predicted row is drawn.
    The bottom still counts as seen: no rule sets the flag bottom_inferred."""
    mask, truth, H = _barrel(extra_rows=9)
    assert 0.10 * H + 1 < 9 < 0.15 * H - 1
    today = _one(mask, det.DetConfig())
    assert today.bbox[3] == truth[3] + 9 and not ed.bottom_within_tol(today, Barrel(io.ORANGE, truth))
    for cfg in (LOW, BOTH, PRED):
        b = _one(mask, cfg)
        assert abs(b.bbox[3] - truth[3]) <= 1 and b.bbox[:3] == today.bbox[:3] and b.flags == today.flags and "bottom_inferred" not in b.flags


def test_a_lower_body_that_is_not_painted_moves_only_the_rules_that_look_up():
    """The lowest nine rows of the body are not painted: the seen bottom is 12 % above the predicted one. "low" keeps it,
    as today (above stays as it is); "both" and "predicted" draw the predicted row."""
    mask, truth, H = _barrel(cut_rows=9)
    today = _one(mask, det.DetConfig())
    assert today.bbox[3] == truth[3] - 9 and _one(mask, LOW) == today
    for cfg in (BOTH, PRED):
        assert abs(_one(mask, cfg).bbox[3] - truth[3]) <= 1


def test_a_clean_barrel_keeps_its_seen_bottom_except_under_predicted():
    mask, truth, _ = _barrel()
    for cfg in (det.DetConfig(), LOW, BOTH, ROWS, replace(ROWS, bottom_rule="low")):
        assert _one(mask, cfg).bbox == truth
    assert abs(_one(mask, PRED).bbox[3] - truth[3]) <= 1


def test_a_narrow_tail_is_not_the_bottom_with_bottom_rows_and_a_wide_shadow_still_is():
    """A streak 4 px wide and nine rows long under the barrel's middle. Today one pixel per row is enough, and the box
    follows it. With bottom_rows = 0.5 a row needs the body's color in half of the columns: the seen bottom is the
    barrel's own. Paint as wide as the barrel passes that test: bottom_rows alone does not remove it."""
    mask, truth, _ = _barrel(tail=(9, 4))
    assert _one(mask, det.DetConfig()).bbox[3] == truth[3] + 9
    assert _one(mask, ROWS).bbox == truth
    wide, truth, _ = _barrel(extra_rows=9)
    assert _one(wide, ROWS).bbox[3] == truth[3] + 9
    assert abs(_one(wide, replace(ROWS, bottom_rule="low")).bbox[3] - truth[3]) <= 1


def test_body_extent_walks_up_as_before_whatever_the_share():
    mask, truth, _ = _barrel(tail=(9, 4))
    r = CAM.barrel_rows(D)
    s0, s1 = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    top, bottom = det._body_extent(mask, io.ORANGE, truth[0], truth[2], s0, s1)
    assert (top, bottom) == (truth[1], truth[3] + 9)
    assert det._body_extent(mask, io.ORANGE, truth[0], truth[2], s0, s1, below_share=0.5) == (truth[1], truth[3])


def test_a_piece_of_stage_1_follows_the_same_rules():
    """Stage 1 predicts the bottom from the top row. The same shadow: today the piece's box follows it; with "low" the
    predicted row is drawn, and the flag bottom_inferred is not set (the bottom was seen)."""
    mask, truth, _ = _barrel(extra_rows=9)
    today = det.find_pieces(mask, CAM)[0].barrel
    assert today.bbox[3] == truth[3] + 9
    low = det.find_pieces(mask, CAM, LOW)[0].barrel
    assert abs(low.bbox[3] - truth[3]) <= 2 and "bottom_inferred" not in low.flags
    tail, truth, _ = _barrel(tail=(9, 4))
    assert det.find_pieces(tail, CAM)[0].barrel.bbox[3] == truth[3] + 9 and det.find_pieces(tail, CAM, ROWS)[0].barrel.bbox[3] == truth[3]


def test_a_cap_follows_the_same_rules():
    """A narrow cap with its lower body showing beside the front barrel. Ending 5 px above the estimate: today and "low"
    draw the seen end, "predicted" the estimate. Running 6 px below it (12 % of the height): today follows it, "low" does not."""
    def caps(mask, front, cfg):
        return [f.barrel for f in det.caps_behind([det.Found(front, "given")], [], mask, CAM, cfg)]
    mask, r, x0, n = _cap()
    top, bottom = int(round(r.top)), int(round(r.bottom))
    front = Barrel(color=io.ORANGE, bbox=(x0 + n - 5, top + 2, x0 + n + 60, bottom + 20))
    mask[int(round(r.stripe_bottom)):bottom - 5, x0:x0 + 8] = io.BLUE
    assert [caps(mask, front, c)[0].bbox[3] for c in (det.DetConfig(), LOW)] == [bottom - 5, bottom - 5]
    assert abs(caps(mask, front, PRED)[0].bbox[3] - bottom) <= 1
    mask[int(round(r.stripe_bottom)):bottom + 6, x0:x0 + 8] = io.BLUE
    assert caps(mask, front, det.DetConfig())[0].bbox[3] == bottom + 6
    assert abs(caps(mask, front, LOW)[0].bbox[3] - bottom) <= 1


def test_a_half_stripe_hidden_from_above_follows_the_same_rules():
    """The stripe and the lower body show, with nine rows of shadow under them. Today the box's bottom is the seen one;
    with "low" it is the bottom the seam predicts. The box is drawn either way: the far edge still counts as seen."""
    mask, truth = _one_barrel()
    r = CAM.barrel_rows(150)
    mask[:int(round(r.stripe_top)) + 2] = 0
    mask[truth[3]:truth[3] + 9, truth[0]:truth[2]] = io.BLUE
    today = det.detect(mask, det.DetConfig(), CAM)
    assert len(today) == 1 and "top_inferred" in today[0].flags and today[0].bbox[3] == truth[3] + 9
    low = det.detect(mask, LOW, CAM)
    assert len(low) == 1 and low[0].flags == today[0].flags and abs(low[0].bbox[3] - truth[3]) <= 2
