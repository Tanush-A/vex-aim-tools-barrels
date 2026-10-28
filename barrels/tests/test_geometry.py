import math

import pytest

from barrels import geometry as g

NOM = g.NOMINAL


def test_horizon_rows_match_constraints():
    assert NOM.horizon_row() == pytest.approx(70.2, abs=0.1)
    assert g.AIM_4A8B6118.horizon_row() == pytest.approx(66.0, abs=0.2)
    assert g.CameraModel(f=355, tilt_deg=21.5).horizon_row() == pytest.approx(100.2, abs=0.2)
    assert g.CameraModel(f=405, tilt_deg=25.5).horizon_row() == pytest.approx(46.8, abs=0.2)
    assert g.CameraModel(f=400, tilt_deg=25.4).horizon_row() == pytest.approx(50.1, abs=0.2)
    assert g.CameraModel(f=400, tilt_deg=18.0).horizon_row() == pytest.approx(110.0, abs=0.2)


def test_row_to_ground_distance_and_round_trip():
    assert NOM.row_to_ground_distance(480) == pytest.approx(31.6, abs=0.05)
    assert g.AIM_4A8B6118.row_to_ground_distance(480) == pytest.approx(31.6, abs=0.1)
    assert NOM.row_to_ground_distance(400) == pytest.approx(43.8, abs=0.1)
    assert math.isinf(NOM.row_to_ground_distance(NOM.horizon_row()))
    assert math.isinf(NOM.row_to_ground_distance(10))
    for row in range(100, 480, 37):
        d = NOM.row_to_ground_distance(row)
        assert NOM.ground_distance_to_row(d) == pytest.approx(row, abs=1e-6)
    # farther ground -> smaller row, converging to the horizon
    assert NOM.ground_distance_to_row(500) - NOM.horizon_row() == pytest.approx(39.6, abs=0.2)
    assert NOM.ground_distance_to_row(2000) - NOM.horizon_row() == pytest.approx(10.2, abs=0.2)


def test_image_to_ground_replicates_project_to_ground():
    cam = g.WORLDMAP_CURRENT  # 23.7 deg / 400, as aim_kin.py has it today
    pinned = {(320, 240): (126.027, 0.0), (320, 480): (57.820, 0.0), (320, 300): (95.947, 0.0),
              (480, 300): (95.947, -32.242), (320, 150): (250.226, 0.0)}
    for (u, v), (x, y) in pinned.items():
        gx, gy = cam.image_to_ground(u, v)
        assert gx == pytest.approx(x, abs=1e-3) and gy == pytest.approx(y, abs=1e-3)
        bu, bv = cam.ground_to_image(gx, gy)
        assert bu == pytest.approx(u, abs=1e-6) and bv == pytest.approx(v, abs=1e-6)
    x, y = cam.image_to_ground(320, 10)          # above the horizon
    assert math.isinf(x)


def test_barrel_rows_and_inverses():
    r70 = NOM.barrel_rows(70)
    assert (r70.top, r70.bottom, r70.width_px) == pytest.approx((175.5, 328.5, 145.7), abs=0.2)
    r300 = NOM.barrel_rows(300)
    assert (r300.top, r300.bottom, r300.width_px) == pytest.approx((99.2, 136.5, 34.0), abs=0.2)
    prev = None
    for d in (40, 70, 100, 150, 300, 600):
        r = NOM.barrel_rows(d)
        assert NOM.horizon_row() < r.top < r.stripe_top < r.stripe_bottom < r.bottom
        if prev is not None:
            assert r.top < prev.top and r.bottom < prev.bottom and r.width_px < prev.width_px
        prev = r
        assert NOM.bottom_row_from_top_row(r.top) == pytest.approx(r.bottom, abs=1e-6)
        assert NOM.bottom_row_from_stripe_row(r.stripe_center) == pytest.approx(r.bottom, abs=1e-6)
        assert r.stripe_top < r.stripe_center < r.stripe_bottom
        assert NOM.bottom_row_from_width(r.width_px) == pytest.approx(r.bottom, abs=1e-6)
        assert NOM.d_axis_from_bottom_row(r.bottom) == pytest.approx(d, abs=1e-6)
        assert NOM.expected_barrel_width_px(bottom_row=r.bottom) == pytest.approx(r.width_px, abs=1e-6)
        assert NOM.expected_barrel_height_px(d) == pytest.approx(r.bottom - r.top, abs=1e-6)
    assert math.isinf(NOM.bottom_row_from_top_row(20))


def test_barrel_axis_xy_matches_worldmap_recipe():
    cam = g.WORLDMAP_CURRENT
    # worldmap: hit = project_to_ground(cx, cy); hit += 11 mm along atan2(hit.y, hit.x)
    for (u, v) in ((320, 300), (480, 300)):
        hx, hy = cam.image_to_ground(u, v)
        ang = math.atan2(hy, hx)
        ex, ey = hx + 11 * math.cos(ang), hy + 11 * math.sin(ang)
        ax, ay = cam.barrel_axis_xy(u, v, radius_mm=11.0)
        assert (ax, ay) == pytest.approx((ex, ey), abs=1e-9)
    ax9, _ = cam.barrel_axis_xy(320, 300)      # default = base radius 9
    assert ax9 == pytest.approx(cam.image_to_ground(320, 300)[0] + 9.0, abs=1e-9)


def test_presets_and_table():
    assert len(g.range_corners()) == 4
    t = g.markdown_table(NOM)
    assert "horizon row | ≈ 70" in t and "146 px wide" in t and "≈ 32 mm" in t
    assert g.main(["--tilt", "23", "--f", "400"]) == 0
