# In-sample views of the judged settings (never a verdict)

`python barrels/experiments/2026-11-26_light/insample.py`. Every number: the setting scored on all 154 ordinary train frames, against the fixed model; found per placement (fixed: 133.8 of 172; bathroom 4.0, ottoman 3.0 of 15), boxes per arrangement. The same frames chose and scored, so the last column is NOT a verdict.

## 1. What a setting picked without a place does at that place

### B1 blue follows the light; light = the brightest 5 % after taking out anything barrel-like (primary)

| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |
|---|---|---|---|---|---|---|---|
| the other places, held out: white, campus_study, abp_gray, glass, ottoman, uc_palewood, abp_white, wooddesk, black | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 88 | +7.42 | +5.75 | +1.67 | +0.75 (+0.75 / +0.00) | +0 / +0.00 | PASS |
| the other places, held out: bathtile | blue follows `without_loose`: from warmth 0.11 to 0.3 the S floor goes 113 -> 45, the hue low end 103 -> 88 | +3.92 | +2.25 | +1.67 | +0.42 (+0.75 / -0.33) | +0 / +0.00 | NO CLEAR DIFFERENCE |
| all eight places | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 88 | +7.42 | +5.75 | +1.67 | +0.75 (+0.75 / +0.00) | +0 / +0.00 | PASS |

### B2 the same; light = the brightest 20 % of the rows above the horizon gate

| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |
|---|---|---|---|---|---|---|---|
| the other places, held out: white, campus_study, abp_gray, glass, ottoman, uc_palewood, abp_white, wooddesk, black | blue follows `above_gate20`: from warmth 0.05 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 88 | +7.42 | +5.75 | +1.67 | +0.95 (+0.75 / +0.00) | +0 / +0.20 | PASS |
| the other places, held out: bathtile | blue follows `above_gate20`: from warmth 0.11 to 0.3 the S floor goes 113 -> 45, the hue low end 103 -> 96 | +2.42 | +0.75 | +1.67 | +0.17 (+0.50 / -0.33) | +0 / +0.00 | NO CLEAR DIFFERENCE |
| all eight places | blue follows `above_gate20`: from warmth 0.05 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 88 | +7.42 | +5.75 | +1.67 | +0.95 (+0.75 / +0.00) | +0 / +0.20 | PASS |

### B3 the same; light = the brightest 5 % of the whole frame (the reading of 2026-11-25)

| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |
|---|---|---|---|---|---|---|---|
| the other places, held out: white, campus_study, abp_gray, glass, ottoman, uc_palewood, abp_white, wooddesk, black | blue follows `whole_frame`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 88 | +7.42 | +5.75 | +1.67 | +0.75 (+0.75 / +0.00) | +0 / +0.00 | PASS |
| the other places, held out: bathtile | blue follows `whole_frame`: from warmth 0.11 to 0.3 the S floor goes 113 -> 45, the hue low end 103 -> 96 | +3.17 | +1.50 | +1.67 | -0.08 (+0.25 / -0.33) | +0 / +0.00 | NO CLEAR DIFFERENCE |
| all eight places | blue follows `whole_frame`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 88 | +7.42 | +5.75 | +1.67 | +0.75 (+0.75 / +0.00) | +0 / +0.00 | PASS |

### B4 = B1 plus 'bluer than the light' for the gray-olive blue

| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |
|---|---|---|---|---|---|---|---|
| the other places, held out: white, campus_study, abp_gray, glass, ottoman, uc_palewood, abp_white, wooddesk, black | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 96; and bluer than the light by 0.25 | +11.42 | +9.75 | +1.67 | +1.00 (+1.00 / +0.00) | +0 / +0.00 | PASS |
| the other places, held out: bathtile | blue follows `without_loose`: from warmth 0.11 to 0.3 the S floor goes 113 -> 60, the hue low end 103 -> 96; and bluer than the light by 0.15 | +13.25 | +10.25 | +3.00 | +4.75 (+4.75 / +0.00) | +0 / +1.25 | FAIL |
| all eight places | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 96; and bluer than the light by 0.25 | +11.42 | +9.75 | +1.67 | +1.00 (+1.00 / +0.00) | +0 / +0.00 | PASS |

### O1 the orange hue high end follows the light

| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |
|---|---|---|---|---|---|---|---|
| the other places, held out: white, campus_study, abp_gray, glass, uc_palewood, abp_white, wooddesk, black | orange hue high end 13 -> 16 as `without_loose` goes 0 -> 0.15 | +1.33 | +0.00 | +1.33 | +0.25 (+0.25 / +0.00) | +0 / +0.00 | NO CLEAR DIFFERENCE |
| the other places, held out: bathtile | orange hue high end 13 -> 22 as `without_loose` goes 0 -> 0.15 | +2.50 | -0.50 | +3.00 | +2.00 (+2.00 / +0.00) | +0 / +0.25 | FAIL |
| the other places, held out: ottoman | the fixed model | +0.00 | +0.00 | +0.00 | +0.00 (+0.00 / +0.00) | +0 / +0.00 | NO CLEAR DIFFERENCE |
| all eight places | orange hue high end 13 -> 16 as `without_loose` goes 0 -> 0.15 | +1.33 | +0.00 | +1.33 | +0.25 (+0.25 / +0.00) | +0 / +0.00 | NO CLEAR DIFFERENCE |

### O2 the orange hue high end follows how dark the scene is

| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |
|---|---|---|---|---|---|---|---|
| the other places, held out: white, campus_study, abp_gray, bathtile, glass, uc_palewood, abp_white, wooddesk, black | orange hue high end 13 -> 16 as `dark` goes 120 -> 60 | +4.67 | +0.00 | +4.67 | +0.00 (+0.00 / +0.00) | +0 / +0.00 | PASS |
| the other places, held out: ottoman | the fixed model | +0.00 | +0.00 | +0.00 | +0.00 (+0.00 / +0.00) | +0 / +0.00 | NO CLEAR DIFFERENCE |
| all eight places | orange hue high end 13 -> 16 as `dark` goes 120 -> 60 | +4.67 | +0.00 | +4.67 | +0.00 (+0.00 / +0.00) | +0 / +0.00 | PASS |

### O3 a wider orange range everywhere it does not flood (the flood guard)

| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |
|---|---|---|---|---|---|---|---|
| the other places, held out: white, campus_study, abp_gray, bathtile, glass, uc_palewood, abp_white, wooddesk, black | orange hue high end 13 -> 16 as `always` goes 0 -> 1, only where the added band is at most 10 % of the frame | +4.67 | +0.00 | +4.67 | +1.50 (+0.50 / +0.00) | +0 / +0.00 | PASS |
| the other places, held out: ottoman | the fixed model | +0.00 | +0.00 | +0.00 | +0.00 (+0.00 / +0.00) | +0 / +0.00 | NO CLEAR DIFFERENCE |
| all eight places | orange hue high end 13 -> 16 as `always` goes 0 -> 1, only where the added band is at most 10 % of the frame | +4.67 | +0.00 | +4.67 | +1.50 (+0.50 / +0.00) | +0 / +0.00 | PASS |

## 2. "Bluer than the light": the margin swept

The ramp of the all-places pick (0.08 to 0.18, S to 30, hue low to 96), reading `without_loose`.

| picked on | the setting | found, all places | found, bathroom (of 15) | found, ottoman (of 15) | boxes not on their barrel, all (bathroom / ottoman) | boxes on empty frames: clean / with clutter | the pass rule on these in-sample numbers |
|---|---|---|---|---|---|---|---|
| no relative rule | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 96 | +6.17 | +4.50 | +1.67 | +1.25 (+1.25 / +0.00) | +0 / +0.00 | PASS |
| delta 0.30 | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 96; and bluer than the light by 0.3 | +9.92 | +8.25 | +1.67 | +1.50 (+1.50 / +0.00) | +0 / +0.00 | PASS |
| delta 0.25 | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 96; and bluer than the light by 0.25 | +11.42 | +9.75 | +1.67 | +1.00 (+1.00 / +0.00) | +0 / +0.00 | PASS |
| delta 0.20 | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 96; and bluer than the light by 0.2 | +11.92 | +10.25 | +1.67 | +2.25 (+2.25 / +0.00) | +0 / +1.00 | FAIL |
| delta 0.15 | blue follows `without_loose`: from warmth 0.08 to 0.18 the S floor goes 113 -> 30, the hue low end 103 -> 96; and bluer than the light by 0.15 | +13.50 | +10.50 | +3.00 | +5.25 (+5.25 / +0.00) | +0 / +1.50 | FAIL |

## 3. The ramp's numbers (family B1, reading `without_loose`, no relative rule)

Gain = found minus boxes not on their barrel, all places. Per value of one number: the mean and the best over the other three.

| number | value: mean gain / best gain |
|---|---|
| start of the ramp (warmth) | 0.05: +4.24 / +6.67; 0.08: +4.13 / +6.67; 0.11: +3.82 / +6.42 |
| end of the ramp (warmth) | 0.18: +5.10 / +6.67; 0.24: +4.39 / +5.67; 0.3: +2.70 / +5.00 |
| blue S floor at the end | 30: +4.64 / +6.67; 45: +4.40 / +5.75; 60: +3.15 / +5.25 |
| blue hue low end at the end | 88: +4.72 / +6.67; 96: +3.41 / +4.92 |

Of the 54 settings, 54 have a gain above zero in-sample; the largest is +6.67, the smallest +0.92.
