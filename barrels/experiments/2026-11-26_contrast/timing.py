#!/usr/bin/env python3
"""How long the contrast path takes per frame, piece by piece (one process, one thread; no verdict, no counting).

    python barrels/experiments/2026-11-26_contrast/timing.py [--setting mode=add,...] [--every 6]

Every ``--every``-th ordinary train frame. Writes results/2026-11-26_contrast/timing.md.
"""
from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidate as cd  # noqa: E402
import common as cm  # noqa: E402

from barrels import contrast_c4 as cn  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import judge as jg  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--setting", default="")
    ap.add_argument("--every", type=int, default=6)
    a = ap.parse_args()
    cv2.setNumThreads(1)
    st = cd.setting_from(a.setting) if a.setting else cd.BEST
    p = st.params()
    stems = cm.frames()["ordinary"][:: a.every]
    rb = cn.row_bands(cm.CAM, 480, p)
    t: dict[str, list[float]] = {k: [] for k in ("fixed colors", "today's detector", "response", "candidates", "own colors and paint", "detector, second run", "whole path (cd.detect)")}
    cm.fixed_mask(jg.load_frame(stems[0]))                      # warm up (the model is loaded once)
    for s in stems:
        frame = jg.load_frame(s)

        def clock(name, fn):
            t0 = time.perf_counter()
            out = fn()
            t[name].append(time.perf_counter() - t0)
            return out
        mask = clock("fixed colors", lambda: cm.fixed_mask(frame))
        base = clock("today's detector", lambda: det.detect(mask, det.DetConfig(), cm.CAM))
        resp = clock("response", lambda: cn.respond(frame.rgb, cm.CAM, p, rb))
        cands = clock("candidates", lambda: cn.find(frame.rgb, cm.CAM, p, resp=resp))
        merged, cands = clock("own colors and paint", lambda: cn.contrast_mask(frame.rgb, mask, cm.CAM, p, skip_boxes=tuple(b.bbox for b in base), resp=resp, cands=cands))
        if any(c.info.get("painted") for c in cands):
            clock("detector, second run", lambda: det.detect(merged, det.DetConfig(), cm.CAM))
        else:
            t["detector, second run"].append(0.0)
        clock("whole path (cd.detect)", lambda: cd.detect(frame, st))
    today = [a_ + b_ for a_, b_ in zip(t["fixed colors"], t["today's detector"])]
    L = [f"# Time per frame ({len(stems)} ordinary train frames, one thread; setting: {st.describe()})", "",
         "| piece | median ms | mean ms | max ms |", "|---|---|---|---|"]
    for k, v in list(t.items()) + [("today's path (fixed colors + detector)", today)]:
        L.append(f"| {k} | {statistics.median(v) * 1000:.0f} | {statistics.mean(v) * 1000:.0f} | {max(v) * 1000:.0f} |")
    L += ["", f"The second detector run is needed on {sum(1 for v in t['detector, second run'] if v > 0)} of {len(stems)} frames (those where a candidate was painted)."]
    (cm.OUT / "timing.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
