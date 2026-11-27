# TODO.md — the plan for the week (meeting with Dave: Monday 2026-11-23)

**Updated:** 2026-11-26 (reviewer session: the re-plan after the review, "Now" below) · 2026-11-23 (data session: 15 conditions in, boxed and slider-labelled) · 2026-11-21 (data session: the occlusion set shot, 18 of 19, `occlx_16` open) · 2026-11-20, later (data session: condition 6 in, kicker check passed, clutter-last shoot order) · 2026-11-20, later (data session: condition 5 in, close-up check passed) · 2026-11-20 (data session: the state of the shoot under "Tanush" and in "Done this week") · 2026-11-18 (evening). Re-planned with Tanush after the 2026-11-16 meeting with Dave. Rule (`CLAUDE.md`): updated whenever a task starts, finishes or changes priority, together with `STATUS.md`.

## Next shoot (agreed with Tanush 2026-11-27, from his phone)

**One place: the gray wood table (low gloss) under a warm lamp.** The window-light shoot on the black table is skipped: black-table glare is a parked extreme case. Why: it is the first place none of our methods were shaped on, so it is the fair test of "stripe by contrast against the vendor" (`REPORT-2026-11-27.md`, "Are we beating the vendor?").

- The 9-shot list below ("Shot list: 9 shots per condition"), **clutter last**, with **the tin and the jar** among the clutter (the shape-check traps).
- **Vendor files on every frame**; without them the comparison cannot be made.
- If this is the same glossy gray table already in the data (ABP, condition 6), say so: the lamp is new but the surface is not, and the reading changes.
- After the shoot, Claude boxes the frames (Claude proposes, Tanush reviews), makes the train / test split before running anything, and scores today's detector, contrast and the vendor on the train part.

## Now: the re-plan after the review (2026-11-26)

Agreed with Tanush in the reviewer session on 2026-11-26, from the review of the detector's logic and the final report (`REPORT-2026-11-25.md`). **Order (Tanush, 2026-11-26, later: he is away, no step waits for a go):** merge `wip/final` (done 2026-11-26, tests 930 pass, never-regress check passes, pushed); then U1, the detector map, with recommendations for restructuring; then M, the measurement; then K, the collapse; then C, the experiments: every idea listed is tried, **each on its own branch** so he can see it. Every step has its checks written down. The reviewer session is the only one editing code for now; the main session is paused. At the end: `docs/OVERNIGHT-2026-11-26.md`. The plan of the week of 2026-11-18 is kept below as the record.

**Decisions from Tanush, 2026-11-26** (to be logged in `DECISIONS.md` by the main session):

- **Labeling:** from now on Claude proposes every box and every threshold label, Tanush reviews briefly and adjusts. Claude may change the labeling tools and asks for a short review. Proposals come from looking at the picture, never from the detector.
- **Never-regress is loosened.** It was meant as a general principle, not a strict rule. The size of the allowed margin is M2.
- **The vendor counts as 100 % on a white table under window or overhead light.** An assumption, not a measurement; every table that uses it says so.
- **The verify step: "understood" on both checks (2026-11-26).** `wip/final` merged into `barrels` 2026-11-26.
- **The tall box around a same-colored barrel straight behind (D4) is accepted** as an edge case; no work.
- **Pass rules are loosened** to above the noise (M3).
- **A calibration step is fine for data collection only** (a shot with known barrels that tells us the light of a place), not as a step of the robot's run.
- **The bottom-edge mismatch (D1) gets fixed** (K2). **A barrel 60 % hidden at the side should still be found** when its stripe, bulge and top or bottom edge show (E7).
- **More data later:** Tanush shoots one or two more places after this block of work.

### Next (2026-11-27)

| # | what | state |
|---|---|---|
| **N1** | Adopt stripe by contrast as the default (Tanush: go) | running on `wip/adopt-contrast` |
| **N2** | One planned look at the test frames with contrast (Tanush asked) | after N1, same branch |
| **N3** | Shoot a new warm-light place (pale table or floor, not the bathroom; clutter last, with the tin and the jar) | Tanush |
| **N4** | **Doc cleanup:** `STATUS.md`, `HOW-IT-WORKS*.md`, `ARCHITECTURE.md`, `CLAUDE.md` "current facts", `HANDOFF.md`, `EVAL.md` still describe the detector before the collapse in places; move the November history to `archive/`; one "Now" block per doc | open |
| **N5** | Occlusion by non-barrel things, from real frames (what is left after contrast is mostly hidden barrels) | after N1 |
| **N6** | A photo-based check for near-barrel traps (the mask cannot tell a printed label from a barrel) | open |

### U. Understand what runs today (first; no code)

| # | what | state |
|---|---|---|
| **U1** | **The detector map.** One flow chart of what `detect` does today, in order: the nine stages, every check inside each, what the check is for in one line, the real frame that motivated it, and how many real train boxes it changes. Answers "stripes first, body first, geometry first or occlusion first" on one page. A doc plus a walkthrough in chat. | **done 2026-11-26:** `DETECTOR-MAP.md` (the detector as it was before the collapse; 760 lines, every statement checked against the code). Stripes first; geometry is the ruler inside every check, not a stage; occlusion is one branch of the stripe step plus three add-on stages. The top level (nine stages) is sound; the mess is inside stages 2 and 3. The walkthrough with Tanush is still open |
| **U2** | **Mark every check on the map:** carries real weight / changes nothing on real frames / justified by simulated scenes only / works by accident. Ends in a proposed collapse list; Tanush decides what goes. | **done 2026-11-26** (section 5 of the map). Of 30 switches: 17 keep real barrels, 6 are sound but no real frame shows their case (they stay, by Tanush's rule), 7 are off (dead paths, they go); none is redundant. Of 20 numbers: `height_max` works by accident, `min_stripe_px` is redundant and works by accident, `stripe_merge` is unclear |
| **D1** | **"More paint, box disappears", explained on real frames.** Known so far: the box is still drawn; extra paint under the barrel moves its bottom edge; the detector accepts a seen bottom within 15 % of the height, the score allows 10 %, so the box is counted as a miss plus a false box. Show three frames, then say what to change. | open |
| **D2** | **Why a straight edge hiding half scores 90 of 100 in the simulated scenes and 0 of 2 on real frames** (`occlx_02`, `occlx_03`, a black box). | **diagnosed 2026-11-26, nothing changed.** The two real barrels are about 60 % hidden, not half (19 of 51 and 22 of 53 px showing). The detector has a cliff between the two: simulated on the same tables, 96 of 104 found at half hidden and 64 of 104 at 60 %. A third of the boxes at half hidden (34 of 99) are a guess centred on the visible half, a quarter width off, which passes the overlap rule only at that amount; at 60 % the stripe is under 0.4 of the width and no guess is drawn. Real extras the scenes lack: the stripe ends 5–6 px before the cut, and the cut leans. Two real frames are too few to say more. For K: one rule for a side-cut barrel, without the cliff |
| **D3** | **The 25 barrels the hand thresholds still miss** (218 of 243): which are the detector's, which could no threshold paint, which had no hand label. First split: 6 on the ABP white table (no hand labels there; real occlusion), about 9 under the warm bathroom lamp (the slider could not reach the blue then), about 10 others. | open |
| **D4** | **A same-colored barrel straight behind another** (`occlx_10`): one tall box around both, and the back barrel is never proposed. | **diagnosed 2026-11-26, nothing changed.** Every size check passes: the back barrel's top is 9 px above where the front barrel's top should be, and a seen top is accepted within 15 % of the height (10 px here); the box is 71 px wide against an allowed 75. The tolerance is that wide because the camera tilt differs between places. The back barrel shows no stripe, so nothing else proposes it, and once its top is taken as the front barrel's top no "barrel behind" piece is left. The mask does show it: the upper part is narrower and shifted 6 px to the left. For C: an idea for the list (the outline steps sideways where two barrels overlap) |

### M. Fix the measurement (before any new experiment is judged)

| # | what | state |
|---|---|---|
| **M1** | **Count placements and places, not lamp settings.** The 243 train barrels are 108 placements at 6 places. A box on a real barrel with a bad bottom edge counts once, not as a miss plus a false box. Vendor on the white table: assumed 100 % (decision above). Eval = main code: walkthrough first. | **done 2026-11-26, merged.** `python barrels/tools/report.py --places` (and with `--vendor`). Per placement: ours 70.8, vendor 83.3 of 108 on the six measured places; the vendor's 30 "false boxes" are 23 on a barrel that fail the strict rule and 7 on nothing (ours 2 and 5). Walkthrough owed |
| **M2** | **The never-regress check with a margin** (decision above). Propose the margin from how much the score moves under a change that means nothing (one hue unit). | **done 2026-11-26, merged.** A change that means nothing moves found by up to 10.92 placements down and 4.00 up. The check judges each protected set on its total with a margin of 1 placement and 1 box (cool-lamp bathroom: 5); a box on a clean empty frame still fails. Protected: home, campus, glass, pale wood, ABP white, cool-lamp bathroom. Passes on today's defaults |
| **M3** | **Pass rules above the noise.** One barrel is about 0.03 of a condition's score; a rule tighter than that rejects everything. Write the standard pass rule once and reuse it. | **done 2026-11-26, merged.** `python barrels/tools/judge.py`: PASS / FAIL / NO CLEAR DIFFERENCE (`EVAL.md`, "The standard pass rule"). A gain counts above +4.0 placements; a PASS under +6 is called weak. Hand thresholds: PASS (+23.0). The light rule: PASS, weak (+5.9) |

### K. Collapse the detector (after U1, U2 and M)

Rule for what goes (Tanush, 2026-11-26): a check that is logically sound stays, even when no frame of ours shows its case; what is redundant or can be folded into another check is collapsed.

| # | what | state |
|---|---|---|
| **K1** | Remove the rules that are switched off and the code only they use; make the rules that are on plain code (no switch); fold the duplicates; name the stages in the code as on the map. Check: the boxes on every train frame and on every simulated scene are the same before and after, box for box. Then the map is rewritten for the collapsed detector. | **done 2026-11-26, merged.** 51 settings became 20 numbers with no switch; `detect` is ten named stages; boxes identical on 5435 masks after each of nine steps (checked twice, once independently); tests 952 pass; the never-regress check passes. The new map is `DETECTOR-MAP.md` (the old one is in `archive/`). The state before is the tag `pre-collapse-2026-11-26`. Left over: 15 changes that would change boxes (map, section 6), each an experiment. Walkthrough owed |
| **K2** | **The bottom edge** (D1): the detector and the score agree on how far a seen bottom may be from the predicted one. Changes boxes, so it is judged with the rule from M3. | **done 2026-11-27** (`wip/exp-bottom`): recommended `bottom_rule=low_uncut`; no clear difference with the fixed colors, and with looser colors it removes about a third of the bottom-edge failures (35 → 24). Worth adopting together with a color change, not alone |
| **K3** | **Second pass of the collapse:** remove what the first pass proved can never decide (the "too far for a stripe" half of the close-up rule, the height check that the horizon check made idle). Same rule: boxes identical. | **done 2026-11-27, merged.** 20 → 18 numbers (`height_max`, `min_stripe_px` gone, each with a test that states the fact it relied on); boxes identical on 5435 masks (checked twice); 955 tests. Declined, as not provably identical: B7 (3 of 43 boxes would differ) and five checks kept on purpose (map, section 6) |

### C. Experiments (each written first, on its own branch `wip/exp-…`, train frames only, judged by place with the rule from M3)

| # | what | state |
|---|---|---|
| **C1** | **Relabel the warm and dim bathroom frames with the wider blue slider** (blue reads hue 26–44 there; the old labels stopped at 60), Claude proposes, Tanush reviews. Re-run the hand-threshold ceiling. Shows whether those hues paint the barrels or the floor. | **done 2026-11-26** (`wip/exp-place-ceiling`). It was a slider limit: blue at hue 26–44 paints the barrels, not the floor; warm bathroom 14 of 15 found (old labels 6, vendor 0). 12 threshold proposals wait for Tanush's review (`data/labels/*_hs_proposed.json` on that branch; see them with `hs_slider.py --render-grid --try saved --try claude`). The best ranges per condition reach 163.2 of 172 placements; the 13 left are hidden or frame-cut barrels |
| **C2** | **Near-miss colors count next to strong evidence** (Tanush's idea). Strict colors start a barrel; a pixel just outside the range counts only where the partner color should be: the stripe band inside a strong body, the body around a strong stripe. Loosening everywhere floods (false boxes 7 → 80); this loosens only beside a barrel. | **done 2026-11-26** (`wip/exp-nearmiss`): **PASS** leave one place out, 133.8 → 147.5 of 172 placements, 38 barrels gained, none lost; boxes off a barrel 1.9 → 3.6 (close to the margin; 3 of the 7 new ones on a jar's label). Plain two-level thresholds fail; the partner condition and never painting past the predicted top and bottom are what make it work. Not adopted: waits for Tanush |
| **C3** | **"Blue follows the light", one fresh try** under the rule from M3 (round 1: 22 barrels gained, none lost, rejected for one box). | **done 2026-11-26** (`wip/exp-light`): the blue ramp gains 14 barrels and loses none, +3.9 placements against a margin of 4.0: NO CLEAR DIFFERENCE. "Bluer than the light" finds the bathroom barrels (14 of 15 placements) but FAILS on 16 boxes on clutter. The setting does not transfer between the only two warm places. Best reading of the light: the brightest pixels that are not barrel-colored. Question for Dave: is comparing a pixel with the light's color image correction? |
| **C4** | **The stripe by contrast, then the barrel's own colors.** A band that is bluer (or oranger) than what is above and below it by a margin, at the size its row predicts; then read that barrel's two colors and grow the body. | **done 2026-11-27** (`wip/exp-contrast`): **PASS** leave one place out, 133.8 → 155.3 of 172 placements (+21.5), 64 gained, none lost, no box on an empty frame. The strongest single result. Caution: guard numbers read in-sample; only two warm places |
| **C6** | **Use more of the photo** (Tanush: keep on the list): how close a pixel came to passing instead of yes or no; the barrel's outline against the table; what is at the unpainted places, table or an object in front. | open |
| **C7** | **Calibration per place:** at the start of a session one orange and one blue barrel stand at a known spot in front of the robot; the program reads their colors there and sets the ranges for that room. Hand thresholds per condition already do this by hand (218 of 243 against 148). Needs Dave's word, since it adds a setup step. | **measured 2026-11-26** (`wip/exp-place-ceiling`): one calibration frame per condition, as registered, FAILS (+8.0 placements but campus 35 → 21: ranges from one frame are too narrow). Keeping the fixed colors when they already find every barrel on the calibration frame reaches the hand level (156.6) but was thought of after the failure: a hypothesis for the next places. A calibration shot should hold free-standing barrels of both colors, near to far, with the usual clutter in view |
| **C5** | **Adaptive thresholds from room statistics: no further round** until the input is measured on the barrel (C4 gives that) and there are more places. Aiming at any value inside the working range was tried twice (range rule 2026-11-24: 112 found against the fixed 121; relation on ranges 2026-11-25: a different chance winner per threshold). | parked |

| **E6** | **What to read the light or the colors from** (Tanush asked for ideas): a barrel already found with the strict colors, used to set the colors for the rest of the frame; the light read from pixels with almost no color (white and gray things) instead of the brightest ones; one frame of a place setting the ranges for the other frames of that place (what a calibration shot during data collection would give). | **done 2026-11-26.** A found or half-found barrel sets the colors (`wip/exp-selfcal`): **PASS** leave one place out, 133.8 → 147.6 of 172, 37 gained, none lost, no box on an empty frame. Light from colorless pixels fails (under a yellow lamp those are the blue barrels); light from the brightest non-barrel pixels is best (`wip/exp-light`). One frame setting a place: see C7 |
| **E7** | **A barrel 60 % hidden at the side:** one rule that uses the stripe, the bulge of the seen side and the seen top or bottom edge; no cliff between half and 60 % (D2). | **done 2026-11-27, not recommended** (`wip/exp-sidecut`): the bulge rule removes the cliff in simulation (60 % hidden: 151 → 269 of 312) and finds both real straight-edge barrels, but on real frames it adds a box on a tin's label and places a shaded barrel on the wrong side; real sides bulge half of what the model predicts. A second round would require the cut side to be straight over its whole height, and needs more real side cuts (shot request) |
| **E9** | **Slack in the stripe tests:** one marginal test can be made up by the others; floors that scale with the barrel. Yardstick: one pixel shaved off every painted region loses 12 of 63 barrels on the white tables. | **ready to merge, waits for Tanush's "understood"** (branch `wip/adopt-slack`, rule D as plain code). Ordinary train frames: 211 → 214 found, 0 lost, no new false box; gate passes; one old test rewritten on purpose (`test_seam_height_is_asked_of_a_short_piece_only_when_the_rest_of_the_barrel_agrees`). On merge: re-measure the noise margins (they tighten slightly) |
| **E8** | **The winners together**, judged once more as one candidate. | **done 2026-11-27** (`wip/exp-combined`): contrast alone does the work (155.3 of 172 held out); the others add nothing above the noise. Against the vendor on the six measured places: 92.3 against 83.3 of 108 (train). Left: hidden and frame-cut barrels. **Next: adopt contrast (walkthrough first), then test on a new warm-lit place** |

### Data and Dave

- **Shooting (Tanush: one or two more places):** most useful is a new surface under warm light, since only two places have it and the light rule (C3) is judged there. A new place counts, a new lamp setting on the same table does not. Three frames at a new place (`core_01`, `clutter_01`, `neg_01`) beat a full nine at an old one. The parked sets (black table, wood, Dave's office) count as places for analysis. No generated images for color work.
- **Shot request:** the home white table with vendor files (9 shots; three times each also gives a shot-to-shot noise floor), so the ASSUMED vendor rows become measured. The one white table with vendor files (ABP) has the vendor at 24 of 32.
- **White balance (2026-11-27, `wip/exp-whitebalance`, numbers for Dave only):** gray world at half strength passes (+9.2 placements, 6 ottoman barrels lost, fewer boxes off a barrel), but 34 of its 38 gains are found by stripe by contrast without touching a pixel. The rule against correction costs about 4 barrels here.
- **Ask Dave:** can the camera's exposure and white balance be locked; is a calibration per place allowed (show the robot one barrel at the start of a session); does learning a barrel's colors from a barrel already found count as image correction.
- **From the final report, still open:** merge of `wip/final` (waits on D4 and "understood"); protecting the new conditions (now M1 and M2); the orange conflict (now C2 and C4); the light rule (now C3).

---

# The plan of the week of 2026-11-18 (the record)

## The goal

A detector at least as good as the vendor's in the vendor's own conditions, and working in more ordinary conditions than the one we had (white table, normal light). Any win beyond that is a bonus.

- **Occlusion gets fixed.**
- **If the segmentation is good, the detector finds the barrel.** A measured test (`experiments/2026-11-18_det_given_seg`), not an assumption.
- **Never regress:** no scenario row of the eval table (`tools/report.py`) on home or campus may drop. A fix for one case that breaks another (close-ups, say) does not merge.
- **Ordinary conditions only.** Parked as extreme: the orange wood table under a lamp, glare on the black table, lamp brightness 1. They stay in the eval table as report-only rows.
- **Adaptive thresholds from evidence:** Tanush sets the best hue and saturation thresholds by hand per frame; if something in the frame's histogram predicts his settings, that relation becomes the adaptive rule.

## Where the detector stands (train frames, 2026-11-18)

| test | found |
|---|---|
| eval table, home | 28 of 29, no false box (was 25) |
| eval table, campus | 35 of 35 |
| perfect home masks in | 28 of 29 |
| lightly / medium / heavily damaged masks in | 141 / 64 / 13 of 145 |
| black table, thresholds read from the labels (extreme) | 19 of 26 |

Still missed on the white tables: one barrel in home `cluster_01` that shows only a wedge of its top between two barrels. Occlusion scorecard (simulated, 3888 scenes): 2737 found, half hidden 1160 of 1296, three quarters hidden 311 of 1298.

## Claude, now (none of this needs new data)

| # | what | state |
|---|---|---|
| **A2** | **Side occlusion.** A barrel half hidden at the side by something that is not a barrel (campus `occl_02`, the live miss with Dave). The old fix (`stripe_w_min` 0.25 + `occl_body_side`) draws boxes half off the barrel because it takes the barrel's own body for the thing hiding it. New rule to try: a side counts as hidden only where a found barrel or the frame edge is, or where the body color visibly stops. Detector = main code: `wip/` branch, pre-registered, walkthrough. | **built 2026-11-18 on `wip/detector-side`, waits for Tanush's "understood".** `side_hidden`: a side counts as hidden only for a reason (frame edge, a found nearer barrel, body and stripe ending apart). Campus 34 → 35 of 35, home unchanged, no row worse; medium damage 64 → 99 of 145 with false boxes 22 → 1 |
| **A3** | **The misses left when the segmentation is good.** The wedge barrel in `cluster_01` (box it or accept it, with the reason); stripes eaten at far range; a highlight across a stripe (medium damage: 64 of 145). Same branch and rule as A2. | **done with A2.** The wedge barrel in `cluster_01`: no box on purpose (nothing to size it from). The second `cluster_01` miss is the bottom predicted 10 px low from the top row (calibration). `seam_height` for thin far stripes: passes, changes no real frame |
| **A4** | **Bottom edges 4 to 7 px low for far barrels: calibrate from the ruler frames.** The 12 `calib` frames and `data/calib.csv` exist; no new shots. New camera constants only if home and campus do not regress; then the `g` size guide in the box tool is right as well. Geometry = main code: `wip/` branch, walkthrough. | **done 2026-11-18 on `wip/calibration`, nothing adopted.** The ruler frames fit only with a lower camera (height 40.2 mm, tilt 20.4°), and that camera fails on home and campus; a second one (tilt 20.95°) gets sizes and bottoms right within a pixel but loses one hidden barrel in home `occl_01`. Each session wants a tilt about 0.3° from the others. Finding to act on: a bottom inferred from the box width is right to 1–2 px with any camera (from the top row: 4–7 px). Next: A5 |
| **A6** | **Occlusion pass with a scorecard** (`wip/detector-occl`, on top of A2 and A5; built 2026-11-19, waits on Tanush). 3888 simulated scenes: a barrel hidden 25 / 50 / 75 % by 15 kinds of thing. Today: fine to half hidden from the side, about 0 at three quarters. Two small parts pass and are on (`edge_check`, `cap_same`). The big part (`slice_box`, `cover_unpinned`, `stripe_two`: draw the full-size box covering every place the barrel can be) lifts three quarters hidden to 73–90 of 100 and medium damage 99 → 124 of 145, home and campus unchanged, but draws 4 wrong boxes instead of 1 on damaged, unhidden barrels: fails the written rule on that clause, so it is OFF pending Tanush's decision. Not handled by anything: hidden from above or below by half or more; a same-colored barrel straight in front. | **2026-11-19, Tanush: the full-size-box part stays OFF; keep iterating on new methods, as many cases as possible, no false positives.** Research running in the background (A7) |
| **A7** | **Occlusion research, four directions in parallel**, all scored on the same scorecard with false boxes as the hard limit: (1) pin the sideways position of a cut barrel (the top edge's highest point, the lid) so the full-size box can be tight and safe; (2) hidden from above or below, and a same-colored barrel in front; (3) a different detector idea as a second opinion: slide a barrel-shaped stencil of the right size for each row and keep where the painted pixels match; (4) how damaged real segmentation actually is, to set the damaged-mask test to realistic levels. | **merged 2026-11-20 (Tanush: "understood"); never-regress check passed; baseline re-saved.** Scorecard 2153 (`barrels`) → 2737 of 3888; half hidden 771 → 1160 of 1296, three quarters 150 → 311 of 1298; boxes where no barrel is 88 → 45; home 28 of 29, campus 35 of 35, nothing on a negative frame; no false box added at realistic damage. Off: `slice_behind` (7 false against 3 at the old medium level over 20 seeds), the cover box (Tanush), the stencil as a checker (loses 2 campus barrels). The old "medium damage" level is far harsher than real white-table segmentation; the only real damage that costs anything is a stripe cut through. Cannot be done from the painted pixels: three quarters hidden by a non-barrel thing (it looks like bare table). All occlusion numbers are simulated: shot requests R1, R3, R4, R5 in `DATA.md` |
| **A8** | **Two guarantees Tanush asked for (2026-11-20), on top of `wip/occl-combined`:** (1) a stripe cut through by a highlight is filled in when the pieces on the same rows clearly belong to one stripe; (2) whenever any piece of stripe with body is visible, even a sliver at three quarters hidden from the side, the barrel gets a well-placed box. No false positives added. | **merged 2026-11-23** (Tanush: follow the recommendation): `thin_span`, `stripe_bridge` and `thin_frame` on, `own_close` off; gate passes, baseline re-saved. As built: `thin_span` (a thin stripe piece whose body shows the whole width gets that width: stripe-colored block hiding 75 % 3 → 77 of 100, no false box anywhere; scorecard 2737 → 2811). Off, each failing one clause by a few boxes: `stripe_bridge` (fills a cut stripe: bad day 547 found / 5 false → 563 / 0, but scorecard wrong boxes 45 → 48 and medium 3 → 4), `thin_frame` (frame edge at 75 %: 29 → 88; boxes 2–3 px too wide against frame-clipped labels), `own_close` (straight edge at 75 % 28 → 57, slanted 0 → 62; fooled when a barrel stands in front) |
| **A9** | **False box on the striped-clutter trap (occlusion set shot 15).** A printed orange fruit on a snack bag, cut by the frame bottom, gets an orange box: the old step-1 rule "a barrel-colored piece reaching the frame bottom is a close barrel whose stripe is below the frame" (`det1`), there since 2026-11-03, not the occlusion work. The never-regress check now fails on it (a box on an empty frame) and will keep failing until it is fixed. Lead: a close barrel at the frame bottom is barrel-shaped (rounded top corners, near-vertical sides, width for its row); a flat printed shape is not. | **merged 2026-11-24 (Tanush: understood)** (`closeup_side`, `closeup_stripe`; `OVERNIGHT-2026-11-24.md` §4.1) |
| **V** | **Ours against the vendor, per condition** (merged 2026-11-24): ours 59 of 123, vendor 99 of 123 on the 7 new conditions; the gap is the color step on the ottoman and gray table. `python barrels/experiments/2026-11-24_vendor/run.py`; all checks together: `python barrels/experiments/run_all.py` | merged |
| **F2** | **Adaptive thresholds** (`wip/tomorrow`, off by default): no relation holds when a whole place is held out (3 labelled places); the pre-registered rule fails tonight; frozen copy tested on tomorrow's places | re-run 2026-11-24 |
| **A5** | **Infer hidden bottoms from the box width, not from the top row** (the A4 finding: it does not depend on the camera tilt). Should bring back the second `cluster_01` barrel and make the calibration question less urgent. Detector = main code: pre-registered, never-regress gate, walkthrough. | **done 2026-11-19 on `wip/detector-bottom`** (one rule, `cap_seen_bottom`: home 27 → 28 of 29; none of the 62 boxes on home and campus used the top-row bottom, so calibration is closed); merges with A2 and A6 |
| **H** | **Vendor column in the eval table.** Reads `data/vendor/<stem>_vendor.json`, scores the vendor's boxes by the same rule against the same labels, next to ours. Ready before the first frames arrive. Eval = main code: `wip/` branch, walkthrough. | **merged 2026-11-19 (Tanush: ok).** `python barrels/tools/report.py --vendor`; run only on made-up vendor files so far |
| **I** | **The never-regress rule as a command.** One command that compares the eval table with the stored numbers for home and campus, row by row, and fails on any drop. Run before every merge. With H. | **merged 2026-11-19 with H.** `python barrels/tools/report.py --gate` against `results/baseline/`; fails and names the row when a home or campus row drops |
| **F** | **Histogram against the hand-set thresholds.** Script merged; needs about 8 ordinary conditions. Re-run as conditions and slider labels arrive: `python barrels/experiments/2026-11-18_hs_relation/run.py`. If a relation holds: the adaptive rule, pre-registered, scored with the eval table. | waiting on data |
| **G** | **Against the vendor, and one look at the test frames** | **done 2026-11-25** (adaptive rules shown not to work in four rounds): home 9 of 9, campus 22 of 24; new conditions ours 14 of 32, vendor 23 of 32; `REPORT-2026-11-25.md` |

## Tanush

1. **Start the data session** (prompt in `HANDOFF.md`).
2. **First shoot, first two minutes: the vendor save.** `simple_cli BarrelTracker`, one orange and one blue barrel, `tm save`: the console line ends `vendor: 2 objects (OrangeBarrel, BlueBarrel)` and `robot_snapN_vendor.png` shows a tight box on each (`RUNBOOK.md`). **Done 2026-11-19: it works.**
3. **Same sitting: the close-up check.** A barrel about 2 cm from the bumper with a far barrel behind it in the picture: both get a box. A barrel seated in the kicker: if it gets no box, `tm save` it. **Close-up: passed 2026-11-20 on pale wood** (ours boxed the near and the far barrel on all three test frames; the vendor missed the near one on two). **Kicker: passed 2026-11-20 on the ABP gray table** (`4A8B_both_abpgray_held_01`: ours and the vendor both boxed it). Done.
4. **Shoot conditions**, 9 shots each (list below), as tables and lights come up. Two lights on one arrangement: same session. **State (the running table in `DATA.md`, "Conditions shot this week"): 6 conditions in. 2026-11-19: the black ottoman lid under the lamp at warm 6, mid 6, cool 6 and mid 3 (36 frames). 2026-11-20: pale wood under weak overhead light on campus (9 frames); the gray table at ABP under window + weak yellow overhead (10 frames incl. the kicker shot). Every frame has the vendor's answer; all boxed 2026-11-21 (Tanush); slider labels on the six conditions 2026-11-21. 2026-11-21: the occlusion set R1, 18 of 19, on a white table at ABP under window light (`occlx_16` open; makeshift colored clutter). 2026-11-23: the glass table (lamp warm/mid/cool 6, mid 3, window) and the bathroom floor (four lamp settings): 9 more conditions, 15 in all, boxed, slider labels on all 27; `occlx_16` shot, R1 complete. White table skipped this week (Tanush: assume the vendor perfect there).**
5. **Box every frame** (`box_tool.py`).
6. **Slider labels**, three frames per condition (`core_01`, `occl_01`, `clutter_01`): `python barrels/tools/hs_slider.py --filter <light>_<surface>`. Criterion: as much barrel painted as needed to detect it, as little else as possible. On first open, check that a slider knob follows the mouse.
7. **Tell Claude when a condition is in** (F is re-run each time).
8. **Read the walkthroughs** for A2 / A3, A4 and H when they are ready; each merges on "understood".
9. Optional, after A4: re-box the three hidden barrels whose boxes are no taller than wide (home `occl_02`, black `occl_02`, `occl_04`) with the corrected size guide.

## Shot list: 9 shots per condition, about 6 minutes

A condition = one table under one light. Aim for ten or more conditions; few scenes each.

Shoot order (Tanush, 2026-11-20): the shots without clutter first, then every shot with clutter in one run, so the clutter is set up once; `neg_02` is the clutter left after the barrels come out.

| # | name | shot |
|---|---|---|
| 1 | `neg_01` | empty table |
| 2 | `core_01` | four barrels spread out, mixed colors, near to far, nothing else |
| 3 | `touch_01` | two or three touching, mixed colors |
| 4 | `close_01` | one barrel about 2 cm from the bumper |
| 5 | `edge_01` | one barrel cut by the left or right frame edge, one fully in view |
| 6 | `occl_01` | a barrel about half hidden behind a barrel of the other color, clutter in the background |
| 7 | `occl_02` | a barrel about half hidden at the side by a clutter object |
| 8 | `clutter_01` | barrels among clutter, an orange or blue non-barrel right next to a barrel |
| 9 | `neg_02` | clutter only, including one orange and one blue thing that is not a barrel |

### Occlusion set: 16 shots, once (consolidated 2026-11-20)

The list is `DATA.md`, "Open shot requests" (R1); the data session reads it at every sitting.

Conditions to try for: white table with window light, overhead light, both, sun, dim evening light; dark wood table with overhead and with window; gray table (yellow overhead); black table with window and with overhead; anything else ordinary. A new table: tell the data session, it adds the tags.

## Later (postponed by Tanush; P1 = next after this week's plan, P2 = after that)

| pri | what | note |
|---|---|---|
| P1 | **A barrel with only its top or only its bottom showing** (hidden three quarters from above or below), and three quarters hidden on both sides | Not decidable from the painted pixels: a non-barrel thing in front looks like bare table. Needs the image itself. First see whether the vendor detector finds these on the occlusion shots (R1 in `DATA.md`); if it does, try; if not, later still |
| P1 | **Is "medium damage" realistic under the new lights?** | On the white tables it is not (real stripes whole on 37 of 38 barrels). Re-measure on the new conditions with `experiments/2026-11-19_damage_realism` once they are boxed |
| P2 | The stencil as a checker of the detector's boxes | Removes most wrong boxes (45 → 8 on the scorecard) but loses 2 real campus barrels at the limit tried; needs a better way to tell a half-hidden barrel from a wrong box |
| P2 | The full-size "cover" box and `slice_behind` | Built, off. Revisit with real occlusion frames |
| P2 | Extreme conditions: orange wood under a lamp, black-table glare, brightness 1; blue barrels from the blue body alone | parked 2026-11-18 |
| P2 | Camera: lens height (about 40 mm fits the ruler frames, 43.5 is in use), auto exposure / white balance lock | calibration closed 2026-11-19: no box on home or campus depends on it |

## Done this week

- **2026-11-18:** A, the detector given good segmentation: the test, `cap_behind` (a barrel behind a found barrel, from its visible top) and `stripe_join` (a stripe in pieces), on by default and merged on Tanush's "understood" · B, `tm save` stores the vendor's detections with each frame (merged; live check open) · C, the shot list · D, the slider tool `tools/hs_slider.py` (merged; window unchecked) · F, the histogram-against-thresholds script (merged; dry run).
- **2026-11-19 (data session):** the vendor save checked on the robot, it works (closes B) · the first four conditions shot and imported with the vendor's answers: the black ottoman lid under four lamp settings (`4A8B_lamp{warm6,mid6,cool6,mid3}_ottoman_*`, 36 frames; boxes and slider labels open).
- **Before (the 2026-11-09 list):** hs color model adopted · doc cleanup · move to the CLI · data: wood ladder 117, black 15, ruler 12 · `tm seg` · eval table `tools/report.py` · side occlusion explained, first fix off · histograms + `HISTOGRAMS-FOR-DAVE.pdf`. Tried and not adopted 2026-11-16: one color range fit on all tables; thresholds read from labels as a ceiling (53 of 152 on black + bright wood).
