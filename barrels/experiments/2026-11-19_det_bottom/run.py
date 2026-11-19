#!/usr/bin/env python3
"""TODO A5 (2026-11-19): hidden bottoms that come from the top row. The test of ``experiments/2026-11-19_det_side``
(which itself loads the harness of ``2026-11-18_det_given_seg``), loaded by path and run with this experiment's
arms (``bottom_arms.py``) and output folder; nothing is copied. Levels 1 to 3, then the eval table of each arm
against ``base`` and the never-regress check.

Train frames only; a test frame is never opened (asserted in the loaded scripts and refused by ``report``).

    python barrels/experiments/2026-11-19_det_bottom/run.py                       # every arm of bottom_arms.py
    python barrels/experiments/2026-11-19_det_bottom/run.py --arms base --out step1_baseline

Outputs: results/2026-11-19_det_bottom/[<out>/] summary.md, scenarios.csv, per_barrel.csv, config.json,
never_regress.md, report_<arm>/ (committed); sheets/ (ignored).
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
import bottom_arms  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

if __name__ == "__main__":
    S.side_arms, S.OUT = bottom_arms, PKG_ROOT / "results" / "2026-11-19_det_bottom"     # this experiment's arms and folder
    raise SystemExit(S.main())
