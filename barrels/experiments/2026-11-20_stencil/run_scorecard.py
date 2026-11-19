#!/usr/bin/env python3
"""The occlusion scorecard of ``2026-11-19_det_occl`` with this experiment's arms. Its ``run.py`` is loaded by path
and run unchanged: the same 50 source barrels (chosen by the same ``base`` settings as on 2026-11-19), the same
3888 scenes, the same scoring. One arm per call next to ``rules``, so the arms can run side by side:

    python barrels/experiments/2026-11-20_stencil/run_scorecard.py stencil        # -> results/2026-11-20_stencil/card_stencil/
    python barrels/experiments/2026-11-20_stencil/run_scorecard.py union --no-sheets

``scorecard.py`` then puts the arms on one page. Train frames only (asserted in the loaded script).
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
import stencil_arms as A  # noqa: E402


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    arm = argv.pop(0)
    spec = importlib.util.spec_from_file_location("det_occl_run", HERE.parent / "2026-11-19_det_occl" / "run.py")
    R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
    R.occl_arms = types.SimpleNamespace(ARMS=A.ARMS, BASE=A.SOURCE_BASE)
    R.OUT = A.OUT
    R.AFTER_TEXT = f"`rules` = the rule detector as it is on this branch. `{arm}`: see experiments/2026-11-20_stencil/stencil_arms.py."
    A.install()
    return R.main(["--arms", f"rules,{arm}", "--out", f"card_{arm.replace('+', '_')}"] + argv)


if __name__ == "__main__":
    raise SystemExit(main())
