# Pre-registration: the two paint checks inside the detector, measured everywhere (2026-11-27)

Written 2026-11-27 on branch `wip/adopt-checks` (from `barrels`), **before any run with a switch on**. Committed
before `harness.py` and `judge_all.py` are first run.

## The question

Tanush (2026-11-27): "what if we add the solid paint (and maybe label) checks to the detector in general?" The
experiment `wip/exp-bluer-geom` found two checks that tell near-barrel traps (the jar with an orange lid and a blue
label, the blue tin, the small figure) from real barrels, as a post-filter on boxes. Here they go into
`detector.py` as a last verify stage, and are measured on everything the detector is asked about:

1. Does either check, or both, cost a real barrel anywhere? (must be 0, or explained barrel by barrel with a picture)
2. Which boxes not on a barrel do they remove, and where?
3. Do they hurt the hard cases: partly hidden barrels, close-ups, far barrels, glare on the lid, barrels on glass?
4. Adopt both, one or neither, as plain code?

## The code (what changes in `detector.py`)

A stage 11, `drop_unlike_paint`, after `drop_single_reading`, and `paint_readings` (the three readings of one box).
Two switches in `DetConfig`, both **off by default**: `check_solid`, `check_label`; three numbers: `solid_min`,
`label_stripe`, `label_body`. With both switches off the stage returns its input untouched.

- **Solid paint** (`check_solid`): of the barrel-colored pixels (either color) in the box, the share whose 3 x 3
  neighbourhood inside the box is all barrel color (box edge replicated). Under `solid_min`: dropped, "speckle".
- **A label, not a stripe** (`check_label`): for a box read from a stripe, the stripe's height (10th-90th percentile
  of its rows with stripe color) over the stripe height its row predicts is over `label_stripe` AND the share of body
  color in the box's rows outside the stripe's rows is under `label_body`: dropped, "label". A box with no stripe is
  not asked.
- Every box is asked whichever rule drew it. A box whose row gives no barrel, or a reading that cannot be made, is
  never dropped. This is exactly the experiment's `checks.removes` on `stages.measure` (whole box, not the evidence);
  `harness.py --ref` checks it box for box on all 5435 masks against copies of the experiment's own code
  (`ref/checks.py`, `ref/stages.py`, unchanged from wip/exp-bluer-geom).

## The numbers (taken from the experiment, not chosen here)

The experiment's folds disagree, family by family, so the rule of the brief applies: the setting chosen on all eight
places.

- **P (primary)**: solid_min **0.40**, label_stripe **1.25**, label_body **0.6**. The choice on all eight places of
  the experiment's primary family G1 (B4 + checks); eight of its ten folds took exactly this; the bathroom fold took
  0.35 / 1.5 / 0.6, the glass fold 0.40 / 1.25 / 0.45. These are the defaults of the three numbers.
- **M (mild, reported beside)**: 0.35, 1.5, 0.6. The choice on all eight places of G2 (the fixed colors + checks),
  which is what the detector sees by default. Measured because the experiment's families disagree on which set goes
  with which color step. Nothing between or around P and M is tried.

Arms: **S** (solid only, P), **L** (label only, P), **SL** (both, P); **Sm**, **Lm**, **SLm** the same at M.

## The yardsticks (all train frames; no test frame is loaded, viewed, scored or listed)

- **H. The proof harness**, all 5435 masks (`harness.py`). At defaults: IDENTICAL BOXES ON EVERY INPUT (run before
  this plan: yes, and the reason logs identical too, against the collapse's second pass). Per arm: every box removed,
  by group, with its reason, rule and readings, and what it was before: on its barrel and found / box off / wrong
  color / second / on nothing. Masks from a train frame are scored against its hand boxes; the 3888 simulated scenes
  against their own true boxes (`scene_truth.json` of experiments/2026-11-26_slack, made at the tag). Found, lost
  (no box left on a barrel that had one), found → box off, boxes not on their barrel, per group.
- **J1. The standard judge, fixed colors** (`judge_all.py`): today's default against the default with each arm on.
- **J2. The hand thresholds**: per condition the median of its slider labels (as experiments/2026-11-26_judge, S3),
  without against with each arm.
- **J3. The contrast winner** (`wip/exp-contrast`, `candidate.py:detect_frame`, setting BEST), run unchanged with the
  checks inside every `detector.detect` call it makes: without against with each arm; and each against today's default.
- **E. The extreme conditions**: printed by every judgement, report only.

## The hard cases (question 3)

From the harness rows and the judgements: removed boxes that were on a barrel, by rule (stripe step whole / partly
seen, close-up, cap, half stripe, pair), by scene kind and hidden share (the simulated occlusion scenes), by the
barrel's expected width (far: under 25 px), and by place (the glass table: reflections; lamp-lit frames: glare on
the lid). The question of the brief, "does the check use the evidence or the whole box?": the whole box, as the
experiment did. Solidity counts barrel-colored pixels only, so table in a hidden barrel's box does not lower it;
the body share of the label check does fall with the table in the box. If a check hurts one of these, a fix is
proposed and measured **only in a dated addendum committed first**.

## Success line and the recommendation rule (fixed now)

A check at P is recommended for adoption as plain code when all hold:

1. J1 is not FAIL;
2. no real barrel is lost (found → missed or found → box off) on the ordinary train frames in J1, J2, J3, or in the
   harness groups made from train frames or the scenes; or each loss is explained barrel by barrel with a contact
   sheet as not a real barrel (a label error) — a real barrel lost by a check is a cost, and it blocks;
3. it removes at least one box that is not on its barrel somewhere (J1-J3 or H).

Losses in the extreme conditions are reported, barrel by barrel, and do not block alone (the parked conditions;
the experiment already saw the label check cost 2 barrels on the parked wood desk), but are named in the
recommendation. If P fails the rule for a check and M passes it, M is recommended for that check, and this is said
to be a choice between two pre-registered sets on these data. Neither passes: that check is not adopted.

## What I expect (written before the run)

- J1: NO CLEAR DIFFERENCE (the fixed colors make few trap boxes: the jar on the glass table, the pale-wood close-up);
  0 barrels lost at M; at P perhaps the striped blue barrel under the cool bathroom lamp if the fixed colors find it.
- J3: boxes not on their barrel 2.83 → about 2.2, nothing lost (as G3).
- H: the scenes are where a loss could hide. Hidden barrels keep their solidity; the label check could take a
  partly hidden barrel whose stripe reads tall (a front barrel's stripe merged) with little body in its box.
- E: the label check costs 1-2 barrels on the parked wood desk under the cool lamp.

## What was looked at before this was written (honesty)

The experiment's PREREG, ENTRY, summary and code (`fitgeo.py`, `checks.py`, `stages.py`). The proof harness at
defaults (IDENTICAL BOXES ON EVERY INPUT; no switch on). Nothing with a switch on was run on any input.

## Rounds

One round. A second round, or any fix, needs a dated addendum here, committed before it runs.

## Outputs

`results/2026-11-27_checks/`: `harness.md`, `harness.json`, `harness_removed.csv`; `judge_<candidate>_vs_<baseline>/`;
`judges_*.md`; `boxes_*.json` (not committed if large); `sheets/` (images, not committed). `ENTRY.md` in this folder.
