#!/usr/bin/env python3
"""IN-SAMPLE views of the settings already run (from the table run.py cached; no new idea, no verdict). Written after
the judged run, to explain it: why a family that gains in-sample does not pass leave one place out.

    python barrels/experiments/2026-11-26_light/insample.py [--jobs 8]

1. Every setting a fold picked, and the setting the rule picks on all eight places, each scored on ALL ordinary frames
   and at the two warm places: what the bathroom gets from a setting picked without the bathroom.
2. "Bluer than the light": the margin delta swept at the ramp the all-places pick uses, the bathroom and all places.
3. The ramp's four numbers: how the gain over all places moves with each (the mean and the best over the other three).

Every number here is in-sample: the same frames chose and scored. Writes results/2026-11-26_light/insample.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as cd  # noqa: E402
import common as cm  # noqa: E402
import rules as ru  # noqa: E402
from sheets import setting_of  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402

WARM = ("home_bathtile", "home_ottoman")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    ordinary = cm.frames()[cnd.ORDINARY]
    truth = jg.load_truth(ordinary)
    margins = jg.load_margins()
    table = cd.build_table(ordinary, None, a.jobs, progress=False)          # read from the cache
    chosen = json.loads((cm.OUT / "chosen.json").read_text())
    base, base_p = cd.tallies(table, ru.FIXED.key, ordinary, truth.placements)

    def score(st: ru.Setting) -> dict:
        c, cp = cd.tallies(table, st.key, ordinary, truth.placements)
        v = jg.decide(base, c, {p: (base_p[p], cp[p]) for p in base_p}, margins)
        return {"found": c.found_w - base.found_w, "extra": c.extra_w - base.extra_w, "clean": c.clean_empty - base.clean_empty,
                "clutter": c.cluttered_empty_w - base.cluttered_empty_w, "verdict": v.result,
                **{p: cp[p].found_w - base_p[p].found_w for p in WARM}, **{p + "_extra": cp[p].extra_w - base_p[p].extra_w for p in WARM}}

    def line(label: str, st: ru.Setting) -> str:
        s = score(st)
        return (f"| {label} | {st.describe()} | {s['found']:+.2f} | {s['home_bathtile']:+.2f} | {s['home_ottoman']:+.2f} | {s['extra']:+.2f} "
                f"({s['home_bathtile_extra']:+.2f} / {s['home_ottoman_extra']:+.2f}) | {s['clean']:+d} / {s['clutter']:+.2f} | {s['verdict']} |")

    head = ["| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | "
            "boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |", "|---|---|---|---|---|---|---|---|"]
    L = ["# In-sample views of the judged settings (never a verdict)", "",
         "`python barrels/experiments/2026-11-26_light/insample.py`. Every number: the setting scored on all 154 ordinary train frames, against the fixed model; "
         f"found per placement (fixed: {base.found_w:.1f} of {base.placements}; bathroom {base_p['home_bathtile'].found_w:.1f}, ottoman {base_p['home_ottoman'].found_w:.1f} of 15), "
         "boxes per arrangement. The same frames chose and scored, so the last column is NOT a verdict.", "",
         "## 1. What a setting picked without a place does at that place", ""]
    for name in cd.FAMILIES:
        L += [f"### {cd.TITLES[name]}", ""] + head
        seen = {}
        for place, c in chosen["folds"][name].items():
            seen.setdefault(c["key"], []).append(place)
        for key, places in seen.items():
            L.append(line("the other places, held out: " + ", ".join(p.replace("home_", "") for p in places), setting_of(key)))
        L.append(line("all eight places", setting_of(chosen["in_sample_all_places"][name]["key"])))
        L.append("")
    pick = setting_of(chosen["in_sample_all_places"]["B4_ramp_rel_without_loose"]["key"])
    L += ["## 2. \"Bluer than the light\": the margin swept", "", f"The ramp of the all-places pick ({pick.w0:g} to {pick.w1:g}, S to {pick.s_warm:g}, hue low to {pick.h_warm:g}), "
          "reading `without_loose`.", ""] + head
    for d in (0.0,) + cd.DELTAS:
        L.append(line("no relative rule" if d == 0 else f"delta {d:.2f}", ru.Setting(pick.reading, pick.w0, pick.w1, pick.s_warm, pick.h_warm, d)))
    L += ["", "## 3. The ramp's numbers (family B1, reading `without_loose`, no relative rule)", "",
          "Gain = found minus boxes not on their barrel, all places. Per value of one number: the mean and the best over the other three.", "",
          "| number | value: mean gain / best gain |", "|---|---|"]
    fam = cd.FAMILIES["B1_ramp_without_loose"]
    gains = {st: (lambda s: s["found"] - s["extra"])(score(st)) for st in fam}
    for field, label in (("w0", "start of the ramp (warmth)"), ("w1", "end of the ramp (warmth)"), ("s_warm", "blue S floor at the end"), ("h_warm", "blue hue low end at the end")):
        vals = sorted({getattr(st, field) for st in fam})
        L.append(f"| {label} | " + "; ".join(f"{v:g}: {np.mean([g for st, g in gains.items() if getattr(st, field) == v]):+.2f} / "
                                              f"{max(g for st, g in gains.items() if getattr(st, field) == v):+.2f}" for v in vals) + " |")
    L += ["", f"Of the 54 settings, {sum(g > 0 for g in gains.values())} have a gain above zero in-sample; the largest is {max(gains.values()):+.2f}, the smallest {min(gains.values()):+.2f}."]
    text = "\n".join(L) + "\n"
    (cm.OUT / "insample.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
