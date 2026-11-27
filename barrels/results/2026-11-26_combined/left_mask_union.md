# G. What is left after `mask_union`: every barrel it does not find on the ordinary conditions, by cause

The held-out boxes of the judged run: 46 barrels not found counted per frame, 19.20 placements (of 307 and 172). Not found = no strict hit: 'box off' (a box of its color is on it and fails the strict rule) or 'missed'. The causes and their order are in PREREG.md, part G; a cause corrected from the picture has a note. Made by `analysis.py left`.

| cause | per frame | placements | of them with a box on the barrel (box off) | by condition (per frame) |
|---|---|---|---|---|
| hidden or cut by the frame | 25 | 13.12 | 2 | lampmid6_ottoman 5, lampwarm6_ottoman 5, window_abpwhite 4, lampmid3_bathtile 2, lampwarm6_bathtile 2, overheaddim_palewood 2, window_light 1, both_abpgray 1, lampcool6_ottoman 1, lampmid6_bathtile 1, window_glass 1 |
| neither color painted | 5 | 1.67 | 0 | lampwarm6_ottoman 5 |
| touching another barrel | 8 | 2.25 | 2 | lampmid3_bathtile 2, lampwarm6_bathtile 2, lampwarm6_ottoman 2, lampmid6_bathtile 1, lampmid6_ottoman 1 |
| a guard refused it | 7 | 1.92 | 0 | lampwarm6_bathtile 5, lampwarm6_ottoman 2 |
| the detector refused a well-painted barrel | 1 | 0.25 | 0 | lampmid6_bathtile 1 |
| **all** | 46 | 19.20 | 4 |  |

## hidden or cut by the frame (25)

| frame | # | color | flags | today / nearmiss / selfcal / mask_union | fixed colors paint | final mask paints | selfcal seed | near-miss added (body / stripe px) | touching | detector's reasons | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light_cluster_01 | 3 | orange | bottom_estimated,occluded | missed / missed / missed / missed | neither (0.05, 0.11) | neither (0.05, 0.11) | kept: found | 80 / 113 | yes | cap: both_sides; half: body_width; piece: covered; stripe: area; stripe: height |  |
| both_abpgray_clutter_01 | 2 | orange | occluded | box off / box off / box off / box off | stripe only (0.50, 0.98) | both (0.83, 1.00) | kept: found | 583 / 62 |  | half: width; piece: covered |  |
| lampcool6_ottoman_occl_02 | 1 | orange | occluded | missed / missed / missed / missed | stripe only (0.30, 0.72) | stripe only (0.30, 0.72) | no seed candidate | 0 / 0 |  | barrel: outline_unknown; cap: width; half: width; piece: stripeless; stripe: area |  |
| lampmid3_bathtile_edge_01 | 1 | blue | truncated | missed / missed / missed / missed | stripe only (0.01, 1.00) | stripe only (0.35, 1.00) | no seed candidate | 530 / 0 |  | cap: width; half: height; piece: stripeless; stripe: height; stripe: width |  |
| lampmid3_bathtile_occl_02 | 1 | orange | occluded | missed / missed / missed / missed | body only (0.77, 0.00) | body only (0.77, 0.08) | refused: stripe:not_two_colors | 0 / 34 |  | cap: narrow; cap: width; piece: stripeless; stripe: height |  |
| lampmid6_bathtile_occl_02 | 1 | orange | occluded | missed / missed / missed / missed | body only (0.82, 0.00) | body only (0.82, 0.25) | refused: stripe:not_two_colors | 0 / 43 |  | barrel: side_unexplained; cap: narrow; cap: width; piece: stripeless |  |
| lampmid6_ottoman_close_01 | 1 | orange | truncated | missed / missed / missed / missed | neither (0.01, 0.00) | neither (0.01, 0.00) | no seed candidate | 0 / 0 |  | cap: width; piece: width |  |
| lampmid6_ottoman_clutter_01 | 2 | blue | occluded | missed / missed / missed / missed | neither (0.49, 0.06) | stripe only (0.49, 1.00) | refused: stripe:not_two_colors | 2 / 419 | yes | barrel: outline_unknown; cap: narrow; cap: width; half: far_edge; half: width; piece: covered; piece: width; stripe: area; stripe: height |  |
| lampmid6_ottoman_clutter_01 | 4 | orange | bottom_estimated,occluded | missed / missed / missed / missed | neither (0.29, 0.00) | neither (0.29, 0.00) | refused: stripe:not_two_colors | 0 / 14 |  | cap: height; cap: width; piece: stripeless; piece: width; stripe: area; stripe: width |  |
| lampmid6_ottoman_edge_01 | 1 | blue | truncated | missed / missed / missed / missed | neither (0.21, 0.01) | neither (0.42, 0.01) | no seed candidate | 0 / 0 |  | cap: width; half: width; piece: width; stripe: area |  |
| lampmid6_ottoman_occl_02 | 1 | orange | occluded | missed / missed / missed / missed | stripe only (0.41, 0.61) | stripe only (0.41, 0.61) | no seed candidate | 0 / 3 |  | cap: width; half: width; piece: width; stripe: area |  |
| lampwarm6_bathtile_edge_01 | 1 | blue | truncated | missed / missed / missed / missed | stripe only (0.00, 1.00) | stripe only (0.03, 1.00) | no seed candidate | 19 / 0 |  | cap: width; piece: width; stripe: area |  |
| lampwarm6_bathtile_occl_02 | 1 | orange | occluded | missed / missed / missed / missed | body only (0.89, 0.00) | body only (0.89, 0.00) | refused: body:not_two_colors | 0 / 5 |  | piece: above_horizon; stripe: area |  |
| lampwarm6_ottoman_close_01 | 1 | orange | truncated | missed / missed / missed / missed | neither (0.04, 0.00) | neither (0.04, 0.00) | no seed candidate | 0 / 0 |  | cap: width; piece: width |  |
| lampwarm6_ottoman_clutter_01 | 2 | blue | occluded | missed / missed / missed / missed | neither (0.00, 0.31) | neither (0.00, 0.31) | refused: stripe:body_like_surround | 0 / 0 | yes | cap: height; stripe: area |  |
| lampwarm6_ottoman_clutter_01 | 4 | orange | bottom_estimated,occluded | missed / missed / missed / missed | neither (0.23, 0.00) | neither (0.23, 0.00) | refused: stripe:stripe_not_painted | 0 / 21 |  | cap: narrow; piece: stripeless; stripe: area |  |
| lampwarm6_ottoman_edge_01 | 1 | blue | truncated | missed / missed / missed / missed | neither (0.00, 0.15) | neither (0.00, 0.15) | no seed candidate | 0 / 0 |  | cap: width |  |
| lampwarm6_ottoman_occl_02 | 1 | orange | occluded | missed / missed / missed / missed | neither (0.42, 0.00) | neither (0.42, 0.00) | no seed candidate | 0 / 11 |  | cap: width; piece: width; stripe: area |  |
| overheaddim_palewood_edge_01 | 1 | blue | truncated | missed / missed / missed / missed | stripe only (0.22, 0.80) | stripe only (0.22, 1.00) | no seed candidate | 0 / 306 |  | barrel: slice_not_full; cap: not_hidden; cap: width; piece: stripeless; stripe: area; stripe: height |  |
| overheaddim_palewood_occl_02 | 1 | orange | occluded | missed / missed / missed / missed | neither (0.27, 0.40) | neither (0.27, 0.40) | no seed candidate | 0 / 15 |  | barrel: side_unexplained; cap: width; half: width; piece: stripeless |  |
| window_abpwhite_occlx_02 | 1 | orange | occluded | missed / missed / missed / missed | neither (0.04, 0.00) | neither (0.04, 0.00) | no seed candidate | 0 / 7 |  | barrel: outline_unknown; cap: width; half: width; piece: width |  |
| window_abpwhite_occlx_03 | 1 | orange | occluded | missed / missed / missed / missed | neither (0.16, 0.07) | neither (0.16, 0.08) | no seed candidate | 0 / 16 |  | barrel: side_unexplained; cap: width; half: width; piece: stripeless |  |
| window_abpwhite_occlx_10 | 1 | orange | bottom_estimated,occluded | missed / missed / missed / missed | body only (0.74, 0.00) | body only (0.74, 0.00) | kept: found | 37 / 31 | yes | half: height; piece: covered; stripe: area |  |
| window_abpwhite_occlx_19 | 2 | orange | bottom_estimated,occluded | missed / missed / missed / missed | neither (0.33, 0.00) | neither (0.33, 0.00) | no seed candidate | 0 / 0 |  | cap: width; half: width; piece: stripeless |  |
| window_glass_occl_02 | 1 | blue | occluded | box off / box off / box off / box off | body only (0.69, 0.38) | body only (0.69, 0.38) | no seed candidate | 0 / 35 |  | piece: covered |  |

## neither color painted (5)

| frame | # | color | flags | today / nearmiss / selfcal / mask_union | fixed colors paint | final mask paints | selfcal seed | near-miss added (body / stripe px) | touching | detector's reasons | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lampwarm6_ottoman_clutter_01 | 1 | blue | - | missed / missed / missed / missed | neither (0.00, 0.04) | neither (0.00, 0.04) | refused: stripe:body_like_surround | 134 / 0 |  | cap: width; stripe: area |  |
| lampwarm6_ottoman_core_01 | 1 | blue | - | missed / missed / missed / missed | neither (0.00, 0.04) | neither (0.30, 0.04) | no seed candidate | 1311 / 0 | yes | cap: not_hidden; cap: width; half: thicker_than_body; half: width; piece: stripeless; stripe: area |  |
| lampwarm6_ottoman_core_01 | 3 | blue | - | missed / missed / missed / missed | neither (0.00, 0.34) | neither (0.00, 0.34) | refused: stripe:stripe_not_painted | 0 / 0 |  | cap: height |  |
| lampwarm6_ottoman_touch_01 | 1 | blue | - | missed / missed / missed / missed | neither (0.00, 0.10) | neither (0.00, 0.10) | refused: stripe:stripe_not_painted | 11 / 0 | yes | cap: height; stripe: area |  |
| lampwarm6_ottoman_touch_01 | 2 | blue | - | missed / missed / missed / missed | neither (0.00, 0.16) | neither (0.00, 0.16) | refused: stripe:body_like_surround | 18 / 0 | yes | cap: height; cap: width |  |

## touching another barrel (8)

| frame | # | color | flags | today / nearmiss / selfcal / mask_union | fixed colors paint | final mask paints | selfcal seed | near-miss added (body / stripe px) | touching | detector's reasons | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lampmid3_bathtile_touch_01 | 2 | blue | - | missed / missed / missed / missed | stripe only (0.00, 1.00) | stripe only (0.00, 1.00) | no seed candidate | 0 / 0 | yes | cap: width; piece: stripeless; piece: width; stripe: area |  |
| lampmid3_bathtile_touch_01 | 3 | blue | - | missed / missed / missed / missed | stripe only (0.00, 1.00) | stripe only (0.00, 1.00) | no seed candidate | 0 / 0 | yes | cap: width; piece: stripeless; piece: width; stripe: area |  |
| lampmid6_bathtile_touch_01 | 2 | blue | - | missed / missed / box off / box off | stripe only (0.00, 1.00) | stripe only (0.37, 1.00) | no seed candidate | 0 / 0 | yes | barrel: slice_not_full; cap: width; half: width; piece: covered; piece: width; stripe: height; stripe: width |  |
| lampmid6_ottoman_core_01 | 1 | blue | - | missed / box off / missed / box off | body only (0.51, 0.04) | both (0.51, 1.00) | refused: stripe:not_two_colors | 0 / 989 | yes | cap: width; half: width; piece: covered; stripe: area; stripe: height |  |
| lampwarm6_bathtile_touch_01 | 2 | blue | - | missed / missed / missed / missed | stripe only (0.00, 1.00) | stripe only (0.00, 1.00) | no seed candidate | 0 / 0 | yes | cap: width; piece: stripeless; piece: width; stripe: area |  |
| lampwarm6_bathtile_touch_01 | 3 | blue | - | missed / missed / missed / missed | stripe only (0.00, 1.00) | stripe only (0.00, 1.00) | no seed candidate | 0 / 0 | yes | cap: not_hidden; cap: width; piece: stripeless |  |
| lampwarm6_ottoman_core_01 | 2 | orange | - | missed / missed / missed / missed | body only (0.52, 0.00) | body only (0.52, 0.00) | refused: stripe:body_like_surround | 0 / 91 | yes | cap: height; cap: width; half: width; piece: covered; piece: width; stripe: area; stripe: height; stripe: width |  |
| lampwarm6_ottoman_touch_01 | 3 | orange | - | missed / missed / missed / missed | body only (0.54, 0.00) | body only (0.54, 0.00) | refused: stripe:body_like_surround | 0 / 34 | yes | cap: height; cap: narrow; cap: width; piece: stripeless; piece: width; stripe: area; stripe: height |  |

## a guard refused it (7)

| frame | # | color | flags | today / nearmiss / selfcal / mask_union | fixed colors paint | final mask paints | selfcal seed | near-miss added (body / stripe px) | touching | detector's reasons | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lampwarm6_bathtile_clutter_01 | 1 | blue | - | missed / missed / missed / missed | stripe only (0.00, 1.00) | stripe only (0.00, 1.00) | no seed candidate | 0 / 0 |  | cap: not_hidden; cap: width |  |
| lampwarm6_bathtile_clutter_01 | 2 | blue | - | missed / missed / missed / missed | stripe only (0.00, 1.00) | stripe only (0.00, 1.00) | no seed candidate | 0 / 0 |  | piece: above_horizon; piece: width |  |
| lampwarm6_bathtile_clutter_01 | 3 | orange | - | missed / missed / missed / missed | body only (1.00, 0.00) | body only (1.00, 0.00) | refused: stripe:not_two_colors | 0 / 11 |  | cap: narrow; stripe: area |  |
| lampwarm6_bathtile_core_01 | 2 | orange | - | missed / missed / missed / missed | body only (1.00, 0.00) | body only (1.00, 0.47) | kept: body | 0 / 5 |  | piece: above_horizon; verify: readings |  |
| lampwarm6_bathtile_edge_01 | 2 | orange | - | missed / missed / missed / missed | body only (1.00, 0.00) | body only (1.00, 0.06) | refused: stripe:not_two_colors | 0 / 39 |  | barrel: outline_unknown; cap: narrow; cap: not_hidden; cap: width; piece: stripeless; stripe: area |  |
| lampwarm6_ottoman_core_01 | 4 | orange | - | missed / missed / missed / missed | body only (0.65, 0.00) | body only (0.65, 0.02) | refused: stripe:body_like_surround | 0 / 51 |  | cap: height; cap: not_hidden; cap: width; piece: stripeless; stripe: area; stripe: height |  |
| lampwarm6_ottoman_edge_01 | 2 | orange | - | missed / missed / missed / missed | body only (0.61, 0.05) | body only (0.61, 0.05) | refused: body:stripe_like_surround+stripe:body_like_surround+stripe:stripe_not_painted | 0 / 34 |  | cap: height; cap: narrow; cap: width; half: width; piece: stripeless; piece: width; stripe: area; stripe: height |  |

## the detector refused a well-painted barrel (1)

| frame | # | color | flags | today / nearmiss / selfcal / mask_union | fixed colors paint | final mask paints | selfcal seed | near-miss added (body / stripe px) | touching | detector's reasons | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lampmid6_bathtile_clutter_01 | 2 | blue | - | missed / missed / missed / missed | stripe only (0.02, 1.00) | both (0.96, 1.00) | kept: stripe | 136 / 0 |  | cap: height; piece: above_horizon; stripe: area; stripe: height; verify: front |  |

