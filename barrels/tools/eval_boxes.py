#!/usr/bin/env python3
"""Score predicted barrels against the per-barrel ground truth (docs/EVAL.md, detection metrics).

    python barrels/tools/eval_boxes.py --pred DIR --split test --name det_x [--cam 4a8b] [--sheets]
    python barrels/tools/eval_boxes.py --pred-masks DIR --split train --name det_cc_gt      # masks -> CC detector first
    python barrels/tools/eval_boxes.py --pred DIR --stems filter:DAVE_ --gt-boxes --name dave   # v2 box labels as truth, frames by name
    python barrels/tools/eval_boxes.py --pred DIR --split train --gt-boxes --rule v2 --name det_v2  # EVAL.md v2 rule (bottom edge, no ignores)

Predictions: <stem>_det.json (a list of Barrel dicts) in --pred, or class masks in --pred-masks run
through the connected-components reference detector. Ground truth: data/labels/<stem>_inst.{png,json}, or
with --gt-boxes the v2 box labels <stem>_boxes.json (whose ``clean`` flag feeds the v2 disqualification).
--rule picks the eval_det rule (v1 = IoU + VOC ignores, the default; v2 = EVAL.md 2026-11-02).
Frames without ground truth / prediction are skipped and listed. Writes results/<date>_<name>/.
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


def load_gt(stem: str, labels_dir: Path, cam: geo.CameraModel, boxes: bool = False) -> tuple[list[dtp.Barrel], bool] | None:
    """(ground truth, clean): from <stem>_boxes.json (v2 box labels, ``clean`` as labeled, default true) when
    ``boxes``, else from the v1.5 instances (clean = true). None when there is no label."""
    try:
        if boxes:
            label = io.load_boxes(stem, labels_dir, check_image=False)
            return [b.with_ground(cam) for b in dtp.barrels_from_boxes(label)], bool(label.get("clean", True))
        inst, meta = io.load_instances(stem, labels_dir)
    except FileNotFoundError:
        return None
    mask = io.load_mask(labels_dir / f"{stem}_mask.png")
    return dtp.barrels_from_instances(inst, meta, mask, cam=cam), True


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
    ap.add_argument("--stems", default="", help="instead of a split: comma-separated stems, or a substring filter over data/raw with 'filter:<text>'")
    ap.add_argument("--gt-boxes", action="store_true", help="ground truth from <stem>_boxes.json (v2) instead of the instances")
    ap.add_argument("--name", required=True)
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR)
    ap.add_argument("--cam", choices=sorted(CAMS), default="4a8b")
    ap.add_argument("--iou", type=float, default=ed.IOU_THR)
    ap.add_argument("--rule", choices=ed.RULES, default="v1", help="eval_det rule: v1 (IoU + VOC ignores, default) or v2 (EVAL.md: + bottom edge, every barrel counts, clean negatives disqualify)")
    ap.add_argument("--sheets", action="store_true")
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)
    cam = CAMS[args.cam]
    sp = splits.load_splits()
    if args.stems.startswith("filter:"):
        stems = sorted(p.stem for p in io.list_images(args.raw) if args.stems[7:] in p.name)
    elif args.stems:
        stems = sorted(x for x in args.stems.split(",") if x)
    else:
        stems = sorted({x for v in sp.values() for x in v}) if args.split == "all" else sorted(sp.get(args.split, []))
    results, skipped = [], []
    out_dir = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    if args.sheets:
        (out_dir / "sheets").mkdir()
    for stem in stems:
        gt = load_gt(stem, args.labels, cam, boxes=args.gt_boxes)
        if gt is None:
            skipped.append(stem); continue
        gts, clean = gt
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
        r = ed.evaluate_frame(stem, preds, gts, cam, iou_thr=args.iou, rule=args.rule, clean=clean)
        results.append(r)
        if args.sheets:
            img = io.load_image(next(p for p in args.raw.glob(f"{stem}.*") if p.suffix.lower() in io.IMAGE_SUFFIXES))
            cv2.imwrite(str(out_dir / "sheets" / f"{stem}.png"), draw_sheet(img, preds, gts, {m.pred_idx for m in r.matches}))
    if skipped:
        print(f"skipped {len(skipped)} (no ground truth / no prediction): {skipped}")
    if not results:
        print("nothing to evaluate"); return 1
    md, _, _ = ed.write_results(results, out_dir, title=f"{args.name} on {args.split} ({len(results)} frames, cam {args.cam}, rule {args.rule})")
    json.dump({"cam": args.cam, "iou": args.iou, "rule": args.rule, "split": args.stems or args.split, "gt": "boxes" if args.gt_boxes else "instances", "git": cv.git_hash(), "pred": str(args.pred or args.pred_masks)}, (out_dir / "config.json").open("w"), indent=1)
    print(md.read_text()); print("written to", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
