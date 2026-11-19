"""The occlusion generator of the occlusion scorecard: each kind hides what its numbers say, and nothing else."""
import numpy as np
import pytest

from barrels import geometry as geo, io, occlude as oc

CAM = geo.AIM_4A8B6118_BOXFIT
BOX = (300, 120, 360, 180)          # W = H = 60


def source(color=io.ORANGE, box=BOX):
    m = np.zeros((480, 640), np.uint8)
    x0, y0, x1, y1 = box
    other = io.BLUE if color == io.ORANGE else io.ORANGE
    m[y0:y1, x0:x1] = color
    m[y0 + 25:y1 - 20, x0:x1] = other          # the stripe, 15 rows
    return oc.cut_source(m, box, color, stem="synthetic")


def test_amount_zero_is_the_barrel_alone_at_its_own_place():
    src = source()
    for kind in oc.KINDS:
        sc = oc.make_scene(src, kind, 0.0, front=src)
        assert sc.target == (io.ORANGE, BOX) and sc.hidden == 0 and not sc.fronts and not sc.clutter
        assert (sc.mask[120:180, 300:360] > 0).all() and (sc.mask > 0).sum() == 3600


def test_same_arguments_same_scene_and_the_source_is_never_changed():
    src = source(); before = src.crop.copy()
    a = oc.make_scene(src, "barrel_low", 0.5, "R", "same", front=src)
    b = oc.make_scene(src, "barrel_low", 0.5, "R", "same", front=src)
    assert (a.mask == b.mask).all() and a.fronts == b.fronts and (src.crop == before).all()


@pytest.mark.parametrize("amount", oc.AMOUNTS)
def test_erasers_hide_the_stated_share_and_only_remove_pixels(amount):
    src = source()
    full = oc.make_scene(src, "edge", 0.0).mask
    for kind in ("edge", "slant", "both", "top", "bottom", "post"):
        for side in ("L", "R"):
            sc = oc.make_scene(src, kind, amount, side)
            assert sc.target == (io.ORANGE, BOX)                       # the truth is the full box
            assert abs(sc.hidden - amount) < 0.03, (kind, side, sc.hidden)
            changed = sc.mask != full
            assert (sc.mask[changed] == 0).all()                       # nothing is added


def test_edge_hides_the_side_it_names_and_both_hides_half_from_each():
    src = source()
    left = oc.make_scene(src, "edge", 0.25, "L").mask
    assert not left[:, 300:315].any() and (left[120:180, 315:360] > 0).all()
    right = oc.make_scene(src, "edge", 0.25, "R").mask
    assert not right[:, 345:].any() and (right[120:180, 300:345] > 0).all()
    both = oc.make_scene(src, "both", 0.5).mask
    assert not both[:, 300:315].any() and not both[:, 345:360].any() and (both[120:180, 315:345] > 0).all()
    post = oc.make_scene(src, "post", 0.5).mask
    assert not post[:, 315:345].any() and (post[120:180, 300:315] > 0).all() and (post[120:180, 345:360] > 0).all()


def test_slant_hides_the_amount_at_mid_height_and_leans_a_quarter_width():
    src = source()
    m = oc.make_scene(src, "slant", 0.5, "L", lean=1).mask
    first = [int(np.flatnonzero(m[r] > 0)[0]) for r in (120, 150, 179)]
    assert abs(first[1] - 330) <= 1 and abs((first[2] - first[0]) - 15) <= 1          # 0.25 x 60 from top to bottom
    m2 = oc.make_scene(src, "slant", 0.5, "L", lean=-1).mask
    assert int(np.flatnonzero(m2[120] > 0)[0]) > int(np.flatnonzero(m2[179] > 0)[0])


def test_top_and_bottom_hide_rows():
    src = source()
    assert not oc.make_scene(src, "top", 0.5).mask[:150].any()
    assert not oc.make_scene(src, "bottom", 0.25).mask[165:].any()


def test_frame_moves_the_barrel_out_of_the_picture_and_the_truth_is_the_cut_box():
    src = source()
    sc = oc.make_scene(src, "frame", 0.25, "L")
    assert sc.target == (io.ORANGE, (0, 120, 45, 180)) and (sc.mask[120:180, 0:45] > 0).all() and not sc.mask[:, 45:].any()
    sc = oc.make_scene(src, "frame", 0.5, "R")
    assert sc.target == (io.ORANGE, (610, 120, 640, 180)) and (sc.mask[120:180, 610:640] > 0).all()
    assert abs(sc.hidden - 0.5) < 0.02


def test_barrel_in_front_is_lower_larger_and_of_the_asked_color():
    src = source()
    for kind, lower in (("barrel_side", oc.SIDE_LOWER), ("barrel_low", oc.LOW_LOWER)):
        for color, want in (("same", io.ORANGE), ("other", io.BLUE)):
            sc = oc.make_scene(src, kind, 0.5, "L", color, front=src)
            (fc, fb), = sc.fronts
            assert fc == want
            assert fb[3] == 180 + round(lower * 60) and fb[2] == 330              # bottom lower; its right edge hides half the width
            assert (fb[2] - fb[0]) > 60 and (fb[3] - fb[1]) > 60                    # nearer = larger
            inside = sc.mask[fb[1]:fb[3], fb[0]:fb[2]]
            assert (inside == want).sum() > (inside == (io.BLUE if want == io.ORANGE else io.ORANGE)).sum()   # its body color is the majority
            assert (sc.mask[120:fb[1], 300:360] == io.ORANGE).all()                 # above the front barrel the back one still shows
            assert 0.3 < sc.hidden < 0.5
    right = oc.make_scene(src, "barrel_side", 0.25, "R", "other", front=src)
    assert right.fronts[0][1][0] == 345


def test_barrel_straight_in_front_hides_the_lower_part():
    src = source()
    for amount in oc.AMOUNTS:
        sc = oc.make_scene(src, "barrel_front", amount, color="other", front=src)
        (fc, fb), = sc.fronts
        assert fc == io.BLUE and abs(fb[1] - (180 - amount * 60)) <= 1              # its top row is where the hidden part starts
        assert abs((fb[0] + fb[2]) / 2 - 330) <= 1 and fb[3] > 180
        alone = oc.make_scene(src, "barrel_front", 0.0, front=src).mask
        assert (sc.mask[120:fb[1] - 1, 300:360] == alone[120:fb[1] - 1, 300:360]).all()   # above its top row the back barrel still shows
        assert abs(sc.hidden - amount) < 0.05


def test_front_scale_is_the_camera_models_width_ratio():
    assert oc.front_scale(CAM, 180, 180) == 1.0
    assert oc.front_scale(CAM, 180, 220) == pytest.approx(CAM.expected_barrel_width_px(bottom_row=220) / CAM.expected_barrel_width_px(bottom_row=180))
    assert oc.front_scale(CAM, 180, 220) > 1


def test_block_is_one_plain_color_and_is_not_a_barrel():
    src = source()
    sc = oc.make_scene(src, "block", 0.5, "L", "same")
    (bc, bb), = sc.clutter
    assert bc == io.ORANGE and bb == (270, 129, 330, 189) and (sc.mask[129:189, 270:330] == io.ORANGE).all() and not sc.fronts
    sc = oc.make_scene(src, "block", 0.25, "R", "other")
    (bc, bb), = sc.clutter
    assert bc == io.BLUE and bb == (345, 129, 405, 189) and (sc.mask[129:189, 345:405] == io.BLUE).all()
    assert abs(sc.hidden - 0.25 * 51 / 60) < 0.03


def test_cut_source_keeps_the_paint_just_outside_the_box_but_not_a_neighbours():
    m = np.zeros((480, 640), np.uint8)
    m[118:182, 298:362] = io.ORANGE                 # paint 2 px outside the hand-drawn box all round
    m[120:180, 361:420] = io.BLUE                   # a touching neighbour, box (361, 120, 420, 180)
    src = oc.cut_source(m, BOX, io.ORANGE, other_boxes=[(361, 120, 420, 180)])
    assert src.origin == (297, 117) and src.crop.shape == (66, 66)
    assert (src.crop == io.ORANGE).sum() == 64 * 64 - 60        # all the paint, less the neighbour's column 361 in its rows
    assert not (src.crop == io.BLUE).any()                      # the neighbour's own pixels are not taken along


def test_no_room_in_front_of_a_very_near_barrel_is_refused():
    near = source(box=(200, 250, 420, 470))                     # a close-up: 220 px tall, bottom at row 470
    with pytest.raises(ValueError):
        oc.make_scene(near, "barrel_front", 0.25, front=near)


def test_swap_colors_and_outline():
    src = source()
    sw = oc.swap_colors(src.crop)
    assert (sw == io.BLUE).sum() == (src.crop == io.ORANGE).sum() and (sw == io.ORANGE).sum() == (src.crop == io.BLUE).sum()
    holed = src.crop.copy(); holed[20:30, 20:30] = 0
    assert oc.outline(holed)[25, 25] and not oc.outline(holed)[0, 0]


def test_bad_arguments_are_refused():
    src = source()
    with pytest.raises(ValueError):
        oc.make_scene(src, "fog", 0.5)
    with pytest.raises(ValueError):
        oc.make_scene(src, "edge", 1.0)
    with pytest.raises(ValueError):
        oc.make_scene(src, "barrel_side", 0.5)
