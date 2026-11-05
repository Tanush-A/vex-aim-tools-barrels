# EVAL.md — metrics + protocol

**Version:** v1 (2026-10-14; protocol detailed 2026-10-19); **v2 detection rule + splits added 2026-11-02; one-table v2.0 splits 2026-11-03** (`DECISIONS.md`). Foundation doc — change only via a logged entry in `DECISIONS.md`. The v2 detection rule (bottom of this file) is the one that matters now; the per-pixel section is how the frozen segmentation was judged.

## Metrics

Per-pixel, computed per class (**orange**, **blue**) against the ground-truth masks (`DATA.md` label format). **Stripes count as their own color:** the orange stripe of a blue barrel is labeled and scored as orange, the blue stripe of an orange barrel as blue — matching `PROBLEM.md`.

- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **IoU** = TP / (TP + FP + FN)

Rules:

- Pixels labeled **255 (ignore)** — glare/uncertain — are excluded from all counts.
- Report **per condition** (surface × lighting × scene tag, from the filename convention in `DATA.md`), plus an overall aggregate. A method that only works on one table or one lamp must be visible as such.
- Aggregate = micro-average (pool pixels across images within a condition). Also report per-image numbers in the results folder so outlier frames are findable.
- **Negative frames** (`neg` scene, no barrels): precision/recall/IoU are undefined when a class is absent, so report instead the **fraction of pixels flagged** per class (false-positive rate), target ≈ 0. Report it per condition like the other metrics. Negative frames are excluded from the IoU aggregates and listed separately.

## Splits

- A **held-out test set is fixed early and never used for tuning.** No threshold fitting, no parameter sweeps, no "just checking" against test. It is evaluated once per milestone, with one pre-chosen config.
- **v1 (decided 2026-10-19):** test = 5 frames (`core_04, edge_02, far_01, neg_03, touch_01`), locked in `data/splits.json`. **Tuning uses leave-one-scene-out cross-validation over the 16 pool frames** (one fold per scene tag; a model never sees its held-out scene). The dev split is empty. `top_01`/`topstripe_01` are in the pool but excluded from the headline score (out of v1 scope); they are still predicted and reported.
- **Selection rule (pre-registered):** primary = mean of pooled orange and blue IoU over in-scope positive pool frames; disqualify any config with negative-frame FP rate > 0.5 % for either class; differences < 0.02 are "no difference" unless consistent in sign across ≥ 6 of 7 positive folds, then prefer the simpler setting; at most two coordinate passes.
- Split assignment is recorded in `DATA.md` and committed. New captures get assigned when added, before any method sees them, and existing assignments never move.
- Splits stratify by condition (don't put all warm-light frames in test); folds never split frames of one scene.

## Protocol

1. Every evaluation runs from a committed experiment script in `experiments/` with an explicit config (thresholds, priors, split).
2. Outputs go to `results/<date>_<name>/`: metrics table (CSV or MD), per-image numbers, and the debug previews for qualitative review. Big artifacts are gitignored; keep the small summary tables.
3. The results table + takeaway are logged in `EXPERIMENTS.md` immediately.
4. Comparisons between methods use the **same split and the same label version**. If labels are re-done, re-run the baselines.

## Implementation

`src/barrels/eval.py` (counts, metrics, per-condition aggregation, result tables), `src/barrels/splits.py` + `tools/make_splits.py` (fixed test set + pool in `data/splits.json`; `--test-only N` locks test once), `src/barrels/cv.py` (leave-one-scene-out driver, sweeps), `tools/eval_masks.py` (score a folder of predicted masks on a split → `results/<date>_<name>/`), `src/barrels/viz.py` (PROBLEM.md output images, debug sheets).

## Infrastructure correctness

Metric computation, mask IO, and label parsing have **unit tests** (`barrels/tests/`) — eval numbers are only meaningful if the harness is right. Algorithms themselves are judged by these eval numbers, not by unit tests.

## Detection metrics (v2, decided 2026-11-02 — `DECISIONS.md`)

Ground truth = one **box per physical barrel** (`DATA.md`, box labels): the full barrel as if occluders were transparent, clipped to the frame, with flags. A prediction is a `Barrel` (color, box in 640×480).

- **A box is correct** when it has the same color as a ground-truth box, overlaps it with **IoU ≥ 0.5**, **and** its bottom edge is within **max(3 px, 10 % of the ground-truth box height)** of the true bottom edge. Both conditions must hold. Rationale: the bottom edge is what the world map will use; a tenth of the height is a few pixels on a far barrel and ≈ 15 px on a near one. (Tanush 2026-11-02: can be adjusted later, via a logged decision.)
- **Matching:** greedy, class-aware, among eligible pairs (both conditions), highest IoU first; deterministic. Unmatched predictions are false positives, unmatched ground truth false negatives.
- **Every ground-truth barrel counts.** Occluded barrels are scored on their inferred full box (Dave 2026-10-30), truncated barrels on their clipped box, held barrels like any other. Nothing is "difficult"/ignored any more. Flags are used only to **report** errors by case (bottom seen vs `bottom_estimated`, occluded, truncated, held).
- **Per class:** precision, recall, F1 under the rule above, pooled over frames (micro). **Primary = mean of the two F1s.**
- **Negative frames** (no barrels): their false detections count as FP in the pooled score and are listed per frame. A false barrel on a negative frame that contains **no orange or blue clutter** (`clean: true` in the label file) **disqualifies** the config — a frame with nothing barrel-like in it must come back with nothing drawn.
- **Reported alongside:** matched-pair IoU; bottom-edge error (px, signed, positive = predicted lower; and as a fraction of box height), split by whether the labeler saw the bottom (`bottom_estimated` boxes are themselves a guess); barrel-count error per frame; color confusions (class-agnostic IoU matches with the wrong color).
- **Aggregation:** per condition (light × surface), per arrangement (scene tag), ALL, and — once a second table exists (v2.1) — **separately for the unseen table** (below). Per-image numbers in the results folder.
- **Floor:** the connected-components baseline (`detect_cc.py`), never tuned, re-scored under this rule.
- **Implementation (since 2026-11-03):** `src/barrels/eval_det.py` (`evaluate_frame(..., rule="v2")`, `match_best_first`), `tools/eval_boxes.py --pred DIR --rule v2`. The v1 rule (IoU only, occluded/truncated truth ignored) stays the tools' default so every earlier number reproduces; the numbers we report are v2. The 15 mm loose criterion and the projected/measured ground errors stay in the code for the world map later; they are not part of the v2 score.

### v2 splits

- The 21 v1 frames keep their split: the 16 pool frames → train, the locked 5-frame test stays test (this also keeps the v1 pixel test clean if the color ranges are re-fit).
- New v2 frames are assigned **at import, before any method sees them**, by `tools/make_splits.py --v2 --filter <robot>_<light>_<surface>` (`splits.assign_holdout_per_scene`): within the session, **one frame per scene tag that has ≥ 2 frames goes to test**, the rest to train; dev stays empty. Tuning uses cross-validation that holds out whole scenes (as v1).
- **v2.0 has one table** (decided 2026-11-03, timeline). The **unseen table** — a whole table × light session used for nothing but the final evaluation — is the v2.1 generalisation check, assigned the same way when that data is shot.
- Calibration frames (`calib`, `ruler`, `horizon`) are geometry-only and in no split.
- Selection rule as v1: primary metric; differences < 0.02 → simplest; at most two coordinate passes; test evaluated once per milestone with one pre-chosen config.

### The `measured` split (deferred 2026-11-02)

Defined 2026-10-28 for ground-position error in mm; **not used in v2**, which outputs boxes only. The known-distance `calib` frames serve geometry calibration instead. Revisit when the world map comes back into scope.
