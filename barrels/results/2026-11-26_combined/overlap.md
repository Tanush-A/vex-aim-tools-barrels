# C. The overlap: what each winner finds that the other does not

The held-out boxes of the judged run, ordinary conditions, 307 barrels counted per frame (172 placements). Made by `analysis.py overlap`.

| barrels | per frame | placements |
|---|---|---|
| found by today's detector | 211 | 133.80 |
| gained by both | 25 | 8.42 |
| gained by nearmiss only | 13 | 5.25 |
| gained by selfcal only | 12 | 5.33 |
| found by neither | 46 | 19.20 |
| LOST by a winner | 0 | 0.00 |

By condition (per frame; conditions with no such barrel are left out):

| condition | gained by both | gained by nearmiss only | gained by selfcal only | found by neither |
|---|---|---|---|---|
| both_abpgray | 2 | 0 | 3 | 1 |
| lampcool6_bathtile | 1 | 1 | 0 | 0 |
| lampcool6_ottoman | 7 | 3 | 1 | 1 |
| lampmid3_bathtile | 7 | 1 | 2 | 4 |
| lampmid6_bathtile | 7 | 3 | 1 | 3 |
| lampmid6_ottoman | 1 | 2 | 0 | 6 |
| lampwarm6_ottoman | 0 | 1 | 0 | 14 |
| window_abpwhite | 0 | 2 | 0 | 4 |
| lampwarm6_bathtile | 0 | 0 | 5 | 9 |
| window_light | 0 | 0 | 0 | 1 |
| overheaddim_palewood | 0 | 0 | 0 | 2 |
| window_glass | 0 | 0 | 0 | 1 |

## gained by nearmiss only (13)

paint = which of (body bands, stripe band) of the hand box a mask paints, with the two shares. `selfcal` = that barrel's state under the other winner. near-miss added = pixels the near-miss step painted in the hand box (body color / stripe color). seed = what self-calibration did with the seed candidates on the barrel. detector = what the reason log says on that barrel in either winner's mask.

| frame | # | color | flags | fixed colors paint | under `selfcal` | near-miss mask paints | near-miss added (body / stripe px) | selfcal mask paints | selfcal seed | touching | detector's reasons |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lampcool6_bathtile_occl_02 | 1 | orange | occluded | body only (0.64, 0.33) | missed | body only (0.64, 0.42) | 0 / 21 | body only (0.64, 0.33) | refused: stripe:body_like_surround |  | cap: narrow; cap: width; piece: covered; piece: stripeless; stripe: height |
| lampcool6_ottoman_close_01 | 1 | orange | truncated | neither (0.00, 0.00) | missed | body only (0.96, 0.00) | 41412 / 0 | neither (0.00, 0.00) | refused: stripe:off_frame |  | cap: width; half: width; piece: width; stripe: width |
| lampcool6_ottoman_edge_01 | 1 | blue | truncated | body only (0.59, 0.00) | missed | both (0.59, 0.67) | 0 / 633 | body only (0.59, 0.00) | refused: stripe:not_two_colors |  | cap: width; half: width; piece: covered; piece: width; stripe: area |
| lampcool6_ottoman_edge_01 | 2 | orange | - | stripe only (0.34, 0.89) | missed | both (1.00, 0.89) | 4046 / 16 | stripe only (0.34, 0.89) | refused: stripe:stripe_not_painted |  | barrel: slice_not_full; cap: height; cap: width; half: far_edge; half: height; half: width; piece: covered; piece: stripeless; piece: width; stripe: area; stripe: width |
| lampmid3_bathtile_core_01 | 2 | orange | - | body only (1.00, 0.00) | missed | body only (1.00, 0.25) | 0 / 46 | both (1.00, 0.50) | kept: body |  | cap: height; cap: narrow; cap: not_hidden; half: width; piece: covered; piece: stripeless; stripe: height |
| lampmid6_bathtile_core_01 | 2 | orange | - | body only (1.00, 0.00) | missed | both (1.00, 0.75) | 0 / 85 | both (1.00, 0.72) | kept: body |  | cap: height; cap: width; piece: covered; piece: stripeless; stripe: height |
| lampmid6_bathtile_edge_01 | 1 | blue | truncated | stripe only (0.00, 1.00) | missed | both (0.90, 1.00) | 938 / 0 | stripe only (0.00, 1.00) | no seed candidate |  | cap: width; half: width; piece: covered; piece: width; stripe: height |
| lampmid6_bathtile_edge_01 | 2 | orange | - | body only (1.00, 0.00) | missed | both (1.00, 0.93) | 0 / 389 | body only (1.00, 0.00) | refused: stripe:body_like_surround |  | cap: narrow; cap: not_hidden; half: height; piece: covered; piece: stripeless; stripe: area |
| lampmid6_ottoman_clutter_01 | 1 | blue | - | body only (0.77, 0.00) | missed | both (0.85, 1.00) | 1790 / 1192 | body only (0.78, 0.00) | refused: stripe:body_like_surround+stripe:stripe_not_painted |  | cap: not_hidden; cap: width; half: height; half: thicker_than_body; half: width; piece: covered; piece: stripeless; piece: width; stripe: area; stripe: height; stripe: width |
| lampmid6_ottoman_core_01 | 3 | blue | - | body only (0.53, 0.09) | missed | both (0.72, 1.00) | 535 / 331 | body only (0.53, 0.09) | no seed candidate |  | cap: height; cap: width; half: height; half: width; piece: covered; piece: stripeless; piece: width; stripe: area |
| lampwarm6_ottoman_clutter_01 | 3 | orange | - | body only (0.64, 0.00) | missed | body only (0.64, 0.01) | 0 / 286 | body only (0.64, 0.00) | refused: stripe:body_like_surround+stripe:not_two_colors | yes | cap: height; cap: narrow; cap: width; half: far_edge; half: width; piece: covered; piece: stripeless; piece: width; stripe: area; stripe: height |
| window_abpwhite_occlx_06 | 1 | orange | bottom_estimated,occluded | stripe only (0.42, 1.00) | missed | both (0.93, 1.00) | 562 / 0 | stripe only (0.42, 1.00) | refused: stripe:body_like_surround+stripe:not_two_colors |  | barrel: slice_not_full; cap: height; cap: not_hidden; cap: width; half: thicker_than_body; half: width; piece: covered; piece: stripeless |
| window_abpwhite_occlx_14 | 1 | orange | occluded,truncated | both (0.60, 1.00) | missed | both (0.60, 1.00) | 153 / 14 | both (0.60, 1.00) | refused: stripe:body_like_surround |  | barrel: slice_not_full; cap: height; cap: not_hidden; cap: width; half: width; piece: covered; piece: stripeless |

## gained by selfcal only (12)

paint = which of (body bands, stripe band) of the hand box a mask paints, with the two shares. `nearmiss` = that barrel's state under the other winner. near-miss added = pixels the near-miss step painted in the hand box (body color / stripe color). seed = what self-calibration did with the seed candidates on the barrel. detector = what the reason log says on that barrel in either winner's mask.

| frame | # | color | flags | fixed colors paint | under `nearmiss` | near-miss mask paints | near-miss added (body / stripe px) | selfcal mask paints | selfcal seed | touching | detector's reasons |
|---|---|---|---|---|---|---|---|---|---|---|---|
| both_abpgray_core_01 | 4 | orange | - | stripe only (0.32, 1.00) | box off | both (0.65, 1.00) | 1265 / 0 | both (1.00, 1.00) | kept: stripe | yes | cap: width; half: far_edge; half: height; half: thicker_than_body; piece: covered |
| both_abpgray_edge_01 | 1 | orange | - | stripe only (0.00, 0.98) | missed | stripe only (0.41, 0.98) | 1619 / 0 | both (1.00, 1.00) | kept: stripe |  | barrel: slice_not_full; cap: height; cap: width; half: height; half: thicker_than_body; half: width; piece: covered; piece: stripeless; stripe: width |
| both_abpgray_touch_01 | 1 | orange | - | stripe only (0.26, 1.00) | missed | stripe only (0.43, 1.00) | 796 / 39 | both (1.00, 1.00) | kept: stripe | yes | barrel: slice_not_full; cap: height; cap: not_hidden; cap: width; half: thicker_than_body; half: width; piece: covered; piece: stripeless; stripe: area |
| lampcool6_ottoman_touch_01 | 1 | blue | - | body only (0.84, 0.01) | missed | body only (0.86, 0.01) | 437 / 0 | both (0.97, 1.00) | refused: body:not_two_colors+stripe:stripe_not_painted | yes | barrel: stripe_piece; cap: not_hidden; cap: width; half: width; piece: covered; stripe: area |
| lampmid3_bathtile_core_01 | 3 | blue | - | stripe only (0.00, 1.00) | missed | stripe only (0.37, 1.00) | 2306 / 0 | both (0.95, 1.00) | kept: stripe |  | barrel: slice_not_full; cap: height; cap: not_hidden; cap: width; half: height; half: thicker_than_body; half: width; piece: covered; piece: stripeless; stripe: area; stripe: height; stripe: width |
| lampmid3_bathtile_core_01 | 4 | blue | - | stripe only (0.00, 1.00) | missed | stripe only (0.03, 1.00) | 15 / 0 | both (0.89, 1.00) | kept: stripe |  | cap: narrow; half: far_edge_against_barrel; half: width; piece: covered; piece: stripeless; stripe: area |
| lampmid6_bathtile_touch_01 | 3 | blue | - | stripe only (0.05, 1.00) | missed | stripe only (0.05, 1.00) | 0 / 0 | both (0.51, 1.00) | no seed candidate | yes | barrel: slice_not_full; cap: height; cap: width; half: width; piece: covered; piece: stripeless; piece: width; stripe: area; stripe: height; stripe: width |
| lampwarm6_bathtile_clutter_01 | 4 | orange | - | body only (1.00, 0.00) | missed | body only (1.00, 0.00) | 0 / 13 | both (1.00, 1.00) | kept: body |  | cap: narrow; cap: width; piece: covered; piece: stripeless; stripe: area |
| lampwarm6_bathtile_core_01 | 1 | orange | - | body only (1.00, 0.00) | missed | body only (1.00, 0.00) | 0 / 14 | both (1.00, 1.00) | kept: body |  | cap: narrow; piece: above_horizon; stripe: area |
| lampwarm6_bathtile_core_01 | 3 | blue | - | stripe only (0.00, 1.00) | missed | stripe only (0.00, 1.00) | 1 / 0 | both (0.96, 1.00) | kept: stripe |  | cap: narrow; cap: width; piece: covered; piece: stripeless; piece: width; stripe: area; stripe: height; stripe: width; verify: readings |
| lampwarm6_bathtile_core_01 | 4 | blue | - | stripe only (0.00, 1.00) | missed | stripe only (0.00, 1.00) | 0 / 0 | both (0.89, 1.00) | kept: stripe |  | cap: narrow; cap: width; half: width; piece: covered; piece: stripeless; stripe: width |
| lampwarm6_bathtile_touch_01 | 1 | orange | - | body only (1.00, 0.00) | missed | body only (1.00, 0.19) | 0 / 34 | both (1.00, 0.99) | kept: body | yes | cap: width; piece: covered; piece: stripeless; stripe: height |

## What the pictures show (written after looking at the sheets)

- Both winners do the same thing: they complete a barrel that has one color at full strength. 25 barrels per frame are gained by both, 13 by the near-miss step only, 12 by self-calibration only, none lost by either.
- Near-miss only (13): orange ottoman barrels whose body hue sits just past the top of the orange range (painted light yellow on the sheets) around a strict blue stripe (3, one cut by the frame); blue ottoman barrels whose orange stripe it completes (3, one cut by the frame); thin blue stripes of orange bathroom barrels (hue 90-101; 4), where self-calibration's seed was refused (body_like_surround) or its paint stayed too thin for a box; a frame-cut blue bathroom barrel (1); two partly hidden barrels of the ABP occlusion set (2). Self-calibration refuses these on its photo check, or has no seed (a cut or hidden barrel gives no stripe-sized band).
- Self-calibration only (12): the red-orange bodies on the gray table (3; the near-miss step paints only part of the lower body, edge mode 'strict' was picked there), blue bodies under the bathroom mid and warm lamps (5) and orange barrels under the warm lamp whose blue stripe is gray-olive (3): the near-miss levels end at hue +-25 of the range, the read range of a kept seed does not. One blue barrel touching another on the ottoman.
- So neither is enough alone, and the reasons are different: the near-miss step is blind outside its ladder (warm lamp), self-calibration needs a seed its guard keeps (cut, hidden or noisy surroundings).

