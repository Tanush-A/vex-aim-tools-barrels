#!/usr/bin/env python3
"""Score predicted masks against ground truth (docs/EVAL.md) and write a results folder.

    python barrels/tools/eval_masks.py --pred results/2026-10-20_rgbbox/pred --split dev --name rgbbox

Predictions: <stem>_pred.png or <stem>.png in --pred, values {0,1,2}. Ground truth: data/labels.
Writes results/<date>_<name>/{summary.md, summary.csv, per_image.csv} (+ debug sheets with --sheets).
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import eval as ev, io, splits as sp, viz  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred", type=Path, required=True, help="folder of predicted masks")
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR)
    ap.add_argument("--split", default="dev", choices=(*sp.SPLIT_NAMES, "all"))
    ap.add_argument("--name", required=True, help="results folder suffix")
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    ap.add_argument("--sheets", action="store_true", help="also write image|pred|gt debug sheets")
    args = ap.parse_args(argv)

    splits = sp.load_splits()
    stems = sorted({x for v in splits.values() for x in v}) if args.split == "all" else sorted(splits[args.split])
    if not stems:
        print(f"no images in split {args.split!r}; run tools/make_splits.py first")
        return 1

    results = []
    missing = []
    for stem in stems:
        pred_path = next((p for p in (args.pred / f"{stem}_pred.png", args.pred / f"{stem}.png") if p.exists()), None)
        gt_path = args.labels / f"{stem}_mask.png"
        if pred_path is None or not gt_path.exists():
            missing.append(stem)
            continue
        pred = io.load_mask(pred_path)
        gt = io.load_mask(gt_path)
        results.append(ev.evaluate_image(stem, pred, gt))
    if missing:
        print(f"WARNING: {len(missing)} images skipped (no prediction or no label): {missing}")
    if not results:
        print("nothing to evaluate")
        return 1

    out_dir = args.out / f"{dt.date.today().isoformat()}_{args.name}"
    summary, _ = ev.write_results(results, out_dir, title=f"{args.name} on {args.split} ({len(results)} images)")
    if args.sheets:
        sheets = out_dir / "sheets"
        sheets.mkdir(exist_ok=True)
        for r in results:
            img_path = next((p for p in args.raw.glob(f"{r.name}.*") if p.suffix.lower() in io.IMAGE_SUFFIXES), None)
            if img_path is None:
                continue
            pred = io.load_mask(next(p for p in (args.pred / f"{r.name}_pred.png", args.pred / f"{r.name}.png") if p.exists()))
            gt = io.load_mask(args.labels / f"{r.name}_mask.png")
            import cv2
            cv2.imwrite(str(sheets / f"{r.name}.png"), viz.debug_sheet(io.load_image(img_path), pred, gt))
    print(summary.read_text())
    print(f"written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
