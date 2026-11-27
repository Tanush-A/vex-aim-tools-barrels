"""The two report-only diagnostics of the PREREG addendum (post hoc; not candidates for adoption).

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_peaks/diagnostics.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import candidates as cd  # noqa: E402
import run as rn  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import judge as jg  # noqa: E402

P2_SETTING = {"cap": 4, "n_min": 50, "pad": 0, "s_follow": True, "mode": "union"}


def d1(stem, frame):
    th = cd.frame_thresholds(cd.peaks_of(stem, frame)["F6_pair_small"], P2_SETTING)
    return cd.boxes_for(stem, frame, th)


d1.describe = f"D1 (report only): F6 finder with the fixed setting {P2_SETTING}"


def fit_d2(train_stems, held_place):
    if ("P2", held_place) not in cd.CHOSEN:
        s, table = cd.choose("P2", list(train_stems))
        cd.CHOSEN[("P2", held_place)] = {"setting": s, "table": table}
    s = cd.CHOSEN[("P2", held_place)]["setting"]

    def detect(stem, frame):
        th = cd.FIXED_TH if s is None else cd.frame_thresholds(cd.peaks_of(stem, frame)["F5_pair"], s)
        return cd.boxes_for(stem, frame, th, selfcal=True)
    detect.describe = f"D2 P2 {s} then selfcal AB, picked without {held_place}"
    return detect


fit_d2.describe = "D2 (report only): P2's fold choices as the first pass of selfcal AB"


def main():
    frames = jg.train_frames()
    truth = jg.load_truth(frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED])
    out = []
    for name, det, fit in (("D1", d1, None), ("D2", None, fit_d2)):
        j = jg.judge(det, fit=fit, name=name, base_name="fixed", frames=frames, truth=truth, out_dir=rn.OUT / f"judge_{name}")
        r = rn.row(name, j)
        out.append(r)
        print(json.dumps(r), flush=True)
        rn.sheets(name, j)
    (rn.OUT / "diagnostics.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
