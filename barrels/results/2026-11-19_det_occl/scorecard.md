# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → `edge+cap` → `all`, of n scenes**. Before = the detector at the start of this work (`base`). `edge+cap` = what passed the pre-registered rule and is on by default (`edge_check`, `cap_same`). `all` = with the three switches that did not pass by the letter and are OFF (`slice_box`, `cover_unpinned`, `stripe_two`): what occlusion handling would be with them on.

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 of 100 | 99 → 99 → 100 of 100 | 3 → 3 → 87 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 of 100 | 82 → 82 → 96 of 100 | 0 → 0 → 73 of 100 |
| a slanted edge, one side | 200 → 200 → 200 of 200 | 154 → 154 → 197 of 200 | 0 → 0 → 125 of 200 |
| both sides cut | 50 → 50 → 50 of 50 | 49 → 49 → 49 of 50 | 0 → 0 → 44 of 50 |
| hidden from above | 50 → 50 → 50 of 50 | 2 → 2 → 2 of 50 | 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 49 → 49 of 50 | 1 → 1 → 1 of 50 | 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 of 50 | 9 → 9 → 43 of 50 | 0 → 0 → 1 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 of 100 | 94 → 94 → 96 of 100 | 49 → 49 → 69 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 of 100 | 92 → 92 → 92 of 100 | 77 → 77 → 84 of 100 |
| a barrel of the OTHER color, straight in front | 29 → 39 → 39 of 47 | 37 → 38 → 38 of 48 | 17 → 17 → 17 of 49 |
| a barrel of the SAME color, beside it | 81 → 81 → 96 of 100 | 36 → 36 → 88 of 100 | 16 → 16 → 24 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 91 → 91 of 100 | 85 → 85 → 87 of 100 | 26 → 26 → 68 of 100 |
| a barrel of the SAME color, straight in front | 44 → 44 → 44 of 47 | 25 → 29 → 29 of 48 | 1 → 2 → 2 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 of 100 | 99 → 99 → 100 of 100 | 5 → 5 → 90 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 of 100 | 99 → 99 → 99 of 100 | 3 → 3 → 88 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 of 100 | 99 → 99 → 100 of 100 | 3 → 3 → 88 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 of 100 | 86 → 86 → 100 of 100 | 0 → 0 → 88 of 100 |
| a slanted edge, one side | 200 → 200 → 200 of 200 | 156 → 156 → 200 of 200 | 0 → 0 → 144 of 200 |
| both sides cut | 50 → 50 → 50 of 50 | 50 → 50 → 50 of 50 | 0 → 0 → 49 of 50 |
| hidden from above | 50 → 50 → 50 of 50 | 2 → 2 → 2 of 50 | 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 50 → 50 of 50 | 1 → 1 → 1 of 50 | 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 of 50 | 9 → 9 → 48 of 50 | 0 → 0 → 6 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 of 100 | 96 → 96 → 96 of 100 | 60 → 60 → 75 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 of 100 | 92 → 92 → 93 of 100 | 90 → 90 → 96 of 100 |
| a barrel of the OTHER color, straight in front | 41 → 41 → 41 of 47 | 39 → 39 → 39 of 48 | 28 → 28 → 28 of 49 |
| a barrel of the SAME color, beside it | 88 → 88 → 99 of 100 | 49 → 49 → 97 of 100 | 31 → 31 → 38 of 100 |
| a barrel of the SAME color, beside it and lower | 98 → 98 → 99 of 100 | 89 → 89 → 94 of 100 | 32 → 32 → 75 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 → 45 of 47 | 30 → 37 → 36 of 48 | 3 → 7 → 7 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 of 100 | 99 → 99 → 100 of 100 | 5 → 5 → 91 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 of 100 | 99 → 99 → 99 of 100 | 4 → 4 → 91 of 100 |

All 3888 scenes together: found 2401 → 2417 → 3155; right place 2521 → 2532 → 3312; boxes drawn where no barrel is 63 → 45 → 58; right-place boxes too small / about right / too big: 305 / 2114 / 102 → 299 / 2129 / 104 → 357 / 2062 / 893.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
