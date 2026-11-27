# The sanity checks of the standard pass rule (2026-11-26, git 63c145d)

`python barrels/experiments/2026-11-26_judge/run.py` (plan: `../../experiments/2026-11-26_judge/PREREG.md`; the rule: `docs/EVAL.md`, "The standard pass rule"). Train frames only; test frames never opened. Baseline everywhere: today's default. Margins: margins.json, made 2026-11-26 at git f20ad1c.

**One judge run** (two detectors on the 231 ordinary and extreme train frames, one process): **27 s**.

| candidate | found, placements | found, per frame | found either way | boxes not on their barrel (per frame) | on empty frames: clean / with clutter | verdict | with the margins as first registered |
|---|---|---|---|---|---|---|---|
| S1 today against itself | 133.8 → 133.8 (+0.0) | 211 → 211 | 135.0 → 135.0 | 1.9 → 1.9 (5 → 5) | 0 → 0 / 0.0 → 0.0 | **NO CLEAR DIFFERENCE** | NO CLEAR DIFFERENCE |
| hand thresholds | 133.8 → 156.8 (+23.0) | 211 → 281 | 135.0 → 158.8 | 1.9 → 1.5 (5 → 3) | 0 → 0 / 0.0 → 0.5 | **PASS** | PASS |
| orange_h_lo-1 | 133.8 → 137.8 (+4.0) | 211 → 215 | 135.0 → 139.0 | 1.9 → 1.9 (5 → 5) | 0 → 0 / 0.0 → 0.0 | **NO CLEAR DIFFERENCE** | NO CLEAR DIFFERENCE |
| orange_h_lo+1 | 133.8 → 127.6 (-6.2) | 211 → 204 | 135.0 → 131.0 | 1.9 → 1.7 (5 → 4) | 0 → 0 / 0.0 → 0.0 | **NO CLEAR DIFFERENCE** | NO CLEAR DIFFERENCE |
| blue follows the light, C2 | 133.8 → 139.7 (+5.9) | 211 → 233 | 135.0 → 141.2 | 1.9 → 3.1 (5 → 10) | 0 → 0 / 0.0 → 0.2 | **PASS** | NO CLEAR DIFFERENCE |
| blue follows the light, C2b | 133.8 → 137.0 (+3.2) | 211 → 222 | 135.0 → 139.4 | 1.9 → 2.9 (5 → 9) | 0 → 0 / 0.0 → 0.2 | **NO CLEAR DIFFERENCE** | NO CLEAR DIFFERENCE |

## S1. Today's detector against itself: as required

NO CLEAR DIFFERENCE; 0 barrels changed, 0 frames with other boxes.

## S2. The changes that mean nothing: as required

- Set A (14, one number moved one step): 14 of 14 NO CLEAR DIFFERENCE. Set B (12, several numbers at once): 12 of 12. Both sets are inside the margins by construction, so this checks the tool, not the margins.
- Set C (12 joint moves the margins have never seen): 10 of 12 NO CLEAR DIFFERENCE; called: check01: PASS, check08: FAIL.
- Through the whole tool (frames, counting, verdict): orange_h_lo-1 NO CLEAR DIFFERENCE with found +4.00 (the noise run recorded NO CLEAR DIFFERENCE, +4.00); orange_h_lo+1 NO CLEAR DIFFERENCE with found -6.20 (the noise run recorded NO CLEAR DIFFERENCE, -6.20).

## S3. Tanush's hand thresholds: PASS (as required)

Per condition, the median of its slider labels; in-sample by nature. Per frame: found 211 → 281 of 307 (the review counted 211 → 281). With the margins as first registered: PASS.

- [BETTER] found, the ordinary conditions together: 133.8 -> 156.8 of 172 placements (+23.0; counted per frame 211 -> 281 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: abp_gray +5.0 of 16 (margin 6.0); home_bathtile +8.5 of 15 (margin 1.2); home_glass +0.2 of 15 (margin 1.0); home_ottoman +10.3 of 15 (margin 2.3); uc_palewood -1.0 of 15 (margin 1.0).
- [within the noise] boxes that are not on their barrel: 1.9 -> 1.5 counted once per arrangement (-0.4; per frame: on nothing 5 -> 2, second box 0 -> 0, wrong color 0 -> 1). Worse above +1.9, better below -1.0.
- [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.5 per arrangement (margin 1.0).
- Verdict: **PASS**. found is up by more than the noise, and nothing is worse by more than the noise.
- At the margin (within one whole unit of it): boxes on empty frames with clutter: +0.50 against a margin of 1.00; found at uc_palewood: -1.00 against a margin of 1.00.
- Barrels, per frame: 71 gained, 1 lost. Every one of them, the tables and the boxes: `hand_thresholds/judge.md`.

## S4. blue follows the light, C2, leave one place out: PASS (with the margins as first registered: NO CLEAR DIFFERENCE)

The setting picked in each fold (on the other places, by the 2026-11-25 rule): home_white: w0 0.08, w1 0.2, blue S -> 40, hue low -> 92; campus_study: w0 0.08, w1 0.2, blue S -> 40, hue low -> 92; abp_gray: w0 0.08, w1 0.2, blue S -> 40, hue low -> 92; home_bathtile: w0 0.06, w1 0.2, blue S -> 30, hue low -> 98; home_glass: w0 0.06, w1 0.2, blue S -> 40, hue low -> 92; home_ottoman: w0 0.08, w1 0.2, blue S -> 40, hue low -> 92; uc_palewood: w0 0.08, w1 0.2, blue S -> 40, hue low -> 92; abp_white: w0 0.08, w1 0.2, blue S -> 40, hue low -> 92; home_wooddesk: w0 0.08, w1 0.2, blue S -> 40, hue low -> 92; home_black: w0 0.08, w1 0.2, blue S -> 40, hue low -> 92.

- [BETTER] found, the ordinary conditions together: 133.8 -> 139.7 of 172 placements (+5.9; counted per frame 211 -> 233 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: home_bathtile +4.2 of 15 (margin 1.2); home_ottoman +1.7 of 15 (margin 2.3).
- [within the noise] boxes that are not on their barrel: 1.9 -> 3.1 counted once per arrangement (+1.2; per frame: on nothing 5 -> 6, second box 0 -> 2, wrong color 0 -> 2). Worse above +1.9, better below -1.0.
- [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.2 per arrangement (margin 1.0).
- Verdict: **PASS**. found is up by more than the noise, and nothing is worse by more than the noise.
- At the margin (within one whole unit of it): boxes not on their barrel: +1.20 against a margin of 1.85; boxes on empty frames with clutter: +0.20 against a margin of 1.00.
- Barrels, per frame: 22 gained, 0 lost. Every one of them, the tables and the boxes: `blue_follows_the_light_c2/judge.md`.

## S4. blue follows the light, C2b, leave one place out: NO CLEAR DIFFERENCE (with the margins as first registered: NO CLEAR DIFFERENCE)

The setting picked in each fold (on the other places, by the 2026-11-25 rule): home_white: w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); campus_study: w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); abp_gray: w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); home_bathtile: w0 0.06, w1 0.3, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); home_glass: w0 0.06, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); home_ottoman: w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); uc_palewood: w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); abp_white: w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); home_wooddesk: w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %); home_black: w0 0.1, w1 0.2, blue S -> 40, hue low -> 92 (light read from rows < 50, brightest 20 %).

- [within the noise] found, the ordinary conditions together: 133.8 -> 137.0 of 172 placements (+3.2; counted per frame 211 -> 222 of 307). Better above +4.0, worse below -10.9.
- [within the noise] found, place by place: home_bathtile +1.5 of 15 (margin 1.2); home_ottoman +1.7 of 15 (margin 2.3).
- [within the noise] boxes that are not on their barrel: 1.9 -> 2.9 counted once per arrangement (+0.9; per frame: on nothing 5 -> 6, second box 0 -> 1, wrong color 0 -> 2). Worse above +1.9, better below -1.0.
- [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.2 per arrangement (margin 1.0).
- Verdict: **NO CLEAR DIFFERENCE**. no count moved by more than a change that means nothing moves it.
- At the margin (within one whole unit of it): found over all places: +3.17 against a margin of 4.00; boxes not on their barrel: +0.95 against a margin of 1.85; boxes on empty frames with clutter: +0.20 against a margin of 1.00.
- Barrels, per frame: 11 gained, 0 lost. Every one of them, the tables and the boxes: `blue_follows_the_light_c2b/judge.md`.

Files: `chosen.json` (the hand thresholds per condition, the setting each fold picked), one folder per candidate.
