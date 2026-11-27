# Real train frames: every box that changes (261 frames with a box label)

Arms: `off` = today; `cut` = {'side_photo': 'cut'}; `cut+bulge` = {'side_photo': 'cut+bulge'}; `slack` = {'side_photo': 'cut', 'photo_slack': 0.1}; `loose` = {'side_photo': 'cut', 'photo_slack': 0.1, 'photo_frac': 0.5, 'photo_cross': 0.2}. The photo is passed to both detector runs (the first and the one on the contrast-painted mask).

Frames whose boxes differ from today: `cut` 2, `cut+bulge` 1, `slack` 3, `loose` 6

| frame | arm | what | box | rule | state |
|---|---|---|---|---|---|
| lampcool6_ottoman_clutter_01 | `loose` | new box | blue [300, 113, 344, 163] | photo_cut | found |
| lampcool6_ottoman_clutter_01 | `loose` | box gone | blue [288, 113, 332, 163] | centred | found |
| lampcool6_ottoman_occl_02 | `cut` | new box | orange [226, 134, 286, 188] | thin_photo_cut | found |
| lampcool6_ottoman_occl_02 | `slack` | new box | orange [226, 134, 286, 188] | thin_photo_cut | found |
| lampcool6_ottoman_occl_02 | `loose` | new box | orange [226, 134, 286, 188] | thin_photo_cut | found |
| lampwarm6_glass_clutter_01 | `loose` | new box | orange [512, 112, 561, 172] | photo_cut | found |
| lampwarm6_glass_clutter_01 | `loose` | box gone | orange [518, 112, 566, 172] | centred | found |
| window_abpwhite_occlx_02 | `cut` | new box | orange [91, 122, 140, 171] | thin_photo_cut | found |
| window_abpwhite_occlx_02 | `cut+bulge` | new box | orange [91, 122, 140, 171] | thin_photo_cut | found |
| window_abpwhite_occlx_02 | `slack` | new box | orange [91, 122, 140, 171] | thin_photo_cut | found |
| window_abpwhite_occlx_02 | `loose` | new box | orange [91, 122, 140, 171] | thin_photo_cut | found |
| window_abpwhite_occlx_03 | `slack` | new box | orange [101, 120, 151, 171] | photo_cut | found |
| window_abpwhite_occlx_03 | `loose` | new box | orange [101, 120, 151, 171] | photo_cut | found |
| window_black_cluster_01 | `loose` | new box | blue [425, 131, 492, 200] | thin_photo_cut | found |

Totals over these frames (per frame, not per placement; states of `counting.classify_frame`):

| | `off` | `cut` | `cut+bulge` | `slack` | `loose` |
|---|---|---|---|---|---|
| found | 362 | 364 | 363 | 365 | 366 |
| off | 17 | 17 | 17 | 17 | 17 |
| missed | 158 | 156 | 157 | 155 | 154 |
| nothing | 6 | 6 | 6 | 6 | 6 |
| second | 1 | 1 | 1 | 1 | 1 |
| wrong_color | 6 | 6 | 6 | 6 | 6 |

Occlusion frames (`occl` in the name), 103 labelled barrels: found (strict) `off` 52, `cut` 54, `cut+bulge` 53, `slack` 55, `loose` 55; found or box off: `off` 58, `cut` 60, `cut+bulge` 59, `slack` 61, `loose` 61.

Occlusion barrels whose state changes:

| frame | barrel | truth | off | cut | cut+bulge | slack | loose |
|---|---|---|---|---|---|---|---|
| lampcool6_ottoman_occl_02 | orange | [225, 125, 286, 192] | missed | found | missed | found | found |
| window_abpwhite_occlx_02 | orange | [92, 119, 143, 170] | missed | found | found | found | found |
| window_abpwhite_occlx_03 | orange | [99, 120, 152, 172] | missed | missed | missed | found | found |
