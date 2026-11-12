#!/usr/bin/env python3
"""TODO step 7, second half: does a lower stripe-width floor (and the hidden side read from the body) recover the
barrel hidden at the side, and what does it cost? Hypothesis, configs, data and the acceptance rule are in
PREREG.md next to this file, committed before the first run.

Outputs: results/2026-11-11_occl_narrow_stripe/ — summary.md, changes.csv (every box added or removed against
`base`, every frame), config.json; sheets/ (gitignored) has one picture per frame whose boxes changed:
raw | `base` boxes | the config's boxes, truth in white.

    python barrels/experiments/2026-11-11_occl_narrow_stripe/run.py
"""
from __future__ import annotations

import csv
import dataclasses
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, detector as det, detect_types as dtp, eval_det as ed, geometry as geo, io, pipeline as pl, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-11_occl_narrow_stripe"
CAM = geo.AIM_4A8B6118_BOXFIT
BASE = det.DetConfig(stripe_w_min=0.4, occl_body_side=False)       # the detector on `barrels` today, spelled out
CONFIGS = {
    "base": BASE,
    "w25": dataclasses.replace(BASE, stripe_w_min=0.25),
    "w25h": dataclasses.replace(BASE, stripe_w_min=0.25, occl_body_side=True),
    "h": dataclasses.replace(BASE, occl_body_side=True),
    "w35 (report only)": dataclasses.replace(BASE, stripe_w_min=0.35),
    "w30 (report only)": dataclasses.replace(BASE, stripe_w_min=0.30),
    "w20 (report only)": dataclasses.replace(BASE, stripe_w_min=0.20),
}
CANDIDATES = ("w25h", "w25")                                       # acceptance order (PREREG.md)


def frame_sets() -> dict[str, list[tuple[str, Path]]]:
    sp = splits.load_splits()
    test = set(sp["test"])
    train = sorted(sp["train"])
    assert not test & set(train)
    sets = {"HOME": [(s, io.find_image(s)) for s in train if s.startswith("4A8B_window_light")],
            "CAMPUS": [(s, io.find_image(s)) for s in train if s.startswith("4A8B_campus_light")],
            "DAVE": [(p.stem.replace("_boxes", ""), io.find_image(p.stem.replace("_boxes", ""))) for p in sorted(io.LABELS_DIR.glob("DAVE_*_boxes.json"))]}
    wood = sorted(p for p in io.RAW_DIR.glob("4A8B_*_wood_*") if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
    assert not any(p.stem in test for p in wood)
    sets["WOOD (unlabeled)"] = [(p.stem, p) for p in wood]
    rec = PKG_ROOT / "data" / "recordings" / "2026-11-07_campus"
    sets["REC (unlabeled)"] = [(f"{d.name}/{p.stem}", p) for d in sorted(rec.iterdir()) if d.is_dir() for p in sorted(d.glob("*.png"))]
    live = PKG_ROOT / "live" / "snapshots" / "robot_snap0.png"
    sets["LIVE (unlabeled)"] = [("robot_snap0", live)] if live.exists() else []
    for name, items in sets.items():
        assert not any(s in test for s, _ in items), name
    return sets


def same(a: dtp.Barrel, b: dtp.Barrel) -> bool:
    return a.color == b.color and ed.box_iou(a.bbox, b.bbox) > 0.5


def main() -> int:
    (OUT / "sheets").mkdir(parents=True, exist_ok=True)
    hook = wb.BarrelDetectorHook.default(cam=CAM)
    sets = frame_sets()
    labeled = ("HOME", "CAMPUS", "DAVE")
    res = {c: {s: [] for s in labeled} for c in CONFIGS}
    stats = {c: {s: {"frames": 0, "boxes": 0, "added": 0, "removed": 0, "moved": 0, "tp": 0, "fp": 0, "fn": 0, "lost": 0, "gained": 0} for s in sets} for c in CONFIGS}
    changes, occl02 = [], {}
    for set_name, items in sets.items():
        for stem, path in items:
            img = cv2.imread(str(path))
            if img is None:
                continue
            mask, _ = pl.segment(pl.Frame.from_image(img), hook.model)
            gts, clean = [], True
            if set_name in labeled:
                label = io.load_boxes(stem); gts = dtp.barrels_from_boxes(label); clean = label.get("clean", True)
            preds = {c: det.detect(mask, cfg, CAM) for c, cfg in CONFIGS.items()}
            hits = {}
            for c in CONFIGS:
                st = stats[c][set_name]; st["frames"] += 1; st["boxes"] += len(preds[c])
                if set_name in labeled:
                    r = ed.evaluate_frame(stem, preds[c], [g.with_ground(CAM) for g in gts], CAM, rule="v2", clean=clean)
                    res[c][set_name].append(r)
                    st["tp"] += sum(r.tp.values()); st["fp"] += sum(r.fp.values()); st["fn"] += sum(r.fn.values())
                    pairs = ed.match_best_first(preds[c], gts, lambda p, g: ed.box_iou(p.bbox, g.bbox), ed.IOU_THR, same_class=True,
                                                eligible=lambda p, g: ed.bottom_within_tol(p, g))
                    hits[c] = {gi for _, gi, _ in pairs}
            for c in CONFIGS:
                if c == "base":
                    continue
                st = stats[c][set_name]
                added = [p for p in preds[c] if not any(same(p, b) for b in preds["base"])]
                removed = [b for b in preds["base"] if not any(same(p, b) for p in preds[c])]
                moved = [p for p in preds[c] if any(same(p, b) and p.bbox != b.bbox for b in preds["base"])]
                st["added"] += len(added); st["removed"] += len(removed); st["moved"] += len(moved)
                if set_name in labeled:
                    st["lost"] += len(hits["base"] - hits[c]); st["gained"] += len(hits[c] - hits["base"])
                for kind, boxes in (("added", added), ("removed", removed), ("moved", moved)):
                    for b in boxes:
                        changes.append({"config": c, "set": set_name, "frame": stem, "change": kind, "color": dtp.COLOR_NAMES[b.color],
                                        "bbox": list(b.bbox), "flags": "+".join(sorted(b.flags))})
                if (added or removed or moved) and "report only" not in c:
                    panels = [img, det.draw(viz.overlay(img, mask), preds["base"]), det.draw(viz.overlay(img, mask), preds[c])]
                    for pnl in panels[1:]:
                        for g in gts:
                            x0, y0, x1, y1 = g.bbox; cv2.rectangle(pnl, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
                    sheet = np.hstack(panels)
                    cv2.putText(sheet, f"{stem}: raw | base | {c}", (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.imwrite(str(OUT / "sheets" / f"{c}__{stem.replace('/', '_')}.png"), sheet)
            if stem == "4A8B_campus_light_occl_02":
                gi = next(i for i, g in enumerate(gts) if "occluded" in g.flags)
                for c in CONFIGS:
                    best = max((p for p in preds[c] if p.color == gts[gi].color), key=lambda p: ed.box_iou(p.bbox, gts[gi].bbox), default=None)
                    occl02[c] = {"found": gi in hits[c], "box": list(best.bbox) if best else None, "truth": list(gts[gi].bbox),
                                 "iou": round(ed.box_iou(best.bbox, gts[gi].bbox), 2) if best else 0.0}

    scores = {c: {s: ed.score(res[c][s], {r.name: io.parse_name(r.name)["scene"] if s != "DAVE" else "dave" for r in res[c][s]}, out_scope=()) for s in labeled} for c in CONFIGS}
    verdict = {}
    for c in CANDIDATES:
        conds = {"1 no found barrel lost (HOME, CAMPUS)": stats[c]["HOME"]["lost"] + stats[c]["CAMPUS"]["lost"] == 0,
                 "2 no false box added (HOME, CAMPUS)": stats[c]["HOME"]["fp"] <= stats["base"]["HOME"]["fp"] and stats[c]["CAMPUS"]["fp"] <= stats["base"]["CAMPUS"]["fp"]
                 and scores[c]["HOME"]["neg_false_detections"] + scores[c]["CAMPUS"]["neg_false_detections"] == 0,
                 "3 Dave score not lower": scores[c]["DAVE"]["primary"] >= scores["base"]["DAVE"]["primary"] - 1e-9,
                 "4 boxes added on unlabeled frames are real (BY EYE, see sheets)": None,
                 "5 occl_02 barrel found": occl02[c]["found"]}
        verdict[c] = conds

    with (OUT / "changes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["config", "set", "frame", "change", "color", "bbox", "flags"]); w.writeheader(); w.writerows(changes)
    json.dump({"git": bcv.git_hash(), "camera": "AIM_4A8B6118_BOXFIT", "model": str(wb.default_model_path()),
               "configs": {c: cfg.to_dict() for c, cfg in CONFIGS.items()}, "sets": {s: [n for n, _ in items] for s, items in sets.items()},
               "stats": stats, "occl_02": occl02, "verdict": verdict,
               "scores": {c: {s: {k: scores[c][s][k] for k in ("primary", "F1_o", "F1_b", "neg_false_detections")} for s in labeled} for c in CONFIGS}},
              (OUT / "config.json").open("w"), indent=1, default=str)
    md = ["# A barrel hidden at the side: lower stripe-width floor, hidden side from the body", "",
          f"git {bcv.git_hash()}; adopted color model; v2 rule; train frames only. Rule and hypothesis: `experiments/2026-11-11_occl_narrow_stripe/PREREG.md`.", "",
          "## Labeled frames", "",
          "| config | HOME v2 (found / false / missed) | CAMPUS v2 (found / false / missed) | Dave v2 | barrels lost vs base | barrels gained vs base | `occl_02` barrel (IoU) |", "|---|---|---|---|---|---|---|"]
    for c in CONFIGS:
        h, cm, d = stats[c]["HOME"], stats[c]["CAMPUS"], stats[c]["DAVE"]
        md.append(f"| {c} | {scores[c]['HOME']['primary']:.2f} ({h['tp']} / {h['fp']} / {h['fn']}) | {scores[c]['CAMPUS']['primary']:.2f} ({cm['tp']} / {cm['fp']} / {cm['fn']}) | "
                  f"{scores[c]['DAVE']['primary']:.2f} ({d['tp']} / {d['fp']} / {d['fn']}) | {h['lost'] + cm['lost']} | {h['gained'] + cm['gained']} | "
                  f"{'found' if occl02[c]['found'] else 'missed'} ({occl02[c]['iou']:.2f}) |")
    md += ["", "HOME here uses the adopted model on all 16 home frames (the model was fit on them), so it is not the leave-one-scene-out headline number; it is only for comparing detector configs.", "",
           "## Unlabeled frames: boxes against `base`", "",
           "| config | set | frames | boxes | added | removed | moved |", "|---|---|---|---|---|---|---|"]
    for c in CONFIGS:
        for s in sets:
            if s in labeled or not stats[c][s]["frames"]:
                continue
            st = stats[c][s]
            md.append(f"| {c} | {s} | {st['frames']} | {st['boxes']} | {st['added']} | {st['removed']} | {st['moved']} |")
    md += ["", "## Acceptance (conditions 1, 2, 3, 5 by the script; 4 by eye)", ""]
    for c, conds in verdict.items():
        md.append(f"- **{c}**: " + "; ".join(f"{k}: {'by eye' if v is None else ('pass' if v else 'FAIL')}" for k, v in conds.items()))
    (OUT / "summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
