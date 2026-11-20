#!/usr/bin/env python3
"""The stencil's shape, measured on the hand-made HOME train masks (PREREG.md, "The stencil").

For every barrel of the HOME train frames that has a hand mask, no flag, and whose box overlaps no other box by more
than 2 columns: the stripe's rows are read off the mask (centre third of the columns, rows where more than half is
stripe color); the camera model is asked for the barrel whose stripe centre is at that row; and the hand-drawn box
is compared with the model's rows. Then every such barrel is resampled to one grid (upper body, stripe and lower
body each to 24 rows, the width to 24 columns) and averaged: the mean barrel.

Chosen here, each by a rule written before the numbers were seen (PREREG.md):
  top_fit, bottom_fit   box row - model row, as a + b x width: the straight line if, leaving one scene out at a
                        time, it predicts the left-out barrels better than the median does by more than 10 % (RMSE);
                        else the median alone.
  seam                  (1 - the 10th percentile of [stripe height in the mask / the model's]) / 2
  rim                   the share of the width, each side, where the mean barrel's first 1/8 of upper-body rows
                        and last 1/8 of lower-body rows are less than half painted
  rim_top, rim_bottom   in those columns, the share of the upper body's rows (from the top) / of the lower body's
                        rows (from the bottom) that are less than half painted

Train frames only; a test frame is never opened (asserted).

    python barrels/experiments/2026-11-20_stencil/fit_stencil.py
Outputs: results/2026-11-20_stencil/fit.md, fit.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, detect_types as dtp, geometry as geo, io, splits  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_stencil"
CAM = geo.AIM_4A8B6118_BOXFIT
N = 24
PAD = 4


def home_masks() -> dict[str, np.ndarray]:
    sp = splits.load_splits()
    test = set(sp["test"])
    stems = [s for s in sorted(sp["train"]) if s.startswith("4A8B_window_light_") and io.mask_path(s).exists() and io.boxes_path(s).exists()]
    assert not set(stems) & test, "a test frame leaked in"
    return {s: io.load_mask(io.mask_path(s)) for s in stems}


def measure(masks) -> tuple[list[dict], np.ndarray, np.ndarray]:
    rows, body, stripe = [], np.zeros((3 * N, N)), np.zeros((3 * N, N))
    for s, m in masks.items():
        bs = io.load_boxes(s)["barrels"]
        for i, b in enumerate(bs):
            x0, y0, x1, y1 = b["bbox"]
            if b.get("flags") or any(min(x1, o["bbox"][2]) - max(x0, o["bbox"][0]) > 2 and min(y1, o["bbox"][3]) > max(y0, o["bbox"][1])
                                     for j, o in enumerate(bs) if j != i):
                continue
            c = dtp.COLOR_BY_NAME[b["color"]]
            o = io.BLUE if c == io.ORANGE else io.ORANGE
            w = x1 - x0
            centre = m[max(0, y0 - PAD):y1 + PAD, x0 + w // 3:x1 - w // 3]
            sr = np.where((centre == o).mean(axis=1) > 0.5)[0]
            if len(sr) == 0:
                continue
            st, sb = int(sr.min()) + max(0, y0 - PAD), int(sr.max()) + 1 + max(0, y0 - PAD)
            d = CAM._d_axis_from_point_row((st + sb) / 2, geo.BARREL_HEIGHT_MM / 2, -geo.BARREL_BULGE_DIAMETER_MM / 2)
            r = CAM.barrel_rows(d)
            rows.append({"stem": s, "scene": io.parse_name(s)["scene"] + "_" + io.parse_name(s)["nn"], "color": b["color"], "bbox": [x0, y0, x1, y1],
                         "stripe_rows": [st, sb], "model_width": round(r.width_px, 1), "top_res": round(y0 - r.top, 2), "bottom_res": round(y1 - r.bottom, 2),
                         "width_ratio": round(w / r.width_px, 3), "stripe_h_ratio": round((sb - st) / (r.stripe_bottom - r.stripe_top), 3)})

            def samp(a, z, n):
                return (a + (np.arange(n) + 0.5) * (z - a) / n).astype(int)
            patch = m[np.ix_(np.concatenate([samp(y0, st, N), samp(st, sb, N), samp(sb, y1, N)]), samp(x0, x1, N))]
            body += patch == c; stripe += patch == o
    return rows, body / len(rows), stripe / len(rows)


def line_or_median(rows: list[dict], key: str) -> tuple[tuple[float, float], dict]:
    """(a, b) of residual = a + b x width, by the rule in the module text; and the numbers behind the choice."""
    w = np.array([r["model_width"] for r in rows]); y = np.array([r[key] for r in rows])
    scenes = sorted({r["scene"] for r in rows})
    e_med, e_lin = [], []
    for sc in scenes:
        tr = np.array([r["scene"] != sc for r in rows])
        if tr.sum() < 3 or (~tr).sum() == 0:
            continue
        b, a = np.polyfit(w[tr], y[tr], 1)
        e_lin += list(y[~tr] - (a + b * w[~tr])); e_med += list(y[~tr] - np.median(y[tr]))
    rm, rl = float(np.sqrt(np.mean(np.square(e_med)))), float(np.sqrt(np.mean(np.square(e_lin))))
    b, a = np.polyfit(w, y, 1)
    use_line = rl < 0.9 * rm
    fit = (round(float(a), 2), round(float(b), 4)) if use_line else (round(float(np.median(y)), 2), 0.0)
    return fit, {"median": round(float(np.median(y)), 2), "line": [round(float(a), 2), round(float(b), 4)], "loso_rmse_median": round(rm, 2),
                 "loso_rmse_line": round(rl, 2), "chosen": "line" if use_line else "median"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    masks = home_masks()
    rows, body, stripe = measure(masks)
    top_fit, top_info = line_or_median(rows, "top_res")
    bottom_fit, bottom_info = line_or_median(rows, "bottom_res")
    sh = np.array([r["stripe_h_ratio"] for r in rows])
    seam = round(float((1 - np.percentile(sh, 10)) / 2), 2)
    # the rim: columns where the first 1/8 of the upper body and the last 1/8 of the lower body are under half painted
    e = N // 8
    corner = (body[:e].mean(axis=0) + body[-e:].mean(axis=0)) / 2
    thin = corner < 0.5
    rim_cols = (int(np.argmax(~thin)) + int(np.argmax(~thin[::-1]))) / 2
    rim = round(rim_cols / N, 3)
    k = max(1, int(round(rim_cols)))
    rim_u = (body[:N, :k].mean(axis=1) + body[:N, -k:].mean(axis=1)) / 2
    rim_l = (body[2 * N:, :k].mean(axis=1) + body[2 * N:, -k:].mean(axis=1)) / 2
    rim_top = round(float(np.argmax(rim_u >= 0.5)) / N, 3)
    rim_bottom = round(float(np.argmax(rim_l[::-1] >= 0.5)) / N, 3)
    fit = {"git": bcv.git_hash(), "camera": "AIM_4A8B6118_BOXFIT", "barrels": len(rows), "frames": sorted(masks),
           "top_fit": list(top_fit), "bottom_fit": list(bottom_fit), "seam": seam, "rim": rim, "rim_top": rim_top, "rim_bottom": rim_bottom,
           "top_info": top_info, "bottom_info": bottom_info, "stripe_h_ratio": {"median": float(np.median(sh)), "p10": float(np.percentile(sh, 10))},
           "width_ratio": {"median": float(np.median([r["width_ratio"] for r in rows])), "min": min(r["width_ratio"] for r in rows),
                           "max": max(r["width_ratio"] for r in rows)}, "per_barrel": rows}
    (OUT / "fit.json").write_text(json.dumps(fit, indent=1) + "\n")
    L = ["# The stencil's shape, measured on the HOME hand masks", "",
         f"git {fit['git']}; camera `AIM_4A8B6118_BOXFIT`; {len(rows)} barrels (no flag, box overlapping no other box) of {len(masks)} HOME train frames with a hand mask.",
         "Each barrel's stripe rows are read off its mask; the camera model gives the barrel whose stripe centre is at that row; the hand-drawn box is compared with it.", "",
         "| frame | barrel | box | stripe rows | model width | box top - model top | box bottom - model bottom | box width / model | stripe height / model |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['stem'].replace('4A8B_window_light_', '')} | {r['color']} | {r['bbox']} | {r['stripe_rows']} | {r['model_width']} | {r['top_res']:+.1f} | "
                 f"{r['bottom_res']:+.1f} | {r['width_ratio']:.2f} | {r['stripe_h_ratio']:.2f} |")
    L += ["", "## What was chosen, and by which rule", "",
          "| number | value | rule | the numbers behind it |", "|---|---|---|---|",
          f"| `top_fit` (px added to the model's top row: a + b x width) | {top_fit} | the line if it predicts left-out scenes better than the median by more than 10 % | "
          f"median {top_info['median']}, line {top_info['line']}; left-one-scene-out error {top_info['loso_rmse_median']} px (median) against {top_info['loso_rmse_line']} px (line) |",
          f"| `bottom_fit` | {bottom_fit} | same | median {bottom_info['median']}, line {bottom_info['line']}; {bottom_info['loso_rmse_median']} px against {bottom_info['loso_rmse_line']} px |",
          f"| `seam` (share of the stripe height not looked at, each side of a band edge) | {seam} | (1 - 10th percentile of stripe height / model) / 2 | "
          f"stripe height / model: median {np.median(sh):.2f}, 10th percentile {np.percentile(sh, 10):.2f} |",
          f"| `rim` (share of the width, each side, with rounded corners) | {rim} | columns where the first 1/8 of the upper body and the last 1/8 of the lower body are under half painted | {rim_cols} of {N} columns |",
          f"| `rim_top` | {rim_top} | in the rim columns, the share of upper-body rows from the top that are under half painted | |",
          f"| `rim_bottom` | {rim_bottom} | the same for the lower body, from the bottom | |", "",
          f"Box width / model width: median {fit['width_ratio']['median']:.2f}, {fit['width_ratio']['min']:.2f} to {fit['width_ratio']['max']:.2f}. The model's width is used as it is.", "",
          "## The mean barrel", "",
          "Left: how often a cell is body color; right: stripe color (0 = never, 9 = always). Rows: upper body (24), stripe (24), lower body (24), each stretched to its own 24 rows; 24 columns.", "", "```"]
    for r in range(3 * N):
        L.append("".join(str(int(v * 9.99)) for v in body[r]) + "   " + "".join(str(int(v * 9.99)) for v in stripe[r]))
    L += ["```", ""]
    (OUT / "fit.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:6 + len(rows) + 12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
