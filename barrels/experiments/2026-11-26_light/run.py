#!/usr/bin/env python3
"""The judged runs of the 2026-11-26 light experiment (plan: PREREG.md, committed before this was first run).

    python barrels/experiments/2026-11-26_light/run.py [--jobs 8] [--only B1_ramp_without_loose,...]

1. Every setting of every family on every ordinary train frame, once (``candidates.build_table``).
2. Every family through the standard pass rule, leave one place out (``judge.leave_one_place_out`` with the family's
   ``fit``): one pass over the frames for the baseline and all candidates, then ``judge.compare`` for each.
3. In-sample, for the record and never a verdict: the setting each family's rule picks on all eight places.

Train frames only (``judge.run_many`` and ``judge.load_frame`` refuse anything else). Writes
results/2026-11-26_light/: summary.md, chosen.json, one folder ``judge_<family>/`` per candidate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as cd  # noqa: E402
import common as cm  # noqa: E402
import rules as ru  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import judge as jg  # noqa: E402

WEAK = 2.0          # a PASS less than this many placements above the gain margin is WEAK (the task's rule)
GLASS = "home_glass"


def strength(j: jg.Judgement) -> str:
    if j.result != jg.PASS:
        return j.result
    d = j.total[1].found_w - j.total[0].found_w
    return "PASS" if d >= j.margins.found_gain + WEAK - 1e-9 else "PASS (WEAK)"


def traps(j: jg.Judgement) -> dict:
    """The traps the plan names, read off the judgement: boxes on empty frames (clean, with clutter), every frame with
    a new box that is not on its barrel, and the glass table."""
    b, c = j.total
    new = [x for x in j.box_changes if x["judged"] and sum(x["after"].values()) > sum(x["before"].values())]
    gb, gc = j.places.get(GLASS, (None, None))
    return {"clean_empty": (b.clean_empty, c.clean_empty), "cluttered_empty_w": (round(b.cluttered_empty_w, 2), round(c.cluttered_empty_w, 2)),
            "empty_frames_with_new_boxes": [x["stem"] for x in new if x["empty"]],
            "frames_with_new_boxes": [x["stem"] for x in new],
            "glass": None if gb is None else {"found_w": (round(gb.found_w, 2), round(gc.found_w, 2)), "extra_w": (round(gb.extra_w, 2), round(gc.extra_w, 2)),
                                              "new_box_frames": [x["stem"] for x in new if ct.place_of(x["stem"]) == GLASS]}}


def row(name: str, j: jg.Judgement) -> str:
    b, c = j.total
    return (f"| {cd.TITLES[name]} | **{strength(j)}** | {b.found_w:.1f} → {c.found_w:.1f} ({c.found_w - b.found_w:+.1f}) | {b.found} → {c.found} | "
            f"{b.extra_w:.1f} → {c.extra_w:.1f} ({b.extra} → {c.extra}) | {b.clean_empty} → {c.clean_empty} / {b.cluttered_empty_w:.1f} → {c.cluttered_empty_w:.1f} | "
            + "; ".join(f"{p} {pc.found_w - pb.found_w:+.1f}" for p, (pb, pc) in j.places.items() if abs(pc.found_w - pb.found_w) > 1e-9) + " |")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default="", help="comma-separated family names (default: all)")
    ap.add_argument("--tag", default="", help="a suffix for the output files of a later round")
    a = ap.parse_args()
    names = [n for n in cd.FAMILIES if not a.only or n in a.only.split(",")]
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    margins = jg.load_margins()
    settings = list(dict.fromkeys([ru.FIXED] + [s for n in names for s in cd.FAMILIES[n]]))
    print(f"{len(settings)} settings x {len(ordinary)} ordinary train frames", flush=True)
    table = cd.build_table(ordinary, settings, a.jobs)
    fitter = cd.Fitter(table, truth.placements, margins)
    detectors = {"today": jg.fixed_detector()}
    for n in names:
        detectors[n] = jg.leave_one_place_out(fitter.fit(n), ordinary, f"{cd.TITLES[n]}; fitted leave one place out")
    runs = jg.run_many(detectors, stems, truth)
    judged = {}
    for n in names:
        j = jg.compare(runs["today"], runs[n], frames, truth, margins, lopo=True)
        jg.write(j, cm.OUT / f"judge_{n}{a.tag}")
        judged[n] = j
        print(f"{n}: {strength(j)}  found {j.total[0].found_w:.1f} -> {j.total[1].found_w:.1f}", flush=True)
    # in-sample, for the record: the pick on all eight places
    final = {}
    for n in names:
        st, info = cd.choose(table, cd.FAMILIES[n], ordinary, truth.placements, margins)
        final[n] = {"setting": st.describe(), "key": st.key, **info}
    out = {"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "folds": {n: fitter.chosen[n] for n in names}, "in_sample_all_places": final,
           "verdicts": {n: {"verdict": strength(j), "found_w": [round(j.total[0].found_w, 2), round(j.total[1].found_w, 2)], "found": [j.total[0].found, j.total[1].found],
                            "extra_w": [round(j.total[0].extra_w, 2), round(j.total[1].extra_w, 2)], "traps": traps(j),
                            "places": {p: [round(pb.found_w, 2), round(pc.found_w, 2), pb.placements] for p, (pb, pc) in j.places.items()},
                            "conditions": {c_: [cb.found, cc.found, cb.barrels] for c_, (cb, cc) in j.conditions.items()},
                            "gained": sum(x.kind == "gained" for x in j.changes if x.judged), "lost": sum(x.kind == "lost" for x in j.changes if x.judged)}
                        for n, j in judged.items()}}
    (cm.OUT / f"chosen{a.tag}.json").write_text(json.dumps(out, indent=1, default=float) + "\n")

    L = [f"# The judged candidates of the light experiment ({out['made']}, git {out['git']})", "",
         "`python barrels/experiments/2026-11-26_light/run.py` (plan: `../../experiments/2026-11-26_light/PREREG.md`). The standard pass rule (`docs/EVAL.md`), leave one "
         f"place out: every place is scored by a setting picked on the other seven. Train frames only. Baseline: today's default. {len(ordinary)} ordinary frames, "
         f"{judged[names[0]].total[0].placements} placements, 8 places. A PASS under +{margins.found_gain + WEAK:.1f} placements is WEAK.", "",
         "| candidate | verdict | found, placements | found, per frame | boxes not on their barrel, per arrangement (per frame) | on empty frames: clean / with clutter | places that moved |",
         "|---|---|---|---|---|---|---|"]
    L += [row(n, judged[n]) for n in names]
    for n in names:
        j = judged[n]
        t = traps(j)
        L += ["", f"## {cd.TITLES[n]}: {strength(j)}", ""]
        L += [f"- [{c.state}] {c.text}" for c in j.verdict.clauses]
        gained = [x for x in j.changes if x.judged and x.kind == "gained"]
        lost = [x for x in j.changes if x.judged and x.kind == "lost"]
        L += [f"- Barrels, per frame: {len(gained)} gained, {len(lost)} lost." + (" Lost: " + "; ".join(f"{x.stem.replace('4A8B_', '')} #{x.index + 1} {x.color}" for x in lost) + "." if lost else ""),
              "- By condition, found per frame (only those that moved): " + ("; ".join(f"{c_} {cb.found} → {cc.found} of {cb.barrels}" for c_, (cb, cc) in j.conditions.items() if cb.found != cc.found) or "none") + ".",
              f"- Traps. Clean empty frames: {t['clean_empty'][0]} → {t['clean_empty'][1]} boxes. Empty frames with clutter: {t['cluttered_empty_w'][0]} → {t['cluttered_empty_w'][1]} per arrangement"
              + (f" (new boxes on: {', '.join(s.replace('4A8B_', '') for s in t['empty_frames_with_new_boxes'])})" if t["empty_frames_with_new_boxes"] else "") + ". "
              + (f"Glass table: found {t['glass']['found_w'][0]} → {t['glass']['found_w'][1]}, boxes not on their barrel {t['glass']['extra_w'][0]} → {t['glass']['extra_w'][1]}"
                 + (f" (new boxes on: {', '.join(s.replace('4A8B_', '') for s in t['glass']['new_box_frames'])})" if t['glass']['new_box_frames'] else "") + "." if t["glass"] else ""),
              "- Every frame with more boxes that are not on their barrel: " + (", ".join(s.replace("4A8B_", "") for s in t["frames_with_new_boxes"]) or "none") + ".",
              "- The setting picked for each held-out place: " + "; ".join(f"{p}: {c_['setting']} (gain on the other places {c_['gain']:+.2f}, {c_['allowed']} of {c_['of']} settings allowed)"
                                                                         for p, c_ in fitter.chosen[n].items() if p in j.places) + ".",
              f"- In-sample, not a verdict: on all eight places the rule picks: {final[n]['setting']} (found {final[n]['found_w']:+.2f} placements, boxes {final[n]['extra_w']:+.2f}).",
              f"- Extreme conditions (report only), found per frame: " + ("; ".join(f"{c_} {cb.found} → {cc.found} of {cb.barrels}" for c_, (cb, cc) in j.report_only.items() if cb.found != cc.found) or "nothing moved") + ".",
              f"- Pages: `judge_{n}{a.tag}/judge.md`, `judge.json`, `changes.csv`."]
    (cm.OUT / f"summary{a.tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
