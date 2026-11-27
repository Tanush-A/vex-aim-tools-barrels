#!/usr/bin/env python3
"""Look: the cut lines found beside each partly seen stripe of one frame, drawn on the photo and the mask (analysis).

    python debug_line.py STEM OUT.png
"""
import sys

import cv2
import numpy as np

import lib
from lib import det, jg, pl

stem, outp = sys.argv[1], sys.argv[2]
frame = jg.load_frame(stem)
mask = pl.segment(frame, lib.model())[0]
steps = det.photo_steps(frame.rgb)
cfg = det.DetConfig()
stripes, _ = det.find_stripes(mask, lib.CAM, cfg)
img, seg = frame.bgr.copy(), lib.seg_image(mask)
crops = []
for s in stripes:
    at = det._at(s, lib.CAM)
    if at is None or (s.bbox[2] - s.bbox[0]) >= cfg.stripe_full * at.W:
        continue
    e = det.read_edges(s, at, mask, cfg)
    if e is None:
        continue
    top, bottom = max(0, e.top), min(480, e.bottom)
    others = tuple((o.bbox[0], o.bbox[2]) for o in stripes if o is not s and not o.thin)
    seen = det.seen_span(s, mask, at.W, top, bottom, cfg, others)
    for side, x_end in (("L", seen.x0), ("R", seen.x1)):
        for band in ("up", "down"):
            m = det.cut_line_in_band(steps, mask, side, x_end, top, bottom, at.W, at.H, s.center_row, band)
            print(stem, s.bbox, side, band, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()})
    x0, x1 = max(0, seen.x0 - 40), min(640, seen.x1 + 40)
    y0, y1 = max(0, top - 40), min(480, bottom + 40)
    sc = 5
    for base in (img, seg):
        c = cv2.resize(base[y0:y1, x0:x1].copy(), None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)
        for side, x_end in (("L", seen.x0), ("R", seen.x1)):
            cv2.line(c, ((x_end - x0) * sc, 0), ((x_end - x0) * sc, c.shape[0]), (0, 255, 0), 1)
            r = int(round(det.PHOTO_REACH * at.W))
            for yy in range(y0, y1):
                if top <= yy < bottom:
                    continue
                win = steps[yy, max(2, x_end - r):min(638, x_end + r + 1)]
                if win.size and win.max() >= det.PHOTO_STEP:
                    xx = max(2, x_end - r) + int(win.argmax())
                    cv2.circle(c, ((xx - x0) * sc + sc // 2, (yy - y0) * sc + sc // 2), 2, (0, 0, 255) if side == "L" else (255, 0, 255), -1)
        cv2.line(c, (0, (top - y0) * sc), (c.shape[1], (top - y0) * sc), (0, 255, 255), 1)
        cv2.line(c, (0, (bottom - y0) * sc), (c.shape[1], (bottom - y0) * sc), (0, 255, 255), 1)
        crops.append(c)
cv2.imwrite(outp, lib.stack([np.hstack(crops[i:i + 2]) for i in range(0, len(crops), 2)]))
