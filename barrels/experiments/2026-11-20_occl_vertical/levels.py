#!/usr/bin/env python3
"""The earlier tests with this experiment's arms: the test of ``experiments/2026-11-19_det_side`` (which loads the
harness of ``2026-11-18_det_given_seg``), loaded by path and run with ``vert_arms.py`` and this experiment's folder;
nothing is copied. Levels 1 to 3 (perfect HOME masks; light / medium / heavy damage; CAMPUS; BLACK with label
thresholds), then the eval table of each arm against ``base`` and the never-regress check.

Train frames only; a test frame is never opened (asserted in the loaded scripts and refused by ``report``).

    python barrels/experiments/2026-11-20_occl_vertical/levels.py [--arms base,all] [--out round1/levels]
Outputs: results/2026-11-20_occl_vertical/[<out>/] summary.md, scenarios.csv, per_barrel.csv, config.json,
never_regress.md, report_<arm>/ (committed); sheets/ (ignored). Without --out they go to the sub-folder ``levels``.
"""
from __future__ import annotations

import sys

import common

SIDE = common.HERE.parent / "2026-11-19_det_side"
sys.path.insert(0, str(SIDE))
S = common.load("det_side_run", SIDE / "run.py")

if __name__ == "__main__":
    S.side_arms, S.OUT = common.vert_arms, common.OUT            # this experiment's arms and folder
    argv = sys.argv[1:]
    if "--out" not in argv:
        argv += ["--out", "levels"]
    raise SystemExit(S.main(argv))
