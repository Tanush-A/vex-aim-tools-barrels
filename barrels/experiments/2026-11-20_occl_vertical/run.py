#!/usr/bin/env python3
"""The occlusion scorecard with this experiment's arms: ``experiments/2026-11-19_det_occl/run.py`` loaded by path
and run with ``vert_arms.py`` and this experiment's results folder; nothing is copied. Same 50 source barrels, same
3888 scenes, same seed.

    python barrels/experiments/2026-11-20_occl_vertical/run.py                               # every arm of vert_arms.py
    python barrels/experiments/2026-11-20_occl_vertical/run.py --arms base,all --after all [--out round1]
Outputs: results/2026-11-20_occl_vertical/[<out>/] scorecard.md, summary.md, cells.csv, scenes.csv, real.md, real.csv,
config.json (committed); sheets/ (ignored).
"""
import common

occ = common.scorecard()
occ.AFTER_TEXT = ("The arms after `base` are those of `experiments/2026-11-20_occl_vertical/vert_arms.py`; which of them is on by default is in `verdict.md`.")

if __name__ == "__main__":
    raise SystemExit(occ.main())
