"""Sanity checks of the v2 detector's mechanics on synthetic barrels (its quality is judged by eval numbers).

The detector has no on/off switches (the collapse of 2026-11-26): every test states what the detector does with its
default numbers. A test of one stage calls that stage's function, or reads the reason log to see which check decided."""
import numpy as np

from barrels import detector as det, geometry as geo, io

CAM = geo.NOMINAL
CFG = det.DetConfig()


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


def pieces(mask, cam=CAM):
    """Stage 1 alone: the barrel-shaped pieces, before the stripe step decides which of them are barrels."""
    return [p.barrel for p in det.find_pieces(mask, cam)]


def stripes_of(mask, cam=CAM):
    """Stage 2 alone: the stripes (without the left-over pieces)."""
    return det.find_stripes(mask, cam)[0]


def caps(mask, boxes, log=None):
    """Stage 6 alone: the barrels behind the given found barrels, from their tops."""
    return [f.barrel for f in det.caps_behind([det.Found(b, "given") for b in boxes], [], mask, CAM, log=log)]


def whys(log, stage):
    """The reasons the log holds for one stage ("kept" = a box was drawn there)."""
    return [e["why"] for e in log if e["stage"] == stage]


def test_single_barrel_seen_bottom_kept():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320)
    for out in (pieces(mask), det.detect(mask, cam=CAM)):         # stage 1 and the whole detector box a plain barrel exactly
        assert len(out) == 1 and out[0].color == io.ORANGE
        assert out[0].bbox == truth and "bottom_inferred" not in out[0].flags


def test_shadowed_bottom_is_inferred_from_the_top_row():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE, cut_bottom_frac=0.35)      # lower face and half the stripe gone
    out = pieces(mask)
    assert len(out) == 1 and out[0].color == io.BLUE and "bottom_inferred" in out[0].flags
    assert abs(out[0].bbox[3] - truth[3]) <= 2
    mask[:] = 0
    truth = paint_barrel(mask, 150, 320, body=io.BLUE, cut_bottom_frac=0.2)       # only the lower face gone, stripe intact
    out = det.detect(mask, cam=CAM)                                                # the stripe's row predicts the bottom
    assert len(out) == 1 and out[0].source == "det2" and "bottom_inferred" in out[0].flags
    assert abs(out[0].bbox[3] - truth[3]) <= 2


def test_two_touching_barrels_are_split_by_expected_width():
    mask = np.zeros((480, 640), np.uint8)
    W = CAM.barrel_rows(150).width_px
    a = paint_barrel(mask, 150, 320 - W / 2 - 1, body=io.ORANGE)
    b = paint_barrel(mask, 150, 320 + W / 2 + 1, body=io.BLUE)
    assert len(det.find_blobs(mask)) == 1                        # they merge into one blob
    out = pieces(mask)                                           # stage 1: split by the expected width
    assert [o.color for o in out] == [io.ORANGE, io.BLUE]
    assert abs(out[0].bbox[2] - a[2]) <= 3 and abs(out[1].bbox[0] - b[0]) <= 3


def test_barrel_cut_by_the_frame_bottom_is_truncated_not_extended():
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(35)                                      # close: bottom below the frame
    assert r.bottom > 480
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    mask[int(r.top):480, x0:x1] = io.ORANGE
    out = pieces(mask)
    assert len(out) == 1 and out[0].bbox[3] == 480 and "truncated" in out[0].flags


def test_specks_and_slivers_are_dropped_and_empty_mask_gives_nothing():
    mask = np.zeros((480, 640), np.uint8)
    mask[200:203, 100:103] = io.ORANGE                           # speck
    mask[250:300, 400:404] = io.BLUE                             # a 4 px wide sliver
    for m in (mask, np.zeros((480, 640), np.uint8)):
        assert pieces(m) == [] and det.detect(m, cam=CAM) == []


def test_draw_only_adds_rectangles():
    img = np.zeros((480, 640, 3), np.uint8)
    out = det.draw(img, det.detect(np.zeros((480, 640), np.uint8), cam=CAM))
    assert (out == img).all()


# ---------------------------------------------------------------- the stripe

def test_stripe_found_and_barrel_rebuilt_from_it():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.ORANGE)
    stripes = stripes_of(mask)
    assert len(stripes) == 1 and stripes[0].body == io.ORANGE and stripes[0].n_other > 0
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].source == "det2" and out[0].color == io.ORANGE
    assert all(abs(a - b) <= 2 for a, b in zip(out[0].bbox, truth))


def test_dark_gap_alone_is_not_a_stripe():
    mask = np.zeros((480, 640), np.uint8)
    paint_barrel(mask, 150, 320, body=io.BLUE)
    r = CAM.barrel_rows(150)
    mask[int(round(r.stripe_top)):int(round(r.stripe_bottom)), :] = 0       # the orange stripe went dark
    assert det.detect(mask, cam=CAM) == []                                   # a gap with no stripe pixel is not a stripe


def test_shadow_glued_to_the_stripe_does_not_veto_it():
    """The lower face below the stripe is unlabeled (shadow), the base row is labeled again."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.ORANGE)
    r = CAM.barrel_rows(150)
    st, sb, top, bottom = int(round(r.stripe_top)), int(round(r.stripe_bottom)), truth[1], truth[3]
    mask[top + 4:st, truth[0]:truth[2]] = 0                                  # both faces dark: only 4 body rows at the top ...
    mask[sb:bottom - 4, truth[0]:truth[2]] = 0                               # ... and 4 at the base survive around the stripe
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and out[0].source == "det2"
    assert abs(out[0].bbox[3] - truth[3]) <= 3


def test_box_must_hold_body_color():
    """A blue barrel's body between two orange things is not an orange barrel: in the stripe's columns, outside the
    stripe's rows, the box must hold more body color than stripe color."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(150)
    W = r.width_px
    top, bottom = int(round(r.top)), int(round(r.bottom))
    st, sb = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    x0, x1 = int(round(320 - W / 2)), int(round(320 + W / 2))
    mask[top:bottom, x0:x1] = io.BLUE                                        # a blue body ...
    mask[st - 3:st, x0:x1] = io.ORANGE                                       # ... with a thin orange rim right above its middle band ...
    mask[sb:sb + 3, x0:x1] = io.ORANGE                                       # ... and right below it: a blue 'stripe' between orange
    assert not any(b.color == io.ORANGE for b in det.detect(mask, cam=CAM))  # the box would be blue, not orange -> no orange box
    # The candidate above is refused twice over: its orange "body" also ends against blue (top_against_barrel, asked first).
    # With six empty rows between each orange rim and the blue beyond it, only the body-color check is left to refuse it.
    mask[st - 9:st - 3, x0:x1] = 0
    mask[sb + 3:sb + 9, x0:x1] = 0
    log = []
    assert not any(b.color == io.ORANGE for b in det.detect(mask, cam=CAM, log=log))
    assert any(e["stage"] == "barrel" and e["why"] == "body_min" and e["body"] == io.ORANGE for e in log)


def test_same_color_barrel_behind_another_gets_its_full_box():
    mask = np.zeros((480, 640), np.uint8)
    back = paint_barrel(mask, 220, 350, body=io.ORANGE)                       # farther, higher in the image
    front = paint_barrel(mask, 150, 320, body=io.ORANGE)                      # nearer, hides the back one's left half
    out = det.detect(mask, cam=CAM)
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
    assert pieces(mask)                                                       # stage 1 has it as a barrel-shaped piece
    assert det.detect(mask, cam=CAM) == []                                    # the detector does not box it


def test_close_barrel_with_stripe_below_the_frame_is_kept_without_a_stripe():
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(35)
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    mask[int(r.top):480, x0:x1] = io.ORANGE
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].bbox[3] == 480 and "truncated" in out[0].flags


def test_far_barrel_above_a_close_one_does_not_hide_it():
    """The close-up with its stripe below the frame must keep its box even when a far barrel with a stripe stands
    directly above it in the picture (same columns, different rows): a box accounts for a piece only if they share rows."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(35)
    x0, x1 = int(320 - r.width_px / 2), int(320 + r.width_px / 2)
    mask[int(r.top):480, x0:x1] = io.ORANGE                 # the close one, stripe below the frame
    paint_barrel(mask, 300, 320, body=io.BLUE)              # a far one, straight above it in the image
    out = sorted(det.detect(mask, cam=CAM), key=lambda b: b.bbox[1])
    assert [b.color for b in out] == [io.BLUE, io.ORANGE]
    assert out[1].bbox[3] == 480 and "truncated" in out[1].flags


def test_touching_same_color_pair_gives_two_stripes():
    mask = np.zeros((480, 640), np.uint8)
    W = CAM.barrel_rows(150).width_px
    a = paint_barrel(mask, 150, 320 - W / 2 - 1, body=io.BLUE)
    b = paint_barrel(mask, 150, 320 + W / 2 + 1, body=io.BLUE)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 2 and all(o.color == io.BLUE and o.source == "det2" for o in out)
    assert abs(out[0].bbox[2] - a[2]) <= 3 and abs(out[1].bbox[0] - b[0]) <= 3


def test_a_barrel_on_the_table_has_a_stripe_tall_enough_to_resolve():
    """The stripe finder, the caps and the half stripes ask only "at least min_width_px wide" (``on_the_table``). That is
    enough because, with each camera preset and the default numbers, the stripe of the farthest such barrel is still
    min_stripe_px tall, and a nearer barrel's is taller. If this fails after a change of the camera numbers or of the two
    limits, ``on_the_table`` must ask the stripe's height again (its assertion says the same at run time)."""
    for cam in (geo.AIM_4A8B6118_BOXFIT, geo.NOMINAL, geo.AIM_4A8B6118):
        d_far = cam.f * geo.BARREL_BULGE_DIAMETER_MM / CFG.min_width_px          # the farthest barrel that is min_width_px wide
        for d in np.arange(20.0, d_far, 5.0).tolist() + [d_far - 1e-6]:
            at = det.BarrelAt(d, cam.barrel_rows(d))
            assert det.on_the_table(at, CFG) and at.Hs >= CFG.min_stripe_px
        assert not det.on_the_table(det.BarrelAt(d_far + 1, cam.barrel_rows(d_far + 1)), CFG)


def test_stripeless_piece_must_be_barrel_tall():
    """A blue blob of barrel width whose bottom sits just below the horizon but which is twice as tall as a barrel
    there (a jacket above the table edge, campus core_01) is not a barrel; the width check alone would take it. Its top
    is above the horizon, where no barrel on the table has its top. And a piece low in the frame that is barrel-wide
    but far too short for its bottom row is not a barrel either."""
    cam = geo.AIM_4A8B6118_BOXFIT
    mask = np.zeros((480, 640), np.uint8)
    mask[75:120, 309:333] = io.BLUE                                          # 24 wide, 45 tall, bottom row 120 (horizon 76)
    assert det.above_horizon(cam, 75) and det.above_horizon(cam, 76) and not det.above_horizon(cam, 77)
    log = []
    assert det.detect(mask, cam=cam, log=log) == []
    assert whys(log, "piece") == ["above_horizon"]                           # refused by stage 1: its top is above the horizon
    W = cam.expected_barrel_width_px(bottom_row=470)
    mask[:] = 0
    mask[440:470, int(320 - 0.3 * W):int(320 + 0.3 * W)] = io.BLUE          # 0.6 of a barrel wide for its bottom row, 30 px tall
    assert cam.expected_barrel_height_px(bottom_row=470) > 2 * 30
    log = []
    assert det.detect(mask, cam=cam, log=log) == []
    assert whys(log, "piece") == ["height"]                                  # refused by stage 1: not barrel-tall
    H = cam.expected_barrel_height_px(bottom_row=120)
    mask[:] = 0
    mask[120 - int(round(H)):120, 309:333] = io.BLUE                         # the same blob at a barrel's height passes the shape checks ...
    assert len(pieces(mask, cam)) == 1
    assert det.detect(mask, cam=cam) == []                                   # ... but a stripe (5.8 px here) could have been seen, so no box


def test_box_is_as_wide_as_the_body_not_the_stripe():
    """A stripe whose outer columns went dark must not make the box thinner than the barrel."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 100, 320, body=io.BLUE)
    x0, top, x1, bottom = truth
    r = CAM.barrel_rows(100)
    sy0, sy1 = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    trim = int(round(0.08 * (x1 - x0)))
    mask[sy0:sy1, x0:x0 + trim] = 0; mask[sy0:sy1, x1 - trim:x1] = 0      # the stripe's outer 8 % per side unlabeled (still a "full" stripe)
    stripes = stripes_of(mask)
    assert len(stripes) == 1 and (stripes[0].bbox[2] - stripes[0].bbox[0]) <= 0.86 * (x1 - x0)      # the stripe alone is narrow
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.BLUE
    assert abs(out[0].bbox[0] - x0) <= 2 and abs(out[0].bbox[2] - x1) <= 2


def test_body_width_cannot_stretch_into_a_touching_neighbour():
    """Two touching same-color barrels: each box stays about one barrel wide."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(100); W = r.width_px
    a = paint_barrel(mask, 100, 320 - W / 2, body=io.ORANGE)
    b = paint_barrel(mask, 100, 320 + W / 2, body=io.ORANGE)
    out = sorted(det.detect(mask, cam=CAM), key=lambda z: z.bbox[0])
    assert len(out) == 2
    for z, truth in zip(out, (a, b)):
        assert (z.bbox[2] - z.bbox[0]) <= 1.25 * W and abs((z.bbox[0] + z.bbox[2]) / 2 - (truth[0] + truth[2]) / 2) <= 0.15 * W


def test_stripe_cut_by_the_frame_edge_widens_into_the_edge():
    """A barrel half out of the frame on the right: the full box goes to the frame edge, not leftward."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(120)
    W = r.width_px
    truth = paint_barrel(mask, 120, 640 - W * 0.3)          # 30 % of the barrel inside the frame, the rest beyond x = 640
    out = det.detect(mask, cam=CAM)
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


def test_a_box_carries_what_it_was_read_from():
    """Each box knows its evidence (the box of the stripe, cap piece, band or slices it was read from) and the rule that
    drew it. The verify stages read that; nothing reads the reason log."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320)
    stripes, _ = det.find_stripes(mask, CAM)
    found, unplaced, lost = det.boxes_from_stripes(stripes, mask, CAM)
    assert len(found) == 1 and found[0].barrel.bbox == truth and found[0].rule == "whole_stripe"
    assert found[0].stripe is stripes[0] and found[0].evidence_box == stripes[0].bbox and unplaced == [] and lost == []
    piece = det.Found(found[0].barrel, "closeup")
    assert piece.evidence_box == truth                              # a stripeless piece is its own evidence


def test_log_names_the_refusing_test_and_never_changes_the_answer():
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(150)
    mask[int(r.top):int(r.bottom), int(320 - r.width_px / 2):int(320 + r.width_px / 2)] = io.ORANGE     # barrel-sized, no stripe
    log = []
    assert det.detect(mask, cam=CAM, log=log) == det.detect(mask, cam=CAM) == []
    assert any(e["stage"] == "piece" and e["why"] == "stripeless" and e["body"] == io.ORANGE for e in log)
    mask2 = np.zeros((480, 640), np.uint8); paint_barrel(mask2, 150, 320)
    log = []
    assert det.detect(mask2, cam=CAM, log=log) == det.detect(mask2, cam=CAM)
    assert whys(log, "barrel") == ["kept"]


# ---------------------------------------------------------------- a stripe in pieces; a barrel behind a barrel of the other color

def _close(box, truth, px=2):
    return all(abs(a - b) <= px for a, b in zip(box, truth))


def test_stripe_cut_by_a_pale_slit_is_one_stripe_with_stripe_join():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320)
    r = CAM.barrel_rows(150); W = truth[2] - truth[0]
    c = truth[0] + int(0.45 * W)
    mask[int(r.stripe_top) - 2:int(r.stripe_bottom) + 3, c:c + int(0.15 * W)] = 0       # a highlight 0.15 of a barrel wide across the stripe
    assert len(stripes_of(mask)) == 1                     # the two pieces are one stripe
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and _close(out[0].bbox, truth) and "occluded" not in out[0].flags


def test_stripe_under_a_washed_out_upper_body_is_one_stripe_with_stripe_join():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE)
    r = CAM.barrel_rows(150); W = truth[2] - truth[0]
    mask[truth[1]:int(round(r.stripe_top)), truth[0] + int(0.25 * W):truth[2] - int(0.25 * W)] = 0   # the upper body pale in the middle half
    out = det.detect(mask, cam=CAM)                                  # the stripe has body above it only at its two ends: two pieces, one stripe
    assert len(out) == 1 and out[0].color == io.BLUE and _close(out[0].bbox, truth)


def test_stripe_join_does_not_join_pieces_that_are_taller_than_wide():
    """Slivers of a body between specks are tall; a cut stripe's pieces are flat. Only flat pieces join (or pieces with
    body color over the whole gap between them)."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(150)
    x0, x1 = int(round(320 - r.width_px / 2)), int(round(320 + r.width_px / 2))
    mask[int(round(r.top)):int(round(r.bottom)), x0:x1] = io.BLUE            # a blue body, no stripe
    st, sb = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    for c in (x0 + 8, x0 + 24, x0 + 40):
        mask[st:sb, c:c + 5] = io.ORANGE                                      # three orange slivers 5 px wide, a stripe tall, 0.55 of a barrel together
    assert sb - st > 5
    stripes, narrow = det.find_stripes(mask, cam=CAM)
    assert len(stripes + narrow) >= 3 and all(s.bbox[2] - s.bbox[0] <= 5 for s in stripes + narrow)     # each sliver alone, none joined


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
    out = caps(mask, [right])
    assert len(out) == 1 and out[0].color == io.BLUE and {"occluded", "bottom_inferred"} <= out[0].flags
    assert out[0].bbox[:3] == (x0, top, x0 + W) and abs(out[0].bbox[3] - bottom) <= 1          # widened to a full barrel toward the hidden side
    below = Barrel(color=io.ORANGE, bbox=(x0 - 5, int(round(r.stripe_top)), x0 + 60, bottom + 20))   # a barrel below it only: no side is hidden
    log = []
    assert caps(mask, [below], log) == [] and [e["why"] for e in log] == ["narrow"]
    left = Barrel(color=io.ORANGE, bbox=(x0 - 60, top + 2, x0 + 5, bottom + 20))               # both sides hidden: a wedge between two barrels
    log = []
    assert caps(mask, [left, right], log) == [] and [e["why"] for e in log] == ["both_sides"]


def test_cap_uses_its_seen_bottom_when_it_agrees():
    from barrels.detect_types import Barrel
    mask, r, x0, n = _cap()
    top, bottom = int(round(r.top)), int(round(r.bottom))
    right = Barrel(color=io.ORANGE, bbox=(x0 + n - 5, top + 2, x0 + n + 60, bottom + 20))
    mask[int(round(r.stripe_bottom)):bottom - 5, x0:x0 + 8] = io.BLUE        # its lower body shows beside the front barrel and ends 5 px above the estimate
    out = caps(mask, [right])
    assert len(out) == 1 and out[0].bbox[3] == bottom - 5
    mask[int(round(r.stripe_bottom)):bottom + 40, x0:x0 + 8] = io.BLUE       # blue running on far below the estimate is not this barrel's bottom
    out = caps(mask, [right])
    assert out == [] or abs(out[0].bbox[3] - bottom) <= 1


def test_stripe_join_joins_nothing_wider_than_one_barrel():
    W = CAM.barrel_rows(150).width_px
    for gap in (0.0, 0.5):                                           # touching, and half a barrel apart: same color, same rows
        mask = np.zeros((480, 640), np.uint8)
        a = paint_barrel(mask, 150, 320 - (1 + gap) * W / 2 - 1, body=io.BLUE)
        b = paint_barrel(mask, 150, 320 + (1 + gap) * W / 2 + 1, body=io.BLUE)
        out = det.detect(mask, cam=CAM)
        assert len(out) == 2 and _close(out[0].bbox, a, 3) and _close(out[1].bbox, b, 3)       # two barrels, not one joined stripe
    mask = np.zeros((480, 640), np.uint8); truth = paint_barrel(mask, 150, 320)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].bbox == truth                    # and a whole stripe is what it was


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
        out = det.detect(mask, cam=CAM, log=log)
        # the back barrel's orange stripe joins the front barrel's orange body: too tall for a stripe, so no stripe finds it
        assert any(e["stage"] == "stripe" and e["why"] == "height" and e["body"] == io.BLUE for e in log)
        assert sorted(b.color for b in out) == [io.ORANGE, io.BLUE]
        b = next(b for b in out if b.color == io.BLUE)
        assert det.box_iou(b.bbox, back) > 0.9 and abs(b.bbox[3] - back[3]) <= 2      # full box, bottom from the cap's width
        assert {"occluded", "bottom_inferred"} <= b.flags and b.source == "det3"
        o = next(b for b in out if b.color == io.ORANGE)
        assert det.box_iou(o.bbox, front) > 0.9 and o.source == "det2" and "occluded" not in o.flags    # the front barrel keeps its box


def test_cap_needs_a_found_barrel_in_front_of_it():
    mask, back, front = _behind(0)
    r = CAM.barrel_rows(220)
    alone = np.zeros((480, 640), np.uint8)
    alone[back[1]:int(round(r.stripe_top)), back[0]:back[2]] = io.BLUE          # the same cap with nothing below it
    assert det.detect(alone, cam=CAM) == []
    lower = mask[front[1]:]
    lower[lower == io.BLUE] = 0                                                  # the front barrel loses its stripe: it is not found any more,
    assert det.detect(mask, cam=CAM) == []                                       # ... so the cap above it is not a barrel either


def test_tall_body_colored_thing_above_a_barrel_is_not_a_cap():
    mask = np.zeros((480, 640), np.uint8)
    front = paint_barrel(mask, 100, 320, body=io.ORANGE)                # a near barrel: its top is low in the picture
    r = CAM.barrel_rows(220)
    top, W = int(round(r.top)), r.width_px
    assert front[1] - top > 1.5 * (r.stripe_top - r.top)                # from a 22 cm barrel's top row down to the near barrel: far more than an upper body
    mask[top:front[1], int(320 - W / 2):int(320 + W / 2)] = io.BLUE     # blue of barrel width for that row, all the way down to the front barrel
    log = []
    out = det.detect(mask, cam=CAM, log=log)
    assert [b.color for b in out] == [io.ORANGE]
    assert any(e["stage"] == "cap" and e["why"] == "height" for e in log)


def test_cap_behind_changes_nothing_when_no_barrel_is_hidden():
    """Where no barrel is hidden behind another, the cap rule draws nothing: the boxes are the barrels painted."""
    W = CAM.barrel_rows(150).width_px
    scenes = []
    m = np.zeros((480, 640), np.uint8); paint_barrel(m, 150, 320); scenes.append((m, [io.ORANGE]))               # one barrel
    m = np.zeros((480, 640), np.uint8)                                                                           # orange, blue, orange touching
    for k, body in ((-1, io.ORANGE), (0, io.BLUE), (1, io.ORANGE)):
        paint_barrel(m, 150, 320 + k * (W + 1), body=body)
    scenes.append((m, [io.ORANGE, io.BLUE, io.ORANGE]))
    m = np.zeros((480, 640), np.uint8)                                                                           # same color behind (stripe shows)
    paint_barrel(m, 220, 350, body=io.ORANGE); paint_barrel(m, 150, 320, body=io.ORANGE); scenes.append((m, [io.ORANGE, io.ORANGE]))
    m = np.zeros((480, 640), np.uint8)                                                                           # a far barrel above a close-up
    r = CAM.barrel_rows(35); m[int(r.top):480, int(320 - r.width_px / 2):int(320 + r.width_px / 2)] = io.ORANGE
    paint_barrel(m, 300, 320, body=io.BLUE); scenes.append((m, [io.ORANGE, io.BLUE]))
    for m, colors in scenes:
        log = []
        out = det.detect(m, cam=CAM, log=log)
        assert sorted(b.color for b in out) == sorted(colors)
        assert "kept" not in whys(log, "cap") and not any(b.source == "det3" for b in out)
