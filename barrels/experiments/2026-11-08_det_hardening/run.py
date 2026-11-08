#!/usr/bin/env python3
"""Detector hardening (TODO P0-3, pre-registered 2026-11-06; mechanisms confirmed by the campus attribution 2026-11-07).

Three changes to the stripe step, each a DetConfig field so the old behaviour stays reproducible:
  (a) a dark gap with no stripe-colored pixel is no longer a stripe (``dark_stripe=False``; the first live run's
      floating boxes and the false wall boxes under the hue segmentation were exactly such gaps);
  (b) the stripe is found from its own colored pixels (``stripe_mode="cores"``), with body color required within
      3 x the stripe height above and below in at least half its columns — unlabeled shadow glued to a stripe can
      no longer make its band "too tall" (core_01, plain_01, close_01, window_01 in the attribution);
  (c) a box must hold >= ``body_min`` (0.3) body color in the stripe's columns outside the stripe rows (core_01's
      orange box on the blue barrel of the touching pair).

Hypothesis, written before the run: on the 16 home train frames with the frozen v1 pixels the hardened detector
scores within 0.02 of the old one under the v2 rule (the old finder's dark-stripe path mattered there only for
shadowed blue stripes, which (b) now reaches through their body pixels); on the campus train frames it fixes the
five "seg+det" frames whose bodies are labeled (count-level) and removes the wrong-color box; under the hue
segmentation of the 2026-11-07 probe it removes the false boxes on the home wall (neg FD 0) and lifts blue.

Arms: old = stripe_mode "bands" (the detector of 2026-11-05); new = defaults (cores, dark_stripe off, body_min 0.3);
new+dark = cores with dark_stripe on. Each under two front ends: v1 (frozen afd85483) and hs (the probe's hs_p10h5
fit on the home train masks). Scored on the 16 home train frames (v2 rule), Dave's 12 labeled frames (v2 rule) and
the 21 campus train frames (count-level, expected.json of the attribution). No test frame is loaded.
Results: results/2026-11-08_det_hardening/.

    python barrels/experiments/2026-11-08_det_hardening/run.py
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, detector as det, detect_types as dtp, eval_det as ed, geometry as geo, io, pipeline as pl, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


probe = load_module("seg_hs_probe", HERE.parent / "2026-11-07_seg_hs_probe" / "run.py")
OUT = PKG_ROOT / "results" / "2026-11-08_det_hardening"
CAM = geo.AIM_4A8B6118_BOXFIT
EXPECTED = json.loads((HERE.parent / "2026-11-07_campus_attribution" / "expected.json").read_text())
ARMS = {"old": dataclasses.replace(det.DetConfig(), stripe_mode="bands", body_min=0.0),
        "new": det.DetConfig(),
        "new+dark": dataclasses.replace(det.DetConfig(), dark_stripe=True)}


def score_labeled(stems, segment, cfg, out_dir) -> dict:
    (out_dir / "sheets").mkdir(parents=True, exist_ok=True)
    res, scenes = [], {}
    for stem in stems:
        img = io.load_image(io.find_image(stem)); mask = segment(img)
        label = io.load_boxes(stem)
        gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes(label)]
        preds = det.detect(mask, cfg, CAM)
        scenes[stem] = io.parse_name(stem)["scene"] if not stem.startswith("DAVE_") else stem.split("_")[2]
        res.append(ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=label.get("clean", True)))
        sheet = det.draw(viz.overlay(img, mask), preds)
        for g in gts:
            x0, y0, x1, y1 = g.bbox; cv2.rectangle(sheet, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        cv2.imwrite(str(out_dir / "sheets" / f"{stem}.png"), sheet)
    ed.write_results(res, out_dir, title=str(out_dir.relative_to(OUT)))
    return ed.score(res, scenes, out_scope=())


def count_campus(stems, segment, cfg, out_dir) -> dict:
    (out_dir / "sheets").mkdir(parents=True, exist_ok=True)
    right, neg_boxes, wrong_color_frames, per = 0, 0, 0, {}
    for stem in stems:
        img = io.load_image(io.find_image(stem)); mask = segment(img)
        preds = det.detect(mask, cfg, CAM)
        o, b = sum(p.color == ORANGE for p in preds), sum(p.color == BLUE for p in preds)
        exp = EXPECTED[stem]
        ok = (o, b) == (exp["orange"], exp["blue"])
        right += ok
        if "_neg_" in stem:
            neg_boxes += len(preds)
        if o > exp["orange"] or b > exp["blue"]:
            wrong_color_frames += 1
        per[stem.replace("4A8B_campus_light_", "")] = f"{o}/{b}" + ("" if ok else f" (exp {exp['orange']}/{exp['blue']})")
        cv2.imwrite(str(out_dir / "sheets" / f"{stem}.png"), det.draw(viz.overlay(img, mask), preds))
    return {"right": right, "n": len(stems), "neg_boxes": neg_boxes, "frames_with_extra_boxes": wrong_color_frames, "per_frame": per}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sp = splits.load_splits()
    home = sorted(s for s in sp["train"] if s.startswith("4A8B_window_light"))
    campus = sorted(s for s in sp["train"] if s.startswith("4A8B_campus_light"))
    dave = sorted(p.stem.replace("_boxes", "") for p in io.LABELS_DIR.glob("DAVE_*_boxes.json"))
    hook = wb.BarrelDetectorHook.default(cam=CAM)
    hs = probe.fit_hs(home, 10, 5, 95)
    fronts = {"v1": lambda img: pl.segment(pl.Frame.from_image(img), hook.model)[0], "hs": hs.segment}
    md = ["# Detector hardening: old (bands) vs new (cores, no dark gaps, body color) vs new+dark", "",
          f"git {bcv.git_hash()}; camera AIM_4A8B6118_BOXFIT; v2 rule where labels exist. Front ends: v1 = frozen afd85483; hs = hue sector + S floor (probe 2026-11-07, hs_p10h5, fit on the home train masks).", "",
          "| front end | detector | home train v2 (F1 o / b) | neg FD | Dave 12 v2 (F1 o / b) | neg FD | campus: right count | campus negatives: boxes | campus frames with extra boxes |",
          "|---|---|---|---|---|---|---|---|---|"]
    summary, per = {}, {}
    for fname, seg in fronts.items():
        for aname, cfg in ARMS.items():
            key = f"{fname}/{aname}"
            h = score_labeled(home, seg, cfg, OUT / fname / aname / "home_train")
            d = score_labeled(dave, seg, cfg, OUT / fname / aname / "dave")
            c = count_campus(campus, seg, cfg, OUT / fname / aname / "campus")
            summary[key] = {"home": h, "dave": d, "campus": {k: v for k, v in c.items() if k != "per_frame"}}
            per[key] = c["per_frame"]
            md.append(f"| {fname} | {aname} | **{h['primary']:.2f}** ({h['F1_o']:.2f} / {h['F1_b']:.2f}) | {h['neg_false_detections']} | **{d['primary']:.2f}** ({d['F1_o']:.2f} / {d['F1_b']:.2f}) | {d['neg_false_detections']} | "
                      f"{c['right']} / {c['n']} | {c['neg_boxes']} | {c['frames_with_extra_boxes']} |")
    md += ["", "## Campus train frames, boxes orange/blue (expected in brackets where wrong)", "",
           "| frame | " + " | ".join(per) + " |", "|---|" + "---|" * len(per)]
    for stem in campus:
        k = stem.replace("4A8B_campus_light_", "")
        md.append(f"| {k} | " + " | ".join(per[a][k] for a in per) + " |")
    (OUT / "summary.md").write_text("\n".join(md))
    json.dump({"git": bcv.git_hash(), "arms": {k: v.to_dict() for k, v in ARMS.items()}, "hs_model": {str(c): b.to_dict() for c, b in hs.boxes.items()},
               "home": home, "campus": campus, "dave": dave, "summary": summary}, (OUT / "config.json").open("w"), indent=1, default=str)
    print("\n".join(md)); print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
