#!/usr/bin/env python3
"""The occlusion scorecard of ``experiments/2026-11-19_det_occl`` (its ``run.py`` is loaded by path; nothing is copied),
run with this experiment's arms (``pin_arms.py``) and results folder. Same 3888 scenes, same counts.

Train frames only; a test frame is never opened (asserted in the loaded script).

    python barrels/experiments/2026-11-20_occl_pin/run.py                         # every arm of pin_arms.py
    python barrels/experiments/2026-11-20_occl_pin/run.py --arms base --out step1_baseline

Outputs: results/2026-11-20_occl_pin/[<out>/] scorecard.md, summary.md, cells.csv, scenes.csv, real.md, real.csv,
config.json (committed); sheets/ (ignored).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OCCL = HERE.parent / "2026-11-19_det_occl"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(OCCL))
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location("det_occl_run", OCCL / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
import pin_arms  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

if __name__ == "__main__":
    R.occl_arms, R.OUT = pin_arms, PKG_ROOT / "results" / "2026-11-20_occl_pin"      # this experiment's arms and folder
    R.AFTER_TEXT = ("`pin` = a partly seen stripe that no side reason places is placed by the barrel's outline, when the outline knows where the "
                    "barrel is (`pin_outline`). `pin+thin` = also: a thin piece of stripe is a barrel when it is a full slice and the outline places it "
                    "(`pin_thin`).")
    raise SystemExit(R.main())
