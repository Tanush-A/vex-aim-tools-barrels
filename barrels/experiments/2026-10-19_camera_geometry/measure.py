#!/usr/bin/env python3
"""Camera geometry of AIM-4A8B6118 from the calib + ruler frames (constraints.md unknowns #2, #3, #7).

    python barrels/experiments/2026-10-19_camera_geometry/measure.py

1. Focal length from barrel width: in each calib frame the barrel is segmented by color
   (orange or blue, saturated), the widest row of the silhouette is measured, and
   f = width_px * d / D with D = 22 mm and d = ruler distance + 3 (camera behind front edge)
   + 11 (barrel radius).
2. Tilt from the ruler frame: image rows of the centimeter marks (read by eye from an
   upscaled crop; see CM_MARK_ROWS) are fit to row = cy + f*tan(atan(h/d) - tilt) with
   h = 43.47 mm, d = 10*cm + 3, f fixed from step 1, cy = 240.
3. Tilt + f from the barrel bottom rows in the calib frames (ground contact at the near edge
   of the 18 mm base), as an independent cross-check.

The three estimates disagree at the ±10 % level (see EXPERIMENTS.md 2026-10-19): the ruler
zero offset, the eyeballed mark rows, and the contact-point assumption are the weak links.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import io  # noqa: E402

H_CAM = 43.47          # mm, aim_kin.py
D_BARREL = 80 / math.pi  # 25.5 mm: widest circumference 80 mm measured with a tape 2026-10-19 (draft spec said 22)
R_BASE = 9.0             # mm: barrel diameter at the base/lid is 18 mm (measured)
CAM_BEHIND_FRONT = 3.0 # mm, aim_kin.py tilt procedure
CY = 240
CALIB = {1: 50, 2: 100, 3: 150, 4: 200, 5: 300}   # calib_NN -> ruler distance front edge -> barrel near edge, mm
CM_MARK_ROWS = {4: 412, 5: 352, 6: 320, 7: 292, 8: 270, 9: 252, 10: 235}  # ruler_01, read by eye (±4 px)


def barrel_width(img: np.ndarray) -> tuple[int, int, tuple[int, int, int, int]]:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    orange = cv2.inRange(hsv, (0, 150, 60), (13, 255, 255)) | cv2.inRange(hsv, (170, 150, 60), (180, 255, 255))
    blue = cv2.inRange(hsv, (95, 90, 40), (130, 255, 255))
    m = cv2.morphologyEx(orange | blue, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    k = max((k for k in range(1, n) if abs(cen[k][0] - 320) < 120 and st[k, cv2.CC_STAT_AREA] > 30),
            key=lambda k: st[k, cv2.CC_STAT_AREA])
    ys, xs = np.where(lab == k)
    widths = {r: int(xs[ys == r].max() - xs[ys == r].min() + 1) for r in np.unique(ys)}
    r = max(widths, key=widths.get)
    return widths[r], int(r), (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


def row_model(cm: float, tilt_deg: float, f: float, cy: float = CY) -> float:
    d = 10 * cm + CAM_BEHIND_FRONT
    return cy + f * math.tan(math.atan(H_CAM / d) - math.radians(tilt_deg))


def main() -> int:
    print("## focal length from barrel width (D = 22 mm)")
    fs = []
    for i, dist in CALIB.items():
        img = io.load_image(io.RAW_DIR / f"4A8B_upcool_wood_calib_{i:02d}.png")
        w, r, bbox = barrel_width(img)
        d = dist + CAM_BEHIND_FRONT + D_BARREL / 2
        f = w * d / D_BARREL
        fs.append(f)
        print(f"calib_{i:02d}: ruler {dist:3} mm -> camera-to-center {d:5.0f} mm, width {w:3} px @row {r}, bbox {bbox}  f = {f:.0f}")
    f_med = float(np.median(fs))
    print(f"f median = {f_med:.0f} px  (spread {min(fs):.0f}–{max(fs):.0f})\n")

    print("## tilt from ruler marks (f fixed)")
    best = None
    for tilt in np.arange(18, 28, 0.05):
        err = sum((row_model(k, tilt, f_med) - r) ** 2 for k, r in CM_MARK_ROWS.items())
        if best is None or err < best[0]:
            best = (err, tilt)
    err, tilt = best
    print(f"tilt = {tilt:.2f} deg, rms {math.sqrt(err / len(CM_MARK_ROWS)):.1f} px")
    for k, r in CM_MARK_ROWS.items():
        print(f"  {k:2} cm: row {r} model {row_model(k, tilt, f_med):.1f}  resid {row_model(k, tilt, f_med) - r:+.1f}")
    horizon = CY - f_med * math.tan(math.radians(tilt))
    print(f"\nhorizon row = {horizon:.1f}")

    print("\n## cross-check: tilt + f from barrel bottom rows (contact at near edge of the 18 mm base)")
    bottoms = {}
    for i, dist in CALIB.items():
        img = io.load_image(io.RAW_DIR / f"4A8B_upcool_wood_calib_{i:02d}.png")
        bottoms[dist] = barrel_width(img)[2][3]
    best = None
    for tilt_b in np.arange(18, 30, 0.05):
        for f_b in np.arange(300, 480, 2):
            err = sum((CY + f_b * math.tan(math.atan(H_CAM / (dist + CAM_BEHIND_FRONT + D_BARREL / 2 - R_BASE)) - math.radians(tilt_b)) - b) ** 2
                      for dist, b in bottoms.items())
            if best is None or err < best[0]:
                best = (err, tilt_b, f_b)
    err, tilt_b, f_b = best
    print(f"tilt = {tilt_b:.2f} deg, f = {f_b:.0f}, rms {math.sqrt(err / 5):.1f} px, horizon row = {CY - f_b * math.tan(math.radians(tilt_b)):.1f}")
    print(f"bottom row sees ground at {H_CAM / math.tan(math.radians(tilt) + math.atan(240 / f_med)):.1f} mm from the camera")
    return 0


if __name__ == "__main__":
    sys.exit(main())
