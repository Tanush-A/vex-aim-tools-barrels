#!/usr/bin/env python3
"""Scene by scene, an arm against `start` on the scorecard (from the battery's ``scenes.csv``): every scene whose result
changes (found, right place, size, boxes where no barrel is). Used to attribute a round's failures (PREREG: "attributed with
the reason log"; the scenes it lists are re-run with the log by ``diag_cells.py``).

    python barrels/experiments/2026-11-20_occl_sliver/compare_scenes.py round1 bridge [--what false|big|lost|all]
"""
from __future__ import annotations

import argparse
import csv
import sys

import sliver as S


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("round")
    ap.add_argument("arm")
    ap.add_argument("--base", default="start")
    ap.add_argument("--what", default="all")
    a = ap.parse_args(argv)
    rows = list(csv.DictReader((S.OUT / a.round / "scenes.csv").open()))
    key = lambda r: (r["pool"], r["row"], r["amount"], r["variant"], r["stem"], r["color"], r["truth"])  # noqa: E731
    base = {key(r): r for r in rows if r["arm"] == a.base}
    n = 0
    for r in rows:
        if r["arm"] != a.arm:
            continue
        b = base[key(r)]
        ch = {"false": int(r["false"]) > int(b["false"]), "big": r["size"] == "big" and b["size"] != "big",
              "lost": (int(r["found"]) < int(b["found"])) or (int(r["place"]) < int(b["place"]))}
        if a.what == "all":
            hit = any(r[k] != b[k] for k in ("found", "place", "size", "false"))
        else:
            hit = ch[a.what]
        if hit:
            n += 1
            print(f"{r['pool']} | {r['row']} {r['amount']} {r['variant']} | {r['stem']} {r['color']} truth {r['truth']} | "
                  f"{a.base}: found {b['found']} place {b['place']} {b['size']} false {b['false']} box {b['box']} | "
                  f"{a.arm}: found {r['found']} place {r['place']} {r['size']} false {r['false']} box {r['box']}")
    print(n, "scenes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
