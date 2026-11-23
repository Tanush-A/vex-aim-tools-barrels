# Run all, 2026-11-23

Steps: tests ok, gate failed (exit 1), eval_table ok, vendor ok, adaptive skipped.

## Missing in the data (file names only; test frames counted, never opened)

7 new conditions (sets with vendor files). Test frames among them, counted from data/splits.json and never opened: 13 (both_abpgray 2, lampcool6_ottoman 2, lampmid3_ottoman 2, lampmid6_ottoman 2, lampwarm6_ottoman 2, overheaddim_palewood 2, window_abpwhite 1).

Complete (split, boxed, slider labels set, a vendor file on every train frame): both_abpgray, lampcool6_ottoman, lampmid3_ottoman, lampmid6_ottoman, lampwarm6_ottoman, overheaddim_palewood, window_abpwhite.

## Tests

Pass: 765 passed in 14.72s.

## Never-regress check

**FAIL**. Failing rows: 4A8B_window_abpwhite occlx.
- 4A8B_window_abpwhite occlx: known: the false orange box on the striped-clutter trap `occlx_15` (TODO A9, the old close-up rule det1); fixed on another branch, not yet merged.

Protected sets (baseline -> now): HOME found 28 -> 28 of 29; false boxes 0 -> 0; boxes on empty frames 0 -> 0; CAMPUS found 35 -> 35 of 35; false boxes 0 -> 0; boxes on empty frames 0 -> 0.

## Full eval table

ok (train frames only): `03_eval_table.txt`.

## Ours against the vendor (train frames with a vendor file)

| condition | barrels | ours found / false | vendor found / false | ours / vendor by place |
|---|---:|---|---|---|
| both_abpgray | 16 | 10 / 2 | 16 / 0 | 11 / 16 |
| lampcool6_ottoman | 15 | 3 / 0 | 13 / 1 | 3 / 14 |
| lampmid3_ottoman | 15 | 1 / 1 | 10 / 1 | 2 / 11 |
| lampmid6_ottoman | 15 | 6 / 0 | 13 / 1 | 6 / 14 |
| lampwarm6_ottoman | 15 | 0 / 1 | 11 / 0 | 0 / 11 |
| overheaddim_palewood | 15 | 12 / 1 | 12 / 1 | 12 / 13 |
| window_abpwhite | 32 | 26 / 2 | 24 / 4 | 26 / 27 |

Strict v2 rule. All together: ours 58 of 123 with 7 false; the vendor 99 of 123 with 8 false.
The vendor finds 45 barrels we miss, on 27 frames (list: `barrels/results/2026-11-23_vendor/summary.md`).
Vendor files: conversion checked (center fit slope 1.99 x, 2.03 y; 2 expected), free-standing barrels median IoU with the hand box 0.82.
Hidden barrels the vendor finds (strict or by place) and we miss: `both_abpgray_clutter_01` #2, `lampcool6_ottoman_occl_02` #1, `lampmid6_ottoman_occl_02` #1, `overheaddim_palewood_occl_02` #1, `lampcool6_ottoman_clutter_01` #4, `lampmid3_ottoman_clutter_01` #4, `lampmid6_ottoman_clutter_01` #4, `window_abpwhite_occlx_03` #1, `window_abpwhite_occlx_06` #1, `window_abpwhite_occlx_10` #1.

## Adaptive-threshold rule

Not run: `experiments/2026-11-24_adaptive/run.py` is not on this branch.

## Needs your decision

- The vendor finds more than ours on both_abpgray, lampcool6_ottoman, lampmid3_ottoman, lampmid6_ottoman, lampwarm6_ottoman: which of these count as ordinary conditions (the goal is to match it there)?

Logs: `01_tests.txt`, `02_gate.txt`, `03_eval_table.txt`, `04_vendor.txt`, `05_adaptive.txt` (in this folder, not committed).
