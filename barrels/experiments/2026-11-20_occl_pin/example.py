#!/usr/bin/env python3
"""The worked example of the write-up, in numbers (no acceptance number comes from here): one scene of the scorecard,
what is seen, what each end costs, and the box before and after.

    python barrels/experiments/2026-11-20_occl_pin/example.py [--pool "HOME hand masks"] [--stem core_02] [--kind edge] [--amount 0.5] [--side L]
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OCCL = HERE.parent / "2026-11-19_det_occl"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(OCCL))
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("det_occl_run", OCCL / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
import pin_arms  # noqa: E402
from barrels import detector as det, occlude as oc  # noqa: E402

R.occl_arms = pin_arms


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="HOME hand masks")
    ap.add_argument("--stem", default="core_02")
    ap.add_argument("--kind", default="edge")
    ap.add_argument("--amount", type=float, default=0.5)
    ap.add_argument("--side", default="L")
    ap.add_argument("--lean", type=int, default=1)
    args = ap.parse_args(argv)
    pools, _ = R.build_sources(R.segmentations(R.train_stems()))
    cfg = pin_arms.ARMS["pin+thin"]
    for src in pools[args.pool]:
        if args.stem not in src.stem:
            continue
        sc = oc.make_scene(src, args.kind, args.amount, args.side, lean=args.lean)
        print(f"{src.stem} {'orange' if src.color == 1 else 'blue'}: true box {list(sc.target[1])} ({src.width} wide)")
        for s in det.find_stripes(sc.mask, R.CAM, cfg):
            if s.body != src.color:
                continue
            d, rows = det._stripe_geometry(R.CAM, s.center_row)
            W, H = rows.width_px, rows.bottom - rows.top
            x0, y0, x1, y1 = s.bbox
            span = det._body_span(sc.mask, s.body, x0, x1, max(0, int(round(rows.top))), int(round(rows.bottom)), y0, y1)
            sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if span else (x0, x1)
            costs = det._end_costs(s, sc.mask, R.CAM, cfg, sx0, sx1)
            print(f"  stripe piece {list(s.bbox)} thin {s.small}; its row {s.center_row:.1f} -> distance {d:.0f} mm, W {W:.1f}, H {H:.1f}, "
                  f"top {rows.top:.1f}, bottom {rows.bottom:.1f}")
            print(f"  seen columns {sx0} to {sx1} = {(sx1 - sx0) / W:.2f} W; window {det.LID_HALF * W:.1f} px; limit {cfg.pin_good} H = {cfg.pin_good * H:.1f} rows")
            print(f"  cost of the left end {costs[0]:.3f} H = {costs[0] * H:.1f} rows; of the right end {costs[1]:.3f} H = {costs[1] * H:.1f} rows")
        for a in ("base", "pin", "pin+thin"):
            preds = det.detect(sc.mask, pin_arms.ARMS[a], R.CAM)
            print(f"  {a}: " + (", ".join(f"{list(p.bbox)} overlap {det.box_iou(p.bbox, sc.target[1]):.2f}" for p in preds) or "no box"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
