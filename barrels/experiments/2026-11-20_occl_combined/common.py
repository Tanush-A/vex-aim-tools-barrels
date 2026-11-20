"""Shared by the scripts of this experiment: paths, the arms (``comb_arms.py``), a loader for the earlier harnesses
(loaded by path and run unchanged; nothing is copied), and which rule drew a box."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
OCCL = EXP / "2026-11-19_det_occl"            # the occlusion scorecard
SIDE = EXP / "2026-11-19_det_side"
SEG = EXP / "2026-11-18_det_given_seg"        # the levels harness, the recordings script
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))

import comb_arms as A  # noqa: E402

OUT = A.OUT
RULE_ARMS = ("before", "stack", "combined", "combined+thin", "combined+cover")
VERIFY_ARMS = ("combined+verify", "combined+verify2")
STAGE_NAME = {"barrel": "stripe step", "cap": "caps_behind", "pair": "post_pairs", "slice": "slices_behind", "half": "half_stripes",
              "piece": "stripeless piece"}


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


def drawn_by(log: list, bbox) -> str:
    """Which part of the detector drew the box ``bbox``, read from the reason log (the last "kept" note carrying this box)."""
    for e in reversed(log):
        if e.get("why") == "kept" and e.get("box") is not None and tuple(e["box"]) == tuple(bbox):
            return STAGE_NAME.get(e.get("stage"), str(e.get("stage")))
    return "stripeless piece"


def arm_list(text: str, default) -> list[str]:
    arms = [a for a in (text.split(",") if text else default) if a]
    missing = [a for a in arms if a not in A.ARMS]
    if missing:
        raise SystemExit(f"no such arm: {missing} (the verify arms exist once verify_calibrate.py has run)")
    return arms
