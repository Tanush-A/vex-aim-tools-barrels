#!/usr/bin/env python3
"""Report only (PREREG, last paragraph): the scorecard's rows "from above", "from below" and "a post" at more amounts
than 25 / 50 / 75 %, because a rule that reads a partly seen stripe works in a window of amounts. Same 50 source
barrels as the scorecard, each hidden by 25 to 75 % in steps of 5; found under the v2 rule against the full box, and
the boxes that are in the right place of no barrel.

    python barrels/experiments/2026-11-20_occl_vertical/amounts.py [--arms base,all] [--out round1]
Output: results/2026-11-20_occl_vertical/[<out>/] amounts.md, amounts.csv.
"""
from __future__ import annotations

import argparse
import csv

import common
from barrels import detector as det, geometry as geo, occlude as oc

CAM = geo.AIM_4A8B6118_BOXFIT
AMOUNTS = tuple(round(0.25 + 0.05 * k, 2) for k in range(11))
KINDS = (("top", "hidden from above"), ("bottom", "hidden from below"), ("post", "a post across the middle"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="base,all")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    arms = [a for a in args.arms.split(",") if a]
    occ = common.scorecard()
    stems, segs, pools, dropped = common.pools_and_segs(occ)
    srcs = [s for p in occ.POOLS for s in pools[p]]
    rows = []
    for kind, name in KINDS:
        for amount in AMOUNTS:
            for a in arms:
                found = false = 0
                for src in srcs:
                    sc = oc.make_scene(src, kind, amount)
                    preds = det.detect(sc.mask, common.vert_arms.ARMS[a], CAM)
                    found += int(occ.found_v2(preds, src.color, src.bbox))
                    false += len(preds) - len(occ.right_place(preds, [sc.target]))
                rows.append({"kind": kind, "amount": amount, "arm": a, "n": len(srcs), "found_v2": found, "false_boxes": false})
    out = common.OUT / args.out if args.out else common.OUT
    out.mkdir(parents=True, exist_ok=True)
    with (out / "amounts.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    cell = {(r["kind"], r["amount"], r["arm"]): r for r in rows}
    L = ["# From above, from below, a post: every 5 % from 25 to 75 % hidden (report only)", "",
         f"{len(srcs)} free-standing barrels of the train frames, each hidden by the stated share of its height (from above, from below) or of its "
         "width (a post). Each cell: found under the v2 rule against the full box (boxes in the right place of no barrel), " +
         " → ".join(f"`{a}`" for a in arms) + ".", "",
         "| hidden | " + " | ".join(name for _, name in KINDS) + " |", "|---|" + "---|" * len(KINDS)]
    for amount in AMOUNTS:
        L.append(f"| {int(round(100 * amount))} % | " + " | ".join(
            " → ".join(f"{cell[(k, amount, a)]['found_v2']} ({cell[(k, amount, a)]['false_boxes']})" for a in arms) for k, _ in KINDS) + " |")
    (out / "amounts.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
