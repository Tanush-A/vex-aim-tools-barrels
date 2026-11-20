# Occlusion scorecard

How often the detector boxes a barrel when part of it is hidden. 50 unhidden barrels of the train frames (12 from HOME hand masks, 12 from HOME color model, 26 from CAMPUS color model), each hidden by one thing at a time, by a measured amount. Each cell: **before → `bridge` → `frame` → `close` → `span` → `sliver` → `start+behind`, of n scenes**. Before = the detector at the start of this work (`start`). `before` = the defaults of `origin/barrels` (none of the unmerged occlusion work); the arms after it are those of `experiments/2026-11-20_occl_combined/comb_arms.py`; which of them is the default is in `verdict.md`.

## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 29 → 29 → 88 → 58 → 29 → 88 → 87 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 90 → 90 → 90 → 94 → 90 → 94 → 90 of 100 | 28 → 28 → 28 → 57 → 28 → 57 → 28 of 100 |
| a slanted edge, one side | 200 → 200 → 200 → 200 → 200 → 200 → 200 of 200 | 170 → 170 → 170 → 182 → 170 → 182 → 170 of 200 | 0 → 0 → 0 → 62 → 0 → 62 → 0 of 200 |
| both sides cut | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 49 → 49 → 49 → 49 → 49 → 49 → 49 of 50 | 0 → 0 → 0 → 0 → 0 → 0 → 0 of 50 |
| hidden from above | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 45 → 45 → 45 → 45 → 45 → 45 → 45 of 50 | 0 → 0 → 0 → 0 → 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 49 → 49 → 49 → 49 → 49 → 49 of 50 | 40 → 40 → 40 → 40 → 40 → 40 → 40 of 50 | 1 → 1 → 1 → 1 → 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 → 49 → 49 → 49 → 49 of 50 | 41 → 41 → 41 → 44 → 41 → 44 → 41 of 50 | 11 → 11 → 11 → 11 → 11 → 11 → 11 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 94 → 95 → 94 → 94 → 94 → 95 → 94 of 100 | 50 → 52 → 50 → 58 → 50 → 61 → 60 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 → 98 → 98 → 98 → 98 of 100 | 92 → 93 → 92 → 92 → 92 → 93 → 92 of 100 | 77 → 79 → 77 → 82 → 77 → 85 → 81 of 100 |
| a barrel of the OTHER color, straight in front | 40 → 40 → 40 → 40 → 40 → 40 → 40 of 47 | 38 → 38 → 38 → 38 → 38 → 38 → 38 of 48 | 22 → 22 → 22 → 22 → 22 → 22 → 22 of 49 |
| a barrel of the SAME color, beside it | 96 → 96 → 96 → 96 → 96 → 96 → 96 of 100 | 88 → 88 → 88 → 87 → 88 → 87 → 88 of 100 | 17 → 17 → 17 → 19 → 17 → 19 → 18 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 91 → 91 → 91 → 91 → 91 → 91 of 100 | 87 → 87 → 87 → 87 → 87 → 87 → 87 of 100 | 29 → 29 → 29 → 43 → 29 → 43 → 44 of 100 |
| a barrel of the SAME color, straight in front | 44 → 44 → 44 → 44 → 44 → 44 → 44 of 47 | 29 → 29 → 29 → 29 → 29 → 29 → 29 of 48 | 8 → 8 → 8 → 8 → 8 → 8 → 8 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 36 → 36 → 36 → 63 → 36 → 63 → 36 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 3 → 3 → 3 → 14 → 77 → 79 → 3 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 29 → 29 → 89 → 59 → 29 → 89 → 88 of 100 |
| a straight upright edge, one side | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 94 → 94 → 94 → 98 → 94 → 98 → 94 of 100 | 28 → 28 → 28 → 58 → 28 → 58 → 28 of 100 |
| a slanted edge, one side | 200 → 200 → 200 → 200 → 200 → 200 → 200 of 200 | 172 → 172 → 172 → 184 → 172 → 184 → 172 of 200 | 0 → 0 → 0 → 71 → 0 → 71 → 0 of 200 |
| both sides cut | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 0 → 0 → 0 → 0 → 0 → 0 → 0 of 50 |
| hidden from above | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 45 → 45 → 45 → 45 → 45 → 45 → 45 of 50 | 0 → 0 → 0 → 0 → 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 50 → 50 → 50 → 50 → 50 → 50 of 50 | 40 → 40 → 40 → 40 → 40 → 40 → 40 of 50 | 1 → 1 → 1 → 1 → 1 → 1 → 1 of 50 |
| a post across the middle | 49 → 49 → 49 → 49 → 49 → 49 → 49 of 50 | 41 → 41 → 41 → 45 → 41 → 45 → 41 of 50 | 13 → 13 → 13 → 13 → 13 → 13 → 13 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 96 → 96 → 96 → 96 → 96 → 96 → 96 of 100 | 61 → 61 → 61 → 68 → 61 → 68 → 71 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 98 → 98 → 98 → 98 → 98 → 98 of 100 | 92 → 93 → 92 → 92 → 92 → 93 → 92 of 100 | 90 → 90 → 90 → 95 → 90 → 95 → 94 of 100 |
| a barrel of the OTHER color, straight in front | 42 → 42 → 42 → 42 → 42 → 42 → 42 of 47 | 39 → 39 → 39 → 39 → 39 → 39 → 39 of 48 | 35 → 35 → 35 → 35 → 35 → 35 → 35 of 49 |
| a barrel of the SAME color, beside it | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 97 → 97 → 97 → 96 → 97 → 96 → 97 of 100 | 33 → 34 → 33 → 35 → 33 → 36 → 34 of 100 |
| a barrel of the SAME color, beside it and lower | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 94 → 94 → 94 → 94 → 94 → 94 → 94 of 100 | 35 → 35 → 35 → 49 → 35 → 49 → 51 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 → 45 → 45 → 45 → 45 → 45 of 47 | 37 → 37 → 37 → 37 → 37 → 37 → 37 of 48 | 14 → 14 → 14 → 14 → 14 → 14 → 14 of 49 |
| a plain block of the barrel's body color | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 36 → 36 → 36 → 64 → 36 → 64 → 36 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 → 100 → 100 → 100 → 100 → 100 of 100 | 99 → 99 → 99 → 99 → 99 → 99 → 99 of 100 | 4 → 4 → 4 → 15 → 80 → 82 → 4 of 100 |

All 3888 scenes together: found 2737 → 2743 → 2796 → 2942 → 2811 → 3045 → 2825; right place 2854 → 2856 → 2914 → 3071 → 2930 → 3170 → 2944; boxes drawn where no barrel is 45 → 48 → 45 → 45 → 45 → 48 → 45; right-place boxes too small / about right / too big: 324 / 2445 / 85 → 318 / 2452 / 86 → 346 / 2478 / 90 → 346 / 2638 / 87 → 333 / 2512 / 85 → 357 / 2721 / 92 → 347 / 2507 / 90.

Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`.
