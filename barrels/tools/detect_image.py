#!/usr/bin/env python3
"""v2: one still image in, the same image with one box per barrel out.

    python barrels/tools/detect_image.py path/to/image.png [--out DIR] [--cam boxfit|4a8b|nominal] [--show] [--json]

Runs the frozen v1 segmentation (config afd85483), then the v2 detector (barrels.detector), and writes
<stem>_boxes.png into --out (default barrels/results/detect_image/). Prints one line per barrel:
color, box, and whether the bottom edge was seen or inferred. --json also writes <stem>_det.json.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import detect_cc, detector as det, geometry as geo, io, pipeline as pl, worldmap_bridge as wb  # noqa: E402

DEFAULT_MODEL = io.PKG_ROOT / "results" / "2026-10-20_v1_test_adaptive" / "config.json"
DEFAULT_OUT = io.PKG_ROOT / "results" / "detect_image"
CAMS = {"boxfit": geo.AIM_4A8B6118_BOXFIT, "4a8b": geo.AIM_4A8B6118, "nominal": geo.NOMINAL}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", type=Path)
    ap.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="results config.json with the fitted v1 'model'")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--cam", choices=sorted(CAMS), default="boxfit", help="camera model (boxfit = provisional 2026-11-03 fit)")
    ap.add_argument("--json", action="store_true", help="also write <stem>_det.json (for eval_boxes.py --pred)")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args(argv)

    hook = wb.BarrelDetectorHook.load(args.model, cam=CAMS[args.cam])
    img = io.load_image(args.image)
    if img.shape[:2] != (480, 640):
        print(f"warning: {img.shape[1]}x{img.shape[0]} image; the model and geometry assume 640x480")
    mask, _ = pl.segment(pl.Frame.from_image(img), hook.model)        # step 0: which pixels are barrel-colored
    barrels = det.detect(mask, cam=hook.cam)                          # steps 1a-c: blobs -> count -> bottom edge
    out = det.draw(img, barrels)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"{args.image.stem}_boxes.png"
    cv2.imwrite(str(path), out)
    for b in barrels:
        x0, y0, x1, y1 = b.bbox
        how = "bottom inferred from top row" if "bottom_inferred" in b.flags else ("cut by frame" if "truncated" in b.flags else "bottom seen")
        print(f"  {b.color_name:6}  x {x0}-{x1}  y {y0}-{y1}  {how}")
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
