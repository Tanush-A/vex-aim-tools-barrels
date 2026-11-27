# EVAL.md — how the detector is scored

**Version:** v1 (2026-10-14) · v2 detection rule 2026-11-02 · one-table splits 2026-11-03 · width ratio reported 2026-11-09 (a reporting addition, not a rule change) · two planned test looks 2026-11-09 (`DECISIONS.md`) · counting per placement, a misplaced box counted once, the never-regress check with a margin, the standard pass rule 2026-11-26 (how results are counted and judged; the v2 rule itself is unchanged). Foundation doc — the rules change only via a logged decision.

## Now — the rule in five lines (2026-11-09)

1. **Truth** = one box per physical barrel, full barrel as if occluders were transparent, clipped to the frame (`DATA.md`).
2. **A predicted box is correct** when it has the same color, overlaps the true box with **IoU ≥ 0.5**, and its bottom edge is within **max(3 px, 10 % of the true height)**. Greedy class-aware matching, highest IoU first. Every true barrel counts (occluded, truncated, held).
3. **Score** = mean over the two colors of F1 (precision and recall pooled over frames). Reported next to it: matched IoU, bottom-edge error (px and fraction), **box width / true width** (median and worst; the IoU match alone passes a box 15 % too thin), count error, color confusions.
4. **Negatives:** any box on a negative frame is a false positive; a box on a *clean* negative (no orange/blue clutter) **disqualifies** the config.
5. **Splits:** train = everything but the test frames; **test (HOME 5 + CAMPUS 10 + wood ladder 27 + black 5, since 2026-11-16) is looked at only when planned in advance** — this week twice, `TODO.md` 9b and 10b. Tuning uses leave-one-scene-out over the train frames; selection rules are written down before a sweep runs.

**The one table** (2026-11-11; presentation only, the rule above is unchanged): `python barrels/tools/report.py` prints data set × scenario rows with found / missed / false / width ratio / bottom error for a candidate and a baseline side by side and the difference, the headline score per data set and the clean-negative disqualifier; train frames only (test frames are refused unless `--split test` is given for a planned look). `--help` shows how to choose the two arms. Code: `src/barrels/report.py`.

**The vendor comparison and the never-regress check** (2026-11-18; reporting and checking tools, the rule above is unchanged): `python barrels/tools/report.py --vendor` scores the robot's built-in detector from the boxes saved with each frame, by rule 2 against the same labels, on the frames that have a vendor file, and prints two looser counts next to the strict ones (found by overlap alone; found by position), which are not the score. `python barrels/tools/report.py --gate` compares a run with a stored baseline (since 2026-11-26 with a margin, next paragraph). Both: `HOW-IT-WORKS.md` §4.

**Since 2026-11-26** (branch `wip/measure`, after the review; awaiting the walkthrough; sections "Counting what was shot" to "The standard pass rule" below). Rule 2 is unchanged and is now called **strict**. Four things were added around it:

1. **Every placement counts once.** A placement is one barrel in one arrangement; shot under five lamp settings it is still one, and it counts the share of its lights in which it is found. Tables are by **place** (table and room) and say how many placements they rest on. `python barrels/tools/report.py --places`.
2. **A misplaced box counts once.** Beside strict: each barrel is found / found with the box off / missed; each box is on its barrel / wrong color / a second box / on nothing. A box is *on* a barrel when at least half of the smaller of the two boxes lies inside the other.
3. **The never-regress check has a margin.** A protected set (home, campus, the glass table, pale wood, the ABP white occlusion set, the bathroom under the cool lamp) fails only when its total is worse than the baseline by more than a change that means nothing moves it. A new box on a clean empty frame still fails outright.
4. **One pass rule for every experiment:** `python barrels/tools/judge.py` gives PASS, FAIL or NO CLEAR DIFFERENCE from written clauses whose margins are measured ("The standard pass rule (2026-11-26)" below).

The vendor counts as finding every barrel on the two white tables that have no vendor file (Tanush, 2026-11-26): an **assumed** row, marked as such, never inside a measured total.

Commands: `python barrels/tools/eval_boxes.py --pred DIR --split train --gt-boxes --rule v2`; the experiment scripts call `eval_det.evaluate_frame(..., rule="v2")` directly. Code: `src/barrels/eval_det.py`.

Everything below is the full statement and the record.

---

## Counting what was shot (2026-11-26)

Proposed on branch `wip/measure` after the review of the measurement; the decisions behind it are Tanush's of 2026-11-26 (`DECISIONS.md`). Code: `src/barrels/counting.py`. Numbers: `results/2026-11-26_measure/summary.md`.

- A **place** is a table in a room (`data/conditions.json`). An **arrangement** is one scene at one place: the frames `{scene}_{nn}` of that place, one per light. A **placement** is one barrel in one arrangement. It is the same physical barrel under every light.
- **A placement counts once.** Shot under k lights and found under j of them, it counts j / k. A total adds these shares.
- Why. The boxes of a scene were copied across its lamp settings, and every copy counted as a barrel. The "243 train barrels" of the new ordinary conditions are 108 placements in 47 arrangements at 6 places. On the glass table one barrel had five votes.
- The count per frame is still printed beside it ("raw", "per frame"). It is the old number and nothing about it changed.
- Every table says what it rests on: lights, frames, barrels, placements.
- Which label box is which placement is read from the labels alone. In every light a box takes the number of the same-colored box it overlaps most in the first frame of its arrangement. Two lights of one arrangement that do not hold the same barrels are an error, not a number.
- Boxes that are not on their barrel are counted the same way: once per arrangement. A tin that gets a box under each of five lights is one box.
- No winner is named for a single condition. Most conditions are 15 placements at one place.

## A misplaced box counts once: the second accounting (2026-11-26)

The strict rule (rule 2: same color, IoU ≥ 0.5, bottom edge within 10 % of the height) is kept and is always printed first. Under it a box that sits on a real barrel of the right color but fails the rule, usually by its bottom edge, was charged twice: the barrel was a miss and the box was a false box. The second accounting, printed beside strict, charges it once.

- Each true barrel is **found** (a strict hit), **found, box off** (a box of its color is on it and fails the strict rule) or **missed**.
- Each box is **on its barrel** (a strict hit, or the one box of a "box off" barrel), **wrong color on a barrel**, a **second box on a barrel**, or **on nothing**.
- Boxes on empty frames are "on nothing". They are also counted on their own, and clean empty frames apart, as before.
- **On a barrel** means: at least half of the smaller of the two boxes lies inside the other. One definition, the same for our boxes and for the vendor's.
- The order: the strict hits are taken first, exactly as before, so "found" is always the strict number. Then, among what is left, a box of the same color that is on a barrel takes it, highest overlap first, one box per barrel. A box still left is a second box, a wrong color or on nothing.

Why this test for "on a barrel", and not one of the two looser counts the table already had:

- *Overlap (IoU ≥ 0.5, bottom not checked)* still asks for a box around the whole barrel. A box around the visible half of a hidden barrel fails it and stays "a miss plus a false box". That is the double charge this accounting removes.
- *Position (centers at most half the true width apart)* depends on the true box's width, so it gets tighter for a barrel the frame cuts, and a pair can pass the strict overlap and fail it.
- *Half of the smaller box inside the other* has no unit, treats both boxes alike, and every pair with IoU ≥ 0.5 passes it. So the states are nested: strict hit, on the barrel, not on it. Its weak point: a small box that lies inside a barrel's box counts as on it wherever it sits. Only one box per barrel gets that; any further one is a second box.

What it changes on today's train frames (new ordinary conditions, frames with vendor files): the vendor's 30 "false boxes" are 23 boxes on a barrel that fail the strict rule and 7 boxes on nothing, all 7 on empty frames. Our 7 are 2 and 5. With "position" as the test instead, not one frame changes; with "overlap", 5 of the vendor's 23 fall back to "miss plus box on nothing" (`results/2026-11-26_measure/sensitivity.md`).

## The vendor on the white tables: assumed (2026-11-26)

The home and campus frames have no vendor file. Decision, Tanush 2026-11-26: on a white table under window or overhead light the vendor counts as finding every barrel. The conditions are marked `vendor_assumed` in `data/conditions.json`.

- In the vendor comparison these are rows of their own, marked ASSUMED, with a star on every assumed number.
- The assumption says nothing about the vendor's boxes there. Those columns are empty.
- A measured total never holds an assumed frame. The total that does says "ASSUMED" in its name.
- As soon as such a condition has one vendor file, it is measured and the mark is ignored.
- The one white table where the vendor was measured is the ABP occlusion set: 24 of 32 strict, 3 more with the box off. It is a harder set than home or campus, and it is the only check on the assumption that exists.

## The noise floor (2026-11-26)

How much do the counts move under a change that means nothing? `python barrels/experiments/2026-11-26_noise_floor/run.py`; plan and addendum in its `PREREG.md`; numbers in `results/2026-11-26_noise_floor/summary.md`.

- **The changes.** The fixed color model with one number moved one step: each hue edge by one unit, each saturation floor by three, the brightness floor by two (14 neighbours). And 12 seeded moves of several numbers at once. The detector and the labels do not change.
- **At one condition** (about 15 barrels): most neighbours change nothing (median 0). The 90th percentile is 0 barrels for one step and 2 for joint moves. The worst case is 6.
- **At one place:** median 0, 90th percentile 0.33 placements, worst case 6 (one step); joint moves 0.22 / 1.33 / 6.
- **Over the ordinary conditions together** (172 placements): one step moves found by 0.67 at the median, 3.58 at the 90th percentile, 6.20 at most. Joint moves: 4.59 / 8.78 / 10.92.
- **It is one-sided.** Of the 26 neighbours 15 lose found and 8 gain. The largest loss is 10.92 placements, the largest gain 4.00. The fixed model was picked because it scores well, so a small move mostly hurts it.
- **One place sits on a threshold edge:** the ABP gray table. Orange hue low 3 → 4 costs it 6 of 16 placements; 3 → 2 gains it 4.
- **Boxes that are not on their barrel** move by up to 1.85 (counted once per arrangement). **Boxes on empty frames with clutter** by up to 0.6. **No neighbour, of 38, puts a box on a clean empty frame.**
- **A margin** is the largest change, in that direction, that any of the 26 neighbours produced at that level, and never less than one whole unit. They are stored in `results/baseline/margins.json`. The script is re-run when the default color model or detector changes.
- **Checked on 12 joint moves the margins had never seen:** the pass rule called 2 of 12 (one PASS, one FAIL); none failed the never-regress check.

## The never-regress check, with a margin (2026-11-26)

`python barrels/tools/report.py --gate`. Tanush, 2026-11-26: never-regress was meant as a general principle, not a strict rule. The first version (2026-11-18) failed when any scenario row of home or campus lost one barrel or gained one false box. One hue unit does that.

- **Judged on the total of a protected set**, not on its rows. Found = strict, every placement once. A box on its barrel that fails the strict rule is not a false box.
- **A protected set fails** when its found is lower than the stored baseline's by more than its margin, or its boxes that are not on their barrel are higher by more than its margin.
- **The margins** (drop in found / rise in boxes): HOME 1.00 / 1.00, CAMPUS 1.00 / 1.00, GLASS 1.00 / 1.00, PALEWOOD 1.00 / 1.00, ABPWHITE 1.00 / 1.00, BATH-COOL 5.00 / 1.00. Each is the largest change a neighbour produced in that set, at least one whole unit. The bathroom under the cool lamp has 5 because one hue unit of the blue range costs it 5 of 15.
- **The protected sets** (`results/baseline/protected.json`): home and campus as before; new, the conditions we already handle: the glass table (five lights, one set, 15 placements), pale wood, the ABP white occlusion set, the bathroom under the cool lamp.
- **Clean empty frames stay strict:** a new box on a clean empty frame fails the check, in any set. The noise run gives no reason to loosen it: none of 38 neighbours drew one.
- **Empty frames with clutter get a margin:** their boxes, once per arrangement and over all train sets, may rise by 1.00.
- **Every barrel and every box that changed is listed**, in every set, pass or fail. A set that is lower inside its margin is named in the result line.
- **The stored baseline** holds one line per frame (the state of every barrel and box), so the list can name the barrel. `--save-baseline` refuses a run that is lower anywhere, even inside a margin, unless `--force` is given. So the reference cannot slide down one margin at a time.
- On today's defaults the check passes with nothing changed.

## The standard pass rule (2026-11-26)

One rule for every experiment: a color-step idea, a detector idea, a whole new pipeline. The tool is `python barrels/tools/judge.py` (code: `src/barrels/judge.py`). No experiment writes its own pass rule any more. Earlier rules were tighter than the noise: one barrel is about 0.03 of a condition's score, the rules allowed 0.02, and hand-set thresholds that found 70 more barrels failed.

**What is compared.** A candidate against a baseline (today's default unless said otherwise), both run on the ordinary train conditions: 154 frames, 17 conditions at 8 places, 172 placements. The extreme conditions (the black table, the wood lamp ladder, the very dark ottoman) are run and printed, never judged. Test frames are refused before any image is opened.

**The clauses.** Candidate minus baseline. Found is the strict rule, every placement once. Boxes are counted once per arrangement.

| # | what | worse when | better when | where the number comes from |
|---|---|---|---|---|
| 1 | found, all ordinary places together | down by more than **10.92** placements | up by more than **4.00** placements | the largest loss and the largest gain among the 26 changes that mean nothing |
| 2 | found, place by place | down at one place by more than its margin: home white 1.00, campus 1.00, ABP gray 6.00, bathroom floor 1.25, glass 1.00, ottoman 2.34, pale wood 1.00, ABP white 1.00 | (not used) | the largest drop at that place, at least one placement |
| 3 | boxes that are not on their barrel (on nothing, a second box, the wrong color) | up by more than **1.85** | down by more than 1.00 | the largest rise; for "better" the floor of one box |
| 4 | boxes on empty frames | any more on clean empty frames than the baseline has; on ones with clutter, up by more than **1.00** | (not used) | no change that means nothing drew a box on a clean empty frame; with clutter the largest rise was 0.6, so the floor |

**The verdict.**

- **FAIL**: any clause says worse.
- **PASS**: no clause says worse and clause 1 says better. Or: no clause says worse, clause 3 says better, and found is not lower.
- **NO CLEAR DIFFERENCE**: everything else. It does not mean "no effect". It means the change is not larger than what one hue unit does.

**Why clause 1 has two numbers.** A change that means nothing loses up to 10.92 placements and gains at most 4.00, because the fixed model was picked for scoring well. A gain is compared with the largest such gain, a loss with the largest such loss. With one number for both (10.92), a candidate would have to recover 29 % of everything missed today to count as better.

**A candidate with fitted numbers is judged leave one place out.** The caller gives a function `fit(train_stems, held_place)`. For each place it is called with the ordinary train frames of the other places, and the detector it returns is run on the held-out place only. The same clauses, on held-out results.

**What it prints and saves.** Per place and over all places, for the baseline and the candidate: found per placement and per frame, found with the box off, missed, the boxes that are not on their barrel, the boxes on empty frames; the same per condition; the extreme conditions; every barrel gained and lost by name; each clause with its numbers; the verdict. Pages: `results/<date>_judge_<name>/judge.md`, `judge.json`, `changes.csv`.

**What the rule said in its sanity checks** (`experiments/2026-11-26_judge`, written first; `results/2026-11-26_judge/summary.md`):

| candidate | found, placements | found, per frame | boxes not on their barrel | verdict |
|---|---|---|---|---|
| today's detector against itself | 133.8 → 133.8 | 211 → 211 | 1.9 → 1.9 | NO CLEAR DIFFERENCE, nothing changed (required) |
| the 14 one-step changes, the 12 joint moves | −10.9 to +4.0 | | | all 26 NO CLEAR DIFFERENCE (by construction: the margins come from them) |
| 12 more joint moves the margins had never seen | −9.3 to +5.4 | | | 10 NO CLEAR DIFFERENCE, 1 PASS (+5.4), 1 FAIL (boxes +2.0) |
| Tanush's hand thresholds, per condition (in-sample) | 133.8 → 156.8 (+23.0) | 211 → 281 | 1.9 → 1.5 | **PASS** (required) |
| "blue follows the light", light read from the whole frame, leave one place out | 133.8 → 139.7 (+5.9) | 211 → 233 | 1.9 → 3.1 | **PASS** |
| the same, light read above the horizon gate, leave one place out | 133.8 → 137.0 (+3.2) | 211 → 222 | 1.9 → 2.9 | NO CLEAR DIFFERENCE |

Read the fifth row with care. Its gain, 5.9 placements, is 1.9 above the margin, and one of the 12 unseen changes that mean nothing gained 5.4 and passed too. With one margin for both directions, as first registered (10.92), it is NO CLEAR DIFFERENCE. The gain is all at two places with warm light: the bathroom floor (+4.2 of 15) and the ottoman (+1.7 of 15).

**What it cannot do.** It sees 172 placements at 8 places. A gain under 4 placements is not visible to it. A loss of up to 6 placements at the ABP gray table is not, either: that place sits on a threshold edge. On changes that mean nothing which it had never seen, it called 2 of 12; so a PASS less than about 1.5 placements above the margin is weak. The margins belong to today's default; when the default changes, the noise floor is measured again. A verdict that sits within one unit of a margin is "at the margin" and should be read with the list of changed barrels.

## Detection metrics (v2, decided 2026-11-02 — `DECISIONS.md`)

Ground truth = one **box per physical barrel** (`DATA.md`, box labels): the full barrel as if occluders were transparent, clipped to the frame, with flags. A prediction is a `Barrel` (color, box in 640×480).

- **A box is correct** when it has the same color as a ground-truth box, overlaps it with **IoU ≥ 0.5**, **and** its bottom edge is within **max(3 px, 10 % of the ground-truth box height)** of the true bottom edge. Both conditions must hold. Rationale: the bottom edge is what the world map will use; a tenth of the height is a few pixels on a far barrel and ≈ 15 px on a near one. (Tanush 2026-11-02: can be adjusted later, via a logged decision.)
- **Matching:** greedy, class-aware, among eligible pairs (both conditions), highest IoU first; deterministic. Unmatched predictions are false positives, unmatched ground truth false negatives.
- **Every ground-truth barrel counts.** Occluded barrels are scored on their inferred full box (Dave 2026-10-30), truncated barrels on their clipped box, held barrels like any other. Nothing is "difficult"/ignored any more. Flags are used only to **report** errors by case (bottom seen vs `bottom_estimated`, occluded, truncated, held).
- **Per class:** precision, recall, F1 under the rule above, pooled over frames (micro). **Primary = mean of the two F1s.**
- **Negative frames** (no barrels): their false detections count as FP in the pooled score and are listed per frame. A false barrel on a negative frame that contains **no orange or blue clutter** (`clean: true` in the label file) **disqualifies** the config — a frame with nothing barrel-like in it must come back with nothing drawn.
- **Reported alongside:** matched-pair IoU; bottom-edge error (px, signed, positive = predicted lower; and as a fraction of box height), split by whether the labeler saw the bottom (`bottom_estimated` boxes are themselves a guess); barrel-count error per frame; color confusions (class-agnostic IoU matches with the wrong color).
- **Aggregation:** per condition (light × surface), per arrangement (scene tag), ALL, and — once a second table exists (v2.1) — **separately for the unseen table** (below). Per-image numbers in the results folder.
- **Floor:** the connected-components baseline (`detect_cc.py`), never tuned, re-scored under this rule.
- **Implementation (since 2026-11-03):** `src/barrels/eval_det.py` (`evaluate_frame(..., rule="v2")`, `match_best_first`), `tools/eval_boxes.py --pred DIR --rule v2`. The v1 rule (IoU only, occluded/truncated truth ignored) stays the tools' default so every earlier number reproduces; the numbers we report are v2. The 15 mm loose criterion and the projected/measured ground errors stay in the code for the world map later; they are not part of the v2 score.

### v2 splits

- The 21 v1 frames keep their split: the 16 pool frames → train, the locked 5-frame test stays test (this also keeps the v1 pixel test clean if the color ranges are re-fit).
- New v2 frames are assigned **at import, before any method sees them**, by `tools/make_splits.py --v2 --filter <robot>_<light>_<surface>` (`splits.assign_holdout_per_scene`): within the session, **one frame per scene tag that has ≥ 2 frames goes to test**, the rest to train; dev stays empty. Tuning uses cross-validation that holds out whole scenes (as v1).
- **A set where one arrangement is shot under several lights** (the wood lamp ladder, 2026-11-16; `DECISIONS.md` 2026-11-16): the unit of assignment is the **arrangement** `{surface}_{scene}_{nn}`, not the frame. All lights of an arrangement go to the same split (`make_splits.py --v2 --by-scene`, `splits.assign_holdout_by_scene`); one arrangement per scene tag that has ≥ 2 arrangements goes to test. Otherwise the same barrels in the same places would be in train under one lamp setting and in test under another, and the test score would be inflated. Cross-validation folds on such a set hold out whole arrangements too.
- **v2.0 has one table** (decided 2026-11-03, timeline). The **unseen table** — a whole table × light session used for nothing but the final evaluation — is the v2.1 generalisation check, assigned the same way when that data is shot.
- Calibration frames (`calib`, `ruler`, `horizon`) are geometry-only and in no split.
- Selection rule as v1: primary metric; differences < 0.02 → simplest; at most two coordinate passes; test evaluated once per milestone with one pre-chosen config.

### The `measured` split (deferred 2026-11-02)

Defined 2026-10-28 for ground-position error in mm; **not used in v2**, which outputs boxes only. The known-distance `calib` frames serve geometry calibration instead. Revisit when the world map comes back into scope.

## Splits

- A **held-out test set is fixed early and never used for tuning.** No threshold fitting, no parameter sweeps, no "just checking" against test. It is evaluated once per milestone, with one pre-chosen config.
- **v1 (decided 2026-10-19):** test = 5 frames (`core_04, edge_02, far_01, neg_03, touch_01`), locked in `data/splits.json`. **Tuning uses leave-one-scene-out cross-validation over the 16 pool frames** (one fold per scene tag; a model never sees its held-out scene). The dev split is empty. `top_01`/`topstripe_01` are in the pool but excluded from the headline score (out of v1 scope); they are still predicted and reported.
- **Selection rule (pre-registered):** primary = mean of pooled orange and blue IoU over in-scope positive pool frames; disqualify any config with negative-frame FP rate > 0.5 % for either class; differences < 0.02 are "no difference" unless consistent in sign across ≥ 6 of 7 positive folds, then prefer the simpler setting; at most two coordinate passes.
- Split assignment is recorded in `DATA.md` and committed. New captures get assigned when added, before any method sees them, and existing assignments never move.
- Splits stratify by condition (don't put all warm-light frames in test); folds never split frames of one scene.

## Protocol

1. Every evaluation runs from a committed experiment script in `experiments/` with an explicit config (thresholds, priors, split).
2. Outputs go to `results/<date>_<name>/`: metrics table (CSV or MD), per-image numbers, and the debug previews for qualitative review. Big artifacts are gitignored; keep the small summary tables.
3. The results table + takeaway are logged in `EXPERIMENTS.md` immediately.
4. Comparisons between methods use the **same split and the same label version**. If labels are re-done, re-run the baselines.

## Implementation

`src/barrels/eval.py` (counts, metrics, per-condition aggregation, result tables), `src/barrels/splits.py` + `tools/make_splits.py` (fixed test set + pool in `data/splits.json`; `--test-only N` locks test once), `src/barrels/cv.py` (leave-one-scene-out driver, sweeps), `tools/eval_masks.py` (score a folder of predicted masks on a split → `results/<date>_<name>/`), `src/barrels/viz.py` (PROBLEM.md output images, debug sheets).

## Infrastructure correctness

Metric computation, mask IO, and label parsing have **unit tests** (`barrels/tests/`) — eval numbers are only meaningful if the harness is right. Algorithms themselves are judged by these eval numbers, not by unit tests.

## Per-pixel metrics (v1, how the first front end was judged; history)

Per-pixel, computed per class (**orange**, **blue**) against the ground-truth masks (`DATA.md` label format). **Stripes count as their own color:** the orange stripe of a blue barrel is labeled and scored as orange, the blue stripe of an orange barrel as blue — matching `PROBLEM.md`.

- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **IoU** = TP / (TP + FP + FN)

Rules:

- Pixels labeled **255 (ignore)** — glare/uncertain — are excluded from all counts.
- Report **per condition** (surface × lighting × scene tag, from the filename convention in `DATA.md`), plus an overall aggregate. A method that only works on one table or one lamp must be visible as such.
- Aggregate = micro-average (pool pixels across images within a condition). Also report per-image numbers in the results folder so outlier frames are findable.
- **Negative frames** (`neg` scene, no barrels): precision/recall/IoU are undefined when a class is absent, so report instead the **fraction of pixels flagged** per class (false-positive rate), target ≈ 0. Report it per condition like the other metrics. Negative frames are excluded from the IoU aggregates and listed separately.

