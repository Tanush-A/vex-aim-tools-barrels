"""2026-11-20, the mechanics of the two position switches on synthetic barrels (their quality is judged by the
occlusion scorecard, ``experiments/2026-11-20_occl_pin``): ``pin_outline`` (the barrel's outline, slid over the seen
part, places a partly seen stripe that no side reason places, when it fits in one place only) and ``pin_thin`` (a thin
piece of stripe is a barrel only as a full slice that the outline places)."""
import dataclasses

import numpy as np

from barrels import detector as det, geometry as geo, io
from test_detector import CAM, CFG2, paint_barrel

BASE = dataclasses.replace(CFG2, pin_outline=False, pin_thin=False)          # the detector before these switches, spelled out
PIN = dataclasses.replace(BASE, pin_outline=True)
THIN = dataclasses.replace(BASE, pin_outline=True, pin_thin=True)


def paint_round_barrel(mask, d_axis_mm, x_center, body=io.BLUE, cam=CAM):
    """A barrel with the outline the camera model predicts (``det.Outline``): rounded corners, an arched stripe.
    Returns its full box."""
    ol = det.Outline.at(cam, d_axis_mm)
    r = cam.barrel_rows(d_axis_mm)
    other = io.ORANGE if body == io.BLUE else io.BLUE
    half = (r.stripe_bottom - r.stripe_top) / 2
    x0, x1 = int(round(x_center - ol.W / 2)), int(round(x_center + ol.W / 2))
    for x in range(max(0, x0), min(mask.shape[1], x1)):
        u = (x + 0.5 - x_center) / ol.W
        top, bottom, mid = float(ol.top(u)), float(ol.bottom(u)), float(ol.stripe(u))
        mask[int(round(top)):int(round(bottom)), x] = body
        mask[int(round(mid - half)):int(round(mid + half)), x] = other
    return (x0, int(round(r.top)), x1, int(round(r.bottom)))


def _round_cut(keep_from, keep_to, d=150, cx=320):
    """A round barrel of which only the columns from ``keep_from`` to ``keep_to`` (shares of its width, from its left
    side) show: cut by straight upright edges that are not barrel-colored."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, d, cx)
    W = truth[2] - truth[0]
    mask[:, :truth[0] + int(round(keep_from * W))] = 0
    mask[:, truth[0] + int(round(keep_to * W)):] = 0
    return mask, truth


def _mirror(box):
    return (640 - box[2], box[1], 640 - box[0], box[3])


# ---------------------------------------------------------------- the outline itself

def test_outline_rows_are_the_camera_models():
    """At the centre, at the lid's ends and at the barrel's sides the three lines are the rows the camera model gives."""
    d = 150
    ol, r = det.Outline.at(CAM, d), CAM.barrel_rows(d)
    assert ol.W == r.width_px
    assert float(ol.top(0.0)) == r.top and float(ol.bottom(0.0)) == r.bottom and float(ol.stripe(0.0)) == r.stripe_center
    lid = det.LID_HALF
    assert abs(lid - 9 / 25.5) < 1e-12
    assert abs(float(ol.top(lid)) - CAM.point_row(d, geo.BARREL_HEIGHT_MM)) < 1e-9 and abs(float(ol.bottom(-lid)) - CAM.point_row(d, 0.0)) < 1e-9
    mid = CAM.point_row(d, geo.BARREL_HEIGHT_MM / 2)
    for line in (ol.top, ol.bottom, ol.stripe):
        assert abs(float(line(0.5)) - mid) < 1e-9 and abs(float(line(-0.5)) - mid) < 1e-9          # all three meet at the side, mid-height
        assert np.allclose(line(np.array([-0.4, -0.2, 0.1])), line(np.array([0.4, 0.2, -0.1])))       # left and right alike
    # the top is nearly flat over the lid and runs down at the shoulder; the bottom the other way round
    assert float(ol.top(0.3)) - float(ol.top(0.0)) < 0.05 * ol.W < float(ol.top(0.46)) - float(ol.top(0.0))
    assert float(ol.bottom(0.0)) - float(ol.bottom(0.3)) < 0.05 * ol.W < float(ol.bottom(0.0)) - float(ol.bottom(0.46))


def test_a_whole_round_barrel_is_found_as_before():
    """The switches do nothing to a barrel seen whole."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, 150, 320)
    base = det.detect(mask, BASE, CAM)
    assert len(base) == 1 and det.box_iou(base[0].bbox, truth) > 0.9
    assert det.detect(mask, PIN, CAM) == base and det.detect(mask, THIN, CAM) == base


# ---------------------------------------------------------------- pin_outline

def test_half_hidden_by_a_straight_edge_is_placed_by_the_outline():
    """The left half shows; the stripe and the body end together on both sides, so no side has a reason. Before: a box
    centred on what is seen, a quarter barrel off. Now: the seen part has rounded corners on the left (the barrel's own
    side) and square ones on the right (the cut), the outline fits in one place only, and the box is the barrel's."""
    mask, truth = _round_cut(0.0, 0.5)
    W = truth[2] - truth[0]
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1 and abs((old[0].bbox[0] + old[0].bbox[2]) / 2 - (truth[0] + 0.25 * W)) <= 3     # centred on the seen half
    out = det.detect(mask, PIN, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and "occluded" in out[0].flags
    assert abs(out[0].bbox[0] - truth[0]) <= 0.05 * W and abs(out[0].bbox[2] - truth[2]) <= 0.05 * W
    assert abs((out[0].bbox[2] - out[0].bbox[0]) - W) <= 1                                               # one barrel wide
    assert det.box_iou(out[0].bbox, truth) > 0.85
    mirrored = det.detect(mask[:, ::-1].copy(), PIN, CAM)
    assert len(mirrored) == 1 and det.box_iou(mirrored[0].bbox, _mirror(truth)) > 0.85


def test_a_third_showing_gets_a_box_where_before_there_was_none():
    """0.35 of the width shows: under the 0.4 floor of the centred box, so before: no box. The corner is there: placed."""
    mask, truth = _round_cut(0.65, 1.0)
    assert det.detect(mask, BASE, CAM) == []
    out = det.detect(mask, PIN, CAM)
    assert len(out) == 1 and det.box_iou(out[0].bbox, truth) > 0.85


def test_a_piece_from_the_middle_fits_in_many_places_and_is_left_as_before():
    """Both sides cut, the middle 45 % shows: the top and the bottom are nearly flat there, the outline fits at many
    positions and does not know. The box is what it was (centred on what is seen)."""
    mask, truth = _round_cut(0.275, 0.725)
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1
    assert det.detect(mask, PIN, CAM) == old
    s = det.find_stripes(mask, CAM, PIN)[0]
    assert det._outline_place(s, mask, CAM, PIN, s.bbox[0], s.bbox[2]) is None


def test_a_square_cornered_piece_is_left_as_before():
    """A barrel painted as a plain rectangle, half hidden: both ends of what is seen are square, like two cuts. The
    outline does not know which end is the barrel's own, and nothing changes."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE)
    mask[:, truth[0] + (truth[2] - truth[0]) // 2:] = 0
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1 and det.detect(mask, PIN, CAM) == old


def test_a_reason_for_one_side_still_decides():
    """Cut by the frame edge: the frame is the reason, and the box is a barrel wide from the seen edge, as before; the
    outline is not asked."""
    mask = np.zeros((480, 640), np.uint8)
    W = CAM.barrel_rows(150).width_px
    truth = paint_round_barrel(mask, 150, 0.1 * W)                    # 0.4 of the barrel is left of the frame
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1 and old[0].bbox[0] == 0
    assert det.detect(mask, PIN, CAM) == old


def test_outline_place_needs_a_barrels_outline():
    """A piece whose top is 30 % of the height too low on one half does not have a barrel's outline: the best position's
    cost is over pin_good x H, and there is no box from the outline."""
    mask, truth = _round_cut(0.0, 0.5)
    W, H = truth[2] - truth[0], truth[3] - truth[1]
    mask[truth[1]:truth[1] + int(0.3 * H), truth[0]:truth[0] + int(0.25 * W)] = 0
    s = max(det.find_stripes(mask, CAM, PIN), key=lambda s: s.bbox[2] - s.bbox[0])
    assert det._outline_place(s, mask, CAM, PIN, truth[0], truth[0] + W // 2) is None


def test_a_slanted_cut_is_not_taken_for_the_barrels_own_side():
    """Round 2. A slanted edge hides the right part: its upper end imitates a rounded top corner, but the bottom corner
    there is square (the seen part even runs on). Each end is asked by itself and all three lines must fit: the left end
    is the barrel's own side, the slanted one is not, and the box starts at the barrel's own side."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, 150, 320)
    W, H = truth[2] - truth[0], truth[3] - truth[1]
    rows, cols = np.arange(480)[:, None], np.arange(640)[None, :]
    for lean in (1, -1):
        m = mask.copy()
        m[cols >= truth[0] + 0.5 * W + lean * 0.25 * W * (rows - (truth[1] + truth[3]) / 2) / H] = 0
        out = det.detect(m, PIN, CAM)
        assert len(out) == 1 and abs(out[0].bbox[0] - truth[0]) <= 2 and det.box_iou(out[0].bbox, truth) > 0.8
        s = max(det.find_stripes(m, CAM, PIN), key=lambda s: s.bbox[2] - s.bbox[0])
        only_right = det._outline_place(s, m, CAM, PIN, truth[0] + int(0.3 * W), s.bbox[2])     # without the own side in view: the slant alone
        assert only_right is None


def test_a_placed_box_never_replaces_a_found_barrels_box():
    """Round 2. A piece with a barrel's corner stands right against a whole barrel of its color, so that a barrel W wide
    from the piece's own side would lie over the whole barrel's box. The whole barrel keeps its box, and the piece is
    treated as before the switch."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, 150, 320)
    W = truth[2] - truth[0]
    piece = np.zeros_like(mask)
    paint_round_barrel(piece, 150, 320 - int(0.3 * W))
    piece[:, truth[0]:] = 0                                            # the left 0.3 W of a second barrel, its own side showing
    mask[piece > 0] = piece[piece > 0]
    old = det.detect(mask, BASE, CAM)
    assert any(det.box_iou(b.bbox, truth) > 0.8 for b in old)
    new = det.detect(mask, PIN, CAM)
    assert any(det.box_iou(b.bbox, truth) > 0.8 for b in new) and len(new) >= len(old)


# ---------------------------------------------------------------- pin_thin

def _thin_share(d=150):
    """A share of the width so small that the stripe piece is narrower than a stripe is tall (under the finder's old floor)."""
    r = CAM.barrel_rows(d)
    return 0.8 * (r.stripe_bottom - r.stripe_top) / r.width_px


def test_thin_slice_with_a_corner_is_a_barrel():
    """A slice narrower than a stripe is tall shows at the barrel's left side. Before, and with pin_outline alone: the
    finder refuses the piece. With pin_thin: it is a full slice (top and bottom where its row predicts them) and its
    corners fit the outline in one place: a box one barrel wide on the barrel."""
    v = _thin_share()
    mask, truth = _round_cut(0.0, v)
    W = truth[2] - truth[0]
    assert det.detect(mask, BASE, CAM) == [] and det.detect(mask, PIN, CAM) == []
    stripes = det.find_stripes(mask, CAM, THIN)
    assert len(stripes) == 1 and stripes[0].small
    out = det.detect(mask, THIN, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and "occluded" in out[0].flags
    assert abs(out[0].bbox[0] - truth[0]) <= 1                                        # anchored on the barrel's own side
    assert 0.9 * W <= out[0].bbox[2] - out[0].bbox[0] <= W + 1 and det.box_iou(out[0].bbox, truth) > 0.7   # a side piece's row reads a little far
    mirrored = det.detect(mask[:, ::-1].copy(), THIN, CAM)
    assert len(mirrored) == 1 and det.box_iou(mirrored[0].bbox, _mirror(truth)) > 0.7


def test_thin_slice_that_is_not_full_gives_no_box():
    """The same slice with its lower body ending a quarter of the height early: not a full slice, no box."""
    mask, truth = _round_cut(0.0, _thin_share())
    H = truth[3] - truth[1]
    mask[truth[3] - int(0.3 * H):] = 0
    assert det.detect(mask, THIN, CAM) == []


def test_thin_slice_from_the_middle_gives_no_box():
    """A thin slice from the middle of a barrel is a full slice, but flat: the outline fits in many places. No box (the
    2026-11-19 slice_box drew a box 1.8 barrels wide here)."""
    v = _thin_share()
    mask, truth = _round_cut(0.5 - v / 2, 0.5 + v / 2)
    assert any(s.small for s in det.find_stripes(mask, CAM, THIN))
    assert det.detect(mask, THIN, CAM) == []


def test_thin_slice_at_the_frame_edge():
    """A barrel entering at the frame's left edge, a thin slice of it in the frame. Its own corner is inside the frame:
    the outline places it, and the box is cut by the frame."""
    v = _thin_share()
    W = CAM.barrel_rows(150).width_px
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, 150, (v - 0.5) * W)              # only the right v of the barrel is in the frame
    assert det.detect(mask, BASE, CAM) == []
    out = det.detect(mask, THIN, CAM)
    assert len(out) == 1 and out[0].bbox[0] == 0 and "truncated" in out[0].flags
    assert abs(out[0].bbox[2] - truth[2]) <= 0.1 * W


def test_thin_piece_of_a_found_barrels_stripe_is_not_another_barrel():
    """A highlight takes a part out of a whole barrel's stripe and leaves a thin piece beside the long one. The barrel
    has its box from the long piece; the thin one is a second piece of the same stripe, and the box does not change."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_round_barrel(mask, 150, 320)
    r = CAM.barrel_rows(150); W = truth[2] - truth[0]
    a, b = truth[0] + int(0.14 * W), truth[0] + int(0.32 * W)
    rows = slice(int(r.stripe_top) - 12, int(r.stripe_bottom) + 6)
    mask[rows, a:b][mask[rows, a:b] == io.ORANGE] = 0                 # the stripe's pixels there are gone, the body stays
    old = det.detect(mask, BASE, CAM)
    assert len(old) == 1 and det.box_iou(old[0].bbox, truth) > 0.85
    assert len(det.find_stripes(mask, CAM, THIN)) >= len(det.find_stripes(mask, CAM, BASE))
    assert det.detect(mask, THIN, CAM) == old


def test_end_costs_tell_a_barrels_own_side_from_a_cut():
    """The left half shows: the left end follows the outline (cost near 0), the cut end does not (cost over pin_good)."""
    mask, truth = _round_cut(0.0, 0.5)
    W = truth[2] - truth[0]
    s = det.find_stripes(mask, CAM, PIN)[0]
    left, right = det._end_costs(s, mask, CAM, PIN, truth[0], truth[0] + W // 2)
    assert left < 0.02 < PIN.pin_good < right
    assert det._outline_place(s, mask, CAM, PIN, truth[0], truth[0] + W // 2)[0] == truth[0]


def test_pin_outline_is_on_by_default_and_pin_thin_is_off_and_needs_it():
    """2026-11-20: pin_outline passed the pre-registered rule and is the default; pin_thin did not and stays off."""
    cfg = det.DetConfig()
    assert cfg.pin_outline is True and cfg.pin_thin is False and cfg.pin_good == 0.05
    mask, truth = _round_cut(0.0, _thin_share())
    assert det.detect(mask, dataclasses.replace(BASE, pin_thin=True), CAM) == []      # pin_thin without pin_outline changes nothing
