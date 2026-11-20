#!/usr/bin/env python3
"""On the unlabeled recordings, which boxes appear or disappear against ``base`` for each arm. The script of
``experiments/2026-11-19_det_side`` is loaded by path and run with this experiment's arms and folder.

    python barrels/experiments/2026-11-20_occl_vertical/recordings.py --rec <path to data/recordings> [--arms all] [--out round1]
Outputs: results/2026-11-20_occl_vertical/[<out>/] recordings.csv, recordings.md, recordings_by_clip.md; sheets/rec_<arm>/ (ignored).
"""
from __future__ import annotations

import sys

import common

SIDE = common.HERE.parent / "2026-11-19_det_side"
sys.path.insert(0, str(SIDE))
T = common.load("det_side_recordings", SIDE / "recordings.py")

if __name__ == "__main__":
    T.side_arms, T.OUT = common.vert_arms, common.OUT
    raise SystemExit(T.main())
