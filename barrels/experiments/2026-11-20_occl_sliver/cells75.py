#!/usr/bin/env python3
"""Every 75 % cell of the scorecard, before (`start`) and after each arm: found (v2) / right place / too big / boxes where no
barrel is, from a battery round's ``cells.csv`` (pool ALL). Also every cell at 25 or 50 % that an arm changes.

    python barrels/experiments/2026-11-20_occl_sliver/cells75.py round2 [--arms start,bridge,frame,close,span,sliver,start+behind]
Outputs: results/2026-11-20_occl_sliver/<round>/cells75.md
"""
from __future__ import annotations

import argparse
import csv

import sliver as S

NAMES = {"frame": "cut by the frame edge", "edge": "a straight upright edge", "slant": "a slanted edge", "both": "both sides cut",
         "top": "hidden from above", "bottom": "hidden from below", "post": "a post across the middle",
         "barrel_side/other": "other color, beside", "barrel_low/other": "other color, beside and lower",
         "barrel_front/other": "other color, straight in front", "barrel_side/same": "same color, beside",
         "barrel_low/same": "same color, beside and lower", "barrel_front/same": "same color, straight in front",
         "block/same": "a block of the body color", "block/other": "a block of the stripe color"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("round")
    ap.add_argument("--arms", default="start,bridge,frame,close,span,sliver,start+behind")
    a = ap.parse_args(argv)
    arms = a.arms.split(",")
    d = {}
    for r in csv.DictReader((S.OUT / a.round / "cells.csv").open()):
        if r["pool"] == "ALL":
            d[(r["arm"], r["row"], r["amount"])] = r

    def cell(arm, row, am):
        r = d[(arm, row, am)]
        return f"{r['found_v2']} / {r['right_place']} / {r['too_big']} / {r['false_boxes']}"

    L = [f"# The scorecard cells, `{a.round}`: found (v2) / right place / too big / boxes where no barrel is", "",
         "Pool ALL (50 source barrels). `start` = the defaults before this experiment. Each cell's n is in `cells.csv`.", "",
         "## Every cell at 75 % hidden", "", "| what hides the barrel (n) | " + " | ".join(f"`{x}`" for x in arms) + " |", "|---|" + "---|" * len(arms)]
    for row, name in NAMES.items():
        if (arms[0], row, "0.75") in d:
            L.append(f"| {name} ({d[(arms[0], row, '0.75')]['n']}) | " + " | ".join(cell(x, row, "0.75") for x in arms) + " |")
    L += ["", "## Cells at 25 and 50 % that any arm changes", "", "| cell | " + " | ".join(f"`{x}`" for x in arms) + " |", "|---|" + "---|" * len(arms)]
    for row, name in NAMES.items():
        for am in ("0.25", "0.5"):
            if (arms[0], row, am) in d and len({cell(x, row, am) for x in arms}) > 1:
                L.append(f"| {name}, {int(float(am) * 100)} % | " + " | ".join(cell(x, row, am) for x in arms) + " |")
    (S.OUT / a.round / "cells75.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
