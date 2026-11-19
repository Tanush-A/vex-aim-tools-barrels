#!/usr/bin/env python3
"""A viewing aid (no number comes from here): one scene of the occlusion scorecard as text, with the boxes drawn and
the detector's reason log, for one arm.

    python barrels/experiments/2026-11-19_det_occl/look.py edge 0.75 --pool CAMPUS --stem hand_02 --color blue --side L --arm base
Row keys as in run.py (edge, slant, both, top, bottom, post, frame, barrel_side/same, block/other, ...).
Also writes results/2026-11-19_det_occl/zoom/<arm>_<row>_<amount>_<stem>.png (ignored by git).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("det_occl_run", HERE / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
from barrels import detect_types as dtp, detector as det, occlude as oc  # noqa: E402

CH = {0: ".", 1: "o", 2: "B", 255: "?"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("row"); ap.add_argument("amount", type=float)
    ap.add_argument("--pool", default="HOME hand", help="start of the pool's name")
    ap.add_argument("--stem", default=""); ap.add_argument("--color", default="")
    ap.add_argument("--side", default="L"); ap.add_argument("--lean", type=int, default=1)
    ap.add_argument("--arm", default="base")
    ap.add_argument("--no-text", action="store_true")
    args = ap.parse_args(argv)
    segs = R.segmentations(R.train_stems())
    pools, _ = R.build_sources(segs)
    pool = next(p for p in R.POOLS if p.startswith(args.pool))
    ki, (key, name, kind, color) = next((i, r) for i, r in enumerate(R.ROWS) if r[0] == args.row)
    n = 0
    for si, src in enumerate(pools[pool]):
        if args.stem not in src.stem or (args.color and dtp.COLOR_NAMES[src.color] != args.color):
            continue
        rng = np.random.default_rng([R.SEED, si, ki])
        front = pools[pool][int(rng.integers(len(pools[pool])))] if kind in oc.BARRELS else None
        sc = oc.make_scene(src, kind, args.amount, args.side, color or "other", front, R.CAM, args.lean)
        log: list = []
        preds = det.detect(sc.mask, R.occl_arms.ARMS[args.arm], R.CAM, log=log)
        r = R.score_scene(sc, R.occl_arms.ARMS[args.arm])
        print(f"{pool} | {src.stem} | {name} | {args.amount} {args.side} | arm {args.arm} | hidden share {sc.hidden:.2f}")
        print(" truth ", sc.target, "fronts", sc.fronts, "clutter", sc.clutter)
        print(" score ", {k: r[k] for k in ("found", "place", "iou", "size", "false", "fronts_found", "cause")})
        for b in preds:
            print(" box   ", b.color, b.bbox, sorted(b.flags), b.source)
        for e in log:
            print("  log  ", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items()})
        boxes = [sc.target[1]] + [b for _, b in sc.fronts + sc.clutter] + [p.bbox for p in preds]
        x0, y0 = max(0, min(b[0] for b in boxes) - 4), max(0, min(b[1] for b in boxes) - 4)
        x1, y1 = min(640, max(b[2] for b in boxes) + 4), min(480, max(b[3] for b in boxes) + 4)
        if not args.no_text:
            print(f"mask, columns {x0} to {x1 - 1} (o orange, B blue):")
            for row in range(y0, y1):
                print(f"{row:4d} " + "".join(CH[int(v)] for v in sc.mask[row, x0:x1]))
        out = R.OUT / "zoom"; out.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out / f"{args.arm}_{key.replace('/', '_')}_{args.amount}_{src.stem.replace('4A8B_', '')}_{dtp.COLOR_NAMES[src.color]}.png"),
                    R.render(sc, preds, f"{args.arm} {key} {args.amount}", size=480))
        n += 1
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
