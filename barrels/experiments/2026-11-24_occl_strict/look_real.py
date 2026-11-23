#!/usr/bin/env python3
"""Close-ups of boxes on train frames (diagnostics): image and class mask around a box, scaled up x3, with the box (red) and
its evidence (magenta).

    python barrels/experiments/2026-11-24_occl_strict/look_real.py "STEM:x0,y0,x1,y1:ex0,ey0,ex1,ey1;..." [--out look_real.png]
"""
from __future__ import annotations

import argparse

import cv2
import numpy as np

import strict as S

CE = S.closeup_census()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("items")
    ap.add_argument("--out", default="look_real.png")
    a = ap.parse_args(argv)
    items = []
    for it in a.items.split(";"):
        stem, box, ev = it.split(":")
        items.append((stem, tuple(map(int, box.split(","))), tuple(map(int, ev.split(",")))))
    want = {s for s, _, _ in items}
    tiles = []
    for label, stem, frame, mask in CE.masks():
        if stem not in want:
            continue
        for s, box, ev in items:
            if s != stem:
                continue
            seg = np.zeros((*mask.shape, 3), np.uint8)
            seg[mask == 1] = (0, 128, 255); seg[mask == 2] = (255, 80, 0)
            cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
            x0, y0 = int(np.clip(cx - 60, 0, 520)), int(np.clip(cy - 50, 0, 380))
            pair = []
            for im in (frame.bgr.copy(), seg):
                cv2.rectangle(im, box[:2], (box[2] - 1, box[3] - 1), (0, 0, 255), 1)
                cv2.rectangle(im, ev[:2], (ev[2] - 1, ev[3] - 1), (255, 0, 255), 1)
                pair.append(cv2.resize(im[y0:y0 + 100, x0:x0 + 120], (360, 300), interpolation=cv2.INTER_NEAREST))
            t = cv2.hconcat(pair)
            cv2.putText(t, stem[5:], (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            tiles.append(t)
    cv2.imwrite(str(S.OUT / a.out), cv2.vconcat(tiles))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
