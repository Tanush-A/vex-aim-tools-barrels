# The color candidates, leave one place out (2026-11-23, git 5185038)

`python barrels/experiments/2026-11-25_color/test.py` (plan: `../../experiments/2026-11-25_color/PREREG.md`). Ordinary train frames: 154 at 8 places; test frames never opened. Each cell: found / barrels, false boxes (boxes on empty frames), score. Each family's setting is chosen on the other 7 places by the written rule and scored on the held-out place.

## Per condition

| condition | place | fixed | C1 constant | C2 light | C3 both |
|---|---|---|---|---|---|
| both_abpgray | abp_gray | 10/16, 2 (0), 0.68 | 14/16, 2 (0), 0.87 | 10/16, 2 (0), 0.68 | 14/16, 2 (0), 0.87 |
| window_abpwhite | abp_white | 26/32, 1 (0), 0.86 | 27/32, 2 (0), 0.87 | 26/32, 1 (0), 0.86 | 27/32, 2 (0), 0.87 |
| campus_light | campus_study | 35/35, 0 (0), 1.00 | 35/35, 0 (0), 1.00 | 35/35, 0 (0), 1.00 | 35/35, 0 (0), 1.00 |
| lampcool6_bathtile | home_bathtile | 13/15, 0 (0), 0.93 | 13/15, 0 (0), 0.93 | 14/15, 0 (0), 0.97 | 13/15, 0 (0), 0.93 |
| lampmid3_bathtile | home_bathtile | 1/15, 0 (0), 0.11 | 1/15, 0 (0), 0.11 | 8/15, 3 (0), 0.61 | 6/15, 5 (0), 0.47 |
| lampmid6_bathtile | home_bathtile | 1/15, 0 (0), 0.11 | 1/15, 1 (0), 0.10 | 10/15, 1 (0), 0.77 | 10/15, 6 (0), 0.68 |
| lampwarm6_bathtile | home_bathtile | 1/15, 0 (0), 0.11 | 1/15, 0 (0), 0.11 | 1/15, 1 (0), 0.10 | 1/15, 1 (0), 0.10 |
| lampcool6_glass | home_glass | 15/15, 0 (0), 1.00 | 15/15, 0 (0), 1.00 | 15/15, 0 (0), 1.00 | **14/15, 0 (0), 0.96** |
| lampmid3_glass | home_glass | 15/15, 2 (1), 0.94 | 15/15, 1 (0), 0.97 | 15/15, 2 (1), 0.94 | 15/15, 0 (0), 1.00 |
| lampmid6_glass | home_glass | 15/15, 2 (0), 0.94 | 15/15, 1 (0), 0.97 | **15/15, 3 (1), 0.92** | 15/15, 1 (0), 0.97 |
| lampwarm6_glass | home_glass | 15/15, 1 (0), 0.97 | 15/15, 1 (0), 0.97 | 15/15, 1 (0), 0.97 | 15/15, 1 (0), 0.97 |
| window_glass | home_glass | 14/15, 2 (1), 0.90 | 14/15, 2 (0), 0.90 | 14/15, 2 (1), 0.90 | 14/15, 1 (0), 0.93 |
| lampcool6_ottoman | home_ottoman | 3/15, 0 (0), 0.33 | 3/15, 0 (0), 0.33 | 3/15, 0 (0), 0.33 | **2/15, 0 (0), 0.22** |
| lampmid6_ottoman | home_ottoman | 6/15, 0 (0), 0.51 | **3/15, 0 (0), 0.27** | 6/15, 0 (0), 0.51 | **4/15, 0 (0), 0.33** |
| lampwarm6_ottoman | home_ottoman | 0/15, 1 (0), 0.00 | 0/15, 0 (0), 0.00 | 5/15, 1 (0), 0.38 | 5/15, 1 (0), 0.38 |
| window_light | home_white | 28/29, 1 (0), 0.97 | 27/29, 1 (0), 0.95 | 28/29, 1 (0), 0.97 | 27/29, 1 (0), 0.95 |
| overheaddim_palewood | uc_palewood | 13/15, 1 (0), 0.90 | 13/15, 0 (0), 0.93 | 13/15, 1 (0), 0.90 | **13/15, 2 (0), 0.88** |
| **all ordinary** | | 211/307, 13 (2), 0.80 | 212/307, 11 (0), 0.80 | 233/307, 19 (3), 0.83 | 230/307, 23 (0), 0.82 |

## Per place (found - 2 x false; held out)

| place | fixed | C1 | C2 | C3 |
|---|---:|---:|---:|---:|
| abp_gray | 6 | 10 | 6 | 10 |
| abp_white | 24 | 23 | 24 | 23 |
| campus_study | 35 | 35 | 35 | 35 |
| home_bathtile | 16 | 14 | 23 | 6 |
| home_glass | 60 | 64 | 58 | 67 |
| home_ottoman | 7 | 6 | 12 | 9 |
| home_white | 26 | 25 | 26 | 25 |
| uc_palewood | 11 | 13 | 11 | 9 |

## Acceptance (PREREG A1-A3 on the held-out numbers)

**C1**: A1 FAIL (net 185 -> 190, +5; better in 3 of 8 places, worse in abp_white, home_bathtile, home_ottoman, home_white); A2 pass (boxes on empty frames 2 -> 0); A3 FAIL (lampmid6_ottoman -0.237).

**C2**: A1 FAIL (net 185 -> 195, +10; better in 2 of 8 places, worse in home_glass); A2 FAIL (boxes on empty frames 2 -> 3, new on 4A8B_lampmid6_glass_neg_02); A3 FAIL (lampmid6_glass -0.023).

**C3**: A1 FAIL (net 185 -> 184, -1; better in 3 of 8 places, worse in abp_white, home_bathtile, home_white, uc_palewood); A2 pass (boxes on empty frames 2 -> 0); A3 FAIL (lampcool6_glass -0.038, lampcool6_ottoman -0.111, lampmid6_ottoman -0.176, overheaddim_palewood -0.023).

**Chosen family: C1** (best, NOT passing A1-A3; held-out J: C1 5.29, C2 5.18, C3 5.00).

## The setting chosen in each fold

| held-out place | C1 | C2 | C3 |
|---|---|---|---|
| abp_gray | orange 2..16 S>=160, blue 103..119 S>=113 (7 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.08, w1 0.2, blue S -> 40, hue low -> 92 (54 eligible) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 (36 eligible) |
| abp_white | orange 2..16 S>=160, blue 103..119 S>=113 (7 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.08, w1 0.2, blue S -> 40, hue low -> 92 (54 eligible) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 (36 eligible) |
| campus_study | orange 2..16 S>=160, blue 103..119 S>=113 (10 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.08, w1 0.2, blue S -> 40, hue low -> 92 (54 eligible) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 (36 eligible) |
| home_bathtile | orange 2..16 S>=160, blue 103..119 S>=113 (9 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.06, w1 0.2, blue S -> 30, hue low -> 98 (63 eligible) | orange 2..17 S>=160, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 (36 eligible) |
| home_glass | orange 2..16 S>=160, blue 103..119 S>=113 (24 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.06, w1 0.2, blue S -> 40, hue low -> 92 (60 eligible) | orange 2..16 S>=170, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 (84 eligible) |
| home_ottoman | orange 2..13 S>=160, blue 103..119 S>=113 (11 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.08, w1 0.2, blue S -> 40, hue low -> 92 (54 eligible) | orange 2..13 S>=160, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 (52 eligible) |
| home_white | orange 2..16 S>=160, blue 103..119 S>=113 (7 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.08, w1 0.2, blue S -> 40, hue low -> 92 (54 eligible) | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 (36 eligible) |
| uc_palewood | orange 2..16 S>=160, blue 103..119 S>=113 (18 eligible) | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.08, w1 0.2, blue S -> 40, hue low -> 92 (54 eligible) | orange 1..14 S>=140, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 (84 eligible) |
| **all 8 (final)** | orange 2..16 S>=160, blue 103..119 S>=113 | orange 3..13 S>=140, blue 103..119 S>=113; light rule w0 0.08, w1 0.2, blue S -> 40, hue low -> 92 | orange 2..15 S>=160, blue 103..119 S>=113; light rule w0 0.08, w1 0.22, blue S -> 40, hue low -> 92 |

## Extreme sets (report only; each family's final setting)

| condition | fixed | C1 | C2 | C3 |
|---|---|---|---|---|
| lampcool3_wood | 2/21, 0 (0), 0.17 | 2/21, 2 (0), 0.16 | 6/21, 0 (0), 0.45 | 5/21, 2 (0), 0.35 |
| lampcool6_wood | 2/21, 4 (0), 0.15 | 4/21, 5 (0), 0.27 | 6/21, 3 (0), 0.40 | 7/21, 4 (0), 0.44 |
| lampmid3_ottoman | 1/15, 1 (0), 0.11 | **0/15, 1 (0), 0.00** | 1/15, 1 (0), 0.11 | **0/15, 1 (0), 0.00** |
| lampmid3_wood | 1/21, 1 (0), 0.08 | 1/21, 0 (0), 0.08 | 4/21, 2 (0), 0.29 | 3/21, 2 (0), 0.21 |
| lampmid6_wood | 1/21, 0 (0), 0.08 | 1/21, 0 (0), 0.08 | 4/21, 3 (0), 0.28 | 5/21, 4 (0), 0.33 |
| lampwarm3_wood | 1/21, 0 (0), 0.08 | 1/21, 1 (0), 0.08 | 1/21, 0 (0), 0.08 | 1/21, 0 (0), 0.08 |
| lampwarm6_wood | 0/21, 1 (0), 0.00 | 1/21, 0 (0), 0.08 | 2/21, 2 (0), 0.16 | 2/21, 1 (0), 0.17 |
| window_black | 5/26, 1 (0), 0.31 | **5/26, 1 (0), 0.28** | 5/26, 1 (0), 0.31 | **3/26, 2 (0), 0.19** |
