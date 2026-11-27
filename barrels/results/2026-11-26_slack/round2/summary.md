# The slack experiment: every arm on every yardstick (git 769f6eb)

`python barrels/experiments/2026-11-26_slack/run.py --round round2 --arms B,C,D,CD`; plan: `experiments/2026-11-26_slack/PREREG.md`. Train frames only. Every arm is compared with today's detector **on the same mask**. Counts are per frame (a barrel once per light) unless they say "placements".

Frames: 154 ordinary (37 on the two white tables), 77 extreme, 30 excluded, 0 unlisted; 33 empty frames; hand thresholds for 15 conditions (100 ordinary frames).

Cell: found by today's detector → by the arm (back X of Y = of the Y barrels today's detector finds on the unharmed mask and loses on this mask, the arm finds X; other +g −l = barrels the arm gains that were not found unharmed, and barrels the arm loses); then the boxes that are not on their barrel.

## (a) Fixed colors, ONE pixel shaved off

| arm | the two white tables | the other ordinary places | all ordinary | judge on this mask (placements) | new boxes on empty frames |
|---|---|---|---|---|---|
| B | 52 → 58 (back 6 of 11; other +0 −0); not on barrel 1 → 0 | 121 → 126 (back 5 of 29; other +0 −0); not on barrel 1 → 1 | 173 → 184 (back 11 of 40; other +0 −0); not on barrel 2 → 1 | PASS: 107.75 → 116.5, boxes 2.0 → 1.0 | 0 |
| C | 52 → 57 (back 5 of 11; other +0 −0); not on barrel 1 → 0 | 121 → 122 (back 1 of 29; other +0 −0); not on barrel 1 → 1 | 173 → 179 (back 6 of 40; other +0 −0); not on barrel 2 → 1 | PASS: 107.75 → 113.75, boxes 2.0 → 1.0 | 0 |
| D | 52 → 58 (back 6 of 11; other +0 −0); not on barrel 1 → 0 | 121 → 126 (back 5 of 29; other +0 −0); not on barrel 1 → 1 | 173 → 184 (back 11 of 40; other +0 −0); not on barrel 2 → 1 | PASS: 107.75 → 116.5, boxes 2.0 → 1.0 | 0 |
| CD | 52 → 58 (back 6 of 11; other +0 −0); not on barrel 1 → 0 | 121 → 126 (back 5 of 29; other +0 −0); not on barrel 1 → 1 | 173 → 184 (back 11 of 40; other +0 −0); not on barrel 2 → 1 | PASS: 107.75 → 116.5, boxes 2.0 → 1.0 | 0 |

Today's detector on the unharmed mask finds 211 of 307; on this mask 173.

## (a) Fixed colors, TWO pixels shaved off

| arm | the two white tables | the other ordinary places | all ordinary | judge on this mask (placements) | new boxes on empty frames |
|---|---|---|---|---|---|
| B | 29 → 52 (back 23 of 34; other +0 −0); not on barrel 1 → 0 | 75 → 111 (back 35 of 73; other +1 −0); not on barrel 0 → 0 | 104 → 163 (back 58 of 107; other +1 −0); not on barrel 1 → 0 | PASS: 61.0 → 101.6, boxes 1.0 → 0.0 | 0 |
| C | 29 → 29 (back 0 of 34; other +0 −0); not on barrel 1 → 1 | 75 → 76 (back 1 of 73; other +0 −0); not on barrel 0 → 0 | 104 → 105 (back 1 of 107; other +0 −0); not on barrel 1 → 1 | NO CLEAR DIFFERENCE: 61.0 → 62.0, boxes 1.0 → 1.0 | 0 |
| D | 29 → 50 (back 21 of 34; other +0 −0); not on barrel 1 → 0 | 75 → 110 (back 34 of 73; other +1 −0); not on barrel 0 → 0 | 104 → 160 (back 55 of 107; other +1 −0); not on barrel 1 → 0 | PASS: 61.0 → 99.4, boxes 1.0 → 0.0 | 0 |
| CD | 29 → 50 (back 21 of 34; other +0 −0); not on barrel 1 → 0 | 75 → 110 (back 34 of 73; other +1 −0); not on barrel 0 → 0 | 104 → 160 (back 55 of 107; other +1 −0); not on barrel 1 → 0 | PASS: 61.0 → 99.4, boxes 1.0 → 0.0 | 0 |

Today's detector on the unharmed mask finds 211 of 307; on this mask 104.

## (b) Realistic damage on the white tables (HOME, CAMPUS, ABP white; three seeds added up)

| arm | white tables, typical | white tables, bad day |
|---|---|---|
| B | 228 → 246 (back 18 of 42; other +0 −0); not on barrel 3 → 0 | 217 → 237 (back 20 of 51; other +0 −0); not on barrel 3 → 0 |
| C | 228 → 243 (back 15 of 42; other +0 −0); not on barrel 3 → 0 | 217 → 232 (back 15 of 51; other +0 −0); not on barrel 3 → 0 |
| D | 228 → 246 (back 18 of 42; other +0 −0); not on barrel 3 → 0 | 217 → 237 (back 20 of 51; other +0 −0); not on barrel 3 → 0 |
| CD | 228 → 246 (back 18 of 42; other +0 −0); not on barrel 3 → 0 | 217 → 237 (back 20 of 51; other +0 −0); not on barrel 3 → 0 |

Unharmed, today's detector: 267 of 288 (three times the 54 frames). Boxes that appear or disappear on the damaged masks: 49 (listed in raw form only; no sheet).

## (c) The unharmed masks, fixed colors (the standard judge)

| arm | verdict | found, placements | found, per frame | barrels gained / lost | boxes not on their barrel, per arrangement (per frame) | pages |
|---|---|---|---|---|---|---|
| B | **NO CLEAR DIFFERENCE** | 133.8 → 135.38 | 211 → 214 | +3 / −0 | 1.93 → 1.93 (5 → 5) | `judge_unharmed_B/` |
| C | **NO CLEAR DIFFERENCE** | 133.8 → 134.3 | 211 → 213 | +2 / −0 | 1.93 → 1.93 (5 → 5) | `judge_unharmed_C/` |
| D | **NO CLEAR DIFFERENCE** | 133.8 → 135.38 | 211 → 214 | +3 / −0 | 1.93 → 1.93 (5 → 5) | `judge_unharmed_D/` |
| CD | **NO CLEAR DIFFERENCE** | 133.8 → 135.63 | 211 → 215 | +4 / −0 | 1.93 → 1.93 (5 → 5) | `judge_unharmed_CD/` |

## (d) Boxes on the empty train frames (every condition)

| arm | fixed colors, unharmed | fixed colors, 1 px shaved off | fixed colors, 2 px shaved off | fixed colors, 1 px added | hand colors, unharmed | hand colors, 1 px shaved off | hand colors, 2 px shaved off |
|---|---|---|---|---|---|---|---|
| B | 0 → 0 (new 0) | 0 → 0 (new 0) | 0 → 0 (new 0) | 3 → 3 (new 0) | 2 → 3 (new 1) | 0 → 0 (new 0) | 0 → 0 (new 0) |
| C | 0 → 0 (new 0) | 0 → 0 (new 0) | 0 → 0 (new 0) | 3 → 3 (new 0) | 2 → 2 (new 0) | 0 → 0 (new 0) | 0 → 0 (new 0) |
| D | 0 → 0 (new 0) | 0 → 0 (new 0) | 0 → 0 (new 0) | 3 → 3 (new 0) | 2 → 2 (new 0) | 0 → 0 (new 0) | 0 → 0 (new 0) |
| CD | 0 → 0 (new 0) | 0 → 0 (new 0) | 0 → 0 (new 0) | 3 → 3 (new 0) | 2 → 2 (new 0) | 0 → 0 (new 0) | 0 → 0 (new 0) |

New boxes on empty frames: 4A8B_lampmid3_bathtile_neg_02 [hand] orange [505, 122, 561, 167].

The simulated scenes and the other masks of the collapse harness: `harness.md` (made by `harness_flag.py`).

## (e) Hand-set colors (the median per condition)

**unharmed**

| arm | all ordinary | the conditions with hand labels | judge on this mask (placements) |
|---|---|---|---|
| B | 281 → 283 (back 0 of 0; other +2 −0); not on barrel 3 → 7 | 192 → 194 (back 0 of 0; other +2 −0); not on barrel 3 → 7 | NO CLEAR DIFFERENCE: 156.83 → 157.33, boxes 1.5 → 2.58 |
| C | 281 → 281 (back 0 of 0; other +0 −0); not on barrel 3 → 3 | 192 → 192 (back 0 of 0; other +0 −0); not on barrel 3 → 3 | NO CLEAR DIFFERENCE: 156.83 → 156.83, boxes 1.5 → 1.5 |
| D | 281 → 283 (back 0 of 0; other +2 −0); not on barrel 3 → 3 | 192 → 194 (back 0 of 0; other +2 −0); not on barrel 3 → 3 | NO CLEAR DIFFERENCE: 156.83 → 157.33, boxes 1.5 → 1.5 |
| CD | 281 → 283 (back 0 of 0; other +2 −0); not on barrel 3 → 3 | 192 → 194 (back 0 of 0; other +2 −0); not on barrel 3 → 3 | NO CLEAR DIFFERENCE: 156.83 → 157.33, boxes 1.5 → 1.5 |

Today's detector, hand colors, unharmed: 281 of 307; on this mask 281.

**one pixel shaved off**

| arm | all ordinary | the conditions with hand labels | judge on this mask (placements) |
|---|---|---|---|
| B | 223 → 245 (back 22 of 61; other +0 −0); not on barrel 2 → 1 | 147 → 163 (back 16 of 47; other +0 −0); not on barrel 1 → 1 | PASS: 131.83 → 142.32, boxes 2.0 → 1.0 |
| C | 223 → 230 (back 7 of 61; other +0 −0); not on barrel 2 → 1 | 147 → 149 (back 2 of 47; other +0 −0); not on barrel 1 → 1 | PASS: 131.83 → 137.33, boxes 2.0 → 1.0 |
| D | 223 → 245 (back 22 of 61; other +0 −0); not on barrel 2 → 1 | 147 → 163 (back 16 of 47; other +0 −0); not on barrel 1 → 1 | PASS: 131.83 → 142.32, boxes 2.0 → 1.0 |
| CD | 223 → 245 (back 22 of 61; other +0 −0); not on barrel 2 → 1 | 147 → 163 (back 16 of 47; other +0 −0); not on barrel 1 → 1 | PASS: 131.83 → 142.32, boxes 2.0 → 1.0 |

Today's detector, hand colors, unharmed: 281 of 307; on this mask 223.

**two pixels shaved off**

| arm | all ordinary | the conditions with hand labels | judge on this mask (placements) |
|---|---|---|---|
| B | 133 → 204 (back 69 of 150; other +2 −0); not on barrel 1 → 0 | 92 → 133 (back 39 of 102; other +2 −0); not on barrel 0 → 0 | PASS: 75.8 → 121.92, boxes 1.0 → 0.0 |
| C | 133 → 134 (back 1 of 150; other +0 −0); not on barrel 1 → 1 | 92 → 92 (back 0 of 102; other +0 −0); not on barrel 0 → 0 | NO CLEAR DIFFERENCE: 75.8 → 76.8, boxes 1.0 → 1.0 |
| D | 133 → 201 (back 66 of 150; other +2 −0); not on barrel 1 → 0 | 92 → 132 (back 38 of 102; other +2 −0); not on barrel 0 → 0 | PASS: 75.8 → 119.67, boxes 1.0 → 0.0 |
| CD | 133 → 201 (back 66 of 150; other +2 −0); not on barrel 1 → 0 | 92 → 132 (back 38 of 102; other +2 −0); not on barrel 0 → 0 | PASS: 75.8 → 119.67, boxes 1.0 → 0.0 |

Today's detector, hand colors, unharmed: 281 of 307; on this mask 133.

## Every box that appears or disappears on a real frame

253 boxes over the six real masks (fixed and hand colors; unharmed, one and two pixels shaved off), 13 sheets in `sheets/`, the list in `boxes_changed.csv` (tile number = the number on the sheet). Left the photo, right the mask the detector saw. White = the hand boxes, gray = today's boxes on that mask, magenta = a box that appears, red = one that disappears.

| arm | appears: found | appears: on its barrel, box off | appears: second box | appears: wrong color | appears: on nothing | disappears: was found | disappears: was off | disappears: was not on a barrel |
|---|---|---|---|---|---|---|---|---|
| B | 193 | 15 | 0 | 0 | 4 | 25 | 0 | 4 |
| C | 26 | 0 | 0 | 2 | 0 | 9 | 0 | 4 |
| D | 186 | 12 | 0 | 0 | 0 | 24 | 0 | 4 |
| CD | 190 | 12 | 0 | 0 | 0 | 27 | 0 | 4 |
