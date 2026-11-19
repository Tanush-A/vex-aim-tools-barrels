"""The damage instruments read back what ``degrade.damage`` put in (``experiments/2026-11-19_damage_realism``)."""
import numpy as np
import pytest

from barrels import damage_measure as dm, degrade as dg, io

BOX = (300, 200, 360, 260)          # W = H = 60
O, B = io.ORANGE, io.BLUE


def barrel_mask():
    m = np.zeros((480, 640), np.uint8)
    x0, y0, x1, y1 = BOX
    m[y0:y1, x0:x1] = O
    m[y0 + 25:y1 - 20, x0:x1] = B          # the stripe, 15 rows
    return m


def measure(d, seed=0):
    m = barrel_mask()
    return dm.measure_barrel(m, dg.damage(m, [BOX], d, seed=seed), BOX, O)


def test_column_runs_counts_pieces_breaks_and_ends():
    r = dm.column_runs(np.array([0, 1, 1, 0, 0, 1, 0, 1, 1, 0], bool), W=10)
    assert (r["pieces"], r["breaks"]) == (3, 2)
    assert r["break_w"] == pytest.approx(0.2) and r["end_gap"] == pytest.approx(0.2) and r["span"] == pytest.approx(0.8)
    r = dm.column_runs(np.ones(10, bool), W=10)
    assert (r["pieces"], r["breaks"], r["break_w"], r["end_gap"], r["span"]) == (1, 0, 0.0, 0.0, 1.0)
    r = dm.column_runs(np.zeros(10, bool), W=10)
    assert r["pieces"] == 0 and r["end_gap"] == 1.0 and np.isnan(r["break_w"])


def test_an_undamaged_barrel_measures_zero():
    m = barrel_mask()
    r = dm.measure_barrel(m, m, BOX, O)
    assert r["lost"] == 0 and r["dropout"] == 0 and r["edge_outer_px"] == 0 and r["edge_seam_px"] == 0
    assert r["holes"] == 0 and r["top_hole_w"] == 0 and r["stripe_hole_w"] == 0 and r["spill"] == 0
    assert (r["stripe_pieces"], r["stripe_breaks"], r["stripe_break_w"], r["stripe_end_gap"]) == (1, 0, 0.0, 0.0)
    assert r["stripe_thickness"] == 1.0 and r["px"] == 3600 and r["stripe_px"] == 900


@pytest.mark.parametrize("e", [1, 2, 3])
def test_eaten_edges_read_back_in_pixels_at_the_outline_and_at_the_seam(e):
    r = measure(dg.Damage(erode_px=e))
    assert r["edge_outer_px"] == pytest.approx(e) and r["edge_seam_px"] == pytest.approx(e)
    assert r["dropout"] == 0 and r["holes"] == 0                       # eaten rings are not holes
    assert r["stripe_thickness"] == pytest.approx((15 - 2 * e) / 15)
    assert r["stripe_breaks"] == 0 and r["stripe_end_gap"] == pytest.approx(2 * e / 60)


def test_dropout_reads_back_and_is_not_taken_for_eaten_edges_or_holes():
    r = measure(dg.Damage(dropout=0.10))
    assert 0.07 <= r["dropout"] <= 0.13 and 0.07 <= r["lost"] <= 0.13
    assert r["edge_outer_px"] < 0.3 and r["edge_seam_px"] < 0.3
    assert r["hole_area"] < 0.01 and r["stripe_breaks"] == 0


def test_top_highlight_reads_back_as_a_hole_of_its_size_on_the_upper_body():
    r = measure(dg.Damage(top_highlight=(0.5, 0.3)))
    assert r["top_hole_w"] == pytest.approx(0.5, abs=0.05) and r["top_hole_h"] == pytest.approx(0.3, abs=0.05)
    assert 0.3 <= r["top_hole_cx"] <= 0.7 and r["top_hole_cy"] == pytest.approx(0.2, abs=0.04)
    assert r["stripe_hole_w"] == 0 and r["stripe_breaks"] == 0 and r["edge_outer_px"] < 0.5 and r["dropout"] == 0


def test_stripe_highlight_and_breaks_read_back_across_the_stripe():
    r = measure(dg.Damage(stripe_highlight=0.3))
    assert r["stripe_hole_w"] == pytest.approx(0.3, abs=0.05)
    # the patch is round: only its middle columns lose the whole stripe, so the column reading is narrower than the patch
    assert 0.1 <= r["stripe_break_w"] + r["stripe_end_gap"] <= 0.3 and r["stripe_thickness"] == 1.0
    m = barrel_mask()
    out = m.copy()
    out[200:260, 310:314] = 0                                           # two slits, 4 and 6 px
    out[200:260, 340:346] = 0
    r = dm.measure_barrel(m, out, BOX, O)
    assert (r["stripe_pieces"], r["stripe_breaks"]) == (3, 2) and r["stripe_break_w"] == pytest.approx(0.1)


def test_everything_together_still_reads_each_kind():
    d = dg.Damage(top_highlight=(0.5, 0.3), stripe_breaks=(1, 0.1), erode_px=1, dropout=0.05)
    r = measure(d, seed=3)
    assert r["top_hole_w"] == pytest.approx(0.5, abs=0.08) and r["edge_outer_px"] == pytest.approx(1, abs=0.25)
    assert 0.03 <= r["dropout"] <= 0.07 and r["stripe_breaks"] >= 1 and r["stripe_break_w"] >= 0.1


def test_wrong_color_and_spill():
    m = barrel_mask()
    out = m.copy()
    out[200:210, 300:360] = B                                            # 600 body px painted the stripe color
    out[262:264, 300:360] = O                                            # 120 px of paint under the barrel
    r = dm.measure_barrel(m, out, BOX, O)
    assert r["wrong_color"] == pytest.approx(600 / 3600) and r["spill"] == pytest.approx(120 / 3600)


def test_measure_box_on_a_good_and_a_damaged_mask():
    m = barrel_mask()
    r = dm.measure_box(m, BOX, O)
    assert r["core_cov"] == 1 and r["upper_cov"] == 1 and (r["stripe_pieces"], r["stripe_breaks"]) == (1, 0)
    assert r["stripe_span"] == 1 and r["top_hole_w"] == 0 and r["mid_hole_w"] == 0
    r = dm.measure_box(dg.damage(m, [BOX], dg.Damage(top_highlight=(0.5, 0.3)), seed=0), BOX, O)
    assert r["top_hole_w"] == pytest.approx(0.5, abs=0.06) and 0.15 <= r["top_hole_h"] <= 0.3 and r["core_cov"] < 0.95
    out = m.copy()
    out[200:260, 325:331] = 0
    r = dm.measure_box(out, BOX, O)
    assert (r["stripe_pieces"], r["stripe_breaks"]) == (2, 1) and r["stripe_break_w"] == pytest.approx(0.1) and r["mid_hole_w"] == pytest.approx(0.1)
    assert dm.measure_box(np.zeros_like(m), BOX, O)["stripe_pieces"] == 0


def test_specks_are_counted_off_the_barrels_only():
    m = barrel_mask()
    out = dg.damage(m, [BOX], dg.Damage(speckle=30), seed=0)
    areas = dm.specks(out, [BOX], m)
    c = dm.speck_counts(areas)
    assert 20 <= c["specks"] <= 30 and c["blobs"] == 0 and c["largest"] <= 18      # 30 specks of 4 or 9 px; a few touch
    assert dm.specks(m, [BOX], m) == []
    out = m.copy()
    out[400:410, 100:110] = B                                            # a blue thing that is not a barrel
    out[203:206, 362:363] = O                                            # paint 2 px beside the box: the barrel's, not a speck
    assert dm.specks(out, [BOX]) == [100] and dm.speck_counts([100]) == {"specks": 0, "blobs": 1, "speck_px": 0, "largest": 100}
