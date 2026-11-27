"""2026-11-20, the switches of the two parallel occlusion branches together (``experiments/2026-11-20_occl_combined``):
occl-vertical's six (``test_detector_vertical.py``) and occl-pin's two (``test_detector_pin.py``). Each branch's own
tests pin the other branch's switches off; here both are on. The mechanics only: the quality of the combination is
judged by the experiment's battery."""
import dataclasses

from barrels import detector as det, io
from test_detector import CAM
from test_detector_occl import _one_barrel
from test_detector_pin import PIN, THIN, _round_cut, _thin_share
from test_detector_vertical import ALL, BASE, NEW, S_BOTTOM, S_TOP, _behind_a_post, _slice_beside_a_nearer_barrel

COMB = dataclasses.replace(BASE, pin_outline=True, **{k: True for k in NEW})           # the six + pin_outline
COMB_THIN = dataclasses.replace(COMB, pin_thin=True)
POST = dataclasses.replace(BASE, post_pair=True)
POST_THIN = dataclasses.replace(POST, pin_outline=True, pin_thin=True)


def test_the_test_arms_are_what_they_say():
    assert BASE.pin_outline is False and BASE.pin_thin is False and not any(getattr(BASE, k) for k in NEW)
    assert PIN.pin_outline and not any(getattr(PIN, k) for k in NEW) and THIN.pin_thin and not any(getattr(THIN, k) for k in NEW)
    assert all(getattr(ALL, k) for k in NEW) and ALL.pin_outline is False


def test_the_finder_hands_over_the_same_pieces_with_or_without_the_lower_floor():
    """``narrow`` = the pieces under the finder's old width floor, whether the stripe step also sees them as thin
    stripes (``pin_thin``) or not; a thin stripe left without a box is not handed over a second time. (Round 1 of the
    combined experiment: with the lower floor a narrow slice was no longer "refused for its width" and never reached the
    left-over rules.)"""
    for mask in (_slice_beside_a_nearer_barrel()[0], _behind_a_post()[0]):
        n0, n1 = [], []
        s0 = det.find_stripes(mask, CAM, POST, narrow=n0)
        s1 = det.find_stripes(mask, CAM, POST_THIN, narrow=n1)
        assert n0 and [s.bbox for s in n0] == [s.bbox for s in n1] and all(s.narrow for s in n1)
        assert not any(s.small for s in s0) and sorted(s.bbox for s in s1 if s.small) == sorted(s.bbox for s in n1)
        assert det.find_stripes(mask, CAM, POST_THIN) == s1                   # the stripes returned do not depend on the list
        unplaced = []
        for s in s1:
            if s.small:
                det.barrel_from_stripe(s, mask, CAM, POST_THIN, unplaced=unplaced)
        assert unplaced == []


def test_two_slices_behind_a_post_are_one_barrel_with_pin_thin_too():
    mask, truth = _behind_a_post()
    alone = det.detect(mask, POST, CAM)
    assert len(alone) == 1
    assert det.detect(mask, POST_THIN, CAM) == alone
    assert det.detect(mask, COMB_THIN, CAM) == det.detect(mask, COMB, CAM) == alone


def test_a_thin_slice_the_outline_places_gets_one_box_with_everything_on():
    """The slice at a barrel's own side that ``pin_thin`` boxes: its ``narrow`` twin is a piece of that found barrel's
    stripe, so the left-over rules add nothing."""
    mask, truth = _round_cut(0.0, _thin_share())
    thin = det.detect(mask, THIN, CAM)
    assert len(thin) == 1
    assert det.detect(mask, COMB_THIN, CAM) == thin
    assert det.detect(mask, COMB, CAM) == det.detect(mask, PIN, CAM) == []


def test_each_branchs_own_cases_come_out_the_same_in_the_combination():
    """Hidden from above, from below, a post, a barrel in front (occl-vertical); half hidden by a straight
    edge, with a barrel's rounded outline (occl-pin). The other branch's switches change none of them."""
    above, _ = _one_barrel(); above[:S_TOP + 2] = 0
    below, _ = _one_barrel(); below[S_BOTTOM - 2:] = 0
    for mask in (above, below, _behind_a_post()[0], _slice_beside_a_nearer_barrel()[0], _one_barrel()[0]):
        want = det.detect(mask, ALL, CAM)
        assert len(want) >= 1 and det.detect(mask, COMB, CAM) == want and det.detect(mask, COMB_THIN, CAM) == want
    for keep in ((0.5, 1.0), (0.0, 0.5), (0.0, 1.0)):
        mask, truth = _round_cut(*keep)
        want = det.detect(mask, PIN, CAM)
        assert len(want) == 1 and det.detect(mask, COMB, CAM) == want
        assert det.detect(mask, COMB_THIN, CAM) == det.detect(mask, THIN, CAM)
