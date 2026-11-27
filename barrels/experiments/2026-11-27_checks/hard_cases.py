#!/usr/bin/env python3
"""The hard cases of question 3 (plan: PREREG.md), from harness_removed.csv: every box an arm removes in the proof
harness, by what it was before (on its barrel: found / box off; or not), split by the rule that drew it, the scene
kind and hidden share (simulated scenes), the expected width of a barrel at the box's row (far: under 25 px), and the
place of the train frame it was made from (glass, lamp-lit). Writes hard_cases.md.

    cd barrels && env PYTHONPATH=src python experiments/2026-11-27_checks/hard_cases.py"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(HERE))
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
import arms as am  # noqa: E402

OUT = BARRELS / "results" / "2026-11-27_checks"
CAM = geo.AIM_4A8B6118_BOXFIT
ON = ("found", "off")


def width_at(bbox: str) -> float:
    x0, y0, x1, y1 = map(int, bbox.split())
    at = det.BarrelAt.from_top_row(CAM, y0)
    return at.W if at is not None else float("nan")


rows = list(csv.DictReader(open(OUT / "harness_removed.csv")))
L = ["# The hard cases: what the checks remove, by kind (question 3)", "",
     "From `harness_removed.csv` (every box removed in the proof harness). 'on a barrel' = found or box off before; "
     "'not' = wrong color, second box, on nothing; 'unscored' = no truth for that mask. Expected width W from the box's top row.", ""]
for a in am.ARMS:
    mine = [r for r in rows if r["arm"] == a]
    L += [f"## {a}: {am.DESCRIBE[a]} — {len(mine)} boxes removed", ""]

    def table(title, key):
        c = defaultdict(Counter)
        for r in mine:
            c[key(r)]["on" if r["before"] in ON else ("unscored" if r["before"] == "unscored" else "not")] += 1
        L.append(f"| {title} | on a barrel | not on a barrel | unscored |")
        L.append("|---|---|---|---|")
        for k in sorted(c, key=str):
            L.append(f"| {k} | {c[k]['on']} | {c[k]['not']} | {c[k]['unscored']} |")
        L.append("")
    table("group", lambda r: r["group"])
    table("reason", lambda r: r["why"])
    table("rule that drew it", lambda r: r["rule"])
    table("scene kind (amount hidden)", lambda r: f"{r['kind']} {r['amount']}" if r["kind"] else "(not a scene)")
    table("expected width", lambda r: "far, W < 25 px" if width_at(r["bbox"]) < 25 else ("close, W >= 60 px" if width_at(r["bbox"]) >= 60 else "25-60 px"))

    def place(r):
        if r["group"] == "scene":
            return "(scene)"
        stem = r["key"].rsplit("/", 1)[1]
        try:
            return ct.place_of(stem)
        except Exception:
            return "(no place)"
    table("place of the frame", place)
(OUT / "hard_cases.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
