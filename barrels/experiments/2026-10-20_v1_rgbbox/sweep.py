#!/usr/bin/env python3
"""Ablations and parameter sweeps for the v1 config, scored by leave-one-scene-out CV.

    python .../sweep.py --mode ablation  --name v1_ablation
    python .../sweep.py --mode coord     --name v1_sweep [--base cfg.json]
    python .../sweep.py --mode pair      --name v1_pair  [--base cfg.json]

Each run appends one CSV row per config to results/<date>_<name>/sweep.csv (so partial runs
survive) and writes a summary.md with per-axis tables and the pre-registered selection
(DECISIONS.md 2026-10-19: primary = mean pooled IoU; neg FP > 0.5 % disqualifies; < 0.02 is a tie,
prefer the simpler setting). Never touches the test split.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
from barrels import cv, io, pipeline as pl  # noqa: E402
from config import ABLATIONS, BASE, PAIR_AXES, SWEEP_AXES  # noqa: E402
from run import load_pool  # noqa: E402


def _f(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def summarize(rows: list[dict], base_row: dict | None, title: str) -> str:
    lines = [f"# {title}", "", "primary = mean pooled IoU (orange, blue) over in-scope positive pool frames; "
             "neg FP = fraction of pixels flagged on no-barrel frames (> 0.005 disqualifies); Δ vs base.", ""]
    axes = []
    for r in rows:
        if r["axis"] not in axes:
            axes.append(r["axis"])
    for axis in axes:
        lines += [f"## {axis}", "", "| value | primary | Δ | orange IoU | blue IoU | blue P / R | neg FP o / b | fold std o / b | oos IoU o / b | guard | DQ |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in [x for x in rows if x["axis"] == axis]:
            d = r["primary"] - base_row["primary"] if base_row else float("nan")
            lines.append(f"| {r['value']} | {_f(r['primary'])} | {d:+.3f} | {_f(r['iou_o'])} | {_f(r['iou_b'])} | {_f(r['prec_b'])} / {_f(r['rec_b'])} | "
                         f"{_f(r['neg_fp_o'])} / {_f(r['neg_fp_b'])} | {_f(r['fold_std_o'])} / {_f(r['fold_std_b'])} | {_f(r['oos_iou_o'])} / {_f(r['oos_iou_b'])} | {r['guard_trips']} | {'yes' if r['disqualified'] else ''} |")
        lines.append("")
    return "\n".join(lines)


def n_stages(cfg: pl.Config) -> int:
    """How many optional stages are active (fewer = simpler, for tie-breaks)."""
    return int(cfg.horizon_row is not None) + int(cfg.s_min > 0) + int(cfg.v_min > 0) + int(cfg.table_prior) + int(cfg.bg_prior)


def choose(rows: list[dict], base_row: dict, cfgs: dict[str, pl.Config]) -> tuple[dict, list[str]]:
    """Pre-registered rule (DECISIONS.md 2026-10-19): best non-disqualified primary; every config within
    TIE_BAND of it is a tie; among ties prefer the simplest = fewest active stages, then the base
    (unchanged parameters). Returns the chosen row and the reasoning."""
    ok = [r for r in rows if not r["disqualified"]]
    best = max(ok, key=lambda r: r["primary"])
    ties = [r for r in ok if best["primary"] - r["primary"] < cv.TIE_BAND]
    notes = [f"best primary {best['primary']:.3f} at {best['axis']}={best['value']}",
             f"tied within {cv.TIE_BAND}: " + ", ".join(f"{r['axis']}={r['value']} ({r['primary']:.3f})" for r in ties)]
    chosen = min(ties, key=lambda r: (n_stages(cfgs[r["id"]]), r["axis"] != "base", -r["primary"]))
    notes.append(f"simplest among ties ({n_stages(cfgs[chosen['id']])} active stages): {chosen['axis']}={chosen['value']}")
    return chosen, notes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=("ablation", "coord", "pair"), required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--base", type=Path, help="config JSON to sweep around (default: BASE)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=JSON", help="override a base field, e.g. --set s_min=50 --set k_bg=2.5")
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results")
    args = ap.parse_args(argv)

    base = pl.Config.from_dict(json.load(args.base.open())) if args.base else BASE
    if args.set:
        overrides = {k: json.loads(v) for k, v in (kv.split("=", 1) for kv in args.set)}
        base = pl.Config.from_dict(base.to_dict() | overrides)
    ds = load_pool()
    folds = cv.loso_folds(ds.stems, ds.scene)
    out_dir = cv.fresh_dir(args.out / f"{dt.date.today().isoformat()}_{args.name}")
    csv_path = out_dir / "sweep.csv"

    if args.mode == "ablation":
        configs = [("base", "base", None, base)] + [("ablation", name, None, pl.with_overrides(base, **ov)) for name, ov in ABLATIONS]
    elif args.mode == "coord":
        configs = [("base", "base", None, base)] + [(axis, str(v), v, pl.with_overrides(base, **{axis: v})) for axis, vals in SWEEP_AXES.items() for v in vals]
    else:
        (a, avals), (b, bvals) = PAIR_AXES
        configs = [("base", "base", None, base)] + [(f"{a}x{b}", f"{a}={x},{b}={y}", None, pl.with_overrides(base, **{a: x, b: y})) for x in avals for y in bvals]
    rows = cv.run_configs(ds, configs, folds, csv_path, out_dir / "configs")
    cfgs = {c.short_hash(): c for _, _, _, c in configs}

    base_row = next(r for r in rows if r["axis"] == "base")
    chosen, notes = choose(rows, base_row, cfgs)
    md = summarize(rows, base_row, f"{args.name} ({args.mode}) around config {base.short_hash()}")
    md += "\n## Selection (pre-registered rule)\n\n- " + "\n- ".join(notes) + f"\n- chosen: `{chosen['id']}` ({chosen['axis']}={chosen['value']}), primary {chosen['primary']:.3f}\n"
    (out_dir / "summary.md").write_text(md)
    json.dump({"base": base.to_dict(), "chosen_id": chosen["id"], "chosen": {"axis": chosen["axis"], "value": chosen["value"]}, "notes": notes, "git": cv.git_hash()},
              (out_dir / "selection.json").open("w"), indent=1)
    print(md); print("written to", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
