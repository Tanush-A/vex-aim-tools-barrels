# Real train frames: every box that changes (261 frames with a box label)

Arms: `off` = today; `cut` = {'side_photo': 'cut'}; `cut+bulge` = {'side_photo': 'cut+bulge'}. The photo is passed to both detector runs (the first and the one on the contrast-painted mask).

Frames whose boxes differ from today: `cut` 2, `cut+bulge` 1

| frame | arm | what | box | rule | state |
|---|---|---|---|---|---|
| lampcool6_ottoman_occl_02 | `cut` | new box | orange [226, 134, 286, 188] | thin_photo_cut | found |
| window_abpwhite_occlx_02 | `cut` | new box | orange [91, 122, 140, 171] | thin_photo_cut | found |
| window_abpwhite_occlx_02 | `cut+bulge` | new box | orange [91, 122, 140, 171] | thin_photo_cut | found |

Totals over these frames (per frame, not per placement; states of `counting.classify_frame`):

| | `off` | `cut` | `cut+bulge` |
|---|---|---|---|
| found | 362 | 364 | 363 |
| off | 17 | 17 | 17 |
| missed | 158 | 156 | 157 |
| nothing | 6 | 6 | 6 |
| second | 1 | 1 | 1 |
| wrong_color | 6 | 6 | 6 |

Occlusion frames (`occl` in the name), 103 labelled barrels: found (strict) `off` 52, `cut` 54, `cut+bulge` 53; found or box off: `off` 58, `cut` 60, `cut+bulge` 59.

Occlusion barrels whose state changes:

| frame | barrel | truth | off | cut | cut+bulge |
|---|---|---|---|---|---|
| lampcool6_ottoman_occl_02 | orange | [225, 125, 286, 192] | missed | found | missed |
| window_abpwhite_occlx_02 | orange | [92, 119, 143, 170] | missed | found | found |
