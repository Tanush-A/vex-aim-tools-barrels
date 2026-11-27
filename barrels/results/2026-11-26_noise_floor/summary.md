# The noise floor of the counts (2026-11-27, git fa3b289)

`python barrels/experiments/2026-11-26_noise_floor/run.py` (plan: `../../experiments/2026-11-26_noise_floor/PREREG.md` and its addendum; the first run, before the addendum: `first_run/`). Train frames only; test frames never opened. 261 frames; the ordinary conditions are 154 frames, 172 placements (307 barrels when every light is counted) at 8 places.

## In short

- **A change that means nothing moves found by up to 9.42 placements down and 4 up** over the ordinary conditions (172 placements). One number moved one step: median 0.56, 90th percentile 3.6, largest 5.2. Several numbers at once: median 3.2, largest 9.42.
- **It is one-sided.** Of the 26 neighbours, 15 lose found and 8 gain. The fixed model was picked because it scores well, so a small move mostly hurts it.
- **At one condition** (about 15 barrels): no change for most neighbours (median 0, 90th percentile 0 for one step, 3 for joint moves), but up to 5 barrels in the worst case.
- **At one place:** median 0, 90th percentile 0.33, largest 5 placements for one step (joint moves: 0.2 / 2.33 / 5).
- **Clean empty frames:** no neighbour of sets A and B puts a box on a clean empty frame. The zero for clean empty frames stays.
- **The check on moves the margins have never seen (set C):** 2 of 12 get a verdict other than NO CLEAR DIFFERENCE (check01: PASS, check08: FAIL); 0 of 12 fail the never-regress check.

The fixed model: orange hue 3..13, S >= 140; blue hue 103..119, S >= 113; brightness floor 40. With it: found 135.4 of 172 placements (214 of 307 per frame), 3 found with the box off, 5 boxes not on their barrel, 0 on empty frames.

## The margins

Each margin is the largest change, in that direction, that a neighbour of sets A and B produced at that level, and never less than one whole unit. Units: placements for found; boxes counted once per arrangement.

- **Pass rule, found over the ordinary conditions:** better above **+4.00**, worse below **-9.42**.
- **Pass rule, boxes not on their barrel:** worse above +1.85, better below -1.00.
- **Pass rule, boxes on empty frames:** with clutter, worse above +1.00; clean, any new box (margin 0).
- **Pass rule, each place (a drop in found larger than):** home_white 1.00, campus_study 1.00, abp_gray 5.00, home_bathtile 1.00, home_glass 1.00, home_ottoman 2.00, uc_palewood 1.00, abp_white 1.00; a place not measured: 1.0.
- **Never-regress check, each protected set (drop in found / rise in boxes):** HOME 1.00 / 1.00, CAMPUS 1.00 / 1.00, GLASS 1.00 / 1.00, PALEWOOD 1.00 / 1.00, ABPWHITE 1.00 / 1.00, BATH-COOL 4.00 / 1.00; boxes on empty frames with clutter, all train sets: 1.00; on clean empty frames: 0.
- *As first registered* (the largest absolute change, the same both ways; kept for the record in `margins.json`): found 9.42, boxes 1.85.

## Every neighbour, the ordinary conditions together (neighbour minus fixed)

found = strict, per placement; either way = strict or found with the box off; boxes = not on their barrel, once per arrangement; a dot = no change. The last two columns apply the pass rule and the never-regress check with the margins above: by construction "no clear difference" and "pass" for sets A and B, a real check for set C.

| set | neighbour | what moved | found | found per frame | found either way | boxes | boxes per frame | on clean empty | on empty with clutter | largest drop at one place | pass rule | never-regress check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| A | orange_h_lo-1 | orange_h_lo 3→2 | +4 | +4 | +4 | . | . | . | . | . | no clear difference | pass |
| A | orange_h_lo+1 | orange_h_lo 3→4 | -5.2 | -6 | -4 | -0.2 | -1 | . | . | abp_gray -5 | no clear difference | pass |
| A | orange_h_hi-1 | orange_h_hi 13→12 | -1.75 | -3 | -1.42 | -0.73 | -3 | . | . | home_white -1 | no clear difference | pass |
| A | orange_h_hi+1 | orange_h_hi 13→14 | +2.67 | +8 | +2.67 | +1.25 | +2 | . | . | . | no clear difference | pass |
| A | orange_s_lo-3 | orange_s_lo 140→137 | -0.87 | -1 | -0.67 | +1 | +1 | . | . | uc_palewood -1 | no clear difference | pass |
| A | orange_s_lo+3 | orange_s_lo 140→143 | -0.08 | . | -0.08 | +1 | +1 | . | . | home_ottoman -0.33 | no clear difference | pass |
| A | blue_h_lo-1 | blue_h_lo 103→102 | +0.25 | +1 | +0.25 | +0.8 | +4 | . | +0.6 | . | no clear difference | pass |
| A | blue_h_lo+1 | blue_h_lo 103→104 | -2.33 | -6 | -1.42 | -0.2 | -1 | . | . | campus_study -1 | no clear difference | pass |
| A | blue_h_hi-1 | blue_h_hi 119→118 | -1 | -1 | . | . | . | . | . | abp_gray -1 | no clear difference | pass |
| A | blue_h_hi+1 | blue_h_hi 119→120 | . | . | . | . | . | . | . | . | no clear difference | pass |
| A | blue_s_lo-3 | blue_s_lo 113→110 | +0.05 | . | +0.25 | . | . | . | . | home_glass -0.2 | no clear difference | pass |
| A | blue_s_lo+3 | blue_s_lo 113→116 | -0.25 | -1 | -0.58 | -0.2 | -1 | . | . | home_bathtile -0.25 | no clear difference | pass |
| A | v_min-2 | v_min 40→38 | . | . | . | . | . | . | . | . | no clear difference | pass |
| A | v_min+2 | v_min 40→42 | . | . | . | . | . | . | . | . | no clear difference | pass |
| B | joint01 | orange_s_lo 140→137, blue_h_lo 103→104, blue_h_hi 119→120, blue_s_lo 113→110 | -3.15 | -7 | -1.83 | +0.8 | . | . | . | campus_study -1 | no clear difference | pass |
| B | joint02 | orange_h_hi 13→14, orange_s_lo 140→137, blue_h_lo 103→104, blue_h_hi 119→120, v_min 40→38 | -0.53 | +1 | +0.58 | +0.33 | +1 | . | . | campus_study -1 | no clear difference | pass |
| B | joint03 | orange_s_lo 140→137, blue_h_lo 103→104, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→42 | -4.2 | -8 | -2.08 | +0.8 | . | . | . | campus_study -1 | no clear difference | pass |
| B | joint04 | orange_h_lo 3→4, blue_h_lo 103→104, v_min 40→38 | -7.53 | -12 | -5.42 | -0.2 | -1 | . | . | abp_gray -5 | no clear difference | pass |
| B | joint05 | orange_h_hi 13→12, orange_s_lo 140→143, blue_h_lo 103→104, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→38 | -5.75 | -12 | -3.5 | +0.27 | -2 | . | . | home_ottoman -2 | no clear difference | pass |
| B | joint06 | orange_h_hi 13→14, blue_h_hi 119→120 | +2.67 | +8 | +2.67 | +1.25 | +2 | . | . | . | no clear difference | pass |
| B | joint07 | orange_h_lo 3→2, blue_h_lo 103→102, blue_h_hi 119→118 | +3.25 | +4 | +4.25 | +0.8 | +4 | . | +0.6 | . | no clear difference | pass |
| B | joint08 | orange_h_lo 3→2, orange_h_hi 13→12, orange_s_lo 140→137, blue_h_lo 103→102, blue_h_hi 119→120 | +1.25 | . | +1.58 | +1.27 | +3 | . | +0.6 | home_white -1 | no clear difference | pass |
| B | joint09 | orange_h_lo 3→4, blue_h_lo 103→104, blue_h_hi 119→120 | -7.53 | -12 | -5.42 | -0.2 | -1 | . | . | abp_gray -5 | no clear difference | pass |
| B | joint10 | orange_h_lo 3→2, orange_s_lo 140→143, blue_h_lo 103→104, blue_h_hi 119→118, v_min 40→38 | +0.58 | -3 | +2.5 | +0.6 | -1 | . | . | campus_study -1 | no clear difference | pass |
| B | joint11 | orange_h_lo 3→4, orange_h_hi 13→14, orange_s_lo 140→143, blue_h_lo 103→102, blue_h_hi 119→120, blue_s_lo 113→110, v_min 40→42 | -2.48 | +2 | -1.08 | +1.85 | +5 | . | +0.2 | abp_gray -5 | no clear difference | pass |
| B | joint12 | orange_h_lo 3→4, orange_h_hi 13→12, blue_h_lo 103→104, blue_s_lo 113→116, v_min 40→42 | -9.42 | -15 | -7.17 | -0.73 | -3 | . | . | abp_gray -5 | no clear difference | pass |
| C | check01 | orange_h_lo 3→2, orange_h_hi 13→14, blue_h_hi 119→120, blue_s_lo 113→110, v_min 40→38 | +6.72 | +12 | +6.92 | +1.25 | +2 | . | . | home_glass -0.2 | PASS | pass |
| C | check02 | orange_s_lo 140→137, blue_h_hi 119→118, blue_s_lo 113→110 | -1.82 | -2 | -0.42 | +1 | +1 | . | . | abp_gray -1 | no clear difference | pass |
| C | check03 | orange_h_lo 3→2, orange_h_hi 13→12, orange_s_lo 140→143, blue_h_lo 103→102, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→42 | +0.58 | -2 | +1.58 | +1.07 | +2 | . | +0.2 | home_ottoman -1.67 | no clear difference | pass |
| C | check04 | orange_h_lo 3→4, orange_s_lo 140→137, blue_h_lo 103→104, blue_h_hi 119→120, blue_s_lo 113→110, v_min 40→38 | -8.35 | -13 | -5.83 | +0.8 | . | . | . | abp_gray -5 | no clear difference | pass |
| C | check05 | orange_h_hi 13→14, orange_s_lo 140→143, blue_h_lo 103→104, blue_h_hi 119→120, blue_s_lo 113→116, v_min 40→42 | -0.08 | +1 | +1.17 | +1.2 | +2 | . | . | campus_study -1 | no clear difference | pass |
| C | check06 | orange_h_lo 3→4, blue_h_lo 103→104, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→38 | -7.53 | -12 | -5.42 | -0.2 | -1 | . | . | abp_gray -5 | no clear difference | pass |
| C | check07 | orange_h_hi 13→12, orange_s_lo 140→143, blue_h_lo 103→102, v_min 40→38 | -2.42 | -5 | -2.08 | +0.87 | +1 | . | +0.2 | home_ottoman -1.67 | no clear difference | pass |
| C | check08 | orange_h_hi 13→14, blue_h_lo 103→104, blue_h_hi 119→118, v_min 40→42 | -0.33 | +2 | +1.58 | +2 | +2 | . | +1 | campus_study -1 | FAIL | pass |
| C | check09 | orange_h_lo 3→2, orange_s_lo 140→143, blue_h_lo 103→104, blue_h_hi 119→118, blue_s_lo 113→116, v_min 40→42 | +0.58 | -3 | +2.5 | +0.8 | . | . | . | campus_study -1 | no clear difference | pass |
| C | check10 | orange_h_lo 3→4, orange_s_lo 140→137, blue_h_lo 103→102, blue_s_lo 113→116, v_min 40→38 | -5.82 | -6 | -4.75 | +1.4 | +3 | . | +0.2 | abp_gray -5 | no clear difference | pass |
| C | check11 | orange_h_hi 13→12, orange_s_lo 140→143, blue_h_lo 103→102, blue_h_hi 119→118, blue_s_lo 113→110, v_min 40→42 | -3.62 | -7 | -2.08 | +1.07 | +2 | . | +0.2 | home_ottoman -1.67 | no clear difference | pass |
| C | check12 | orange_h_lo 3→4, orange_h_hi 13→14, orange_s_lo 140→137, blue_h_hi 119→118 | -3.73 | . | -2.33 | . | . | . | . | abp_gray -5 | no clear difference | pass |

## How far the counts move (absolute change: median / 90th percentile / maximum)

| level | what | one step (set A) | joint moves (set B) | check moves (set C) |
|---|---|---|---|---|
| condition, all | found (per placement; at condition level = per frame) | 0 / 0 / 5 (n 392) | 0 / 2 / 5 (n 336) | 0 / 2 / 5 (n 336) |
| condition, all | found either way | 0 / 0 / 5 (n 392) | 0 / 2 / 5 (n 336) | 0 / 2 / 5 (n 336) |
| condition, all | boxes not on their barrel (per arrangement) | 0 / 0 / 2 (n 392) | 0 / 1 / 2 (n 336) | 0 / 1 / 2 (n 336) |
| condition, all | boxes on nothing (per arrangement) | 0 / 0 / 2 (n 392) | 0 / 0 / 2 (n 336) | 0 / 0 / 2 (n 336) |
| condition, all | boxes on clean empty frames | 0 / 0 / 0 (n 392) | 0 / 0 / 0 (n 336) | 0 / 0 / 0 (n 336) |
| condition, all | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 1 (n 392) | 0 / 0 / 1 (n 336) | 0 / 0 / 1 (n 336) |
| condition, ordinary | found (per placement; at condition level = per frame) | 0 / 0 / 5 (n 238) | 0 / 3 / 5 (n 204) | 0 / 3 / 5 (n 204) |
| condition, ordinary | found either way | 0 / 0 / 5 (n 238) | 0 / 2 / 5 (n 204) | 0 / 2 / 5 (n 204) |
| condition, ordinary | boxes not on their barrel (per arrangement) | 0 / 0 / 2 (n 238) | 0 / 1 / 2 (n 204) | 0 / 1 / 2 (n 204) |
| condition, ordinary | boxes on nothing (per arrangement) | 0 / 0 / 2 (n 238) | 0 / 1 / 2 (n 204) | 0 / 1 / 2 (n 204) |
| condition, ordinary | boxes on clean empty frames | 0 / 0 / 0 (n 238) | 0 / 0 / 0 (n 204) | 0 / 0 / 0 (n 204) |
| condition, ordinary | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 1 (n 238) | 0 / 0 / 1 (n 204) | 0 / 0 / 1 (n 204) |
| place | found (per placement; at condition level = per frame) | 0 / 0.33 / 5 (n 112) | 0.2 / 2.33 / 5 (n 96) | 0.22 / 2.17 / 5 (n 96) |
| place | found either way | 0 / 0.25 / 4 (n 112) | 0 / 2.17 / 4 (n 96) | 0 / 2 / 4 (n 96) |
| place | boxes not on their barrel (per arrangement) | 0 / 0 / 1 (n 112) | 0 / 0.5 / 1 (n 96) | 0 / 1 / 1 (n 96) |
| place | boxes on nothing (per arrangement) | 0 / 0 / 1 (n 112) | 0 / 0.5 / 1 (n 96) | 0 / 1 / 1 (n 96) |
| place | boxes on clean empty frames | 0 / 0 / 0 (n 112) | 0 / 0 / 0 (n 96) | 0 / 0 / 0 (n 96) |
| place | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 0.6 (n 112) | 0 / 0 / 0.6 (n 96) | 0 / 0 / 1 (n 96) |
| protected set | found (per placement; at condition level = per frame) | 0 / 0.76 / 4 (n 84) | 0 / 2.8 / 4 (n 72) | 0 / 1 / 4 (n 72) |
| protected set | found either way | 0 / 0 / 3 (n 84) | 0 / 1.9 / 3 (n 72) | 0 / 1 / 3 (n 72) |
| protected set | boxes not on their barrel (per arrangement) | 0 / 0 / 1 (n 84) | 0 / 0.78 / 1 (n 72) | 0 / 1 / 1 (n 72) |
| protected set | boxes on nothing (per arrangement) | 0 / 0 / 1 (n 84) | 0 / 0.78 / 1 (n 72) | 0 / 1 / 1 (n 72) |
| protected set | boxes on clean empty frames | 0 / 0 / 0 (n 84) | 0 / 0 / 0 (n 72) | 0 / 0 / 0 (n 72) |
| protected set | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 0.6 (n 84) | 0 / 0 / 0.6 (n 72) | 0 / 0 / 1 (n 72) |
| overall, ordinary | found (per placement; at condition level = per frame) | 0.56 / 3.6 / 5.2 (n 14) | 3.2 / 7.53 / 9.42 (n 12) | 3.02 / 7.45 / 8.35 (n 12) |
| overall, ordinary | found either way | 0.42 / 3.6 / 4 (n 14) | 2.58 / 5.42 / 7.17 (n 12) | 2.21 / 5.79 / 6.92 (n 12) |
| overall, ordinary | boxes not on their barrel (per arrangement) | 0.2 / 1 / 1.25 (n 14) | 0.77 / 1.27 / 1.85 (n 12) | 1.03 / 1.38 / 2 (n 12) |
| overall, ordinary | boxes on nothing (per arrangement) | 0.2 / 1 / 1 (n 14) | 0.77 / 1.24 / 1.6 (n 12) | 1 / 1.38 / 2 (n 12) |
| overall, ordinary | boxes on clean empty frames | 0 / 0 / 0 (n 14) | 0 / 0 / 0 (n 12) | 0 / 0 / 0 (n 12) |
| overall, ordinary | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 0.6 (n 14) | 0 / 0.56 / 0.6 (n 12) | 0 / 0.2 / 1 (n 12) |
| overall, all train | found (per placement; at condition level = per frame) | 1.09 / 3.86 / 5.2 (n 14) | 2.32 / 7.28 / 12.14 (n 12) | 1.88 / 7.08 / 7.34 (n 12) |
| overall, all train | found either way | 1.25 / 4.31 / 4.64 (n 14) | 4.07 / 7.26 / 11.14 (n 12) | 2.47 / 5.74 / 9.58 (n 12) |
| overall, all train | boxes not on their barrel (per arrangement) | 0.2 / 0.99 / 1.11 (n 14) | 0.8 / 1.12 / 1.85 (n 12) | 0.9 / 1.47 / 1.67 (n 12) |
| overall, all train | boxes on nothing (per arrangement) | 0.2 / 1 / 1 (n 14) | 0.72 / 1.32 / 1.6 (n 12) | 1 / 1.38 / 2 (n 12) |
| overall, all train | boxes on clean empty frames | 0 / 0 / 0 (n 14) | 0 / 0 / 0 (n 12) | 0 / 0 / 0 (n 12) |
| overall, all train | boxes on empty frames with clutter (per arrangement) | 0 / 0 / 0.6 (n 14) | 0 / 0.56 / 0.6 (n 12) | 0 / 0.2 / 1 (n 12) |
| place | the largest drop in found at any one place, per neighbour | 0.22 / 1 / 5 (n 14) | 1 / 5 / 5 (n 12) | 1.67 / 5 / 5 (n 12) |

n = neighbours x units (28 conditions, 17 ordinary conditions, 8 places, 6 protected sets) or neighbours (overall).

## Place by place: found, per placement

| place | placements | found with the fixed model | largest drop, one step | largest drop, joint | largest gain, any | margin (a drop larger than) | on a threshold edge? |
|---|---:|---:|---:|---:|---:|---:|---|
| home_white | 29 | 28.0 | 1 | 1 | 0 | 1.00 | no |
| campus_study | 35 | 35.0 | 1 | 1 | 0 | 1.00 | no |
| abp_gray | 16 | 11.0 | 5 | 5 | 4 | 5.00 | no |
| home_bathtile | 15 | 4.2 | 1 | 1 | 0.25 | 1.00 | no |
| home_glass | 15 | 14.8 | 0.2 | 0.4 | 0 | 1.00 | no |
| home_ottoman | 15 | 3.3 | 1 | 2 | 2.67 | 2.00 | no |
| uc_palewood | 15 | 13.0 | 1 | 1 | 0 | 1.00 | no |
| abp_white | 32 | 26.0 | 0 | 0 | 0 | 1.00 | no |

No place moves by more than a third of its placements under one step.

## The protected sets

| protected set | placements | found | largest drop in found | margin, found | largest rise in boxes | margin, boxes |
|---|---:|---:|---:|---:|---:|---:|
| HOME | 29 | 28.0 | 1 | 1.00 | 0 | 1.00 |
| CAMPUS | 35 | 35.0 | 1 | 1.00 | 0 | 1.00 |
| GLASS | 15 | 14.8 | 0.4 | 1.00 | 0.8 | 1.00 |
| PALEWOOD | 15 | 13.0 | 1 | 1.00 | 1 | 1.00 |
| ABPWHITE | 32 | 26.0 | 0 | 1.00 | 0 | 1.00 |
| BATH-COOL | 15 | 14.0 | 4 | 4.00 | 0 | 1.00 |

HOME is scored here with the model as it is (a neighbour is a model moved by hand; there is nothing to re-fit). The never-regress check itself keeps the leave-one-scene-out protocol for HOME; its margin is a difference and is taken from here.

## How the margins were arrived at (the registered rules, in order)

1. *Rule 1 as first registered:* the largest absolute change in set A, at least one unit: found 5.20, boxes 1.25; places home_white 1.00, campus_study 1.00, abp_gray 5.00, home_bathtile 1.00, home_glass 1.00, home_ottoman 2.67, uc_palewood 1.00, abp_white 1.00.
2. *Rule 3:* with those margins, 6 of 12 joint moves get a verdict other than NO CLEAR DIFFERENCE (joint04: FAIL, joint05: FAIL, joint08: FAIL, joint09: FAIL, joint11: FAIL, joint12: FAIL) and 0 of 12 fail the never-regress check. More than 2: small changes that come together add up, so the margins are taken over sets A and B.
3. *The addendum (written after the first run, before any candidate was judged):* the changes are one-sided, so each margin is taken per direction. The absolute version would ask for a gain of 9.42 placements when no change that means nothing gained more than 4.00.
4. *Set C,* 12 joint moves the margins have never seen: 2 of 12 called by the pass rule, 0 of 12 fail the never-regress check (with the margins as first registered: 1 of 12 called by the pass rule).

Files: `noise.json` (every change at every level), `per_neighbour.csv`; the margins as data: `results/baseline/margins.json`.
