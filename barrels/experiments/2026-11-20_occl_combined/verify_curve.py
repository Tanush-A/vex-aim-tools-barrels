#!/usr/bin/env python3
"""REPORT ONLY (nothing is chosen here, and nothing here may be used to choose the verifier's limit: that limit is
fixed by ``verify_calibrate.py``). For every box the rule detector (arm ``combined``) draws, the stencil's score at
its place, next to whether the box is right; then, for a list of limits, how many right and how many wrong boxes a
verifier at that limit would drop. It answers "was the calibrated limit unlucky, or is there no good limit?".

Boxes scored:
  scorecard   the 3888 scenes (right = v2 match with the hidden barrel or a pasted front barrel; "no barrel there" =
              in the right place of no true barrel; the rest = on a barrel, box not right)
  frames      the train frames with box labels: HOME (color model, leave one scene out), CAMPUS, and report-only
              BLACK and WOOD (right = v2 match; wrong = no match)

Train frames only (asserted in the loaded script).

    python barrels/experiments/2026-11-20_occl_combined/verify_curve.py
Outputs: results/2026-11-20_occl_combined/verify/ verify_curve.md, verify_curve.csv
"""
from __future__ import annotations

import collections
import csv
import sys
import types

import common as C
from barrels import detect_types as dtp, eval_det as ed, io

A = C.A
ARM = "combined"
LIMITS = (0.0, 0.02, 0.05, 0.08, 0.10, 0.13, 0.16, 0.20)


def main() -> int:
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS=A.ARMS, BASE=A.SOURCE_BASE)
    stems = R.train_stems()
    segs = R.segmentations(stems, with_extreme=True)
    pools, _ = R.build_sources(segs)
    cfg = A.ARMS[ARM]
    rows = []

    def add(where, kind, mask, truths):
        log: list = []
        scored = A.checked_scores(mask, cfg, R.CAM, log)
        preds = [b for b, _ in scored]
        gts = [dtp.Barrel(color=c, bbox=tuple(b), source="gt") for c, b in truths if b[2] > b[0] and b[3] > b[1]]
        res = ed.evaluate_frame("x", preds, gts, R.CAM, rule="v2")
        place = set(R.right_place(preds, truths).values())
        for i, (p, s) in enumerate(scored):
            what = "right" if i not in res.unmatched_pred else ("on a barrel, box not right" if i in place else "no barrel there")
            rows.append({"where": where, "kind": kind, "what": what, "color": dtp.COLOR_NAMES[p.color], "bbox": list(p.bbox),
                         "drawn_by": C.drawn_by(log, p.bbox), "score": round(max(s, -9.0), 4)})

    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            add("scorecard", f"{key} {amount}", sc.mask, [sc.target] + list(sc.fronts))
    for name, pool in (("HOME", "HOME color model"), ("CAMPUS", "CAMPUS color model"), ("BLACK (report only)", "BLACK"), ("WOOD (report only)", "WOOD")):
        for stem, mask in sorted(segs[pool].items()):
            add(name, stem, mask, [(g.color, g.bbox) for g in dtp.barrels_from_boxes(io.load_boxes(stem))])
    out = C.OUT / "verify"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "verify_curve.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    L = ["# The stencil as a checker of the `combined` detector's boxes: every limit (REPORT ONLY)", "",
         "Every box `combined` draws gets the stencil's score at its place. A verifier at limit t drops the boxes scoring under t. Each cell: boxes "
         f"dropped of boxes drawn. The registered limit is {A.VERIFY} (`verify_calibration.md`); the other columns were not used to choose anything and "
         "may not be: they show what a different limit would have cost and bought.", "",
         "| boxes of `combined` | " + " | ".join(f"limit {t}" for t in LIMITS) + " |", "|---|" + "---|" * len(LIMITS)]
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault((r["where"], r["what"]), []).append(r["score"])
    for (where, what), sc in groups.items():
        L.append(f"| {where}: {what} | " + " | ".join(f"{sum(1 for s in sc if s < t)} of {len(sc)}" for t in LIMITS) + " |")
    L += ["", "## The scorecard's right boxes a verifier would drop, by the rule that drew them", "",
          "| drawn by | boxes | " + " | ".join(f"limit {t}" for t in LIMITS) + " |", "|---|---|" + "---|" * len(LIMITS)]
    by = collections.OrderedDict()
    for r in rows:
        if r["where"] == "scorecard" and r["what"] == "right":
            by.setdefault(r["drawn_by"], []).append(r["score"])
    for k, sc in by.items():
        L.append(f"| {k} | {len(sc)} | " + " | ".join(str(sum(1 for s in sc if s < t)) for t in LIMITS) + " |")
    L += ["", "## The scorecard's boxes where no barrel is, by the rule that drew them", "",
          "| drawn by | boxes | " + " | ".join(f"limit {t}" for t in LIMITS) + " |", "|---|---|" + "---|" * len(LIMITS)]
    by = collections.OrderedDict()
    for r in rows:
        if r["where"] == "scorecard" and r["what"] == "no barrel there":
            by.setdefault(r["drawn_by"], []).append(r["score"])
    for k, sc in by.items():
        L.append(f"| {k} | {len(sc)} | " + " | ".join(str(sum(1 for s in sc if s < t)) for t in LIMITS) + " |")
    low = sorted((r for r in rows if r["what"] == "right" and r["where"] in ("HOME", "CAMPUS")), key=lambda r: r["score"])[:8]
    L += ["", "The eight lowest right boxes on HOME (leave one scene out) and CAMPUS:", ""]
    L += [f"- {r['score']:.3f}  {r['where']} {r['kind'].replace('4A8B_', '')} {r['color']} {r['bbox']} ({r['drawn_by']})" for r in low]
    (out / "verify_curve.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
