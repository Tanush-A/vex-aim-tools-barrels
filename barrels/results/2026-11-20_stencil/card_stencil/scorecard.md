# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → `stencil`, of n scenes**. Before = the detector at the start of this work (`rules`). `rules` = the rule detector as it is on this branch. `stencil`: see experiments/2026-11-20_stencil/stencil_arms.py.

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 99 of 100 | 99 → 97 of 100 | 3 → 4 of 100 |
| a straight upright edge, one side | 100 → 99 of 100 | 82 → 86 of 100 | 0 → 0 of 100 |
| a slanted edge, one side | 200 → 198 of 200 | 154 → 142 of 200 | 0 → 0 of 200 |
| both sides cut | 50 → 50 of 50 | 49 → 49 of 50 | 0 → 7 of 50 |
| hidden from above | 50 → 46 of 50 | 2 → 0 of 50 | 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 8 of 50 | 1 → 0 of 50 | 1 → 0 of 50 |
| a post across the middle | 49 → 49 of 50 | 9 → 27 of 50 | 0 → 0 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 of 100 | 94 → 93 of 100 | 49 → 11 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 99 of 100 | 92 → 91 of 100 | 77 → 13 of 100 |
| a barrel of the OTHER color, straight in front | 39 → 44 of 47 | 38 → 28 of 48 | 17 → 9 of 49 |
| a barrel of the SAME color, beside it | 81 → 99 of 100 | 36 → 83 of 100 | 16 → 8 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 99 of 100 | 85 → 96 of 100 | 26 → 18 of 100 |
| a barrel of the SAME color, straight in front | 44 → 45 of 47 | 29 → 28 of 48 | 2 → 13 of 49 |
| a plain block of the barrel's body color | 100 → 96 of 100 | 99 → 19 of 100 | 5 → 2 of 100 |
| a plain block of the barrel's stripe color | 100 → 98 of 100 | 99 → 81 of 100 | 3 → 0 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 99 of 100 | 99 → 97 of 100 | 3 → 4 of 100 |
| a straight upright edge, one side | 100 → 99 of 100 | 86 → 91 of 100 | 0 → 0 of 100 |
| a slanted edge, one side | 200 → 198 of 200 | 156 → 154 of 200 | 0 → 0 of 200 |
| both sides cut | 50 → 50 of 50 | 50 → 49 of 50 | 0 → 7 of 50 |
| hidden from above | 50 → 46 of 50 | 2 → 0 of 50 | 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 43 of 50 | 1 → 0 of 50 | 1 → 0 of 50 |
| a post across the middle | 49 → 49 of 50 | 9 → 28 of 50 | 0 → 0 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 of 100 | 96 → 94 of 100 | 60 → 11 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 99 of 100 | 92 → 94 of 100 | 90 → 26 of 100 |
| a barrel of the OTHER color, straight in front | 41 → 46 of 47 | 39 → 38 of 48 | 28 → 25 of 49 |
| a barrel of the SAME color, beside it | 88 → 99 of 100 | 49 → 84 of 100 | 31 → 17 of 100 |
| a barrel of the SAME color, beside it and lower | 98 → 99 of 100 | 89 → 96 of 100 | 32 → 30 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 of 47 | 37 → 38 of 48 | 7 → 29 of 49 |
| a plain block of the barrel's body color | 100 → 96 of 100 | 99 → 58 of 100 | 5 → 2 of 100 |
| a plain block of the barrel's stripe color | 100 → 98 of 100 | 99 → 84 of 100 | 4 → 0 of 100 |

All 3888 scenes together: found 2417 → 2233; right place 2532 → 2421; boxes drawn where no barrel is 45 → 10; right-place boxes too small / about right / too big: 299 / 2129 / 104 → 96 / 2298 / 27.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
