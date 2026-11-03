#!/usr/bin/env python3
"""Detector step 1 vs the CC floor, on the 16 train frames, provisional (EXPERIMENTS.md 2026-11-03).

Hypothesis: counting barrels by the expected width and filling hidden bottoms from the top row lifts
detection F1 well above the connected-components floor on the same masks, because the floor's losses were
merged touching barrels and shadow-shortened boxes, not misplaced edges.

Both arms use the same pixels: the frozen v1 model afd85483 run on each train frame (it was fit on these
frames, so pixel quality is optimistic for both; the comparison between arms is fair). Ground truth = the
per-barrel instances (IoU >= 0.5 rule, VOC-style ignores for occluded/truncated/top_only, as eval_det does
today; the v2 box rule comes with M2). No test frames are touched.

    python barrels/experiments/2026-11-03_det_step1/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import cv, detect_cc, detector as det, detect_types as dtp, eval_det as ed, geometry as geo, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402

MODEL = io.PKG_ROOT / "results" / "2026-10-20_v1_test_adaptive" / "config.json"
OUT = io.PKG_ROOT / "results" / "2026-11-03_det_step1"


def main() -> int:
    cam = geo.AIM_4A8B6118_BOXFIT          # provisional camera (experiments/2026-11-03_geo_boxfit)
    hook = wb.BarrelDetectorHook.load(MODEL, cam=cam)
    stems = sorted(splits.load_splits()["train"])
    out = cv.fresh_dir(OUT)
    (out / "sheets").mkdir(); (out / "det_step1").mkdir(); (out / "det_cc").mkdir()
    res = {"cc": [], "step1": []}
    scenes = {}
    for stem in stems:
        img = io.load_image(io.find_image(stem))
        mask, _ = pl.segment(pl.Frame.from_image(img), hook.model)
        inst, meta = io.load_instances(stem)
        gts = dtp.barrels_from_instances(inst, meta, io.load_mask(io.LABELS_DIR / f"{stem}_mask.png"), cam=cam)
        preds = {"cc": detect_cc.detect(mask, cam=cam), "step1": det.detect(mask, cam=cam)}
        scenes[stem] = io.parse_name(stem)["scene"]
        for arm, p in preds.items():
            detect_cc.write_detections(out / f"det_{arm}", stem, p)
            res[arm].append(ed.evaluate_frame(stem, p, gts, cam))
        sheet = det.draw(img, preds["step1"])
        for g in gts:                                                 # ground truth in thin white
            x0, y0, x1, y1 = g.bbox
            cv2.rectangle(sheet, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        cv2.imwrite(str(out / "sheets" / f"{stem}.png"), sheet)
    summary = {}
    for arm in res:
        ed.write_results(res[arm], out / arm, title=f"{arm} on train (16 frames, 4A8B boxfit camera)")
        summary[arm] = ed.score(res[arm], scenes)
    json.dump({"model": str(MODEL), "cam": "AIM_4A8B6118_BOXFIT", "cfg": det.DetConfig().to_dict(), "split": "train", "git": cv.git_hash(), "summary": summary},
              (out / "config.json").open("w"), indent=1)
    print(f"{'arm':6} {'primary':>8} {'F1_o':>6} {'F1_b':>6} {'IoU':>6} {'bottom err px':>14} {'neg FD':>7}")
    for arm, s in summary.items():
        print(f"{arm:6} {s['primary']:8.3f} {s['F1_o']:6.3f} {s['F1_b']:6.3f} {s['mean_iou']:6.3f} {s['bottom_err_median_px']:14.1f} {s['neg_false_detections']:7d}")
    print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
