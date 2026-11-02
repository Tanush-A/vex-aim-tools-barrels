# STATUS.md — current state

**Updated:** 2026-11-02 (v2.0 spec written after the 2026-10-30 meeting with Dave; waiting on Tanush's OK of the milestone plan). Plain-English code guide: `docs/HOW-IT-WORKS.md`.

## Where we are

- **v1 (per-pixel segmentation) done, frozen at `afd85483`:** test orange IoU 0.843, blue 0.813, zero false pixels on the negative frame; the saturation floor and wall model adapt per image; only the two RGB boxes are learned. Details: `EXPERIMENTS.md` 2026-10-20/22, `OVERNIGHT-2026-10-20.md`, `Post-v1-SUMMARY.md`.
- **v1.5 (detection scaffolding) done except what v2 replaces:** `geometry.py`, instance auto-split + tool, `Barrel` type, `eval_det.py`, cleanup flags (tie, not adopted), CC reference detector (provisional floor F1 0.45 on v1 masks / 0.63 on GT masks), world-map bridge stub. `OVERNIGHT-2026-10-28.md`. The measured set and the instance review were superseded on 2026-11-02 (below).
- **Dave meeting 2026-10-30 (Tanush's recap):** v2 = barrel detection = draw boxes on a still image; the bottom edge matters most; infer the full box and clip it to the frame; handle hidden bottoms via geometry; a few known-distance frames as a lookup table for close barrels; clutter and other objects in the data; the world map is separate and untouched. And: Tanush must understand the main code himself.
- **v2.0 spec written 2026-11-02:** `PROBLEM.md` (v2 section), `EVAL.md` (box rule + v2 splits), `DATA.md` (box labels, v2 capture plan, calibration session), `constraints.md` (close zone, v2 scene assumptions), `DECISIONS.md` 2026-11-02, `HOW-IT-WORKS.md`.

## Next steps — v2.0 milestones (proposed 2026-11-02; Tanush to OK)

Main code (pipeline, geometry, detector, eval) gets a walkthrough before every commit and a section in `HOW-IT-WORKS.md`; side tools don't.

| # | milestone | who | needs |
|---|---|---|---|
| M1 | **Box labels.** `_boxes.json` format + loader/validator in `io.py`; `tools/box_tool.py` (drag boxes, color, flags, `--from-inst` conversion of the 21 v1 frames); Tanush fixes the 21 converted frames (≈ 15 min: make occluded boxes amodal, set flags). Side tool + IO. | Claude, then Tanush | — |
| M2 | **Eval under the v2 rule.** `eval_det.py` reads box GT; correct = IoU ≥ 0.5 **and** bottom edge within max(3 px, 10 % height); every GT counts; negatives pooled + clean-negative disqualification; per-arrangement and unseen-table reports; `make_splits.py --holdout-condition`; re-score the CC floor. Tests. **Main code → walkthrough.** | Claude | M1 |
| M3 | **Data.** Tanush shoots white / beige / black (≈ 19 frames each, `DATA.md` v2 capture plan) + the 12-frame calibration session (+ `horizon`); imports; splits assigned at import (beige = unseen table); labels boxes (≈ 30 s/frame); optional 2 masks per table. | Tanush | M1 |
| M4 | **Geometry calibration** from the `calib` frames: fit f and tilt for 4A8B from the top-edge row and the width at known distances; the close-zone table; update `constraints.md` #2/#3/#7. Experiment + `EXPERIMENTS.md`. **Main code → walkthrough.** | Claude | M3 |
| M5 | **Segmentation check on the new tables.** Run `afd85483` on each table's training frames, look at overlays, decide whether the RGB boxes need the one re-fit (same method); log. **Main code if re-fit → walkthrough.** | Claude | M3 |
| M6 | **The detector** (`detect_stripe.py`), built and explained in steps: stripe finder → barrel from stripe (color, distance, expected box) → stripeless candidates with the size/shape check → carving boxes out of merged blobs → bottom-edge precedence → clip → draw. CLI `tools/detect_image.py image.png` → `<stem>_boxes.png`. Tuned by scene-held-out CV on train under the pre-registered rule. **Main code → walkthrough per step.** | Claude (+ Tanush reading) | M2; M3–M5 for tuning (can start on the 21 frames) |
| M7 | **One test run** (locked test + unseen table), results, `EXPERIMENTS.md`, plain-English recap, short email to Dave. | Claude drafts, Tanush sends | M6 |

Rough effort: Claude ≈ 14 h of sessions; Tanush ≈ 3 h (shooting ≈ 1.5 h, labeling ≈ 1 h, reading).

## Housekeeping

- `segment_image.py` used to write its four output images next to the input; eight such files landed in `data/raw/` on 2026-11-02. Fixed: outputs default to `results/segment_image/`, `io.list_images` skips `_pred/_overlay/_orange/_blue`, and the stray files were moved there.
- Five `_inst.json` files were reviewed by Tanush (uncommitted as of 2026-11-02): close_01/02, cluster_01/02, core_01. The instance review is superseded by box labels (M1); the files stay as they are and feed the `--from-inst` conversion.
- Both earlier draft emails (v1 result; v1.5 / v2 proposal) were sent or superseded by the 2026-10-30 meeting; removed from this doc (in git history).

## Open questions for Dave (v2)

- **Knocked-over barrels:** upright only in v2; does a barrel on its side ever need detecting?
- **Per-robot calibration:** one (f, tilt) for every robot, or the 12 `calib` frames per robot? (Dave 2026-10-30: f should not differ much.)
- **"Drawn correctly" tolerance:** we use bottom edge within a tenth of the barrel height; fine, or tighter?

## Parked until the world map comes back (not v2)

Integration route (display vs replace aivision), latency, worldmap's 22 mm / 11 mm / `1.1·w` pad vs the measured barrel, ground-position targets in mm, the `measured` split, the skin-vs-orange hue test, Dave's `detect.py` / Lab 6 material, the `openvocab` / `depthmap` branches.

## Navigator requests

N-001…N-004 and the 2026-10-14 review notes: all done (`DECISIONS.md`, git history). Nothing open.

## Blockers

Tanush's OK on the milestone plan above; then M1 starts.
