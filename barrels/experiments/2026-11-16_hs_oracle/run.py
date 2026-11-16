#!/usr/bin/env python3
"""A ceiling check before any per-image threshold method is designed: if the thresholds of every frame were set
**perfectly, from that frame's own labels**, how many barrels would today's detector find?

This is not a method (it reads the answer). It says how much a per-image threshold estimator could gain at best,
with the model kept as it is (one hue sector + one saturation floor per color) and the detector unchanged.

Written before the run. Hypothesis: with per-frame thresholds the black table and the bright wood frames go from
9 of 152 barrels found to well over half; if they stay low, per-image thresholds are not the lever and the
detector's own tests are (the reason log of 2026-11-16 points at stripes broken by highlights).

Arms (per frame, per color that has an unoccluded box in the frame; otherwise the adopted range is kept):
  base      the adopted model, the same for every frame.
  hue       hue sector from this frame's body pixels (5th to 95th percentile, widened by 2); S floor as adopted.
  hue+sat   the adopted recipe on this frame alone: S floor = 5th (orange) / 15th (blue) percentile of the body
            pixels' S, hue sector from the pixels above it.
Body pixels: home masks; elsewhere the box cores at the class's hue peak (as in 2026-11-16_hs_pooled, run 2).
Train frames only; test frames are never opened.

    python barrels/experiments/2026-11-16_hs_oracle/run.py
Outputs: results/2026-11-16_hs_oracle/ — summary.md, config.json, sheets/ (ignored).
"""
from __future__ import annotations

import collections
import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import boxfit as bf, cv as bcv, detect_types as dtp, detector as det, eval_det as ed, io, pipeline as pl, report as rp, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

_spec = importlib.util.spec_from_file_location("pooled", HERE.parent / "2026-11-16_hs_pooled" / "run.py")
pooled = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(pooled)
_spec = importlib.util.spec_from_file_location("att", HERE.parent / "2026-11-11_occl_attribution" / "run.py")
att = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(att)

OUT = PKG_ROOT / "results" / "2026-11-16_hs_oracle"
ARMS = ("base", "hue", "hue+sat")
MIN_PX = 200


def frame_model(arm: str, frame: pl.Frame, mask: np.ndarray, base: pl.Model) -> pl.Model:
    if arm == "base":
        return base
    cfg = base.cfg
    keep = pl._fixed_keep(frame, cfg)
    boxes = dict(base.boxes)
    for c in (ORANGE, BLUE):
        f = frame.hs(pl.HUE_SHIFT[c])[(mask == c) & keep]
        if len(f) < MIN_PX:
            continue
        if arm == "hue":
            s_lo = base.boxes[c].lo[1]
        else:
            s_lo = float(np.percentile(f[:, 1], cfg.hs_s_pct[0 if c == ORANGE else 1]))
        hh_ = f[f[:, 1] >= s_lo, 0]
        if len(hh_) < 50:
            hh_ = f[:, 0]
        h_lo, h_hi = (float(np.percentile(hh_, q)) for q in cfg.hs_h_pct)
        boxes[c] = bf.Box((h_lo - cfg.hs_h_margin, s_lo), (h_hi + cfg.hs_h_margin, 255.0))
    return dataclasses.replace(base, boxes=boxes)


def main() -> int:
    (OUT / "sheets").mkdir(parents=True, exist_ok=True)
    base = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=pooled.CAM).model
    data = pooled.Data(base.cfg)
    dcfg = det.DetConfig()
    res = {a: {} for a in ARMS}
    masks = {a: {} for a in ARMS}
    causes = {a: collections.Counter() for a in ARMS}
    for s in data.stems:
        label = io.load_boxes(s)
        gts = dtp.barrels_from_boxes(label)
        for a in ARMS:
            m = frame_model(a, data.frame[s], data.mask[s], base)
            mk = pl.segment(data.frame[s], m)[0]
            masks[a][s] = mk
            res[a][s] = rp.score_frame(s, mk, dcfg, pooled.CAM)
            if data.group[s] in pooled.TARGET:
                log: list = []
                preds = det.detect(mk, dcfg, pooled.CAM, log=log)
                pairs = ed.match_best_first(preds, gts, lambda p, g: ed.box_iou(p.bbox, g.bbox), ed.IOU_THR, same_class=True,
                                            eligible=lambda p, g: ed.bottom_within_tol(p, g))
                hit = {gi for _, gi, _ in pairs}
                for gi, g in enumerate(gts):
                    if gi not in hit:
                        causes[a][att.attribute(g, preds, log, att.inside(mk, g))[0]] += 1
    L = ["# Ceiling check: per-frame thresholds set from the frame's own labels", "",
         f"git {bcv.git_hash()}; v2 rule; train frames only; today's detector. Not a method: the thresholds read the answer.", "",
         "## Found / barrels (false boxes), score", "", "| set | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
    rows = list(pooled.GROUPS)
    lights = sorted({io.parse_name(s)["light"] for s in data.stems if data.group[s] == "WOOD bright"})
    def cell(stems, a):
        c = rp.summarize([res[a][s] for s in stems])
        sc = "-" if c.score != c.score else f"{c.score:.2f}"
        return f"{c.found} / {c.barrels} ({c.false}), {sc}"
    for g in rows:
        L.append(f"| {g} | " + " | ".join(cell([s for s in data.stems if data.group[s] == g], a) for a in ARMS) + " |")
    for lt in lights:
        L.append(f"|   wood {lt.replace('lamp', '')} | " + " | ".join(cell([s for s in data.stems if io.parse_name(s)['light'] == lt and data.group[s] == 'WOOD bright'], a) for a in ARMS) + " |")
    scenes = sorted({data.scene[s] for s in data.stems if data.group[s] in pooled.TARGET})
    L += ["", "## Black + bright wood, by scene tag", "", "| scene | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
    for sc in scenes:
        L.append(f"| {sc} | " + " | ".join(cell([s for s in data.stems if data.scene[s] == sc and data.group[s] in pooled.TARGET], a) for a in ARMS) + " |")
    L += ["", "## Why the remaining barrels on black + bright wood are missed (the detector's reason log)", ""]
    for a in ARMS:
        L.append(f"- `{a}`: " + ", ".join(f"{k} {v}" for k, v in causes[a].most_common()))
    (OUT / "summary.md").write_text("\n".join(L) + "\n")
    json.dump({"git": bcv.git_hash(), "arms": ARMS, "min_px": MIN_PX, "frames": data.stems}, (OUT / "config.json").open("w"), indent=1)
    for a in ("hue", "hue+sat"):
        cv2.imwrite(str(OUT / "sheets" / f"{a}_black.png"), pooled.sheet([s for s in data.stems if data.group[s] == "BLACK"], data, masks[a], a))
        cv2.imwrite(str(OUT / "sheets" / f"{a}_wood.png"), pooled.sheet(pooled.SHEET_WOOD, data, masks[a], a))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
