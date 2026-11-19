#!/usr/bin/env python3
"""The arms side by side, from the files the other scripts wrote; computes nothing new.

  eval table   results/2026-11-20_stencil/report_<arm>/report.csv   (run_levels.py; candidate = the arm, baseline = rules)
  levels       results/2026-11-20_stencil/levels/scenarios.csv       (run_levels.py)

    python barrels/experiments/2026-11-20_stencil/tables.py [stencil union veto veto+union]
Output: results/2026-11-20_stencil/tables.md (and the same as text).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_stencil"
FULL = ("HOME", "CAMPUS")            # sets listed scenario by scenario; the others by their total


def num(x: str, fmt: str) -> str:
    return "-" if x in ("", None) else f"{float(x):{fmt}}"


def main(argv=None) -> int:
    want = list(sys.argv[1:] if argv is None else argv) or ["stencil", "union", "veto", "veto+union"]
    reports = {}
    for a in want:
        f = OUT / f"report_{a}" / "report.csv"
        if f.exists():
            reports[a] = list(csv.DictReader(f.open()))
    arms = list(reports)
    L = ["# The arms side by side", "", "## Eval table (v2 rule; train frames; HOME leave one scene out; adopted color model)", "",
         "Each cell: found / missed / false, then median box width / true width, then median bottom-edge error in px (over the found barrels). "
         "`neg` = boxes on negative frames. HOME and CAMPUS scenario by scenario; the other sets (report only) by their total; `*` = indicative.", "",
         "| set | scenario | barrels | `rules` | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|---|---|---|" + "---|" * len(arms)]
    if arms:
        first = reports[arms[0]]
        for i, r in enumerate(first):
            if r["kind"] == "total" or (r["kind"] == "scene" and r["label"].rstrip("*") not in FULL):
                continue

            def cell(row, p):
                t = f"{row[p + '_found']} / {row[p + '_missed']} / {row[p + '_false']}; {num(row[p + '_width'], '.2f')}; {num(row[p + '_bottom'], '.1f')}"
                if row["kind"] == "subtotal":
                    t += f"; neg {row[p + '_neg_false']}"
                return t
            cells = [cell(reports[a][i], "cand") for a in arms]
            name = "**all**" if r["kind"] == "subtotal" else r["scene"]
            L.append(f"| {r['label']} | {name} | {r['barrels']} | {cell(r, 'base')} | " + " | ".join(cells) + " |")
    f = OUT / "levels" / "scenarios.csv"
    if f.exists():
        rows = list(csv.DictReader(f.open()))
        larms = list(dict.fromkeys(r["arm"] for r in rows))
        keys = list(dict.fromkeys((r["level"], r["scenario"], r["in_rule"]) for r in rows))
        by = {(r["arm"], r["level"], r["scenario"]): r for r in rows}
        L += ["", "## The levels: good segmentation in, and the same with damage (found / barrels (false boxes); level 2 = 5 seeds x the 16 HOME hand masks)", "",
              "| level | scenario | " + " | ".join(f"`{a}`" for a in larms) + " |", "|---|---|" + "---|" * len(larms)]
        for lv, sc, _ in keys:
            L.append(f"| {lv} | {sc} | " + " | ".join(f"{by[(a, lv, sc)]['found']} / {by[(a, lv, sc)]['barrels']} ({by[(a, lv, sc)]['false']})" for a in larms) + " |")
    (OUT / "tables.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
