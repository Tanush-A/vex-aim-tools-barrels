# Verdict: the verify step (occl_strict), round 1

Rule: `experiments/2026-11-24_occl_strict/PREREG.md` (committed 0f28971 before the detector change). Data: `origin/barrels`
b72ed6f (glass x5 lights, bathroom tile x4, the glass occlusion set). Train frames only; no test frame opened. One round;
no addendum. **Both checks pass every clause and are on by default on `wip/occl-strict`.**

| clause | `verify_front` | `verify_readings` | `strict` (both, the default) | where |
|---|---|---|---|---|
| 1. `report.py --gate --cand-det ...` | – | – | **PASS** (defaults: FAIL on two glass empty frames) | `report.py --gate` |
| 2. no real barrel lost, ordinary sets | 0 lost | 0 lost | **0 lost** (hits 237 -> 237) | `diff_strict.md` |
| 3. false boxes on real frames down | -2 | -3 | **v2 false 20 -> 15; boxes on no barrel 6 -> 2; wrong color 4 -> 3** | `round1/report_strict_vs_start.txt` |
| 4. scorecard: no-barrel boxes not up; found within 15 | 48 -> 32; 2876 -> 2869 | 48 -> 34; 2876 -> 2876 | **48 -> 23; 2876 -> 2869** | `round1/scorecard.md` |
| 5. damage levels: false not up | – | – | **not up anywhere** (medium 4 -> 3, worst seen 4 -> 3, 20 seeds) | `round1/levels.md` |
| 6. recordings by eye | – | – | **0 appear; 9 disappear, all wrong boxes** | `round1/by_eye.md` |

Every box removed on a real train frame (all sets):

| frame | box | what it was | removed by | fact |
|---|---|---|---|---|
| ABP white `occlx_17` | orange (161, 105, 196, 143) | no barrel: the far blue barrel's upper body read as a stripe | `verify_front` | F5 |
| gray `clutter_01` | blue (512, 113, 556, 168) | wrong color, on the orange barrel's upper half | `verify_front` | F5 |
| glass `lampmid3_glass_neg_02` (empty frame) | orange (556, 118, 606, 172) | the tin's blue label read as a stripe | `verify_readings` | F2 |
| glass `lampmid6_glass_occl_02` | orange (559, 119, 610, 174) | the same tin | `verify_readings` | F2 |
| glass `window_glass_occlx_16` (empty frame) | blue (395, 107, 431, 146) | blue tin under an orange sticky note | `verify_readings` | F2 |

The 7 scorecard scenes lost (all HOME / CAMPUS color-model pools, barrel in front: other color front 50 % and 75 %,
beside 75 %; same color front 25 % x2, beside-and-lower 75 % x2): in each the box that had "found" the hidden barrel was
read from the front barrel's picture (0 to 16 own pixels; `look_r1.png`). The barrel is there; the reading was not of it.
Damage levels: -3 found at medium and -2 at worst seen (report-only levels), same kind; 1 found more at worst seen
(`post_pair` reaches a barrel once a wrong box is gone).

Remaining false boxes on real frames (not caught; no listed fact separates them in the class mask): the wood grain of
palewood `core_01` (stripeless close-up: speckle, not a solid face), glass `lampmid3_glass_occl_02` (the tin, top inferred
but its bottom seen where the stripe row puts it); misplaced boxes on real barrels (ottoman `lampwarm6` core_01, Dave's
close-ups, the glass `clutter_01` tin boxes beside a real barrel), the extreme wood and black sets.

Risk stated: `verify_front` trusts the nearer boxes it keeps. With the defaults no nearer wrong box removed a right farther
one on any bed; with `edge_check` off (a test arm) it does (`tests/test_detector_occl.py` pins the verify step off there).
