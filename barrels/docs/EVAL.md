# EVAL.md — metrics + protocol

**Version:** v1 (2026-10-14; protocol detailed 2026-10-19, see `DECISIONS.md`). Foundation doc — change only via a logged entry in `DECISIONS.md`. Open question for Dave: what counts as "good" (targets)? See `STATUS.md`.

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
