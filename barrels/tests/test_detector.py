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


def test_dark_gap_alone_is_not_a_stripe_unless_asked():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE)
    r = CAM.barrel_rows(150)
    mask[int(round(r.stripe_top)):int(round(r.stripe_bottom)), :] = 0       # the orange stripe went dark
    assert det.detect(mask, CFG2, CAM) == []                                 # hardening (a): a gap with no stripe pixel is not a stripe
    out = det.detect(mask, dataclasses.replace(CFG2, dark_stripe=True), CAM)  # the 2026-11-03 behaviour, on request
    assert len(out) == 1 and out[0].color == io.BLUE and out[0].confidence < 1.0
    out = det.detect(mask, dataclasses.replace(CFG2, stripe_mode="bands"), CAM)   # and the old finder still does it
    assert len(out) == 1 and out[0].color == io.BLUE


def test_shadow_glued_to_the_stripe_does_not_veto_it():
    """Hardening (b): the lower face below the stripe is unlabeled (shadow), the base row is labeled again."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.ORANGE)
    r = CAM.barrel_rows(150)
    st, sb, top, bottom = int(round(r.stripe_top)), int(round(r.stripe_bottom)), truth[1], truth[3]
    mask[top + 4:st, truth[0]:truth[2]] = 0                                  # both faces dark: only 4 body rows at the top ...
    mask[sb:bottom - 4, truth[0]:truth[2]] = 0                               # ... and 4 at the base survive around the stripe
    assert det.detect(mask, dataclasses.replace(CFG2, stripe_mode="bands"), CAM) == []   # the old finder: band (stripe + shadow) too tall
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and out[0].source == "det2"
    assert abs(out[0].bbox[3] - truth[3]) <= 3


def test_box_must_hold_body_color():
    """Hardening (c): a blue barrel's body between two orange things is not an orange barrel."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(150)
    W = r.width_px
    top, bottom = int(round(r.top)), int(round(r.bottom))
    st, sb = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    x0, x1 = int(round(320 - W / 2)), int(round(320 + W / 2))
    mask[top:bottom, x0:x1] = io.BLUE                                        # a blue body ...
    mask[st - 3:st, x0:x1] = io.ORANGE                                       # ... with a thin orange rim right above its middle band ...
    mask[sb:sb + 3, x0:x1] = io.ORANGE                                       # ... and right below it: a blue 'stripe' between orange
    assert any(b.color == io.ORANGE for b in det.detect(mask, dataclasses.replace(CFG2, body_min=0.0), CAM))   # without (c): an orange box
    out = det.detect(mask, CFG2, CAM)
    assert not any(b.color == io.ORANGE for b in out)                        # with (c): the box would be blue, not orange -> no orange box


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


def test_far_barrel_above_a_close_one_does_not_hide_it():
    """(g) 2026-11-09: the close-up with its stripe below the frame must keep its box even when a far barrel with a
    stripe stands directly above it in the picture (same columns, different rows)."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(35)
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    mask[int(r.top):480, x0:x1] = io.ORANGE                 # the close one, stripe below the frame
    paint_barrel(mask, 300, 320, body=io.BLUE)              # a far one, straight above it in the image
    out = sorted(det.detect(mask, CFG2, CAM), key=lambda b: b.bbox[1])
    assert [b.color for b in out] == [io.BLUE, io.ORANGE]
    assert out[1].bbox[3] == 480 and "truncated" in out[1].flags


def test_touching_same_color_pair_gives_two_stripes():
    mask = np.zeros((480, 640), np.uint8)
    W = CAM.barrel_rows(150).width_px
    a = paint_barrel(mask, 150, 320 - W / 2 - 1, body=io.BLUE)
    b = paint_barrel(mask, 150, 320 + W / 2 + 1, body=io.BLUE)
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 2 and all(o.color == io.BLUE and o.source == "det2" for o in out)
    assert abs(out[0].bbox[2] - a[2]) <= 3 and abs(out[1].bbox[0] - b[0]) <= 3


def test_stripeless_piece_must_be_barrel_tall():
    """Hardening (d): a blue blob of barrel width whose bottom sits just below the horizon but which is twice as tall
    as a barrel there (a jacket above the table edge, campus core_01) is not a barrel; the width check alone took it."""
    cam = geo.AIM_4A8B6118_BOXFIT
    mask = np.zeros((480, 640), np.uint8)
    mask[75:120, 309:333] = io.BLUE                                          # 24 wide, 45 tall, bottom row 120 (horizon 76)
    assert det.detect(mask, CFG2, cam) == []
    assert len(det.detect(mask, dataclasses.replace(CFG2, height_max=0.0), cam)) == 1   # the pre-2026-11-08 check (width only) took it
    H = cam.expected_barrel_height_px(bottom_row=120)
    mask[:] = 0
    mask[120 - int(round(H)):120, 309:333] = io.BLUE                         # the same blob at a barrel's height passes the shape checks ...
    assert len(det.detect_step1(mask, CFG2, cam)) == 1
    assert det.detect(mask, CFG2, cam) == []                                 # ... but a stripe (5.8 px here) could have been seen, so no box


def test_box_is_as_wide_as_the_body_not_the_stripe():
    """(f) 2026-11-09: a stripe whose outer columns went dark must not make the box thinner than the barrel."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 100, 320, body=io.BLUE)
    x0, top, x1, bottom = truth
    r = CAM.barrel_rows(100)
    sy0, sy1 = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    trim = int(round(0.08 * (x1 - x0)))
    mask[sy0:sy1, x0:x0 + trim] = 0; mask[sy0:sy1, x1 - trim:x1] = 0      # the stripe's outer 8 % per side unlabeled (still a "full" stripe)
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE
    assert abs(out[0].bbox[0] - x0) <= 2 and abs(out[0].bbox[2] - x1) <= 2
    thin = det.detect(mask, dataclasses.replace(CFG2, body_width=0.0), CAM)     # the old rule: stripe width
    assert len(thin) == 1 and (thin[0].bbox[2] - thin[0].bbox[0]) <= 0.86 * (x1 - x0)


def test_body_width_cannot_stretch_into_a_touching_neighbour():
    """Two touching same-color barrels: each box stays about one barrel wide."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(100); W = r.width_px
    a = paint_barrel(mask, 100, 320 - W / 2, body=io.ORANGE)
    b = paint_barrel(mask, 100, 320 + W / 2, body=io.ORANGE)
    out = sorted(det.detect(mask, CFG2, CAM), key=lambda z: z.bbox[0])
    assert len(out) == 2
    for z, truth in zip(out, (a, b)):
        assert (z.bbox[2] - z.bbox[0]) <= 1.25 * W and abs((z.bbox[0] + z.bbox[2]) / 2 - (truth[0] + truth[2]) / 2) <= 0.15 * W


def test_stripe_cut_by_the_frame_edge_widens_into_the_edge():
    """Hardening (e): a barrel half out of the frame on the right — the full box goes to the frame edge, not leftward."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(120)
    W = r.width_px
    truth = paint_barrel(mask, 120, 640 - W * 0.3)          # 30 % of the barrel inside the frame, the rest beyond x = 640
    out = det.detect(mask, CFG2, CAM)
    assert len(out) == 1 and "truncated" in out[0].flags
    assert out[0].bbox[2] == 640 and abs(out[0].bbox[0] - truth[0]) <= 2   # left edge where the barrel starts, right edge at the frame
