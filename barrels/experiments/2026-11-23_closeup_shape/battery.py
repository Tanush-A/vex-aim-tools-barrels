#!/usr/bin/env python3
"""The battery of ``2026-11-20_occl_combined``, run unchanged with this experiment's arms (``closeup.ARMS``) and results
folder. Its scripts are loaded by path; only the arm table and the output folder are swapped.

    python barrels/experiments/2026-11-23_closeup_shape/battery.py card --arms start,shape --out round1 --no-sheets
    python barrels/experiments/2026-11-23_closeup_shape/battery.py eval --arms start,shape --against start --out round1
    python barrels/experiments/2026-11-23_closeup_shape/battery.py levels --arms start,shape --out round1
    python barrels/experiments/2026-11-23_closeup_shape/battery.py recordings --rec <data/recordings> --arms shape --against start --out round1

Train frames only (asserted in the loaded scripts). Outputs: results/2026-11-23_closeup_shape/<out>/.
"""
from __future__ import annotations

import sys

import closeup as K

PARTS = {"card": "run_card.py", "eval": "run_eval.py", "levels": "run_levels.py", "recordings": "run_recordings.py"}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in PARTS:
        print(__doc__)
        return 2
    C = K.battery()
    mod = C.load(f"comb_{argv[0]}", K.COMB / PARTS[argv[0]])
    return mod.main(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
