#!/usr/bin/env python3
"""The battery of ``2026-11-20_occl_combined`` (as A8 ran it), unchanged, with this experiment's arms and results folder.

    python barrels/experiments/2026-11-23_own_convex/battery.py card --arms start,close --out diag --no-sheets
    python barrels/experiments/2026-11-23_own_convex/battery.py levels --arms start,close --out diag

One shim, stated plainly: the levels harness takes the HOME frames from ``2026-11-18_det_given_seg/run.py:train_sets``,
which raises on the sets imported 2026-11-19..21 (its grouping knows HOME, CAMPUS, BLACK and wood only). For this
process only, ``splits.load_splits`` hands it the train list without those new sets; the HOME frames it gets (and so the
masks and seeds) are exactly those of A8. The test list is passed through untouched; no test frame is opened.
Outputs: results/2026-11-23_own_convex/<out>/ (the files each script names).
"""
from __future__ import annotations

import sys

import own_arms as O
from barrels import io, splits

C, A, S = O.C, O.A, O.S
PARTS = {"card": "run_card.py", "eval": "run_eval.py", "levels": "run_levels.py", "recordings": "run_recordings.py"}
_KNOWN = {"window_light", "campus_light", "window_black"}


def _old_sets_only():
    real = splits.load_splits

    def load(*a, **k):
        sp = dict(real(*a, **k))
        keep = []
        for s in sp["train"]:
            try:
                t = io.parse_name(s)
            except ValueError:
                continue
            if t["surface"] == "wood" or f"{t['light']}_{t['surface']}" in _KNOWN:
                keep.append(s)
        sp["train"] = keep
        return sp
    splits.load_splits = load


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in PARTS:
        print(__doc__)
        return 2
    O.register()
    assert not O.check_start(), O.check_start()
    C.OUT = A.OUT = O.OUT
    C.RULE_ARMS = tuple(O.ARMS)
    if argv[0] in ("levels", "eval"):
        _old_sets_only()
    mod = C.load(f"own_{argv[0]}", S.COMB / PARTS[argv[0]])
    return mod.main(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
