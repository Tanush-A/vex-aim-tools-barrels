#!/usr/bin/env python3
"""Exploration (before the pre-registration): a grid of orange rules (constant sectors and hysteresis), each with
the blue part fixed or "light", summarised per rule: found, false, boxes on empty frames, and the conditions whose
score (mean of the orange and blue F1) drops by more than 0.02 against the fixed model. Train frames only.

    python barrels/experiments/2026-11-25_color/grid.py [--blue fixed|light] [--kind const|hyst]
"""
from __future__ import annotations

import argparse
import itertools
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import explore as ex  # noqa: E402


def cond_scores(res: dict, spec: str) -> dict:
    agg = defaultdict(lambda: {"tp": np.zeros(2), "fp": np.zeros(2), "gt": np.zeros(2), "e": 0})
    for stem, out in res.items():
        c = cm.condition_of(stem)
        if cm.class_of(c) != "ordinary":
            continue
        r = out[spec]
        a = agg[c]
        for i, k in enumerate(("1", "2")):
            a["tp"][i] += r["tp"].get(k, 0); a["fp"][i] += r["fp"].get(k, 0); a["gt"][i] += r["n_gt"].get(k, 0)
        if r["neg"]:
            a["e"] += sum(r["fp"].values())
    out = {}
    for c, a in agg.items():
        f1 = []
        for i in range(2):
            den = 2 * a["tp"][i] + a["fp"][i] + (a["gt"][i] - a["tp"][i])
            if den > 0:
                f1.append(2 * a["tp"][i] / den)
        out[c] = {"score": float(np.mean(f1)) if f1 else float("nan"), "found": int(a["tp"].sum()), "barrels": int(a["gt"].sum()),
                  "false": int(a["fp"].sum()), "empty": a["e"]}
    return out


def summary(res: dict, specs: list[str], ref: str = "fixed") -> list[str]:
    base = cond_scores(res, ref)
    lines = []
    for s in specs:
        cs = cond_scores(res, s)
        drops = [f"{c.split('_')[0][:9]}_{c.split('_')[1][:5]}{cs[c]['score'] - base[c]['score']:+.2f}" for c in cs
                 if cs[c]["score"] < base[c]["score"] - 0.02]
        f = sum(v["found"] for v in cs.values()); fa = sum(v["false"] for v in cs.values()); e = sum(v["empty"] for v in cs.values())
        lines.append((f - 2 * fa, f"{s:70s} found {f} false {fa} empty {e}  drops: {' '.join(drops) or '-'}"))
    return [x[1] for x in sorted(lines, key=lambda t: -t[0])]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blue", default="fixed")
    ap.add_argument("--kind", default="const")
    a = ap.parse_args()
    blue = "" if a.blue == "fixed" else ",blue=light,w0=0.1,w1=0.25,s_warm=40,h_warm=92"
    specs = ["fixed"]
    if a.kind == "const":
        for lo, hi, s in itertools.product((-4, -2, 0), (15, 16, 17, 18, 19), (140, 150, 160, 170)):
            specs.append(f"combo:orange=const,o_const={lo}/{hi}/{s}{blue}")
    else:
        for lo, hi, s, r in itertools.product((-5, -3), (17, 19, 21), (150, 160, 170), (4, 8)):
            specs.append(f"combo:orange=hyst,o_loose={lo}/{hi}/{s},radius={r}{blue}")
    res = ex.run(specs)
    for line in summary(res, specs)[:25]:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
