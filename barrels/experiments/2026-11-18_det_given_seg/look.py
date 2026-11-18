#!/usr/bin/env python3
"""A close look at one frame of the test: the photo crop next to the mask crop (class colors on black), enlarged,
with the truth boxes (white), the boxes drawn (yellow / green) and every stripe candidate (magenta = kept, red =
refused). A viewing aid only; no number comes from here.

    python barrels/experiments/2026-11-18_det_given_seg/look.py "1 perfect" occl_01 [--arm base] [--tag seed0]
writes results/2026-11-18_det_given_seg/zoom/<arm>_<level>_<stem>.png and prints the reason log around the truth boxes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as R  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402


def render(img, mask, gts, preds, log, pad=25, scale=6):
    xs = [v for g in gts for v in (g.bbox[0], g.bbox[2])] + [v for p in preds for v in (p.bbox[0], p.bbox[2])]
    ys = [v for g in gts for v in (g.bbox[1], g.bbox[3])] + [v for p in preds for v in (p.bbox[1], p.bbox[3])]
    h, w = mask.shape
    if not xs:
        xs, ys = [0, w], [0, h]
    x0, x1, y0, y1 = max(0, min(xs) - pad), min(w, max(xs) + pad), max(0, min(ys) - pad), min(h, max(ys) + pad)
    scale = max(1, min(scale, 1200 // max(1, x1 - x0)))
    seg = np.zeros((h, w, 3), np.uint8)
    seg[mask == ORANGE] = (0, 140, 255); seg[mask == BLUE] = (255, 120, 0)

    def up(a):
        return cv2.resize(a[y0:y1, x0:x1], None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

    def box(a, b, color, t=1):
        cv2.rectangle(a, ((b[0] - x0) * scale, (b[1] - y0) * scale), ((b[2] - x0) * scale - 1, (b[3] - y0) * scale - 1), color, t)

    photo, m = up(img), up(seg)
    for e in log:
        if e["stage"] in ("stripe", "barrel", "cap"):
            box(m, e["bbox"], (255, 0, 255) if e["why"] == "kept" else (0, 0, 255))
    for g in gts:
        box(m, g.bbox, (255, 255, 255)); box(photo, g.bbox, (255, 255, 255))
    for p in preds:
        box(m, p.bbox, det.BOX_COLOR_BGR[p.color], 2); box(photo, p.bbox, det.BOX_COLOR_BGR[p.color], 2)
    return np.hstack([photo, m])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario"); ap.add_argument("stem")
    ap.add_argument("--arm", default="base"); ap.add_argument("--tag", default="")
    args = ap.parse_args(argv)
    scenarios, images = R.build_scenarios(R.train_sets())
    out = R.OUT / "zoom"; out.mkdir(parents=True, exist_ok=True)
    n = 0
    for sc in scenarios:
        if not sc.key.startswith(args.scenario):
            continue
        for stem, tag, mask in sc.items:
            if args.stem not in stem or (tag not in ("", args.tag or "seed0")):
                continue
            gts, _ = R.truth(stem)
            log: list = []
            preds = det.detect(mask, R.ARMS[args.arm], R.CAM, log=log)
            p = out / f"{args.arm}_{sc.level}_{sc.name.split(',')[0].replace(' ', '-')}_{stem.replace('4A8B_', '')}.png"
            cv2.imwrite(str(p), render(images[stem], mask, gts, preds, log))
            print(p)
            for g in gts:
                print(" truth", g.color, g.bbox, sorted(g.flags))
            for b in preds:
                print(" box  ", b.color, b.bbox, sorted(b.flags), b.source)
            for e in log:
                if any(R.att.overlaps(e["bbox"], g.bbox) for g in gts):
                    print("  log ", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items()})
            n += 1
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
