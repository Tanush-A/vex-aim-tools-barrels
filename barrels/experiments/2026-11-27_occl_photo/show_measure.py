#!/usr/bin/env python3
"""Print measure.csv grouped by the truth of the side, with the cut-line decision (analysis).

    python show_measure.py [all|cut|open] [name filter]
      all  = every side; cut = the sides the cut line calls cut; open = the sides of stripes today has no reason for
"""
import csv
import sys

import lib

rows = list(csv.DictReader(open(lib.OUT / "measure.csv")))
what = sys.argv[1] if len(sys.argv) > 1 else "all"
only = sys.argv[2] if len(sys.argv) > 2 else ""
FRAC, LEAN, CROSS, TOUCH_W, TOUCH_PX = 0.6, 0.5, 0.1, 0.15, 3.0


def f(v, n=5):
    return (v or "")[:n]


def band_ok(r, k):
    if float(r[f"{k}_frac"]) < FRAC or not r[f"{k}_lean"] or abs(float(r[f"{k}_lean"])) > LEAN:
        return False
    if float(r[f"{k}_cross"]) > CROSS or not r[f"{k}_touch"]:
        return False
    return abs(float(r[f"{k}_touch"])) <= max(TOUCH_PX, TOUCH_W * float(r["W"]))


def cut(r):
    return band_ok(r, "up") or band_ok(r, "dn")


tally = {}
for t in ("hidden", "free", "unclear", "none"):
    print(f"== {t}")
    for r in rows:
        if r["truth"] != t or only not in r["stem"]:
            continue
        c = cut(r)
        tally.setdefault((t, r["today"] in ("", "centred", "outline")), [0, 0])[c] += 1
        if (what == "cut" and not c) or (what == "open" and r["today"] not in ("", "centred", "outline")):
            continue
        band = "  ".join(f"{k}{'*' if band_ok(r, k) else ' '}{float(r[k + '_frac']):4.2f} ln={f(r[k + '_lean'], 5):>5} x={f(r[k + '_cross'], 4):>4} "
                         f"t={f(r[k + '_touch'], 4):>4} s={f(r[k + '_s'], 4):>4}" for k in ("up", "dn"))
        print(f"  {'CUT' if c else '   '} {r['stem'][5:]:36s} {r['side']} {r['today'][:11]:11s} th={r['thin']} W={r['W']:>5} {band} | bes={r['beside_diff']}")
print("\n(truth, today has no reason) : [not cut, cut]")
for k, v in sorted(tally.items()):
    print(" ", k, v)
