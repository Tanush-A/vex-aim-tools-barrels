#!/usr/bin/env python3
"""Part A, two more questions, from per_frame.csv (no image is opened; written after the PREREG, in-sample analysis,
not a judged run):

    python barrels/experiments/2026-11-26_light/extra.py

1. Does the reading still track the blue paint when the parked (extreme) conditions are counted too: the wood desk
   under the lamp, the black table, the very dark ottoman? (They are other places; never judged.)
2. Is the light's color enough, or does how dim the scene is matter as well? A line on the reading alone against a line
   on the reading and the brightness of the blue paint's surroundings (the median brightness below the gate), leave one
   place out.

Writes results/2026-11-26_light/readings_extra.md.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import table as tb  # noqa: E402

READINGS = ("without_loose", "above_gate20", "whole_frame", "tiles", "max_rgb", "gray_world")
T = "blue_all.s_med"


def lopo2(rows: list[dict], xkeys: list[str], ykey: str) -> dict:
    """Leave one place out with several inputs (a plane), every place weighing the same."""
    use = [r for r in rows if all(np.isfinite(r[k]) for k in xkeys) and np.isfinite(r[ykey])]
    n_place = defaultdict(int)
    for r in use:
        n_place[r["place"]] += 1
    mse, mse0 = [], []
    for p in sorted(n_place):
        tr, te = [r for r in use if r["place"] != p], [r for r in use if r["place"] == p]
        w = np.sqrt(np.array([1.0 / n_place[r["place"]] for r in tr]))
        X = np.array([[1.0] + [r[k] for k in xkeys] for r in tr])
        y = np.array([r[ykey] for r in tr])
        coef, *_ = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)
        y0 = float(np.average(y, weights=w ** 2))
        Xt, yt = np.array([[1.0] + [r[k] for k in xkeys] for r in te]), np.array([r[ykey] for r in te])
        mse.append(float(np.mean((Xt @ coef - yt) ** 2)))
        mse0.append(float(np.mean((y0 - yt) ** 2)))
    return {"rmse": float(np.mean(mse)) ** 0.5, "rmse_baseline": float(np.mean(mse0)) ** 0.5, "skill": 1.0 - float(np.mean(mse)) / float(np.mean(mse0)), "places": len(mse)}


def main() -> int:
    rows = tb.load()
    ordinary = [r for r in rows if r["class"] == "ordinary"]
    conds = sorted({r["condition"] for r in rows})
    oconds = sorted({r["condition"] for r in ordinary})
    means = {k: tb.cond_mean(rows, k) for k in [f"{n}.w" for n in READINGS] + [T, "blue_all.v_med", "v_med_below"]}
    L = ["# Part A, two more questions (in-sample; written after the pre-registration; not a judged run)", "",
         "## 1. With the parked conditions counted too", "",
         "r / rho between a reading's condition mean and the blue paint's median S.", "",
         "| reading | 17 ordinary conditions | all 25 (the wood desk lamp ladder, the black table, the very dark ottoman added) | "
         "leave one place out line, 8 ordinary places: skill | 10 places: skill |", "|---|---|---|---|---|"]
    for n in READINGS:
        k = f"{n}.w"
        a = lambda cs: f"{tb.fmt(tb.pearson([means[k].get(c, np.nan) for c in cs], [means[T].get(c, np.nan) for c in cs]))} / " \
                       f"{tb.fmt(tb.spearman([means[k].get(c, np.nan) for c in cs], [means[T].get(c, np.nan) for c in cs]))}"  # noqa: E731
        L.append(f"| `{n}` | {a(oconds)} | {a(conds)} | {tb.fmt(tb.lopo(ordinary, k, T)['skill'])} | {tb.fmt(tb.lopo(rows, k, T)['skill'])} |")
    L += ["", "The lamp conditions side by side (ordinary and parked): the reading, how bright the scene is, and the blue paint.", "",
          "| condition | class | `without_loose` | median brightness below the gate | blue paint brightness | blue paint S (median) |", "|---|---|---|---|---|---|"]
    lamp = [c for c in conds if c.startswith("lamp") and "glass" not in c]
    for c in sorted(lamp, key=lambda c: (c.split("_")[1], c)):
        klass = next(r["class"] for r in rows if r["condition"] == c)
        L.append(f"| {c} | {klass} | {tb.fmt(means['without_loose.w'].get(c, np.nan))} | {tb.fmt(means['v_med_below'].get(c, np.nan), 0)} | "
                 f"{tb.fmt(means['blue_all.v_med'].get(c, np.nan), 0)} | {tb.fmt(means[T].get(c, np.nan), 0)} |")
    L += ["", "## 2. The light's color alone, or the color and how dim it is", "",
          "Leave one place out, per frame, target = the blue paint's median S. The second input is the median brightness of the frame below the gate "
          "(readable without knowing where a barrel is).", "",
          "| inputs | 8 ordinary places: skill (error against baseline, S units) | 10 places with the parked ones: skill (error against baseline) |", "|---|---|---|"]
    for name, keys in (("`without_loose` alone", ["without_loose.w"]), ("`without_loose` and the scene's brightness", ["without_loose.w", "v_med_below"]),
                       ("the scene's brightness alone", ["v_med_below"]), ("`above_gate20` alone", ["above_gate20.w"]),
                       ("`above_gate20` and the scene's brightness", ["above_gate20.w", "v_med_below"])):
        a, b = lopo2(ordinary, keys, T), lopo2(rows, keys, T)
        L.append(f"| {name} | {tb.fmt(a['skill'])} ({tb.fmt(a['rmse'], 0)} against {tb.fmt(a['rmse_baseline'], 0)}) | {tb.fmt(b['skill'])} ({tb.fmt(b['rmse'], 0)} against {tb.fmt(b['rmse_baseline'], 0)}) |")
    text = "\n".join(L) + "\n"
    (cm.OUT / "readings_extra.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
