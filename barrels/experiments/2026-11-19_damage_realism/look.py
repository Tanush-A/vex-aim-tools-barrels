#!/usr/bin/env python3
"""A viewing aid (no number comes from here): the barrels of one measured set that are worst by one field of
``per_box.csv`` or ``per_barrel.csv``, each as photo | what the color model paints (the rest dimmed), enlarged, with
the hand-drawn box.

    python barrels/experiments/2026-11-19_damage_realism/look.py CAMPUS mid_hole_w            # the 8 largest
    python barrels/experiments/2026-11-19_damage_realism/look.py CAMPUS core_cov --low -n 6   # the 6 smallest
    python barrels/experiments/2026-11-19_damage_realism/look.py "HOME, leave-one-scene-out" lost --csv per_barrel.csv
Writes results/2026-11-19_damage_realism/look/<set>_<field>.png (ignored by git) and prints the rows.
Train frames only (the csv holds nothing else; asserted).
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
from barrels import cv as bcv, geometry as geo, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-19_damage_realism"
CAM = geo.AIM_4A8B6118_BOXFIT
PADPX, TILE_H = 8, 260


def segment(stem: str, loso: bool) -> np.ndarray:
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    if loso:                                              # HOME as the eval table segments it
        sp = splits.load_splits()
        home = [s for s in sorted(sp["train"]) if s.startswith("4A8B_window_light_") and io.mask_path(s).exists()]
        fold = next(f for f in bcv.loso_folds(home, {s: io.parse_name(s)["scene"] for s in home}) if stem in f.held_out)
        model = pl.fit([pl.Frame.from_image(io.load_image(io.find_image(s))) for s in fold.train], [io.load_mask(io.mask_path(s)) for s in fold.train], model.cfg)
    return pl.segment(pl.Frame.from_image(io.load_image(io.find_image(stem))), model)[0]


def tile(img: np.ndarray, mask: np.ndarray, box, text: str) -> np.ndarray:
    x0, y0, x1, y1 = box
    a, b, c, d = max(0, x0 - PADPX), max(0, y0 - PADPX), min(640, x1 + PADPX), min(480, y1 + PADPX)
    photo = img[b:d, a:c].copy()
    paint = (photo * 0.35).astype(np.uint8)
    m = mask[b:d, a:c]
    paint[m == ORANGE] = (0, 140, 255)
    paint[m == BLUE] = (255, 90, 0)
    s = TILE_H / photo.shape[0]
    both = []
    for p in (photo, paint):
        p = cv2.resize(p, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)
        cv2.rectangle(p, (int((x0 - a) * s), int((y0 - b) * s)), (int((x1 - a) * s) - 1, int((y1 - b) * s) - 1), (255, 255, 255), 1)
        both.append(p)
    t = np.hstack(both)
    head = np.zeros((34, t.shape[1], 3), np.uint8)
    for i, line in enumerate(text.split("\n")):
        cv2.putText(head, line, (3, 13 + 15 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
    return np.vstack([head, t])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source"); ap.add_argument("field")
    ap.add_argument("--csv", default="per_box.csv")
    ap.add_argument("--low", action="store_true", help="the smallest values instead of the largest")
    ap.add_argument("-n", type=int, default=8)
    args = ap.parse_args(argv)
    test = set(splits.load_splits()["test"])
    rows = [r for r in csv.DictReader((OUT / args.csv).open()) if r["source"] == args.source and r.get(args.field, "") not in ("", "nan")]
    rows.sort(key=lambda r: float(r[args.field]), reverse=not args.low)
    tiles = []
    for r in rows[:args.n]:
        assert r["stem"] not in test, "a test frame"
        b = next(b for b in io.load_boxes(r["stem"])["barrels"] if str(b["id"]) == r["id"])
        short = r["stem"].replace("4A8B_", "")
        print(short, r["id"], r["color"], b["bbox"], {k: v for k, v in r.items() if k not in ("source", "stem", "tag", "id", "color")})
        mask = segment(r["stem"], loso="leave-one" in args.source)
        tiles.append(tile(io.load_image(io.find_image(r["stem"])), mask, b["bbox"], f"{short} #{r['id']} {r['color']}\n{args.field} {float(r[args.field]):.2f}  W {r['W']} H {r['H']}"))
    w = max(t.shape[1] for t in tiles)
    tiles = [np.hstack([t, np.zeros((t.shape[0], w - t.shape[1], 3), np.uint8)]) for t in tiles]
    per_row = 4
    grid = [np.hstack(tiles[i:i + per_row] + [np.zeros_like(tiles[0])] * (per_row - len(tiles[i:i + per_row]))) for i in range(0, len(tiles), per_row)]
    (OUT / "look").mkdir(parents=True, exist_ok=True)
    path = OUT / "look" / f"{args.source.split(',')[0].replace(' ', '-')}_{args.field}{'_low' if args.low else ''}.png"
    cv2.imwrite(str(path), np.vstack(grid))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
