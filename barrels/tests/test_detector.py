"""Sanity checks of the v2 detector's mechanics on synthetic barrels (its quality is judged by eval numbers)."""
import numpy as np

from barrels import detector as det, geometry as geo, io

CAM = geo.NOMINAL


def paint_barrel(mask, d_axis_mm, x_center, body=io.ORANGE, cam=CAM, cut_bottom_frac=0.0):
    """A barrel at axis distance d as a solid rectangle (body color, stripe in the other color)."""
    r = cam.barrel_rows(d_axis_mm)
    top, bottom, W = int(round(r.top)), int(round(r.bottom)), r.width_px
    x0, x1 = int(round(x_center - W / 2)), int(round(x_center + W / 2))
    y1 = bottom - int(round(cut_bottom_frac * (bottom - top)))
    mask[top:y1, x0:x1] = body
    other = io.BLUE if body == io.ORANGE else io.ORANGE
    mask[int(round(r.stripe_top)):int(round(r.stripe_bottom)), x0:x1] = other
    return (x0, top, x1, bottom)


def test_single_barrel_seen_bottom_kept():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE
    assert out[0].bbox == truth and "bottom_inferred" not in out[0].flags


def test_shadowed_bottom_is_inferred_from_the_top_row():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE, cut_bottom_frac=0.35)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and "bottom_inferred" in out[0].flags
    assert abs(out[0].bbox[3] - truth[3]) <= 2


def test_two_touching_barrels_are_split_by_expected_width():
    mask = np.zeros((480, 640), np.uint8)
    W = CAM.barrel_rows(150).width_px
    a = paint_barrel(mask, 150, 320 - W / 2 - 1, body=io.ORANGE)
    b = paint_barrel(mask, 150, 320 + W / 2 + 1, body=io.BLUE)
    assert len(det.find_blobs(mask)) == 1                        # they merge into one blob
    out = det.detect(mask, cam=CAM)
    assert [o.color for o in out] == [io.ORANGE, io.BLUE]
    assert abs(out[0].bbox[2] - a[2]) <= 3 and abs(out[1].bbox[0] - b[0]) <= 3


def test_barrel_cut_by_the_frame_bottom_is_truncated_not_extended():
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(35)                                      # close: bottom below the frame
    assert r.bottom > 480
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    mask[int(r.top):480, x0:x1] = io.ORANGE
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].bbox[3] == 480 and "truncated" in out[0].flags


def test_specks_and_slivers_are_dropped_and_empty_mask_gives_nothing():
    mask = np.zeros((480, 640), np.uint8)
    mask[200:203, 100:103] = io.ORANGE                           # speck
    mask[250:300, 400:404] = io.BLUE                             # a 4 px wide sliver
    assert det.detect(mask, cam=CAM) == []
    assert det.detect(np.zeros((480, 640), np.uint8), cam=CAM) == []


def test_draw_only_adds_rectangles():
    img = np.zeros((480, 640, 3), np.uint8)
    out = det.draw(img, det.detect(np.zeros((480, 640), np.uint8), cam=CAM))
    assert (out == img).all()
