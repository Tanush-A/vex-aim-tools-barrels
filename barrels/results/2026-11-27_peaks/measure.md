# Peaks, parts A and B (descriptive; train frames only)

Per frame and color: the barrels' own hue (mode of the hand-box cores) against the largest peak each finder finds. `|err|` = |found - true| in hue units (log R/B for F4). `ok` = within 3, `fooled` = 5 or more. `rank` = where the barrels' own peak stands among the finder's local peaks (1 = it is the largest; 0 = no separate peak). F4: ok = inside the barrels' own 10-90 % range of log R/B.

## ordinary, orange: 97 frames

| finder | ok (<=3) | fooled (>=5) | none | median abs err | rank 1 | rank 2-3 | rank 4+ | no separate peak |
|---|---|---|---|---|---|---|---|---|
| F0_naive | 38/97 | 56 | 0 | 6.0 | 28 | 41 | 27 | 1 |
| F0_naive_hv | 23/97 | 74 | 0 | 8.0 | 15 | 46 | 30 | 6 |
| F1_sat | 75/97 | 21 | 0 | 1.0 | 71 | 22 | 3 | 1 |
| F2_rows | 45/97 | 50 | 0 | 5.0 | 31 | 44 | 21 | 1 |
| F3_small | 68/97 | 27 | 0 | 1.0 | 60 | 31 | 5 | 1 |
| F4_logrb | 54/97 (inside 10-90 %) | 43 | 0 | 0.15 (log units) | | | | |
| F5_pair | 82/97 | 11 | 4 | 0.0 | 79 | 7 | 0 | 11 |
| F6_pair_small | 89/97 | 4 | 4 | 1.0 | 86 | 0 | 0 | 11 |
| F7_pair_sat | 89/97 | 4 | 4 | 0.0 | 86 | 1 | 0 | 10 |

### ordinary, orange, by condition: ok / fooled of frames (median true mode hue; median purity; median body share)

| condition | frames | true hue | true S | purity | body share | F0_naive | F0_naive_hv | F1_sat | F2_rows | F3_small | F5_pair | F6_pair_small | F7_pair_sat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| both_abpgray | 5 | 2 | 232 | 1.00 | 0.007 | 0/4 r1=0 | 0/5 r1=0 | 4/0 r1=4 | 0/4 r1=0 | 1/2 r1=0 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| campus_light | 14 | 8 | 216 | 1.00 | 0.039 | 11/3 r1=11 | 5/9 r1=5 | 14/0 r1=14 | 12/2 r1=12 | 13/1 r1=13 | 13/1 r1=12 | 13/1 r1=12 | 13/1 r1=12 |
| lampcool6_bathtile | 5 | 9 | 216 | 1.00 | 0.004 | 0/5 r1=0 | 0/5 r1=0 | 2/3 r1=2 | 0/5 r1=0 | 1/4 r1=1 | 3/2 r1=3 | 5/0 r1=5 | 5/0 r1=5 |
| lampcool6_glass | 5 | 8 | 216 | 1.00 | 0.011 | 4/1 r1=4 | 1/4 r1=1 | 5/0 r1=5 | 4/1 r1=4 | 5/0 r1=5 | 5/0 r1=4 | 5/0 r1=4 | 5/0 r1=4 |
| lampcool6_ottoman | 5 | 17 | 200 | 1.00 | 0.165 | 2/3 r1=2 | 0/5 r1=0 | 5/0 r1=5 | 4/1 r1=4 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=5 |
| lampmid3_bathtile | 5 | 10 | 216 | 1.00 | 0.005 | 0/5 r1=0 | 0/5 r1=0 | 1/4 r1=1 | 0/5 r1=0 | 1/4 r1=1 | 4/1 r1=4 | 5/0 r1=5 | 5/0 r1=5 |
| lampmid3_glass | 5 | 8 | 216 | 1.00 | 0.043 | 1/4 r1=1 | 1/4 r1=1 | 5/0 r1=5 | 1/4 r1=1 | 5/0 r1=5 | 4/1 r1=4 | 4/1 r1=4 | 4/1 r1=4 |
| lampmid6_bathtile | 5 | 9 | 216 | 0.97 | 0.004 | 0/5 r1=0 | 0/5 r1=0 | 1/4 r1=1 | 0/5 r1=0 | 1/4 r1=1 | 2/3 r1=2 | 5/0 r1=5 | 5/0 r1=5 |
| lampmid6_glass | 5 | 8 | 216 | 1.00 | 0.061 | 1/4 r1=1 | 0/5 r1=0 | 5/0 r1=5 | 1/4 r1=1 | 5/0 r1=5 | 4/1 r1=4 | 4/1 r1=4 | 4/1 r1=4 |
| lampmid6_ottoman | 5 | 15 | 216 | 1.00 | 0.080 | 2/3 r1=0 | 2/3 r1=0 | 5/0 r1=5 | 4/1 r1=0 | 5/0 r1=4 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=5 |
| lampwarm6_bathtile | 5 | 8 | 216 | 0.88 | 0.005 | 0/5 r1=0 | 0/5 r1=0 | 0/5 r1=0 | 0/5 r1=0 | 1/4 r1=1 | 3/1 r1=3 | 4/0 r1=4 | 3/1 r1=3 |
| lampwarm6_glass | 5 | 7 | 216 | 1.00 | 0.028 | 2/3 r1=1 | 1/4 r1=1 | 5/0 r1=5 | 2/3 r1=1 | 5/0 r1=5 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampwarm6_ottoman | 5 | 14 | 216 | 0.93 | 0.075 | 2/3 r1=0 | 2/3 r1=0 | 3/2 r1=3 | 3/2 r1=0 | 4/1 r1=1 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=5 |
| overheaddim_palewood | 5 | 8 | 216 | 0.92 | 0.011 | 5/0 r1=0 | 5/0 r1=1 | 5/0 r1=1 | 5/0 r1=0 | 3/2 r1=0 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=5 |
| window_abpwhite | 3 | 7 | 216 | 0.96 | 0.007 | 0/3 r1=0 | 0/3 r1=0 | 0/3 r1=0 | 0/3 r1=0 | 0/3 r1=0 | 3/0 r1=3 | 3/0 r1=3 | 3/0 r1=3 |
| window_glass | 5 | 7 | 216 | 1.00 | 0.008 | 4/1 r1=4 | 4/1 r1=4 | 5/0 r1=5 | 4/1 r1=4 | 5/0 r1=5 | 4/1 r1=4 | 4/1 r1=4 | 5/0 r1=4 |
| window_light | 10 | 8 | 216 | 1.00 | 0.011 | 4/4 r1=4 | 2/8 r1=2 | 10/0 r1=10 | 5/4 r1=4 | 8/2 r1=8 | 9/0 r1=8 | 9/0 r1=8 | 9/0 r1=9 |

## ordinary, blue: 92 frames

| finder | ok (<=3) | fooled (>=5) | none | median abs err | rank 1 | rank 2-3 | rank 4+ | no separate peak |
|---|---|---|---|---|---|---|---|---|
| F0_naive | 68/92 | 22 | 0 | 1.0 | 53 | 15 | 19 | 5 |
| F0_naive_hv | 48/92 | 38 | 0 | 2.0 | 41 | 10 | 28 | 13 |
| F1_sat | 83/92 | 9 | 0 | 0.0 | 79 | 7 | 0 | 6 |
| F2_rows | 69/92 | 22 | 0 | 1.0 | 55 | 14 | 19 | 4 |
| F3_small | 56/92 | 36 | 0 | 1.0 | 54 | 15 | 22 | 1 |
| F4_logrb | 64/92 (inside 10-90 %) | 21 | 7 | 0.07 (log units) | | | | |
| F5_pair | 88/92 | 4 | 0 | 0.0 | 87 | 2 | 0 | 3 |
| F6_pair_small | 88/92 | 3 | 1 | 0.0 | 86 | 3 | 0 | 3 |
| F7_pair_sat | 83/92 | 8 | 0 | 0.0 | 79 | 5 | 2 | 6 |

### ordinary, blue, by condition: ok / fooled of frames (median true mode hue; median purity; median body share)

| condition | frames | true hue | true S | purity | body share | F0_naive | F0_naive_hv | F1_sat | F2_rows | F3_small | F5_pair | F6_pair_small | F7_pair_sat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| both_abpgray | 5 | 109 | 232 | 0.91 | 0.004 | 4/0 r1=3 | 3/2 r1=2 | 3/2 r1=3 | 4/0 r1=4 | 5/0 r1=5 | 4/1 r1=4 | 4/0 r1=4 | 4/1 r1=4 |
| campus_light | 12 | 106 | 232 | 0.95 | 0.029 | 3/9 r1=3 | 4/6 r1=1 | 12/0 r1=12 | 3/9 r1=3 | 1/11 r1=1 | 11/1 r1=11 | 11/1 r1=11 | 11/1 r1=11 |
| lampcool6_bathtile | 4 | 102 | 208 | 1.00 | 0.009 | 4/0 r1=4 | 4/0 r1=3 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampcool6_glass | 4 | 108 | 232 | 1.00 | 0.007 | 0/4 r1=0 | 0/3 r1=0 | 4/0 r1=4 | 0/4 r1=0 | 0/4 r1=0 | 4/0 r1=4 | 4/0 r1=3 | 4/0 r1=4 |
| lampcool6_ottoman | 4 | 103 | 168 | 1.00 | 0.077 | 4/0 r1=4 | 2/2 r1=2 | 4/0 r1=3 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=3 |
| lampmid3_bathtile | 4 | 100 | 72 | 0.99 | 0.004 | 3/1 r1=2 | 4/0 r1=4 | 2/2 r1=2 | 3/1 r1=2 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 3/1 r1=3 |
| lampmid3_glass | 4 | 109 | 232 | 1.00 | 0.020 | 2/2 r1=0 | 3/1 r1=3 | 4/0 r1=4 | 2/2 r1=0 | 1/3 r1=0 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampmid6_bathtile | 4 | 98 | 80 | 1.00 | 0.006 | 4/0 r1=4 | 4/0 r1=4 | 2/2 r1=2 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 2/1 r1=2 |
| lampmid6_glass | 4 | 108 | 232 | 1.00 | 0.039 | 3/1 r1=3 | 0/4 r1=0 | 4/0 r1=4 | 3/1 r1=3 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampmid6_ottoman | 4 | 104 | 136 | 1.00 | 0.034 | 4/0 r1=4 | 3/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampwarm6_bathtile | 4 | 74 | 40 | 1.00 | 0.000 | 3/1 r1=3 | 2/2 r1=2 | 3/1 r1=3 | 3/1 r1=3 | 3/1 r1=3 | 2/2 r1=2 | 2/2 r1=2 | 0/4 r1=0 |
| lampwarm6_glass | 4 | 109 | 216 | 1.00 | 0.018 | 4/0 r1=4 | 3/1 r1=3 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampwarm6_ottoman | 4 | 104 | 56 | 1.00 | 0.018 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=2 |
| overheaddim_palewood | 4 | 107 | 216 | 1.00 | 0.003 | 3/1 r1=2 | 3/1 r1=2 | 3/1 r1=2 | 3/1 r1=2 | 4/0 r1=3 | 4/0 r1=3 | 4/0 r1=3 | 4/0 r1=3 |
| window_abpwhite | 14 | 108 | 232 | 1.00 | 0.014 | 13/1 r1=13 | 0/14 r1=0 | 14/0 r1=14 | 14/0 r1=14 | 10/4 r1=10 | 14/0 r1=14 | 14/0 r1=14 | 14/0 r1=14 |
| window_glass | 4 | 109 | 232 | 0.98 | 0.006 | 4/0 r1=0 | 4/0 r1=4 | 3/1 r1=3 | 4/0 r1=0 | 0/4 r1=0 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| window_light | 9 | 109 | 232 | 1.00 | 0.009 | 6/2 r1=0 | 5/2 r1=3 | 9/0 r1=7 | 6/3 r1=0 | 0/9 r1=0 | 9/0 r1=9 | 9/0 r1=9 | 9/0 r1=9 |

## extreme, orange: 35 frames

| finder | ok (<=3) | fooled (>=5) | none | median abs err | rank 1 | rank 2-3 | rank 4+ | no separate peak |
|---|---|---|---|---|---|---|---|---|
| F0_naive | 7/35 | 26 | 0 | 6.0 | 7 | 9 | 7 | 12 |
| F0_naive_hv | 5/35 | 30 | 0 | 7.0 | 5 | 4 | 11 | 15 |
| F1_sat | 9/35 | 25 | 0 | 5.0 | 9 | 18 | 0 | 8 |
| F2_rows | 7/35 | 26 | 0 | 6.0 | 7 | 11 | 6 | 11 |
| F3_small | 8/35 | 25 | 0 | 7.0 | 8 | 19 | 5 | 3 |
| F4_logrb | 23/35 (inside 10-90 %) | 11 | 1 | 0.21 (log units) | | | | |
| F5_pair | 28/35 | 2 | 3 | 1.0 | 27 | 3 | 0 | 5 |
| F6_pair_small | 29/35 | 2 | 3 | 1.0 | 28 | 2 | 0 | 5 |
| F7_pair_sat | 29/35 | 2 | 3 | 1.0 | 29 | 0 | 1 | 5 |

### extreme, orange, by condition: ok / fooled of frames (median true mode hue; median purity; median body share)

| condition | frames | true hue | true S | purity | body share | F0_naive | F0_naive_hv | F1_sat | F2_rows | F3_small | F5_pair | F6_pair_small | F7_pair_sat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lampcool3_wood | 4 | 14 | 200 | 0.95 | 0.014 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 3/1 r1=3 | 3/1 r1=3 | 4/0 r1=4 |
| lampcool6_wood | 4 | 12 | 216 | 0.98 | 0.014 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampmid3_ottoman | 5 | 14 | 200 | 1.00 | 0.406 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=5 | 2/0 r1=2 | 2/0 r1=2 | 2/0 r1=2 |
| lampmid3_wood | 4 | 14 | 200 | 0.64 | 0.014 | 0/2 r1=0 | 0/4 r1=0 | 0/3 r1=0 | 0/2 r1=0 | 0/4 r1=0 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampmid6_wood | 4 | 12 | 216 | 0.92 | 0.013 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| lampwarm3_wood | 4 | 13 | 216 | 0.49 | 0.014 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/2 r1=0 | 3/0 r1=3 | 4/0 r1=4 | 4/0 r1=4 |
| lampwarm6_wood | 4 | 10 | 216 | 0.88 | 0.015 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 0/4 r1=0 | 4/0 r1=4 | 4/0 r1=4 | 4/0 r1=4 |
| window_black | 6 | 18 | 144 | 1.00 | 0.128 | 2/4 r1=2 | 0/6 r1=0 | 4/2 r1=4 | 2/4 r1=2 | 3/3 r1=3 | 4/1 r1=3 | 4/1 r1=3 | 3/2 r1=3 |

## extreme, blue: 48 frames

| finder | ok (<=3) | fooled (>=5) | none | median abs err | rank 1 | rank 2-3 | rank 4+ | no separate peak |
|---|---|---|---|---|---|---|---|---|
| F0_naive | 41/48 | 4 | 0 | 0.0 | 40 | 4 | 0 | 4 |
| F0_naive_hv | 33/48 | 14 | 0 | 1.0 | 32 | 11 | 5 | 0 |
| F1_sat | 43/48 | 3 | 0 | 0.0 | 39 | 4 | 1 | 4 |
| F2_rows | 41/48 | 4 | 0 | 0.0 | 40 | 4 | 0 | 4 |
| F3_small | 45/48 | 1 | 0 | 0.0 | 42 | 4 | 1 | 1 |
| F4_logrb | 28/48 (inside 10-90 %) | 0 | 20 | 0.03 (log units) | | | | |
| F5_pair | 35/48 | 9 | 1 | 1.0 | 32 | 4 | 3 | 9 |
| F6_pair_small | 34/48 | 4 | 7 | 0.0 | 31 | 3 | 1 | 13 |
| F7_pair_sat | 33/48 | 10 | 1 | 1.0 | 29 | 6 | 3 | 10 |

### extreme, blue, by condition: ok / fooled of frames (median true mode hue; median purity; median body share)

| condition | frames | true hue | true S | purity | body share | F0_naive | F0_naive_hv | F1_sat | F2_rows | F3_small | F5_pair | F6_pair_small | F7_pair_sat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lampcool3_wood | 7 | 103 | 104 | 1.00 | 0.004 | 5/1 r1=4 | 5/1 r1=5 | 7/0 r1=5 | 5/1 r1=4 | 6/1 r1=4 | 4/3 r1=2 | 4/2 r1=2 | 6/1 r1=4 |
| lampcool6_wood | 7 | 103 | 152 | 1.00 | 0.006 | 7/0 r1=7 | 7/0 r1=6 | 7/0 r1=6 | 7/0 r1=7 | 7/0 r1=6 | 5/2 r1=4 | 5/1 r1=4 | 5/2 r1=4 |
| lampmid3_ottoman | 2 | 106 | 96 | 1.00 | 0.049 | 2/0 r1=2 | 2/0 r1=2 | 2/0 r1=2 | 2/0 r1=2 | 2/0 r1=2 | 1/0 r1=1 | 1/0 r1=1 | 1/0 r1=1 |
| lampmid3_wood | 7 | 104 | 56 | 0.97 | 0.003 | 5/2 r1=5 | 6/1 r1=6 | 6/0 r1=5 | 5/2 r1=5 | 7/0 r1=7 | 5/0 r1=5 | 5/0 r1=5 | 5/0 r1=4 |
| lampmid6_wood | 7 | 102 | 88 | 1.00 | 0.004 | 7/0 r1=7 | 7/0 r1=7 | 7/0 r1=7 | 7/0 r1=7 | 7/0 r1=7 | 5/2 r1=5 | 5/1 r1=5 | 5/2 r1=5 |
| lampwarm3_wood | 6 | 104 | 56 | 0.91 | 0.001 | 5/1 r1=5 | 3/3 r1=3 | 6/0 r1=6 | 5/1 r1=5 | 6/0 r1=6 | 5/0 r1=5 | 4/0 r1=4 | 4/1 r1=4 |
| lampwarm6_wood | 6 | 89 | 48 | 0.98 | 0.001 | 5/0 r1=5 | 3/3 r1=3 | 3/2 r1=3 | 5/0 r1=5 | 5/0 r1=5 | 4/2 r1=4 | 4/0 r1=4 | 2/3 r1=2 |
| window_black | 6 | 101 | 168 | 1.00 | 0.143 | 5/0 r1=5 | 0/6 r1=0 | 5/1 r1=5 | 5/0 r1=5 | 5/0 r1=5 | 6/0 r1=6 | 6/0 r1=6 | 5/1 r1=5 |

