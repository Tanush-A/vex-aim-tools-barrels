#!/usr/bin/env python3
"""The census tables, from the two CSVs ``census_convex.py`` writes (no detection here).

    python barrels/experiments/2026-11-23_own_convex/census_summary.py
Output: results/2026-11-23_own_convex/census.md
"""
from __future__ import annotations

import collections
import csv

import numpy as np

import own_arms as O

ZONES = ("0.1", "0.15", "0.2")
MEASURES = ("chord", "chord_min", "chord_top", "chord_bot", "hull", "side")
THRESH = (-0.02, -0.01, -0.005, 0.0, 0.005, 0.01, 0.015, 0.02, 0.03)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def dist(v) -> str:
    v = np.array([x for x in v if x == x])
    if not len(v):
        return "-"
    return f"{np.median(v):+.3f} ({np.percentile(v, 5):+.3f} to {np.percentile(v, 95):+.3f}; {v.min():+.3f}; {v.max():+.3f})"


def share(v, pred) -> str:
    v = [x for x in v if x == x]
    return f"{sum(1 for x in v if pred(x))} / {len(v)}" if v else "-"


def main() -> int:
    ends = list(csv.DictReader((O.OUT / "census_ends.csv").open()))
    calls = list(csv.DictReader((O.OUT / "census_calls.csv").open()))
    L = ["# Does an own end bulge outward and a barrel-cut end inward? (a census, before any detector change; no acceptance number)", "",
         "Measures (`convex.py`), at one end of the seen part, over the zone x W columns nearest it, in barrel heights H, signed "
         "(+ = the boundary bulges OUTWARD, convex; - = INWARD, concave): `chord` = mean of (top: chord minus top row; bottom: bottom "
         "row minus chord), the chord running from the end column to the zone's inner column; `chord_min` = the smaller of the top's "
         "and the bottom's; `hull` = 1 - region area / convex-hull area (unsigned, 0 = convex); `side` = the end column per row against "
         "the chord from the top row to the bottom row (in W). Top and bottom read exactly as `own_close` reads them. "
         "`closed` = own_close's closure (0.05 W). Median (5th to 95th percentile; lowest; highest).", ""]

    # ---------------- Part A
    L += ["## Part A: every end of the target's piece in the scorecard scenes (seen < 0.8 W), by how the scene was made", ""]
    kinds = list(dict.fromkeys(r["kind"] for r in ends))
    kinds.sort(key=lambda k: (not k.startswith("own"), "barrel" in k, k))
    for subset, pred in (("all ends", lambda r: True),
                         ("ends own_close would call closed (closed >= 0.15), full slices", lambda r: num(r["closed"]) >= 0.15 and r["full_slice"] == "1"),
                         ("... and not against barrel color (own_close's round-2 test): the ends own_close can call own",
                          lambda r: num(r["closed"]) >= 0.15 and r["full_slice"] == "1" and r["seen_edge"] == "1")):
        for z in ZONES:
            L += [f"### {subset}; zone {z} W", "", "| end | masks | n | closed | chord | chord_min | hull | side | chord > 0 | chord_min > 0 |", "|---|---|---|---|---|---|---|---|---|---|"]
            for k in kinds:
                for grp, gp in (("hand", lambda r: "hand" in r["pool"]), ("color model", lambda r: "hand" not in r["pool"])):
                    rs = [r for r in ends if r["kind"] == k and gp(r) and pred(r)]
                    if not rs:
                        continue
                    g = lambda m: [num(r[f"{m}_{z}"]) for r in rs]
                    L.append(f"| {k} | {grp} | {len(rs)} | {dist([num(r['closed']) for r in rs])} | {dist(g('chord'))} | {dist(g('chord_min'))} | "
                             f"{dist(g('hull'))} | {dist(g('side'))} | {share(g('chord'), lambda x: x > 0)} | {share(g('chord_min'), lambda x: x > 0)} |")
            L.append("")

    # ---------------- Part B
    L += ["## Part B: every call own_close makes (arm `close`), and the end it calls own", "",
          "A call speaks when own_close returns a box. RIGHT = the end called own is `own` by the true boxes; WRONG otherwise "
          "(`cut by barrel` = another true barrel's box holds the column beyond the end).", "",
          "| where | calls | speaks | right | wrong | wrong: cut by barrel / cut / no barrel |", "|---|---|---|---|---|---|"]
    def pick_kind(r):
        return r[f"{r['pick']}_kind"] if r["pick"] else ""
    groups = list(dict.fromkeys((r["group"], r["level"] if r["group"] != "scorecard, HOME hand masks" else "") for r in calls))
    by = collections.defaultdict(list)
    for r in calls:
        g = r["group"] if r["group"].startswith("scorecard") else f"{r['group']}: {r['level']}"
        by[g].append(r)
    for g, rs in by.items():
        sp = [r for r in rs if r["pick"]]
        wr = [r for r in sp if pick_kind(r) != "own"]
        c = collections.Counter(pick_kind(r) for r in wr)
        L.append(f"| {g} | {len(rs)} | {len(sp)} | {len(sp) - len(wr)} | {len(wr)} | {c['cut by barrel']} / {c['cut']} / {c['no barrel']} |")
    sp = [r for r in calls if r["pick"]]
    right = [r for r in sp if pick_kind(r) == "own"]
    wrong = [r for r in sp if pick_kind(r) != "own"]
    L += ["", f"All: {len(calls)} calls, {len(sp)} speak, {len(right)} right, {len(wrong)} wrong.", ""]
    L += ["### The measure at the end called own: right calls against wrong ones", "", "| zone | measure | right | wrong |", "|---|---|---|---|"]
    for z in ZONES:
        for m in MEASURES:
            L.append(f"| {z} | {m} | {dist([num(r[f'{r['pick']}_{m}_{z}']) for r in right])} | {dist([num(r[f'{r['pick']}_{m}_{z}']) for r in wrong])} |")
    L += ["", "### Every wrong call", "", "| where | level | item | body | piece | seen | called own | kind | closed | " + " | ".join(f"chord {z}" for z in ZONES) + " | chord_min 0.15 | hull 0.15 |",
          "|---|---|---|---|---|---|---|---|---|" + "---|" * len(ZONES) + "---|---|"]
    for r in wrong:
        p = r["pick"]
        L.append(f"| {r['group']} | {r['level']} | {r['item']} | {r['body']} | {r['piece']} | {r['seen']} | {p} | {pick_kind(r)} | {r[f'{p}_closed']} | "
                 + " | ".join(r[f"{p}_chord_{z}"] for z in ZONES) + f" | {r[f'{p}_chord_min_0.15']} | {r[f'{p}_hull_0.15']} |")
    L += ["", "### The rule \"own only if also measure >= limit\": right calls kept / wrong calls removed (of "
          f"{len(right)} right, {len(wrong)} wrong)", "", "| zone | measure | " + " | ".join(f">= {t:+}" for t in THRESH) + " |", "|---|---|" + "---|" * len(THRESH)]
    for z in ZONES:
        for m in ("chord", "chord_min", "chord_top", "chord_bot", "side"):
            cells = []
            for t in THRESH:
                kr = sum(1 for r in right if num(r[f"{r['pick']}_{m}_{z}"]) >= t)
                rw = sum(1 for r in wrong if not num(r[f"{r['pick']}_{m}_{z}"]) >= t)
                cells.append(f"{kr} / {rw}")
            L.append(f"| {z} | {m} | " + " | ".join(cells) + " |")
    for z in ZONES:
        cells = []
        for t in (0.3, 0.2, 0.15, 0.1, 0.05, 0.03, 0.02):
            kr = sum(1 for r in right if num(r[f"{r['pick']}_hull_{z}"]) <= t)
            rw = sum(1 for r in wrong if not num(r[f"{r['pick']}_hull_{z}"]) <= t)
            cells.append(f"<= {t}: {kr} / {rw}")
        L.append(f"| {z} | hull | " + " | ".join(cells) + " |" + " |" * (len(THRESH) - 7))
    (O.OUT / "census.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
