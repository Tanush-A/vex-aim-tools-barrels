# Validation of the ruler-fit camera on the train frames (rule: PREREG.md)

git 160de06. Old camera: f 400, tilt 22.25°, height 43.47 mm, horizon row 76.4. New camera: f 400, tilt 20.4°, height 40.2 mm, horizon row 91.2. Train frames only.

## Verdict

- (a) the top-row bottom bias shrinks on HOME and CAMPUS: **FAIL**
- (b) width and height ratios of HOME and CAMPUS within 0.95 to 1.05: **FAIL**
- (c) never regress: **FAIL** (rows: HOME cluster, HOME occl; negative frames that gain a box: none)
- **The new camera does NOT pass the pre-registered rule: no default changes.**

## Rule (a) and (b): the size check

| set | boxes | median bottom from top, old | new | far + mid boxes | old | new | (a) | median width ratio, new | median height ratio, new | (b) |
|---|---|---|---|---|---|---|---|---|---|---|
| HOME | 19 | +4.4 | -8.1 | 15 | +4.8 | -8.1 | FAIL | 1.07 | 1.06 | FAIL |
| CAMPUS | 32 | +5.4 | -6.7 | 16 | +6.7 | -5.9 | FAIL | 1.05 | 1.04 | FAIL |

## The size check in full (191 boxes; 0 left out because a camera has no finite size at their row)

Ratio = drawn size / the size the camera expects for a barrel whose bottom edge is at the box's bottom row. Bottom from top / from width = inferred bottom row minus drawn bottom row (+ = inferred lower). Median (10th to 90th percentile).

| set | boxes | camera | width ratio | height ratio | bottom from top, px | bottom from width, px |
|---|---|---|---|---|---|---|
| HOME | 19 | old | 0.99 (0.92 to 1.03) | 0.97 (0.93 to 1.00) | +4.4 (-0.6 to +8.4) | +1.4 (-1.1 to +3.6) |
| HOME | 19 | new | 1.07 (1.03 to 1.14) | 1.06 (1.03 to 1.12) | -8.1 (-10.7 to -4.2) | +0.6 (-1.8 to +2.9) |
| CAMPUS | 32 | old | 0.98 (0.92 to 1.10) | 0.97 (0.89 to 1.01) | +5.4 (-3.0 to +11.5) | +0.8 (-2.5 to +10.0) |
| CAMPUS | 32 | new | 1.05 (1.00 to 1.17) | 1.04 (1.00 to 1.07) | -6.7 (-10.7 to +0.1) | +0.4 (-3.2 to +13.1) |
| BLACK | 14 | old | 1.03 (0.96 to 1.17) | 0.99 (0.95 to 1.02) | +1.1 (-4.9 to +5.6) | +2.1 (-2.3 to +10.0) |
| BLACK | 14 | new | 1.09 (0.99 to 1.26) | 1.07 (1.02 to 1.09) | -8.3 (-12.7 to -6.4) | +1.3 (-3.0 to +9.2) |
| WOOD | 126 | old | 0.95 (0.93 to 1.09) | 0.96 (0.90 to 0.99) | +7.1 (+3.3 to +10.2) | +0.6 (-1.6 to +9.2) |
| WOOD | 126 | new | 1.02 (0.98 to 1.14) | 1.02 (0.98 to 1.07) | -3.9 (-7.7 to +2.6) | -0.1 (-2.4 to +8.5) |

By distance (drawn width: far under 35 px, mid 35 to 60, near over 60):

| set | range | boxes | camera | width ratio | height ratio | bottom from top, px | bottom from width, px |
|---|---|---|---|---|---|---|---|
| HOME | far | 3 | old | 0.93 (0.92 to 0.95) | 0.91 (0.86 to 0.98) | +7.4 (+1.8 to +11.1) | +1.7 (-2.1 to +2.5) |
| HOME | far | 3 | new | 1.12 (1.08 to 1.15) | 1.12 (1.06 to 1.17) | -8.5 (-14.1 to -4.3) | +1.1 (-2.8 to +1.9) |
| HOME | mid | 12 | old | 0.99 (0.95 to 1.05) | 0.97 (0.94 to 0.98) | +4.7 (+3.0 to +8.2) | +1.3 (-0.6 to +4.6) |
| HOME | mid | 12 | new | 1.08 (1.03 to 1.13) | 1.06 (1.03 to 1.08) | -7.9 (-10.1 to -4.5) | +0.6 (-1.4 to +3.8) |
| HOME | near | 4 | old | 1.02 (1.01 to 1.03) | 1.00 (1.00 to 1.02) | -0.9 (-3.5 to -0.4) | +1.2 (-0.5 to +2.3) |
| HOME | near | 4 | new | 1.04 (1.03 to 1.05) | 1.03 (1.03 to 1.04) | -7.7 (-10.8 to -6.8) | +0.7 (-1.1 to +1.8) |
| CAMPUS | far | 2 | old | 0.90 (0.90 to 0.90) | 0.89 (0.88 to 0.90) | +10.2 (+9.1 to +11.3) | +0.4 (+0.0 to +0.9) |
| CAMPUS | far | 2 | new | 1.05 (1.04 to 1.05) | 1.05 (1.04 to 1.07) | -4.5 (-5.8 to -3.2) | -0.2 (-0.6 to +0.2) |
| CAMPUS | mid | 14 | old | 0.95 (0.92 to 1.01) | 0.95 (0.92 to 0.98) | +6.6 (+3.1 to +8.8) | +0.3 (-2.3 to +2.4) |
| CAMPUS | mid | 14 | new | 1.05 (0.99 to 1.09) | 1.05 (1.03 to 1.08) | -6.1 (-9.0 to -3.5) | -0.4 (-3.1 to +1.7) |
| CAMPUS | near | 16 | old | 1.03 (0.97 to 1.26) | 1.00 (0.89 to 1.02) | +0.7 (-5.1 to +88.4) | +3.3 (-1.3 to +70.0) |
| CAMPUS | near | 16 | new | 1.08 (1.00 to 1.27) | 1.03 (0.85 to 1.05) | -8.3 (-10.9 to +141.0) | +2.5 (-2.1 to +79.1) |
| BLACK | far | 1 | old | 0.91 (0.91 to 0.91) | 0.89 (0.89 to 0.89) | +9.1 (+9.1 to +9.1) | +0.7 (+0.7 to +0.7) |
| BLACK | far | 1 | new | 1.09 (1.09 to 1.09) | 1.08 (1.08 to 1.08) | -6.3 (-6.3 to -6.3) | +0.1 (+0.1 to +0.1) |
| BLACK | mid | 5 | old | 1.05 (1.03 to 1.16) | 0.98 (0.95 to 0.99) | +2.1 (+1.0 to +5.6) | +3.9 (+2.2 to +9.4) |
| BLACK | mid | 5 | new | 1.18 (1.12 to 1.28) | 1.08 (1.07 to 1.11) | -11.4 (-12.3 to -8.3) | +3.2 (+1.4 to +8.7) |
| BLACK | near | 8 | old | 1.00 (0.97 to 1.09) | 1.01 (0.99 to 1.02) | -2.6 (-5.1 to +2.4) | -1.3 (-3.3 to +6.5) |
| BLACK | near | 8 | new | 1.02 (0.99 to 1.15) | 1.04 (1.02 to 1.07) | -7.2 (-12.6 to -6.5) | -1.5 (-3.8 to +5.8) |
| WOOD | far | 18 | old | 0.94 (0.91 to 0.97) | 0.90 (0.89 to 0.92) | +8.8 (+7.4 to +10.2) | +1.5 (+1.0 to +2.1) |
| WOOD | far | 18 | new | 1.10 (1.06 to 1.14) | 1.07 (1.05 to 1.09) | -6.1 (-7.7 to -4.5) | +0.9 (+0.3 to +1.4) |
| WOOD | mid | 54 | old | 0.95 (0.93 to 0.99) | 0.95 (0.90 to 0.97) | +7.6 (+5.7 to +13.9) | -0.3 (-1.6 to +5.4) |
| WOOD | mid | 54 | new | 1.00 (0.99 to 1.07) | 1.02 (0.98 to 1.03) | -3.1 (-4.5 to +2.6) | -1.1 (-2.4 to +4.6) |
| WOOD | near | 54 | old | 0.99 (0.94 to 1.15) | 0.98 (0.96 to 0.99) | +3.7 (+1.1 to +9.4) | +1.2 (-4.8 to +11.1) |
| WOOD | near | 54 | new | 1.04 (0.95 to 1.22) | 1.02 (0.98 to 1.07) | -2.9 (-10.7 to +5.4) | +0.6 (-5.3 to +11.0) |

## Rule (c): the eval table, scenario rows that differ between the cameras

Adopted color model, `DetConfig()`, v2 rule, HOME leave-one-scene-out. Full table: `eval_new_vs_old/report.md` (candidate = new camera, baseline = old).

| set | scenario | barrels | found, old | found, new | false, old | false, new | in the rule |
|---|---|---|---|---|---|---|---|
| HOME | cluster | 8 | 6 | 6 | 0 | 1 | yes |
| HOME | occl | 4 | 4 | 3 | 0 | 0 | yes |
| DAVE* | snap | 34 | 12 | 12 | 2 | 3 | report only |

Subtotals:

| set | barrels | found, old | found, new | false, old | false, new | boxes on negative frames, old | new | score, old | new |
|---|---|---|---|---|---|---|---|---|---|
| HOME | 29 | 27 | 26 | 0 | 1 | 0 | 0 | 0.97 | 0.93 |
| CAMPUS | 35 | 34 | 34 | 0 | 0 | 0 | 0 | 0.99 | 0.99 |
| 4A8B_lampcool1_wood | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 |
| 4A8B_lampcool3_wood | 21 | 2 | 2 | 0 | 0 | 0 | 0 | 0.17 | 0.17 |
| 4A8B_lampcool6_wood | 21 | 2 | 2 | 2 | 2 | 0 | 0 | 0.16 | 0.16 |
| 4A8B_lampmid1_wood | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 |
| 4A8B_lampmid3_wood | 21 | 1 | 1 | 1 | 1 | 0 | 0 | 0.08 | 0.08 |
| 4A8B_lampmid6_wood | 21 | 1 | 1 | 0 | 0 | 0 | 0 | 0.08 | 0.08 |
| 4A8B_lampwarm1_wood | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 |
| 4A8B_lampwarm3_wood | 21 | 1 | 1 | 0 | 0 | 0 | 0 | 0.08 | 0.08 |
| 4A8B_lampwarm6_wood | 21 | 0 | 0 | 1 | 1 | 0 | 0 | 0.00 | 0.00 |
| 4A8B_window_black | 26 | 3 | 3 | 1 | 1 | 0 | 0 | 0.16 | 0.16 |
| DAVE* | 34 | 12 | 12 | 2 | 3 | 0 | 0 | 0.49 | 0.48 |

Negative frames with a box under either camera: none.

Frames where the two cameras differ (found / false):

| set | frame | barrels | found, old | new | false, old | new |
|---|---|---|---|---|---|---|
| HOME | 4A8B_window_light_cluster_01 | 4 | 2 | 2 | 0 | 1 |
| HOME | 4A8B_window_light_occl_01 | 2 | 2 | 1 | 0 | 0 |
| DAVE* | DAVE_office_speckle_snap_03 | 2 | 0 | 0 | 1 | 2 |

## Report only

### Bottom from the width against bottom from the top row

Median of the absolute error in px (how far the inferred bottom is from the drawn one, either way).

| set | range | boxes | from top, old | from width, old | from top, new | from width, new |
|---|---|---|---|---|---|---|
| HOME | all | 19 | 4.4 | 1.7 | 8.1 | 1.5 |
| HOME | far | 3 | 7.4 | 2.6 | 8.5 | 2.1 |
| HOME | mid | 12 | 4.7 | 1.4 | 7.9 | 1.1 |
| HOME | near | 4 | 0.9 | 1.5 | 7.7 | 1.6 |
| CAMPUS | all | 32 | 5.8 | 2.3 | 7.6 | 1.7 |
| CAMPUS | far | 2 | 10.2 | 0.5 | 4.5 | 0.5 |
| CAMPUS | mid | 14 | 6.6 | 1.4 | 6.1 | 1.4 |
| CAMPUS | near | 16 | 4.4 | 4.0 | 9.5 | 3.7 |
| BLACK | all | 14 | 3.8 | 2.7 | 8.3 | 2.4 |
| BLACK | far | 1 | 9.1 | 0.7 | 6.3 | 0.1 |
| BLACK | mid | 5 | 2.1 | 3.9 | 11.4 | 3.2 |
| BLACK | near | 8 | 3.8 | 2.4 | 7.2 | 2.4 |
| WOOD | all | 126 | 7.1 | 1.6 | 4.4 | 1.9 |
| WOOD | far | 18 | 8.8 | 1.5 | 6.1 | 0.9 |
| WOOD | mid | 54 | 7.6 | 1.2 | 3.1 | 1.9 |
| WOOD | near | 54 | 3.7 | 3.4 | 5.0 | 3.8 |

### Width against the exact outline instead of the shortcut `f × 25.5 / distance`

| set | range | boxes | shortcut, old | exact, old | shortcut, new | exact, new |
|---|---|---|---|---|---|---|
| HOME | all | 19 | 0.99 | 0.98 | 1.07 | 1.06 |
| HOME | far | 3 | 0.93 | 0.89 | 1.12 | 1.08 |
| HOME | mid | 12 | 0.99 | 0.97 | 1.08 | 1.05 |
| HOME | near | 4 | 1.02 | 1.04 | 1.04 | 1.05 |
| CAMPUS | all | 32 | 0.98 | 0.98 | 1.05 | 1.04 |
| CAMPUS | far | 2 | 0.90 | 0.87 | 1.05 | 1.01 |
| CAMPUS | mid | 14 | 0.95 | 0.93 | 1.05 | 1.02 |
| CAMPUS | near | 16 | 1.03 | 1.04 | 1.08 | 1.08 |
| BLACK | all | 14 | 1.03 | 1.03 | 1.09 | 1.08 |
| BLACK | far | 1 | 0.91 | 0.88 | 1.09 | 1.05 |
| BLACK | mid | 5 | 1.05 | 1.02 | 1.18 | 1.14 |
| BLACK | near | 8 | 1.00 | 1.04 | 1.02 | 1.04 |
| WOOD | all | 126 | 0.95 | 0.95 | 1.02 | 1.01 |
| WOOD | far | 18 | 0.94 | 0.91 | 1.10 | 1.06 |
| WOOD | mid | 54 | 0.95 | 0.94 | 1.00 | 0.99 |
| WOOD | near | 54 | 0.99 | 0.99 | 1.04 | 1.03 |

### Bottom-from-top error against the box's column (far and mid boxes)

A camera rolled about its axis would put barrels on one side of the frame lower than on the other; the error would then change with the column. Slope in px of error per 100 px of column, with its 1-sigma.

| set | boxes | columns covered | slope, old | slope, new |
|---|---|---|---|---|
| HOME | 15 | -106 to +152 | -0.4 ± 1.0 | -0.5 ± 1.1 |
| CAMPUS | 16 | -122 to +300 | -0.2 ± 0.6 | +1.1 ± 0.6 |
| BLACK | 6 | -104 to +216 | -0.6 ± 1.3 | -0.6 ± 1.0 |
| WOOD | 72 | -201 to +74 | -1.2 ± 0.3 | -2.9 ± 0.3 |
