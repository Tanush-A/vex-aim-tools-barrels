#!/usr/bin/env python3
"""The arms' scorecards on one page. Reads ``card_<arm>/cells.csv`` written by ``run_scorecard.py`` (each holds
``rules`` and one arm on the same 3888 scenes); computes nothing new.

    python barrels/experiments/2026-11-20_stencil/scorecard.py [stencil union veto veto+union]
Output: results/2026-11-20_stencil/scorecard.md (and the same as text).
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_stencil"
FIELDS = ("n", "found_v2", "right_place", "too_small", "about_right", "too_big", "false_boxes", "fronts", "fronts_found")
POOLS = ("HOME hand masks", "HOME color model", "CAMPUS color model")


def main(argv=None) -> int:
    want = list(sys.argv[1:] if argv is None else argv) or ["stencil", "union", "veto", "veto+union", "union1"]
    spec = importlib.util.spec_from_file_location("det_occl_run", HERE.parent / "2026-11-19_det_occl" / "run.py")
    R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
    cells: dict[tuple, dict] = {}
    arms = ["rules"]
    for a in want:
        f = OUT / f"card_{a.replace('+', '_')}" / "cells.csv"
        if not f.exists():
            continue
        arms.append(a)
        for r in csv.DictReader(f.open()):
            key = (r["arm"], r["pool"], r["row"], float(r["amount"]))
            val = {k: int(r[k]) for k in FIELDS}
            assert cells.get(key, val) == val, f"`rules` differs between the cards at {key}"
            cells[key] = val
    keys = [(k, a) for k, _, _, _ in R.ROWS for a in (0.25, 0.5, 0.75)]

    def tot(arm, field, pool="ALL"):
        return sum(cells[(arm, pool, k, a)][field] for k, a in keys if (arm, pool, k, a) in cells)

    def chain(k, a, field):
        return " → ".join(str(cells[(arm, "ALL", k, a)][field]) for arm in arms) + f" of {cells[('rules', 'ALL', k, a)]['n']}"

    L = ["# Occlusion scorecard: the rule detector, the stencil, and the combinations", "",
         f"The scorecard of `experiments/2026-11-19_det_occl`, unchanged: {tot('rules', 'n')} scenes made from 50 unhidden barrels of the train frames "
         "(12 HOME hand masks, 12 HOME color model, 26 CAMPUS color model), each hidden 25 / 50 / 75 % by one thing. "
         f"Each cell: **{' → '.join(f'`{a}`' for a in arms)}, of n scenes**.", "",
         "## Found: right color, overlap with the barrel's FULL box of half or more, bottom edge right (the v2 rule)", "",
         "| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |", "|---|---|---|---|"]
    for k, name, _, _ in R.ROWS:
        L.append(f"| {name} | " + " | ".join(chain(k, a, "found_v2") for a in (0.25, 0.5, 0.75)) + " |")
    L += ["", "## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size", "",
          "| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |", "|---|---|---|---|"]
    for k, name, _, _ in R.ROWS:
        L.append(f"| {name} | " + " | ".join(chain(k, a, "right_place") for a in (0.25, 0.5, 0.75)) + " |")
    L += ["", "## All scenes together", "",
          "| | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|" + "---|" * len(arms)]
    for name, field in (("found (v2)", "found_v2"), ("box in the right place", "right_place"), ("boxes where no barrel is", "false_boxes"),
                        ("right-place boxes too small", "too_small"), ("... about right", "about_right"), ("... too big", "too_big"),
                        (f"the barrel pasted in front found, of {tot('rules', 'fronts')}", "fronts_found")):
        L.append(f"| {name} | " + " | ".join(str(tot(a, field)) for a in arms) + " |")
    for pool in POOLS:
        L.append(f"| found, {pool} (of {tot('rules', 'n', pool)}) | " + " | ".join(str(tot(a, "found_v2", pool)) for a in arms) + " |")
    for pool in POOLS:
        L.append(f"| boxes where no barrel is, {pool} | " + " | ".join(str(tot(a, "false_boxes", pool)) for a in arms) + " |")
    L += ["", "## Each arm against `rules`, cell by cell (kind x amount, the three pools together)", "",
          "| arm | cells with more found | cells with fewer found | cells with fewer right-place boxes | boxes where no barrel is |", "|---|---|---|---|---|"]
    detail = []
    for a in arms[1:]:
        up = [(k, m) for k, m in keys if cells[(a, "ALL", k, m)]["found_v2"] > cells[("rules", "ALL", k, m)]["found_v2"]]
        down = [(k, m) for k, m in keys if cells[(a, "ALL", k, m)]["found_v2"] < cells[("rules", "ALL", k, m)]["found_v2"]]
        place = [(k, m) for k, m in keys if cells[(a, "ALL", k, m)]["right_place"] < cells[("rules", "ALL", k, m)]["right_place"]]
        L.append(f"| `{a}` | {len(up)} | {len(down)} | {len(place)} | {tot('rules', 'false_boxes')} → {tot(a, 'false_boxes')} |")
        for k, m in down:
            detail.append(f"- `{a}`, fewer found: {R.ROW_NAME[k]} at {int(round(100 * m))} %: {cells[('rules', 'ALL', k, m)]['found_v2']} → {cells[(a, 'ALL', k, m)]['found_v2']} "
                          f"of {cells[('rules', 'ALL', k, m)]['n']}")
    L += [""] + detail + ["",
          "Limits, as on 2026-11-19: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front). A real "
          "occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers."]
    (OUT / "scorecard.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
