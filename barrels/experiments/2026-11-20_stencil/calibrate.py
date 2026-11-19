#!/usr/bin/env python3
"""The stencil's three score numbers (accept, absent_cost, outside_cost) and the veto level, chosen by the rule of
PREREG.md on HOME train masks and negative frames. No CAMPUS frame, no scorecard scene, no recording is opened.

Masks:
  A1  the 16 HOME hand masks                          A2  the same frames, color model, leave one scene out
  A3  hand masks, `light` damage, seeds 10 to 14      A4  train negatives of the other tables (wood, black), adopted color model
  B   hand masks, `medium` damage, seeds 10 to 14

Step 1 (slow, one process per combination): for each (absent_cost, outside_cost, band_full) of the grid the stencil runs once with
accept 0.10 on every mask; every box is stored with its score (calibration_boxes.csv).
Step 2: T0, accept, the chosen pair, the direct run, leave-one-scene-out, the cost, the veto level (calibration.md, .json).

    python barrels/experiments/2026-11-20_stencil/calibrate.py            # both steps
    python barrels/experiments/2026-11-20_stencil/calibrate.py --step 2   # from the stored boxes
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, degrade as dg, detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, pipeline as pl  # noqa: E402
from barrels import splits, stencil as stn, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_stencil"
CAM = geo.AIM_4A8B6118_BOXFIT
SEEDS = (10, 11, 12, 13, 14)
GRID = [(m, o, bf) for bf in (1.0, 0.5, 0.25) for m in (0.1, 0.25, 0.5) for o in (0.25, 0.5, 1.0)]     # band_full added by PREREG addendum A
FLOOR, MARGIN = 0.10, 0.05
TS = [round(0.10 + 0.01 * i, 2) for i in range(61)]
ZERO = ("A1", "A2", "A3", "A4")           # pools that must hold no false box


def build_items() -> list[dict]:
    """Every mask of the calibration: pool, stem, scene tag, tag (seed), the mask."""
    sp = splits.load_splits()
    test = set(sp["test"])
    train = [s for s in sorted(sp["train"]) if io.boxes_path(s).exists()]
    assert not set(train) & test, "a test frame leaked in"
    home = [s for s in train if s.startswith("4A8B_window_light_") and io.mask_path(s).exists()]
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    hand = {}
    for s in home:
        m = io.load_mask(io.mask_path(s)); m[m == io.IGNORE] = 0
        hand[s] = m
    frames = {s: pl.Frame.from_image(io.load_image(io.find_image(s))) for s in home}
    items = [{"pool": "A1", "stem": s, "tag": "", "mask": hand[s]} for s in home]
    for fold in bcv.loso_folds(home, {s: io.parse_name(s)["scene"] for s in home}):
        fm = pl.fit([frames[s] for s in fold.train], [io.load_mask(io.mask_path(s)) for s in fold.train], model.cfg)
        items += [{"pool": "A2", "stem": s, "tag": "", "mask": pl.segment(frames[s], fm)[0]} for s in fold.held_out]
    boxes = {s: [tuple(b["bbox"]) for b in io.load_boxes(s)["barrels"]] for s in home}
    for pool, level in (("A3", "light"), ("B", "medium")):
        for seed in SEEDS:
            for i, s in enumerate(home):
                items.append({"pool": pool, "stem": s, "tag": f"seed{seed}", "mask": dg.damage(hand[s], boxes[s], dg.SEVERITIES[level], seed=1000 * seed + i)})
    for s in train:
        t = io.parse_name(s)
        if t["scene"] == "neg" and f"{t['light']}_{t['surface']}" not in ("window_light", "campus_light"):
            assert not io.load_boxes(s)["barrels"]
            items.append({"pool": "A4", "stem": s, "tag": "", "mask": pl.segment(pl.Frame.from_image(io.load_image(io.find_image(s))), model)[0]})
    for it in items:
        it["scene"] = io.parse_name(it["stem"])["scene"]
        it["key"] = f"{it['pool']}|{it['stem']}|{it['tag']}"
    return items


def gts_of(stem: str) -> list[dtp.Barrel]:
    return dtp.barrels_from_boxes(io.load_boxes(stem))


def run_pair(pair) -> list[dict]:
    mu, lam, bf = pair
    cfg = dataclasses.replace(stn.StencilConfig(), accept=FLOOR, absent_cost=mu, outside_cost=lam, band_full=bf)
    rows = []
    for it in build_items():
        for p in stn.detect(it["mask"], cfg, CAM):
            rows.append({"absent_cost": mu, "outside_cost": lam, "band_full": bf, "key": it["key"], "color": p.color, "bbox": json.dumps(list(p.bbox)), "score": round(p.confidence, 4)})
    return rows


def count(preds: list[dtp.Barrel], stem: str) -> tuple[int, int]:
    """(found, false) under the v2 rule."""
    gts = gts_of(stem)
    res = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2")
    return len(gts) - len(res.unmatched_gt), len(res.unmatched_pred)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--step", type=int, default=0)
    ap.add_argument("--procs", type=int, default=10)
    args = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    store = OUT / "calibration_boxes.csv"
    if args.step in (0, 1):
        with mp.Pool(args.procs) as pool:
            rows = [r for part in pool.map(run_pair, GRID) for r in part]
        with store.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        if args.step == 1:
            return 0
    items = build_items()
    by_key = {it["key"]: it for it in items}
    stored: dict[tuple, dict[str, list[dtp.Barrel]]] = {p: {} for p in GRID}
    for r in csv.DictReader(store.open()):
        stored[(float(r["absent_cost"]), float(r["outside_cost"]), float(r["band_full"]))].setdefault(r["key"], []).append(
            dtp.Barrel(color=int(r["color"]), bbox=tuple(json.loads(r["bbox"])), confidence=float(r["score"]), source="stencil"))
    rules = {it["key"]: count(det.detect(it["mask"], det.DetConfig(), CAM), it["stem"]) for it in items}
    rules_false_B = sum(v[1] for k, v in rules.items() if k.startswith("B|"))
    n_barrels = {pool: sum(len(gts_of(it["stem"])) for it in items if it["pool"] == pool) for pool in ("A1", "A2", "A3", "A4", "B")}

    def table(pair, keep=lambda it: True):
        """T -> {pool: (found, false)} from the stored boxes of ``pair``, over the items that ``keep``."""
        out = {}
        for T in TS:
            c = {p: [0, 0] for p in ("A1", "A2", "A3", "A4", "B")}
            for it in items:
                if not keep(it):
                    continue
                fnd, fls = count([b for b in stored[pair].get(it["key"], []) if b.confidence >= T], it["stem"])
                c[it["pool"]][0] += fnd; c[it["pool"]][1] += fls
            out[T] = c
        return out

    def t0_of(tab, limit_B):
        for T in TS:
            if all(tab[T][p][1] == 0 for p in ZERO) and tab[T]["B"][1] <= limit_B:
                return T
        return None

    tabs = {pair: table(pair) for pair in GRID}
    summary = []
    for pair in GRID:
        t0 = t0_of(tabs[pair], rules_false_B)
        acc = None if t0 is None else round(t0 + MARGIN, 2)

        def found(T):
            return None if T is None or T not in tabs[pair] else sum(tabs[pair][T][p][0] for p in ("A1", "A2", "A3", "B"))
        summary.append({"absent_cost": pair[0], "outside_cost": pair[1], "band_full": pair[2], "T0": t0, "accept": acc, "found_floor": found(FLOOR), "found_T0": found(t0),
                        "found_accept": found(acc), "false_floor": {p: tabs[pair][FLOOR][p][1] for p in tabs[pair][FLOOR]}})
    ok = [s for s in summary if s["accept"] is not None and s["found_accept"] is not None]
    best = max(ok, key=lambda s: (s["found_accept"], -s["accept"], -s["absent_cost"], -s["outside_cost"], s["band_full"]))
    pair = (best["absent_cost"], best["outside_cost"], best["band_full"])

    # step 4: the direct run with the chosen numbers
    accept = best["accept"]
    while True:
        cfg = dataclasses.replace(stn.StencilConfig(), accept=accept, absent_cost=pair[0], outside_cost=pair[1], band_full=pair[2])
        direct = {p: [0, 0] for p in ("A1", "A2", "A3", "A4", "B")}
        direct_boxes = {}
        for it in items:
            preds = stn.detect(it["mask"], cfg, CAM)
            direct_boxes[it["key"]] = preds
            fnd, fls = count(preds, it["stem"])
            direct[it["pool"]][0] += fnd; direct[it["pool"]][1] += fls
        if all(direct[p][1] == 0 for p in ZERO) or accept >= 0.7:
            break
        accept = round(accept + 0.01, 2)

    # step 5: leave one scene out
    loso = []
    for scene in sorted({it["scene"] for it in items if it["pool"] != "A4"}):
        tab = table(pair, keep=lambda it: it["pool"] == "A4" or it["scene"] != scene)
        lim = sum(v[1] for k, v in rules.items() if k.startswith("B|") and by_key[k]["scene"] != scene)
        t0 = t0_of(tab, lim)
        T = round(t0 + MARGIN, 2)
        fnd = fls = n = 0
        for it in items:
            if it["pool"] != "A4" and it["scene"] == scene:
                a, b = count([x for x in stored[pair].get(it["key"], []) if x.confidence >= T], it["stem"])
                fnd += a; fls += b; n += len(gts_of(it["stem"]))
        loso.append({"scene": scene, "T0_without_it": t0, "accept": T, "found": fnd, "barrels": n, "false": fls})

    # the veto level: the lowest stencil score at the place of a RIGHT rule box in A1, A2, A3
    low = []
    for it in items:
        if it["pool"] not in ("A1", "A2", "A3"):
            continue
        preds = det.detect(it["mask"], det.DetConfig(), CAM)
        gts = gts_of(it["stem"])
        res = ed.evaluate_frame(it["stem"], preds, gts, CAM, rule="v2")
        for i, p in enumerate(preds):
            if i not in res.unmatched_pred:
                low.append((stn.box_score(it["mask"], p, cfg, CAM, others=[o for o in preds if o is not p]), it["key"], list(p.bbox)))
    low.sort()
    veto = round(low[0][0] - MARGIN, 2)

    out = {"git": bcv.git_hash(), "grid": summary, "chosen": {"absent_cost": pair[0], "outside_cost": pair[1], "band_full": pair[2], "T0": best["T0"], "accept_by_rule": best["accept"],
           "accept": accept, "veto": veto}, "direct": direct, "rules_on_same_masks": {p: [sum(v[0] for k, v in rules.items() if k.startswith(p + "|")),
           sum(v[1] for k, v in rules.items() if k.startswith(p + "|"))] for p in ("A1", "A2", "A3", "A4", "B")}, "barrels": n_barrels, "loso": loso,
           "lowest_right_rule_box_scores": [[round(a, 3), b, c] for a, b, c in low[:8]], "seeds": SEEDS,
           "masks": {p: sum(1 for it in items if it["pool"] == p) for p in ("A1", "A2", "A3", "A4", "B")}}
    (OUT / "calibration.json").write_text(json.dumps(out, indent=1) + "\n")
    mu = pair[0]
    L = ["# Calibration of the stencil's score (PREREG.md, \"The three score numbers\")", "",
         f"git {out['git']}. Masks: " + ", ".join(f"{p} {n}" for p, n in out["masks"].items()) + f". Barrels: A1 {n_barrels['A1']}, A2 {n_barrels['A2']}, "
         f"A3 {n_barrels['A3']}, B {n_barrels['B']}. The rule detector draws {rules_false_B} false boxes on B.", "",
         "## The grid (from the boxes stored with accept 0.10)", "",
         "T0 = the smallest accept with no false box in A1 to A4 and no more in B than the rule detector. accept = T0 + 0.05. Found = A1 + A2 + A3 + B "
         f"({n_barrels['A1'] + n_barrels['A2'] + n_barrels['A3'] + n_barrels['B']} barrels).", "",
         "| band_full | absent_cost | outside_cost | false boxes at 0.10 (A1 / A2 / A3 / A4 / B) | T0 | accept | found at 0.10 | at T0 | at accept |", "|---|---|---|---|---|---|---|---|---|"]
    for s in summary:
        f = s["false_floor"]
        mark = " **chosen**" if (s["absent_cost"], s["outside_cost"], s["band_full"]) == pair else ""
        L.append(f"| {s['band_full']} | {s['absent_cost']} | {s['outside_cost']} | {f['A1']} / {f['A2']} / {f['A3']} / {f['A4']} / {f['B']} | {s['T0']} | {s['accept']}{mark} | {s['found_floor']} | {s['found_T0']} | {s['found_accept']} |")
    r = out["rules_on_same_masks"]
    L += ["", "## The direct run with the chosen numbers", "",
          f"band_full {pair[2]}, absent_cost {pair[0]}, outside_cost {pair[1]}, accept {accept}" + ("" if accept == best["accept"] else f" (the rule gave {best['accept']}; raised until the direct run had no false box in A1 to A4)") + ".", "",
          "| masks | barrels | stencil found | stencil false | rules found | rules false |", "|---|---|---|---|---|---|"]
    for p, name in (("A1", "HOME hand masks"), ("A2", "HOME color model, leave one scene out"), ("A3", "light damage, seeds 10 to 14"), ("A4", "negatives of the other tables"), ("B", "medium damage, seeds 10 to 14")):
        L.append(f"| {p} {name} | {n_barrels[p]} | {direct[p][0]} | {direct[p][1]} | {r[p][0]} | {r[p][1]} |")
    L += ["", f"What the tolerance means: a barrel hidden by a thing that is not painted, showing the share v of its width, scores about v - {mu} x (1 - v). "
          f"It passes accept {accept} from v = {(accept + mu) / (1 + mu):.2f} up (with a perfect mask). At T0 = {best['T0']} that would be {(best['T0'] + mu) / (1 + mu):.2f}; "
          f"at the floor 0.10, {(0.10 + mu) / (1 + mu):.2f}.", "",
          "## Leaving one HOME scene out (does the tolerance transfer?)", "",
          "T0 from the masks of the other scenes (and the negatives); the left-out scene's masks (hand, color model, light, medium) at that T0 + 0.05.", "",
          "| scene left out | T0 without it | accept | found on it | false on it |", "|---|---|---|---|---|"]
    for row in loso:
        L.append(f"| {row['scene']} | {row['T0_without_it']} | {row['accept']} | {row['found']} of {row['barrels']} | {row['false']} |")
    L += ["", "## The veto level", "",
          f"The lowest stencil score at the place of a right rule box in A1, A2, A3 is {low[0][0]:.3f}; veto = that - 0.05 = **{veto}**. The eight lowest:", ""]
    L += [f"- {a:.3f}  {b}  {c}" for a, b, c in low[:8]]
    (OUT / "calibration.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
