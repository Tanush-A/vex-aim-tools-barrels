#!/usr/bin/env python3
"""Clause R3 of PREREG.md: in the simulated side cuts, the boxes that are not the barrel, split into boxes that touch the
true box (on the barrel, failing the strict rule, or a second box on it) and boxes that do not touch it at all.

    python barrels/experiments/2026-11-26_sidecut/r3.py

Reads results/2026-11-26_sidecut/sidecut_scenes.csv to find the scenes with such boxes, remakes those scenes and
counts. Writes results/2026-11-26_sidecut/r3.md."""
from __future__ import annotations

import collections
import csv

import lib
from lib import ed

rows = list(csv.DictReader((lib.OUT / "sidecut_scenes.csv").open()))
want = {(r["pool"], r["stem"], r["truth"], r["kind"], r["amount"], r["side"], r["lean"], r["short"]) for r in rows if int(r["wrong"]) > 0}
pools = {p: lib.sources(p) for p in lib.POOLS}
count = collections.Counter()
for pool, srcs in pools.items():
    for src in srcs:
        for kind, amount, side, lean, short, sc in lib.side_cut_scenes(src):
            key = (pool, src.stem, str(list(src.bbox)), kind, str(amount), side, str(lean if kind == "slant" else 0), str(short))
            if key not in want:
                continue
            for mode in lib.MODES:
                preds, _ = lib.detect(sc.mask, mode)
                r = lib.score(preds, src.color, src.bbox)
                extra = sorted(preds, key=lambda p: -ed.box_iou(p.bbox, src.bbox))[r["found"]:]
                for p in extra:
                    touch = ed.box_iou(p.bbox, src.bbox) > 0
                    count[(mode, short, "touches the barrel" if touch else "OFF THE BARREL")] += 1
L = ["# R3: boxes that are not the barrel, in the simulated side cuts", "", "| arm | stripe short | touches the barrel | off the barrel |", "|---|---|---|---|"]
for mode in lib.MODES:
    for short in (0, lib.SHORT_PX):
        L.append(f"| `{mode}` | {short} px | {count[(mode, short, 'touches the barrel')]} | {count[(mode, short, 'OFF THE BARREL')]} |")
(lib.OUT / "r3.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
