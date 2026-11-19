"""The stencil second opinion (``barrels.stencil``): the rendering, the score, the arbitration, on synthetic masks.
What it is worth on real frames is measured by experiments/2026-11-20_stencil, not here."""
import dataclasses

import numpy as np
import pytest

from barrels import geometry as geo, stencil as stn
from barrels.detect_types import Barrel
from barrels.io import BLUE, ORANGE

CAM = geo.AIM_4A8B6118_BOXFIT
CFG = dataclasses.replace(stn.StencilConfig(), accept=0.3, absent_cost=0.25, outside_cost=0.5, band_full=1.0)     # pinned: the tests do not move with the calibration
H, W = 480, 640


def stencil_of(width: float) -> stn.Stencil:
    return min(stn.stencils(CAM, CFG), key=lambda s: abs(s.W - width))


def paint(mask, st, color, u, dy=0):
    """A perfect barrel of this stencil's size: its box in the body color, its stripe rows in the other color."""
    x0, y0, x1, y1 = st.box(u, dy)
    mask[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = color
    mask[st.s_top + dy:st.s_bot + dy, max(0, x0):max(0, x1)] = stn.OTHER[color]
    return (max(0, x0), max(0, y0), min(W, x1), min(H, y1))


def iou(a, b):
    iw = max(0, min(a[2], b[2]) - max(a[0], b[0])); ih = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return iw * ih / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - iw * ih)


# ---------------------------------------------------------------- the stencils and their picture

def test_stencils_grow_five_percent_at_a_time_and_nearer_is_lower_and_larger():
    sts = stn.stencils(CAM, CFG)
    assert sts[0].W == 16 and sts[-1].W <= CFG.max_width_px
    for a, b in zip(sts, sts[1:]):
        assert a.W < b.W <= a.W * 1.13 + 1 and a.d_mm > b.d_mm
        assert a.bottom <= b.bottom and (a.bottom - a.top) <= (b.bottom - b.top)
    for s in sts:
        assert s.top < s.s_top < s.s_bot < s.bottom
        b = s.bands()
        assert all(b[k][1] > b[k][0] for k in ("U", "S", "L", "Ur", "Lr", "top", "bot"))


def test_a_stencil_follows_the_camera_model_at_its_distance():
    st = stn.make_stencil(CAM, 200.0, dataclasses.replace(CFG, top_fit=(0.0, 0.0), bottom_fit=(0.0, 0.0)))
    r = CAM.barrel_rows(200.0)
    assert (st.W, st.top, st.s_top, st.s_bot, st.bottom) == (round(r.width_px), round(r.top), round(r.stripe_top), round(r.stripe_bottom), round(r.bottom))
    fit = stn.make_stencil(CAM, 200.0, dataclasses.replace(CFG, top_fit=(2.0, 0.0), bottom_fit=(-3.0, 0.1)))
    assert fit.top == round(r.top + 2.0) and fit.bottom == round(r.bottom - 3.0 + 0.1 * r.width_px)


def test_render_body_stripe_body_with_rounded_corners_and_a_ring_outside():
    st = stencil_of(50)
    lab, (c_off, r_off) = stn.render(st)
    assert c_off == -st.pad and r_off == st.top - st.pad
    box = lab[st.pad:-st.pad, st.pad:-st.pad]                       # the box itself
    assert box.shape == (st.bottom - st.top, st.W)
    mid = box[:, st.W // 2]
    seq = [v for i, v in enumerate(mid) if v and (i == 0 or mid[i - 1] != v)]
    assert seq == [stn.U, stn.S, stn.L]                              # top to bottom: body, stripe, body
    assert not (box == stn.HALO).any()
    assert (box[:, 0] == stn.U).sum() < (mid == stn.U).sum() and (box[:, 0] == stn.L).sum() < (mid == stn.L).sum()   # corners
    assert (box[:, 0] == stn.S).sum() == (mid == stn.S).sum()
    assert (lab[:st.halo] == stn.HALO).any() and (lab[-st.halo:] == stn.HALO).any()
    assert (lab[:, :st.halo] == stn.HALO).any() and (lab[:, -st.halo:] == stn.HALO).any()
    assert set(np.unique(lab[:, :st.pad])) <= {stn.NONE, stn.HALO}
    lab2, (_, r2) = stn.render(st, dy=3)
    assert r2 == r_off + 3 and (lab2 == lab).all()


# ---------------------------------------------------------------- the score

def test_a_perfect_barrel_scores_near_one_and_an_empty_place_zero():
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    paint(m, st, ORANGE, 300)
    r = stn.score_at(m, st, ORANGE, 300, 0, CFG)
    assert r["seen"] > 0.99 and r["missing"] < 0.01 and r["outside"] == 0 and r["score"] > 0.99
    assert stn.score_at(m, st, BLUE, 300, 0, CFG)["score"] <= 0          # the wrong color: every band is wrong
    assert stn.score_at(m, st, ORANGE, 100, 0, CFG)["score"] <= 0
    e = stn.score_at(np.zeros((H, W), np.uint8), st, ORANGE, 300, 0, CFG)
    assert e["seen"] == 0 and e["missing"] == pytest.approx(1.0) and e["score"] == pytest.approx(-CFG.absent_cost)


def test_a_column_is_worth_its_worst_band():
    st = stencil_of(50)
    block = np.zeros((H, W), np.uint8); block[st.top:st.bottom, 300:300 + st.W] = ORANGE         # a barrel-sized orange block: no stripe
    assert stn.score_at(block, st, ORANGE, 300, 0, CFG)["seen"] == 0
    bar = np.zeros((H, W), np.uint8); bar[st.s_top:st.s_bot, 300:300 + st.W] = BLUE              # a stripe with nothing above or below
    assert stn.score_at(bar, st, ORANGE, 300, 0, CFG)["seen"] == 0
    half = np.zeros((H, W), np.uint8); paint(half, st, ORANGE, 300); half[:st.s_top] = 0        # stripe + lower body, no upper body
    assert stn.score_at(half, st, ORANGE, 300, 0, CFG)["seen"] == 0


def test_band_full_a_band_with_a_hole_is_not_a_missing_band():
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    paint(m, st, ORANGE, 300)
    u0, u1 = st.bands()["U"]
    m[u0 + 2:u1, 300:300 + st.W] = 0                                    # a highlight: only 2 rows of upper body are left, in every column
    share = 2 / (u1 - u0)
    centre = (st.W - 2 * st.rim) / st.W                                 # in the rim columns the upper body starts below those 2 rows: worth 0
    assert st.bands()["Ur"][0] >= u0 + 2
    strict = stn.score_at(m, st, ORANGE, 300, 0, CFG)
    soft = stn.score_at(m, st, ORANGE, 300, 0, dataclasses.replace(CFG, band_full=0.25))
    assert strict["seen"] == pytest.approx(centre * share, abs=0.01)    # the painted share of the worst band
    assert soft["seen"] == pytest.approx(centre * min(1.0, share / 0.25), abs=0.01) and soft["seen"] > 2 * strict["seen"]
    m[u0:u1, 300:300 + st.W] = 0                                        # no upper body at all: still nothing, however soft
    assert stn.score_at(m, st, ORANGE, 300, 0, dataclasses.replace(CFG, band_full=0.25))["seen"] == 0
    cum = {c: stn._cum_rows(m == c) for c in (ORANGE, BLUE)}
    m2 = np.zeros((H, W), np.uint8); paint(m2, st, ORANGE, 300); m2[u0 + 2:u1, 300:300 + st.W] = 0
    cum = {c: stn._cum_rows(m2 == c) for c in (ORANGE, BLUE)}
    soft_cfg = dataclasses.replace(CFG, band_full=0.25)
    q = stn.score_map(st, ORANGE, cum, np.array([0]), soft_cfg, (H, W))
    assert q[0, 300 + st.W] == pytest.approx(stn.score_at(m2, st, ORANGE, 300, 0, soft_cfg)["score"], abs=1e-9)


def test_touching_barrels_each_get_their_best_place_not_a_shifted_copy():
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    boxes = [paint(m, st, c, 200 + i * st.W) for i, c in enumerate((ORANGE, BLUE, ORANGE, BLUE))]
    out = stn.detect(m, dataclasses.replace(CFG, accept=0.15), CAM)
    assert len(out) == 4
    for o, b in zip(out, boxes):
        assert iou(o.bbox, b) > 0.85 and o.confidence > 0.85


def test_hidden_by_an_unpainted_thing_costs_and_hidden_by_the_frame_does_not():
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    paint(m, st, ORANGE, 300); m[:, 300 + st.W // 2:] = 0               # the right half behind something that is not painted
    r = stn.score_at(m, st, ORANGE, 300, 0, CFG)
    v = (st.W // 2) / st.W
    assert r["seen"] == pytest.approx(v, abs=0.01) and r["missing"] == pytest.approx(1 - v, abs=0.01)
    assert r["score"] == pytest.approx(v - CFG.absent_cost * (1 - v), abs=0.02)
    f = np.zeros((H, W), np.uint8); paint(f, st, ORANGE, -(st.W // 2))  # the left half outside the frame
    r = stn.score_at(f, st, ORANGE, -(st.W // 2), 0, CFG)
    assert r["seen"] == pytest.approx(1 - v, abs=0.01) and r["missing"] < 0.01 and r["explained"] == pytest.approx(v, abs=0.01)


def test_paint_outside_the_outline_says_the_thing_is_bigger():
    small, big = stencil_of(40), stencil_of(60)
    m = np.zeros((H, W), np.uint8); paint(m, big, BLUE, 300)
    u = 300 + (big.W - small.W) // 2
    dy = (big.s_top + big.s_bot) // 2 - (small.s_top + small.s_bot) // 2  # the small stencil's stripe inside the big barrel's
    r = stn.score_at(m, small, BLUE, u, dy, CFG)
    assert r["outside"] > 0.8 and r["score"] < stn.score_at(m, big, BLUE, 300, 0, CFG)["score"] - 0.3


def test_claimed_pixels_are_no_evidence_and_a_nearer_barrel_hides():
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    x0, y0, x1, y1 = paint(m, st, ORANGE, 300)
    claimed = np.zeros((H, W), bool); claimed[y0:y1, x0 + st.W // 2:x1] = True
    taken = stn.score_at(m, st, ORANGE, 300, 0, CFG, claimed=claimed)                     # claimed by a barrel that does not stand nearer
    hidden = stn.score_at(m, st, ORANGE, 300, 0, CFG, claimed=claimed, hidden=claimed)    # ... by one that does
    assert taken["missing"] == pytest.approx(0.5, abs=0.02) and hidden["missing"] < 0.01
    assert hidden["seen"] == pytest.approx(0.5, abs=0.02) == pytest.approx(taken["seen"], abs=0.02)
    assert hidden["score"] > taken["score"]


def test_the_fast_scorer_gives_the_same_numbers_as_counting_pixels():
    rng = np.random.default_rng(0)
    sts = stn.stencils(CAM, CFG)
    m = np.zeros((H, W), np.uint8)
    a, b = stencil_of(48), stencil_of(90)
    paint(m, a, ORANGE, 200); paint(m, b, BLUE, 215); paint(m, a, BLUE, 2 - a.W // 2); paint(m, stencil_of(250), ORANGE, 380)
    m[rng.random(m.shape) < 0.1] = 0                                                       # holes
    m[(rng.random(m.shape) < 0.01) & (np.arange(H)[:, None] > 60)] = BLUE                  # specks
    claimed = np.zeros((H, W), bool); claimed[150:260, 215:300] = True
    hidden = np.zeros((H, W), bool); hidden[150:260, 215:300] = True
    cum = {c: stn._cum_rows((m == c) & ~claimed) for c in (ORANGE, BLUE)}
    for with_claim in (False, True):
        cu = cum if with_claim else {c: stn._cum_rows(m == c) for c in (ORANGE, BLUE)}
        ch = stn._cum_rows(hidden) if with_claim else None
        for _ in range(25):
            st = sts[int(rng.integers(len(sts)))]; color = int(rng.integers(1, 3)); dys = stn.offsets(st, CFG)
            q = stn.score_map(st, color, cu, dys, CFG, (H, W), ch)
            assert q.shape == (len(dys), W + st.W)
            for i, j in [np.unravel_index(int(np.argmax(q)), q.shape), (int(rng.integers(len(dys))), int(rng.integers(q.shape[1])))]:
                ref = stn.score_at(m, st, color, int(j) - st.W, int(dys[i]), CFG, claimed=claimed if with_claim else None, hidden=hidden if with_claim else None)
                assert q[i, j] == pytest.approx(ref["score"], abs=1e-9)


# ---------------------------------------------------------------- detect: accept, claim, hide, again

def test_nothing_in_nothing_out_and_one_barrel_one_box():
    assert stn.detect(np.zeros((H, W), np.uint8), CFG, CAM) == []
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    box = paint(m, st, BLUE, 300)
    out = stn.detect(m, CFG, CAM)
    assert len(out) == 1 and out[0].color == BLUE and iou(out[0].bbox, box) > 0.85 and out[0].source == "stencil"
    assert abs(out[0].bbox[3] - box[3]) <= 2


def test_a_block_a_bar_and_specks_are_not_barrels():
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    m[st.top:st.bottom, 100:100 + st.W] = ORANGE                       # a block of body color
    m[st.s_top:st.s_bot, 300:300 + st.W] = BLUE                        # a bar of stripe color
    rng = np.random.default_rng(1)
    for _ in range(60):
        y, x = int(rng.integers(60, 470)), int(rng.integers(0, 630))
        m[y:y + 3, x:x + 3] = int(rng.integers(1, 3))
    assert stn.detect(m, CFG, CAM) == []


def test_two_touching_barrels_of_one_color_are_two_boxes():
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    a = paint(m, st, ORANGE, 250); b = paint(m, st, ORANGE, 250 + st.W)
    out = stn.detect(m, CFG, CAM)
    assert len(out) == 2 and all(o.color == ORANGE for o in out)
    assert iou(out[0].bbox, a) > 0.7 and iou(out[1].bbox, b) > 0.7


def test_a_barrel_behind_a_barrel_is_explained_by_the_front_one():
    back, front = stencil_of(46), stencil_of(80)
    m = np.zeros((H, W), np.uint8)
    bb = paint(m, back, BLUE, 300)                                     # the far barrel first ...
    fb = paint(m, front, ORANGE, 300 + back.W // 2 - 4)                # ... then the near one over its right half
    alone = np.zeros((H, W), np.uint8); paint(alone, back, BLUE, 300); alone[:, 300 + back.W // 2 - 4:] = 0
    out = stn.detect(m, CFG, CAM)
    assert sorted(o.color for o in out) == [ORANGE, BLUE]
    got = {o.color: o for o in out}
    assert iou(got[ORANGE].bbox, fb) > 0.85 and iou(got[BLUE].bbox, bb) > 0.6
    # the same half barrel with nothing found in front of it scores lower: its missing half is unexplained
    lone = stn.detect(alone, dataclasses.replace(CFG, accept=0.05), CAM)
    assert lone and max(o.confidence for o in lone) < got[BLUE].confidence
    # given the front barrel, only the back one comes back
    again = stn.detect(m, CFG, CAM, given=[Barrel(color=ORANGE, bbox=fb)])
    assert [o.color for o in again] == [BLUE] and iou(again[0].bbox, bb) > 0.6


def test_a_slice_with_nothing_saying_which_side_is_hidden_gets_the_box_in_the_middle():
    st = stencil_of(60); m = np.zeros((H, W), np.uint8)
    paint(m, st, ORANGE, 300)
    lo, hi = 300 + st.W // 4, 300 + st.W - st.W // 4                   # both sides cut: the middle half shows
    m[:, :lo] = 0; m[:, hi:] = 0
    out = stn.detect(m, dataclasses.replace(CFG, accept=0.2), CAM)
    assert len(out) == 1 and "occluded" in out[0].flags
    cx = (out[0].bbox[0] + out[0].bbox[2]) / 2
    assert abs(cx - (lo + hi) / 2) <= 3 and abs((out[0].bbox[2] - out[0].bbox[0]) - st.W) <= 6


def test_a_barrel_cut_by_the_frame_gets_its_box_into_the_edge():
    st = stencil_of(60); m = np.zeros((H, W), np.uint8)
    box = paint(m, st, BLUE, -st.W // 2)
    out = stn.detect(m, CFG, CAM)
    assert len(out) == 1 and out[0].bbox[0] == 0 and "truncated" in out[0].flags and iou(out[0].bbox, box) > 0.7


# ---------------------------------------------------------------- the stencil as a checker

def test_box_score_is_high_on_a_barrel_and_low_on_a_box_drawn_on_something_else():
    st = stencil_of(50); m = np.zeros((H, W), np.uint8)
    box = paint(m, st, ORANGE, 300)
    m[st.top:st.bottom, 100:100 + st.W] = ORANGE
    assert stn.box_score(m, Barrel(color=ORANGE, bbox=box), CFG, CAM) > 0.9
    assert stn.box_score(m, Barrel(color=ORANGE, bbox=(100, st.top, 100 + st.W, st.bottom)), CFG, CAM) <= 0.0
    assert stn.box_score(m, Barrel(color=BLUE, bbox=box), CFG, CAM) <= 0.0


def test_the_shortcut_changes_no_answer():
    back, front = stencil_of(46), stencil_of(80)
    m = np.zeros((H, W), np.uint8)
    paint(m, back, BLUE, 300); paint(m, front, ORANGE, 300 + back.W // 2 - 4); paint(m, stencil_of(30), ORANGE, 100)
    m[np.random.default_rng(3).random(m.shape) < 0.05] = 0
    cfg = dataclasses.replace(CFG, accept=0.15)
    a, b = stn.detect(m, cfg, CAM), stn.detect(m, cfg, CAM, shortcut=False)
    assert len(a) >= 3 and [(x.color, x.bbox, round(x.confidence, 9)) for x in a] == [(x.color, x.bbox, round(x.confidence, 9)) for x in b]


def test_same_barrel_same_color_same_place_same_depth():
    rule_box = Barrel(color=BLUE, bbox=(404, 117, 449, 163))
    assert stn.same_barrel(Barrel(color=BLUE, bbox=(421, 122, 470, 173)), rule_box, CFG)          # a second box on the barrel, a third off
    assert not stn.same_barrel(Barrel(color=ORANGE, bbox=(421, 122, 470, 173)), rule_box, CFG)    # another color: another barrel
    assert not stn.same_barrel(Barrel(color=BLUE, bbox=(445, 117, 490, 163)), rule_box, CFG)      # touching beside it: under a quarter shared
    assert not stn.same_barrel(Barrel(color=BLUE, bbox=(410, 100, 445, 140)), rule_box, CFG)      # behind it (bottom 23 rows higher): a barrel further away
    assert stn.same_barrel(Barrel(color=BLUE, bbox=(410, 120, 445, 162)), rule_box, CFG)          # bottom 1 row higher: not further away
