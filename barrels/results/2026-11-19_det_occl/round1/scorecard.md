# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → after of n scenes**. Before = the detector at the start of this work (`base`); after = `all`.

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 of 100 | 99 → 100 of 100 | 3 → 91 of 100 |
| a straight upright edge, one side | 100 → 100 of 100 | 82 → 96 of 100 | 0 → 74 of 100 |
| a slanted edge, one side | 200 → 200 of 200 | 154 → 197 of 200 | 0 → 127 of 200 |
| both sides cut | 50 → 50 of 50 | 49 → 49 of 50 | 0 → 44 of 50 |
| hidden from above | 50 → 50 of 50 | 2 → 2 of 50 | 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 49 of 50 | 1 → 1 of 50 | 1 → 1 of 50 |
| a post across the middle | 49 → 49 of 50 | 9 → 43 of 50 | 0 → 1 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 of 100 | 94 → 95 of 100 | 49 → 69 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 of 100 | 92 → 91 of 100 | 77 → 83 of 100 |
| a barrel of the OTHER color, straight in front | 29 → 39 of 47 | 37 → 38 of 48 | 17 → 17 of 49 |
| a barrel of the SAME color, beside it | 81 → 96 of 100 | 36 → 89 of 100 | 16 → 32 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 91 of 100 | 85 → 90 of 100 | 26 → 77 of 100 |
| a barrel of the SAME color, straight in front | 44 → 44 of 47 | 25 → 29 of 48 | 1 → 1 of 49 |
| a plain block of the barrel's body color | 100 → 100 of 100 | 99 → 100 of 100 | 5 → 94 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 of 100 | 99 → 99 of 100 | 3 → 91 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 of 100 | 99 → 100 of 100 | 3 → 92 of 100 |
| a straight upright edge, one side | 100 → 100 of 100 | 86 → 100 of 100 | 0 → 89 of 100 |
| a slanted edge, one side | 200 → 200 of 200 | 156 → 200 of 200 | 0 → 146 of 200 |
| both sides cut | 50 → 50 of 50 | 50 → 50 of 50 | 0 → 49 of 50 |
| hidden from above | 50 → 50 of 50 | 2 → 2 of 50 | 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 50 of 50 | 1 → 1 of 50 | 1 → 1 of 50 |
| a post across the middle | 49 → 49 of 50 | 9 → 48 of 50 | 0 → 6 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 of 100 | 96 → 95 of 100 | 60 → 77 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 of 100 | 92 → 92 of 100 | 90 → 94 of 100 |
| a barrel of the OTHER color, straight in front | 41 → 41 of 47 | 39 → 39 of 48 | 28 → 28 of 49 |
| a barrel of the SAME color, beside it | 88 → 99 of 100 | 49 → 98 of 100 | 31 → 50 of 100 |
| a barrel of the SAME color, beside it and lower | 98 → 99 of 100 | 89 → 98 of 100 | 32 → 91 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 of 47 | 30 → 36 of 48 | 3 → 6 of 49 |
| a plain block of the barrel's body color | 100 → 100 of 100 | 99 → 100 of 100 | 5 → 95 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 of 100 | 99 → 99 of 100 | 4 → 94 of 100 |

All 3888 scenes together: found 2401 → 3186; right place 2521 → 3356; boxes drawn where no barrel is 63 → 300; right-place boxes too small / about right / too big: 305 / 2114 / 102 → 362 / 2088 / 906.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
