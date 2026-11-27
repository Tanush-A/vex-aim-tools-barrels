#!/usr/bin/env python3
"""Exploration for part B, in-sample, at pixel level (no detector): which blue rules paint the labelled blue paint,
and how much of everything else do they paint? Looked at BEFORE the pre-registration; listed there.

    python barrels/experiments/2026-11-26_light/explore_blue.py [--reading without_loose] [--jobs 8]

Per ordinary train frame and per rule: the share of the labelled blue paint painted blue (body and stripe bands of
free-standing barrels), and the share of the background painted blue (rows from 50, brightness >= 40, outside every
hand box grown by 4 px). Rules:

- ``fixed``: hue 103..119, S >= 113.
- ``box h s``: hue h..119, S >= s (what the two moving numbers can reach at the end of the ramp).
- ``rel d``: the fixed box, or: the pixel's own warmth (R - B) / (R + G + B) is at least d BELOW the light's warmth
  (the reading), and the pixel is not strongly colored (S <= 150) and not painted orange by the fixed model. "Bluer
  than the light by d." Only meaningful where the light is warm.
- ``relbg m``: the same idea on the blue channel alone: log(B / G) of the pixel at least m above the light's.
- ``on rel d`` / ``on relmin d`` / ``on relsur d``: the relative rule only where the light reads at least ``W_ON`` warm,
  for pixels under the fixed S floor (S < 113), compared with: the light / the lower of the light and the whole scene
  below the gate (so a dark neutral table is not "bluer than the light") / the lower of the light and the mean warmth
  of the gated pixels in a ``SUR`` px window around the pixel ("bluer than its surroundings").

Writes results/2026-11-26_light/explore_blue.md (per condition means).
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import lightread as lr  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels.io import ORANGE  # noqa: E402

BOXES = [(103, 113), (98, 60), (92, 40), (92, 30), (85, 30), (60, 20), (20, 20)]
RELS = [0.15, 0.20, 0.25, 0.30]
RELBG = [0.5]
W_ON = 0.08         # the relative rules below are switched on only where the light reads at least this warm
SUR = 151           # the window of the local surround, px
READING = "without_loose"


def rules(frame, reading: str) -> dict[str, np.ndarray]:
    g = cm.gate(frame)
    h, s = cm.hue_blue(frame), cm.sat(frame)
    out = {}
    for h_lo, s_lo in BOXES:
        out["fixed" if (h_lo, s_lo) == (103, 113) else f"box {h_lo} {s_lo}"] = g & (h >= h_lo) & (h <= 119) & (s >= s_lo)
    m = cm.reading_masks(frame)[reading]
    r = lr.read(frame.rgb, m)
    orange = pl.segment(frame, cm.model())[0] == ORANGE
    pw = lr.pixel_warmth(frame.rgb)
    x = frame.rgb.astype(np.float32)
    lbg = np.log((x[..., 2] + 1) / (x[..., 1] + 1))
    for d in RELS:
        out[f"rel {d:.2f}"] = out["fixed"] | (g & ~orange & (s <= 150) & (pw <= r.warmth - d)) if r.ok else out["fixed"]
    on = r.ok and r.warmth >= W_ON
    scene = lr.gray_world(frame.rgb).warmth                       # the scene below the gate (mostly the table)
    import cv2
    gf = g.astype(np.float32)
    sur = cv2.blur(pw * gf, (SUR, SUR)) / np.maximum(cv2.blur(gf, (SUR, SUR)), 1e-3)     # mean warmth of the gated pixels around
    for d in RELS:
        out[f"on rel {d:.2f}"] = out["fixed"] | (g & ~orange & (s < 113) & (pw <= r.warmth - d)) if on else out["fixed"]
        out[f"on relmin {d:.2f}"] = out["fixed"] | (g & ~orange & (s < 113) & (pw <= min(r.warmth, scene) - d)) if on else out["fixed"]
        out[f"on relsur {d:.2f}"] = out["fixed"] | (g & ~orange & (s < 113) & (pw <= np.minimum(r.warmth, sur) - d)) if on else out["fixed"]
    for mm in RELBG:
        out[f"relbg {mm:.1f}"] = out["fixed"] | (g & ~orange & (s <= 150) & (lbg >= r.log_bg + mm)) if r.ok else out["fixed"]
    return out


def one(args) -> dict:
    import cv2
    cv2.setNumThreads(1)
    stem, reading = args
    frame = jg.load_frame(stem)
    pm = cm.paint_masks(stem, frame.shape)
    paint = pm["blue_body"] | pm["blue_stripe"]
    bg = cm.gate(frame) & ~pm["boxes"]
    row = {"stem": stem, "condition": ct.condition_of(stem), "paint": int(paint.sum()), "bg": int(bg.sum())}
    for name, m in rules(frame, reading).items():
        row[f"{name}|paint"] = float(m[paint].mean()) if paint.sum() >= 30 else float("nan")
        row[f"{name}|body"] = float(m[pm["blue_body"]].mean()) if pm["blue_body"].sum() >= 30 else float("nan")
        row[f"{name}|stripe"] = float(m[pm["blue_stripe"]].mean()) if pm["blue_stripe"].sum() >= 30 else float("nan")
        row[f"{name}|bg"] = float(m[bg].mean()) if bg.any() else 0.0
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--reading", default=READING)
    a = ap.parse_args()
    stems = cm.frames()[cnd.ORDINARY]
    with Pool(a.jobs) as pool:
        rows = pool.map(one, [(s, a.reading) for s in stems], chunksize=4)
    names = [k.split("|")[0] for k in rows[0] if k.endswith("|paint")]
    by = defaultdict(list)
    for r in rows:
        by[r["condition"]].append(r)
    L = [f"# Exploration: blue rules at pixel level (in-sample; the light read by `{a.reading}`)", "",
         "Each cell: share of the labelled blue paint painted (body / stripe) and, after the semicolon, the share of the background painted, in percent. "
         "Means over the condition's frames.", "",
         "| condition | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for c in sorted(by, key=lambda c: (ct.place_of(by[c][0]["stem"]), c)):
        cells = []
        for n in names:
            f = lambda k: float(np.nanmean([r[f"{n}|{k}"] for r in by[c]])) * 100  # noqa: E731
            cells.append(f"{f('body'):.0f} / {f('stripe'):.0f}; {f('bg'):.2f}")
        L.append(f"| {c} | " + " | ".join(cells) + " |")
    text = "\n".join(L) + "\n"
    cm.OUT.mkdir(parents=True, exist_ok=True)
    (cm.OUT / f"explore_blue_{a.reading}.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
