"""Sanity checks of the v2 detector's mechanics on synthetic barrels (its quality is judged by eval numbers)."""
import dataclasses

import numpy as np

from barrels import detector as det, geometry as geo, io

CAM = geo.NOMINAL
CFG1 = dataclasses.replace(det.DetConfig(), require_stripe=False)    # step 1 alone (the detector before 2026-11-05)
CFG2 = dataclasses.replace(det.DetConfig(), require_stripe=True)     # the stripe step — also the default
PRE19 = dataclasses.replace(CFG2, side_hidden=False, seam_height=False, cap_seen_bottom=False)   # the detector before 2026-11-19 (tests/test_detector_side.py and test_detector_bottom.py have the three switches)


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
    no_c = dataclasses.replace(CFG2, body_min=0.0, edge_check=False)        # edge_check (2026-11-19) refuses this candidate too, for another reason
    assert any(b.color == io.ORANGE for b in det.detect(mask, no_c, CAM))    # without (c): an orange box
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
    old = det.detect(mask, dataclasses.replace(CFG2, cover_rows=False), CAM)     # the pre-2026-11-09 rule loses the close one
    assert [b.color for b in old] == [io.BLUE]


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


def _barrel_behind_a_slanted_edge(seen_at_stripe=0.3, seen_at_bottom=0.95):
    """A blue barrel whose right part is hidden by something that is not barrel-colored and whose edge slants
    (like the robot's body in campus occl_02): the stripe shows `seen_at_stripe` of the width, the bottom more."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE)
    x0, top, x1, bottom = truth
    r = CAM.barrel_rows(150)
    mid = (r.stripe_top + r.stripe_bottom) / 2
    for y in range(top, bottom):
        frac = seen_at_stripe + (seen_at_bottom - seen_at_stripe) * max(0.0, (y - mid) / (bottom - mid))
        mask[y, x0 + int(round(frac * (x1 - x0))):] = 0
    return mask, truth


def test_log_names_the_refusing_test_and_never_changes_the_answer():
    mask, truth = _barrel_behind_a_slanted_edge()
    log = []
    assert det.detect(mask, PRE19, CAM, log=log) == det.detect(mask, PRE19, CAM) == []    # 0.3 of a width: under stripe_w_min 0.4 (the finder's floor before 2026-11-19)
    assert any(e["stage"] == "stripe" and e["why"] == "width" and e["body"] == io.BLUE for e in log)
    mask2 = np.zeros((480, 640), np.uint8); paint_barrel(mask2, 150, 320)
    log = []
    assert det.detect(mask2, CFG2, CAM, log=log) == det.detect(mask2, CFG2, CAM)
    assert [e["why"] for e in log if e["stage"] == "barrel"] == ["kept"]


def test_barrel_hidden_at_the_side_narrow_stripe_and_hidden_side_from_the_body():
    mask, truth = _barrel_behind_a_slanted_edge()
    narrow = dataclasses.replace(PRE19, stripe_w_min=0.25)          # the 2026-11-11 switches, on the detector they were made for
    out = det.detect(mask, narrow, CAM)                              # the stripe is accepted; the box is centred on it
    assert len(out) == 1 and out[0].color == io.BLUE and "occluded" in out[0].flags
    centred = det.box_iou(out[0].bbox, truth)
    out_h = det.detect(mask, dataclasses.replace(narrow, occl_body_side=True), CAM)
    assert len(out_h) == 1 and "occluded" in out_h[0].flags          # (h): the body below the stripe shows the real extent
    assert det.box_iou(out_h[0].bbox, truth) > max(0.8, centred)
    # (h) changes nothing for a barrel that is not hidden
    full = np.zeros((480, 640), np.uint8); paint_barrel(full, 150, 320)
    assert det.detect(full, dataclasses.replace(CFG2, occl_body_side=True), CAM) == det.detect(full, CFG2, CAM)


# ---------------------------------------------------------------- 2026-11-18: a stripe in pieces; a barrel behind a barrel of the other color

OLD = dataclasses.replace(PRE19, stripe_join=False, cap_behind=False)    # the detector before 2026-11-18, spelled out
JOIN = dataclasses.replace(OLD, stripe_join=True)
CAP = dataclasses.replace(OLD, cap_behind=True)


def _close(box, truth, px=2):
    return all(abs(a - b) <= px for a, b in zip(box, truth))


def test_stripe_cut_by_a_pale_slit_is_one_stripe_with_stripe_join():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320)
    r = CAM.barrel_rows(150); W = truth[2] - truth[0]
    c = truth[0] + int(0.45 * W)
    mask[int(r.stripe_top) - 2:int(r.stripe_bottom) + 3, c:c + int(0.15 * W)] = 0       # a highlight 0.15 of a barrel wide across the stripe
    old = det.detect(mask, OLD, CAM)                                 # each piece alone: "partly hidden" stripes, boxes in the wrong place
    assert not any(_close(b.bbox, truth) for b in old)
    out = det.detect(mask, JOIN, CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and _close(out[0].bbox, truth) and "occluded" not in out[0].flags


def test_stripe_under_a_washed_out_upper_body_is_one_stripe_with_stripe_join():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE)
    r = CAM.barrel_rows(150); W = truth[2] - truth[0]
    mask[truth[1]:int(round(r.stripe_top)), truth[0] + int(0.25 * W):truth[2] - int(0.25 * W)] = 0   # the upper body pale in the middle half
    assert det.detect(mask, OLD, CAM) == []                          # the stripe has body above it only at its two ends: each under the width floor
    out = det.detect(mask, JOIN, CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and _close(out[0].bbox, truth)


def test_stripe_join_does_not_join_pieces_that_are_taller_than_wide():
    """Round 2: slivers of a body between specks are tall; a cut stripe's pieces are flat. Only flat pieces join."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(150)
    x0, x1 = int(round(320 - r.width_px / 2)), int(round(320 + r.width_px / 2))
    mask[int(round(r.top)):int(round(r.bottom)), x0:x1] = io.BLUE            # a blue body, no stripe
    st, sb = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    for c in (x0 + 8, x0 + 24, x0 + 40):
        mask[st:sb, c:c + 5] = io.ORANGE                                      # three orange slivers 5 px wide, a stripe tall, 0.55 of a barrel together
    assert sb - st > 5
    assert det.detect(mask, OLD, CAM) == [] and det.detect(mask, JOIN, CAM) == []


def _cap(seen=0.55):
    """The top of a blue barrel 22 cm away of which only the left `seen` shows (top row to the stripe's top)."""
    r = CAM.barrel_rows(220)
    mask = np.zeros((480, 640), np.uint8)
    x0, n = 300, int(round(seen * r.width_px))
    mask[int(round(r.top)):int(round(r.stripe_top)), x0:x0 + n] = io.BLUE
    return mask, r, x0, n


def test_narrow_cap_needs_one_side_hidden_by_a_found_barrel():
    from barrels.detect_types import Barrel
    mask, r, x0, n = _cap()
    top, bottom, W = int(round(r.top)), int(round(r.bottom)), int(round(r.width_px))
    right = Barrel(color=io.ORANGE, bbox=(x0 + n - 5, top + 2, x0 + n + 60, bottom + 20))      # a nearer barrel over the cap's right side
    out = det.caps_behind(mask, [right], [], CAM, CAP)
    assert len(out) == 1 and out[0].color == io.BLUE and {"occluded", "bottom_inferred"} <= out[0].flags
    assert out[0].bbox[:3] == (x0, top, x0 + W) and abs(out[0].bbox[3] - bottom) <= 1          # widened to a full barrel toward the hidden side
    below = Barrel(color=io.ORANGE, bbox=(x0 - 5, int(round(r.stripe_top)), x0 + 60, bottom + 20))   # a barrel below it only: no side is hidden
    log = []
    assert det.caps_behind(mask, [below], [], CAM, CAP, log) == [] and [e["why"] for e in log] == ["narrow"]
    left = Barrel(color=io.ORANGE, bbox=(x0 - 60, top + 2, x0 + 5, bottom + 20))               # both sides hidden: a wedge between two barrels
    log = []
    assert det.caps_behind(mask, [left, right], [], CAM, CAP, log) == [] and [e["why"] for e in log] == ["both_sides"]


def test_cap_uses_its_seen_bottom_when_it_agrees():
    from barrels.detect_types import Barrel
    mask, r, x0, n = _cap()
    top, bottom = int(round(r.top)), int(round(r.bottom))
    right = Barrel(color=io.ORANGE, bbox=(x0 + n - 5, top + 2, x0 + n + 60, bottom + 20))
    mask[int(round(r.stripe_bottom)):bottom - 5, x0:x0 + 8] = io.BLUE        # its lower body shows beside the front barrel and ends 5 px above the estimate
    out = det.caps_behind(mask, [right], [], CAM, CAP)
    assert len(out) == 1 and out[0].bbox[3] == bottom - 5
    mask[int(round(r.stripe_bottom)):bottom + 40, x0:x0 + 8] = io.BLUE       # blue running on far below the estimate is not this barrel's bottom
    out = det.caps_behind(mask, [right], [], CAM, CAP)
    assert out == [] or abs(out[0].bbox[3] - bottom) <= 1


def test_stripe_join_joins_nothing_wider_than_one_barrel():
    W = CAM.barrel_rows(150).width_px
    for gap in (0.0, 0.5):                                           # touching, and half a barrel apart: same color, same rows
        mask = np.zeros((480, 640), np.uint8)
        paint_barrel(mask, 150, 320 - (1 + gap) * W / 2 - 1, body=io.BLUE)
        paint_barrel(mask, 150, 320 + (1 + gap) * W / 2 + 1, body=io.BLUE)
        assert len(det.detect(mask, OLD, CAM)) == 2
        assert det.detect(mask, JOIN, CAM) == det.detect(mask, OLD, CAM)
    mask = np.zeros((480, 640), np.uint8); paint_barrel(mask, 150, 320)
    assert det.detect(mask, JOIN, CAM) == det.detect(mask, OLD, CAM)          # and nothing changes for a whole stripe


def _behind(dx):
    """A blue barrel 22 cm away, and an orange one 15 cm away in front of it, dx px to the left of it."""
    mask = np.zeros((480, 640), np.uint8)
    back = paint_barrel(mask, 220, 320 + dx, body=io.BLUE)
    front = paint_barrel(mask, 150, 320, body=io.ORANGE)
    return mask, back, front


def test_barrel_behind_one_of_the_other_color_is_found_from_its_cap():
    for dx in (0, 15, 30):
        mask, back, front = _behind(dx)
        log = []
        old = det.detect(mask, OLD, CAM, log=log)                    # the back barrel's orange stripe joins the front barrel's orange body
        assert [b.color for b in old] == [io.ORANGE]
        assert any(e["stage"] == "stripe" and e["why"] == "height" and e["body"] == io.BLUE for e in log)
        out = det.detect(mask, CAP, CAM)
        assert sorted(b.color for b in out) == [io.ORANGE, io.BLUE]
        b = next(b for b in out if b.color == io.BLUE)
        assert det.box_iou(b.bbox, back) > 0.9 and abs(b.bbox[3] - back[3]) <= 2      # full box, bottom from the cap's width
        assert {"occluded", "bottom_inferred"} <= b.flags and b.source == "det3"
        assert [o for o in out if o.color == io.ORANGE] == old                        # the front barrel is untouched


def test_cap_needs_a_found_barrel_in_front_of_it():
    mask, back, front = _behind(0)
    r = CAM.barrel_rows(220)
    alone = np.zeros((480, 640), np.uint8)
    alone[back[1]:int(round(r.stripe_top)), back[0]:back[2]] = io.BLUE          # the same cap with nothing below it
    assert det.detect(alone, CAP, CAM) == []
    lower = mask[front[1]:]
    lower[lower == io.BLUE] = 0                                                  # the front barrel loses its stripe:
    assert det.detect(mask, OLD, CAM) == []                                      # ... it is not found any more,
    assert det.detect(mask, CAP, CAM) == []                                      # ... so the cap above it is not a barrel either


def test_tall_body_colored_thing_above_a_barrel_is_not_a_cap():
    mask = np.zeros((480, 640), np.uint8)
    front = paint_barrel(mask, 100, 320, body=io.ORANGE)                # a near barrel: its top is low in the picture
    r = CAM.barrel_rows(220)
    top, W = int(round(r.top)), r.width_px
    assert front[1] - top > 1.5 * (r.stripe_top - r.top)                # from a 22 cm barrel's top row down to the near barrel: far more than an upper body
    mask[top:front[1], int(320 - W / 2):int(320 + W / 2)] = io.BLUE     # blue of barrel width for that row, all the way down to the front barrel
    log = []
    out = det.detect(mask, CAP, CAM, log=log)
    assert [b.color for b in out] == [io.ORANGE]
    assert any(e["stage"] == "cap" and e["why"] == "height" for e in log)


def test_cap_behind_changes_nothing_when_no_barrel_is_hidden():
    W = CAM.barrel_rows(150).width_px
    scenes = []
    m = np.zeros((480, 640), np.uint8); paint_barrel(m, 150, 320); scenes.append(m)                      # one barrel
    m = np.zeros((480, 640), np.uint8)                                                                   # orange, blue, orange touching
    for k, body in ((-1, io.ORANGE), (0, io.BLUE), (1, io.ORANGE)):
        paint_barrel(m, 150, 320 + k * (W + 1), body=body)
    scenes.append(m)
    m = np.zeros((480, 640), np.uint8)                                                                   # same color behind (stripe shows)
    paint_barrel(m, 220, 350, body=io.ORANGE); paint_barrel(m, 150, 320, body=io.ORANGE); scenes.append(m)
    m = np.zeros((480, 640), np.uint8)                                                                   # a far barrel above a close-up
    r = CAM.barrel_rows(35); m[int(r.top):480, int(320 - r.width_px / 2):int(320 + r.width_px / 2)] = io.ORANGE
    paint_barrel(m, 300, 320, body=io.BLUE); scenes.append(m)
    for m in scenes:
        assert det.detect(m, CAP, CAM) == det.detect(m, OLD, CAM)
