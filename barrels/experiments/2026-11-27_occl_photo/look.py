#!/usr/bin/env python3
"""Look first (no rule): today's boxes on the failing frames, the labels, the mask, and per labelled barrel today's state.

    python barrels/experiments/2026-11-27_occl_photo/look.py STEM [STEM ...]      # default: the frames named in the brief

Writes results/2026-11-27_occl_photo/look/<stem>.png (not committed) and prints each barrel's state.
"""
from __future__ import annotations

import sys

import cv2

import lib
from lib import ct, jg, pl

DEFAULT = ["4A8B_window_abpwhite_occlx_02", "4A8B_window_abpwhite_occlx_03", "4A8B_overheaddim_palewood_occl_02",
           "4A8B_lampcool6_ottoman_occl_02", "4A8B_lampmid6_ottoman_occl_02", "4A8B_lampwarm6_glass_occl_02"]


def main(stems) -> int:
    out = lib.OUT / "look"
    out.mkdir(parents=True, exist_ok=True)
    for stem in stems:
        frame = jg.load_frame(stem)
        mask = pl.segment(frame, lib.model())[0]
        log: list = []
        boxes = pl.detect_frame(frame, lib.model(), lib.CAM, log=log)
        gts, clean = lib.truth(stem)
        fc = ct.classify_frame(stem, boxes, gts, clean)
        print(stem)
        for g, s in zip(gts, fc.gt):
            print("   truth", lib.dtp.COLOR_NAMES[g.color], g.bbox, sorted(g.flags), s)
        for b, s in zip(boxes, fc.boxes):
            print("   box  ", lib.dtp.COLOR_NAMES[b.color], b.bbox, lib.rule_of(log, b.bbox) or b.source, s)
        for e in log:
            if e.get("stage") == "barrel" and e.get("why") not in ("kept",):
                print("   no box:", e.get("why"), e.get("bbox"), {k: v for k, v in e.items() if k in ("expected_w",)})
        img = lib.sheet(frame.bgr, mask, gts, {"today": (boxes, (255, 255, 255))}, pad=40, scale=2, title=stem)
        cv2.imwrite(str(out / f"{stem}.png"), img)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or DEFAULT))
