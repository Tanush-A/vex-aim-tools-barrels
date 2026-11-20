# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → `reduced+thin+verify` → `reduced+thin+verify2`, of n scenes**. Before = the detector at the start of this work (`reduced+thin`). `before` = the defaults of `origin/barrels` (none of the unmerged occlusion work); the arms after it are those of `experiments/2026-11-20_occl_combined/comb_arms.py`; which of them is the default is in `verdict.md`.

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 of 100 | 99 → 98 → 98 of 100 | 29 → 21 → 21 of 100 |
| a straight upright edge, one side | 100 → 99 → 99 of 100 | 90 → 90 → 90 of 100 | 28 → 0 → 0 of 100 |
| a slanted edge, one side | 200 → 198 → 198 of 200 | 170 → 158 → 158 of 200 | 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 of 50 | 49 → 48 → 48 of 50 | 0 → 0 → 0 of 50 |
| hidden from above | 50 → 47 → 47 of 50 | 45 → 0 → 43 of 50 | 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 47 → 47 of 50 | 40 → 0 → 39 of 50 | 1 → 0 → 0 of 50 |
| a post across the middle | 49 → 49 → 49 of 50 | 41 → 33 → 33 of 50 | 11 → 0 → 0 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 of 100 | 94 → 88 → 88 of 100 | 50 → 15 → 15 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 97 → 97 of 100 | 92 → 91 → 91 of 100 | 77 → 45 → 45 of 100 |
| a barrel of the OTHER color, straight in front | 40 → 40 → 40 of 47 | 38 → 37 → 37 of 48 | 22 → 19 → 19 of 49 |
| a barrel of the SAME color, beside it | 96 → 95 → 95 of 100 | 88 → 87 → 87 of 100 | 17 → 16 → 16 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 91 → 91 of 100 | 87 → 85 → 85 of 100 | 29 → 21 → 21 of 100 |
| a barrel of the SAME color, straight in front | 44 → 42 → 42 of 47 | 29 → 28 → 28 of 48 | 8 → 8 → 8 of 49 |
| a plain block of the barrel's body color | 100 → 97 → 97 of 100 | 99 → 74 → 74 of 100 | 36 → 2 → 2 of 100 |
| a plain block of the barrel's stripe color | 100 → 99 → 99 of 100 | 99 → 91 → 91 of 100 | 3 → 0 → 0 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 of 100 | 99 → 98 → 98 of 100 | 29 → 21 → 21 of 100 |
| a straight upright edge, one side | 100 → 99 → 99 of 100 | 94 → 92 → 92 of 100 | 28 → 0 → 0 of 100 |
| a slanted edge, one side | 200 → 198 → 198 of 200 | 172 → 158 → 158 of 200 | 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 of 50 | 50 → 48 → 48 of 50 | 0 → 0 → 0 of 50 |
| hidden from above | 50 → 47 → 47 of 50 | 45 → 0 → 43 of 50 | 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 47 → 47 of 50 | 40 → 0 → 39 of 50 | 1 → 0 → 0 of 50 |
| a post across the middle | 49 → 49 → 49 of 50 | 41 → 33 → 33 of 50 | 13 → 0 → 0 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 of 100 | 96 → 89 → 89 of 100 | 61 → 16 → 16 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 97 → 97 of 100 | 92 → 91 → 91 of 100 | 90 → 48 → 48 of 100 |
| a barrel of the OTHER color, straight in front | 42 → 42 → 42 of 47 | 39 → 38 → 38 of 48 | 35 → 31 → 31 of 49 |
| a barrel of the SAME color, beside it | 99 → 98 → 98 of 100 | 97 → 96 → 96 of 100 | 33 → 30 → 30 of 100 |
| a barrel of the SAME color, beside it and lower | 99 → 99 → 99 of 100 | 94 → 92 → 92 of 100 | 35 → 21 → 21 of 100 |
| a barrel of the SAME color, straight in front | 45 → 43 → 43 of 47 | 37 → 33 → 33 of 48 | 14 → 13 → 13 of 49 |
| a plain block of the barrel's body color | 100 → 97 → 97 of 100 | 99 → 74 → 74 of 100 | 36 → 2 → 2 of 100 |
| a plain block of the barrel's stripe color | 100 → 99 → 99 of 100 | 99 → 91 → 91 of 100 | 4 → 0 → 0 of 100 |

All 3888 scenes together: found 2737 → 2405 → 2487; right place 2854 → 2479 → 2561; boxes drawn where no barrel is 45 → 8 → 8; right-place boxes too small / about right / too big: 324 / 2445 / 85 → 270 / 2138 / 71 → 270 / 2219 / 72.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
