#!/usr/bin/env python3
"""Time per frame of the new default against the previous one (2026-11-27), one thread, the ordinary train frames.

    python barrels/experiments/2026-11-27_adopt_contrast/timing.py

Each frame is read once (``judge.load_frame``, train only), then each path is timed three times and the fastest of
the three is kept (the machine's own noise out). Writes results/2026-11-27_adopt_contrast/timing.md.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
import cv2  # noqa: E402
import numpy as np  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

cv2.setNumThreads(1)
OUT = BARRELS / "results" / "2026-11-27_adopt_contrast"


def best(fn, n: int = 3) -> float:
    out = []
    for _ in range(n):
        t = time.perf_counter(); fn(); out.append(time.perf_counter() - t)
    return min(out)


def main() -> int:
    stems = jg.train_frames()[cnd.ORDINARY]
    model = pl.default_model()
    pl.detect_frame(jg.load_frame(stems[0]))                  # warm up (the row bands are computed once)
    prev, now, second = [], [], 0
    for s in stems:
        f = jg.load_frame(s)
        prev.append(best(lambda: pl.detect_frame(f, model, contrast=False)))
        now.append(best(lambda: pl.detect_frame(f, model)))
        log: list = []
        pl.detect_frame(f, model, log=log)
        second += any(e.get("stage") == "contrast" and e.get("painted") for e in log)
    p, n = 1000 * np.array(prev), 1000 * np.array(now)
    lines = ["# Time per frame, previous default against the new default", "",
             f"Made by `experiments/2026-11-27_adopt_contrast/timing.py`: {len(stems)} ordinary train frames, one thread, the fastest of three runs per frame.", "",
             "| path | median ms | mean ms | 90th percentile ms | max ms |", "|---|---:|---:|---:|---:|",
             f"| previous default (color step + detector) | {np.median(p):.0f} | {p.mean():.0f} | {np.percentile(p, 90):.0f} | {p.max():.0f} |",
             f"| new default (+ the stripe by contrast) | {np.median(n):.0f} | {n.mean():.0f} | {np.percentile(n, 90):.0f} | {n.max():.0f} |",
             f"| the contrast stage alone (difference) | {np.median(n - p):.0f} | {(n - p).mean():.0f} | {np.percentile(n - p, 90):.0f} | {(n - p).max():.0f} |", "",
             f"The second detector run (on the painted mask) happens on {second} of {len(stems)} frames: only when a candidate was painted.", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "timing.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
