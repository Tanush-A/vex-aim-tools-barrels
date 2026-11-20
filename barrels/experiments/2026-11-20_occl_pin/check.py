#!/usr/bin/env python3
"""The scorecard against the PREREG's scorecard clauses, read off a scorecard run: for every arm against ``base``, the
cells (kind x amount, the three pools together) where found (v2) or the right-place count is lower, the targeted
cells one by one and their sum, the boxes where no barrel is, and the share of right-place boxes that are too big.
Reads ``cells.csv`` of a results folder; computes nothing new.

    python barrels/experiments/2026-11-20_occl_pin/check.py [round1]
Output: results/2026-11-20_occl_pin/<folder>/scorecard_check.md, and the same as text.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_occl_pin"
# the targeted cells (PREREG): the straight edge, the slanted edge, both sides, the frame edge, the two plain blocks, at 50 and 75 % hidden
TARGETS = [(row, amount) for row in ("edge", "slant", "both", "frame", "block/same", "block/other") for amount in (0.5, 0.75)]
# the cells each arm commits to raising (PREREG, "Expected")
COMMITTED = {
    "pin": [("edge", 0.5), ("slant", 0.5)],
    "pin+thin": [("edge", 0.5), ("slant", 0.5), ("edge", 0.75), ("slant", 0.75), ("frame", 0.75), ("block/same", 0.75)],
}


def main(argv=None) -> int:
    folder = OUT / (sys.argv[1] if len(sys.argv) > 1 else "")
    rows = [r for r in csv.DictReader((folder / "cells.csv").open()) if r["pool"] == "ALL"]
    cells = {(r["arm"], r["row"], float(r["amount"])): r for r in rows}
    arms = list(dict.fromkeys(r["arm"] for r in rows))
    keys = list(dict.fromkeys((r["row"], float(r["amount"])) for r in rows))

    def v(arm, key, field):
        return int(cells[(arm, *key)][field])

    def tot(arm, field, ks=None):
        return sum(v(arm, k, field) for k in (ks or keys))

    def big_share(arm):
        return tot(arm, "too_big") / max(1, tot(arm, "right_place"))

    L = ["# The scorecard against the PREREG's scorecard clauses, per arm", "",
         f"`base`: found {tot('base', 'found_v2')}, right place {tot('base', 'right_place')}, boxes where no barrel is {tot('base', 'false_boxes')}, "
         f"too big {tot('base', 'too_big')} of the right-place boxes ({100 * big_share('base'):.2f} %), of {tot('base', 'n')} scenes. "
         f"Targeted cells together: {tot('base', 'found_v2', TARGETS)} of {tot('base', 'n', TARGETS)}.", "",
         "| arm | found | right place | boxes where no barrel is | too big (share) | cells with found lower | cells with right place lower | targeted cells together | "
         "committed cells not higher | scorecard clauses |", "|---|---|---|---|---|---|---|---|---|---|"]
    detail = []
    for a in arms:
        if a == "base":
            continue
        lower_f = [k for k in keys if v(a, k, "found_v2") < v("base", k, "found_v2")]
        lower_p = [k for k in keys if v(a, k, "right_place") < v("base", k, "right_place")]
        flat = [k for k in COMMITTED.get(a, []) if v(a, k, "found_v2") <= v("base", k, "found_v2")]
        more_false = tot(a, "false_boxes") > tot("base", "false_boxes")
        more_big = big_share(a) > big_share("base")
        t_up = tot(a, "found_v2", TARGETS) > tot("base", "found_v2", TARGETS)
        ok = not lower_f and not lower_p and not flat and not more_false and not more_big and t_up
        L.append(f"| {a} | {tot(a, 'found_v2')} | {tot(a, 'right_place')} | {tot(a, 'false_boxes')}{' (more)' if more_false else ''} | "
                 f"{tot(a, 'too_big')} ({100 * big_share(a):.2f} %){' (more)' if more_big else ''} | {len(lower_f)} | {len(lower_p)} | "
                 f"{tot('base', 'found_v2', TARGETS)} → {tot(a, 'found_v2', TARGETS)} | {len(flat)} | {'pass' if ok else '**FAILS**'} |")
        for name, lst, field in (("found lower", lower_f, "found_v2"), ("right place lower", lower_p, "right_place")):
            for k in lst:
                detail.append(f"- `{a}`, {name}: {k[0]} at {int(round(100 * k[1]))} %: {v('base', k, field)} → {v(a, k, field)} of {v('base', k, 'n')}")
        for k in flat:
            detail.append(f"- `{a}`, committed cell not higher: {k[0]} at {int(round(100 * k[1]))} %: {v('base', k, 'found_v2')} → {v(a, k, 'found_v2')}")
    L += [""] + detail + ["", "## The targeted cells, found of n", "", "| cell | n | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|---|" + "---|" * len(arms)]
    for k in TARGETS:
        L.append(f"| {k[0]} at {int(round(100 * k[1]))} % | {v('base', k, 'n')} | " + " | ".join(str(v(a, k, "found_v2")) for a in arms) + " |")
    L += ["", "## Every other cell that changes (found; right place)", "", "| cell | n | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|---|" + "---|" * len(arms)]
    for k in keys:
        if k in TARGETS:
            continue
        if any(v(a, k, f) != v("base", k, f) for a in arms for f in ("found_v2", "right_place")):
            L.append(f"| {k[0]} at {int(round(100 * k[1]))} % | {v('base', k, 'n')} | " + " | ".join(f"{v(a, k, 'found_v2')}; {v(a, k, 'right_place')}" for a in arms) + " |")
    (folder / "scorecard_check.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
