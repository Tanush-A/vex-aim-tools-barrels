# G. What is left after `cn_alone`: every barrel it does not find on the ordinary conditions, by cause

The held-out boxes of the judged run: 32 barrels not found counted per frame, 16.70 placements (of 307 and 172). Not found = no strict hit: 'box off' (a box of its color is on it and fails the strict rule) or 'missed'. The causes and their order are in PREREG.md, part G; a cause corrected from the picture has a note. Made by `analysis.py left`.

| cause | per frame | placements | of them with a box on the barrel (box off) | by condition (per frame) |
|---|---|---|---|---|
| hidden or cut by the frame | 27 | 15.03 | 2 | window_abpwhite 6, lampmid6_ottoman 4, lampwarm6_ottoman 4, lampcool6_ottoman 2, lampmid3_bathtile 2, lampmid6_bathtile 2, lampwarm6_bathtile 2, overheaddim_palewood 2, window_light 1, both_abpgray 1, window_glass 1 |
| neither color painted | 2 | 0.67 | 0 | lampwarm6_ottoman 2 |
| touching another barrel | 3 | 1.00 | 0 | lampcool6_ottoman 1, lampmid6_ottoman 1, lampwarm6_ottoman 1 |
| a guard refused it | 0 | 0.00 | 0 |  |
| the detector refused a well-painted barrel | 0 | 0.00 | 0 |  |
| **all** | 32 | 16.70 | 2 |  |

## hidden or cut by the frame (27)

| frame | # | color | flags | today / nearmiss / selfcal / cn_alone / mask_union | fixed colors paint | final mask paints | selfcal seed | contrast candidate | near-miss added (body / stripe px) | touching | detector's reasons | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light_cluster_01 | 3 | orange | bottom_estimated,occluded | missed / missed / missed / missed / missed | neither (0.05, 0.11) | neither (0.05, 0.11) | no seed candidate | no contrast candidate | 80 / 113 | yes | cap: both_sides; piece: covered; stripe: area; verify: front |  |
| both_abpgray_clutter_01 | 2 | orange | occluded | box off / box off / box off / box off / box off | stripe only (0.50, 0.98) | stripe only (0.50, 0.98) | no seed candidate | refused: found_already | 583 / 62 |  | half: thicker_than_body; half: width; piece: covered |  |
| lampcool6_ottoman_close_01 | 1 | orange | truncated | missed / found / missed / missed / found | neither (0.00, 0.00) | neither (0.00, 0.00) | no seed candidate | no contrast candidate | 41412 / 0 |  | cap: width; half: width; piece: width |  |
| lampcool6_ottoman_occl_02 | 1 | orange | occluded | missed / missed / missed / missed / missed | stripe only (0.30, 0.72) | stripe only (0.30, 0.72) | no seed candidate | no contrast candidate | 0 / 0 |  | barrel: outline_unknown; cap: width; half: width; piece: stripeless; stripe: area |  |
| lampmid3_bathtile_edge_01 | 1 | blue | truncated | missed / missed / missed / missed / missed | stripe only (0.01, 1.00) | stripe only (0.01, 1.00) | no seed candidate | no contrast candidate | 530 / 0 |  | cap: width; piece: width |  |
| lampmid3_bathtile_occl_02 | 1 | orange | occluded | missed / missed / missed / missed / missed | body only (0.77, 0.00) | body only (0.77, 0.00) | no seed candidate | no contrast candidate | 0 / 34 |  | cap: narrow; piece: stripeless |  |
| lampmid6_bathtile_edge_01 | 1 | blue | truncated | missed / found / missed / missed / found | stripe only (0.00, 1.00) | stripe only (0.00, 1.00) | no seed candidate | no contrast candidate | 938 / 0 |  | cap: width; piece: width |  |
| lampmid6_bathtile_occl_02 | 1 | orange | occluded | missed / missed / missed / missed / missed | body only (0.82, 0.00) | body only (0.82, 0.00) | no seed candidate | no contrast candidate | 0 / 43 |  | cap: narrow; piece: stripeless |  |
| lampmid6_ottoman_close_01 | 1 | orange | truncated | missed / missed / missed / missed / missed | neither (0.01, 0.00) | neither (0.01, 0.00) | no seed candidate | no contrast candidate | 0 / 0 |  | cap: width; piece: width |  |
| lampmid6_ottoman_clutter_01 | 2 | blue | occluded | missed / missed / missed / missed / missed | neither (0.49, 0.06) | neither (0.49, 0.06) | no seed candidate | no contrast candidate | 2 / 419 | yes | cap: height; cap: narrow; cap: width; half: far_edge; half: width; piece: covered; piece: stripeless; piece: width; stripe: area; stripe: height |  |
| lampmid6_ottoman_clutter_01 | 4 | orange | bottom_estimated,occluded | missed / missed / missed / missed / missed | neither (0.29, 0.00) | neither (0.29, 0.00) | no seed candidate | refused: d_min | 0 / 14 |  | cap: height; cap: width; piece: stripeless; piece: width; stripe: area |  |
| lampmid6_ottoman_occl_02 | 1 | orange | occluded | missed / missed / missed / missed / missed | stripe only (0.41, 0.61) | stripe only (0.41, 0.61) | no seed candidate | no contrast candidate | 0 / 3 |  | cap: width; half: width; piece: width; stripe: area |  |
| lampwarm6_bathtile_edge_01 | 1 | blue | truncated | missed / missed / missed / missed / missed | stripe only (0.00, 1.00) | stripe only (0.00, 1.00) | no seed candidate | no contrast candidate | 19 / 0 |  | cap: width; piece: width |  |
| lampwarm6_bathtile_occl_02 | 1 | orange | occluded | missed / missed / missed / missed / missed | body only (0.89, 0.00) | body only (0.89, 0.00) | no seed candidate | no contrast candidate | 0 / 5 |  | piece: above_horizon |  |
| lampwarm6_ottoman_close_01 | 1 | orange | truncated | missed / missed / missed / missed / missed | neither (0.04, 0.00) | neither (0.04, 0.00) | no seed candidate | no contrast candidate | 0 / 0 |  | cap: width; piece: width |  |
| lampwarm6_ottoman_clutter_01 | 2 | blue | occluded | missed / missed / missed / missed / missed | neither (0.00, 0.31) | neither (0.00, 0.31) | no seed candidate | no contrast candidate | 0 / 0 | yes | cap: width; piece: width; stripe: area |  |
| lampwarm6_ottoman_clutter_01 | 4 | orange | bottom_estimated,occluded | missed / missed / missed / missed / missed | neither (0.23, 0.00) | neither (0.23, 0.00) | no seed candidate | refused: d_min | 0 / 21 |  | cap: narrow; piece: stripeless |  |
| lampwarm6_ottoman_occl_02 | 1 | orange | occluded | missed / missed / missed / missed / missed | neither (0.42, 0.00) | neither (0.42, 0.00) | no seed candidate | no contrast candidate | 0 / 11 |  | cap: width; piece: width |  |
| overheaddim_palewood_edge_01 | 1 | blue | truncated | missed / missed / missed / missed / missed | stripe only (0.22, 0.80) | stripe only (0.22, 0.80) | no seed candidate | no contrast candidate | 0 / 306 |  | cap: width; half: width; piece: stripeless; stripe: area; stripe: height |  |
| overheaddim_palewood_occl_02 | 1 | orange | occluded | missed / missed / missed / missed / missed | neither (0.27, 0.40) | neither (0.27, 0.40) | no seed candidate | no contrast candidate | 0 / 15 |  | barrel: side_unexplained; cap: width; half: width; piece: stripeless |  |
| window_abpwhite_occlx_02 | 1 | orange | occluded | missed / missed / missed / missed / missed | neither (0.04, 0.00) | neither (0.04, 0.00) | no seed candidate | no contrast candidate | 0 / 7 |  | barrel: outline_unknown; cap: width; half: width; piece: width |  |
| window_abpwhite_occlx_03 | 1 | orange | occluded | missed / missed / missed / missed / missed | neither (0.16, 0.07) | neither (0.16, 0.07) | no seed candidate | no contrast candidate | 0 / 16 |  | barrel: side_unexplained; cap: width; half: width; piece: stripeless |  |
| window_abpwhite_occlx_06 | 1 | orange | bottom_estimated,occluded | missed / found / missed / missed / found | stripe only (0.42, 1.00) | stripe only (0.42, 1.00) | no seed candidate | refused: alike_feat | 562 / 0 |  | barrel: slice_not_full; cap: height; cap: not_hidden; cap: width; half: thicker_than_body; half: width; piece: stripeless |  |
| window_abpwhite_occlx_10 | 1 | orange | bottom_estimated,occluded | missed / missed / missed / missed / missed | body only (0.74, 0.00) | body only (0.74, 0.00) | no seed candidate | refused: found_already | 37 / 31 | yes | cap: width; half: height; piece: covered; stripe: area |  |
| window_abpwhite_occlx_14 | 1 | orange | occluded,truncated | missed / found / missed / missed / found | both (0.60, 1.00) | both (0.60, 1.00) | no seed candidate | refused: alike_feat | 153 / 14 |  | barrel: slice_not_full; cap: height; cap: not_hidden; half: width; piece: stripeless |  |
| window_abpwhite_occlx_19 | 2 | orange | bottom_estimated,occluded | missed / missed / missed / missed / missed | neither (0.33, 0.00) | neither (0.33, 0.00) | no seed candidate | no contrast candidate | 0 / 0 |  | cap: width; half: width; piece: stripeless |  |
| window_glass_occl_02 | 1 | blue | occluded | box off / box off / box off / box off / box off | body only (0.69, 0.38) | body only (0.69, 0.38) | no seed candidate | refused: found_already | 0 / 35 |  | piece: covered |  |

## neither color painted (2)

| frame | # | color | flags | today / nearmiss / selfcal / cn_alone / mask_union | fixed colors paint | final mask paints | selfcal seed | contrast candidate | near-miss added (body / stripe px) | touching | detector's reasons | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lampwarm6_ottoman_touch_01 | 1 | blue | - | missed / missed / missed / missed / missed | neither (0.00, 0.10) | neither (0.00, 0.10) | no seed candidate | no contrast candidate | 11 / 0 | yes | cap: height; stripe: area |  |
| lampwarm6_ottoman_touch_01 | 2 | blue | - | missed / missed / missed / missed / missed | neither (0.00, 0.16) | neither (0.00, 0.16) | no seed candidate | no contrast candidate | 18 / 0 | yes | cap: height; cap: width |  |

## touching another barrel (3)

| frame | # | color | flags | today / nearmiss / selfcal / cn_alone / mask_union | fixed colors paint | final mask paints | selfcal seed | contrast candidate | near-miss added (body / stripe px) | touching | detector's reasons | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lampcool6_ottoman_touch_01 | 1 | blue | - | missed / missed / found / missed / found | body only (0.84, 0.01) | both (0.97, 1.00) | no seed candidate | painted | 437 / 0 | yes | cap: width; half: width; piece: covered |  |
| lampmid6_ottoman_touch_01 | 1 | blue | - | missed / found / found / missed / found | body only (0.53, 0.10) | both (0.79, 1.00) | no seed candidate | painted | 1031 / 488 | yes | cap: width; half: height; half: width; piece: covered |  |
| lampwarm6_ottoman_core_01 | 2 | orange | - | missed / missed / missed / missed / missed | body only (0.52, 0.00) | body only (0.52, 0.00) | no seed candidate | refused: found_already | 0 / 91 | yes | cap: height; cap: narrow; cap: width; half: width; piece: covered; piece: width; stripe: area | from the picture: contrast's candidate on it is 'found_already' because today's close-up box on the ottoman's glints below it ([166, 248, 282, 480], a box on nothing) holds its stripe point; the touching is real but is not what stops it |

