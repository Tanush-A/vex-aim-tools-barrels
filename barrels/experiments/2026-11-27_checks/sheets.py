#!/usr/bin/env python3
"""Contact sheets of what the paint checks change (plan: PREREG.md). Images only, not committed.

    cd barrels && env PYTHONPATH=src python experiments/2026-11-27_checks/sheets.py judge <boxes_*.json> <base> <cand> <name>
    cd barrels && env PYTHONPATH=src python experiments/2026-11-27_checks/sheets.py harness <inputs.pkl> <arm> [--states found,off] [--groups ...]

``judge``: every box of ``base`` that ``cand`` does not draw, on every train frame (ordinary and extreme), with the
hand boxes (the mask shown is always the fixed colors' mask). ``harness``: every box an arm removes in the proof harness whose state before was in ``--states``.
A tile: left the photo (when the input is a train frame), right the class mask the detector saw; white = the hand
(or scene) boxes, red = the removed box, gray = the boxes kept. Caption: the input, why, the three readings.
Outputs: results/2026-11-27_checks/sheets/<name>_NN.jpg."""
from __future__ import annotations

import csv
import json
import pickle
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(HERE))
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
import arms as am  # noqa: E402

OUT = BARRELS / "results" / "2026-11-27_checks" / "sheets"
CAM = geo.AIM_4A8B6118_BOXFIT
TILE_H = 200


def color_mask(m: np.ndarray) -> np.ndarray:
    out = np.zeros(m.shape + (3,), np.uint8)
    out[m == 1] = (0, 140, 255)
    out[m == 2] = (255, 90, 0)
    out[m == 255] = (60, 60, 60)
    return out


def crop(img, box, pad=0.8):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    m = int(max(w, h) * pad) + 10
    X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(img.shape[1], x1 + m), min(img.shape[0], y1 + m)
    return img[Y0:Y1, X0:X1], (X0, Y0)


def draw(img, boxes, color, off, scale, th=1):
    for b in boxes:
        x0, y0, x1, y1 = b
        cv2.rectangle(img, (int((x0 - off[0]) * scale), int((y0 - off[1]) * scale)), (int((x1 - off[0]) * scale) - 1, int((y1 - off[1]) * scale) - 1), color, th)


def tile(photo, mask, box, truths, kept, caption: list[str]):
    panels = []
    for src in ([photo] if photo is not None else []) + [color_mask(mask)]:
        c, off = crop(src, box)
        s = TILE_H / c.shape[0]
        c = cv2.resize(c, (max(1, int(c.shape[1] * s)), TILE_H), interpolation=cv2.INTER_NEAREST)
        draw(c, kept, (150, 150, 150), off, s)
        draw(c, truths, (255, 255, 255), off, s)
        draw(c, [box], (0, 0, 255), off, s, 2)
        panels.append(c)
    t = np.concatenate(panels, axis=1)
    t = cv2.copyMakeBorder(t, 0, 16 * len(caption), 0, max(0, 420 - t.shape[1]), cv2.BORDER_CONSTANT, value=(20, 20, 20))
    for i, line in enumerate(caption):
        cv2.putText(t, line[:70], (3, TILE_H + 12 + 16 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
    return t


def write(tiles: list, name: str, cols: int = 3, per: int = 15) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob(f"{name}_*.jpg"):
        old.unlink()
    n = 0
    for i in range(0, len(tiles), per):
        chunk = tiles[i:i + per]
        W = max(t.shape[1] for t in chunk)
        H = max(t.shape[0] for t in chunk)
        rows = (len(chunk) + cols - 1) // cols
        sheet = np.zeros((rows * (H + 6), cols * (W + 6), 3), np.uint8)
        for j, t in enumerate(chunk):
            r, c = divmod(j, cols)
            sheet[r * (H + 6):r * (H + 6) + t.shape[0], c * (W + 6):c * (W + 6) + t.shape[1]] = t
        n += 1
        cv2.imwrite(str(OUT / f"{name}_{n:02d}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"{name}: {len(tiles)} tiles, {n} sheets in {OUT}")
    return n


def judge_sheets(boxes_path: str, base: str, cand: str, name: str) -> None:
    boxes = json.loads(Path(boxes_path).read_text())
    model = hl.adopted_model()
    stems = sorted(boxes)
    jg.require_train(stems)
    gts, clean = ct.load_gts(stems)
    tiles = []
    for s in stems:
        b0 = {(c, tuple(bb)) for c, bb, *_ in boxes[s][base]}
        b1 = {(c, tuple(bb)) for c, bb, *_ in boxes[s][cand]}
        gone = sorted(b0 - b1, key=lambda x: x[1][0])
        new = sorted(b1 - b0, key=lambda x: x[1][0])
        if not gone and not new:
            continue
        frame = jg.load_frame(s)
        mask = pl.segment(frame, model)[0]
        pre = [dtp.Barrel(color=c, bbox=tuple(bb), source="x") for c, bb, *_ in boxes[s][base]]
        fc = ct.classify_frame(s, pre, gts[s], clean[s])
        state = {(p.color, tuple(p.bbox)): st for p, st in zip(pre, fc.boxes)}
        for c, bb in gone:
            tiles.append(tile(frame.bgr.copy(), mask, bb, [g.bbox for g in gts[s]], [x[1] for x in b1],
                              [s, f"removed {'orange' if c == 1 else 'blue'} box, was: {state.get((c, bb))}", f"{base} -> {cand}"]))
        for c, bb in new:
            tiles.append(tile(frame.bgr.copy(), mask, bb, [g.bbox for g in gts[s]], [x[1] for x in b1],
                              [s, f"NEW {'orange' if c == 1 else 'blue'} box (red)", f"{base} -> {cand}"]))
    write(tiles, name)


def harness_sheets(inputs: str, arm: str, states: set, groups: set | None, name: str) -> None:
    enc = pickle.load(open(inputs, "rb"))
    rows = [r for r in csv.DictReader(open(BARRELS / "results" / "2026-11-27_checks" / "harness_removed.csv"))
            if r["arm"] == arm and r["before"] in states and (not groups or r["group"] in groups)]
    truth_p = Path(sys.argv[sys.argv.index("--truth") + 1]) if "--truth" in sys.argv else None
    scene_truth = json.loads(truth_p.read_text()) if truth_p else {}
    model = hl.adopted_model()
    tiles = []
    for r in rows:
        k = r["key"]
        mask = cv2.imdecode(np.frombuffer(enc[k], np.uint8), cv2.IMREAD_UNCHANGED)
        bb = tuple(int(v) for v in r["bbox"].split())
        stem = None if k.startswith("scene/") else k.rsplit("/", 1)[1]
        photo, truths = None, []
        if stem:
            photo = jg.load_frame(stem).bgr.copy()
            if io.boxes_path(stem).exists():
                truths = [g.bbox for g in dtp.barrels_from_boxes(io.load_boxes(stem, check_image=False))]
        elif k in scene_truth:
            truths = [tuple(b) for _, b in scene_truth[k]["truths"]]
        kept = [p.bbox for p in det.detect(mask, det.DetConfig(**am.ARMS[arm]))]
        cap = [k[:70], f"{r['why']} rule {r['rule']} {r['color']} was {r['before']}",
               f"solid {r['solid']} stripe {r['stripe_h']} body {r['body_share']} {r.get('kind', '')} {r.get('hidden', '')}"]
        tiles.append(tile(photo, mask, bb, truths, kept, cap))
    write(tiles, name)


if __name__ == "__main__":
    if sys.argv[1] == "judge":
        judge_sheets(*sys.argv[2:6])
    else:
        st = set(sys.argv[sys.argv.index("--states") + 1].split(",")) if "--states" in sys.argv else {"found", "off"}
        gr = set(sys.argv[sys.argv.index("--groups") + 1].split(",")) if "--groups" in sys.argv else None
        nm = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else f"harness_{sys.argv[3]}"
        harness_sheets(sys.argv[2], sys.argv[3], st, gr, nm)
