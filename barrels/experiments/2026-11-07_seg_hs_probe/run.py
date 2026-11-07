#!/usr/bin/env python3
"""Probe for the segmentation redesign: class boxes in hue + HSV-saturation instead of RGB, and no top-row stages.

Hypothesis (from the attribution 2026-11-07): the three stages that lose the barrels in a real room — the background
prior and the saturation floor, both derived from the top 50 rows, and the RGB boxes — are all brightness-bound.
Hue is not; HSV saturation (S = (max-min)/max) is not either, unlike v1's max-min. So: fit per-class boxes in (H, S)
on the labeled home train frames exactly as v1 fits its RGB boxes (percentile boxes of labeled pixels), keep only
the brightness floor (V >= 40) and the horizon gate, drop the priors and the per-image floor. Nothing per image is
adapted, nothing is corrected.

Arms, all with the same detector (DetConfig()) and camera (AIM_4A8B6118_BOXFIT):
  v1       the frozen model afd85483 (RGB boxes, band floor, bg prior)
  hs       (H, S) boxes at the 1–99 percentiles of the home train labels, V >= 40, horizon 50
  hs_tight (H, S) boxes at 2–98

Scored where labels exist and counted where they do not:
  * the 16 home train frames (Tanush's boxes), v2 rule: the regression check (v1 = 0.91 there);
  * Dave's 12 labeled office frames, v2 rule: the outside check (v1 = 0 barrel pixels on all of them);
  * the 21 campus train frames: frames with the expected count per color (expected.json of the attribution
    experiment), boxes drawn on the 4 negatives.
No test frame of any session is loaded. A probe, not a tuning run: three arms, no sweep. Results: results/2026-11-07_seg_hs_probe/.

    python barrels/experiments/2026-11-07_seg_hs_probe/run.py
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import boxfit as bf, cv as bcv, detector as det, detect_types as dtp, eval_det as ed, geometry as geo, io, pipeline as pl, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, OTHER, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-07_seg_hs_probe"
CAM = geo.AIM_4A8B6118_BOXFIT
HOME, CAMPUS, DAVE = "4A8B_window_light", "4A8B_campus_light", "DAVE_"
EXPECTED = json.loads((HERE.parent / "2026-11-07_campus_attribution" / "expected.json").read_text())


def hs(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return hsv[..., :2].astype(np.float32)          # H 0-179, S 0-255


@dataclass
class HSModel:
    boxes: dict[int, bf.Box]
    v_min: int = 40
    horizon_row: int = 50

    def segment(self, bgr: np.ndarray) -> np.ndarray:
        f = hs(bgr)
        v = bgr.max(axis=-1)
        keep = v >= self.v_min
        keep[: self.horizon_row] = False
        cand = {c: keep & bf.in_box(f, self.boxes[c]) for c in (ORANGE, BLUE)}
        both = cand[ORANGE] & cand[BLUE]
        if both.any():                                   # v1's tie rule: redder pixel -> orange
            orange_wins = bgr[..., 2] > bgr[..., 0]
            cand[ORANGE] &= ~both | orange_wins; cand[BLUE] &= ~both | ~orange_wins
        mask = np.full(bgr.shape[:2], OTHER, np.uint8)
        mask[cand[ORANGE]] = ORANGE; mask[cand[BLUE]] = BLUE
        return mask


def fit_hs(stems: list[str], p_lo: float, p_hi: float, v_min: int = 40) -> HSModel:
    px = {ORANGE: [], BLUE: []}
    for s in stems:
        img = io.load_image(io.find_image(s)); m = io.load_mask(io.mask_path(io.find_image(s)))
        f = hs(img); v = img.max(axis=-1)
        for c in px:
            sel = (m == c) & (v >= v_min)
            px[c].append(f[sel])
    return HSModel({c: bf.fit_box(np.concatenate(px[c]), p_lo, p_hi) for c in px}, v_min=v_min)


def score_labeled(stems, segment, title, out_dir) -> dict:
    res, scenes = [], {}
    for stem in stems:
        img = io.load_image(io.find_image(stem))
        mask = segment(img)
        label = io.load_boxes(stem)
        gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes(label)]
        preds = det.detect(mask, det.DetConfig(), CAM)
        scenes[stem] = io.parse_name(stem)["scene"] if not stem.startswith(DAVE) else stem.split("_")[2]
        res.append(ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=label.get("clean", True)))
    ed.write_results(res, out_dir, title=title)
    return ed.score(res, scenes, out_scope=())


def count_campus(stems, segment, out_dir) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    right, neg_boxes, per = 0, 0, {}
    for stem in stems:
        img = io.load_image(io.find_image(stem))
        mask = segment(img)
        preds = det.detect(mask, det.DetConfig(), CAM)
        o, b = sum(p.color == ORANGE for p in preds), sum(p.color == BLUE for p in preds)
        exp = EXPECTED[stem]
        ok = (o, b) == (exp["orange"], exp["blue"])
        right += ok
        if "_neg_" in stem:
            neg_boxes += len(preds)
        per[stem.replace(CAMPUS + "_", "")] = f"{o}/{b}" + ("" if ok else f" (exp {exp['orange']}/{exp['blue']})")
        cv2.imwrite(str(out_dir / f"{stem}.png"), det.draw(viz.overlay(img, mask), preds))
    return {"right": right, "n": len(stems), "neg_boxes": neg_boxes, "per_frame": per}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sp = splits.load_splits()
    home_train = sorted(s for s in sp["train"] if s.startswith(HOME))
    campus_train = sorted(s for s in sp["train"] if s.startswith(CAMPUS))
    dave = sorted(p.stem.replace("_boxes", "") for p in io.LABELS_DIR.glob("DAVE_*_boxes.json"))
    assert not any(s in sp["test"] for s in home_train + campus_train)
    hook = wb.BarrelDetectorHook.default(cam=CAM)
    arms = {"v1": lambda img: pl.segment(pl.Frame.from_image(img), hook.model)[0]}
    models = {"hs": fit_hs(home_train, 1, 99), "hs_tight": fit_hs(home_train, 2, 98)}
    for k, m in models.items():
        arms[k] = m.segment
    md = ["# Segmentation probe: (hue, HSV-saturation) boxes, no top-row stages", "",
          f"git {bcv.git_hash()}; boxes fit on the {len(home_train)} home train frames' masks; detector DetConfig(), camera AIM_4A8B6118_BOXFIT; v2 rule.", ""]
    for k, m in models.items():
        md.append(f"- `{k}` boxes (H 0–179, S 0–255): orange {m.boxes[ORANGE].to_dict()}, blue {m.boxes[BLUE].to_dict()}; V >= {m.v_min}, horizon {m.horizon_row}")
    md += ["", "| arm | home train v2 (F1 o / b) | neg FD | Dave 12 v2 (F1 o / b) | neg FD | campus train: frames with the right count | boxes on the 4 campus negatives |",
           "|---|---|---|---|---|---|---|"]
    summary = {}
    for name, seg in arms.items():
        h = score_labeled(home_train, seg, f"{name} on home train", OUT / name / "home_train")
        d = score_labeled(dave, seg, f"{name} on Dave's 12", OUT / name / "dave")
        c = count_campus(campus_train, seg, OUT / name / "campus_sheets")
        summary[name] = {"home": h, "dave": d, "campus": c}
        md.append(f"| {name} | **{h['primary']:.2f}** ({h['F1_o']:.2f} / {h['F1_b']:.2f}) | {h['neg_false_detections']} | **{d['primary']:.2f}** ({d['F1_o']:.2f} / {d['F1_b']:.2f}) | {d['neg_false_detections']} | "
                  f"{c['right']} / {c['n']} | {c['neg_boxes']} |")
    md += ["", "## Campus train frames: boxes orange/blue per arm (expected in brackets where wrong)", "",
           "| frame | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for stem in campus_train:
        key = stem.replace(CAMPUS + "_", "")
        md.append(f"| {key} | " + " | ".join(summary[a]["campus"]["per_frame"][key] for a in arms) + " |")
    (OUT / "summary.md").write_text("\n".join(md))
    json.dump({"git": bcv.git_hash(), "home_train": home_train, "campus_train": campus_train, "dave": dave,
               "models": {k: {"boxes": {str(c): b.to_dict() for c, b in m.boxes.items()}, "v_min": m.v_min, "horizon_row": m.horizon_row} for k, m in models.items()},
               "summary": {a: {"home": s["home"], "dave": s["dave"], "campus": {k: v for k, v in s["campus"].items() if k != "per_frame"}} for a, s in summary.items()}},
              (OUT / "config.json").open("w"), indent=1, default=str)
    print("\n".join(md)); print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
