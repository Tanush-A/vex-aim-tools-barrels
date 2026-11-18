#!/usr/bin/env python3
"""A close look at one frame of the test (a viewing aid; no number comes from here): the 2026-11-18 ``look.py``
loaded by path, with this experiment's arms and output folder.

    python barrels/experiments/2026-11-19_det_side/look.py "3a" occl_02 --arm side
writes results/2026-11-19_det_side/zoom/<arm>_<level>_<stem>.png and prints the reason log around the truth boxes.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE.parent / "2026-11-18_det_given_seg"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location("det_given_seg_look", PREV / "look.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
import side_arms  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

if __name__ == "__main__":
    L.R.ARMS, L.R.OUT = side_arms.ARMS, PKG_ROOT / "results" / "2026-11-19_det_side"
    raise SystemExit(L.main())
