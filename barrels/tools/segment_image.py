#!/usr/bin/env python3
"""Run the v1 color segmentation (and the reference CC detector) on one image.

    python barrels/tools/segment_image.py path/to/image.png [--out DIR] [--model results/.../config.json] [--boxes]

Loads the fitted v1 model (default: the one saved by the final test run, config afd85483), segments
the image, and writes next to it (or into --out):
    <stem>_orange.png, <stem>_blue.png   the PROBLEM.md outputs (flat class color on gray)
    <stem>_overlay.png                   the image dimmed with the classes painted on
    <stem>_pred.png                      the class mask (0 other, 1 orange, 2 blue)
With --boxes it also runs the connected-components reference detector and prints one line per barrel.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import detect_cc, geometry as geo, io, pipeline as pl, viz, worldmap_bridge as wb  # noqa: E402

DEFAULT_MODEL = io.PKG_ROOT / "results" / "2026-10-20_v1_test_adaptive" / "config.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", type=Path)
    ap.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="results config.json with a fitted 'model'")
    ap.add_argument("--out", type=Path, help="output folder (default: next to the image)")
    ap.add_argument("--boxes", action="store_true", help="also run the CC reference detector")
    ap.add_argument("--show", action="store_true", help="open a window with the overlay")
    args = ap.parse_args(argv)

    hook = wb.BarrelDetectorHook.load(args.model, cam=geo.AIM_4A8B6118)
    img = io.load_image(args.image)
    if img.shape[:2] != (480, 640):
        print(f"warning: {img.shape[1]}x{img.shape[0]} image; the model and geometry assume 640x480")
    frame = pl.Frame.from_image(img)
    mask, info = pl.segment(frame, hook.model)
    out_dir = args.out or args.image.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.image.stem
    orange, blue = viz.render_outputs(mask)
    cv2.imwrite(str(out_dir / f"{stem}_orange.png"), orange)
    cv2.imwrite(str(out_dir / f"{stem}_blue.png"), blue)
    io.save_mask(out_dir / f"{stem}_pred.png", mask)
    overlay = (img.astype(np.float32) * 0.35).astype(np.uint8)
    overlay[mask == io.ORANGE] = viz.ORANGE_BGR; overlay[mask == io.BLUE] = viz.BLUE_BGR
    n_o, n_b = int((mask == io.ORANGE).sum()), int((mask == io.BLUE).sum())
    print(f"{args.image.name}: saturation floor used {info.get('s_min_eff')}, orange {n_o} px, blue {n_b} px")
    if args.boxes:
        barrels = detect_cc.detect(mask, cam=hook.cam)
        for b in barrels:
            x, y = b.ground_xy_mm
            print(f"  {b.color_name:6} box x {b.bbox[0]}-{b.bbox[2]} y {b.bbox[1]}-{b.bbox[3]}  ground ({x:.0f}, {y:.0f}) mm  flags {sorted(b.flags) or '-'}")
            cv2.rectangle(overlay, (b.bbox[0], b.bbox[1]), (b.bbox[2] - 1, b.bbox[3] - 1), (255, 255, 255), 1)
        if not barrels:
            print("  no barrels")
    cv2.imwrite(str(out_dir / f"{stem}_overlay.png"), overlay)
    print(f"wrote {stem}_orange.png, {stem}_blue.png, {stem}_pred.png, {stem}_overlay.png in {out_dir}")
    if args.show:
        cv2.imshow("segment_image", overlay); cv2.waitKey(0); cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    sys.exit(main())
