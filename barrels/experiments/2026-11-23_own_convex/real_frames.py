#!/usr/bin/env python3
"""Every labeled TRAIN frame, frame by frame, with this experiment's arms: which boxes appear or disappear against
``start``, whether each is right (a v2 match) or wrong, and, for the occlusion set R1 (``4A8B_window_abpwhite_occlx_*``),
every box of every arm whatever changes. Segmented as the eval table segments them (HOME leave one scene out, every
other set with the adopted model file); scored by the v2 rule against the hand boxes. A sheet (the photo with each
arm's boxes, side by side) for every frame where a box changes and for every occlusion-set frame.

Train frames only: ``report.select_frames`` keeps the train split and refuses test frames; nothing asks for one.

    python barrels/experiments/2026-11-23_own_convex/real_frames.py [--arms start,close,convex] [--out round1]
Outputs: results/2026-11-23_own_convex/<out>/ real_frames.md, real_frames.csv; sheets_real/ (ignored)
"""
from __future__ import annotations

import argparse
import csv

import cv2
import numpy as np

import own_arms as O
from barrels import cv as bcv, detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, pipeline as pl, report as rp, \
    splits as spl, worldmap_bridge as wb

A = O.A
CAM = geo.AIM_4A8B6118_BOXFIT
OCCLX = "4A8B_window_abpwhite_occlx_"


def segment_all(sel, cache) -> dict:
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    out = {}
    for key, stems in sel.sets.items():
        if key == rp.FIT_SET:
            scenes = {s: io.parse_name(s)["scene"] for s in stems}
            for fold in bcv.loso_folds(stems, scenes):
                m = pl.fit([cache.frame(s) for s in fold.train], [cache.mask(s) for s in fold.train], model.cfg)
                for s in fold.held_out:
                    out[s] = pl.segment(cache.frame(s), m)[0]
        else:
            for s in stems:
                out[s] = pl.segment(cache.frame(s), model)[0]
    return out


def box_text(b, ok: bool) -> str:
    return f"{dtp.COLOR_NAMES[b.color]} {list(b.bbox)} {'right' if ok else 'WRONG'}"


def same(a, b) -> bool:
    return a.color == b.color and tuple(a.bbox) == tuple(b.bbox)


def sheet(img, panels, path):
    tiles = []
    for name, preds, gts in panels:
        t = img.copy()
        for g in gts:
            cv2.rectangle(t, tuple(g.bbox[:2]), (g.bbox[2] - 1, g.bbox[3] - 1), (255, 255, 255), 1)
        t = det.draw(t, preds, thickness=2)
        cv2.putText(t, name, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        tiles.append(t)
    cv2.imwrite(str(path), np.hstack(tiles))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="start,close,convex")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    O.register()
    arms = [a for a in args.arms.split(",") if a]
    splits = spl.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), splits, "train")
    rp.refuse_test_frames(sel.stems, splits)
    test = set(splits["test"])
    cache = rp.FrameCache()
    masks = segment_all(sel, cache)
    out = O.OUT / args.out if args.out else O.OUT
    sheets = out / "sheets_real"
    sheets.mkdir(parents=True, exist_ok=True)
    rows, lines = [], []
    totals = {a: {"found": 0, "false": 0, "gt": 0} for a in arms}
    for key, stems in sel.sets.items():
        for s in stems:
            assert s not in test
            gts, clean = rp_truth(s)
            res, preds = {}, {}
            for a in arms:
                p = det.detect(masks[s], A.rule_config(A.ARMS[a]), CAM)
                r = ed.evaluate_frame(s, p, gts, CAM, rule="v2", clean=clean)
                res[a], preds[a] = r, p
                totals[a]["found"] += len(gts) - len(r.unmatched_gt)
                totals[a]["false"] += len(r.unmatched_pred)
                totals[a]["gt"] += len(gts)
            base = arms[0]
            changed = False
            for a in arms[1:]:
                ok_a = {i for i in range(len(preds[a])) if i not in res[a].unmatched_pred}
                ok_b = {i for i in range(len(preds[base])) if i not in res[base].unmatched_pred}
                added = [(b, i in ok_a) for i, b in enumerate(preds[a]) if not any(same(b, o) for o in preds[base])]
                removed = [(b, i in ok_b) for i, b in enumerate(preds[base]) if not any(same(b, o) for o in preds[a])]
                if added or removed:
                    changed = True
                    rows.append({"set": rp.set_label(key, list(sel.sets)), "frame": s.replace("4A8B_", ""), "arm": a,
                                 "added": "; ".join(box_text(b, ok) for b, ok in added), "removed": "; ".join(box_text(b, ok) for b, ok in removed),
                                 "found": f"{len(gts) - len(res[base].unmatched_gt)} -> {len(gts) - len(res[a].unmatched_gt)} of {len(gts)}",
                                 "false": f"{len(res[base].unmatched_pred)} -> {len(res[a].unmatched_pred)}"})
            if s.startswith(OCCLX):
                cells = []
                for a in arms:
                    ok = {i for i in range(len(preds[a])) if i not in res[a].unmatched_pred}
                    cells.append("; ".join(box_text(b, i in ok) for i, b in enumerate(preds[a])) or "no box")
                lines.append(f"| {s.replace(OCCLX, '')} | " + " | ".join(f"{len(gts) - len(res[a].unmatched_gt)} of {len(gts)}, {len(res[a].unmatched_pred)} false" for a in arms)
                             + " | " + " | ".join(cells) + " |")
            if changed or s.startswith(OCCLX):
                img = io.load_image(io.find_image(s))
                sheet(img, [(a, preds[a], gts) for a in arms], sheets / f"{s}.png")
    out.mkdir(parents=True, exist_ok=True)
    with (out / "real_frames.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["set", "frame", "arm", "found", "false", "added", "removed"]); w.writeheader(); w.writerows(rows)
    L = ["# Every labeled train frame: boxes that appear or disappear against `" + arms[0] + "`", "",
         "Segmented as the eval table does (HOME leave one scene out; every other set the adopted model file); v2 rule against the hand boxes. "
         "`right` = matched to a true barrel by the v2 rule; `WRONG` = not. Sheets (white = hand boxes): `sheets_real/` (not committed).", "",
         "| set | frame | arm | found | false | boxes added | boxes removed |", "|---|---|---|---|---|---|---|"]
    L += [f"| {r['set']} | {r['frame']} | {r['arm']} | {r['found']} | {r['false']} | {r['added'] or '-'} | {r['removed'] or '-'} |" for r in rows] or ["| (none) | | | | | | |"]
    L += ["", "Totals over every train frame: " + "; ".join(f"`{a}` found {t['found']} of {t['gt']}, false {t['false']}" for a, t in totals.items()), "",
          "## The occlusion set R1 (`4A8B_window_abpwhite_occlx_*`, train frames), every box of every arm", "",
          "| shot | " + " | ".join(f"`{a}` found, false" for a in arms) + " | " + " | ".join(f"`{a}` boxes" for a in arms) + " |",
          "|---|" + "---|" * (2 * len(arms))] + lines
    (out / "real_frames.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


def rp_truth(stem: str):
    """The hand boxes as ``report.score_boxes`` reads them (with their ground rows), and the label's clean flag."""
    label = io.load_boxes(stem)
    return [b.with_ground(CAM) for b in dtp.barrels_from_boxes(label)], bool(label.get("clean", True))


if __name__ == "__main__":
    raise SystemExit(main())
