#!/usr/bin/env python3
"""Acceptance clauses 1 and 3 of PREREG.md, frame by frame: every train frame of every set (segmented as the report does),
each arm against ``start``. Lists every box that appears or disappears (with what it is: a labeled barrel found under the v2
rule, or not), every labeled barrel of the scenes close / held / edge / top / topstripe (and any labeled barrel touching
the frame bottom) found or not by each arm, and every box on an empty frame.

    python barrels/experiments/2026-11-23_closeup_shape/compare.py [--arms side,stripe,shape] [--out round1]
Outputs: results/2026-11-23_closeup_shape/<out>/compare.md, compare_changes.csv, compare_closeups.csv
"""
from __future__ import annotations

import argparse
import csv

import census as CE
import closeup as K
from barrels import detect_types as dtp, detector as det, io, report as rp
from barrels.io import ORANGE, parse_name

SCENES = ("close", "held", "edge", "top", "topstripe")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="side,stripe,shape")
    ap.add_argument("--out", default="round1")
    a = ap.parse_args(argv)
    arms = ["start"] + [x for x in a.arms.split(",") if x and x != "start"]
    out_dir = K.OUT / a.out
    out_dir.mkdir(parents=True, exist_ok=True)
    changes, closeups, empty = [], [], []
    for label, stem, frame, mask in CE.masks():
        h = mask.shape[0]
        lab = io.load_boxes(stem)
        gts = dtp.barrels_from_boxes(lab)
        res, boxes = {}, {}
        for arm in arms:
            preds = det.detect(mask, K.ARMS[arm], CE.CAM)
            boxes[arm] = preds
            res[arm] = rp.score_boxes(stem, preds, CE.CAM)
        for arm in arms:
            if lab.get("negative") and boxes[arm]:
                empty.append(dict(arm=arm, set=label, stem=stem, boxes=" ".join(str(b.bbox) for b in boxes[arm])))
        scene = parse_name(stem)["scene"]
        for gi, g in enumerate(gts):
            if scene in SCENES or g.bbox[3] >= h - 2 or {"close", "held"} & set(g.flags):
                row = dict(set=label, stem=stem, color="orange" if g.color == ORANGE else "blue", box=" ".join(map(str, g.bbox)),
                           flags=" ".join(sorted(g.flags)))
                for arm in arms:
                    row[arm] = int(any(m.gt_idx == gi for m in res[arm].matches))
                closeups.append(row)
        base = {b.bbox: b for b in boxes["start"]}
        for arm in arms[1:]:
            now = {b.bbox: b for b in boxes[arm]}
            hit = {boxes[arm][m.pred_idx].bbox for m in res[arm].matches}
            hit0 = {boxes["start"][m.pred_idx].bbox for m in res["start"].matches}
            for bb in set(now) - set(base):
                changes.append(dict(arm=arm, set=label, stem=stem, what="added", box=" ".join(map(str, bb)), source=now[bb].source,
                                    on_barrel=int(bb in hit)))
            for bb in set(base) - set(now):
                changes.append(dict(arm=arm, set=label, stem=stem, what="removed", box=" ".join(map(str, bb)), source=base[bb].source,
                                    on_barrel=int(bb in hit0)))
    with open(out_dir / "compare_changes.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, ["arm", "set", "stem", "what", "box", "source", "on_barrel"]); wr.writeheader(); wr.writerows(changes)
    with open(out_dir / "compare_closeups.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, list(closeups[0])); wr.writeheader(); wr.writerows(closeups)
    L = ["# Every box that changes against `start`, every close-up / held / edge / top barrel, every box on an empty frame", "",
         "Train frames of every set, segmented as the report does (HOME leave one scene out). `on_barrel` = the box finds a",
         "labeled barrel under the v2 rule.", "", "## Boxes that appear or disappear", "",
         "| arm | set | frame | what | box | source | on a barrel |", "|---|---|---|---|---|---|---|"]
    for c in changes:
        L.append(f"| {c['arm']} | {c['set']} | {c['stem']} | {c['what']} | {c['box']} | {c['source']} | {'yes' if c['on_barrel'] else 'no'} |")
    L += ["", "## Close-up / held / edge / top barrels (and any labeled barrel at the frame bottom): found (1) or not (0)", "",
          "| set | frame | color | label box | flags | " + " | ".join(arms) + " |", "|---|---|---|---|---|" + "---|" * len(arms)]
    for r in closeups:
        L.append(f"| {r['set']} | {r['stem']} | {r['color']} | {r['box']} | {r['flags']} | " + " | ".join(str(r[x]) for x in arms) + " |")
    L += ["", "| arm | found of " + str(len(closeups)) + " |", "|---|---|"] + [f"| {x} | {sum(r[x] for r in closeups)} |" for x in arms]
    L += ["", "## Boxes on empty frames", "", "| arm | set | frame | boxes |", "|---|---|---|---|"]
    L += [f"| {e['arm']} | {e['set']} | {e['stem']} | {e['boxes']} |" for e in empty] or ["| – | – | none | – |"]
    (out_dir / "compare.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
