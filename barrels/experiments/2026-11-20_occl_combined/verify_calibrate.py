#!/usr/bin/env python3
"""The verifier's limit, by the rule of PREREG.md ("The stencil as a verifier"). Opens HOME train frames and the
clutter negatives of the other tables only: no scorecard scene, no CAMPUS frame, no recording, no damaged mask.

  A1  the 16 HOME hand masks
  A2  the same frames, color model, leave one scene out (as the eval table)
  A4  the train negative frames of the other tables (wood `neg_02`, black `neg_01`), adopted color model

The rule detector (``--arm``, pinned; `combined` as registered, or the combination that became the default) is run on
each; every box gets the stencil's score at its place (``stencil.box_score``, the other boxes given). A box is right
when it matches a hand-drawn box under the v2 rule.

    limit  = (the lowest score among the right boxes of A1 and A2) - 0.02, rounded down to 0.01
    limit2 = the same over the right boxes that ``half_stripes`` did not make (arm ``<arm>+verify2``)

A score of -inf (no stencil place overlaps the box by half) is written as -9.

    python barrels/experiments/2026-11-20_occl_combined/verify_calibrate.py [--arm reduced+thin]
Outputs: results/2026-11-20_occl_combined/ verify_calibration[_<arm>].json, .md, _boxes.csv (no suffix for `combined`)
"""
from __future__ import annotations

import argparse
import csv
import json
import math

import common as C
from barrels import cv as bcv, detect_types as dtp, eval_det as ed, geometry as geo, io, pipeline as pl, splits, stencil as stn, worldmap_bridge as wb

A = C.A
CAM = geo.AIM_4A8B6118_BOXFIT
MARGIN = 0.02


def build_items() -> list[dict]:
    sp = splits.load_splits()
    test = set(sp["test"])
    train = [s for s in sorted(sp["train"]) if io.boxes_path(s).exists()]
    assert not set(train) & test, "a test frame leaked in"
    home = [s for s in train if s.startswith("4A8B_window_light_") and io.mask_path(s).exists()]
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    hand = {s: io.load_mask(io.mask_path(s)) for s in home}
    frames = {s: pl.Frame.from_image(io.load_image(io.find_image(s))) for s in home}
    items = [{"pool": "A1", "stem": s, "mask": hand[s]} for s in home]
    for fold in bcv.loso_folds(home, {s: io.parse_name(s)["scene"] for s in home}):
        fm = pl.fit([frames[s] for s in fold.train], [hand[s] for s in fold.train], model.cfg)
        items += [{"pool": "A2", "stem": s, "mask": pl.segment(frames[s], fm)[0]} for s in fold.held_out]
    for s in train:
        t = io.parse_name(s)
        if t["scene"] == "neg" and f"{t['light']}_{t['surface']}" not in ("window_light", "campus_light"):
            assert not io.load_boxes(s)["barrels"]
            items.append({"pool": "A4", "stem": s, "mask": pl.segment(pl.Frame.from_image(io.load_image(io.find_image(s))), model)[0]})
    return items


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", default="combined")
    args = ap.parse_args(argv)
    arm = args.arm
    C.OUT.mkdir(parents=True, exist_ok=True)
    out_json = A.cal_path(arm)
    cfg = A.rule_config(A.ARMS[arm])
    rows = []
    items = build_items()
    for it in items:
        log: list = []
        found = A.RULES_DETECT(it["mask"], cfg, CAM, log)
        gts = dtp.barrels_from_boxes(io.load_boxes(it["stem"]))
        res = ed.evaluate_frame(it["stem"], found, gts, CAM, rule="v2")
        for i, b in enumerate(found):
            s = stn.box_score(it["mask"], b, A.STENCIL, CAM, others=[o for o in found if o is not b])
            rows.append({"pool": it["pool"], "stem": it["stem"].replace("4A8B_", ""), "color": dtp.COLOR_NAMES[b.color], "bbox": list(b.bbox),
                         "flags": "+".join(sorted(b.flags)), "drawn_by": C.drawn_by(log, b.bbox), "right": int(i not in res.unmatched_pred),
                         "score": round(max(s, -9.0), 4)})
    with out_json.with_name(out_json.stem + "_boxes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    right = sorted((r for r in rows if r["right"] and r["pool"] in ("A1", "A2")), key=lambda r: r["score"])
    right2 = [r for r in right if r["drawn_by"] != C.STAGE_NAME["half"]]

    def limit_of(rs):
        return math.floor((rs[0]["score"] - MARGIN) * 100 + 1e-9) / 100

    limit, limit2 = limit_of(right), limit_of(right2)
    wrong = [r for r in rows if not r["right"]]
    out = {"git": bcv.git_hash(), "arm": arm, "margin": MARGIN, "limit": limit, "limit2": limit2,
           "masks": {p: sum(1 for it in items if it["pool"] == p) for p in ("A1", "A2", "A4")},
           "right_boxes": {p: sum(1 for r in rows if r["right"] and r["pool"] == p) for p in ("A1", "A2")},
           "right_boxes_made_by_half_stripes": len(right) - len(right2),
           "lowest_right": right[:8], "wrong_or_negative_boxes": wrong}
    out_json.write_text(json.dumps(out, indent=1) + "\n")
    L = ["# The verifier's limit (PREREG.md, \"The stencil as a verifier\")", "",
         f"git {out['git']}. Rule detector: arm `{arm}`. Masks: " + ", ".join(f"{p} {n}" for p, n in out["masks"].items()) +
         f". Right boxes: A1 {out['right_boxes']['A1']}, A2 {out['right_boxes']['A2']}; made by `half_stripes`: {out['right_boxes_made_by_half_stripes']}.", "",
         f"The lowest stencil score at a right box of A1 and A2 is {right[0]['score']:.3f}; **limit = that − {MARGIN} = {limit}** (rounded down to 0.01). "
         f"Without the boxes of `half_stripes`: lowest {right2[0]['score']:.3f}, **limit2 = {limit2}**.", "",
         "The eight lowest right boxes:", "", "| pool | frame | color | box | flags | drawn by | score |", "|---|---|---|---|---|---|---|"]
    L += [f"| {r['pool']} | {r['stem']} | {r['color']} | {r['bbox']} | {r['flags']} | {r['drawn_by']} | {r['score']:.3f} |" for r in right[:8]]
    L += ["", "Boxes that are not right (A1, A2), and every box on a negative frame (A4); they do not enter the limit:", ""]
    L += [f"- {r['pool']} {r['stem']} {r['color']} {r['bbox']} ({r['drawn_by']}): score {r['score']:.3f}" + (" → the verifier would drop it" if r["score"] < limit else " → kept") for r in wrong] or ["- none"]
    out_json.with_suffix(".md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
