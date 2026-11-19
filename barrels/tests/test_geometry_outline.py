"""geometry additions of 2026-11-19 (the ruler calibration): the exact outline width, the named cameras."""
import math

import pytest

from barrels import geometry as g

CAM = g.CameraModel(f=400, tilt_deg=20.4, height_mm=40.2)


def test_ring_halfwidth_is_the_projection_of_the_tangent_points():
    for d, r, z in ((60.0, 12.75, 12.0), (150.0, 9.0, 24.0), (300.0, 12.75, 12.0)):
        ahead, side = (d * d - r * r) / d, r * math.sqrt(d * d - r * r) / d
        u, _ = CAM.ground_to_image(CAM.camera_from_origin_mm + ahead, side, z)       # the left tangent point, by the general projection
        assert CAM.ring_halfwidth_px(d, r, z) == pytest.approx(CAM.cx - u, abs=1e-9)
    assert math.isinf(CAM.ring_halfwidth_px(10.0, 12.75, 12.0))                     # the camera inside the ring


def test_silhouette_width_against_the_shortcut():
    """f * 25.5 / d uses the horizontal distance; the exact outline divides by the depth along the tilted axis."""
    for d in (40, 60, 100, 150, 200, 300):
        assert CAM.silhouette_width_px(d) >= 2 * CAM.ring_halfwidth_px(d, 12.75, 12.0) - 1e-9     # at least the bulge ring
    assert CAM.expected_barrel_width_px(155.0) == pytest.approx(CAM.silhouette_width_px(155.0), rel=0.02)   # they cross near 15 cm
    assert CAM.expected_barrel_width_px(300.0) / CAM.silhouette_width_px(300.0) == pytest.approx(0.97, abs=0.015)   # the shortcut is narrow far away
    assert CAM.expected_barrel_width_px(60.0) / CAM.silhouette_width_px(60.0) == pytest.approx(1.08, abs=0.03)      # and wide close up
    prev = math.inf
    for d in (30, 60, 120, 240, 480):
        w = CAM.silhouette_width_px(d)
        assert w < prev
        prev = w
    assert math.isinf(CAM.silhouette_width_px(9.0))
