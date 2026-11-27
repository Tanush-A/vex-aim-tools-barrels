"""The barrel as its own color reference (src/barrels/selfcal.py; experiment 2026-11-26_selfcal): the geometry of a
seed, the bands, reading a band, the frame's ranges and their bounds, the flood guard, combining the two passes, and
the whole two-pass run on synthetic pictures (a barrel whose stripe the fixed colors do not paint). Synthetic images
only; no data frame is opened."""
import dataclasses
from pathlib import Path

import numpy as np
import pytest

from barrels import boxfit as bf, geometry as geo, hslabel as hl, io, pipeline as pl, selfcal as sc
from barrels.detect_types import Barrel

O, B = io.ORANGE, io.BLUE
CAM = geo.AIM_4A8B6118_BOXFIT
MODEL = hl.adopted_model()
CFG = sc.SelfCalConfig()
TABLE = (180, 180, 180)                 # R, G, B
ORANGE_RGB = (200, 70, 25)              # hue 8, S 223: inside the fixed orange range
BLUE_RGB = (15, 60, 140)                # hue 109, S 228: inside the fixed blue range
PALE_BLUE_RGB = (60, 70, 85)            # hue 108, S 75: under the fixed blue floor (113)


def picture(barrels=(), table=TABLE):
    """A 640 x 480 picture: a flat table and, per barrel (distance mm, centre column, body rgb, stripe rgb), a
    rectangle with the rows and the width the camera geometry gives it."""
    rgb = np.empty((480, 640, 3), np.uint8)
    rgb[:] = table
    boxes = []
    for d, cx, body, stripe in barrels:
        r = CAM.barrel_rows(d)
        x0, x1 = int(round(cx - r.width_px / 2)), int(round(cx + r.width_px / 2))
        top, bottom = int(round(r.top)), int(round(r.bottom))
        rgb[top:bottom, x0:x1] = body
        rgb[int(round(r.stripe_top)):int(round(r.stripe_bottom)), x0:x1] = stripe
        boxes.append((x0, top, x1, bottom))
    frame = pl.Frame.from_image(np.ascontiguousarray(rgb[..., ::-1]))
    for a in (frame.bgr, frame.rgb, frame.sat, frame.val):
        a.setflags(write=False)
    return frame, boxes


def reading(cls, hue, sat=200.0, spread=2.0, colorful=1.0, n=100):
    return sc.Reading(cls, n, (hue - spread, hue, hue + spread), (sat - 10, sat, sat + 10), (100.0, 120.0, 140.0),
                      (hue - spread, hue, hue + spread), colorful, int(n * colorful), 0.0, 0.0)


def six(boxes):
    return {c: (boxes[c].lo[0] - pl.HUE_SHIFT[c], boxes[c].hi[0] - pl.HUE_SHIFT[c], boxes[c].lo[1]) for c in (O, B)}


FIXED = six(MODEL.boxes)                # {orange: (3, 13, 140), blue: (103, 119, 113)}


# ---------------------------------------------------------------- geometry and bands

def test_rows_at_stripe_inverts_the_camera_model():
    for d in (120.0, 200.0, 400.0):
        rows = sc.rows_at_stripe(CAM, CAM.barrel_rows(d).stripe_center)
        assert rows is not None and rows.d_axis_mm == pytest.approx(d, abs=1e-6)
    assert sc.rows_at_stripe(CAM, CAM.horizon_row() - 5) is None


def test_bands_of_a_box_lie_in_it_in_order_and_in_the_centre_columns():
    b = sc.bands((100, 100, 160, 170), (480, 640))
    assert b["upper"][3] <= b["stripe"][1] and b["stripe"][3] <= b["lower"][1]
    for x0, y0, x1, y1 in b.values():
        assert 100 <= y0 < y1 <= 170 and 100 + 0.3 * 60 <= x0 < x1 <= 100 + 0.7 * 60
    assert sc.bands((100, 470, 160, 560), (480, 640)) is None             # the lower band is under the frame


def test_bands_around_a_seen_stripe_follow_the_stripe_not_the_box():
    b = sc.bands((100, 100, 160, 170), (480, 640), stripe=(140.0, 152.0))
    assert b["stripe"][1] >= 140 and b["stripe"][3] <= 152
    assert b["upper"][3] <= 140 and b["upper"][1] >= 140 - 12
    assert b["lower"][1] >= 152 and b["lower"][3] <= 152 + 12


def test_the_upper_band_sits_lower_in_a_tall_box():
    assert sc.upper_rows(30) < sc.upper_rows(60) < sc.upper_rows(100)


# ---------------------------------------------------------------- reading a band

def test_read_band_reports_the_colors_of_the_photo_and_what_the_mask_paints():
    frame, _ = picture([(200.0, 320, ORANGE_RGB, PALE_BLUE_RGB)])
    mask, _ = pl.segment(frame, MODEL)
    r = CAM.barrel_rows(200.0)
    rect = (310, int(r.stripe_top) + 2, 330, int(r.stripe_bottom) - 1)
    st = sc.read_band(frame, mask, [rect], B, CFG)
    assert st.cls == B and st.painted == 0.0 and 100 <= st.hue[1] <= 115 and 60 <= st.sat[1] <= 90
    assert st.lrb == pytest.approx(np.log(61 / 86), abs=1e-6) and st.colorful == 1.0
    body = sc.read_band(frame, mask, [(310, int(r.top) + 3, 330, int(r.top) + 8)], O, CFG)
    assert body.painted == 1.0 and 3 <= body.hue[1] <= 13 and body.lrb > 1.5
    assert sc.read_band(frame, mask, [(0, 0, 2, 2)], O, CFG) is None      # too few pixels


def test_orange_hue_is_read_on_a_line_across_the_red_wrap():
    rgb = np.empty((480, 640, 3), np.uint8)
    rgb[:] = (200, 30, 40)                                                # a red just past the wrap: OpenCV hue 178
    frame = pl.Frame.from_image(np.ascontiguousarray(rgb[..., ::-1]))
    r = sc.read_band(frame, np.zeros((480, 640), np.uint8), [(10, 100, 30, 120)], O, CFG)
    assert -5 <= r.hue[1] <= 0


def test_in_read_box_keeps_the_read_colors_and_refuses_the_table():
    frame, _ = picture([(200.0, 320, ORANGE_RGB, PALE_BLUE_RGB)])
    mask, _ = pl.segment(frame, MODEL)
    r = CAM.barrel_rows(200.0)
    rect = (310, int(r.stripe_top) + 2, 330, int(r.stripe_bottom) - 1)
    box = sc.read_box(sc.read_band(frame, mask, [rect], B, CFG), CFG)
    assert sc.in_read_box(frame, box, rect).all()
    assert not sc.in_read_box(frame, box, (0, 300, 50, 350)).any()        # the gray table


# ---------------------------------------------------------------- the frame's ranges

def test_no_reading_leaves_the_fixed_ranges():
    boxes, info = sc.frame_ranges({O: [], B: []}, MODEL.boxes, CFG)
    assert boxes == MODEL.boxes and info["orange"]["used"] == 0


def test_a_range_only_widens_and_holds_what_was_read():
    boxes, info = sc.frame_ranges({O: [reading(O, 16.0)], B: [reading(B, 110.0)]}, MODEL.boxes, CFG)
    got = six(boxes)
    assert got[O] == (FIXED[O][0], 16 + 2 + CFG.hue_margin, FIXED[O][2])    # the high end moved out to the reading + margin
    assert got[B] == FIXED[B] and not info["blue"]["moved"]               # a reading inside the fixed range moves nothing


def test_a_hue_end_moves_at_most_hue_move_max():
    got = six(sc.frame_ranges({O: [reading(O, 40.0)]}, MODEL.boxes, CFG)[0])
    assert got[O][1] == FIXED[O][1] + CFG.hue_move_max
    got = six(sc.frame_ranges({O: [reading(O, -25.0)]}, MODEL.boxes, CFG)[0])
    assert got[O][0] == FIXED[O][0] - CFG.hue_move_max


def test_the_saturation_floor_goes_down_but_never_under_the_bound():
    got = six(sc.frame_ranges({B: [reading(B, 110.0, sat=110.0)]}, MODEL.boxes, CFG)[0])
    assert got[B][2] == 110 - 10 - CFG.s_margin
    got = six(sc.frame_ranges({B: [reading(B, 110.0, sat=75.0)]}, MODEL.boxes, CFG)[0])
    assert got[B][2] == CFG.s_floor_min


def test_a_washed_out_or_scattered_reading_moves_nothing():
    assert sc.frame_ranges({B: [reading(B, 95.0, colorful=0.3)]}, MODEL.boxes, CFG)[0] == MODEL.boxes
    assert sc.frame_ranges({B: [reading(B, 95.0, spread=10.0)]}, MODEL.boxes, CFG)[0] == MODEL.boxes
    assert sc.frame_ranges({B: [reading(B, 95.0, n=10)]}, MODEL.boxes, CFG)[0] == MODEL.boxes


def test_readings_must_agree():
    two = six(sc.frame_ranges({O: [reading(O, 0.0), reading(O, 18.0)]}, MODEL.boxes, CFG)[0])
    assert two[O] == FIXED[O]                                             # 18 apart: neither is used
    three = six(sc.frame_ranges({O: [reading(O, 15.0), reading(O, 16.0), reading(O, -20.0)]}, MODEL.boxes, CFG)[0])
    assert three[O] == (FIXED[O][0], 16 + 2 + CFG.hue_margin, FIXED[O][2])  # the odd one is left out


def test_flood_guard_takes_back_a_range_that_paints_the_table():
    frame, _ = picture(table=(150, 90, 40))                               # an orange-brown table: hue 14, S 187
    wide = {O: bf.Box((MODEL.boxes[O].lo[0], 140.0), (MODEL.boxes[O].hi[0] + 6, 255.0)), B: MODEL.boxes[B]}
    boxes, shares = sc.flood(frame, MODEL, wide, CFG)
    assert shares["orange"] > 0.9 and boxes == MODEL.boxes
    frame2, _ = picture()                                                  # a gray table: the same range paints nothing new
    boxes2, shares2 = sc.flood(frame2, MODEL, wide, CFG)
    assert shares2["orange"] == 0.0 and boxes2 == wide


def test_flood_guard_does_not_count_paint_on_a_kept_seed():
    frame, gt = picture([(60.0, 320, (200, 122, 25), BLUE_RGB)])           # a near barrel in an orange the fixed range misses (hue 16)
    wide = {O: bf.Box((MODEL.boxes[O].lo[0], 140.0), (MODEL.boxes[O].hi[0] + 6, 255.0)), B: MODEL.boxes[B]}
    _, alone = sc.flood(frame, MODEL, wide, CFG)
    seed = sc.Seed("stripe", O, gt[0], ok=True, why="ok")
    kept, on_seed = sc.flood(frame, MODEL, wide, CFG, [seed])
    assert alone["orange"] > CFG.flood_max and on_seed["orange"] == 0.0 and kept == wide


# ---------------------------------------------------------------- combining the two passes

def bx(color, x0, y0, w=40, h=40):
    return Barrel(color=color, bbox=(x0, y0, x0 + w, y0 + h))


def test_combine_keeps_the_first_pass_and_adds_only_where_it_has_no_box():
    first, second = [bx(O, 100, 100)], [bx(O, 105, 102), bx(B, 300, 100)]
    out = sc.combine(first, second, "add")
    assert first[0] in out and second[1] in out and second[0] not in out and len(out) == 2
    out = sc.combine(first, second, "second")
    assert second[0] in out and second[1] in out and first[0] not in out
    with pytest.raises(ValueError):
        sc.combine(first, second, "both")


# ---------------------------------------------------------------- the two passes on synthetic pictures

def test_a_barrel_with_an_unpainted_stripe_is_found_by_its_own_colors():
    frame, boxes = picture([(200.0, 320, ORANGE_RGB, PALE_BLUE_RGB)])
    before = frame.bgr.copy()
    r = sc.SelfCal(MODEL, CFG, CAM).run(frame)
    assert r.first == []                                                   # the fixed colors: body in two pieces, no stripe, no box
    kept = r.kept
    assert len(kept) == 1 and kept[0].kind == "body" and kept[0].body == O and kept[0].stripe_box is not None
    assert len(r.boxes) == 1 and r.boxes[0].color == O
    x0, y0, x1, y1 = r.boxes[0].bbox
    gx0, gy0, gx1, gy1 = boxes[0]
    assert abs(x0 - gx0) <= 3 and abs(x1 - gx1) <= 3 and abs(y0 - gy0) <= 4 and abs(y1 - gy1) <= 4
    assert (r.mask2 == B).sum() > 0 and (r.mask1 == B).sum() == 0
    assert np.array_equal(frame.bgr, before)                               # no pixel was changed


def test_a_stripe_with_an_unpainted_body_is_found_by_its_own_colors():
    frame, boxes = picture([(200.0, 320, PALE_BLUE_RGB, ORANGE_RGB)], table=(200, 200, 200))
    r = sc.SelfCal(MODEL, dataclasses.replace(CFG, frame=False), CAM).run(frame)
    assert r.first == [] and [s.kind for s in r.kept] == ["stripe"] and r.kept[0].body == B
    assert len(r.boxes) == 1 and r.boxes[0].color == B
    assert r.info["moved"] == []                                           # local only: the frame's ranges did not move


def test_one_seed_sets_the_frame_ranges_for_a_barrel_that_is_not_a_seed():
    # two barrels with the same pale blue; the second one's orange is off too (hue 16), so it is no seed
    frame, boxes = picture([(200.0, 200, ORANGE_RGB, PALE_BLUE_RGB), (200.0, 420, (200, 122, 25), PALE_BLUE_RGB)])
    local = sc.SelfCal(MODEL, dataclasses.replace(CFG, frame=False), CAM).run(frame)
    both = sc.SelfCal(MODEL, CFG, CAM).run(frame)
    assert "blue" in both.info["moved"] and both.info["ranges"]["blue"]["s_lo"] == CFG.s_floor_min
    assert (both.mask2 == B).sum() > (local.mask2 == B).sum()             # the second barrel's stripe is painted by the frame range only


def test_an_empty_table_changes_nothing():
    frame, _ = picture()
    r = sc.SelfCal(MODEL, CFG, CAM).run(frame)
    assert r.boxes == [] and r.seeds == [] and r.mask2 is r.mask1


def test_two_orange_bars_with_the_table_between_them_are_not_a_barrel():
    frame, _ = picture([(200.0, 320, ORANGE_RGB, TABLE)])                  # the 'stripe' is the table showing through
    r = sc.SelfCal(MODEL, CFG, CAM).run(frame)
    assert [s.why for s in r.seeds if s.kind == "body"] == ["stripe_like_surround"] and r.kept == [] and r.boxes == r.first


def test_a_band_between_colors_that_are_not_two_barrel_colors_is_refused():
    frame, _ = picture([(200.0, 320, ORANGE_RGB, (190, 90, 40))])          # an orange thing with a slightly different orange band
    r = sc.SelfCal(MODEL, CFG, CAM).run(frame)
    assert r.kept == [] and all(s.why in ("not_two_colors", "body_not_painted", "stripe_not_painted", "too_small", "off_frame") for s in r.seeds)


def test_nothing_is_carried_from_one_frame_to_the_next():
    cal = sc.SelfCal(MODEL, CFG, CAM)
    a, _ = picture([(200.0, 320, ORANGE_RGB, PALE_BLUE_RGB)])
    b, _ = picture([(250.0, 200, BLUE_RGB, (200, 122, 25))])
    first = cal.run(a)
    cal.run(b)
    again = cal.run(a)
    assert [x.bbox for x in first.boxes] == [x.bbox for x in again.boxes] and np.array_equal(first.mask2, again.mask2)
    assert first.info == again.info


def test_a_fully_painted_barrel_is_left_as_the_first_pass_found_it():
    frame, _ = picture([(200.0, 320, ORANGE_RGB, BLUE_RGB)])
    r = sc.SelfCal(MODEL, CFG, CAM).run(frame)
    assert len(r.first) == 1 and r.boxes == r.first and r.info["moved"] == []


def test_the_fixed_model_must_be_an_hs_model():
    bad = dataclasses.replace(MODEL, cfg=dataclasses.replace(MODEL.cfg, color_model="rgb_box"))
    with pytest.raises(ValueError):
        sc.SelfCal(bad)


def test_nothing_that_runs_by_default_imports_selfcal():
    src = Path(sc.__file__).parent
    users = [p.name for p in src.glob("*.py") if p.name != "selfcal.py" and "selfcal" in p.read_text()]
    assert users == []
