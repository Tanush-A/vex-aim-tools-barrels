"""combined.py: the two color-step winners run together on one frame (experiment 2026-11-26_combined). Infrastructure
tests on drawn pictures: with a step off a way is the other step alone, the building blocks are the winners' own code
paths, today's paint and today's boxes are never changed, and the box rules do what they say. No data frame is opened."""
import numpy as np
import pytest

from barrels import combined as cmb
from barrels import detector as det
from barrels import geometry as geo
from barrels import hslabel as hl
from barrels import nearmiss as nm
from barrels import pipeline as pl
from barrels import selfcal as sc
from barrels.detect_types import Barrel
from barrels.io import BLUE, ORANGE, OTHER

CAM = geo.AIM_4A8B6118_BOXFIT
MODEL = hl.adopted_model()
TABLE = (180, 180, 180)                 # R, G, B
ORANGE_RGB = (200, 70, 25)              # inside the fixed orange range
BLUE_RGB = (15, 60, 140)                # inside the fixed blue range
PALE_BLUE_RGB = (60, 70, 85)            # hue 108, S 75: under the fixed blue floor (113); near-miss level 2 and up reaches it
NM = nm.NearMissConfig(stripe_level=5, body_level=5, bottom="pred")
NM_WEAK = nm.NearMissConfig(stripe_level=1)                         # S floor 93: does not reach the pale stripe
SC = sc.SelfCalConfig(rel_margin=1.0, hue_move_max=6.0, flood_max=0.03)


def picture(barrels=()):
    """A flat table and, per barrel (distance mm, centre column, body rgb, stripe rgb), a rectangle with the rows and
    the width the camera geometry gives it. Returns (frame, the barrels' boxes)."""
    rgb = np.empty((480, 640, 3), np.uint8)
    rgb[:] = TABLE
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


@pytest.fixture(scope="module")
def scene():
    """A whole barrel the fixed colors find, and an orange barrel whose blue stripe they do not paint."""
    return picture([(250.0, 150, ORANGE_RGB, BLUE_RGB), (200.0, 400, ORANGE_RGB, PALE_BLUE_RGB)])


def same(a: list, b: list) -> bool:
    return [(x.color, tuple(x.bbox)) for x in a] == [(x.color, tuple(x.bbox)) for x in b]


def on(box: Barrel, truth: tuple) -> bool:
    return det.box_iou(tuple(box.bbox), truth) >= 0.5


def test_today_misses_the_pale_striped_barrel_and_each_winner_alone_finds_it(scene):
    frame, truth = scene
    strict, first = cmb.fixed_pass(frame, MODEL)
    assert len(first) == 1 and on(first[0], truth[0])
    assert len(det.detect(cmb.near_miss(frame, MODEL, NM, CAM, strict))) == 2
    assert len(sc.SelfCal(MODEL, SC, CAM).run(frame).boxes) == 2


@pytest.mark.parametrize("way", list(cmb.WAYS))
def test_with_both_steps_off_every_way_is_today(scene, way):
    frame, _ = scene
    strict, first = cmb.fixed_pass(frame, MODEL)
    c = cmb.WAYS[way](frame, MODEL, None, None)
    assert same(c.boxes, first) and (c.mask == strict).all() and (c.strict == strict).all()
    off = nm.NearMissConfig()                                       # both directions at level 0 is "off" too
    assert same(cmb.WAYS[way](frame, MODEL, off, None).boxes, first)


@pytest.mark.parametrize("way", list(cmb.WAYS))
def test_every_way_finds_both_barrels_and_changes_no_paint_of_today(scene, way):
    frame, truth = scene
    c = cmb.WAYS[way](frame, MODEL, NM, SC)
    assert len(c.boxes) == 2 and on(c.boxes[0], truth[0]) and on(c.boxes[1], truth[1])
    painted = c.strict != OTHER
    assert (c.mask[painted] == c.strict[painted]).all()             # strict paint is never changed
    assert (c.mask != OTHER).sum() > painted.sum()                  # and something was added
    assert any(tuple(b.bbox) == tuple(c.first[0].bbox) for b in c.boxes)        # today's box stays as it is


def test_calibrate_on_the_fixed_mask_is_selfcal_run(scene):
    frame, _ = scene
    strict, first = cmb.fixed_pass(frame, MODEL)
    r = sc.SelfCal(MODEL, SC, CAM).run(frame)
    mask2, second, seeds, info = cmb.calibrate(frame, MODEL, strict, first, SC, CAM)
    assert (mask2 == r.mask2).all() and same(second, r.second) and len(seeds) == len(r.seeds) and info == r.info
    assert same(sc.combine(first, second, "add"), r.boxes)
    for way in ("box_union", "mask_union", "sc_then_nm", "nm_then_sc"):      # the near-miss step off: self-calibration alone
        assert same(cmb.WAYS[way](frame, MODEL, None, SC).boxes, r.boxes), way


def test_with_selfcal_off_the_near_miss_step_is_alone(scene):
    frame, _ = scene
    strict, first = cmb.fixed_pass(frame, MODEL)
    alone = det.detect(nm.partner_mask(frame, MODEL, NM, CAM, strict=strict)[0])
    assert same(cmb.nm_then_sc(frame, MODEL, NM, None).boxes, alone)
    assert same(cmb.box_agree(frame, MODEL, NM, None).boxes, first)             # nothing was added by self-calibration: nothing to agree on


def test_calibrate_with_no_kept_seed_returns_what_it_was_given():
    frame, _ = picture()                                            # an empty table: no seed of any kind
    strict, first = cmb.fixed_pass(frame, MODEL)
    mask2, second, seeds, info = cmb.calibrate(frame, MODEL, strict, first, SC, CAM)
    assert mask2 is strict and second is first and info == {} and not [s for s in seeds if s.ok]
    frame, _ = picture([(250.0, 150, ORANGE_RGB, BLUE_RGB)])
    strict, first = cmb.fixed_pass(frame, MODEL)
    off = cmb.calibrate(frame, MODEL, strict, first, None, CAM)     # the step off: nothing is looked for
    assert off[0] is strict and off[1] is first and off[2] == [] and off[3] == {}


def test_nothing_that_runs_by_default_imports_combined():
    import re
    from pathlib import Path
    src = Path(cmb.__file__).parent
    imports = re.compile(r"^\s*(from\s+(\.|barrels)\s+import\s+.*\bcombined\b|from\s+(\.|barrels\.)combined\b|import\s+.*\bcombined\b)", re.M)
    users = [p.name for p in src.glob("*.py") if p.name != "combined.py" and imports.search(p.read_text())]
    assert users == []
    assert imports.search("from . import combined as cmb") and imports.search("from barrels.combined import WAYS")
    assert not imports.search("the boxes of the two passes are combined")


def test_box_union_takes_what_one_step_finds_and_box_agree_needs_both(scene):
    frame, truth = scene
    union = cmb.box_union(frame, MODEL, NM_WEAK, SC)                # the weak near-miss level does not reach the pale stripe
    agree = cmb.box_agree(frame, MODEL, NM_WEAK, SC)
    assert len(union.boxes) == 2 and on(union.boxes[1], truth[1])
    assert len(agree.boxes) == 1 and on(agree.boxes[0], truth[0])
    assert agree.info["added_by_selfcal"] == 1 and agree.info["agreed"] == 0
    assert len(cmb.box_agree(frame, MODEL, NM, SC).boxes) == 2      # with the level that reaches it, both drew it


def test_nm_then_sc_keeps_the_near_miss_paint_in_the_second_pass_mask(scene):
    frame, _ = scene
    c = cmb.nm_then_sc(frame, MODEL, NM, SC)
    assert (c.mask[c.nm_mask != OTHER] != OTHER).all()
    assert (c.nm_mask != OTHER).sum() > (c.strict != OTHER).sum()


def test_sc_then_nm_hands_selfcals_mask_to_the_near_miss_step(scene):
    frame, _ = scene
    c = cmb.sc_then_nm(frame, MODEL, NM, SC)
    painted = c.sc_mask != OTHER
    assert (c.mask[painted] == c.sc_mask[painted]).all()            # the near-miss step only adds to the mask it is given


def test_overlay_top_wins_and_under_shows_through():
    top = np.array([[ORANGE, OTHER, OTHER]], np.uint8)
    under = np.array([[BLUE, BLUE, OTHER]], np.uint8)
    assert cmb.overlay(top, under).tolist() == [[ORANGE, BLUE, OTHER]]
    assert top.tolist() == [[ORANGE, OTHER, OTHER]]                 # a copy: the inputs are not written to


def test_merge_boxes_keeps_the_base_and_adds_only_where_no_box_is():
    base = [Barrel(ORANGE, (100, 100, 150, 160))]
    more = [Barrel(ORANGE, (105, 102, 152, 161)), Barrel(BLUE, (300, 100, 350, 160))]
    out = cmb.merge_boxes(base, more)
    assert [tuple(b.bbox) for b in out] == [(100, 100, 150, 160), (300, 100, 350, 160)]


def test_seed_rule_drops_a_box_of_the_other_color_on_a_kept_seed():
    seed = sc.Seed("body", ORANGE, (100, 100, 150, 160), ok=True)
    boxes = [Barrel(BLUE, (102, 104, 148, 158)), Barrel(ORANGE, (102, 104, 148, 158)), Barrel(BLUE, (300, 100, 350, 160))]
    assert [b.color for b in cmb.seed_rule(boxes, [seed])] == [ORANGE, BLUE]


# ---------------------------------------------------------------- the third winner (addendum 2026-11-27)

from barrels import contrast as cn  # noqa: E402

CN = cn.Params(strength_min=1.15, orange_min=0.8, extent_top=0.15, extent_bottom=0.15)


def test_with_contrast_off_each_three_way_is_its_base(scene):
    frame, _ = scene
    strict, first = cmb.fixed_pass(frame, MODEL)
    assert same(cmb.cn_alone(frame, MODEL, NM, SC, CAM, None, None).boxes, first)
    assert same(cmb.cn_on_nm(frame, MODEL, NM, SC, CAM, None, None).boxes, cmb.nm_then_sc(frame, MODEL, NM, None).boxes)
    assert same(cmb.cn_on_sc(frame, MODEL, NM, SC, CAM, None, None).boxes, sc.SelfCal(MODEL, SC, CAM).run(frame).boxes)
    assert same(cmb.cn_on_all(frame, MODEL, NM, SC, CAM, None, None).boxes, cmb.mask_union(frame, MODEL, NM, SC).boxes)
    for w in ("cn_box_nm", "cn_box_sc", "cn_box_all"):
        assert same(cmb.WAYS3[w](frame, MODEL, None, None, CAM, None, None).boxes, first), w


def test_contrast_alone_finds_the_pale_striped_barrel_and_keeps_todays_box(scene):
    frame, truth = scene
    strict, first = cmb.fixed_pass(frame, MODEL)
    c = cmb.cn_alone(frame, MODEL, None, None, CAM, None, CN)
    assert len(c.boxes) == 2 and on(c.boxes[1], truth[1]) and any(tuple(b.bbox) == tuple(first[0].bbox) for b in c.boxes)
    painted = strict != OTHER
    assert (c.mask[painted] == strict[painted]).all()


def test_contrast_on_leaves_a_found_barrel_alone():
    frame, _ = picture([(250.0, 150, ORANGE_RGB, BLUE_RGB)])
    strict, first = cmb.fixed_pass(frame, MODEL)
    mask, boxes, cands = cmb.contrast_on(frame, strict, first, CN, CAM)
    assert mask is strict and boxes is first
    assert all(c.info.get("painted", 0) == 0 for c in cands)


@pytest.mark.parametrize("way", ["cn_on_nm", "cn_on_sc", "cn_on_all", "cn_box_nm", "cn_box_sc", "cn_box_all"])
def test_every_three_way_finds_both_barrels(scene, way):
    frame, truth = scene
    c = cmb.WAYS3[way](frame, MODEL, NM, SC, CAM, None, CN)
    assert len(c.boxes) == 2 and on(c.boxes[0], truth[0]) and on(c.boxes[1], truth[1])
