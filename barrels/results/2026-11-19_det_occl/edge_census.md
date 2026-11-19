# The top and bottom edges of the boxes drawn from a stripe (a census of the baseline; no acceptance number)

Counts are right / wrong / no truth: a box is `right` when it overlaps a true barrel of its color by half or more (IoU; the bottom is not asked here).

| set | boxes from a stripe | neither edge seen where the stripe predicts it | ... and the seen top ends against the other barrel color | seen bottom kept, table under it | seen bottom kept, the other barrel color under it |
|---|---|---|---|---|---|
| HOME (eval table) | 23 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 23 / 0 / 0 | 0 / 0 / 0 |
| CAMPUS | 32 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 32 / 0 / 0 | 0 / 0 / 0 |
| HOME hand masks, medium damage | 88 / 1 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 88 / 1 / 0 | 0 / 0 / 0 |
| HOME hand masks, heavy damage | 11 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 11 / 0 / 0 | 0 / 0 / 0 |
| scorecard: every kind without a barrel in front | 1378 / 4 / 0 | 0 / 1 / 0 | 0 / 0 / 0 | 1329 / 3 / 0 | 0 / 0 / 0 |
| scorecard: a barrel of the OTHER color, beside it | 493 / 8 / 0 | 2 / 4 / 0 | 0 / 0 / 0 | 457 / 1 / 0 | 15 / 3 / 0 |
| scorecard: a barrel of the OTHER color, beside it and lower | 515 / 2 / 0 | 8 / 2 / 0 | 0 / 0 / 0 | 437 / 0 / 0 | 39 / 0 / 0 |
| scorecard: a barrel of the OTHER color, straight in front | 183 / 23 / 0 | 5 / 19 / 0 | 1 / 18 / 0 | 115 / 1 / 0 | 23 / 3 / 0 |
| scorecard: a barrel of the SAME color, beside it | 387 / 18 / 0 | 6 / 4 / 0 | 0 / 0 / 0 | 371 / 10 / 0 | 0 / 4 / 0 |
| scorecard: a barrel of the SAME color, beside it and lower | 503 / 1 / 0 | 0 / 1 / 0 | 0 / 0 / 0 | 423 / 0 / 0 | 0 / 0 / 0 |
| scorecard: a barrel of the SAME color, straight in front | 210 / 14 / 0 | 16 / 2 / 0 | 0 / 0 / 0 | 115 / 2 / 0 | 1 / 9 / 0 |
| recording campus | 0 / 0 / 466 | 0 / 0 / 3 | 0 / 0 / 0 | 0 / 0 / 454 | 0 / 0 / 9 |
| recording black | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 1 | 0 / 0 / 0 |
| recording wood | 0 / 0 / 30 | 0 / 0 / 19 | 0 / 0 / 0 | 0 / 0 / 3 | 0 / 0 / 0 |
| recording data | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 1 | 0 / 0 / 0 |

Where a kept seen bottom has the other barrel color under it (right boxes): the seen bottom and the bottom the stripe's row predicts, minus the true bottom, px (median; 10th to 90th percentile; n):

| set | seen bottom | predicted bottom |
|---|---|---|
| scorecard: a barrel of the OTHER color, straight in front | -5.0 (-12.0 to +6.4; n 23) | -1.4 (-3.4 to +5.6; n 23) |
| scorecard: a barrel of the OTHER color, beside it and lower | +0.0 (-2.0 to +2.0; n 39) | -2.1 (-5.0 to +1.4; n 39) |
| scorecard: a barrel of the OTHER color, beside it | -2.0 (-13.0 to +0.0; n 15) | -7.1 (-12.2 to -1.7; n 15) |
| scorecard: a barrel of the SAME color, straight in front | +4.0 (+4.0 to +4.0; n 1) | +0.1 (+0.1 to +0.1; n 1) |
