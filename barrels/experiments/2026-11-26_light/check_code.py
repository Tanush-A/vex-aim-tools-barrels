#!/usr/bin/env python3
"""A check of the candidate code that produces no result: the fixed setting must give exactly today's mask and boxes,
a setting whose ramp never starts must too, and the families must hold what PREREG.md says. Run before the judged run.

    python barrels/experiments/2026-11-26_light/check_code.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as cd  # noqa: E402
import common as cm  # noqa: E402
import rules as ru  # noqa: E402

from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

FRAMES = ["4A8B_window_light_core_01", "4A8B_lampwarm6_bathtile_core_01", "4A8B_lampcool6_ottoman_close_01"]


def main() -> int:
    sizes = {n: len(f) for n, f in cd.FAMILIES.items()}
    print(sizes, "all settings:", len(cd.all_settings()))
    assert sizes == {"B1_ramp_without_loose": 54, "B2_ramp_above_gate": 54, "B3_ramp_whole_frame": 54, "B4_ramp_rel_without_loose": 270,
                     "O1_orange_follows_light": 9, "O2_orange_follows_dark": 9, "O3_orange_wide_with_guard": 12}
    assert len({s.key for s in cd.all_settings()}) == len(cd.all_settings())
    fixed = jg.fixed_detector()
    for stem in FRAMES:
        frame = jg.load_frame(stem)
        base = pl.segment(frame, cm.model())[0]
        assert (ru.segment(frame, ru.FIXED) == base).all()
        never = [ru.Setting("without_loose", 5.0, 6.0, 30, 88, 0.15), ru.Setting(o_reading="without_loose", o_x0=5.0, o_x1=6.0, o_hi=22.0),
                 ru.Setting(o_reading="dark", o_x0=-5.0, o_x1=-6.0, o_hi=22.0), ru.Setting(o_reading="always", o_x0=0.0, o_x1=1.0, o_hi=22.0, o_guard=1e-9)]
        for st in never:
            assert (ru.segment(frame, st) == base).all(), (stem, st)
        assert [b.bbox for b in ru.detect(frame, ru.FIXED)] == [b.bbox for b in fixed(stem, frame)]
        lower = ru.segment(frame, ru.Setting("without_loose", -1.0, -0.5, 30, 88))          # the ramp fully on: blue only grows
        assert ((lower == 2) | (base != 2)).all(), stem
        rel = ru.segment(frame, ru.Setting("without_loose", -1.0, -0.5, 30, 88, 0.15))
        assert ((rel == 2) | (lower != 2)).all() and ((rel == 1) == (lower == 1)).all(), stem      # the relative rule only adds blue, never touches orange
        assert not frame.rgb.flags.writeable
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
