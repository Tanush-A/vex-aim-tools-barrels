# Time per frame

37 HOME and CAMPUS train frames, 640 x 480, 0 to 4 barrels per frame (median 2); this laptop, one core, best of 3 runs per frame. Detection only; the color segmentation, which every arm needs once, is the first row.

| | median ms | 90th percentile | slowest frame |
|---|---|---|---|
| color segmentation | 26 | 26 | 28 |
| `rules` | 19 | 33 | 41 |
| `stencil` | 89 | 154 | 266 |
| `union` | 70 | 90 | 126 |
| `veto` | 78 | 160 | 167 |
| `veto+union` | 127 | 209 | 264 |
| `union1` | 70 | 89 | 126 |

On the frames with no barrel: `rules` 11 ms, `stencil` 15 ms, `union` 26 ms, `veto` 11 ms, `veto+union` 26 ms, `union1` 26 ms.
