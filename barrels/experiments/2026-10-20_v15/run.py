#!/usr/bin/env python3
"""v1.5 arms under the same leave-one-scene-out CV as v1 (CV only — the test set is NOT used).

    python barrels/experiments/2026-10-20_v15/run.py --name v15 [--v1 path/to/ee36a1e9.json]

Arms, all starting from the final v1 config:
  refit:*   barrel-referenced re-fit (pipeline.RefitConfig): per image, pixels inside the
            train-fold "inner" box (10–90 %) are high-confidence; the class box is re-fit to them
            (percentile + margin_scale·MAD), clipped to the train-fold outer box; falls back to
            the v1 box when fewer than min_px confident pixels exist (negatives).
  yuv:*     the class box lives in the YUV chroma plane (U, V) instead of RGB; gates/priors
            unchanged (a per-pixel threshold in another space, not an image correction).
Writes results/<date>_<name>/sweep.csv + summary.md (same format as the v1 sweeps).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE.parent / "2026-10-20_v1_rgbbox"))
from barrels import cv, io, pipeline as pl  # noqa: E402
from run import load_pool  # noqa: E402
from sweep import summarize  # noqa: E402

V1_DEFAULT = io.PKG_ROOT / "results" / "2026-10-20_v1_sweep2_pair" / "configs" / "ee36a1e9.json"


def arms(v1: pl.Config) -> list[tuple[str, str, object, pl.Config]]:
    out = [("base", "v1 final", None, v1)]
    R = pl.RefitConfig
    for name, rc in [
        ("default", R()),
        ("min_px=100", R(min_px=100)),
        ("min_px=1000", R(min_px=1000)),
        ("margin=0.5", R(margin_scale=0.5)),
        ("margin=2", R(margin_scale=2.0)),
        ("margin=3", R(margin_scale=3.0)),
        ("inner=5-95", R(inner_pct=(5.0, 95.0))),
        ("inner=25-75", R(inner_pct=(25.0, 75.0))),
        ("pct=0.5-99.5", R(pct=(0.5, 99.5))),
        ("outer=0-100", R(outer_pct=(0.0, 100.0))),
        ("n_iter=1", R(n_iter=1)),
    ]:
        out.append(("refit", name, None, pl.with_overrides(v1, refit=rc)))
    for name, ov in [
        ("box 1-99", {}),
        ("box 0.5-99.5", {"box_pct": (0.5, 99.5)}),
        ("box 2-98", {"box_pct": (2.0, 98.0)}),
        ("s_min 40", {"s_min": 40}),
        ("s_min 60", {"s_min": 60}),
        ("+refit", {"refit": R()}),
    ]:
        out.append(("yuv", name, None, pl.with_overrides(v1, box_space="yuv_chroma", **ov)))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default="v15")
    ap.add_argument("--v1", type=Path, default=V1_DEFAULT)
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)
    v1 = pl.Config.from_dict(json.load(args.v1.open()))
    ds = load_pool()
    folds = cv.loso_folds(ds.stems, ds.scene)
    out_dir = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    configs = arms(v1)
    rows = cv.run_configs(ds, configs, folds, out_dir / "sweep.csv", out_dir / "configs")
    base_row = next(r for r in rows if r["axis"] == "base")
    # refit engagement: how many pool frames actually re-fit (from a fresh CV of the default refit arm)
    res = cv.cross_validate(ds, pl.with_overrides(v1, refit=pl.RefitConfig()), folds)
    used = {c: sum(1 for i in res.infos.values() if i.get("refit", {}).get(str(c), {}).get("used")) for c in (io.ORANGE, io.BLUE)}
    md = summarize(rows, base_row, f"{args.name}: v1.5 arms vs v1 final `{v1.short_hash()}` (LOSO CV, no test)")
    md += f"\nRefit (default) engaged on {used[io.ORANGE]} / {len(ds.stems)} frames for orange and {used[io.BLUE]} / {len(ds.stems)} for blue; negatives never re-fit (min_px guard).\n"
    (out_dir / "summary.md").write_text(md)
    print(md); print("written to", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
