# ENTRY.md — text ready to paste (branch `wip/exp-place-ceiling`, 2026-11-26)

`TODO.md`, `STATUS.md`, `EXPERIMENTS.md` and `DECISIONS.md` were not edited on this branch. Below: the entry for
`EXPERIMENTS.md`, then lines for `TODO.md`. Everything is train frames only; no test frame was opened, scored or
listed. No pixel was changed. Nothing that runs by default was changed.

---

## For `EXPERIMENTS.md`

### 2026-11-26 — What a color setting made per place can reach, without sliders (`experiments/2026-11-26_place_ceiling`; C1, C7, E6)

- **Question.** The fixed colors find 133.8 of 172 placements. Tanush's hand thresholds per condition find 156.8,
  in-sample. (A) Under the warm bathroom lamp even they find 6 of 15: with the full hue range, does blue at hue 26 to
  44 paint the barrels or the floor? (B) If ONE frame of a condition and its boxes set the six numbers, with no
  slider, what is reached on the other frames? (C) What is the best any rectangle pair per condition can do? (D) How
  much of the gap to the vendor does knowing the place close?
- **Method** (PREREG first; one dated addendum for round 2, before it ran).
  - New helper `src/barrels/placecal.py` (nothing calls it by default; 18 unit tests). Per color, the barrel pixels of
    a frame are the body rows of that color's free-standing boxes and the stripe rows of the other color's (where
    they sit was measured on the home masks). **net**: the hue range and S floor that paint the most barrel pixels
    minus the pixels painted outside the boxes, over the full hue circle. **mid** (primary): the slider tool's recipe
    on top (pick the net setting with which the detector finds most on that frame, then the middle of each number's
    working run). **tool**: `hsrange.propose` as it is today.
  - Held out: every frame is scored with a setting computed from another frame. `cal_core`: `core_01` sets its
    condition (the backup frame sets `core_01`). `cal_rot1..4`: each frame in turn. `cal_otherlight`: the next light
    of the same place. `cal_otherplace`: another place (the control).
  - In-sample ceilings: `hand`; `relabel` (hand, the bathroom replaced by 12 new proposals); `relabel_blue` (his
    orange, the proposals' blue); `cal_all_net` (all frames of a condition pooled); `oracle` (the best of 12 or more
    seeds per condition, then single-number steps while the score rises).
  - Judge: `barrels.judge`, today's default as the baseline, margins from `results/baseline/margins.json`.
    `python barrels/experiments/2026-11-26_place_ceiling/run.py all`.
- **Data.** The ordinary train conditions: 154 frames, 17 conditions at 8 places, 172 placements, 307 barrels per
  frame. 99 frames can calibrate (they hold a free-standing barrel). Vendor files exist at six places (108
  placements).
- **Result, every judged candidate** (found = strict, per placement; boxes = not on their barrel, once per
  arrangement):

| candidate | kind | found | per frame | boxes | verdict |
|---|---|---|---|---|---|
| fixed colors (baseline) | | 133.8 | 211 | 1.9 | |
| `cal_core_mid` (**primary**) | held out | 141.8 (+8.0) | 269 | 1.2 | **FAIL** (campus 35 → 21) |
| `cal_core_net` | held out | 140.9 (+7.1) | 266 | 2.2 | FAIL (campus, ABP white, home) |
| `cal_core_tool` | held out | 150.8 (+17.0) | 272 | 7.3 | FAIL (campus, home, boxes, a box on a clean empty frame) |
| `cal_rot1..4_mid` | held out | 138.1, 139.6, 130.9, 141.1 (mean 137.4) | 263, 267, 256, 269 | 2.7, 1.2, 0.2, 2.5 | FAIL × 4 (campus, home, ABP white) |
| `cal_otherlight_mid` | held out | 148.9 (+15.1) | 263 | 1.2 | PASS |
| `cal_otherplace_mid` | control | 80.9 (−52.8) | 142 | 6.8 | FAIL, as it should |
| `cal_all_net` | in-sample | 141.0 (+7.2) | 261 | 0.5 | FAIL (campus, ABP white, home) |
| `hand` | in-sample | 156.8 (+23.0) | 281 | 1.5 | PASS |
| `relabel` | in-sample | 158.3 (+24.5) | 287 | 1.2 | PASS |
| `relabel_blue` | in-sample | 158.6 (+24.8) | 288 | 1.2 | PASS |
| `oracle` | in-sample | 163.2 (+29.4) | 294 | 0.0 | PASS |
| round 2: `cal_core_keep` | held out, designed after round 1 | 156.6 (+22.8) | 281 | 2.6 | PASS |
| round 2: `cal_rot1..4_keep` | the same | 154.4, 156.2, 154.0, 153.0 (mean 154.4) | 278, 280, 277, 278 | 3.1, 1.6, 1.6, 3.8 | PASS, PASS, PASS, **FAIL** (boxes +1.9, margin 1.85) |
| round 2: `cal_core_wide` | the same | 158.5 (+24.7) | 287 | 7.4 | FAIL (pale wood, boxes, boxes on empty frames) |

- **By place** (found placements; per frame in brackets):

| place | placements | fixed | one frame, `core_01` | each frame in turn, mean | round 2: keep rule | hand | relabelled | oracle | vendor |
|---|---|---|---|---|---|---|---|---|---|
| ABP gray | 16 | 10.0 | 15.0 | 11.8 | 15.0 | 15.0 | 15.0 | 16.0 | 16.0 |
| campus | 35 | 35.0 | 21.0 | 23.0 | 35.0 | 35.0 | 35.0 | 35.0 | 35.0* |
| bathroom floor (4 lamps) | 15 | 4.0 (16) | 14.0 (56) | 13.9 | 13.5 (54) | 12.5 (50) | 14.0 (56) | 14.5 (58) | 7.0 (28) |
| glass table (5 lights) | 15 | 14.8 (74) | 14.8 (74) | 14.8 | 14.8 (74) | 15.0 (75) | 15.0 (75) | 15.0 (75) | 12.0 (60) |
| ottoman (3 lamps) | 15 | 3.0 (9) | 13.0 (39) | 12.7 | 12.3 (37) | 13.3 (40) | 13.3 (40) | 13.7 (41) | 12.3 (37) |
| pale wood | 15 | 13.0 | 12.0 | 12.8 | 12.0 | 12.0 | 12.0 | 14.0 | 12.0 |
| ABP white | 32 | 26.0 | 25.0 | 24.0 | 26.0 | 26.0 | 26.0 | 27.0 | 24.0 |
| home white | 29 | 28.0 | 27.0 | 24.5 | 28.0 | 28.0 | 28.0 | 28.0 | 29.0* |
| **six places with vendor files** | 108 | **70.8 (148)** | **93.8 (221)** | **89.9** | **93.6 (218)** | **93.8 (218)** | **95.3 (224)** | **100.2 (231)** | **83.3 (177)** |
| boxes not on their barrel there | | 1.9 | 1.2 | 1.4 | 2.6 | 1.5 | 1.2 | 0.0 | 3.0 |
| **all eight places** | 172 | **133.8 (211)** | **141.8 (269)** | **137.4** | **156.6 (281)** | **156.8 (281)** | **158.3 (287)** | **163.2 (294)** | **147.3\*** |

  \* the vendor is ASSUMED perfect on the two white tables without vendor files.

- **A. The warm bathroom.**
  - Under the warm lamp the blue paint reads gray-olive: the middle half of its pixels is at hue 25 to 57, S about
    42. The floor is hue 10 to 29 with S above 100.
  - Blue at hue 26 to 44 paints the barrels, not the floor: over the six frames it paints 1331 barrel pixels and 610
    others, of 1.5 million. Start the range at hue 20 and it paints 820,842 floor pixels.
  - Found under the warm lamp, of 15: fixed 1, hand 6, **relabelled 14**, one frame 13, oracle 14, the vendor 0.
  - The whole bathroom: hand 12.5 → relabelled 14.0 of 15 placements. With only the blue numbers changed: 14.2.
  - The one barrel still missed is half hidden behind a tin.
- **B. One frame sets the place.**
  - **The registered answer is: it fails.** `core_01` as the calibration frame gains 78 barrels and loses 20.
    Counted per placement that is +8.0, and campus drops from 35 to 21.
  - Where the fixed colors fail (bathroom, ottoman, gray table) one frame does the hand thresholds' job: 42.0 of 46
    placements against the hand's 40.8 and the fixed 17.0.
  - Where the fixed colors work (campus, home, glass, pale wood, ABP white) it loses: 99.8 of 126 against 116.8.
  - Why, from the pictures: a setting from one frame is too narrow. The median orange hue range of a one-frame
    setting is 7 units, the smallest 1; the fixed range is 10, the hand's 9. On campus the blue range of `core_01`
    ends at hue 106, and the barrels of the other frames read 107 and more, so their blue stays unpainted.
  - Pooling all frames of a condition does not fix it (141.0). The limit is the rule "most barrel pixels minus
    outside pixels", which cuts the tails of the barrel's color, not the number of frames.
  - The tool's proposal as it is today finds more (150.8) and floods: 7.3 boxes not on their barrel, one on a clean
    empty frame.
  - Which frame matters. Over the rotations found runs from 130.9 to 141.1. A shot of barrels seen from above
    (`top_01`, `topstripe_01`) finds 1 of 34 on the other campus frames. Best kinds of shot: touching barrels (92 %
    found on the other frames) and `core_01` (84 %).
  - Another light of the same place: the cool-lamp setting finds 1 of 15 under each other bathroom lamp; the mid
    lamps' settings find 3 of 15 under the warm lamp; on the glass table any light's setting works under any light.
    Over every pair: the same condition 87.2 % found, another light 82.5 %, another place 53.5 % (fixed colors on
    the same frames: about 70 %, 64 %, 69 %).
  - The control behaves: a setting from another place finds 80.9 placements, far below the fixed 133.8.
- **Round 2** (designed after round 1 was seen; a hypothesis, not a held-out result). The calibration frame first
  tests the fixed colors: if they find every free-standing barrel on it and draw nothing else, keep them; otherwise
  use its setting. With `core_01`: 156.6 placements, PASS, the hand thresholds' level, with 2.6 boxes not on their
  barrel against 1.9. Nine of 17 conditions keep the fixed colors. With each frame in turn: three PASS, one FAIL on
  boxes (+1.9 against a margin of 1.85). By the addendum's own line ("all four rotations pass") it is **not** shown
  safe. "Only widen" finds most (158.5) and fails on boxes (7.4).
- **C. The oracle.** 163.2 of 172 placements, 294 of 307 barrels, no box that is not on its barrel. It is the best
  seed in every condition; no single step improved any. The 13 barrels it misses are not color: 5 hidden by a box,
  a hand, a glass or a barrel of the same color (ABP white), 3 cut by the frame edge, 3 half hidden behind an
  object, 1 close-up seen from above, 1 wedge between two barrels.
- **D. The gap to the vendor** (six places, 108 placements): fixed 70.8, the vendor 83.3, a gap of 12.5. One
  calibration frame: 93.8. Hand: 93.8. Relabelled: 95.3. Oracle: 100.2. Knowing the place closes the gap and goes 10
  placements past it, with fewer boxes off the barrels than the vendor (1.2 against 3.0).
- **Takeaway.**
  - A rectangle pair per place is enough for 163 of 172. What is left is the detector's.
  - A calibration shot gives the hand thresholds' gain where the fixed colors fail. Used everywhere it is worse
    than the fixed colors where they work.
  - So a calibration shot needs a guard. The simple one (test the fixed colors on the shot first) reaches the hand
    level on these frames, but it was chosen after looking, and one of its four rotations fails by a box.
  - The warm bathroom was a slider limit, not a limit of the rectangle.
- **What a calibration shot should contain.**
  - Free-standing barrels of both colors. A half-hidden or frame-cut barrel gives no usable pixels (`occl_02`,
    `close_01`).
  - Several barrels from near to far, with their shaded sides, seen from the side as the robot sees them. Not from
    above.
  - The empty table and the usual clutter in the same shot: the pixels outside the boxes are what stops the range.
  - One shot per light. A new lamp setting needs a new shot.
  - The fixed colors tested on it first.
- **Caveats.** In-sample ceilings are ceilings. Round 2 is post hoc. 21 comparisons were judged. The rotations are
  not independent of each other (in a condition with four usable frames rotation 4 repeats rotation 1 for those
  frames). The oracle is a search and so a lower bound. The extreme conditions were not run.
- **Next.** (1) A margin rule for the one-frame setting: how far past the calibration frame's barrel pixels the
  range should reach; registered before it runs, judged on the places Tanush shoots next. (2) The keep rule on those
  new places, unchanged. (3) Tanush reviews the 12 bathroom proposals. (4) Ask Dave whether a calibration shot per
  place and per light is allowed in data collection.

---

## Proposals written for Tanush (`data/labels/<stem>` + the proposal suffix; his slider labels are untouched)

`core_01`, `clutter_01`, `occl_02` of `lampcool6_bathtile`, `lampmid3_bathtile`, `lampmid6_bathtile`,
`lampwarm6_bathtile`: 12 files, written by `write_proposals.py` through `hs_slider.py --save-proposal`, each with its
reasoning. To see one next to his label:
`python barrels/tools/hs_slider.py --filter 4A8B_lampwarm6_bathtile_core_01 --render-grid /tmp/g.png --try saved --try claude`.
The slider window opens a saved label before a proposal, so on these frames the proposal shows only that way.

## For `TODO.md` ("Now", section C)

- **C1** done on `wip/exp-place-ceiling`: 12 proposals written; relabelled ceiling 158.3 against 156.8; warm lamp 6 →
  14 of 15. Blue at hue 26 and up paints the barrels, not the floor. Waits for Tanush's review of the proposals.
- **C7 / E6 (third idea)** measured: one calibration frame per condition FAILS the pass rule (+8.0 placements, campus
  35 → 21); with "keep the fixed colors where the shot says they work" it reaches 156.6 (round 2, post hoc, one of
  four rotations fails by a box). Per-place oracle 163.2 of 172.
- **New:** a margin rule for the one-frame setting; the keep rule on the next places shot.
- **For D3:** the 13 barrels no rectangle pair finds are listed in `results/2026-11-26_place_ceiling/summary.md`
  (sheet `oracle_still_missed`); none is a color case.
