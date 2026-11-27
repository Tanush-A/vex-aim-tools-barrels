# The judged candidates of the white-balance experiment (2026-11-26, git 3778d2e)

**EXPERIMENT ONLY.** The standing rule (Dave, 2026-10-07) forbids correcting the image. Nothing here may be adopted without Dave.

`run.py`. The standard pass rule; F = full correction, judged as is; P and U = alpha chosen leave one place out. Train frames only, 154 ordinary frames, 172 placements, 8 places. A PASS under +6 placements is WEAK.

| candidate | verdict | found, placements | found, per frame | barrels gained / lost (per frame) | boxes not on their barrel, per arrangement (per frame) | on empty frames: clean / with clutter | places that moved |
|---|---|---|---|---|---|---|---|
| F1 gray_world, full correction | **FAIL** | 133.8 → 141.8 (+8.0) | 211 → 239 | 39 / 11 | 1.93 → 4.52 (5 → 9) | 0 → 0 / 0.00 → 2.00 | campus_study 35.0 → 34.0; abp_gray 10.0 → 12.0; home_bathtile 4.0 → 11.5; home_glass 14.8 → 15.0; home_ottoman 3.0 → 1.3; uc_palewood 13.0 → 12.0; abp_white 26.0 → 28.0 |
| F2 white_patch, full correction | **FAIL** | 133.8 → 137.0 (+3.2) | 211 → 228 | 34 / 17 | 1.93 → 6.97 (5 → 18) | 0 → 0 / 0.00 → 2.25 | campus_study 35.0 → 34.0; home_bathtile 4.0 → 10.5; home_glass 14.8 → 14.2; home_ottoman 3.0 → 1.3 |
| F3 without_loose, full correction | **FAIL** | 133.8 → 144.3 (+10.5) | 211 → 254 | 50 / 7 | 1.93 → 5.88 (5 → 14) | 0 → 0 / 0.00 → 1.98 | campus_study 35.0 → 34.0; home_bathtile 4.0 → 13.0; home_glass 14.8 → 15.0; home_ottoman 3.0 → 5.3 |
| F4 gray_above, full correction | **FAIL** | 133.8 → 141.6 (+7.8) | 211 → 246 | 46 / 11 | 1.93 → 6.42 (5 → 18) | 0 → 0 / 0.00 → 1.12 | home_white 28.0 → 27.0; abp_gray 10.0 → 11.0; home_bathtile 4.0 → 13.5; home_ottoman 3.0 → 2.3; uc_palewood 13.0 → 12.0 |
| F5 shades_of_gray, full correction | **FAIL** | 133.8 → 138.2 (+4.5) | 211 → 232 | 32 / 11 | 1.93 → 4.85 (5 → 12) | 0 → 0 / 0.00 → 2.20 | campus_study 35.0 → 34.0; abp_gray 10.0 → 11.0; home_bathtile 4.0 → 11.2; home_glass 14.8 → 15.0; home_ottoman 3.0 → 0.0 |
| P1 gray_world, partial (alpha chosen in the fold) | **PASS** | 133.8 → 143.0 (+9.2) | 211 → 243 | 38 / 6 | 1.93 → 1.05 (5 → 5) | 0 → 0 / 0.00 → 0.20 | abp_gray 10.0 → 12.0; home_bathtile 4.0 → 12.0; home_glass 14.8 → 15.0; home_ottoman 3.0 → 2.0 |
| P2 white_patch, partial (alpha chosen in the fold) | **NO CLEAR DIFFERENCE** | 133.8 → 133.1 (-0.7) | 211 → 208 | 7 / 10 | 1.93 → 2.67 (5 → 8) | 0 → 0 / 0.00 → 0.00 | home_glass 14.8 → 14.4; home_ottoman 3.0 → 2.7 |
| P3 without_loose, partial (alpha chosen in the fold) (primary) | **FAIL** | 133.8 → 134.8 (+1.0) | 211 → 215 | 6 / 2 | 1.93 → 4.65 (5 → 7) | 0 → 0 / 0.00 → 2.00 | home_bathtile 4.0 → 5.0 |
| P4 gray_above, partial (alpha chosen in the fold) | **PASS (WEAK)** | 133.8 → 138.5 (+4.7) | 211 → 234 | 30 / 7 | 1.93 → 2.47 (5 → 10) | 0 → 0 / 0.00 → 0.20 | home_white 28.0 → 27.0; abp_gray 10.0 → 11.0; home_bathtile 4.0 → 10.5; home_glass 14.8 → 15.0; home_ottoman 3.0 → 2.0; uc_palewood 13.0 → 12.0 |
| P5 shades_of_gray, partial (alpha chosen in the fold) | **NO CLEAR DIFFERENCE** | 133.8 → 132.7 (-1.1) | 211 → 208 | 3 / 6 | 1.93 → 0.80 (5 → 4) | 0 → 0 / 0.00 → 0.20 | home_glass 14.8 → 15.0; home_ottoman 3.0 → 1.7 |
| U3 today's mask plus the without_loose-corrected paint where today paints nothing (alpha in the fold) | **FAIL** | 133.8 → 135.5 (+1.7) | 211 → 217 | 7 / 1 | 1.93 → 5.43 (5 → 10) | 0 → 0 / 0.00 → 2.00 | home_bathtile 4.0 → 5.0; home_ottoman 3.0 → 3.7 |

## F1 gray_world, full correction: FAIL

- [BETTER] found, the ordinary conditions together: 133.8 -> 141.8 of 172 placements (+8.0; counted per frame 211 -> 239 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: campus_study -1.0 of 35 (margin 1.0); abp_gray +2.0 of 16 (margin 6.0); home_bathtile +7.5 of 15 (margin 1.2); home_glass +0.2 of 15 (margin 1.0); home_ottoman -1.7 of 15 (margin 2.3); uc_palewood -1.0 of 15 (margin 1.0); abp_white +2.0 of 32 (margin 1.0).
- [WORSE] boxes that are not on their barrel: 1.9 -> 4.5 counted once per arrangement (+2.6; per frame: on nothing 5 -> 8, second box 0 -> 0, wrong color 0 -> 1). Worse above +1.9, better below -1.0.
- [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 2.0 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): campus_light 35 → 34 of 35; both_abpgray 10 → 12 of 16; lampcool6_bathtile 13 → 15 of 15; lampcool6_ottoman 3 → 1 of 15; lampmid3_bathtile 1 → 15 of 15; lampmid6_bathtile 1 → 15 of 15; lampmid6_ottoman 6 → 2 of 15; lampwarm6_ottoman 0 → 1 of 15; overheaddim_palewood 13 → 12 of 15; window_abpwhite 26 → 28 of 32; window_glass 14 → 15 of 15.
- Lost: campus_light_room_01 #1 blue; both_abpgray_held_01 #1 blue; lampcool6_ottoman_core_01 #3 blue; lampcool6_ottoman_touch_01 #3 orange; lampmid6_ottoman_clutter_01 #3 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_edge_01 #2 orange; lampmid6_ottoman_touch_01 #2 blue; lampmid6_ottoman_touch_01 #3 orange; lampwarm6_bathtile_close_01 #1 orange; overheaddim_palewood_touch_01 #3 orange.
- Frames with more boxes not on their barrel: lampmid3_bathtile_occl_02, lampmid3_glass_clutter_01, lampwarm6_ottoman_clutter_01, lampwarm6_ottoman_occl_02, overheaddim_palewood_clutter_01, window_abpwhite_occlx_15 (EMPTY clutter), window_glass_occlx_16 (EMPTY clutter).
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 11 of 21; lampcool6_wood 2 → 15 of 21; lampmid3_ottoman 1 → 0 of 15; lampmid3_wood 1 → 5 of 21; lampmid6_wood 1 → 13 of 21; lampwarm3_wood 1 → 4 of 21; lampwarm6_wood 0 → 3 of 21; window_black 5 → 3 of 26.
- Pages: `judge_F1_gray_world/judge.md`.

## F2 white_patch, full correction: FAIL

- [within the noise] found, the ordinary conditions together: 133.8 -> 137.0 of 172 placements (+3.2; counted per frame 211 -> 228 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: campus_study -1.0 of 35 (margin 1.0); home_bathtile +6.5 of 15 (margin 1.2); home_glass -0.6 of 15 (margin 1.0); home_ottoman -1.7 of 15 (margin 2.3).
- [WORSE] boxes that are not on their barrel: 1.9 -> 7.0 counted once per arrangement (+5.0; per frame: on nothing 5 -> 17, second box 0 -> 0, wrong color 0 -> 1). Worse above +1.9, better below -1.0.
- [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 2.2 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): campus_light 35 → 34 of 35; lampcool6_bathtile 13 → 14 of 15; lampcool6_glass 15 → 14 of 15; lampcool6_ottoman 3 → 1 of 15; lampmid3_bathtile 1 → 14 of 15; lampmid6_bathtile 1 → 14 of 15; lampmid6_ottoman 6 → 2 of 15; lampwarm6_bathtile 1 → 0 of 15; lampwarm6_glass 15 → 14 of 15; lampwarm6_ottoman 0 → 1 of 15; window_glass 14 → 13 of 15.
- Lost: campus_light_room_01 #1 blue; lampcool6_bathtile_close_01 #1 orange; lampcool6_glass_occl_02 #1 blue; lampcool6_ottoman_core_01 #3 blue; lampcool6_ottoman_touch_01 #2 blue; lampcool6_ottoman_touch_01 #3 orange; lampmid3_bathtile_close_01 #1 orange; lampmid6_bathtile_close_01 #1 orange; lampmid6_ottoman_clutter_01 #3 orange; lampmid6_ottoman_core_01 #2 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_edge_01 #2 orange; lampmid6_ottoman_touch_01 #2 blue; lampmid6_ottoman_touch_01 #3 orange; lampwarm6_bathtile_close_01 #1 orange; lampwarm6_glass_occl_02 #1 blue; window_glass_clutter_01 #2 blue.
- Frames with more boxes not on their barrel: lampcool6_bathtile_close_01, lampmid3_bathtile_clutter_01, lampmid3_bathtile_neg_02 (EMPTY clutter), lampmid3_bathtile_occl_02, lampmid6_bathtile_close_01, lampwarm6_glass_occl_02, lampwarm6_ottoman_clutter_01, lampwarm6_ottoman_occl_02, overheaddim_palewood_neg_02 (EMPTY clutter), window_glass_clutter_01.
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 5 of 21; lampcool6_wood 2 → 16 of 21; lampmid3_ottoman 1 → 0 of 15; lampmid3_wood 1 → 7 of 21; lampmid6_wood 1 → 16 of 21; lampwarm3_wood 1 → 11 of 21; lampwarm6_wood 0 → 12 of 21.
- Pages: `judge_F2_white_patch/judge.md`.

## F3 without_loose, full correction: FAIL

- [BETTER] found, the ordinary conditions together: 133.8 -> 144.3 of 172 placements (+10.5; counted per frame 211 -> 254 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: campus_study -1.0 of 35 (margin 1.0); home_bathtile +9.0 of 15 (margin 1.2); home_glass +0.2 of 15 (margin 1.0); home_ottoman +2.3 of 15 (margin 2.3).
- [WORSE] boxes that are not on their barrel: 1.9 -> 5.9 counted once per arrangement (+4.0; per frame: on nothing 5 -> 12, second box 0 -> 1, wrong color 0 -> 1). Worse above +1.9, better below -1.0.
- [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 2.0 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): campus_light 35 → 34 of 35; lampcool6_bathtile 13 → 15 of 15; lampcool6_ottoman 3 → 9 of 15; lampmid3_bathtile 1 → 15 of 15; lampmid6_bathtile 1 → 15 of 15; lampmid6_ottoman 6 → 1 of 15; lampwarm6_bathtile 1 → 7 of 15; lampwarm6_ottoman 0 → 6 of 15; window_glass 14 → 15 of 15.
- Lost: campus_light_room_01 #1 blue; lampmid6_ottoman_clutter_01 #3 orange; lampmid6_ottoman_core_01 #2 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_edge_01 #2 orange; lampmid6_ottoman_touch_01 #3 orange; lampwarm6_bathtile_close_01 #1 orange.
- Frames with more boxes not on their barrel: lampcool6_bathtile_neg_02 (EMPTY clutter), lampcool6_glass_neg_02 (EMPTY clutter), lampmid3_bathtile_occl_02, lampwarm6_bathtile_edge_01, lampwarm6_glass_neg_02 (EMPTY clutter), lampwarm6_ottoman_clutter_01, lampwarm6_ottoman_neg_02 (EMPTY clutter), lampwarm6_ottoman_occl_02, lampwarm6_ottoman_touch_01, overheaddim_palewood_clutter_01, overheaddim_palewood_neg_02 (EMPTY clutter), window_glass_clutter_01.
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 4 of 21; lampcool6_wood 2 → 13 of 21; lampmid3_wood 1 → 4 of 21; lampmid6_wood 1 → 9 of 21; lampwarm3_wood 1 → 6 of 21; lampwarm6_wood 0 → 13 of 21.
- Pages: `judge_F3_without_loose/judge.md`.

## F4 gray_above, full correction: FAIL

- [BETTER] found, the ordinary conditions together: 133.8 -> 141.6 of 172 placements (+7.8; counted per frame 211 -> 246 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: home_white -1.0 of 29 (margin 1.0); abp_gray +1.0 of 16 (margin 6.0); home_bathtile +9.5 of 15 (margin 1.2); home_ottoman -0.7 of 15 (margin 2.3); uc_palewood -1.0 of 15 (margin 1.0).
- [WORSE] boxes that are not on their barrel: 1.9 -> 6.4 counted once per arrangement (+4.5; per frame: on nothing 5 -> 13, second box 0 -> 0, wrong color 0 -> 5). Worse above +1.9, better below -1.0.
- [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 1.1 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): window_light 28 → 27 of 29; both_abpgray 10 → 11 of 16; lampcool6_bathtile 13 → 15 of 15; lampcool6_ottoman 3 → 5 of 15; lampmid3_bathtile 1 → 15 of 15; lampmid6_bathtile 1 → 15 of 15; lampmid6_ottoman 6 → 1 of 15; lampwarm6_bathtile 1 → 9 of 15; lampwarm6_ottoman 0 → 1 of 15; overheaddim_palewood 13 → 12 of 15.
- Lost: window_light_occl_01 #2 blue; lampcool6_ottoman_touch_01 #3 orange; lampmid6_ottoman_clutter_01 #3 orange; lampmid6_ottoman_core_01 #2 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_edge_01 #2 orange; lampmid6_ottoman_touch_01 #2 blue; lampmid6_ottoman_touch_01 #3 orange; lampwarm6_bathtile_close_01 #1 orange; overheaddim_palewood_core_01 #3 orange; window_glass_clutter_01 #4 orange.
- Frames with more boxes not on their barrel: window_light_far_02, lampcool6_ottoman_clutter_01, lampmid3_bathtile_edge_01, lampmid3_bathtile_neg_02 (EMPTY clutter), lampmid3_bathtile_occl_02, lampmid6_glass_neg_02 (EMPTY clutter), lampmid6_glass_occl_02, lampwarm6_glass_occl_02, lampwarm6_ottoman_clutter_01, lampwarm6_ottoman_neg_02 (EMPTY clutter), lampwarm6_ottoman_occl_02, overheaddim_palewood_clutter_01, window_glass_clutter_01.
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 7 of 21; lampcool6_wood 2 → 14 of 21; lampmid3_ottoman 1 → 0 of 15; lampmid3_wood 1 → 6 of 21; lampmid6_wood 1 → 13 of 21; lampwarm3_wood 1 → 5 of 21; lampwarm6_wood 0 → 15 of 21; window_black 5 → 7 of 26.
- Pages: `judge_F4_gray_above/judge.md`.

## F5 shades_of_gray, full correction: FAIL

- [BETTER] found, the ordinary conditions together: 133.8 -> 138.2 of 172 placements (+4.5; counted per frame 211 -> 232 of 307). Better above +4.0, worse below -10.9.
- [WORSE] found, place by place: campus_study -1.0 of 35 (margin 1.0); abp_gray +1.0 of 16 (margin 6.0); home_bathtile +7.2 of 15 (margin 1.2); home_glass +0.2 of 15 (margin 1.0); home_ottoman -3.0 of 15 (margin 2.3, WORSE).
- [WORSE] boxes that are not on their barrel: 1.9 -> 4.8 counted once per arrangement (+2.9; per frame: on nothing 5 -> 10, second box 0 -> 0, wrong color 0 -> 2). Worse above +1.9, better below -1.0.
- [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 2.2 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): campus_light 35 → 34 of 35; both_abpgray 10 → 11 of 16; lampcool6_bathtile 13 → 15 of 15; lampcool6_ottoman 3 → 0 of 15; lampmid3_bathtile 1 → 15 of 15; lampmid6_bathtile 1 → 15 of 15; lampmid6_ottoman 6 → 0 of 15; lampwarm6_bathtile 1 → 0 of 15; window_glass 14 → 15 of 15.
- Lost: campus_light_room_01 #1 blue; lampcool6_ottoman_core_01 #3 blue; lampcool6_ottoman_touch_01 #2 blue; lampcool6_ottoman_touch_01 #3 orange; lampmid6_ottoman_clutter_01 #3 orange; lampmid6_ottoman_core_01 #2 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_edge_01 #2 orange; lampmid6_ottoman_touch_01 #2 blue; lampmid6_ottoman_touch_01 #3 orange; lampwarm6_bathtile_close_01 #1 orange.
- Frames with more boxes not on their barrel: lampcool6_glass_clutter_01, lampcool6_glass_neg_02 (EMPTY clutter), lampcool6_ottoman_close_01, lampmid3_bathtile_occl_02, lampmid6_ottoman_close_01, lampwarm6_ottoman_occl_02, window_glass_occlx_16 (EMPTY clutter).
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 10 of 21; lampcool6_wood 2 → 18 of 21; lampmid3_ottoman 1 → 0 of 15; lampmid3_wood 1 → 9 of 21; lampmid6_wood 1 → 15 of 21; lampwarm3_wood 1 → 5 of 21; lampwarm6_wood 0 → 15 of 21; window_black 5 → 6 of 26.
- Pages: `judge_F5_shades_of_gray/judge.md`.

## P1 gray_world, partial (alpha chosen in the fold): PASS

- [BETTER] found, the ordinary conditions together: 133.8 -> 143.0 of 172 placements (+9.2; counted per frame 211 -> 243 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: abp_gray +2.0 of 16 (margin 6.0); home_bathtile +8.0 of 15 (margin 1.2); home_glass +0.2 of 15 (margin 1.0); home_ottoman -1.0 of 15 (margin 2.3).
- [within the noise] boxes that are not on their barrel: 1.9 -> 1.1 counted once per arrangement (-0.9; per frame: on nothing 5 -> 4, second box 0 -> 0, wrong color 0 -> 1). Worse above +1.9, better below -1.0.
- [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.2 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): both_abpgray 10 → 12 of 16; lampcool6_bathtile 13 → 15 of 15; lampcool6_ottoman 3 → 1 of 15; lampmid3_bathtile 1 → 7 of 15; lampmid6_bathtile 1 → 15 of 15; lampmid6_ottoman 6 → 2 of 15; lampwarm6_bathtile 1 → 11 of 15; lampwarm6_ottoman 0 → 3 of 15; window_glass 14 → 15 of 15.
- Lost: lampcool6_ottoman_core_01 #3 blue; lampcool6_ottoman_touch_01 #3 orange; lampmid6_ottoman_clutter_01 #3 orange; lampmid6_ottoman_core_01 #2 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_touch_01 #2 blue.
- Frames with more boxes not on their barrel: lampcool6_glass_neg_02 (EMPTY clutter), lampwarm6_bathtile_touch_01, window_glass_clutter_01.
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 7 of 21; lampcool6_wood 2 → 16 of 21; lampmid3_ottoman 1 → 0 of 15; lampmid3_wood 1 → 5 of 21; lampmid6_wood 1 → 17 of 21; lampwarm3_wood 1 → 6 of 21; lampwarm6_wood 0 → 13 of 21.
- Picked per held-out place: home_white: gray_world, alpha 0.5 (gain on the other places +10.08); campus_study: gray_world, alpha 0.5 (gain on the other places +10.08); abp_gray: gray_world, alpha 0.5 (gain on the other places +8.08); home_bathtile: gray_world, alpha 0.5 (gain on the other places +2.33); home_glass: gray_world, alpha 0.5 (gain on the other places +10.08); home_ottoman: gray_world, alpha 0.5 (gain on the other places +10.75); uc_palewood: gray_world, alpha 0.5 (gain on the other places +9.08); abp_white: gray_world, alpha 0.5 (gain on the other places +10.08).
- In-sample, not a verdict: on all eight places the rule picks gray_world, alpha 0.5 (gain +10.08).
- Pages: `judge_P1_gray_world_partial/judge.md`.

## P2 white_patch, partial (alpha chosen in the fold): NO CLEAR DIFFERENCE

- [within the noise] found, the ordinary conditions together: 133.8 -> 133.1 of 172 placements (-0.7; counted per frame 211 -> 208 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: home_glass -0.4 of 15 (margin 1.0); home_ottoman -0.3 of 15 (margin 2.3).
- [within the noise] boxes that are not on their barrel: 1.9 -> 2.7 counted once per arrangement (+0.7; per frame: on nothing 5 -> 4, second box 0 -> 0, wrong color 0 -> 4). Worse above +1.9, better below -1.0.
- [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.0 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): lampcool6_glass 15 → 14 of 15; lampcool6_ottoman 3 → 0 of 15; lampmid3_glass 15 → 14 of 15; lampmid6_ottoman 6 → 5 of 15; lampwarm6_ottoman 0 → 3 of 15.
- Lost: lampcool6_glass_clutter_01 #2 blue; lampcool6_ottoman_core_01 #3 blue; lampcool6_ottoman_touch_01 #2 blue; lampcool6_ottoman_touch_01 #3 orange; lampmid3_glass_clutter_01 #2 blue; lampmid6_ottoman_clutter_01 #3 orange; lampmid6_ottoman_core_01 #2 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_edge_01 #2 orange; lampmid6_ottoman_touch_01 #3 orange.
- Frames with more boxes not on their barrel: lampmid3_glass_clutter_01, lampwarm6_ottoman_close_01, window_glass_clutter_01.
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 6 of 21; lampcool6_wood 2 → 15 of 21; lampmid3_ottoman 1 → 0 of 15; lampmid3_wood 1 → 3 of 21; lampmid6_wood 1 → 8 of 21; lampwarm6_wood 0 → 3 of 21.
- Picked per held-out place: home_white: white_patch, alpha 0.5 (gain on the other places +6.28); campus_study: white_patch, alpha 0.5 (gain on the other places +6.28); abp_gray: white_patch, alpha 0.5 (gain on the other places +6.28); home_bathtile: no correction (today) (gain on the other places +0.00); home_glass: white_patch, alpha 0.5 (gain on the other places +7.08); home_ottoman: white_patch, alpha 0.5 (gain on the other places +6.95); uc_palewood: white_patch, alpha 0.5 (gain on the other places +6.28); abp_white: white_patch, alpha 0.5 (gain on the other places +6.28).
- In-sample, not a verdict: on all eight places the rule picks white_patch, alpha 0.5 (gain +6.28).
- Pages: `judge_P2_white_patch_partial/judge.md`.

## P3 without_loose, partial (alpha chosen in the fold) (primary): FAIL

- [within the noise] found, the ordinary conditions together: 133.8 -> 134.8 of 172 placements (+1.0; counted per frame 211 -> 215 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: home_bathtile +1.0 of 15 (margin 1.2).
- [WORSE] boxes that are not on their barrel: 1.9 -> 4.7 counted once per arrangement (+2.7; per frame: on nothing 5 -> 7, second box 0 -> 0, wrong color 0 -> 0). Worse above +1.9, better below -1.0.
- [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 2.0 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): lampcool6_bathtile 13 → 14 of 15; lampcool6_ottoman 3 → 4 of 15; lampmid3_bathtile 1 → 2 of 15; lampmid6_bathtile 1 → 3 of 15; lampmid6_ottoman 6 → 5 of 15.
- Lost: lampcool6_ottoman_touch_01 #3 orange; lampmid6_ottoman_touch_01 #2 blue.
- Frames with more boxes not on their barrel: lampmid6_bathtile_touch_01, overheaddim_palewood_clutter_01, overheaddim_palewood_neg_02 (EMPTY clutter).
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 3 of 21; lampcool6_wood 2 → 3 of 21; lampmid6_wood 1 → 3 of 21; lampwarm6_wood 0 → 1 of 21.
- Picked per held-out place: home_white: without_loose, alpha 0.25 (gain on the other places +1.28); campus_study: without_loose, alpha 0.25 (gain on the other places +1.28); abp_gray: without_loose, alpha 0.25 (gain on the other places +1.28); home_bathtile: without_loose, alpha 0.25 (gain on the other places +0.53); home_glass: without_loose, alpha 0.25 (gain on the other places +1.08); home_ottoman: without_loose, alpha 0.25 (gain on the other places +0.95); uc_palewood: without_loose, alpha 0.75 (gain on the other places +11.37); abp_white: without_loose, alpha 0.25 (gain on the other places +1.28).
- In-sample, not a verdict: on all eight places the rule picks without_loose, alpha 0.25 (gain +1.28).
- Pages: `judge_P3_without_loose_partial/judge.md`.

## P4 gray_above, partial (alpha chosen in the fold): PASS (WEAK)

- [BETTER] found, the ordinary conditions together: 133.8 -> 138.5 of 172 placements (+4.7; counted per frame 211 -> 234 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: home_white -1.0 of 29 (margin 1.0); abp_gray +1.0 of 16 (margin 6.0); home_bathtile +6.5 of 15 (margin 1.2); home_glass +0.2 of 15 (margin 1.0); home_ottoman -1.0 of 15 (margin 2.3); uc_palewood -1.0 of 15 (margin 1.0).
- [within the noise] boxes that are not on their barrel: 1.9 -> 2.5 counted once per arrangement (+0.5; per frame: on nothing 5 -> 7, second box 0 -> 2, wrong color 0 -> 1). Worse above +1.9, better below -1.0.
- [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.2 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): window_light 28 → 27 of 29; both_abpgray 10 → 11 of 16; lampcool6_bathtile 13 → 15 of 15; lampmid3_bathtile 1 → 6 of 15; lampmid6_bathtile 1 → 15 of 15; lampmid6_ottoman 6 → 2 of 15; lampwarm6_bathtile 1 → 6 of 15; lampwarm6_ottoman 0 → 1 of 15; overheaddim_palewood 13 → 12 of 15; window_glass 14 → 15 of 15.
- Lost: window_light_far_02 #2 orange; lampcool6_ottoman_touch_01 #3 orange; lampmid6_ottoman_clutter_01 #3 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_touch_01 #2 blue; lampmid6_ottoman_touch_01 #3 orange; overheaddim_palewood_core_01 #3 orange.
- Frames with more boxes not on their barrel: lampmid6_glass_neg_02 (EMPTY clutter), lampmid6_glass_occl_02, lampwarm6_bathtile_clutter_01, lampwarm6_bathtile_touch_01, lampwarm6_ottoman_clutter_01, window_glass_clutter_01.
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 5 of 21; lampcool6_wood 2 → 13 of 21; lampmid3_wood 1 → 3 of 21; lampmid6_wood 1 → 7 of 21; lampwarm6_wood 0 → 7 of 21.
- Picked per held-out place: home_white: gray_above, alpha 0.75 (gain on the other places +9.67); campus_study: gray_above, alpha 0.75 (gain on the other places +8.67); abp_gray: gray_above, alpha 0.75 (gain on the other places +7.67); home_bathtile: gray_above, alpha 0.5 (gain on the other places +1.67); home_glass: gray_above, alpha 0.75 (gain on the other places +8.67); home_ottoman: gray_above, alpha 0.75 (gain on the other places +10.00); uc_palewood: gray_above, alpha 0.75 (gain on the other places +8.67); abp_white: gray_above, alpha 0.75 (gain on the other places +8.67).
- In-sample, not a verdict: on all eight places the rule picks gray_above, alpha 0.75 (gain +8.67).
- Pages: `judge_P4_gray_above_partial/judge.md`.

## P5 shades_of_gray, partial (alpha chosen in the fold): NO CLEAR DIFFERENCE

- [within the noise] found, the ordinary conditions together: 133.8 -> 132.7 of 172 placements (-1.1; counted per frame 211 -> 208 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: home_glass +0.2 of 15 (margin 1.0); home_ottoman -1.3 of 15 (margin 2.3).
- [BETTER] boxes that are not on their barrel: 1.9 -> 0.8 counted once per arrangement (-1.1; per frame: on nothing 5 -> 4, second box 0 -> 0, wrong color 0 -> 0). Worse above +1.9, better below -1.0.
- [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.2 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): lampcool6_ottoman 3 → 0 of 15; lampmid6_ottoman 6 → 3 of 15; lampwarm6_ottoman 0 → 2 of 15; window_glass 14 → 15 of 15.
- Lost: lampcool6_ottoman_core_01 #3 blue; lampcool6_ottoman_touch_01 #2 blue; lampcool6_ottoman_touch_01 #3 orange; lampmid6_ottoman_core_01 #2 orange; lampmid6_ottoman_core_01 #4 orange; lampmid6_ottoman_touch_01 #2 blue.
- Frames with more boxes not on their barrel: lampcool6_glass_neg_02 (EMPTY clutter), window_glass_clutter_01.
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 3 of 21; lampcool6_wood 2 → 11 of 21; lampmid3_ottoman 1 → 0 of 15; lampmid3_wood 1 → 3 of 21; lampmid6_wood 1 → 5 of 21; lampwarm6_wood 0 → 2 of 21.
- Picked per held-out place: home_white: shades_of_gray, alpha 0.5 (gain on the other places +6.50); campus_study: shades_of_gray, alpha 0.5 (gain on the other places +6.50); abp_gray: shades_of_gray, alpha 0.5 (gain on the other places +6.50); home_bathtile: no correction (today) (gain on the other places +0.00); home_glass: shades_of_gray, alpha 0.5 (gain on the other places +6.50); home_ottoman: shades_of_gray, alpha 0.5 (gain on the other places +7.50); uc_palewood: shades_of_gray, alpha 0.5 (gain on the other places +5.50); abp_white: shades_of_gray, alpha 0.5 (gain on the other places +6.50).
- In-sample, not a verdict: on all eight places the rule picks shades_of_gray, alpha 0.5 (gain +6.50).
- Pages: `judge_P5_shades_of_gray_partial/judge.md`.

## U3 today's mask plus the without_loose-corrected paint where today paints nothing (alpha in the fold): FAIL

- [within the noise] found, the ordinary conditions together: 133.8 -> 135.5 of 172 placements (+1.7; counted per frame 211 -> 217 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: home_bathtile +1.0 of 15 (margin 1.2); home_ottoman +0.7 of 15 (margin 2.3).
- [WORSE] boxes that are not on their barrel: 1.9 -> 5.4 counted once per arrangement (+3.5; per frame: on nothing 5 -> 9, second box 0 -> 1, wrong color 0 -> 0). Worse above +1.9, better below -1.0.
- [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 2.0 per arrangement (margin 1.0).
- By condition, found per frame (only those that moved): lampcool6_bathtile 13 → 14 of 15; lampcool6_ottoman 3 → 5 of 15; lampmid3_bathtile 1 → 2 of 15; lampmid6_bathtile 1 → 3 of 15.
- Lost: lampcool6_ottoman_touch_01 #2 blue.
- Frames with more boxes not on their barrel: lampmid3_bathtile_core_01, lampmid6_bathtile_touch_01, overheaddim_palewood_clutter_01, overheaddim_palewood_neg_02 (EMPTY clutter).
- Extreme conditions (report only), found per frame: lampcool3_wood 2 → 3 of 21; lampcool6_wood 2 → 3 of 21; lampmid6_wood 1 → 3 of 21; lampwarm6_wood 0 → 1 of 21.
- Picked per held-out place: home_white: without_loose, alpha 0.25, added to today's mask (gain on the other places +1.17); campus_study: without_loose, alpha 0.25, added to today's mask (gain on the other places +1.17); abp_gray: without_loose, alpha 0.25, added to today's mask (gain on the other places +1.17); home_bathtile: without_loose, alpha 0.25, added to today's mask (gain on the other places +0.67); home_glass: without_loose, alpha 0.25, added to today's mask (gain on the other places +1.17); home_ottoman: without_loose, alpha 0.25, added to today's mask (gain on the other places +0.50); uc_palewood: without_loose, alpha 0.5, added to today's mask (gain on the other places +7.63); abp_white: without_loose, alpha 0.25, added to today's mask (gain on the other places +1.17).
- In-sample, not a verdict: on all eight places the rule picks without_loose, alpha 0.25, added to today's mask (gain +1.17).
- Pages: `judge_U3_without_loose_added/judge.md`.
