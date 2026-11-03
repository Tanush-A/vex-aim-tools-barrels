#!/usr/bin/env python3
"""Detector step 1 on Dave's 20 snapshots (his robot, his office, two tables) — an outside check, nothing tuned.

Hypothesis: on frames from a different robot and tables never seen, the segmentation + step-1 detector still
boxes the mid-range barrels; the close-up frames (bottom below the frame, lid filling the image) and the
dark warm-lit table are where it breaks, and the geometry (fit to our robot) may be off for his.

Runs the frozen v1 model afd85483 + detector.detect (and the CC floor) on every DAVE_ frame, writes the
drawn output for all 20 (results/2026-11-03_dave_snaps/boxes/), and scores the 12 with Dave's boxes via
tools/eval_boxes.py (IoU >= 0.5 rule, box ground truth). No split, no tuning.

    python barrels/experiments/2026-11-03_dave_snaps/run.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import cv, detect_cc, detector as det, geometry as geo, io, pipeline as pl, worldmap_bridge as wb  # noqa: E402

MODEL = io.PKG_ROOT / "results" / "2026-10-20_v1_test_adaptive" / "config.json"
OUT = io.PKG_ROOT / "results" / "2026-11-03_dave_snaps"


def main() -> int:
    cam = geo.AIM_4A8B6118_BOXFIT
    hook = wb.BarrelDetectorHook.load(MODEL, cam=cam)
    out = cv.fresh_dir(OUT)
    (out / "boxes").mkdir(); (out / "det_step1").mkdir(); (out / "det_cc").mkdir(); (out / "overlay").mkdir()
    frames = [p for p in io.list_images() if p.name.startswith("DAVE_")]
    for p in frames:
        img = io.load_image(p)
        mask, info = pl.segment(pl.Frame.from_image(img), hook.model)
        preds = {"step1": det.detect(mask, cam=cam), "cc": detect_cc.detect(mask, cam=cam)}
        for arm, b in preds.items():
            detect_cc.write_detections(out / f"det_{arm}", p.stem, b)
        cv2.imwrite(str(out / "boxes" / f"{p.stem}_boxes.png"), det.draw(img, preds["step1"]))
        ov = (img * 0.35).astype("uint8"); ov[mask == io.ORANGE] = (0, 128, 255); ov[mask == io.BLUE] = (255, 100, 0)
        cv2.imwrite(str(out / "overlay" / f"{p.stem}_overlay.png"), ov)
        print(f"{p.stem}: floor {info.get('s_min_eff')}, {len(preds['step1'])} barrel(s): " + ", ".join(f"{b.color_name[0]}{list(b.bbox)}{'*' if 'bottom_inferred' in b.flags else ''}" for b in preds["step1"]))
    json.dump({"model": str(MODEL), "cam": "AIM_4A8B6118_BOXFIT", "cfg": det.DetConfig().to_dict(), "frames": [p.stem for p in frames], "git": cv.git_hash()},
              (out / "config.json").open("w"), indent=1)
    for arm in ("step1", "cc"):
        subprocess.run([sys.executable, str(io.PKG_ROOT / "tools" / "eval_boxes.py"), "--pred", str(out / f"det_{arm}"), "--stems", "filter:DAVE_",
                        "--gt-boxes", "--name", f"dave_snaps_{arm}", "--sheets", "--out", str(out)], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
