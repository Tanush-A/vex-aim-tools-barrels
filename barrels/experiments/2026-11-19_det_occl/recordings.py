#!/usr/bin/env python3
"""On the unlabeled recordings, which boxes appear or disappear against ``base`` for each arm. The script of
``experiments/2026-11-19_det_side`` is loaded by path and run with this experiment's arms and folder.

    python barrels/experiments/2026-11-19_det_occl/recordings.py --rec <path to data/recordings> [--arms all] [--out round1]
Outputs: results/2026-11-19_det_occl/[<out>/] recordings.csv, recordings.md, recordings_by_clip.md; sheets/rec_<arm>/ (ignored).
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

spec = importlib.util.spec_from_file_location("det_side_recordings", SIDE / "recordings.py")
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
import occl_arms  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

if __name__ == "__main__":
    T.side_arms, T.OUT = occl_arms, PKG_ROOT / "results" / "2026-11-19_det_occl"
    raise SystemExit(T.main())
