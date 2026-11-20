#!/usr/bin/env python3
"""A census after round 1 and before round 2 (no acceptance number comes from here): does the outline "know" wrongly
when the cut is slanted, and what stops it?

Round 1 placed some barrels cut by a SLANTED edge in the wrong place: a slanted cut imitates a rounded corner on the
top line or on the bottom line (never both), and the mean over the three lines let one good line pay for a bad one.
This census repeats ``shape_census.py`` part C on the scorecard's own scenes (a straight edge, a slanted edge, both
sides; 25 / 50 / 75 % hidden) for two ways of putting the three lines together:

  ``mean``   the cost of a position = the mean of the three lines' distances (round 1);
  ``worst``  the cost of a position = the largest of the three lines' distances: every line must fit.

and for the best cost limited to 0.05 H or 0.03 H.

    python barrels/experiments/2026-11-20_occl_pin/slant_census.py
Output: results/2026-11-20_occl_pin/slant_census.md.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
spec = importlib.util.spec_from_file_location("shape_census", HERE / "shape_census.py")
C = importlib.util.module_from_spec(spec); sys.modules["shape_census"] = C; spec.loader.exec_module(C)
from barrels import occlude as oc  # noqa: E402

R, OUT = C.R, C.OUT
NEAR, HALF = 0.01, 0.15


def curves(m):
    """(centres, mean cost, worst cost) of the outline slid over the seen part."""
    W, ol, xs = m["W"], m["ol"], m["xs"]
    lo, hi = m["sx1"] - 0.65 * W, m["sx0"] + 0.65 * W
    if hi < lo:
        return None
    per = []
    for seen, line in ((m["top"], ol.top), (m["st"], ol.stripe), (m["bot"], ol.bottom)):
        cands, cost = C.slide(xs, [(seen, line)], W, lo, hi)
        if not np.all(np.isnan(cost)):
            per.append(cost)
    if not per:
        return None
    per = np.array(per)
    return cands, per.mean(axis=0), per.max(axis=0)


def verdict(cands, cost, m, good):
    best = float(np.nanmin(cost))
    fit = cands[cost <= best + NEAR * m["H"]]
    mid = (fit.min() + fit.max()) / 2
    return (best <= good * m["H"] and fit.max() - mid <= HALF * m["W"]), mid


def main() -> int:
    pools, _ = R.build_sources(R.segmentations(R.train_stems()))
    rows = []
    for pool in R.POOLS:
        for src in pools[pool]:
            cx_true = (src.bbox[0] + src.bbox[2]) / 2
            variants = [("a straight edge", "edge", a, s, 1) for a in oc.AMOUNTS for s in ("L", "R")]
            variants += [("a slanted edge", "slant", a, s, ln) for a in oc.AMOUNTS for s in ("L", "R") for ln in (1, -1)]
            variants += [("both sides (equal)", "both", a, "L", 1) for a in oc.AMOUNTS]
            for name, kind, amount, side, lean in variants:
                sc = oc.make_scene(src, kind, amount, side, lean=lean)
                m = C.measure(sc.mask, src.color)
                cv = curves(m) if m is not None else None
                row = {"kind": name, "hidden": amount}
                if cv is not None:
                    for agg, cost in (("mean", cv[1]), ("worst", cv[2])):
                        for good in (0.05, 0.03):
                            k, mid = verdict(cv[0], cost, m, good)
                            row[(agg, good)] = (k, abs(mid - cx_true) / src.width)
                rows.append(row)
    L = ["# Does the outline know wrongly when the cut is slanted? (a census after round 1; no acceptance number)", "",
         "The scorecard's own scenes (50 source barrels). Each cell: **scenes where the outline knows / of those, the centre wrong by more than 0.15 W / "
         "the largest error**, of n scenes. `mean` = the cost of a position is the mean of the three lines' distances (round 1); `worst` = it is the "
         "largest of the three (every line must fit). Fitting = within 0.01 H of the best; knows = every fitting position within 0.15 W of their "
         "middle and the best cost at most the limit.", "",
         "| what hides the barrel | hidden | n | mean, 0.05 H | mean, 0.03 H | worst, 0.05 H | worst, 0.03 H |", "|---|---|---|---|---|---|---|"]
    for name in ("a straight edge", "a slanted edge", "both sides (equal)"):
        for amount in oc.AMOUNTS:
            rs = [r for r in rows if r["kind"] == name and r["hidden"] == amount]
            cells = []
            for key in (("mean", 0.05), ("mean", 0.03), ("worst", 0.05), ("worst", 0.03)):
                v = [r[key][1] for r in rs if key in r and r[key][0]]
                cells.append(f"{len(v)} / {sum(e > 0.15 for e in v)} / {max(v) if v else 0:.2f}")
            L.append(f"| {name} | {int(amount * 100)} % | {len(rs)} | " + " | ".join(cells) + " |")
    (OUT / "slant_census.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
