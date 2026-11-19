#!/usr/bin/env python3
"""A census before the fix (no acceptance number comes from here): the top and bottom edges of the boxes the
baseline draws from a stripe.

A stripe's row gives the barrel's distance, hence where its top and bottom must be. ``barrel_from_stripe`` uses the
seen end of the body color when it agrees with that (15 % of the height, at least 4 px), else draws the predicted
edge and flags it (``top_inferred`` / ``bottom_inferred``). Two questions:

1. How often is NEITHER edge seen where the stripe's row predicts it (both flags), on right boxes and on wrong ones?
2. When the seen bottom is kept: what lies right under it, in the stripe's columns? Table, or the other barrel color
   (another barrel standing in front)? And which is nearer the hand-drawn bottom there: the seen end or the predicted?

Sets: HOME as in the eval table, CAMPUS, the HOME hand masks under medium and heavy damage (5 seeds), the scorecard's
scenes (``run.py``), and with --rec the unlabeled recordings (no truth: counts only).

    python barrels/experiments/2026-11-19_det_occl/edge_census.py [--rec <data/recordings>]
Output: results/2026-11-19_det_occl/edge_census.md
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("det_occl_run", HERE / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
from barrels import degrade as dg, detect_types as dtp, detector as det, eval_det as ed, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

CFG = R.occl_arms.BASE
UNDER_ROWS = 4            # "right under the seen bottom" = the next rows, this many (the 3-row gap the body walk allows, + 1)


def under_is_barrel(mask, body: int, x0: int, x1: int, bottom: int) -> float:
    """Share of the stripe's columns that hold the OTHER barrel color in the UNDER_ROWS rows under ``bottom``."""
    other = BLUE if body == ORANGE else ORANGE
    band = mask[bottom:bottom + UNDER_ROWS, x0:x1]
    return float((band == other).any(axis=0).mean()) if band.size else 0.0


def stripe_boxes(mask):
    """(barrel, stripe, predicted rows) for every box the baseline draws from a stripe (its log's kept entries)."""
    log: list = []
    preds = det.detect(mask, CFG, R.CAM, log=log)
    stripes = det.find_stripes(mask, R.CAM, CFG)
    out = []
    for e in log:
        if e["stage"] == "barrel" and e["why"] == "kept":
            b = next((p for p in preds if p.source == "det2" and tuple(p.bbox) == tuple(e["box"]) and p.color == e["body"]), None)
            s = next((s for s in stripes if tuple(s.bbox) == tuple(e["bbox"]) and s.body == e["body"]), None)
            if b is not None and s is not None:
                out.append((b, s, det._stripe_geometry(R.CAM, s.center_row)[1]))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rec", default="")
    args = ap.parse_args(argv)
    stems = R.train_stems()
    segs = R.segmentations(stems)
    pools, _ = R.build_sources(segs)
    items = []                                           # (set, mask, truths [(color, box)] or None)
    for name, pool in (("HOME (eval table)", "HOME color model"), ("CAMPUS", "CAMPUS color model")):
        for s, m in segs[pool].items():
            items.append((name, m, [(g.color, g.bbox) for g in dtp.barrels_from_boxes(io.load_boxes(s))]))
    home = sorted(segs["HOME hand masks"])
    for sev in ("medium", "heavy"):
        for seed in range(5):
            for i, s in enumerate(home):
                gts = dtp.barrels_from_boxes(io.load_boxes(s))
                items.append((f"HOME hand masks, {sev} damage", dg.damage(segs["HOME hand masks"][s], [tuple(g.bbox) for g in gts], dg.SEVERITIES[sev], seed=1000 * seed + i),
                              [(g.color, g.bbox) for g in gts]))
    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            items.append((f"scorecard: {R.ROW_NAME[key]}" if key.startswith("barrel") else "scorecard: every kind without a barrel in front", sc.mask,
                          [sc.target] + list(sc.fronts)))
    if args.rec:
        model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=R.CAM).model
        test = set(splits.load_splits()["test"])
        for p in sorted(Path(args.rec).rglob("*.png")):
            assert p.stem not in test
            img = cv2.imread(str(p))
            if img is not None:
                items.append((f"recording {p.parent.parent.name.split('_')[-1]}", pl.segment(pl.Frame.from_image(img), model)[0], None))

    n = collections.defaultdict(collections.Counter)
    errs = collections.defaultdict(lambda: {"seen": [], "pred": []})
    for name, mask, truths in items:
        for b, s, rows in stripe_boxes(mask):
            both = {"top_inferred", "bottom_inferred"} <= set(b.flags)
            right = None if truths is None else any(c == b.color and ed.box_iou(b.bbox, t) >= 0.5 for c, t in truths)
            kind = "no truth" if right is None else ("right" if right else "wrong")
            n[name][f"boxes {kind}"] += 1
            if both:
                n[name][f"both inferred {kind}"] += 1
                # the seen top of the body in the stripe's columns: does it end against the other barrel color?
                top_seen = det._body_extent(mask, s.body, s.bbox[0], s.bbox[2], s.bbox[1], s.bbox[3])[0]
                other = BLUE if s.body == ORANGE else ORANGE
                band = mask[max(0, top_seen - UNDER_ROWS):top_seen, s.bbox[0]:s.bbox[2]]
                if band.size and float((band == other).any(axis=0).mean()) >= 0.5:
                    n[name][f"both inferred, top against barrel color {kind}"] += 1
            if "bottom_inferred" not in b.flags and b.bbox[3] < mask.shape[0]:
                on = under_is_barrel(mask, b.color, s.bbox[0], s.bbox[2], b.bbox[3]) >= 0.5
                n[name][f"seen bottom on {'barrel color' if on else 'table'} {kind}"] += 1
                if on and right:
                    c, t = max(((c, t) for c, t in truths if c == b.color), key=lambda ct: ed.box_iou(b.bbox, ct[1]))
                    errs[name]["seen"].append(b.bbox[3] - t[3]); errs[name]["pred"].append(rows.bottom - t[3])

    def cnt(c, key):
        return " / ".join(str(c[f"{key} {k}"]) for k in ("right", "wrong", "no truth"))

    L = ["# The top and bottom edges of the boxes drawn from a stripe (a census of the baseline; no acceptance number)", "",
         "Counts are right / wrong / no truth: a box is `right` when it overlaps a true barrel of its color by half or more (IoU; the bottom is not asked here).", "",
         "| set | boxes from a stripe | neither edge seen where the stripe predicts it | ... and the seen top ends against the other barrel color | seen bottom kept, table under it | seen bottom kept, the other barrel color under it |",
         "|---|---|---|---|---|---|"]
    for name, c in n.items():
        L.append(f"| {name} | {cnt(c, 'boxes')} | {cnt(c, 'both inferred')} | {cnt(c, 'both inferred, top against barrel color')} | {cnt(c, 'seen bottom on table')} | "
                 f"{cnt(c, 'seen bottom on barrel color')} |")
    L += ["", "Where a kept seen bottom has the other barrel color under it (right boxes): the seen bottom and the bottom the stripe's row predicts, "
          "minus the true bottom, px (median; 10th to 90th percentile; n):", "", "| set | seen bottom | predicted bottom |", "|---|---|---|"]
    for name, e in errs.items():
        if e["seen"]:
            def st(v):
                v = np.asarray(v, float)
                return f"{np.median(v):+.1f} ({np.percentile(v, 10):+.1f} to {np.percentile(v, 90):+.1f}; n {len(v)})"
            L.append(f"| {name} | {st(e['seen'])} | {st(e['pred'])} |")
    (R.OUT / "edge_census.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
