#!/usr/bin/env python3
"""Part A: B4 of the light experiment, leave one place out, on this branch (the collapsed detector).
Must give 145.72 placements / 257 per frame (results/2026-11-26_light/chosen.json)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg  # noqa: E402
from bg import cd  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import judge as jg  # noqa: E402


def main() -> int:
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    margins = jg.load_margins()
    fam = cd.FAMILIES[bg.B4]
    table = cd.build_table(ordinary, list(dict.fromkeys([cd.ru.FIXED] + fam)), 9)
    fitter = cd.Fitter(table, truth.placements, margins)
    dets = {"today": jg.fixed_detector(), "B4": jg.leave_one_place_out(fitter.fit(bg.B4), ordinary, "B4 reproduced")}
    runs = jg.run_many(dets, stems, truth)
    j = jg.compare(runs["today"], runs["B4"], frames, truth, margins, lopo=True)
    jg.write(j, bg.OUT / "judge_A_B4_repro")
    b, c = j.total
    out = {"found_w": [round(b.found_w, 2), round(c.found_w, 2)], "found": [b.found, c.found], "extra_w": [round(b.extra_w, 2), round(c.extra_w, 2)],
           "verdict": j.result, "folds": fitter.chosen[bg.B4]}
    (bg.OUT / "repro.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "folds"}))
    for p, ch in fitter.chosen[bg.B4].items():
        print(p, ch["key"], ch["gain"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
