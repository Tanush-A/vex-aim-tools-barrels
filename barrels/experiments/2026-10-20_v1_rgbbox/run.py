#!/usr/bin/env python3
"""Cross-validate one v1 config on the pool frames (leave-one-scene-out) and write a results folder.

    python barrels/experiments/2026-10-20_v1_rgbbox/run.py --name v1_base            # BASE from config.py
    python barrels/experiments/2026-10-20_v1_rgbbox/run.py --name x --config path.json [--sheets] [--outputs]

Never touches the test split.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
from barrels import cv, io, pipeline as pl, splits, viz  # noqa: E402
from config import BASE  # noqa: E402


def load_pool() -> cv.Dataset:
    sp = splits.load_splits()
    if not sp["test"]:
        raise SystemExit("no locked test set in data/splits.json; run tools/make_splits.py --test-only first")
    return cv.Dataset(sp["train"])


def write_sheets(ds: cv.Dataset, preds: dict, out_dir: Path, outputs: bool = False) -> None:
    sheets = out_dir / "sheets"; sheets.mkdir(exist_ok=True)
    for s, pred in preds.items():
        cv2.imwrite(str(sheets / f"{s}.png"), viz.debug_sheet(ds.frames[s].bgr, pred, ds.masks[s]))
    if outputs:
        od = out_dir / "outputs"; od.mkdir(exist_ok=True)
        for s, pred in preds.items():
            o, b = viz.render_outputs(pred)
            cv2.imwrite(str(od / f"{s}_orange.png"), o); cv2.imwrite(str(od / f"{s}_blue.png"), b)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--config", type=Path, help="config JSON (default: BASE)")
    ap.add_argument("--sheets", action="store_true", help="write image|pred|gt debug sheets")
    ap.add_argument("--outputs", action="store_true", help="write the PROBLEM.md orange/blue output images")
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)

    cfg = pl.Config.from_dict(json.load(args.config.open())) if args.config else BASE
    ds = load_pool()
    res = cv.cross_validate(ds, cfg)
    out_dir = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    md = cv.write_cv_results(res, out_dir, title=f"{args.name}: LOSO CV on {len(ds.stems)} pool frames")
    if args.sheets or args.outputs:
        write_sheets(ds, res.preds, out_dir, outputs=args.outputs)
    print(md.read_text()); print("written to", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
