# Test look 2026-11-27: the tables

Made by `experiments/2026-11-27_test_look/tables.py` from `numbers.json` (git 9d43df8). 78 test frames, 31 with a usable vendor file (47 without a file, 0 not measured).

## Totals

Ordinary = the conditions the judge judges (data/conditions.json); report only = extreme and other.

**Every test frame** (found per placement; per frame; boxes not on their barrel per frame; boxes on empty frames clean / with clutter):

| group | frames | found per placement, before → now | found per frame, before → now | found with the box off, before → now | boxes not on their barrel, before → now | on empty frames, before → now |
|---|---:|---|---|---|---|---|
| all test frames | 78 | 39.31 → 43.95 of 61 | 48 → 70 of 121 | 3 → 5 | 3 → 3 | 0/0 → 0/0 (of 27 empty frames) |
| ordinary conditions | 44 | 38.37 → 39.12 of 45 | 46 → 49 of 63 | 2 → 2 | 3 → 3 | 0/0 → 0/0 (of 16 empty frames) |
| report only (extreme / other) | 34 | 1.11 → 5 of 18 | 2 → 21 of 58 | 1 → 3 | 0 → 0 | 0/0 → 0/0 (of 11 empty frames) |

**The frames with a vendor file** (the same three counts for ours before, ours now and the vendor):

| group | frames | found per placement: before / now / vendor | found per frame: before / now / vendor | off: b / n / v | boxes not on their barrel: b / n / v | on empty frames (clean): b / n / v |
|---|---:|---|---|---|---|---|
| all test frames | 31 | 7.2 / 7.95 / 9.1 of 12 | 15 / 18 / 23 of 32 | 2 / 2 / 5 | 2 / 2 / 0 | 0 / 0 / 0 |
| ordinary conditions | 29 | 7.37 / 8.12 / 9.35 of 12 | 15 / 18 / 22 of 30 | 2 / 2 / 4 | 2 / 2 / 0 | 0 / 0 / 0 |
| report only (extreme / other) | 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |

## By data set

The data sets of `report.py` (HOME, CAMPUS, and one per {robot}_{light}_{surface}).

**Every test frame** (found per placement; per frame; boxes not on their barrel per frame; boxes on empty frames clean / with clutter):

| group | frames | found per placement, before → now | found per frame, before → now | found with the box off, before → now | boxes not on their barrel, before → now | on empty frames, before → now |
|---|---:|---|---|---|---|---|
| HOME | 5 | 9 → 9 of 9 | 9 → 9 of 9 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| CAMPUS | 10 | 22 → 22 of 24 | 22 → 22 of 24 | 0 → 0 | 1 → 1 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_both_abpgray | 2 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampcool1_wood | 3 | 0 → 0 of 5 | 0 → 0 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampcool3_wood | 3 | 0 → 4 of 5 | 0 → 4 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampcool6_bathtile | 2 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampcool6_glass | 2 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampcool6_ottoman | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampcool6_wood | 3 | 1 → 4 of 5 | 1 → 4 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid1_wood | 3 | 0 → 0 of 5 | 0 → 0 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid3_bathtile | 2 | 0 → 2 of 2 | 0 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid3_glass | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 1 → 1 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid3_ottoman | 2 | 0 → 0 of 2 | 0 → 0 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid3_wood | 3 | 0 → 2 of 5 | 0 → 2 of 5 | 0 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid6_bathtile | 2 | 0 → 0 of 2 | 0 → 0 of 2 | 1 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid6_glass | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 1 → 1 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid6_ottoman | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampmid6_wood | 3 | 0 → 2 of 5 | 0 → 2 of 5 | 1 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampwarm1_wood | 3 | 0 → 0 of 5 | 0 → 0 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampwarm3_wood | 3 | 0 → 2 of 5 | 0 → 2 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampwarm6_bathtile | 2 | 0 → 1 of 2 | 0 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampwarm6_glass | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampwarm6_ottoman | 2 | 0 → 0 of 2 | 0 → 0 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_lampwarm6_wood | 3 | 0 → 4 of 5 | 0 → 4 of 5 | 0 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_overheaddim_palewood | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_window_abpwhite | 1 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 0 empty frames) |
| 4A8B_window_black | 5 | 1 → 3 of 11 | 1 → 3 of 11 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| 4A8B_window_glass | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 1 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |

**The frames with a vendor file** (the same three counts for ours before, ours now and the vendor):

| group | frames | found per placement: before / now / vendor | found per frame: before / now / vendor | off: b / n / v | boxes not on their barrel: b / n / v | on empty frames (clean): b / n / v |
|---|---:|---|---|---|---|---|
| 4A8B_both_abpgray | 2 | 2 / 2 / 2 of 2 | 2 / 2 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool6_bathtile | 2 | 2 / 2 / 1 of 2 | 2 / 2 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool6_glass | 2 | 2 / 2 / 2 of 2 | 2 / 2 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool6_ottoman | 2 | 1 / 1 / 2 of 2 | 1 / 1 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid3_bathtile | 2 | 0 / 2 / 1 of 2 | 0 / 2 / 1 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid3_glass | 2 | 1 / 1 / 2 of 2 | 1 / 1 / 2 of 2 | 0 / 0 / 0 | 1 / 1 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid3_ottoman | 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid6_bathtile | 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 of 2 | 1 / 1 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid6_glass | 2 | 1 / 1 / 2 of 2 | 1 / 1 / 2 of 2 | 0 / 0 / 0 | 1 / 1 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid6_ottoman | 2 | 1 / 1 / 2 of 2 | 1 / 1 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm6_bathtile | 2 | 0 / 1 / 0 of 2 | 0 / 1 / 0 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm6_glass | 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm6_ottoman | 2 | 0 / 0 / 2 of 2 | 0 / 0 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_overheaddim_palewood | 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_window_abpwhite | 1 | 2 / 2 / 2 of 2 | 2 / 2 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_window_glass | 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |

## By place, ordinary conditions

Each place pools its lights; a placement counts the share of its lights in which it is found.

**Every test frame** (found per placement; per frame; boxes not on their barrel per frame; boxes on empty frames clean / with clutter):

| group | frames | found per placement, before → now | found per frame, before → now | found with the box off, before → now | boxes not on their barrel, before → now | on empty frames, before → now |
|---|---:|---|---|---|---|---|
| home_white | 5 | 9 → 9 of 9 | 9 → 9 of 9 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| campus_study | 10 | 22 → 22 of 24 | 22 → 22 of 24 | 0 → 0 | 1 → 1 | 0/0 → 0/0 (of 1 empty frames) |
| abp_gray | 2 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| home_bathtile | 8 | 0.5 → 1.25 of 2 | 2 → 5 of 8 | 1 → 1 | 0 → 0 | 0/0 → 0/0 (of 4 empty frames) |
| home_glass | 10 | 1.2 → 1.2 of 2 | 6 → 6 of 10 | 1 → 1 | 2 → 2 | 0/0 → 0/0 (of 5 empty frames) |
| home_ottoman | 6 | 0.67 → 0.67 of 2 | 2 → 2 of 6 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 3 empty frames) |
| uc_palewood | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| abp_white | 1 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 0 empty frames) |

**The frames with a vendor file** (the same three counts for ours before, ours now and the vendor):

| group | frames | found per placement: before / now / vendor | found per frame: before / now / vendor | off: b / n / v | boxes not on their barrel: b / n / v | on empty frames (clean): b / n / v |
|---|---:|---|---|---|---|---|
| abp_gray | 2 | 2 / 2 / 2 of 2 | 2 / 2 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| home_bathtile | 8 | 0.5 / 1.25 / 0.75 of 2 | 2 / 5 / 3 of 8 | 1 / 1 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| home_glass | 10 | 1.2 / 1.2 / 1.6 of 2 | 6 / 6 / 8 of 10 | 1 / 1 / 2 | 2 / 2 / 0 | 0 / 0 / 0 |
| home_ottoman | 6 | 0.67 / 0.67 / 2 of 2 | 2 / 2 / 6 of 6 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| uc_palewood | 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| abp_white | 1 | 2 / 2 / 2 of 2 | 2 / 2 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

## By place, report only

Extreme conditions (parked): never judged.

**Every test frame** (found per placement; per frame; boxes not on their barrel per frame; boxes on empty frames clean / with clutter):

| group | frames | found per placement, before → now | found per frame, before → now | found with the box off, before → now | boxes not on their barrel, before → now | on empty frames, before → now |
|---|---:|---|---|---|---|---|
| home_wooddesk | 27 | 0.11 → 2 of 5 | 1 → 18 of 45 | 1 → 3 | 0 → 0 | 0/0 → 0/0 (of 9 empty frames) |
| home_ottoman | 2 | 0 → 0 of 2 | 0 → 0 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| home_black | 5 | 1 → 3 of 11 | 1 → 3 of 11 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |

**The frames with a vendor file** (the same three counts for ours before, ours now and the vendor):

| group | frames | found per placement: before / now / vendor | found per frame: before / now / vendor | off: b / n / v | boxes not on their barrel: b / n / v | on empty frames (clean): b / n / v |
|---|---:|---|---|---|---|---|
| home_ottoman | 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |

## By condition

One light at one place.

**Every test frame** (found per placement; per frame; boxes not on their barrel per frame; boxes on empty frames clean / with clutter):

| group | frames | found per placement, before → now | found per frame, before → now | found with the box off, before → now | boxes not on their barrel, before → now | on empty frames, before → now |
|---|---:|---|---|---|---|---|
| window_light | 5 | 9 → 9 of 9 | 9 → 9 of 9 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| campus_light | 10 | 22 → 22 of 24 | 22 → 22 of 24 | 0 → 0 | 1 → 1 | 0/0 → 0/0 (of 1 empty frames) |
| both_abpgray | 2 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampcool1_wood | 3 | 0 → 0 of 5 | 0 → 0 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampcool3_wood | 3 | 0 → 4 of 5 | 0 → 4 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampcool6_bathtile | 2 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampcool6_glass | 2 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampcool6_ottoman | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampcool6_wood | 3 | 1 → 4 of 5 | 1 → 4 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid1_wood | 3 | 0 → 0 of 5 | 0 → 0 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid3_bathtile | 2 | 0 → 2 of 2 | 0 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid3_glass | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 1 → 1 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid3_ottoman | 2 | 0 → 0 of 2 | 0 → 0 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid3_wood | 3 | 0 → 2 of 5 | 0 → 2 of 5 | 0 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid6_bathtile | 2 | 0 → 0 of 2 | 0 → 0 of 2 | 1 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid6_glass | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 1 → 1 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid6_ottoman | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampmid6_wood | 3 | 0 → 2 of 5 | 0 → 2 of 5 | 1 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampwarm1_wood | 3 | 0 → 0 of 5 | 0 → 0 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampwarm3_wood | 3 | 0 → 2 of 5 | 0 → 2 of 5 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampwarm6_bathtile | 2 | 0 → 1 of 2 | 0 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampwarm6_glass | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampwarm6_ottoman | 2 | 0 → 0 of 2 | 0 → 0 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| lampwarm6_wood | 3 | 0 → 4 of 5 | 0 → 4 of 5 | 0 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| overheaddim_palewood | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| window_abpwhite | 1 | 2 → 2 of 2 | 2 → 2 of 2 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 0 empty frames) |
| window_black | 5 | 1 → 3 of 11 | 1 → 3 of 11 | 0 → 0 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |
| window_glass | 2 | 1 → 1 of 2 | 1 → 1 of 2 | 1 → 1 | 0 → 0 | 0/0 → 0/0 (of 1 empty frames) |

**The frames with a vendor file** (the same three counts for ours before, ours now and the vendor):

| group | frames | found per placement: before / now / vendor | found per frame: before / now / vendor | off: b / n / v | boxes not on their barrel: b / n / v | on empty frames (clean): b / n / v |
|---|---:|---|---|---|---|---|
| both_abpgray | 2 | 2 / 2 / 2 of 2 | 2 / 2 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampcool6_bathtile | 2 | 2 / 2 / 1 of 2 | 2 / 2 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampcool6_glass | 2 | 2 / 2 / 2 of 2 | 2 / 2 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampcool6_ottoman | 2 | 1 / 1 / 2 of 2 | 1 / 1 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampmid3_bathtile | 2 | 0 / 2 / 1 of 2 | 0 / 2 / 1 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampmid3_glass | 2 | 1 / 1 / 2 of 2 | 1 / 1 / 2 of 2 | 0 / 0 / 0 | 1 / 1 / 0 | 0 / 0 / 0 |
| lampmid3_ottoman | 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampmid6_bathtile | 2 | 0 / 0 / 1 of 2 | 0 / 0 / 1 of 2 | 1 / 1 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampmid6_glass | 2 | 1 / 1 / 2 of 2 | 1 / 1 / 2 of 2 | 0 / 0 / 0 | 1 / 1 / 0 | 0 / 0 / 0 |
| lampmid6_ottoman | 2 | 1 / 1 / 2 of 2 | 1 / 1 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampwarm6_bathtile | 2 | 0 / 1 / 0 of 2 | 0 / 1 / 0 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampwarm6_glass | 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| lampwarm6_ottoman | 2 | 0 / 0 / 2 of 2 | 0 / 0 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| overheaddim_palewood | 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 of 2 | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| window_abpwhite | 1 | 2 / 2 / 2 of 2 | 2 / 2 / 2 of 2 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| window_glass | 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 of 2 | 1 / 1 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
