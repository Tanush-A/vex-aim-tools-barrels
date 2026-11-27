# The noise floor of the counts (2026-11-27, git 50a7e7f)

`python barrels/experiments/2026-11-26_noise_floor/run.py` (plan: `../../experiments/2026-11-26_noise_floor/PREREG.md` and its addendum; the first run, before the addendum: `first_run/`). Train frames only; test frames never opened. 261 frames; the ordinary conditions are 154 frames, 172 placements (307 barrels when every light is counted) at 8 places.

## In short

- **A change that means nothing moves found by up to 2.78 placements down and 0.33 up** over the ordinary conditions (172 placements). One number moved one step: median 0.18, 90th percentile 0.97, largest 1.2. Several numbers at once: median 1.95, largest 2.78.
- **It is one-sided.** Of the 26 neighbours, 17 lose found and 3 gain. The fixed model was picked because it scores well, so a small move mostly hurts it.
- **At one condition** (about 15 barrels): no change for most neighbours (median 0, 90th percentile 0 for one step, 1 for joint moves), but up to 1 barrels in the worst case.
- **At one place:** median 0, 90th percentile 0.25, largest 1 placements for one step (joint moves: 0.2 / 1 / 1).
- **Clean empty frames:** no neighbour of sets A and B puts a box on a clean empty frame. The zero for clean empty frames stays.
- **The check on moves the margins have never seen (set C):** 2 of 12 get a verdict other than NO CLEAR DIFFERENCE (check04: FAIL, check08: FAIL); 0 of 12 fail the never-regress check.

The fixed model: orange hue 3..13, S >= 140; blue hue 103..119, S >= 113; brightness floor 40. With it: found 156.6 of 172 placements (277 of 307 per frame), 4 found with the box off, 7 boxes not on their barrel, 0 on empty frames.

## The margins

Each margin is the largest change, in that direction, that a neighbour of sets A and B produced at that level, and never less than one whole unit. Units: placements for found; boxes counted once per arrangement.

- **Pass rule, found over the ordinary conditions:** better above **+1.00**, worse below **-2.79**.
- **Pass rule, boxes not on their barrel:** worse above +2.10, better below -1.24.
- **Pass rule, boxes on empty frames:** with clutter, worse above +1.00; clean, any new box (margin 0).
- **Pass rule, each place (a drop in found larger than):** home_white 1.00, campus_study 1.00, abp_gray 1.00, home_bathtile 1.00, home_glass 1.00, home_ottoman 1.00, uc_palewood 1.00, abp_white 1.00; a place not measured: 1.0.
- **Never-regress check, each protected set (drop in found / rise in boxes):** HOME 1.00 / 1.00, CAMPUS 1.00 / 1.00, GLASS 1.00 / 1.00, PALEWOOD 1.00 / 1.00, ABPWHITE 1.00 / 1.00, BATH-COOL 1.00 / 1.00; boxes on empty frames with clutter, all train sets: 1.00; on clean empty frames: 0.
- *As first registered* (the largest absolute change, the same both ways; kept for the record in `margins.json`): found 2.79, boxes 2.10.

## Every neighbour, the ordinary conditions together (neighbour minus fixed)

found = strict, per placement; either way = strict or found with the box off; boxes = not on their barrel, once per arrangement; a dot = no change. The last two columns apply the pass rule and the never-regress check with the margins above: by construction "no clear difference" and "pass" for sets A and B, a real check for set C.

| set | neighbour | what moved | found | found per frame | found either way | boxes | boxes per frame | on clean empty | on empty with clutter | largest drop at one place | pass rule | never-regress check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| A | orange_h_lo-1 | orange_h_lo 3→2 | . | . | . | . | . | . | . | . | no clear difference | pass |
| A | orange_h_lo+1 | orange_h_lo 3→4 | -1.2 | -2 | . | -0.2 | -1 | . | . | abp_gray -1 | no clear difference | pass |
| A | orange_h_hi-1 | orange_h_hi 13→12 | -0.67 | . | -0.33 | -1.23 | -5 | . | . | home_white -1 | no clear difference | pass |
| A | orange_h_hi+1 | orange_h_hi 13→14 | +0.17 | . | +0.42 | +1.75 | +4 | . | . | home_bathtile -0.5 | no clear difference | pass |
| A | orange_s_lo-3 | orange_s_lo 140→137 | -0.87 | -1 | -0.67 | +1.25 | +2 | . | . | uc_palewood -1 | no clear difference | pass |
| A | orange_s_lo+3 | orange_s_lo 140→143 | . | . | . | +1 | +1 | . | . | . | no clear difference | pass |
| A | blue_h_lo-1 | blue_h_lo 103→102 | . | . | . | +0.8 | +4 | . | +0.6 | . | no clear difference | pass |
| A | blue_h_lo+1 | blue_h_lo 103→104 | -0.92 | -1 | . | -0.2 | -1 | . | . | campus_study -1 | no clear difference | pass |
| A | blue_h_hi-1 | blue_h_hi 119→118 | -1 | -1 | . | . | . | . | . | abp_gray -1 | no clear difference | pass |
| A | blue_h_hi+1 | blue_h_hi 119→120 | . | . | . | . | . | . | . | . | no clear difference | pass |
| A | blue_s_lo-3 | blue_s_lo 113→110 | -0.2 | -1 | . | . | . | . | . | home_glass -0.2 | no clear difference | pass |
| A | blue_s_lo+3 | blue_s_lo 113→116 | +0.33 | +1 | . | -0.2 | -1 | . | . | . | no clear difference | pass |
| A | v_min-2 | v_min 40→38 | . | . | . | . | . | . | . | . | no clear difference | pass |
| A | v_min+2 | v_min 40→42 | . | . | . | . | . | . | . | . | no clear difference | pass |
| B | joint01 | orange_s_lo 140→137, blue_h_lo 103→104, blue_h_hi 119→120, blue_s_lo 113→110 | -1.98 | -3 | -0.67 | +1.05 | +1 | . | . | campus_study -1 | no clear difference | pass |
| B | joint02 | orange_h_hi 13→14, orange_s_lo 140→137, blue_h_lo 103→104, blue_h_hi 119→120, v_min 40→38 | -1.7 | -2 | -0.33 | +0.33 | +1 | . | . | campus_study -1 | no clear difference | pass |
| B | joint03 | orange_s_lo 140→137, blue_h_lo 103→104, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→42 | -2.78 | -3 | -0.67 | +1.05 | +1 | . | . | campus_study -1 | no clear difference | pass |
| B | joint04 | orange_h_lo 3→4, blue_h_lo 103→104, v_min 40→38 | -2.12 | -3 | . | -0.2 | -1 | . | . | campus_study -1 | no clear difference | pass |
| B | joint05 | orange_h_hi 13→12, orange_s_lo 140→143, blue_h_lo 103→104, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→38 | -2.58 | -2 | -0.33 | -0.23 | -4 | . | . | home_white -1 | no clear difference | pass |
| B | joint06 | orange_h_hi 13→14, blue_h_hi 119→120 | +0.17 | . | +0.42 | +1.75 | +4 | . | . | home_bathtile -0.5 | no clear difference | pass |
| B | joint07 | orange_h_lo 3→2, blue_h_lo 103→102, blue_h_hi 119→118 | -1 | -1 | . | +0.8 | +4 | . | +0.6 | abp_gray -1 | no clear difference | pass |
| B | joint08 | orange_h_lo 3→2, orange_h_hi 13→12, orange_s_lo 140→137, blue_h_lo 103→102, blue_h_hi 119→120 | -1.67 | -1 | -1.33 | +0.77 | +1 | . | +0.6 | home_white -1 | no clear difference | pass |
| B | joint09 | orange_h_lo 3→4, blue_h_lo 103→104, blue_h_hi 119→120 | -2.12 | -3 | . | -0.2 | -1 | . | . | campus_study -1 | no clear difference | pass |
| B | joint10 | orange_h_lo 3→2, orange_s_lo 140→143, blue_h_lo 103→104, blue_h_hi 119→118, v_min 40→38 | -1.92 | -2 | . | +0.6 | -1 | . | . | campus_study -1 | no clear difference | pass |
| B | joint11 | orange_h_lo 3→4, orange_h_hi 13→14, orange_s_lo 140→143, blue_h_lo 103→102, blue_h_hi 119→120, blue_s_lo 113→110, v_min 40→42 | -1.23 | -3 | +0.42 | +2.1 | +6 | . | +0.2 | abp_gray -1 | no clear difference | pass |
| B | joint12 | orange_h_lo 3→4, orange_h_hi 13→12, blue_h_lo 103→104, blue_s_lo 113→116, v_min 40→42 | -2.58 | -2 | -0.33 | -0.23 | -4 | . | . | home_white -1 | no clear difference | pass |
| C | check01 | orange_h_lo 3→2, orange_h_hi 13→14, blue_h_hi 119→120, blue_s_lo 113→110, v_min 40→38 | -0.03 | -1 | +0.42 | +1.5 | +3 | . | . | home_bathtile -0.5 | no clear difference | pass |
| C | check02 | orange_s_lo 140→137, blue_h_hi 119→118, blue_s_lo 113→110 | -2.07 | -3 | -0.67 | +1.25 | +2 | . | . | abp_gray -1 | no clear difference | pass |
| C | check03 | orange_h_lo 3→2, orange_h_hi 13→12, orange_s_lo 140→143, blue_h_lo 103→102, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→42 | -1.33 | . | -0.33 | +0.57 | . | . | +0.2 | home_white -1 | no clear difference | pass |
| C | check04 | orange_h_lo 3→4, orange_s_lo 140→137, blue_h_lo 103→104, blue_h_hi 119→120, blue_s_lo 113→110, v_min 40→38 | -3.18 | -5 | -0.67 | +0.8 | . | . | . | campus_study -1 | FAIL | pass |
| C | check05 | orange_h_hi 13→14, orange_s_lo 140→143, blue_h_lo 103→104, blue_h_hi 119→120, blue_s_lo 113→116, v_min 40→42 | -1.17 | -2 | +0.33 | +1.45 | +3 | . | . | campus_study -1 | no clear difference | pass |
| C | check06 | orange_h_lo 3→4, blue_h_lo 103→104, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→38 | -2.12 | -3 | . | -0.2 | -1 | . | . | campus_study -1 | no clear difference | pass |
| C | check07 | orange_h_hi 13→12, orange_s_lo 140→143, blue_h_lo 103→102, v_min 40→38 | -0.67 | . | -0.33 | +0.37 | -1 | . | +0.2 | home_white -1 | no clear difference | pass |
| C | check08 | orange_h_hi 13→14, blue_h_lo 103→104, blue_h_hi 119→118, v_min 40→42 | -1.5 | -1 | +0.67 | +2.5 | +4 | . | +1 | campus_study -1 | FAIL | pass |
| C | check09 | orange_h_lo 3→2, orange_s_lo 140→143, blue_h_lo 103→104, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→42 | -1.92 | -2 | . | +0.8 | . | . | . | campus_study -1 | no clear difference | pass |
| C | check10 | orange_h_lo 3→4, orange_s_lo 140→137, blue_h_lo 103→102, blue_s_lo 113→116, v_min 40→38 | -1.73 | -2 | -0.67 | +1.4 | +3 | . | +0.2 | abp_gray -1 | no clear difference | pass |
| C | check11 | orange_h_hi 13→12, orange_s_lo 140→143, blue_h_lo 103→102, blue_h_hi 119→118, blue_s_lo 113→110, v_min 40→42 | -1.87 | -2 | -0.33 | +0.57 | . | . | +0.2 | home_white -1 | no clear difference | pass |
| C | check12 | orange_h_lo 3→4, orange_h_hi 13→14, orange_s_lo 140→137, blue_h_hi 119→118 | -1.98 | -3 | -0.33 | +0.25 | +1 | . | . | abp_gray -1 | no clear difference | pass |

## How far the counts move (absolute change: median / 90th percentile / maximum)

| level | what | one step (set A) | joint moves (set B) | check moves (set C) |
|---|---|---|---|---|
| condition, all | found (per placement; at condition level = per frame) | 0 / 0 / 3 (n 392) | 0 / 1 / 5 (n 336) | 0 / 1 / 6 (n 336) |
| condition, all | found either way | 0 / 0 / 3 (n 392) | 0 / 1 / 5 (n 336) | 0 / 1 / 5 (n 336) |
| condition, all | boxes not on their barrel (per arrangement) | 0 / 0 / 2 (n 392) | 0 / 1 / 2 (n 336) | 0 / 1 / 2 (n 336) |
| condition, all | boxes on nothing (per arrangement) | 0 / 0 / 2 (n 392) | 0 / 1 / 2 (n 336) | 0 / 0.5 / 2 (n 336) |
| condition, all | boxes on clean empty frames | 0 / 0 / 0 (n 392) | 0 / 0 / 0 (n 336) | 0 / 0 / 0 (n 336) |
| condition, all | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 1 (n 392) | 0 / 0 / 1 (n 336) | 0 / 0 / 1 (n 336) |
| condition, ordinary | found (per placement; at condition level = per frame) | 0 / 0 / 1 (n 238) | 0 / 1 / 2 (n 204) | 0 / 1 / 2 (n 204) |
| condition, ordinary | found either way | 0 / 0 / 1 (n 238) | 0 / 1 / 2 (n 204) | 0 / 1 / 1 (n 204) |
| condition, ordinary | boxes not on their barrel (per arrangement) | 0 / 0 / 2 (n 238) | 0 / 1 / 2 (n 204) | 0 / 1 / 2 (n 204) |
| condition, ordinary | boxes on nothing (per arrangement) | 0 / 0 / 2 (n 238) | 0 / 1 / 2 (n 204) | 0 / 1 / 2 (n 204) |
| condition, ordinary | boxes on clean empty frames | 0 / 0 / 0 (n 238) | 0 / 0 / 0 (n 204) | 0 / 0 / 0 (n 204) |
| condition, ordinary | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 1 (n 238) | 0 / 0 / 1 (n 204) | 0 / 0 / 1 (n 204) |
| place | found (per placement; at condition level = per frame) | 0 / 0.25 / 1 (n 112) | 0.2 / 1 / 1 (n 96) | 0 / 1 / 1 (n 96) |
| place | found either way | 0 / 0 / 1 (n 112) | 0 / 0.67 / 1 (n 96) | 0 / 0.67 / 1 (n 96) |
| place | boxes not on their barrel (per arrangement) | 0 / 0.18 / 1 (n 112) | 0 / 0.68 / 1 (n 96) | 0 / 1 / 1 (n 96) |
| place | boxes on nothing (per arrangement) | 0 / 0 / 1 (n 112) | 0 / 0.5 / 1 (n 96) | 0 / 1 / 1 (n 96) |
| place | boxes on clean empty frames | 0 / 0 / 0 (n 112) | 0 / 0 / 0 (n 96) | 0 / 0 / 0 (n 96) |
| place | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 0.6 (n 112) | 0 / 0 / 0.6 (n 96) | 0 / 0 / 1 (n 96) |
| protected set | found (per placement; at condition level = per frame) | 0 / 0 / 1 (n 84) | 0 / 1 / 1 (n 72) | 0 / 1 / 1 (n 72) |
| protected set | found either way | 0 / 0 / 1 (n 84) | 0 / 0 / 1 (n 72) | 0 / 0 / 1 (n 72) |
| protected set | boxes not on their barrel (per arrangement) | 0 / 0 / 1 (n 84) | 0 / 0.98 / 1 (n 72) | 0 / 1 / 1 (n 72) |
| protected set | boxes on nothing (per arrangement) | 0 / 0 / 1 (n 84) | 0 / 0.78 / 1 (n 72) | 0 / 1 / 1 (n 72) |
| protected set | boxes on clean empty frames | 0 / 0 / 0 (n 84) | 0 / 0 / 0 (n 72) | 0 / 0 / 0 (n 72) |
| protected set | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 0.6 (n 84) | 0 / 0 / 0.6 (n 72) | 0 / 0 / 1 (n 72) |
| overall, ordinary | found (per placement; at condition level = per frame) | 0.18 / 0.97 / 1.2 (n 14) | 1.95 / 2.58 / 2.78 (n 12) | 1.8 / 2.11 / 3.18 (n 12) |
| overall, ordinary | found either way | 0 / 0.39 / 0.67 (n 14) | 0.33 / 0.67 / 1.33 (n 12) | 0.33 / 0.67 / 0.67 (n 12) |
| overall, ordinary | boxes not on their barrel (per arrangement) | 0.2 / 1.24 / 1.75 (n 14) | 0.68 / 1.68 / 2.1 (n 12) | 0.8 / 1.49 / 2.5 (n 12) |
| overall, ordinary | boxes on nothing (per arrangement) | 0.2 / 1.18 / 1.25 (n 14) | 0.77 / 1.27 / 1.6 (n 12) | 1.03 / 1.38 / 2.25 (n 12) |
| overall, ordinary | boxes on clean empty frames | 0 / 0 / 0 (n 14) | 0 / 0 / 0 (n 12) | 0 / 0 / 0 (n 12) |
| overall, ordinary | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 0.6 (n 14) | 0 / 0.56 / 0.6 (n 12) | 0 / 0.2 / 1 (n 12) |
| overall, all train | found (per placement; at condition level = per frame) | 0.62 / 1.84 / 2.11 (n 14) | 1.36 / 3.12 / 4.04 (n 12) | 0.99 / 2.83 / 4.43 (n 12) |
| overall, all train | found either way | 0 / 2.14 / 3.11 (n 14) | 1.58 / 3.04 / 5.36 (n 12) | 1.82 / 3.19 / 4.47 (n 12) |
| overall, all train | boxes not on their barrel (per arrangement) | 0.2 / 1.52 / 1.75 (n 14) | 0.75 / 1.68 / 2.21 (n 12) | 0.63 / 2.17 / 3.39 (n 12) |
| overall, all train | boxes on nothing (per arrangement) | 0.2 / 1.18 / 1.25 (n 14) | 0.78 / 1.25 / 1.6 (n 12) | 1.02 / 1.39 / 2.25 (n 12) |
| overall, all train | boxes on clean empty frames | 0 / 0 / 0 (n 14) | 0 / 0 / 0 (n 12) | 0 / 0 / 0 (n 12) |
| overall, all train | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 0.6 (n 14) | 0 / 0.56 / 0.6 (n 12) | 0 / 0.2 / 1 (n 12) |
| place | the largest drop in found at any one place, per neighbour | 0.1 / 1 / 1 (n 14) | 1 / 1 / 1 (n 12) | 1 / 1 / 1 (n 12) |

n = neighbours x units (28 conditions, 17 ordinary conditions, 8 places, 6 protected sets) or neighbours (overall).

## Place by place: found, per placement

| place | placements | found with the fixed model | largest drop, one step | largest drop, joint | largest gain, any | margin (a drop larger than) | on a threshold edge? |
|---|---:|---:|---:|---:|---:|---:|---|
| home_white | 29 | 28.0 | 1 | 1 | 0 | 1.00 | no |
| campus_study | 35 | 35.0 | 1 | 1 | 0 | 1.00 | no |
| abp_gray | 16 | 15.0 | 1 | 1 | 0 | 1.00 | no |
| home_bathtile | 15 | 13.5 | 0.5 | 0.5 | 0 | 1.00 | no |
| home_glass | 15 | 14.8 | 0.2 | 0.4 | 0 | 1.00 | no |
| home_ottoman | 15 | 10.3 | 0 | 0 | 1 | 1.00 | no |
| uc_palewood | 15 | 13.0 | 1 | 1 | 0 | 1.00 | no |
| abp_white | 32 | 27.0 | 0 | 0 | 0 | 1.00 | no |

No place moves by more than a third of its placements under one step.

## The protected sets

| protected set | placements | found | largest drop in found | margin, found | largest rise in boxes | margin, boxes |
|---|---:|---:|---:|---:|---:|---:|
| HOME | 29 | 28.0 | 1 | 1.00 | 1 | 1.00 |
| CAMPUS | 35 | 35.0 | 1 | 1.00 | 0 | 1.00 |
| GLASS | 15 | 14.8 | 0.4 | 1.00 | 0.8 | 1.00 |
| PALEWOOD | 15 | 13.0 | 1 | 1.00 | 1 | 1.00 |
| ABPWHITE | 32 | 27.0 | 0 | 1.00 | 0 | 1.00 |
| BATH-COOL | 15 | 15.0 | 1 | 1.00 | 0 | 1.00 |

HOME is scored here with the model as it is (a neighbour is a model moved by hand; there is nothing to re-fit). The never-regress check itself keeps the leave-one-scene-out protocol for HOME; its margin is a difference and is taken from here.

## How the margins were arrived at (the registered rules, in order)

1. *Rule 1 as first registered:* the largest absolute change in set A, at least one unit: found 1.20, boxes 1.75; places home_white 1.00, campus_study 1.00, abp_gray 1.00, home_bathtile 1.00, home_glass 1.00, home_ottoman 1.00, uc_palewood 1.00, abp_white 1.00.
2. *Rule 3:* with those margins, 10 of 12 joint moves get a verdict other than NO CLEAR DIFFERENCE (joint01: FAIL, joint02: FAIL, joint03: FAIL, joint04: FAIL, joint05: FAIL, joint08: FAIL, joint09: FAIL, joint10: FAIL, joint11: FAIL, joint12: FAIL) and 0 of 12 fail the never-regress check. More than 2: small changes that come together add up, so the margins are taken over sets A and B.
3. *The addendum (written after the first run, before any candidate was judged):* the changes are one-sided, so each margin is taken per direction. The absolute version would ask for a gain of 2.79 placements when no change that means nothing gained more than 1.00.
4. *Set C,* 12 joint moves the margins have never seen: 2 of 12 called by the pass rule, 0 of 12 fail the never-regress check (with the margins as first registered: 2 of 12 called by the pass rule).

Files: `noise.json` (every change at every level), `per_neighbour.csv`; the margins as data: `results/baseline/margins.json`.
