# The verifier's rule: each arm against `reduced+thin`

`reduced+thin`: scorecard found 2737, right place 2854, boxes where no barrel is 45.

## `reduced+thin+verify`

- removes wrong boxes somewhere: **yes** (scorecard boxes where no barrel is 45 → 8).
- HOME 28 / 1 / 0 → 28 / 1 / 0, CAMPUS 35 / 0 / 0 → 33 / 2 / 0; rows that lose a found barrel: ['CAMPUS clutter: found 3 → 2', 'CAMPUS occl: found 1 → 0'].
- perfect masks and typical, found lower: none.
- scorecard: found 2737 → 2405, right place 2854 → 2479; cells lower at all: 34; cells that drop by more than 1: frame at 75 % (29 → 21), edge at 75 % (28 → 0), slant at 25 % (200 → 198), slant at 50 % (170 → 158), top at 25 % (50 → 47), top at 50 % (45 → 0), bottom at 25 % (49 → 47), bottom at 50 % (40 → 0), post at 50 % (41 → 33), post at 75 % (11 → 0), barrel_side/other at 50 % (94 → 88), barrel_side/other at 75 % (50 → 15), barrel_low/other at 75 % (77 → 45), barrel_front/other at 75 % (22 → 19), barrel_low/same at 50 % (87 → 85), barrel_low/same at 75 % (29 → 21), barrel_front/same at 25 % (44 → 42), block/same at 25 % (100 → 97), block/same at 50 % (99 → 74), block/same at 75 % (36 → 2), block/other at 50 % (99 → 91), block/other at 75 % (3 → 0).

| level | seeds | `reduced+thin`: found (false) | `reduced+thin+verify`: found (false) |
|---|---|---|---|
| perfect masks | - | 28 (0) | 28 (0) |
| white tables, typical | 5 | 145 (0) | 145 (0) |
| white tables, typical | 20 | 579 (0) | 579 (0) |
| white tables, bad day | 5 | 135 (3) | 134 (3) |
| white tables, bad day | 20 | 547 (5) | 536 (5) |
| bad day without the stripe patch | 5 | 144 (0) | 141 (0) |
| bad day without the stripe patch | 20 | 577 (0) | 563 (0) |
| light | 5 | 143 (0) | 129 (0) |
| light | 20 | 574 (0) | 516 (0) |
| medium | 5 | 102 (1) | 52 (0) |
| medium | 20 | 400 (3) | 209 (1) |
| heavy | 5 | 21 (0) | 5 (0) |
| heavy | 20 | 89 (0) | 20 (0) |
| white tables, worst seen | 5 | 95 (2) | 41 (0) |
| white tables, worst seen | 20 | 378 (6) | 186 (1) |

**`reduced+thin+verify`: FAILS.**

## `reduced+thin+verify2`

- removes wrong boxes somewhere: **yes** (scorecard boxes where no barrel is 45 → 8).
- HOME 28 / 1 / 0 → 28 / 1 / 0, CAMPUS 35 / 0 / 0 → 33 / 2 / 0; rows that lose a found barrel: ['CAMPUS clutter: found 3 → 2', 'CAMPUS occl: found 1 → 0'].
- perfect masks and typical, found lower: none.
- scorecard: found 2737 → 2487, right place 2854 → 2561; cells lower at all: 34; cells that drop by more than 1: frame at 75 % (29 → 21), edge at 75 % (28 → 0), slant at 25 % (200 → 198), slant at 50 % (170 → 158), top at 25 % (50 → 47), top at 50 % (45 → 43), bottom at 25 % (49 → 47), post at 50 % (41 → 33), post at 75 % (11 → 0), barrel_side/other at 50 % (94 → 88), barrel_side/other at 75 % (50 → 15), barrel_low/other at 75 % (77 → 45), barrel_front/other at 75 % (22 → 19), barrel_low/same at 50 % (87 → 85), barrel_low/same at 75 % (29 → 21), barrel_front/same at 25 % (44 → 42), block/same at 25 % (100 → 97), block/same at 50 % (99 → 74), block/same at 75 % (36 → 2), block/other at 50 % (99 → 91), block/other at 75 % (3 → 0).

| level | seeds | `reduced+thin`: found (false) | `reduced+thin+verify2`: found (false) |
|---|---|---|---|
| perfect masks | - | 28 (0) | 28 (0) |
| white tables, typical | 5 | 145 (0) | 145 (0) |
| white tables, typical | 20 | 579 (0) | 579 (0) |
| white tables, bad day | 5 | 135 (3) | 134 (3) |
| white tables, bad day | 20 | 547 (5) | 536 (5) |
| bad day without the stripe patch | 5 | 144 (0) | 141 (0) |
| bad day without the stripe patch | 20 | 577 (0) | 563 (0) |
| light | 5 | 143 (0) | 129 (0) |
| light | 20 | 574 (0) | 516 (0) |
| medium | 5 | 102 (1) | 52 (0) |
| medium | 20 | 400 (3) | 209 (1) |
| heavy | 5 | 21 (0) | 5 (0) |
| heavy | 20 | 89 (0) | 20 (0) |
| white tables, worst seen | 5 | 95 (2) | 41 (0) |
| white tables, worst seen | 20 | 378 (6) | 186 (1) |

**`reduced+thin+verify2`: FAILS.**

