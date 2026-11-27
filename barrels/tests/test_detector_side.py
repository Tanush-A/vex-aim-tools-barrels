"""The partly seen stripe and the second height reading, on synthetic barrels (their quality is judged by eval
numbers): a stripe narrower than 0.8 of its barrel is placed by what is seen of the barrel, and a side counts as hidden
only for a reason; a stripe too thin by its own rows is read at the seams too."""
import numpy as np

from barrels import degrade as dg, detector as det, io
from test_detector import CAM, CFG, _barrel_behind_a_slanted_edge, paint_barrel, whys


def _close(box, truth, px=2):
    return all(abs(a - b) <= px for a, b in zip(box, truth))


def _cut_straight(seen):
    """A blue barrel of which only the left `seen` of the width shows, cut by a straight upright edge that is not barrel-colored."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.BLUE)
    mask[:, truth[0] + int(round(seen * (truth[2] - truth[0]))):] = 0
    return mask, truth


# ---------------------------------------------------------------- the partly seen stripe

def test_body_showing_the_whole_width_gives_the_box_when_the_stripe_is_cut():
    """A highlight takes the right 55 % of the stripe; the body above and below is all there. The piece is a partly seen
    stripe, and the body joined to it is the box (not a box centred on the piece, a quarter barrel off)."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320)
    r = CAM.barrel_rows(150); W = truth[2] - truth[0]
    mask[int(round(r.stripe_top)) - 2:int(round(r.stripe_bottom)) + 2, truth[0] + int(0.45 * W):] = 0
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and _close(out[0].bbox, truth)


def test_slanted_occluder_the_lower_body_shows_the_width():
    """Campus occl_02 in small: 0.3 of the stripe shows, the lower body nearly all of the width (the edge slants)."""
    mask, truth = _barrel_behind_a_slanted_edge(seen_at_stripe=0.3, seen_at_bottom=0.95)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.BLUE and "occluded" in out[0].flags
    assert abs(out[0].bbox[0] - truth[0]) <= 2 and det.box_iou(out[0].bbox, truth) > 0.9


def test_outline_cut_on_one_side_widens_toward_that_side():
    """The stripe shows 0.3 of the width and the lower body 0.6: under 0.8, so a side must be hidden. On the left the
    body and the stripe end together (the barrel's own edge); on the right they end far apart: hidden there."""
    mask, truth = _barrel_behind_a_slanted_edge(seen_at_stripe=0.3, seen_at_bottom=0.6)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and "occluded" in out[0].flags
    assert abs(out[0].bbox[0] - truth[0]) <= 2 and abs(out[0].bbox[2] - truth[2]) <= 3      # a full barrel from the seen left edge
    mirrored = det.detect(mask[:, ::-1].copy(), cam=CAM)                                    # the same scene, left and right swapped
    assert len(mirrored) == 1 and abs(mirrored[0].bbox[2] - (640 - truth[0])) <= 2 and abs(mirrored[0].bbox[0] - (640 - truth[2])) <= 3


def test_body_running_into_a_same_colored_neighbour_still_says_where_the_stripe_is_cut():
    """The body joined to the stripe runs on into something of the same color (in the frames: a touching barrel's
    stripe), so it is wider than a barrel can be and cannot give the box. It still says which side is cut: on the left
    the body and the stripe end together (the barrel's own edge), on the right the body runs far past the end of the
    stripe. The box is a barrel wide from the left edge."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320)
    r = CAM.barrel_rows(150); W = truth[2] - truth[0]
    mask[int(round(r.stripe_top)) - 2:int(round(r.stripe_bottom)) + 2, truth[0] + int(0.45 * W):] = 0   # a highlight takes the stripe's right 55 %
    mask[truth[1]:truth[3], truth[2]:truth[2] + int(0.6 * W)] = io.ORANGE                               # an orange thing with no stripe touches its right side
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and "occluded" in out[0].flags
    assert abs(out[0].bbox[0] - truth[0]) <= 2 and abs(out[0].bbox[2] - truth[2]) <= 3
    mirrored = det.detect(mask[:, ::-1].copy(), cam=CAM)
    assert len(mirrored) == 1 and abs(mirrored[0].bbox[2] - (640 - truth[0])) <= 2 and abs(mirrored[0].bbox[0] - (640 - truth[2])) <= 3


def test_narrow_stripe_with_no_reason_gives_no_box():
    """Cut by a straight upright edge, the stripe and the body end together on both sides: nothing says which side the
    rest of the barrel is on. Under 0.4 of a barrel: no box. From 0.4: centred on what is seen."""
    mask, truth = _cut_straight(0.3)
    log = []
    assert det.detect(mask, cam=CAM, log=log) == []
    assert "side_unexplained" in whys(log, "barrel")
    mask, truth = _cut_straight(0.5)
    W = truth[2] - truth[0]
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and "occluded" in out[0].flags and abs((out[0].bbox[2] - out[0].bbox[0]) - W) <= 1
    assert abs((out[0].bbox[0] + out[0].bbox[2]) / 2 - (truth[0] + 0.25 * W)) <= 2          # one barrel wide, centred on the seen half


def test_frame_edge_is_a_reason():
    """A barrel with 0.3 of its width inside the frame: the box starts at the seen edge and runs into the frame edge."""
    mask = np.zeros((480, 640), np.uint8)
    W = CAM.barrel_rows(120).width_px
    truth = paint_barrel(mask, 120, 640 + 0.2 * W)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].bbox[2] == 640 and abs(out[0].bbox[0] - truth[0]) <= 2 and "truncated" in out[0].flags
    mirrored = det.detect(mask[:, ::-1].copy(), cam=CAM)
    assert len(mirrored) == 1 and mirrored[0].bbox[0] == 0 and abs(mirrored[0].bbox[2] - (640 - truth[0])) <= 2


def test_found_nearer_barrel_is_a_reason():
    """A barrel half behind a nearer one of the same color: its body joins the front barrel's (not trusted), so the
    outline says nothing; the found front barrel beside its stripe is the reason."""
    mask = np.zeros((480, 640), np.uint8)
    back = paint_barrel(mask, 220, 350, body=io.ORANGE)
    front = paint_barrel(mask, 150, 320, body=io.ORANGE)
    out = sorted(det.detect(mask, cam=CAM), key=lambda b: b.bbox[0])
    assert len(out) == 2 and _close(out[0].bbox, front)
    b = out[1]
    assert "occluded" in b.flags and abs(b.bbox[2] - back[2]) <= 2 and abs(b.bbox[0] - back[0]) <= 3     # the full box through the front barrel
    s = next(s for s in det.find_stripes(mask, CAM) if s.bbox[0] >= front[2] - 2)                        # the back barrel's stripe
    W = CAM.barrel_rows(220).width_px
    # the body says the same without the found barrel: it runs on into the front barrel on the left (cut there) and
    # ends with the stripe on the right (the barrel's own edge)
    alone = det._partly_seen(s, mask, W, back[1], back[3], back[3], CFG, found=())
    assert alone is not None and abs(alone[1] - back[2]) <= 2 and abs(alone[0] - back[0]) <= 3
    # the found barrel alone is a reason too: a mask that holds the stripe and no body at all gives the body nothing to say
    bare = np.zeros_like(mask)
    bare[s.bbox[1]:s.bbox[3], s.bbox[0]:s.bbox[2]] = io.BLUE
    front_b = out[0]
    assert det._partly_seen(s, bare, W, back[1], back[3], back[3], CFG, found=()) != det._partly_seen(s, bare, W, back[1], back[3], back[3], CFG, found=(front_b,))
    with_front = det._partly_seen(s, bare, W, back[1], back[3], back[3], CFG, found=(front_b,))
    assert with_front is not None and abs(with_front[1] - s.bbox[2]) <= 1 and with_front[1] - with_front[0] == int(round(W))


def test_side_hidden_changes_nothing_for_barrels_seen_whole():
    """Barrels seen whole never take the partly seen branch: each is one box, none flagged occluded."""
    W = CAM.barrel_rows(150).width_px
    scenes = []
    m = np.zeros((480, 640), np.uint8); paint_barrel(m, 150, 320); scenes.append((m, 1))
    m = np.zeros((480, 640), np.uint8)
    for k, body in ((-1, io.ORANGE), (0, io.BLUE), (1, io.ORANGE)):
        paint_barrel(m, 150, 320 + k * (W + 1), body=body)
    scenes.append((m, 3))
    m = np.zeros((480, 640), np.uint8)
    paint_barrel(m, 150, 320 - W / 2 - 1, body=io.BLUE); paint_barrel(m, 150, 320 + W / 2 + 1, body=io.BLUE); scenes.append((m, 2))
    scenes.append((np.zeros((480, 640), np.uint8), 0))
    for m, n in scenes:
        out = det.detect(m, cam=CAM)
        assert len(out) == n and not any("occluded" in b.flags for b in out)


def test_body_span_reads_the_body_joined_to_the_stripe():
    mask = np.zeros((480, 640), np.uint8)
    mask[100:110, 200:260] = io.ORANGE; mask[120:130, 210:240] = io.ORANGE      # body above (200..260) and below (210..240) a stripe at rows 110..120
    mask[100:110, 300:320] = io.ORANGE                                          # more orange far to the right: not joined
    assert det._body_span(mask, io.ORANGE, 215, 235, 100, 130, 110, 120) == (200, 260)
    assert det._body_span(mask, io.ORANGE, 215, 235, 100, 130, 110, 120, others=((240, 262),)) == (200, 240)   # a neighbour's stripe columns never count
    assert det._body_span(mask, io.ORANGE, 400, 420, 100, 130, 110, 120) is None


# ---------------------------------------------------------------- the second height reading, at the seams

def _far_barrel_with_eaten_edges(e=2):
    """A far orange barrel whose stripe is 6 to 7 px tall, with e px eaten off every edge of every color."""
    d = next(d for d in range(200, 600, 5) if 5.5 <= CAM.barrel_rows(d).stripe_bottom - CAM.barrel_rows(d).stripe_top <= 7.0)
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, d, 320)
    r = CAM.barrel_rows(d)
    return dg.damage(mask, [truth], dg.Damage(erode_px=e)), truth, r.stripe_bottom - r.stripe_top


def test_stripe_eaten_at_both_seams_is_read_at_the_seams():
    mask, truth, Hs = _far_barrel_with_eaten_edges(2)                             # 2 or 3 rows of stripe left where 6 to 7 are expected
    stripes = det.find_stripes(mask, CAM)
    x0, y0, x1, y1 = stripes[0].bbox
    ys = np.where(mask[y0:y1, x0:x1] == io.BLUE)[0]
    assert len(stripes) == 1 and np.percentile(ys, 90) - np.percentile(ys, 10) + 1 < CFG.stripe_h_min * Hs      # too thin by its own rows (the finder's measure)
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and det.box_iou(out[0].bbox, truth) > 0.7
    whole, truth, _ = _far_barrel_with_eaten_edges(0)
    out = det.detect(whole, cam=CAM)                                              # a stripe that passes by its own rows
    assert len(out) == 1 and det.box_iou(out[0].bbox, truth) > 0.9


def test_seam_height_is_not_asked_of_a_short_piece():
    """Thin because the seams were eaten, or short because partly hidden, not both. A thin piece under 0.8 of a barrel
    long is not read a second time (in a campus clip: a blue sliver between two fingers, skin above and below)."""
    mask, truth, _ = _far_barrel_with_eaten_edges(2)
    mask[:, truth[0] + int(round(0.6 * (truth[2] - truth[0]))):] = 0             # ... and only its left 0.6 shows
    log = []
    assert det.detect(mask, cam=CAM, log=log) == []
    assert any(e["stage"] == "stripe" and e["why"] == "height" and "seam_h" not in e for e in log)


def test_thin_line_in_a_tall_gap_is_not_a_stripe():
    """Two rows of blue in a gap four stripe heights tall between two orange things: the middle of the two readings is
    two stripe heights, still not a stripe."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(150)
    Hs = int(round(r.stripe_bottom - r.stripe_top)); W = int(round(r.width_px))
    mid = int(round(r.stripe_center))
    mask[mid - 2 * Hs - 20:mid - 2 * Hs, 320 - W // 2:320 + W // 2] = io.ORANGE
    mask[mid + 2 * Hs:mid + 2 * Hs + 20, 320 - W // 2:320 + W // 2] = io.ORANGE
    mask[mid - 1:mid + 1, 320 - W // 2:320 + W // 2] = io.BLUE
    log = []
    assert det.detect(mask, cam=CAM, log=log) == []
    assert any(e["stage"] == "stripe" and e["why"] == "height" and "seam_h" in e for e in log)


def test_seam_height_leaves_a_stripe_with_shadow_glued_to_it_alone():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 150, 320, body=io.ORANGE)
    r = CAM.barrel_rows(150)
    st, sb = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    mask[truth[1] + 4:st, truth[0]:truth[2]] = 0; mask[sb:truth[3] - 4, truth[0]:truth[2]] = 0     # both faces dark: a stripe of full height in a tall gap
    out = det.detect(mask, cam=CAM)
    assert len(out) == 1 and out[0].color == io.ORANGE and abs(out[0].bbox[3] - truth[3]) <= 3
