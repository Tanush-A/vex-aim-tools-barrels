# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → `vertical_all` → `pin` → `pin+thin`, of n scenes**. Before = the detector at the start of this work (`stack`). Sanity run: each arm as its own experiment pinned it, on the merged code.

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 of 100 | 3 → 87 → 3 → 29 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 → 100 of 100 | 82 → 82 → 90 → 90 of 100 | 0 → 0 → 2 → 28 of 100 |
| a slanted edge, one side | 200 → 200 → 200 → 200 of 200 | 154 → 154 → 170 → 170 of 200 | 0 → 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 → 50 of 50 | 49 → 49 → 49 → 49 of 50 | 0 → 0 → 0 → 0 of 50 |
| hidden from above | 50 → 50 → 50 → 50 of 50 | 2 → 45 → 2 → 2 of 50 | 0 → 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 49 → 49 → 49 of 50 | 1 → 40 → 1 → 1 of 50 | 1 → 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 → 49 of 50 | 9 → 41 → 11 → 31 of 50 | 0 → 9 → 0 → 5 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 → 99 of 100 | 94 → 94 → 94 → 94 of 100 | 49 → 60 → 49 → 50 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 → 98 of 100 | 92 → 92 → 92 → 92 of 100 | 77 → 81 → 77 → 77 of 100 |
| a barrel of the OTHER color, straight in front | 39 → 40 → 39 → 39 of 47 | 38 → 38 → 38 → 38 of 48 | 17 → 22 → 17 → 17 of 49 |
| a barrel of the SAME color, beside it | 81 → 96 → 81 → 81 of 100 | 36 → 88 → 36 → 36 of 100 | 16 → 18 → 16 → 16 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 91 → 91 → 91 of 100 | 85 → 87 → 85 → 85 of 100 | 26 → 42 → 26 → 28 of 100 |
| a barrel of the SAME color, straight in front | 44 → 44 → 44 → 44 of 47 | 29 → 29 → 29 → 29 of 48 | 2 → 8 → 2 → 2 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 of 100 | 5 → 5 → 5 → 36 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 of 100 | 3 → 3 → 3 → 3 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 of 100 | 3 → 88 → 3 → 29 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 → 100 of 100 | 86 → 86 → 94 → 94 of 100 | 0 → 0 → 2 → 28 of 100 |
| a slanted edge, one side | 200 → 200 → 200 → 200 of 200 | 156 → 156 → 172 → 172 of 200 | 0 → 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 → 50 of 50 | 50 → 50 → 50 → 50 of 50 | 0 → 0 → 0 → 0 of 50 |
| hidden from above | 50 → 50 → 50 → 50 of 50 | 2 → 45 → 2 → 2 of 50 | 0 → 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 50 → 50 → 50 of 50 | 1 → 40 → 1 → 1 of 50 | 1 → 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 → 49 of 50 | 9 → 41 → 11 → 31 of 50 | 0 → 11 → 0 → 5 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 → 99 of 100 | 96 → 96 → 96 → 96 of 100 | 60 → 71 → 60 → 61 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 → 98 of 100 | 92 → 92 → 92 → 92 of 100 | 90 → 94 → 90 → 90 of 100 |
| a barrel of the OTHER color, straight in front | 41 → 42 → 41 → 41 of 47 | 39 → 39 → 39 → 39 of 48 | 28 → 35 → 28 → 28 of 49 |
| a barrel of the SAME color, beside it | 88 → 99 → 88 → 88 of 100 | 49 → 97 → 49 → 49 of 100 | 31 → 34 → 31 → 31 of 100 |
| a barrel of the SAME color, beside it and lower | 98 → 99 → 98 → 98 of 100 | 89 → 94 → 89 → 89 of 100 | 32 → 49 → 32 → 34 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 → 45 → 45 of 47 | 37 → 37 → 37 → 37 of 48 | 7 → 14 → 7 → 7 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 of 100 | 5 → 5 → 5 → 36 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 of 100 | 4 → 4 → 4 → 4 of 100 |

All 3888 scenes together: found 2417 → 2738 → 2445 → 2556; right place 2532 → 2857 → 2560 → 2671; boxes drawn where no barrel is 45 → 45 → 45 → 45; right-place boxes too small / about right / too big: 299 / 2129 / 104 → 344 / 2421 / 92 → 301 / 2157 / 102 → 308 / 2259 / 104.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
