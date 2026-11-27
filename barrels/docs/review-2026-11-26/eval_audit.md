# Audit of how the barrel detector is measured

Read-only audit of the snapshot `scratchpad/final/barrels` (identical to branch `wip/final`), the final report `barrels/docs/REPORT-2026-11-25.md`, and the git history. Nothing in the project was changed. No test image was loaded, viewed or scored: test numbers below come only from the stored result files of the project's own test look and from label files and split lists.

Scripts and outputs of this audit: `/private/tmp/claude-502/-Users-tanush-Desktop-Celeste-vex-aim-tools-barrels/bc194f8a-459b-4746-98d1-b23688f2f947/scratchpad/work_eval/` (`counts.py`, `train_run.py`, `analyse.py` with `analyse_out.txt`, `intervals.py` with `intervals_out.txt`, `verify_off.py`, `per_barrel.csv`, `per_frame.csv`). `train_run.py` re-ran the snapshot's default detector and the saved vendor boxes on the train frames only and reproduces the project's train totals (ours 148, vendor 177 of 243 with 30 false).

Short answer: the numbers are honest counts, produced by real scripts, and the test frames were kept closed. They are not strong enough to steer most of the decisions that were taken on them. The three largest problems are (1) sample sizes that are 3 to 5 times smaller than they look, (2) a comparison with the vendor whose size and, per condition, whose sign depend on a labelling convention, and (3) a gate plus a simulator that together pulled five days of detector work toward a part of the problem that is not where the detector loses.

---

## 1. Sample sizes and power

### 1.1 What exists (label files and `data/splits.json`)

| place (conditions) | train frames | train barrels (orange / blue) | train empty frames (clean) | test frames | test barrels | test empty frames |
|---|---:|---:|---:|---:|---:|---:|
| home white table, HOME (1) | 16 | 29 (16 / 13) | 2 (2) | 5 | 9 | 1 |
| campus study room, CAMPUS (1) | 21 | 35 (17 / 18) | 4 (4) | 10 | 24 | 1 |
| ABP gray table (1) | 8 | 16 (7 / 9) | 1 (0) | 2 | 2 | 1 |
| ABP white, occlusion set (1) | 17 | 32 (15 / 17) | 1 (0) | 1 | 2 | 0 |
| pale wood (1) | 7 | 15 (9 / 6) | 1 (0) | 2 | 2 | 1 |
| ottoman, 4 lamp settings | 28 | 60 (32 / 28) | 4 (0) | 8 | 8 | 4 |
| glass table, 5 lights | 36 | 75 (40 / 35) | 6 (0) | 10 | 10 | 5 |
| bathroom floor, 4 lamp settings | 28 | 60 (32 / 28) | 4 (0) | 8 | 8 | 4 |
| black table, parked (1) | 10 | 26 | 1 (1) | 5 | 11 | 1 |
| wood desk, 9 lamp settings, parked | 90 | 189 | 9 (0) | 27 | 45 | 9 |
| **all** | **261** | **537 (273 / 264)** | **33 (7)** | **78** | **121** | **27** |

Dave's office (another robot): 12 frames, 34 barrels, in no split.

Three structural facts that the tables in the project's reports do not show:

- **A "condition" is not an independent sample.** On the ottoman, the glass table, the bathroom floor and the wood desk the same arrangement was shot under 4, 5, 4 and 9 lamp settings without touching the robot or the scene, and the boxes were copied between lights. The 243 "barrels" of the ordinary new conditions on train are 108 physical barrel placements in 47 arrangements at 6 places. Of the 45 placements that were shot under several lights, 25 (ours) and 30 (vendor) have the same outcome under every light; the intraclass correlation of "found" is 0.57 and 0.59, a design effect of about 2.7. The effective number of independent barrels behind "243" is about 90, and behind "glass 75" it is 15.
- **The test set of the new conditions is one scenario.** For every new condition the split sends `neg_01` (empty table) and `occl_01` (a barrel half hidden behind a barrel of the other color) to test. The "32 test barrels" are 16 frames of 6 physical arrangements, 2 barrels each: 12 placements, one of each pair occluded. No free-standing, touching, close, edge or clutter scene of any new condition is in test.
- **The clean empty frames are in the wrong split.** Because `neg_01` (the clean empty table) goes to test and `neg_02` (clutter only) stays in train, no new condition has a clean empty frame in train. The rule "a box on a clean empty frame disqualifies" acts on 7 train frames in total (home 2, campus 4, black 1). Zero false boxes on 7 frames bounds the per-frame rate at 43 % (rule of three); on all 33 train empty frames at 9 %.

All sets use one robot (4A8B) and, as far as the docs say (`DATA.md`, campus session: "four barrels"), the same four physical barrels.

### 1.2 Intervals on the headline numbers

Wilson 95 % intervals, treating barrels as independent, which is optimistic:

| claim | rate | 95 % interval |
|---|---:|---|
| test, new conditions, ours 14 of 32 | 0.44 | 0.28 to 0.61 |
| test, new conditions, vendor 23 of 32 | 0.72 | 0.55 to 0.84 |
| the same with the effective n (12 placements): 5 of 12, 9 of 12 | 0.42, 0.75 | 0.19 to 0.68, 0.47 to 0.91 |
| home test 9 of 9 | 1.00 | 0.70 to 1.00 |
| campus test 22 of 24 | 0.92 | 0.74 to 0.98 |
| home train 28 of 29 | 0.97 | 0.83 to 0.99 |
| campus train 35 of 35 | 1.00 | 0.90 to 1.00 |
| train, ordinary new, ours 148 of 243 | 0.61 | 0.55 to 0.67 (wider by about 1.6 times once the design effect is applied) |
| train, ordinary new, vendor 177 of 243 | 0.73 | 0.67 to 0.78 (same) |
| glass train, ours 74 of 75 | 0.99 | 0.93 to 1.00 as printed; 15 placements in truth |
| glass test, ours 6 of 10 | 0.60 | 0.31 to 0.83; one arrangement in truth |
| any 15-barrel condition at 12 of 15 | 0.80 | 0.55 to 0.93 |
| any 2-barrel test condition at 1 of 2 | 0.50 | 0.09 to 0.91 |
| Dave's office 13 of 34 | 0.38 | 0.24 to 0.55 |

Smallest difference between two arms that would be detected (5 % two-sided, 80 % power, independent barrels, rates near 0.6): 0.50 with 15 barrels per arm, 0.34 with 32, 0.24 with 64, 0.12 with 243. A per-condition comparison (15 barrels, in truth 15 placements at one place) can only see differences of half the scale.

### 1.3 Which published comparisons hold

Distinguishable from noise:

- **The vendor is far ahead on the ottoman.** Train 9 against 37 of 45 (cool lamp alone 3 against 13 of 15, Fisher p = 0.001); test 1 against 7 of 8. Fifteen placements, one place, but the effect is the size of the scale and holds under every counting rule.
- **The vendor is ahead on the gray table** (10 against 16 of 16, p = 0.018; 16 independent placements at one place) and on the dim and mid bathroom lights (ours 2, vendor 17 of 30).
- **We find most barrels on the two white tables.** Best unbiased estimate: test 31 of 33, 0.94, interval 0.80 to 0.98.

Not distinguishable from noise:

- **"Vendor 177, ours 148 on train" as a pooled claim.** The naive interval on the difference (ours minus vendor) is −0.19 to −0.05. Resampling arrangements instead of barrels gives −0.26 to +0.03; resampling the 6 places gives −0.42 to +0.11. By place it is 3 places each way (strict rule). The pooled number is a weighted sum in which the weights are how many lamp settings each place happened to get.
- **"Ours 14, vendor 23 of 32" on test.** Fisher p = 0.042 only if the 32 are independent. By place the vendor is ahead in 3 (ottoman 1 v 7 of 8, glass 6 v 8 of 10, bathroom 2 v 3 of 8) and tied in 3; sign test p = 0.25. Six of the nine barrels of difference are one ottoman arrangement under four lamp settings. The test look adds almost nothing to what the train frames already said about the ottoman, and says nothing about any other scenario.
- **Every "we win" row:** pale wood 13 v 12 of 15 (p = 1.0), the white occlusion set 26 v 24 of 32 (p = 0.76), the cool-lamp bathroom 13 v 11 of 15. The 23 train barrels we find and the vendor does not (strict rule) are 11 physical placements; under the place rule they are 7 barrels, 6 placements. Glass 74 v 60 of 75 looks significant and is three physical placements counted five times each (section 2.4).
- **"Glass is worse on test (6 of 10) than on train (74 of 75)".** The test side is one arrangement: its occluded barrel is missed under 4 of 5 lights. One event. It is also a different scenario (`occl_01`) from anything in the glass train rows, and the test boxes are hand-drawn while the glass train boxes are AI proposals (section 3).
- **Campus train 35 of 35 against test 22 of 24** (p = 0.16).
- **False-box claims on test:** ours 4 against the vendor's 5 (p = 0.72); the verify step 9 to 6 (p = 0.58).
- **Every single-switch decision** in the detector work (sections 5 to 7), and "the light rule finds 36 of 60 on the bathroom floor, beating the vendor's 28": 15 placements under 4 lights, with a rule fit on those frames.

Consequence. The project can trust three statements: the white tables work, the ottoman and gray table do not, and the reason is the color step. It cannot rank itself against the vendor on any other condition, cannot tell a 5-point change from none, and cannot evaluate a single detector switch on real data. Most of the week's decisions were of the last kind.

---

## 2. The metric

### 2.1 The bottom clause in pixels, against label noise

Tolerance = max(3 px, 10 % of the true box height). Box heights of the 537 train barrels: minimum 29 px, 10th percentile 40, median 62, 75th percentile 79, maximum 248. So the tolerance is 4 px or less for 12 % of the barrels, 5 px or less for 26 %, 6 px or less for 46 %, 8 px or less for 76 %. Only close barrels get the "about 15 px" that `EVAL.md` mentions.

What the labels are good for:

- `DATA.md` tells the labeller "1 to 2 px precision is enough".
- AI proposals against the human on 12 frames (`results/2026-11-24_box_proposals/summary.md`): IoU median 0.89, worst 0.80; edges median 1 px, worst 5 px; bottom edge median 1 px, worst 3 px; a systematic 2 px inward shift on the left and top edges; a flag or `clean` difference on 3 of 12 frames.
- Boxes copied between lamp settings are stated to shift by less than 0.3 px, so this adds little.
- 102 of 537 train barrels are flagged `occluded` and 45 `bottom_estimated`: for these the true bottom is a guess, made with a size guide that draws the barrel the detector's own camera model expects (`box_tool.py` key `g`, `box_look.py --expect`).
- The documented systematic geometry error (bottoms inferred from the top row 4 to 7 px low for far barrels, 2026-11-18) is by itself as large as the whole tolerance of a far barrel. It was not fixed by calibration (the better camera was rejected by the gate, section 5); it was sidestepped by a rule that no longer takes bottoms from the top row on home and campus.

So for the farther half of the barrels, label noise of 1 to 3 px uses a quarter to three quarters of a 4 to 6 px budget.

### 2.2 How many misses fail only the bottom clause

From `train_run.py` on all train frames plus Dave's (571 barrels):

| arm | barrels scored | misses | misses that fail only the bottom clause |
|---|---:|---:|---:|
| ours, all train | 571 | 334 | 4 (1 %) |
| ours, ordinary new conditions | 243 | 95 | 2 |
| ours, home + campus | 64 | 1 | 0 |
| vendor, ordinary new conditions | 243 | 66 | 18 (27 %) |

The clause costs our detector nothing and costs the vendor a quarter of its misses. Fourteen of the vendor's 18 are occluded barrels, where it boxes the visible part; ten of the 18 are two glass placements (`clutter_01` barrel 2, `occl_02` barrel 1) repeated under five lights; the four on free-standing barrels miss a 5.5 to 5.6 px tolerance by 0.4 to 1.4 px.

Bottom error on matched pairs (prediction minus label): ours on free-standing barrels median −1 px, 10th to 90th percentile −2 to +2 (n = 166); vendor median +2 px, −2 to +4 (n = 146). Of our 250 matched pairs, 25 pass within 2 px of the line; of the vendor's, 32 pass and 7 fail within 2 px of it. About a tenth of all hits of either arm would flip under a 2 px change in a label.

### 2.3 Is the detector tuned to the labelling convention?

Yes, in four documented ways, none hidden:

1. The camera in use (`AIM_4A8B6118_BOXFIT`) was fit to the labelled boxes (2026-11-03, 24 instances) and later ruler measurements that disagreed were not adopted. Inferred bottoms are scored against the labels the camera was fit to.
2. Hidden bottoms in the labels are estimated with that same camera's size guide. Agreement between an inferred box and its label on an occluded barrel is partly agreement of the model with itself.
3. Labels were adjusted to the convention after the fact (38 box edges snapped to the frame edge on 2026-11-16 and 2026-11-21, with Tanush's go), and a rule was rejected for boxes "2 to 3 px too wide against frame-clipped labels" (`thin_frame`, later switched on by word).
4. The detector has its own bottom gate at 15 % of the height and the score has 10 %. The final report already names this as the largest single cause (65 of 138 events) of "more paint, box disappears". The fix proposed there is to tighten the detector to the score's number, that is, to tune further to the convention.

The convention itself is tight boxes "bulge to bulge". Our boxes have median width ratio 0.94 to 1.00; the vendor's are 6 to 9 % larger (3 px each side, 6 px higher at the top). The AI proposals sit 2 px inside the human boxes on two edges, the same direction. None of this is wrong; it means IoU thresholds bite the vendor first.

### 2.4 Is the vendor treated fairly? The comparison under each rule

Train, ordinary new conditions, 243 barrels, frames with vendor files (found, false boxes in brackets):

| rule | ours | vendor |
|---|---|---|
| strict v2 (IoU 0.5 and bottom within 10 %) | 148 (7; 12 without the verify step) | 177 (30) |
| overlap (IoU 0.5, bottom not checked) | 150 (5) | 195 (12) |
| place (right color, centers within half a box width) | 150 (5) | 200 (7) |

By place, strict then place rule (ours v vendor): gray 10 v 16, then 11 v 16; ottoman 9 v 37, then 9 v 39; pale wood 13 v 12, then 13 v 13; white occlusion set 26 v 24, then 26 v 27; glass 74 v 60, then 75 v 74; bathroom 16 v 28, then 16 v 31.

Test, new conditions, 32 barrels (from the stored test-look files): strict 14 (4) v 23 (5); overlap 16 (2) v 27 (1); place 16 (2) v 28 (0).

Sensitivity on the train set (found, ours v vendor): bottom tolerance 5 / 10 / 15 / 20 %: 139 v 144, 148 v 177, 150 v 185, 150 v 193. IoU alone at 0.4 / 0.5 / 0.6 / 0.7: 150 v 200, 150 v 195, 148 v 183, 145 v 146.

What this shows:

- **Every "we win" in the final report exists only under the strict rule.** Under the place rule we win nowhere: glass 75 v 74, pale wood 13 v 13, cool-lamp bathroom 13 v 13, white occlusion set 26 v 27. The report lists these four as the conditions to protect "where we already match or beat the vendor".
- **"Glass 74 against 60", the largest claimed win, is three physical placements.** The vendor's boxes on two occluded barrels end 5 to 9 px below labels with a 4.9 px tolerance and on one more barrel fall under IoU 0.5; each is counted under five lights. Those labels are AI proposals accepted unchanged (section 3). Whether the vendor box includes the mirror image in the glass or the label is high was not looked at by anyone.
- **"The vendor draws about 2.5 times as many false boxes" is a counting artifact.** 23 of the vendor's 30 "false" boxes sit on a real barrel and fail the overlap or bottom clause; the strict rule counts each of them twice, as a miss and as a false box, while a barrel we simply do not see costs us one. Boxes on no barrel: vendor 7, ours 5. The real difference is narrower and more specific: all 7 of the vendor's are on empty frames (about three physical scenes: glass clutter-only, the glass trap shot, the fruit wrapper), and we draw none on an empty frame.
- **The report's headline table mixes two detectors.** The train row (ours 148 found, 12 false) is the detector without the verify step; the test row is the detector with it. With the verify step the train count is 7 false (`verify_off.py`).
- **The size of the gap is a convention parameter.** Depending on the rule it is 1 barrel (IoU 0.7) to 50 barrels (place) of 243. The direction is stable: the vendor finds at least as many under every rule tried.
- **On occluded barrels the two rules give opposite answers.** 47 train barrels flagged `occluded`: strict ours 25, vendor 17; place ours 27, vendor 32. "Occlusion is where we beat the vendor" is true only if the full inferred box is what matters and the hand-estimated full box is right.

Which rule is right depends on use. If the bottom edge will feed distance, the vendor's partial box on a hidden barrel really is wrong (its bottom is 8 to 16 px above the label on `bottom_estimated` barrels) and the strict rule measures a real capability. That argument needs the distance error to be measured, and it is not (section 8). Until then the strict number is a statement about agreement with a labelling convention the vendor never signed.

Other properties of the score: the headline is the mean of two F1 values, so the double counting above enters twice; per-condition scores are F1 on 6 to 9 barrels per color; the published "campus 0.99 / home 0.93" in `CLAUDE.md` and `STATUS.md` are from 2026-11-09 and no longer what the code produces (28 of 29 and 35 of 35 today); `STATUS.md` still lists the black table at 2 of 26 while the stored baseline has 5.

---

## 3. Label provenance and circularity

### 3.1 Box labels (truth for every score)

| source | train frames | test frames |
|---|---:|---:|
| drawn by Tanush | 91 | 47 |
| drawn by Tanush under one light, copied to the other lights | 90 | 26 |
| converted from v1 instances, then fixed by hand (home) | 16 | 5 |
| proposed by Claude from looking at the picture, accepted unchanged | 22 | 0 |
| copies of those proposals to other lights | 42 | 0 |

- All 64 glass and bathroom train frames, 135 of the 243 ordinary-new train barrels (56 %), rest on 15 AI proposals. The proposals were committed at 14:19:55 and "accepted unchanged", all 15, with the four test frames hand-boxed as well, by 14:28:53 (commit `9b7824f`, whose message also says "copies unreviewed"; a later commit at 15:02 says checked). Zero edits in nine minutes is acceptance at a glance, the risk the decision record of that day names.
- The measured quality of proposals (median 1 px, 3 of 12 frames with a flag difference) is fine for the IoU clause and marginal for the bottom clause on far barrels.
- Test labels are all human. So train and test differ in labeller exactly on the two places (glass, bathroom) where train and test numbers are being compared.
- Independence of the AI labeller from the detector is asserted ("a Claude labeler's mistakes are independent of the detector's"). The same model family also wrote the detector, its acceptance rules and its verdicts, and its boxes lean tight in the same direction as the detector's. The independence was not measured.

### 3.2 Slider labels (`_hs.json`, the target of the adaptive-threshold work)

45 files, 3 frames for each of 15 conditions. 20 were set from the adopted values (gray, ottoman, pale wood, two glass frames); 25 started from the "computed" proposal, 23 of them then moved.

All 45 were set while the tool showed the boxes that the detector of that moment drew from the thresholds under the mouse. The file records which detector (`detector_git`: four different versions across the 45) and how many boxes it drew. The criterion is "as much barrel painted as needed to detect it". The computed proposal and the green "feasible" bands are defined as the settings under which today's detector still finds every barrel and adds no false box.

These are therefore not labels of the color of barrels. They are the operating point of one detector version on one frame. Consequences:

- **"Your slider labels prove the fix exists"** (overnight report; ottoman 12 to 15 of 15 with hand thresholds against 0 to 6) is in-sample: the thresholds were tuned, watching the boxes, on the 3 frames that hold 9 of each condition's 15 barrels. The table calls it "ceiling, not a method"; the summary sentence drops the caveat.
- **The target is noisy and not even optimal.** Hand thresholds find fewer barrels than the fixed model on pale wood (11 v 12) and fewer than the failed adaptive rule on gray (15 v 16). Hand and box-derived thresholds differ by a median of 26 to 46 saturation units. Tanush says some are suboptimal. The sweep found 138 cases on 35 of the 45 frames where painting more loses a barrel, so "the best threshold" is not well defined.
- **The negative result is uninterpretable.** "Nothing in the histogram predicts the thresholds when a place is held out" was tested with 3, then 5 places, against a target that depends on the detector version and on which of several equally good settings the hand stopped at. That design could not have found a relation of moderate strength if one exists.
- **The target moves with the thing it is meant to fix.** Four detector switches changed on the day the last 27 labels were set.

### 3.3 Other circular or in-sample links

- The "realistic" damage levels that now judge detector rules were measured on the home train frames, the frames the color model was fit on, where the color step works best.
- The 50 source barrels of the occlusion scorecard are free-standing home and campus train barrels, the same frames the gate protects.
- "Campus 0.99" is the best of 42 configurations scored on those 21 frames, picked by a rule that was rewritten after the first pre-registered rule chose a regression (`DECISIONS.md` 2026-11-09: "accepted as the rule that picked it").
- Before each shoot the detector was run on one to four trial shots of the new place (12 in all, kept locally, not in any split). These are not held-out test frames, so the "possible peek" in the final report is a naming false alarm. They do mean each condition's failure was known before any rule about it was written.

---

## 4. Train and test hygiene

What is sound: splits are assigned at import, by arrangement where lights repeat; the tools refuse test frames; the one test look was written first and no source file changed after it; the two v1 looks in October were pixel scores on the 5 home frames only.

What is weak:

- **There is no held-out place.** Every place has train frames from the same session, table, light and barrels as its test frames. The only data from another robot and room is Dave's office (13 of 34, 0.38, interval 0.24 to 0.55), and it is set aside as "indicative" because his boxes group barrels. It is the only out-of-distribution number the project has and it is the worst one.
- **The test set cannot detect overfitting.** For the new conditions it is 12 placements of one scenario. For the white tables it is 33 barrels: an interval of 0.80 to 0.98 is compatible with no optimism and with a 15-point drop.
- **Everything was decided on train.** All 18 pre-registrations (28 rounds), all 26 new switches, the camera, the color model and the realistic damage levels were developed and judged on the train frames, most of them on the 37 home and campus frames that the gate also protects, or on simulations built from those frames.
- **Direction of the gaps.** Home and campus go from 63 of 64 with no false box on train to 31 of 33 with one false box on test; glass from 74 of 75 to 6 of 10. Each is within noise on its own; all point the same way; none is conclusive. The honest reading is "not measurable with this test set", not "holds up on unseen frames".
- **Leave-one-place-out exists and was used only for the color relation.** There it failed every time. The same test was never applied to a detector rule.

---

## 5. The never-regress gate as a ratchet

The gate (`gate.py`) fails a change if any of 26 scenario rows of home and campus loses one found barrel or gains one false box, or if any set gains a box on an empty frame. The protected rows hold 64 barrels, 63 found, 0 false; 13 of the 26 rows hold one or two barrels.

**(a) It locks in the current state, luck included.** At 63 of 64 the protected sets can no longer show an improvement; the gate can only say no. Six of the 63 protected hits pass the bottom clause by 2 px or less (section 2.2). If a change with no average effect flips each protected barrel with probability 1 %, it fails the gate 47 % of the time; at 2 %, 72 %.

**(b) It has already blocked principled changes on single barrels.**
- The ruler calibration: a camera with bottoms within 1 px and sizes within 2 % was rejected because home `occl` went 4 to 3. The camera known to be 4 to 7 px off stayed.
- The stencil detector as a second opinion: 10 wrong boxes against 45 on the scorecard, rejected for losing barrels on home and campus.
- Every color candidate has to hold all 63 while moving the thresholds that find them. The light rule failed on one box on an empty glass frame.

**(c) Rules are fitted until the gate passes.** From the switch census (git history of `detector.py`, `EXPERIMENTS.md`, verdict files):

| | 2026-11-16 | 2026-11-23 |
|---|---:|---:|
| `DetConfig` fields | 24 | 51 |
| boolean switches | 4 | 30 |
| `detector.py` lines | 621 | 1904 |

- 26 switches and one threshold were added in 5 calendar days (11-18 to 11-23); 21 are on.
- 3 of them change a home or campus count, for 4 barrels in total (home 25 to 28, campus 34 to 35), all in place by 11-19. The 16 switches turned on after that moved no protected count. From 11-19 on, the gate could register nothing but a regression.
- 5 certainly (estimate 8 to 10) are on by simulated evidence alone, as far as the project's own records show. One verdict says of two of them "on real pixels untested".

**What the switches do on real frames, measured for this audit** (`week_switches.py`: the snapshot default against the same detector with the 21 switches off, train frames only; found of barrels, false boxes in brackets):

| real set | 21 switches off | default |
|---|---|---|
| home + campus (protected) | 59 of 64 (0) | 63 of 64 (0) |
| ABP white occlusion set, shot 11-21 | 19 of 32 (3) | 26 of 32 (0) |
| gray, pale wood, glass, ottoman, bathroom | 108 of 226 (7) | 123 of 226 (8) |
| black, wood, Dave (parked or indicative) | 20 of 249 (5) | 25 of 249 (11) |
| **all real train frames** | **206 of 571 (15)** | **237 of 571 (19)** |

- As a group the switches are worth 31 real barrels, 13 of them on occluded barrels (23 to 36 of 102), on 37 of 273 frames. This is a better result than the project's documents claim for themselves, and it is in none of them: no report has a "week's switches off" arm on the new data.
- The 5 switches of 11-18 and 11-19 that moved the protected counts carry 23 of the 31. The 16 later ones together add 8 barrels on 16 frames. No single one of those 16 can be judged on real data: the effect per switch is under one barrel.
- The project's own one-switch-off column (`results/2026-11-24_occl_strict/boxes/boxes.csv`, 261 real boxes) says the same. Of 237 real hits, 59 disappear when `side_hidden` alone is off, 17 without `stripe_join` and 5 without `cap_behind`; `half_stripe`, `stripe_wide`, `pin_outline`, `stripe_bridge` and `seam_height` carry 2 or 3 each; `thin_frame`, `pin_thin`, `half_thin`, `cap_seen_bottom` and `closeup_stripe` one each; `post_pair`, `thin_span`, `cap_same`, `cap_low` and `edge_check` none. Two switches do nearly all the real work; five that are on do none that the real frames can show.
- The 17 occlusion switches add false boxes on real frames (12 to 19 with the close-up and verify switches held on), all on sets the gate does not protect: wood 3, Dave 2, black 1, glass 1, ottoman 1, with one removed on the ABP white set (net 7). The gate and the simulator both reported "no false box added".

**The direction this pushed the work.** Of the 52 train barrels the vendor finds and we do not (strict rule), 50 are on the ottoman (28), the bathroom floor (16) and the gray table (6), where the color step paints too little; only 4 of the 52 are occluded barrels. The occlusion work paid on real frames, as the table shows, but it could not close the gap that the week's goal names, and about 21 of the 26 switches went to it. The measurement machinery explains why: the gate and the scorecard can both see occlusion on white-table masks, and neither can see the color step.

**Should glass, pale wood, the occlusion set and the cool-lamp bathroom be added to the protected list?** No, not in the present form.
- They were chosen as the places "where we already match or beat the vendor". Under the place rule we beat it on none of them; the selection is on the outcome of a contested rule.
- Glass would add 36 frames that are 6 arrangements under 5 lights, with AI labels: one physical barrel gets five votes, and one flip fails the gate.
- These are exactly the places a color change must be free to move. The next planned step (a fresh try of the light rule "with the glass frames as the trap") would be judged by a gate that the previous try failed by one box.
- A protected list that only grows makes every later change harder to pass and so makes each accepted change more likely to be a narrow patch.

A gate is worth having. Its unit should be the place and its test a tolerance on the aggregate, with the clean-empty-frame rule kept as the one hard line (section 9).

---

## 6. Simulated evidence

### 6.1 What a simulated scene is

`occlude.py` builds each scene from an empty 640 x 480 mask, the class-mask pixels of one barrel at its own place, and one occluder. Seven kinds of occluder erase barrel pixels and leave nothing behind (the occluder looks like empty table); three paste a scaled copy of another barrel; one pastes a plain rectangle of barrel color. The module's own header lists what is absent: the occluder's shadow, its reflection, color bleeding at the seam, the change in exposure. Also absent: any paint on the table or the room, any clutter of barrel color except the one rectangle, any second barrel except the pasted one, and any failure of the color step, because a barrel enters the pool only if the detector already finds it alone.

The "50 source barrels" are 12 home barrels as hand masks, the same 12 home barrels as color-model masks, and 26 campus barrels (`results/2026-11-19_det_occl/scorecard.md`): 38 distinct barrel images from 21 frames of two white tables. The 3888 scenes are deterministic transforms of them with one seed. The effective sample behind "2811 of 3888" is 38 images, 21 frames, or two places.

The damaged-mask test (`degrade.py`) is 29 home barrels times 5 seeds (the "145") or 20 seeds (the "580").

### 6.2 Is a difference of a few boxes signal?

No interval is printed for any simulated number, and decisions were taken at this resolution: wrong boxes 45 to 48 of 3888, 63 to 66 of 3888, medium damage 3 to 4 of 580 and 1 to 4 of 145, "too big" 4.14 % against 4.11 %, 7 against a limit of 6 of 580.

Some simulated differences are large enough to mean something: at "medium" with 20 seeds the default draws 3 false boxes of 580 and the rejected cover-box arm 20. The margins that decided other switches are not of that kind. A count of 3 has a 95 % Poisson interval of about 1 to 9 and a count of 4 about 1 to 10, so "3 to 4" and "1 to 4" separate nothing. The three scenes behind "45 to 48" come from one source barrel at three amounts, and the four boxes behind "7 against 6" are one frame under four seeds: one event each.

Resampling the 21 source frames of the project's own `scenes.csv` files (`work_eval/sim/card_stats.py`, 2000 resamples) puts numbers on this:

| scorecard quantity | value | 95 % interval over source frames |
|---|---:|---|
| found, before the verify step | 2876 of 3888 | 2775 to 2970 |
| boxes where no barrel is | 48 | 23 to 79 |
| `stripe_bridge`: 45 to 48 | +3 | 0 to +10; all three on one campus barrel |
| the verify step: 48 to 23 | −25 | −43 to −9 |
| the verify step, found | −7 | −14 to −2 |

Nine of the 48 wrong boxes, and 9 of the 23 that remain, sit on one source barrel (campus `topstripe_01`). The large moves (88 to 45, 48 to 23, found +300) are outside the noise; the three-box margins that switched rules on and off are inside it.

Because the scenes are paired and deterministic, a changed scene is a real change in the code's behaviour on that scene. What it is not is evidence about the rate of that behaviour on real frames.

### 6.3 "Medium" is harsher than real, and so is its replacement

`results/2026-11-19_damage_realism/measured.md`, 12 free-standing home barrels: the real stripe is in one piece on 12 of 12; the simulated "medium" leaves it in one piece on 5 of 60, "bad day" on 11 of 60 (it applies the 90th percentile of every kind of damage to every barrel at once). The real masks have paint spilled beside the barrel (2 to 24 % of its area: reflections and shadow); every simulated level has none. The spill is the kind of damage behind the largest group of "more paint, box disappears" events (section 2.3).

Consequences:

- The realistic levels were measured only on the home white table, the frames the color model was fit on. "Typical" damage there finds 145 of 145. The statement "given good segmentation the detector finds the barrel" is true for the white tables almost by construction and says nothing about the ottoman, the bathroom floor or the gray table, where a fifth to a quarter of a stripe can be under the brightness gate. No damage level represents the places where the detector loses.
- "Medium" was counted as evidence when it agreed (`side_hidden`: "medium 64 to 99 of 145 with false boxes 22 to 1") and set aside when it did not (`stripe_bridge`: "failed only on harsher-than-real damage"). The timeline of that reversal is in section 7.

### 6.4 Simulation against the real frames

The project has no head-to-head: real labels carry an `occluded` flag and no hidden amount or occluder kind, and no document scores the same detector change on simulated and real occlusion side by side. The run made for this audit (section 5, `week_switches.py`) gives the comparison that exists:

| | before the week's switches | default |
|---|---|---|
| simulated scorecard, found | 2153 of 3888 (55 %) | 2869 of 3888 (74 %) |
| real occlusion set (ABP white, 17 train frames) | 19 of 32 | 26 of 32 |
| real barrels flagged occluded, white tables | 7 of 24 | 17 of 24 |
| real barrels flagged occluded, all train sets | 23 of 102 | 36 of 102 |
| simulated "boxes where no barrel is" | 88 | 23 |
| real false boxes, all train frames | 15 | 19 |

- **Direction: confirmed.** The occlusion set was shot on 11-21, after the 17 occlusion switches were written (two of them were switched on only afterwards, on 11-23). Seven of its frames gain a barrel and none loses one (sign test p = 0.016). This is close to out-of-sample evidence that the occlusion work transfers, and the project never reports it; its documents quote the simulated numbers.
- **Size: does not transfer.** Mapping each of the 14 occluded barrels of the real occlusion set to its nearest scorecard cell predicts about 11 found (an approximate mapping made for this audit); 8 are. Four of the six real misses fall in cells the simulation scores at 77 to 98 %. Half hidden is "1160 of 1296" in simulation; on the real occlusion set 6 of 14 occluded barrels are still missed, and off the white tables occlusion handling is irrelevant because the barrel is not painted (0 of 22 occluded barrels found on the ottoman, bathroom and black table).
- **False boxes: the simulation points the wrong way.** On an empty mask the only false box possible is one built from barrel pixels. Real false boxes come from a tin, wood grain, a fruit wrapper, a blue chair. Simulated wrong boxes fell by three quarters while real false boxes rose from 15 to 19, and with the close-up and verify switches held fixed the 17 occlusion switches add 7.

### 6.5 What can be concluded from the simulations

Safe: that a mechanism does what it was written to do on a clean mask, and, as a group and on white tables, that the direction of the effect carries to real occluded barrels.

Not safe: the size of any gain; any on or off decision that rests on a difference of a few scenes; any claim that a rule adds no false boxes; anything about a place where the color step is the failure.

---

## 7. Pre-registration practice

Counts (all 18 `experiments/*/PREREG.md`, their verdict files, `DECISIONS.md`, git author dates):

| | |
|---|---:|
| PREREG files / rounds | 18 / 28 |
| passed in full, adopted | 5 |
| passed in part, the passing part adopted | 4 |
| failed | 6 (one of them adopted in full anyway) |
| nothing adopted | 7 |
| no verdict possible (dry run; the test look) | 2 |
| switches now on that failed their own registered rule | 5 of 21 (`stripe_join`, `cap_behind`, `pin_thin`, `stripe_bridge`, `thin_frame`) |
| experiments with a round-2 addendum | 10; in none did the first-choice arm pass round 1 |

**Where the rule was bent after the result.**
- `det_given_seg` (2026-11-18). The PREREG says "Anything that does not pass stays behind its switch, off. The rule is not re-picked after the results." The verdict says "No arm passes. Nothing is adopted." Both switches were turned on 73 minutes later: "the two boxes on which the pre-registered rule failed do not block it" (`DECISIONS.md`).
- `stripe_bridge`, `thin_frame` (2026-11-20, on since 2026-11-23). Verdict "Off by the rule"; switched on by "follow ur rec", on the ground that the failure was "only on harsher-than-real damage". One of the two failed clauses was the scorecard (45 to 48), which is not a damage level.
- `pin_thin`. Failed its own rule; the next PREREG states that the old failure "is not part of this rule"; it is on.
- The "medium" damage level. Rules failed on it on 11-19 (17:49 and 18:50). That night the next PREREG relaxed it to "not more than double"; on 11-20 a decision made it "reported, not decisive"; half an hour later a new PREREG registered it as judged again; a rule failed on it and the failure was waived on 11-23. The level counts when it agrees and is discounted when it does not.
- `occl_strict` (the verify step). Its tolerance, "found not down by more than 15 of 3888", was written with the measured loss already known, and the arm results are in the same commit as the PREREG.

**Where one box decides.** The deciding margins, with their denominators: 1 box of 26 at 0.6 px over the tolerance of a hand-estimated bottom (`det_given_seg`); 3 of 145 and 3 of 3888 (`det_occl`); 1 of 3888 and 1 of 145 (`occl_vertical`); 3 of 3888 and one box on a share, 4.14 % against 4.11 % (`occl_pin`); 7 against a limit of 6 of 580, all four extra boxes on one frame under four seeds (`occl_combined`); 3 of 3888, 1 of 580 twice, 5 boxes of 100 too wide by 2 to 3 px (`occl_sliver`); one box on an empty frame (`adaptive`, `color`); a score drop of 0.023 against an allowed 0.02 on 15 barrels (`color`). None of these PREREGs states a noise level, says that 3888 scenes come from 50 barrels or 580 from 29, or says what happens on a marginal failure. In practice the letter was applied except twice, when Tanush's word overrode it. Nine PREREGs include a "by eye" clause judged unblinded by the author of the rule.

**Where the candidates were explored on the judging data first.** Eight of the detector PREREG commits also contain census or baseline files computed on the benchmark that then judges the rule. In `occl_vertical` the census forecasts four cell changes and round 1 reproduces all four exactly. `pin_good` 0.05, the cap floor 0.4, the closure lines 0.15 and 0.1 and the 0.85 shape line were read off the same 50 barrels or the same handful of frames. `det_bottom` derives a rule from one barrel and gains exactly that barrel. For `occl_strict`, nine candidate checks were screened on the judging data and the adopted one was in its third iteration. These PREREGs are honest descriptions of a fit plus a regression guard. They are not prior commitments, and passing them is not evidence of generalization. The genuinely prior ones are `hs_pooled`, `hs_relation`, `adaptive_range`, the selection rule of `color` and the test look; all of those that could fail did fail.

**Timing.** The median time from the PREREG commit to the first result commit is about 13 minutes. Test look: 42 seconds. `occl_strict`: zero. The `color` PREREG was committed 38 seconds after a commit that had already scored the candidate families on the new places. Ten of 18 PREREG files were edited after results existed (addenda, append-only). With one author writing rule, code and verdict within minutes, the record shows order, not independence.

**Dating.** The machine date is 2026-11-23 and the last commit in the repository is 17:10:51 that day. Everything dated 2026-11-23, 24 or 25 was committed between 01:06 and 17:10 on 2026-11-23:

| real time, 2026-11-23 | event | date printed on it |
|---|---|---|
| 01:35 | adaptive rule PREREG | "2026-11-23, evening" |
| 01:44 | adaptive rule fails; a copy "frozen tonight" for "tomorrow's places" | 2026-11-24 experiment |
| 01:51 | overnight report | 2026-11-24 |
| 13:44 to 14:11 | glass and bathroom shot and imported | 2026-11-23 |
| 14:19 to 15:06 | AI box proposals accepted; slider labels | 2026-11-23 / 24 |
| 16:20 | verify-step PREREG and results | 2026-11-24 |
| 16:42 to 17:01 | color exploration, PREREG, two failed rounds | 2026-11-25 |
| 17:09:25 | test-look PREREG | 2026-11-25 |
| 17:10:07 | test-look results | folders 2026-11-23, summary 2026-11-25 |
| 17:10:51 | final report | 2026-11-25 |

What really happened:
- **The order of events is as claimed.** Git supports every "written before". The glass and bathroom frames did not exist when the adaptive rule was frozen (vendor-file timestamps and commit times agree), so that hold-out was real: 12 hours, same calendar day.
- **The promised held-out test was never run.** The frozen rule has one run, from before the new data ("C7: not applicable"). `TODO.md` still promises it. The test-look PREREG and the final report count "four rounds" in which adaptive rules failed, without it. Instead, new candidate families were explored on the new places and then registered. The one test this week that had a genuinely unseen place available did not use it.
- **Elapsed time is misstated.** "Overnight" was a two-hour block (01:06 to 03:06). "The week's push" is 157 commits in 5.0 days (11-18 16:33 to 11-23 17:10) with none on 11-17 or 11-22, printed across 8 calendar dates. A reader of the final report "of 2026-11-25" at a meeting on 2026-11-23 would assume two more days of work and review than took place. The shift is disclosed in two places only.
- **Review time.** Tanush's "understood" is the control that main code is explained before it lands. On 11-23 four switches, the verify step, the label policy and the test look happened inside 16 hours; the final report was committed 44 seconds after the test results.

Consequence. Pre-registration here works as a changelog discipline and as a guard against silent regressions, which has value. It does not work as protection against overfitting, because the rules are derived on the judging data, judged within minutes by their author, decided by single boxes, and overridden when they fail on something the team wants.

---

## 8. What is not measured at all

| quantity | state | why it matters |
|---|---|---|
| **The vendor in its own conditions** | Not measured. No white-table frame of home or campus has a vendor file; on 2026-11-23 the white table was skipped ("assume the vendor perfect there"). The only white-table vendor data is the occlusion set. | This is the first line of the week's goal ("at least as good as the vendor in the vendor's own conditions"). The goal has no number. |
| **Distance accuracy of the bottom edge** | Not measured. The `measured` split was defined on 2026-10-28 and never shot (`data/measured.csv` is a header). The 12 ruler frames were used to fit a camera, which was then not adopted. `eval_det` computes a projected ground error and a 15 mm criterion for every match; the one table does not print them. | The bottom clause exists because of distance. Converted with the adopted camera (computed here from the train labels, not measured): one pixel at the bottom edge is about 1.9 mm of range for the median barrel, and 10 % of the height is about 2.5 mm for a barrel at the bumper, 7 mm at 80 to 150 mm, 10 to 11 mm at 150 to 250 mm (309 of 497 barrels) and 14 to 16 mm at 250 to 400 mm. So the clause is of the same order as the 15 mm the planner's inflation suggests, and label noise of 1 to 3 px is 2 to 6 mm. That is a reasonable design, but it is arithmetic on a camera model that the ruler frames contradicted; nobody has checked a strict hit against a tape measure. |
| **Pixel quality of the color step on new conditions** | No masks outside the 21 home frames. The slider tool prints "painted inside your boxes" (38 to 73 %), an uncalibrated proxy; the color session measured single causes ad hoc (share of blue stripe under the brightness gate). | The diagnosis "the gap is the color step" is the main conclusion of the week and rests on in-sample slider ceilings and reason logs. |
| **Per-stage attribution on new conditions** | The last attribution tables are campus (2026-11-07) and occlusion (2026-11-11). For the ottoman, bathroom, gray table: none. | Supporting evidence from this audit: 50 of 52 vendor-only barrels are in those three places and only 4 are occluded. That is indirect; a table of misses by first failing stage does not exist. |
| **Variance across repeated shots** | None. Every scene was saved once per light ("one save each, no retakes"). Auto exposure and white balance are unlocked; whether they can be locked is an open question in `STATUS.md`. | There is no noise floor for any number in the project. The lamp ladders show that the same placement flips outcome between lights in 20 of 45 cases, so frame-level instability is large. |
| **Runtime** | Not measured. The report file notes 9.9 s for two arms on 78 frames on the laptop. No per-frame time, no budget, no figure for the robot loop. | `detector.py` tripled in a week and a verify pass was added. |
| **Video and live behaviour** | Six recordings, unlabelled, replayed for counts and "boxes changed" checks. No labelled sequence, no metric for the tracker, no measure of the motion or timing of the vendor's list (noted as not done). | Live impressions (the run with Dave) set the agenda twice; nothing measures them. |
| **Other robots and rooms** | Dave's office: 13 of 34 and 4 false, called indicative. | The only out-of-distribution number, and the lowest. |
| **False boxes in the wild** | 33 train empty frames, 7 clean, none clean in a new condition. | "No false box on a clean empty frame" is the project's hard line and has almost no data under it. |
| **Label agreement** | Human against AI on 12 frames; human against human never; the slider labels have no repeat. | Tolerances are within a factor of two to four of the measured disagreement. |


---

## 9. Verdict: the measurement problems most likely to be misleading the project, ranked

Recommendations only; nothing was implemented.

**1. Lamp settings are counted as samples, and the test set is 12 placements of one scenario.**
"243 barrels" is about 90 independent ones; "glass 75" is 15; "32 test barrels" is 12 placements at 6 places, all `occl_01`. Per-condition winners, the pooled train comparison and the test comparison are inside the noise once this is respected.
*Cheapest fix:* in `report.py`, print next to every count the number of physical placements and places behind it and an interval from resampling arrangements. Stop naming a winner for a condition. For the next shoot, send one whole 9-shot condition per place to test instead of `neg_01` + `occl_01`.

**2. The comparison with the vendor is a function of a labelling convention, and one box is charged twice.**
The gap is 1 to 50 barrels of 243 depending on the rule; all four "we win" conditions vanish under the place rule; 23 of the vendor's 30 "false boxes" sit on real barrels; the report's table mixes two detector versions.
*Cheapest fix:* always print the three rules side by side (the code already computes them) and lead with the place count, boxes on no barrel, and boxes on empty frames. Keep the strict rule as a separate "full box quality" number. Count a box that is on a barrel but fails the strict rule once, as "misplaced", not as a miss plus a false box.

**3. The gate is saturated and zero-tolerance, so the simulator became the only instrument, and it steered the work away from the real deficit.**
The protected sets stopped moving on 11-19 (63 of 64); 16 more switches were turned on after that on simulated evidence, worth 8 real barrels between them, and the occlusion switches added 7 false boxes on unprotected real sets that neither instrument reported. 50 of the 52 barrels the vendor finds and we miss are a color problem that no switch touches. The gate also rejected a better camera and blocks every color change on single barrels.
*Cheapest fix:* change the gate's unit from scenario row to place and its test from "no barrel lost" to "not worse by more than a stated margin" (for 64 barrels, 2), keeping one hard line: no box on a clean empty frame. Do not add conditions to the protected list. Add a cost side: a new switch stays off unless it gains real barrels on real frames at two places or more; stop adding switches on simulated evidence until item 5 is done.

**4. No place is held out, and the one honest held-out test available this week was not run.**
Every rule is developed and judged on the same train frames; the frozen adaptive rule was never tested on glass and bathroom; instead those places were explored and then "pre-registered" 38 seconds later.
*Cheapest fix:* with 8 places in hand, make leave-one-place-out the standard report for any rule that has fitted numbers, color or detector. Run the frozen rule now and log the result whatever it is. Shoot two or three new places whose frames are all test and are looked at once.

**5. Decisions are taken at single-box resolution on simulated scenes.**
Clauses such as 45 to 48 of 3888, 3 to 4 of 580 and 4.14 % against 4.11 % decided what is on and off, with no noise estimate, on scenes that are transforms of 50 barrels from two white tables. The same benchmark is waived when it disagrees (section 6, section 7).
*Cheapest fix:* resample the source barrels and print an interval with every scorecard number; decide only on differences outside it. Make the real frames the judge: a "switches off" arm on all real train frames (section 5) costs one minute and already shows what the group is worth; the simulator stays as a unit test of mechanisms.

**6. The targets of the color work are not labels, and over half of the new train boxes were accepted from the assistant unchanged.**
Slider thresholds are one detector version's operating point, set while watching its boxes, and are not well defined (138 non-monotone cases). The "no relation" result and the "ceiling" both inherit that. 135 of 243 ordinary-new train barrels have AI boxes accepted in nine minutes, and the largest claimed win over the vendor sits on them.
*Cheapest fix:* judge the color step directly and without the detector: share of each hand box's core that is painted and share of paint outside all boxes, per place (both are already computed by the slider tool's score line). Have Tanush re-box 20 frames blind to any proposal, twice, to measure the real label noise on bottoms; require it before the next comparison that turns on a 5 px tolerance.

**7. The things the project says it is for are not measured.**
The vendor on a white table (the first line of the goal), the distance error of the bottom edge (the reason for the strict rule), and the shot-to-shot noise of any number.
*Cheapest fix:* one sitting on the home white table: the 9 shots saved three times each with vendor files (27 frames: the vendor's own conditions and a noise floor at once), and five placements at ruler-measured distances scored in millimetres for both detectors. Print the ground-error column `eval_det` already computes.

**8. The pre-registration and the dates describe more independence and more time than there was.**
Rules are derived on the judging data, results follow in a median of 13 minutes, five live switches failed their own rule, and one calendar day carries three dates.
*Cheapest fix:* mark each PREREG "exploratory" (data seen while designing) or "confirmatory" (data not seen: a new place), and let only confirmatory ones support a claim. Require every acceptance clause to name its unit, its effective n and a margin, and to say what a marginal failure means. Date documents by the commit clock.

### What can be relied on today

- The detector finds about 9 in 10 barrels on the two white tables it was built on (test 31 of 33, interval 0.80 to 0.98), with few false boxes.
- The vendor finds clearly more on the ottoman and the gray table, and under dim or warm light on the bathroom floor; the cause is very probably the fixed color thresholds.
- The vendor finds at least as many barrels as we do under every counting rule tried; we draw no box on an empty frame where the vendor draws a few.
- The week's detector switches, as a group, find more real barrels (206 to 237 of 571 on train; 19 to 26 of 32 on the real occlusion set shot after most of them were written), at the cost of a few false boxes on sets outside the gate.
- The test frames were not used for tuning.

Everything else in the week's tables (per-condition winners, the false-box ratio, the glass gap, the worth of any single switch, the size of the simulated occlusion gains) is not established by the measurements that exist.
