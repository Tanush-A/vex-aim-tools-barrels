#!/usr/bin/env python3
"""Contact sheets of what each judged candidate changed: every barrel gained, every barrel lost, every frame with a
new box that is not on its barrel. Made after run.py, from its judge.json and chosen.json; to be LOOKED at.

    python barrels/experiments/2026-11-26_light/sheets.py [--only B1_ramp_without_loose,...] [--tag ""]

Each item is three pictures: the photo with the hand box (white); what the fixed model paints and boxes; what the
candidate (the setting its fold picked for that place) paints and boxes. Painted pixels are orange and blue on the
dimmed photo; boxes are yellow (orange barrel) and cyan (blue barrel); on the new-box sheets the boxes that are not on
their barrel are magenta. Train frames only. Writes results/2026-11-26_light/sheets/<family>_*.png (not committed).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as cd  # noqa: E402
import common as cm  # noqa: E402
import rules as ru  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

PAINT = {ORANGE: (0, 140, 255), BLUE: (255, 80, 0)}
BOX = {ORANGE: (0, 255, 255), BLUE: (255, 255, 0)}
P = 168             # a crop panel's side
FW, FH = 320, 240   # a whole-frame panel


def setting_of(key: str) -> ru.Setting:
    r, w0, w1, s, h, d, o, x0, x1, hi, g = key.split("|")
    return ru.Setting(r, float(w0), float(w1), float(s), float(h), float(d), o, float(x0), float(x1), float(hi), float(g))


def painted(frame, mask) -> np.ndarray:
    img = (frame.bgr.astype(np.float32) * 0.45).astype(np.uint8)
    for c, col in PAINT.items():
        img[mask == c] = col
    return img


def boxes(img, preds, extra=()) -> np.ndarray:
    for p in preds:
        x0, y0, x1, y1 = p.bbox
        is_extra = (dtp.COLOR_NAMES[p.color], tuple(int(v) for v in p.bbox)) in extra
        cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255) if is_extra else BOX[p.color], 3 if is_extra else 2)
    return img


def label(img, text: str, scale: float = 0.36) -> np.ndarray:
    cv2.rectangle(img, (0, 0), (img.shape[1], 13), (0, 0, 0), -1)
    cv2.putText(img, text, (2, 10), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def crop(img, bbox, side: int = P) -> np.ndarray:
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = max(48, int(0.9 * max(x1 - x0, y1 - y0)))
    a0, b0 = int(cx - half), int(cy - half)
    out = np.zeros((2 * half, 2 * half, 3), np.uint8)
    xa, ya, xb, yb = max(0, a0), max(0, b0), min(img.shape[1], a0 + 2 * half), min(img.shape[0], b0 + 2 * half)
    out[ya - b0:yb - b0, xa - a0:xb - a0] = img[ya:yb, xa:xb]
    return cv2.resize(out, (side, side), interpolation=cv2.INTER_AREA if 2 * half > side else cv2.INTER_NEAREST)


class Frames:
    """A frame's photo, masks and boxes under the fixed model and under a setting, made once."""

    def __init__(self):
        self.cache: dict = {}

    def get(self, stem: str, st: ru.Setting) -> dict:
        k = (stem, st.key)
        if k not in self.cache:
            frame = jg.load_frame(stem)
            info: dict = {}
            mf, mc = ru.segment(frame, ru.FIXED), ru.segment(frame, st, info)
            self.cache[k] = {"frame": frame, "fixed": (mf, det.detect(mf, det.DetConfig(), ru.CAM)), "cand": (mc, det.detect(mc, det.DetConfig(), ru.CAM)), "info": info,
                             "gts": dtp.barrels_from_boxes(io.load_boxes(stem, check_image=False))}
        return self.cache[k]


def barrel_item(d: dict, ch: dict) -> np.ndarray:
    frame, bbox = d["frame"], tuple(ch["bbox"])
    photo = frame.bgr.copy()
    cv2.rectangle(photo, (bbox[0], bbox[1]), (bbox[2] - 1, bbox[3] - 1), (255, 255, 255), 1)
    a = label(crop(photo, bbox), f"{ch['stem'].replace('4A8B_', '')} #{ch['index'] + 1}")
    b = label(crop(boxes(painted(frame, d["fixed"][0]), d["fixed"][1]), bbox), f"fixed: {ch['before']}")
    w = d["info"].get("warmth", float("nan"))
    c = label(crop(boxes(painted(frame, d["cand"][0]), d["cand"][1]), bbox), f"cand: {ch['after']}" + (f" w {w:.2f}" if np.isfinite(w) else ""))
    return np.hstack([a, b, c])


def frame_item(d: dict, bc: dict) -> np.ndarray:
    frame = d["frame"]
    extra = {(c, tuple(b)) for c, b in bc["boxes_after"]}
    photo = frame.bgr.copy()
    for g in d["gts"]:
        cv2.rectangle(photo, (g.bbox[0], g.bbox[1]), (g.bbox[2] - 1, g.bbox[3] - 1), (255, 255, 255), 1)
    kind = "" if not bc["empty"] else " EMPTY clean" if bc["clean"] else " EMPTY clutter"
    small = lambda im: cv2.resize(im, (FW, FH), interpolation=cv2.INTER_AREA)  # noqa: E731
    a = label(small(photo), bc["stem"].replace("4A8B_", "") + kind, 0.4)
    b = label(small(boxes(painted(frame, d["fixed"][0]), d["fixed"][1])), f"fixed: not on a barrel {sum(bc['before'].values())}", 0.4)
    w = d["info"].get("warmth", float("nan"))
    c = label(small(boxes(painted(frame, d["cand"][0]), d["cand"][1], extra)), f"cand: not on a barrel {sum(bc['after'].values())}" + (f" w {w:.2f}" if np.isfinite(w) else ""), 0.4)
    return np.hstack([a, b, c])


def write_sheets(items: list[np.ndarray], path_stem: Path, per_row: int, rows_per_sheet: int) -> list[Path]:
    out = []
    if not items:
        return out
    h, w = items[0].shape[:2]
    per = per_row * rows_per_sheet
    for k in range(0, len(items), per):
        chunk = items[k:k + per]
        sheet = np.zeros((h * ((len(chunk) + per_row - 1) // per_row), w * per_row, 3), np.uint8)
        for i, it in enumerate(chunk):
            sheet[(i // per_row) * h:(i // per_row + 1) * h, (i % per_row) * w:(i % per_row + 1) * w] = it
        p = Path(f"{path_stem}_{k // per + 1}.png")
        cv2.imwrite(str(p), sheet)
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default="")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    chosen = json.loads((cm.OUT / f"chosen{a.tag}.json").read_text())["folds"]
    out = cm.OUT / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    fr = Frames()
    for name in chosen:
        if a.only and name not in a.only.split(","):
            continue
        j = json.loads((cm.OUT / f"judge_{name}{a.tag}" / "judge.json").read_text())
        st_of = lambda stem: setting_of(chosen[name][ct.place_of(stem)]["key"])  # noqa: E731
        for kind in ("gained", "lost"):
            chs = [c for c in j["changes"] if c["judged"] and c["kind"] == kind]
            items = [barrel_item(fr.get(c["stem"], st_of(c["stem"])), c) for c in chs]
            for p in write_sheets(items, out / f"{name}{a.tag}_{kind}", 3, 6):
                print(p, f"({len(items)} barrels {kind})")
        new = [b for b in j["box_changes"] if b["judged"] and sum(b["after"].values()) > sum(b["before"].values())]
        items = [frame_item(fr.get(b["stem"], st_of(b["stem"])), b) for b in new]
        for p in write_sheets(items, out / f"{name}{a.tag}_newboxes", 2, 4):
            print(p, f"({len(items)} frames with new boxes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
