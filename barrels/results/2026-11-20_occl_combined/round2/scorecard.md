# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → `stack` → `combined` → `reduced` → `reduced+thin` → `combined+thin` → `combined+cover`, of n scenes**. Before = the detector at the start of this work (`before`). `before` = the defaults of `origin/barrels` (none of the unmerged occlusion work); the arms after it are those of `experiments/2026-11-20_occl_combined/comb_arms.py`; which of them is the default is in `verdict.md`.

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 86 → 99 → 99 → 99 → 99 → 99 → 100 of 100 | 0 → 3 → 87 → 3 → 29 → 87 → 88 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 38 → 82 → 90 → 90 → 90 → 90 → 96 of 100 | 0 → 0 → 2 → 2 → 28 → 28 → 74 of 100 |
| a slanted edge, one side | 200 → 200 → 200 → 200 → 200 → 200 → 200 of 200 | 116 → 154 → 170 → 170 → 170 → 170 → 197 of 200 | 0 → 0 → 0 → 0 → 0 → 0 → 125 of 200 |
| both sides cut | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 49 → 49 → 49 → 49 → 49 → 49 → 49 of 50 | 0 → 0 → 0 → 0 → 0 → 0 → 44 of 50 |
| hidden from above | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 1 → 2 → 45 → 45 → 45 → 45 → 45 of 50 | 0 → 0 → 0 → 0 → 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 49 → 49 → 49 → 49 → 49 → 49 of 50 | 1 → 1 → 40 → 40 → 40 → 40 → 40 of 50 | 1 → 1 → 1 → 1 → 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 → 49 → 49 → 49 → 49 of 50 | 9 → 9 → 41 → 41 → 41 → 41 → 43 of 50 | 0 → 0 → 9 → 9 → 11 → 11 → 11 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 67 → 94 → 94 → 94 → 94 → 94 → 96 of 100 | 44 → 49 → 60 → 49 → 50 → 60 → 69 of 100 |
| a barrel of the OTHER color, beside it and lower | 93 → 98 → 98 → 98 → 98 → 98 → 98 of 100 | 81 → 92 → 92 → 92 → 92 → 92 → 92 of 100 | 69 → 77 → 81 → 77 → 77 → 81 → 84 of 100 |
| a barrel of the OTHER color, straight in front | 29 → 39 → 40 → 40 → 40 → 40 → 40 of 47 | 36 → 38 → 38 → 38 → 38 → 38 → 38 of 48 | 17 → 17 → 22 → 22 → 22 → 22 → 22 of 49 |
| a barrel of the SAME color, beside it | 80 → 81 → 96 → 96 → 96 → 96 → 96 of 100 | 32 → 36 → 88 → 88 → 88 → 88 → 88 of 100 | 15 → 16 → 18 → 17 → 17 → 18 → 24 of 100 |
| a barrel of the SAME color, beside it and lower | 88 → 91 → 91 → 91 → 91 → 91 → 91 of 100 | 60 → 85 → 87 → 87 → 87 → 87 → 87 of 100 | 1 → 26 → 42 → 27 → 29 → 44 → 68 of 100 |
| a barrel of the SAME color, straight in front | 45 → 44 → 44 → 44 → 44 → 44 → 44 of 47 | 25 → 29 → 29 → 29 → 29 → 29 → 29 of 48 | 1 → 2 → 8 → 8 → 8 → 8 → 8 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 85 → 99 → 99 → 99 → 99 → 99 → 100 of 100 | 2 → 5 → 5 → 5 → 36 → 36 → 90 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 85 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 0 → 3 → 3 → 3 → 3 → 3 → 88 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 86 → 99 → 99 → 99 → 99 → 99 → 100 of 100 | 0 → 3 → 88 → 3 → 29 → 88 → 89 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 62 → 86 → 94 → 94 → 94 → 94 → 100 of 100 | 0 → 0 → 2 → 2 → 28 → 28 → 88 of 100 |
| a slanted edge, one side | 200 → 200 → 200 → 200 → 200 → 200 → 200 of 200 | 116 → 156 → 172 → 172 → 172 → 172 → 200 of 200 | 0 → 0 → 0 → 0 → 0 → 0 → 144 of 200 |
| both sides cut | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 0 → 0 → 0 → 0 → 0 → 0 → 49 of 50 |
| hidden from above | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 1 → 2 → 45 → 45 → 45 → 45 → 45 of 50 | 0 → 0 → 0 → 0 → 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 1 → 1 → 40 → 40 → 40 → 40 → 40 of 50 | 1 → 1 → 1 → 1 → 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 → 49 → 49 → 49 → 49 of 50 | 9 → 9 → 41 → 41 → 41 → 41 → 48 of 50 | 0 → 0 → 11 → 11 → 13 → 13 → 14 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 77 → 96 → 96 → 96 → 96 → 96 → 96 of 100 | 55 → 60 → 71 → 60 → 61 → 71 → 75 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 → 98 → 98 → 98 → 98 of 100 | 86 → 92 → 92 → 92 → 92 → 92 → 93 of 100 | 89 → 90 → 94 → 90 → 90 → 94 → 96 of 100 |
| a barrel of the OTHER color, straight in front | 41 → 41 → 42 → 42 → 42 → 42 → 42 of 47 | 38 → 39 → 39 → 39 → 39 → 39 → 39 of 48 | 28 → 28 → 35 → 35 → 35 → 35 → 35 of 49 |
| a barrel of the SAME color, beside it | 88 → 88 → 99 → 99 → 99 → 99 → 99 of 100 | 46 → 49 → 97 → 97 → 97 → 97 → 97 of 100 | 30 → 31 → 34 → 33 → 33 → 34 → 38 of 100 |
| a barrel of the SAME color, beside it and lower | 98 → 98 → 99 → 99 → 99 → 99 → 99 of 100 | 68 → 89 → 94 → 94 → 94 → 94 → 94 of 100 | 3 → 32 → 49 → 33 → 35 → 51 → 76 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 → 45 → 45 → 45 → 45 → 45 of 47 | 29 → 37 → 37 → 37 → 37 → 37 → 36 of 48 | 3 → 7 → 14 → 14 → 14 → 14 → 14 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 85 → 99 → 99 → 99 → 99 → 99 → 100 of 100 | 2 → 5 → 5 → 5 → 36 → 36 → 91 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 85 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 1 → 4 → 4 → 4 → 4 → 4 → 91 of 100 |

All 3888 scenes together: found 2153 → 2417 → 2764 → 2649 → 2737 → 2825 → 3261; right place 2318 → 2532 → 2883 → 2766 → 2854 → 2944 → 3419; boxes drawn where no barrel is 88 → 45 → 45 → 45 → 45 → 45 → 58; right-place boxes too small / about right / too big: 157 / 1998 / 163 → 299 / 2129 / 104 → 346 / 2447 / 90 → 318 / 2365 / 83 → 324 / 2445 / 85 → 347 / 2507 / 90 → 362 / 2421 / 636.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
