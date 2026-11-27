#!/usr/bin/env python3
"""The judged runs of the white-balance experiment (PREREG.md, committed before this was first run).
EXPERIMENT ONLY: the standing rule forbids correcting the image; nothing here may be adopted without Dave.

    python barrels/experiments/2026-11-27_whitebalance/run.py [--jobs 8]

F1..F5 judged as plain detect_frames; P1..P5 and U3 leave one place out. One pass over the frames for the baseline and
every candidate, then ``judge.compare`` for each. Writes results/2026-11-27_whitebalance/: summary.md, chosen.json,
one folder judge_<name>/ per candidate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as cd  # noqa: E402
import wb  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import judge as jg  # noqa: E402

OUT = wb.BARRELS / "results" / "2026-11-27_whitebalance"
WEAK_BELOW = 6.0


def strength(j) -> str:
    if j.result != jg.PASS:
        return j.result
    return "PASS" if j.total[1].found_w - j.total[0].found_w >= WEAK_BELOW - 1e-9 else "PASS (WEAK)"


def row(name, j) -> str:
    b, c = j.total
    gained = sum(x.kind == "gained" for x in j.changes if x.judged)
    lost = sum(x.kind == "lost" for x in j.changes if x.judged)
    return (f"| {cd.TITLES[name]} | **{strength(j)}** | {b.found_w:.1f} → {c.found_w:.1f} ({c.found_w - b.found_w:+.1f}) | {b.found} → {c.found} | {gained} / {lost} | "
            f"{b.extra_w:.2f} → {c.extra_w:.2f} ({b.extra} → {c.extra}) | {b.clean_empty} → {c.clean_empty} / {b.cluttered_empty_w:.2f} → {c.cluttered_empty_w:.2f} | "
            + "; ".join(f"{p} {pb.found_w:.1f} → {pc.found_w:.1f}" for p, (pb, pc) in j.places.items() if abs(pc.found_w - pb.found_w) > 1e-9) + " |")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    margins = jg.load_margins()
    print(f"table: {len(cd.all_settings())} settings x {len(ordinary)} ordinary frames", flush=True)
    table = cd.build_table(ordinary, jobs=a.jobs)
    fitter = cd.Fitter(table, truth.placements, margins)
    detectors = {"today": jg.fixed_detector()}
    for n, st in cd.FULL.items():
        detectors[n] = wb.detector_for(st)
    for n in cd.FAMILIES:
        detectors[n] = jg.leave_one_place_out(fitter.fit(n), ordinary, cd.TITLES[n])
    runs = jg.run_many(detectors, stems, truth)
    names = list(cd.FULL) + list(cd.FAMILIES)
    judged = {}
    for n in names:
        j = jg.compare(runs["today"], runs[n], frames, truth, margins, lopo=n in cd.FAMILIES)
        jg.write(j, OUT / f"judge_{n}")
        judged[n] = j
        print(f"{n}: {strength(j)}  found {j.total[0].found_w:.2f} -> {j.total[1].found_w:.2f}  extra {j.total[0].extra_w:.2f} -> {j.total[1].extra_w:.2f}", flush=True)
    insample = {}
    for n, fam in cd.FAMILIES.items():
        st, info = cd.choose(table, fam, ordinary, truth.placements, margins)
        insample[n] = {"setting": st.describe(), **info}
    out = {"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "folds": fitter.chosen, "in_sample_all_places": insample,
           "verdicts": {n: {"verdict": strength(j), "found_w": [round(j.total[0].found_w, 2), round(j.total[1].found_w, 2)], "found": [j.total[0].found, j.total[1].found],
                            "extra_w": [round(j.total[0].extra_w, 2), round(j.total[1].extra_w, 2)], "extra": [j.total[0].extra, j.total[1].extra],
                            "clean_empty": [j.total[0].clean_empty, j.total[1].clean_empty], "cluttered_empty_w": [round(j.total[0].cluttered_empty_w, 2), round(j.total[1].cluttered_empty_w, 2)],
                            "places": {p: [round(pb.found_w, 2), round(pc.found_w, 2), pb.placements] for p, (pb, pc) in j.places.items()},
                            "conditions": {c: [cb.found, cc.found, cb.barrels] for c, (cb, cc) in j.conditions.items()},
                            "report_only": {c: [cb.found, cc.found, cb.barrels] for c, (cb, cc) in j.report_only.items()},
                            "gained": sum(x.kind == "gained" for x in j.changes if x.judged), "lost": sum(x.kind == "lost" for x in j.changes if x.judged),
                            "clauses": [f"[{c.state}] {c.text}" for c in j.verdict.clauses]}
                        for n, j in judged.items()}}
    (OUT / "chosen.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    L = [f"# The judged candidates of the white-balance experiment ({out['made']}, git {out['git']})", "",
         "**EXPERIMENT ONLY.** The standing rule (Dave, 2026-10-07) forbids correcting the image. Nothing here may be adopted without Dave.", "",
         f"`run.py`. The standard pass rule; F = full correction, judged as is; P and U = alpha chosen leave one place out. Train frames only, {len(ordinary)} ordinary frames, "
         f"{judged[names[0]].total[0].placements} placements, 8 places. A PASS under +{WEAK_BELOW:.0f} placements is WEAK.", "",
         "| candidate | verdict | found, placements | found, per frame | barrels gained / lost (per frame) | boxes not on their barrel, per arrangement (per frame) | on empty frames: clean / with clutter | places that moved |",
         "|---|---|---|---|---|---|---|---|"]
    L += [row(n, judged[n]) for n in names]
    for n in names:
        j = judged[n]
        L += ["", f"## {cd.TITLES[n]}: {strength(j)}", ""]
        L += [f"- [{c.state}] {c.text}" for c in j.verdict.clauses]
        lost = [x for x in j.changes if x.judged and x.kind == "lost"]
        L += ["- By condition, found per frame (only those that moved): " + ("; ".join(f"{c} {cb.found} → {cc.found} of {cb.barrels}" for c, (cb, cc) in j.conditions.items() if cb.found != cc.found) or "none") + ".",
              "- Lost: " + ("; ".join(f"{x.stem.replace('4A8B_', '')} #{x.index + 1} {x.color}" for x in lost) or "none") + ".",
              "- Frames with more boxes not on their barrel: " + (", ".join(x["stem"].replace("4A8B_", "") + (" (EMPTY clean)" if x["empty"] and x["clean"] else " (EMPTY clutter)" if x["empty"] else "")
                                                                        for x in j.box_changes if x["judged"] and sum(x["after"].values()) > sum(x["before"].values())) or "none") + ".",
              "- Extreme conditions (report only), found per frame: " + ("; ".join(f"{c} {cb.found} → {cc.found} of {cb.barrels}" for c, (cb, cc) in j.report_only.items() if cb.found != cc.found) or "nothing moved") + "."]
        if n in cd.FAMILIES:
            L += ["- Picked per held-out place: " + "; ".join(f"{p}: {c['setting']} (gain on the other places {c['gain']:+.2f})" for p, c in fitter.chosen[n].items() if p in j.places) + ".",
                  f"- In-sample, not a verdict: on all eight places the rule picks {insample[n]['setting']} (gain {insample[n]['gain']:+.2f})."]
        L.append(f"- Pages: `judge_{n}/judge.md`.")
    (OUT / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:len(names) + 8]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
