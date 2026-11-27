#!/usr/bin/env python3
"""Part B, the table: every B4 box that is not on its barrel, with its measurements, next to the spread of the same
measurement over every real barrel B4 finds (state found or off). In-sample, all eight places: this is what the
checks were designed from, and it is never a verdict. Writes results/2026-11-27_bluer_geom/false_boxes.md."""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg  # noqa: E402

FEATS = ["w_ratio", "h_ratio", "seen_w_ratio", "fill", "body_fill", "top_err", "bot_err", "stripe_h_ratio", "stripe_over_body",
         "up_share", "low_share", "bands_alike", "bulge_top", "bulge_bot", "aspect",
         "stripe_w_ratio", "ring_left", "ring_right", "ring_lr_min", "ring_top", "solid"]


def num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def load(arm="b4"):
    with open(bg.OUT / "boxes.csv") as fh:
        return [r for r in csv.DictReader(fh) if r["arm"] == arm]


def main() -> int:
    rows = load()
    real = [r for r in rows if r["state"] in ("found", "off")]
    bad = [r for r in rows if r["state"] not in ("found", "off")]
    L = ["# B4's boxes that are not on their barrel, measured (in-sample, all eight places; never a verdict)", "",
         f"B4 = the light experiment's candidate, each place under the setting its own fold picked. {len(rows)} boxes on the 154 ordinary train frames: "
         f"{len(real)} on a real barrel (found or box off), {len(bad)} not on their barrel. Measurements: `stages.measure` (definitions in `stages.py`).", "",
         "## The real barrels: the spread of each measurement", "",
         "| measurement | n | min | 1 % | 5 % | median | 95 % | 99 % | max |", "|---|---|---|---|---|---|---|---|---|"]
    for f in FEATS:
        v = np.array([x for x in (num(r[f]) for r in real) if x is not None])
        if v.size:
            q = np.percentile(v, [0, 1, 5, 50, 95, 99, 100])
            L.append(f"| {f} | {v.size} | " + " | ".join(f"{x:.2f}" for x in q) + " |")
    by_rule = {}
    for r in real:
        by_rule[r["rule"]] = by_rule.get(r["rule"], 0) + 1
    L += ["", "Real barrels by the rule that drew them: " + ", ".join(f"{k} {v}" for k, v in sorted(by_rule.items(), key=lambda kv: -kv[1])), ""]
    L += ["## Every box not on its barrel", "",
          "| # | frame | state | also with fixed colors | color | rule | box | " + " | ".join(FEATS) + " |",
          "|---|---|---|---|---|---|---|" + "---|" * len(FEATS)]
    for k, r in enumerate(bad):
        cells = []
        for f in FEATS:
            x = num(r[f])
            cells.append("" if x is None else f"{x:.2f}")
        L.append(f"| {k + 1} | {r['stem'].replace('4A8B_', '')} | {r['state']} | {r['in_fixed']} | {r['color']} | {r['rule']} | "
                 f"{r['x0']},{r['y0']} {r['w']}x{r['h']} | " + " | ".join(cells) + " |")
    # for each measurement: how many false boxes fall outside the real barrels' 1-99 % range
    L += ["", "## How far each measurement separates (in-sample)", "",
          "For each measurement: the false boxes outside the real barrels' range (min..max), and outside 1 %..99 %.", "",
          "| measurement | false boxes below real min / above real max | below 1 % / above 99 % |", "|---|---|---|"]
    for f in FEATS:
        v = np.array([x for x in (num(r[f]) for r in real) if x is not None])
        fb = [num(r[f]) for r in bad]
        fb = [x for x in fb if x is not None]
        if not v.size:
            continue
        lo, hi = v.min(), v.max()
        p1, p99 = np.percentile(v, [1, 99])
        L.append(f"| {f} | {sum(x < lo for x in fb)} / {sum(x > hi for x in fb)} | {sum(x < p1 for x in fb)} / {sum(x > p99 for x in fb)} |")
    (bg.OUT / "false_boxes.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
