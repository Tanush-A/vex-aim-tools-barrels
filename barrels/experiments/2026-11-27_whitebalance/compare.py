#!/usr/bin/env python3
"""Part D: does correction gain barrels that the ideas which change no pixel do not? (white-balance experiment).

    python barrels/experiments/2026-11-27_whitebalance/compare.py

Reads the barrel-level changes (``changes.csv``, judged ordinary frames, counted per frame) of every candidate here
and of the other experiments' main candidates, from their branches with ``git show`` (stripe by contrast C1, near-miss
B_partner_fit, self-calibration AB, blue follows the light B1). For each candidate here: how many of its gained
barrels each of those also gains, how many none of them gains, and what it loses. Writes compare.md.
"""
from __future__ import annotations

import csv
import io as _io
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
OUT = BARRELS / "results" / "2026-11-27_whitebalance"
OTHERS = {
    "stripe by contrast (C1, +21.5)": ("wip/exp-contrast", "barrels/results/2026-11-26_contrast/judge_C1_add_guards/changes.csv"),
    "near-miss (B_partner_fit, +13.7)": ("wip/exp-nearmiss", "barrels/results/2026-11-26_nearmiss/B_partner_fit/changes.csv"),
    "self-calibration (AB, +13.8)": ("wip/exp-selfcal", "barrels/results/2026-11-26_selfcal/AB/changes.csv"),
    "blue follows the light (B1, +3.9)": ("wip/exp-light", "barrels/results/2026-11-26_light/judge_B1_ramp_without_loose/changes.csv"),
}


def read(text: str) -> dict[str, set]:
    g, l_ = set(), set()
    for r in csv.DictReader(_io.StringIO(text)):
        if r["judged"] != "1":
            continue
        k = (r["stem"], r["barrel"])
        if r["kind"] == "gained":
            g.add(k)
        elif r["kind"] == "lost":
            l_.add(k)
    return {"gained": g, "lost": l_}


def main() -> int:
    others = {n: read(subprocess.run(["git", "-C", str(BARRELS), "show", f"{b}:{p}"], check=True, capture_output=True, text=True).stdout) for n, (b, p) in OTHERS.items()}
    union = set().union(*(o["gained"] for n, o in others.items() if "light" not in n))
    mine = {d.name[len("judge_"):]: read((d / "changes.csv").read_text()) for d in sorted(OUT.glob("judge_*")) if (d / "changes.csv").exists()}
    L = ["# Part D: what correction gains that the ideas which change no pixel do not", "",
         "Barrels counted per frame, judged ordinary frames, from each candidate's `changes.csv` (the others read from their branches with `git show`). "
         "*None of the three* = not gained by contrast C1, near-miss or self-calibration AB.", "",
         "| candidate | gained | also by contrast C1 | also by near-miss | also by self-cal AB | also by blue-follows-light B1 | by none of the three | lost |", "|---|---|---|---|---|---|---|---|"]
    for n, m in mine.items():
        g = m["gained"]
        L.append(f"| {n} | {len(g)} | " + " | ".join(str(len(g & o["gained"])) for o in others.values()) + f" | {len(g - union)} | {len(m['lost'])} |")
    for n in ("P1_gray_world_partial", "F3_without_loose"):
        if n in mine:
            rest = sorted(mine[n]["gained"] - union)
            L += ["", f"## {n}: gained by none of the three ({len(rest)})", ""] + [f"- {s.replace('4A8B_', '')} barrel {b}" for s, b in rest]
    L += ["", "## The others, for scale", "", "| idea | gained | lost |", "|---|---|---|"] + [f"| {n} | {len(o['gained'])} | {len(o['lost'])} |" for n, o in others.items()]
    L += ["", f"Union of contrast C1, near-miss and self-calibration AB: {len(union)} barrels gained."]
    (OUT / "compare.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
