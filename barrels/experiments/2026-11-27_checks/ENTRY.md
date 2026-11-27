## 2026-11-27 — The two paint checks inside the detector, measured everywhere (branch `wip/adopt-checks`)

Ready to paste into `docs/EXPERIMENTS.md`. Plan: `experiments/2026-11-27_checks/PREREG.md`, committed (2bb405b)
before any run with a switch on; addendum 1 (round 2) committed (625f33f) before round 2 ran. Two rounds.

#### Hypothesis

Tanush: "what if we add the solid paint (and maybe label) checks to the detector in general?" The bluer_geom
experiment found two checks that tell near-barrel traps (the jar with a blue label, the blue tin, the small figure)
from real barrels, as a post-filter. Put inside the detector, do they cost a real barrel anywhere?

#### Method

- A stage 11 in `detector.py`, `drop_unlike_paint`, after `drop_single_reading`. Two switches, off by default:
  `check_solid`, `check_label`. Three numbers: `solid_min`, `label_stripe`, `label_body`. Every box is asked.
- **Solid paint**: of the barrel-colored pixels in the box, the share that is barrel color all around (3 x 3).
  Too low = speckle, dropped. **Label, not a stripe**: the stripe is taller than `label_stripe` x a stripe height
  AND the body share around it is under `label_body`: dropped. A box with no stripe is not asked the label question.
- Numbers from the experiment, not chosen here. P = 0.40 / 1.25 / 0.6 (its primary family on all eight places; its
  folds disagreed). M = 0.35 / 1.5 / 0.6 (its fixed-color family), measured beside.
- Arms S, L, SL at P; Sm, Lm, SLm at M. Measured on: the proof harness (all 5435 masks, scenes scored against their
  own boxes), the standard judge with the fixed colors (J1), the hand thresholds (J2), the contrast winner
  (`candidate.detect_frame`, J3), and the extreme conditions (report only).
- With both switches off: IDENTICAL BOXES ON EVERY INPUT (and the reason logs identical), in both rounds. Round 1's
  stage drew exactly the boxes of the experiment's own code on all 5435 masks, for SL and SLm.

#### Data

Train frames only. 154 ordinary frames (172 placements, 8 places), 77 extreme or unlisted frames, 5435 harness
masks. No test frame was loaded, viewed, scored or listed.

#### Results, round 1 (the experiment's readings: the whole box)

| arm | J1 fixed colors | J2 hand thresholds | J3 contrast winner | extreme: lost | harness: barrels lost (damage / scenes / real) | harness: boxes not on a barrel removed |
|---|---|---|---|---|---|---|
| S P | NCD; boxes 1.93 → 0.73; **1 lost** | NCD; 1.50 → 1.00 | PASS; 2.43 → 1.23 | 1 (box off) | **43** (32 / 10 / 1) | 2 |
| L P | NCD; 1.93 → 1.33 | NCD; 1.50 → 1.25 | NCD; 2.43 → 2.18 | 2 | **54** (10 / 41 / 3) | 25 |
| SL P | NCD; 1.93 → 0.33; **1 lost** | NCD; 1.50 → 1.00 | PASS; 2.43 → 1.18 | 3 | **98** | 26 |
| S M | NCD; 1.93 → 0.93 | NCD; 1.50 → 1.00 | NCD; 2.43 → 1.43 | 1 (box off) | **16** (11 / 5 / 0) | 1 |
| L M | NCD; 1.93 → 1.33 | NCD; 1.50 → 1.50 | NCD; 2.43 → 2.43 | 2 | **37** (9 / 25 / 3) | 17 |
| SL M | PASS; 1.93 → 0.33 | NCD; 1.50 → 1.00 | NCD; 2.43 → 1.43 | 3 | **54** | 18 |

NCD = NO CLEAR DIFFERENCE. J2 and J3 are each against the same color step without the checks. Boxes = boxes not on
their barrel, per arrangement. Found placements never moved in J2 and J3 (156.83 and 156.97).

- The ordinary barrel lost at P: the blue barrel painted in stripes under the cool bathroom lamp
  (`lampcool6_bathtile_clutter_01`, solidity 0.399).
- The extreme losses: the parked wood desk under the cool lamp, an orange barrel behind a nearer blue one. Its box
  holds the front barrel's blue body, which reads as a tall stripe with little orange around it.
- The harness is where it shows. Solid paint drops real barrels on the damaged masks (dotted holes, ragged edges)
  and small slivers of partly hidden barrels. The label check drops barrels standing beside or behind a barrel of
  the other color: the neighbour's body is the stripe's color, so the "stripe" reads 1.5-2.0 x tall.

#### Results, round 2 (addendum 1: solid paint read after the detector's 3 x 3 closing; the stripe's height column by column, the median; the body share in the stripe's columns only)

| arm | J1 fixed colors | J2 hand thresholds | J3 contrast winner | extreme: lost | harness: barrels lost | harness: boxes not on a barrel removed |
|---|---|---|---|---|---|---|
| S P | NCD; nothing changes | NCD; 1.50 → 1.25 | NCD; nothing | 0 | **0** | 0 |
| L P | NCD; 1.93 → 1.73 | NCD; 1.50 → 1.25 | NCD; 2.43 → 2.23 | 0 (+1 found on J3) | **7** (scenes: 3 found, 4 box off) | 18 |
| SL P | NCD; 1.93 → 1.73 | NCD; 1.50 → 1.00; cluttered empty 0.50 → 0 | NCD; 2.43 → 2.23 | 0 | **7** | 18 |
| S M | NCD; nothing | NCD; 1.50 → 1.25 | NCD; nothing | 0 | **0** | 0 |
| L M | NCD; nothing | NCD; nothing | NCD; nothing | 0 | **0 found lost**; 1 barrel with its box off loses it | 2 (scenes) |
| SL M | NCD; nothing | NCD; 1.50 → 1.25 | NCD; nothing | 0 | as L M | 2 |

- No barrel lost on any real frame, ordinary or extreme, in any arm.
- The closing makes solid paint safe and nearly idle: it removes one box in all of this, the jar on
  `lampmid6_bathtile_neg_02` under the hand thresholds.
- The label check at P still loses 7 barrels in the simulated scenes: a barrel 50-80 % hidden by one of the other
  color, where the neighbour covers most of the stripe's columns. At M it removes 2 scene boxes (a wrong color, a
  second box) and costs one box-off barrel its box (scene 01438, 68 % hidden).
- What the checks removed on real frames, looked at: the jar on the glass table, a wrong-colored box on the wood
  desk, the jars on the cluttered empty bathroom frames (hand thresholds). On the contrast path a box removed lets
  the contrast step find the front blue barrel on the wood desk (gained, report only).

#### Takeaway

- The checks, as the experiment read them, cost real barrels wherever the mask is not clean: damaged paint and
  partly hidden barrels. The ordinary frames did not show it; the harness did.
- Closing the mask first makes solid paint safe and almost idle. Reading the stripe column by column halves the
  label check's losses but does not end them at 1.25.
- By the pre-registered rule: **adopt solid paint (round 2 reading) at 0.40, and the label check (round 2 reading)
  at 1.5 / 0.6.** Neither changes one box on the ordinary train frames with the fixed colors. Together they change
  3 of the 6152 harness boxes. They are a safety net for looser color steps, not a gain today.
- Not adopted: the label check at 1.25 (7 barrels lost), and every round-1 reading.

#### What next

1. Tanush: "understood" on the walkthrough, then merge `wip/adopt-checks` (the second commit is the plain code).
2. The trap that made the checks (the jar under the warm lamp, the tin, the figure) is caught by round 1 and not
   measured with round 2 on the B4 color step. Run bluer_geom's G1 with the round-2 readings before relying on them.
3. A barrel behind one of the other color reads as a label. A reading that leaves out the nearer barrel's own
   pixels (as `drop_seen_through` does) is the next idea for the label check.

#### Not done

- The B4 color step with the checks (bluer_geom's G1) was not re-run with the round-2 readings.
- The judge with the checks was not run leave one place out: nothing was fitted here.

#### Adoption (the second commit on the branch, awaiting Tanush's "understood")

- The switches are gone: stage 11 always runs, with `solid_min` 0.40, `label_stripe` 1.5, `label_body` 0.6 (21
  numbers). Tests: `tests/test_detector_paint.py` (6), `tests/test_report.py` (21 numbers, no switch).
- Checked against the detector before it (`verify_plain.py`, `results/2026-11-27_checks/plain/`): fixed colors, no
  box changes on any train frame (NO CLEAR DIFFERENCE, 133.80 placements, boxes 1.93); hand thresholds, one box goes
  (the jar on `lampmid6_bathtile_neg_02`; 1.50 → 1.25); contrast winner, no box changes (156.97, 2.43). Proof harness
  (`plain/harness_diff.md`): 3 of 5435 inputs differ, all scenes, exactly round 2's L M removals.
- `harness.py`, `judge_all.py` and `arms.py` name the switches: they run at commit 4863839 (round 2).

#### Addendum 2: does the adopted stage still catch the traps it was made for? (B4, "bluer than the light")

`b4_traps.py` (`results/2026-11-27_checks/b4/`), the plain code with bluer_geom's code unchanged, leave one place out.
(i) = the folds pick as bluer_geom did (before stage 11), then run with stage 11 off / on; (ii) = the folds pick
with stage 11 in the detector.

| candidate | verdict vs today | found, placements | per frame | gained / lost | boxes not on their barrel (per frame) | cluttered empty |
|---|---|---|---|---|---|---|
| B4, stage 11 off (reproduces bluer_geom) | FAIL | 145.72 | 257 | 46 / 0 | 6.68 (24) | 1.25 |
| B4, stage 11 on (i) | FAIL | 145.72 | 257 | 46 / 0 | 6.18 (22) | 0.75 |
| B4, stage 11 on (ii) | FAIL | 145.72 | 257 | 46 / 0 | 6.18 (22) | 0.75 |
| delta 0.20, stage 11 off | FAIL | 143.80 | 251 | 40 / 0 | 3.93 (13) | 0.75 |
| delta 0.20, stage 11 on (i) | PASS | 143.80 | 251 | 40 / 0 | 3.43 (11) | 0.25 |
| delta 0.20, stage 11 on (ii) | PASS | 145.80 | 257 | 46 / 0 | 3.43 (11) | 0.25 |

B4's 24 false boxes, named from the contact sheet (`sheets/b4_false_*.jpg`): the jar with the gold lid and blue label
12 (#1, 2, 4, 5, 6, 7, 9, 10, 14, 15, 21, 22), the Vaseline tin 4 (#13, 18, 19, 20), the small figure 2 (#16, 17),
other 6 (#3 a cap over a real barrel, #8 a cap beside one, #11 and #23 wrong colors, #12 beside a barrel, #24 the
pale-wood close-up). **The adopted stage removes 2: jar #4 and jar #15. Tin 0 of 4, figure 0 of 2, other 0 of 6.**
Round 1 at P would have removed 20 of 24 (all but #3, #8, #11, #23). Delta 0.20: 2 of 13 (jar #27, #32).

Why: the closing heals the tin's and the figure's speckle as it heals damaged paint. Solidity without the closing
0.17-0.24, with it 0.59-0.95. The column median lowers the glass jars' label (1.65 → 1.27, 1.53 → 0.71). The safe
readings and the trap readings are the same readings: what made the stage safe is what stopped it catching traps.

#### Addendum 3: a setting that keeps the harness and catches the traps? (fusion's "mild" among the candidates)

Fusion (`wip/exp-fusion`, `fusion.MILD`) used the round-1 readings (`stages.measure`: whole box, no closing) at
0.35 / 1.5 / 0.6. `traps_all.py`, `results/2026-11-27_checks/variants/`. The ten stages, then each variant as a
post-filter; "lost" = a barrel found or with its box off that ends with no box, or found → box off.

| variant | harness: real lost | ordinary lost (4 color steps) | extreme lost | contrast C1: boxes not on barrel (per frame) | B4: per frame | B4 traps removed: jar / tin / figure / other |
|---|---|---|---|---|---|---|
| V0 adopted | 1 (a box-off barrel, 68 % hidden) | 0 | 0 | 2.83 → 2.63 (9 → 8) | 24 → 22 | 2 / 0 / 0 / 0 |
| V1 fusion mild | **54** | 0 | 2 | 2.83 → 1.43 (9 → 6) | 24 → 11 | 7 / 3 / 2 / 1 |
| V2 row label, nearer boxes left out | 5 | 0 | 1 | 9 → 8 | 24 → 18 | 5 / 1 / 0 / 0 |
| **V3 column label at 1.25, nearer boxes left out** | **0** | 0 | 0 | 2.83 → 2.43 (9 → 7) | 24 → 20 | 4 / 0 / 0 / 0 |
| V4 V0 + raw speckle < 0.25 (not at the frame edge) | 1 (as V0) | 0 | 0 | 9 → 8 | 24 → 17 | 2 / 3 / 2 / 0 |
| V5 V2 + V4 | 5 | 0 | 1 | 9 → 8 | 24 → 14 | 5 / 3 / 2 / 0 |

- Contrast's 9 per frame: V3 removes 2 (the glass jar on `lampmid3_glass_occl_02`, a small box on
  `lampwarm6_glass_occl_02`). The glass clutter jar (`lampmid6_` and `lampwarm6_glass_clutter_01`) and the pale-wood
  close-up are removed only by V1 and V2 (the whole-box readings), which lose real barrels. Through this code fusion's
  setting gives 9 → 6, not fusion's 9 → 3: there the checks act on fused proposals, here inside every detect call
  of the contrast path, where a removed base box lets the contrast step paint again.
- V3's label (column median, nearer boxes left out, 1.25) and V4's raw speckle decide box by box on the same input,
  so V3 + V4 is their union, not measured as one arm: 0 harness barrels lost, the same 2 of contrast's 9, and on B4 4
  jars, 3 of 4 tin boxes and both figure boxes (9 of 24).
- Honest limit: V2-V5 were written after looking at the harness rows and the trap readings. That makes them in-sample
  for those, and the 0.25 sits just above the one harness barrel it would have cost (a 16-px sliver at the frame edge,
  excused by the edge rule). They need frames they were not shaped on before adoption.
- Recommendation for the contrast path: **V3** (solid paint closed < 0.40; label, column median with nearer boxes left
  out, > 1.25 and body < 0.6). It is the only candidate that loses nothing anywhere, and it removes 2 of contrast's 9.
  Add V4's raw speckle (< 0.25, not at the frame edge) if the tin and figure matter. Nothing tried keeps the harness
  and also removes the glass clutter jar and the pale-wood close-up. Not adopted here; the plain code is unchanged.
