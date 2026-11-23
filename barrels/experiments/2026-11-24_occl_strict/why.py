#!/usr/bin/env python3
"""The reason log of single train frames (diagnostics only): every box, and every stripe-step note.

    python barrels/experiments/2026-11-24_occl_strict/why.py STEM[,STEM...] [--cfg start] [--all]
"""
from __future__ import annotations

import argparse

import strict as S
CE = S.closeup_census()                 # 2026-11-23_closeup_shape: the report.s frames and segmentation
from barrels import detector as det


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stems")
    ap.add_argument("--cfg", default="start")
    ap.add_argument("--all", action="store_true", help="every log note, not only the kept ones and the stripe step")
    a = ap.parse_args(argv)
    want = set(a.stems.split(","))
    for label, stem, frame, mask in CE.masks():
        if stem not in want:
            continue
        log: list = []
        out = det.detect(mask, S.ARMS[a.cfg], S.CAM, log)
        print("==", label, stem)
        for b in out:
            print("  BOX", "orange" if b.color == 1 else "blue", b.bbox, b.source, sorted(b.flags))
        for e in log:
            if a.all or e["why"] == "kept" or (e["stage"] == "barrel"):
                print("    ", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
