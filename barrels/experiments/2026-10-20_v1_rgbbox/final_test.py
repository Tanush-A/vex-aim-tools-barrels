#!/usr/bin/env python3
"""The single evaluation of a chosen v1 config on the locked test set (EVAL.md).

    python .../final_test.py --config results/<...>/configs/<id>.json --name v1_test

Fits on ALL 16 pool frames, predicts the 5 test frames once, writes the EVAL.md tables, debug
sheets, the PROBLEM.md output images, and the predicted masks (so tools/eval_masks.py can
re-score them independently). Refuses to run if a *_v1_test results folder already exists
unless --allow-rerun "<reason>" is given; the reason is written into the new folder.
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
from barrels import cv, eval as ev, io, pipeline as pl, splits, viz  # noqa: E402
from config import BASE  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, help="chosen config JSON (default: BASE)")
    ap.add_argument("--name", default="v1_test")
    ap.add_argument("--allow-rerun", metavar="REASON", help="required if a test run already exists")
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)

    existing = sorted(args.out.glob(f"*_{args.name}*"))
    if existing and not args.allow_rerun:
        print(f"REFUSING: test already evaluated in {[p.name for p in existing]}. Pass --allow-rerun '<reason>' to run again.")
        return 2

    cfg = pl.Config.from_dict(json.load(args.config.open())) if args.config else BASE
    sp = splits.load_splits()
    pool, test = cv.Dataset(sp["train"]), cv.Dataset(sp["test"])
    model, results, preds, infos = cv.fit_final_and_predict(pool, test, cfg)

    out_dir = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    md, _ = ev.write_results(results, out_dir, title=f"{args.name}: config {cfg.short_hash()} fit on {len(pool.stems)} pool frames, evaluated once on {len(test.stems)} test frames")
    json.dump({"config": cfg.to_dict(), "config_hash": cfg.short_hash(), "git": cv.git_hash(), "test": test.stems,
               "model": model.to_dict(), "rerun_reason": args.allow_rerun, "infos": infos},
              (out_dir / "config.json").open("w"), indent=1, default=float)
    for sub in ("pred", "sheets", "outputs"):
        (out_dir / sub).mkdir()
    for s, pred in preds.items():
        io.save_mask(out_dir / "pred" / f"{s}_pred.png", pred)
        cv2.imwrite(str(out_dir / "sheets" / f"{s}.png"), viz.debug_sheet(test.frames[s].bgr, pred, test.masks[s]))
        o, b = viz.render_outputs(pred)
        cv2.imwrite(str(out_dir / "outputs" / f"{s}_orange.png"), o); cv2.imwrite(str(out_dir / "outputs" / f"{s}_blue.png"), b)
    print(md.read_text()); print("written to", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
