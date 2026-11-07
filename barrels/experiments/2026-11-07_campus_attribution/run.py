#!/usr/bin/env python3
"""Attribution of the live failures on the real campus frames (session 2026-11-07): segmentation or detector?

The detector as it stands (BarrelDetectorHook.default(): frozen v1 model afd85483 -> stripe-anchored detector,
camera AIM_4A8B6118_BOXFIT) on the 21 **train** frames of the campus session (`4A8B_campus_light_*`; the 10
test frames are never loaded). No box labels exist yet, so the truth here is count-level: how many orange-body
and blue-body barrels are in the frame (`expected.json`, counted by eye from the raw frames; superseded by
Tanush's box labels when they exist) — enough to say "missed", "false box", "right count" per frame. Per frame:

  * the segmentation's per-image numbers (the saturation floor it chose from the top rows, the background and
    table priors' rejection rates, barrel pixels per class),
  * one diagnostic arm, `floor40`: the same model with the saturation floor fixed at 40 (the v1 constant before
    the per-image floor) — how much of the loss is the adaptive floor alone,
  * the stripe finder's verdict on every band it considered (the band log of experiments/2026-11-06_live_first_run),
  * a sheet: raw | segmentation tint | tint + boxes (yellow/green) + stripes found (magenta) | pixels inside a
    class color box that the saturation floor removed (what the floor costs, in that class's color).

`judgments.json` (hand-written after looking at the sheets; "seg" / "det" / "ok" per frame with a note) is merged
into the summary so the attribution is one table. Results: results/2026-11-07_campus_attribution/ (summary.md,
per_frame.csv, config.json committed; sheets gitignored). Verdict: EXPERIMENTS.md 2026-11-07.

    python barrels/experiments/2026-11-07_campus_attribution/run.py
"""
from __future__ import annotations

import csv
import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import boxfit as bf, cv as bcv, detector as det, geometry as geo, io, pipeline as pl, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-07_campus_attribution"
FILTER = "4A8B_campus_light"
CAM = geo.AIM_4A8B6118_BOXFIT
_spec = importlib.util.spec_from_file_location("live_first_run", HERE.parent / "2026-11-06_live_first_run" / "run.py")
_first_run = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_first_run)
band_report = _first_run.band_report                      # the same tests as detector.find_stripes, one line per band


def campus_train_stems() -> list[str]:
    sp = splits.load_splits()
    test = {s for s in sp["test"] if FILTER in s}
    stems = sorted(s for s in sp["train"] if FILTER in s)
    assert not (set(stems) & test), "a test frame leaked into the train list"
    return stems


def floor_loss(frame: pl.Frame, model: pl.Model, smin: dict[int, int]) -> dict[int, np.ndarray]:
    """Pixels inside a class's color box, past the fixed gates and the priors, that the saturation floor removed."""
    cfg = model.cfg
    keep = pl._fixed_keep(frame, cfg)
    keep &= pl._prior_keep(frame, cfg, {}, smin[ORANGE])
    feats = frame.features(cfg.box_space)
    return {c: keep & (frame.sat < smin[c]) & bf.in_box(feats, model.boxes[c]) for c in (ORANGE, BLUE)}


def sheet(img: np.ndarray, mask: np.ndarray, barrels, stripes, lost: dict[int, np.ndarray], title: str) -> np.ndarray:
    tint = viz.overlay(img, mask)
    boxes = det.draw(tint, barrels)
    for s in stripes:
        x0, y0, x1, y1 = s.bbox
        cv2.rectangle(boxes, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 1)
    lostimg = img.copy()
    lostimg[lost[ORANGE]] = (0, 128, 255)
    lostimg[lost[BLUE]] = (255, 100, 0)
    panels = [img, tint, boxes, lostimg]
    labels = ["raw", "segmentation", "boxes + stripes found (magenta)", "in a color box, removed by the saturation floor"]
    for p, t in zip(panels, labels):
        cv2.putText(p, t, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
        cv2.putText(p, t, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    top, bottom = np.hstack(panels[:2]), np.hstack(panels[2:])
    out = np.vstack([top, bottom])
    cv2.putText(out, title, (8, out.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
    cv2.putText(out, title, (8, out.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sheets").mkdir(exist_ok=True)
    hook = wb.BarrelDetectorHook.default(cam=CAM)
    model40 = dataclasses.replace(hook.model, cfg=dataclasses.replace(hook.model.cfg, s_min_mode="fixed", s_min=40, s_min_blue=None))
    expected = json.loads((HERE / "expected.json").read_text()) if (HERE / "expected.json").exists() else {}
    judgments = json.loads((HERE / "judgments.json").read_text()) if (HERE / "judgments.json").exists() else {}
    stems = campus_train_stems()
    rows, md = [], []
    md += ["# Campus session 2026-11-07 — attribution on the 21 train frames", "",
           f"git {bcv.git_hash()}; model afd85483 (frozen v1), detector DetConfig() (the stripe step), camera AIM_4A8B6118_BOXFIT. "
           "Expected = barrels of each body color counted by eye (`expected.json`); `floor40` = the same model with the saturation floor fixed at 40. "
           "Verdict/notes = hand judgments from the sheets (`judgments.json`).", "",
           "| frame | expected O/B | floor | bg rej | table rej | orange px | blue px | boxes O/B | floor40: px O/B, boxes O/B | verdict | notes |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    bands_md = ["", "## The stripe finder, band by band", "",
                "Columns: body color the band sits between; band x, y, size; pixels of the other barrel color (a real stripe) and unlabeled pixels "
                "(shadow) inside it; expected barrel width / stripe height at that row. Bands under 200 px are not listed.", ""]
    for stem in stems:
        img = io.load_image(io.find_image(stem))
        frame = pl.Frame.from_image(img)
        mask, info = pl.segment(frame, hook.model)
        barrels = det.detect(mask, hook.det_cfg, CAM)
        stripes = det.find_stripes(mask, CAM, hook.det_cfg)
        smin, _ = pl.effective_s_min(frame, hook.model.cfg)
        lost = floor_loss(frame, hook.model, smin)
        mask40, _ = pl.segment(frame, model40)
        barrels40 = det.detect(mask40, hook.det_cfg, CAM)
        n_o, n_b = int((mask == ORANGE).sum()), int((mask == BLUE).sum())
        bo, bb = sum(b.color == ORANGE for b in barrels), sum(b.color == BLUE for b in barrels)
        n_o40, n_b40 = int((mask40 == ORANGE).sum()), int((mask40 == BLUE).sum())
        bo40, bb40 = sum(b.color == ORANGE for b in barrels40), sum(b.color == BLUE for b in barrels40)
        exp = expected.get(stem, {})
        exp_s = f"{exp.get('orange', '?')}/{exp.get('blue', '?')}"
        j = judgments.get(stem, {})
        bg = info.get("bg") or {}; tb = info.get("table") or {}
        row = dict(stem=stem, scene=io.parse_name(stem)["scene"], exp_orange=exp.get("orange"), exp_blue=exp.get("blue"),
                   s_min_eff=info["s_min_eff"], band_sat_pct=round(info.get("band_sat_pct", float("nan")), 1),
                   bg_rejected=round(bg.get("rejected_frac", float("nan")), 3), table_rejected=round(tb.get("rejected_frac", float("nan")), 3),
                   orange_px=n_o, blue_px=n_b, boxes_orange=bo, boxes_blue=bb,
                   lost_orange_px=int(lost[ORANGE].sum()), lost_blue_px=int(lost[BLUE].sum()),
                   f40_orange_px=n_o40, f40_blue_px=n_b40, f40_boxes_orange=bo40, f40_boxes_blue=bb40,
                   verdict=j.get("verdict", ""), notes=j.get("notes", ""))
        rows.append(row)
        md.append(f"| {stem.replace(FILTER + '_', '')} | {exp_s} | {row['s_min_eff']} | {row['bg_rejected']} | {row['table_rejected']} | {n_o} | {n_b} | "
                  f"{bo}/{bb} | {n_o40}/{n_b40}, {bo40}/{bb40} | {row['verdict']} | {row['notes']} |")
        bands_md += [f"### {stem.replace(FILTER + '_', '')}", "", "| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |", "|---|---|---|---|---|---|---|---|"]
        band_report(mask, bands_md)
        bands_md += ["", "detect() returns:" if barrels else "detect() returns nothing.", ""]
        for b in barrels:
            bands_md.append(f"- {b.color_name} x {b.bbox[0]}-{b.bbox[2]} y {b.bbox[1]}-{b.bbox[3]} from {b.source} {sorted(b.flags)} conf {b.confidence:.2f}")
        bands_md.append("")
        cv2.imwrite(str(OUT / "sheets" / f"{stem}.png"), sheet(img, mask, barrels, stripes, lost,
                     f"{stem}  floor {row['s_min_eff']}  orange {n_o} px  blue {n_b} px  boxes {bo}/{bb}  (floor40: {n_o40}/{n_b40} px, {bo40}/{bb40})"))
        cv2.imwrite(str(OUT / "sheets" / f"{stem}_floor40.png"), det.draw(viz.overlay(img, mask40), barrels40))
    with (OUT / "per_frame.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # totals the judgments allow
    verdicts = [r["verdict"] for r in rows if r["verdict"]]
    md += ["", f"Frames judged: {len(verdicts)} of {len(rows)}; " + ", ".join(f"{v}: {verdicts.count(v)}" for v in sorted(set(verdicts))) if verdicts else "", ""]
    (OUT / "summary.md").write_text("\n".join(md + bands_md))
    json.dump({"git": bcv.git_hash(), "model": str(wb.DEFAULT_MODEL), "cam": "AIM_4A8B6118_BOXFIT", "det_cfg": hook.det_cfg.to_dict(),
               "floor40_cfg": model40.cfg.to_dict(), "stems": stems, "expected": expected, "judgments": judgments},
              (OUT / "config.json").open("w"), indent=1)
    print("\n".join(md))
    print(f"\nwrote {OUT}/summary.md, per_frame.csv, sheets/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
