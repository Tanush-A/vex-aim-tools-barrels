"""nearmiss.py: loose colors painted only beside a barrel's partner color (experiment 2026-11-26_nearmiss).
Infrastructure tests on drawn pictures: what gets painted where, and that nothing else changes."""
import cv2
import numpy as np
import pytest

from barrels import detector as det
from barrels import geometry as geo
from barrels import hslabel as hl
from barrels import nearmiss as nm
from barrels import pipeline as pl
from barrels.io import BLUE, ORANGE, OTHER

CAM = geo.AIM_4A8B6118_BOXFIT
H, W = 480, 640
GRAY = (0, 10, 120)
S_ORANGE, S_BLUE = (8, 220, 180), (110, 200, 150)           # inside the strict ranges
L1_ORANGE = (15, 200, 180)                                  # hue 2 past the orange sector: level 1 and up
L2_BLUE = (110, 90, 150)                                    # S 23 under the blue floor: level 2 and up
OLIVE = (35, 45, 60)                                        # the gray-olive a blue stripe reads under a warm lamp: no ladder level but "anything"


@pytest.fixture(scope="module")
def model():
    return hl.adopted_model()


def canvas():
    img = np.empty((H, W, 3), np.uint8)
    img[:] = GRAY
    return img


def frame_of(hsv: np.ndarray) -> pl.Frame:
    f = pl.Frame.from_image(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    for a in (f.bgr, f.rgb, f.sat, f.val):
        a.setflags(write=False)                             # as judge.load_frame hands frames out
    return f


def barrel_rows(center_row=150.5):
    g = nm.stripe_geometry(CAM, center_row)[1]
    return (int(round(g.top)), int(round(g.stripe_top)), int(round(g.stripe_bottom)), int(round(g.bottom)), int(round(g.width_px)))


def draw_barrel(hsv, x0, body, stripe, center_row=150.5):
    """A barrel as a rectangle: body color with a stripe band where the geometry puts it. Returns its rows."""
    top, st, sb, bottom, w = barrel_rows(center_row)
    hsv[top:bottom, x0:x0 + w] = body
    hsv[st:sb, x0:x0 + w] = stripe
    return top, st, sb, bottom, w


# ---------------------------------------------------------------- loose colors

def test_ladder_is_nested_and_holds_the_strict_pixels(model):
    hsv = canvas()
    draw_barrel(hsv, 100, S_ORANGE, S_BLUE)
    hsv[300:320, 100:200] = L1_ORANGE
    hsv[300:320, 300:400] = L2_BLUE
    f = frame_of(hsv)
    strict = nm.strict_mask(f, model)
    for c in (ORANGE, BLUE):
        prev = strict == c
        for lvl in nm.LADDER[1:]:
            cur = nm.loose_class(f, model, c, lvl)
            assert not (prev & ~cur).any(), f"level {lvl.name} lost pixels of class {c}"
            prev = cur
    assert nm.loose_class(f, model, ORANGE, nm.LADDER[1])[310, 150] and strict[310, 150] == OTHER
    assert not nm.loose_class(f, model, BLUE, nm.LADDER[1])[310, 350]
    assert nm.loose_class(f, model, BLUE, nm.LADDER[2])[310, 350]
    with pytest.raises(ValueError):
        nm.loose_class(f, model, BLUE, nm.STRIPE_LADDER[nm.STRIPE_ANY])


def test_loose_class_keeps_the_horizon_gate(model):
    hsv = canvas()
    hsv[10:40, 100:200] = L2_BLUE
    assert not nm.loose_class(frame_of(hsv), model, BLUE, nm.LADDER[3]).any()


def test_config_refuses_bad_values():
    with pytest.raises(ValueError):
        nm.NearMissConfig(stripe_level=7)
    with pytest.raises(ValueError):
        nm.NearMissConfig(body_level=8)
    assert nm.STRIPE_LADDER[:6] == nm.BODY_LADDER[:6] == nm.LADDER
    with pytest.raises(ValueError):
        nm.NearMissConfig(bottom="anywhere")


# ---------------------------------------------------------------- the reference: hysteresis

def test_hysteresis_keeps_loose_joined_to_strict_only(model):
    hsv = canvas()
    hsv[200:230, 100:140] = S_ORANGE
    hsv[200:230, 140:170] = L1_ORANGE                       # touches the strict piece
    hsv[300:330, 400:440] = L1_ORANGE                       # alone
    f = frame_of(hsv)
    strict = nm.strict_mask(f, model)
    m = nm.hysteresis_mask(f, model, 1)
    assert (m[200:230, 140:170] == ORANGE).all()
    assert (m[300:330, 400:440] == OTHER).all()
    assert (m[strict != OTHER] == strict[strict != OTHER]).all()
    assert (nm.hysteresis_mask(f, model, 0) == strict).all()


def test_hysteresis_bottom_guard(model):
    hsv = canvas()
    hsv[200:230, 100:140] = S_ORANGE
    hsv[230:245, 100:140] = L1_ORANGE                       # under the strict piece (a reflection)
    hsv[190:200, 100:140] = L1_ORANGE                       # above it
    f = frame_of(hsv)
    plain = nm.hysteresis_mask(f, model, 1)
    guarded = nm.hysteresis_mask(f, model, 1, guard_bottom=True)
    assert (plain[230:245, 100:140] == ORANGE).all()
    assert (guarded[230:245, 100:140] == OTHER).all()
    assert (guarded[190:200, 100:140] == ORANGE).all()


# ---------------------------------------------------------------- geometry

def test_stripe_geometry_is_the_detectors():
    for row in (60.0, 76.0, 90.5, 150.5, 300.0, 470.0):
        a, b = nm.stripe_geometry(CAM, row), det._stripe_geometry(CAM, row)
        assert (a is None) == (b is None)
        if a is not None:
            assert a[0] == b[0] and a[1] == b[1]


def test_stripe_height_by_row():
    hs = nm.stripe_height_by_row(CAM, H)
    assert hs[60] == -1 and hs[76] == -1                    # above / at the horizon
    g = nm.stripe_geometry(CAM, 150.5)[1]
    assert hs[150] == pytest.approx(g.stripe_bottom - g.stripe_top)
    assert (np.diff(hs[hs > 0]) > 0).all()                  # nearer = lower in the picture = taller stripe


# ---------------------------------------------------------------- direction 1: the stripe slot

def test_stripe_slots_need_a_gap_of_stripe_height_between_two_pieces():
    hs = nm.stripe_height_by_row(CAM, H)
    top, st, sb, bottom, w = barrel_rows()
    body = np.zeros((H, W), bool)
    body[top:st, 100:100 + w] = True
    body[sb:bottom, 100:100 + w] = True
    slot = nm.stripe_slots(body, hs)
    assert slot[st:sb, 100:100 + w].all() and slot.sum() == (sb - st) * w
    tall = np.zeros((H, W), bool)                           # two pieces three stripe heights apart: not a stripe
    tall[top:st, 100:100 + w] = True
    tall[st + 3 * (sb - st):st + 5 * (sb - st), 100:100 + w] = True
    assert not nm.stripe_slots(tall, hs).any()
    thin = np.zeros((H, W), bool)                           # the piece below is two rows: not strong evidence
    thin[top:st, 100:100 + w] = True
    thin[sb:sb + 2, 100:100 + w] = True
    assert not nm.stripe_slots(thin, hs).any()
    one = np.zeros((H, W), bool)                            # body on one side only
    one[top:st, 100:100 + w] = True
    assert not nm.stripe_slots(one, hs).any()
    narrow = np.zeros((H, W), bool)                         # two columns wide: dropped
    narrow[top:st, 100:102] = True
    narrow[sb:bottom, 100:102] = True
    assert not nm.stripe_slots(narrow, hs).any()


def test_partner_paints_a_loose_stripe_between_strict_body(model):
    hsv = canvas()
    top, st, sb, bottom, w = draw_barrel(hsv, 100, S_ORANGE, L2_BLUE)
    hsv[300:320, 300:400] = L2_BLUE                         # the same loose blue with no body around it
    f = frame_of(hsv)
    strict = nm.strict_mask(f, model)
    assert (strict[st:sb, 100:100 + w] == OTHER).all()
    m1, _ = nm.partner_mask(f, model, nm.NearMissConfig(stripe_level=1), CAM)
    assert (m1 == strict).all()                             # level 1 does not reach it
    m2, info = nm.partner_mask(f, model, nm.NearMissConfig(stripe_level=2), CAM)
    assert (m2[st:sb, 100:100 + w] == BLUE).all()
    assert (m2[300:320, 300:400] == OTHER).all()
    assert info["stripe_px"][BLUE] == (sb - st) * w
    changed = m2 != strict
    assert (strict[changed] == OTHER).all()                 # paint is only added


def test_anything_level_paints_a_gray_stripe_but_never_body_color(model):
    hsv = canvas()
    top, st, sb, bottom, w = draw_barrel(hsv, 100, S_ORANGE, OLIVE)
    draw_barrel(hsv, 300, S_ORANGE, L1_ORANGE)              # the "gap" is loose ORANGE: clearly the body's own color
    f = frame_of(hsv)
    m5, _ = nm.partner_mask(f, model, nm.NearMissConfig(stripe_level=5), CAM)
    assert (m5[st:sb, 100:100 + w] == OTHER).all()          # no ladder level reaches gray-olive
    m, _ = nm.partner_mask(f, model, nm.NearMissConfig(stripe_level=nm.STRIPE_ANY), CAM)
    assert (m[st:sb, 100:100 + w] == BLUE).all()
    assert (m[st:sb, 300:300 + w] == OTHER).all()


def test_a_found_barrel_from_a_loose_stripe(model):
    hsv = canvas()
    draw_barrel(hsv, 100, S_ORANGE, L2_BLUE)
    f = frame_of(hsv)
    assert not [b for b in det.detect(nm.strict_mask(f, model), det.DetConfig(), CAM) if "no_stripe" not in b.flags and b.source == "det2"]
    m, _ = nm.partner_mask(f, model, nm.NearMissConfig(stripe_level=2), CAM)
    found = det.detect(m, det.DetConfig(), CAM)
    assert len(found) == 1 and found[0].color == ORANGE and found[0].source == "det2"


# ---------------------------------------------------------------- direction 2: the body around a band

def test_stripe_bands_by_size(model):
    hsv = canvas()
    top, st, sb, bottom, w = barrel_rows()
    hsv[st:sb, 100:100 + w] = S_ORANGE                      # a stripe-sized band
    hsv[st:st + 4 * (sb - st), 300:300 + w] = S_ORANGE      # four stripe heights tall
    hsv[st:sb, 500:500 + w // 4] = S_ORANGE                 # a quarter of a barrel wide
    strict = nm.strict_mask(frame_of(hsv), model)
    bands, lab = nm.stripe_bands(strict, ORANGE, CAM)
    assert [b.bbox for b in bands] == [(100, st, 100 + w, sb)]
    assert (lab[st:sb, 100:100 + w] == bands[0].label).all()
    assert bands[0].top == pytest.approx(nm.stripe_geometry(CAM, bands[0].center_row)[1].top)


def test_a_band_with_its_own_color_above_is_not_a_stripe(model):
    hsv = canvas()
    top, st, sb, bottom, w = draw_barrel(hsv, 100, S_ORANGE, GRAY)     # an orange barrel whose stripe is not painted
    strict = nm.strict_mask(frame_of(hsv), model)
    assert nm.stripe_bands(strict, ORANGE, CAM)[0] == []    # its lower body has stripe size, but orange is above the gap


def test_partner_paints_loose_body_around_a_strict_stripe(model):
    hsv = canvas()
    top, st, sb, bottom, w = draw_barrel(hsv, 100, L2_BLUE, S_ORANGE)
    hsv[bottom:bottom + 30, 100:100 + w] = L2_BLUE          # the same loose blue under the barrel (a reflection)
    hsv[top:bottom, 400:400 + w] = L2_BLUE                  # loose blue with no stripe
    f = frame_of(hsv)
    strict = nm.strict_mask(f, model)
    assert (strict[top:st, 100:100 + w] == OTHER).all()
    m, info = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2), CAM)
    assert (m[top:st, 100:100 + w] == BLUE).all() and (m[sb:bottom, 100:100 + w] == BLUE).all()
    assert (m[bottom:, 100:100 + w] == OTHER).all()         # nothing below the bottom the stripe's row predicts
    assert (m[top:bottom, 400:400 + w] == OTHER).all()
    assert info["bands"][BLUE] == 1
    free, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, bottom="free"), CAM)
    assert (free[bottom:bottom + 4, 100:100 + w] == BLUE).all()         # unprotected: paint runs on under the barrel
    found = det.detect(m, det.DetConfig(), CAM)
    assert len(found) == 1 and found[0].color == BLUE and found[0].bbox[3] == bottom


def test_strict_bottom_mode_stops_at_the_strict_body(model):
    hsv = canvas()
    top, st, sb, bottom, w = draw_barrel(hsv, 100, L2_BLUE, S_ORANGE)
    hsv[sb:sb + 5, 100:100 + w] = S_BLUE                    # five rows of strict body under the stripe
    f = frame_of(hsv)
    strict_mode, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, bottom="strict"), CAM)
    pred_mode, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, bottom="pred"), CAM)
    assert (strict_mode[sb + 5:bottom, 100:100 + w] == OTHER).all()
    assert (pred_mode[sb + 5:bottom, 100:100 + w] == BLUE).all()
    assert (strict_mode[top:st, 100:100 + w] == BLUE).all()             # no strict body above: filled to the predicted top


def test_strict_mode_protects_the_top_too(model):
    hsv = canvas()
    top, st, sb, bottom, w = draw_barrel(hsv, 100, L2_BLUE, S_ORANGE)
    hsv[st - 5:st, 100:100 + w] = S_BLUE                    # five rows of strict body above the stripe
    hsv[top - 20:top, 100:100 + w] = L2_BLUE                # loose blue behind the barrel, right above it
    f = frame_of(hsv)
    # runs_on off: this test is about the three edge modes alone (with it on, nothing is painted above this band in any mode)
    strict_mode, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, bottom="strict", runs_on=0.0), CAM)
    pred_mode, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, bottom="pred", runs_on=0.0), CAM)
    free_mode, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, bottom="free", runs_on=0.0), CAM)
    guarded, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, bottom="pred"), CAM)
    assert (guarded[:st - 5, 100:100 + w] == OTHER).all()
    assert (strict_mode[:st - 5, 100:100 + w] == OTHER).all()
    assert (pred_mode[top:st - 5, 100:100 + w] == BLUE).all() and (pred_mode[:top, 100:100 + w] == OTHER).all()
    assert (free_mode[top - 4:top, 100:100 + w] == BLUE).all()


def test_the_body_of_an_own_colored_barrel_is_not_a_stripe(model):
    hsv = canvas()
    top, st, sb, bottom, w = draw_barrel(hsv, 100, S_ORANGE, S_BLUE, center_row=100.5)      # a far orange barrel, well painted
    hsv[top - 30:top, 80:140] = L2_BLUE                     # a loose-blue wall behind it, right above its top
    f = frame_of(hsv)
    strict = nm.strict_mask(f, model)
    assert nm.stripe_bands(strict, ORANGE, CAM, nm.NearMissConfig(own_max=1.0))[0] == []    # refused by the slot rule alone
    m, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, bottom="free"), CAM)
    assert (m == strict).all()


def test_loose_body_must_start_at_the_band(model):
    hsv = canvas()
    top, st, sb, bottom, w = barrel_rows()
    hsv[st:sb, 100:100 + w] = S_ORANGE
    hsv[top:st - 8, 100:100 + w] = L2_BLUE                  # loose blue in the window, but eight rows away from the band
    m, _ = nm.partner_mask(frame_of(hsv), model, nm.NearMissConfig(body_level=2), CAM)
    assert (m[top:st - 8, 100:100 + w] == OTHER).all()


def test_body_color_that_runs_on_above_the_top_is_background(model):
    hsv = canvas()
    top, st, sb, bottom, w = barrel_rows()
    hsv[st:sb, 100:100 + w] = S_ORANGE                      # a stripe-sized orange band ...
    hsv[60:st, 60:200] = L2_BLUE                            # ... in front of a loose-blue wall that goes on far above the predicted top
    hsv[sb:bottom, 100:100 + w] = L2_BLUE
    f = frame_of(hsv)
    m, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2), CAM)
    assert (m[:st] == OTHER).all()                          # nothing above the band
    assert (m[sb:bottom, 100:100 + w] == BLUE).all()        # below it the paint completes a body
    off, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, runs_on=0.0), CAM)
    assert (off[top:st, 100:100 + w] == BLUE).all()


def test_loose_paint_must_complete_a_body(model):
    hsv = canvas()
    top, st, sb, bottom, w = barrel_rows()
    hsv[st:sb, 100:100 + w] = S_ORANGE
    hsv[st - 6:st, 100:100 + w // 4] = L2_BLUE              # a scrap of loose blue above the band: a tenth of an upper body
    hsv[sb:bottom, 100:100 + w] = L2_BLUE                   # a whole lower body
    f = frame_of(hsv)
    m, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2), CAM)
    assert (m[:st] == OTHER).all() and (m[sb:bottom, 100:100 + w] == BLUE).all()
    off, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=2, cover_min=0.0), CAM)
    assert (off[st - 6:st, 100:100 + w // 4] == BLUE).all()


def test_anything_body_fills_the_predicted_box_in_the_bands_columns(model):
    hsv = canvas()
    top, st, sb, bottom, w = barrel_rows()
    hsv[st:sb, 100:100 + w] = S_ORANGE
    m, _ = nm.partner_mask(frame_of(hsv), model, nm.NearMissConfig(body_level=nm.BODY_ANY), CAM)
    assert (m[top:st, 100:100 + w] == BLUE).all() and (m[sb:bottom, 100:100 + w] == BLUE).all()
    assert (m[:, :100] == OTHER).all() and (m[:, 100 + w:] == OTHER).all() and (m[bottom:] == OTHER).all()


def test_dark_level_paints_a_body_darker_than_the_ground(model):
    hsv = canvas()                                          # the ground: brightness 120
    top, st, sb, bottom, w = draw_barrel(hsv, 100, OLIVE, S_ORANGE)       # a gray-olive body, brightness 60: half the ground's
    draw_barrel(hsv, 300, (35, 45, 100), S_ORANGE)          # the same, brightness 100: not clearly darker
    f = frame_of(hsv)
    m5, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=5), CAM)
    assert (m5 == nm.strict_mask(f, model)).all()           # no color range reaches gray-olive
    m, _ = nm.partner_mask(f, model, nm.NearMissConfig(body_level=nm.BODY_DARK), CAM)
    assert (m[top:st, 100:100 + w] == BLUE).all() and (m[sb:bottom, 100:100 + w] == BLUE).all()
    assert (m[:, 300:300 + w] != BLUE).all()
    assert (m[:, :100] == OTHER).all() and (m[bottom:] == OTHER).all()
    found = det.detect(m, det.DetConfig(), CAM)
    assert len(found) == 1 and found[0].color == BLUE


def test_ground_value(model):
    hsv = canvas()
    top, st, sb, bottom, w = draw_barrel(hsv, 100, OLIVE, S_ORANGE)
    hsv[:, 100 + w:] = (0, 10, 200)                         # a brighter ground on the right
    f = frame_of(hsv)
    strict = nm.strict_mask(f, model)
    band = nm.stripe_bands(strict, ORANGE, CAM)[0][0]
    assert 118 <= nm.ground_value(f.val, strict, band) <= 202           # left strip 120, right strip 200: the median is one of them or between
    hsv2 = canvas()
    draw_barrel(hsv2, 0, OLIVE, S_ORANGE)                   # at the frame's left edge: only the right strip exists
    f2 = frame_of(hsv2)
    s2 = nm.strict_mask(f2, model)
    assert nm.ground_value(f2.val, s2, nm.stripe_bands(s2, ORANGE, CAM)[0][0]) == pytest.approx(120, abs=2)


def test_the_picture_is_only_read_and_strict_paint_never_changes(model):
    hsv = canvas()
    draw_barrel(hsv, 100, S_ORANGE, L2_BLUE)
    draw_barrel(hsv, 300, L2_BLUE, S_ORANGE)
    draw_barrel(hsv, 450, S_BLUE, S_ORANGE, center_row=250.5)
    f = frame_of(hsv)
    before = f.bgr.copy()
    strict = nm.strict_mask(f, model)
    for cfg in (nm.NearMissConfig(s, b, mode) for s in (0, 2, nm.STRIPE_ANY) for b in (0, 2, nm.BODY_DARK, nm.BODY_ANY) for mode in nm.BOTTOM_MODES):
        m, _ = nm.partner_mask(f, model, cfg, CAM)
        assert (m[strict != OTHER] == strict[strict != OTHER]).all()
    assert (nm.partner_mask(f, model, nm.NearMissConfig(), CAM)[0] == strict).all()         # both directions off = the fixed mask
    assert (f.bgr == before).all()
