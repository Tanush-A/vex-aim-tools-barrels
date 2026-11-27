#!/usr/bin/env python3
"""Exploration before the pre-registration (listed there): what a few hand-picked settings paint and box on a few
frames, in-sample. A smoke test of ``rules.py`` and a look at the masks; no number from here is a result.

    python barrels/experiments/2026-11-26_light/look_rules.py

One row per frame: the frame with the hand boxes (white), then per setting the frame dimmed with the painted pixels
in their class color (orange, blue) and the detector's boxes. Writes results/2026-11-26_light/sheets/rules_*.png.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import rules as ru  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

SETTINGS = {
    "fixed": ru.FIXED,
    "ramp": ru.Setting("without_loose", 0.08, 0.20, 40, 92),
    "ramp+rel.20": ru.Setting("without_loose", 0.08, 0.20, 40, 92, 0.20),
    "ramp+rel.30": ru.Setting("without_loose", 0.08, 0.20, 40, 92, 0.30),
}
SHEETS = {
    "bath": ["4A8B_lampwarm6_bathtile_core_01", "4A8B_lampwarm6_bathtile_clutter_01", "4A8B_lampwarm6_bathtile_neg_02", "4A8B_lampmid6_bathtile_core_01",
             "4A8B_lampmid3_bathtile_clutter_01", "4A8B_lampcool6_bathtile_core_01"],
    "ottoman_glass": ["4A8B_lampwarm6_ottoman_core_01", "4A8B_lampwarm6_ottoman_clutter_01", "4A8B_lampwarm6_ottoman_neg_02", "4A8B_lampmid6_ottoman_core_01",
                      "4A8B_lampwarm6_glass_neg_02", "4A8B_lampmid6_glass_neg_02"],
}
W, H = 400, 300
BGR = {ORANGE: (0, 140, 255), BLUE: (255, 80, 0)}


def draw(frame, mask, preds, gts, title: str) -> np.ndarray:
    img = frame.bgr.copy() if mask is None else (frame.bgr.astype(np.float32) * 0.45).astype(np.uint8)
    if mask is not None:
        for c, col in BGR.items():
            img[mask == c] = col
    for g in gts:
        x0, y0, x1, y1 = g.bbox
        cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
    for p in preds:
        x0, y0, x1, y1 = p.bbox
        cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (0, 255, 255) if p.color == ORANGE else (255, 255, 0), 2)
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    cv2.rectangle(img, (0, 0), (W, 16), (0, 0, 0), -1)
    cv2.putText(img, title, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def main() -> int:
    out = cm.OUT / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    for name, stems in SHEETS.items():
        rows = []
        for stem in stems:
            frame = jg.load_frame(stem)
            label = io.load_boxes(stem, check_image=False)
            gts = dtp.barrels_from_boxes(label)
            cells = [draw(frame, None, [], gts, stem.replace("4A8B_", ""))]
            for sname, st in SETTINGS.items():
                info: dict = {}
                mask = ru.segment(frame, st, info)
                preds = det.detect(mask, det.DetConfig(), ru.CAM)
                fc = ct.classify_frame(stem, preds, gts, bool(label.get("clean", True)))
                txt = f"{sname}: found {fc.n_gt(ct.FOUND)}/{len(gts)} extra {fc.extra}"
                if "warmth" in info and np.isfinite(info["warmth"]):
                    txt += f" w {info['warmth']:.2f} t {info['share']:.2f}"
                print(f"{stem:45s} {txt}  {({k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items()})}")
                cells.append(draw(frame, mask, preds, gts, txt))
            rows.append(np.hstack(cells))
        p = out / f"rules_{name}.png"
        cv2.imwrite(str(p), np.vstack(rows))
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
