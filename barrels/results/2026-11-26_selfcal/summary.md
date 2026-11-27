# Self-calibration (2026-11-26_selfcal): the judged runs

Made by `python barrels/experiments/2026-11-26_selfcal/run.py`. Train frames only. Every verdict is the standard pass rule's (`docs/EVAL.md`), leave one place out for the four families.

## Every judged candidate

| candidate | verdict | found, placements (of 172) | found, per frame (of 307) | boxes not on their barrel (per arrangement) | boxes on empty frames (clean) | gained / lost | places that moved |
|---|---|---|---|---|---|---|---|
| A_found | PASS | 133.8 -> 141.0 (+7.2) | 211 -> 223 | 1.93 -> 2.13 | 0 -> 0 (0 -> 0) | 12 / 0 | abp_gray +5.0, home_bathtile +0.2, home_ottoman +2.0 |
| B_local | PASS | 133.8 -> 146.0 (+12.2) | 211 -> 243 | 1.93 -> 2.18 | 0 -> 0 (0 -> 0) | 32 / 0 | abp_gray +5.0, home_bathtile +5.5, home_ottoman +1.7 |
| B_frame | PASS | 133.8 -> 143.1 (+9.2) | 211 -> 230 | 1.93 -> 1.93 | 0 -> 0 (0 -> 0) | 19 / 0 | abp_gray +5.0, home_bathtile +1.2, home_ottoman +3.0 |
| AB | PASS | 133.8 -> 147.6 (+13.8) | 211 -> 248 | 1.93 -> 2.18 | 0 -> 0 (0 -> 0) | 37 / 0 | abp_gray +5.0, home_bathtile +5.8, home_ottoman +3.0 |
| AB_noguard | FAIL | 133.8 -> 152.6 (+18.8) | 211 -> 261 | 1.93 -> 29.23 | 0 -> 7 (0 -> 0) | 50 / 0 | abp_gray +5.0, home_bathtile +5.8, home_ottoman +7.0, abp_white +1.0 |

## The setting each fold picked

| family | held-out place | setting picked on the other places |
|---|---|---|
| AB | abp_gray | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| AB | abp_white | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| AB | campus_study | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| AB | home_bathtile | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| AB | home_black | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| AB | home_glass | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| AB | home_ottoman | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.01} |
| AB | home_white | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| AB | home_wooddesk | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| AB | uc_palewood | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | abp_gray | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | abp_white | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | campus_study | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | home_bathtile | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | home_black | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | home_glass | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | home_ottoman | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | home_white | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | home_wooddesk | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| A_found | uc_palewood | {"found_flags": "any", "hue_move_max": 6.0, "flood_max": 0.03} |
| B_frame | abp_gray | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.03} |
| B_frame | abp_white | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.03} |
| B_frame | campus_study | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.03} |
| B_frame | home_bathtile | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| B_frame | home_black | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.03} |
| B_frame | home_glass | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.03} |
| B_frame | home_ottoman | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.01} |
| B_frame | home_white | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.03} |
| B_frame | home_wooddesk | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.03} |
| B_frame | uc_palewood | {"rel_margin": 1.0, "hue_move_max": 10.0, "flood_max": 0.03} |
| B_local | abp_gray | {"rel_margin": 1.0} |
| B_local | abp_white | {"rel_margin": 1.0} |
| B_local | campus_study | {"rel_margin": 1.0} |
| B_local | home_bathtile | {"rel_margin": 1.0} |
| B_local | home_black | {"rel_margin": 1.0} |
| B_local | home_glass | {"rel_margin": 1.0} |
| B_local | home_ottoman | {"rel_margin": 1.0} |
| B_local | home_white | {"rel_margin": 1.0} |
| B_local | home_wooddesk | {"rel_margin": 1.0} |
| B_local | uc_palewood | {"rel_margin": 1.0} |

## Seeds per condition (AB, each place with its own held-out setting)

```
condition              class       frm    brl    fix   cand    off   xtr1    xtr    emp   fr.b  fr.sd  s.fnd  s.bdy  s.str  s.off sd.emp  moved paint.out1 paint.out2
window_light           ordinary     16     29     28     28      0      0      0      0     14     11     18      4      0      0      0      6       3126       4823
campus_light           ordinary     21     35     35     35      0      0      0      0     17     12     20      7      0      0      0     10      27960      28363
both_abpgray           ordinary      8     16     10     15      1      0      0      0      7      4      5      3      4      0      0      4      34995      38188
lampcool6_bathtile     ordinary      7     15     13     14      0      0      0      0      6      4      4      4      3      0      0      4       9687      10902
lampcool6_glass        ordinary      7     15     15     15      0      0      0      0      6      4      9      2      0      0      0      3      30607      30744
lampcool6_ottoman      ordinary      7     15      3     11      0      0      0      0      6      3      0      2      5      0      0      3       8688       9426
lampmid3_bathtile      ordinary      7     15      1     10      0      0      1      0      6      4      0      6      4      0      0      2      18309      20529
lampmid3_glass         ordinary      7     15     15     15      0      1      1      0      6      4      8      2      1      0      0      1      29717      30652
lampmid6_bathtile      ordinary      7     15      1      9      1      0      0      0      6      3      0      4      4      0      0      3      31540      38078
lampmid6_glass         ordinary      7     15     15     15      0      1      1      0      6      4      8      2      0      0      0      1      27777      27777
lampmid6_ottoman       ordinary      7     15      6      7      0      0      0      0      6      4      1      0      3      0      0      3       7058       7134
lampwarm6_bathtile     ordinary      7     15      1      6      0      0      0      0      6      3      0      4      2      0      0      1      94435      97991
lampwarm6_glass        ordinary      7     15     15     15      0      1      1      0      6      4      8      2      0      0      0      1      23637      23637
lampwarm6_ottoman      ordinary      7     15      0      0      0      1      1      0      6      0      0      0      0      0      0      0       8135       8135
overheaddim_palewood   ordinary      7     15     13     13      0      1      1      0      6      4      3      5      3      0      0      4     155091     162798
window_abpwhite        ordinary     17     32     26     26      0      0      0      0     16     15     15      2      0      0      0     13      69519      71028
window_glass           ordinary      8     15     14     14      1      0      0      0      6      4      8      2      0      0      0      2      53935      53938
lampcool3_wood         extreme      10     21      2     11      0      0      1      0      9      6      0      4      7      0      0      4       6754       9866
lampcool6_wood         extreme      10     21      2      8      2      2      2      0      9      4      0      3      5      0      0      4       8825       8865
lampmid3_ottoman       extreme       7     15      1      1      1      0      0      0      6      0      0      0      0      0      0      0       4945       4945
lampmid3_wood          extreme      10     21      1     11      1      1      1      0      9      6      0      3      8      0      0      2      20352      27853
lampmid6_wood          extreme      10     21      1      9      1      0      0      0      9      5      0      5      5      0      0      1      40087      44482
lampwarm3_wood         extreme      10     21      1      6      0      0      0      0      9      5      0      2      3      0      0      0      50238      50238
lampwarm6_wood         extreme      10     21      0      6      0      1      1      0      9      4      0      4      4      0      0      3      63876      69330
window_black           extreme      10     26      5      8      1      0      0      0      9      3      0      0      3      0      0      3       4806       5557
ALL ORDINARY                       154    307    211    248      3      5      6      0    132     87    107     51     29      0      0     61     634216     664143
```

fix / cand = barrels found per frame by the fixed detector / the candidate; fr.b = frames with barrels; fr.sd = of those, frames with at least one kept seed; s.fnd / s.bdy / s.str = kept seeds by kind; s.off = kept seeds that are not on a hand box; sd.emp = empty frames with a kept seed; moved = frames whose range moved; paint.out = painted pixels outside the hand boxes (grown 4 px), first and second pass.

## The guards on seed candidates that are not on a barrel

| conditions | frame | seed kind | verdict | n |
|---|---|---|---|---|
| extreme | clutter | body | not_two_colors | 1 |
| extreme | clutter | stripe | body_like_surround | 2 |
| extreme | clutter | stripe | not_two_colors | 6 |
| extreme | clutter | stripe | stripe_not_painted | 4 |
| extreme | empty | body | not_two_colors | 1 |
| extreme | empty | stripe | not_two_colors | 7 |
| extreme | plain | body | body_not_painted | 7 |
| extreme | plain | body | not_two_colors | 12 |
| extreme | plain | stripe | not_two_colors | 10 |
| extreme | plain | stripe | stripe_not_painted | 3 |
| ordinary | clutter | body | body_not_painted | 7 |
| ordinary | clutter | body | not_two_colors | 11 |
| ordinary | clutter | body | too_small | 1 |
| ordinary | clutter | stripe | body_like_surround | 5 |
| ordinary | clutter | stripe | not_two_colors | 23 |
| ordinary | clutter | stripe | off_frame | 5 |
| ordinary | clutter | stripe | stripe_not_painted | 10 |
| ordinary | clutter | stripe | too_small | 8 |
| ordinary | empty | body | body_not_painted | 8 |
| ordinary | empty | body | not_two_colors | 8 |
| ordinary | empty | body | too_small | 1 |
| ordinary | empty | stripe | body_like_surround | 2 |
| ordinary | empty | stripe | not_two_colors | 16 |
| ordinary | empty | stripe | off_frame | 2 |
| ordinary | empty | stripe | stripe_not_painted | 7 |
| ordinary | empty | stripe | too_small | 3 |
| ordinary | plain | body | body_not_painted | 17 |
| ordinary | plain | body | not_two_colors | 6 |
| ordinary | plain | body | too_small | 7 |
| ordinary | plain | stripe | body_like_surround | 1 |
| ordinary | plain | stripe | not_two_colors | 26 |
| ordinary | plain | stripe | off_frame | 3 |
| ordinary | plain | stripe | stripe_not_painted | 6 |
| ordinary | plain | stripe | too_small | 6 |

## REPORT ONLY: the colors carried across the frames of one condition (one table, one light)

Ordinary conditions, found per placement: per frame 147.6, with the session's readings 150.4 (per frame counted 248 and 253 of 307); boxes not on their barrel 2.2 and 3.8. Not a judged candidate: it uses other frames of the same place.

| condition | class | barrels | fixed | per frame | session | extra boxes per frame | extra boxes session |
|---|---|---|---|---|---|---|---|
| window_light | ordinary | 29 | 28 | 28 | 28 | 0 | 0 |
| campus_light | ordinary | 35 | 35 | 35 | 35 | 0 | 0 |
| both_abpgray | ordinary | 16 | 10 | 15 | 15 | 0 | 0 |
| lampcool6_bathtile | ordinary | 15 | 13 | 14 | 15 | 0 | 0 |
| lampcool6_glass | ordinary | 15 | 15 | 15 | 15 | 0 | 1 |
| lampcool6_ottoman | ordinary | 15 | 3 | 11 | 12 | 0 | 0 |
| lampmid3_bathtile | ordinary | 15 | 1 | 10 | 10 | 1 | 1 |
| lampmid3_glass | ordinary | 15 | 15 | 15 | 15 | 1 | 1 |
| lampmid6_bathtile | ordinary | 15 | 1 | 9 | 10 | 0 | 0 |
| lampmid6_glass | ordinary | 15 | 15 | 15 | 15 | 1 | 3 |
| lampmid6_ottoman | ordinary | 15 | 6 | 7 | 7 | 0 | 0 |
| lampwarm6_bathtile | ordinary | 15 | 1 | 6 | 6 | 0 | 0 |
| lampwarm6_glass | ordinary | 15 | 15 | 15 | 15 | 1 | 1 |
| lampwarm6_ottoman | ordinary | 15 | 0 | 0 | 0 | 1 | 1 |
| overheaddim_palewood | ordinary | 15 | 13 | 13 | 13 | 1 | 2 |
| window_abpwhite | ordinary | 32 | 26 | 26 | 28 | 0 | 0 |
| window_glass | ordinary | 15 | 14 | 14 | 14 | 0 | 0 |
| lampcool3_wood | extreme | 21 | 2 | 11 | 10 | 1 | 1 |
| lampcool6_wood | extreme | 21 | 2 | 8 | 12 | 2 | 2 |
| lampmid3_ottoman | extreme | 15 | 1 | 1 | 1 | 0 | 0 |
| lampmid3_wood | extreme | 21 | 1 | 11 | 10 | 1 | 1 |
| lampmid6_wood | extreme | 21 | 1 | 9 | 9 | 0 | 0 |
| lampwarm3_wood | extreme | 21 | 1 | 6 | 6 | 0 | 0 |
| lampwarm6_wood | extreme | 21 | 0 | 6 | 6 | 1 | 1 |
| window_black | extreme | 26 | 5 | 8 | 16 | 0 | 0 |

## Sheets (not committed)

- `2026-11-26_selfcal/sheets/AB_gained_01.png`
- `2026-11-26_selfcal/sheets/AB_gained_02.png`
- `2026-11-26_selfcal/sheets/AB_gained_03.png`
- `2026-11-26_selfcal/sheets/AB_boxes_01.png`
