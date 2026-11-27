#!/usr/bin/env python3
"""Part C, the measurement (in-sample, pixel level, no detector): does anything read from the frame predict the
orange hue a place needs, and what does each wider orange range paint besides the barrels?

    python barrels/experiments/2026-11-26_light/explore_orange.py [--jobs 8]

1. From per_frame.csv (measure.py): per condition the labelled orange paint's hue (median and 98th percentile: the
   high end a range must reach) next to things read from the frame: the light's warmth by three readings, the scene's
   cast, how dark the scene below the gate is, and how much of the frame already sits in the band the ottoman needs.
   Correlation over the conditions, and leave one place out per frame (a line fitted on the other places).
2. Per frame, for orange ranges hue 3..hi with S >= s: the share of the labelled orange paint painted, and the share
   of the background painted (rows from 50, brightness >= 40, outside every hand box grown by 4 px).

Ordinary conditions carry every number; the extreme ones are printed beside them. Writes
results/2026-11-26_light/explore_orange.md.
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
import table as tb  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402

BANDS = [(13, 140), (16, 140), (19, 140), (22, 140), (16, 170), (19, 170), (22, 170), (22, 200), (25, 170)]
PREDICTORS = ["without_loose.w", "above_gate20.w", "whole_frame.w", "gray_world.w", "near_strip.w", "v_med_below", "v_mean", "ext_share"]
TARGETS = ["orange_all.h_med", "orange_all.h_p98"]


def one(stem: str) -> dict:
    import cv2
    cv2.setNumThreads(1)
    frame = jg.load_frame(stem)
    pm = cm.paint_masks(stem, frame.shape)
    paint = pm["orange_body"] | pm["orange_stripe"]
    g = cm.gate(frame)
    bg = g & ~pm["boxes"]
    ho, s = cm.hue_orange(frame), cm.sat(frame)
    row = {"stem": stem, "condition": ct.condition_of(stem), "class": cnd.info(ct.condition_of(stem)).klass}
    for hi, s_lo in BANDS:
        m = g & (ho >= 3) & (ho <= hi) & (s >= s_lo)
        row[f"{hi} {s_lo}|paint"] = float(m[paint].mean()) if paint.sum() >= 30 else float("nan")
        row[f"{hi} {s_lo}|bg"] = float(m[bg].mean()) if bg.any() else 0.0
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    rows = tb.load()
    ordinary = [r for r in rows if r["class"] == "ordinary"]
    conds = sorted({r["condition"] for r in rows}, key=lambda c: (next(r["class"] for r in rows if r["condition"] == c) != "ordinary",
                                                                  next(r["place"] for r in rows if r["condition"] == c), c))
    L = ["# Part C, the measurement: what predicts the orange hue (in-sample; pixel level)", "",
         "## Per condition: the orange paint and what can be read from the frame", "",
         "| condition | orange hue median / 98th pct | orange S 10th pct | orange brightness | " + " | ".join(f"`{p}`" for p in PREDICTORS) + " |",
         "|---|---|---|---|" + "---|" * len(PREDICTORS)]
    means = {k: tb.cond_mean(rows, k) for k in PREDICTORS + TARGETS + ["orange_all.s_p10", "orange_all.v_med"]}
    f = lambda k, c, d=2: tb.fmt(means[k].get(c, np.nan), d)  # noqa: E731
    for c in conds:
        ext = "" if next(r["class"] for r in rows if r["condition"] == c) == "ordinary" else " (extreme)"
        L.append(f"| {c}{ext} | {f('orange_all.h_med', c, 1)} / {f('orange_all.h_p98', c, 1)} | {f('orange_all.s_p10', c, 0)} | {f('orange_all.v_med', c, 0)} | "
                 + " | ".join(f(p, c, 0 if p.startswith("v_") else 3 if p == "ext_share" else 2) for p in PREDICTORS) + " |")
    L += ["", "## Does it predict the orange hue?", "",
          "r / rho over the 17 ordinary conditions (and over all 25 with the extreme ones); leave one place out per frame on the ordinary frames: skill = 1 - error / "
          "error of predicting the other places' mean (above 0 = it helps).", "",
          "| read from the frame | orange hue median: r / rho (17) | r / rho (25) | leave one place out: skill (error against baseline, hue units) | "
          "orange hue 98th pct: r / rho (17) | r / rho (25) | leave one place out: skill |", "|---|---|---|---|---|---|---|"]
    oc = [c for c in conds if next(r["class"] for r in rows if r["condition"] == c) == "ordinary"]
    for p in PREDICTORS:
        cells = []
        for t in TARGETS:
            x17, y17 = [means[p].get(c, np.nan) for c in oc], [means[t].get(c, np.nan) for c in oc]
            x25, y25 = [means[p].get(c, np.nan) for c in conds], [means[t].get(c, np.nan) for c in conds]
            lo = tb.lopo(ordinary, p, t)
            cells += [f"{tb.fmt(tb.pearson(x17, y17))} / {tb.fmt(tb.spearman(x17, y17))}", f"{tb.fmt(tb.pearson(x25, y25))} / {tb.fmt(tb.spearman(x25, y25))}",
                      f"{tb.fmt(lo['skill'])} ({tb.fmt(lo['rmse'], 1)} against {tb.fmt(lo['rmse_baseline'], 1)})"]
        L.append(f"| `{p}` | " + " | ".join(cells) + " |")
    lo_all = tb.lopo(rows, "v_med_below", "orange_all.h_med")
    L += ["", f"With the extreme places counted as places too (10 places, analysis only): `v_med_below` -> orange hue median, leave one place out skill "
              f"{tb.fmt(lo_all['skill'])}; `without_loose.w`: {tb.fmt(tb.lopo(rows, 'without_loose.w', 'orange_all.h_med')['skill'])}.", ""]
    stems = [r["stem"] for r in rows]
    with Pool(a.jobs) as pool:
        px = pool.map(one, stems, chunksize=4)
    by = defaultdict(list)
    for r in px:
        by[r["condition"]].append(r)
    names = [f"{hi} {s}" for hi, s in BANDS]
    L += ["## What each orange range paints", "",
          "Orange range hue 3..hi with S >= s (column = `hi s`; `13 140` is the fixed model). Each cell: share of the labelled orange paint painted; after the "
          "semicolon the share of the background painted, in percent.", "",
          "| condition | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for c in conds:
        ext = "" if by[c][0]["class"] == "ordinary" else " (extreme)"
        g = lambda n, k: float(np.nanmean([r[f"{n}|{k}"] for r in by[c]])) * 100  # noqa: E731
        L.append(f"| {c}{ext} | " + " | ".join(f"{g(n, 'paint'):.0f}; {g(n, 'bg'):.2f}" for n in names) + " |")
    text = "\n".join(L) + "\n"
    (cm.OUT / "explore_orange.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
