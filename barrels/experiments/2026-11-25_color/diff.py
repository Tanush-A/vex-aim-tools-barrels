#!/usr/bin/env python3
"""Exploration helper: per frame, where rule B differs from rule A (found / false), from the explore cache.

    python barrels/experiments/2026-11-25_color/diff.py RULE_A RULE_B [--render DIR]

With --render, writes one picture per differing frame: the raw frame with the hand boxes, then A's and B's painted
pixels and boxes (train frames only)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import explore as ex  # noqa: E402

from barrels import detector as det  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels import viz  # noqa: E402


def render(stem: str, specs: list[str], out: Path) -> Path:
    bgr, lab = cm.load(stem)
    fr = pl.Frame.from_image(bgr)
    tiles = []
    raw = bgr.copy()
    for b in lab.get("barrels", []):
        x0, y0, x1, y1 = b["bbox"]
        cv2.rectangle(raw, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
    tiles.append(raw)
    for spec in specs:
        m = ex.make_rule(spec)(fr)
        pic = (bgr * 0.3).astype(np.uint8)
        pic[m == 1] = viz.ORANGE_BGR
        pic[m == 2] = viz.BLUE_BGR
        pic = det.draw(pic, det.detect(m, det.DetConfig(), ex.CAM), thickness=2)
        for b in lab.get("barrels", []):
            x0, y0, x1, y1 = b["bbox"]
            cv2.rectangle(pic, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        cv2.putText(pic, spec[:70], (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(pic)
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{stem}.png"
    cv2.imwrite(str(p), np.hstack(tiles))
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--render", type=Path, default=None)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    res = ex.run([args.a, args.b])
    for stem in sorted(res):
        if args.only not in stem:
            continue
        ra, rb = res[stem][args.a], res[stem][args.b]
        fa, fb = sum(ra["fp"].values()), sum(rb["fp"].values())
        if ra["found"] != rb["found"] or fa != fb:
            lost = sorted(set(ra["found"]) - set(rb["found"]))
            gain = sorted(set(rb["found"]) - set(ra["found"]))
            print(f"{stem[5:]:36s} found {len(ra['found'])}->{len(rb['found'])} (+{[g + 1 for g in gain]} -{[g + 1 for g in lost]})  false {fa}->{fb}{'  EMPTY' if rb['neg'] else ''}")
            if args.render:
                render(stem, [args.a, args.b], args.render)
    return 0


if __name__ == "__main__":
    sys.exit(main())
