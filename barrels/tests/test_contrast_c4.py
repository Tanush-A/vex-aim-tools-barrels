"""The experiment C4 copy of the contrast module (contrast_c4.py, imported by nothing that runs by default; ported 2026-11-27)."""
import numpy as np
import pytest

from barrels import contrast_c4 as cn
from barrels import detector as det
from barrels import geometry as geo
from barrels.io import BLUE, ORANGE, OTHER

CAM = geo.AIM_4A8B6118_BOXFIT
ORANGE_RGB, BLUE_RGB, TABLE_RGB = (230, 110, 30), (30, 70, 160), (150, 150, 150)


def scene(barrels=(), light=(1.0, 1.0, 1.0), table=TABLE_RGB) -> np.ndarray:
    """A gray table with barrels drawn where the camera model puts them. ``barrels``: (color, axis distance mm, x
    centre[, stripe height factor]). Body = the predicted box, stripe = the predicted stripe rows (x the factor)."""
    rgb = np.zeros((480, 640, 3), np.float64)
    rgb[:] = table
    rgb[:70] = (90, 90, 90)
    for b in barrels:
        color, d, x = b[:3]
        k = b[3] if len(b) > 3 else 1.0
        r = CAM.barrel_rows(d)
        x0, x1 = int(round(x - r.width_px / 2)), int(round(x + r.width_px / 2))
        body, stripe = (ORANGE_RGB, BLUE_RGB) if color == ORANGE else (BLUE_RGB, ORANGE_RGB)
        rgb[int(round(r.top)):int(round(r.bottom)), x0:x1] = body
        mid, hs = (r.stripe_top + r.stripe_bottom) / 2, (r.stripe_bottom - r.stripe_top) * k
        rgb[int(round(mid - hs / 2)):int(round(mid + hs / 2)), x0:x1] = stripe
    out = np.clip(rgb * np.array(light), 0, 255).astype(np.int16)
    out.setflags(write=False)
    return out


# ---------------------------------------------------------------- the channel

def test_channel_is_zero_for_gray_and_signed_for_red_and_blue():
    px = np.array([[[100, 100, 100], [200, 80, 20], [20, 80, 200]]])
    for kind in ("logrb", "opp"):
        c = cn.channel(px, kind, 8.0)[0]
        assert c[0] == pytest.approx(0.0, abs=1e-6) and c[1] > 0.5 and c[2] < -0.5
    with pytest.raises(ValueError):
        cn.channel(px, "hue")


def test_logrb_does_not_depend_on_brightness_and_a_cast_adds_a_constant():
    px = np.array([[[200.0, 80.0, 20.0], [20.0, 80.0, 200.0]]])
    c = cn.channel(px, "logrb", 0.0)[0]
    assert cn.channel(px * 0.5, "logrb", 0.0)[0] == pytest.approx(c, abs=1e-6)
    cast = cn.channel(px * np.array([1.0, 0.8, 0.5]), "logrb", 0.0)[0]
    assert cast - c == pytest.approx([np.log(2.0), np.log(2.0)], abs=1e-6)        # the same shift for both: a difference removes it


def test_usable_leaves_out_dark_and_clipped_pixels():
    px = np.array([[[10, 12, 9], [100, 50, 20], [255, 200, 100]]])
    assert cn.usable(px, cn.Params(v_min=25, clip=250)).tolist() == [[False, True, False]]


# ---------------------------------------------------------------- what the row predicts

def test_row_bands_follow_the_camera_model():
    p = cn.Params()
    rb = cn.row_bands(CAM, 480, p)
    assert not rb.ok[: int(CAM.horizon_row()) + 1].any()                # nothing at or above the horizon
    ys = np.nonzero(rb.ok)[0]
    assert len(ys) > 250
    for y in (ys[0], 150, 250, ys[-1]):
        at = det.BarrelAt.from_stripe_row(CAM, y + 0.5)                # the detector's own reading of that row (ported 2026-11-27: was det._stripe_geometry)
        d, rows = at.d, at.rows
        assert rb.width[y] == pytest.approx(rows.width_px) and rb.top[y] == pytest.approx(rows.top) and rb.bottom[y] == pytest.approx(rows.bottom)
        assert rb.u0[y] < rb.u1[y] <= rb.s0[y] < rb.s1[y] <= rb.l0[y] < rb.l1[y]
        assert rows.stripe_top - 1 <= rb.s0[y] and rb.s1[y] <= rows.stripe_bottom + 1     # the stripe band is inside the stripe
        assert rows.top - 1 <= rb.u0[y] and rb.l1[y] <= rows.bottom + 1                     # the body bands are inside the barrel
        assert rb.stripe_h[y] >= p.min_stripe_px and rb.width[y] >= p.min_width_px
    assert (np.diff(rb.width[ys]) > 0).all()                            # nearer (lower in the picture) = larger


def test_barrel_at_is_none_above_the_horizon():
    assert cn.barrel_at(CAM, CAM.horizon_row() - 5) is None
    assert cn.barrel_at(CAM, 150.0).width_px == pytest.approx(det.BarrelAt.from_stripe_row(CAM, 150.0).W)


# ---------------------------------------------------------------- band means and the sandwich

def test_band_means_are_the_means_of_the_usable_pixels_of_each_band():
    p = cn.Params()
    rb = cn.row_bands(CAM, 480, p)
    rng = np.random.default_rng(0)
    chan = rng.normal(size=(480, 6))
    good = np.ones((480, 6), bool)
    y = 200
    good[rb.u0[y], 2] = False                                           # one unusable pixel in the upper band of column 2
    S, U, L, valid = cn.band_means(chan, good, rb, p)
    assert S[y, 1] == pytest.approx(chan[rb.s0[y]:rb.s1[y], 1].mean())
    assert L[y, 4] == pytest.approx(chan[rb.l0[y]:rb.l1[y], 4].mean())
    assert U[y, 2] == pytest.approx(chan[rb.u0[y] + 1:rb.u1[y], 2].mean())
    assert valid[y].all() and not valid[10].any()                       # row 10 is above the horizon
    good[rb.s0[y]:rb.s1[y], 3] = False                                  # a stripe band with nothing usable
    assert not cn.band_means(chan, good, rb, p)[3][y, 3]


def test_sandwich_takes_the_smaller_difference_and_needs_one_sign():
    S = np.array([0.0, 0.0, 0.0, 0.0])
    U = np.array([2.0, -1.0, 1.0, 0.5])
    L = np.array([1.5, -3.0, -1.0, 0.0])
    assert cn.sandwich(S, U, L).tolist() == [1.5, -1.0, 0.0, 0.0]
    assert cn.sandwich(S, U, L, np.array([False, True, True, True])).tolist() == [0.0, -1.0, 0.0, 0.0]


def test_hmean_counts_the_part_outside_the_frame_as_not_agreeing():
    a = np.ones((2, 10))
    m = cn._hmean(a, np.array([1, 2]))
    assert m[0, 5] == pytest.approx(1.0) and m[0, 0] == pytest.approx(2 / 3)
    assert m[1, 5] == pytest.approx(1.0) and m[1, 9] == pytest.approx(3 / 5)


# ---------------------------------------------------------------- candidates

def _near(c: cn.Candidate, d: float, x: float) -> bool:
    r = CAM.barrel_rows(d)
    return abs(c.row - r.stripe_center) <= 2 and abs(c.x - x) <= 0.12 * r.width_px


def test_find_gives_one_candidate_per_barrel_with_its_color():
    rgb = scene([(ORANGE, 200, 200), (BLUE, 300, 420)])
    cands = cn.find(rgb, CAM)
    assert [c.color for c in cands] == [ORANGE, BLUE] or [c.color for c in cands] == [BLUE, ORANGE]
    o = next(c for c in cands if c.color == ORANGE)
    b = next(c for c in cands if c.color == BLUE)
    assert _near(o, 200, 200) and _near(b, 300, 420)
    r = CAM.barrel_rows(200)
    assert o.box == pytest.approx((o.x + 0.5 - r.width_px / 2, r.top, o.x + 0.5 + r.width_px / 2, r.bottom), abs=2.0)
    assert o.share > 0.9 and o.strength > 2.0 and o.stripe_color == BLUE and b.stripe_color == ORANGE


def test_find_is_the_same_under_a_strong_color_cast():
    plain = cn.find(scene([(ORANGE, 200, 200), (BLUE, 300, 420)]), CAM)
    warm = cn.find(scene([(ORANGE, 200, 200), (BLUE, 300, 420)], light=(1.0, 0.75, 0.4)), CAM)
    assert sorted((c.color, c.x) for c in warm) == sorted((c.color, c.x) for c in plain)
    assert all(abs(a.row - b.row) <= 1 for a, b in zip(sorted(warm, key=lambda c: c.x), sorted(plain, key=lambda c: c.x)))


def test_find_gives_nothing_on_an_empty_table_or_a_block_without_a_stripe():
    assert cn.find(scene(), CAM) == []
    rgb = scene().copy()
    rgb[120:180, 300:350] = ORANGE_RGB                                  # an orange block: no band inside it
    assert cn.find(rgb, CAM) == []


def test_find_refuses_a_band_of_the_wrong_size_for_its_row():
    tall = scene([(ORANGE, 200, 200, 3.2)])                             # a blue band over three stripes tall
    cands = cn.find(tall, CAM)
    assert not any(c.color == ORANGE for c in cands)                    # no orange barrel: the body bands fall inside the band
    # what is left is the thin orange top between the table and the blue band, read as a blue barrel's stripe; its
    # two "body bands" are two different things (gray table, blue), which is what the alike guard is for
    p = cn.Params(alike_feat=0.42)
    assert cands and all("alike_feat" in c.info["reasons"] for c in _measured(tall, p)[0])
    thin = scene([(ORANGE, 200, 200, 0.2)])                             # a hairline: the stripe band is mostly body
    assert cn.find(thin, CAM, cn.Params(strength_min=2.0)) == [] and len(cn.find(scene([(ORANGE, 200, 200)]), CAM, cn.Params(strength_min=2.0))) == 1


def test_recentre_takes_the_middle_of_a_stripe_and_the_end_barrel_of_a_shared_one():
    row = np.zeros(200, bool)
    row[80:120] = True                                                  # one stripe, 40 wide
    assert cn._recentre(row, 85, 16, 40.0) == 100
    assert cn._recentre(row, 110, 16, 40.0) == 100
    assert cn._recentre(row, 82, 8, 40.0) == 90                         # the move is at most half a window
    row[80:200] = True                                                  # three touching barrels: one long stripe
    assert cn._recentre(row, 90, 16, 40.0) == 100                       # the barrel at the left end
    assert cn._recentre(row, 130, 16, 40.0) == 140                      # the middle barrel
    assert cn._recentre(row, 185, 16, 40.0) == 180                      # the barrel at the right end
    assert cn._recentre(np.zeros(200, bool), 50, 16, 40.0) == 50


def test_recentre_row_takes_the_middle_of_a_flat_top():
    col = np.array([0, 0, 1, 3, 3, 3, 3, 3, 1, 0, 0], float)
    assert cn._recentre_row(col, 3, 5) == 5 and cn._recentre_row(col, 7, 5) == 5
    assert cn._recentre_row(col, 3, 1) == 4                             # ... looking at most ``reach`` rows each way


def test_touching_barrels_of_one_color_give_one_candidate_each():
    r = CAM.barrel_rows(200)
    w = int(round(r.width_px))
    cands = cn.find(scene([(ORANGE, 200, 200), (ORANGE, 200, 200 + w), (ORANGE, 200, 200 + 2 * w)]), CAM)
    assert len(cands) == 3 and all(c.color == ORANGE for c in cands)
    assert sorted(c.x for c in cands) == pytest.approx([200, 200 + w, 200 + 2 * w], abs=0.2 * w)


def test_find_ranks_by_strength_and_respects_the_limit():
    rgb = scene([(ORANGE, 200, 150), (BLUE, 250, 330), (ORANGE, 320, 500)])
    assert len(cn.find(rgb, CAM)) == 3
    one = cn.find(rgb, CAM, limit=1)
    assert len(one) == 1 and one[0].strength == max(c.strength for c in cn.find(rgb, CAM))
    assert cn.find(rgb, CAM, cn.Params(strength_min=50.0)) == []


def test_find_does_not_write_to_the_picture():
    rgb = scene([(ORANGE, 200, 200)])
    before = rgb.copy()
    cn.contrast_mask(rgb, None, CAM)
    assert (rgb == before).all()


# ---------------------------------------------------------------- own colors and the paint

def _measured(rgb, p=cn.Params()):
    resp = cn.respond(rgb, CAM, p)
    feat = cn.features(rgb, p.feat_offset, p.bright)
    cands = cn.find(rgb, CAM, p, resp=resp)
    for c in cands:
        cn.measure(c, resp, feat, p)
    return cands, resp, feat


def test_measure_reads_the_barrels_own_colors_and_its_surround():
    cands, _, _ = _measured(scene([(ORANGE, 200, 200)]))
    info = cands[0].info
    assert info["reasons"] == []
    assert info["chan_body"] > 1.0 and info["chan_stripe"] < -1.0 and info["orange_part"] == pytest.approx(info["chan_body"])
    assert info["alike"] == pytest.approx(0.0, abs=1e-6) and info["alike_feat"] == pytest.approx(0.0, abs=1e-6)
    assert all(info["off"][k] > 0.3 for k in ("left", "right", "above", "below"))        # the gray table is not the body color
    cands, _, _ = _measured(scene([(BLUE, 200, 200)]))
    assert cands[0].info["orange_part"] == pytest.approx(cands[0].info["chan_stripe"]) and cands[0].info["orange_part"] > 1.0


def test_guards_name_what_they_refuse():
    rgb = scene([(ORANGE, 200, 200)])
    assert _measured(rgb, cn.Params(orange_min=5.0))[0][0].info["reasons"] == ["orange_min"]
    assert _measured(rgb, cn.Params(d_min=50.0))[0][0].info["reasons"] == ["d_min"]
    assert _measured(rgb, cn.Params(extent_top=5.0, surround=5.0))[0][0].info["reasons"] == ["extent_top", "surround"]
    two = scene([(ORANGE, 200, 200)]).copy()                            # the lower body in another color: two things, not one body
    r = CAM.barrel_rows(200)
    two[int(round(r.stripe_bottom)):int(round(r.bottom)), 150:250] = (200, 60, 60)
    reasons = _measured(two, cn.Params(alike_feat=0.1))[0][0].info["reasons"]
    assert "alike_feat" in reasons


def test_paint_stays_inside_the_predicted_box_and_keeps_the_fixed_paint():
    rgb = scene([(ORANGE, 200, 200), (BLUE, 300, 420)])
    base = np.zeros((480, 640), np.uint8)
    base[100:104, 100:104] = BLUE                                       # the fixed model's paint somewhere else
    r = CAM.barrel_rows(200)
    y, x = int(r.top) + 3, 200
    base[y, x] = BLUE                                                   # ... and one (wrong) pixel on the orange barrel
    p = cn.Params()
    mask, cands = cn.contrast_mask(rgb, base, CAM, p)
    assert (mask[100:104, 100:104] == BLUE).all() and mask[y, x] == BLUE    # never overwritten
    for c in cands:
        x0, top, x1, bottom = c.box
        sx, sy = p.box_slack * (x1 - x0) + 1, p.box_slack * (bottom - top) + 1
        ys, xs = np.nonzero((mask != OTHER) & (base == OTHER))
        mine = (xs >= x0 - sx) & (xs < x1 + sx) & (ys >= top - sy) & (ys < bottom + sy)
        other = next(o for o in cands if o is not c)
        ox0, otop, ox1, obottom = other.box
        theirs = (xs >= ox0 - sx) & (xs < ox1 + sx) & (ys >= otop - sy) & (ys < obottom + sy)
        assert (mine | theirs).all()
    o = next(c for c in cands if c.color == ORANGE)
    assert o.info["painted"] > 0.8 * (r.bottom - r.top) * r.width_px
    assert mask[int(r.stripe_center), 200] == BLUE and mask[int(r.top) + 6, 205] == ORANGE and mask[int(r.bottom) - 4, 195] == ORANGE
    assert mask[int(r.bottom) + 12, 200] == OTHER and mask[int(r.stripe_center), int(200 + r.width_px)] == OTHER   # the table stays table


def test_the_detector_boxes_a_barrel_painted_by_the_contrast_path_alone():
    rgb = scene([(ORANGE, 200, 200), (BLUE, 300, 420)], light=(1.0, 0.75, 0.4))
    mask, _ = cn.contrast_mask(rgb, None, CAM)
    found = det.detect(mask, det.DetConfig(), CAM)
    assert sorted(b.color for b in found) == [ORANGE, BLUE]
    for b, (d, x) in zip(sorted(found, key=lambda b: b.bbox[0]), ((200, 200), (300, 420))):
        r = CAM.barrel_rows(d)
        assert abs(b.bbox[1] - r.top) <= 3 and abs(b.bbox[3] - r.bottom) <= 3 and abs((b.bbox[0] + b.bbox[2]) / 2 - x) <= 3


def test_contrast_mask_leaves_candidates_in_found_boxes_alone_and_refused_ones_unpainted():
    rgb = scene([(ORANGE, 200, 200), (BLUE, 300, 420)])
    r = CAM.barrel_rows(200)
    box = (int(200 - r.width_px / 2), int(r.top), int(200 + r.width_px / 2), int(r.bottom))
    mask, cands = cn.contrast_mask(rgb, np.zeros((480, 640), np.uint8), CAM, skip_boxes=(box,))
    o = next(c for c in cands if c.color == ORANGE)
    assert o.info == {"reasons": ["found_already"], "painted": 0}
    assert (mask[box[1]:box[3], box[0]:box[2]] == OTHER).all() and (mask == BLUE).any()
    mask, cands = cn.contrast_mask(rgb, None, CAM, cn.Params(orange_min=5.0))
    assert (mask == OTHER).all() and all(c.info["painted"] == 0 for c in cands)
