#!/usr/bin/env python3
"""Contact sheet of scorecard scenes (diagnostics): the scene's mask, the truths (white), the boxes of ``start`` (thin) and of an
arm (thick), and the verify notes of the arm's log.

    python barrels/experiments/2026-11-24_occl_strict/look_scenes.py --arm verify_front --scenes "KEY|AMOUNT|VARIANT|STEM|[BOX]";... [--out look.png]
Scene ids as in census_card.csv's ``scene`` column.
"""
from __future__ import annotations

import argparse
import types

import cv2
import numpy as np

import strict as S
from barrels import detector as det


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="verify_front")
    ap.add_argument("--scenes", required=True, help="scene ids separated by ';'")
    ap.add_argument("--out", default="look.png")
    a = ap.parse_args(argv)
    want = [s for s in a.scenes.split(";") if s]
    C = S.battery()
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={}, BASE=C.A.SOURCE_BASE)
    pools, _ = R.build_sources(R.segmentations(R.train_stems()))
    tiles = []
    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            sid = f"{key}|{amount}|{variant}|{src.stem}|{list(src.bbox)}"
            if sid not in want:
                continue
            img = np.zeros((*sc.mask.shape, 3), np.uint8)
            img[sc.mask == 1] = (0, 128, 255); img[sc.mask == 2] = (255, 80, 0)
            for c, b in [sc.target] + list(sc.fronts):
                cv2.rectangle(img, tuple(b[:2]), (b[2] - 1, b[3] - 1), (255, 255, 255), 1)
            log: list = []
            for b in det.detect(sc.mask, S.START, S.CAM):
                cv2.rectangle(img, b.bbox[:2], (b.bbox[2] - 1, b.bbox[3] - 1), (0, 0, 255), 1)
            for b in det.detect(sc.mask, S.ARMS[a.arm], S.CAM, log):
                cv2.rectangle(img, b.bbox[:2], (b.bbox[2] - 1, b.bbox[3] - 1), (0, 255, 0), 2)
            for e in log:
                if e["stage"] == "verify":
                    x0, y0, x1, y1 = e["evidence"]
                    cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 1)
                    print(sid, e)
            xs = [b[0] for _, b in [sc.target] + list(sc.fronts)] + [b[2] for _, b in [sc.target] + list(sc.fronts)]
            cx = int(np.clip((min(xs) + max(xs)) / 2, 160, 480))
            crop = img[40:340, cx - 160:cx + 160]
            cv2.putText(crop, sid[:48], (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
            tiles.append(cv2.resize(crop, (640, 600), interpolation=cv2.INTER_NEAREST))
    if tiles:
        rows = [cv2.hconcat(tiles[i:i + 2] + [np.zeros_like(tiles[0])] * (2 - len(tiles[i:i + 2]))) for i in range(0, len(tiles), 2)]
        cv2.imwrite(str(S.OUT / a.out), cv2.vconcat(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
