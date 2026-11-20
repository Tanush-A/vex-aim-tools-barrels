# Pre-registration: the occlusion work combined (one branch, one before-and-after)

Written 2026-11-19 on branch `wip/occl-combined`, after the merge commit 7292004 ("Merge wip/damage-realism,
wip/stencil, wip/occl-vertical and wip/occl-pin onto wip/detector-occl") and **before any part of the battery was run
on the combined code**. What had been run when this was written: the unit tests of all five branches together (637
pass). Nothing else: no scorecard scene, no eval table, no damaged mask and no recording has been scored with two
branches' switches on together.

## What is combined

| branch | what it brings | state there |
|---|---|---|
| `wip/detector-occl` (the base) | `side_hidden`, `seam_height`, `cap_seen_bottom`, `edge_check`, `cap_same`; the scorecard; `slice_box`, `cover_unpinned`, `stripe_two` | the first five on; the last three off, and they **stay off** (Tanush, 2026-11-19) |
| `wip/occl-vertical` | `half_stripe`, `half_thin`, `post_pair`, `stripe_wide`, `slice_behind`, `cap_low` | on there: scorecard 2417 → 2738, boxes where no barrel is 45 → 45 |
| `wip/occl-pin` | `pin_outline`, `pin_thin` | `pin_outline` on there (2417 → 2445, 45 → 45); `pin_thin` off (2556, 45; failed a cell it was committed to) |
| `wip/damage-realism` | no detector change; `degrade.REALISTIC` ("white tables, typical", "white tables, bad day"), `WORST_SEEN` | |
| `wip/stencil` | `stencil.py`, a second opinion; lead: as a verifier of the rule boxes | not a detector |

The detector code after the merge: both branches' functions and `DetConfig` fields are kept. Where they meet:

- **The stripe step** (inside the loop of `detect`): `pin_outline` places a partly seen stripe that no side reason places;
  `occl-vertical` collects the stripes that get no box (`unplaced`) for `post_pair`. Merged so that a piece is handed
  over only when the outline has not placed it either, and the re-run "as before the switch" (a box the outline placed
  would duplicate a found one) hands over as before the switch.
- **The end of `detect`**: `caps_behind`, then `post_pairs`, then `slices_behind`, then `half_stripes` (the order of
  `occl-vertical`; `occl-pin` adds no call there, it acts inside the stripe step). The order, decided on purpose: a
  rule runs after everything it leans on and before nothing that leans on it. A stripe seen whole or placed for a
  reason is the strongest reading, so the stripe step (with the outline) is first. Caps lean on found stripe barrels.
  The left-over rules (pairs, slices behind, half stripes) take only pieces that gave no box, each checks "is there
  already a box of this color here" (overlap over half) and adds nothing then, and no cap may lean on a box made from a
  left-over piece: so they are last. Among them: pairs before slices behind (a paired piece is no longer a lone slice);
  half stripes last (it reads whole bands, and may replace a box made from a corner of its own band).

The defaults in the code at the merge commit are the mechanical union of the two branches (the six + `pin_outline`
on, `pin_thin` off). They carry no verdict; this experiment decides them.

## What I expect to go wrong when the switches meet (from reading the code, nothing measured)

1. **`pin_thin` starves `post_pair` and `slice_behind`.** `pin_thin` lowers the finder's width floor, so the pieces that
   `occl-vertical` receives as "refused for their width" (`narrows`) become thin stripes instead; one that the outline
   does not place, or that is not a full slice, gets no box and is not handed over. Expected in `combined+thin`: "a post"
   and "same color beside and lower" lower than in `combined`.
2. **`pin_outline` may box each half of a barrel behind a post** (each slice has one own end): two boxes, W wide from
   each outer edge, should coincide on the barrel and be merged as duplicates; if the outer edges are not exactly W
   apart they may not be.
3. **`half_stripes` may meet a box the outline placed from a corner of the same band**; it replaces boxes "made from a
   narrow, partly seen piece of this band", which should cover it.
4. **`cap_low` and `slice_behind` both next to a found barrel**: a low cap and a slice of the same back barrel could
   both be boxed (a cap box and a slice box on one barrel).

These are predictions. The battery says which are real.

## The arms (`comb_arms.py`; every arm spelled out field by field)

| arm | what |
|---|---|
| `before` | the defaults of `origin/barrels`: none of the unmerged occlusion work (every newer switch pinned off) |
| `stack` | the defaults of `wip/detector-occl` |
| `combined` | `stack` + the six of `occl-vertical` + `pin_outline` |
| `combined+thin` | `combined` + `pin_thin` |
| `combined+cover` | report only: `combined` + `slice_box`, `cover_unpinned`, `stripe_two` |
| `combined+verify`, `combined+verify2` | `combined`, then the stencil check (below) |

Sanity checks that must hold before any number is read: `stack` gives scorecard 2417 found / 45 boxes where no barrel
is, eval table HOME 28 / 1 / 0, CAMPUS 35 / 0 / 0, light / medium / heavy 143 (0) / 99 (1) / 21 (0); the arms `all` of
`2026-11-20_occl_vertical/vert_arms.py` and `pin`, `pin+thin` of `2026-11-20_occl_pin/pin_arms.py` (each with the other
branch's switches pinned off) give their published scorecard totals 2738 / 45, 2445 / 45, 2556 / 45 on the merged
code. If one does not, the merge is wrong and is fixed before anything else.

## The battery (every arm)

1. **The eval table** (`barrels.report`, v2 rule, train frames): HOME leave-one-scene-out, CAMPUS; black, the wood
   lamp settings and Dave's frames report only; per set and scenario: found / missed / false; boxes on negative frames.
2. **The occlusion scorecard** (`2026-11-19_det_occl/run.py`, unchanged: the same 50 source barrels, 3888 scenes, seed):
   15 rows × 25 / 50 / 75 %: found (v2); totals: found, right place, boxes where no barrel is, too small / right / too big.
3. **The damage levels**, on the 16 HOME hand masks (29 barrels): perfect; "white tables, typical"; "white tables, bad
   day"; **"bad day without the stripe patch"** (= bad day with `stripe_highlight` 0); the old light / medium / heavy;
   "worst seen" (report only). Found and false, with seeds 0 to 4 (as every earlier test: "of 145") and with seeds 0 to
   19 (of 580). Seeding as before: `seed = 1000 * seed + frame index`.
4. **The real occluded or cut barrels of the train frames**, one by one (the scorecard script's `real.md`).
5. **The recordings** (337 frames, read-only): boxes appearing / disappearing against `before` and against `stack`;
   every changed campus frame looked at on a sheet and judged; black and wood clips described.

Train frames only. No test frame is opened, loaded or scored (`data/splits.json`; asserted in every loaded script).
No camera constant, no color model, no image correction, nothing over several frames.

## The rule: what becomes the default on this branch

A switch is on by default only if, **in the combination**:

- **(a)** no HOME or CAMPUS scenario row of the eval table loses a found barrel or gains a false box against `stack`,
  and no box appears on any negative frame of any set;
- **(b)** the scorecard's "boxes where no barrel is" is not above `stack`'s 45, and no scorecard cell (found, v2; the
  45 cells of the three pools together) is lower than `stack`'s;
- **(c)** false boxes are not higher than `stack`'s on the perfect masks, "typical", "bad day without the stripe patch"
  and light, **with 5 seeds and with 20 seeds**; and the campus recordings show no new wrong box against `stack` (a box
  that disappears must have been wrong). False boxes on "bad day" and on "medium" are **reported** (they are harsher
  than real white-table segmentation: `results/2026-11-19_damage_realism`) and must not be more than double `stack`'s,
  with 5 seeds and with 20.

Not in the rule, reported and named if they move the wrong way: found at each damage level; heavy and "worst seen";
the scorecard's right-place counts and box sizes; black, wood and Dave's rows; the black and wood clips.

How it is applied:

1. To `combined` as one block (seven switches). If it passes: all seven are on.
2. If `combined` fails a clause: the boxes that break it are attributed to the rule that drew them (the detector's
   reason log). The switch or switches responsible are taken out and the reduced combination is run through the whole
   battery once; it is on only if it passes every clause. No further search.
3. To `pin_thin` on top of whatever passed 1 or 2, compared with `stack` by the same clauses, and in addition: no
   scorecard cell lower than the combination without it, and false boxes at every judged level not higher than the
   combination without it. (Its old failure, a cell it was committed to and did not raise, is not part of this rule.)
4. `slice_box`, `cover_unpinned`, `stripe_two` stay off whatever `combined+cover` shows.

**Interaction fixes.** If the battery shows a conflict between rules of different branches (two boxes on one barrel,
one rule's box blocking another's, a count lower than either branch alone), it is fixed with the smallest change:
an order, a hand-over, or an "this barrel already has a box" check. No new detection rule, no new number. Each fix is
written in a dated addendum below **before** its code, with the scene that shows the conflict; then the whole battery
is run again. At most two such rounds. The numbers of each round are kept (`round1/`).

## The stencil as a verifier (a separate arm; report only unless it passes)

`combined+verify`: after the rule detector (`combined`) has drawn its boxes, each box gets the stencil's score at its
place: `stencil.box_score(mask, box, StencilConfig(), cam, others = the other boxes drawn)`, the best stencil place
overlapping the box by half or more, same color, the other boxes that stand nearer counted as hiding (exactly what
`wip/stencil`'s `veto` arm computes; the stencil's numbers are its calibrated defaults, untouched). A box scoring under
the **limit** is dropped. The verifier never adds or moves a box.

**The limit, by this rule (fixed now; `verify_calibrate.py`):**

- Masks: **A1** the 16 HOME hand masks; **A2** the same 16 frames segmented by the color model, leave one scene out (as
  the eval table does); **A4** the 10 train negative frames of the other tables with clutter (9 wood `neg_02`, 1 black
  `neg_01`), adopted color model (HOME's own two negatives are in A1 and A2). Exactly the stencil branch's pools, without
  its damaged masks. **Not** the scorecard, not CAMPUS, not the recordings, not the damage levels.
- `combined` is run on them. A box is right when it matches a hand-drawn box under the v2 rule.
- **limit = (the lowest stencil score among the right boxes of A1 and A2) − 0.02, rounded down to 0.01.** The margin:
  on `wip/stencil` the same right box scored 0.043 to 0.047 over four damage seeds (a spread of 0.004); 0.02 is five
  times that. (The stencil branch's own veto used − 0.05 and was a no-op by construction; that is why the margin is
  smaller here. It is chosen now, before any score of this arm is seen.)
- Boxes on A4 and wrong boxes on A1 / A2 are listed with their scores (expected: none on A4). They do not enter the limit.

`combined+verify2`, registered at the same time: the same, but **a box made by `half_stripes` is not checked** and
does not enter the calibration. Reason, known before any result: the stencil's score is built so that a column counts
only if it shows body, stripe and body; a barrel hidden from above or below by a thing that is not painted has no such
column and scores near 0 by design (stencil PREREG, "What follows from the design"). `combined+verify` will therefore
remove what `half_stripe` finds; `verify2` asks what the verifier is worth for the boxes the stencil can judge. Its
limit `limit2` comes from the same rule over the checked right boxes.

**The verifier's rule.** It becomes the default (as a `DetConfig` switch, coded only then) only if, against `combined`
(or the combination that passed), it

- removes wrong boxes somewhere in the battery, **and**
- loses no right box on HOME, on CAMPUS, on the campus recordings (by eye), on the perfect masks or on "typical"
  (5 and 20 seeds), **and**
- no scorecard cell (found, v2) drops by more than 1.

Otherwise it is OFF and the numbers are reported: what it removes and what it costs, everywhere in the battery. If
both arms pass, `combined+verify` (no exemption) is the one. No limit is re-picked after the scorecard, CAMPUS or the
recordings have been seen.

## What is written at the end

`results/2026-11-20_occl_combined/`: `verdict.md` (the rule, clause by clause), `scorecard.md` (one table, `before →`
the default of this branch, totals and false boxes everywhere, five sentences), `walkthrough.md` (the occlusion logic as
one idea, each rule an instance, one worked example each), `by_eye.md` (the recordings); `docs/HOW-IT-WORKS.md` §3 and
`HOW-IT-WORKS-SHORT.md` rewritten so that they describe the combined detector once.
