# The color candidates, leave one place out (2026-11-23, git 651c105)

`python barrels/experiments/2026-11-25_color/test.py` (plan: `../../experiments/2026-11-25_color/PREREG.md`). Ordinary train frames: 154 at 8 places; test frames never opened. Each cell: found / barrels, false boxes (boxes on empty frames), score. Each family's setting is chosen on the other 7 places by the written rule and scored on the held-out place.

Round 2 (the PREREG addendum: the light read above the horizon gate).

## Per condition

| condition | place | fixed | C1 | C2b | C3b |
|---|---|---|---|---|---|
| both_abpgray | abp_gray | 10/16, 2 (0), 0.68 | 14/16, 2 (0), 0.87 | 10/16, 2 (0), 0.68 | 14/16, 2 (0), 0.87 |
| window_abpwhite | abp_white | 26/32, 1 (0), 0.86 | 27/32, 2 (0), 0.87 | 26/32, 1 (0), 0.86 | 27/32, 2 (0), 0.87 |
| campus_light | campus_study | 35/35, 0 (0), 1.00 | 35/35, 0 (0), 1.00 | 35/35, 0 (0), 1.00 | 35/35, 0 (0), 1.00 |
| lampcool6_bathtile | home_bathtile | 13/15, 0 (0), 0.93 | 13/15, 0 (0), 0.93 | 14/15, 0 (0), 0.97 | 13/15, 0 (0), 0.93 |
| lampmid3_bathtile | home_bathtile | 1/15, 0 (0), 0.11 | 1/15, 0 (0), 0.11 | 3/15, 2 (0), 0.23 | 3/15, 4 (0), 0.23 |
| lampmid6_bathtile | home_bathtile | 1/15, 0 (0), 0.11 | 1/15, 1 (0), 0.10 | 4/15, 5 (0), 0.33 | 7/15, 5 (0), 0.53 |
| lampwarm6_bathtile | home_bathtile | 1/15, 0 (0), 0.11 | 1/15, 0 (0), 0.11 | 1/15, 1 (0), 0.10 | 1/15, 1 (0), 0.10 |
| lampcool6_glass | home_glass | 15/15, 0 (0), 1.00 | 15/15, 0 (0), 1.00 | 15/15, 0 (0), 1.00 | **14/15, 0 (0), 0.96** |
| lampmid3_glass | home_glass | 15/15, 2 (1), 0.94 | 15/15, 1 (0), 0.97 | 15/15, 2 (1), 0.94 | 15/15, 0 (0), 1.00 |
| lampmid6_glass | home_glass | 15/15, 2 (0), 0.94 | 15/15, 1 (0), 0.97 | 15/15, 2 (0), 0.94 | 15/15, 1 (0), 0.97 |
| lampwarm6_glass | home_glass | 15/15, 1 (0), 0.97 | 15/15, 1 (0), 0.97 | **15/15, 2 (1), 0.94** | 15/15, 1 (0), 0.97 |
| window_glass | home_glass | 14/15, 2 (1), 0.90 | 14/15, 2 (0), 0.90 | 14/15, 2 (1), 0.90 | 14/15, 1 (0), 0.93 |
| lampcool6_ottoman | home_ottoman | 3/15, 0 (0), 0.33 | 3/15, 0 (0), 0.33 | 3/15, 0 (0), 0.33 | 3/15, 0 (0), 0.33 |
| lampmid6_ottoman | home_ottoman | 6/15, 0 (0), 0.51 | **3/15, 0 (0), 0.27** | 6/15, 0 (0), 0.51 | **4/15, 0 (0), 0.33** |
| lampwarm6_ottoman | home_ottoman | 0/15, 1 (0), 0.00 | 0/15, 0 (0), 0.00 | 5/15, 1 (0), 0.38 | 5/15, 1 (0), 0.38 |
| window_light | home_white | 28/29, 1 (0), 0.97 | 27/29, 1 (0), 0.95 | 28/29, 1 (0), 0.97 | 27/29, 1 (0), 0.95 |
| overheaddim_palewood | uc_palewood | 13/15, 1 (0), 0.90 | 13/15, 0 (0), 0.93 | 13/15, 1 (0), 0.90 | **13/15, 2 (0), 0.88** |
| **all ordinary** | | 211/307, 13 (2), 0.80 | 212/307, 11 (0), 0.80 | 222/307, 22 (3), 0.81 | 225/307, 21 (0), 0.81 |

## Per place (found - 2 x false; held out)

| place | fixed | C1 | C2b | C3b |
|---|---:|---:|---:|---:|
| abp_gray | 6 | 10 | 6 | 10 |
| abp_white | 24 | 23 | 24 | 23 |
| campus_study | 35 | 35 | 35 | 35 |
| home_bathtile | 16 | 14 | 6 | 4 |
| home_glass | 60 | 64 | 58 | 67 |
| home_ottoman | 7 | 6 | 12 | 10 |
| home_white | 26 | 25 | 26 | 25 |
| uc_palewood | 11 | 13 | 11 | 9 |

## Acceptance (PREREG A1-A3 on the held-out numbers)

**C1**: A1 FAIL (net 185 -> 190, +5; better in 3 of 8 places, worse in abp_white, home_bathtile, home_ottoman, home_white); A2 pass (boxes on empty frames 2 -> 0); A3 FAIL (lampmid6_ottoman -0.237).

**C2b**: A1 FAIL (net 185 -> 178, -7; better in 1 of 8 places, worse in home_bathtile, home_glass); A2 FAIL (boxes on empty frames 2 -> 3, new on 4A8B_lampwarm6_glass_neg_02); A3 FAIL (lampwarm6_glass -0.026).

**C3b**: A1 FAIL (net 185 -> 183, -2; better in 3 of 8 places, worse in abp_white, home_bathtile, home_white, uc_palewood); A2 pass (boxes on empty frames 2 -> 0); A3 FAIL (lampcool6_glass -0.038, lampmid6_ottoman -0.176, overheaddim_palewood -0.023).

**Chosen family: C1** (best, NOT passing A1-A3; held-out J: C1 5.29, C2b 4.89, C3b 4.99).

## The setting chosen in each fold

| held-out place | C1 | C2b | C3b |
|---|---|---|---|
| abp_gray | orange 2..16 S>=160, blue 103..119 S>=113 (7 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (42 eligible) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.1, w1 0.22, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (27 eligible) |
| abp_white | orange 2..16 S>=160, blue 103..119 S>=113 (7 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (42 eligible) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.1, w1 0.22, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (27 eligible) |
| campus_study | orange 2..16 S>=160, blue 103..119 S>=113 (10 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (42 eligible) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.1, w1 0.22, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (27 eligible) |
| home_bathtile | orange 2..16 S>=160, blue 103..119 S>=113 (9 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.06, w1 0.3, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (48 eligible) | orange 2..16 S>=160, blue 103..119 S>=113; light rule w0 0.08, w1 0.25, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (27 eligible) |
| home_glass | orange 2..16 S>=160, blue 103..119 S>=113 (24 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.06, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (60 eligible) | orange 2..16 S>=170, blue 103..119 S>=113; light rule w0 0.1, w1 0.22, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (84 eligible) |
| home_ottoman | orange 2..13 S>=160, blue 103..119 S>=113 (11 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (42 eligible) | orange 2..13 S>=160, blue 103..119 S>=113; light rule w0 0.1, w1 0.22, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (39 eligible) |
| home_white | orange 2..16 S>=160, blue 103..119 S>=113 (7 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (42 eligible) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.1, w1 0.22, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (27 eligible) |
| uc_palewood | orange 2..16 S>=160, blue 103..119 S>=113 (18 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (42 eligible) | orange 1..14 S>=140, blue 103..119 S>=113; light rule w0 0.1, w1 0.22, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) (63 eligible) |
| **all 8 (final)** | orange 2..16 S>=160, blue 103..119 S>=113 | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.1, w1 0.22, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %) |

## Extreme sets (report only; each family's final setting)

| condition | fixed | C1 | C2b | C3b |
|---|---|---|---|---|
| lampcool3_wood | 2/21, 0 (0), 0.17 | 2/21, 2 (0), 0.16 | 2/21, 0 (0), 0.17 | 2/21, 2 (0), 0.16 |
| lampcool6_wood | 2/21, 4 (0), 0.15 | 4/21, 5 (0), 0.27 | 2/21, 4 (0), 0.15 | 4/21, 5 (0), 0.27 |
| lampmid3_ottoman | 1/15, 1 (0), 0.11 | **0/15, 1 (0), 0.00** | 1/15, 1 (0), 0.11 | **0/15, 1 (0), 0.00** |
| lampmid3_wood | 1/21, 1 (0), 0.08 | 1/21, 0 (0), 0.08 | 1/21, 1 (0), 0.08 | 1/21, 0 (0), 0.08 |
| lampmid6_wood | 1/21, 0 (0), 0.08 | 1/21, 0 (0), 0.08 | 3/21, 4 (0), 0.21 | 2/21, 3 (0), 0.15 |
| lampwarm3_wood | 1/21, 0 (0), 0.08 | 1/21, 1 (0), 0.08 | 1/21, 0 (0), 0.08 | 1/21, 0 (0), 0.08 |
| lampwarm6_wood | 0/21, 1 (0), 0.00 | 1/21, 0 (0), 0.08 | 1/21, 2 (0), 0.08 | 2/21, 1 (0), 0.17 |
| window_black | 5/26, 1 (0), 0.31 | **5/26, 1 (0), 0.28** | 5/26, 1 (0), 0.31 | **3/26, 2 (0), 0.19** |
