#!/usr/bin/env python3
"""v2: one still image in, the same image with one box per barrel out.

    python barrels/tools/detect_image.py path/to/image.png [--out DIR] [--cam boxfit|4a8b|nominal] [--show] [--json] [--step1]

Runs the color segmentation (the hs model, config eb863d84, since 2026-11-09), then the v2 detector (barrels.detector: the stripe step, with
step 1 for the stripeless cases), and writes <stem>_boxes.png into --out (default barrels/results/detect_image/).
Prints one line per barrel: color, box, and how its edges were decided (seen / inferred / cut by the frame /
occluded). --json also writes <stem>_det.json. --step1 runs step 1 alone (the detector before 2026-11-05).
"""
from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import detect_cc, detector as det, geometry as geo, io, pipeline as pl, worldmap_bridge as wb  # noqa: E402

DEFAULT_MODEL = wb.default_model_path()                           # the hs model eb863d84 (or $BARRELS_MODEL); shared with the live feed
DEFAULT_OUT = io.PKG_ROOT / "results" / "detect_image"
CAMS = {"boxfit": geo.AIM_4A8B6118_BOXFIT, "4a8b": geo.AIM_4A8B6118, "nominal": geo.NOMINAL}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", type=Path)
    ap.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="results config.json with a fitted 'model' (v1 or hs); default $BARRELS_MODEL or the frozen v1")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--cam", choices=sorted(CAMS), default="boxfit", help="camera model (boxfit = provisional 2026-11-03 fit)")
    ap.add_argument("--json", action="store_true", help="also write <stem>_det.json (for eval_boxes.py --pred)")
    ap.add_argument("--step1", action="store_true", help="step 1 only (blobs -> count -> bottom edge), without the stripe step; for comparison")
    ap.add_argument("--stripe", action="store_true", help=argparse.SUPPRESS)   # the 2026-11-03 opt-in flag: accepted, now the default
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args(argv)
    if args.stripe:
        print("note: --stripe is the default since 2026-11-05; use --step1 for the detector without it")

    hook = wb.BarrelDetectorHook.load(args.model, cam=CAMS[args.cam])
    img = io.load_image(args.image)
    if img.shape[:2] != (480, 640):
        print(f"warning: {img.shape[1]}x{img.shape[0]} image; the model and geometry assume 640x480")
    mask, _ = pl.segment(pl.Frame.from_image(img), hook.model)        # step 0: which pixels are barrel-colored
    cfg = dataclasses.replace(det.DetConfig(), require_stripe=not args.step1)
    barrels = det.detect(mask, cfg, hook.cam)                         # the stripe step (+ step 1 where no stripe can show); --step1 = step 1 alone
    out = det.draw(img, barrels)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"{args.image.stem}_boxes.png"
    cv2.imwrite(str(path), out)
    for b in barrels:
        x0, y0, x1, y1 = b.bbox
        how = ["bottom inferred" if "bottom_inferred" in b.flags else "bottom seen"]
        if "top_inferred" in b.flags: how.append("top inferred")
        if "occluded" in b.flags: how.append("partly hidden, full box drawn")
        if "truncated" in b.flags: how.append("cut by frame")
        how.append("from its stripe" if b.source == "det2" else "no stripe seen")
        print(f"  {b.color_name:6}  x {x0}-{x1}  y {y0}-{y1}  {', '.join(how)}")
    if not barrels:
        print("  no barrels")
    if args.json:
        detect_cc.write_detections(args.out, args.image.stem, barrels)
    print(f"wrote {path}")
    if args.show:
        cv2.imshow("detect_image", out); cv2.waitKey(0); cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    sys.exit(main())
