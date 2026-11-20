"""2026-11-20 (A8), the mechanics of the four switches of ``experiments/2026-11-20_occl_sliver`` on synthetic barrels (their
quality is judged there): ``stripe_bridge`` (two stripe pieces with body over the whole gap are one stripe), ``thin_frame``
(a thin full slice cut by the frame is W wide from its other end), ``own_close`` (the end where the body closes on the stripe
is the barrel's own side) and ``thin_span`` (a thin full slice whose body shows the whole width gets that width)."""
import dataclasses

import numpy as np

from barrels import detector as det, io
from test_detector import CAM, CFG2
from test_detector_pin import _round_cut, paint_round_barrel

FOUR = dict(stripe_bridge=False, thin_frame=False, own_close=False, thin_span=False)
OFF = dataclasses.replace(CFG2, **FOUR)                       # the defaults before this experiment, spelled out
D = 150


def _stripe_rows(d=D):
    r = CAM.barrel_rows(d)
    return int(round(r.stripe_top)) - 3, int(round(r.stripe_bottom)) + 3


def _erase_stripe(mask, x0, x1, body=io.BLUE, d=D):
    """Unpaint the stripe color (only) in columns x0..x1: a pale patch across the stripe, the body above and below kept."""
    other = io.ORANGE if body == io.BLUE else io.BLUE
    y0, y1 = _stripe_rows(d)
    sl = mask[y0:y1, x0:x1]
    sl[sl == other] = 0


# ---------------------------------------------------------------- stripe_bridge

def _cut_near_end():
    """A round barrel whose stripe a patch cuts 3 px from its left end: the end piece is narrower than it is tall."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, D, 320)
    _erase_stripe(mask, truth[0] + 3, truth[0] + 7)
    return mask, truth


def test_bridge_joins_a_piece_that_fails_the_shape_test_when_body_spans_the_gap():
    mask, truth = _cut_near_end()
    off = det.find_stripes(mask, CAM, OFF)
    on = det.find_stripes(mask, CAM, dataclasses.replace(OFF, stripe_bridge=True))
    assert len(on) == 1 and on[0].bbox[0] <= truth[0] + 3          # one stripe, the end piece and the gap included
    assert all(s.bbox[0] > truth[0] + 3 for s in off)               # before: the end piece stays out
    b = det.detect(mask, dataclasses.replace(OFF, stripe_bridge=True), CAM)
    assert len(b) == 1 and det.box_iou(b[0].bbox, truth) > 0.9


def test_bridge_needs_body_over_every_column_of_the_gap():
    mask, truth = _cut_near_end()
    mask[:, truth[0] + 3:truth[0] + 7] = 0                          # the gap's columns hold no body at all (wider than close_px fills)
    on = det.find_stripes(mask, CAM, dataclasses.replace(OFF, stripe_bridge=True))
    assert all(s.bbox[0] > truth[0] + 3 for s in on)


def test_bridge_needs_the_pieces_at_the_same_rows():
    """Round 2: two pieces whose box middles are more than half a stripe height apart are not one stripe."""
    mask, truth = _cut_near_end()
    cols = slice(truth[0], truth[0] + 3)
    mask[:, cols] = np.roll(mask[:, cols], -12, axis=0)              # the end piece 12 rows higher (a stripe is ~16 rows here)
    on = det.find_stripes(mask, CAM, dataclasses.replace(OFF, stripe_bridge=True))
    assert all(s.bbox[0] >= truth[0] + 3 for s in on)


def test_bridge_needs_the_gap_to_be_at_most_half_the_span():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, D, 320)
    W = truth[2] - truth[0]
    _erase_stripe(mask, truth[0] + 3, truth[0] + int(0.75 * W))     # a 3 px end piece, then a gap of most of the barrel
    on = det.find_stripes(mask, CAM, dataclasses.replace(OFF, stripe_bridge=True))
    assert all(s.bbox[0] > truth[0] + 3 for s in on)


def test_bridge_leaves_whole_barrels_and_two_barrels_alone():
    mask = np.zeros((480, 640), np.uint8)
    a = paint_round_barrel(mask, D, 250)
    b = paint_round_barrel(mask, D, 250 + (a[2] - a[0]) + 12)
    on = dataclasses.replace(OFF, stripe_bridge=True)
    assert det.detect(mask, on, CAM) == det.detect(mask, OFF, CAM)
    assert len(det.detect(mask, on, CAM)) == 2


# ---------------------------------------------------------------- thin_frame

def _at_frame(share=0.2, left=True):
    """A round barrel of which only ``share`` of its width is inside the frame, at the left (or right) frame edge."""
    big = np.zeros((480, 640 + 200), np.uint8)
    cx = 100 + 640 if not left else 100
    t = paint_round_barrel(big, D, cx)
    W = t[2] - t[0]
    shift = (t[2] - int(round(share * W)) - 100) if left else (t[0] + int(round(share * W)) - (640 + 100))
    mask = (big[:, 100 + shift:100 + shift + 640] if left else big[:, 100 + shift:100 + shift + 640]).copy()
    truth = (max(0, t[0] - 100 - shift), t[1], min(640, t[2] - 100 - shift), t[3])
    return mask, truth


def test_thin_frame_places_a_slice_cut_by_the_frame():
    for left in (True, False):
        mask, truth = _at_frame(0.2, left)
        on = det.detect(mask, dataclasses.replace(OFF, thin_frame=True), CAM)
        assert len(on) == 1 and det.box_iou(on[0].bbox, truth) > 0.8, (left, on, truth)


def test_thin_frame_changes_nothing_away_from_the_frame():
    mask, truth = _round_cut(0.78, 1.0)
    assert det.detect(mask, dataclasses.replace(OFF, thin_frame=True), CAM) == det.detect(mask, OFF, CAM)


# ---------------------------------------------------------------- own_close

def test_closure_is_large_at_the_own_end_and_small_at_a_straight_cut():
    mask, truth = _round_cut(0.6, 1.0)                              # hidden from the left by a straight edge
    s = [s for s in det.find_stripes(mask, CAM, OFF)][0]
    cols = np.flatnonzero((mask > 0).any(axis=0))
    sx0, sx1 = int(cols[0]), int(cols[-1]) + 1                       # what is seen of the barrel (stripe and body)
    c = det._end_closure(s, mask, CAM, OFF, sx0, sx1)
    assert c[0] <= det.CLOSE_CUT and c[1] >= OFF.bottom_tol
    assert det._closed_end(s, mask, CAM, OFF, sx0, sx1)[1] == sx1
    other = mask.copy()                                              # a barrel standing right beside the own end: no longer a seen edge
    other[s.bbox[1]:s.bbox[3], sx1:sx1 + 6] = io.ORANGE
    assert det._closed_end(s, other, CAM, OFF, sx0, sx1) is None


def test_closure_says_nothing_when_both_sides_are_cut():
    mask, truth = _round_cut(0.35, 0.65)
    s = det.find_stripes(mask, CAM, OFF)[0]
    assert det._closed_end(s, mask, CAM, OFF, s.bbox[0], s.bbox[2]) is None
    assert det.detect(mask, dataclasses.replace(OFF, own_close=True), CAM) == det.detect(mask, OFF, CAM)


def test_own_close_places_a_slice_that_the_outline_leaves():
    """A straight cut whose own side has its corners rounded more than the outline allows: only the closure places it."""
    for keep in ((0.7, 1.0), (0.0, 0.3)):
        mask, truth = _round_cut(*keep)
        x0, x1 = truth[0] + int(round(keep[0] * (truth[2] - truth[0]))), truth[0] + int(round(keep[1] * (truth[2] - truth[0])))
        own = x1 - 2 if keep[0] > 0 else x0 + 1                      # round the own corner a little more: one column of body less
        r = CAM.barrel_rows(D)
        mask[:int(round(r.stripe_top)) - 1, own] = 0
        mask[int(round(r.stripe_bottom)) + 1:, own] = 0
        on = det.detect(mask, dataclasses.replace(OFF, own_close=True), CAM)
        off = det.detect(mask, OFF, CAM)
        assert len(on) == 1 and det.box_iou(on[0].bbox, truth) > 0.75, (keep, on, off, truth)


# ---------------------------------------------------------------- thin_span

def test_thin_span_takes_the_whole_width_the_body_shows():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, D, 320)
    _erase_stripe(mask, truth[0], truth[2] - 14)                    # only the last 14 columns of the stripe show (under a stripe height); the body shows whole
    assert det.find_stripes(mask, CAM, OFF)[0].small
    on = det.detect(mask, dataclasses.replace(OFF, thin_span=True), CAM)
    assert len(on) == 1 and det.box_iou(on[0].bbox, truth) > 0.9


def test_thin_span_refuses_a_span_whose_body_crosses_the_stripe_rows():
    """A body-colored block joined to the slice: its columns hold body color where the stripe must be."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, D, 320)
    _erase_stripe(mask, truth[0], truth[2] - 14)
    y0, y1 = _stripe_rows()
    mask[y0 + 3:y1 - 3, truth[0] + 2:truth[0] + 30] = io.BLUE       # body color across the stripe rows on the left
    s = [s for s in det.find_stripes(mask, CAM, OFF) if s.small][0]
    assert det._body_crosses(mask, s, truth[0], truth[2])
