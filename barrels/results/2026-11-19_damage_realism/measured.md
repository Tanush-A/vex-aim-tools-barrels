# Measured: the damage real segmentation has, next to the simulated levels

git cdd0ce1; train frames only; adopted color model `2026-11-09_hs_candidate`. Barrels measured: no flag, free-standing (the occlusion scorecard's rule). W, H = the hand-drawn box.

## 1. With the hand-made masks (HOME): the same units as `degrade.py`

12 barrels of the 16 HOME train frames. Real columns: median / 90th percentile / worst barrel. Simulated columns: the level's setting, then what the same instrument reads back from the simulated masks (median / 90th percentile; 5 seeds).

| kind of damage | HOME, stored model | HOME, leave-one-scene-out | light | medium | heavy | white tables, typical | white tables, bad day | white tables, worst seen |
|---|---|---|---|---|---|---|---|---|
| barrel pixels not painted, share | 0.14 / 0.20 / 0.28 | 0.14 / 0.20 / 0.28 | 0.27 / 0.42 | 0.47 / 0.63 | 0.75 / 0.88 | 0.17 / 0.29 | 0.24 / 0.39 | 0.48 / 0.62 |
| edges eaten at the outline, px | 0.8 / 1.1 / 1.2 | 0.7 / 1.1 / 1.2 | **1** → 1.0 / 1.0 | **1** → 1.0 / 1.1 | **2** → 2.4 / 2.5 | **1** → 1.0 / 1.0 | **1** → 1.0 / 1.0 | **1** → 1.0 / 1.1 |
| edges eaten at the body / stripe seam, px | 0.8 / 1.0 / 1.1 | 0.8 / 1.1 / 1.2 | **1** → 1.0 / 1.0 | **1** → 1.1 / 1.2 | **2** → 2.6 / 2.8 | **1** → 1.0 / 1.0 | **1** → 1.0 / 1.1 | **1** → 1.2 / 1.3 |
| random dropout inside, share | 0.000 / 0.004 / 0.014 | 0.000 / 0.005 / 0.006 | **0.02** → 0.020 / 0.027 | **0.05** → 0.048 / 0.057 | **0.1** → 0.125 / 0.304 | **0** → 0.000 / 0.000 | **0.005** → 0.005 / 0.008 | **0.014** → 0.013 / 0.020 |
| largest hole on the upper body: width / W | 0.00 / 0.16 / 0.17 | 0.00 / 0.16 / 0.18 | **0.3** → 0.37 / 0.38 | **0.5** → 0.57 / 0.64 | **0.7** → 0.74 / 0.83 | **0** → 0.00 / 0.00 | **0.16** → 0.22 / 0.25 | **0.41** → 0.54 / 0.68 |
| ... its height / H | 0.00 / 0.09 / 0.21 | 0.00 / 0.09 / 0.30 | **0.2** → 0.27 / 0.28 | **0.3** → 0.39 / 0.43 | **0.4** → 0.33 / 0.43 | **0** → 0.00 / 0.00 | **0.09** → 0.13 / 0.17 | **0.3** → 0.39 / 0.45 |
| widest hole across the stripe, / W | 0.00 / 0.05 / 0.40 | 0.00 / 0.06 / 0.40 | **0** → 0.00 / 0.00 | **0.15** → 0.22 / 0.27 | **0.3** → 0.35 / 0.54 | **0** → 0.00 / 0.00 | **0.06** → 0.12 / 0.17 | **0.4** → 0.46 / 0.52 |
| breaks in the stripe (count) | 0 / 0 / 0 | 0 / 0 / 0 | **0** → 0 / 0 | **1** → 1 / 2 | **2** → 1 / 2 | **0** → 0 / 0 | **0** → 1 / 1 | **1** → 1 / 2 |
| widest break in the stripe, / W | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | **0** → 0.00 / 0.00 | **0.06** → 0.18 / 0.24 | **0.08** → 0.18 / 0.45 | **0** → 0.00 / 0.00 | **0** → 0.11 / 0.17 | **0.03** → 0.36 / 0.50 |
| stripe unpainted at its two ends, / W | 0.02 / 0.07 / 0.08 | 0.02 / 0.07 / 0.08 | 0.04 / 0.07 | 0.06 / 0.25 | 0.41 / 0.71 | 0.04 / 0.07 | 0.05 / 0.13 | 0.05 / 0.43 |
| painted stripe thickness / hand-made (low = worse) | 0.87 / 0.71 / 0.62 | 0.83 / 0.71 / 0.62 | 0.82 / 0.71 | 0.75 / 0.67 | 0.55 / 0.33 | 0.82 / 0.71 | 0.82 / 0.71 | 0.79 / 0.67 |
| paint spilled beside the barrel, / its area | 0.02 / 0.07 / 0.24 | 0.03 / 0.10 / 0.24 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| barrels with a hole on the upper body | 3 of 12 | 3 of 12 | 60 of 60 | 60 of 60 | 60 of 60 | 0 of 60 | 60 of 60 | 60 of 60 |
| barrels with a hole across the stripe | 2 of 12 | 4 of 12 | 0 of 60 | 60 of 60 | 45 of 60 | 0 of 60 | 57 of 60 | 60 of 60 |
| barrels whose stripe is in one piece | 12 of 12 | 12 of 12 | 60 of 60 | 5 of 60 | 19 of 60 | 60 of 60 | 11 of 60 | 5 of 60 |
| barrels whose stripe is not painted at all | 0 of 12 | 0 of 12 | 0 of 60 | 0 of 60 | 0 of 60 | 0 of 60 | 0 of 60 | 0 of 60 |

Where the largest upper-body hole sits (HOME, leave-one-scene-out; centre as a share of the box, 0 = left / top): close_01 orange 0.18 x 0.30 at (0.83, 0.28); cluster_02 orange 0.07 x 0.06 at (0.94, 0.32); far_02 blue 0.17 x 0.09 at (0.14, 0.41).

## 2. With the hand-drawn boxes only (every set): comparable between the rows of THIS table

No hand mask is needed, so CAMPUS, the black table and the wood table can be measured. The first row is the zero point: the hand-made masks read with this instrument (a barrel is not a rectangle, so the core is not all paint). Median / 90th percentile / worst (for the 'low = worse' columns: median / 10th percentile / lowest).

| set | barrels | box core painted, share (low = worse) | upper core painted body color (low = worse) | stripe: first to last painted column / W (low = worse) | breaks in the stripe (count) | widest break in the stripe, / W | largest hole in the upper core: width / W | ... its height / H | widest hole across the middle rows, / W | stripe in one piece | no stripe paint |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HOME hand masks (no damage) | 12 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 0.98 / 0.86 | 0 / 0 / 0 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 12 of 12 | 0 of 12 |
| simulated: light | 60 | 0.73 / 0.64 / 0.63 | 0.43 / 0.41 / 0.37 | 0.94 / 0.87 / 0.80 | 0 / 0 / 0 | 0.00 / 0.00 / 0.00 | 0.37 / 0.38 / 0.38 | 0.24 / 0.27 / 0.34 | 0.00 / 0.05 / 0.38 | 60 of 60 | 0 of 60 |
| simulated: medium | 60 | 0.50 / 0.38 / 0.32 | 0.18 / 0.10 / 0.01 | 0.93 / 0.74 / 0.46 | 1 / 2 / 3 | 0.18 / 0.24 / 0.37 | 0.52 / 0.59 / 0.61 | 0.65 / 0.68 / 0.70 | 0.52 / 0.59 / 0.61 | 5 of 60 | 0 of 60 |
| simulated: heavy | 60 | 0.24 / 0.16 / 0.10 | 0.00 / 0.00 / 0.00 | 0.59 / 0.24 / 0.07 | 1 / 2 / 3 | 0.18 / 0.45 / 0.62 | 0.59 / 0.61 / 0.62 | 0.61 / 0.69 / 0.70 | 0.60 / 0.61 / 0.62 | 19 of 60 | 0 of 60 |
| simulated: white tables, typical | 60 | 0.90 / 0.82 / 0.82 | 1.00 / 1.00 / 0.99 | 0.94 / 0.87 / 0.80 | 0 / 0 / 0 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.00 / 0.03 / 0.05 | 60 of 60 | 0 of 60 |
| simulated: white tables, bad day | 60 | 0.78 / 0.67 / 0.64 | 0.78 / 0.69 / 0.67 | 0.94 / 0.80 / 0.70 | 1 / 1 / 1 | 0.11 / 0.17 / 0.17 | 0.22 / 0.26 / 0.38 | 0.13 / 0.20 / 0.59 | 0.12 / 0.24 / 0.38 | 11 of 60 | 0 of 60 |
| simulated: white tables, worst seen | 60 | 0.46 / 0.35 / 0.30 | 0.28 / 0.19 / 0.11 | 0.94 / 0.56 / 0.40 | 1 / 2 / 3 | 0.36 / 0.50 / 0.57 | 0.50 / 0.60 / 0.61 | 0.64 / 0.67 / 0.70 | 0.52 / 0.60 / 0.61 | 5 of 60 | 0 of 60 |
| HOME, stored model | 12 | 0.93 / 0.88 / 0.87 | 1.00 / 1.00 / 0.96 | 0.96 / 0.93 / 0.91 | 0 / 0 / 0 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.05 | 0.00 / 0.00 / 0.10 | 0.00 / 0.04 / 0.12 | 12 of 12 | 0 of 12 |
| HOME, leave-one-scene-out | 12 | 0.93 / 0.87 / 0.87 | 1.00 / 1.00 / 0.95 | 0.96 / 0.93 / 0.91 | 0 / 0 / 0 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.05 | 0.00 / 0.00 / 0.28 | 0.00 / 0.04 / 0.13 | 12 of 12 | 0 of 12 |
| CAMPUS | 26 | 0.89 / 0.81 / 0.55 | 1.00 / 0.87 / 0.38 | 0.90 / 0.86 / 0.04 | 0 / 0 / 1 | 0.00 / 0.00 / 0.03 | 0.00 / 0.12 / 0.41 | 0.00 / 0.10 / 0.26 | 0.05 / 0.33 / 0.61 | 25 of 26 | 0 of 26 |
| BLACK table | 7 | 0.12 / 0.02 / 0.00 | 0.00 / 0.00 / 0.00 | 0.88 / 0.00 / 0.00 | 0 / 1 / 2 | 0.02 / 0.37 / 0.46 | 0.00 / 0.60 / 0.61 | 0.00 / 0.52 / 0.52 | 0.60 / 0.61 / 0.61 | 2 of 7 | 2 of 7 |
| WOOD cool lamp 3 | 12 | 0.34 / 0.17 / 0.08 | 0.30 / 0.04 / 0.00 | 0.46 / 0.00 / 0.00 | 0 / 2 / 2 | 0.00 / 0.19 / 0.27 | 0.27 / 0.59 / 0.61 | 0.12 / 0.32 / 0.51 | 0.59 / 0.62 / 0.62 | 6 of 12 | 2 of 12 |
| WOOD mid lamp 6 | 12 | 0.41 / 0.27 / 0.19 | 0.16 / 0.00 / 0.00 | 0.47 / 0.00 / 0.00 | 0 / 0 / 1 | 0.00 / 0.01 / 0.02 | 0.59 / 0.61 / 0.62 | 0.29 / 0.37 / 0.39 | 0.59 / 0.62 / 0.62 | 6 of 12 | 5 of 12 |
| WOOD warm lamp 6 | 12 | 0.45 / 0.30 / 0.26 | 0.19 / 0.00 / 0.00 | 0.45 / 0.00 / 0.00 | 0 / 0 / 0 | 0.00 / 0.00 / 0.00 | 0.59 / 0.61 / 0.62 | 0.28 / 0.34 / 0.36 | 0.59 / 0.61 / 0.62 | 6 of 12 | 6 of 12 |

## 3. Barrel-colored paint off the barrels, per frame

Groups of barrel-colored pixels more than 4 px outside every hand-drawn box (HOME: and where the hand mask says 'other'). A speck is a group under 20 px (the detector drops those); a blob is larger (an orange or blue thing that is not a barrel, a reflection). The simulation's specks are 4 or 9 px: light 5, medium 15, heavy 30 per frame. Median / 90th percentile / worst frame.

| set | frames | specks per frame | blobs per frame | largest group, px | median speck size, px |
|---|---|---|---|---|---|
| HOME, stored model | 16 | 1 / 13 / 32 | 0 / 4 / 8 | 4 / 352 / 953 | 3 |
| HOME, leave-one-scene-out | 16 | 6 / 16 / 37 | 1 / 6 / 15 | 40 / 674 / 942 | 4 |
| CAMPUS | 21 | 6 / 22 / 26 | 2 / 10 / 19 | 527 / 2298 / 2966 | 2 |
| BLACK table | 10 | 2 / 5 / 17 | 1 / 3 / 5 | 128 / 979 / 1004 | 2 |
| WOOD cool lamp 3 | 10 | 4 / 52 / 63 | 0 / 19 / 20 | 10 / 864 / 894 | 8 |
| WOOD mid lamp 6 | 10 | 48 / 172 / 345 | 10 / 34 / 65 | 223 / 2875 / 6039 | 4 |
| WOOD warm lamp 6 | 10 | 90 / 205 / 503 | 14 / 53 / 157 | 931 / 3223 / 8077 | 8 |

## 4. The levels the rule gives

From the 12 HOME barrels (leave-one-scene-out) and the specks of 37 HOME and CAMPUS frames. Unrounded: white tables, typical: top_hole_w 0, top_hole_h 0, stripe_hole_w 0, stripe_breaks 0, stripe_break_w 0, edge_outer_px 0.7259, edge_seam_px 0.7698, dropout 0, specks 6; white tables, bad day: top_hole_w 0.161, top_hole_h 0.0877, stripe_hole_w 0.0572, stripe_breaks 0, stripe_break_w 0, edge_outer_px 1.0522, edge_seam_px 1.1299, dropout 0.0052, specks 20.2.

- `white tables, typical`: `Damage(top_highlight=(0.0, 0.0), stripe_highlight=0.0, stripe_breaks=(0, 0.0), erode_px=1, dropout=0.0, speckle=6)`
- `white tables, bad day`: `Damage(top_highlight=(0.16, 0.09), stripe_highlight=0.06, stripe_breaks=(0, 0.0), erode_px=1, dropout=0.005, speckle=20)`

`degrade.REALISTIC` holds exactly these.
