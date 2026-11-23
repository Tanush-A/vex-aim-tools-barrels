#!/usr/bin/env python3
"""Per-frame features from the frame alone (no label) next to the barrels' own colors (from the hand boxes), for every
boxed train frame. Used by step 3 (the relation) of the 2026-11-25 color work.

    python barrels/experiments/2026-11-25_color/features.py

Frame features (pixels below row 50 with V >= 40, OpenCV hue): the nine ``hsrel.FEATURES`` that need no reference,
plus for orange (window hue -10..30) and blue (75..135): the hue of the tallest smoothed peak among pixels with
S >= 100 / 150, the 90th percentile of S of the pixels in the window with S >= 40, the share of the frame's pixels in
the window with S >= 100; and the frame's overall warmth: the median of (R - B) / (R + G + B) over the gated pixels,
and the median hue of all pixels with S >= 40 (rotated so orange is contiguous).
Barrel colors (needs the boxes; the TARGET, never an input): per color the median hue and S of the body pixels of
free-standing barrels (``common.expected_regions``). Writes results/2026-11-25_color/features.csv.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

WIN = {"orange": (-10, 30), "blue": (75, 135)}


def frame_features(bgr: np.ndarray) -> dict:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    H, S, V = (hsv[..., i].astype(np.int32) for i in range(3))
    sel = V >= 40
    sel[:50] = False
    h, s = H[sel], S[sel]
    f = {"n_px": int(sel.sum()), "v_mean": float(V[sel].mean())}
    rgb = bgr[..., ::-1][sel].astype(np.float32)
    f["warmth"] = float(np.median((rgb[:, 0] - rgb[:, 2]) / (rgb.sum(1) + 1)))
    col = s >= 40
    hr = np.where(h > 150, h - 180, h)
    f["hue_med_colored"] = float(np.median(hr[col])) if col.any() else float("nan")
    f["s_med"] = float(np.median(s))
    for c, (lo, hi) in WIN.items():
        hh = hr if c == "orange" else h
        inw = (hh >= lo) & (hh <= hi)
        for s0 in (100, 150):
            m = inw & (s >= s0)
            if m.sum() >= 200:
                cnt = np.bincount(hh[m] - lo, minlength=hi - lo + 1).astype(float)
                cnt = np.convolve(cnt, [1, 2, 3, 2, 1], "same")
                f[f"{c}_peak{s0}"] = float(lo + np.argmax(cnt))
            else:
                f[f"{c}_peak{s0}"] = float("nan")
        m = inw & (s >= 40)
        f[f"{c}_s_p90"] = float(np.percentile(s[m], 90)) if m.sum() >= 200 else float("nan")
        f[f"{c}_s_p50"] = float(np.percentile(s[m], 50)) if m.sum() >= 200 else float("nan")
        f[f"{c}_share100"] = float((inw & (s >= 100)).mean())
    return f


def barrel_colors(bgr: np.ndarray, lab: dict) -> dict:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    H, S = hsv[..., 0].astype(int), hsv[..., 1].astype(int)
    out = {}
    for c in ("orange", "blue"):
        m = np.zeros(H.shape, bool)
        for b in lab.get("barrels", []):
            if set(b.get("flags", [])) & {"occluded", "truncated"}:
                continue
            reg = cm.expected_regions(b, bgr.shape)
            m |= reg["body"] if b["color"] == c else reg["stripe"]
        if m.sum() >= 30:
            hh = H[m]
            if c == "orange":
                hh = np.where(hh > 150, hh - 180, hh)
            out[f"bar_{c}_h"] = float(np.median(hh))
            out[f"bar_{c}_s"] = float(np.median(S[m]))
            out[f"bar_{c}_s_p10"] = float(np.percentile(S[m], 10))
        else:
            out[f"bar_{c}_h"] = out[f"bar_{c}_s"] = out[f"bar_{c}_s_p10"] = float("nan")
    return out


def main() -> int:
    rows = []
    for stem in cm.train_stems_with_boxes():
        key = cm.condition_of(stem)
        if cm.class_of(key) == "excluded":
            continue
        bgr, lab = cm.load(stem)
        rows.append({"stem": stem, "condition": key, "place": cm.place_of(key), "class": cm.class_of(key),
                     **frame_features(bgr), **barrel_colors(bgr, lab)})
    out = cm.RESULTS / "features.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} frames -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
