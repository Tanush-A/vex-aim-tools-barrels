#!/usr/bin/env python3
"""Part A, the pictures: which pixels each reading reads, on the frames where a reading is off and on typical ones.

    python barrels/experiments/2026-11-26_light/look_readings.py

One row per frame, one column per reading: the frame dimmed, the pixels that reading read in magenta, its warmth in
the corner. Train frames only. Writes results/2026-11-26_light/sheets/readings_*.png (images are not committed).
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import judge as jg  # noqa: E402

COLS = ("whole_frame", "above_gate20", "without_barrels", "without_loose", "least_colored", "highlights", "tiles")
SHEETS = {
    "off": ["4A8B_lampcool6_bathtile_close_01", "4A8B_lampcool6_ottoman_core_01", "4A8B_lampcool6_ottoman_close_01", "4A8B_lampwarm6_glass_neg_02",
            "4A8B_lampmid6_glass_neg_02", "4A8B_lampwarm6_ottoman_close_01"],
    "typical": ["4A8B_lampwarm6_bathtile_core_01", "4A8B_lampmid6_bathtile_clutter_01", "4A8B_lampwarm6_ottoman_core_01", "4A8B_lampmid6_ottoman_clutter_01",
                "4A8B_overheaddim_palewood_core_01", "4A8B_window_light_core_01"],
    "other": ["4A8B_lampcool6_ottoman_clutter_01", "4A8B_window_abpwhite_occlx_18", "4A8B_lampwarm6_glass_clutter_01", "4A8B_campus_light_hand_02",
              "4A8B_both_abpgray_core_01", "4A8B_lampmid3_bathtile_neg_02"],
    "parked": ["4A8B_lampcool3_wood_core_01", "4A8B_lampcool6_wood_core_01", "4A8B_lampwarm6_wood_core_01", "4A8B_lampmid3_ottoman_core_01",
               "4A8B_window_black_close_02", "4A8B_lampcool6_bathtile_core_01"],
}
W, H = 256, 192


def cell(frame, mask, text: str) -> np.ndarray:
    img = (frame.bgr.astype(np.float32) * 0.55).astype(np.uint8)
    if mask is not None:
        img[mask] = (255, 0, 255)
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    cv2.rectangle(img, (0, 0), (W, 16), (0, 0, 0), -1)
    cv2.putText(img, text, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def main() -> int:
    out = cm.OUT / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    for name, stems in SHEETS.items():
        rows = []
        for stem in stems:
            frame = jg.load_frame(stem)
            masks = cm.reading_masks(frame)
            vals = cm.all_readings(frame)
            first = cv2.resize(frame.bgr, (W, H), interpolation=cv2.INTER_AREA)
            cv2.rectangle(first, (0, 0), (W, 16), (0, 0, 0), -1)
            cv2.putText(first, stem.replace("4A8B_", ""), (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1, cv2.LINE_AA)
            rows.append(np.hstack([first] + [cell(frame, masks[c], f"{c} {vals[c].warmth:+.2f}") for c in COLS]))
        p = out / f"readings_{name}.png"
        cv2.imwrite(str(p), np.vstack(rows))
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
