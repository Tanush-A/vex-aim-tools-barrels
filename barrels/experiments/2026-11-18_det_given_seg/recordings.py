#!/usr/bin/env python3
"""PREREG rule 5: on the unlabeled recordings, which boxes appear or disappear against `base` for an arm.

Every frame under the recordings folder (local, not in git; none of them is in any split) is segmented with the
adopted color model and detected with `base` and with each arm. A box "appears" when the arm draws it and `base`
has no box of the same color overlapping it by IoU > 0.5; "disappears" is the reverse. Every changed frame goes on
a contact sheet: the arm's boxes in yellow / green, an appearing box ringed in red, a disappearing box drawn in
magenta. The verdict is written by hand into by_eye.md after looking at the sheets.

    python barrels/experiments/2026-11-18_det_given_seg/recordings.py --rec <path to data/recordings> --arms cap,side
Outputs: results/2026-11-18_det_given_seg/recordings.csv, recordings.md; sheets/rec_<arm>/ (ignored).
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
from barrels import detect_types as dtp, detector as det, eval_det as ed, geometry as geo, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402
from arms import ARMS  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-18_det_given_seg"
CAM = geo.AIM_4A8B6118_BOXFIT
PER_SHEET = 6


def same(a: dtp.Barrel, b: dtp.Barrel) -> bool:
    return a.color == b.color and ed.box_iou(a.bbox, b.bbox) > 0.5


def tile(img, preds, added, removed, label):
    t = det.draw(img, preds, 1)
    for b in added:
        x0, y0, x1, y1 = b.bbox
        cv2.rectangle(t, (x0 - 3, y0 - 3), (x1 + 2, y1 + 2), (0, 0, 255), 2)
    for b in removed:
        x0, y0, x1, y1 = b.bbox
        cv2.rectangle(t, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 2)
    cv2.putText(t, label, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
    cv2.putText(t, label, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rec", default=str(PKG_ROOT / "data" / "recordings"))
    ap.add_argument("--arms", default="cap,join,cap+join,cap+join+side,side")
    args = ap.parse_args(argv)
    rec = Path(args.rec)
    frames = sorted(rec.rglob("*.png"))
    if not frames:
        print("no recordings under", rec); return 1
    test = set(splits.load_splits()["test"])
    assert not any(p.stem in test for p in frames), "a test frame among the recordings"
    arms = [a for a in args.arms.split(",") if a]
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    rows, tiles = [], {a: [] for a in arms}
    counts = {a: {"frames_changed": 0, "added": 0, "removed": 0, "boxes": 0} for a in arms}
    base_boxes = 0
    for p in frames:
        img = cv2.imread(str(p))
        if img is None:
            continue
        mask = pl.segment(pl.Frame.from_image(img), model)[0]
        base = det.detect(mask, ARMS["base"], CAM)
        base_boxes += len(base)
        name = f"{p.parent.parent.name}/{p.parent.name}/{p.stem}" if p.parent.parent != rec else f"{p.parent.name}/{p.stem}"
        for a in arms:
            preds = det.detect(mask, ARMS[a], CAM)
            added = [b for b in preds if not any(same(b, o) for o in base)]
            removed = [o for o in base if not any(same(b, o) for b in preds)]
            counts[a]["boxes"] += len(preds)
            if added or removed:
                counts[a]["frames_changed"] += 1; counts[a]["added"] += len(added); counts[a]["removed"] += len(removed)
                tiles[a].append(tile(img, preds, added, removed, f"{name}  +{len(added)} -{len(removed)}"))
                for kind, bs in (("added", added), ("removed", removed)):
                    for b in bs:
                        rows.append({"arm": a, "frame": name, "what": kind, "color": dtp.COLOR_NAMES[b.color], "bbox": list(b.bbox),
                                     "flags": "+".join(sorted(b.flags)), "source": b.source})
    for a in arms:
        d = OUT / "sheets" / f"rec_{a}"
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.png"):
            old.unlink()
        ts = tiles[a]
        for k in range(0, len(ts), PER_SHEET):
            chunk = ts[k:k + PER_SHEET]
            while len(chunk) % 2:
                chunk.append(np.zeros_like(chunk[0]))
            cv2.imwrite(str(d / f"sheet_{k // PER_SHEET:02d}.png"), np.vstack([np.hstack(chunk[i:i + 2]) for i in range(0, len(chunk), 2)]))
    with (OUT / "recordings.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["arm", "frame", "what", "color", "bbox", "flags", "source"]); w.writeheader(); w.writerows(rows)
    L = ["# Recordings: boxes that appear or disappear against `base`", "",
         f"{len(frames)} unlabeled frames ({', '.join(sorted({p.parent.name for p in frames}))}); adopted color model; `base` draws {base_boxes} boxes.", "",
         "| arm | boxes | frames changed | boxes appearing | boxes disappearing |", "|---|---|---|---|---|"]
    for a in arms:
        c = counts[a]
        L.append(f"| {a} | {c['boxes']} | {c['frames_changed']} | {c['added']} | {c['removed']} |")
    (OUT / "recordings.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
