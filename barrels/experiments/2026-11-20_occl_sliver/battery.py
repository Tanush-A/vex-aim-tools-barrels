#!/usr/bin/env python3
"""The battery of ``2026-11-20_occl_combined``, run unchanged with this experiment's arms and results folder. Its
scripts are loaded by path; only the arm table and the output folder are swapped (``sliver.register``).

    python barrels/experiments/2026-11-20_occl_sliver/battery.py card --arms start,sliver --out round1 [--no-sheets]
    python barrels/experiments/2026-11-20_occl_sliver/battery.py eval --arms start,sliver --against start --out round1
    python barrels/experiments/2026-11-20_occl_sliver/battery.py levels --arms start,sliver --out round1
    python barrels/experiments/2026-11-20_occl_sliver/battery.py recordings --rec <data/recordings> --arms sliver --against start --out round1

``card``: the occlusion scorecard (3888 scenes) and the real occluded barrels; ``eval``: the eval table (HOME leave one
scene out, CAMPUS; black, wood and Dave's report only); ``levels``: the damaged masks (perfect, typical, bad day, bad day
without the stripe patch, light, medium, heavy, worst seen; 5 and 20 seeds); ``recordings``: boxes appearing and
disappearing on the recorded frames. Train frames only (asserted in the loaded scripts).
Outputs: results/2026-11-20_occl_sliver/<out>/ (the files each script names).
"""
from __future__ import annotations

import sys

import sliver as S

C, A = S.C, S.A
PARTS = {"card": "run_card.py", "eval": "run_eval.py", "levels": "run_levels.py", "recordings": "run_recordings.py"}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in PARTS:
        print(__doc__)
        return 2
    S.register()
    C.OUT = A.OUT = S.OUT
    C.RULE_ARMS = tuple(S.ARMS)
    mod = C.load(f"comb_{argv[0]}", S.COMB / PARTS[argv[0]])
    return mod.main(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
