"""A stripe cut through, and a sliver with stripe and body in view, on synthetic barrels (their quality is judged in
``experiments/2026-11-20_occl_sliver``): two stripe pieces with body over the whole gap are one stripe (the bridge); a
thin full slice cut by the frame is W wide from its other end; a thin full slice whose body shows the whole width gets
that width."""
import numpy as np

from barrels import detector as det, io
from test_detector import CAM, whys
from test_detector_pin import _round_cut, paint_round_barrel

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


# ---------------------------------------------------------------- the bridge

def _cut_near_end():
    """A round barrel whose stripe a patch cuts 3 px from its left end: the end piece is narrower than it is tall."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, D, 320)
    _erase_stripe(mask, truth[0] + 3, truth[0] + 7)
    return mask, truth


def test_bridge_joins_a_piece_that_fails_the_shape_test_when_body_spans_the_gap():
    mask, truth = _cut_near_end()
    on = det.find_stripes(mask, CAM)
    assert len(on) == 1 and on[0].bbox[0] <= truth[0] + 3          # one stripe, the end piece and the gap included
    b = det.detect(mask, cam=CAM)
    assert len(b) == 1 and det.box_iou(b[0].bbox, truth) > 0.9


def test_bridge_needs_body_over_every_column_of_the_gap():
    mask, truth = _cut_near_end()
    mask[:, truth[0] + 3:truth[0] + 7] = 0                          # the gap's columns hold no body at all (wider than close_px fills)
    on = det.find_stripes(mask, CAM)
    assert all(s.bbox[0] > truth[0] + 3 for s in on)


def test_bridge_needs_the_pieces_at_the_same_rows():
    """Two pieces whose box middles are more than half a stripe height apart are not one stripe."""
    mask, truth = _cut_near_end()
    cols = slice(truth[0], truth[0] + 3)
    mask[:, cols] = np.roll(mask[:, cols], -12, axis=0)              # the end piece 12 rows higher (a stripe is ~16 rows here)
    on = det.find_stripes(mask, CAM)
    assert all(s.bbox[0] >= truth[0] + 3 for s in on)


def test_bridge_needs_the_gap_to_be_at_most_half_the_span():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, D, 320)
    W = truth[2] - truth[0]
    _erase_stripe(mask, truth[0] + 3, truth[0] + int(0.75 * W))     # a 3 px end piece, then a gap of most of the barrel
    on = det.find_stripes(mask, CAM)
    assert all(s.bbox[0] > truth[0] + 3 for s in on)


def test_bridge_leaves_whole_barrels_and_two_barrels_alone():
    mask = np.zeros((480, 640), np.uint8)
    a = paint_round_barrel(mask, D, 250)
    b = paint_round_barrel(mask, D, 250 + (a[2] - a[0]) + 12)
    assert len(det.find_stripes(mask, CAM)) == 2                    # two barrels 12 px apart: two stripes, not one bridged
    out = det.detect(mask, cam=CAM)
    assert len(out) == 2 and det.box_iou(out[0].bbox, a) > 0.9 and det.box_iou(out[1].bbox, b) > 0.9


# ---------------------------------------------------------------- a thin slice cut by the frame

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
        on = det.detect(mask, cam=CAM)
        assert len(on) == 1 and det.box_iou(on[0].bbox, truth) > 0.8, (left, on, truth)


def test_thin_slice_at_the_frame_that_is_not_full_gives_no_box():
    """The frame edge says where a barrel would be, not that there is one: the same slice with its lower body ending
    0.3 of the height early is not a slice seen from top to bottom, and gets no box."""
    for left in (True, False):
        mask, truth = _at_frame(0.2, left)
        mask[truth[3] - int(0.3 * (truth[3] - truth[1])):] = 0
        log = []
        assert det.detect(mask, cam=CAM, log=log) == [] and "slice_not_full" in whys(log, "barrel")


def test_thin_frame_changes_nothing_away_from_the_frame():
    """A slice of the same share in the middle of the frame touches no frame edge: the frame rule is not asked, and the box
    (placed by the barrel's own corner) is nowhere near the frame."""
    mask, truth = _round_cut(0.78, 1.0)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and det.box_iou(out[0].bbox, truth) > 0.7 and out[0].bbox[0] > 0 and out[0].bbox[2] < 640


# ---------------------------------------------------------------- a thin slice whose body shows the whole width

def test_thin_span_takes_the_whole_width_the_body_shows():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, D, 320)
    _erase_stripe(mask, truth[0], truth[2] - 14)                    # only the last 14 columns of the stripe show (under a stripe height); the body shows whole
    assert det.find_stripes(mask, CAM)[0].small
    on = det.detect(mask, cam=CAM)
    assert len(on) == 1 and det.box_iou(on[0].bbox, truth) > 0.9


def test_thin_span_refuses_a_span_whose_body_crosses_the_stripe_rows():
    """A body-colored block joined to the slice: its columns hold body color where the stripe must be."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, D, 320)
    _erase_stripe(mask, truth[0], truth[2] - 14)
    y0, y1 = _stripe_rows()
    mask[y0 + 3:y1 - 3, truth[0] + 2:truth[0] + 30] = io.BLUE       # body color across the stripe rows on the left
    s = [s for s in det.find_stripes(mask, CAM) if s.small][0]
    assert det._body_crosses(mask, s, truth[0], truth[2])
