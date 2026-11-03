#!/usr/bin/env python3
"""Fit the camera (f, tilt) from the train frames' ground-truth boxes (EXPERIMENTS.md 2026-11-03).

Hypothesis: the preset AIM_4A8B6118 (f 404, tilt 23.3) predicts bottoms ~20 px too low from the top row
on the v1 frames; one (f, tilt) pair exists that makes both the barrel height and the barrel width at
every row consistent with the known barrel (24 mm tall, 25.5 mm bulge) and camera height (43.47 mm).

Data: unflagged GT instances (bottom and both sides visible) on the 16 train frames; no test frames.
For each barrel the known-shape model must reproduce (a) its bottom row from its top row and (b) its width
at its bottom row. Grid search, then the residuals. Writes results/2026-11-03_geo_boxfit/.

    python barrels/experiments/2026-11-03_geo_boxfit/run.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import cv, geometry as geo, io, splits  # noqa: E402

OUT = io.PKG_ROOT / "results" / "2026-11-03_geo_boxfit"


def load_boxes() -> list[tuple[str, int, int, int, int]]:
    rows = []
    for stem in sorted(splits.load_splits()["train"]):
        _, meta = io.load_instances(stem)
        for b in meta["barrels"]:
            if b.get("flags"):
                continue
            x0, y0, x1, y1 = b["bbox"]
            if x0 == 0 or y0 == 0 or x1 == 640 or y1 == 480 or (x1 - x0) < 15:
                continue
            rows.append((stem, x0, y0, x1, y1))
    return rows


def residuals(cam: geo.CameraModel, boxes) -> tuple[np.ndarray, np.ndarray]:
    """(bottom-row error px, width error px) per box: predicted − measured."""
    eb, ew = [], []
    for _, x0, y0, x1, y1 in boxes:
        pb = cam.bottom_row_from_top_row(y0)
        pw = cam.expected_barrel_width_px(bottom_row=y1)
        eb.append((pb - y1) if math.isfinite(pb) else 1e3)
        ew.append((pw - (x1 - x0)) if math.isfinite(pw) else 1e3)
    return np.array(eb), np.array(ew)


def main() -> int:
    boxes = load_boxes()
    out = cv.fresh_dir(OUT)
    best = None
    grid = []
    for f in np.arange(280, 461, 2.0):
        for tilt in np.arange(15.0, 32.01, 0.25):
            cam = geo.CameraModel(f=float(f), tilt_deg=float(tilt))
            eb, ew = residuals(cam, boxes)
            cost = float(np.mean(eb ** 2) + np.mean(ew ** 2))
            grid.append((cost, float(f), float(tilt)))
            if best is None or cost < best[0]:
                best = (cost, float(f), float(tilt))
    cost, f, tilt = best
    fit = geo.CameraModel(f=f, tilt_deg=tilt)
    # f and tilt trade off (the cost surface is flat along a ridge), so also fit tilt with f held at the two
    # independently measured values (DATA.md calibration table: 356 from barrel widths; aim_fsm's 400)
    fixed = {}
    for f_fixed in (356.0, 400.0):
        c, _, t = min((c, ff, tt) for c, ff, tt in grid if abs(ff - f_fixed) < 1.01)
        fixed[f"f{int(f_fixed)}"] = geo.CameraModel(f=f_fixed, tilt_deg=t)
    report = {}
    for name, cam in (("preset_4A8B", geo.AIM_4A8B6118), ("nominal", geo.NOMINAL), ("boxfit_free", fit),
                      ("boxfit_f356", fixed["f356"]), ("boxfit_f400", fixed["f400"])):
        eb, ew = residuals(cam, boxes)
        report[name] = {"f": cam.f, "tilt_deg": cam.tilt_deg, "horizon_row": cam.horizon_row(),
                        "bottom_err_mean": float(eb.mean()), "bottom_err_abs_median": float(np.median(np.abs(eb))), "bottom_err_p90": float(np.percentile(np.abs(eb), 90)),
                        "width_err_mean": float(ew.mean()), "width_err_abs_median": float(np.median(np.abs(ew))), "width_err_p90": float(np.percentile(np.abs(ew), 90))}
    # how flat is the optimum? everything within 1.1x the best cost
    near = [(c, ff, tt) for c, ff, tt in grid if c <= 1.1 * cost]
    report["boxfit_free"]["flat_region"] = {"f": [min(x[1] for x in near), max(x[1] for x in near)], "tilt": [min(x[2] for x in near), max(x[2] for x in near)], "n": len(near)}
    json.dump({"n_boxes": len(boxes), "boxes": boxes, "best": {"cost": cost, "f": f, "tilt_deg": tilt}, "report": report, "git": cv.git_hash()},
              (out / "fit.json").open("w"), indent=1)
    print(f"{len(boxes)} unflagged train boxes")
    print(f"{'camera':12} {'f':>6} {'tilt':>6} {'horizon':>8} | bottom err: mean  |med|   p90 | width err: mean  |med|   p90")
    for k, r in report.items():
        print(f"{k:12} {r['f']:6.0f} {r['tilt_deg']:6.2f} {r['horizon_row']:8.1f} | {r['bottom_err_mean']:9.1f} {r['bottom_err_abs_median']:6.1f} {r['bottom_err_p90']:6.1f} | {r['width_err_mean']:9.1f} {r['width_err_abs_median']:6.1f} {r['width_err_p90']:6.1f}")
    print("flat region (cost within 10 % of best):", report["boxfit_free"]["flat_region"])
    print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
