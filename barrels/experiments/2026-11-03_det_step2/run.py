#!/usr/bin/env python3
"""Detector step 2 (the stripe anchor) vs step 1 vs the CC floor, on the 16 train frames, against Tanush's
reviewed box labels (EXPERIMENTS.md 2026-11-03).

Hypothesis: anchoring on the stripe recovers the barrels step 1 lost to same-color occlusion (occl_01/02,
cluster_01) and removes the hand's false boxes, without losing the touching rows step 1 already splits.

All arms use the same pixels (frozen v1 model afd85483 on each frame) and the same camera (AIM_4A8B6118_BOXFIT).
Ground truth = <stem>_boxes.json (Tanush, 2026-11-03). Scored with eval_det under the rule given by --rule
(v1 = IoU >= 0.5 with VOC-style ignores; v2 = EVAL.md's box rule, when available). No test frames.

    python barrels/experiments/2026-11-03_det_step2/run.py [--rule v1|v2]
"""
from __future__ import annotations

import argparse
import dataclasses
import inspect
import json
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import cv, detect_cc, detector as det, detect_types as dtp, eval_det as ed, geometry as geo, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402

MODEL = io.PKG_ROOT / "results" / "2026-10-20_v1_test_adaptive" / "config.json"
OUT = io.PKG_ROOT / "results" / "2026-11-03_det_step2"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rule", default="v1", choices=("v1", "v2"))
    ap.add_argument("--split", default="train")
    args = ap.parse_args(argv)
    cam = geo.AIM_4A8B6118_BOXFIT
    hook = wb.BarrelDetectorHook.load(MODEL, cam=cam)
    stems = sorted(splits.load_splits()[args.split])
    out = cv.fresh_dir(OUT.with_name(OUT.name + (f"_{args.split}" if args.split != "train" else "") + (f"_{args.rule}" if args.rule != "v1" else "")))
    for d in ("sheets", "det_cc", "det_step1", "det_step2"):
        (out / d).mkdir()
    cfg1 = dataclasses.replace(det.DetConfig(), require_stripe=False)
    cfg2 = dataclasses.replace(det.DetConfig(), require_stripe=True)
    res = {"cc": [], "step1": [], "step2": []}
    scenes = {}
    extra = {"rule": args.rule} if "rule" in inspect.signature(ed.evaluate_frame).parameters else {}
    for stem in stems:
        img = io.load_image(io.find_image(stem))
        mask, _ = pl.segment(pl.Frame.from_image(img), hook.model)
        label = io.load_boxes(stem)
        gts = [b.with_ground(cam) for b in dtp.barrels_from_boxes(label)]
        preds = {"cc": detect_cc.detect(mask, cam=cam), "step1": det.detect(mask, cfg1, cam), "step2": det.detect(mask, cfg2, cam)}
        scenes[stem] = io.parse_name(stem)["scene"]
        kw = dict(extra)
        if extra and "clean" in inspect.signature(ed.evaluate_frame).parameters:
            kw["clean"] = label.get("clean", True)
        for arm, p in preds.items():
            detect_cc.write_detections(out / f"det_{arm}", stem, p)
            res[arm].append(ed.evaluate_frame(stem, p, gts, cam, **kw))
        sheet = det.draw(img, preds["step2"])
        for g in gts:
            x0, y0, x1, y1 = g.bbox
            cv2.rectangle(sheet, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        for s in det.find_stripes(mask, cam, cfg2):
            x0, y0, x1, y1 = s.bbox
            cv2.rectangle(sheet, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 1)          # magenta = the stripes found
        cv2.imwrite(str(out / "sheets" / f"{stem}.png"), sheet)
    summary = {}
    for arm in res:
        ed.write_results(res[arm], out / arm, title=f"{arm} on {args.split} ({len(stems)} frames, boxfit camera, rule {args.rule})")
        summary[arm] = ed.score(res[arm], scenes, out_scope=())
    json.dump({"model": str(MODEL), "cam": "AIM_4A8B6118_BOXFIT", "cfg": cfg2.to_dict(), "split": args.split, "rule": args.rule,
               "gt": "boxes", "git": cv.git_hash(), "summary": summary}, (out / "config.json").open("w"), indent=1)
    print(f"rule {args.rule}, {args.split} ({len(stems)} frames), GT = Tanush's boxes")
    print(f"{'arm':6} {'primary':>8} {'F1_o':>6} {'F1_b':>6} {'IoU':>6} {'bottom err px':>14} {'neg FD':>7} {'disq':>5}")
    for arm, s in summary.items():
        print(f"{arm:6} {s['primary']:8.3f} {s['F1_o']:6.3f} {s['F1_b']:6.3f} {s['mean_iou']:6.3f} {s['bottom_err_median_px']:14.1f} {s['neg_false_detections']:7d} {str(s['disqualified']):>5}")
    print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
