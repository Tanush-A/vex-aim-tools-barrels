#!/usr/bin/env python3
"""Acceptance clause 7, the close look: on the recordings (read only), every frame where either new rule is ASKED (a
stripeless frame-bottom piece cut by the frame's side, or a stripeless piece whose predicted stripe runs past the frame
bottom), what it answers, on contact sheets for the eye. The battery's recordings script only shows frames whose boxes
change; this one also shows the frames where the rule was asked and kept the box.

    python barrels/experiments/2026-11-23_closeup_shape/rec_asked.py --rec <data/recordings> [--out round1]
Outputs: results/2026-11-23_closeup_shape/<out>/rec_asked.md, rec_asked.csv; sheets/rec_asked_*.png (ignored).
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np

import closeup as K
from barrels import detector as det, geometry as geo, pipeline as pl, worldmap_bridge as wb

CAM = geo.AIM_4A8B6118_BOXFIT


def asked(mask, cfg):
    """[(piece box, what the rule says)] for the pieces either rule is asked about on this mask."""
    h, w = mask.shape
    out = []
    for p, seen_y1 in det._step1_pieces(mask, cfg, CAM):
        x0, y0, x1, y1 = p.bbox
        reach = y1 >= h
        cut_stripe = not reach and det._closeup_stripe_rows(CAM, y0)[1] >= h
        side = (reach or cut_stripe) and (x0 == 0 or x1 == w)
        if side:
            out.append((p, "side: seen to stripe" if det._seen_to_stripe(CAM, cfg, y0, seen_y1, h) else "side: NOT seen to stripe"))
        elif cut_stripe:
            out.append((p, "stripe cut by frame bottom"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rec", required=True)
    ap.add_argument("--out", default="round1")
    a = ap.parse_args(argv)
    rec = Path(a.rec)
    out_dir = K.OUT / a.out
    (out_dir / "sheets").mkdir(parents=True, exist_ok=True)
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    rows, tiles = [], []
    for f in sorted(rec.rglob("*.png")):
        img = cv2.imread(str(f))
        if img is None or img.shape[:2] != (480, 640):
            continue
        mask = pl.segment(pl.Frame.from_image(img), model)[0]
        q = asked(mask, K.ARMS["shape"])
        if not q:
            continue
        before = det.detect(mask, K.ARMS["start"], CAM)
        after = det.detect(mask, K.ARMS["shape"], CAM)
        for p, what in q:
            rows.append(dict(frame=str(f.relative_to(rec)), piece=" ".join(map(str, p.bbox)), asked=what,
                             start=int(any(b.bbox == p.bbox for b in before)), shape=int(any(b.bbox == p.bbox for b in after))))
        t = det.draw(img, after, 2)
        for p, what in q:
            x0, y0, x1, y1 = p.bbox
            cv2.rectangle(t, (x0, y0), (x1 - 1, y1 - 1), (0, 0, 255) if "NOT" in what else (255, 0, 255), 1)
        cv2.putText(t, str(f.relative_to(rec))[-40:], (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        tiles.append(cv2.resize(t, (320, 240)))
    for i in range(0, len(tiles), 12):
        chunk = tiles[i:i + 12] + [np.zeros((240, 320, 3), np.uint8)] * (-len(tiles[i:i + 12]) % 4)
        sheet = np.vstack([np.hstack(chunk[j:j + 4]) for j in range(0, len(chunk), 4)])
        cv2.imwrite(str(out_dir / "sheets" / f"rec_asked_{i // 12:02d}.png"), sheet)
    with open(out_dir / "rec_asked.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, ["frame", "piece", "asked", "start", "shape"]); wr.writeheader(); wr.writerows(rows)
    L = ["# Recordings: every frame where a new rule is asked", "", f"{len(tiles)} frames, {len(rows)} pieces.", "",
         "| frame | piece | asked | box before | box after |", "|---|---|---|---|---|"]
    L += [f"| {r['frame']} | {r['piece']} | {r['asked']} | {r['start']} | {r['shape']} |" for r in rows]
    (out_dir / "rec_asked.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
