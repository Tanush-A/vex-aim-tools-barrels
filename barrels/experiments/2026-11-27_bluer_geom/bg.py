"""Shared by the scripts of the 2026-11-27 "bluer than the light, false boxes by geometry" experiment.

It reuses the color steps of the 2026-11-26 light experiment (``experiments/2026-11-26_light``: ``rules.py``,
``candidates.py``) unchanged, and keeps its own cache under ``results/2026-11-27_bluer_geom/``. Train frames only:
every image is read with ``judge.load_frame``, which refuses anything else.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
LIGHT = BARRELS / "experiments" / "2026-11-26_light"
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(LIGHT))
sys.path.insert(0, str(HERE))

import candidates as cd  # noqa: E402  (the light experiment's families and its choose())
import common as lcm  # noqa: E402,F401
import rules as ru  # noqa: E402,F401

import barrels  # noqa: E402

OUT = BARRELS / "results" / "2026-11-27_bluer_geom"
assert str(Path(barrels.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {barrels.__file__}, not this checkout"
cd.CACHE = OUT / "cache_light"          # a fresh cache, made by this branch's detector
B4 = "B4_ramp_rel_without_loose"
