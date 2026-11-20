#!/usr/bin/env python3
"""Do the rules of the two branches get in each other's way? Read off two scorecard runs, scene by scene; computes
nothing new.

  the sanity run   (``run_card.py --sanity``): `stack`, `vertical_all` (occl-vertical's six alone), `pin`, `pin+thin`
  a combined run   (``run_card.py --out <folder>``): `combined`, `combined+thin`, ...

For the same 3888 scenes (same key: pool, row, amount, variant, frame, color, true box):

  lost     the hidden barrel is found by a branch alone and not by the combination;
  extra    the combination draws more boxes where no barrel is than either branch alone;
  gained   found by the combination and by neither branch alone (the rules helping each other).

`combined` is compared with `vertical_all` and `pin`; `combined+thin` with `vertical_all` and `pin+thin`.

    python barrels/experiments/2026-11-20_occl_combined/interactions.py [round1]
Output: results/2026-11-20_occl_combined/<folder>/interactions.md, and the same as text.
"""
from __future__ import annotations

import collections
import csv
import sys

import common as C

PAIRS = {"combined": ("vertical_all", "pin"), "combined+thin": ("vertical_all", "pin+thin")}


def read(path):
    out = {}
    for r in csv.DictReader(path.open()):
        out[(r["arm"], r["pool"], r["row"], r["amount"], r["variant"], r["stem"], r["color"], r["truth"])] = r
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    folder = C.OUT / (argv[0] if argv else "")
    alone, comb = read(C.OUT / "sanity" / "scenes.csv"), read(folder / "scenes.csv")
    scenes = sorted({k[1:] for k in comb})
    L = ["# Interactions: the combination against each branch alone, scene by scene", "",
         f"{len(scenes)} scenes. `vertical_all` = `stack` + the six switches of occl-vertical; `pin`, `pin+thin` = `stack` + those of occl-pin "
         "(`sanity/scenes.csv`). Found = the v2 rule against the full box; a box where no barrel is = a box in the right place of no true barrel.", ""]
    for arm, (va, pa) in PAIRS.items():
        if (arm, *scenes[0]) not in comb:
            continue
        lost, extra, gained = [], [], []
        tot = collections.Counter()
        for s in scenes:
            c, v, p = comb[(arm, *s)], alone[(va, *s)], alone[(pa, *s)]
            cf, vf, pf = int(c["found"]), int(v["found"]), int(p["found"])
            cx, vx, px = int(c["false"]), int(v["false"]), int(p["false"])
            tot["comb"] += cf; tot["v"] += vf; tot["p"] += pf; tot["either"] += max(vf, pf)
            tot["comb_false"] += cx; tot["v_false"] += vx; tot["p_false"] += px
            if cf < max(vf, pf):
                lost.append((s, c, "vertical" if vf else "", "pin" if pf else ""))
            if cx > max(vx, px):
                extra.append((s, c, vx, px))
            if cf > max(vf, pf):
                gained.append(s)
        L += [f"## `{arm}` against `{va}` and `{pa}`", "",
              f"Found: `{va}` {tot['v']}, `{pa}` {tot['p']}, by either alone {tot['either']}, `{arm}` {tot['comb']}. "
              f"Boxes where no barrel is: {tot['v_false']}, {tot['p_false']}, `{arm}` {tot['comb_false']}.", "",
              f"- **lost** (found by a branch alone, not by the combination): {len(lost)} scenes",
              f"- **extra** (more boxes where no barrel is than either alone): {len(extra)} scenes",
              f"- gained (found by the combination only): {len(gained)} scenes", ""]
        for name, items in (("lost", lost), ("extra", extra)):
            by = collections.Counter((s[1], s[2]) for s, *_ in items)
            if by:
                L += [f"`{name}`, by cell: " + "; ".join(f"{row} at {int(round(100 * float(a)))} %: {n}" for (row, a), n in sorted(by.items())), ""]
        if gained:
            by = collections.Counter((s[1], s[2]) for s in gained)
            L += ["`gained`, by cell: " + "; ".join(f"{row} at {int(round(100 * float(a)))} %: {n}" for (row, a), n in sorted(by.items())), ""]
        if lost:
            L += ["| lost: pool | row | hidden | variant | frame | color | true box | found alone by | the combination's box | why not found |", "|---|---|---|---|---|---|---|---|---|---|"]
            for s, c, v, p in lost[:60]:
                L.append(f"| {s[0]} | {s[1]} | {int(round(100 * float(s[2])))} % | {s[3]} | {s[4]} | {s[5]} | {s[6]} | {' '.join(x for x in (v, p) if x)} | {c['box'] or 'none'} | {c['cause']} |")
            L.append("")
        if extra:
            L += ["| extra: pool | row | hidden | variant | frame | color | true box | boxes where no barrel is: vertical / pin / combination |", "|---|---|---|---|---|---|---|---|"]
            for s, c, vx, px in extra[:60]:
                L.append(f"| {s[0]} | {s[1]} | {int(round(100 * float(s[2])))} % | {s[3]} | {s[4]} | {s[5]} | {s[6]} | {vx} / {px} / {c['false']} |")
            L.append("")
    (folder / "interactions.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
