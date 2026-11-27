#!/usr/bin/env python3
"""EXPLORATION (listed in PREREG.md): where do the blue and the orange pixels of the barrels sit in hue and
saturation on the bathroom floor, and where do the floor's pixels sit?

Bathroom train frames only. Per condition, pooled over its frames with barrels: for each color the zone pixels
(``barrels.placecal.zones``: body rows of that color's barrels, stripe rows of the other color's) and the pixels
outside every box, in a coarse (hue x S) table. Then, for a list of blue rectangles, how many zone pixels and how
many outside pixels each paints.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-26_place_ceiling/explore/bath_hist.py [surface]
"""
from __future__ import annotations

import sys

import numpy as np

from barrels import counting as ct, hslabel as hl, io, judge as jg, placecal as pc

S_BINS = (0, 20, 40, 60, 100, 150, 256)
H_STEP = 10
RECTS = {"adopted 103-119 S>=113": (103, 119, 113), "olive 26-44 S>=20": (26, 44, 20), "olive 20-50 S>=15": (20, 50, 15),
         "olive 26-44 S>=30": (26, 44, 30), "wide 20-125 S>=15": (20, 125, 15), "60-125 S>=10": (60, 125, 10),
         "85-125 S>=30": (85, 125, 30), "85-125 S>=50": (85, 125, 50), "95-120 S>=60": (95, 120, 60)}


def coarse(h: np.ndarray) -> np.ndarray:
    """(180, 256) counts -> (18, 6) counts."""
    out = np.zeros((180 // H_STEP, len(S_BINS) - 1), np.int64)
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            out[i, j] = h[i * H_STEP:(i + 1) * H_STEP, S_BINS[j]:S_BINS[j + 1]].sum()
    return out


def pct(h: np.ndarray, axis: int, qs=(5, 25, 50, 75, 95)) -> list[int]:
    m = h.sum(1 - axis)
    c = np.cumsum(m)
    if c[-1] == 0:
        return []
    return [int(np.searchsorted(c, q / 100 * c[-1])) for q in qs]


def main() -> None:
    surface = sys.argv[1] if len(sys.argv) > 1 else "bathtile"
    frames = jg.train_frames()
    stems = [s for s in frames["ordinary"] + frames["extreme"] if ct.condition_of(s).endswith("_" + surface)]
    jg.require_train(stems)
    base = hl.adopted_model()
    for cond, ss in sorted(ct.group_stems(sorted(stems), "condition").items()):
        total, n_frames = None, 0
        per_zone = {"blue body": np.zeros((180, 256), np.int64), "blue stripe": np.zeros((180, 256), np.int64),
                    "orange body": np.zeros((180, 256), np.int64), "orange stripe": np.zeros((180, 256), np.int64)}
        dark = {"blue": [0, 0], "orange": [0, 0]}
        for s in ss:
            boxes = io.load_boxes(s, check_image=False)["barrels"]
            if not boxes:
                continue
            frame = jg.load_frame(s)
            n_frames += 1
            total = pc.add_hists(total, pc.frame_hists(frame, boxes, base))
            keep = np.asarray(frame.val) >= base.cfg.v_min
            for color in ("orange", "blue"):          # body and stripe apart, to see whether they differ
                own = [b for b in boxes if b["color"] == color]
                oth = [b for b in boxes if b["color"] != color]
                zb = pc.zones(frame.shape, own, base.cfg.horizon_row).pos[color]
                zs = pc.zones(frame.shape, oth, base.cfg.horizon_row).pos[color]
                hs = frame.hs(30 if color == "orange" else 0)
                per_zone[f"{color} body"] += pc._hist(hs, keep & zb)
                per_zone[f"{color} stripe"] += pc._hist(hs, keep & zs)
                dark[color][0] += int(((zb | zs) & ~keep).sum())
                dark[color][1] += int((zb | zs).sum())
        print(f"\n=================== {cond}: {n_frames} frames with barrels")
        for name, h in per_zone.items():
            shift = 30 if name.startswith("orange") else 0
            hp = [v - shift for v in pct(h, 0)]
            print(f"  {name:13s} {int(h.sum()):6d} px   hue 5/25/50/75/95 %: {hp}   S: {pct(h, 1)}")
        for color in ("blue", "orange"):
            print(f"  {color}: {dark[color][0]} of {dark[color][1]} zone pixels are under the brightness floor (V < {base.cfg.v_min})")
        hin, hout = total["blue"]
        ci, co = coarse(hin), coarse(hout)
        print("  BLUE zone pixels / pixels blue must not paint, by hue (rows) and S (columns " + ", ".join(f"{a}-{b - 1}" for a, b in zip(S_BINS, S_BINS[1:])) + ")")
        for i in range(ci.shape[0]):
            if ci[i].sum() + co[i].sum() == 0:
                continue
            print(f"   hue {i * H_STEP:3d}-{i * H_STEP + H_STEP - 1:3d}  " + "  ".join(f"{ci[i, j]:5d}/{co[i, j]:<6d}" for j in range(ci.shape[1])))
        print("  blue rectangles: zone pixels painted (of %d) / must-not pixels painted (of %d)" % (hin.sum(), hout.sum()))
        for name, (a, b, s0) in RECTS.items():
            print(f"   {name:24s} {int(hin[a:b + 1, s0:].sum()):6d} / {int(hout[a:b + 1, s0:].sum()):6d}")
        hin, hout = total["orange"]
        ci, co = coarse(hin), coarse(hout)
        print("  ORANGE zone pixels / must-not pixels, by hue (rows, real hue; -30 = 150) and S")
        for i in range(ci.shape[0]):
            if ci[i].sum() + co[i].sum() == 0:
                continue
            print(f"   hue {i * H_STEP - 30:3d}-{i * H_STEP + H_STEP - 31:3d}  " + "  ".join(f"{ci[i, j]:5d}/{co[i, j]:<6d}" for j in range(ci.shape[1])))
        adopted = hl.thresholds_from_model(base)
        for w in pc.NET_WEIGHTS:
            print(f"  pooled net setting, outside weight {w:g}: {pc.net_from_hists(total, adopted, w)}")


if __name__ == "__main__":
    main()
