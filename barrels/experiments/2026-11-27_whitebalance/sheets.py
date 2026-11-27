#!/usr/bin/env python3
"""Contact sheets of what each judged white-balance candidate changed: every barrel gained, every barrel lost, every
frame with a new box that is not on its barrel. EXPERIMENT ONLY. Made after run.py; to be LOOKED at.

    python barrels/experiments/2026-11-27_whitebalance/sheets.py [--only P1_gray_world_partial,...]

Each item is four panels: the photo with the hand box (white); what the fixed model paints and boxes on the photo;
the corrected photo (in memory only, the setting the candidate used at that place); what the fixed model paints and
boxes on it. Paint orange / blue on the dimmed image; boxes yellow (orange barrel) and cyan (blue barrel); boxes not on
their barrel magenta. Writes results/2026-11-27_whitebalance/sheets/*.png (not committed).
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
import wb  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

OUT = wb.BARRELS / "results" / "2026-11-27_whitebalance"
PAINT = {ORANGE: (0, 140, 255), BLUE: (255, 80, 0)}
BOX = {ORANGE: (0, 255, 255), BLUE: (255, 255, 0)}
P = 150
FW, FH = 240, 180


def painted(bgr, mask):
    img = (bgr.astype(np.float32) * 0.45).astype(np.uint8)
    for c, col in PAINT.items():
        img[mask == c] = col
    return img


def boxes(img, preds, extra=()):
    for p in preds:
        x0, y0, x1, y1 = p.bbox
        e = (dtp.COLOR_NAMES[p.color], tuple(int(v) for v in p.bbox)) in extra
        cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255) if e else BOX[p.color], 3 if e else 2)
    return img


def label(img, text, scale=0.34):
    cv2.rectangle(img, (0, 0), (img.shape[1], 12), (0, 0, 0), -1)
    cv2.putText(img, text, (2, 9), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def crop(img, bbox, side=P):
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = max(48, int(0.9 * max(x1 - x0, y1 - y0)))
    a0, b0 = int(cx - half), int(cy - half)
    out = np.zeros((2 * half, 2 * half, 3), np.uint8)
    xa, ya, xb, yb = max(0, a0), max(0, b0), min(img.shape[1], a0 + 2 * half), min(img.shape[0], b0 + 2 * half)
    out[ya - b0:yb - b0, xa - a0:xb - a0] = img[ya:yb, xa:xb]
    return cv2.resize(out, (side, side), interpolation=cv2.INTER_AREA if 2 * half > side else cv2.INTER_NEAREST)


_cache: dict = {}


def get(stem, st):
    k = (stem, st.key)
    if k not in _cache:
        frame = jg.load_frame(stem)
        info: dict = {}
        mf = wb.segment(frame, wb.FIXED)
        mc = wb.segment(frame, st, info)
        _cache[k] = {"frame": frame, "fixed": (mf, det.detect(mf, det.DetConfig(), wb.CAM)), "cand": (mc, det.detect(mc, det.DetConfig(), wb.CAM)),
                     "corr": info.get("corrected", frame).bgr, "gains": info.get("gains"), "gts": dtp.barrels_from_boxes(io.load_boxes(stem, check_image=False))}
    return _cache[k]


def gtxt(d):
    return "" if d["gains"] is None else " g " + " ".join(f"{v:.2f}" for v in d["gains"])


def barrel_item(d, ch):
    f, bbox = d["frame"], tuple(ch["bbox"])
    photo = f.bgr.copy()
    cv2.rectangle(photo, bbox[:2], (bbox[2] - 1, bbox[3] - 1), (255, 255, 255), 1)
    return np.hstack([label(crop(photo, bbox), ch["stem"].replace("4A8B_", "")[:26]),
                      label(crop(boxes(painted(f.bgr, d["fixed"][0]), d["fixed"][1]), bbox), f"fixed: {ch['before']}"),
                      label(crop(d["corr"].copy(), bbox), "corrected" + gtxt(d)),
                      label(crop(boxes(painted(d["corr"], d["cand"][0]), d["cand"][1]), bbox), f"cand: {ch['after']}")])


def frame_item(d, bc):
    f = d["frame"]
    extra = {(c, tuple(b)) for c, b in bc["boxes_after"]}
    photo = f.bgr.copy()
    for g in d["gts"]:
        cv2.rectangle(photo, (g.bbox[0], g.bbox[1]), (g.bbox[2] - 1, g.bbox[3] - 1), (255, 255, 255), 1)
    kind = "" if not bc["empty"] else " EMPTY clean" if bc["clean"] else " EMPTY clutter"
    sm = lambda im: cv2.resize(im, (FW, FH), interpolation=cv2.INTER_AREA)  # noqa: E731
    return np.hstack([label(sm(photo), bc["stem"].replace("4A8B_", "")[:28] + kind),
                      label(sm(boxes(painted(f.bgr, d["fixed"][0]), d["fixed"][1])), f"fixed: off {sum(bc['before'].values())}"),
                      label(sm(d["corr"].copy()), "corrected" + gtxt(d)),
                      label(sm(boxes(painted(d["corr"], d["cand"][0]), d["cand"][1], extra)), f"cand: off {sum(bc['after'].values())}")])


def write_sheets(items, stem, per_row, rows):
    out = []
    if not items:
        return out
    h, w = items[0].shape[:2]
    per = per_row * rows
    for k in range(0, len(items), per):
        chunk = items[k:k + per]
        sheet = np.zeros((h * ((len(chunk) + per_row - 1) // per_row), w * per_row, 3), np.uint8)
        for i, it in enumerate(chunk):
            sheet[(i // per_row) * h:(i // per_row + 1) * h, (i % per_row) * w:(i % per_row + 1) * w] = it
        p = Path(f"{stem}_{k // per + 1}.png")
        cv2.imwrite(str(p), sheet)
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    folds = json.loads((OUT / "chosen.json").read_text())["folds"]
    out = OUT / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    for name in list(cd.FULL) + list(cd.FAMILIES):
        if a.only and name not in a.only.split(","):
            continue
        j = json.loads((OUT / f"judge_{name}" / "judge.json").read_text())
        st_of = (lambda s, n=name: cd.FULL[n]) if name in cd.FULL else (lambda s, n=name: wb.Setting.from_key(folds[n][ct.place_of(s)]["key"]))
        for kind in ("gained", "lost"):
            chs = [c for c in j["changes"] if c["judged"] and c["kind"] == kind]
            for p in write_sheets([barrel_item(get(c["stem"], st_of(c["stem"])), c) for c in chs], out / f"{name}_{kind}", 2, 7):
                print(p, len(chs), kind)
        new = [b for b in j["box_changes"] if b["judged"] and sum(b["after"].values()) > sum(b["before"].values())]
        for p in write_sheets([frame_item(get(b["stem"], st_of(b["stem"])), b) for b in new], out / f"{name}_newboxes", 1, 7):
            print(p, len(new), "new-box frames")
        _cache.clear()
    return 0


if __name__ == "__main__":
    sys.exit(main())
