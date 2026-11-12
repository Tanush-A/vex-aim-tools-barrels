# Unattended block, 2026-11-11: TODO 5, 6 and 7

Written by Claude for Tanush. Plain English. Read sections 1 and 2; sections 3 and 4 are the two walkthroughs you asked for.

## 1. What happened, in six lines

- **Step 5, `tm seg`:** coded, tested, pushed on `wip/tm-seg`. Not run on the robot. Needs your live check.
- **Step 6, the one eval table:** done on `wip/eval-report`. `python barrels/tools/report.py` prints it in 10 s. The published numbers reproduce: home 0.93, campus 0.99, Dave 0.47.
- **Step 7, occlusion:** the misses are reproduced and explained. A fix was built and tested by a rule written first. It finds the campus barrel behind the robot. **It also adds 2 false boxes on wood frames, so by the rule it is not switched on.** The code is on `wip/occlusion` behind two switches, both off.
- Nothing was merged into `barrels`. `barrels` has only the docs from this block. What runs on the robot is unchanged.
- No test frame was opened. No headline number changed.
- Tests: 220 on `barrels`, 222 on `wip/tm-seg`, 222 on `wip/occlusion`, 232 on `wip/eval-report`. All pass.

## 2. What I need from you

1. **Shoot step 3** (list in `DATA.md`, "Next shoot"). The `occl` shots at 25 / 50 / 75 % are now the real check for step 7.
2. **Live check of `tm seg`** (5 minutes with the robot):
   - `git checkout wip/tm-seg`, then from `barrels/live`: `simple_cli BarrelViewer`.
   - `tm seg`: the main window goes dark except the barrel pixels, and a second window `barrels seg` shows orange and blue on black.
   - `tm both`: the same, with boxes.
   - `tm boxes`: the second window closes within a second.
   - Repeat in `BarrelTracker`, and try `tm raw`. If the picture freezes: `restart img_thread`.
   - Tell me "tm seg works" and I merge it.
3. **Confirm the close-up fix live** while you are there (step 4, still open).
4. **Read section 3, say "understood"**, and I merge `wip/eval-report`.
5. **Read section 4, then decide** one of:
   - (a) keep the occlusion fix off until the wood front end exists (what the pre-registered rule says, my recommendation), or
   - (b) switch it on now and accept the two wood boxes.
   Either way say "understood" and I merge the branch with the switches as you chose.

Merge order when the time comes: `wip/tm-seg`, `wip/eval-report`, `wip/occlusion`. All three touch the HOW-IT-WORKS files, so I rebase each one; that is my job, not yours.

## 3. Walkthrough, step 6: the one table (`src/barrels/report.py`, `tools/report.py`)

**What it is for.** One command shows data set × scenario rows, a candidate and a baseline side by side, and the difference. No metric changed. Every number still comes from `eval_det` under the v2 rule.

**The command.**

- `python barrels/tools/report.py` compares today's detector with the v1 front end.
- `--cand-det stripe_w_min=0.25 --base-model default` compares a detector change against today.
- `--cand-model results/<x>/config.json --base-model default` compares a new color model against today.
- `--sets HOME,CAMPUS` limits the rows. `--out NAME` saves `report.md`, `.csv`, `.json` under `results/`.
- A full `python -m pytest` prints the same table at the end (about 12 s more; `BARRELS_NO_REPORT=1` turns it off).

**How it works, in the order the data flows.**

1. **Which frames.** Every frame with a box label. The frame name gives the set (robot, light, surface) and the scenario (the fourth field). A new session becomes its own group of rows with no code change.
2. **Train only.** Train frames and Dave's frames are scored. Test frames, ruler and horizon frames, and frames not yet in a split are left out. A guard raises an error before any image is opened if a test frame is in the list. The only way past it is typing `--split test`.
3. **An arm** is one side of the comparison: a color-model file plus the detector settings changed from the default.
4. **Scoring one frame.** Segment with the model, run the detector, compare the boxes with your boxes using the existing `eval_det.evaluate_frame`.
5. **Home is special.** The color model was learned from the home frames. Scoring them with that model would be grading its own homework. So each home scene is segmented by a model re-fit on the other home scenes. That is how the published 0.93 was made.
6. **One cell** of the table: found, missed, false; the median of box width ÷ true width; the median bottom-edge error in pixels. The last two are over found barrels only. The set row also has the score (mean of the orange and blue F1) and the count of false boxes on empty frames.
7. **The delta** is candidate minus baseline, column by column. A dot means no change.
8. **The ALL row** adds the counts of home and campus. It has no score, because no agreed headline pools sets. Dave's set is marked `*` and stays out of it.

**What the table says today.**

| set | frames | barrels | found | missed | false | width ratio | bottom error | score |
|---|---|---|---|---|---|---|---|---|
| HOME | 16 | 29 | 25 | 4 | 0 | 0.98 | 1.0 px | 0.93 |
| CAMPUS | 21 | 35 | 34 | 1 | 0 | 0.96 | 2.0 px | 0.99 |
| DAVE* | 12 | 34 | 11 | 23 | 2 | 0.96 | 1.0 px | 0.47 |

- All five misses on home and campus are in `occl` or `cluster` rows. The v1 front end misses the same four home barrels, so the color model is not the cause.
- `edge` rows are found but wide: width ratio 1.29 at home, 1.50 on campus. Worth a look later.
- One number to know: the table's default baseline is v1 pixels with **today's** detector, which scores 0.39 on campus. The published "v1 0.41" is v1 pixels with the **2026-11-05** detector. The tool reproduces 0.41 exactly when the baseline is given the old detector settings. Both figures were already in `EXPERIMENTS.md`.

I reviewed the helper's code and ran the tool myself. It also reproduces my step 7 number independently (campus 34 to 35 found with `stripe_w_min=0.25`).

## 4. Walkthrough, step 7: occlusion (`src/barrels/detector.py` on `wip/occlusion`)

### 4a. The reason log

`detect(mask, cfg, cam, log=[])` now fills the list with every candidate the detector dropped, the name of the test that dropped it, and the numbers it compared. Without `log` nothing is recorded. The boxes are identical either way, and a test checks that. This is what made the attribution below possible, and it is there for every future "why no box?" question.

### 4b. Why the barrels are missed

On the 37 train frames the detector misses 5 barrels. All 5 are occluded. There are 10 occluded barrels in total, so half are found. The 5 misses have two different causes.

| cause | barrels | what happens | step |
|---|---|---|---|
| Hidden at the side by a thing that is not a barrel | 1: campus `occl_02`, the blue barrel behind the robot | The stripe is found. It is 16 px wide. A barrel there is 53.6 px wide. The width test wants 0.4 × 53.6 = 21.4 px. Refused. | 7 |
| Behind a barrel of the other color | 4: home `occl_01`, `occl_02`, two in `cluster_01` | The back barrel's stripe has the same color as the front barrel's body. The two join into one patch. The patch is 28 px tall where a stripe should be 15. Refused for height. | 9 |

The first cause is what you saw live with Dave. A stripe is about 15 % narrower than its barrel, so "half the barrel showing" sits right at the 0.4 limit.

The second cause is the "mixed-color stacking" already listed in step 9. I did not touch it. One correction to step 9: `occl_02`'s stripe is not fully hidden, it is just narrow.

The one false box on home (`cluster_01`, with the adopted model) comes from the same stacking: a sliver of blue between two orange barrels is read as a stripe.

### 4c. The fix that was tried

The rule was written and committed before the run (`experiments/2026-11-11_occl_narrow_stripe/PREREG.md`). Two changes:

1. **`stripe_w_min` 0.4 → 0.25.** Why a quarter and not some other number: a stripe is about a quarter as tall as its barrel is wide, and the finder already refuses a stripe that is taller than wide. Below a quarter that test takes over anyway.
2. **Switch (h), `occl_body_side`.** A narrow stripe tells where the barrel is but not which side is hidden. The old rule: widen to a full barrel toward a barrel-colored neighbour, else centre on the stripe. With (h): first look at the body color joined to the stripe, above and below it. If it already spans most of a barrel, that span is the box. If not, widen that span by the old rule. On `occl_02` the robot's edge slants, so the blue body under the stripe shows almost the full width. The box overlap with your box goes from 0.51 to 0.68.

The acceptance conditions, written first: (1) no found barrel lost on home or campus, (2) no false box added there, (3) Dave's score not lower, (4) every box added on unlabeled frames is a real barrel by eye, (5) `occl_02` found.

### 4d. The result

| config | home found / false | campus found / false | Dave | `occl_02` |
|---|---|---|---|---|
| today | 25 / 1 | 34 / 0 | 0.47 | missed |
| 0.25 only | 25 / 1 | 35 / 0 | 0.49 | found, overlap 0.51 |
| 0.25 + (h) | 25 / 1 | 35 / 0 | 0.49 | found, overlap 0.68 |
| (h) only | 25 / 1 | 34 / 0 | 0.47 | missed |

Home here uses the adopted model on its own fit frames, so it is for comparing rows only. It is not the 0.93 headline.

Report-only widths: 0.35 and 0.30 do not find `occl_02`; 0.20 adds a false box on home. So 0.25 is not a lucky pick, it is where the case starts to work and before the damage starts.

The 8 boxes the fix adds, each looked at on a sheet:

| frame | what the new box is on | verdict |
|---|---|---|
| campus `occl_02` | the barrel behind the robot | real |
| Dave `speckle_snap_10` | the orange barrel in front | real |
| recording `r2_pan`, frames 34 and 35 | a blue barrel entering at the right edge | real |
| recording `r3_enter_leave`, frames 14 and 47 | an orange barrel entering at the right edge | real |
| wood `atwarm_wood_core_01` | a second box on half of an orange barrel, table included | **false** |
| wood `upmid_wood_core_01` | an orange box on a far blue barrel | **false** |

Conditions 1, 2, 3 and 5 pass. **Condition 4 fails on the two wood frames.** The rule said: if neither config passes, nothing is adopted. So the defaults are unchanged.

### 4e. My reading, and your decision

- On every set where the color model works (home, campus, Dave, the recordings) the fix only adds real barrels.
- On wood the color model already fails: the table itself reads orange and today's detector draws 61 boxes on those 25 frames. The two new false boxes are a symptom of that, and wood is the job of steps 8 and 10.
- Still, I wrote the rule before the run and it failed. I do not get to reinterpret it afterwards. That is why the choice in section 2 item 5 is yours.
- The frames that will settle it are your step-3 `occl` shots at 25, 50 and 75 %. One campus frame is thin evidence either way.
- (h) alone changes little: it moves 90 boxes on unlabeled frames by a median of 2 px on the recordings. It only earns its place together with the lower floor.

### 4f. What was not done

- No saved frame of the live miss with Dave exists. The match to `occl_02` is by reasoning, not by replay. If it happens again, `tm save` it.
- The other-color occlusion (4 of the 5 misses) is untouched. It is step 9.
- The headline sweep was not re-run, because no default changed.

## 5. Where everything is

| what | where |
|---|---|
| `tm seg` | branch `wip/tm-seg`, commit `75020c7` |
| eval table | branch `wip/eval-report`, commit `f4f77c2`; `tools/report.py`, `src/barrels/report.py`, `results/2026-11-11_eval_report/` |
| occlusion | branch `wip/occlusion`, commit `939065e`; `experiments/2026-11-11_occl_attribution/`, `experiments/2026-11-11_occl_narrow_stripe/` and the two `results/` folders of the same names |
| sheets to look at | on `wip/occlusion`, local only: `results/2026-11-11_occl_attribution/sheets/`, `results/2026-11-11_occl_narrow_stripe/sheets/` |
| log entries | `EXPERIMENTS.md`, three entries dated 2026-11-11 |
