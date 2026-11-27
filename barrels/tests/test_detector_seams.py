"""The second reading of a stripe, at its seams (``detector.read_at_seams``, ``detector.rest_of_barrel_agrees``; adopted
from experiments/2026-11-26_slack, rule D), on synthetic barrels. Its quality is judged by the experiment's numbers;
these tests say what the rule does and what it must not do.

A stripe too thin, or too small, by its own pixels is measured again from the seams when the barrel is seen whole: a
thin one by its width (eaten pixels given back) or by the rest of the barrel; a small one only by the rest of the
barrel, its top and bottom as seen."""
import dataclasses

import numpy as np
import pytest

from barrels import degrade as dg, detector as det, io
from test_detector import CAM, paint_barrel, whys


def detect(mask, log=None):
    return det.detect(mask, det.DetConfig(), CAM, log=log)


def _eaten(d_mm: int, px: int, x: int = 320):
    """An orange barrel at d_mm with px pixels eaten off every edge of every color."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, d_mm, x)
    return dg.damage(mask, [truth], dg.Damage(erode_px=px)), truth


def _sliver_in_a_slit(skin_rows: tuple[int, int] | None):
    """Skin (orange) above and below a slit, 150 px wide, and in the middle of the slit a blue sliver 4 rows tall and 0.63
    of a barrel long (the campus clip that the "seen whole" gate was written for). ``skin_rows``: how far the skin reaches
    above and below the slit; None = exactly as far as a barrel at that row would."""
    r = CAM.barrel_rows(250)
    mid, W = int(round(r.stripe_center)), int(round(r.width_px))
    top, bottom = (int(round(r.top)), int(round(r.bottom))) if skin_rows is None else (mid - 5 - skin_rows[0], mid + 5 + skin_rows[1])
    mask = np.zeros((480, 640), np.uint8)
    mask[top:mid - 5, 250:400] = io.ORANGE
    mask[mid + 5:bottom, 250:400] = io.ORANGE
    mask[mid - 2:mid + 2, 310:310 + int(0.63 * W)] = io.BLUE
    return mask


# ---------------------------------------------------------------- plain code: no switch

def test_the_seam_reading_is_plain_code_with_no_switch():
    """Adopted as rule D alone: no ``slack`` setting, and the code of the arms not adopted (A, B, C) is gone."""
    assert "slack" not in det.DetConfig().to_dict()
    for gone in ("area_floor", "_fits_well", "_seam_reading", "_rest_supports", "FITS_FILL"):
        assert not hasattr(det, gone)
    assert "marginal" not in {f.name for f in dataclasses.fields(det.Stripe)}


# ---------------------------------------------------------------- a stripe that passes by its own pixels is not read again

@pytest.mark.parametrize("d", [150, 250, 400, 600])
def test_a_stripe_that_passes_by_its_own_pixels_is_not_read_again(d):
    """Unharmed: the stripe is its own pixels' box (not the band between its bodies), it asks the verify step for
    min_area_px, and the barrel gets its box."""
    mask, truth = _eaten(d, 0)
    stripes, _ = det.find_stripes(mask, CAM)
    r = CAM.barrel_rows(d)
    assert len(stripes) == 1 and stripes[0].own_px is None
    ys = np.where(mask[:, truth[0]:truth[2]] == io.BLUE)[0]
    assert (stripes[0].bbox[1], stripes[0].bbox[3]) == (ys.min(), ys.max() + 1)
    out = detect(mask)
    assert len(out) == 1 and det.box_iou(out[0].bbox, truth) > 0.9


# ---------------------------------------------------------------- the area floor stays min_area_px

def _small_stripe(d_mm: int, keep_px: int = 4):
    """A barrel at d_mm of whose stripe only the left keep_px columns are painted."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, d_mm, 320)
    r = CAM.barrel_rows(d_mm)
    mask[int(round(r.stripe_top)):int(round(r.stripe_bottom)), truth[0] + keep_px:truth[2]] = 0
    return mask, truth


def test_a_small_stripe_is_still_refused_when_its_seams_eat_nothing():
    """A sliver of a stripe on a whole barrel: the rest of the barrel agrees, but nothing was eaten at the seams, so the
    pixels scaled by seam height / own height are still under min_area_px. The floor is not lowered."""
    for d, keep in ((600, 4), (300, 2)):
        mask, _ = _small_stripe(d, keep)
        log = []
        assert detect(mask, log) == [] and "area" in whys(log, "stripe")


def test_read_at_seams_scales_a_small_stripe_by_what_its_seams_ate():
    """Two pixels eaten off a barrel at 55 cm: 14 stripe pixels, under min_area_px, and the barrel's top and bottom where
    the row predicts them. The seams give the pixels back: the stripe passes, as the band between its two bodies."""
    mask, truth = _eaten(550, 2)
    stripes, _ = det.find_stripes(mask, CAM)
    assert len(stripes) == 1 and stripes[0].own_px is not None and stripes[0].own_px < det.DetConfig().min_area_px
    out = detect(mask)
    assert len(out) == 1 and det.box_iou(out[0].bbox, truth) > 0.7


def test_a_small_stripe_asks_the_verify_step_for_its_own_pixels():
    """The verify step asks a box for min_area_px pixels of its own once a nearer barrel is in the frame. A stripe admitted
    with fewer is asked for the pixels it has."""
    mask, truth = _eaten(550, 2)
    near = paint_barrel(mask, 200, 150)
    out = detect(mask)
    assert len(out) == 2
    assert any(det.box_iou(b.bbox, truth) > 0.7 for b in out) and any(det.box_iou(b.bbox, near) > 0.9 for b in out)


# ---------------------------------------------------------------- a thin stripe: read at the seams when the barrel is seen whole

def test_a_thin_stripe_is_read_at_the_seams_when_the_rest_of_the_barrel_agrees():
    """Two pixels eaten off every edge of a far barrel: the stripe is too thin by its own rows, and by its own columns
    just under 0.8 of the barrel (the old second reading was not asked). The body still ends where the stripe's row puts
    the top and the bottom: the rest of the barrel agrees."""
    mask, truth = _eaten(500, 2)
    stripes, _ = det.find_stripes(mask, CAM)
    s = stripes[0]
    assert (s.bbox[2] - s.bbox[0]) < det.DetConfig().stripe_full * CAM.barrel_rows(500).width_px
    at = det.BarrelAt._at_distance(CAM, 500)
    assert det.rest_of_barrel_agrees(io.ORANGE, s.bbox[0], s.bbox[2] - s.bbox[0], s.bbox[1], s.bbox[3], at, 0.0, mask, det.DetConfig())
    out = detect(mask)
    assert len(out) == 1 and out[0].color == io.ORANGE and det.box_iou(out[0].bbox, truth) > 0.6
    assert not {"top_inferred", "bottom_inferred"} & out[0].flags                 # the body walk starts at the body: both edges are seen


def test_read_at_seams_gives_back_the_eaten_pixels():
    mask, _ = _eaten(500, 2)
    sw = det.sandwiches(mask, CAM, det.DetConfig())[io.ORANGE]
    sel = sw.stripe & sw.above & sw.below
    ys = np.where(sel)[0]
    core = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
    height, eaten, y0, y1 = det.read_at_seams(sw, sel, core)
    r = CAM.barrel_rows(500)
    assert eaten == pytest.approx(2.0, abs=0.5) and height == pytest.approx(r.stripe_bottom - r.stripe_top, abs=1.0)
    assert y1 - y0 == pytest.approx(core + 4 * eaten, abs=1.0)                    # the band runs from body to body
    assert eaten <= det.SEAM_MAX_EATEN


def test_a_sliver_in_a_slit_is_refused():
    """The known false box of the second reading: thin and short, skin above and below. Whatever the skin's height, the
    sliver ends inside the skin on both sides, so no side is a barrel's own edge."""
    for skin in ((40, 40), None):
        log = []
        assert detect(_sliver_in_a_slit(skin), log) == [] and "height" in whys(log, "stripe")


def test_the_seams_must_still_give_a_stripes_height():
    """Two rows of blue in a gap four stripe heights tall between two orange things, one barrel tall together."""
    r = CAM.barrel_rows(150)
    Hs, W, mid = int(round(r.stripe_bottom - r.stripe_top)), int(round(r.width_px)), int(round(r.stripe_center))
    mask = np.zeros((480, 640), np.uint8)
    mask[int(round(r.top)):mid - 2 * Hs, 320 - W // 2:320 + W // 2] = io.ORANGE
    mask[mid + 2 * Hs:int(round(r.bottom)), 320 - W // 2:320 + W // 2] = io.ORANGE
    mask[mid - 1:mid + 1, 320 - W // 2:320 + W // 2] = io.BLUE
    assert detect(mask) == []


# ---------------------------------------------------------------- a floor missed by a pixel is not forgiven as such

def _thin_stripe(rows: int):
    """A barrel at 300 mm whose stripe is only `rows` rows tall (the floor is 4.05), body color right up to it."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 300, 320)
    r = CAM.barrel_rows(300)
    st, sb = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    mask[st:sb, truth[0]:truth[2]] = io.ORANGE
    mask[st + 3:st + 3 + rows, truth[0]:truth[2]] = io.BLUE
    return mask, truth


def test_a_thin_stripe_with_no_gap_at_its_seams_stays_thin():
    """Body right up to a stripe 3 rows tall: nothing was eaten, the seam height is the stripe's own, and it is under the
    floor. (Experiment arm C forgave one floor missed by a pixel; it was not adopted.)"""
    mask, _ = _thin_stripe(3)
    log = []
    assert detect(mask, log) == [] and "height" in whys(log, "stripe")


def test_a_thin_stripe_whose_barrel_is_not_where_its_row_says_stays_thin():
    mask, truth = _thin_stripe(3)
    mask[truth[1]:truth[1] + 8, :] = 0                                             # the top is not where the stripe's row puts it
    log = []
    assert detect(mask, log) == [] and "height" in whys(log, "stripe")


def test_two_rows_of_stripe_in_a_five_row_gap_are_too_thin():
    mask, truth = _thin_stripe(3)
    st = int(round(CAM.barrel_rows(300).stripe_top))
    mask[st + 2:st + 7, truth[0]:truth[2]] = 0                                     # a gap of 5 rows between the bodies ...
    mask[st + 3:st + 5, truth[0]:truth[2]] = io.BLUE                               # ... and 2 rows of stripe in it: (2 + 5) / 2 where 4.05 are asked
    log = []
    assert detect(mask, log) == [] and "height" in whys(log, "stripe")


# ---------------------------------------------------------------- a small stripe needs the rest of the barrel, as seen

def test_a_thin_stripe_with_enough_pixels_may_be_seen_whole_by_its_width():
    """The width reading, with the eaten pixels given back: a stripe 3 rows tall in a gap of 13 (2.5 px eaten at each
    edge) and 0.7 of a barrel wide (24 of 34 px), under stripe_full by its own columns, over it with 2 x 2.5 px given back. It lies in
    the middle of a body two barrels wide, so the rest of the barrel does not agree: the width alone lets it through."""
    r = CAM.barrel_rows(300)
    W, mid = r.width_px, int(round(r.stripe_center))
    mask = np.zeros((480, 640), np.uint8)
    x0, x1 = 320 - int(W), 320 + int(W)
    mask[int(round(r.top)):mid - 7, x0:x1] = io.ORANGE                            # two barrels wide: no side ends with the stripe
    mask[mid + 6:int(round(r.bottom)), x0:x1] = io.ORANGE
    xs0, xs1 = 320 - int(0.37 * W), 320 + int(0.37 * W)
    mask[mid - 1:mid + 2, xs0:xs1] = io.BLUE
    assert xs1 - xs0 < det.DetConfig().stripe_full * W <= xs1 - xs0 + 5
    stripes, _ = det.find_stripes(mask, CAM)
    assert len(stripes) == 1 and stripes[0].bbox[0] == xs0 and stripes[0].bbox[1] == mid - 7 and stripes[0].bbox[3] == mid + 6
    assert stripes[0].own_px is None                                               # enough pixels of its own


def test_a_small_wide_stripe_is_not_taken_on_its_width_alone():
    """A few stripe-colored pixels spread over a barrel's width between two blocks of body color that do not end where a
    barrel's top and bottom would: by its width it would be "seen whole"; the rest of the barrel says no."""
    r = CAM.barrel_rows(250)
    W, mid = int(round(r.width_px)), int(round(r.stripe_center))
    mask = np.zeros((480, 640), np.uint8)
    x0 = 320 - W // 2
    mask[mid - 30:mid - 3, x0:x0 + W] = io.ORANGE                                 # body-colored blocks taller than a barrel's halves
    mask[mid + 3:mid + 30, x0:x0 + W] = io.ORANGE
    for c in range(x0, x0 + W, 6):
        mask[mid - 1:mid + 1, c:c + 1] = io.BLUE                                  # 2 px every 6 columns: under 20 px in all
    assert detect(mask) == []
