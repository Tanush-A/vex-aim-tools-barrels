"""2026-11-20, the mechanics of the switches of ``experiments/2026-11-20_occl_vertical`` on synthetic barrels (their
quality is judged by the occlusion scorecard): ``half_stripe`` / ``half_thin`` (a stripe with body color on one side
only, seen in its whole width: a barrel hidden from above or from below), ``post_pair`` (two slices of one barrel left
and right of a post), ``stripe_wide`` (``stripe_two`` with a guard), ``slice_behind`` (a narrow full slice beside a found
nearer barrel) and ``cap_low`` (the cap rule's height floor)."""
import dataclasses

import numpy as np

from barrels import detector as det, io
from barrels.detect_types import Barrel
from test_detector import CAM, CFG2, paint_barrel
from test_detector_occl import _close, _front_of_other_color, _one_barrel

NEW = ("half_stripe", "half_thin", "post_pair", "stripe_wide", "slice_behind", "cap_low")
BASE = dataclasses.replace(CFG2, slice_box=False, cover_unpinned=False, stripe_two=False, **{k: False for k in NEW})   # the detector before this round
HALF = dataclasses.replace(BASE, half_stripe=True)
THIN = dataclasses.replace(BASE, half_stripe=True, half_thin=True)
POST = dataclasses.replace(BASE, post_pair=True)
WIDE = dataclasses.replace(BASE, stripe_wide=True)
BEHIND = dataclasses.replace(BASE, slice_behind=True)
CAPLOW = dataclasses.replace(BASE, cap_low=True)
ALL = dataclasses.replace(BASE, **{k: True for k in NEW})
R = CAM.barrel_rows(150)                                    # the barrel of _one_barrel: blue, 150 mm away, centred on column 320
S_TOP, S_BOTTOM = int(round(R.stripe_top)), int(round(R.stripe_bottom))


def _whys(log, stage):
    return [e["why"] for e in log if e["stage"] == stage]


# ---------------------------------------------------------------- half_stripe, half_thin

def test_stripe_and_lower_body_is_a_barrel_hidden_from_above():
    """Everything above the stripe is hidden, and the stripe's top two rows. No band has body color above AND below:
    before, no box. Now: the stripe shows the whole width, the body under it ends where the seam predicts the base, so it
    is a barrel; the top is drawn where the seam's distance puts it."""
    mask, truth = _one_barrel()
    mask[:S_TOP + 2] = 0
    assert det.detect(mask, BASE, CAM) == []
    out = det.detect(mask, HALF, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and {"occluded", "top_inferred"} <= out[0].flags
    assert out[0].bbox[3] == truth[3] and out[0].bbox[0] == truth[0] and out[0].bbox[2] == truth[2]
    assert abs(out[0].bbox[1] - truth[1]) <= 2


def test_upper_body_and_stripe_is_a_barrel_hidden_from_below():
    """Everything below the stripe is hidden, and the stripe's bottom two rows (a book lying in front). The upper body's
    top is where the seam predicts it: a barrel; the bottom is drawn where the seam's distance puts it."""
    mask, truth = _one_barrel()
    mask[S_BOTTOM - 2:] = 0
    assert det.detect(mask, BASE, CAM) == []
    out = det.detect(mask, HALF, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and {"occluded", "bottom_inferred"} <= out[0].flags
    assert out[0].bbox[:3] == truth[:3] and abs(out[0].bbox[3] - truth[3]) <= 2


def test_a_thin_line_of_stripe_counts_only_with_half_thin():
    """Three rows of stripe under the upper body: under 0.45 of a stripe height. ``half_stripe`` alone refuses it;
    with ``half_thin`` the other tests decide, and they all hold."""
    mask, truth = _one_barrel()
    mask[S_TOP + 3:] = 0
    log = []
    assert det.detect(mask, HALF, CAM, log=log) == [] and "height" in _whys(log, "half")
    out = det.detect(mask, THIN, CAM)
    assert len(out) == 1 and out[0].bbox[:3] == truth[:3] and abs(out[0].bbox[3] - truth[3]) <= 2


def test_a_top_alone_or_a_base_alone_gets_no_box():
    """No stripe color at all: an upper body alone, a lower body alone. Not a barrel by any switch."""
    for cut in (lambda m: m.__setitem__(slice(S_TOP, None), 0), lambda m: m.__setitem__(slice(None, S_BOTTOM), 0)):
        mask, truth = _one_barrel()
        cut(mask)
        assert det.detect(mask, ALL, CAM) == []


def test_half_stripe_needs_the_body_to_end_where_the_seam_predicts():
    """Hidden from above, and the lower body ends 14 px early (the tolerance is 15 % of the height): the second reading
    does not agree with the seam, so no box."""
    mask, truth = _one_barrel()
    mask[:S_TOP + 2] = 0
    mask[truth[3] - 14:] = 0
    log = []
    assert det.detect(mask, THIN, CAM, log=log) == [] and "far_edge" in _whys(log, "half")


def test_half_stripe_needs_the_whole_width():
    """Hidden from above and the right half hidden too: nothing says where the rest is. No box."""
    mask, truth = _one_barrel()
    mask[:S_TOP + 2] = 0
    mask[:, (truth[0] + truth[2]) // 2:] = 0
    log = []
    assert det.detect(mask, THIN, CAM, log=log) == [] and "width" in _whys(log, "half")


def test_half_stripe_needs_a_clear_open_side():
    """Hidden from below, but 3 rows under what shows of the stripe something barrel-colored begins: the band is not a
    stripe cut by a thing that is not a barrel. No box."""
    mask, truth = _one_barrel()
    mask[S_BOTTOM - 2:] = 0
    assert len(det.detect(mask, THIN, CAM)) == 1
    mask[S_BOTTOM + 1:S_BOTTOM + 12, truth[0]:truth[2]] = io.ORANGE
    log = []
    assert [o for o in det.detect(mask, THIN, CAM, log=log) if o.color == io.BLUE] == []
    assert "open_side" in _whys(log, "half")


def test_an_ordinary_barrel_is_not_also_a_smaller_barrel_of_the_other_color():
    """A barrel whose top 30 % is hidden: its short upper body over its stripe has the proportions of "a stripe over a
    lower body" of a smaller ORANGE barrel hidden from above. That reading's bottom edge ends against the real barrel's
    lower body, which is barrel-colored: not a seen edge. One box, as before."""
    mask, truth = _one_barrel()
    mask[:truth[1] + int(0.3 * (truth[3] - truth[1]))] = 0
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1 and old[0].color == io.BLUE
    log = []
    assert det.detect(mask, THIN, CAM, log=log) == old
    assert "far_edge_against_barrel" in _whys(log, "half")


def test_half_stripe_changes_nothing_for_barrels_standing_free():
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 150, 200); paint_barrel(mask, 300, 400, body=io.BLUE); paint_barrel(mask, 100, 560)
    assert det.detect(mask, THIN, CAM) == det.detect(mask, BASE, CAM)


def test_half_stripe_replaces_a_box_made_from_a_corner_of_the_same_band():
    """A box the stripe step made from a narrow, partly seen piece of the band (given here by hand) is replaced: the band
    shows the whole width. The same box, when it did NOT come from a piece of this band, is a found barrel and stays."""
    mask, truth = _one_barrel()
    mask[S_BOTTOM - 2:] = 0
    piece = det.Stripe(io.BLUE, (truth[0], S_TOP, truth[0] + 14, S_BOTTOM - 2), 14 * 15, 0, (S_TOP + S_BOTTOM) / 2)
    corner = Barrel(color=io.BLUE, bbox=(truth[0] - 20, truth[1], truth[2] - 20, truth[3] - 6), flags=frozenset({"occluded"}), source="det2")
    new, replaced = det.half_stripes(mask, [corner], [(piece, corner)], CAM, HALF)
    assert len(new) == 1 and replaced == [corner] and det.box_iou(new[0].bbox, truth) > 0.9
    new, replaced = det.half_stripes(mask, [corner], [], CAM, HALF)
    assert new == [] and replaced == []


# ---------------------------------------------------------------- post_pair

def _behind_a_post(hidden=0.6):
    mask, truth = _one_barrel()
    W = truth[2] - truth[0]
    mask[:, truth[0] + int(round((1 - hidden) / 2 * W)):truth[0] + int(round((1 + hidden) / 2 * W))] = 0
    return mask, truth


def test_two_slices_left_and_right_of_a_post_are_one_barrel():
    """A post hides the middle 0.6: two pieces 0.2 of the width, each narrower than a stripe is tall, so the finder
    refuses both. They share rows, each is seen from top to bottom, and their outer edges are one barrel apart."""
    mask, truth = _behind_a_post()
    assert det.detect(mask, BASE, CAM) == []
    log = []
    out = det.detect(mask, POST, CAM, log=log)
    assert len(out) == 1 and out[0].color == io.BLUE and "occluded" in out[0].flags and _close(out[0].bbox, truth, 1)
    assert "kept" in _whys(log, "pair")


def test_a_pair_needs_both_slices_seen_from_top_to_bottom():
    """The right slice's lower body ends a quarter of the height early: not a full slice, so no pair."""
    mask, truth = _behind_a_post()
    mask[truth[3] - (truth[3] - truth[1]) // 4:, (truth[0] + truth[2]) // 2:] = 0
    assert det.detect(mask, POST, CAM) == []


def test_slices_of_two_different_barrels_are_not_a_pair():
    """The left edge of one barrel and the right edge of another, two and a half widths apart; and two slices one barrel
    apart whose stripes are at different rows (different distances). Neither is one barrel."""
    mask = np.zeros((480, 640), np.uint8)
    a = paint_barrel(mask, 150, 250, body=io.BLUE)
    b = paint_barrel(mask, 150, 250 + int(1.5 * (a[2] - a[0])), body=io.BLUE)
    W = a[2] - a[0]
    mask[:, a[0] + int(0.2 * W):b[2] - int(0.2 * W)] = 0
    assert det.detect(mask, POST, CAM) == []
    mask[:] = 0
    a = paint_barrel(mask, 150, 300, body=io.BLUE)
    mask[:, a[0] + int(0.2 * W):] = 0
    far = np.zeros_like(mask)
    b = paint_barrel(far, 200, a[0] + W - (CAM.barrel_rows(200).width_px / 2), body=io.BLUE)
    far[:, :b[2] - int(0.2 * W)] = 0
    mask[far > 0] = far[far > 0]
    assert det.detect(mask, POST, CAM) == []


def test_post_pair_changes_nothing_for_barrels_standing_free():
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 150, 200); paint_barrel(mask, 300, 400, body=io.BLUE); paint_barrel(mask, 100, 560)
    assert det.detect(mask, POST, CAM) == det.detect(mask, BASE, CAM)


# ---------------------------------------------------------------- stripe_wide

def _two_overlapping():
    mask = np.zeros((480, 640), np.uint8)
    a = paint_barrel(mask, 150, 300)
    b = paint_barrel(mask, 150, 300 + int(round(0.3 * (a[2] - a[0]))))
    return mask, a, b


def test_stripe_wide_cuts_a_joined_stripe_with_body_right_above_and_below():
    """Two orange barrels 0.3 of a width apart: one stripe region 1.3 barrels wide, body right above and below it. Two
    boxes, each a barrel wide from its own outer edge (what ``stripe_two`` does)."""
    mask, a, b = _two_overlapping()
    assert len(det.detect(mask, BASE, CAM)) == 1
    out = det.detect(mask, WIDE, CAM)
    assert len(out) == 2 and all(o.color == io.ORANGE and "occluded" in o.flags for o in out)
    assert _close(out[0].bbox, a) and _close(out[1].bbox, b)
    assert out == det.detect(mask, dataclasses.replace(BASE, stripe_two=True), CAM)


def test_stripe_wide_leaves_a_wide_stripe_alone_when_no_body_is_seen_right_beside_it():
    """The same region, but with 5 empty rows between the stripe and the body on both sides (the unlabeled seam of a
    large near barrel): nothing but the row says how big the barrel is, so the stripe is not cut. ``stripe_two`` cuts it."""
    mask, a, b = _two_overlapping()
    r = CAM.barrel_rows(150)
    mask[int(round(r.stripe_top)) - 5:int(round(r.stripe_top))] = 0
    mask[int(round(r.stripe_bottom)):int(round(r.stripe_bottom)) + 5] = 0
    old = det.detect(mask, BASE, CAM)
    assert det.detect(mask, WIDE, CAM) == old
    assert det.detect(mask, dataclasses.replace(BASE, stripe_two=True), CAM) != old


def test_stripe_wide_leaves_one_barrel_and_a_touching_pair_alone():
    one = np.zeros((480, 640), np.uint8); paint_barrel(one, 150, 320)
    assert det.detect(one, WIDE, CAM) == det.detect(one, BASE, CAM)
    pair = np.zeros((480, 640), np.uint8)
    a = paint_barrel(pair, 150, 300); paint_barrel(pair, 150, 300 + (a[2] - a[0]))
    assert len(det.detect(pair, WIDE, CAM)) == 2 and det.detect(pair, WIDE, CAM) == det.detect(pair, BASE, CAM)


# ---------------------------------------------------------------- slice_behind

def _slice_beside_a_nearer_barrel(front_color=io.ORANGE):
    """A blue barrel 22 cm away of which only the right 0.15 shows, from top to bottom: an orange barrel 15 cm away hides
    its left 0.85 from the stripe down, and something that is not a barrel hides the top that would show above it (with
    that top showing, the cap rule finds the barrel already)."""
    mask = np.zeros((480, 640), np.uint8)
    back = paint_barrel(mask, 220, 320, body=io.BLUE)
    Wf = CAM.barrel_rows(150).width_px
    edge = int(round(back[0] + 0.85 * (back[2] - back[0])))
    mask[:, :edge] = 0
    front = paint_barrel(mask, 150, edge - Wf / 2, body=front_color)
    return mask, back, front


def test_narrow_slice_beside_a_found_nearer_barrel_is_a_barrel():
    """What shows of the back barrel's stripe is 0.15 of its width: narrower than a stripe is tall, refused by the finder.
    It is seen from top to bottom, and its left side is next to a found barrel standing nearer: a barrel wide from its
    right edge."""
    mask, back, front = _slice_beside_a_nearer_barrel()
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1 and old[0].color == io.ORANGE
    out = det.detect(mask, BEHIND, CAM)
    assert len(out) == 2
    blue = next(o for o in out if o.color == io.BLUE)
    assert "occluded" in blue.flags and _close(blue.bbox, back, 2)


def test_narrow_slice_with_no_found_barrel_beside_it_gets_no_box():
    """The same slice, but what hides the rest is not a barrel (nothing in the mask): no reason for a side, no box."""
    mask, back, front = _slice_beside_a_nearer_barrel()
    mask[front[1]:front[3], front[0]:front[2]] = 0
    log = []
    assert [o for o in det.detect(mask, BEHIND, CAM, log=log) if o.color == io.BLUE] == []
    assert "no_reason" in _whys(log, "slice")


def test_slice_behind_needs_the_full_slice():
    """The slice's lower body ends a third of the height early: a reason says where a barrel would be, not that there is one."""
    mask, back, front = _slice_beside_a_nearer_barrel()
    mask[back[3] - (back[3] - back[1]) // 3:back[3], front[2]:] = 0
    assert det.detect(mask, BEHIND, CAM) == det.detect(mask, BASE, CAM)


def test_slice_at_the_frame_edge_is_placed_by_its_seen_edge():
    """0.15 of the width shows at the left frame edge, seen from top to bottom: W from the seen right edge, cut at the frame."""
    full, truth = _one_barrel()
    shift = truth[0] + int(round(0.85 * (truth[2] - truth[0])))
    mask = np.zeros_like(full)
    mask[:, :640 - shift] = full[:, shift:]
    assert det.detect(mask, BASE, CAM) == []
    out = det.detect(mask, BEHIND, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and {"occluded", "truncated"} <= out[0].flags
    assert out[0].bbox[0] == 0 and abs(out[0].bbox[2] - (truth[2] - shift)) <= 2


# ---------------------------------------------------------------- cap_low

def test_cap_between_four_and_five_tenths_of_an_upper_body_counts_with_cap_low():
    """An orange barrel behind a blue one that hides so much that the top showing is between 0.4 and 0.5 of an upper body
    tall: under the old floor, over the new one. Hidden further (under 0.4), no switch boxes it."""
    upper = CAM.barrel_rows(220).stripe_top - CAM.barrel_rows(220).top
    found = None
    for hidden in np.arange(0.70, 0.95, 0.01):
        mask, back, front = _front_of_other_color(float(hidden))
        if 0.4 * upper <= front[1] - back[1] < 0.5 * upper:
            found = (mask, back, front)
            break
    assert found is not None
    mask, back, front = found
    assert [o for o in det.detect(mask, BASE, CAM) if o.color == io.ORANGE] == []
    caps = [o for o in det.detect(mask, CAPLOW, CAM) if o.color == io.ORANGE]
    assert len(caps) == 1 and caps[0].source == "det3" and caps[0].bbox[1] == back[1] and det.box_iou(caps[0].bbox, back) > 0.5
    mask, back, front = _front_of_other_color(0.93)
    assert front[1] - back[1] < 0.4 * upper
    assert [o for o in det.detect(mask, CAPLOW, CAM) if o.color == io.ORANGE] == []


# ---------------------------------------------------------------- round 2

def test_the_stripe_is_the_thinner_band():
    """Hidden from below with the stripe whole, and the top hidden too so that the upper body is short: the upper body
    over the stripe also reads as "a stripe over a lower body" of an ORANGE barrel hidden from above. The upper body is
    taller than the stripe, so it is not the stripe: no orange box, whatever the cut. (With the upper body cut down to
    the stripe's own height the picture is two equal bands and cannot be read: that case is not claimed.)"""
    why = []
    for rows in range(23, 32):
        mask, truth = _one_barrel()
        mask[S_BOTTOM:] = 0
        mask[:S_TOP - rows] = 0
        log = []
        assert [o for o in det.detect(mask, THIN, CAM, log=log) if o.color == io.ORANGE] == []
        why += _whys(log, "half")
    assert "thicker_than_body" in why


def test_a_slice_that_ends_against_the_other_barrel_color_is_not_a_full_slice():
    """The narrow slice beside a found nearer barrel, but its bottom lies on something orange: not a seen edge."""
    mask, back, front = _slice_beside_a_nearer_barrel()
    assert len(det.detect(mask, BEHIND, CAM)) == 2
    mask[back[3]:back[3] + 6, front[2]:back[2]] = io.ORANGE
    assert [o for o in det.detect(mask, BEHIND, CAM) if o.color == io.BLUE] == []


def test_a_piece_of_a_found_barrels_own_stripe_is_not_a_slice_behind_it():
    """A narrow piece at the frame edge is a barrel (see above); the same piece, when a found barrel of its color has its
    stripe at those rows and the piece inside its box, is a fragment of that barrel's stripe."""
    full, truth = _one_barrel()
    shift = truth[0] + int(round(0.85 * (truth[2] - truth[0])))
    mask = np.zeros_like(full)
    mask[:, :640 - shift] = full[:, shift:]
    narrow = []
    det.find_stripes(mask, CAM, BEHIND, narrow=narrow)
    assert len(narrow) == 1 and narrow[0].narrow
    assert len(det.slices_behind(narrow, mask, [], CAM, BEHIND)) == 1
    owner = Barrel(color=io.BLUE, bbox=(0, 300, 14, 360), source="det2")
    log = []
    assert det.slices_behind(narrow, mask, [owner], CAM, BEHIND, log, made=((narrow[0], owner),)) == []
    assert "stripe_piece" in _whys(log, "slice")
    assert det.post_pairs(narrow, mask, [owner], CAM, POST, made=((narrow[0], owner),)) == ([], [])


def test_every_new_switch_is_off_by_default_or_named_in_the_tests():
    """A new DetConfig field must be pinned in BASE above, or these tests no longer compare with the detector before."""
    assert all(hasattr(det.DetConfig(), k) for k in NEW)
    assert det.detect(_one_barrel()[0], ALL, CAM) == det.detect(_one_barrel()[0], BASE, CAM)
