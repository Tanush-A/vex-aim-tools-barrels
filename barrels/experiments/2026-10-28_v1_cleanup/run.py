#!/usr/bin/env python3
"""v1.5: pixel cleanup flags (small-blob removal, opening, hole filling) on top of the v1 final
config, scored under the same leave-one-scene-out CV and chosen by the pre-registered rule.

    python barrels/experiments/2026-10-28_v1_cleanup/run.py --name v1_cleanup

Hypothesis, stated before running: a tie. The error attribution (EXPERIMENTS.md 2026-10-22) says
v1's false pixels are hundreds-of-pixel lid reflections and edge halos, not specks, and its misses
are shadowed faces, which no cleanup recovers. Test set untouched.
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
from sweep import choose, summarize  # noqa: E402

V1_FINAL = io.PKG_ROOT / "results" / "2026-10-20_v1_adaptive_cv" / "configs" / "afd85483.json"
AXES = {"min_blob_px": [0, 10, 25, 50, 100], "open_px": [0, 3, 5], "fill_holes": [False, True]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default="v1_cleanup")
    ap.add_argument("--config", type=Path, default=V1_FINAL)
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)
    base = pl.Config.from_dict(json.load(args.config.open()))
    assert base.short_hash() == "afd85483", "expected the v1 final config"
    ds = load_pool(); folds = cv.loso_folds(ds.stems, ds.scene)
    out = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    configs = [("base", "v1 final (no cleanup)", None, base)]
    for axis, vals in AXES.items():
        for v in vals:
            if v == getattr(base, axis):
                continue
            configs.append((axis, str(v), v, pl.with_overrides(base, **{axis: v})))
    # the two most plausible pairs
    configs.append(("pair", "min_blob_px=25,fill_holes", None, pl.with_overrides(base, min_blob_px=25, fill_holes=True)))
    configs.append(("pair", "open_px=3,min_blob_px=25", None, pl.with_overrides(base, open_px=3, min_blob_px=25)))
    rows = cv.run_configs(ds, configs, folds, out / "sweep.csv", out / "configs")
    cfgs = {c.short_hash(): c for _, _, _, c in configs}
    base_row = next(r for r in rows if r["axis"] == "base")
    chosen, notes = choose(rows, base_row, cfgs)
    md = summarize(rows, base_row, f"{args.name}: cleanup flags on v1 final `{base.short_hash()}` (LOSO CV, no test)")
    md += "\n## Selection (pre-registered rule)\n\n- " + "\n- ".join(notes) + f"\n- chosen: `{chosen['id']}` ({chosen['axis']}={chosen['value']}), primary {chosen['primary']:.3f}\n"
    (out / "summary.md").write_text(md); print(md); print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
