# C (addendum). The overlap of the three winners

Held-out boxes of the judged runs, ordinary conditions, 307 barrels counted per frame (172 placements). A row = the set of winners that find the barrel (strict rule) among the barrels today's detector misses. Made by `analysis.py overlap3`.

| found by | per frame | placements |
|---|---|---|
| found by today's detector | 211 | 133.80 |
| found by none of the three | 26 | 13.45 |
| nearmiss + selfcal + cn_alone | 24 | 8.08 |
| cn_alone | 20 | 5.75 |
| selfcal + cn_alone | 11 | 5.00 |
| nearmiss + cn_alone | 9 | 2.67 |
| nearmiss | 4 | 2.58 |
| nearmiss + selfcal | 1 | 0.33 |
| selfcal | 1 | 0.33 |

- Gained by contrast: 64 per frame. Gained by near-miss or self-calibration: 50; of them contrast finds 44, and 6 it does not. Gained by contrast and by neither of the other two: 20.

## Found by near-miss or self-calibration, not by contrast (6)

contrast candidate = what contrast's own path did on the barrel: no candidate (no stripe-like band at the size its row predicts), refused by a guard (the reasons), or painted (the detector then drew no strict box). final mask = contrast's mask.

| frame | # | color | flags | nearmiss / selfcal / contrast | fixed colors paint | contrast candidate | contrast mask paints | touching | detector's reasons (contrast mask) |
|---|---|---|---|---|---|---|---|---|---|
| lampcool6_ottoman_close_01 | 1 | orange | truncated | found / missed / missed | neither (0.00, 0.00) | no contrast candidate | neither (0.00, 0.00) |  | cap: width; half: width; piece: width |
| lampcool6_ottoman_touch_01 | 1 | blue | - | missed / found / missed | body only (0.84, 0.01) | painted | both (0.97, 1.00) | yes | cap: width; half: width; piece: covered |
| lampmid6_bathtile_edge_01 | 1 | blue | truncated | found / missed / missed | stripe only (0.00, 1.00) | no contrast candidate | stripe only (0.00, 1.00) |  | cap: width; piece: width |
| lampmid6_ottoman_touch_01 | 1 | blue | - | found / found / missed | body only (0.53, 0.10) | painted | both (0.79, 1.00) | yes | cap: width; half: height; half: width; piece: covered |
| window_abpwhite_occlx_06 | 1 | orange | bottom_estimated,occluded | found / missed / missed | stripe only (0.42, 1.00) | refused: alike_feat | stripe only (0.42, 1.00) |  | barrel: slice_not_full; cap: height; cap: not_hidden; cap: width; half: thicker_than_body; half: width; piece: stripeless |
| window_abpwhite_occlx_14 | 1 | orange | occluded,truncated | found / missed / missed | both (0.60, 1.00) | refused: alike_feat | both (0.60, 1.00) |  | barrel: slice_not_full; cap: height; cap: not_hidden; half: width; piece: stripeless |

## Found by contrast and by neither of the other two (20)

| frame | # | color | flags | condition |
|---|---|---|---|---|
| lampmid3_bathtile_touch_01 | 2 | blue | - | lampmid3_bathtile |
| lampmid3_bathtile_touch_01 | 3 | blue | - | lampmid3_bathtile |
| lampmid6_bathtile_clutter_01 | 2 | blue | - | lampmid6_bathtile |
| lampmid6_bathtile_touch_01 | 2 | blue | - | lampmid6_bathtile |
| lampmid6_ottoman_core_01 | 1 | blue | - | lampmid6_ottoman |
| lampmid6_ottoman_edge_01 | 1 | blue | truncated | lampmid6_ottoman |
| lampwarm6_bathtile_clutter_01 | 1 | blue | - | lampwarm6_bathtile |
| lampwarm6_bathtile_clutter_01 | 2 | blue | - | lampwarm6_bathtile |
| lampwarm6_bathtile_clutter_01 | 3 | orange | - | lampwarm6_bathtile |
| lampwarm6_bathtile_core_01 | 2 | orange | - | lampwarm6_bathtile |
| lampwarm6_bathtile_edge_01 | 2 | orange | - | lampwarm6_bathtile |
| lampwarm6_bathtile_touch_01 | 2 | blue | - | lampwarm6_bathtile |
| lampwarm6_bathtile_touch_01 | 3 | blue | - | lampwarm6_bathtile |
| lampwarm6_ottoman_clutter_01 | 1 | blue | - | lampwarm6_ottoman |
| lampwarm6_ottoman_core_01 | 1 | blue | - | lampwarm6_ottoman |
| lampwarm6_ottoman_core_01 | 3 | blue | - | lampwarm6_ottoman |
| lampwarm6_ottoman_core_01 | 4 | orange | - | lampwarm6_ottoman |
| lampwarm6_ottoman_edge_01 | 1 | blue | truncated | lampwarm6_ottoman |
| lampwarm6_ottoman_edge_01 | 2 | orange | - | lampwarm6_ottoman |
| lampwarm6_ottoman_touch_01 | 3 | orange | - | lampwarm6_ottoman |

## By condition (per frame)

| condition | found by none of the three | nearmiss + selfcal + cn_alone | cn_alone | selfcal + cn_alone | nearmiss + cn_alone | nearmiss | nearmiss + selfcal | selfcal |
|---|---|---|---|---|---|---|---|---|
| both_abpgray | 1 | 2 | 0 | 3 | 0 | 0 | 0 | 0 |
| lampcool6_bathtile | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| lampcool6_ottoman | 1 | 7 | 0 | 0 | 2 | 1 | 0 | 1 |
| lampmid3_bathtile | 2 | 7 | 2 | 2 | 1 | 0 | 0 | 0 |
| lampmid6_bathtile | 1 | 7 | 2 | 1 | 2 | 1 | 0 | 0 |
| lampmid6_ottoman | 4 | 0 | 2 | 0 | 2 | 0 | 1 | 0 |
| lampwarm6_bathtile | 2 | 0 | 7 | 5 | 0 | 0 | 0 | 0 |
| lampwarm6_ottoman | 7 | 0 | 7 | 0 | 1 | 0 | 0 | 0 |
| overheaddim_palewood | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| window_abpwhite | 4 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| window_glass | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| window_light | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## What the pictures show

- Contrast does most of the work. Of the 50 barrels per frame near-miss or self-calibration gain, contrast finds 44; it adds 20 that neither finds (bathroom, ottoman, gray table). Nothing it finds is lost by it.
- The 6 it misses that another winner finds (sheets/cn_alone/found_by_a_winner_not_by_it_*.png): a close-up cut by the frame (no stripe in the frame, so no candidate) and a frame-cut blue barrel (the same); two blue barrels touching another blue barrel on the ottoman (contrast paints both, but their stripes join into one band two barrels wide and the detector draws one box on the pair); two partly hidden barrels of the ABP occlusion set, refused by contrast's guard 'one body' (the lower body is hidden by the black object, so the two body bands differ).
- So what the other two add on top of contrast is 2 to 6 barrels per frame (1 to 3 placements), mostly frame-cut and hidden ones, and each brings boxes on clutter (near-miss: the jar on the glass table). The judge calls every such sum inside the noise against contrast alone.

