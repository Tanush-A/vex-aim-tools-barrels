#!/usr/bin/env python3
"""A census after round 1 and before round 2 (no acceptance number comes from here): can ONE END of the seen part be
recognised as the barrel's own side, whatever the other end looks like?

If the left end of what is seen is the barrel's own side, the barrel's centre is W / 2 to the right of it: there is
nothing to slide. So ask each end by itself: put the predicted outline with its side on that end, and look only at
the columns near that end (``WINDOW`` x W, or all that is seen if less). The end's cost = the LARGEST of the three
lines' mean distances in rows (seen against predicted, each line's own up-down offset taken out): the top corner, the
stripe and the bottom corner must all follow the outline. A straight cut has square corners (both lines off), a
slanted cut imitates one corner and never both.

For the scorecard's own scenes (unhidden; a straight edge; a slanted edge; both sides), per kind of end: the cost in
barrel heights. Then the rule "exactly one end costs at most the limit: that end is the barrel's own side, the centre
is W / 2 in from it": how often it speaks, and how wrong the centre is.

    python barrels/experiments/2026-11-20_occl_pin/end_census.py
Output: results/2026-11-20_occl_pin/end_census.md, end_census.csv.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
spec = importlib.util.spec_from_file_location("shape_census", HERE / "shape_census.py")
C = importlib.util.module_from_spec(spec); sys.modules["shape_census"] = C; spec.loader.exec_module(C)
from barrels import occlude as oc  # noqa: E402

R, OUT = C.R, C.OUT
WINDOWS = (0.25, 0.35, 0.5)
LIMITS = (0.02, 0.03, 0.04, 0.05)


def end_cost(m, side: str, window: float) -> float:
    """The cost (in barrel heights) of "this end of the seen part is the barrel's own side"."""
    W, ol, xs = m["W"], m["ol"], m["xs"]
    cx = m["sx0"] + W / 2 if side == "L" else m["sx1"] - W / 2
    near = (xs + 0.5 - m["sx0"] <= window * W) if side == "L" else (m["sx1"] - (xs + 0.5) <= window * W)
    u = (xs[near] + 0.5 - cx) / W
    worst = 0.0
    for seen, line in ((m["top"], ol.top), (m["st"], ol.stripe), (m["bot"], ol.bottom)):
        ok = ~np.isnan(seen[near])
        if ok.sum() < 2:
            continue
        r = seen[near][ok] - line(u[ok])
        worst = max(worst, float(np.mean(np.abs(r - np.median(r)))))
    return worst / m["H"]


def main() -> int:
    pools, _ = R.build_sources(R.segmentations(R.train_stems()))
    ends, scenes = [], []
    for pool in R.POOLS:
        group = "hand masks" if pool == "HOME hand masks" else "color model"
        for src in pools[pool]:
            cx_true = (src.bbox[0] + src.bbox[2]) / 2
            variants = [("unhidden", "edge", 0.0, "L", 1)]
            variants += [("a straight edge", "edge", a, s, 1) for a in oc.AMOUNTS for s in ("L", "R")]
            variants += [("a slanted edge", "slant", a, s, ln) for a in oc.AMOUNTS for s in ("L", "R") for ln in (1, -1)]
            variants += [("both sides (equal)", "both", a, "L", 1) for a in oc.AMOUNTS]
            for name, kind, amount, side, lean in variants:
                sc = oc.make_scene(src, kind, amount, side, lean=lean)
                m = C.measure(sc.mask, src.color)
                row = {"group": group, "stem": src.stem, "kind": name, "hidden": amount, "side": side, "lean": lean, "W_true": src.width, "piece": int(m is not None)}
                if m is not None:
                    row["seen"] = round((m["sx1"] - m["sx0"]) / m["W"], 3)
                    for sd in ("L", "R"):
                        what = "own" if name == "unhidden" or (kind != "both" and sd != side) else ("cut straight" if kind in ("edge", "both") else "cut slanted")
                        for w in WINDOWS:
                            c = end_cost(m, sd, w)
                            row[f"cost_{sd}_{w}"] = round(c, 4)
                            ends.append({"group": group, "what": what, "window": w, "cost": c, "hidden": amount})
                        row[f"centre_if_{sd}"] = round((((m["sx0"] + m["W"] / 2) if sd == "L" else (m["sx1"] - m["W"] / 2)) - cx_true) / src.width, 4)
                scenes.append(row)
    keys = list(dict.fromkeys(k for r in scenes for k in r))
    with (OUT / "end_census.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, restval=""); w.writeheader(); w.writerows(scenes)

    L = ["# Can one end of the seen part be recognised as the barrel's own side? (a census after round 1; no acceptance number)", "",
         "The scorecard's own scenes (50 source barrels). An end's cost = the largest of the three lines' mean distances in rows between seen and "
         "predicted, with the outline's side put on that end, over the columns within `window` x W of the end; in barrel heights H.", "",
         "## The cost, per kind of end", "", "Median (10th to 90th percentile; n), and how many ends cost at most each limit.", "",
         "| window | group | end | cost | " + " | ".join(f"at most {x} H" for x in LIMITS) + " |", "|---|---|---|---|" + "---|" * len(LIMITS)]
    for w in WINDOWS:
        for group in ("hand masks", "color model"):
            for what in ("own", "cut straight", "cut slanted"):
                v = np.array([e["cost"] for e in ends if e["window"] == w and e["group"] == group and e["what"] == what])
                L.append(f"| {w} W | {group} | {what} | {np.median(v):.3f} ({np.percentile(v, 10):.3f} to {np.percentile(v, 90):.3f}; n {len(v)}) | "
                         + " | ".join(str(int((v <= x).sum())) for x in LIMITS) + " |")
    L += ["", "## The rule: exactly one end costs at most the limit", "",
          "Then that end is the barrel's own side and the centre is W / 2 in from it. Each cell: **scenes where the rule speaks / of those, the centre "
          "wrong by more than 0.15 W / the largest error**. Seen parts 0.8 W wide or wider are left out (the detector takes the seen width as the box "
          "there), so `n` is the number of scenes with less than 0.8 W seen.", ""]
    for w in WINDOWS:
        L += [f"### window {w} W", "", "| what hides the barrel | hidden | n | " + " | ".join(f"limit {x} H" for x in LIMITS) + " |", "|---|---|---|" + "---|" * len(LIMITS)]
        for name in ("a straight edge", "a slanted edge", "both sides (equal)"):
            for amount in oc.AMOUNTS:
                rs = [r for r in scenes if r["kind"] == name and r["hidden"] == amount and r["piece"] and r["seen"] < 0.8]
                cells = []
                for x in LIMITS:
                    errs = []
                    for r in rs:
                        own = [sd for sd in ("L", "R") if r[f"cost_{sd}_{w}"] <= x]
                        if len(own) == 1:
                            errs.append(abs(r[f"centre_if_{own[0]}"]))
                    cells.append(f"{len(errs)} / {sum(e > 0.15 for e in errs)} / {max(errs) if errs else 0:.2f}")
                L.append(f"| {name} | {int(amount * 100)} % | {len(rs)} | " + " | ".join(cells) + " |")
        L.append("")
    (OUT / "end_census.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
