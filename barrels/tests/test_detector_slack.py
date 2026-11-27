"""The slack experiment (``DetConfig.slack``, off by default; experiments/2026-11-26_slack), on synthetic barrels. Its
quality is judged by the experiment's numbers; these tests say what each letter does and what it must not do.
A: the stripe's area floor scales with the barrel. B: a thin or small stripe is read at the seams when the barrel is
seen whole, by the stripe's width or by the rest of the barrel. C: one size floor missed by a pixel is forgiven when
the rest fits."""
import dataclasses

import numpy as np
import pytest

from barrels import degrade as dg, detector as det, io
from test_detector import CAM, paint_barrel, whys


def cfg(letters: str) -> det.DetConfig:
    return dataclasses.replace(det.DetConfig(), slack=letters)


def detect(mask, letters: str = "", log=None):
    return det.detect(mask, cfg(letters), CAM, log=log)


def _eaten(d_mm: int, px: int):
    """An orange barrel at d_mm with px pixels eaten off every edge of every color."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, d_mm, 320)
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


# ---------------------------------------------------------------- the flag

def test_slack_is_off_by_default_and_takes_only_its_letters():
    assert det.DetConfig().slack == ""
    for letters in ("A", "B", "C", "AB", "ABC"):
        assert cfg(letters).slack == letters
    for bad in ("E", "true", "a"):
        with pytest.raises(ValueError):
            cfg(bad)


@pytest.mark.parametrize("letters", ["A", "B", "C", "ABC"])
def test_slack_changes_nothing_on_a_barrel_that_passes_by_its_own_pixels(letters):
    for d in (150, 250, 400, 600):
        mask, _ = _eaten(d, 0)
        assert detect(mask, letters) == detect(mask)


# ---------------------------------------------------------------- A: the area floor scales with the barrel

def test_area_floor_is_a_share_of_the_predicted_stripe_and_never_above_todays():
    for d in (150, 300, 600):
        at = det.BarrelAt._at_distance(CAM, d)
        assert det.area_floor(at, cfg("")) == 20                                   # off: the fixed floor
        assert det.area_floor(at, cfg("A")) == pytest.approx(min(20, 0.45 * 0.4 * at.W * at.Hs))
    assert det.area_floor(det.BarrelAt._at_distance(CAM, 300), cfg("A")) == 20     # near: nothing changes
    assert 12 < det.area_floor(det.BarrelAt._at_distance(CAM, 600), cfg("A")) < 16  # far: 18 % of the predicted stripe


def _small_stripe(d_mm: int, keep_px: int = 4):
    """A barrel at d_mm of whose stripe only the left keep_px columns are painted."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, d_mm, 320)
    r = CAM.barrel_rows(d_mm)
    mask[int(round(r.stripe_top)):int(round(r.stripe_bottom)), truth[0] + keep_px:truth[2]] = 0
    return mask, truth


def test_A_admits_a_small_stripe_far_away_and_not_nearby():
    mask, truth = _small_stripe(600)                                               # 16 px of stripe where 14 are asked at that distance
    log = []
    assert detect(mask, "", log) == [] and "area" in whys(log, "stripe")
    out = detect(mask, "A")
    assert len(out) == 1 and det.box_iou(out[0].bbox, truth) > 0.9
    near, _ = _small_stripe(300, keep_px=2)                                        # 18 px where 20 are asked: A changes nothing here
    assert detect(near, "A") == detect(near) == []


def test_a_small_stripe_is_not_dropped_by_the_verify_step_for_being_small():
    """The verify step asks a box for 20 pixels of its own once a nearer barrel is in the frame. A stripe admitted
    with a smaller floor is asked for that floor."""
    mask, truth = _small_stripe(600)
    near = paint_barrel(mask, 200, 150)
    out = detect(mask, "A")
    assert len(out) == 2 and {det.box_iou(b.bbox, truth) > 0.9 for b in out} == {True, False} and any(det.box_iou(b.bbox, near) > 0.9 for b in out)
    assert len(detect(mask)) == 1


# ---------------------------------------------------------------- B: read at the seams when the barrel is seen whole

def test_B_reads_a_thin_stripe_at_the_seams_when_the_rest_of_the_barrel_supports_it():
    """Two pixels eaten off every edge of a far barrel: the stripe is too thin by its own rows, and too narrow (under 0.8
    of the barrel) for today's second reading. The body still ends where the stripe's row puts the top and the bottom."""
    mask, truth = _eaten(500, 2)
    log = []
    assert detect(mask, "", log) == [] and "height" in whys(log, "stripe")
    out = detect(mask, "B")
    assert len(out) == 1 and out[0].color == io.ORANGE and det.box_iou(out[0].bbox, truth) > 0.6
    assert not {"top_inferred", "bottom_inferred"} & out[0].flags                 # the body walk starts at the body: both edges are seen


def test_B_seam_reading_gives_back_the_eaten_pixels():
    mask, _ = _eaten(500, 2)
    sw = det.sandwiches(mask, CAM, det.DetConfig())[io.ORANGE]
    sel = sw.stripe & sw.above & sw.below
    ys = np.where(sel)[0]
    core = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
    height, eaten, y0, y1 = det._seam_reading(sw, sel, core)
    r = CAM.barrel_rows(500)
    assert eaten == pytest.approx(2.0, abs=0.5) and height == pytest.approx(r.stripe_bottom - r.stripe_top, abs=1.0)
    assert y1 - y0 == pytest.approx(core + 4 * eaten, abs=1.0)                    # the band runs from body to body


def test_B_refuses_a_sliver_in_a_slit():
    """The known false box of the second reading: thin and short, skin above and below. Whatever the skin's height, the
    sliver ends inside the skin on both sides, so no side is a barrel's own edge."""
    for skin in ((40, 40), None):
        log = []
        assert detect(_sliver_in_a_slit(skin), "B", log) == [] and "height" in whys(log, "stripe")


def test_B_still_wants_a_stripes_height_at_the_seams():
    """Two rows of blue in a gap four stripe heights tall between two orange things, one barrel tall together."""
    r = CAM.barrel_rows(150)
    Hs, W, mid = int(round(r.stripe_bottom - r.stripe_top)), int(round(r.width_px)), int(round(r.stripe_center))
    mask = np.zeros((480, 640), np.uint8)
    mask[int(round(r.top)):mid - 2 * Hs, 320 - W // 2:320 + W // 2] = io.ORANGE
    mask[mid + 2 * Hs:int(round(r.bottom)), 320 - W // 2:320 + W // 2] = io.ORANGE
    mask[mid - 1:mid + 1, 320 - W // 2:320 + W // 2] = io.BLUE
    assert detect(mask, "B") == []


# ---------------------------------------------------------------- C: one floor missed by a pixel

def _thin_stripe(rows: int):
    """A barrel at 300 mm whose stripe is only `rows` rows tall (the floor is 4.05), body color right up to it."""
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 300, 320)
    r = CAM.barrel_rows(300)
    st, sb = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    mask[st:sb, truth[0]:truth[2]] = io.ORANGE
    mask[st + 3:st + 3 + rows, truth[0]:truth[2]] = io.BLUE
    return mask, truth


def test_C_forgives_one_floor_missed_by_a_pixel_when_the_rest_fits():
    mask, truth = _thin_stripe(3)
    log = []
    assert detect(mask, "", log) == [] and "height" in whys(log, "stripe")
    out = detect(mask, "C")
    assert len(out) == 1 and out[0].bbox == truth


def test_C_does_not_forgive_when_the_rest_does_not_fit():
    mask, truth = _thin_stripe(3)
    mask[truth[1]:truth[1] + 8, :] = 0                                             # the top is not where the stripe's row puts it
    log = []
    assert detect(mask, "C", log) == [] and "marginal" in whys(log, "barrel")


def test_C_does_not_forgive_more_than_a_pixel_on_each_edge():
    mask, truth = _thin_stripe(3)
    st = int(round(CAM.barrel_rows(300).stripe_top))
    mask[st + 2:st + 7, truth[0]:truth[2]] = 0                                     # a gap of 5 rows between the bodies ...
    mask[st + 3:st + 5, truth[0]:truth[2]] = io.BLUE                               # ... and 2 rows of stripe in it: 2 + 2 where 4.05 are asked
    log = []
    assert detect(mask, "C", log) == [] and "height" in whys(log, "stripe")


# ---------------------------------------------------------------- D (round 2): a small stripe needs the rest of the barrel, as seen

def test_D_reads_a_thin_stripe_like_B():
    mask, truth = _eaten(500, 2)
    assert detect(mask, "D") == detect(mask, "B") and len(detect(mask, "D")) == 1


def test_D_does_not_take_a_small_wide_stripe_on_its_width_alone():
    """A few stripe-colored pixels spread over a barrel's width between two blocks of body color that do not end where a
    barrel's top and bottom would: B reads it as seen whole by its width; D asks the rest of the barrel and says no."""
    r = CAM.barrel_rows(250)
    W, mid = int(round(r.width_px)), int(round(r.stripe_center))
    mask = np.zeros((480, 640), np.uint8)
    x0 = 320 - W // 2
    mask[mid - 30:mid - 3, x0:x0 + W] = io.ORANGE                                 # body-colored blocks taller than a barrel's halves
    mask[mid + 3:mid + 30, x0:x0 + W] = io.ORANGE
    for c in range(x0, x0 + W, 6):
        mask[mid - 1:mid + 1, c:c + 1] = io.BLUE                                  # 2 px every 6 columns: under 20 px in all
    assert detect(mask, "D") == []
