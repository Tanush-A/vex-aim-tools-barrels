"""The mask damage generator of the "detector given good segmentation" test: each kind does what its numbers say."""
import numpy as np

from barrels import degrade as dg, io

BOX = (300, 200, 360, 260)          # W = H = 60


def barrel_mask():
    m = np.zeros((480, 640), np.uint8)
    x0, y0, x1, y1 = BOX
    m[y0:y1, x0:x1] = io.ORANGE
    m[y0 + 25:y1 - 20, x0:x1] = io.BLUE          # the stripe, 15 rows
    return m


def test_no_damage_is_the_same_mask_and_the_input_is_never_changed():
    m = barrel_mask(); before = m.copy()
    assert (dg.damage(m, [BOX], dg.Damage()) == m).all()
    dg.damage(m, [BOX], dg.SEVERITIES["heavy"], seed=3)
    assert (m == before).all()


def test_same_seed_same_result_other_seed_other_result():
    m = barrel_mask()
    d = dg.SEVERITIES["medium"]
    assert (dg.damage(m, [BOX], d, seed=1) == dg.damage(m, [BOX], d, seed=1)).all()
    assert (dg.damage(m, [BOX], d, seed=1) != dg.damage(m, [BOX], d, seed=2)).any()


def test_damage_only_removes_barrel_pixels_except_the_specks():
    m = barrel_mask()
    for name, d in dg.SEVERITIES.items():
        out = dg.damage(m, [BOX], dg.Damage(**{**d.to_dict(), "speckle": 0}), seed=0)
        changed = out != m
        assert changed.any(), name
        assert (out[changed] == 0).all() and (m[changed] != 0).all(), name


def test_top_highlight_is_on_the_upper_body_and_as_big_as_stated():
    m = barrel_mask()
    out = dg.damage(m, [BOX], dg.Damage(top_highlight=(0.5, 0.3)), seed=0)
    ys, xs = np.where(out != m)
    x0, y0, x1, y1 = BOX
    assert ys.min() >= y0 and ys.max() <= y0 + 0.2 * 60 + 0.15 * 60 + 1          # centre a fifth down, half height 0.15 H
    assert xs.max() - xs.min() + 1 <= 0.5 * 60 + 2                               # 0.5 W wide
    assert 0.5 * np.pi * 15 * 9 <= len(ys) <= np.pi * 16 * 10                    # about the ellipse 30 x 18 (the part inside the box)
    assert (out[y0 + 25:y1 - 20] == m[y0 + 25:y1 - 20]).all()                    # the stripe is untouched


def test_stripe_highlight_and_breaks_cross_the_stripe():
    m = barrel_mask()
    x0, y0, x1, y1 = BOX
    out = dg.damage(m, [BOX], dg.Damage(stripe_highlight=0.3), seed=0)
    gone = (m == io.BLUE) & (out == 0)
    assert gone.any() and np.ptp(np.where(gone)[1]) + 1 <= 0.3 * 60 + 2
    out = dg.damage(m, [BOX], dg.Damage(stripe_breaks=(2, 0.1)), seed=0)
    cols = np.flatnonzero((out[y0 + 30] == 0)[x0:x1])                            # a row inside the stripe
    assert 6 <= len(cols) <= 12                                                  # two slits of 6 px (they may overlap)
    assert (out[y0:y0 + 14] == m[y0:y0 + 14]).all() and (out[y1 - 14:y1] == m[y1 - 14:y1]).all()   # only the middle half of the rows


def test_edges_are_eaten_by_the_stated_pixels_but_not_at_the_frame_edge():
    m = np.zeros((480, 640), np.uint8)
    m[100:120, 100:120] = io.ORANGE
    m[300:320, 0:20] = io.BLUE                                                   # touches the left frame edge
    out = dg.damage(m, [], dg.Damage(erode_px=2))
    ys, xs = np.where(out == io.ORANGE)
    assert (xs.min(), xs.max(), ys.min(), ys.max()) == (102, 117, 102, 117)
    ys, xs = np.where(out == io.BLUE)
    assert xs.min() == 0 and xs.max() == 17


def test_dropout_loses_about_the_stated_share():
    m = barrel_mask()
    out = dg.damage(m, [BOX], dg.Damage(dropout=0.10), seed=0)
    lost = ((m != 0) & (out == 0)).sum() / (m != 0).sum()
    assert 0.07 <= lost <= 0.13


def test_specks_are_small_outside_the_boxes_and_below_the_gate_row():
    m = barrel_mask()
    out = dg.damage(m, [BOX], dg.Damage(speckle=30), seed=0)
    added = (out != 0) & (m == 0)
    assert 30 * 4 * 0.5 <= added.sum() <= 30 * 9
    ys, xs = np.where(added)
    assert ys.min() >= dg.GATE_ROW
    x0, y0, x1, y1 = BOX
    assert not added[y0 - dg.SPECK_PAD:y1 + dg.SPECK_PAD, x0 - dg.SPECK_PAD:x1 + dg.SPECK_PAD].any()
    assert (out[m != 0] == m[m != 0]).all()                                      # the barrel itself is untouched


def test_severities_get_worse():
    m = barrel_mask()
    left = [int((dg.damage(m, [BOX], dg.Damage(**{**d.to_dict(), "speckle": 0}), seed=0) != 0).sum()) for d in dg.SEVERITIES.values()]
    assert left[0] > left[1] > left[2] > 0
