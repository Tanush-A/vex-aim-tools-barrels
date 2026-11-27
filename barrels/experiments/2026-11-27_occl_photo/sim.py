#!/usr/bin/env python3
"""Yardstick: the simulated side cuts of 2026-11-26_sidecut, with a synthetic photo (PREREG.md).

Every source barrel of the three pools (HOME, CAMPUS, ABP white; chosen exactly as the sidecut experiment chose them:
no flag, 3 px inside the frame, not overlapping another box, found by today's detector alone) is cut at the side by a
straight upright edge and by a slanted one (both leans), from the left and the right, 50 / 60 / 65 / 75 % of its width
hidden, plain and "real-like" (the stripe ends 6 px before the cut) — the sidecut scenes (``occlude.make_scene``).

The detector needs a photo for the rule. The photo of a scene = the source frame's own photo with the occluder painted
over it as a flat dark gray (40, 40, 40) block: from the cut 1.5 W outward, from 0.6 H above the barrel's top to 0.3 H
below its bottom (a box taller than the barrel, standing nearer). Variant ``short``: the block ends at the barrel's
top (a thing exactly as tall as the barrel, so only the band below can show the line). This tests the geometry of the
rule and nothing about real occluders (no shadow, no blur, no lens curve).

Scored against the FULL box: found (strict v2 rule) and placed (found and the box centre within 10 % of the true width).

    python barrels/experiments/2026-11-27_occl_photo/sim.py

Train frames only. Writes results/2026-11-27_occl_photo/sim.md, sim.csv.
"""
from __future__ import annotations

import collections
import csv
import dataclasses

import numpy as np

import candidate as cd
import lib
from lib import det, dtp, ed, io, jg
from barrels import occlude as oc

POOLS = {"HOME": "4A8B_window_light_", "CAMPUS": "4A8B_campus_light_", "ABP white": "4A8B_window_abpwhite_"}
AMOUNTS = (0.5, 0.6, 0.65, 0.75)
SHORT_PX = 6
ARMS = {"off": {}, **cd.ARMS}
DARK = (40, 40, 40)


def eligible(b, others):
    x0, y0, x1, y1 = b["bbox"]
    if b.get("flags") or x0 < 3 or y0 < 3 or x1 > 637 or y1 > 477:
        return False
    return not any(min(x1, o["bbox"][2]) - max(x0, o["bbox"][0]) > 2 and min(y1, o["bbox"][3]) > max(y0, o["bbox"][1]) for o in others)


def score(preds, color, box):
    g = dtp.Barrel(color=color, bbox=tuple(box), source="gt")
    right = [p for p in preds if p.color == color and ed.box_iou(p.bbox, box) >= ed.IOU_THR and ed.bottom_within_tol(p, g)]
    cx, W = (box[0] + box[2]) / 2, box[2] - box[0]
    placed = any(abs((p.bbox[0] + p.bbox[2]) / 2 - cx) <= 0.1 * W for p in right)
    return int(bool(right)), int(placed), len(preds) - int(bool(right))


def sources():
    out = []
    for pool, prefix in POOLS.items():
        for stem in lib.train_stems((prefix,)):
            frame = jg.load_frame(stem)
            mask = lib.pl.segment(frame, lib.model())[0]
            bs = io.load_boxes(stem)["barrels"]
            for i, b in enumerate(bs):
                others = [o for j, o in enumerate(bs) if j != i]
                if not eligible(b, others):
                    continue
                src = oc.cut_source(mask, b["bbox"], dtp.COLOR_BY_NAME[b["color"]], [o["bbox"] for o in others], stem=stem, pool=pool)
                if score(det.detect(oc.make_scene(src, "edge", 0.0).mask, det.DetConfig(), lib.CAM), src.color, src.bbox)[0]:
                    out.append((src, frame.rgb))
    return out


def shorten(mask, src, kind, amount, side, lean, px):
    x0, y0, x1, y1 = src.bbox
    W, H = x1 - x0, y1 - y0
    cut = int(round(amount * W))
    other = oc.BLUE if src.color == oc.ORANGE else oc.ORANGE
    for r in range(mask.shape[0]):
        off = lean * oc.SLANT_LEAN * W * (r - (y0 + y1) / 2) / H if kind == "slant" else 0.0
        b = int(np.ceil(x0 + cut + off)) if side == "L" else int(np.ceil(x1 - cut + off))
        seg = mask[r, max(0, b):max(0, b + px)] if side == "L" else mask[r, max(0, b - px):max(0, b)]
        seg[seg == other] = 0


def photo_of(rgb, src, kind, amount, side, lean, tall: bool):
    x0, y0, x1, y1 = src.bbox
    W, H = x1 - x0, y1 - y0
    cut = int(round(amount * W))
    img = np.array(rgb, copy=True)
    r0, r1 = max(0, int(y0 - (0.6 * H if tall else 0))), min(480, int(y1 + 0.3 * H))
    for r in range(r0, r1):
        off = lean * oc.SLANT_LEAN * W * (r - (y0 + y1) / 2) / H if kind == "slant" else 0.0
        if side == "L":
            b = int(np.ceil(x0 + cut + off))
            img[r, max(0, int(b - 1.5 * W)):max(0, b)] = DARK
        else:
            b = int(np.ceil(x1 - cut + off))
            img[r, max(0, b):min(640, int(b + 1.5 * W))] = DARK
    return img


def main() -> int:
    srcs = sources()
    print(len(srcs), "source barrels")
    rows = []
    cfgs = {a: det.DetConfig(**kv) for a, kv in ARMS.items()}
    for src, rgb in srcs:
        for kind in ("edge", "slant"):
            for amount in AMOUNTS:
                for side in "LR":
                    for lean in ((1, -1) if kind == "slant" else (1,)):
                        for short in (0, SHORT_PX):
                            sc = oc.make_scene(src, kind, amount, side, cam=lib.CAM, lean=lean)
                            if short:
                                shorten(sc.mask, src, kind, amount, side, lean, short)
                            for tall in (True, False):
                                photo = photo_of(rgb, src, kind, amount, side, lean, tall)
                                for a, cfg in cfgs.items():
                                    preds = det.detect(sc.mask, cfg, lib.CAM, photo=photo if a != "off" else None)
                                    f, p, wrong = score(preds, src.color, src.bbox)
                                    rows.append({"pool": src.pool, "stem": src.stem, "kind": kind, "amount": amount, "side": side, "lean": lean,
                                                 "short": short, "occluder": "tall" if tall else "barrel-high", "arm": a, "found": f, "placed": p, "wrong": wrong})
    out = lib.OUT
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "sim.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    agg = collections.defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        k = (r["occluder"], r["short"], r["arm"], r["amount"])
        a = agg[k]
        a[0] += r["found"]; a[1] += r["placed"]; a[2] += r["wrong"]; a[3] += 1
    L = ["# Simulated side cuts with a synthetic photo", "", f"{len(srcs)} source barrels (HOME, CAMPUS, ABP white), edge + slant (both leans), "
         "left and right: 6 scenes per barrel per amount. Cell = found (strict) / placed (centre within 10 %) / other boxes, of n.", ""]
    for occl in ("tall", "barrel-high"):
        for short in (0, SHORT_PX):
            L += [f"## occluder {occl}, {'stripe ends 6 px early' if short else 'plain'}", "", "| arm | " + " | ".join(f"{int(a * 100)} %" for a in AMOUNTS) + " |",
                  "|---|" + "---|" * len(AMOUNTS)]
            for arm in ARMS:
                cells = []
                for a in AMOUNTS:
                    f, p, wr, n = agg[(occl, short, arm, a)]
                    cells.append(f"{f} / {p} / {wr} of {n}")
                L.append(f"| `{arm}` | " + " | ".join(cells) + " |")
            L.append("")
    (out / "sim.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
