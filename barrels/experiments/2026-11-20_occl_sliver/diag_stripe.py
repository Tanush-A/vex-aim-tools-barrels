#!/usr/bin/env python3
"""Part 1, measurement: a stripe cut through. The 16 HOME hand masks (29 barrels) with ONE kind of damage at a time,
the stripe patch (``stripe_highlight`` w: a pale ellipse w x W wide and H / 3 tall across the stripe) or stripe
breaks (``stripe_breaks`` (n, w): n upright slits w x W wide through the middle half of the box), at several widths,
seeds 0 to 19 (``seed = 1000 * seed + frame index``, as every earlier test). Per level and arm: found / barrels
(false boxes), which test refused each missed barrel (the detector's reason log), which rule drew each false box and
whether it is the misplaced box of a barrel that is also missed.

Train frames only; a test frame is never opened (asserted in the loaded script).

    python barrels/experiments/2026-11-20_occl_sliver/diag_stripe.py [--arms start,start+cover] [--out stripe_before]
Outputs: results/2026-11-20_occl_sliver/<out>/ stripe.md, stripe_levels.csv, stripe_misses.csv, stripe_false.csv
"""
from __future__ import annotations

import argparse
import collections
import csv

import sliver as S
from barrels import degrade as dg, detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, report as rp

C, A = S.C, S.A
CAM = geo.AIM_4A8B6118_BOXFIT
WIDTHS = (0.03, 0.06, 0.1, 0.15, 0.2, 0.3)
SEEDS = tuple(range(20))
LEVELS = {"perfect masks": None}
LEVELS.update({f"stripe patch {w} W": dg.Damage(stripe_highlight=w) for w in WIDTHS})
LEVELS.update({f"one stripe break {w} W": dg.Damage(stripe_breaks=(1, w)) for w in WIDTHS})
LEVELS.update({f"two stripe breaks {w} W": dg.Damage(stripe_breaks=(2, w)) for w in WIDTHS})
LEVELS.update({"white tables, bad day": dg.REALISTIC["white tables, bad day"], "medium": dg.SEVERITIES["medium"]})


def overlaps(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="start,start+cover")
    ap.add_argument("--out", default="stripe_before")
    args = ap.parse_args(argv)
    S.register()
    arms = C.arm_list(args.arms, ())
    out = S.OUT / args.out
    out.mkdir(parents=True, exist_ok=True)
    G = C.load("det_given_seg_run", C.SEG / "run.py")
    A.install()
    home = [s for s in G.train_sets()["HOME"] if io.mask_path(s).exists()]
    hand = {s: io.load_mask(io.mask_path(s)) for s in home}
    truth = {s: G.truth(s) for s in home}
    boxes = {s: [tuple(g.bbox) for g in truth[s][0]] for s in home}
    results = collections.defaultdict(list)
    causes = collections.defaultdict(collections.Counter)
    drawn = collections.defaultdict(collections.Counter)
    miss_rows, false_rows = [], []
    for level, d in LEVELS.items():
        for seed in ((-1,) if d is None else SEEDS):
            for i, s in enumerate(home):
                mask = hand[s] if d is None else dg.damage(hand[s], boxes[s], d, seed=1000 * seed + i)
                gts, clean = truth[s]
                for a in arms:
                    log: list = []
                    preds = det.detect(mask, A.ARMS[a], CAM, log=log)
                    res = ed.evaluate_frame(s, preds, gts, CAM, rule="v2", clean=clean)
                    results[(level, a)].append(res)
                    stem = s.replace("4A8B_window_light_", "")
                    for gi in res.unmatched_gt:
                        g = gts[gi]
                        cause, detail = G.att.attribute(g, preds, log, G.att.inside(mask, g))
                        causes[(level, a)][cause] += 1
                        notes = [f"{e['stage']}:{e['why']}{list(e['bbox'])}" for e in log if overlaps(e["bbox"], g.bbox) and e.get("body", g.color) == g.color]
                        miss_rows.append({"level": level, "arm": a, "stem": stem, "seed": seed, "color": dtp.COLOR_NAMES[g.color], "truth": list(g.bbox),
                                          "flags": "+".join(sorted(g.flags)), "cause": cause, "detail": detail, "log": " | ".join(notes)})
                    for pi in res.unmatched_pred:
                        p = preds[pi]
                        same = [(ed.box_iou(p.bbox, g.bbox), g) for g in gts if g.color == p.color]
                        iou, g = max(same, key=lambda t: t[0]) if same else (0.0, None)
                        by = C.drawn_by(log, p.bbox)
                        also = int(g is not None and any(gts[gi] is g for gi in res.unmatched_gt))
                        drawn[(level, a)][by + (" (misplaced box of a missed barrel)" if also and iou > 0.1 else "")] += 1
                        false_rows.append({"level": level, "arm": a, "stem": stem, "seed": seed, "color": dtp.COLOR_NAMES[p.color], "box": list(p.bbox),
                                           "flags": "+".join(sorted(p.flags)), "drawn_by": by, "best_overlap_same_color": round(iou, 2),
                                           "that_truth_box": list(g.bbox) if g is not None else "", "that_truth_also_missed": also})
    with (out / "stripe_levels.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["level", "arm", "barrels", "found", "missed", "false"])
        for (level, a), rs in results.items():
            c = rp.summarize(rs); w.writerow([level, a, c.barrels, c.found, c.missed, c.false])
    for name, rows in (("stripe_misses.csv", miss_rows), ("stripe_false.csv", false_rows)):
        if rows:
            with (out / name).open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    L = ["# A stripe cut through: one kind of damage at a time, found / barrels (false boxes)", "",
         "The 16 HOME hand masks (29 barrels), seeds 0 to 19 (580 barrels per level; the perfect masks once). v2 rule. Train frames only.", "",
         "| damage | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|" + "---|" * len(arms)]
    for level in LEVELS:
        cells = []
        for a in arms:
            c = rp.summarize(results[(level, a)]); cells.append(f"{c.found} / {c.barrels} ({c.false})")
        L.append(f"| {level} | " + " | ".join(cells) + " |")
    for a in arms:
        L += ["", f"## `{a}`: which test refused the missed barrels", ""]
        L += [f"- {level}: " + ", ".join(f"{k} {v}" for k, v in causes[(level, a)].most_common()) for level in LEVELS if causes[(level, a)]]
        L += ["", f"## `{a}`: which rule drew the false boxes", ""]
        L += [f"- {level}: " + ", ".join(f"{k} {v}" for k, v in drawn[(level, a)].most_common()) for level in LEVELS if drawn[(level, a)]]
    (out / "stripe.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
