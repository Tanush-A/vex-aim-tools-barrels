#!/usr/bin/env python3
"""Detection floor: the connected-components reference detector (NOT v2) scored with the detection
eval under the same leave-one-scene-out folds as v1.

    python barrels/experiments/2026-10-28_det_baseline/run.py --name det_baseline [--cam 4a8b] [--allow-unreviewed]

Arms:
  A  ground-truth class mask -> CC -> boxes       (what not splitting touching barrels costs, with perfect pixels)
  B  v1 LOSO-CV predicted mask -> CC -> boxes      (the real floor v2 must beat)
Ground truth = per-barrel instances (data/labels/<stem>_inst.*). Refuses to run on instance files
that have not been reviewed in the instance tool unless --allow-unreviewed (then the results are
labeled PROVISIONAL). Test and measured splits untouched. Writes <stem>_det.json per arm so
tools/eval_boxes.py can re-score them.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE.parent / "2026-10-20_v1_rgbbox"))
from barrels import cv, detect_cc, detect_types as dtp, eval_det as ed, geometry as geo, io, pipeline as pl  # noqa: E402
from run import load_pool  # noqa: E402

V1_FINAL = io.PKG_ROOT / "results" / "2026-10-20_v1_adaptive_cv" / "configs" / "afd85483.json"
CAMS = {"nominal": geo.NOMINAL, "4a8b": geo.AIM_4A8B6118}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default="det_baseline")
    ap.add_argument("--config", type=Path, default=V1_FINAL)
    ap.add_argument("--cam", choices=sorted(CAMS), default="4a8b")
    ap.add_argument("--allow-unreviewed", action="store_true")
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)
    cam = CAMS[args.cam]
    cfg = pl.Config.from_dict(json.load(args.config.open()))
    ds = load_pool(); folds = cv.loso_folds(ds.stems, ds.scene)

    gts, unreviewed = {}, []
    for s in ds.stems:
        inst, meta = io.load_instances(s)
        if not meta.get("reviewed"):
            unreviewed.append(s)
        gts[s] = dtp.barrels_from_instances(inst, meta, ds.masks[s], cam=cam)
    provisional = bool(unreviewed)
    if provisional and not args.allow_unreviewed:
        print(f"REFUSING: {len(unreviewed)} instance file(s) not reviewed: {unreviewed}. Review in tools/instance_tool.py or pass --allow-unreviewed.")
        return 2

    res = cv.cross_validate(ds, cfg, folds)                      # arm B's masks, one prediction per pool frame
    out = cv.fresh_dir(args.out / (f"{dt.date.today().isoformat()}_{args.name}" + ("_PROVISIONAL" if provisional else "")))
    lines = [f"# {args.name}: connected-components reference detector (BASELINE, not v2){' — PROVISIONAL: instances not yet reviewed' if provisional else ''}", "",
             f"v1 config `{cfg.short_hash()}`, camera `{args.cam}` (f {cam.f:g}, tilt {cam.tilt_deg:g}°), {len(ds.stems)} pool frames, LOSO folds; test/measured untouched.", ""]
    arms = {"A_gtmask_cc": {s: detect_cc.detect(ds.masks[s], cam=cam) for s in ds.stems},
            "B_v1mask_cc": {s: detect_cc.detect(res.preds[s], cam=cam) for s in ds.stems}}
    scores = {}
    for arm, preds in arms.items():
        results = [ed.evaluate_frame(s, preds[s], gts[s], cam) for s in ds.stems]
        sub = out / arm
        md, _, _ = ed.write_results(results, sub, title=f"{arm}")
        for s in ds.stems:
            detect_cc.write_detections(sub / "det", s, preds[s])
        scores[arm] = ed.score(results, ds.scene)
        lines += [f"## {arm}", "", md.read_text().split("\n", 3)[3]]
    lines += ["## Scores (in-scope frames; primary = mean strict F1)", "", "| arm | primary | F1 o / b | loose F1 o / b | mean IoU | bottom err median px | ground proj median mm | neg false det | color conf |", "|---|---|---|---|---|---|---|---|---|"]
    for arm, sc in scores.items():
        lines.append(f"| {arm} | {sc['primary']:.3f} | {sc['F1_o']:.3f} / {sc['F1_b']:.3f} | {sc['F1loose_o']:.3f} / {sc['F1loose_b']:.3f} | {sc['mean_iou']:.3f} | {sc['bottom_err_median_px']:.1f} | {sc['ground_proj_median_mm']:.1f} | {sc['neg_false_detections']} | {sc['color_confusions']} |")
    # geometry sensitivity of the projected ground error (arm B)
    lines += ["", "## Geometry sensitivity (arm B, projected ground error, matched pairs)", "", "| camera | f | tilt | ground err median / p90 mm |", "|---|---|---|---|"]
    for name, c in [("nominal", geo.NOMINAL), ("4a8b", geo.AIM_4A8B6118)] + [(f"corner{i}", c) for i, c in enumerate(geo.range_corners())]:
        g2 = {s: dtp.barrels_from_instances(*io.load_instances(s), ds.masks[s], cam=c) for s in ds.stems}
        rr = [ed.evaluate_frame(s, [b.with_ground(c) for b in arms["B_v1mask_cc"][s]], g2[s], c) for s in ds.stems]
        a = ed.aggregate(rr)["ALL"]
        st = ed._stats(a.ground_proj)
        lines.append(f"| {name} | {c.f:g} | {c.tilt_deg:g} | {st['median']:.1f} / {st['p90']:.1f} |")
    json.dump({"config": cfg.to_dict(), "cam": args.cam, "git": cv.git_hash(), "provisional": provisional, "unreviewed": unreviewed, "scores": scores},
              (out / "config.json").open("w"), indent=1, default=float)
    (out / "summary.md").write_text("\n".join(lines) + "\n"); print("\n".join(lines)); print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
