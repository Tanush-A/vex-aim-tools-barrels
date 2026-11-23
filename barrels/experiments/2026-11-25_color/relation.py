#!/usr/bin/env python3
"""Step 3 (part 1) of the 2026-11-25 color work: with the slider-labelled places of today, does any feature of the
frame's own histogram predict the working RANGES (leave one PLACE out)? Run ``sweep.py`` first.

    python barrels/experiments/2026-11-25_color/relation.py

Unit: an ordinary slider-labelled condition (its range of a threshold = the intersection of its labelled frames'
one-at-a-time working ranges from the sweep; when empty, the median of the low ends to the median of the high ends).
Features (from the frame alone, no label; the condition's mean over its labelled frames): the nine ``hsrel``
features that need no reference, plus ``light_warmth`` (white patch: (R - B) / (R + G + B) of the brightest 5 % of the
frame), ``warmth`` (the same, median over all gated pixels), ``blue_top300`` (the S of the 300th most saturated
blue-window pixel), ``orange_peak150``.
Predictors, per held-out place, fit on the other places only: the fixed value; the place-weighted mean of the other
places' range midpoints; per feature a line through the CENTRE of the training places (mean feature, mean midpoint),
slope by place-weighted least squares on the midpoints; per feature the same line with the slope that puts the most
training conditions inside their ranges (``hsrange.interval_slope``, anchored at the centre). Right = inside the held-out
condition's range. Score per predictor = mean over places of the share of the place's conditions that are right.
Writes results/2026-11-25_color/relation.md and relation.csv.
"""
from __future__ import annotations

import csv
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import rules as rl  # noqa: E402

from barrels import hsrange as hx  # noqa: E402
from barrels import hsrel as hr  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

PARAMS = ("orange_h_lo", "orange_h_hi", "orange_s_lo", "blue_h_lo", "blue_h_hi", "blue_s_lo")
FIXED = rl.FIXED
FEATS = ("v_mean", "s_median", "s_share100", "blue_peak_h", "blue_s_p90", "orange_peak_h", "orange_s_p90",
         "light_warmth", "warmth", "blue_top300", "orange_peak150")


def frame_feats(stem: str) -> dict:
    bgr, _ = cm.load(stem)
    hist, vm = hr.gated_hist(bgr)
    f = hr.frame_features(hist, vm, None)
    fr = pl.Frame.from_image(bgr)
    f["light_warmth"] = rl.light_warmth(fr)
    f["warmth"] = rl.warmth(fr)
    f["blue_top300"] = rl.blue_top(fr)
    p = rl.orange_peak(fr)
    f["orange_peak150"] = float("nan") if p is None else p
    return {k: f[k] for k in FEATS}


def main() -> int:
    data = [json.loads(Path(p).read_text()) for p in sorted(glob.glob(str(cm.RESULTS / "sweep" / "*.json")))]
    data = [d for d in data if cm.class_of(d["condition"]) == "ordinary"]
    for d in data:
        cm.require_train(d["stem"])
    conds = defaultdict(list)
    for d in data:
        conds[d["condition"]].append(d)
    keys = sorted(conds)
    place = {k: cm.place_of(k) for k in keys}
    feats = {}
    for k in keys:
        fs = [frame_feats(d["stem"]) for d in conds[k]]
        feats[k] = {f: float(np.nanmean([x[f] for x in fs])) if np.isfinite([x[f] for x in fs]).any() else float("nan") for f in FEATS}
    rng = {}
    for k in keys:
        for p in PARAMS:
            lo, hi, empty = hx.intersect([tuple(d["ranges"][p]) for d in conds[k]])
            rng[(k, p)] = (lo, hi, empty)
    places = sorted(set(place.values()))
    rows = []
    L = ["# Does anything in the frame predict the working ranges? (leave one PLACE out; 2026-11-25, step 3)", "",
         f"`python barrels/experiments/2026-11-25_color/relation.py`. {len(keys)} ordinary slider-labelled conditions at "
         f"{len(places)} places ({', '.join(places)}); ranges from the sweep (detector version, around his values). "
         "Right = the prediction lies inside the held-out condition's range. Score = mean over places of the share of the "
         "place's conditions that are right. Lines are anchored at the centre of the training places, not at home.", "",
         "| threshold | fixed | mean of others | best feature (kind) | its score | features beating fixed AND the mean |", "|---|---:|---:|---|---:|---|"]
    for p in PARAMS:
        score = defaultdict(lambda: defaultdict(list))     # predictor -> place -> [right]
        for held in places:
            test = [k for k in keys if place[k] == held]
            train = [k for k in keys if place[k] != held]
            w = np.array([1.0 / sum(place[t] == place[k] for t in train) for k in train])
            mids = np.array([(rng[(k, p)][0] + rng[(k, p)][1]) / 2 for k in train])
            ranges = [rng[(k, p)][:2] for k in train]
            preds = {"fixed": lambda k: FIXED[p], "mean of others": lambda k, m=float(np.average(mids, weights=w)): m}
            for f in FEATS:
                x = np.array([feats[k][f] for k in train])
                ok = np.isfinite(x)
                if ok.sum() < 3 or np.ptp(x[ok]) == 0:
                    continue
                xc, yc = float(np.average(x[ok], weights=w[ok])), float(np.average(mids[ok], weights=w[ok]))
                dx = x[ok] - xc
                b_ls = float(np.sum(w[ok] * dx * (mids[ok] - yc)) / np.sum(w[ok] * dx * dx))
                b_iv, _ = hx.interval_slope(x[ok], [r for r, o in zip(ranges, ok) if o], yc, xc, 1e9, w[ok])
                for kind, b in (("line", b_ls), ("interval", b_iv)):
                    preds[f"{f} ({kind})"] = (lambda k, f=f, b=b, xc=xc, yc=yc: yc + b * (feats[k][f] - xc) if np.isfinite(feats[k][f]) else yc)
            for name, fn in preds.items():
                for k in test:
                    v = fn(k)
                    lo, hi, _ = rng[(k, p)]
                    right = lo <= v <= hi
                    score[name][held].append(right)
                    rows.append({"threshold": p, "held_place": held, "condition": k, "predictor": name, "pred": round(v, 2),
                                 "lo": lo, "hi": hi, "right": right})
        tot = {n: float(np.mean([np.mean(v) for v in per.values()])) for n, per in score.items() if len(per) == len(places)}
        feats_only = {n: s for n, s in tot.items() if n not in ("fixed", "mean of others")}
        best = max(feats_only, key=feats_only.get) if feats_only else "-"
        beat = [n for n, s in feats_only.items() if s > tot["fixed"] and s > tot["mean of others"]]
        L.append(f"| {p} | {tot['fixed']:.2f} | {tot['mean of others']:.2f} | {best} | {feats_only.get(best, float('nan')):.2f} | "
                 f"{', '.join(sorted(beat, key=lambda n: -tot[n])[:5]) or 'none'}{' ...' if len(beat) > 5 else ''} |")
    L += ["", "Each condition's range and features: `relation.csv` (one row per threshold x held-out condition x predictor).",
          "With 5 places a feature that 'beats' both baselines on one threshold is description, not proof: 11 features x 2 "
          "kinds = 22 tries per threshold, so a chance winner is expected.", ""]
    with open(cm.RESULTS / "relation.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    L += ["## The conditions (range of each threshold; features)", "", "| condition | place | " + " | ".join(PARAMS) + " | light_warmth | blue_top300 | orange_peak150 |",
          "|---|---|" + "---|" * (len(PARAMS) + 3)]
    for k in keys:
        L.append(f"| {k} | {place[k]} | " + " | ".join(f"{rng[(k, p)][0]:.0f}..{rng[(k, p)][1]:.0f}{'*' if rng[(k, p)][2] else ''}" for p in PARAMS)
                 + f" | {feats[k]['light_warmth']:.2f} | {feats[k]['blue_top300']:.0f} | {feats[k]['orange_peak150']:.0f} |")
    L += ["", "\\* = the frames' ranges do not overlap (median of the ends shown)."]
    (cm.RESULTS / "relation.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
