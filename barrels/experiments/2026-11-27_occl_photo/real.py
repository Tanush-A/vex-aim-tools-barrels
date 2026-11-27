#!/usr/bin/env python3
"""Yardstick: real train frames, every box that changes, before and after (PREREG.md).

Every train frame that has an image and a box label is run through today's photo-in, boxes-out path (fixed colors,
detector, stripe by contrast; ``lib.run_frame``) with ``DetConfig.side_photo`` = "off" (today), "cut", "cut+bulge"
(and any further arm given with --arm NAME:field=value,...). Per arm: every box added, moved or removed against today,
with its state against the labels (``counting.classify_frame``) and the rule that drew it; one contact sheet per changed
frame; the occlusion frames (``occl`` in the name) barrel by barrel; totals.

    python barrels/experiments/2026-11-27_occl_photo/real.py [--out real] [--arm name:side_photo=cut,photo_cross=0]

Train frames only (``judge.load_frame`` refuses anything else). Writes results/2026-11-27_occl_photo/<out>/:
real.md, changes.csv, occl.csv, sheets/*.png (not committed).
"""
from __future__ import annotations

import argparse
import csv
import dataclasses

import cv2

import lib
from lib import ct, det, dtp, jg

EXTRA = (ct.NOTHING, ct.SECOND, ct.WRONG)
COLORS = {"off": (255, 255, 255), "cut": (255, 0, 255), "cut+bulge": (255, 255, 0)}


def parse_arm(spec: str):
    name, _, fields = spec.partition(":")
    kv = {}
    for item in filter(None, fields.split(",")):
        k, _, v = item.partition("=")
        kv[k] = v if k == "side_photo" else float(v)
    return name, kv


def run_arm(frame, kv: dict):
    cfg = dataclasses.replace(det.DetConfig(), **kv)
    log: list = []
    boxes = lib.run_frame(frame, cfg=cfg, log=log)
    return boxes, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="real")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--contains", nargs="*", default=[""])
    a = ap.parse_args()
    arms = {"off": {}, "cut": {"side_photo": "cut"}, "cut+bulge": {"side_photo": "cut+bulge"}}
    for spec in a.arm:
        n, kv = parse_arm(spec)
        arms[n] = kv
    out = lib.OUT / a.out
    (out / "sheets").mkdir(parents=True, exist_ok=True)
    for old in (out / "sheets").glob("*.png"):
        old.unlink()
    stems = lib.train_stems(tuple(a.contains))
    totals = {m: {k: 0 for k in (ct.FOUND, ct.OFF, ct.MISSED) + EXTRA} for m in arms}
    changes, occl = [], []
    n_changed = {m: 0 for m in arms if m != "off"}
    for stem in stems:
        frame = jg.load_frame(stem)
        gts, clean = lib.truth(stem)
        res = {}
        for m, kv in arms.items():
            boxes, log = run_arm(frame, kv)
            fc = ct.classify_frame(stem, boxes, gts, clean)
            res[m] = (boxes, log, fc)
            for s in fc.gt:
                totals[m][s] += 1
            for s in fc.boxes:
                if s in EXTRA:
                    totals[m][s] += 1
        base = {(b.color, b.bbox) for b in res["off"][0]}
        changed_any = False
        for m in arms:
            if m == "off":
                continue
            boxes, log, fc = res[m]
            now = {(b.color, b.bbox) for b in boxes}
            if now == base:
                continue
            n_changed[m] += 1
            changed_any = True
            for i, b in enumerate(boxes):
                if (b.color, b.bbox) not in base:
                    changes.append({"frame": stem, "arm": m, "what": "new box", "color": dtp.COLOR_NAMES[b.color], "box": list(b.bbox),
                                    "rule": lib.rule_of(log, b.bbox) or b.source, "state": fc.boxes[i]})
            b0, _, fc0 = res["off"]
            for i, b in enumerate(b0):
                if (b.color, b.bbox) not in now:
                    changes.append({"frame": stem, "arm": m, "what": "box gone", "color": dtp.COLOR_NAMES[b.color], "box": list(b.bbox),
                                    "rule": lib.rule_of(res["off"][1], b.bbox) or b.source, "state": fc0.boxes[i]})
        if changed_any:
            focus = [b.bbox for m in arms for b in res[m][0] if (b.color, b.bbox) not in base]
            focus += [b for c, b in base if any((c, b) not in {(x.color, x.bbox) for x in res[m][0]} for m in arms)]
            img = lib.sheet(frame.bgr, lib.pl.segment(frame, lib.model())[0], gts,
                            {m: (res[m][0], COLORS.get(m, (0, 255, 255))) for m in arms}, focus=focus, title=stem[5:])
            cv2.imwrite(str(out / "sheets" / f"{stem}.png"), img)
        if "occl" in stem:
            for gi, g in enumerate(gts):
                row = {"frame": stem[5:], "barrel": dtp.COLOR_NAMES[g.color], "truth": list(g.bbox), "flags": "+".join(sorted(g.flags))}
                for m in arms:
                    row[m] = res[m][2].gt[gi]
                occl.append(row)
    with open(out / "changes.csv", "w", newline="") as f:
        w = csv.DictWriter(f, ["frame", "arm", "what", "color", "box", "rule", "state"])
        w.writeheader()
        w.writerows(changes)
    with open(out / "occl.csv", "w", newline="") as f:
        w = csv.DictWriter(f, ["frame", "barrel", "truth", "flags"] + list(arms))
        w.writeheader()
        w.writerows(occl)
    L = [f"# Real train frames: every box that changes ({len(stems)} frames with a box label)", "",
         "Arms: " + "; ".join(f"`{m}` = {kv or 'today'}" for m, kv in arms.items()) + ". The photo is passed to both detector runs "
         "(the first and the one on the contrast-painted mask).", "",
         "Frames whose boxes differ from today: " + ", ".join(f"`{m}` {n}" for m, n in n_changed.items()), "",
         "| frame | arm | what | box | rule | state |", "|---|---|---|---|---|---|"]
    L += [f"| {c['frame'][5:]} | `{c['arm']}` | {c['what']} | {c['color']} {c['box']} | {c['rule']} | {c['state']} |" for c in changes]
    L += ["", "Totals over these frames (per frame, not per placement; states of `counting.classify_frame`):", "",
          "| | " + " | ".join(f"`{m}`" for m in arms) + " |", "|---|" + "---|" * len(arms)]
    for k in (ct.FOUND, ct.OFF, ct.MISSED) + EXTRA:
        L.append(f"| {k} | " + " | ".join(str(totals[m][k]) for m in arms) + " |")
    occ_found = {m: sum(r[m] in (ct.FOUND,) for r in occl) for m in arms}
    occ_on = {m: sum(r[m] in (ct.FOUND, ct.OFF) for r in occl) for m in arms}
    L += ["", f"Occlusion frames (`occl` in the name), {len(occl)} labelled barrels: found (strict) "
          + ", ".join(f"`{m}` {occ_found[m]}" for m in arms) + "; found or box off: " + ", ".join(f"`{m}` {occ_on[m]}" for m in arms) + "."]
    occ_changed = [r for r in occl if len({r[m] for m in arms}) > 1]
    if occ_changed:
        L += ["", "Occlusion barrels whose state changes:", "", "| frame | barrel | truth | " + " | ".join(arms) + " |", "|---|---|---|" + "---|" * len(arms)]
        L += [f"| {r['frame']} | {r['barrel']} | {r['truth']} | " + " | ".join(r[m] for m in arms) + " |" for r in occ_changed]
    (out / "real.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
