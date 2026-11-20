#!/usr/bin/env python3
"""On the unlabeled recordings, which boxes each arm draws that ``rules`` does not, and the reverse. The script of
``2026-11-19_det_side`` (which loads the one of ``2026-11-18_det_given_seg``) is loaded by path and run with this
experiment's arms and folder. The recordings are read, never written.

    python barrels/experiments/2026-11-20_stencil/run_recordings.py --rec <path to data/recordings> [--arms stencil,union]
Outputs: results/2026-11-20_stencil/recordings.csv, recordings.md, recordings_by_clip.md; sheets/rec_<arm>/ (ignored).
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIDE = HERE.parent / "2026-11-19_det_side"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(SIDE))
sys.path.insert(0, str(HERE))
import stencil_arms as A  # noqa: E402

if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("det_side_recordings", SIDE / "recordings.py")
    T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
    T.side_arms = types.SimpleNamespace(ARMS={"base": A.ARMS["rules"], **{m: A.ARMS[m] for m in A.METHODS if m != "rules"}})
    T.OUT = A.OUT
    A.install()
    raise SystemExit(T.main())
