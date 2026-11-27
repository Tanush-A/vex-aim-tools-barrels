#!/usr/bin/env python3
"""Contact sheets from ``boxes.csv`` (part B) or from a list of changed boxes: per box, the photo crop with the box
and the hand boxes, and the mask crop. To be LOOKED at. Images are not committed.

    python bgsheets.py false            # every B4 box not on its barrel
    python bgsheets.py real [rule]      # every real barrel B4 finds (optionally one rule)
    python bgsheets.py csv <file.csv> <name>   # rows with stem,x0,y0,x1,y1,color[,mask],[note]: any list of boxes

Train frames only (``judge.load_frame``)."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg  # noqa: E402

from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

PAINT = {ORANGE: (0, 140, 255), BLUE: (255, 80, 0)}
P = 150
SHEETS = bg.OUT / "sheets"


def crop(img, x0, y0, x1, y1, pad=0.6):
    w, h = x1 - x0, y1 - y0
    s = max(w, h) * (1 + 2 * pad)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a, b = int(max(0, cx - s / 2)), int(max(0, cy - s / 2))
    c, d = int(min(img.shape[1], cx + s / 2)), int(min(img.shape[0], cy + s / 2))
    out = img[b:d, a:c]
    return cv2.resize(out, (P, P), interpolation=cv2.INTER_NEAREST)


def panel(stem, box, color, mask_name="b4", note=""):
    frame = jg.load_frame(stem)
    img = frame.bgr.copy()
    for g in io.load_boxes(stem, check_image=False).get("barrels", []):
        a, b, c, d = (int(v) for v in g["bbox"])
        cv2.rectangle(img, (a, b), (c - 1, d - 1), (255, 255, 255), 1)
    x0, y0, x1, y1 = box
    cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 1)
    mp = bg.OUT / "masks" / f"{stem}.npz"
    m = np.load(mp)[mask_name] if mp.exists() else np.zeros(img.shape[:2], np.uint8)
    mi = (frame.bgr.astype(np.float32) * 0.35).astype(np.uint8)
    for c_, col in PAINT.items():
        mi[m == c_] = col
    cv2.rectangle(mi, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 1)
    row = np.hstack([crop(img, *box), crop(mi, *box)])
    lab = np.zeros((28, row.shape[1], 3), np.uint8)
    cv2.putText(lab, stem.replace("4A8B_", "")[:44], (2, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1)
    cv2.putText(lab, f"{color} {note}"[:50], (2, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (200, 255, 200), 1)
    return np.vstack([lab, row])


def grid(panels, cols=6):
    if not panels:
        return None
    h, w = panels[0].shape[:2]
    rows = []
    for i in range(0, len(panels), cols):
        r = panels[i:i + cols]
        r += [np.zeros((h, w, 3), np.uint8)] * (cols - len(r))
        rows.append(np.hstack(r))
    return np.vstack(rows)


def save(panels, name, per=36):
    SHEETS.mkdir(parents=True, exist_ok=True)
    for k in range(0, len(panels), per):
        g = grid(panels[k:k + per])
        cv2.imwrite(str(SHEETS / f"{name}_{k // per + 1:02d}.png"), g)
    print(name, len(panels), "panels")


def rows_of(kind, rule=None):
    with open(bg.OUT / "boxes.csv") as fh:
        rows = [r for r in csv.DictReader(fh) if r["arm"] == "b4"]
    if kind == "false":
        return [r for r in rows if r["state"] not in ("found", "off")]
    return [r for r in rows if r["state"] in ("found", "off") and (rule is None or r["rule"] == rule)]


def main() -> int:
    kind = sys.argv[1]
    if kind in ("false", "real"):
        rule = sys.argv[2] if len(sys.argv) > 2 else None
        rows = rows_of(kind, rule)
        ps = []
        for k, r in enumerate(rows):
            box = tuple(int(r[x]) for x in ("x0", "y0", "x1", "y1"))
            note = f"#{k + 1} {r['rule']} {r['state']} sh{float(r['stripe_h_ratio'] or 'nan'):.2f} bf{float(r['body_fill']):.2f}"
            ps.append(panel(r["stem"], box, r["color"], "b4", note))
        save(ps, kind + (f"_{rule}" if rule else ""), per=36 if kind == "false" else 48)
    elif kind == "csv":
        path, name = sys.argv[2], sys.argv[3]
        with open(path) as fh:
            rows = list(csv.DictReader(fh))
        ps = [panel(r["stem"], tuple(int(r[x]) for x in ("x0", "y0", "x1", "y1")), r.get("color", ""), r.get("mask", "b4") or "b4", r.get("note", "")) for r in rows]
        save(ps, name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
