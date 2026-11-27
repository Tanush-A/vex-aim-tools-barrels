"""The paint checks (stage 11, ``drop_unlike_paint``, the last; experiments/2026-11-27_checks). Mechanics on synthetic masks:
a barrel painted solid keeps its box; a box whose barrel color is speckle is dropped ("speckle"); a box read from a
"stripe" taller than a stripe, with little body around it, is dropped ("label"); a reading that cannot be made never
drops a box. Quality is judged by the experiment."""
import dataclasses

import numpy as np

from barrels import detector as det, io
from barrels.detect_types import Barrel
from test_detector import CAM, paint_barrel, whys

ON = det.DetConfig()


def test_a_solid_barrel_keeps_its_box():
    mask = np.zeros((480, 640), np.uint8)
    box = paint_barrel(mask, 220, 320, body=io.BLUE)
    log: list = []
    on = det.detect(mask, ON, cam=CAM, log=log)
    assert len(on) == 1 and det.box_iou(on[0].bbox, box) > 0.8
    assert not whys(log, "verify")
    f = det.Found(on[0], "whole_stripe", evidence=on[0].bbox)
    solid, _, body = det.paint_readings(f, mask, CAM)
    assert solid > 0.9 and body > 0.8


def test_speckle_paint_is_dropped():
    """The same barrel painted as dots: 3 x 3 dots of barrel color 3 px apart, as a printed tin reads. The closing (3 x 3)
    does not join them, so about one pixel in nine is solid: dropped as speckle. With solid_min 0 it would stay. (A pixel
    checkerboard is closed into solid paint first: test_pinholes_close.)"""
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 220, 320, body=io.BLUE)
    found = [f for f in det.boxes_from_stripes(det.find_stripes(mask, CAM)[0], mask, CAM)[0]]
    assert len(found) == 1
    yy, xx = np.mgrid[0:480, 0:640]
    speckled = mask.copy()
    speckled[((yy // 3) % 2 == 1) | ((xx // 3) % 2 == 1)] = 0
    log: list = []
    assert det.drop_unlike_paint(found, speckled, CAM, ON, log) == []
    assert whys(log, "verify") == ["speckle"]
    assert det.drop_unlike_paint(found, speckled, CAM, dataclasses.replace(ON, solid_min=0.0)) == found


def test_a_label_taller_than_a_stripe_with_thin_body_is_dropped():
    """A jar: a blue band twice as tall as the stripe its row predicts, a thin rim of orange above and below. The box's
    rows outside the band hold little orange: a label, not a stripe."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(220)
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    top, bottom = int(r.top), int(r.bottom)
    hs = r.stripe_bottom - r.stripe_top
    s0, s1 = int(r.stripe_center - hs), int(r.stripe_center + hs)               # twice a stripe's height
    mask[s0:s1, x0:x1] = io.BLUE
    mask[s0 - 3:s0, x0:x1] = io.ORANGE
    mask[s1:s1 + 3, x0:x1] = io.ORANGE
    stripe = det.Stripe(body=io.ORANGE, bbox=(x0, s0, x1, s1), n_other=(s1 - s0) * (x1 - x0), n_dark=0, center_row=r.stripe_center)
    f = det.Found(Barrel(color=io.ORANGE, bbox=(x0, top, x1, bottom), source="det2"), "whole_stripe", stripe=stripe, evidence=stripe.bbox)
    solid, stripe_h, body = det.paint_readings(f, mask, CAM)
    assert stripe_h > 1.5 and body < 0.3            # 10th to 90th percentile of the rows: 1.6 of a stripe
    log: list = []
    assert det.drop_unlike_paint([f], mask, CAM, ON, log) == [] and whys(log, "verify") == ["label"]
    assert det.drop_unlike_paint([f], mask, CAM, dataclasses.replace(ON, label_stripe=2.0)) == [f]       # under 2 x: a stripe


def test_a_box_with_no_stripe_is_not_asked_the_label_question():
    mask = np.zeros((480, 640), np.uint8)
    box = paint_barrel(mask, 220, 320, body=io.ORANGE)
    f = det.Found(Barrel(color=io.ORANGE, bbox=box, source="det1"), "closeup")
    solid, stripe_h, body = det.paint_readings(f, mask, CAM)
    assert np.isnan(stripe_h)
    assert det.drop_unlike_paint([f], mask, CAM, ON) == [f]


def test_two_painted_barrels_keep_both_boxes():
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 220, 200, body=io.ORANGE)
    paint_barrel(mask, 300, 420, body=io.BLUE)
    log: list = []
    assert len(det.detect(mask, cam=CAM, log=log)) == 2 and not whys(log, "verify")


def test_pinholes_close():
    """Damage that is one pixel wide (every other pixel missing) is closed before solidity is read: the barrel stays."""
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 220, 320, body=io.BLUE)
    found = det.boxes_from_stripes(det.find_stripes(mask, CAM)[0], mask, CAM)[0]
    yy, xx = np.mgrid[0:480, 0:640]
    holes = mask.copy()
    holes[((yy + xx) % 2 == 1) & (yy % 2 == 1)] = 0
    solid, _, _ = det.paint_readings(found[0], holes, CAM)
    assert solid > 0.8
    assert det.drop_unlike_paint(found, holes, CAM, ON) == found
