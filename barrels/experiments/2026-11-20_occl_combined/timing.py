#!/usr/bin/env python3
"""Time per frame of the detector (detection only; the class mask is made before the clock starts), for a few arms,
on the HOME (leave one scene out) and CAMPUS train frames. One core; each frame three times, the fastest counts.
Run it when nothing else is running. Report only.

    python barrels/experiments/2026-11-20_occl_combined/timing.py [--arms before,stack,reduced+thin]
Output: results/2026-11-20_occl_combined/timing.md
"""
from __future__ import annotations

import argparse
import sys
import time
import types

import numpy as np

import common as C

A = C.A


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="before,stack,combined,reduced,reduced+thin")
    args = ap.parse_args(argv)
    arms = C.arm_list(args.arms, None)
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS=A.ARMS, BASE=A.SOURCE_BASE)
    segs = R.segmentations(R.train_stems())
    masks = list(segs["HOME color model"].values()) + list(segs["CAMPUS color model"].values())
    A.install()
    L = ["# Time per frame, detection only", "",
         f"{len(masks)} HOME and CAMPUS train frames; one core; the fastest of three runs per frame; milliseconds. Segmentation (about 26 ms) is not in it.", "",
         "| arm | median | 90th percentile | slowest frame |", "|---|---|---|---|"]
    for a in arms:
        ts = []
        for m in masks:
            best = 1e9
            for _ in range(3):
                t0 = time.perf_counter()
                A.detect(m, A.ARMS[a], R.CAM)
                best = min(best, time.perf_counter() - t0)
            ts.append(1000 * best)
        L.append(f"| `{a}` | {np.median(ts):.0f} | {np.percentile(ts, 90):.0f} | {max(ts):.0f} |")
    (C.OUT / "timing.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
