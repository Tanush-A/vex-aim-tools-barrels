"""The best candidate of the self-calibration experiment as ONE function with fixed numbers, for another script or
agent to import or to hand to the judge.

    from best import detect_frame          # detect_frame(stem, frame) -> list[barrels.detect_types.Barrel]
    python barrels/tools/judge.py --cand-callable barrels/experiments/2026-11-26_selfcal/best.py:detect_frame

It is the family ``AB`` (all seeds, local paint and frame ranges; ``src/barrels/selfcal.py``) with the setting that 9
of the 10 leave-one-place-out folds picked: ``rel_margin`` 1.0, ``hue_move_max`` 6, ``flood_max`` 0.03 (the fold that
held out the ottoman picked ``flood_max`` 0.01). READ THIS BEFORE QUOTING A NUMBER FROM IT: with one fixed setting it
is no longer held out, so judging this function gives an in-sample number. The held-out verdict of the experiment is
``candidates.py:fit_AB`` (results/2026-11-26_selfcal/AB/judge.md): PASS, 133.8 -> 147.6 of 172 placements.

``run(frame)`` returns the whole ``selfcal.Result`` (both masks, the seeds with the guard that refused each, the
ranges the frame got). Per frame: nothing is kept between calls. Pixels are never changed.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import selfcal as sc  # noqa: E402

CONFIG = sc.SelfCalConfig(rel_margin=1.0, hue_move_max=6.0, flood_max=0.03)
_CAL = sc.SelfCal(hl.adopted_model(), CONFIG, geo.AIM_4A8B6118_BOXFIT)


def run(frame) -> sc.Result:
    return _CAL.run(frame)


def detect_frame(stem: str, frame) -> list:
    return _CAL.run(frame).boxes


detect_frame.describe = "selfcal AB, fixed numbers (rel_margin 1.0, hue_move_max 6, flood_max 0.03): in-sample when judged"
