#!/usr/bin/env python3
"""The battery of ``2026-11-20_occl_combined`` (scorecard, eval table, damage levels, recordings), run unchanged with this
experiment's arms (``strict.ARMS``) and results folder, as ``2026-11-23_closeup_shape/battery.py`` does.

    python barrels/experiments/2026-11-24_occl_strict/battery.py card --arms start,strict --out round1 --no-sheets
    python barrels/experiments/2026-11-24_occl_strict/battery.py eval --arms start,strict --against start --out round1
    python barrels/experiments/2026-11-24_occl_strict/battery.py levels --arms start,strict --out round1
    python barrels/experiments/2026-11-24_occl_strict/battery.py recordings --rec <data/recordings> --arms strict --against start --out round1

Train frames only (asserted in the loaded scripts). Outputs: results/2026-11-24_occl_strict/<out>/.
"""
from __future__ import annotations

import sys

import strict as S

PARTS = {"card": "run_card.py", "eval": "run_eval.py", "levels": "run_levels.py", "recordings": "run_recordings.py"}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in PARTS:
        print(__doc__)
        return 2
    C = S.battery()
    mod = C.load(f"comb_{argv[0]}", S.COMB / PARTS[argv[0]])
    return mod.main(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
