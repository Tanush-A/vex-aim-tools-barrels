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
