#!/usr/bin/env python3
"""The hs color model scored properly: Tanush's box labels on the campus frames (2026-11-08), per-class S floors.

Follows experiments/2026-11-08_seg_hs (count-level, single S percentile). Two things changed: the 21 campus train
frames now have boxes, so they are scored under the v2 rule like the home frames; and the S floor percentile may
differ per class (pipeline.Config(hs_s_pct=(orange, blue))) because the first sweep showed orange wants a lower
floor (the far blue barrels' orange stripes in room_01 fall under S 174) and blue a higher one (the bluish home
wall enters the blue class below S ~110).

Hypothesis: a per-class floor — orange at the 5th–10th percentile, blue at the 15th–20th — keeps the home score at
v1's level (>= 0.91 LOSO), draws nothing on any negative frame of either session, and beats the single-percentile
runner-up (s15 h5-95 m4) on the campus v2 score.

Grid: orange S pct in {5, 10, 15} x blue S pct in {10, 15, 20} x hue pct (5, 95) x hue margin in {2, 4} = 18 configs.
Baselines: v1 afd85483 with the old (bands) detector = the detector on `barrels`; v1 with the hardened detector.
Scores: home = leave-one-scene-out over the 16 home train frames (v2 rule, pixel IoU); campus = one model fit on all
16 home frames, v2 rule on the 21 campus train frames (held_01, left unboxed by Tanush, counts as a negative);
Dave = his 12 frames, indicative only (his boxes group touching barrels). The 10 campus test frames and the 5 home
test frames are never loaded.

Selection rule — PROPOSED to Tanush in OVERNIGHT-2026-11-08.md, not yet agreed, written here before the run: home
LOSO v2 >= 0.91; zero false detections on every negative frame of both sessions (home LOSO negatives, campus
negatives incl. held_01); then the highest campus v2 score; ties by home v2, then the lower blue percentile.
Whatever it picks is a candidate for the walkthrough, not an adoption. Results: results/2026-11-08_seg_hs_v2/.

    python barrels/experiments/2026-11-08_seg_hs_v2/run.py
"""
from __future__ import annotations

import dataclasses
import itertools
import json
import sys
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, detector as det, detect_types as dtp, eval as ev, eval_det as ed, geometry as geo, io, pipeline as pl, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-08_seg_hs_v2"
CAM = geo.AIM_4A8B6118_BOXFIT
DET_NEW = det.DetConfig()
DET_OLD = dataclasses.replace(det.DetConfig(), stripe_mode="bands", body_min=0.0, height_max=0.0)
GRID = {"orange_pct": [5, 10, 15], "blue_pct": [10, 15, 20], "margin": [2, 4]}


def load(stems):
    frames, masks, imgs = {}, {}, {}
    for s in stems:
        img = io.load_image(io.find_image(s)); imgs[s] = img; frames[s] = pl.Frame.from_image(img)
        mp = io.mask_path(io.find_image(s)); masks[s] = io.load_mask(mp) if mp.exists() else None
    return frames, masks, imgs


def score(stem, mask, dcfg):
    label = io.load_boxes(stem)
    gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes(label)]
    preds = det.detect(mask, dcfg, CAM)
    return preds, gts, ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=label.get("clean", True))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sp = splits.load_splits()
    home = sorted(s for s in sp["train"] if s.startswith("4A8B_window_light"))
    campus = sorted(s for s in sp["train"] if s.startswith("4A8B_campus_light"))
    dave = sorted(p.stem.replace("_boxes", "") for p in io.LABELS_DIR.glob("DAVE_*_boxes.json"))
    assert not any(s in sp["test"] for s in home + campus)
    hf, hm, hi = load(home); cf, _, ci = load(campus); df, _, di = load(dave)
    hscenes = {s: io.parse_name(s)["scene"] for s in home}; cscenes = {s: io.parse_name(s)["scene"] for s in campus}
    folds = bcv.loso_folds(home, hscenes)
    hook = wb.BarrelDetectorHook.default(cam=CAM)
    rows = []

    def evaluate(name, cfg, dcfg):
        res, pix = [], []
        for fold in folds:
            model = pl.fit([hf[s] for s in fold.train], [hm[s] for s in fold.train], cfg)
            for s in fold.held_out:
                mask, _ = pl.segment(hf[s], model); _, _, r = score(s, mask, dcfg); res.append(r); pix.append(ev.evaluate_image(s, mask, hm[s]))
        h = ed.score(res, hscenes, out_scope=()); agg = ev.aggregate(pix)["ALL"]
        model = pl.fit([hf[s] for s in home], [hm[s] for s in home], cfg)
        out_dir = OUT / name.replace(" ", "_").replace("/", "-"); (out_dir / "sheets").mkdir(parents=True, exist_ok=True)
        cres = []
        for s in campus:
            mask, _ = pl.segment(cf[s], model); preds, gts, r = score(s, mask, dcfg); cres.append(r)
            sheet = det.draw(viz.overlay(ci[s], mask), preds)
            for g in gts:
                x0, y0, x1, y1 = g.bbox; cv2.rectangle(sheet, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
            cv2.imwrite(str(out_dir / "sheets" / f"{s}.png"), sheet)
        ed.write_results(cres, out_dir / "campus", title=f"{name} on the 21 campus train frames (v2)")
        c = ed.score(cres, cscenes, out_scope=())
        dres = []
        for s in dave:
            mask, _ = pl.segment(df[s], model); preds, gts, r = score(s, mask, dcfg); dres.append(r)
        d = ed.score(dres, {s: "dave" for s in dave}, out_scope=())
        neg_total = h["neg_false_detections"] + c["neg_false_detections"]
        row = dict(name=name, cfg=cfg.to_dict(), det=dcfg.to_dict(), hash=cfg.short_hash(),
                   home_v2=h["primary"], home_F1_o=h["F1_o"], home_F1_b=h["F1_b"], home_negFD=h["neg_false_detections"],
                   home_iou_o=agg.pos[ORANGE].iou, home_iou_b=agg.pos[BLUE].iou,
                   campus_v2=c["primary"], campus_F1_o=c["F1_o"], campus_F1_b=c["F1_b"], campus_negFD=c["neg_false_detections"],
                   campus_bottom_med=c["bottom_err_median_px"], neg_total=neg_total,
                   dave_v2=d["primary"], dave_F1_o=d["F1_o"], dave_F1_b=d["F1_b"],
                   model={str(k): b.to_dict() for k, b in model.boxes.items()}, fit_info=model.fit_info)
        rows.append(row)
        print(f"{name:34} home {h['primary']:.2f} ({h['F1_o']:.2f}/{h['F1_b']:.2f}) negFD {h['neg_false_detections']} | campus {c['primary']:.2f} ({c['F1_o']:.2f}/{c['F1_b']:.2f}) negFD {c['neg_false_detections']} | Dave {d['primary']:.2f}")

    evaluate("v1 + old detector (barrels today)", hook.model.cfg, DET_OLD)
    evaluate("v1 + hardened detector", hook.model.cfg, DET_NEW)
    evaluate("hs s15 h5-95 m4 (count-level runner-up)", pl.Config(color_model="hs", hs_s_pct=15, hs_h_pct=(5, 95), hs_h_margin=4), DET_NEW)
    for o, b, m in itertools.product(*GRID.values()):
        evaluate(f"hs o{o} b{b} h5-95 m{m}", pl.Config(color_model="hs", hs_s_pct=(o, b), hs_h_pct=(5, 95), hs_h_margin=m), DET_NEW)
    hs_rows = [r for r in rows if r["name"].startswith("hs")]
    ok = [r for r in hs_rows if r["home_v2"] >= 0.91 and r["neg_total"] == 0]
    chosen = max(ok, key=lambda r: (r["campus_v2"], r["home_v2"], -(r["cfg"]["hs_s_pct"][1] if isinstance(r["cfg"]["hs_s_pct"], tuple) else r["cfg"]["hs_s_pct"]))) if ok else None
    md = ["# The hs color model with per-class S floors, scored on Tanush's campus boxes (v2 rule)", "",
          f"git {bcv.git_hash()}; camera AIM_4A8B6118_BOXFIT; home = LOSO over the 16 home train frames; campus = 21 train frames, boxes by Tanush 2026-11-08 (held_01 unboxed = negative); Dave = 12 frames, indicative. "
          "Detector: hardened DetConfig() unless the row says old.", "",
          "Selection rule (proposed, written before the run): home v2 >= 0.91, zero false detections on every negative of both sessions, then campus v2, then home v2, then the lower blue percentile.", "",
          "| config | hash | home v2 (o / b) | home neg FD | home px IoU o / b | **campus v2** (o / b) | campus neg FD | campus bottom err (median px) | Dave v2 (o / b) |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        mark = " **<- chosen**" if chosen is not None and r is chosen else ""
        md.append(f"| {r['name']}{mark} | {r['hash']} | {r['home_v2']:.2f} ({r['home_F1_o']:.2f} / {r['home_F1_b']:.2f}) | {r['home_negFD']} | {r['home_iou_o']:.2f} / {r['home_iou_b']:.2f} | "
                  f"**{r['campus_v2']:.2f}** ({r['campus_F1_o']:.2f} / {r['campus_F1_b']:.2f}) | {r['campus_negFD']} | {r['campus_bottom_med']:.1f} | {r['dave_v2']:.2f} ({r['dave_F1_o']:.2f} / {r['dave_F1_b']:.2f}) |")
    if chosen:
        fi = chosen["fit_info"]
        md += ["", f"## Chosen by the proposed rule: {chosen['name']} (config `{chosen['hash']}`)", "",
               f"- orange: hue {fi['1']['hue_unshifted'][0]:.0f}–{fi['1']['hue_unshifted'][1]:.0f}, S >= {chosen['model']['1']['lo'][1]:.0f}; blue: hue {fi['2']['hue_unshifted'][0]:.0f}–{fi['2']['hue_unshifted'][1]:.0f}, S >= {chosen['model']['2']['lo'][1]:.0f}; V >= 40; rows above 50 never barrel.",
               f"- per-frame and per-barrel tables: `{(OUT / chosen['name'].replace(' ', '_').replace('/', '-') / 'campus').relative_to(PKG_ROOT)}/`"]
    (OUT / "summary.md").write_text("\n".join(md))
    json.dump({"git": bcv.git_hash(), "grid": GRID, "det_new": DET_NEW.to_dict(), "det_old": DET_OLD.to_dict(), "home": home, "campus": campus, "dave": dave,
               "rows": rows, "chosen": chosen["name"] if chosen else None}, (OUT / "config.json").open("w"), indent=1, default=str)
    print("\n".join(md[-6:])); print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
