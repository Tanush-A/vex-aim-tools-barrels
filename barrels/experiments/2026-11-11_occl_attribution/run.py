#!/usr/bin/env python3
"""TODO step 7, first half: reproduce the occlusion misses on saved frames and say which test refuses each barrel.

Live with Dave (2026-11-09) a barrel with about half its body showing got no box. Before any fix: which barrels
does the detector as it stands miss on the labeled **train** frames (HOME 16 + CAMPUS 21; the 15 test frames are
never loaded), and for each missed one, where in the chain does it die?

Hypothesis (written before the run): the misses are occluded barrels, and they die in one of three places —
  (a) no stripe candidate at all (the stripe is hidden, or its pixels are not sandwiched by body color),
  (b) a stripe candidate exists and is refused by a proportion test (`height`, `width`) or by `body_min`,
  (c) a box is drawn but in the wrong place (IoU < 0.5 or bottom off) — a localisation miss, not a detection miss.

Method: `detector.detect(..., log=[])` records every candidate the detector drops and why (the log never changes
the answer). For each ground-truth barrel the v2 rule leaves unmatched, the script lists the log entries that
overlap its box, plus what the segmentation shows inside the box (body pixels, stripe-colored pixels, the fraction
of the box they cover). The cause is then read off by the fixed order in `attribute()`.

Outputs: results/2026-11-11_occl_attribution/ — summary.md, per_barrel.csv, config.json (committed) and one sheet
per frame with a miss or an occluded barrel (gitignored): raw | segmentation + truth (white) + boxes drawn
(yellow/green) + every stripe candidate (magenta = kept, red = refused).

    python barrels/experiments/2026-11-11_occl_attribution/run.py
    python barrels/experiments/2026-11-11_occl_attribution/run.py --det occl_hidden_stripe=True --out-suffix _fix
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import detector as det, detect_types as dtp, eval_det as ed, geometry as geo, io, pipeline as pl, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
SETS = {"HOME": "4A8B_window_light_", "CAMPUS": "4A8B_campus_light_"}


def train_stems() -> list[tuple[str, str]]:
    sp = splits.load_splits()
    test = set(sp["test"])
    out = []
    for s in sorted(sp["train"]):
        assert s not in test, "a test frame leaked into the train list"
        for name, prefix in SETS.items():
            if s.startswith(prefix) and io.boxes_path(s).exists():
                out.append((name, s))
    return out


def parse_det(pairs: list[str]) -> det.DetConfig:
    base = det.DetConfig()
    kw = {}
    for p in pairs:
        k, v = p.split("=", 1)
        cur = getattr(base, k)
        kw[k] = (v.lower() in ("1", "true", "yes")) if isinstance(cur, bool) else type(cur)(v)
    return dataclasses.replace(base, **kw)


def overlaps(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def inside(mask: np.ndarray, g: dtp.Barrel) -> dict:
    x0, y0, x1, y1 = g.bbox
    box = mask[y0:y1, x0:x1]
    other = BLUE if g.color == ORANGE else ORANGE
    return {"body_px": int((box == g.color).sum()), "stripe_px": int((box == other).sum()),
            "body_frac": round(float((box == g.color).mean()), 3), "stripe_frac": round(float((box == other).mean()), 3)}


def attribute(g: dtp.Barrel, preds: list[dtp.Barrel], log: list[dict], px: dict) -> tuple[str, str]:
    """(cause, detail) for one unmatched truth barrel, by a fixed order:
    drawn-but-misplaced > a stripe of this body color refused (the refusing test) > a stripeless piece refused >
    nothing barrel-colored in the box > no candidate."""
    same = [p for p in preds if p.color == g.color and ed.box_iou(p.bbox, g.bbox) > 0.1]
    if same:
        best = max(same, key=lambda p: ed.box_iou(p.bbox, g.bbox))
        return "misplaced", f"box {best.bbox} iou {ed.box_iou(best.bbox, g.bbox):.2f} flags {sorted(best.flags)}"
    near = [e for e in log if overlaps(e["bbox"], g.bbox)]
    stripes = [e for e in near if e["stage"] in ("stripe", "barrel") and e.get("body") == g.color and e["why"] != "kept"]
    if stripes:
        e = max(stripes, key=lambda e: (e["bbox"][2] - e["bbox"][0]) * (e["bbox"][3] - e["bbox"][1]))
        vals = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in e.items() if k not in ("stage", "why", "bbox", "body")}
        return f"stripe_refused:{e['why']}", f"stripe {e['bbox']} {vals}"
    if px["body_px"] < 20:
        return "not_segmented", f"{px['body_px']} body px in the box"
    if px["stripe_px"] < 20:
        pieces = [e for e in near if e["stage"] == "piece"]
        why = ",".join(sorted({e["why"] for e in pieces})) or "none"
        return "stripe_hidden", f"{px['stripe_px']} stripe px in the box; body piece: {why}"
    return "stripe_not_sandwiched", f"{px['stripe_px']} stripe px in the box but no candidate with body above and below"


def sheet(img, mask, gts, preds, log, title) -> np.ndarray:
    seg = viz.overlay(img, mask)
    for e in log:
        if e["stage"] not in ("stripe", "barrel"):
            continue
        x0, y0, x1, y1 = e["bbox"]
        cv2.rectangle(seg, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255) if e["why"] == "kept" else (0, 0, 255), 1)
    for g in gts:
        x0, y0, x1, y1 = g.bbox
        cv2.rectangle(seg, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
    seg = det.draw(seg, preds)
    out = np.hstack([img, seg])
    out = cv2.resize(out, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    cv2.putText(out, title, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
    cv2.putText(out, title, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--det", nargs="*", default=[], help="DetConfig overrides, e.g. occl_hidden_stripe=True")
    ap.add_argument("--out-suffix", default="")
    args = ap.parse_args(argv)
    out = PKG_ROOT / "results" / f"2026-11-11_occl_attribution{args.out_suffix}"
    (out / "sheets").mkdir(parents=True, exist_ok=True)
    dcfg = parse_det(args.det)
    hook = wb.BarrelDetectorHook.default(cam=CAM)

    rows, totals = [], {}
    for set_name, stem in train_stems():
        label = io.load_boxes(stem)
        img = io.load_image(io.find_image(stem))
        mask, _ = pl.segment(pl.Frame.from_image(img), hook.model)
        log: list[dict] = []
        preds = det.detect(mask, dcfg, CAM, log=log)
        gts = dtp.barrels_from_boxes(label)
        res = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=label.get("clean", True))
        t = totals.setdefault(set_name, {"frames": 0, "gt": 0, "tp": 0, "fn": 0, "fp": 0, "occl_gt": 0, "occl_tp": 0})
        t["frames"] += 1; t["gt"] += len(gts); t["tp"] += sum(res.tp.values()); t["fn"] += sum(res.fn.values()); t["fp"] += sum(res.fp.values())
        pairs = ed.match_best_first(preds, gts, lambda p, g: ed.box_iou(p.bbox, g.bbox), ed.IOU_THR, same_class=True,
                                    eligible=lambda p, g: ed.bottom_within_tol(p, g))
        hit = {gi for _, gi, _ in pairs}
        interesting = False
        for gi, g in enumerate(gts):
            occl = "occluded" in g.flags
            t["occl_gt"] += occl; t["occl_tp"] += occl and gi in hit
            if gi in hit and not occl:
                continue
            interesting = True
            px = inside(mask, g)
            cause, detail = ("found", "") if gi in hit else attribute(g, preds, log, px)
            rows.append({"set": set_name, "stem": stem, "gt": gi + 1, "color": dtp.COLOR_NAMES[g.color], "bbox": list(g.bbox),
                         "flags": "+".join(sorted(g.flags)), "found": gi in hit, "cause": cause, "detail": detail, **px})
        matched_p = {pi for pi, _, _ in pairs}
        for pi, p in enumerate(preds):
            if pi not in matched_p:
                interesting = True
                rows.append({"set": set_name, "stem": stem, "gt": 0, "color": dtp.COLOR_NAMES[p.color], "bbox": list(p.bbox),
                             "flags": "+".join(sorted(p.flags)), "found": False, "cause": "false_box", "detail": p.source,
                             "body_px": 0, "stripe_px": 0, "body_frac": 0, "stripe_frac": 0})
        if interesting:
            cv2.imwrite(str(out / "sheets" / f"{stem}.png"), sheet(img, mask, gts, preds, log, stem))

    with (out / "per_barrel.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump({"det_cfg": dcfg.to_dict(), "camera": "AIM_4A8B6118_BOXFIT", "model": str(wb.default_model_path()),
               "frames": [s for _, s in train_stems()]}, (out / "config.json").open("w"), indent=1)
    lines = [f"# Occlusion attribution — detector overrides: {args.det or 'none (the detector as it stands)'}", "",
             "Train frames only, v2 rule. `occl` = truth barrels flagged `occluded`.", "",
             "| set | frames | barrels | found | missed | false | occl barrels | occl found |", "|---|---|---|---|---|---|---|---|"]
    for n, t in totals.items():
        lines.append(f"| {n} | {t['frames']} | {t['gt']} | {t['tp']} | {t['fn']} | {t['fp']} | {t['occl_gt']} | {t['occl_tp']} |")
    lines += ["", "## Every occluded barrel, every miss, every false box", "",
              "| frame | barrel | flags | found | cause | detail | body px / stripe px in its box |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['stem'].replace('4A8B_', '')} | {r['color']} {r['bbox']} | {r['flags']} | {'yes' if r['found'] else 'NO'} | "
                     f"{r['cause']} | {r['detail']} | {r['body_px']} / {r['stripe_px']} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
