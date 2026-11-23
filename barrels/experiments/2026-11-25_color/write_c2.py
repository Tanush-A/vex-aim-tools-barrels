#!/usr/bin/env python3
"""Writes the model file of round 1's C2 final setting (the blue box follows the light, read from the whole frame:
w0 0.08, w1 0.20, blue S -> 40, hue low -> 92), which did NOT pass its PREREG, for the report-only comparisons of step 4
(the never-regress check and ours against the vendor). Not a proposal.

    python barrels/experiments/2026-11-25_color/write_c2.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import test as t  # noqa: E402


def main() -> int:
    st = t.Setting(t.ADOPTED, (0.08, 0.20, 40, 92))
    p = t.write_model(st, passing=False, family="C2 (round 1)")
    target = cm.RESULTS / "config_c2_round1_not_passing.json"
    p.replace(target)
    best = t.write_model(t.Setting((2, 16, 160, 103, 119, 113)), passing=False, family="C1")   # the rule's best, rewritten as it was
    print(f"wrote {target} (and {best} unchanged)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
