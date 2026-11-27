"""The stripeless close-up piece, on synthetic masks (its quality is judged in ``experiments/2026-11-23_closeup_shape``):
a close-up piece that the frame's side also cuts must be seen down to where its top row puts the stripe; a piece whose
predicted stripe runs past the frame bottom is a close-up too."""
import numpy as np

from barrels import detector as det, io
from test_detector import CAM, whys


def _blank():
    return np.zeros((480, 640), np.uint8)


def test_close_barrel_cut_by_the_frame_bottom_and_side_with_no_stripe_keeps_its_box():
    """A barrel near the bumper at the frame's right edge: body from its top row down to the frame bottom, no stripe."""
    r = CAM.barrel_rows(30)
    assert r.stripe_top > 480                                       # its stripe is below the frame
    mask = _blank()
    x0 = int(round(640 - 0.63 * r.width_px))
    mask[int(round(r.top)):480, x0:640] = io.ORANGE
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].bbox == (x0, int(round(r.top)), 640, 480) and out[0].source == "det1"


def test_flat_orange_print_cut_by_the_frame_corner_gets_no_box():
    """The trap of ``occlx_15``: a flat orange shape at the bottom-right corner, its pixels ending far above where its top
    row puts a barrel's stripe. Its top row predicts a base below the frame, so its box is drawn to the frame bottom and
    it counts as a close-up; but the frame's side cuts it too, and it is not seen down to its stripe."""
    r = CAM.barrel_rows(26)
    top = int(round(r.top))
    mask = _blank()
    mask[top:top + 82, 465:640] = io.ORANGE                         # 175 px = 0.45 of a barrel at that row; ends at row ~365
    log: list = []
    assert det.detect(mask, cam=CAM, log=log) == []
    assert whys(log, "piece") == ["closeup_side"]


def test_uncut_close_up_showing_only_its_lid_is_still_a_barrel():
    """Under a warm lamp only the lit lid of a close barrel is barrel-colored. The frame's side does not cut it, so its width
    is the check, and the side rule leaves it alone."""
    r = CAM.barrel_rows(35)
    top = int(round(r.top))
    mask = _blank()
    half = int(round(0.375 * r.width_px))
    mask[top:top + int(0.5 * (r.stripe_top - top)), 320 - half:320 + half] = io.BLUE
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].bbox[3] == 480 and out[0].color == io.BLUE


def test_barrel_whose_stripe_straddles_the_frame_bottom_is_found_with_closeup_stripe():
    """The "specific position": the stripe runs past the frame bottom, so no body is seen below it (not a stripe), and the
    seen bottom agrees with the predicted one (the piece does not reach the frame bottom). It is a close-up all the same."""
    r = CAM.barrel_rows(37)
    assert r.stripe_top < 470 and r.stripe_bottom >= 480
    top = int(round(r.top))
    x0, x1 = int(round(320 - r.width_px / 2)), int(round(320 + r.width_px / 2))
    mask = _blank()
    mask[top:477, x0:x1] = io.ORANGE                                # as on palewood close_01: the stripe rows read as body or
                                                                    # nothing, the last rows are dark
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and out[0].bbox == (x0, top, x1, 477) and out[0].source == "det1"


def test_closeup_stripe_leaves_a_stripeless_piece_whose_stripe_should_be_in_view_refused():
    """A barrel-shaped orange piece with no stripe, whose stripe the geometry puts wholly inside the frame, is still not a
    barrel."""
    r = CAM.barrel_rows(150)
    mask = _blank()
    x0, x1 = int(round(320 - r.width_px / 2)), int(round(320 + r.width_px / 2))
    mask[int(round(r.top)):int(round(r.bottom)), x0:x1] = io.ORANGE
    log: list = []
    assert det.detect(mask, cam=CAM, log=log) == []
    assert whys(log, "piece") == ["stripeless"]


def test_closeup_side_only_asks_pieces_cut_by_the_side_and_the_seen_bottom_is_the_pieces_own():
    """The same flat print away from the frame's side is left to the width test; the side rule only reads the piece's own
    pixels (another piece inside its box does not lengthen it)."""
    r = CAM.barrel_rows(26)
    top = int(round(r.top))
    mask = _blank()
    mask[top:top + 82, 300:480] = io.ORANGE                         # not cut by a side
    assert [b.bbox[3] for b in det.detect(mask, cam=CAM)] == [480]
    mask = _blank()
    mask[top:top + 82, 465:640] = io.ORANGE
    mask[top + 140:480, 555:560] = io.ORANGE                        # a sliver inside its box down to the frame bottom
    assert all(b.bbox[0] != 465 for b in det.detect(mask, cam=CAM))
