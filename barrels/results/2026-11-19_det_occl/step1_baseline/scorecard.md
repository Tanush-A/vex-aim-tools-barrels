# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **found of n scenes** (the baseline, before any fix). Before = the detector at the start of this work (`base`).

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 of 100 | 99 of 100 | 3 of 100 |
| a straight upright edge, one side | 100 of 100 | 82 of 100 | 0 of 100 |
| a slanted edge, one side | 200 of 200 | 154 of 200 | 0 of 200 |
| both sides cut | 50 of 50 | 49 of 50 | 0 of 50 |
| hidden from above | 50 of 50 | 2 of 50 | 0 of 50 |
| hidden from below (a low thing in front) | 49 of 50 | 1 of 50 | 1 of 50 |
| a post across the middle | 49 of 50 | 9 of 50 | 0 of 50 |
| a barrel of the OTHER color, beside it | 99 of 100 | 94 of 100 | 49 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 of 100 | 92 of 100 | 77 of 100 |
| a barrel of the OTHER color, straight in front | 29 of 47 | 37 of 48 | 17 of 49 |
| a barrel of the SAME color, beside it | 81 of 100 | 36 of 100 | 16 of 100 |
| a barrel of the SAME color, beside it and lower | 91 of 100 | 85 of 100 | 26 of 100 |
| a barrel of the SAME color, straight in front | 44 of 47 | 25 of 48 | 1 of 49 |
| a plain block of the barrel's body color | 100 of 100 | 99 of 100 | 5 of 100 |
| a plain block of the barrel's stripe color | 100 of 100 | 99 of 100 | 3 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 of 100 | 99 of 100 | 3 of 100 |
| a straight upright edge, one side | 100 of 100 | 86 of 100 | 0 of 100 |
| a slanted edge, one side | 200 of 200 | 156 of 200 | 0 of 200 |
| both sides cut | 50 of 50 | 50 of 50 | 0 of 50 |
| hidden from above | 50 of 50 | 2 of 50 | 0 of 50 |
| hidden from below (a low thing in front) | 50 of 50 | 1 of 50 | 1 of 50 |
| a post across the middle | 49 of 50 | 9 of 50 | 0 of 50 |
| a barrel of the OTHER color, beside it | 99 of 100 | 96 of 100 | 60 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 of 100 | 92 of 100 | 90 of 100 |
| a barrel of the OTHER color, straight in front | 41 of 47 | 39 of 48 | 28 of 49 |
| a barrel of the SAME color, beside it | 88 of 100 | 49 of 100 | 31 of 100 |
| a barrel of the SAME color, beside it and lower | 98 of 100 | 89 of 100 | 32 of 100 |
| a barrel of the SAME color, straight in front | 45 of 47 | 30 of 48 | 3 of 49 |
| a plain block of the barrel's body color | 100 of 100 | 99 of 100 | 5 of 100 |
| a plain block of the barrel's stripe color | 100 of 100 | 99 of 100 | 4 of 100 |

All 3888 scenes together: found 2401; right place 2521; boxes drawn where no barrel is 63; right-place boxes too small / about right / too big: 305 / 2114 / 102.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
