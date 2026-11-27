#!/usr/bin/env python3
"""Does the adopted stage 11 still catch the traps "bluer than the light" draws? (plan: PREREG.md, addendum 2)

    env PYTHONPATH=<export>/src python b4_traps.py <export> [--jobs 8]

``<export>`` = a ``barrels/`` folder holding ``experiments/2026-11-26_light`` and ``experiments/2026-11-27_bluer_geom``
of branch wip/exp-bluer-geom unchanged (``git archive``), and ``src/`` = this branch's ``src/`` at f4de264 plus
``lightread.py`` and ``contrast.py`` of that branch; ``data`` and ``results/baseline`` linked to this checkout's.
The bluer_geom code asserts that ``barrels`` is imported from that folder, so the export holds the copy.

Families B4_no_checks and D0.20_no_checks, picked per fold by ``fitgeo.choose`` (leave one place out), judged against
today's default (fixed colors, stage 11 off):
  (i)  folds pick on the detector before stage 11 (the experiment exactly); the pick runs with stage 11 off and on;
  (ii) folds pick on the detector with stage 11 (the table built with it); the pick runs with stage 11.
Stage 11 "off" = ``DetConfig(solid_min=0, label_stripe=inf)``: neither check can fire, so the ten stages alone.
Every box not on its barrel that (i) draws without stage 11 on the ordinary frames: its round-1 readings
(``stages.measure``), its round-2 readings (``detector.paint_readings``), and whether stage 11 removes it.

Outputs: results/2026-11-27_checks/b4/ (summary.md, false_boxes.csv, picks.json, judge_*/); sheets/b4_false_*.jpg."""
from __future__ import annotations

import csv
import dataclasses
import json
import math
import multiprocessing as mp
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
EXPORT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(EXPORT / "src"))
sys.path.insert(0, str(EXPORT / "experiments" / "2026-11-27_bluer_geom"))
import bg  # noqa: E402
import checks as ck  # noqa: E402
import fitgeo as fg  # noqa: E402
import stages as sg  # noqa: E402
from bg import ru  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import judge as jg  # noqa: E402

assert hasattr(det, "drop_unlike_paint") and not hasattr(det.DetConfig(), "check_solid"), "needs the plain code (f4de264)"
OUT = BARRELS / "results" / "2026-11-27_checks" / "b4"
SHEETS = BARRELS / "results" / "2026-11-27_checks" / "sheets"
CAM = sg.CAM
OFF = dataclasses.replace(det.DetConfig(), solid_min=0.0, label_stripe=math.inf)
ON = det.DetConfig()
P1 = ck.Checks(0.40, 1.25, 0.6)                   # round 1 at P, for comparison
FAMS = {"B4": fg.fam(fg.B4, [ck.OFF]), "D0.20": fg.FAMILIES["D0.20_no_checks"]}
ORIG_FOUND = sg.found


def found_with_stage11(mask, cfg=det.DetConfig(), cam=CAM):
    fs = ORIG_FOUND(mask, cfg, cam)
    return sorted(det.drop_unlike_paint(fs, mask, cam, ON), key=lambda f: f.barrel.bbox[0])


def make_fit(table, family, cfg, placements, margins, record):
    def fit(train_stems, held):
        m, info = fg.choose(table, family, [s for s in train_stems if s in table], placements, margins)
        record[held] = None if m is None else fg.key(m)
        c = (m or fg.FIXED)[0]

        def detect_frame(stem, frame):
            return det.detect(ru.segment(frame, c), cfg, CAM)
        detect_frame.setting = c
        return detect_frame
    return fit


def row(j):
    b, c = j.total
    g = sum(1 for x in j.changes if x.judged and x.kind == "gained")
    lo = sum(1 for x in j.changes if x.judged and x.kind == "lost")
    moved = "; ".join(f"{p} {v[0].found_w:g} → {v[1].found_w:g}" for p, v in j.places.items() if abs(v[0].found_w - v[1].found_w) > 1e-9)
    return (f"**{j.verdict.result}** | {b.found_w:.2f} → {c.found_w:.2f} | {b.found} → {c.found} | {g} / {lo} | {b.extra_w:.2f} → {c.extra_w:.2f} ({b.extra} → {c.extra}) | "
            f"{b.clean_empty} → {c.clean_empty} / {b.cluttered_empty_w:.2f} → {c.cluttered_empty_w:.2f} | {moved}")


def main() -> int:
    mp.set_start_method("fork", force=True)
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    OUT.mkdir(parents=True, exist_ok=True)
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    margins = jg.load_margins()
    members = list(dict.fromkeys([fg.FIXED] + FAMS["B4"] + FAMS["D0.20"]))
    fg.CACHE = bg.OUT / "cache_geo_before11"
    print("table, before stage 11", flush=True)
    t_before = fg.build_table(ordinary, members, jobs)
    sg.found = found_with_stage11
    fg.CACHE = bg.OUT / "cache_geo_with11"
    print("table, with stage 11", flush=True)
    t_with = fg.build_table(ordinary, members, jobs)
    sg.found = ORIG_FOUND
    picks: dict = {}
    dets = {"today": jg.model_detector(det_overrides={"solid_min": 0.0, "label_stripe": math.inf}, describe="today's default (stage 11 off)"),
            "today_plain": jg.fixed_detector()}
    for f, fam in FAMS.items():
        for name, table, cfg in ((f"{f}_i_off", t_before, OFF), (f"{f}_i_on", t_before, ON), (f"{f}_ii_on", t_with, ON)):
            picks[name] = {}
            dets[name] = jg.leave_one_place_out(make_fit(table, fam, cfg, truth.placements, margins, picks[name]), ordinary, name)
    runs = jg.run_many(dets, stems, truth)
    same_today = all([(b.color, b.bbox) for b in runs["today"].boxes[s]] == [(b.color, b.bbox) for b in runs["today_plain"].boxes[s]] for s in stems)
    L = ["# Does the adopted stage 11 still catch B4's traps? (addendum 2)", "",
         f"Leave one place out, the standard rule. Today's default = fixed colors, stage 11 off (with stage 11: the same boxes on every train frame: {same_today}).",
         "(i) = folds pick on the detector before stage 11, as bluer_geom did; (ii) = folds pick with stage 11 in the detector.", "",
         "| baseline | candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel (per frame) | empty: clean / cluttered | places that moved |",
         "|---|---|---|---|---|---|---|---|---|"]
    pairs = []
    for f in FAMS:
        pairs += [("today", f"{f}_i_off"), ("today", f"{f}_i_on"), ("today", f"{f}_ii_on"), (f"{f}_i_off", f"{f}_i_on")]
    for b, c in pairs:
        j = jg.compare(runs[b], runs[c], frames, truth, margins, lopo=True)
        jg.write(j, OUT / f"judge_{c}_vs_{b}")
        L.append(f"| {b} | {c} | {row(j)} |")
        print(L[-1], flush=True)
    (OUT / "picks.json").write_text(json.dumps(picks, indent=1) + "\n")

    # every box not on its barrel that (i) draws without stage 11, ordinary frames
    rows = []
    for f in FAMS:
        off_run, on_run = runs[f"{f}_i_off"], runs[f"{f}_i_on"]
        fitted = dets[f"{f}_i_off"].fitted
        for s in ordinary:
            fc = off_run.counts[s]
            bad = [i for i, st in enumerate(fc.boxes) if st in ct.EXTRA_STATES]
            if not bad:
                continue
            frame = jg.load_frame(s)
            c = fitted[ct.place_of(s)].setting
            mask = ru.segment(frame, c)
            fs = ORIG_FOUND(mask)
            kept_on = {(b.color, tuple(b.bbox)) for b in on_run.boxes[s]}
            for i in bad:
                b = off_run.boxes[s][i]
                hit = [x for x in fs if x.barrel.color == b.color and tuple(x.barrel.bbox) == tuple(b.bbox)]
                assert len(hit) == 1, (s, b.bbox)
                fnd = hit[0]
                m1 = sg.measure(fnd, mask)
                r2 = det.paint_readings(fnd, mask, CAM, ON)
                rows.append({"family": f, "stem": s, "state": fc.boxes[i], "color": "orange" if b.color == 1 else "blue", "rule": fnd.rule,
                             "bbox": " ".join(map(str, b.bbox)), "r1_solid": m1.get("solid"), "r1_stripe": m1.get("stripe_h_ratio"), "r1_body": m1.get("body_fill"),
                             "r1_removes_P": ck.removes(m1, P1), "r2_solid": None if r2 is None else round(r2[0], 4),
                             "r2_stripe": None if r2 is None else round(r2[1], 4), "r2_body": None if r2 is None else round(r2[2], 4),
                             "stage11_removes": (b.color, tuple(b.bbox)) not in kept_on})
    with open(OUT / "false_boxes.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    L += ["", "## Every box not on its barrel drawn by (i) without stage 11 (ordinary frames)", "",
          "| family | # | frame | state | color | rule | box | round 1: solid / stripe / body → removes at P | round 2: solid / stripe / body | stage 11 removes |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in enumerate(rows, 1):
        L.append(f"| {r['family']} | {k} | {r['stem'].replace('4A8B_', '')} | {r['state']} | {r['color']} | {r['rule']} | {r['bbox']} | "
                 f"{r['r1_solid']} / {r['r1_stripe']} / {r['r1_body']} → {'yes' if r['r1_removes_P'] else 'no'} | {r['r2_solid']} / {r['r2_stripe']} / {r['r2_body']} | "
                 f"{'**yes**' if r['stage11_removes'] else 'no'} |")
    (OUT / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[-len(rows) - 2:]))

    # contact sheets of those boxes
    sys.path.insert(0, str(HERE))
    import sheets as sh
    tiles = []
    for k, r in enumerate(rows, 1):
        s = r["stem"]
        frame = jg.load_frame(s)
        c = dets[f"{r['family']}_i_off"].fitted[ct.place_of(s)].setting
        mask = ru.segment(frame, c)
        bb = tuple(int(v) for v in r["bbox"].split())
        tiles.append(sh.tile(frame.bgr.copy(), mask, bb, [g.bbox for g in truth.gts[s]], [b.bbox for b in runs[f"{r['family']}_i_off"].boxes[s]],
                             [f"{r['family']} #{k} {s}", f"{r['state']} {r['color']} {r['rule']}; stage 11 removes: {r['stage11_removes']}",
                              f"r2 solid {r['r2_solid']} stripe {r['r2_stripe']} body {r['r2_body']}"]))
    sh.OUT = SHEETS
    sh.write(tiles, "b4_false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
