#!/usr/bin/env python3
"""The importable callable ``fuse.detect_frame`` (F3r, all-places picks): same boxes as the record path, and its time.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_fusion/timing.py

Every 6th ordinary train frame, one thread. Writes results/2026-11-27_fusion/timing.md.
"""
import statistics
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fuse  # noqa: E402

from barrels import judge as jg  # noqa: E402

cv2.setNumThreads(1)
stems = jg.train_frames()["ordinary"][::6]
same, ts, t0s = 0, [], []
for s in stems:
    f = jg.load_frame(s)
    t = time.perf_counter()
    a = fuse.detect_frame(s, f)
    ts.append(time.perf_counter() - t)
    t = time.perf_counter()
    fuse.M.Frame(f).c1(fuse.BEST_BUNDLE["C1"], "def")
    t0s.append(time.perf_counter() - t)
    b = fuse.boxes("F3r", fuse.record(s), fuse.BEST_BUNDLE, fuse.BEST_CHOICE)
    same += [x.bbox for x in a] == [x.bbox for x in b]
md = ["# F3r as one callable: time per frame (one thread)", "",
      f"{len(stems)} ordinary train frames (every 6th). Same boxes as the judged record path: {same} of {len(stems)}.", "",
      f"- F3r (`fuse.detect_frame`): median {1000 * statistics.median(ts):.0f} ms, mean {1000 * statistics.mean(ts):.0f}, max {1000 * max(ts):.0f}.",
      f"- contrast alone (C1, the same frames, this code): median {1000 * statistics.median(t0s):.0f} ms, mean {1000 * statistics.mean(t0s):.0f}, max {1000 * max(t0s):.0f}."]
(fuse.OUT / "timing.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
