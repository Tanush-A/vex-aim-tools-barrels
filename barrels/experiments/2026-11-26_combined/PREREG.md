# Pre-registration: the two color-step winners together (2026-11-26, TODO E8)

Written 2026-11-26 on branch `wip/exp-combined`, **before any combination was run on a real frame**. Committed before
the first judged run of a combination. Train frames only: no test frame is loaded, viewed, scored or listed
(`judge.load_frame` refuses them). Nothing that runs by default changes: `detector.py` and the default color model
stay as they are. The combination is a new module that nothing calls (`src/barrels/combined.py`) and functions in
this folder.

## The question

Two color-step ideas passed the standard pass rule today, each alone, each leave one place out:

| winner | what it does | found, of 172 placements | per frame, of 307 | gained / lost | boxes not on their barrel |
|---|---|---|---|---|---|
| today's detector (fixed colors) | | 133.8 | 211 | | 1.9 |
| `nearmiss` (`B_partner_fit`) | a pixel just outside the range counts where the partner color says a barrel is | 147.5 | 249 | +38 / −0 | 3.6 |
| `selfcal` (`AB`) | a half-found barrel paints its own missing color; found barrels widen that frame's ranges | 147.6 | 248 | +37 / −0 | 2.2 |

1. Put together on today's collapsed detector, do they find more than either alone, without failing the clause on
   boxes that are not on their barrel? That clause is the binding one: `nearmiss` alone used +1.6 of the +1.85 allowed.
2. Do they find the same barrels? If one does the work of both, the answer is the simpler one, not the pair.
3. What does the best combination do on frames neither was judged on, and against the vendor detector?
4. What is still missed, and why?

## Step A, before anything else: each winner alone reproduces (`repro.py`)

Both winners were built on the detector as it was before today's collapse. The collapse changed no box, but it
renamed internals. What had to be ported:

- `nearmiss.py` uses one private function, `geometry.CameraModel._d_axis_from_point_row`. It was not renamed. No
  change to the module.
- `selfcal.py` uses `detector.detect` and `detector.DetConfig` only. No change to the module.
- One unit test of `nearmiss` compared its geometry with `detector._stripe_geometry`, which is now
  `detector.BarrelAt.from_stripe_row`. The test was ported. One unit test of `selfcal` says no other module may
  mention it; it now allows `combined.py`, which has the same guard of its own.

`repro.py` runs each winner's own `fit` through the judge on this branch and compares the judge's pages with the
ones committed on the winner's branch: totals, every place, every condition, the report-only conditions, every
barrel that changed, every frame whose boxes changed, and what each fold picked. **Result, before this file was
committed: see `results/2026-11-26_combined/repro.md` and the last section of this file.** A combination is only
run if both are identical.

## The candidates (five combinations, and the two winners alone; every one is reported)

All in `src/barrels/combined.py`; the judged functions are in `candidates.py`.

| name | what |
|---|---|
| `nearmiss` | the winner alone: its own `fit_partner`, untouched |
| `selfcal` | the winner alone: its own `fit_AB`, untouched |
| `nm_then_sc` | **Near-miss paint first, then self-calibration on that mask.** The near-miss mask and its boxes are self-calibration's first pass. Its seeds are looked for there. The near-miss boxes stay as they are; a second-pass box is added where no box is. When a seed widens the frame's ranges, the near-miss paint stays in the mask. |
| `sc_then_nm` | **The other order.** Self-calibration runs as it was judged. Its second-pass mask is then what the near-miss step takes as "strict": a color that a seed painted can be the partner. Today's boxes stay as they are; a box of the last pass is added where none of today's is. |
| `mask_union` | **The union of the two masks.** Each step alone on the fixed mask. The two masks are laid over each other and the detector runs once more. Today's boxes stay; a box of that pass is added where none of today's is. |
| `box_union` | **The one I think is cleanest.** Each winner alone, from start to end, exactly as judged. Then the boxes are merged: every self-calibration box stays (they hold every box of today's detector); a near-miss box is added where no box is. No step sees the other's paint. Each can be explained, tested and switched off alone. |
| `box_agree` | **A second reading.** Each winner alone. Today's boxes stay. A box that self-calibration adds stays only when the near-miss step, alone, drew a box of the same color on it. This asks whether the boxes that are not on a barrel are the same for both. |

"On a box" is everywhere the rule the counting and `selfcal.combine` already use: half of the smaller box inside the
other.

Three choices of structure, made by reasoning, before any run, and not varied:

1. Where the two steps paint one pixel in different colors (`mask_union`), self-calibration's color stays. Its seed
   passed a check on the photo. The near-miss paint has no such check.
2. In `box_union` self-calibration's boxes come first and near-miss boxes fill in. Reason: in their own judged runs
   self-calibration drew fewer boxes that are not on a barrel (2.2 against 3.6). This uses a known result.
3. Self-calibration's rule "a box of the other color on a kept seed is dropped" is kept in every way that has kept
   seeds.

## How every number is chosen

**No number is chosen for a combination, and no number is added.**

- In each fold (one place held out) each step gets the setting that **its own rule** picks on the other seven
  places, **for that step alone**: the near-miss step by `nm_common.choose` over its 65 settings (highest found
  minus 2 × boxes not on their barrel, no new box on a clean empty frame, no training place under its margin);
  self-calibration by its `candidates.choose` over its 8 settings (most found among those that do not break a box
  clause). Code: `candidates.py`, `fold_settings`.
- The five combinations share that one pair of settings per fold. A combination is never scored on the training
  places. So nothing about a combination is fitted, and there is nothing to overfit in the fold. The cost: the
  settings are the best for each step alone, not for the pair.
- Every other number belongs to one of the two modules and stays as the winner registered it.

## The judge

The standard pass rule, `barrels.judge`, leave one place out, on the 154 ordinary train frames (8 places, 172
placements). Margins as stored in `results/baseline/margins.json`: found better above +4.0 and worse below −10.92
placements; boxes not on their barrel worse above +1.85; any new box on a clean empty frame fails; boxes on empty
frames with clutter worse above +1.0; no place may drop by more than its own margin. No rule of my own for the
verdict.

`run.py` runs all eight detectors (today's, the two winners, the five combinations) in one pass over the frames
with `judge.run_many` and compares pairs with `judge.compare`. That is what `judge.judge(fit=...)` does for one
candidate. The final candidate is also run once through `tools/judge.py --cand-fit`, alone, as a check.

Two comparisons per combination:

1. **Against today's detector.** This is the verdict.
2. **Against each winner alone**, with the winner as the baseline and the same clauses and margins. This answers
   "is it worth having both?". Caution: the margins were measured around today's default, not around a winner. A
   verdict here is an indication.

## What counts as success

- **A combination works** when the judge says PASS against today's detector. That includes the binding clause:
  boxes not on their barrel may not rise by more than 1.85 over today's 1.9. A PASS under +6.0 placements is called
  WEAK. A PASS whose boxes rise by more than 0.85 is called "at the margin".
- **Which one is "the best combination"** (the rule in `run.py`, `pick`): among the combinations that PASS, the one
  that finds the most placements. Within 1.0 placement of it, the one with the fewest boxes not on their barrel.
  Within 0.25 box of that, the simpler one, in this order: `mask_union`, `box_union`, `nm_then_sc`, `sc_then_nm`,
  `box_agree`. If none passes, the same rule over the ones that do not FAIL, and it is said plainly that no
  combination passed.
- **It is worth having both** only when the best combination is PASS against **each** winner alone: more than +4.0
  placements over the winner, and nothing worse. Otherwise the registered answer is: **one winner is enough**, and
  the combination is not recommended, whatever its own verdict against today's detector.
- If one winner is enough, which one: the one with fewer boxes not on their barrel, unless the other finds more than
  4.0 placements more. By their own judged numbers that is `selfcal`.

## Predictions, written before any combination ran

- Both winners complete a barrel that has one color at full strength. I expect them to gain mostly the same barrels:
  30 or more of the 37 or 38 in common.
- `mask_union`, `nm_then_sc`, `sc_then_nm`: 150 to 153 placements. Boxes not on their barrel 3.6 to 4.2. The limit is
  3.78 (1.93 + 1.85). I expect at least one of them to FAIL on that clause.
- `box_union`: 150 to 152 placements, boxes about 3.9. It may FAIL by a fraction of a box.
- `box_agree`: 143 to 146 placements, boxes 2.0 to 2.3, PASS.
- No combination will be PASS against a winner alone (that needs +4.0 over 147.5). So I expect the registered answer
  to be "one is enough".
- Nothing new under the warm ottoman lamp and little under the warm bathroom lamp: neither color is strict there, so
  neither step has a start.

## Reported, never judged

- **C, the overlap.** From the two winners' held-out runs: the barrels each gains that the other does not, listed,
  with pictures, and why.
- **D, every box that is not on its barrel** for the best combination: frame, color, box, the object (from the
  picture). For each: whether today's detector, with the fixed colors, boxes the same object in that frame or in
  another light of the same arrangement; and what kind of check would remove it (shape, size for the row, a second
  reading). **No rule is tuned on these frames and none is run.** `box_agree` was registered above, before any
  picture, and is the only "second reading" that is tried.
- **E, the extreme conditions** (the orange wood desk under the lamp at six settings, the black table, the very dark
  ottoman; 77 frames): found, boxes not on their barrel, boxes on empty frames, per condition and together, for
  today's detector, each winner and the best combination. Each is scored by the settings picked on all the ordinary
  frames (the dark ottoman by the fold that left the ottoman out). And Dave's office frames (12, in no split, his
  boxes group touching barrels: indicative only).
  - **Were these frames looked at while the two methods were shaped? I checked before writing this, in the two
    PREREGs and the exploration scripts. Yes, as counts.** `nearmiss`: `PREREG.md` point 4 ("the extreme conditions
    in-sample for the same settings, found per frame 13 → 58"), `explore.py --extreme`, and `look_body.py` read the
    body, stripe and ground colors on the report-only frames too. `selfcal`: `explore0.py`, `explore1.py` and
    `explore2.py` run on the ordinary **and** extreme frames; the four in-sample tables its design list rests on
    have a row per extreme condition (`results/2026-11-26_selfcal/explore2_in_sample_v4.md`); a kept seed on the
    extreme empty frame `lampmid3_ottoman_neg_02` is named in its PREREG as a reason for `rel_margin` 1.0. Neither
    PREREG lists a picture of an extreme frame among the pictures looked at, and no number was chosen on them. So
    these frames are **not blind**: both authors saw the per-condition counts there while they decided the design.
    They are the nearest thing to a blind test on train data, and no more than that.
- **F, against the vendor.** The six places with vendor files (117 frames, 243 barrels, 108 placements; the
  accounting of `tools/report.py --vendor --places`, code `counting.py`): today's detector, each winner, the best
  combination and the vendor side by side, by place and in total: found (strict, per placement and per frame), found
  with the box off, missed, boxes on nothing. Ours are the held-out boxes of the judged run. The vendor's are the
  saved files. This is train data, and the methods were shaped on it.
- **G, what is left.** Every barrel the best combination does not find on the ordinary conditions, by cause, in
  this order: (1) hidden or cut by the frame (the label's flags `occluded`, `truncated`, `held`); (2) neither color
  painted by the fixed colors (under half of its body bands and under half of its stripe band, the bands of
  `selfcal.bands`); (3) touching another barrel (its hand box, grown by 2 px, meets another hand box); (4) a guard
  refused it (a seed candidate on it was refused, or the near-miss step found no band or slot on it although one
  color is painted); (5) the detector refused a well-painted barrel (in the final mask both its body bands and its
  stripe band are painted at least half, and there is still no strict hit). Each is checked on a contact sheet, and
  a cause is corrected by hand where the picture says otherwise, with a note.
- Run time per frame of every candidate (fixed numbers, one process, nothing cached).
- The fixed-number callable of each combination (`candidates.py`, `detect_<way>`): the two settings the winners
  offered. Judged, it is in-sample, and it is labelled so.
- Contact sheets, looked at: every barrel the best combination gains over the better winner; every barrel it still
  misses that is not hidden; every box that is not on a barrel.

## What I looked at before writing this (honesty)

- **Each winner's results are known to me**, in full: both `ENTRY.md` and `PREREG.md`, the judge pages of
  `B_partner_fit` and `AB` (by place and by condition, held out), the list of the 7 new boxes of `nearmiss` (3 on
  the jar label on the glass table) and the 1 of `selfcal`, what each fold picked, the in-sample number of
  `nearmiss` at its offered setting (152.8), `selfcal`'s table of what it still misses by seed.
- The four newest entries of `docs/EXPERIMENTS.md` (near-miss, self-calibration, the place ceiling, the light): so
  I know the per-place numbers of the hand thresholds, the oracle (163.2) and the vendor (83.3 of 108).
- `tools/report.py --vendor --places` for today's detector, printed once: today's and the vendor's counts by place
  and by condition, the vendor's on the extreme dark ottoman included.
- The code of both modules and of both experiment folders.
- Unit tests of `combined.py` on drawn pictures (one whole barrel, one barrel with a pale stripe).
- Step A: each winner alone on this branch, through the judge. Its numbers are the winners' known numbers.
- **Not seen:** any output of any combination on a real frame; any count, verdict or picture of a combination; any
  contact sheet of either winner (I have looked at no picture at all so far); any test frame.

## What would make me distrust the result

- Both winners were shaped while looking at all eight places. Leave one place out guards only the settings picked
  in a fold (two levels and an edge mode; three numbers). A combination inherits that. The verdict is optimistic by
  an amount that cannot be measured here.
- Seven candidates and ten more comparisons against the winners are judged. The judge called 2 of 12 changes that
  mean nothing. A lone PASS near a margin among these is weak evidence.
- A verdict within one unit of a margin, in either direction, is "at the margin" and is read with the list of
  barrels and boxes that changed.
- The comparison with the vendor is on train frames at six places.

## Outputs

`results/2026-11-26_combined/`: `repro.md` and `repro_<winner>/`; one folder per candidate (`judge.md`,
`judge.json`, `changes.csv`); `<way>_vs_<winner>/`; `boxes.json`, `chosen.json`, `timing.json`, `summary.md`,
`summary.json`; the tables for C to G; `sheets/` (images, not committed). `ENTRY.md` in this folder: the
experiment-log entry. A second round, if any, gets a dated addendum here, committed before it runs.

## Step A result (filled in before the commit, before any combination ran)

`python barrels/experiments/2026-11-26_combined/repro.py`, on this branch, finished before this file was committed.
**Both winners reproduce exactly** (`results/2026-11-26_combined/repro.md`):

| winner | found, placements | per frame | boxes not on their barrel | gained / lost | compared with its committed pages |
|---|---|---|---|---|---|
| `nearmiss` | 133.80 → 147.47 (committed 147.47) | 249 (249) | 3.57 (3.57) | 38 / 0 (38 / 0) | 0 differences in the totals, 8 places, 17 conditions, 8 report-only conditions, 98 changed barrels, 11 frames with changed boxes |
| `selfcal` | 133.80 → 147.55 (committed 147.55) | 248 (248) | 2.18 (2.18) | 37 / 0 (37 / 0) | 0 differences in the totals, 8 places, 17 conditions, 8 report-only conditions, 87 changed barrels, 2 frames with changed boxes |

What each fold picked is identical too: near-miss `pc:5,5,pred` in every fold but the gray table's (`pc:5,5,strict`)
and the ottoman's (`pc:5,4,pred`); self-calibration `rel_margin` 1.0, `hue_move_max` 6, `flood_max` 0.03 in every
fold but the ottoman's (`flood_max` 0.01). So the combinations below run with these settings, place by place.

---

## Addendum, 2026-11-27: the third winner (the stripe by color difference). Written and committed before any run of it on this branch

**Why.** A third color-step idea finished after the two-way runs above: `wip/exp-contrast` (`src/barrels/contrast.py`,
`experiments/2026-11-26_contrast/`). A band that is bluer (or redder) than what is right above AND right below it, at
the size its row predicts, is a stripe; that barrel's own two colors are read there and painted; the new boxes are
ADDED to today's boxes. Its held-out judged result, as committed on its branch: PASS, 133.8 → 155.3 of 172
placements (+21.5), 275 per frame, 64 gained, 0 lost, boxes not on their barrel 1.93 → 2.83, no box on an empty
frame. That is more than my best two-way combination (`mask_union`, 152.8), so the question of this experiment
changes: **which single method does most of the work, and does anything add to it above the noise?**

**What I know before this addendum (honesty).** All the two-way results above, judged, including C to G for
`mask_union` and its contact sheets. Contrast's `ENTRY.md` (its judged numbers by place, its five candidates, its
caveats: its four guard thresholds and three floors were read off an in-sample table of all eight places; painting
into the fixed mask in one run FAILS on boxes while adding to today's boxes passes), its `PREREG.md`, and its code.
I have not run contrast on any frame. The two-way results stay as they are.

**What was ported.** Two of contrast's unit tests called `detector._stripe_geometry`, now
`detector.BarrelAt.from_stripe_row` (same reading). `contrast.py` itself uses no private name of the detector.

**Step A again (`cn_picks.py`, in a process of its own).** Contrast's own `table.py:fit` (family C1) through the
judge on this branch, compared with its committed pages (`results/2026-11-26_contrast/judge_C1_add_guards/`) and
its committed fold picks. Then the setting its rule picks for each held-out place, on the other places, alone, is
written to `results/2026-11-26_combined/cn_chosen.json`. If contrast does not reproduce exactly, nothing below is
run and that is reported.

**The new candidates** (`barrels.combined.WAYS3`; no new number; contrast always in its own judged "add" mode,
`combined.contrast_on`: the base's boxes stay, a candidate whose stripe point is in one of them is left alone, the
rest paint their own colors where the base mask is empty, the detector runs once more, a new box is added where no
base box is):

| name | what |
|---|---|
| `cn_alone` | contrast alone, on today's mask and boxes, built from `barrels.combined` (must equal contrast's own judged pages) |
| `cn_on_nm` | near-miss alone, then contrast added on top of its mask and boxes |
| `cn_on_sc` | self-calibration alone, then contrast added on top of its second-pass mask and boxes |
| `cn_on_all` | all three: `mask_union`, then contrast added on top of its mask and boxes |
| `cn_box_nm` | near-miss alone and contrast alone, each from start to end; boxes merged, near-miss first |
| `cn_box_sc` | self-calibration alone and contrast alone; boxes merged, self-calibration first |
| `cn_box_all` | `mask_union` and contrast alone; boxes merged, `mask_union` first |

**How every number is chosen.** As above: in each fold each component gets the setting its own rule picks on the
other places, for that component alone. Contrast's rule is its `table.choose` over its 48 settings of family C1
(allowed = not FAIL against today on the training places; the highest found minus boxes not on their barrel; ties
to the most cautious). The report-only places get the picks made on all ordinary places. Nothing is chosen for a
combination.

**The comparisons** (`run3.py`, one pass, `judge.run_many` and `judge.compare`):

1. every new candidate against today's detector (the verdict);
2. every combination against **contrast alone** as the baseline, same clauses and margins;
3. `nearmiss`, `selfcal` and `mask_union` against contrast alone (from the boxes of the first judged run), for C.

**The rule for the answer, written now.** The owner wants the simplest thing that works. **Contrast alone is the
answer**, unless a combination is PASS against today's detector AND PASS against contrast alone (more than +4.0
placements over contrast alone, and nothing worse by more than the margins). Among such combinations: the most
found; within 1.0 placement, the fewest boxes not on their barrel; within 0.25 box, the simpler, in this order:
`cn_box_sc`, `cn_box_nm`, `cn_on_sc`, `cn_on_nm`, `cn_box_all`, `cn_on_all` (two components before three; a box merge,
where no step sees another's paint, before one on top of another). The caution about the margins (measured around
today's default, not around contrast) holds for comparison 2.

**C, D, E, F, G** are then reported for the answer (and, beside it, today, each winner and `mask_union`): the overlap
of all three winners (which barrels each finds that the others do not); every box of the answer that is not on its
barrel; the extreme conditions and Dave's frames; the vendor table; what is left, by the same causes.

**Predictions, written now.** Contrast reaches nearly every barrel the other two reach (it needs no strict color):
of the 50 barrels per frame the other two gain together, contrast alone finds 45 or more. So every combination
gains less than +4.0 over contrast alone, and contrast alone is the answer. Boxes: the combinations that hold
near-miss add its jar boxes on the glass table (about +0.8 per arrangement over contrast alone).
