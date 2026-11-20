#!/usr/bin/env python3
"""Part 2, measurement: the scorecard's scenes, cell by cell, with WHY the hidden barrel is not found. The scorecard
of ``2026-11-19_det_occl`` is loaded by path (the same 50 source barrels, the same scenes, the same scoring). For
every scene of the chosen amounts and each arm: found (v2), box in the right place, its size class, boxes where no
barrel is, the cause the reason log gives, and what the stripe step saw of the barrel's widest stripe piece: its
width, whether it is thin, whether it is a full slice, the seen span, and the corner cost of the barrel's own end
and of the cut end (``_end_costs``; the own end is known from how the scene was made).

Train frames only (asserted in the loaded script).

    python barrels/experiments/2026-11-20_occl_sliver/diag_cells.py [--arms start,start+behind] [--amounts 0.75] [--out cells_before]
Outputs: results/2026-11-20_occl_sliver/<out>/ cells.md, cell_scenes.csv
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import sys
import types

import sliver as S
from barrels import detect_types as dtp, detector as det, geometry as geo

C, A = S.C, S.A
CAM = geo.AIM_4A8B6118_BOXFIT


def overlaps(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def widest_piece(sc, cfg) -> dict:
    """What the stripe step sees of the target's widest stripe piece (of its body color, overlapping its full box)."""
    mask = sc.mask
    h, w = mask.shape
    color, tb = sc.target
    narrow: list = []
    stripes = det.find_stripes(mask, CAM, cfg, narrow=narrow)
    cands = [s for s in stripes if s.body == color and overlaps(s.bbox, tb)]
    cands += [s for s in narrow if s.body == color and overlaps(s.bbox, tb) and not any(s.bbox == o.bbox for o in cands)]
    if not cands:
        return {"piece": ""}
    s = max(cands, key=lambda s: s.bbox[2] - s.bbox[0])
    g = det._stripe_geometry(CAM, s.center_row)
    if g is None:
        return {"piece": list(s.bbox)}
    rows = g[1]
    W, H = rows.width_px, rows.bottom - rows.top
    x0, y0, x1, y1 = s.bbox
    top_s, bot_s = det._body_extent(mask, s.body, x0, x1, y0, y1)
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
    top_inf, bot_inf = abs(top_s - rows.top) > tol, abs(bot_s - rows.bottom) > tol
    top, bottom = (int(round(rows.top)) if top_inf else top_s), (int(round(rows.bottom)) if bot_inf else bot_s)
    span = det._body_span(mask, s.body, x0, x1, max(0, top), min(h, bottom), y0, y1) if bottom - top >= 2 else None
    trusted = span is not None and max(span[1], x1) - min(span[0], x0) <= cfg.body_width * W
    sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if trusted else (x0, x1)
    costs = det._end_costs(s, mask, CAM, cfg, sx0, sx1) or (math.nan, math.nan)
    return {"piece": list(s.bbox), "piece_w": round((x1 - x0) / W, 3), "thin": int(s.small or s.narrow), "in_stripe_step": int(any(s is o for o in stripes)),
            "top_off": round((top_s - rows.top) / H, 3), "bottom_off": round((bot_s - rows.bottom) / H, 3), "full_slice": int(not (top_inf or bot_inf)),
            "span_w": round((sx1 - sx0) / W, 3), "span_trusted": int(trusted), "cost_left": round(costs[0], 4), "cost_right": round(costs[1], 4),
            "W": round(W, 1), "H": round(H, 1), "true_w_over_W": round((tb[2] - tb[0]) / W, 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="start,start+behind")
    ap.add_argument("--amounts", default="0.75")
    ap.add_argument("--out", default="cells_before")
    args = ap.parse_args(argv)
    S.register()
    arms = C.arm_list(args.arms, ())
    amounts = {float(a) for a in args.amounts.split(",")}
    out = S.OUT / args.out
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={a: A.ARMS[a] for a in arms}, BASE=A.SOURCE_BASE)
    A.install()
    stems = R.train_stems()
    segs = R.segmentations(stems)
    pools, _ = R.build_sources(segs)
    rows = []
    cell = collections.defaultdict(collections.Counter)
    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            if amount not in amounts:
                continue
            for a in arms:
                cfg = A.ARMS[a]
                r = R.score_scene(sc, cfg)
                tc, tb = sc.target
                notes = [f"{e['stage']}:{e['why']}" for e in r["log"] if overlaps(e["bbox"], tb) and e.get("body", tc) == tc and e["why"] != "kept"]
                p = widest_piece(sc, A.rule_config(cfg))
                if variant[:1] in ("L", "R") and p.get("piece") and "cost_left" in p:
                    own_right = variant[0] == "L"                      # hidden from the left: the right end is the barrel's own side
                    p["cost_own"], p["cost_cut"] = (p["cost_right"], p["cost_left"]) if own_right else (p["cost_left"], p["cost_right"])
                c = cell[(a, key, amount)]
                c["n"] += 1; c["found"] += r["found"]; c["place"] += r["place"]; c["big"] += r["size"] == "big"; c["small"] += r["size"] == "small"
                c["false"] += r["false"]
                if not r["found"]:
                    c["cause: " + r["cause"]] += 1
                rows.append({"arm": a, "pool": pool, "row": key, "amount": amount, "variant": variant, "stem": src.stem.replace("4A8B_", ""),
                             "color": dtp.COLOR_NAMES[src.color], "truth": list(tb), "found": r["found"], "place": r["place"], "size": r["size"],
                             "iou": r["iou"], "false": r["false"], "box": r["box"], "cause": r["cause"], "log": " | ".join(notes), **p})
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (out / "cell_scenes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval=""); w.writeheader(); w.writerows(rows)
    L = ["# The scorecard's cells, scene by scene: found / right place / too big / boxes where no barrel is, of n; then why not found", ""]
    for a in arms:
        L += [f"## `{a}`", "", "| cell | found | right place | too big | too small | no barrel there | n | why not found |", "|---|---|---|---|---|---|---|---|"]
        for (aa, key, amount), c in cell.items():
            if aa != a:
                continue
            why = ", ".join(f"{k[7:]} {v}" for k, v in c.most_common() if k.startswith("cause: "))
            L.append(f"| {R.ROW_NAME[key]}, {int(round(100 * amount))} % | {c['found']} | {c['place']} | {c['big']} | {c['small']} | {c['false']} | {c['n']} | {why} |")
        L.append("")
    (out / "cells.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
