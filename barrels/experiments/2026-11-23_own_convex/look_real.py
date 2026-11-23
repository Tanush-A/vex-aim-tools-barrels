#!/usr/bin/env python3
"""On named TRAIN frames (adopted color model): every own_close call (arm ``close``), with closure and the bulge measures,
and why each hand-boxed barrel without a box was refused (the reason log). Train frames only (asserted).

    python barrels/experiments/2026-11-23_own_convex/look_real.py 4A8B_window_abpwhite_occlx_02 ...
"""
from __future__ import annotations

import sys

import convex as V
import own_arms as O
from barrels import detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, pipeline as pl, splits as spl, \
    worldmap_bridge as wb

A = O.A
CAM = geo.AIM_4A8B6118_BOXFIT


def main(argv) -> int:
    O.register()
    test = set(spl.load_splits()["test"])
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    orig = det._closed_end
    for stem in argv:
        assert stem not in test, "test frame"
        mask = pl.segment(pl.Frame.from_image(io.load_image(io.find_image(stem))), model)[0]
        gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes(io.load_boxes(stem))]
        print("=" * 90, "\n", stem, "truth", [(dtp.COLOR_NAMES[g.color], g.bbox, g.flags) for g in gts])

        def spy(s, m, cam, cfg, sx0, sx1):
            res = orig(s, m, cam, cfg, sx0, sx1)
            rows = det._stripe_geometry(cam, s.center_row)[1]
            W, H = rows.width_px, rows.bottom - rows.top
            t, b = V.profiles(m, s, rows, sx0, sx1, cfg)
            print(f"  own_close call: piece {s.bbox} {dtp.COLOR_NAMES[s.body]} seen {sx0}..{sx1} closure "
                  f"{tuple(round(c, 3) for c in det._end_closure(s, m, cam, cfg, sx0, sx1))} -> {res}; chord 0.15 L "
                  f"{V.end_measures(t, b, True, W, H, 0.15)['chord']:+.3f} R {V.end_measures(t, b, False, W, H, 0.15)['chord']:+.3f}")
            return res
        det._closed_end = spy
        log: list = []
        preds = det.detect(mask, A.ARMS["close"], CAM, log=log)
        det._closed_end = orig
        res = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2")
        print("  boxes:", [(dtp.COLOR_NAMES[p.color], p.bbox) for p in preds], "missed:", [gts[i].bbox for i in res.unmatched_gt])
        for gi in res.unmatched_gt:
            g = gts[gi]
            near = [e for e in log if e.get("why") != "kept" and e.get("bbox") is not None
                    and min(e["bbox"][2], g.bbox[2]) > max(e["bbox"][0], g.bbox[0]) and min(e["bbox"][3], g.bbox[3]) > max(e["bbox"][1], g.bbox[1])]
            for e in near[:6]:
                print("    refused:", e.get("stage"), e.get("why"), e.get("bbox"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
