#!/usr/bin/env python3
"""PREREG rule 3, read off a scorecard run: for every arm against ``base``, the false boxes of the whole card (not
above ``base``'s), the cells (kind x amount, the three pools together) where found (v2) or the right-place count is
lower, and the target cells where found is not higher. Then the seven rows of this experiment, arm by arm. Reads
``cells.csv`` of a results folder; computes nothing new.

    python barrels/experiments/2026-11-20_occl_vertical/check.py [round1]
Output: results/2026-11-20_occl_vertical/<folder>/scorecard_check.md, and the same as text.
"""
from __future__ import annotations

import csv
import sys

import common

TARGETS = {
    "half": [("top", 0.5)],
    "half+thin": [("top", 0.5), ("bottom", 0.5)],
    "post": [("post", 0.5)],
    "wide": [("barrel_side/same", 0.25), ("barrel_side/same", 0.5)],
    "behind": [("barrel_low/same", 0.75)],
    "caplow": [("barrel_front/other", 0.75), ("barrel_front/same", 0.75)],
}
TARGETS["all"] = sorted({t for v in TARGETS.values() for t in v})
ROW_NAMES = {"top": "hidden from above", "bottom": "hidden from below", "post": "a post across the middle",
             "barrel_front/other": "OTHER color straight in front", "barrel_front/same": "SAME color straight in front",
             "barrel_side/same": "SAME color beside", "barrel_low/same": "SAME color beside and lower"}


def main(argv=None) -> int:
    folder = common.OUT / (sys.argv[1] if len(sys.argv) > 1 else "")
    rows = [r for r in csv.DictReader((folder / "cells.csv").open()) if r["pool"] == "ALL"]
    cells = {(r["arm"], r["row"], float(r["amount"])): r for r in rows}
    arms = list(dict.fromkeys(r["arm"] for r in rows))
    keys = list(dict.fromkeys((r["row"], float(r["amount"])) for r in rows))

    def tot(arm, field):
        return sum(int(cells[(arm, *k)][field]) for k in keys)

    def val(arm, k, field):
        return int(cells[(arm, *k)][field])

    L = ["# The scorecard against PREREG rule 3, per arm", "",
         f"`base`: found {tot('base', 'found_v2')}, right place {tot('base', 'right_place')}, boxes where no barrel is {tot('base', 'false_boxes')}, "
         f"of {tot('base', 'n')} scenes.", "",
         "| arm | found | right place | boxes where no barrel is | cells where found is lower | cells where right place is lower | target cells not higher | rule 3 |",
         "|---|---|---|---|---|---|---|---|"]
    detail = []
    for a in arms:
        if a == "base":
            continue
        lower_f = [k for k in keys if val(a, k, "found_v2") < val("base", k, "found_v2")]
        lower_p = [k for k in keys if val(a, k, "right_place") < val("base", k, "right_place")]
        flat = [k for k in TARGETS.get(a, []) if val(a, k, "found_v2") <= val("base", k, "found_v2")]
        more_false = tot(a, "false_boxes") > tot("base", "false_boxes")
        ok = not lower_f and not lower_p and not flat and not more_false
        L.append(f"| {a} | {tot(a, 'found_v2')} | {tot(a, 'right_place')} | {tot(a, 'false_boxes')}{' (more)' if more_false else ''} | {len(lower_f)} | {len(lower_p)} | "
                 f"{len(flat)} | {'pass' if ok else '**FAILS**'} |")
        for name, lst, field in (("found lower", lower_f, "found_v2"), ("right place lower", lower_p, "right_place")):
            for k in lst:
                detail.append(f"- `{a}`, {name}: {k[0]} at {int(round(100 * k[1]))} %: {val('base', k, field)} → {val(a, k, field)} of {val('base', k, 'n')}")
        for k in flat:
            detail.append(f"- `{a}`, target not higher: {k[0]} at {int(round(100 * k[1]))} %: {val('base', k, 'found_v2')} → {val(a, k, 'found_v2')}")
        for k in keys:
            if val(a, k, "false_boxes") != val("base", k, "false_boxes"):
                detail.append(f"- `{a}`, boxes where no barrel is: {k[0]} at {int(round(100 * k[1]))} %: {val('base', k, 'false_boxes')} → {val(a, k, 'false_boxes')}")
    L += [""] + detail + ["", "## The seven rows: found (v2) of n, at 25 / 50 / 75 % hidden", "",
                          "| what hides the barrel | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|" + "---|" * len(arms)]
    for row in common.TARGET_ROWS:
        ks = [k for k in keys if k[0] == row]
        L.append(f"| {ROW_NAMES[row]} (of {' / '.join(str(val('base', k, 'n')) for k in ks)}) | " +
                 " | ".join(" / ".join(str(val(a, k, "found_v2")) for k in ks) for a in arms) + " |")
    (folder / "scorecard_check.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
