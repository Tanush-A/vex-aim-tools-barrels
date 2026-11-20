#!/usr/bin/env python3
"""The occlusion scorecard of ``2026-11-19_det_occl`` with this experiment's arms. Its ``run.py`` is loaded by path and
run unchanged: the same 50 source barrels (chosen by the same ``base`` settings as on 2026-11-19), the same 3888
scenes, the same scoring; and its part 2, the real occluded or cut barrels of the train frames, one by one.

    python barrels/experiments/2026-11-20_occl_combined/run_card.py                       # before, stack, combined, +thin, +cover
    python barrels/experiments/2026-11-20_occl_combined/run_card.py --arms combined,combined+verify,combined+verify2 --out verify
    python barrels/experiments/2026-11-20_occl_combined/run_card.py --sanity              # the merged code against the published totals

``--sanity``: `stack` and the arms `all` of ``2026-11-20_occl_vertical`` and `pin`, `pin+thin` of ``2026-11-20_occl_pin``,
each as its own experiment pins it (the other branch's switches off). They must give 2417 / 45, 2738 / 45, 2445 / 45,
2556 / 45 (found / boxes where no barrel is).

Train frames only (asserted in the loaded script).
Outputs: results/2026-11-20_occl_combined/[<out>/] scorecard.md, summary.md, cells.csv, scenes.csv, real.md, real.csv,
config.json (committed); sheets/ (ignored).
"""
from __future__ import annotations

import argparse
import sys
import types

import common as C

A = C.A


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--no-sheets", action="store_true")
    ap.add_argument("--sanity", action="store_true")
    args = ap.parse_args(argv)
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    if args.sanity:
        vert = C.load("vert_arms_2026_11_20", C.EXP / "2026-11-20_occl_vertical" / "vert_arms.py")
        pin = C.load("pin_arms_2026_11_20", C.EXP / "2026-11-20_occl_pin" / "pin_arms.py")
        arms = {"stack": A.ARMS["stack"], "vertical_all": vert.ARMS["all"], "pin": pin.ARMS["pin"], "pin+thin": pin.ARMS["pin+thin"]}
        names, out = list(arms), args.out or "sanity"
        R.AFTER_TEXT = "Sanity run: each arm as its own experiment pinned it, on the merged code."
    else:
        names = C.arm_list(args.arms, C.RULE_ARMS)
        arms, out = {a: A.ARMS[a] for a in names}, args.out
        R.AFTER_TEXT = ("`before` = the defaults of `origin/barrels` (none of the unmerged occlusion work); the arms after it are those of "
                        "`experiments/2026-11-20_occl_combined/comb_arms.py`; which of them is the default is in `verdict.md`.")
    R.occl_arms = types.SimpleNamespace(ARMS=arms, BASE=A.SOURCE_BASE)
    R.OUT = C.OUT
    A.install()
    return R.main(["--arms", ",".join(names), "--after", ",".join(names[1:])] + (["--out", out] if out else []) + (["--no-sheets"] if args.no_sheets else []))


if __name__ == "__main__":
    raise SystemExit(main())
