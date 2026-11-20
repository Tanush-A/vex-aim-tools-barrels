# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → `reduced+thin` → `before`, of n scenes**. Before = the detector at the start of this work (`stack`). `before` = the defaults of `origin/barrels` (none of the unmerged occlusion work); the arms after it are those of `experiments/2026-11-20_occl_combined/comb_arms.py`; which of them is the default is in `verdict.md`.

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 of 100 | 99 → 99 → 86 of 100 | 3 → 29 → 0 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 of 100 | 82 → 90 → 38 of 100 | 0 → 28 → 0 of 100 |
| a slanted edge, one side | 200 → 200 → 200 of 200 | 154 → 170 → 116 of 200 | 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 of 50 | 49 → 49 → 49 of 50 | 0 → 0 → 0 of 50 |
| hidden from above | 50 → 50 → 50 of 50 | 2 → 45 → 1 of 50 | 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 49 → 49 of 50 | 1 → 40 → 1 of 50 | 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 of 50 | 9 → 41 → 9 of 50 | 0 → 11 → 0 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 of 100 | 94 → 94 → 67 of 100 | 49 → 50 → 44 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 93 of 100 | 92 → 92 → 81 of 100 | 77 → 77 → 69 of 100 |
| a barrel of the OTHER color, straight in front | 39 → 40 → 29 of 47 | 38 → 38 → 36 of 48 | 17 → 22 → 17 of 49 |
| a barrel of the SAME color, beside it | 81 → 96 → 80 of 100 | 36 → 88 → 32 of 100 | 16 → 17 → 15 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 91 → 88 of 100 | 85 → 87 → 60 of 100 | 26 → 29 → 1 of 100 |
| a barrel of the SAME color, straight in front | 44 → 44 → 45 of 47 | 29 → 29 → 25 of 48 | 2 → 8 → 1 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 of 100 | 99 → 99 → 85 of 100 | 5 → 36 → 2 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 of 100 | 99 → 99 → 85 of 100 | 3 → 3 → 0 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 of 100 | 99 → 99 → 86 of 100 | 3 → 29 → 0 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 of 100 | 86 → 94 → 62 of 100 | 0 → 28 → 0 of 100 |
| a slanted edge, one side | 200 → 200 → 200 of 200 | 156 → 172 → 116 of 200 | 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 of 50 | 50 → 50 → 50 of 50 | 0 → 0 → 0 of 50 |
| hidden from above | 50 → 50 → 50 of 50 | 2 → 45 → 1 of 50 | 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 50 → 49 of 50 | 1 → 40 → 1 of 50 | 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 of 50 | 9 → 41 → 9 of 50 | 0 → 13 → 0 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 of 100 | 96 → 96 → 77 of 100 | 60 → 61 → 55 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 of 100 | 92 → 92 → 86 of 100 | 90 → 90 → 89 of 100 |
| a barrel of the OTHER color, straight in front | 41 → 42 → 41 of 47 | 39 → 39 → 38 of 48 | 28 → 35 → 28 of 49 |
| a barrel of the SAME color, beside it | 88 → 99 → 88 of 100 | 49 → 97 → 46 of 100 | 31 → 33 → 30 of 100 |
| a barrel of the SAME color, beside it and lower | 98 → 99 → 98 of 100 | 89 → 94 → 68 of 100 | 32 → 35 → 3 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 → 45 of 47 | 37 → 37 → 29 of 48 | 7 → 14 → 3 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 of 100 | 99 → 99 → 85 of 100 | 5 → 36 → 2 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 of 100 | 99 → 99 → 85 of 100 | 4 → 4 → 1 of 100 |

All 3888 scenes together: found 2417 → 2737 → 2153; right place 2532 → 2854 → 2318; boxes drawn where no barrel is 45 → 45 → 88; right-place boxes too small / about right / too big: 299 / 2129 / 104 → 324 / 2445 / 85 → 157 / 1998 / 163.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
