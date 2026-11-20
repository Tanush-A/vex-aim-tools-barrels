#!/usr/bin/env python3
"""The damage levels with this experiment's arms: the 16 HOME hand masks (29 barrels) as they are, and with seeded
damage (``barrels.degrade``) at each level of PREREG.md:

  perfect masks                        no damage
  white tables, typical                ``degrade.REALISTIC`` (measured on real white-table segmentation)
  white tables, bad day                ``degrade.REALISTIC``
  bad day without the stripe patch     "bad day" with ``stripe_highlight`` 0
  light, medium, heavy                 ``degrade.SEVERITIES`` (the made-up levels of 2026-11-18, for continuity)
  white tables, worst seen             ``degrade.WORST_SEEN`` (report only)

Masks and seeds exactly as in ``2026-11-18_det_given_seg`` and ``2026-11-19_damage_realism``:
``damage(hand[s], boxes[s], d, seed=1000 * seed + frame index)``; seeds 0 to 4 ("of 145") and seeds 0 to 19 ("of 580").
Scored by the v2 rule. Every false box is listed with the rule that drew it.

Train frames only; a test frame is never opened (asserted in the loaded script).

    python barrels/experiments/2026-11-20_occl_combined/run_levels.py [--arms before,stack,combined] [--out round1]
Outputs: results/2026-11-20_occl_combined/[<out>/] levels.md, levels.csv, levels_false_boxes.csv, levels_config.json.
"""
from __future__ import annotations

import argparse
import collections
import csv
import dataclasses
import json

import common as C
from barrels import cv as bcv, degrade as dg, detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, report as rp

A = C.A
CAM = geo.AIM_4A8B6118_BOXFIT
SEEDS, MORE_SEEDS = tuple(range(5)), tuple(range(20))
TYPICAL, BAD = "white tables, typical", "white tables, bad day"
NO_PATCH = "bad day without the stripe patch"
LEVELS = {
    "perfect masks": None,
    TYPICAL: dg.REALISTIC[TYPICAL],
    BAD: dg.REALISTIC[BAD],
    NO_PATCH: dataclasses.replace(dg.REALISTIC[BAD], stripe_highlight=dg.Damage().stripe_highlight),
    **dg.SEVERITIES,
    **dg.WORST_SEEN,
}
JUDGED = ("perfect masks", TYPICAL, NO_PATCH, "light")          # PREREG (c): false boxes not above `stack`
DOUBLE = (BAD, "medium")                                        # PREREG (c): reported; not more than double `stack`


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    arms = C.arm_list(args.arms, C.RULE_ARMS)
    out = C.OUT / args.out if args.out else C.OUT
    out.mkdir(parents=True, exist_ok=True)
    G = C.load("det_given_seg_run", C.SEG / "run.py")            # train_sets, truth, att (the reason log's attribution)
    A.install()
    home = [s for s in G.train_sets()["HOME"] if io.mask_path(s).exists()]
    hand = {s: io.load_mask(io.mask_path(s)) for s in home}
    truth = {s: G.truth(s) for s in home}
    boxes = {s: [tuple(g.bbox) for g in truth[s][0]] for s in home}

    results = collections.defaultdict(list)       # (level, arm, seed or -1) -> [DetImageResult]
    false_rows, causes = [], collections.defaultdict(collections.Counter)
    for level, d in LEVELS.items():
        seeds = (-1,) if d is None else MORE_SEEDS
        for seed in seeds:
            for i, s in enumerate(home):
                mask = hand[s] if d is None else dg.damage(hand[s], boxes[s], d, seed=1000 * seed + i)
                gts, clean = truth[s]
                for a in arms:
                    log: list = []
                    preds = det.detect(mask, A.ARMS[a], CAM, log=log)
                    res = ed.evaluate_frame(s, preds, gts, CAM, rule="v2", clean=clean)
                    results[(level, a, seed)].append(res)
                    if seed < len(SEEDS):
                        for gi in res.unmatched_gt:
                            causes[(level, a)][G.att.attribute(gts[gi], preds, log, G.att.inside(mask, gts[gi]))[0]] += 1
                    for pi in res.unmatched_pred:
                        p = preds[pi]
                        same = [(ed.box_iou(p.bbox, g.bbox), g) for g in gts if g.color == p.color]
                        iou, g = max(same, key=lambda t: t[0]) if same else (0.0, None)
                        false_rows.append({"level": level, "arm": a, "stem": s.replace("4A8B_window_light_", ""), "seed": "" if seed < 0 else seed,
                                           "color": dtp.COLOR_NAMES[p.color], "box": list(p.bbox), "flags": "+".join(sorted(p.flags)),
                                           "drawn_by": C.drawn_by(log, p.bbox),
                                           "width_over_expected": round(p.width / CAM.expected_barrel_width_px(bottom_row=p.bbox[3]), 2),
                                           "best_overlap_same_color": round(iou, 2), "that_truth_box": list(g.bbox) if g is not None else "",
                                           "that_truth_also_missed": int(g is not None and any(gts[gi] is g for gi in res.unmatched_gt))})

    def cell(level, a, seeds):
        rs = [r for sd in ((-1,) if LEVELS[level] is None else seeds) for r in results[(level, a, sd)]]
        return rp.summarize(rs)

    with (out / "levels.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["level", "arm", "seeds", "frames", "barrels", "found", "missed", "false"])
        for level in LEVELS:
            for a in arms:
                for seeds in ((SEEDS,) if LEVELS[level] is None else (SEEDS, MORE_SEEDS)):
                    c = cell(level, a, seeds)
                    w.writerow([level, a, 1 if LEVELS[level] is None else len(seeds), c.frames, c.barrels, c.found, c.missed, c.false])
    with (out / "levels_false_boxes.csv").open("w", newline="") as f:
        fields = ["level", "arm", "stem", "seed", "color", "box", "flags", "drawn_by", "width_over_expected", "best_overlap_same_color",
                  "that_truth_box", "that_truth_also_missed"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(false_rows)

    def txt(c):
        return f"{c.found} / {c.barrels} ({c.false})"

    def mark(level):
        return " **(judged)**" if level in JUDGED else (" (reported; not more than double)" if level in DOUBLE else " (report only)")

    L = ["# The damage levels: found / barrels (false boxes)", "",
         f"git {bcv.git_hash()}; v2 rule; the 16 HOME hand masks (29 barrels), train frames only. Arms: `experiments/2026-11-20_occl_combined/comb_arms.py`. "
         "PREREG clause (c): at the judged levels the false boxes may not be above `stack`'s, with 5 seeds and with 20.", ""]
    for seeds, title in ((SEEDS, "## Seeds 0 to 4 (as every earlier test: 145 barrels per damaged level)"),
                         (MORE_SEEDS, "## Seeds 0 to 19 (580 barrels per damaged level)")):
        L += [title, "", "| level | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|" + "---|" * len(arms)]
        for level in LEVELS:
            L.append(f"| {level}{mark(level)} | " + " | ".join(txt(cell(level, a, seeds)) for a in arms) + " |")
        L.append("")
    L += ["## What each level is", ""]
    for level, d in LEVELS.items():
        L.append(f"- `{level}`: " + ("no damage" if d is None else
                                     (", ".join(f"{k} {v}" for k, v in d.to_dict().items() if v not in (0, 0.0, (0.0, 0.0), (0, 0.0))) or "no damage")))
    L += ["", "## The false boxes, by the rule that drew them (seeds 0 to 19)", "",
          "| level | arm | " + " | ".join(C.STAGE_NAME.values()) + " |", "|---|---|" + "---|" * len(C.STAGE_NAME)]
    by = collections.Counter((r["level"], r["arm"], r["drawn_by"]) for r in false_rows)
    for level in LEVELS:
        for a in arms:
            if any(by[(level, a, k)] for k in C.STAGE_NAME.values()):
                L.append(f"| {level} | `{a}` | " + " | ".join(str(by[(level, a, k)]) for k in C.STAGE_NAME.values()) + " |")
    L += ["", "## Which test refused the missed barrels (seeds 0 to 4; the detector's reason log)", ""]
    for level in LEVELS:
        for a in arms:
            if causes[(level, a)]:
                L.append(f"- {level}, `{a}`: " + ", ".join(f"{k} {v}" for k, v in causes[(level, a)].most_common()))
    L += ["", "## Every false box at the judged levels (seeds 0 to 19)", "",
          "| level | arm | frame | seed | color | box | drawn by | width / a barrel's | best overlap with a true box of its color | that barrel also missed |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in false_rows:
        if r["level"] in JUDGED:
            L.append(f"| {r['level']} | `{r['arm']}` | {r['stem']} | {r['seed']} | {r['color']} | {r['box']} | {r['drawn_by']} | {r['width_over_expected']} | "
                     f"{r['best_overlap_same_color']} | {'yes' if r['that_truth_also_missed'] else 'no'} |")
    (out / "levels.md").write_text("\n".join(L) + "\n")
    json.dump({"git": bcv.git_hash(), "camera": "AIM_4A8B6118_BOXFIT", "seeds": SEEDS, "more_seeds": MORE_SEEDS,
               "levels": {k: (None if d is None else d.to_dict()) for k, d in LEVELS.items()},
               "arms": {a: dataclasses.asdict(A.ARMS[a]) for a in arms}, "home_frames": home}, (out / "levels_config.json").open("w"), indent=1)
    print("\n".join(L[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
