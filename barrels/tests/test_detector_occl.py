"""2026-11-19, the mechanics of the occlusion switches on synthetic barrels (their quality is judged by the occlusion
scorecard, ``experiments/2026-11-19_det_occl``): ``slice_box`` and ``cover_unpinned`` (a narrow slice of a barrel is a
barrel; where nothing pins the box it covers every place the barrel can be), ``stripe_two`` (a stripe wider than a
barrel is two barrels), ``edge_check`` (an edge is seen only against something that is not a barrel) and ``cap_same``
(a top above a found barrel of its own color)."""
import dataclasses

import numpy as np

from barrels import detector as det, io
from test_detector import CAM, CFG2, paint_barrel
from test_detector_side import _cut_straight

BASE = dataclasses.replace(CFG2, slice_box=False, cover_unpinned=False, stripe_two=False, edge_check=False, cap_same=False)   # the detector before this round
SLICE = dataclasses.replace(BASE, slice_box=True)
COVER = dataclasses.replace(BASE, slice_box=True, cover_unpinned=True)
TWO = dataclasses.replace(BASE, stripe_two=True)
EDGE = dataclasses.replace(BASE, edge_check=True)
CAP = dataclasses.replace(BASE, cap_same=True)


def _holds(box, truth, px=2):
    """The box holds the whole true box (to ``px``)."""
    return box[0] <= truth[0] + px and box[2] >= truth[2] - px and box[1] <= truth[1] + px and box[3] >= truth[3] - px


def _close(box, truth, px=3):
    return all(abs(a - b) <= px for a, b in zip(box, truth))


def _d_with_top(row):
    """The distance of a barrel whose top row is nearest ``row``."""
    return min(range(45, 400), key=lambda d: abs(CAM.barrel_rows(d).top - row))


def _one_barrel():
    mask = np.zeros((480, 640), np.uint8)
    return mask, paint_barrel(mask, 150, 320, body=io.BLUE)


# ---------------------------------------------------------------- slice_box, cover_unpinned

def test_three_quarters_hidden_by_a_straight_edge_gets_the_cover_box():
    """A quarter of the width shows; body and stripe end together on both sides, so no side has a reason. Before: no box.
    Now the slice is seen from top to bottom, so it is a barrel, and the box runs from (seen right end - W) to (seen left
    end + W): it holds the barrel wherever it is, and overlaps the true box by 1 / (2 - 0.25) = 0.57."""
    mask, truth = _cut_straight(0.25)
    W = truth[2] - truth[0]
    seen_right = truth[0] + int(round(0.25 * W))
    assert det.detect(mask, BASE, CAM) == []
    out = det.detect(mask, SLICE, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and "occluded" in out[0].flags
    assert abs(out[0].bbox[0] - (seen_right - W)) <= 2 and abs(out[0].bbox[2] - (truth[0] + W)) <= 2
    assert _holds(out[0].bbox, truth) and det.box_iou(out[0].bbox, truth) >= 0.5
    mirrored = det.detect(mask[:, ::-1].copy(), SLICE, CAM)
    assert len(mirrored) == 1 and _holds(mirrored[0].bbox, (640 - truth[2], truth[1], 640 - truth[0], truth[3]))


def test_narrow_piece_not_seen_from_top_to_bottom_gives_no_box():
    """The same quarter, but the lower body ends a quarter of the height early (no reason on a side, and no full slice)."""
    mask, truth = _cut_straight(0.25)
    mask[truth[3] - (truth[3] - truth[1]) // 4:] = 0
    log = []
    assert det.detect(mask, SLICE, CAM, log=log) == []
    assert "side_unexplained" in [e["why"] for e in log]


def test_both_sides_cut_gets_the_cover_box_around_what_is_seen():
    mask, truth = _one_barrel()
    W = truth[2] - truth[0]
    mask[:, :truth[0] + int(round(0.375 * W))] = 0
    mask[:, truth[0] + int(round(0.625 * W)):] = 0                      # the middle quarter shows
    assert det.detect(mask, BASE, CAM) == []
    out = det.detect(mask, SLICE, CAM)
    assert len(out) == 1 and _holds(out[0].bbox, truth)
    assert abs((out[0].bbox[0] + out[0].bbox[2]) / 2 - (truth[0] + truth[2]) / 2) <= 2
    assert abs((out[0].bbox[2] - out[0].bbox[0]) - 1.75 * W) <= 3


def test_piece_at_the_frame_edge_is_placed_by_its_seen_edge():
    """0.15 of the width shows at the left frame edge: narrower than a stripe is tall, so the finder refused it. The
    frame edge is a reason: W from the seen right edge, cut at the frame."""
    full, truth = _one_barrel()
    W = truth[2] - truth[0]
    shift = truth[0] + int(round(0.85 * W))
    mask = np.zeros_like(full)
    mask[:, :640 - shift] = full[:, shift:]
    assert det.detect(mask, BASE, CAM) == []
    out = det.detect(mask, SLICE, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and {"occluded", "truncated"} <= out[0].flags
    assert out[0].bbox[0] == 0 and abs(out[0].bbox[2] - (truth[2] - shift)) <= 2


def test_cover_unpinned_widens_a_half_seen_barrel_that_was_centred():
    """Half the width shows behind a straight edge: no reason on either side, stripe 0.5 wide. ``slice_box`` alone
    leaves the box as before (W wide, centred on what is seen: a quarter barrel off). With ``cover_unpinned`` it is
    the cover box, 1.5 W wide, and holds the barrel."""
    mask, truth = _cut_straight(0.5)
    W = truth[2] - truth[0]
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1 and abs(old[0].bbox[0] - (truth[0] - 0.25 * W)) <= 2 and not _holds(old[0].bbox, truth)
    assert det.detect(mask, SLICE, CAM) == old
    out = det.detect(mask, COVER, CAM)
    assert len(out) == 1 and _holds(out[0].bbox, truth) and abs((out[0].bbox[2] - out[0].bbox[0]) - 1.5 * W) <= 3
    assert det.box_iou(out[0].bbox, truth) > det.box_iou(old[0].bbox, truth)


def test_two_pieces_of_one_stripe_left_and_right_of_a_post_are_one_barrel():
    """A post hides the middle 0.6: two pieces 0.2 wide, each a full slice. The first gives the cover box; the second
    shares its rows and lies inside that box, so it is a piece of the same stripe, not another barrel."""
    mask, truth = _one_barrel()
    W = truth[2] - truth[0]
    mask[:, truth[0] + int(round(0.2 * W)):truth[0] + int(round(0.8 * W))] = 0
    assert det.detect(mask, BASE, CAM) == []
    log = []
    out = det.detect(mask, SLICE, CAM, log=log)
    assert len(out) == 1 and _holds(out[0].bbox, truth)
    assert "stripe_piece" in [e["why"] for e in log]


def test_slice_box_changes_nothing_for_barrels_seen_whole():
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 150, 200); paint_barrel(mask, 300, 400, body=io.BLUE); paint_barrel(mask, 100, 560)
    assert det.detect(mask, COVER, CAM) == det.detect(mask, BASE, CAM)


# ---------------------------------------------------------------- stripe_two

def test_joined_stripe_of_two_overlapping_same_colored_barrels_is_two_barrels():
    """Two orange barrels at the same distance, 0.3 of a width apart: body and stripe are one region 1.3 barrels wide.
    Before: one box (a stripe is cut in two only from 1.5 widths). Now two, each a barrel wide from its own outer edge;
    they overlap by more than half and are still not each other's duplicate."""
    mask = np.zeros((480, 640), np.uint8)
    a = paint_barrel(mask, 150, 300)
    b = paint_barrel(mask, 150, 300 + int(round(0.3 * (a[2] - a[0]))))
    assert len(det.detect(mask, BASE, CAM)) == 1
    out = det.detect(mask, TWO, CAM)
    assert len(out) == 2 and all(o.color == io.ORANGE and "occluded" in o.flags for o in out)
    assert _close(out[0].bbox, a) and _close(out[1].bbox, b)
    assert det.box_iou(out[0].bbox, out[1].bbox) > 0.5


def test_stripe_two_leaves_one_barrel_and_a_touching_pair_alone():
    one = np.zeros((480, 640), np.uint8); paint_barrel(one, 150, 320)
    assert det.detect(one, TWO, CAM) == det.detect(one, BASE, CAM)
    pair = np.zeros((480, 640), np.uint8)
    a = paint_barrel(pair, 150, 300); paint_barrel(pair, 150, 300 + (a[2] - a[0]))
    assert len(det.detect(pair, TWO, CAM)) == 2 and det.detect(pair, TWO, CAM) == det.detect(pair, BASE, CAM)


# ---------------------------------------------------------------- edge_check

def _front_of_other_color(hidden):
    """An orange barrel 22 cm away and a blue one straight in front whose top row hides the lower ``hidden`` of it."""
    mask = np.zeros((480, 640), np.uint8)
    back = paint_barrel(mask, 220, 320)
    front = paint_barrel(mask, _d_with_top(back[3] - hidden * (back[3] - back[1])), 320, body=io.BLUE)
    return mask, back, front


def test_piece_of_the_back_barrel_between_two_blues_is_not_a_blue_barrel():
    """What shows of the orange barrel's lower body lies between its own blue stripe and the blue barrel in front: a
    band of orange with blue above and below. Before: a second BLUE box over the orange barrel. Its top is not where
    its row predicts, nor its bottom, and the blue above it ends against orange inside its own box: not a barrel."""
    mask, back, front = _front_of_other_color(0.1)
    old = det.detect(mask, BASE, CAM)
    assert sum(o.color == io.BLUE for o in old) == 2 and sum(o.color == io.ORANGE for o in old) == 1
    log = []
    out = det.detect(mask, EDGE, CAM, log=log)
    assert sorted(o.color for o in out) == [io.ORANGE, io.BLUE]
    assert "top_against_barrel" in [e["why"] for e in log]
    blue = next(o for o in out if o.color == io.BLUE)
    assert det.box_iou(blue.bbox, front) > 0.8


def test_bottom_that_ends_against_another_barrel_is_the_lower_of_seen_and_predicted():
    """The blue barrel hides the lowest tenth of the orange one: inside the tolerance, so the seen end was kept as
    the bottom, short. It ends against blue: the barrel may go on behind it, and the predicted bottom is lower."""
    mask, back, front = _front_of_other_color(0.1)
    old = next(o for o in det.detect(mask, BASE, CAM) if o.color == io.ORANGE)
    assert old.bbox[3] <= front[1] + 1 and "bottom_inferred" not in old.flags
    new = next(o for o in det.detect(mask, EDGE, CAM) if o.color == io.ORANGE)
    assert abs(new.bbox[3] - back[3]) <= 2 and "bottom_inferred" in new.flags and new.bbox[:3] == old.bbox[:3]


def test_edge_check_keeps_a_barrel_whose_top_is_under_an_orange_thing():
    """A hand (orange) over the top of a blue barrel: the top is not seen and ends against orange, but the bottom is
    seen where the stripe's row predicts it. The blue barrel keeps its box, unchanged."""
    mask, truth = _one_barrel()
    H = truth[3] - truth[1]
    mask[truth[1] - 12:truth[1] + int(0.3 * H), truth[0] - 6:truth[2] + 6] = io.ORANGE
    old = [o for o in det.detect(mask, BASE, CAM) if o.color == io.BLUE]
    new = [o for o in det.detect(mask, EDGE, CAM) if o.color == io.BLUE]
    assert new == old and len(new) == 1 and "top_inferred" in new[0].flags and det.box_iou(new[0].bbox, truth) > 0.8


def test_edge_check_changes_nothing_for_barrels_standing_free():
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 150, 200); paint_barrel(mask, 300, 400, body=io.BLUE); paint_barrel(mask, 100, 560)
    assert det.detect(mask, EDGE, CAM) == det.detect(mask, BASE, CAM)


# ---------------------------------------------------------------- cap_same

def test_top_above_a_found_barrel_of_its_own_color_is_a_cap():
    """An orange barrel behind an orange one that hides its lower 0.65: stripe hidden, and its top is one blob with the
    front barrel. Before: skipped as "the found barrel's own body". Now the found barrel's box is taken out first, and
    what is left above it is barrel-wide and as tall as an upper body: a barrel behind."""
    mask = np.zeros((480, 640), np.uint8)
    back = paint_barrel(mask, 220, 320)
    front = paint_barrel(mask, _d_with_top(back[3] - 0.65 * (back[3] - back[1])), 320)
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1 and det.box_iou(old[0].bbox, front) > 0.8
    out = det.detect(mask, CAP, CAM)
    assert len(out) == 2 and all(o.color == io.ORANGE for o in out)
    cap = next(o for o in out if o.source == "det3")
    assert cap.bbox[1] == back[1] and abs(cap.bbox[0] - back[0]) <= 2 and abs(cap.bbox[2] - back[2]) <= 2
    assert det.box_iou(cap.bbox, back) > 0.7 and {"occluded", "bottom_inferred"} <= cap.flags


def test_cap_same_changes_nothing_when_no_barrel_is_hidden():
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 150, 200); paint_barrel(mask, 150, 268); paint_barrel(mask, 300, 400, body=io.BLUE); paint_barrel(mask, 100, 560)
    assert det.detect(mask, CAP, CAM) == det.detect(mask, BASE, CAM)
