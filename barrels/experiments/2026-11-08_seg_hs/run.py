#!/usr/bin/env python3
"""The "hs" color model (pipeline.Config(color_model="hs")): pre-registered sweep of its three fit parameters.

Hypothesis (from the attribution 2026-11-07 and the probe the same day): a per-class hue sector plus a floor on HSV
saturation, both read off the labeled home frames, with no top-row stage, finds the barrel bodies in a real room
that v1 loses, while the hardened detector (2026-11-08) keeps the false boxes at zero. What the probe could not
settle: how high the S floor must be to keep the bluish home wall out (its S reaches 110 in the blue hue sector)
without losing shaded blue bodies (S 60-130 on the far campus barrels), and how much hue slack orange needs (home
labels give hue 5-10; the campus barrels in daylight read 7-13).

Grid: hs_s_pct in {5, 10, 15, 20} x hs_h_pct in {(2,98), (5,95)} x hs_h_margin in {0, 2, 4} = 24 configs; detector
DetConfig() (hardened), camera AIM_4A8B6118_BOXFIT. For each config:
  * home: leave-one-scene-out over the 16 home train frames (fit on the other scenes, segment and detect the held-out
    frame): v2 score (Tanush's boxes) and per-pixel IoU per class (the masks) — the only labeled data;
  * campus: fit on all 16 home frames, count-level on the 21 campus train frames (expected.json) and boxes on the 4
    campus negatives;
  * Dave: the same model on his 12 labeled office frames, v2 rule — the outside check, NOT used to choose (his
    boxes are one per group of touching barrels, so the number is indicative only).
Selection rule, fixed before the run: among configs with 0 false detections on the home negatives (LOSO) and 0
boxes on the campus negatives, the one with the most campus frames at the right count; ties broken by the home
LOSO v2 score, then by the lower S percentile (the more inclusive floor). The v1 row is the frozen afd85483 with
the same hardened detector. No test frame of either session is loaded. Results: results/2026-11-08_seg_hs/.

    python barrels/experiments/2026-11-08_seg_hs/run.py
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, detector as det, detect_types as dtp, eval as ev, eval_det as ed, geometry as geo, io, pipeline as pl, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-08_seg_hs"
CAM = geo.AIM_4A8B6118_BOXFIT
DET = det.DetConfig()
EXPECTED = json.loads((HERE.parent / "2026-11-07_campus_attribution" / "expected.json").read_text())
GRID = {"hs_s_pct": [5, 10, 15, 20], "hs_h_pct": [(2, 98), (5, 95)], "hs_h_margin": [0, 2, 4]}


def load(stems):
    frames, masks, imgs = {}, {}, {}
    for s in stems:
        img = io.load_image(io.find_image(s)); imgs[s] = img; frames[s] = pl.Frame.from_image(img)
        mp = io.mask_path(io.find_image(s))
        masks[s] = io.load_mask(mp) if mp.exists() else None
    return frames, masks, imgs


def det_result(stem, mask, cam=CAM):
    label = io.load_boxes(stem)
    gts = [b.with_ground(cam) for b in dtp.barrels_from_boxes(label)]
    preds = det.detect(mask, DET, cam)
    return preds, ed.evaluate_frame(stem, preds, gts, cam, rule="v2", clean=label.get("clean", True))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sp = splits.load_splits()
    home = sorted(s for s in sp["train"] if s.startswith("4A8B_window_light"))
    campus = sorted(s for s in sp["train"] if s.startswith("4A8B_campus_light"))
    dave = sorted(p.stem.replace("_boxes", "") for p in io.LABELS_DIR.glob("DAVE_*_boxes.json"))
    assert not any(s in sp["test"] for s in home + campus)
    hf, hm, hi = load(home); cf, _, ci = load(campus); df, _, di = load(dave)
    scenes = {s: io.parse_name(s)["scene"] for s in home}
    folds = bcv.loso_folds(home, scenes)
    hook = wb.BarrelDetectorHook.default(cam=CAM)
    rows = []

    def evaluate(name, cfg, fit_fn, seg_fn):
        # home LOSO
        res, pix = [], []
        for fold in folds:
            model = fit_fn([hf[s] for s in fold.train], [hm[s] for s in fold.train], cfg)
            for s in fold.held_out:
                mask, _ = pl.segment(hf[s], model)
                _, r = det_result(s, mask); res.append(r)
                pix.append(ev.evaluate_image(s, mask, hm[s]))
        h = ed.score(res, scenes, out_scope=())
        agg = ev.aggregate(pix)["ALL"]
        # one model on all home frames -> campus + Dave
        model = fit_fn([hf[s] for s in home], [hm[s] for s in home], cfg)
        right, neg_boxes, extra, per = 0, 0, 0, {}
        sheets = OUT / "sheets" / name; sheets.mkdir(parents=True, exist_ok=True)
        for s in campus:
            mask, _ = pl.segment(cf[s], model); preds = det.detect(mask, DET, CAM)
            o, b = sum(p.color == ORANGE for p in preds), sum(p.color == BLUE for p in preds)
            exp = EXPECTED[s]; ok = (o, b) == (exp["orange"], exp["blue"]); right += ok
            neg_boxes += len(preds) if "_neg_" in s else 0
            extra += (o > exp["orange"] or b > exp["blue"])
            per[s.replace("4A8B_campus_light_", "")] = f"{o}/{b}" + ("" if ok else f" (exp {exp['orange']}/{exp['blue']})")
            cv2.imwrite(str(sheets / f"{s}.png"), det.draw(viz.overlay(ci[s], mask), preds))
        dres = []
        for s in dave:
            mask, _ = pl.segment(df[s], model); preds, r = det_result(s, mask); dres.append(r)
            cv2.imwrite(str(sheets / f"{s}.png"), det.draw(viz.overlay(di[s], mask), preds))
        d = ed.score(dres, {s: "dave" for s in dave}, out_scope=())
        row = dict(name=name, cfg=cfg.to_dict(), hash=cfg.short_hash(), home_v2=h["primary"], home_F1_o=h["F1_o"], home_F1_b=h["F1_b"], home_negFD=h["neg_false_detections"],
                   home_iou_o=agg.pos[ORANGE].iou, home_iou_b=agg.pos[BLUE].iou,
                   campus_right=right, campus_n=len(campus), campus_neg_boxes=neg_boxes, campus_extra=extra,
                   dave_v2=d["primary"], dave_F1_o=d["F1_o"], dave_F1_b=d["F1_b"], per=per,
                   model={str(c): b.to_dict() for c, b in model.boxes.items()}, fit_info=model.fit_info)
        rows.append(row)
        print(f"{name:28} home v2 {h['primary']:.2f} ({h['F1_o']:.2f}/{h['F1_b']:.2f}) negFD {h['neg_false_detections']} | campus {right}/{len(campus)} neg {neg_boxes} extra {extra} | Dave {d['primary']:.2f}")

    evaluate("v1 afd85483 (+hardened det)", hook.model.cfg, lambda fr, mk, cfg: pl.fit(fr, mk, cfg), None)
    for s_pct, h_pct, margin in itertools.product(*GRID.values()):
        cfg = pl.Config(color_model="hs", hs_s_pct=s_pct, hs_h_pct=h_pct, hs_h_margin=margin)
        evaluate(f"hs s{s_pct} h{h_pct[0]}-{h_pct[1]} m{margin}", cfg, pl.fit, None)
    hs_rows = [r for r in rows if r["name"].startswith("hs")]
    ok = [r for r in hs_rows if r["home_negFD"] == 0 and r["campus_neg_boxes"] == 0]
    chosen = max(ok, key=lambda r: (r["campus_right"], r["home_v2"], -r["cfg"]["hs_s_pct"])) if ok else None
    md = ["# The hs color model: sweep of the S percentile, the hue percentiles and the hue margin", "",
          f"git {bcv.git_hash()}; detector DetConfig() (hardened 2026-11-08); camera AIM_4A8B6118_BOXFIT; home = LOSO over the 16 train frames (v2 rule, Tanush's boxes; "
          "pixel IoU from the masks); campus = count-level on the 21 train frames; Dave = his 12 labeled frames (indicative: his boxes group touching barrels).", "",
          "Selection rule (fixed before the run): 0 home false detections, 0 boxes on the campus negatives, then most campus frames right, then home v2, then the lower S percentile.", "",
          "| config | hash | home v2 (F1 o / b) | home neg FD | home pixel IoU o / b | campus right | campus neg boxes | campus extra-box frames | Dave v2 (o / b) |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        mark = " **<- chosen**" if chosen is not None and r is chosen else ""
        iou = f"{r['home_iou_o']:.2f} / {r['home_iou_b']:.2f}" if r["home_iou_o"] is not None else "–"
        md.append(f"| {r['name']}{mark} | {r['hash']} | **{r['home_v2']:.2f}** ({r['home_F1_o']:.2f} / {r['home_F1_b']:.2f}) | {r['home_negFD']} | {iou} | {r['campus_right']} / {r['campus_n']} | {r['campus_neg_boxes']} | {r['campus_extra']} | {r['dave_v2']:.2f} ({r['dave_F1_o']:.2f} / {r['dave_F1_b']:.2f}) |")
    if chosen:
        fi = chosen["fit_info"]
        md += ["", f"## Chosen: {chosen['name']} (config `{chosen['hash']}`)", "",
               f"- orange: hue {fi['1']['hue_unshifted'][0]:.0f}–{fi['1']['hue_unshifted'][1]:.0f} (OpenCV 0–179), S >= {chosen['model']['1']['lo'][1]:.0f}; blue: hue {fi['2']['hue_unshifted'][0]:.0f}–{fi['2']['hue_unshifted'][1]:.0f}, S >= {chosen['model']['2']['lo'][1]:.0f}; V >= 40; rows above 50 never barrel. Fit on all 16 home train frames.", "",
               "| campus frame | boxes O/B (expected where wrong) |", "|---|---|"]
        md += [f"| {k} | {v} |" for k, v in chosen["per"].items()]
    (OUT / "summary.md").write_text("\n".join(md))
    json.dump({"git": bcv.git_hash(), "grid": {k: [list(v) if isinstance(v, tuple) else v for v in vals] for k, vals in GRID.items()}, "det": DET.to_dict(), "home": home, "campus": campus, "dave": dave,
               "rows": [{k: v for k, v in r.items() if k != "per"} for r in rows], "chosen": chosen["name"] if chosen else None}, (OUT / "config.json").open("w"), indent=1, default=str)
    print("\n".join(md[-30:])); print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
