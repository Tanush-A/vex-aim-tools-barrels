#!/usr/bin/env python3
"""Which boxes an arm removes (or adds) against ``start``, per test bed, from two census folders (census_facts.py output).

    python barrels/experiments/2026-11-24_occl_strict/diff.py --base census --arm arm_front [--beds real,card,levels] [--out diff_front.md]
A removed box is counted by what it was (strict.judge on real and levels; right place / false on the scorecard).
"""
from __future__ import annotations

import argparse
import collections
import csv

import strict as S


def load(folder, bed):
    p = S.OUT / folder / f"census_{bed}.csv"
    return {(r["set"], r["scene"], r["color"], r["box"]): r for r in csv.DictReader(p.open())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="census")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--beds", default="real,card,levels")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    L = [f"# `{a.arm}` against `{a.base}`: boxes removed and added", ""]
    for bed in a.beds.split(","):
        base, arm = load(a.base, bed), load(a.arm, bed)
        rem = [base[k] for k in base if k not in arm]
        add = [arm[k] for k in arm if k not in base]
        tb = collections.Counter(r["kind"] for r in base.values())
        L += [f"## {bed}", "", f"boxes {len(base)} -> {len(arm)}; by kind before: {dict(tb)}",
              f"removed: {dict(collections.Counter(r['kind'] for r in rem))}; added: {dict(collections.Counter(r['kind'] for r in add))}", "",
              "| what | set | scene | color | box | kind | stage | flags |", "|---|---|---|---|---|---|---|---|"]
        for what, rs in (("removed", rem), ("added", add)):
            for r in rs:
                L.append(f"| {what} | {r['set']} | {r['scene']} | {r['color']} | {r['box']} | {r['kind']} | {r['stage']} | {r['flags']} |")
        L.append("")
    text = "\n".join(L) + "\n"
    if a.out:
        (S.OUT / a.out).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
