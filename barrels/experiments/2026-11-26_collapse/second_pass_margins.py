"""Second pass: how far from breaking are the facts behind B1, B13 and "a stripe's row gives a distance"?
For each camera and each set of numbers, every top row and every seen bottom row. usage: second_pass_margins.py <barrels/src>"""
import dataclasses
import math
import sys

sys.path.insert(0, sys.argv[1])
from barrels import detector as det, geometry as geo  # noqa: E402

BASE = det.DetConfig()


def facts(cam, cfg):
    h = cam.height
    max_ratio, short_pred, short_nopred, far, min_hs_mid = 0.0, 0, 0, 0, math.inf
    for y0 in range(h):
        if det.above_horizon(cam, y0):
            continue
        pred = det.predicted_bottom(cam, y0)
        for seen in range(y0 + 1, h + 1):
            y1, _ = det.resolve_bottom((0, y0, 10, seen), cam, h, cfg)
            W = cam.expected_barrel_width_px(bottom_row=y1) if y1 < h else det.expected_width_px((0, y0, 10, h), cam, h)
            if not math.isfinite(W) or W < cfg.min_width_px:
                continue
            if y1 < h and y0 > 0:
                H = cam.expected_barrel_height_px(bottom_row=y1)
                if math.isfinite(H):
                    max_ratio = max(max_ratio, (y1 - y0) / H)
                    if (y1 - y0) < cfg.height_min * H:
                        if math.isinf(pred):
                            short_nopred += 1
                        else:
                            short_pred += 1
                        continue
            close = y1 >= h or det._closeup_stripe_rows(cam, y0)[1] >= h
            if not close:
                at = det.BarrelAt.from_stripe_row(cam, (y0 + y1) / 2)
                hs = at.Hs if at else math.inf
                min_hs_mid = min(min_hs_mid, hs)
                far += hs < 4.0
    d_far = cam.f * geo.BARREL_BULGE_DIAMETER_MM / cfg.min_width_px
    hs_far = det.BarrelAt(d_far, cam.barrel_rows(d_far)).Hs
    halves = [k / 2 for k in range(0, 2 * h + 1)]
    ok = [det.BarrelAt.from_stripe_row(cam, r) is not None for r in halves]
    first = ok.index(True)
    return (f"tallest piece {max_ratio:.3f} x H | too short with a predicted bottom {short_pred}, with none {short_nopred} | "
            f"not a close-up: thinnest stripe at the middle row {min_hs_mid:.2f} px, under 4 px: {far} | stripe of the farthest barrel on the table "
            f"{hs_far:.2f} px | stripe rows: a distance from row {halves[first]} down without a gap: {all(ok[first:])}")


cams = [("BOXFIT", geo.AIM_4A8B6118_BOXFIT), ("NOMINAL", geo.NOMINAL), ("AIM_4A8B6118", geo.AIM_4A8B6118), ("WORLDMAP_CURRENT", geo.WORLDMAP_CURRENT)]
cams += [(f"corner f={c.f:.0f} tilt={math.degrees(c.tilt):.2f}", c) for c in geo.range_corners()]
for name, cam in cams:
    print(f"{name:28s} default numbers: {facts(cam, BASE)}", flush=True)
for name, cam in cams[:2]:
    for field, values in (("bottom_tol", (0.05, 0.10, 0.20, 0.25, 0.30, 0.40, 0.50)), ("bottom_tol_min_px", (2, 6, 8, 12)), ("min_width_px", (10.0, 12.0, 14.0, 20.0)),
                          ("height_min", (0.3, 0.7))):
        for v in values:
            print(f"{name:10s} {field}={v}: {facts(cam, dataclasses.replace(BASE, **{field: v}))}", flush=True)
