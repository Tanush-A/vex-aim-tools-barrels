#!/usr/bin/env python3
"""A census of the partly hidden stripes (a look at the baseline; no acceptance number comes from here): on the
judged frames, every stripe the finder returns that is narrower than ``stripe_full`` x a barrel, with what the
side rule of ``barrel_from_stripe`` sees: the stripe's width as a fraction of the barrel, the pixel left and right
of it at its middle row (what today's rule reads), the columns of the body joined to it, the box drawn, and (on
labeled frames) the best overlap with a hand-drawn box of that color.

It answers two questions before the side rule is changed: which barrels found today lean on the present rule, and
what the stripe and the body look like at a barrel's real edge and at a hidden one.

    python barrels/experiments/2026-11-19_det_side/census.py [--arm base] [--floor 0.2] [--rec <data/recordings>]
Sets: HOME as in the eval table (leave-one-scene-out), HOME hand masks, CAMPUS, BLACK and wood-cool with label
thresholds; with --rec also the unlabeled recordings. Train frames only.
Output: results/2026-11-19_det_side/census_<arm>.csv and the same as text.
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import importlib.util
import sys
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
PREV = HERE.parent / "2026-11-18_det_given_seg"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location("det_given_seg_run", PREV / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_given_seg_run"] = R; spec.loader.exec_module(R)
import side_arms  # noqa: E402
from barrels import cv as bcv, detector as det, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-19_det_side"
NAME = {0: ".", ORANGE: "o", BLUE: "B", 255: "?"}


def frames(rec: str):
    """(set, stem, mask, truth barrels or None)."""
    sets = R.train_sets()
    base = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=R.CAM).model
    home = [s for s in sets["HOME"] if io.mask_path(s).exists()]
    fr = {s: pl.Frame.from_image(io.load_image(io.find_image(s))) for s in home}
    scenes = {s: io.parse_name(s)["scene"] for s in home}
    for fold in bcv.loso_folds(home, scenes):
        m = pl.fit([fr[s] for s in fold.train], [io.load_mask(io.mask_path(s)) for s in fold.train], base.cfg)
        for s in fold.held_out:
            yield "HOME loso", s, pl.segment(fr[s], m)[0], R.truth(s)[0]
    for s in home:
        yield "HOME mask", s, io.load_mask(io.mask_path(s)), R.truth(s)[0]
    for s in sets["CAMPUS"]:
        yield "CAMPUS", s, pl.segment(pl.Frame.from_image(io.load_image(io.find_image(s))), base)[0], R.truth(s)[0]
    scen, _ = R.build_scenarios(sets)
    for sc in scen:
        if sc.level in ("3b", "3c"):
            for s, _, mask in sc.items:
                yield ("BLACK oracle" if sc.level == "3b" else "WOOD oracle"), s, mask, R.truth(s)[0]
    if rec:
        test = set(splits.load_splits()["test"])
        for p in sorted(Path(rec).rglob("*.png")):
            assert p.stem not in test
            img = cv2.imread(str(p))
            if img is not None:
                yield f"REC {p.parent.name}", p.stem, pl.segment(pl.Frame.from_image(img), base)[0], None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", default="base")
    ap.add_argument("--floor", type=float, default=0.2, help="stripe_w_min used for the census (the finder's floor), default 0.2")
    ap.add_argument("--rec", default="")
    args = ap.parse_args(argv)
    cfg = dataclasses.replace(side_arms.ARMS[args.arm], stripe_w_min=args.floor)
    rows = []
    for group, stem, mask, gts in frames(args.rec):
        h, w = mask.shape
        stripes = det.find_stripes(mask, R.CAM, cfg)
        for s in stripes:
            g = det._stripe_geometry(R.CAM, s.center_row)
            if g is None:
                continue
            W = g[1].width_px
            x0, y0, x1, y1 = s.bbox
            if (x1 - x0) >= cfg.stripe_full * W:
                continue
            others = tuple((o.bbox[0], o.bbox[2]) for o in stripes if o is not s)
            b = det.barrel_from_stripe(s, mask, R.CAM, cfg, others=others)
            row = int(s.center_row)
            top, bottom = max(0, int(round(g[1].top))), min(h, int(round(g[1].bottom)))
            cx0, cx1 = det._body_columns(mask, s.body, x0, x1, top, bottom, y0, y1, cap_px=float("inf"), others=others)
            iou = max((det.box_iou(b.bbox, t.bbox) for t in gts if t.color == s.body), default=0.0) if (b and gts is not None) else ""
            rows.append({"set": group, "stem": stem.replace("4A8B_", ""), "body": NAME[s.body], "stripe": list(s.bbox), "W": round(W, 1),
                         "stripe_w": round((x1 - x0) / W, 2), "left_px": "edge" if x0 <= 0 else NAME[int(mask[row, x0 - 1])],
                         "right_px": "edge" if x1 >= w else NAME[int(mask[row, x1])], "body_cols": [cx0, cx1], "body_w": round((cx1 - cx0) / W, 2),
                         "box": list(b.bbox) if b else "refused", "best_iou": round(iou, 2) if iou != "" else ""})
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"census_{args.arm}.csv").open("w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    for r in rows:
        print(" | ".join(f"{k} {v}" for k, v in r.items()))
    print(len(rows), "stripes narrower than stripe_full")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
