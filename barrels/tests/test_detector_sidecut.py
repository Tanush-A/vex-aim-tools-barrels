"""The experiment 2026-11-26_sidecut (``DetConfig.side_cut``): a barrel hidden at the side by a thing that is not a
barrel is placed from its own side, the side that bulges. On synthetic barrels; the rule's quality is judged by
``experiments/2026-11-26_sidecut``. At the default ("centred") nothing here runs."""
import dataclasses

import numpy as np
import pytest

from barrels import detector as det, io, report as rp
from test_detector import CAM
from test_detector_pin import paint_round_barrel

OWN = dataclasses.replace(det.DetConfig(), side_cut="own_side")
KEEP = dataclasses.replace(det.DetConfig(), side_cut="own_side+centred")


def cut_round(d=200, keep_from=0.0, keep_to=1.0, lean=0.0, lid=0.0, short=0, cx=320):
    """A round barrel (blue body, orange stripe) of which only the columns from ``keep_from`` to ``keep_to`` (shares of
    its width, from its left side, at mid-height) show. A cut side is a straight edge that leans by ``lean`` x the width
    over the barrel's height. ``lid``: this share of the height is not painted at the top (a real mask often loses the
    lid). ``short``: the stripe ends this many pixels before a cut. Returns (mask, the full box)."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, d, cx)
    x0, y0, x1, y1 = truth
    W, H = x1 - x0, y1 - y0
    if lid:
        mask[:y0 + int(round(lid * H))] = 0
    rows, cols = np.arange(480)[:, None], np.arange(640)[None, :]
    off = lean * W * (rows - (y0 + y1) / 2) / H
    hide = np.zeros(mask.shape, bool)
    stripe = mask == io.ORANGE
    if keep_from > 0:
        a = x0 + keep_from * W + off
        mask[stripe & (cols < a + short)] = 0
        hide |= cols < a
    if keep_to < 1:
        b = x0 + keep_to * W + off
        mask[stripe & (cols >= b - short)] = 0
        hide |= cols >= b
    mask[hide] = 0
    return mask, truth


def rules(mask, cfg):
    log = []
    out = det.detect(mask, cfg, CAM, log=log)
    return out, [e.get("rule", e["why"]) for e in log if e["stage"] == "barrel"]


def off_centre(box, truth):
    """How far the box's centre column is from the true one, in barrel widths."""
    return abs((box[0] + box[2]) - (truth[0] + truth[2])) / 2 / (truth[2] - truth[0])


def seen(mask, truth):
    """(the widest stripe, first seen column, one past the last seen column) of the one barrel in ``mask``."""
    s = max(det.find_stripes(mask, CAM)[0], key=lambda s: s.bbox[2] - s.bbox[0])
    cols = np.flatnonzero((mask[truth[1]:truth[3]] > 0).any(axis=0))
    return s, int(cols[0]), int(cols[-1]) + 1


# ---------------------------------------------------------------- the flag

def test_the_default_is_today_and_the_flag_is_the_only_field_that_is_not_a_number():
    fields = det.DetConfig().to_dict()
    assert fields["side_cut"] == "centred"
    assert sum(isinstance(v, (int, float)) and not isinstance(v, bool) for v in fields.values()) == 20
    assert rp.parse_det_overrides(["side_cut=own_side"]) == {"side_cut": "own_side"}
    with pytest.raises(ValueError):
        dataclasses.replace(det.DetConfig(), side_cut="on")


def test_every_value_draws_todays_box_on_a_barrel_seen_whole():
    mask, truth = cut_round()
    today = det.detect(mask, cam=CAM)
    assert len(today) == 1 and det.box_iou(today[0].bbox, truth) > 0.9
    assert det.detect(mask, OWN, CAM) == today and det.detect(mask, KEEP, CAM) == today


# ---------------------------------------------------------------- the measure

def test_the_outline_is_widest_at_mid_height_and_as_wide_as_the_lid_at_the_lids_end():
    ol = det.Outline.at(CAM, 200)
    span = ol.bot_apex - ol.top_apex
    v = np.array([0.0, (ol.top_end - ol.top_apex) / span, (ol.mid - ol.top_apex) / span, (ol.bot_end - ol.top_apex) / span, 1.0])
    hw = det._outline_half_width(ol, v)
    assert hw[0] < 0.05 and hw[4] < 0.05                           # the top row and the bottom row: the middle of a rim
    assert abs(hw[2] - 0.5) < 0.005                                # mid-height: the bulge
    assert abs(hw[1] - det.LID_HALF) < 0.01 and abs(hw[3] - det.LID_HALF) < 0.01        # the ends of the lid and of the base
    up = det._outline_half_width(ol, np.linspace(0.0, v[2], 30))
    assert np.all(np.diff(up) >= 0)                                # wider and wider from the top down to mid-height


def test_a_barrels_own_sides_bulge():
    mask, truth = cut_round()
    s, sx0, sx1 = seen(mask, truth)
    left, right, own = det.side_bulges(s, mask, CAM, truth[1], truth[3], sx0, sx1)
    assert own > 3                                                  # the outline's own bulge, in pixels, at 20 cm
    assert left >= 0.5 * own and right >= 0.5 * own
    assert det.own_side_by_bulge(s, mask, CAM, truth[1], truth[3], sx0, sx1) == (True, True)


@pytest.mark.parametrize("lean", [0.0, 0.25, -0.25])
def test_a_straight_cut_does_not_bulge_whichever_way_it_leans(lean):
    mask, truth = cut_round(keep_to=0.4, lean=lean)                 # the left 40 % shows: the left side is the barrel's own
    s, sx0, sx1 = seen(mask, truth)
    left, right, own = det.side_bulges(s, mask, CAM, truth[1], truth[3], sx0, sx1)
    assert left >= 0.5 * own and abs(right) < 1.0
    assert det.own_side_by_bulge(s, mask, CAM, truth[1], truth[3], sx0, sx1) == (True, False)
    mirrored = mask[:, ::-1].copy()
    s, sx0, sx1 = seen(mirrored, (640 - truth[2], truth[1], 640 - truth[0], truth[3]))
    assert det.own_side_by_bulge(s, mirrored, CAM, truth[1], truth[3], sx0, sx1) == (False, True)


def test_a_piece_from_the_middle_has_no_own_side():
    mask, truth = cut_round(keep_from=0.3, keep_to=0.7, lean=0.25)
    s, sx0, sx1 = seen(mask, truth)
    assert det.own_side_by_bulge(s, mask, CAM, truth[1], truth[3], sx0, sx1) == (False, False)


def test_too_few_rows_cannot_be_measured():
    mask, truth = cut_round(keep_to=0.4)
    s, sx0, sx1 = seen(mask, truth)
    assert det.side_bulges(s, mask, CAM, truth[1], truth[1] + 6, sx0, sx1) is None
    assert det.own_side_by_bulge(s, mask, CAM, truth[1], truth[1] + 6, sx0, sx1) is None


# ---------------------------------------------------------------- the detector with the flag

@pytest.mark.parametrize("keep_from, keep_to, lean", [(0.0, 0.4, 0.25), (0.0, 0.35, 0.25), (0.6, 1.0, 0.25), (0.6, 1.0, -0.25)])
def test_sixty_percent_hidden_by_a_leaning_edge_is_placed_from_the_own_side(keep_from, keep_to, lean):
    """The lid is not painted, so the outline's rounded corners are not there to read; the stripe is under 0.4 W wide. Today:
    no box. With the rule: the barrel's box, from the side that bulges."""
    mask, truth = cut_round(keep_from=keep_from, keep_to=keep_to, lean=lean, lid=0.1)
    assert det.detect(mask, cam=CAM) == []
    for cfg in (OWN, KEEP):
        out, why = rules(mask, cfg)
        assert len(out) == 1 and why[-1] == "own_side" and out[0].color == io.BLUE and "occluded" in out[0].flags
        assert off_centre(out[0].bbox, truth) <= 0.05 and det.box_iou(out[0].bbox, truth) > 0.8


def test_it_works_when_the_stripe_stops_before_the_cut():
    """The stripe ends 6 px before the cut while the body runs up to it (as in the real frames): the piece of stripe is thin.
    Today: no box. With the rule: placed from the own side."""
    mask, truth = cut_round(keep_from=0.65, lean=0.25, lid=0.1, short=6)
    out, why = rules(mask, det.DetConfig())
    assert out == [] and why[-1] == "outline_unknown"
    out, why = rules(mask, OWN)
    assert len(out) == 1 and why[-1] == "thin_own_side" and off_centre(out[0].bbox, truth) <= 0.05


def test_a_piece_from_the_middle_gets_no_box_where_today_guesses():
    """Both sides cut: no side is the barrel's own. Today's centred guess draws a box (right here only because the two cuts
    are alike); the candidate draws none; the comparison arm keeps today's box."""
    mask, truth = cut_round(keep_from=0.3, keep_to=0.7)
    today, why = rules(mask, det.DetConfig())
    assert len(today) == 1 and why[-1] == "centred"
    assert det.detect(mask, OWN, CAM) == []
    assert det.detect(mask, KEEP, CAM) == today


def test_narrow_paint_on_a_whole_barrel_keeps_todays_centred_box():
    """Both sides bulge: all of the barrel is seen, only its paint is narrow. Centred on what is seen, as today."""
    mask, truth = cut_round(d=150)
    x0, y0, x1, y1 = truth
    W = x1 - x0
    keep = np.zeros(mask.shape, bool)
    cols = np.arange(640)[None, :]
    for r in range(y0, y1):                                         # shave 15 % of the width off each side, row by row
        on = np.flatnonzero(mask[r] > 0)
        if len(on):
            keep[r] = (cols[0] >= on[0] + 0.15 * W) & (cols[0] <= on[-1] - 0.15 * W)
    mask[~keep] = 0
    today, why = rules(mask, det.DetConfig())
    if why[-1] == "centred":                                        # the case this test is about
        out, why_own = rules(mask, OWN)
        assert why_own[-1] == "two_sides" and out == today


def test_with_the_bottom_hidden_the_own_side_is_not_asked():
    """One of the two edges is not seen: a leaning cut and a barrel's side look the same, so the rule says nothing."""
    mask, truth = cut_round(keep_to=0.4, lean=0.25, lid=0.1)
    mask[truth[3] - int(0.35 * (truth[3] - truth[1])):] = 0        # something low hides the bottom third
    out, why = rules(mask, OWN)
    assert "own_side" not in why and "thin_own_side" not in why
