#!/usr/bin/env python3
"""Time per frame of each arm on the HOME and CAMPUS train frames (640 x 480, adopted color model): the color
segmentation once, then each arm's detection on the mask, best of 3 runs per frame.

    python barrels/experiments/2026-11-20_stencil/timing.py
Output: results/2026-11-20_stencil/timing.md
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
import stencil_arms as A  # noqa: E402
from barrels import geometry as geo, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT


def main() -> int:
    sp = splits.load_splits()
    test = set(sp["test"])
    stems = [s for s in sorted(sp["train"]) if s.startswith(("4A8B_window_light_", "4A8B_campus_light_")) and io.boxes_path(s).exists()]
    assert not set(stems) & test
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    seg, t = [], {m: [] for m in A.METHODS}
    nbar = []
    for s in stems:
        img = io.load_image(io.find_image(s))
        t0 = time.perf_counter(); mask = pl.segment(pl.Frame.from_image(img), model)[0]; seg.append(time.perf_counter() - t0)
        nbar.append(len(io.load_boxes(s)["barrels"]))
        for m in A.METHODS:
            best = 1e9
            for _ in range(3):
                t0 = time.perf_counter(); A.detect(mask, A.ARMS[m], CAM); best = min(best, time.perf_counter() - t0)
            t[m].append(best)

    def ms(v):
        v = np.asarray(v) * 1000
        return f"{np.median(v):.0f} | {np.percentile(v, 90):.0f} | {v.max():.0f}"
    L = ["# Time per frame", "",
         f"{len(stems)} HOME and CAMPUS train frames, 640 x 480, 0 to {max(nbar)} barrels per frame (median {int(np.median(nbar))}); this laptop, one core, "
         "best of 3 runs per frame. Detection only; the color segmentation, which every arm needs once, is the first row.", "",
         "| | median ms | 90th percentile | slowest frame |", "|---|---|---|---|", f"| color segmentation | {ms(seg)} |"]
    for m in A.METHODS:
        L.append(f"| `{m}` | {ms(t[m])} |")
    empty = [i for i, n in enumerate(nbar) if n == 0]
    if empty:
        L += ["", "On the frames with no barrel: " + ", ".join(f"`{m}` {np.median(np.asarray(t[m])[empty]) * 1000:.0f} ms" for m in A.METHODS) + "."]
    (A.OUT / "timing.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
