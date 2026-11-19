#!/usr/bin/env python3
"""The earlier tests, with this experiment's arms: the test of ``experiments/2026-11-19_det_side`` (which loads the
harness of ``2026-11-18_det_given_seg``), loaded by path and run with ``occl_arms.py`` and this experiment's folder;
nothing is copied. Levels 1 to 3 (perfect HOME masks; light / medium / heavy damage; CAMPUS; BLACK with label
thresholds), then the eval table of each arm against ``base`` and the never-regress check.

Train frames only; a test frame is never opened (asserted in the loaded scripts and refused by ``report``).

    python barrels/experiments/2026-11-19_det_occl/levels.py                       # every arm of occl_arms.py
    python barrels/experiments/2026-11-19_det_occl/levels.py --arms base --out step1_baseline/levels

Outputs: results/2026-11-19_det_occl/[<out>/] summary.md, scenarios.csv, per_barrel.csv, config.json,
never_regress.md, report_<arm>/ (committed); sheets/ (ignored). Without --out they go to the sub-folder ``levels``.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIDE = HERE.parent / "2026-11-19_det_side"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(SIDE))
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location("det_side_run", SIDE / "run.py")
S = importlib.util.module_from_spec(spec); sys.modules["det_side_run"] = S; spec.loader.exec_module(S)
import occl_arms  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

if __name__ == "__main__":
    S.side_arms, S.OUT = occl_arms, PKG_ROOT / "results" / "2026-11-19_det_occl"     # this experiment's arms and folder
    argv = sys.argv[1:]
    if "--out" not in argv:
        argv += ["--out", "levels"]
    raise SystemExit(S.main(argv))
