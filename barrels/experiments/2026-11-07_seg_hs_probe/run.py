#!/usr/bin/env python3
"""Probe for the segmentation redesign: class boxes in hue + HSV-saturation instead of RGB, and no top-row stages.

Hypothesis (from the attribution 2026-11-07): the three stages that lose the barrels in a real room — the background
prior and the saturation floor, both derived from the top 50 rows, and the RGB boxes — are all brightness-bound.
Hue is not; HSV saturation (S = (max-min)/max) is not either, unlike v1's max-min. So: fit per-class boxes in (H, S)
on the labeled home train frames exactly as v1 fits its RGB boxes (percentile boxes of labeled pixels), keep only
the brightness floor (V >= 40) and the horizon gate, drop the priors and the per-image floor. Nothing per image is
adapted, nothing is corrected.

Arms, all with the same detector (DetConfig()) and camera (AIM_4A8B6118_BOXFIT):
  v1        the frozen model afd85483 (RGB boxes, band floor, bg prior)
  hs_p5     per class: S floor = the 5th percentile of the labeled pixels' S; hue sector = the 2nd–98th percentile of
            the labeled pixels above that floor (orange's hue shifted by +30 so its sector does not wrap at 0/180)
  hs_p10    the same with the 10th percentile as the S floor
  hs_p10h5  the 10th percentile floor and a 5th–95th hue sector
The first run of this script (git 9563b50) fit plain 1–99 / 2–98 percentile boxes on (H, S) without the shift or the
floor: hue is circular and dark labeled pixels have random hue, so the sectors spanned most of the circle (orange
2–168, blue 5–170) and blue boxes appeared everywhere (22 on the 4 campus negatives). That run stays in
EXPERIMENTS.md as the failed iteration; this version is the fit done properly.

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


@dataclass
class HSModel:
    boxes: dict[int, bf.Box]
    v_min: int = 40
    horizon_row: int = 50

    def segment(self, bgr: np.ndarray) -> np.ndarray:
        v = bgr.max(axis=-1)
        keep = v >= self.v_min
        keep[: self.horizon_row] = False
        cand = {c: keep & bf.in_box(hs(bgr, HUE_SHIFT[c]), self.boxes[c]) for c in (ORANGE, BLUE)}
        both = cand[ORANGE] & cand[BLUE]
        if both.any():                                   # v1's tie rule: redder pixel -> orange
            orange_wins = bgr[..., 2] > bgr[..., 0]
            cand[ORANGE] &= ~both | orange_wins; cand[BLUE] &= ~both | ~orange_wins
        mask = np.full(bgr.shape[:2], OTHER, np.uint8)
        mask[cand[ORANGE]] = ORANGE; mask[cand[BLUE]] = BLUE
        return mask


HUE_SHIFT = {ORANGE: 30, BLUE: 0}      # orange sits at hue ~5-12 next to the 0/180 wrap; shifting by +30 makes its sector contiguous


def hs(bgr: np.ndarray, shift: int = 0) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    out = hsv[..., :2].astype(np.float32)          # H 0-179, S 0-255
    if shift:
        out[..., 0] = (out[..., 0] + shift) % 180
    return out


def fit_hs(stems: list[str], s_pct: float, h_lo: float, h_hi: float, v_min: int = 40) -> HSModel:
    """Per class: S floor = the s_pct percentile of the labeled pixels' S (V >= v_min, below the horizon); hue sector =
    the h_lo–h_hi percentiles of the labeled pixels above that floor, in the class's shifted hue."""
    px = {ORANGE: [], BLUE: []}
    for s in stems:
        img = io.load_image(io.find_image(s)); m = io.load_mask(io.mask_path(io.find_image(s)))
        v = img.max(axis=-1)
        for c in px:
            sel = (m == c) & (v >= v_min); sel[:50] = False
            px[c].append(hs(img, HUE_SHIFT[c])[sel])
    boxes = {}
    for c in px:
        f = np.concatenate(px[c])
        s_lo = float(np.percentile(f[:, 1], s_pct))
        hh = f[f[:, 1] >= s_lo, 0]
        boxes[c] = bf.Box((float(np.percentile(hh, h_lo)), s_lo), (float(np.percentile(hh, h_hi)), 255.0))
    return HSModel(boxes, v_min=v_min)


def score_labeled(stems, segment, title, out_dir) -> dict:
    res, scenes = [], {}
    (out_dir / "sheets").mkdir(parents=True, exist_ok=True)
    for stem in stems:
        img = io.load_image(io.find_image(stem))
        mask = segment(img)
        label = io.load_boxes(stem)
        gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes(label)]
        preds = det.detect(mask, det.DetConfig(), CAM)
        sheet = det.draw(viz.overlay(img, mask), preds)
        for g in gts:
            x0, y0, x1, y1 = g.bbox; cv2.rectangle(sheet, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        cv2.imwrite(str(out_dir / "sheets" / f"{stem}.png"), sheet)
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
    models = {"hs_p5": fit_hs(home_train, 5, 2, 98), "hs_p10": fit_hs(home_train, 10, 2, 98), "hs_p10h5": fit_hs(home_train, 10, 5, 95)}
    for k, m in models.items():
        arms[k] = m.segment
    md = ["# Segmentation probe: hue sector + HSV-saturation floor per class, no top-row stages", "",
          f"git {bcv.git_hash()}; boxes fit on the {len(home_train)} home train frames' masks; detector DetConfig(), camera AIM_4A8B6118_BOXFIT; v2 rule.", ""]
    for k, m in models.items():
        md.append(f"- `{k}`: orange hue {m.boxes[ORANGE].lo[0] - 30:.0f}–{m.boxes[ORANGE].hi[0] - 30:.0f} (OpenCV 0–179, unshifted), S >= {m.boxes[ORANGE].lo[1]:.0f}; "
                  f"blue hue {m.boxes[BLUE].lo[0]:.0f}–{m.boxes[BLUE].hi[0]:.0f}, S >= {m.boxes[BLUE].lo[1]:.0f}; V >= {m.v_min}, horizon {m.horizon_row}")
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
