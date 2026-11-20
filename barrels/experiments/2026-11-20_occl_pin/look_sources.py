#!/usr/bin/env python3
"""A viewing aid (no number comes from here): every source barrel of the occlusion scorecard, its mask blown up, one
sheet per pool, so the outline (top arc, shoulders, stripe arc, base arc) can be looked at before it is measured.

    python barrels/experiments/2026-11-20_occl_pin/look_sources.py
Output: results/2026-11-20_occl_pin/sheets/sources_<pool>.png (ignored by git).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
OCCL = HERE.parent / "2026-11-19_det_occl"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(OCCL))
spec = importlib.util.spec_from_file_location("det_occl_run", OCCL / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_occl_pin"


def tile(src, size=260):
    crop = src.crop
    img = np.full((*crop.shape, 3), 45, np.uint8)
    img[crop == ORANGE] = (0, 140, 255); img[crop == BLUE] = (255, 120, 0)
    f = min(size / crop.shape[1], size / crop.shape[0])
    big = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST)
    t = np.zeros((size + 18, size, 3), np.uint8)
    t[18:18 + big.shape[0], :big.shape[1]] = big[:size, :size]
    cv2.putText(t, f"{src.stem.split('_', 3)[-1]} W{src.width} H{src.height}", (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
    return t


def main() -> int:
    stems = R.train_stems()
    pools, _ = R.build_sources(R.segmentations(stems))
    (OUT / "sheets").mkdir(parents=True, exist_ok=True)
    for pool, srcs in pools.items():
        tiles = [tile(s) for s in sorted(srcs, key=lambda s: -s.width)]
        per = 7
        rows = []
        for i in range(0, len(tiles), per):
            r = tiles[i:i + per] + [np.zeros_like(tiles[0])] * (per - len(tiles[i:i + per]))
            rows.append(np.hstack(r))
        cv2.imwrite(str(OUT / "sheets" / f"sources_{pool.replace(' ', '_')}.png"), np.vstack(rows))
        print(pool, len(srcs), sorted(s.width for s in srcs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
