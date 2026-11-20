# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → `pin` → `pin+thin`, of n scenes**. Before = the detector at the start of this work (`base`). `pin` = a partly seen stripe that no side reason places is placed by the barrel's outline, when the outline knows where the barrel is (`pin_outline`). `pin+thin` = also: a thin piece of stripe is a barrel when it is a full slice and the outline places it (`pin_thin`).

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 of 100 | 99 → 100 → 100 of 100 | 3 → 3 → 80 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 of 100 | 82 → 94 → 94 of 100 | 0 → 3 → 80 of 100 |
| a slanted edge, one side | 200 → 200 → 200 of 200 | 154 → 148 → 148 of 200 | 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 of 50 | 49 → 49 → 49 of 50 | 0 → 0 → 0 of 50 |
| hidden from above | 50 → 50 → 50 of 50 | 2 → 2 → 2 of 50 | 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 49 → 49 of 50 | 1 → 1 → 1 of 50 | 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 of 50 | 9 → 12 → 47 of 50 | 0 → 0 → 6 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 of 100 | 94 → 94 → 94 of 100 | 49 → 49 → 55 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 of 100 | 92 → 92 → 92 of 100 | 77 → 77 → 79 of 100 |
| a barrel of the OTHER color, straight in front | 39 → 39 → 39 of 47 | 38 → 38 → 38 of 48 | 17 → 17 → 17 of 49 |
| a barrel of the SAME color, beside it | 81 → 81 → 81 of 100 | 36 → 36 → 36 of 100 | 16 → 16 → 17 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 91 → 91 of 100 | 85 → 85 → 85 of 100 | 26 → 25 → 37 of 100 |
| a barrel of the SAME color, straight in front | 44 → 44 → 44 of 47 | 29 → 29 → 29 of 48 | 2 → 2 → 2 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 of 100 | 99 → 99 → 99 of 100 | 5 → 5 → 53 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 of 100 | 99 → 99 → 99 of 100 | 3 → 3 → 9 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 of 100 | 99 → 100 → 100 of 100 | 3 → 3 → 80 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 of 100 | 86 → 98 → 98 of 100 | 0 → 3 → 80 of 100 |
| a slanted edge, one side | 200 → 200 → 200 of 200 | 156 → 160 → 160 of 200 | 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 of 50 | 50 → 50 → 50 of 50 | 0 → 0 → 0 of 50 |
| hidden from above | 50 → 50 → 50 of 50 | 2 → 2 → 2 of 50 | 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 50 → 50 of 50 | 1 → 1 → 1 of 50 | 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 of 50 | 9 → 12 → 47 of 50 | 0 → 0 → 6 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 of 100 | 96 → 96 → 96 of 100 | 60 → 60 → 66 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 of 100 | 92 → 92 → 92 of 100 | 90 → 90 → 92 of 100 |
| a barrel of the OTHER color, straight in front | 41 → 41 → 41 of 47 | 39 → 39 → 39 of 48 | 28 → 28 → 28 of 49 |
| a barrel of the SAME color, beside it | 88 → 88 → 88 of 100 | 49 → 49 → 49 of 100 | 31 → 31 → 32 of 100 |
| a barrel of the SAME color, beside it and lower | 98 → 98 → 98 of 100 | 89 → 89 → 89 of 100 | 32 → 31 → 43 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 → 45 of 47 | 37 → 37 → 37 of 48 | 7 → 7 → 7 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 of 100 | 99 → 99 → 99 of 100 | 5 → 5 → 53 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 of 100 | 99 → 99 → 99 of 100 | 4 → 4 → 10 of 100 |

All 3888 scenes together: found 2417 → 2429 → 2699; right place 2532 → 2554 → 2824; boxes drawn where no barrel is 45 → 45 → 48; right-place boxes too small / about right / too big: 299 / 2129 / 104 → 301 / 2149 / 104 → 309 / 2398 / 117.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
