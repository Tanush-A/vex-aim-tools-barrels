#!/usr/bin/env python3
"""Every box the detector draws on every train frame of every set, with what it is (by the hand labels) and which rule
made it. No detector change.

Which rule made it, two ways: (1) the reason log's stage (stripe step / stripeless piece / caps / pairs / half stripes) and
the box's flags; (2) knock-out: the creating switches (``strict.CREATORS``) whose being turned off alone removes this exact
box (a box that survives every single knock-out is made by the plain stripe step or the plain stripeless piece).

    python barrels/experiments/2026-11-24_occl_strict/boxes.py [--cfg start] [--out boxes] [--sheets]
Outputs: results/2026-11-24_occl_strict/<out>/boxes.csv, boxes.md, sheets/<stem>.png (every frame with a box that is not a hit)
Train frames only (``report.select_frames`` refuses test frames).
"""
from __future__ import annotations

import argparse
import csv
import dataclasses

import cv2

import strict as S
CE = S.closeup_census()                 # 2026-11-23_closeup_shape: the report.s frames and segmentation
from barrels import detect_types as dtp, detector as det, io, report as rp
from barrels.io import ORANGE

STAGE = {"barrel": "stripe", "cap": "cap", "pair": "post_pair", "slice": "slice", "half": "half_stripe", "piece": "piece"}
COL = {"hit": (0, 200, 0), "loose": (0, 200, 200), "part": (0, 140, 255), "wrongcolor": (255, 0, 255), "false": (0, 0, 255)}


def stage_of(log, bbox) -> str:
    for e in reversed(log):
        if e.get("why") == "kept" and e.get("box") is not None and tuple(e["box"]) == tuple(bbox):
            return STAGE.get(e.get("stage"), e.get("stage"))
    return "piece"


def knockouts(mask, cfg, boxes):
    """For each box (bbox tuple): the creating switches whose being off alone removes it."""
    out = {b: [] for b in boxes}
    for name in S.CREATORS:
        if not getattr(cfg, name):
            continue
        got = {b.bbox for b in det.detect(mask, dataclasses.replace(cfg, **{name: False}), S.CAM)}
        for b in boxes:
            if b not in got:
                out[b].append(name)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", default="start")
    ap.add_argument("--out", default="boxes")
    ap.add_argument("--sets", default=None)
    ap.add_argument("--sheets", action="store_true")
    a = ap.parse_args(argv)
    cfg = S.ARMS[a.cfg]
    out_dir = S.OUT / a.out
    (out_dir / "sheets").mkdir(parents=True, exist_ok=True)
    rows = []
    for label, stem, frame, mask in CE.masks(a.sets.split(",") if a.sets else None):
        lab = io.load_boxes(stem)
        gts = dtp.barrels_from_boxes(lab)
        log: list = []
        found = det.detect(mask, cfg, S.CAM, log)
        res = rp.score_boxes(stem, found, S.CAM)
        hit = {m.pred_idx for m in res.matches}
        ko = knockouts(mask, cfg, [b.bbox for b in found])
        frame_rows = []
        for i, b in enumerate(found):
            kind = S.judge(b.bbox, b.color, gts, i in hit)
            frame_rows.append(dict(set=label, extreme=int(S.is_extreme(label)), stem=stem, negative=int(bool(lab.get("negative"))),
                                   color="orange" if b.color == ORANGE else "blue", x0=b.bbox[0], y0=b.bbox[1], x1=b.bbox[2],
                                   y1=b.bbox[3], kind=kind, stage=stage_of(log, b.bbox), source=b.source,
                                   flags=" ".join(sorted(b.flags)), knockout=" ".join(ko[b.bbox])))
        rows += frame_rows
        if a.sheets and any(r["kind"] != "hit" for r in frame_rows):
            img = frame.bgr.copy()
            for g in gts:
                cv2.rectangle(img, g.bbox[:2], (g.bbox[2] - 1, g.bbox[3] - 1), (255, 255, 255), 1)
            for r in frame_rows:
                c = COL[r["kind"]]
                cv2.rectangle(img, (r["x0"], r["y0"]), (r["x1"] - 1, r["y1"] - 1), c, 2 if r["kind"] != "hit" else 1)
                if r["kind"] != "hit":
                    txt = f"{r['color'][0]} {r['stage']} {r['knockout']}"[:60]
                    cv2.putText(img, txt, (r["x0"], max(12, r["y0"] - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, c, 1)
            seg = cv2.cvtColor((mask == 1).astype("uint8") * 0, cv2.COLOR_GRAY2BGR)
            seg[mask == 1] = (0, 128, 255); seg[mask == 2] = (255, 80, 0)
            for r in frame_rows:
                if r["kind"] != "hit":
                    cv2.rectangle(seg, (r["x0"], r["y0"]), (r["x1"] - 1, r["y1"] - 1), COL[r["kind"]], 1)
            cv2.imwrite(str(out_dir / "sheets" / f"{stem}.png"), cv2.hconcat([img, seg]))
    keys = list(rows[0]) if rows else ["stem"]
    with open(out_dir / "boxes.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, keys); wr.writeheader(); wr.writerows(rows)
    L = [f"# Every box on every train frame, arm `{a.cfg}`", "",
         "kind: hit = v2 match; loose = same color IoU >= 0.5, bottom off; part = same color IoU 0.1-0.5; wrongcolor = on a",
         "labeled barrel of the other color; false = no labeled barrel there. knockout = the creating switches whose being off",
         "alone removes the box.", "", "## Totals per set", "", "| set | boxes | hit | loose | part | wrongcolor | false |",
         "|---|---|---|---|---|---|---|"]
    sets = list(dict.fromkeys(r["set"] for r in rows))
    for s in sets:
        rs = [r for r in rows if r["set"] == s]
        L.append(f"| {s}{' (extreme)' if S.is_extreme(s) else ''} | {len(rs)} | " +
                 " | ".join(str(sum(r['kind'] == k for r in rs)) for k in ("hit", "loose", "part", "wrongcolor", "false")) + " |")
    L += ["", "## Every box that is not a hit", "", "| set | frame | color | box | kind | stage | flags | knockout |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] != "hit":
            L.append(f"| {r['set']} | {r['stem']} | {r['color']} | {r['x0']} {r['y0']} {r['x1']} {r['y1']} | {r['kind']} | {r['stage']} | "
                     f"{r['flags']} | {r['knockout']} |")
    (out_dir / "boxes.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
