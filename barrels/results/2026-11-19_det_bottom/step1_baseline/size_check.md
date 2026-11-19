# Expected barrel size against the hand-drawn boxes

Camera `AIM_4A8B6118_BOXFIT` (f 400, tilt 22.25, horizon row 76). Train frames only. Boxes flagged occluded, truncated, held or bottom_estimated, and boxes touching the frame, are left out.
Ratio = hand-drawn size / the size the camera model expects for a barrel whose bottom edge is at the box's bottom row (what `g` in the box tool draws). Median (10th to 90th percentile).
`bottom from top` = the bottom row the detector predicts from the box's top row, minus the drawn bottom row, in px (+ = predicted lower).

| set | boxes | width ratio | height ratio | bottom from top, px |
|---|---|---|---|---|
| HOME | 19 | 0.99 (0.93 to 1.03) | 0.97 (0.93 to 1.00) | 4.40 (-0.60 to 8.44) |
| CAMPUS | 32 | 0.98 (0.92 to 1.10) | 0.97 (0.89 to 1.01) | 5.35 (-3.05 to 11.54) |
| BLACK | 14 | 1.03 (0.96 to 1.17) | 0.99 (0.95 to 1.02) | 1.10 (-4.92 to 5.58) |
| WOOD bright | 84 | 0.95 (0.93 to 1.09) | 0.96 (0.90 to 0.99) | 7.05 (3.30 to 10.20) |
| WOOD dark | 42 | 0.96 (0.93 to 1.09) | 0.96 (0.90 to 0.99) | 7.05 (3.30 to 10.20) |
| wood, all 9 lamp settings | 126 | 0.95 (0.93 to 1.09) | 0.96 (0.90 to 0.99) | 7.05 (3.30 to 10.20) |

By distance (expected width: far under 35 px, mid 35 to 60, near over 60):

| set | range | boxes | width ratio | height ratio | bottom from top, px |
|---|---|---|---|---|---|
| HOME | far | 3 | 0.96 (0.93 to 1.06) | 0.91 (0.86 to 0.93) | 7.40 (5.80 to 11.16) |
| HOME | mid | 12 | 0.99 (0.92 to 1.03) | 0.97 (0.94 to 0.98) | 4.50 (2.82 to 8.27) |
| HOME | near | 4 | 1.02 (1.01 to 1.03) | 1.00 (1.00 to 1.02) | -0.90 (-3.50 to -0.40) |
| CAMPUS | mid | 17 | 0.95 (0.91 to 1.04) | 0.95 (0.90 to 0.98) | 6.60 (2.22 to 9.98) |
| CAMPUS | near | 15 | 1.02 (0.94 to 1.28) | 1.00 (0.87 to 1.02) | 0.70 (-5.10 to 101.68) |
| BLACK | far | 1 | 0.91 (0.91 to 0.91) | 0.89 (0.89 to 0.89) | 9.10 (9.10 to 9.10) |
| BLACK | mid | 6 | 1.06 (1.03 to 1.21) | 0.98 (0.95 to 0.99) | 3.25 (1.10 to 5.50) |
| BLACK | near | 7 | 1.00 (0.97 to 1.05) | 1.01 (1.00 to 1.02) | -3.30 (-5.10 to -0.38) |
| WOOD | mid | 54 | 0.96 (0.92 to 1.15) | 0.93 (0.89 to 0.99) | 7.65 (1.10 to 13.90) |
| WOOD | near | 72 | 0.95 (0.94 to 1.09) | 0.96 (0.94 to 0.99) | 5.70 (3.30 to 10.20) |
