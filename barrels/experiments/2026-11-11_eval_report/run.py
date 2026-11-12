#!/usr/bin/env python3
"""The one-table eval report, first run (TODO step 6, "Clean up the eval", 2026-11-11).

Purpose (no new method, so no hypothesis about the detector): one command shows what is better where — rows =
data set x scenario, a candidate and a baseline side by side with the difference — and its per-set headline
numbers reproduce the published ones (campus 0.99, home LOSO 0.93, Dave 0.47 indicative; no box on any
negative). Metrics unchanged: eval_det's v2 rule (EVAL.md). Train frames only; the 15 test frames are refused
by ``barrels.report`` and never opened.

Arms: candidate = what runs today (hs model eb863d84 + DetConfig()); baseline = the v1 front end (afd85483)
with the same detector. A second table pins the baseline to the 2026-11-05 detector, which is the pairing behind
the published "v1 0.41 on campus" (v1 + today's detector is 0.39, as EXPERIMENTS.md 2026-11-08 already lists).

    python barrels/experiments/2026-11-11_eval_report/run.py

Writes results/2026-11-11_eval_report/{report.md,report.csv,report.json} and .../v1_old_detector/ (same three).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import report as report_tool  # noqa: E402  (tools/report.py)
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-11_eval_report"
OLD_DETECTOR = "stripe_mode=bands,body_min=0,height_max=0,body_width=0,cover_rows=false"     # = DET_OLD of experiments/2026-11-08_seg_hs_v2


def main() -> int:
    rc = report_tool.main(["--out", str(OUT)])                                                  # the default arms
    print()
    return rc or report_tool.main(["--base-det", OLD_DETECTOR, "--out", str(OUT / "v1_old_detector")])


if __name__ == "__main__":
    sys.exit(main())
