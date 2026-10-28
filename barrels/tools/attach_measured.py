#!/usr/bin/env python3
"""Attach ruler-measured ground positions to the instance labels of the `meas` frames.

    python barrels/tools/attach_measured.py [--csv barrels/data/measured.csv] [--cam 4a8b] [--dry-run]

CSV columns: stem, idx, color, d_ruler_mm, lateral_mm, note
  idx          left-to-right order of the barrel in the image (1 = leftmost)
  d_ruler_mm   ruler reading from the robot's front-edge centre to the NEAR edge of the barrel's
               18 mm base, at table level, along the vertical crosshair
  lateral_mm   sideways offset of the barrel axis from the ruler line, left positive
Truth in the robot base frame (DATA.md): x = d_ruler + 30 (front edge from the centre) + 9 (base
radius), y = lateral. Each row is matched to the instance with the same left-to-right rank and
color; a count or color mismatch aborts the frame. Prints measured vs projected (from the bottom-mid
pixel through the camera model) so a mis-association is visible immediately.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import geometry as geo, io  # noqa: E402

CAMS = {"nominal": geo.NOMINAL, "4a8b": geo.AIM_4A8B6118}
FRONT_EDGE_MM = geo.FRONT_EDGE_FROM_ORIGIN_MM
BASE_R_MM = geo.BARREL_END_DIAMETER_MM / 2


def truth_xy(d_ruler_mm: float, lateral_mm: float) -> tuple[float, float]:
    return d_ruler_mm + FRONT_EDGE_MM + BASE_R_MM, lateral_mm


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, default=io.PKG_ROOT / "data" / "measured.csv")
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--cam", choices=sorted(CAMS), default="4a8b")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    cam = CAMS[args.cam]
    rows = defaultdict(list)
    with args.csv.open() as fh:
        for r in csv.DictReader(fh):
            rows[r["stem"]].append(r)
    n_ok = 0
    for stem, rs in sorted(rows.items()):
        try:
            inst, meta = io.load_instances(stem, args.labels)
        except (FileNotFoundError, ValueError) as ex:
            print(f"{stem}: SKIP ({ex})"); continue
        barrels = sorted(meta["barrels"], key=lambda b: b["bbox"][0])
        rs = sorted(rs, key=lambda r: int(r["idx"]))
        if len(barrels) != len(rs):
            print(f"{stem}: ABORT — {len(barrels)} instances but {len(rs)} CSV rows"); continue
        bad = [(b["color"], r["color"]) for b, r in zip(barrels, rs) if b["color"] != r["color"]]
        if bad:
            print(f"{stem}: ABORT — color mismatch in left-to-right order {bad}"); continue
        for b, r in zip(barrels, rs):
            tx, ty = truth_xy(float(r["d_ruler_mm"]), float(r["lateral_mm"]))
            px, py = cam.barrel_axis_xy(*b["bottom_mid"])
            b["ground_xy_mm"] = [tx, ty]; b["measured_idx"] = int(r["idx"])
            print(f"{stem} #{r['idx']} {r['color']:6} measured ({tx:6.1f}, {ty:6.1f})  projected ({px:6.1f}, {py:6.1f})  Δ {px - tx:+6.1f} / {py - ty:+6.1f} mm")
        if not args.dry_run:
            io.save_instances(stem, inst, meta, args.labels)
        n_ok += 1
    print(f"{n_ok} frame(s) {'checked' if args.dry_run else 'updated'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
