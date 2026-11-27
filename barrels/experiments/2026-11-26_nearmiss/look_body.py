#!/usr/bin/env python3
"""IN-SAMPLE look for experiment 2026-11-26_nearmiss: what do a barrel's body and stripe read, against the ground
right beside the barrel? Per condition and barrel color, at the hand boxes (train frames only).

    python barrels/experiments/2026-11-26_nearmiss/look_body.py

Patches as in docs/review-2026-11-26/color_physics.md: centre columns 0.36-0.64 of the box; stripe rows 0.51-0.61;
lower body rows 0.75-0.90. The ground: a ring around the box (the box grown by a quarter of its width, less the
box grown by 4 px and less every other hand box). Barrels flagged occluded, truncated or held are left out, and so
are boxes under 24 px tall. Printed: the median hue, S, V of body, stripe and ground, and V(body) / V(ground).
Its question: is a blue body that reads gray-olive at least darker than the ground beside it?
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nm_common as cm  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402


def med(hsv: np.ndarray, sel: np.ndarray):
    px = hsv[sel]
    if len(px) == 0:
        return None
    h = px[:, 0].astype(int)
    h = np.where(h > 150, h - 180, h)                     # orange sits at the wrap: 177 reads -3
    return float(np.median(h)), float(np.median(px[:, 1])), float(np.median(px[:, 2]))


def main() -> int:
    rows = defaultdict(list)
    for stem in cm.ordinary() + cm.report_only():
        label = io.load_boxes(stem, check_image=False)
        barrels = label.get("barrels", [])
        if not barrels:
            continue
        frame = jg.load_frame(stem)
        hsv = cv2.cvtColor(np.ascontiguousarray(frame.bgr), cv2.COLOR_BGR2HSV)
        h, w = hsv.shape[:2]
        inside = np.zeros((h, w), bool)
        for b in barrels:
            x0, y0, x1, y1 = b["bbox"]
            inside[max(0, y0 - 4):y1 + 4, max(0, x0 - 4):x1 + 4] = True
        for b in barrels:
            x0, y0, x1, y1 = b["bbox"]
            bw, bh = x1 - x0, y1 - y0
            if set(b.get("flags", ())) & {"occluded", "truncated", "held"} or bh < 24:
                continue
            c0, c1 = x0 + int(0.36 * bw), x0 + int(np.ceil(0.64 * bw))
            body = np.zeros((h, w), bool); body[y0 + int(0.75 * bh):y0 + int(0.90 * bh), c0:c1] = True
            stripe = np.zeros((h, w), bool); stripe[y0 + int(0.51 * bh):y0 + int(0.61 * bh), c0:c1] = True
            g = int(0.25 * bw)
            ring = np.zeros((h, w), bool); ring[max(50, y0 - g):y1 + g, max(0, x0 - g):x1 + g] = True
            ring &= ~inside
            m = [med(hsv, s) for s in (body, stripe, ring)]
            if any(v is None for v in m):
                continue
            rows[(ct.condition_of(stem), b["color"])].append(m)
    print(f"{'condition':<24}{'barrel':<8}{'n':>3}   {'body h/S/V':<16}{'stripe h/S/V':<16}{'ground h/S/V':<16}{'V body/ground':>14}{'  (10th-90th)':<14}")
    for (cond, color), ms in sorted(rows.items()):
        a = np.array(ms)                                    # n x 3 (body, stripe, ground) x 3 (h, S, V)
        mm = np.median(a, axis=0)
        ratio = a[:, 0, 2] / np.maximum(1.0, a[:, 2, 2])
        cell = lambda v: f"{v[0]:.0f}/{v[1]:.0f}/{v[2]:.0f}"
        print(f"{cond:<24}{color:<8}{len(ms):>3}   {cell(mm[0]):<16}{cell(mm[1]):<16}{cell(mm[2]):<16}{np.median(ratio):>14.2f}"
              f"  ({np.percentile(ratio, 10):.2f}-{np.percentile(ratio, 90):.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
