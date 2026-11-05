"""Sanity checks of the v2 detector's mechanics on synthetic barrels (its quality is judged by eval numbers)."""
import dataclasses

import numpy as np

from barrels import detector as det, geometry as geo, io

CAM = geo.NOMINAL
CFG1 = dataclasses.replace(det.DetConfig(), require_stripe=False)    # step 1 alone (the detector before 2026-11-05)
CFG2 = dataclasses.replace(det.DetConfig(), require_stripe=True)     # the stripe step — also the default


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
    for cfg in (CFG1, CFG2):                                      # both steps box a plain barrel exactly
        out = det.detect(mask, cfg, CAM)
        assert len(out) == 1 and out[0].color == io.ORANGE
        assert out[0].bbox == truth and "bottom_inferred" not in out[0].flags


def test_shadowed_bottom_is_inferred_from_the_top_row():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE, cut_bottom_frac=0.35)      # lower face and half the stripe gone
    out = det.detect_step1(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and "bottom_inferred" in out[0].flags
    assert abs(out[0].bbox[3] - truth[3]) <= 2
    mask[:] = 0
    truth = paint_barrel(mask, 150, 320, body=io.BLUE, cut_bottom_frac=0.2)       # only the lower face gone, stripe intact
    out = det.detect(mask, CFG2, CAM)                                              # step 2: the stripe's row predicts the bottom
    assert len(out) == 1 and out[0].source == "det2" and "bottom_inferred" in out[0].flags
    assert abs(out[0].bbox[3] - truth[3]) <= 2


def test_two_touching_barrels_are_split_by_expected_width():
    mask = np.zeros((480, 640), np.uint8)
    W = CAM.barrel_rows(150).width_px
    a = paint_barrel(mask, 150, 320 - W / 2 - 1, body=io.ORANGE)
    b = paint_barrel(mask, 150, 320 + W / 2 + 1, body=io.BLUE)
    assert len(det.find_blobs(mask)) == 1                        # they merge into one blob
    out = det.detect(mask, CFG1, CAM)                            # step 1: split by the expected width
    assert [o.color for o in out] == [io.ORANGE, io.BLUE]
    assert abs(out[0].bbox[2] - a[2]) <= 3 and abs(out[1].bbox[0] - b[0]) <= 3


def test_barrel_cut_by_the_frame_bottom_is_truncated_not_extended():
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(35)                                      # close: bottom below the frame
    assert r.bottom > 480
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    mask[int(r.top):480, x0:x1] = io.ORANGE
    out = det.detect(mask, CFG1, CAM)
    assert len(out) == 1 and out[0].bbox[3] == 480 and "truncated" in out[0].flags


def test_specks_and_slivers_are_dropped_and_empty_mask_gives_nothing():
    mask = np.zeros((480, 640), np.uint8)
    mask[200:203, 100:103] = io.ORANGE                           # speck
    mask[250:300, 400:404] = io.BLUE                             # a 4 px wide sliver
    for cfg in (CFG1, CFG2):
        assert det.detect(mask, cfg, CAM) == []
        assert det.detect(np.zeros((480, 640), np.uint8), cfg, CAM) == []


def test_draw_only_adds_rectangles():
    img = np.zeros((480, 640, 3), np.uint8)
    out = det.draw(img, det.detect(np.zeros((480, 640), np.uint8), cam=CAM))
    assert (out == img).all()


# ---------------------------------------------------------------- step 2: the stripe

def test_stripe_found_and_barrel_rebuilt_from_it():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.ORANGE)
    stripes = det.find_stripes(mask, CAM, CFG2)
    assert len(stripes) == 1 and stripes[0].body == io.ORANGE and stripes[0].n_other > 0
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 1 and out[0].source == "det2" and out[0].color == io.ORANGE
    assert all(abs(a - b) <= 2 for a, b in zip(out[0].bbox, truth))


def test_shadowed_stripe_still_anchors_the_barrel():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE)
    r = CAM.barrel_rows(150)
    mask[int(round(r.stripe_top)):int(round(r.stripe_bottom)), :] = 0       # the orange stripe went dark
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and out[0].confidence < 1.0
    assert all(abs(a - b) <= 2 for a, b in zip(out[0].bbox, truth))


def test_same_color_barrel_behind_another_gets_its_full_box():
    mask = np.zeros((480, 640), np.uint8)
    back = paint_barrel(mask, 220, 350, body=io.ORANGE)                       # farther, higher in the image
    front = paint_barrel(mask, 150, 320, body=io.ORANGE)                      # nearer, hides the back one's left half
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 2 and all(o.color == io.ORANGE for o in out)
    by_x = sorted(out, key=lambda o: o.bbox[0])
    assert abs(by_x[0].bbox[3] - front[3]) <= 2                               # front barrel: seen bottom
    b = by_x[1]
    assert abs(b.bbox[3] - back[3]) <= 3 and abs(b.bbox[1] - back[1]) <= 3    # back barrel: full box through the occluder
    assert "occluded" in b.flags and (b.bbox[2] - b.bbox[0]) >= 0.9 * (back[2] - back[0])


def test_orange_thing_without_a_stripe_is_not_a_barrel():
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(150)
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    mask[int(r.top):int(r.bottom), x0:x1] = io.ORANGE                        # barrel-sized, no stripe
    assert det.detect_step1(mask, cam=CAM)                                    # step 1 would box it
    assert det.detect(mask, CFG2, CAM) == []                                    # step 2 does not
    assert det.DetConfig().require_stripe and det.detect(mask, cam=CAM) == []    # ... and step 2 is the default


def test_close_barrel_with_stripe_below_the_frame_is_kept_without_a_stripe():
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(35)
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    mask[int(r.top):480, x0:x1] = io.ORANGE
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 1 and out[0].bbox[3] == 480 and "truncated" in out[0].flags


def test_touching_same_color_pair_gives_two_stripes():
    mask = np.zeros((480, 640), np.uint8)
    W = CAM.barrel_rows(150).width_px
    a = paint_barrel(mask, 150, 320 - W / 2 - 1, body=io.BLUE)
    b = paint_barrel(mask, 150, 320 + W / 2 + 1, body=io.BLUE)
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 2 and all(o.color == io.BLUE and o.source == "det2" for o in out)
    assert abs(out[0].bbox[2] - a[2]) <= 3 and abs(out[1].bbox[0] - b[0]) <= 3
