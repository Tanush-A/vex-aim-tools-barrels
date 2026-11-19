# Occlusion scorecard: the rule detector, the stencil, and the combinations

The scorecard of `experiments/2026-11-19_det_occl`, unchanged: 3888 scenes made from 50 unhidden barrels of the train frames (12 HOME hand masks, 12 HOME color model, 26 CAMPUS color model), each hidden 25 / 50 / 75 % by one thing. Each cell: **`rules` → `stencil` → `union` → `veto` → `veto+union`, of n scenes**.

## Found: right color, overlap with the barrel's FULL box of half or more, bottom edge right (the v2 rule)

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 99 → 100 → 100 → 100 of 100 | 99 → 97 → 100 → 99 → 100 of 100 | 3 → 4 → 6 → 3 → 6 of 100 |
| a straight upright edge, one side | 100 → 99 → 100 → 100 → 100 of 100 | 82 → 86 → 91 → 82 → 91 of 100 | 0 → 0 → 0 → 0 → 0 of 100 |
| a slanted edge, one side | 200 → 198 → 200 → 200 → 200 of 200 | 154 → 142 → 175 → 154 → 175 of 200 | 0 → 0 → 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 → 50 → 50 of 50 | 49 → 49 → 49 → 49 → 50 of 50 | 0 → 7 → 7 → 0 → 7 of 50 |
| hidden from above | 50 → 46 → 50 → 50 → 50 of 50 | 2 → 0 → 2 → 0 → 0 of 50 | 0 → 0 → 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 8 → 49 → 49 → 49 of 50 | 1 → 0 → 1 → 1 → 1 of 50 | 1 → 0 → 1 → 0 → 0 of 50 |
| a post across the middle | 49 → 49 → 50 → 49 → 50 of 50 | 9 → 27 → 32 → 9 → 32 of 50 | 0 → 0 → 0 → 0 → 0 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 100 → 99 → 100 of 100 | 94 → 93 → 99 → 94 → 99 of 100 | 49 → 11 → 50 → 49 → 50 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 99 → 100 → 98 → 100 of 100 | 92 → 91 → 98 → 92 → 98 of 100 | 77 → 13 → 77 → 77 → 77 of 100 |
| a barrel of the OTHER color, straight in front | 39 → 44 → 43 → 39 → 43 of 47 | 38 → 28 → 40 → 38 → 40 of 48 | 17 → 9 → 20 → 17 → 20 of 49 |
| a barrel of the SAME color, beside it | 81 → 99 → 81 → 81 → 82 of 100 | 36 → 83 → 36 → 36 → 36 of 100 | 16 → 8 → 16 → 16 → 16 of 100 |
| a barrel of the SAME color, beside it and lower | 91 → 99 → 92 → 91 → 92 of 100 | 85 → 96 → 87 → 85 → 87 of 100 | 26 → 18 → 26 → 25 → 25 of 100 |
| a barrel of the SAME color, straight in front | 44 → 45 → 44 → 44 → 44 of 47 | 29 → 28 → 32 → 29 → 32 of 48 | 2 → 13 → 4 → 2 → 4 of 49 |
| a plain block of the barrel's body color | 100 → 96 → 100 → 100 → 100 of 100 | 99 → 19 → 99 → 98 → 98 of 100 | 5 → 2 → 5 → 2 → 2 of 100 |
| a plain block of the barrel's stripe color | 100 → 98 → 100 → 100 → 100 of 100 | 99 → 81 → 99 → 98 → 98 of 100 | 3 → 0 → 3 → 3 → 3 of 100 |

## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 99 → 100 → 100 → 100 of 100 | 99 → 97 → 100 → 99 → 100 of 100 | 3 → 4 → 6 → 3 → 6 of 100 |
| a straight upright edge, one side | 100 → 99 → 100 → 100 → 100 of 100 | 86 → 91 → 95 → 84 → 93 of 100 | 0 → 0 → 0 → 0 → 0 of 100 |
| a slanted edge, one side | 200 → 198 → 200 → 200 → 200 of 200 | 156 → 154 → 178 → 156 → 178 of 200 | 0 → 0 → 0 → 0 → 0 of 200 |
| both sides cut | 50 → 50 → 50 → 50 → 50 of 50 | 50 → 49 → 50 → 49 → 50 of 50 | 0 → 7 → 7 → 0 → 7 of 50 |
| hidden from above | 50 → 46 → 50 → 50 → 50 of 50 | 2 → 0 → 2 → 0 → 0 of 50 | 0 → 0 → 0 → 0 → 0 of 50 |
| hidden from below (a low thing in front) | 50 → 43 → 50 → 50 → 50 of 50 | 1 → 0 → 1 → 1 → 1 of 50 | 1 → 0 → 1 → 0 → 0 of 50 |
| a post across the middle | 49 → 49 → 50 → 49 → 50 of 50 | 9 → 28 → 33 → 9 → 33 of 50 | 0 → 0 → 0 → 0 → 0 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 → 100 → 99 → 100 of 100 | 96 → 94 → 99 → 96 → 99 of 100 | 60 → 11 → 61 → 60 → 61 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 → 99 → 100 → 98 → 100 of 100 | 92 → 94 → 99 → 92 → 99 of 100 | 90 → 26 → 90 → 90 → 90 of 100 |
| a barrel of the OTHER color, straight in front | 41 → 46 → 45 → 41 → 45 of 47 | 39 → 38 → 42 → 39 → 42 of 48 | 28 → 25 → 34 → 28 → 34 of 49 |
| a barrel of the SAME color, beside it | 88 → 99 → 88 → 88 → 89 of 100 | 49 → 84 → 49 → 49 → 49 of 100 | 31 → 17 → 31 → 31 → 31 of 100 |
| a barrel of the SAME color, beside it and lower | 98 → 99 → 99 → 98 → 99 of 100 | 89 → 96 → 91 → 89 → 91 of 100 | 32 → 30 → 33 → 31 → 32 of 100 |
| a barrel of the SAME color, straight in front | 45 → 45 → 45 → 45 → 45 of 47 | 37 → 38 → 43 → 37 → 43 of 48 | 7 → 29 → 15 → 7 → 15 of 49 |
| a plain block of the barrel's body color | 100 → 96 → 100 → 100 → 100 of 100 | 99 → 58 → 99 → 98 → 98 of 100 | 5 → 2 → 5 → 2 → 2 of 100 |
| a plain block of the barrel's stripe color | 100 → 98 → 100 → 100 → 100 of 100 | 99 → 84 → 99 → 98 → 98 of 100 | 4 → 0 → 4 → 4 → 4 of 100 |

## All scenes together

| | `rules` | `stencil` | `union` | `veto` | `veto+union` |
|---|---|---|---|---|---|
| found (v2) | 2417 | 2233 | 2514 | 2408 | 2507 |
| box in the right place | 2532 | 2421 | 2644 | 2520 | 2634 |
| boxes where no barrel is | 45 | 10 | 47 | 42 | 44 |
| right-place boxes too small | 299 | 96 | 308 | 292 | 301 |
| ... about right | 2129 | 2298 | 2230 | 2124 | 2227 |
| ... too big | 104 | 27 | 106 | 104 | 106 |
| the barrel pasted in front found, of 1488 | 1284 | 1311 | 1286 | 1284 | 1286 |
| found, HOME hand masks (of 936) | 593 | 594 | 621 | 592 | 620 |
| found, HOME color model (of 936) | 576 | 538 | 599 | 575 | 598 |
| found, CAMPUS color model (of 2016) | 1248 | 1101 | 1294 | 1241 | 1289 |
| boxes where no barrel is, HOME hand masks | 3 | 1 | 3 | 3 | 3 |
| boxes where no barrel is, HOME color model | 19 | 2 | 21 | 18 | 20 |
| boxes where no barrel is, CAMPUS color model | 23 | 7 | 23 | 21 | 21 |

## Each arm against `rules`, cell by cell (kind x amount, the three pools together)

| arm | cells with more found | cells with fewer found | cells with fewer right-place boxes | boxes where no barrel is |
|---|---|---|---|---|
| `stencil` | 12 | 25 | 24 | 45 → 10 |
| `union` | 19 | 0 | 0 | 45 → 47 |
| `veto` | 0 | 6 | 8 | 45 → 42 |
| `veto+union` | 21 | 6 | 5 | 45 → 44 |

- `stencil`, fewer found: cut by the frame edge at 25 %: 100 → 99 of 100
- `stencil`, fewer found: cut by the frame edge at 50 %: 99 → 97 of 100
- `stencil`, fewer found: a straight upright edge, one side at 25 %: 100 → 99 of 100
- `stencil`, fewer found: a slanted edge, one side at 25 %: 200 → 198 of 200
- `stencil`, fewer found: a slanted edge, one side at 50 %: 154 → 142 of 200
- `stencil`, fewer found: hidden from above at 25 %: 50 → 46 of 50
- `stencil`, fewer found: hidden from above at 50 %: 2 → 0 of 50
- `stencil`, fewer found: hidden from below (a low thing in front) at 25 %: 49 → 8 of 50
- `stencil`, fewer found: hidden from below (a low thing in front) at 50 %: 1 → 0 of 50
- `stencil`, fewer found: hidden from below (a low thing in front) at 75 %: 1 → 0 of 50
- `stencil`, fewer found: a barrel of the OTHER color, beside it at 50 %: 94 → 93 of 100
- `stencil`, fewer found: a barrel of the OTHER color, beside it at 75 %: 49 → 11 of 100
- `stencil`, fewer found: a barrel of the OTHER color, beside it and lower at 50 %: 92 → 91 of 100
- `stencil`, fewer found: a barrel of the OTHER color, beside it and lower at 75 %: 77 → 13 of 100
- `stencil`, fewer found: a barrel of the OTHER color, straight in front at 50 %: 38 → 28 of 48
- `stencil`, fewer found: a barrel of the OTHER color, straight in front at 75 %: 17 → 9 of 49
- `stencil`, fewer found: a barrel of the SAME color, beside it at 75 %: 16 → 8 of 100
- `stencil`, fewer found: a barrel of the SAME color, beside it and lower at 75 %: 26 → 18 of 100
- `stencil`, fewer found: a barrel of the SAME color, straight in front at 50 %: 29 → 28 of 48
- `stencil`, fewer found: a plain block of the barrel's body color at 25 %: 100 → 96 of 100
- `stencil`, fewer found: a plain block of the barrel's body color at 50 %: 99 → 19 of 100
- `stencil`, fewer found: a plain block of the barrel's body color at 75 %: 5 → 2 of 100
- `stencil`, fewer found: a plain block of the barrel's stripe color at 25 %: 100 → 98 of 100
- `stencil`, fewer found: a plain block of the barrel's stripe color at 50 %: 99 → 81 of 100
- `stencil`, fewer found: a plain block of the barrel's stripe color at 75 %: 3 → 0 of 100
- `veto`, fewer found: hidden from above at 50 %: 2 → 0 of 50
- `veto`, fewer found: hidden from below (a low thing in front) at 75 %: 1 → 0 of 50
- `veto`, fewer found: a barrel of the SAME color, beside it and lower at 75 %: 26 → 25 of 100
- `veto`, fewer found: a plain block of the barrel's body color at 50 %: 99 → 98 of 100
- `veto`, fewer found: a plain block of the barrel's body color at 75 %: 5 → 2 of 100
- `veto`, fewer found: a plain block of the barrel's stripe color at 50 %: 99 → 98 of 100
- `veto+union`, fewer found: hidden from above at 50 %: 2 → 0 of 50
- `veto+union`, fewer found: hidden from below (a low thing in front) at 75 %: 1 → 0 of 50
- `veto+union`, fewer found: a barrel of the SAME color, beside it and lower at 75 %: 26 → 25 of 100
- `veto+union`, fewer found: a plain block of the barrel's body color at 50 %: 99 → 98 of 100
- `veto+union`, fewer found: a plain block of the barrel's body color at 75 %: 5 → 2 of 100
- `veto+union`, fewer found: a plain block of the barrel's stripe color at 50 %: 99 → 98 of 100

Limits, as on 2026-11-19: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front). A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers.
