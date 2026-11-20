#!/usr/bin/env python3
"""Report only (not an arm, nothing is chosen here): the stencil as a CHECKER of the rule detector's boxes.

For every box the rule detector draws, the stencil's score at that place (``stencil.box_score``), next to whether the
box is right. Then, for a list of veto levels: how many right boxes and how many wrong boxes a veto at that level
would remove. The pre-registered `veto` arm sits at the level read from the calibration (-0.01); this shows what a
stricter one would cost and buy.

Boxes scored:
  scorecard   the 3888 scenes of ``2026-11-19_det_occl`` (right = v2 match with the hidden barrel or a pasted front
              barrel; "no barrel there" = in the right place of no true barrel; the rest = on a barrel, box not right)
  frames      the train frames with box labels: HOME (color model, leave one scene out), CAMPUS, and report-only
              BLACK and WOOD (right = v2 match; wrong = no match)

Train frames only (asserted in the loaded script).

    python barrels/experiments/2026-11-20_stencil/veto_curve.py
Outputs: results/2026-11-20_stencil/veto_curve.md, veto_curve.csv
"""
from __future__ import annotations

import collections
import csv
import importlib.util
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
import stencil_arms as A  # noqa: E402
from barrels import detect_types as dtp, eval_det as ed, io, stencil as stn  # noqa: E402

LEVELS = (-0.01, 0.0, 0.05, 0.10, 0.15, 0.20)


def main() -> int:
    spec = importlib.util.spec_from_file_location("det_occl_run", HERE.parent / "2026-11-19_det_occl" / "run.py")
    R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
    R.occl_arms = types.SimpleNamespace(ARMS=A.ARMS, BASE=A.SOURCE_BASE)
    stems = R.train_stems()
    segs = R.segmentations(stems, with_extreme=True)
    pools, _ = R.build_sources(segs)
    rows = []

    def add(where, kind, mask, preds, truths):
        gts = [dtp.Barrel(color=c, bbox=tuple(b), source="gt") for c, b in truths if b[2] > b[0] and b[3] > b[1]]
        res = ed.evaluate_frame("x", preds, gts, R.CAM, rule="v2")
        place = set(R.right_place(preds, truths).values())
        for i, p in enumerate(preds):
            what = "right" if i not in res.unmatched_pred else ("on a barrel, box not right" if i in place else "no barrel there")
            s = stn.box_score(mask, p, A.STENCIL, R.CAM, others=[o for o in preds if o is not p])
            rows.append({"where": where, "kind": kind, "what": what, "color": dtp.COLOR_NAMES[p.color], "bbox": list(p.bbox), "score": round(max(s, -9.0), 4)})

    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            add("scorecard", f"{key} {amount}", sc.mask, A.RULES_DETECT(sc.mask, A.RULES_CFG, R.CAM), [sc.target] + list(sc.fronts))
    for name, pool in (("HOME", "HOME color model"), ("CAMPUS", "CAMPUS color model"), ("BLACK (report only)", "BLACK"), ("WOOD (report only)", "WOOD")):
        for stem, mask in sorted(segs[pool].items()):
            truths = [(g.color, g.bbox) for g in dtp.barrels_from_boxes(io.load_boxes(stem))]
            add(name, stem, mask, A.RULES_DETECT(mask, A.RULES_CFG, R.CAM), truths)
    with (A.OUT / "veto_curve.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    L = ["# The stencil as a checker of the rule detector's boxes (report only)", "",
         "Every box the rule detector draws gets the stencil's score at its place (the best stencil place overlapping the box by half or more, same "
         "color). A veto at level t removes the boxes scoring under t. Each cell: boxes removed of boxes drawn. The pre-registered `veto` arm is the "
         "first column (-0.01: the lowest score of a right box on the calibration masks, minus 0.05). Nothing here was used to choose anything.", "",
         "| boxes of the rule detector | " + " | ".join(f"veto {t}" for t in LEVELS) + " |", "|---|" + "---|" * len(LEVELS)]
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault((r["where"], r["what"]), []).append(r["score"])
    for (where, what), sc in groups.items():
        L.append(f"| {where}: {what} | " + " | ".join(f"{sum(1 for s in sc if s < t)} of {len(sc)}" for t in LEVELS) + " |")
    L += ["", "On the scorecard a \"right\" box is right for a barrel that is partly hidden in most scenes, which is where the stencil scores low.", ""]
    (A.OUT / "veto_curve.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
