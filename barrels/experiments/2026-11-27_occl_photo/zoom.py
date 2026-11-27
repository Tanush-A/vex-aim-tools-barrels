#!/usr/bin/env python3
"""Look: one train frame's photo crop, enlarged, with the labels (green) and optional grid. Side tool.

    python zoom.py STEM X0 Y0 X1 Y1 SCALE OUT.png
"""
import sys

import cv2

import lib

stem, (x0, y0, x1, y1, sc), out = sys.argv[1], map(int, sys.argv[2:7]), sys.argv[7]
f = lib.jg.load_frame(stem)
gts, _ = lib.truth(stem)
img = cv2.resize(f.bgr[y0:y1, x0:x1].copy(), None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)
for g in gts:
    b = g.bbox
    cv2.rectangle(img, ((b[0] - x0) * sc, (b[1] - y0) * sc), ((b[2] - x0) * sc - 1, (b[3] - y0) * sc - 1), (0, 255, 0), 1)
for x in range((x0 // 10 + 1) * 10, x1, 10):
    cv2.line(img, ((x - x0) * sc, 0), ((x - x0) * sc, 6), (0, 0, 255), 1)
for y in range((y0 // 10 + 1) * 10, y1, 10):
    cv2.line(img, (0, (y - y0) * sc), (6, (y - y0) * sc), (0, 0, 255), 1)
cv2.imwrite(out, img)
