# The unattended block of 2026-11-26 (reviewer session)

Written by Claude for Tanush. Plain English. **Updated 2026-11-27 with every result. Start with section 0.** Everything is on train frames only. No test frame was opened.

## 0. The headline (2026-11-27)

**One idea does most of the work: find the stripe by color difference, then paint that barrel with its own colors** (branch `wip/exp-contrast`). Judged with a whole place held out: 133.8 → 155.3 of 172 placements, 64 barrels gained, none lost, no box on an empty frame. On the six places with vendor files it finds 92.3 of 108 placements against the vendor's 83.3 and today's 70.8 (train frames; our methods were shaped on them). Adding the other two winners on top adds nothing above the noise (`wip/exp-combined`). What is left is nearly all hidden or frame-cut barrels. Next: walk you through contrast, adopt it, then test it on a new warm-lit place.

| branch | result |
|---|---|
| `wip/exp-contrast` | **PASS +21.5**, the best |
| `wip/exp-combined` | contrast alone wins; mixes add 0.2 to 2.7, inside the noise |
| `wip/exp-nearmiss`, `wip/exp-selfcal` | PASS +13.7 / +13.8; mostly covered by contrast |
| `wip/exp-slack` | `slack=D`: 11 of 40 erosion losses back, no new false box; being prepared for adoption (`wip/adopt-slack`) |
| `wip/exp-bottom` | `bottom_rule=low_uncut`: helps with looser colors, no effect with fixed ones |
| `wip/exp-sidecut` | not recommended (one box on a tin, one on the wrong side) |
| `wip/collapse-2` | merged: 18 numbers, boxes identical |

## 1. What you asked for, and where each step stands

| step | state |
|---|---|
| 1. Merge `wip/final` | done: merged and pushed; 930 tests and the never-regress check passed |
| 2. The detector map, with recommendations | done: `docs/archive/DETECTOR-MAP-before-collapse-2026-11-26.md` (the detector as it was) |
| 3. The measurement | done, merged: counting by placement and place, a misplaced box once, the noise floor, never-regress with a margin, one pass rule (`tools/judge.py`) |
| 4. The collapse | done, merged: no switches, ten named stages, 20 numbers; boxes identical on 5435 masks. **The map of the collapsed detector is `docs/DETECTOR-MAP.md`: start there** |
| 5. The experiments | six done, five running; each on its own branch `wip/exp-…`, nothing adopted |

The state before the collapse is the tag `pre-collapse-2026-11-26`.

## 2. The three things to know

1. **The detector is now readable.** `detect` is eleven lines: pieces, stripes, a box per stripe, close-ups, verify, barrels behind barrels, pairs, half stripes, verify again. Stripes come first. Geometry is the ruler inside every check, not a stage. Nothing about the boxes changed; that was checked box for box.
2. **Color per place is enough; the open question is only how to know it.** The best ranges per condition find 163.2 of 172 placements, and the 13 they miss are hidden or cut by the frame. Your warm-bathroom labels were stopped by the slider, not by the idea: with blue at hue 26 to 44, 14 of 15 are found (vendor 0).
3. **Two ideas pass the new pass rule with a whole place held out, each with about 37 barrels gained and none lost:** your near-miss idea (a pixel just outside the range counts next to strong evidence) and the barrel as its own color reference (a half-found barrel completes itself). Both lift the gray table, the bathroom and the ottoman and leave the other five places alone.

## 3. The experiments so far

Baseline everywhere: the fixed colors find 133.8 of 172 placements (211 of 307 barrels counted per frame). A gain counts above +4.0 placements.

| branch | idea | result |
|---|---|---|
| `wip/exp-nearmiss` | near-miss colors next to strong evidence (yours) | **PASS**: 147.5 (+13.7), 38 gained, 0 lost; boxes off a barrel 1.9 → 3.6, close to the limit |
| `wip/exp-selfcal` | a found or half-found barrel sets the colors | **PASS**: 147.6 (+13.8), 37 gained, 0 lost; boxes 1.9 → 2.2; no box on an empty frame |
| `wip/exp-place-ceiling` | what a setting per place can reach | ceiling 163.2; hand thresholds 156.8; one calibration frame as planned FAILS (campus 35 → 21) |
| `wip/exp-light` | blue follows the light; what to read the light from | no clear difference (+3.9, 14 gained, 0 lost); "bluer than the light" finds the bathroom but FAILS on clutter boxes |
| `wip/measure` (merged) | the measurement itself | per placement on the six measured places: ours 70.8, vendor 83.3 of 108 |
| `wip/collapse` (merged) | the collapse | boxes identical; 952 tests |

What did not work, plainly: adaptive thresholds from the light alone do not clear the bar; plain two-level thresholds flood the home wall; one calibration frame gives ranges that are too narrow; no reading of the light predicts the orange the ottoman needs.

## 4. Calls I made while you were away (say if you disagree)

- The stage-1-alone mode of the detector is gone; `stripe_bridge` and `thin_frame` became plain code as they were; the six rules that are sound but that no real frame shows stay.
- The pass rule compares a gain with the largest gain a meaningless change makes (4.0 placements) and a loss with the largest such loss (10.9). A pass under +6 is called weak.
- The never-regress check protects home, campus, glass, pale wood, the ABP white set and the cool-lamp bathroom, each with a margin of one placement and one box.
- Experiments are NOT merged. Each waits on its branch for your word.

## 5. For you and Dave

- Is comparing a pixel with the light's color ("bluer than the light") image correction? It changes no pixel, but it is the same arithmetic.
- Is a color setting that a barrel in the frame sets for that frame acceptable? (It is the "barrel-referenced thresholds" of the 2026-10-07 decision.)
- Can the camera's exposure and white balance be locked?

## 6. What you can do

- Shoot one or two places: most useful is the warm lamp on a pale table or floor that is not the bathroom (a third warm place), with the blue tin and the red jar in the clutter frame; then a dark cloth under ordinary white light.
- Shoot the home white table with vendor files, so the assumed vendor rows become measured.
- Review the 12 bathroom threshold proposals.
- Read `docs/DETECTOR-MAP.md`; the walkthroughs of the measurement and the collapse are owed to you in chat.

## 7. Still running when this was written

`wip/exp-contrast` (the stripe by color difference), `wip/exp-combined` (the two winners together, against the vendor, and on frames nobody designed on), `wip/exp-bottom` (the bottom edge), `wip/exp-sidecut` (a barrel 60 % hidden at the side), `wip/exp-slack` (slack in the stripe tests), `wip/collapse-2` (a second, smaller pass of the collapse).
