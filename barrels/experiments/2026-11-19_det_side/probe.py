#!/usr/bin/env python3
"""A viewing aid (no number comes from here): one frame's mask as text, the boxes drawn, and the detector's
reason log, for one arm. Where the mask comes from:

    --level seg            the adopted color model on the photo (CAMPUS as in the eval table, level 3a)
    --level loso           HOME as in the eval table: the color model re-fit without this frame's scene
    --level mask           the hand-made mask (level 1)
    --level dmg:medium:0   the hand-made mask with seeded damage (level 2; name of a severity or of a single damage, seed)
    --level oracle         thresholds read from the frame's own labels (level 3b / 3c)
    --file <png>           an unlabeled frame (a recording), adopted color model

    python barrels/experiments/2026-11-19_det_side/probe.py occl_02 --set CAMPUS --level seg --arm base
Train frames only (the stem is looked up in the train list; a recording is checked against the test list).
Also writes results/2026-11-19_det_side/zoom/<arm>_<level>_<stem>.png (photo | mask, enlarged; ignored by git).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
PREV = HERE.parent / "2026-11-18_det_given_seg"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location("det_given_seg_look", PREV / "look.py")
LOOK = importlib.util.module_from_spec(spec); spec.loader.exec_module(LOOK)
R = LOOK.R
import side_arms  # noqa: E402
from barrels import degrade as dg, detector as det, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-19_det_side" / "zoom"
CH = {0: ".", 1: "o", 2: "B", 255: "?"}


def get_mask(level: str, stem: str, group: str):
    sets = R.train_sets()
    pool = sets[group] if group else [s for v in sets.values() for s in v]
    match = [s for s in pool if stem in s]
    assert len(match) == 1, f"{stem!r} matches {match}"
    s = match[0]
    img = io.load_image(io.find_image(s))
    frame = pl.Frame.from_image(img)
    base = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=R.CAM).model
    if level == "seg":
        mask = pl.segment(frame, base)[0]
    elif level == "loso":
        scene = io.parse_name(s)["scene"]
        others = [h for h in sets["HOME"] if io.parse_name(h)["scene"] != scene and io.mask_path(h).exists()]
        m = pl.fit([pl.Frame.from_image(io.load_image(io.find_image(h))) for h in others], [io.load_mask(io.mask_path(h)) for h in others], base.cfg)
        mask = pl.segment(frame, m)[0]
    elif level == "mask":
        mask = io.load_mask(io.mask_path(s))
    elif level.startswith("dmg:"):
        _, name, seed = level.split(":")
        home = [h for h in sets["HOME"] if io.mask_path(h).exists()]
        boxes = [tuple(g.bbox) for g in R.truth(s)[0]]
        mask = dg.damage(io.load_mask(io.mask_path(s)), boxes, {**dg.SEVERITIES, **dg.SINGLE}[name], seed=1000 * int(seed) + home.index(s))
    elif level == "oracle":
        barrels = io.load_boxes(s)["barrels"]
        lab = R.oracle.with_stripes(img, barrels, R.pooled.body_mask(img, barrels, base.cfg), base.cfg)
        mask = pl.segment(frame, R.oracle.frame_model("hue+sat+stripes", frame, lab, base))[0]
    else:
        raise SystemExit(f"unknown level {level}")
    return s, img, mask, R.truth(s)[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stem", nargs="?", default="")
    ap.add_argument("--set", default="", help="HOME, CAMPUS, BLACK, ... (when the stem text is in several sets)")
    ap.add_argument("--level", default="seg")
    ap.add_argument("--file", default="")
    ap.add_argument("--arm", default="base")
    ap.add_argument("--win", default="", help="x0,y0,x1,y1 of the text window (default: around the truth boxes and the boxes drawn)")
    ap.add_argument("--no-text", action="store_true")
    ap.add_argument("--tilt", type=float, default=0.0, help="detect with this camera tilt in degrees instead of the preset's (a what-if, report only)")
    args = ap.parse_args(argv)
    if args.file:
        p = Path(args.file)
        assert p.stem not in set(splits.load_splits()["test"]), "a test frame"
        img = cv2.imread(str(p))
        mask = pl.segment(pl.Frame.from_image(img), wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=R.CAM).model)[0]
        s, gts, level = f"{p.parent.name}_{p.stem}", [], "rec"
    else:
        s, img, mask, gts = get_mask(args.level, args.stem, args.set)
        level = args.level.replace(":", "-").replace(" ", "")
    log: list = []
    cam = R.CAM.with_(tilt_deg=args.tilt) if args.tilt else R.CAM          # --tilt: a what-if camera for the detector only (report only)
    preds = det.detect(mask, side_arms.ARMS[args.arm], cam, log=log)
    print(s, "|", args.level, "|", args.arm, "|", f"tilt {cam.tilt_deg}, horizon row {cam.horizon_row():.0f}")
    for g in gts:
        print(" truth", g.color, g.bbox, sorted(g.flags))
    for b in preds:
        print(" box  ", b.color, b.bbox, sorted(b.flags), b.source)
    for e in log:
        print("  log ", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items()})
    boxes = [g.bbox for g in gts] + [b.bbox for b in preds]
    if args.win:
        x0, y0, x1, y1 = (int(v) for v in args.win.split(","))
    elif boxes:
        x0, y0 = max(0, min(b[0] for b in boxes) - 6), max(0, min(b[1] for b in boxes) - 6)
        x1, y1 = min(mask.shape[1], max(b[2] for b in boxes) + 6), min(mask.shape[0], max(b[3] for b in boxes) + 6)
    else:
        x0, y0, x1, y1 = 0, 0, 0, 0
    if not args.no_text and x1 > x0:
        print(f"mask, columns {x0} to {x1 - 1} (o orange, B blue):")
        for r in range(y0, y1):
            print(f"{r:4d} " + "".join(CH[int(v)] for v in mask[r, x0:x1]))
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{args.arm}_{level}_{s.replace('4A8B_', '')}.png"
    cv2.imwrite(str(path), LOOK.render(img, mask, gts, preds, log))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
