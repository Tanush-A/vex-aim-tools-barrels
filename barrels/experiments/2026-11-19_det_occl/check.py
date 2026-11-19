#!/usr/bin/env python3
"""PREREG rule 4, read off a scorecard run: for every arm against ``base``, the cells (kind x amount, the three pools
together) where found (v2) or the right-place count is lower, the cells where found is higher, and the false boxes
of the whole card. Reads ``cells.csv`` of a results folder; computes nothing new.

    python barrels/experiments/2026-11-19_det_occl/check.py round1
Output: results/2026-11-19_det_occl/<folder>/scorecard_check.md, and the same as text.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-19_det_occl"
# the cells each switch is aimed at (PREREG rule 4): found must be higher there
TARGETS = {
    "slice": [("frame", 0.75), ("edge", 0.75), ("slant", 0.75), ("both", 0.75), ("block/same", 0.75), ("block/other", 0.75), ("edge", 0.5), ("slant", 0.5)],
    "two": [("barrel_side/same", 0.5)],
    "edge": [("barrel_front/other", 0.25)],
    "cap": [("barrel_front/same", 0.5)],
}
TARGETS["slice+cover"] = TARGETS["slice"]
TARGETS["edge+cap"] = TARGETS["edge"] + TARGETS["cap"]
TARGETS["all"] = TARGETS["all-cover"] = TARGETS["slice"] + TARGETS["two"] + TARGETS["edge"] + TARGETS["cap"]


def main(argv=None) -> int:
    folder = OUT / (sys.argv[1] if len(sys.argv) > 1 else "")
    rows = [r for r in csv.DictReader((folder / "cells.csv").open()) if r["pool"] == "ALL"]
    cells = {(r["arm"], r["row"], float(r["amount"])): r for r in rows}
    arms = list(dict.fromkeys(r["arm"] for r in rows))
    keys = list(dict.fromkeys((r["row"], float(r["amount"])) for r in rows))

    def tot(arm, field):
        return sum(int(cells[(arm, *k)][field]) for k in keys)

    L = ["# The scorecard against PREREG rule 4, per arm", "",
         f"`base`: found {tot('base', 'found_v2')}, right place {tot('base', 'right_place')}, false boxes {tot('base', 'false_boxes')}, "
         f"of {tot('base', 'n')} scenes.", "",
         "| arm | found | right place | false boxes | cells where found is lower | cells where right place is lower | target cells not higher | rule 4 |", "|---|---|---|---|---|---|---|---|"]
    detail = []
    for a in arms:
        if a == "base":
            continue
        lower_f = [(k, int(cells[("base", *k)]["found_v2"]), int(cells[(a, *k)]["found_v2"])) for k in keys if int(cells[(a, *k)]["found_v2"]) < int(cells[("base", *k)]["found_v2"])]
        lower_p = [(k, int(cells[("base", *k)]["right_place"]), int(cells[(a, *k)]["right_place"])) for k in keys
                   if int(cells[(a, *k)]["right_place"]) < int(cells[("base", *k)]["right_place"])]
        flat = [k for k in TARGETS.get(a, []) if int(cells[(a, *k)]["found_v2"]) <= int(cells[("base", *k)]["found_v2"])]
        more_false = tot(a, "false_boxes") > tot("base", "false_boxes")
        ok = not lower_f and not lower_p and not flat and not more_false
        L.append(f"| {a} | {tot(a, 'found_v2')} | {tot(a, 'right_place')} | {tot(a, 'false_boxes')}{' (more)' if more_false else ''} | {len(lower_f)} | {len(lower_p)} | "
                 f"{len(flat)} | {'pass' if ok else '**FAILS**'} |")
        for name, lst in (("found lower", lower_f), ("right place lower", lower_p)):
            for (row, amount), b, c in lst:
                detail.append(f"- `{a}`, {name}: {row} at {int(round(100 * amount))} %: {b} → {c} of {cells[('base', row, amount)]['n']}")
        for row, amount in flat:
            detail.append(f"- `{a}`, target not higher: {row} at {int(round(100 * amount))} %: {cells[('base', row, amount)]['found_v2']} → {cells[(a, row, amount)]['found_v2']}")
    L += [""] + detail
    (folder / "scorecard_check.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
