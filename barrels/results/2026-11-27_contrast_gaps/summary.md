# Contrast gaps: every judged candidate

Baseline: today's default (fixed colors, detector, stripe by contrast). Ordinary train frames: 154 frames, 172 placements, 8 places.

## Round 1: leave one place out (the registered result)

| candidate | setting | verdict | found per placement | found per frame (strict) | gained / lost (ordinary) | report only gained / lost | boxes not on their barrel (per arrangement) | boxes on empty frames | places that moved (found; boxes) | traps |
|---|---|---|---|---|---|---|---|---|---|---|
| E_edge | per fold | NO CLEAR DIFFERENCE | 156.63 -> 156.63 | 277 -> 277 | 0 / 0 | 3 / 0 | 2.43 -> 2.43 | 0 -> 0 (clean 0 -> 0) | none | clean |
| H_half | per fold | NO CLEAR DIFFERENCE | 156.63 -> 156.63 | 277 -> 277 | 0 / 0 | 0 / 0 | 2.43 -> 2.43 | 0 -> 0 (clean 0 -> 0) | none | clean |
| S_split | per fold | NO CLEAR DIFFERENCE | 156.63 -> 156.63 | 277 -> 277 | 0 / 0 | 0 / 0 | 2.43 -> 2.43 | 0 -> 0 (clean 0 -> 0) | none | clean |
| B_beside | per fold | NO CLEAR DIFFERENCE | 156.63 -> 156.63 | 277 -> 277 | 0 / 0 | 0 / 0 | 2.43 -> 3.43 | 0 -> 0 (clean 0 -> 0) | none; boxes campus_study +1 | clean |
| O_other | per fold | NO CLEAR DIFFERENCE | 156.63 -> 156.63 | 277 -> 277 | 0 / 0 | 0 / 0 | 2.43 -> 2.43 | 0 -> 0 (clean 0 -> 0) | none | clean |
| ALL | per fold | NO CLEAR DIFFERENCE | 156.63 -> 156.63 | 277 -> 277 | 0 / 0 | 3 / 0 | 2.43 -> 3.43 | 0 -> 0 (clean 0 -> 0) | none; boxes campus_study +1 | clean |

## Round 2 (PREREG addendum): fixed at the all-places pick, IN-SAMPLE

| candidate | setting | verdict | found per placement | found per frame (strict) | gained / lost (ordinary) | report only gained / lost | boxes not on their barrel (per arrangement) | boxes on empty frames | places that moved (found; boxes) | traps |
|---|---|---|---|---|---|---|---|---|---|---|
| E_edge | e0.6|h-|s-|b-|o- | NO CLEAR DIFFERENCE | 156.63 -> 157.38 | 277 -> 280 | 3 / 0 | 3 / 0 | 2.43 -> 2.43 | 0 -> 0 (clean 0 -> 0) | home_bathtile +0.75 | clean |
| H_half | e-|h1.3|s-|b-|o- | NO CLEAR DIFFERENCE | 156.63 -> 157.63 | 277 -> 280 | 3 / 0 | 0 / 0 | 2.43 -> 2.43 | 0 -> 0 (clean 0 -> 0) | home_ottoman +1 | clean |
| S_split | e-|h-|s1.25|b-|o- | NO CLEAR DIFFERENCE | 156.63 -> 156.97 | 277 -> 278 | 1 / 0 | 0 / 0 | 2.43 -> 2.43 | 0 -> 0 (clean 0 -> 0) | home_ottoman +0.33 | clean |
| B_beside | e-|h-|s-|b1|o- | NO CLEAR DIFFERENCE | 156.63 -> 156.97 | 277 -> 278 | 1 / 0 | 0 / 0 | 2.43 -> 2.43 | 0 -> 0 (clean 0 -> 0) | home_ottoman +0.33 | clean |
| O_other | e-|h-|s-|b-|o0.4 | NO CLEAR DIFFERENCE | 156.63 -> 156.63 | 277 -> 277 | 0 / 0 | 0 / 0 | 2.43 -> 2.18 | 0 -> 0 (clean 0 -> 0) | none; boxes home_bathtile -0.25 | clean |
| ALL | e0.6|h1.3|s1.25|b1|o0.4 | PASS | 156.63 -> 159.05 | 277 -> 285 | 8 / 0 | 3 / 0 | 2.43 -> 2.18 | 0 -> 0 (clean 0 -> 0) | home_bathtile +0.75; home_ottoman +1.67; boxes home_bathtile -0.25 | clean |

