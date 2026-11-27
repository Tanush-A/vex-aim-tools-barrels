#!/usr/bin/env python3
"""Yardstick (c), second half (PREREG.md): the masks of the proof harness with the flag ON.

The harness (``experiments/2026-11-26_collapse``) holds 5435 class masks: the 261 real train masks, each with one
pixel taken off or added, the 45 hand-threshold masks, the 53 pool masks, 666 damaged masks and 3888 simulated scenes.
Each is run with every value of ``DetConfig.side_cut``. Where the mask belongs to a labelled train frame (every group
but ``scene``) each box gets its state against the labels (``counting.classify_frame``): found / off / second /
wrong_color / nothing. For ``scene`` only the boxes are compared (their truth is scored by ``sim.py``).

    python barrels/experiments/2026-11-26_sidecut/harness_on.py <inputs.pkl>

Train frames only: every stem is checked with ``judge.require_train``. Writes results/2026-11-26_sidecut/
harness_on.md and harness_on_changes.csv.
"""
from __future__ import annotations

import collections
import csv
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

import cv2
import numpy as np

import lib
from lib import dtp, io, jg
from barrels import counting as ct

STATES = (ct.FOUND, ct.OFF, ct.SECOND, ct.WRONG, ct.NOTHING)


def stem_of(key: str) -> str | None:
    return None if key.startswith("scene/") else key.split("/")[-1]


def work(items: list[tuple[str, bytes]]) -> list[dict]:
    rows = []
    for key, png in items:
        mask = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)
        stem = stem_of(key)
        gts, clean, labelled = [], True, False
        if stem is not None and io.boxes_path(stem).exists():
            label = io.load_boxes(stem)
            gts, clean, labelled = dtp.barrels_from_boxes(label), label.get("clean", True), True
        base = None
        for mode in lib.MODES:
            preds, log = lib.detect(mask, mode)
            k = tuple(sorted((int(p.color), tuple(int(v) for v in p.bbox)) for p in preds))
            base = k if mode == lib.MODES[0] else base
            row = {"key": key, "group": key.split("/")[0], "mode": mode, "boxes": len(preds), "changed": int(k != base), "labelled": int(labelled),
                   "new": [list(b) + [lib.rule_of(log, b[1])] for b in k if b not in base], "gone": [list(b) for b in base if b not in k]}
            if labelled:
                fc = ct.classify_frame(stem, preds, gts, clean)
                row.update({f"box_{s}": sum(x == s for x in fc.boxes) for s in STATES})
                row.update({f"gt_{s}": sum(x == s for x in fc.gt) for s in ct.GT_STATES})
                by = {(int(p.color), tuple(int(v) for v in p.bbox)): fc.boxes[i] for i, p in enumerate(preds)}
                row["new"] = [n + [by[(n[0], tuple(n[1]))]] for n in row["new"]]
            rows.append(row)
    return rows


def main(argv=None) -> int:
    path = (argv or sys.argv[1:])[0]
    enc = pickle.load(open(path, "rb"))
    keys = sorted(enc)
    stems = sorted({s for s in map(stem_of, keys) if s})
    jg.require_train(stems)
    chunks = [[(k, enc[k]) for k in keys[i:i + 40]] for i in range(0, len(keys), 40)]
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 2)) as ex:
        rows = [r for rs in ex.map(work, chunks) for r in rs]
    groups = list(dict.fromkeys(r["group"] for r in rows))
    L = ["# The proof harness's masks with the flag on", "",
         f"{len(keys)} masks ({', '.join(f'{g} {sum(1 for k in keys if k.split(chr(47))[0] == g)}' for g in groups)}), each run with `centred` (today), `own_side` and "
         "`own_side+centred`. A box's state is read against the frame's labels: found (strict) / off (on its barrel, fails strict) / second / wrong color / nothing. "
         "`scene` has no labels here; `sim.py` scores those kinds.", "",
         "| group | arm | masks whose boxes differ from today | boxes | barrels found | box off | missed | boxes on nothing | second | wrong color |", "|---|---|---|---|---|---|---|---|---|---|"]
    for g in groups:
        for mode in lib.MODES:
            rs = [r for r in rows if r["group"] == g and r["mode"] == mode]
            lab = [r for r in rs if r["labelled"]]

            def s(k):
                return str(sum(r[k] for r in lab)) if lab else "-"
            L.append(f"| {g} | `{mode}` | {sum(r['changed'] for r in rs)} of {len(rs)} | {sum(r['boxes'] for r in rs)} | {s('gt_found')} | {s('gt_off')} | {s('gt_missed')} | "
                     f"{s('box_nothing')} | {s('box_second')} | {s('box_wrong_color')} |")
    L += ["", "## The new boxes on labelled masks, by the rule that drew them and their state", ""]
    for mode in lib.MODES[1:]:
        c = collections.Counter((r["group"], n[2], n[3]) for r in rows if r["mode"] == mode and r["labelled"] for n in r["new"])
        L.append(f"- `{mode}`: " + (", ".join(f"{g} {rule} {state} {v}" for (g, rule, state), v in sorted(c.items())) or "none"))
    L += ["", "## New boxes that are not on their barrel (every one)", ""]
    bad = [(r["key"], r["mode"], n) for r in rows if r["mode"] != lib.MODES[0] and r["labelled"] for n in r["new"] if n[3] in (ct.NOTHING, ct.SECOND, ct.WRONG)]
    L += [f"- `{mode}` {key}: {dtp.COLOR_NAMES[n[0]]} {n[1]} by {n[2]}: {n[3]}" for key, mode, n in bad] or ["none"]
    (lib.OUT / "harness_on.md").write_text("\n".join(L) + "\n")
    with (lib.OUT / "harness_on_changes.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "mode", "new boxes (color, box, rule, state)", "boxes gone (color, box)"])
        for r in rows:
            if r["changed"]:
                w.writerow([r["key"], r["mode"], r["new"], r["gone"]])
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
