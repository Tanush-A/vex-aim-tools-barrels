"""placecal: a color setting from ONE frame and its boxes (an analysis helper; nothing calls it by default).
Synthetic frames and a fake evaluator; no data files except the adopted model's config."""
import cv2
import numpy as np
import pytest

from barrels import hslabel as hl, hsrange as hx, pipeline as pl, placecal as pc

ADOPTED = {"orange_h_lo": 3, "orange_h_hi": 13, "orange_s_lo": 140, "blue_h_lo": 103, "blue_h_hi": 119, "blue_s_lo": 113}
ORANGE_HSV, BLUE_HSV, GRAY_HSV = (8, 220, 200), (108, 230, 150), (0, 0, 200)


def bgr_of(hsv) -> np.ndarray:
    return cv2.cvtColor(np.uint8([[list(hsv)]]), cv2.COLOR_HSV2BGR)[0, 0]


def paint_barrel(img, box, body_hsv, stripe_hsv) -> None:
    x0, y0, x1, y1 = box
    h = y1 - y0
    img[y0:y1, x0:x1] = bgr_of(body_hsv)
    img[y0 + int(0.42 * h):y0 + int(0.66 * h), x0:x1] = bgr_of(stripe_hsv)


def scene(orange_box=(100, 200, 180, 290), blue_box=(300, 200, 380, 290), blue_hsv=BLUE_HSV):
    img = np.empty((480, 640, 3), np.uint8)
    img[:] = bgr_of(GRAY_HSV)
    boxes = []
    if orange_box:
        paint_barrel(img, orange_box, ORANGE_HSV, blue_hsv)
        boxes.append({"bbox": list(orange_box), "color": "orange", "flags": []})
    if blue_box:
        paint_barrel(img, blue_box, blue_hsv, ORANGE_HSV)
        boxes.append({"bbox": list(blue_box), "color": "blue", "flags": []})
    return img, boxes


@pytest.fixture(scope="module")
def base():
    return hl.adopted_model()


# ---------------------------------------------------------------- zones

def test_zones_put_body_and_stripe_rows_in_the_central_half():
    z = pc.zones((480, 640), [{"bbox": [100, 100, 200, 200], "color": "orange", "flags": []}], row0=50)
    assert z.used == 1 and z.skipped == 0
    assert z.pos["orange"][120, 150] and z.pos["orange"][180, 150]          # 20 % and 80 % of the height: body
    assert not z.pos["orange"][155, 150] and z.pos["blue"][155, 150]        # 55 %: the stripe is the other color
    assert not z.pos["orange"][142, 150] and not z.pos["blue"][142, 150]    # 42 %: the seam belongs to nobody
    assert not z.pos["orange"][120, 110] and not z.pos["orange"][120, 190]  # outside the central half of the width
    assert not z.pos["orange"][102, 150]                                    # the top 12 % may hold table
    assert int(z.pos["orange"].sum()) == (23 + 18) * 50 and int(z.pos["blue"].sum()) == 10 * 50


def test_outside_starts_a_pad_away_and_below_the_horizon_row():
    z = pc.zones((480, 640), [{"bbox": [100, 100, 200, 200], "color": "orange", "flags": []}], row0=50)
    assert not z.outside[98, 150] and not z.outside[203, 150] and not z.outside[150, 97]
    assert z.outside[205, 150] and z.outside[150, 95] and z.outside[300, 400]
    assert not z.outside[49, 400] and z.outside[50, 400]
    z2 = pc.zones((480, 640), [{"bbox": [100, 20, 200, 120], "color": "blue", "flags": []}], row0=50)
    assert not z2.pos["blue"][:50].any() and not z2.pos["orange"][:50].any()


@pytest.mark.parametrize("flag", pc.SKIP_FLAGS)
def test_a_flagged_box_gives_no_zone_but_is_not_outside(flag):
    z = pc.zones((480, 640), [{"bbox": [100, 100, 200, 200], "color": "orange", "flags": [flag]}], row0=0)
    assert z.used == 0 and z.skipped == 1
    assert not z.pos["orange"].any() and not z.pos["blue"].any()
    assert not z.outside[150, 150] and z.outside[300, 300]


def test_pixels_claimed_by_both_colors_belong_to_nobody():
    box = [100, 100, 200, 200]
    z = pc.zones((480, 640), [{"bbox": box, "color": "orange", "flags": []}, {"bbox": box, "color": "blue", "flags": []}])
    assert not z.pos["orange"].any() and not z.pos["blue"].any()


# ---------------------------------------------------------------- the net rectangle

def test_net_rect_is_the_exact_optimum():
    hin, hout = np.zeros((180, 256), np.int64), np.zeros((180, 256), np.int64)
    hin[40, 200], hin[42, 180] = 100, 50
    hout[41, 100], hout[41, 190] = 500, 10
    assert pc.net_rect(hin, hout) == (40, 42, 180)                  # 150 barrel pixels for 10 outside
    assert pc.net_rect(hin, hout, w_out=20.0) == (40, 40, 200)      # outside costs 200 now: one hue, and the higher floor on a tie
    assert pc.net_rect(hin, hout, lo=41, hi=179) == (42, 42, 180)   # the span is respected


def test_net_rect_with_nothing_to_gain_is_none():
    z = np.zeros((180, 256), np.int64)
    assert pc.net_rect(z, z) is None
    hin, hout = z.copy(), z.copy()
    hin[40, 200], hout[40, 200] = 5, 9
    assert pc.net_rect(hin, hout) is None


# ---------------------------------------------------------------- the net setting of a frame

def test_net_setting_finds_both_colors_and_changes_no_pixel(base):
    img, boxes = scene()
    before = img.copy()
    frame = pl.Frame.from_image(img)
    t = pc.net_setting(frame, boxes, base, ADOPTED)
    assert np.array_equal(img, before)
    hs_o, hs_b = (cv2.cvtColor(np.uint8([[bgr_of(c)]]), cv2.COLOR_BGR2HSV)[0, 0] for c in (ORANGE_HSV, BLUE_HSV))
    assert t["orange_h_lo"] <= hs_o[0] <= t["orange_h_hi"] and t["orange_s_lo"] <= hs_o[1]
    assert t["blue_h_lo"] <= hs_b[0] <= t["blue_h_hi"] and t["blue_s_lo"] <= hs_b[1]
    assert t["orange_h_hi"] < 60 and t["blue_h_lo"] > 60                # each color keeps to its own paint
    mask = pl.segment(frame, hl.model_from_thresholds(base, hx.nested(t)))[0]
    z = pc.zones(frame.shape, boxes, base.cfg.horizon_row)
    assert (mask[z.pos["orange"]] == 1).all() and (mask[z.pos["blue"]] == 2).all() and (mask[z.outside] == 0).all()


def test_blue_can_sit_anywhere_on_the_hue_circle(base):
    olive = (35, 60, 120)                                            # the warm-lamp blue: hue 35, weak saturation
    img, boxes = scene(blue_hsv=olive)
    t = pc.net_setting(pl.Frame.from_image(img), boxes, base, ADOPTED)
    got = cv2.cvtColor(np.uint8([[bgr_of(olive)]]), cv2.COLOR_BGR2HSV)[0, 0]
    assert t["blue_h_lo"] <= got[0] <= t["blue_h_hi"] and t["blue_s_lo"] <= got[1]
    old = pc.net_setting(pl.Frame.from_image(img), boxes, base, ADOPTED, limits=hx.LIMITS)      # the slider's span before 2026-11-25
    assert (old["blue_h_lo"], old["blue_h_hi"], old["blue_s_lo"]) == (103, 119, 113)            # out of reach: the adopted values stay


def test_the_other_colors_pixels_count_against_a_color(base):
    img, boxes = scene(blue_box=None, blue_hsv=ORANGE_HSV)           # an orange barrel whose "stripe" is orange too
    t = pc.net_setting(pl.Frame.from_image(img), boxes, base, ADOPTED)
    assert (t["blue_h_lo"], t["blue_h_hi"], t["blue_s_lo"]) == (103, 119, 113)      # painting it blue would paint the orange body: no gain
    assert t["orange_h_lo"] <= 8 <= t["orange_h_hi"]


def test_same_hue_outside_the_boxes_raises_the_floor(base):
    img, boxes = scene()
    img[350:470, 20:620] = bgr_of((8, 150, 200))                    # a big orange-ish table patch, less saturated than the barrel
    t = pc.net_setting(pl.Frame.from_image(img), boxes, base, ADOPTED)
    assert 152 < t["orange_s_lo"] <= 222


def test_a_frame_without_usable_boxes_keeps_the_adopted_values(base):
    img, boxes = scene()
    frame = pl.Frame.from_image(img)
    assert pc.net_setting(frame, [], base, ADOPTED) == ADOPTED
    flagged = [dict(b, flags=["occluded"]) for b in boxes]
    assert pc.net_setting(frame, flagged, base, ADOPTED) == ADOPTED
    assert pc.pooled_net_setting([], base, ADOPTED) == ADOPTED


def test_pooled_setting_is_the_setting_of_the_summed_histograms(base):
    a, boxes_a = scene()
    b, boxes_b = scene(blue_hsv=(100, 200, 150))
    fa, fb = pl.Frame.from_image(a), pl.Frame.from_image(b)
    total = pc.add_hists(pc.add_hists(None, pc.frame_hists(fa, boxes_a, base)), pc.frame_hists(fb, boxes_b, base))
    pooled = pc.pooled_net_setting([(fa, boxes_a), (fb, boxes_b)], base, ADOPTED)
    assert pooled == pc.net_from_hists(total, ADOPTED)
    assert pooled["blue_h_lo"] <= 100 and pooled["blue_h_hi"] >= 107     # one range over both frames' blues


def test_pixels_under_the_brightness_floor_are_not_counted(base):
    img, boxes = scene(blue_hsv=(108, 230, 30))                     # the blue paint is darker than V 40: it can never be painted
    h = pc.frame_hists(pl.Frame.from_image(img), boxes, base)
    assert h["blue"][0].sum() == 0 and h["orange"][0].sum() > 0


# ---------------------------------------------------------------- the middle of what works

class Fake:
    """A stand-in for hsrange.FrameEval: a real frame and boxes, and a rule instead of the detector."""

    def __init__(self, base, rule):
        img, self.boxes = scene()
        self.frame, self.base, self.rule = pl.Frame.from_image(img), base, rule

    def evaluate(self, thr, detect=True):
        if not hx.valid(thr):
            return hx.Outcome(frozenset(), 10 ** 6, {"orange": float("nan"), "blue": float("nan")}, {"orange": 10 ** 9, "blue": 10 ** 9}, 0, True)
        return self.rule(hx.flat(thr))


def test_mid_setting_takes_the_best_anchor_and_the_middle_of_its_run(base):
    def rule(t):            # the barrel is found only with the blue S floor between 100 and 200
        return hx.Outcome(frozenset({0}) if 100 <= t["blue_s_lo"] <= 200 else frozenset(), 0, {"orange": 0.8, "blue": 0.8}, {"orange": 0, "blue": 0}, 1)
    m = pc.mid_setting(Fake(base, rule), ADOPTED)
    assert m.source.startswith("adopted")                           # the net settings put the floor at the paint's S (about 230): nothing found
    assert m.thresholds["blue_s_lo"] == 150 and m.ranges["blue_s_lo"] == (101, 199)
    assert {k: v for k, v in m.thresholds.items() if k != "blue_s_lo"} == {k: v for k, v in ADOPTED.items() if k != "blue_s_lo"}
    assert m.found == 1 and m.n_boxes == 2


def test_mid_setting_prefers_the_careful_net_setting_on_a_tie(base):
    def rule(t):            # everything finds the barrel
        return hx.Outcome(frozenset({0}), 0, {"orange": 0.8, "blue": 0.8}, {"orange": 0, "blue": 0}, 1)
    fe = Fake(base, rule)
    m = pc.mid_setting(fe, ADOPTED)
    assert m.source.startswith("net setting (outside weight 1)")
    assert m.anchor == pc.net_setting(fe.frame, fe.boxes, base, ADOPTED, 1.0)
    assert m.thresholds == m.anchor                                 # every run reaches an end of its span: the middle says nothing
