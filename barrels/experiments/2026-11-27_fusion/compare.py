#!/usr/bin/env python3
"""Report only (not pre-registered; no choice is made from it): one held-out candidate against another held-out one.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_fusion/compare.py F3r F1a

Asks what the color fusion adds once the shape checks are in: F3r (the votes) against F1a (contrast + checks).
Writes results/2026-11-27_fusion/vs_<base>_<name>/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fuse  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import judge as jg  # noqa: E402


def main(name: str, base: str) -> None:
    frames = jg.train_frames()
    F = fuse.fitter()
    b = jg.leave_one_place_out(F.fit(base), frames[cnd.ORDINARY], fuse.TITLES[base])
    j = jg.judge(fit=F.fit(name), baseline=b, name=name, base_name=base, frames=frames, truth=F.truth,
                 out_dir=fuse.OUT / f"vs_{base}_{name}")
    print(jg.format_judgement(j))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
