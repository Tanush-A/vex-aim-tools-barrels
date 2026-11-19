#!/usr/bin/env python3
"""A viewing aid for the scorecard (no acceptance number comes from here): the scenes where an arm does worse than
``base`` (the hidden barrel no longer found, or more boxes where no barrel is), one line each with the boxes and the
detector's reasons, and a contact sheet of them (left: ``base``, right: the arm); and why the hidden barrel is not
found in the cells named with --why.

    python barrels/experiments/2026-11-20_occl_pin/diag.py --arms pin,pin+thin --why slant:0.75,edge:0.75 [--out round1]
Output: text; results/2026-11-20_occl_pin/[<out>/]sheets/diag_<arm>.png (ignored by git).
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
OCCL = HERE.parent / "2026-11-19_det_occl"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(OCCL))
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("det_occl_run", OCCL / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
import pin_arms  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

R.occl_arms = pin_arms
OUT = PKG_ROOT / "results" / "2026-11-20_occl_pin"


def reasons(log) -> str:
    return ", ".join(f"{e['stage']}:{e['why']}{list(e['bbox'])}" for e in log if e["stage"] in ("barrel", "stripe", "cap"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="pin,pin+thin")
    ap.add_argument("--why", default="", help="cells (row:amount, comma-separated) whose misses are counted by cause for each arm")
    ap.add_argument("--out", default="")
    ap.add_argument("--big", action="store_true", help="also list the right-place boxes that are too big with the arm and were not with base")
    args = ap.parse_args(argv)
    arms = [a for a in args.arms.split(",") if a]
    why = [(c.split(":")[0], float(c.split(":")[1])) for c in args.why.split(",") if c]
    pools, _ = R.build_sources(R.segmentations(R.train_stems()))
    tiles = {a: [] for a in arms}
    causes = {a: collections.defaultdict(collections.Counter) for a in arms}
    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            b = R.score_scene(sc, pin_arms.ARMS["base"])
            for a in arms:
                r = R.score_scene(sc, pin_arms.ARMS[a])
                name = f"{key} {int(amount * 100)}% {variant} {pool.split(' ')[0]} {src.stem.split('_', 3)[-1]} W{src.width}"
                worse = []
                if b["found"] and not r["found"]:
                    worse.append("found -> not found")
                if b["place"] and not r["place"]:
                    worse.append("right place -> not")
                if r["false"] > b["false"]:
                    worse.append(f"false boxes {b['false']} -> {r['false']}")
                if worse:
                    print(f"[{a}] {name}: {'; '.join(worse)}\n    truth {list(sc.target[1])} fronts {[list(f[1]) for f in sc.fronts]}\n"
                          f"    base {[list(p.bbox) for p in b['preds']]} iou {b['iou']}\n    {a} {[(list(p.bbox), p.source) for p in r['preds']]} iou {r['iou']} cause {r['cause']}\n"
                          f"    reasons: {reasons(r['log'])}")
                    tiles[a].append(np.hstack([R.render(sc, b["preds"], f"base {name}"[:44]), R.render(sc, r["preds"], f"{a} {'; '.join(worse)}"[:44])]))
                if args.big and r["size"] == "big" and b["size"] != "big":
                    print(f"[{a}] too big: {name}: truth {list(sc.target[1])} box {r['box']} w {r['w_ratio']} h {r['h_ratio']} (base: {b['box']} {b['size']})")
                if (key, amount) in why and not r["found"]:
                    last = [e for e in r["log"] if e["stage"] in ("barrel", "stripe") and e["why"] != "kept"]
                    causes[a][(key, amount)][r["cause"] + (" / right place" if r["place"] else "") + (f" [{last[-1]['why']}]" if last and not r["place"] else "")] += 1
    d = (OUT / args.out if args.out else OUT) / "sheets"
    d.mkdir(parents=True, exist_ok=True)
    for a in arms:
        ts = tiles[a][:48]
        if ts:
            per = 3
            while len(ts) % per:
                ts.append(np.zeros_like(ts[0]))
            cv2.imwrite(str(d / f"diag_{a}.png"), np.vstack([np.hstack(ts[i:i + per]) for i in range(0, len(ts), per)]))
        for cell, cnt in causes[a].items():
            print(f"[{a}] not found, {cell[0]} at {int(cell[1] * 100)} %: " + ", ".join(f"{k} {v}" for k, v in cnt.most_common()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
