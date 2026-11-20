"""Shared by the scripts of this experiment: the occlusion scorecard's harness (``experiments/2026-11-19_det_occl/run.py``)
loaded by path, with this experiment's arms and results folder. Nothing is copied."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OCCL = HERE.parent / "2026-11-19_det_occl"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(OCCL))
sys.path.insert(0, str(HERE))

from barrels.io import PKG_ROOT  # noqa: E402
import vert_arms  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_occl_vertical"

# the seven rows this experiment is about (keys of the scorecard's ROWS)
TARGET_ROWS = ("top", "bottom", "post", "barrel_front/other", "barrel_front/same", "barrel_side/same", "barrel_low/same")


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


def scorecard():
    """The scorecard module of 2026-11-19 with this experiment's arms and folder."""
    occ = load("det_occl_run", OCCL / "run.py")
    occ.occl_arms, occ.OUT = vert_arms, OUT
    return occ


def pools_and_segs(occ):
    stems = occ.train_stems()
    segs = occ.segmentations(stems, with_extreme=False)
    pools, dropped = occ.build_sources(segs)
    return stems, segs, pools, dropped
