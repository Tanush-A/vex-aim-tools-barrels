#!/usr/bin/env python3
"""Part 1, census: when are two pieces of stripe color at the same rows ONE stripe? Measurement only.

A piece = a connected group of stripe-colored pixels that have body color above and below them (exactly the stripe
finder's candidates, before any size test). For every piece, the nearest piece to its right that shares rows with it
(half the height of the shorter, as ``stripe_join``) makes a pair. Per pair:

    span / W        left end of the left piece to right end of the right piece, in barrel widths at that row
    gap / W         the columns between them
    shaped          both pieces have a stripe's shape (not taller than wide, not taller than 1.6 stripe heights):
                    what ``stripe_join`` asks today
    body over gap   the share of the gap's columns where body color is seen right above AND right below the stripe rows
                    (the finder's sandwich, asked of the gap's own pixels)
    in the gap      what the gap's pixels at the stripe rows are: unpainted, body color, stripe color
    truth           do the two pieces lie in the same hand-drawn barrel box of that body color, in two different
                    boxes, or is one of them (or both) on no barrel at all

Masks: the train frames as the eval table segments them (HOME hand masks, HOME leave one scene out, CAMPUS; the black
and wood tables report only), and the HOME hand masks with the stripe patch or one stripe break at each width of
``diag_stripe.py``, seeds 0 to 4.

Train frames only (asserted in the loaded scripts).

    python barrels/experiments/2026-11-20_occl_sliver/census_pairs.py
Outputs: results/2026-11-20_occl_sliver/ census_pairs.md, census_pairs.csv
"""
from __future__ import annotations

import collections
import csv
import sys
import types

import cv2
import numpy as np

import sliver as S
from barrels import degrade as dg, detect_types as dtp, detector as det, geometry as geo, io
from barrels.io import BLUE, ORANGE

C, A = S.C, S.A
CAM = geo.AIM_4A8B6118_BOXFIT
WIDTHS = (0.03, 0.06, 0.1, 0.15, 0.2, 0.3)
SEEDS = tuple(range(5))
SPAN_MAX = 2.5                    # pairs further apart than this many barrel widths are not listed


def pieces_of(mask: np.ndarray, body: int, cfg):
    h, w = mask.shape
    other = BLUE if body == ORANGE else ORANGE
    rows_idx = np.arange(h)[:, None]
    reach = det._reach_by_row(CAM, h, cfg)[:, None]
    bm = det._closed(mask == body, cfg)
    om = det._closed(mask == other, cfg) & ~bm
    up = np.maximum.accumulate(np.where(bm, rows_idx, -10 ** 6), axis=0)
    dn = np.minimum.accumulate(np.where(bm, rows_idx, 10 ** 6)[::-1], axis=0)[::-1]
    sand = ((rows_idx - up) <= reach) & ((dn - rows_idx) <= reach)
    n, lab, st, _ = cv2.connectedComponentsWithStats((om & sand).astype(np.uint8), connectivity=8)
    core = {}
    for i in range(1, n):
        ys = np.where(lab == i)[0]
        core[tuple(int(v) for v in st[i])] = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)   # the finder's height measure
    return sand, [tuple(int(v) for v in st[i]) for i in range(1, n)], core


def owner(piece, body: int, truths) -> int:
    """Index of the hand-drawn box of body color ``body`` that holds the piece's centre (the nearest centre wins); -1 = none."""
    x, y, bw, bh, _ = piece
    cx, cy = x + bw / 2, y + bh / 2
    best, bd = -1, 1e9
    for i, (c, b) in enumerate(truths):
        if c == body and b[0] <= cx < b[2] and b[1] <= cy < b[3]:
            d = abs(cx - (b[0] + b[2]) / 2)
            if d < bd:
                best, bd = i, d
    return best


def pairs_of(mask: np.ndarray, truths, cfg) -> list[dict]:
    out = []
    for body in (ORANGE, BLUE):
        other = BLUE if body == ORANGE else ORANGE
        sand, pcs, core = pieces_of(mask, body, cfg)
        pcs.sort(key=lambda p: (p[0], p[1]))
        for i, a in enumerate(pcs):
            ax, ay, aw, ah, aa = a
            best = None
            for b in pcs[i + 1:]:
                bx, by, bw, bh, ba = b
                shared = min(ay + ah, by + bh) - max(ay, by)
                if 2 * shared < min(ah, bh):
                    continue
                gap = bx - (ax + aw)
                if best is None or gap < best[0]:
                    best = (gap, b)
            if best is None:
                continue
            gap, b = best
            bx, by, bw, bh, ba = b
            y0, y1 = min(ay, by), max(ay + ah, by + bh)
            g = det._stripe_geometry(CAM, (y0 + y1) / 2)
            if g is None:
                continue
            W, Hs = g[1].width_px, g[1].stripe_bottom - g[1].stripe_top
            if W < cfg.min_width_px or Hs < cfg.min_stripe_px:
                continue
            span = max(ax + aw, bx + bw) - ax
            if span > SPAN_MAX * W:
                continue

            def shaped(p):
                return p[3] <= p[2] and p[3] <= cfg.stripe_h_max * Hs
            ga, gb = ax + aw, bx
            if gb > ga:
                ya, yb = max(ay, by), min(ay + ah, by + bh)
                if yb <= ya:
                    ya, yb = y0, y1
                over = float(sand[ya:yb, ga:gb].any(axis=0).mean())
                box = mask[y0:y1, ga:gb]
                fill = (float((box == 0).mean()), float((box == body).mean()), float((box == other).mean()))
            else:
                over, fill = 1.0, (0.0, 0.0, 0.0)
            oa, ob = owner(a, body, truths), owner(b, body, truths)
            truth = "same barrel" if oa >= 0 and oa == ob else ("two barrels" if oa >= 0 and ob >= 0 else ("one on no barrel" if max(oa, ob) >= 0 else "both on no barrel"))
            out.append({"body": dtp.COLOR_NAMES[body], "left": [ax, ay, ax + aw, ay + ah], "right": [bx, by, bx + bw, by + bh], "area_left": aa, "area_right": ba,
                        "W": round(W, 1), "Hs": round(Hs, 1), "span_w": round(span / W, 3), "gap_w": round(gap / W, 3), "gap_hs": round(gap / Hs, 2),
                        "shaped_left": int(shaped(a)), "shaped_right": int(shaped(b)), "body_over_gap": round(over, 3),
                        "core_left_hs": round(core[a] / Hs, 2), "core_right_hs": round(core[b] / Hs, 2),
                        "gap_unpainted": round(fill[0], 3), "gap_body": round(fill[1], 3), "gap_stripe_color": round(fill[2], 3), "truth": truth})
    return out


def main(argv=None) -> int:
    S.register()
    cfg = A.rule_config(A.ARMS["start"])
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={"start": A.ARMS["start"]}, BASE=A.SOURCE_BASE)
    stems = R.train_stems()
    segs = R.segmentations(stems, with_extreme=True)

    def truths_of(stem):
        return [(dtp.COLOR_BY_NAME[b["color"]], tuple(b["bbox"])) for b in io.load_boxes(stem)["barrels"]]

    rows = []
    for source, pool in (("HOME hand masks", "HOME hand masks"), ("HOME, leave one scene out", "HOME color model"), ("CAMPUS", "CAMPUS color model"),
                         ("BLACK (report only)", "BLACK"), ("WOOD (report only)", "WOOD")):
        for stem, mask in sorted(segs[pool].items()):
            for p in pairs_of(mask, truths_of(stem), cfg):
                rows.append({"source": source, "stem": stem.replace("4A8B_", ""), "seed": "", **p})
    hand = segs["HOME hand masks"]
    home = sorted(hand)
    levels = {f"stripe patch {w} W": dg.Damage(stripe_highlight=w) for w in WIDTHS}
    levels.update({f"one stripe break {w} W": dg.Damage(stripe_breaks=(1, w)) for w in WIDTHS})
    levels.update({f"two stripe breaks {w} W": dg.Damage(stripe_breaks=(2, w)) for w in WIDTHS})
    levels.update({"white tables, bad day": dg.REALISTIC["white tables, bad day"], "medium": dg.SEVERITIES["medium"]})
    for level, d in levels.items():
        for seed in SEEDS:
            for i, s in enumerate(home):
                t = truths_of(s)
                mask = dg.damage(hand[s], [b for _, b in t], d, seed=1000 * seed + i)
                for p in pairs_of(mask, t, cfg):
                    rows.append({"source": level, "stem": s.replace("4A8B_", ""), "seed": seed, **p})
    S.OUT.mkdir(parents=True, exist_ok=True)
    with (S.OUT / "census_pairs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    groups = {"real masks (HOME hand, HOME leave one scene out, CAMPUS)": lambda r: r["source"] in ("HOME hand masks", "HOME, leave one scene out", "CAMPUS"),
              "black and wood tables (report only)": lambda r: "report only" in r["source"],
              "HOME hand masks with a stripe patch": lambda r: r["source"].startswith("stripe patch"),
              "HOME hand masks with one stripe break": lambda r: r["source"].startswith("one stripe break"),
              "HOME hand masks with two stripe breaks": lambda r: r["source"].startswith("two stripe breaks"),
              "HOME hand masks, bad day": lambda r: r["source"] == "white tables, bad day",
              "HOME hand masks, medium": lambda r: r["source"] == "medium"}
    kinds = ("same barrel", "two barrels", "one on no barrel", "both on no barrel")
    span_lim = max(cfg.body_width, 1.0)
    L = ["# Two pieces of stripe color at the same rows: one stripe or not? (a census; no acceptance number)", "",
         "A pair = a piece of sandwiched stripe color and the nearest such piece to its right that shares rows with it. `fits` = the two together span at most "
         f"{span_lim} barrel widths (the limit of `stripe_join`). `shaped` = both pieces have a stripe's shape (what `stripe_join` asks today). "
         "`body over the gap` = the share of the gap's columns with body color right above and right below.", ""]
    for name, pred in groups.items():
        rs = [r for r in rows if pred(r)]
        L += [f"## {name}", "", "| the two pieces lie on | pairs | fits | fits and shaped (joined today) | fits, not shaped | fits, body over the whole gap (1.0) | "
              "fits, body over 0.8 of the gap | fits, gap at most one stripe height | fits, either (0.8 or one stripe height) |", "|---|---|---|---|---|---|---|---|---|"]
        for k in kinds:
            v = [r for r in rs if r["truth"] == k]
            fit = [r for r in v if r["span_w"] <= span_lim]
            sh = [r for r in fit if r["shaped_left"] and r["shaped_right"]]
            full = [r for r in fit if r["body_over_gap"] >= 1.0]
            most = [r for r in fit if r["body_over_gap"] >= 0.8]
            small = [r for r in fit if r["gap_hs"] <= 1.0]
            either = [r for r in fit if r["body_over_gap"] >= 0.8 or r["gap_hs"] <= 1.0]
            L.append(f"| {k} | {len(v)} | {len(fit)} | {len(sh)} | {len(fit) - len(sh)} | {len(full)} | {len(most)} | {len(small)} | {len(either)} |")
        L.append("")
        for k in kinds:
            fit = [r for r in rs if r["truth"] == k and r["span_w"] <= span_lim]
            if fit:
                sp = np.array([r["span_w"] for r in fit]); gp = np.array([r["gap_w"] for r in fit]); bo = np.array([r["body_over_gap"] for r in fit])
                L.append(f"- {k}, pairs that fit: span / W median {np.median(sp):.2f} (largest {sp.max():.2f}); gap / W median {np.median(gp):.2f} "
                         f"(largest {gp.max():.2f}); body over the gap median {np.median(bo):.2f} (lowest {bo.min():.2f}).")
        L.append("")
    L += ["## The bridge: pieces that fit, each no taller than a stripe by the finder's own height measure, body over EVERY column of the gap", "",
          "`core` = the 10th to 90th percentile of the piece's rows + 1, against the expected stripe height (the finder's height measure; the limit "
          f"`stripe_h_max` = {cfg.stripe_h_max}). `bridged` = fits, both cores at most that, body right above and right below in every column of the gap. "
          "`joined today` = fits and both shaped. Each cell: bridged pairs (of them joined today already).", "",
          "| masks | same barrel | two barrels | one on no barrel | both on no barrel |", "|---|---|---|---|---|"]
    for name, pred in groups.items():
        rs = [r for r in rows if pred(r)]
        cells = []
        for k in kinds:
            br = [r for r in rs if r["truth"] == k and r["span_w"] <= span_lim and r["body_over_gap"] >= 1.0
                  and max(r["core_left_hs"], r["core_right_hs"]) <= cfg.stripe_h_max]
            cells.append(f"{len(br)} ({sum(1 for r in br if r['shaped_left'] and r['shaped_right'])})")
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    L += ["", "Every bridged pair that is not on one barrel:", "", "| masks | frame | seed | body | left piece | right piece | span / W | gap / W | cores / Hs | truth |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if (r["truth"] != "same barrel" and r["span_w"] <= span_lim and r["body_over_gap"] >= 1.0
                and max(r["core_left_hs"], r["core_right_hs"]) <= cfg.stripe_h_max):
            L.append(f"| {r['source']} | {r['stem']} | {r['seed']} | {r['body']} | {r['left']} ({r['area_left']} px) | {r['right']} ({r['area_right']} px) | "
                     f"{r['span_w']} | {r['gap_w']} | {r['core_left_hs']}, {r['core_right_hs']} | {r['truth']} |")
    L.append("")
    L += ["## Every pair on the real masks that fits in one barrel's width and is NOT on one barrel", "",
          "| frames | frame | body | left piece | right piece | span / W | gap / W | shaped | body over the gap | truth |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["source"] in ("HOME hand masks", "HOME, leave one scene out", "CAMPUS") and r["span_w"] <= span_lim and r["truth"] != "same barrel":
            L.append(f"| {r['source']} | {r['stem']} | {r['body']} | {r['left']} ({r['area_left']} px) | {r['right']} ({r['area_right']} px) | {r['span_w']} | {r['gap_w']} | "
                     f"{'yes' if r['shaped_left'] and r['shaped_right'] else 'no'} | {r['body_over_gap']} | {r['truth']} |")
    (S.OUT / "census_pairs.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
