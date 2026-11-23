#!/usr/bin/env python3
"""Look at named scorecard scenes: every own_close call (piece, seen columns, closure, the measures, what it returned),
the boxes of each arm, the truth, and a picture of the mask (enlarged) with the boxes.

    python barrels/experiments/2026-11-23_own_convex/look_scenes.py "HOME hand masks|barrel_low/same|0.75|L|window_light_core_03|orange"
Output: results/2026-11-23_own_convex/look/<n>.png (ignored) and the text on stdout.
"""
from __future__ import annotations

import sys
import types

import cv2
import numpy as np

import convex as V
import own_arms as O
from barrels import detect_types as dtp, detector as det, geometry as geo, occlude as oc

C, A = O.C, O.A
CAM = geo.AIM_4A8B6118_BOXFIT


def main(argv) -> int:
    O.register()
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={"start": A.ARMS["start"]}, BASE=A.SOURCE_BASE)
    A.install()
    segs = R.segmentations(R.train_stems())
    pools, _ = R.build_sources(segs)
    want = [tuple(a.split("|")) for a in argv]
    out = O.OUT / "look"
    out.mkdir(parents=True, exist_ok=True)
    orig = det._closed_end
    n = 0
    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            k = (pool, key, str(amount), variant, src.stem.replace("4A8B_", ""), dtp.COLOR_NAMES[src.color])
            if k not in want:
                continue
            n += 1
            print("=" * 100, "\n", n, k, "truth", sc.target, "fronts", sc.fronts)

            def spy(s, mask, cam, cfg, sx0, sx1):
                res = orig(s, mask, cam, cfg, sx0, sx1)
                rows = det._stripe_geometry(cam, s.center_row)[1]
                W, H = rows.width_px, rows.bottom - rows.top
                t, b = V.profiles(mask, s, rows, sx0, sx1, cfg)
                ms = {side: V.end_measures(t, b, side == "L", W, H, 0.15) for side in "LR"}
                print(f"  own_close call: piece {s.bbox} body {dtp.COLOR_NAMES[s.body]} seen {sx0}..{sx1} W {W:.1f} H {H:.1f} "
                      f"closure {det._end_closure(s, mask, cam, cfg, sx0, sx1)} -> {res}")
                for side in "LR":
                    print(f"     {side}: " + ", ".join(f"{a} {v:+.3f}" for a, v in ms[side].items()))
                return res
            det._closed_end = spy
            imgs = []
            for arm in ("start", "close"):
                print(" arm", arm)
                preds = det.detect(sc.mask, A.ARMS[arm], CAM)
                print("  boxes:", [(dtp.COLOR_NAMES[p.color], p.bbox) for p in preds])
                vis = np.zeros(sc.mask.shape + (3,), np.uint8)
                vis[sc.mask == det.ORANGE] = (0, 140, 255)
                vis[sc.mask == det.BLUE] = (255, 80, 0)
                x0, y0, x1, y1 = sc.target[1]
                cv2.rectangle(vis, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
                for p in preds:
                    cv2.rectangle(vis, p.bbox[:2], (p.bbox[2] - 1, p.bbox[3] - 1), (0, 255, 0), 1)
                pad = 40
                crop = vis[max(0, y0 - pad):y1 + pad, max(0, x0 - 2 * pad):x1 + 2 * pad]
                imgs.append(cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST))
            det._closed_end = orig
            cv2.imwrite(str(out / f"{n}.png"), np.hstack(imgs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
