#!/usr/bin/env python3
"""Where do v1's errors come from? Attribute every missed / false pixel of the final config's LOSO-CV
predictions to a stage or a location, and re-check the table prior on the non-close frames.

    python barrels/experiments/2026-10-22_error_attribution/run.py [--config cfg.json]

Misses (GT barrel, predicted other/other class) are attributed in pipeline order: above horizon,
brightness gate, saturation floor, wall prior, outside the class box, tie rule. False pixels
(predicted barrel, GT other) are split into: within 4 px of a true barrel (boundary halo), in a hand
frame and far from barrels, or elsewhere (shadows/reflections/clutter).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE.parent / "2026-10-20_v1_rgbbox"))
from barrels import boxfit as bf, cv, io, pipeline as pl  # noqa: E402
from run import load_pool  # noqa: E402

FINAL = io.PKG_ROOT / "results" / "2026-10-20_v1_adaptive_cv" / "configs" / "afd85483.json"
HAND = ("core_03", "far_02")


def attribute(frame: pl.Frame, gt: np.ndarray, pred: np.ndarray, model: pl.Model) -> dict:
    cfg = model.cfg
    keep_fixed = pl._fixed_keep(frame, cfg)
    smin, _ = pl.effective_s_min(frame, cfg)
    info = {}
    keep_prior = pl._prior_keep(frame, cfg, info, smin[io.ORANGE])
    out = {}
    for c, nm in ((io.ORANGE, "orange"), (io.BLUE, "blue")):
        miss = (gt == c) & (pred != c)
        reasons = {}
        above = miss & (np.arange(frame.shape[0])[:, None] < (cfg.horizon_row or 0))
        reasons["above horizon"] = int(above.sum()); rem = miss & ~above
        dark = rem & (frame.val < cfg.v_min); reasons["brightness gate"] = int(dark.sum()); rem &= ~dark
        low = rem & (frame.sat < smin[c]); reasons["saturation floor"] = int(low.sum()); rem &= ~low
        wall = rem & ~keep_prior; reasons["wall prior"] = int(wall.sum()); rem &= ~wall
        outbox = rem & ~bf.in_box(frame.features(cfg.box_space), model.boxes[c]); reasons["outside class box"] = int(outbox.sum()); rem &= ~outbox
        reasons["lost tie to other class"] = int(rem.sum())
        fp = (pred == c) & (gt == io.OTHER)
        near = cv2.dilate(np.isin(gt, (io.ORANGE, io.BLUE)).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        fp_kinds = {"boundary halo (≤4 px from a barrel)": int((fp & near).sum()), "elsewhere": int((fp & ~near).sum())}
        out[nm] = {"n_gt": int((gt == c).sum()), "missed": reasons, "false": fp_kinds, "s_min_eff": smin[c],
                   "false_px_stats": None}
        if (fp & ~near).sum() > 20:
            px = frame.rgb[fp & ~near]
            out[nm]["false_px_stats"] = {"median_rgb": np.median(px, 0).astype(int).tolist(), "median_sat": int(np.median(frame.sat[fp & ~near])), "n": int((fp & ~near).sum())}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=FINAL)
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)
    cfg = pl.Config.from_dict(json.load(args.config.open()))
    ds = load_pool(); folds = cv.loso_folds(ds.stems, ds.scene)
    res = cv.cross_validate(ds, cfg, folds)
    model_of = {s: res.fold_models[f.name] for f in folds for s in f.held_out}
    out = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_error_attribution")
    per = {s: attribute(ds.frames[s], ds.masks[s], res.preds[s], model_of[s]) for s in ds.stems}
    json.dump(per, (out / "attribution.json").open("w"), indent=1)

    md = [f"# Error attribution, final config `{cfg.short_hash()}`, LOSO-CV predictions on the 16 pool frames", ""]
    for nm in ("orange", "blue"):
        tot_gt = sum(p[nm]["n_gt"] for p in per.values())
        miss = {}; fp = {}
        for s, p in per.items():
            for k, v in p[nm]["missed"].items(): miss[k] = miss.get(k, 0) + v
            for k, v in p[nm]["false"].items():
                key = k if k.startswith("boundary") else ("hand frame, elsewhere" if s.endswith(HAND) else "elsewhere (shadow / reflection / clutter)")
                fp[key] = fp.get(key, 0) + v
        md += [f"## {nm}: {tot_gt} labeled pixels", "", "| missed because | pixels | % of labeled |", "|---|---|---|"]
        for k, v in miss.items(): md.append(f"| {k} | {v} | {v / tot_gt * 100:.1f} % |")
        md += ["", "| false pixels | pixels | % of labeled |", "|---|---|---|"]
        for k, v in fp.items(): md.append(f"| {k} | {v} | {v / tot_gt * 100:.1f} % |")
        md.append("")
    md += ["## Per frame", "", "| frame | floor | orange: missed (floor / wall / box) · false (halo / elsewhere) | blue: missed (floor / wall / box) · false (halo / elsewhere) | 'elsewhere' false pixels look like |", "|---|---|---|---|---|"]
    for s, p in per.items():
        o, b = p["orange"], p["blue"]
        look = "; ".join(f"{nm} {st['median_rgb']} sat {st['median_sat']} (n={st['n']})" for nm, st in (("o", o["false_px_stats"]), ("b", b["false_px_stats"])) if st)
        md.append(f"| {s[17:]} | {o['s_min_eff']} | {o['missed']['saturation floor']} / {o['missed']['wall prior']} / {o['missed']['outside class box']} · {o['false']['boundary halo (≤4 px from a barrel)']} / {o['false']['elsewhere']} | "
                  f"{b['missed']['saturation floor']} / {b['missed']['wall prior']} / {b['missed']['outside class box']} · {b['false']['boundary halo (≤4 px from a barrel)']} / {b['false']['elsewhere']} | {look} |")

    # table prior on the non-close frames (primary already excludes top/topstripe)
    md += ["", "## Table prior back on (band floor config), LOSO CV — primary excludes the two close/top-only frames", "", "| k_table | primary | orange IoU | blue IoU | top/topstripe orange IoU |", "|---|---|---|---|---|"]
    for k in (None, 1.5, 2.0, 2.5, 3.0):
        c = cfg if k is None else pl.with_overrides(cfg, table_prior=True, k_table=k)
        sc = cv.cross_validate(ds, c, folds).score()
        md.append(f"| {'off' if k is None else k} | {sc['primary']:.3f} | {sc['iou_o']:.3f} | {sc['iou_b']:.3f} | {sc['oos_iou_o']:.3f} |")
    (out / "summary.md").write_text("\n".join(md) + "\n"); print("\n".join(md)); print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
