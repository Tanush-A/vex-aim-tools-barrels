#!/usr/bin/env python3
"""The judged runs (plan: PREREG.md, committed before this was first run).

    python barrels/experiments/2026-11-27_bluer_geom/run.py [--only G1_b4_checks,...] [--jobs 9]

1. Every member of every family on every ordinary train frame, once (``fitgeo.build_table``).
2. Every family through the standard pass rule, leave one place out, against today's default (the verdict).
3. Beside it, not a verdict: each family with checks against the same family without them (does a check cost
   barrels?): G1 against B4 (``B4_no_checks``, the reproduction), D<d>_checks against D<d>_no_checks; G2 is against
   the fixed colors already.
4. In-sample, for the record: the member each rule picks on all eight places.

Writes results/2026-11-27_bluer_geom/: summary.md, chosen.json, judge_<family>/ and vs_own_<family>/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg  # noqa: E402
import fitgeo as fg  # noqa: E402
from bg import ru  # noqa: E402
import checks as ck  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import judge as jg  # noqa: E402

fg.FAMILIES["B4_no_checks"] = fg.fam(fg.B4, [ck.OFF])
fg.TITLES["B4_no_checks"] = "B4 of the light experiment, reproduced through this code (no checks)"
OWN = {"G1_b4_checks": "B4_no_checks", "G1a_b4_k1_only": "B4_no_checks", "G1b_b4_k2_only": "B4_no_checks"}
OWN.update({f"D{d:.2f}_checks": f"D{d:.2f}_no_checks" for d in fg.DELTAS})
WEAK = 2.0


def strength(j) -> str:
    if j.result != jg.PASS:
        return j.result
    d = j.total[1].found_w - j.total[0].found_w
    return "PASS" if d >= j.margins.found_gain + WEAK - 1e-9 else "PASS (WEAK)"


def summary_row(name, j) -> dict:
    b, c = j.total
    return {"verdict": strength(j), "found_w": [round(b.found_w, 2), round(c.found_w, 2)], "found": [b.found, c.found],
            "extra_w": [round(b.extra_w, 2), round(c.extra_w, 2)], "extra": [b.extra, c.extra],
            "clean_empty": [b.clean_empty, c.clean_empty], "cluttered_empty_w": [round(b.cluttered_empty_w, 2), round(c.cluttered_empty_w, 2)],
            "gained": sum(x.kind == "gained" for x in j.changes if x.judged), "lost": sum(x.kind == "lost" for x in j.changes if x.judged),
            "places": {p: [round(pb.found_w, 2), round(pc.found_w, 2)] for p, (pb, pc) in j.places.items() if abs(pc.found_w - pb.found_w) > 1e-9},
            "conditions": {c_: [cb.found, cc.found, cb.barrels] for c_, (cb, cc) in j.conditions.items() if cb.found != cc.found},
            "report_only": {c_: [cb.found, cc.found, cb.barrels, cb.extra, cc.extra] for c_, (cb, cc) in j.report_only.items() if cb.found != cc.found or cb.extra != cc.extra}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=9)
    a = ap.parse_args()
    names = [n for n in fg.FAMILIES if not a.only or n in a.only.split(",")]
    for n in list(names):
        if n in OWN and OWN[n] not in names:
            names.append(OWN[n])
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    margins = jg.load_margins()
    members = list(dict.fromkeys([fg.FIXED] + [m for n in names for m in fg.FAMILIES[n]]))
    print(f"{len(members)} members x {len(ordinary)} ordinary train frames", flush=True)
    table = fg.build_table(ordinary, members, a.jobs)
    fitter = fg.Fitter(table, truth.placements, margins)
    fitter.chosen.update({n: {} for n in names if n not in fitter.chosen})
    dets = {"today": jg.fixed_detector()}
    for n in names:
        dets[n] = jg.leave_one_place_out(fitter.fit(n), ordinary, f"{fg.TITLES[n]}; fitted leave one place out")
    runs = jg.run_many(dets, stems, truth)
    out = {"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "verdicts": {}, "vs_own": {}, "folds": {}, "in_sample_all_places": {}}
    for n in names:
        j = jg.compare(runs["today"], runs[n], frames, truth, margins, lopo=True)
        jg.write(j, bg.OUT / f"judge_{n}")
        out["verdicts"][n] = summary_row(n, j)
        print(f"{n}: {strength(j)} found {j.total[0].found_w:.2f} -> {j.total[1].found_w:.2f} ({j.total[0].found} -> {j.total[1].found}) "
              f"extra {j.total[0].extra_w:.2f} -> {j.total[1].extra_w:.2f}", flush=True)
    for n, own in OWN.items():
        if n in names:
            j = jg.compare(runs[own], runs[n], frames, truth, margins, lopo=True)
            jg.write(j, bg.OUT / f"vs_own_{n}")
            out["vs_own"][n] = {"against": own, **summary_row(n, j)}
    for n in names:
        out["folds"][n] = fitter.chosen[n]
        m, info = fg.choose(table, fg.FAMILIES[n], ordinary, truth.placements, margins)
        out["in_sample_all_places"][n] = {"member": fg.describe(m), **info}
    (bg.OUT / "chosen.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
