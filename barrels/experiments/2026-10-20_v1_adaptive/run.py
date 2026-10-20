#!/usr/bin/env python3
"""Per-image (band-derived) saturation floor vs the fixed one; synthetic lighting-shift stress; overlays.

    run.py cv    --name v1_adaptive_cv            LOSO CV grid: fixed floor vs band-derived floor variants
    run.py shift --name v1_adaptive_shift         train on ORIGINAL frames, score held-out frames after a
                                                  SYNTHETIC global gain / color cast (not real data; a probe
                                                  of which parts of the method are lighting-dependent)
    run.py viz   --config cfg.json --name v1_viz  dimmed-image overlays of the predicted orange/blue for
                                                  all 21 frames (pool via CV predictions, test via the
                                                  final fit), with the ground truth as thin white outlines

Test split is used only by `viz` (predictions for display; the numbers come from the earlier single run).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE.parent / "2026-10-20_v1_rgbbox"))
from barrels import cv, eval as ev, io, pipeline as pl, splits, viz  # noqa: E402
from run import load_pool  # noqa: E402
from sweep import summarize  # noqa: E402

V1_FIXED = io.PKG_ROOT / "results" / "2026-10-20_v1_sweep2_pair" / "configs" / "ee36a1e9.json"


def _f(x):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


# ------------------------------------------------------------------ cv
def do_cv(args, v1: pl.Config) -> None:
    ds = load_pool(); folds = cv.loso_folds(ds.stems, ds.scene)
    out = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    configs = [("base", "fixed s_min=50", None, v1)]
    for src in ("bg", "both"):
        for q in (99.0, 99.5, 99.9):
            for m in (5.0, 10.0, 15.0, 20.0):
                configs.append((f"band[{src}]", f"q={q} m={m}", None, pl.with_overrides(v1, s_min_mode="band", s_band_q=q, s_band_margin=m, s_band_source=src)))
    rows = cv.run_configs(ds, configs, folds, out / "sweep.csv", out / "configs")
    base_row = next(r for r in rows if r["axis"] == "base")
    md = summarize(rows, base_row, f"{args.name}: fixed vs band-derived saturation floor (LOSO CV, no test)")
    # what floor did band mode actually pick per frame?
    res = cv.cross_validate(ds, pl.with_overrides(v1, s_min_mode="band"), folds)
    eff = {s: i["s_min_eff"] for s, i in res.infos.items()}
    md += "\n## Floor chosen per frame by band mode (q 99.5, margin 10, bg rows)\n\n" + ", ".join(f"{s[17:]}: {v}" for s, v in sorted(eff.items())) + "\n"
    (out / "summary.md").write_text(md); print(md); print("written to", out)


# ------------------------------------------------------------------ shift
def transforms() -> dict:
    def gain(g):
        return lambda bgr: np.clip(bgr.astype(np.float32) * g, 0, 255).astype(np.uint8)
    def cast(r, g, b):
        return lambda bgr: np.clip(bgr.astype(np.float32) * np.array([b, g, r], np.float32), 0, 255).astype(np.uint8)
    return {"gain 0.5": gain(0.5), "gain 0.75": gain(0.75), "gain 1.25": gain(1.25),
            "warm cast (R×1.2, B×0.8)": cast(1.2, 1.0, 0.8), "cool cast (R×0.8, B×1.2)": cast(0.8, 1.0, 1.2)}


def cv_shifted(ds: cv.Dataset, cfg: pl.Config, folds, tf) -> dict:
    """Fit on original train frames; segment the held-out frames after transform tf."""
    results = []
    for f in folds:
        model = pl.fit([ds.frames[s] for s in f.train], [ds.masks[s] for s in f.train], cfg)
        for s in f.held_out:
            frame = pl.Frame.from_image(tf(ds.frames[s].bgr))
            pred, _ = pl.segment(frame, model)
            results.append(ev.evaluate_image(s, pred, ds.masks[s]))
    r = cv.CVResult(cfg, folds, results, {}, {s: {} for s in ds.stems}, {}, dict(ds.scene))
    return r.score()


def do_shift(args, v1: pl.Config) -> None:
    ds = load_pool(); folds = cv.loso_folds(ds.stems, ds.scene)
    out = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    band = pl.with_overrides(v1, s_min_mode="band")
    configs = [("fixed floor (v1 final)", v1), ("band floor", band),
               ("band floor + YUV chroma box", pl.with_overrides(band, box_space="yuv_chroma", box_pct=(0.5, 99.5))),
               ("band floor + re-fit (margin 3)", pl.with_overrides(band, refit=pl.RefitConfig(margin_scale=3.0))),
               ("band floor + YUV + re-fit", pl.with_overrides(band, box_space="yuv_chroma", box_pct=(0.5, 99.5), refit=pl.RefitConfig(margin_scale=3.0)))]
    lines = [f"# {args.name}: SYNTHETIC lighting shifts applied to held-out frames only (train frames untouched)", "",
             "Not real data: a probe of which parts of the method depend on the lighting. gain g multiplies every pixel by g; "
             "a cast multiplies channels differently. Scores: primary = mean pooled IoU (orange, blue); neg FP.", "",
             "| shift | config | primary | orange IoU (P/R) | blue IoU (P/R) | neg FP o/b |", "|---|---|---|---|---|---|"]
    table = {}
    for tname, tf in [("none", lambda x: x)] + list(transforms().items()):
        for cname, cfg in configs:
            sc = cv_shifted(ds, cfg, folds, tf)
            table[(tname, cname)] = sc
            lines.append(f"| {tname} | {cname} | {_f(sc['primary'])} | {_f(sc['iou_o'])} ({_f(sc['prec_o'])}/{_f(sc['rec_o'])}) | {_f(sc['iou_b'])} ({_f(sc['prec_b'])}/{_f(sc['rec_b'])}) | {_f(sc['neg_fp_o'])}/{_f(sc['neg_fp_b'])} |")
            print(lines[-1], flush=True)
    json.dump({f"{k[0]} | {k[1]}": {kk: vv for kk, vv in v.items() if kk != "fold_rows"} for k, v in table.items()}, (out / "shift.json").open("w"), indent=1, default=float)
    (out / "summary.md").write_text("\n".join(lines) + "\n"); print("written to", out)


# ------------------------------------------------------------------ viz
def overlay_dim(bgr: np.ndarray, pred: np.ndarray, gt: np.ndarray | None, dim: float = 0.35) -> np.ndarray:
    out = (bgr.astype(np.float32) * dim).astype(np.uint8)
    out[pred == io.ORANGE] = viz.ORANGE_BGR
    out[pred == io.BLUE] = viz.BLUE_BGR
    if gt is not None:
        for c in (io.ORANGE, io.BLUE):
            cnts, _ = cv2.findContours((gt == c).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(out, cnts, -1, (255, 255, 255), 1)
    return out


def do_viz(args, cfg: pl.Config) -> None:
    sp = splits.load_splits()
    pool, test = cv.Dataset(sp["train"]), cv.Dataset(sp["test"])
    res = cv.cross_validate(pool, cfg)
    _, test_results, test_preds, _ = cv.fit_final_and_predict(pool, test, cfg)
    out = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    (out / "overlays").mkdir()
    tiles = []
    by_name = {r.name: r for r in res.results + test_results}
    for ds, preds, tag in ((pool, res.preds, "pool/CV"), (test, test_preds, "TEST")):
        for s in ds.stems:
            ov = overlay_dim(ds.frames[s].bgr, preds[s], ds.masks[s])
            r = by_name[s]
            label = f"{s[17:]} [{tag}]  orange IoU {_f(r.counts[io.ORANGE].iou)}  blue IoU {_f(r.counts[io.BLUE].iou)}" if not r.negative else f"{s[17:]} [{tag}]  negative, flagged {r.counts[io.ORANGE].fp + r.counts[io.BLUE].fp} px"
            cv2.putText(ov, label, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3); cv2.putText(ov, label, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imwrite(str(out / "overlays" / f"{s}.png"), ov)
            tiles.append(cv2.resize(ov, (640, 480)))
    while len(tiles) % 3:
        tiles.append(np.zeros_like(tiles[0]))
    sheet = np.concatenate([np.concatenate(tiles[i:i + 3], 1) for i in range(0, len(tiles), 3)], 0)
    cv2.imwrite(str(out / "overlays_sheet.png"), sheet)
    figs = HERE / "figures"; figs.mkdir(exist_ok=True)
    cv2.imwrite(str(figs / "overlays_sheet.png"), cv2.resize(sheet, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_PNG_COMPRESSION, 9])
    json.dump({"config": cfg.to_dict(), "config_hash": cfg.short_hash(), "git": cv.git_hash()}, (out / "config.json").open("w"), indent=1)
    print("written to", out, "and", figs / "overlays_sheet.png")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=("cv", "shift", "viz"))
    ap.add_argument("--name", required=True)
    ap.add_argument("--config", type=Path, default=V1_FIXED, help="starting config JSON (default: v1 fixed final)")
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)
    cfg = pl.Config.from_dict(json.load(args.config.open()))
    {"cv": do_cv, "shift": do_shift, "viz": do_viz}[args.mode](args, cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
