#!/usr/bin/env python3
"""Score predicted barrels against the per-barrel ground truth (docs/EVAL.md, detection metrics).

    python barrels/tools/eval_boxes.py --pred DIR --split test --name det_x [--cam 4a8b] [--sheets]
    python barrels/tools/eval_boxes.py --pred-masks DIR --split train --name det_cc_gt      # masks -> CC detector first

Predictions: <stem>_det.json (a list of Barrel dicts) in --pred, or class masks in --pred-masks run
through the connected-components reference detector. Ground truth: data/labels/<stem>_inst.{png,json}.
Frames without instances are skipped and listed. Writes results/<date>_<name>/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import cv, detect_types as dtp, eval_det as ed, geometry as geo, io, splits  # noqa: E402

CAMS = {"nominal": geo.NOMINAL, "4a8b": geo.AIM_4A8B6118}


def load_gt(stem: str, labels_dir: Path, cam: geo.CameraModel) -> list[dtp.Barrel] | None:
    try:
        inst, meta = io.load_instances(stem, labels_dir)
    except FileNotFoundError:
        return None
    mask = io.load_mask(labels_dir / f"{stem}_mask.png")
    return dtp.barrels_from_instances(inst, meta, mask, cam=cam)


def draw_sheet(img, preds: list[dtp.Barrel], gts: list[dtp.Barrel], matched_pred: set[int]):
    out = img.copy()
    for g in gts:
        x0, y0, x1, y1 = g.bbox
        cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
    for i, p in enumerate(preds):
        x0, y0, x1, y1 = p.bbox
        col = (0, 128, 255) if p.color == io.ORANGE else (255, 100, 0)
        if i in matched_pred:
            cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), col, 2)
        else:
            for x in range(x0, x1, 6):
                cv2.line(out, (x, y0), (min(x + 3, x1 - 1), y0), col, 2); cv2.line(out, (x, y1 - 1), (min(x + 3, x1 - 1), y1 - 1), col, 2)
            for y in range(y0, y1, 6):
                cv2.line(out, (x0, y), (x0, min(y + 3, y1 - 1)), col, 2); cv2.line(out, (x1 - 1, y), (x1 - 1, min(y + 3, y1 - 1)), col, 2)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pred", type=Path, help="folder of <stem>_det.json")
    g.add_argument("--pred-masks", type=Path, help="folder of predicted class masks (<stem>_pred.png or <stem>_mask.png)")
    ap.add_argument("--split", default="test", choices=(*splits.SPLIT_NAMES, "all"))
    ap.add_argument("--name", required=True)
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR)
    ap.add_argument("--cam", choices=sorted(CAMS), default="4a8b")
    ap.add_argument("--iou", type=float, default=ed.IOU_THR)
    ap.add_argument("--sheets", action="store_true")
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)
    cam = CAMS[args.cam]
    sp = splits.load_splits()
    stems = sorted({x for v in sp.values() for x in v}) if args.split == "all" else sorted(sp.get(args.split, []))
    results, skipped = [], []
    out_dir = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    if args.sheets:
        (out_dir / "sheets").mkdir()
    for stem in stems:
        gts = load_gt(stem, args.labels, cam)
        if gts is None:
            skipped.append(stem); continue
        if args.pred is not None:
            pj = args.pred / f"{stem}_det.json"
            if not pj.exists():
                skipped.append(stem); continue
            preds = [dtp.Barrel.from_dict(d) for d in json.load(pj.open())]
        else:
            from barrels import detect_cc
            pm = next((p for p in (args.pred_masks / f"{stem}_pred.png", args.pred_masks / f"{stem}_mask.png") if p.exists()), None)
            if pm is None:
                skipped.append(stem); continue
            preds = detect_cc.detect(io.load_mask(pm), cam=cam)
        r = ed.evaluate_frame(stem, preds, gts, cam, iou_thr=args.iou)
        results.append(r)
        if args.sheets:
            img = io.load_image(next(p for p in args.raw.glob(f"{stem}.*") if p.suffix.lower() in io.IMAGE_SUFFIXES))
            cv2.imwrite(str(out_dir / "sheets" / f"{stem}.png"), draw_sheet(img, preds, gts, {m.pred_idx for m in r.matches}))
    if skipped:
        print(f"skipped {len(skipped)} (no instances / no prediction): {skipped}")
    if not results:
        print("nothing to evaluate"); return 1
    md, _, _ = ed.write_results(results, out_dir, title=f"{args.name} on {args.split} ({len(results)} frames, cam {args.cam})")
    json.dump({"cam": args.cam, "iou": args.iou, "split": args.split, "git": cv.git_hash(), "pred": str(args.pred or args.pred_masks)}, (out_dir / "config.json").open("w"), indent=1)
    print(md.read_text()); print("written to", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
