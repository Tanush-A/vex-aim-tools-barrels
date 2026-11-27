# Reviewer session, 2026-11-23: the logic behind the barrel detector

Read-only review. No file in the repo was changed. Everything was measured on train frames only, from a copy of branch `wip/final`.
Five supporting reports sit beside this file: `adaptive_forensic.md`, `color_physics.md`, `detector_audit.md`, `eval_audit.md`, `vendor_and_methods.md`.

## 1. The one-paragraph verdict

The program decides, pixel by pixel, "is this the home orange or the home blue", turns the photo into a three-value mask, and throws the photo away. Everything that hurts follows from that order of operations. The absolute colors move between places, so the mask breaks. The adaptive work tried to predict the right absolute colors from whole-frame statistics, which describe the room and not the barrels. The detector then has to guess, from a mask with holes, things the photo shows plainly, and each guess became a switch. The vendor does the opposite: it is a trained model that reads local contrast and shape, so a color cast mostly cancels.

## 2. Why adaptive thresholding failed

It was not the hue and saturation rectangle. Per-condition hand thresholds through today's detector, train frames:

| color step | found of 243 (frames with vendor files) | found of 307 (all ordinary) |
|---|---|---|
| fixed model | 148 | 211 |
| vendor | 177 | no files for home and campus |
| hand thresholds per condition | 218 | 281 |

Caveat: in-sample and circular, because the sliders were set while watching the detector's boxes.

What failed was the prediction, for five reasons:

1. **Chicken and egg.** Barrels cover a median 4.2 % of the pixels. The "orange peak" feature sat 5 or more hue units from the barrel's hue on 37 of 99 frames (bathroom 15 of 16, ABP white 16 of 16). To read a barrel's color you must first know where the barrel is.
2. **There is no single light shift.** One shared shift explains about 41 % of the color movement. Orange and blue move in opposite directions in 15 of 17 ordinary conditions. Orange follows the surface or camera (hue 14 to 16 on the ottoman under cool, mid and warm lamps). Blue follows the lamp (S 233 at home, 31 to 57 on the tile under the mid and warm lamp). "The image is more yellow, shift the thresholds" cannot be one knob.
3. **The target was a slider position, not a fact about the barrel.** The working range on a frame is 1.7 to 4.4 times the between-condition spread for four of six thresholds. Labels within one condition differ by up to 34 hue and 129 saturation units. Some are copied or pinned at the slider limit.
4. **Too few places.** 3, then 5 labelled places, 2 with warm light, against grids of 480, 72 and 320 settings.
5. **Pass rules below the noise floor.** One box is about 0.03 of a condition's score against a 0.02 limit. 10 of 12 one-step neighbours of the fixed model fail the clauses. The hand thresholds, with 70 more barrels, fail A1, A2 and A3.

One idea worked and was rejected by the rules, not by the data: the blue saturation floor following the light. Round 1 gained 22 barrels and lost none. It failed on one box on one empty frame and one condition at minus 0.023.

## 3. The detector's logic

**Stupid**
- A barrel needs both colors to pass. Of 63 clean missed barrels on the new conditions, 57 have one color unpainted, and 49 of those 63 have the other color at full strength. A perfectly painted, right-sized blue body is refused because its stripe is a few hue units off.
- The verify step reads the diagnostic log to make decisions.
- The never-regress check protects 64 barrels with 63 found. It can only say no. It rejected a better-calibrated camera over one barrel.

**Naive**
- Seventeen hard yes or no tests in a row, none able to make up for another. Eroding the mask by one pixel takes home and campus from 63 to 51 found.
- Simulated occluders look like empty table. Straight edge hiding half: scorecard 90 of 100, real frames 0 of 2.
- Geometry is a hard veto while the best tilt varies 0.9 degrees across places. 15 % of true bottoms fall outside the detector's own tolerance.
- The week went to occlusion. Of the 52 barrels the vendor finds and we miss, 50 are color failures and 4 are occluded.

**Can be collapsed**
- 30 switches, 23 on. 14 of the 23 rest on simulation only. Flipping 9 of the 30 changes no box on 199 frame-runs. Inert and on: `cap_same`, `edge_check`, `post_pair`, `cap_low`, `thin_span`.
- The 13 simulation-only switches together find 10 barrels and add 2 false boxes. Two switches carry the real weight: `side_hidden` (26 barrels) and `stripe_join`.
- Four constants for "wider than a barrel", seven edge-against tests, four meanings of "nearer", five distance estimators.
- The caps, the verify step, the frame-edge cases and the duplicate checks are one idea: propose a barrel at a ground position, render what should be visible given nearer barrels, score it. A reformulation removes edge cases. Only new evidence removes misses: a crude one-score probe on the same mask did not beat the rules (90 against 102).

**Accidental**
- `height_max` is the only guard on two later branches. Off, false boxes go from 7 to 105.
- The far-stripeless branch cannot accept a real far barrel.
- There is no fill test, though it separates all 19 kept close-up pieces.

## 4. What is not considered

- **Relative color.** Compare a barrel's body with its own stripe on log(R/B), sign and a minimum margin. At known barrel locations: 220 of 220 ordinary and 97 of 98 extreme barrels pass at margin 0.3, with 0.63 % of random non-barrel patches (1.65 % in clutter). At margin 1.0: 98.2 % and 0.05 %. This is a candidate finder, not a detector. It was measured where the barrel is known to be, and it breaks when very dark or under glare.
- **The barrel as its own color reference.** Find the stripe by contrast, read that barrel's two colors, grow the body from them. This is the way out of the chicken and egg, and it is what the RoboCup teams that solved color calibration did: geometry labels the pixels, color is learned from them.
- **The photo after the mask.** Edges, soft color evidence, and a third state for "something is in front here". Thirteen switches exist to guess that one bit.
- **Calibration per place.** The hand-threshold numbers above are a per-place calibration. The robot works in one place per session.
- **The camera.** No exposure or white-balance lock was found in any public interface. Not yet asked.
- **The vendor's score.** 227 of 248 saved vendor boxes score 90 or more. Its false boxes are likely the low-score ones. A fair comparison matches false-box rates.
- **The vendor on a white table.** The week's first goal was to match the vendor in its own conditions. No white-table frame has a vendor file.

## 5. Measurement

- Lamp settings were counted as samples. 243 train barrels are 108 placements at 6 places. 32 test barrels are 12 placements of one scene.
- A vendor box on a real barrel that fails the bottom clause is charged twice. Boxes on nothing: vendor 7, ours 5. All four "we win" conditions vanish under the place rule.
- 135 of 243 new train barrels have Claude-proposed boxes accepted unchanged.
- 18 pre-registrations, 28 rounds, median 13 minutes from plan to result. Everything dated 11-23 to 11-25 was committed on 11-23.
- The frozen adaptive rule was never run on the new places.

## 6. What I would do, in order

1. Fix the ruler: count placements and places, lead with the place rule, count a misplaced box once, give the gate a margin. One white-table sitting with vendor files.
2. Freeze the occlusion switches. Remove the five inert ones.
3. One experiment on the "both colors" dependence: stripe by signed contrast at the size the row predicts, then that barrel's own colors. Judged by place, with a pass rule above the noise floor.
4. Re-run "blue follows the light" under a sane rule, with more than two warm places.
5. Two questions for Dave: can exposure and white balance be locked, and is a per-place calibration or a small learned verifier allowed.

## 7. Where I was wrong, and limits

- I guessed sensor clipping caused the ottoman's orange shift. Refuted: no orange pixel there is saturated. The cause is not identified.
- I guessed one physical light shift would describe the color movement. Refuted.
- Nothing here was built or tested as a detector.
- The vendor being a trained model is an inference at about 90 % confidence. VEX does not name the method.
- "Surface matters more than lamp" is confounded with room, daylight and lamp aim.
- The vendor score count read vendor files of test frames, boxes and scores only.
