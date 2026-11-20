# The rule, clause by clause: each arm against `stack`

Folder `round1`. `stack`: scorecard found 2417, boxes where no barrel is 45; eval table HOME 28 / 1 / 0, CAMPUS 35 / 0 / 0.

## `combined`

- **(a) eval table: pass.** HOME 28 / 1 / 0 → 28 / 1 / 0, CAMPUS 35 / 0 / 0 → 35 / 0 / 0 (found / missed / false); rows that lose a barrel: none; rows that gain a false box: none; boxes on negative frames, any set: 0.
- **(b) scorecard: pass.** Found 2417 → 2764 of 3888; right place 2532 → 2883; boxes where no barrel is 45 → 45; cells lower: none.
- **(c) damage levels: FAILS** (the recordings: `by_eye.md`).

| level | seeds | false, `stack` | false, `combined` | must be | | found |
|---|---|---|---|---|---|---|
| perfect masks | - | 0 | 0 | not higher | pass | 28 → 28 of 29 |
| white tables, typical | 5 | 0 | 0 | not higher | pass | 145 → 145 of 145 |
| white tables, typical | 20 | 0 | 0 | not higher | pass | 579 → 579 of 580 |
| bad day without the stripe patch | 5 | 0 | 0 | not higher | pass | 144 → 144 of 145 |
| bad day without the stripe patch | 20 | 0 | 0 | not higher | pass | 577 → 577 of 580 |
| light | 5 | 0 | 0 | not higher | pass | 143 → 143 of 145 |
| light | 20 | 0 | 0 | not higher | pass | 574 → 574 of 580 |
| white tables, bad day | 5 | 3 | 3 | not more than double | pass | 135 → 136 of 145 |
| white tables, bad day | 20 | 5 | 6 | not more than double | pass | 547 → 555 of 580 |
| medium | 5 | 1 | 1 | not more than double | pass | 99 → 115 of 145 |
| medium | 20 | 3 | 7 | not more than double | **FAILS** | 388 → 444 of 580 |
| heavy | 5 | 0 | 0 | report only | | 21 → 21 of 145 |
| heavy | 20 | 0 | 0 | report only | | 89 → 89 of 580 |
| white tables, worst seen | 5 | 2 | 2 | report only | | 84 → 105 of 145 |
| white tables, worst seen | 20 | 6 | 10 | report only | | 337 → 419 of 580 |

Found lower at a damage level (not in the rule, named): none.

**`combined`: FAILS.**

## `combined+thin`

- **(a) eval table: pass.** HOME 28 / 1 / 0 → 28 / 1 / 0, CAMPUS 35 / 0 / 0 → 35 / 0 / 0 (found / missed / false); rows that lose a barrel: none; rows that gain a false box: none; boxes on negative frames, any set: 0.
- **(b) scorecard: pass.** Found 2417 → 2738 of 3888; right place 2532 → 2856; boxes where no barrel is 45 → 45; cells lower: none.
- **(c) damage levels: pass** (the recordings: `by_eye.md`).

| level | seeds | false, `stack` | false, `combined+thin` | must be | | found |
|---|---|---|---|---|---|---|
| perfect masks | - | 0 | 0 | not higher | pass | 28 → 28 of 29 |
| white tables, typical | 5 | 0 | 0 | not higher | pass | 145 → 145 of 145 |
| white tables, typical | 20 | 0 | 0 | not higher | pass | 579 → 579 of 580 |
| bad day without the stripe patch | 5 | 0 | 0 | not higher | pass | 144 → 144 of 145 |
| bad day without the stripe patch | 20 | 0 | 0 | not higher | pass | 577 → 577 of 580 |
| light | 5 | 0 | 0 | not higher | pass | 143 → 143 of 145 |
| light | 20 | 0 | 0 | not higher | pass | 574 → 574 of 580 |
| white tables, bad day | 5 | 3 | 3 | not more than double | pass | 135 → 135 of 145 |
| white tables, bad day | 20 | 5 | 5 | not more than double | pass | 547 → 547 of 580 |
| medium | 5 | 1 | 1 | not more than double | pass | 99 → 103 of 145 |
| medium | 20 | 3 | 4 | not more than double | pass | 388 → 404 of 580 |
| heavy | 5 | 0 | 0 | report only | | 21 → 21 of 145 |
| heavy | 20 | 0 | 0 | report only | | 89 → 89 of 580 |
| white tables, worst seen | 5 | 2 | 2 | report only | | 84 → 98 of 145 |
| white tables, worst seen | 20 | 6 | 6 | report only | | 337 → 387 of 580 |

Found lower at a damage level (not in the rule, named): none.

- **on top of `combined`: FAILS.** Scorecard found 2764 → 2738, boxes where no barrel is 45 → 45; cells lower than `combined`: frame at 75 % (87 → 30), barrel_side/other at 75 % (60 → 50), barrel_low/other at 75 % (81 → 77), barrel_side/same at 75 % (18 → 17), barrel_low/same at 75 % (42 → 29); false boxes higher than `combined` at a judged level: none.

**`combined+thin`: FAILS.**

## `combined+cover`

- **(a) eval table: pass.** HOME 28 / 1 / 0 → 28 / 1 / 0, CAMPUS 35 / 0 / 0 → 35 / 0 / 0 (found / missed / false); rows that lose a barrel: none; rows that gain a false box: none; boxes on negative frames, any set: 0.
- **(b) scorecard: FAILS.** Found 2417 → 3261 of 3888; right place 2532 → 3419; boxes where no barrel is 45 → 58; cells lower: none.
- **(c) damage levels: FAILS** (the recordings: `by_eye.md`).

| level | seeds | false, `stack` | false, `combined+cover` | must be | | found |
|---|---|---|---|---|---|---|
| perfect masks | - | 0 | 0 | not higher | pass | 28 → 28 of 29 |
| white tables, typical | 5 | 0 | 0 | not higher | pass | 145 → 145 of 145 |
| white tables, typical | 20 | 0 | 0 | not higher | pass | 579 → 579 of 580 |
| bad day without the stripe patch | 5 | 0 | 0 | not higher | pass | 144 → 144 of 145 |
| bad day without the stripe patch | 20 | 0 | 0 | not higher | pass | 577 → 577 of 580 |
| light | 5 | 0 | 0 | not higher | pass | 143 → 143 of 145 |
| light | 20 | 0 | 2 | not higher | **FAILS** | 574 → 572 of 580 |
| white tables, bad day | 5 | 3 | 4 | not more than double | pass | 135 → 139 of 145 |
| white tables, bad day | 20 | 5 | 17 | not more than double | **FAILS** | 547 → 560 of 580 |
| medium | 5 | 1 | 4 | not more than double | **FAILS** | 99 → 125 of 145 |
| medium | 20 | 3 | 21 | not more than double | **FAILS** | 388 → 481 of 580 |
| heavy | 5 | 0 | 0 | report only | | 21 → 24 of 145 |
| heavy | 20 | 0 | 0 | report only | | 89 → 98 of 580 |
| white tables, worst seen | 5 | 2 | 6 | report only | | 84 → 115 of 145 |
| white tables, worst seen | 20 | 6 | 17 | report only | | 337 → 463 of 580 |

Found lower at a damage level (not in the rule, named): light (20 seeds): 574 → 572.

- **on top of `combined`: FAILS.** Scorecard found 2764 → 3261, boxes where no barrel is 45 → 58; cells lower than `combined`: none; false boxes higher than `combined` at a judged level: light (20 seeds): 0 → 2; white tables, bad day (5 seeds): 3 → 4; white tables, bad day (20 seeds): 6 → 17; medium (5 seeds): 1 → 4; medium (20 seeds): 7 → 21.

**`combined+cover`: FAILS.**

