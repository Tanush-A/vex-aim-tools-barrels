"""Camera geometry for the VEX AIM robot (docs/constraints.md, Geometry).

Pinhole camera at height ``height_mm`` above the ground plane, tilted ``tilt_deg`` below
horizontal, principal point (cx, cy), focal length f px. Everything is in millimetres and
640x480 pixels. Ground distances are measured horizontally from the camera unless a method
says "base frame" (robot origin; x forward, y left — the convention of aim_kin.project_to_ground).

The barrel is a bulged cylinder: 24 mm tall, 18 mm diameter at the lid/base, 25.5 mm at the
bulge, 6 mm stripe centred at mid-height. Its silhouette is bounded by the lid's FAR edge on
top and the base's NEAR edge on the bottom; its width is the bulge.

    python -m barrels.geometry [--tilt 23 --f 400]     prints the constraints.md table
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, replace

H_CAM_MM = 43.47                 # aim_kin.py camera_height
CAM_FROM_ORIGIN_MM = 27.0        # aim_kin.py camera_from_origin (camera is ahead of the robot centre)
FRONT_EDGE_FROM_ORIGIN_MM = 30.0 # body_diameter 60 / 2 -> the camera sits 3 mm behind the front edge
BARREL_HEIGHT_MM = 24.0
BARREL_END_DIAMETER_MM = 18.0
BARREL_BULGE_DIAMETER_MM = 25.5
STRIPE_HEIGHT_MM = 6.0
WORLDMAP_DIAMETER_MM = 22.0      # what worldmap.py's BarrelObj uses (adds half of it along the bearing)

_END_R = BARREL_END_DIAMETER_MM / 2
_BULGE_R = BARREL_BULGE_DIAMETER_MM / 2


@dataclass(frozen=True)
class BarrelRows:
    """Image rows of a barrel standing at horizontal distance d_axis (its axis) from the camera."""
    d_axis_mm: float
    top: float            # lid far edge, z = 24 mm, distance d + 9
    stripe_top: float     # z = 15 mm at the bulge's near edge, distance d - 12.75
    stripe_center: float  # z = 12 mm (NOT the mean of stripe_top/bottom: rows are nonlinear in height)
    stripe_bottom: float  # z = 9 mm
    bottom: float         # base near edge, z = 0, distance d - 9
    width_px: float       # bulge diameter at distance d


@dataclass(frozen=True)
class CameraModel:
    f: float = 400.0
    tilt_deg: float = 23.0
    cx: float = 320.0
    cy: float = 240.0
    height_mm: float = H_CAM_MM
    width: int = 640
    height: int = 480
    camera_from_origin_mm: float = CAM_FROM_ORIGIN_MM

    # ---------------------------------------------------------------- basics
    @property
    def tilt(self) -> float:
        return math.radians(self.tilt_deg)

    def horizon_row(self) -> float:
        """Row where the ground plane projects at infinite distance (rays exactly horizontal)."""
        return self.cy - self.f * math.tan(self.tilt)

    def point_row(self, d_mm: float, z_mm: float = 0.0) -> float:
        """Row of a point at horizontal distance d from the camera and height z above the ground."""
        if d_mm <= 0:
            raise ValueError("distance must be positive")
        return self.cy + self.f * math.tan(math.atan2(self.height_mm - z_mm, d_mm) - self.tilt)

    def row_to_ground_distance(self, row: float) -> float:
        """Horizontal distance from the camera of the ground point seen at ``row``; inf at/above the horizon."""
        angle = math.atan2(row - self.cy, self.f) + self.tilt      # angle below horizontal of the ray
        if angle <= 0:
            return math.inf
        return self.height_mm / math.tan(angle)

    def ground_distance_to_row(self, d_mm: float) -> float:
        return self.point_row(d_mm, 0.0)

    # ---------------------------------------------------------------- base frame (aim_kin convention)
    def image_to_ground(self, u: float, v: float) -> tuple[float, float]:
        """Ground point seen at pixel (u, v), in the robot base frame (x forward, y left), mm.
        Replicates aim_kin.AIMKinematics.project_to_ground (camera 27 mm ahead of the origin)."""
        up = (u - self.cx) / self.f
        vp = (v - self.cy) / self.f
        denom = math.sin(self.tilt) + vp * math.cos(self.tilt)
        if denom <= 1e-9:
            return math.inf, math.copysign(math.inf, -up) if up else 0.0
        z = self.height_mm / denom                                # distance along the optical axis
        x_fwd = self.camera_from_origin_mm + z * (math.cos(self.tilt) - vp * math.sin(self.tilt))
        y_left = -up * z
        return x_fwd, y_left

    def ground_to_image(self, x_fwd: float, y_left: float, z_mm: float = 0.0) -> tuple[float, float]:
        """Inverse of image_to_ground for a point at height z (base frame, mm)."""
        d = x_fwd - self.camera_from_origin_mm                      # horizontal distance ahead of the camera
        dz = self.height_mm - z_mm
        # camera-frame forward coordinate along the optical axis and vertical offset
        zc = d * math.cos(self.tilt) + dz * math.sin(self.tilt)
        vc = dz * math.cos(self.tilt) - d * math.sin(self.tilt)
        if zc <= 0:
            raise ValueError("point is behind the camera")
        return self.cx - self.f * y_left / zc, self.cy + self.f * vc / zc

    def barrel_axis_xy(self, u_bottom_mid: float, v_bottom_mid: float, radius_mm: float = _END_R) -> tuple[float, float]:
        """worldmap.py's recipe: project the bottom-edge midpoint to the ground, then step ``radius_mm``
        further along the bearing to reach the barrel axis. radius 11 reproduces worldmap exactly;
        the physically right value is the base radius (9)."""
        x, y = self.image_to_ground(u_bottom_mid, v_bottom_mid)
        if math.isinf(x):
            return x, y
        ang = math.atan2(y, x)
        return x + radius_mm * math.cos(ang), y + radius_mm * math.sin(ang)

    # ---------------------------------------------------------------- barrels
    def barrel_rows(self, d_axis_mm: float) -> BarrelRows:
        return BarrelRows(
            d_axis_mm=d_axis_mm,
            top=self.point_row(d_axis_mm + _END_R, BARREL_HEIGHT_MM),
            stripe_top=self.point_row(d_axis_mm - _BULGE_R, BARREL_HEIGHT_MM / 2 + STRIPE_HEIGHT_MM / 2),
            stripe_center=self.point_row(d_axis_mm - _BULGE_R, BARREL_HEIGHT_MM / 2),
            stripe_bottom=self.point_row(d_axis_mm - _BULGE_R, BARREL_HEIGHT_MM / 2 - STRIPE_HEIGHT_MM / 2),
            bottom=self.point_row(d_axis_mm - _END_R, 0.0),
            width_px=self.f * BARREL_BULGE_DIAMETER_MM / d_axis_mm,
        )

    def d_axis_from_bottom_row(self, bottom_row: float) -> float:
        return self.row_to_ground_distance(bottom_row) + _END_R

    def expected_barrel_width_px(self, d_axis_mm: float | None = None, *, bottom_row: float | None = None) -> float:
        d = d_axis_mm if d_axis_mm is not None else self.d_axis_from_bottom_row(bottom_row)
        return self.f * BARREL_BULGE_DIAMETER_MM / d

    def expected_barrel_height_px(self, d_axis_mm: float | None = None, *, bottom_row: float | None = None) -> float:
        d = d_axis_mm if d_axis_mm is not None else self.d_axis_from_bottom_row(bottom_row)
        r = self.barrel_rows(d)
        return r.bottom - r.top

    def _d_axis_from_point_row(self, row: float, z_mm: float, offset_mm: float) -> float:
        """Axis distance for a barrel whose point at height z and horizontal offset ``offset`` from the axis sits at ``row``."""
        angle = math.atan2(row - self.cy, self.f) + self.tilt
        if angle <= 0:
            return math.inf
        return (self.height_mm - z_mm) / math.tan(angle) - offset_mm

    def bottom_row_from_top_row(self, top_row: float) -> float:
        """Where the base must be if the lid's far edge is at ``top_row`` (24 mm tall barrel)."""
        d = self._d_axis_from_point_row(top_row, BARREL_HEIGHT_MM, +_END_R)
        return math.inf if math.isinf(d) else self.barrel_rows(d).bottom

    def bottom_row_from_stripe_row(self, stripe_center_row: float) -> float:
        d = self._d_axis_from_point_row(stripe_center_row, BARREL_HEIGHT_MM / 2, -_BULGE_R)
        return math.inf if math.isinf(d) else self.barrel_rows(d).bottom

    def bottom_row_from_width(self, width_px: float) -> float:
        d = self.f * BARREL_BULGE_DIAMETER_MM / width_px
        return self.barrel_rows(d).bottom

    def with_(self, **kw) -> "CameraModel":
        return replace(self, **kw)


NOMINAL = CameraModel()                                      # Dave's 23 deg / 400 px
AIM_4A8B6118 = CameraModel(f=404.0, tilt_deg=23.3)           # best single fit, 2026-10-19 (horizon 66)
AIM_4A8B6118_RANGE = {"f": (355.0, 405.0), "tilt_deg": (21.5, 25.5)}   # the honest ranges (EXPERIMENTS.md 2026-10-19)
WORLDMAP_CURRENT = CameraModel(f=400.0, tilt_deg=23.7)       # aim_kin.py's live constant (another robot)


def range_corners(center: CameraModel = AIM_4A8B6118, rng: dict = AIM_4A8B6118_RANGE) -> list[CameraModel]:
    return [center.with_(f=f, tilt_deg=t) for f in rng["f"] for t in rng["tilt_deg"]]


def markdown_table(cam: CameraModel) -> str:
    lines = [f"| | value (tilt {cam.tilt_deg:g}°, f {cam.f:g} px, barrel 24 × 25.5 mm) |", "|---|---|",
             f"| horizon row | ≈ {cam.horizon_row():.0f} |",
             f"| bottom row ({cam.height}) sees the ground at | ≈ {cam.row_to_ground_distance(cam.height):.0f} mm from the camera |"]
    for d, label in ((70, "the `close` scene"), (150, "`core`"), (300, "worldmap's max range")):
        r = cam.barrel_rows(d)
        lines.append(f"| barrel axis at {d} mm ({label}) | rows ≈ {r.top:.0f}–{r.bottom:.0f}, ≈ {r.width_px:.0f} px wide |")
    hz = cam.horizon_row()
    lines.append(f"| ground at 0.5 m / 2 m | ≈ {cam.ground_distance_to_row(500) - hz:.0f} px / ≈ {cam.ground_distance_to_row(2000) - hz:.0f} px below the horizon |")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="print the constraints.md geometry table")
    ap.add_argument("--tilt", type=float, default=NOMINAL.tilt_deg)
    ap.add_argument("--f", type=float, default=NOMINAL.f)
    a = ap.parse_args(argv)
    print(markdown_table(CameraModel(f=a.f, tilt_deg=a.tilt)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
