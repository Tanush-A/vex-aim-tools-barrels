#!/usr/bin/env python3
"""The judged runs of the 2026-11-26 contrast experiment (plan: PREREG.md, committed before this was first run).

    python barrels/experiments/2026-11-26_contrast/run.py [--jobs 8] [--only C1_add_guards,...] [--tag _r2]

1. Every setting of every family on every ordinary train frame, once (``table.build_table``).
2. Every family through the standard pass rule, leave one place out (``judge.leave_one_place_out`` with the family's
   ``fit``): one pass over the frames for today's detector and all candidates, then ``judge.compare`` for each.
3. In-sample, for the record and never a verdict: the setting each family's rule picks on all eight places.

Train frames only (``judge.run_many`` and ``judge.load_frame`` refuse anything else). Writes
results/2026-11-26_contrast/: summary.md, chosen.json, one folder ``judge_<family>/`` per candidate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import table as tb  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.detect_types import COLOR_NAMES  # noqa: E402

WEAK = 2.0          # a PASS less than this many placements above the gain margin is WEAK (the task's rule)
WATCH = ("home_bathtile", "home_ottoman", "abp_gray")
SHORT = lambda s: s.replace("4A8B_", "")     # noqa: E731


def strength(j: jg.Judgement) -> str:
    if j.result != jg.PASS:
        return j.result
    d = j.total[1].found_w - j.total[0].found_w
    return "PASS" if d >= j.margins.found_gain + WEAK - 1e-9 else "PASS (WEAK)"


def new_box_frames(j: jg.Judgement) -> list[dict]:
    return [x for x in j.box_changes if x["judged"] and sum(x["after"].values()) > sum(x["before"].values())]


def row(name: str, j: jg.Judgement) -> str:
    b, c = j.total
    return (f"| {tb.TITLES[name]} | **{strength(j)}** | {b.found_w:.1f} → {c.found_w:.1f} ({c.found_w - b.found_w:+.1f}) | {b.found} → {c.found} | "
            f"{b.extra_w:.2f} → {c.extra_w:.2f} ({b.extra} → {c.extra}) | {b.clean_empty} → {c.clean_empty} / {b.cluttered_empty_w:.2f} → {c.cluttered_empty_w:.2f} | "
            + ("; ".join(f"{p} {pb.found_w:.1f} → {pc.found_w:.1f} of {pb.placements}" for p, (pb, pc) in j.places.items() if abs(pc.found_w - pb.found_w) > 1e-9) or "none") + " |")


def boxes_text(boxes) -> str:
    return ", ".join(f"{COLOR_NAMES[b.color]} {list(int(v) for v in b.bbox)}" for b in boxes) or "none"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default="", help="comma-separated family names (default: all)")
    ap.add_argument("--tag", default="", help="a suffix for the output files of a later round")
    a = ap.parse_args()
    names = [n for n in list(tb.FAMILIES) + [tb.ALONE] if not a.only or n in a.only.split(",")]
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    margins = jg.load_margins()
    settings = tb.all_settings()
    print(f"{len(settings)} settings x {len(ordinary)} ordinary train frames", flush=True)
    table = tb.build_table(ordinary, settings, a.jobs)
    fitter = tb.Fitter(table, truth.placements, margins)
    detectors = {"today": jg.fixed_detector()}
    for n in names:
        detectors[n] = jg.leave_one_place_out(fitter.fit(n), ordinary, f"{tb.TITLES[n]}; fitted leave one place out")
    runs = jg.run_many(detectors, stems, truth)
    judged = {}
    for n in names:
        j = jg.compare(runs["today"], runs[n], frames, truth, margins, lopo=True)
        jg.write(j, cm.OUT / f"judge_{n}{a.tag}")
        judged[n] = j
        print(f"{n}: {strength(j)}  found {j.total[0].found_w:.1f} -> {j.total[1].found_w:.1f}", flush=True)
    final = {}
    for n in names:
        if n == tb.ALONE:
            continue
        st, info = tb.choose(table, tb.FAMILIES[n], ordinary, truth.placements, margins)
        final[n] = {"setting": tb.describe(st), "spec": "" if st is None else st.spec, **info}
    per_frame = {n: runs[n].seconds / len(stems) for n in ["today"] + names}
    out = {"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "folds": {n: fitter.chosen[n] for n in names}, "in_sample_all_places": final,
           "seconds_per_frame": {n: round(v, 3) for n, v in per_frame.items()},
           "verdicts": {n: {"verdict": strength(j), "found_w": [round(j.total[0].found_w, 2), round(j.total[1].found_w, 2)], "found": [j.total[0].found, j.total[1].found],
                            "extra_w": [round(j.total[0].extra_w, 2), round(j.total[1].extra_w, 2)], "extra": [j.total[0].extra, j.total[1].extra],
                            "clean_empty": [j.total[0].clean_empty, j.total[1].clean_empty],
                            "cluttered_empty_w": [round(j.total[0].cluttered_empty_w, 2), round(j.total[1].cluttered_empty_w, 2)],
                            "places": {p: [round(pb.found_w, 2), round(pc.found_w, 2), pb.placements] for p, (pb, pc) in j.places.items()},
                            "conditions": {c_: [cb.found, cc.found, cb.barrels] for c_, (cb, cc) in j.conditions.items()},
                            "report_only": {c_: [cb.found, cc.found, cb.barrels, cb.extra, cc.extra] for c_, (cb, cc) in j.report_only.items()},
                            "traps": {SHORT(s): {"today": boxes_text(runs["today"].boxes[s]), "candidate": boxes_text(runs[n].boxes[s])} for s in cm.TRAPS},
                            "frames_with_new_boxes": [SHORT(x["stem"]) for x in new_box_frames(j)],
                            "gained": sum(x.kind == "gained" for x in j.changes if x.judged), "lost": sum(x.kind == "lost" for x in j.changes if x.judged)}
                        for n, j in judged.items()}}
    (cm.OUT / f"chosen{a.tag}.json").write_text(json.dumps(out, indent=1, default=float) + "\n")

    j0 = judged[names[0]]
    L = [f"# The judged candidates of the contrast experiment ({out['made']}, git {out['git']})", "",
         "`python barrels/experiments/2026-11-26_contrast/run.py` (plan: `../../experiments/2026-11-26_contrast/PREREG.md`). The standard pass rule (`docs/EVAL.md`), leave one "
         f"place out: every place is scored by a setting picked on the other seven. Train frames only. Baseline: today's default. {len(ordinary)} ordinary frames, "
         f"{j0.total[0].placements} placements, {len(j0.places)} places. A PASS under +{margins.found_gain + WEAK:.1f} placements is WEAK. "
         f"Margins: found better above +{margins.found_gain:.2f}; boxes not on their barrel worse above +{margins.extra_rise:.2f}; "
         f"boxes on empty frames with clutter worse above +{margins.cluttered_empty:.2f}; a box on a clean empty frame fails.", "",
         "| candidate | verdict | found, placements | found, per frame | boxes not on their barrel, per arrangement (per frame) | on empty frames: clean / with clutter | places that moved |",
         "|---|---|---|---|---|---|---|"]
    L += [row(n, judged[n]) for n in names]
    L += ["", "Time in the detector per frame: " + "; ".join(f"{n} {v * 1000:.0f} ms" for n, v in per_frame.items()) + "."]
    for n in names:
        j = judged[n]
        gained = [x for x in j.changes if x.judged and x.kind == "gained"]
        lost = [x for x in j.changes if x.judged and x.kind == "lost"]
        L += ["", f"## {tb.TITLES[n]}: {strength(j)}", ""]
        L += [f"- [{c.state}] {c.text}" for c in j.verdict.clauses]
        L += [f"- Barrels, per frame: {len(gained)} gained, {len(lost)} lost." + (" Lost: " + "; ".join(f"{SHORT(x.stem)} #{x.index + 1} {x.color}" for x in lost) + "." if lost else ""),
              "- The three places the vendor wins at: " + "; ".join(f"{p} {j.places[p][0].found_w:.2f} → {j.places[p][1].found_w:.2f} of {j.places[p][0].placements} "
                                                                    f"(per frame {j.places[p][0].found} → {j.places[p][1].found} of {j.places[p][0].barrels}; boxes not on their barrel "
                                                                    f"{j.places[p][0].extra} → {j.places[p][1].extra})" for p in WATCH) + ".",
              "- By condition, found per frame (only those that moved): " + ("; ".join(f"{c_} {cb.found} → {cc.found} of {cb.barrels}" for c_, (cb, cc) in j.conditions.items() if cb.found != cc.found) or "none") + ".",
              "- The named traps (boxes today → boxes of the candidate): " + "; ".join(f"{SHORT(s)}: {boxes_text(runs['today'].boxes[s])} → {boxes_text(runs[n].boxes[s])}" for s in cm.TRAPS) + ".",
              "- Every frame with more boxes that are not on their barrel: " + ("; ".join(f"{SHORT(x['stem'])}{' [empty]' if x['empty'] else ''} {[(c_, list(bb)) for c_, bb in x['boxes_after']]}" for x in new_box_frames(j)) or "none") + ".",
              "- The setting picked for each held-out place: " + "; ".join(f"{p}: {c_['setting']} (gain on the other places {c_['gain']:+.2f}, {c_['allowed']} of {c_['of']} settings allowed)"
                                                                         for p, c_ in fitter.chosen[n].items() if p in j.places) + "."]
        if n in final:
            L.append(f"- In-sample, not a verdict: on all eight places the rule picks: {final[n]['setting']} (found {final[n]['found_w']:+.2f} placements, boxes {final[n]['extra_w']:+.2f}).")
        L += ["- Extreme conditions (report only), found per frame and boxes not on their barrel: "
              + "; ".join(f"{c_} {cb.found} → {cc.found} of {cb.barrels} (boxes {cb.extra} → {cc.extra})" for c_, (cb, cc) in j.report_only.items()) + ".",
              f"- Pages: `judge_{n}{a.tag}/judge.md`, `judge.json`, `changes.csv`."]
    (cm.OUT / f"summary{a.tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
