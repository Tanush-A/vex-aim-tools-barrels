# EVAL.md — metrics + protocol

**Version:** v1 (2026-10-14). Foundation doc — change only via a logged entry in `DECISIONS.md`. Open question for Dave: what counts as "good" (targets)? See `STATUS.md`.

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

- A **held-out test set is fixed early and never used for tuning.** No threshold fitting, no parameter sweeps, no "just checking" against test. Tune on train/dev only.
- Split assignment is recorded in `DATA.md` and committed. New captures get assigned to a split when added, before any method sees them.
- Splits should stratify by condition (don't put all warm-light frames in test).

## Protocol

1. Every evaluation runs from a committed experiment script in `experiments/` with an explicit config (thresholds, priors, split).
2. Outputs go to `results/<date>_<name>/`: metrics table (CSV or MD), per-image numbers, and the debug previews for qualitative review. Big artifacts are gitignored; keep the small summary tables.
3. The results table + takeaway are logged in `EXPERIMENTS.md` immediately.
4. Comparisons between methods use the **same split and the same label version**. If labels are re-done, re-run the baselines.

## Infrastructure correctness

Metric computation, mask IO, and label parsing have **unit tests** (`barrels/tests/`) — eval numbers are only meaningful if the harness is right. Algorithms themselves are judged by these eval numbers, not by unit tests.
