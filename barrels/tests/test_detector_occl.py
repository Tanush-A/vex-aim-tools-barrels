"""2026-11-19, the mechanics of the occlusion switches on synthetic barrels (their quality is judged by the occlusion
scorecard, ``experiments/2026-11-19_det_occl``): ``edge_check`` (an edge is seen only against something that is not a
barrel) and ``cap_same`` (a top above a found barrel of its own color). The three switches of that round that stayed off
(``slice_box``, ``cover_unpinned``, ``stripe_two``) were deleted on 2026-11-26, and their tests with them."""
import dataclasses

import numpy as np

from barrels import detector as det, io
from test_detector import CAM, CFG2, paint_barrel

BASE = dataclasses.replace(CFG2, edge_check=False, cap_same=False,   # the detector before this round
                           half_stripe=False, half_thin=False, post_pair=False, stripe_wide=False, cap_low=False,   # ... and without the switches of 2026-11-20 (tests/test_detector_vertical.py)
                           pin_thin=False,   # ... and without pin_thin, on by default since 2026-11-20 (tests/test_detector_pin.py)
                           verify_front=False, verify_readings=False)   # ... and without the verify step of 2026-11-24 (tests/test_detector_verify.py)
EDGE = dataclasses.replace(BASE, edge_check=True)
CAP = dataclasses.replace(BASE, cap_same=True)


def _close(box, truth, px=3):
    return all(abs(a - b) <= px for a, b in zip(box, truth))


def _d_with_top(row):
    """The distance of a barrel whose top row is nearest ``row``."""
    return min(range(45, 400), key=lambda d: abs(CAM.barrel_rows(d).top - row))


def _one_barrel():
    mask = np.zeros((480, 640), np.uint8)
    return mask, paint_barrel(mask, 150, 320, body=io.BLUE)


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
