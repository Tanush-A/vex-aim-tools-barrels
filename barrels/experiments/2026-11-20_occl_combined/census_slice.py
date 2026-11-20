#!/usr/bin/env python3
"""REPORT ONLY, a lead for a later experiment (nothing here changes the detector or the verdict): what do the boxes
of ``slices_behind`` have in common when they are wrong?

``slice_behind`` boxes a narrow full slice when exactly one of its sides is hidden by the frame edge or by a found
barrel "standing nearer" (its box reaches lower than the bottom the slice's row predicts). On damaged masks it draws
boxes on the wrong side of a slice (PREREG addendum). For every box it draws, with arm ``combined``:

  where    the 3888 scorecard scenes; the damaged HOME masks of ``run_levels.py`` (seeds 0 to 19)
  right    scorecard: in the right place of a true barrel; damaged masks: a v2 match
  reason   the frame edge, or a found barrel; for a barrel: how far its bottom lies below the slice's predicted bottom
           (px, and as a share of the barrel height H the slice's row gives), and how wide the hiding box is next to
           what the slice's row predicts

    python barrels/experiments/2026-11-20_occl_combined/census_slice.py
Output: results/2026-11-20_occl_combined/census_slice.md, census_slice.csv
"""
from __future__ import annotations

import csv
import dataclasses
import sys
import types

import numpy as np

import common as C
from barrels import degrade as dg, detect_types as dtp, eval_det as ed, geometry as geo, io

A = C.A
CAM = geo.AIM_4A8B6118_BOXFIT
ARM = "combined"
BINS = (0.0, 0.05, 0.10, 0.15, 0.25, 0.5, 9.0)


def slice_rows(mask, cfg, where, kind, is_right):
    """One row per box of slices_behind on this mask. ``is_right(index, preds)`` says whether the box is right."""
    log: list = []
    preds = A.RULES_DETECT(mask, cfg, CAM, log)
    h, w = mask.shape
    rows = []
    for e in log:
        if e.get("stage") != "slice" or e.get("why") != "kept":
            continue
        box = tuple(e["box"])
        i = next((k for k, p in enumerate(preds) if tuple(p.bbox) == box), None)
        if i is None:
            continue
        sx0, sx1 = e["seen"]
        row = (e["bbox"][1] + e["bbox"][3]) // 2
        left = e["hidden_side"] == "left"
        H = e["predicted_bottom"] - e["predicted_top"]
        at_frame = (sx0 <= 0) if left else (sx1 >= w)
        px = range(sx0 - 3, sx0) if left else range(sx1, sx1 + 3)
        hiders = [p for k, p in enumerate(preds) if k != i and p.bbox[3] > e["predicted_bottom"] and p.bbox[1] <= row < p.bbox[3]
                  and any(p.bbox[0] <= x < p.bbox[2] for x in px)]
        margin = max((p.bbox[3] - e["predicted_bottom"] for p in hiders), default=float("nan"))
        rows.append({"where": where, "kind": kind, "right": int(is_right(i, preds)), "reason": "frame edge" if at_frame else ("found barrel" if hiders else "?"),
                     "color": dtp.COLOR_NAMES[preds[i].color], "box": list(box), "slice_w_over_W": round((sx1 - sx0) / e["expected_w"], 2),
                     "nearer_by_px": "" if at_frame or not hiders else round(margin, 1), "nearer_by_H": "" if at_frame or not hiders else round(margin / H, 3)})
    return rows


def main() -> int:
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS=A.ARMS, BASE=A.SOURCE_BASE)
    G = C.load("det_given_seg_run", C.SEG / "run.py")
    cfg = A.rule_config(A.ARMS[ARM])
    rows = []
    pools, _ = R.build_sources(R.segmentations(R.train_stems()))
    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            truths = [sc.target] + list(sc.fronts)
            rows += slice_rows(sc.mask, cfg, "scorecard", f"{key} {amount}", lambda i, preds, t=truths: i in set(R.right_place(preds, t).values()))
    home = [s for s in G.train_sets()["HOME"] if io.mask_path(s).exists()]
    bad = dg.REALISTIC["white tables, bad day"]
    levels = {"white tables, typical": dg.REALISTIC["white tables, typical"], "white tables, bad day": bad,
              "bad day without the stripe patch": dataclasses.replace(bad, stripe_highlight=dg.Damage().stripe_highlight),
              "light": dg.SEVERITIES["light"], "medium": dg.SEVERITIES["medium"], **dg.WORST_SEEN}
    for level, d in levels.items():
        for seed in range(20):
            for i, s in enumerate(home):
                gts, clean = G.truth(s)
                mask = dg.damage(io.load_mask(io.mask_path(s)), [tuple(g.bbox) for g in gts], d, seed=1000 * seed + i)

                def right(k, preds, s=s, gts=gts, clean=clean):
                    return k not in ed.evaluate_frame(s, preds, gts, CAM, rule="v2", clean=clean).unmatched_pred
                rows += slice_rows(mask, cfg, "damaged masks", level, right)
    with (C.OUT / "census_slice.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    def n(where, right, reason=None, lo=None, hi=None):
        out = 0
        for r in rows:
            if r["where"] != where or r["right"] != right or (reason and r["reason"] != reason):
                continue
            if lo is not None and (r["nearer_by_H"] == "" or not (lo <= r["nearer_by_H"] < hi)):
                continue
            out += 1
        return out

    L = ["# The boxes of `slices_behind`: what the wrong ones have in common (REPORT ONLY, a lead)", "",
         f"Arm `{ARM}`. Scorecard: 3888 scenes, a box is right when it is in the right place of a true barrel. Damaged masks: the 16 HOME hand masks at "
         "typical, bad day, bad day without the stripe patch, light, medium and worst seen, seeds 0 to 19 (1920 masks); a box is right when it matches a "
         "hand-drawn box (v2). Nothing here was used to decide anything.", "",
         "| boxes of `slices_behind` | scorecard: right | scorecard: wrong | damaged masks: right | damaged masks: wrong |", "|---|---|---|---|---|",
         "| all | " + " | ".join(str(n(w_, r_)) for w_ in ("scorecard", "damaged masks") for r_ in (1, 0)) + " |",
         "| hidden side = the frame edge | " + " | ".join(str(n(w_, r_, "frame edge")) for w_ in ("scorecard", "damaged masks") for r_ in (1, 0)) + " |",
         "| hidden side = a found barrel | " + " | ".join(str(n(w_, r_, "found barrel")) for w_ in ("scorecard", "damaged masks") for r_ in (1, 0)) + " |"]
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        L.append(f"| ... whose bottom is {lo:g} to {hi:g} H below the slice's predicted bottom | " +
                 " | ".join(str(n(w_, r_, "found barrel", lo, hi)) for w_ in ("scorecard", "damaged masks") for r_ in (1, 0)) + " |")
    by_level = {}
    for r in rows:
        if r["where"] == "damaged masks":
            by_level.setdefault(r["kind"], [0, 0])[1 - r["right"]] += 1
    L += ["", "Damaged masks, by level (right / wrong): " + "; ".join(f"{k}: {v[0]} / {v[1]}" for k, v in by_level.items()) + ".", "",
          "Every wrong box on the damaged masks:", "", "| level | color | box | hidden side | slice width / W | the hiding barrel's bottom below the predicted one (px; share of H) |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["where"] == "damaged masks" and not r["right"]:
            L.append(f"| {r['kind']} | {r['color']} | {r['box']} | {r['reason']} | {r['slice_w_over_W']} | {r['nearer_by_px']}; {r['nearer_by_H']} |")
    vals = [r["nearer_by_H"] for r in rows if r["where"] == "scorecard" and r["right"] and r["nearer_by_H"] != ""]
    if vals:
        L += ["", f"Scorecard, right boxes hidden by a found barrel: its bottom is below the predicted one by a median {np.median(vals):.2f} H "
              f"(10th percentile {np.percentile(vals, 10):.2f}, lowest {min(vals):.2f})."]
    (C.OUT / "census_slice.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
