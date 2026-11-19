# Time per frame

37 HOME and CAMPUS train frames, 640 x 480, 0 to 4 barrels per frame (median 2); this laptop, one core, best of 3 runs per frame. Detection only; the color segmentation, which every arm needs once, is the first row.

| | median ms | 90th percentile | slowest frame |
|---|---|---|---|
| color segmentation | 26 | 28 | 32 |
| `rules` | 20 | 35 | 43 |
| `stencil` | 92 | 157 | 280 |
| `union` | 72 | 93 | 133 |
| `veto` | 81 | 165 | 178 |
| `veto+union` | 131 | 217 | 279 |

On the frames with no barrel: `rules` 12 ms, `stencil` 16 ms, `union` 28 ms, `veto` 12 ms, `veto+union` 28 ms.
