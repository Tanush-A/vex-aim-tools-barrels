# EXPERIMENTS.md — lab notebook

One entry per experiment, newest first; the index is the fast path, the entries carry the tables. Template at the bottom.

**Now (2026-11-16):** step-3 frames split and looked at through H × S histograms (entry 2026-11-16): the fixed model keeps about half of the orange and a third of the blue body on wood. Before that (2026-11-09): the front end is the hs model `eb863d84` and the detector has hardening a–g. Numbers that define the state: campus train v2 **0.99** vs 0.41 for the v1 front end, home LOSO **0.93**, no false detection on any negative of either session, median box width / true width 0.96 (entries 2026-11-08 later, 2026-11-09 ×2). Test frames: untouched since the v1 pixel test of 2026-10-20.

## Index (newest first; the headline of each entry)

| date | experiment | headline |
|---|---|---|
| 2026-11-27 | **The barrels' colors as histogram peaks** (Tanush's idea; branch `wip/exp-peaks`; leave one place out; nothing adopted) | Barrels are their own small peak in nearly every frame but rarely the biggest. Counting only pixels in a stripe sandwich of the two colors finds the barrel peak in about 9 of 10 frames. As a color step: PASS +14.0 (32 gained, 1 lost); fixes the ottoman and the gray table, not the warm bathroom. Below stripe by contrast (+21.5) |
| 2026-11-27 | **White balance, then the fixed colors** (branch `wip/exp-whitebalance`; tests what Dave's 2026-10-07 rule forbids, run for numbers only; pre-registered, leave one place out) | Full corrections all FAIL on boxes (they turn the warm-bathroom orange pink and the dark ottoman fabric blue). Gray world at half strength PASSES: 133.8 → 143.0 of 172 (+9.2), 38 gained, 6 lost (ottoman), boxes off a barrel 1.93 → 1.05. 34 of its 38 gains are already found by the ideas that change no pixel (33 by stripe by contrast, which is +21.5). Correction cannot fix the ottoman's orange. Plainly: the rule against correction costs about 4 barrels here |
| 2026-11-27 | **The winners together (E8)** (branch `wip/exp-combined`; pre-registered plus a dated addendum; nothing adopted) | **Contrast alone is the answer:** 133.8 → 155.3 of 172 placements held out; adding near-miss or self-calibration gains 0.2 to 2.7 more, never above the noise, and brings their clutter boxes. Contrast finds 44 of the 50 barrels the other two gain, plus 20 neither finds. **Against the vendor** (six measured places, train): contrast 92.3, vendor 83.3, today 70.8 of 108 placements; boxes off a barrel 2.83 against the vendor's 3.00. It still loses at the gray table (15.0 against 16.0) and the ottoman (10.0 against 12.3). What is left after contrast: 16.7 placements, nearly all hidden or frame-cut (15.0). Methods were shaped on these frames; the vendor's were not |
| 2026-11-26 | **Slack in the stripe tests (E9)** (branch `wip/exp-slack`; pre-registered, two rounds; missed its own success line) | One pixel shaved off every painted region loses 40 barrels on the ordinary frames. Best rule `slack=D`: a stripe refused as too thin is measured again from the gap between the bodies; one refused as too small is asked again only when the barrel's own top and bottom show where its row predicts. It brings back 11 of 40 (target was 14) and 55 of 107 at two pixels, adds no box off a barrel on any of 5435 masks or any empty frame, and changes nothing that matters on unharmed frames (NO CLEAR DIFFERENCE, +1.6). Forgiving exactly one failed test barely helps: one pixel fails several tests at once |
| 2026-11-26 | **A barrel 60 % hidden at the side (E7, B9)** (branch `wip/exp-sidecut`; pre-registered, one round; not recommended) | Place the box from the side that bulges (the barrel's own side; a cut side is straight). In simulated side cuts the cliff mostly goes: at 60 % hidden 151 → 269 of 312 found, at 75 % 28 → 195, no simulated box off a barrel. Both real straight-edge frames are now found (`occlx_02`, `occlx_03`; seen during development). But on ordinary frames: NO CLEAR DIFFERENCE (+2.0), one new box on a tin's red and blue label on glass, and one box on the wrong side of a dark-shaded ottoman barrel; real own sides bulge only half of what the camera model predicts. Failed four of eight pre-registered clauses |
| 2026-11-26 | **The stripe by color difference, then the barrel's own colors** (branch `wip/exp-contrast`; pre-registered, leave one place out; nothing adopted) | A band redder or bluer than the body above and below it by a margin, at the size the row predicts, proposes a barrel; that barrel's own colors are painted and its boxes ADDED to today's. As a finder it has a candidate on 211 of 211 clean barrels, 63 of 63 that the fixed colors miss. Judged: **PASS, 133.8 → 155.3 of 172 placements (+21.5)**, 64 gained, 0 lost, no box on any empty frame, boxes off a barrel 1.9 → 2.8. Bathroom 4.0 → 13.5, ottoman 3.0 → 10.0, gray 10 → 15; the other five places do not move. Painting into the fixed mask instead FAILS on boxes. Out of reach: the very dark ottoman, lamp brightness 1, close-ups with the stripe below the frame. Caution: four guard numbers were read off an in-sample table of all eight places |
| 2026-11-26 | **The bottom edge (K2, B8)** (branch `wip/exp-bottom`; pre-registered, two rounds; nothing adopted) | The flaw is smaller than thought: 2 to 13 boxes per color step fail only by the bottom edge. Recommended rule `bottom_rule=low_uncut`: a seen bottom more than 10 % below the predicted one is drawn at the predicted row, unless the stripe touches the frame side. NO CLEAR DIFFERENCE everywhere (no PASS was possible at this size); over five "more paint" color steps found +5.9 placements, the bottom-edge failures 35 → 24, far bottoms outside the scorer's tolerance 11 % → 0 at the loosest step; fixed colors unchanged (1 gained, 1 lost). The frame-side exception was chosen after round 1 |
| 2026-11-26 | **Near-miss colors next to strong evidence** (Tanush's idea; branch `wip/exp-nearmiss`; pre-registered, leave one place out, 28 candidates judged; nothing adopted) | A pixel outside the range counts only where the partner color says a barrel is: a loose stripe between two strict body pieces, a loose body around a strict stripe, never past the top and bottom the row predicts. 133.8 → 147.5 of 172 placements (+13.7, PASS, not weak), 211 → 249 per frame, 38 gained, 0 lost, no box on a clean empty frame; boxes off a barrel 1.9 → 3.6 (margin +1.85: close). Plain two-level thresholds FAIL (the home wall floods). The stripe direction alone is free: +7.2, no new paint outside the boxes. Conditioned like this the loose level can go to the loosest range; false boxes start only when the color test is dropped. Out of reach: a barrel with neither color in the strict range (warm bathroom 1 → 1 of 15). The 7 new boxes: 3 on a jar's label on the glass table |
| 2026-11-26 | **K1: the detector collapsed** (`wip/collapse`, merged; proof harness in `experiments/2026-11-26_collapse`) | 51 settings → 20 numbers, no switch, no mode; `detect` is ten named stages; 7 dead rules and the stage-1-alone mode deleted; each box carries its own evidence. Boxes identical on 5435 masks (6152 boxes: every train frame, each with one pixel shaved off and added, the hand-threshold frames, the damaged masks, all 3888 simulated scenes), checked after each of nine steps and once more independently. Tests 930 → 907 (27 removed with their deleted subject); 952 with the measurement work. The map is rewritten for it (435 lines from 760) |
| 2026-11-26 | **The barrel as its own color reference** (branch `wip/exp-selfcal`; pre-registered, leave one place out; nothing adopted) | A half-found barrel completes itself (the color that is not painted is read where the geometry says it must be), and found barrels set that frame's ranges: 133.8 → 147.6 of 172 placements (+13.8, PASS, not weak), 211 → 248 per frame, no barrel lost, no box on an empty frame, boxes off a barrel 1.9 → 2.2. Gains: gray table +5.0, bathroom +5.8, ottoman +3.0; the other five places do not move. With the guards off: FAIL (29 boxes off a barrel). Out of reach: the warm ottoman (neither color painted), touching blue barrels under the bathroom lamp. Caution: the method was shaped while looking at all eight places |
| 2026-11-26 | **What a setting per place can reach, without sliders** (branch `wip/exp-place-ceiling`; pre-registered, two rounds; nothing adopted) | A rectangle pair per condition is enough: the oracle finds 163.2 of 172 placements (fixed 133.8, hand 156.8), 0 boxes off a barrel, and its 13 misses are all hidden or frame-cut barrels, none a color case. On the six measured places: fixed 70.8, one calibration frame 93.8, hand 93.8, vendor 83.3 of 108. The warm bathroom was a slider limit: blue at hue 26–44 paints the barrels, not the floor (14 of 15 found; hand 6, vendor 0); 12 threshold proposals written for review. One frame setting the place, as registered, FAILS: +8.0 placements but campus 35 → 21 (its ranges come out too narrow). Post hoc "keep the fixed colors when they find every barrel on the calibration frame": 156.6, PASS on 4 of 5 frame choices. A setting from another place is worse than fixed (53.5 % against 69.4 %) |
| 2026-11-26 | **What to read the light from; blue follows the light, a clean try** (branch `wip/exp-light`; pre-registered, one round, leave one place out; nothing adopted) | 13 ways to read the light: the best is the brightest pixels that are not barrel-colored (r −0.96 with the blue paint's saturation; a close orange barrel no longer fools it); pixels with almost no color fail (under a yellow lamp those are the blue barrels). No reading predicts the orange hue. Blue ramp: +3.9 placements, 14 barrels gained, 0 lost, NO CLEAR DIFFERENCE (margin +4.0). With "bluer than the light": +11.9 (bathroom 4.0 → 14.25 of 15) but FAIL, 16 more boxes on clutter that is orange with a blue band; in-sample with the cautious setting +11.4 and 1 box. The setting does not transfer between the only two warm places |
| 2026-11-26 | **M3: the standard pass rule** (`tools/judge.py`; pre-registered sanity checks) | One rule for every experiment: PASS / FAIL / NO CLEAR DIFFERENCE from four clauses with measured margins; fitted candidates leave one place out. Today's detector against itself: no difference. 26 changes that mean nothing: all no difference; 12 unseen ones: 1 PASS, 1 FAIL. Hand thresholds per condition: PASS (+23.0 placements). "Blue follows the light" leave one place out: PASS, weak (+5.9 against a margin of 4.0) |
| 2026-11-26 | **M2: the noise floor** (pre-registered; one dated addendum) | A change that means nothing (one hue unit, three saturation units) moves found over the ordinary conditions by up to 10.92 placements down and 4.00 up; one condition by up to 6 barrels (the ABP gray table sits on a hue edge); never a box on a clean empty frame. The never-regress check now has margins and six protected sets; it passes on today's defaults |
| 2026-11-26 | **M1: every placement once, a misplaced box once** (`report.py --places`) | The 243 new train barrels are 108 placements at 6 places. Per placement: ours 70.8, vendor 83.3 of 108 (per frame 148 / 177, reproduced exactly). The vendor's 30 "false boxes" are 23 boxes on a barrel that fail the strict rule and 7 on nothing; ours 2 and 5. With the two white tables where the vendor is ASSUMED perfect: 133.8 against 147.3* of 172 |
| 2026-11-25 | **The test look (TODO G)** (pre-registered, one configuration: `wip/final`) | Home 9 of 9 (score 1.00), campus 22 of 24 (0.94). New conditions, frames with vendor files: ours 14 of 32 (4 false), vendor 23 of 32 (5). Verify step on unseen frames: same barrels, false 9 → 6. Glass worse than on train (6 of 10). `results/2026-11-25_test_look_summary.md` on `wip/final` |
| 2026-11-25 | **Color step with ~8 places** (`wip/color`; pre-registered, two rounds; nothing adopted) | Warm-bathroom blue reads hue 26–44 (outside the blue range); ottoman stripes partly under the brightness gate; slider tool extended. No histogram relation leave one place out. Re-centred constant 212 / 11 vs fixed 211 / 13; light rule 233 / 19 with 3 boxes on empty frames; both fail. 138 non-monotone events, 65 from the bottom tolerance. |
| 2026-11-25 | **Verify step against false boxes** (`wip/occl-strict`; pre-registered) | Logical audit of every box-making rule against six barrel facts. `verify_front` + `verify_readings`: real no-barrel boxes 6 → 2, false 20 → 15, 0 real lost (237 / 237), gate passes on all new data; scorecard no-barrel 48 → 23. |
| 2026-11-24 | **Box proposals by Claude, checked against Tanush's boxes** (12 train frames he had boxed, proposed blind) | 27 of 27 barrels found, 0 extra, 0 color mistakes; IoU median 0.89 (worst 0.80); edges median 1 px, worst 5 px; proposals sit about 2 px inside on the left and top; 3 flag / `clean` differences in 12 frames. Tooling merged (`box_look.py`, proposals in `box_tool.py`). `results/2026-11-24_box_proposals/` |
| 2026-11-24 | **Overnight: vendor, adaptive, close-up, bulge** (`OVERNIGHT-2026-11-24.md`) | Vendor files sound (center slope 1.99 / 2.03, IoU 0.82); ours 59 / 123 (6 false) vs vendor 99 / 123 (8) on 7 new conditions, gap = color on ottoman and gray. Adaptive: 6 places, 3 labelled, no relation leave-one-place-out; pre-registered rule fails (+1 barrel, ottoman worse, 1 box on an empty frame); frozen for tomorrow. Close-up: `closeup_side` + `closeup_stripe` remove the fruit box on `occlx_15`, find palewood `close_01`, nothing else moves, gate passes. Bulge (own side): barrel-cut ends are flat on the mask (853 ends), no separation; `own_close` makes 0 wrong-side calls in 400 but loses 3 same-colored-pair scenes; stays off. |
| 2026-11-20 | **A cut stripe, and a sliver with stripe and body** (A8; pre-registered, two rounds; branch `wip/occl-sliver`, waits on Tanush) | On: `thin_span` (stripe-colored block hiding 75 % 3 → 77 of 100; scorecard 2737 → 2811, wrong boxes 45 → 45, gate passes, nothing else moves). Off: `stripe_bridge` (pieces on the same rows with body over every gap column are one stripe; 0 of 114 two-barrel pairs joined; bad day 547 (5) → 563 (0); fails on scorecard wrong boxes 45 → 48 and medium 3 → 4), `thin_frame` (frame edge 75 %: 29 → 88; fails "too big" 3 → 8 by 2–3 px), `own_close` (own side by closure, right in 1330 of 1330 calls on full slices; straight edge 28 → 57, slanted 0 → 62; fails where a back barrel's cut end follows a front barrel's round outline). Both sides cut at 75 %: no cue in the mask. Results on the branch: `results/2026-11-20_occl_sliver/verdict.md`. |
| 2026-11-20 | **Occlusion, combined** (five branches on `wip/occl-combined`, pre-registered against `wip/detector-occl`; waits on Tanush) | Scorecard 2153 (`barrels`) → 2417 → 2737 of 3888 found, boxes where no barrel is 88 → 45 → 45; home 28 / 1 / 0, campus 35 / 0 / 0, nothing on a negative; false boxes at every damage level unchanged against the stack. On: `half_stripe`, `half_thin` (cut from above or below to about half), `post_pair`, `stripe_wide` (same-colored pair), `cap_low`, `pin_outline`, `pin_thin` (a cut barrel placed by the rounded corners of its own side). Off: `slice_behind`, the cover box, the stencil verifier. Parts: damage realism (old "medium" is not white-table damage: real stripes whole on 37 of 38 barrels), occl_vertical, occl_pin (top arc 1 px, corners 10–17 px), stencil (alone 2233, fails never-regress; 10 wrong boxes against 45). Not possible from the mask: three quarters hidden by a non-barrel. Every number simulated. Results on the branch: `results/2026-11-20_occl_combined/` (`scorecard.md`, `walkthrough.md`, `verdict.md`). |
| 2026-11-19 | **Occlusion: the scorecard, and one idea** (pre-registered, two rounds; branch `wip/detector-occl`, waits on Tanush) | 3888 simulated scenes (50 free-standing train barrels, 25 / 50 / 75 % hidden by 15 kinds of thing), scored against the full box. Found 2401 → 2417 with the two parts that pass and are on (`edge_check`, `cap_same`); 3155 with `slice_box` + `cover_unpinned` + `stripe_two`, which are OFF: three quarters hidden by a straight edge 0 → 73 of 100, both sides 0 → 44 of 50, same color beside at a half 36 → 88 of 100; home 28 / 29 and campus 35 / 35 unchanged in every arm, nothing on negatives; but medium damage false boxes 1 → 4 (found 99 → 124 of 145), which breaks the rule. Not handled: hidden from above or below by half or more, a same-colored barrel straight in front. Results on the branch: `results/2026-11-19_det_occl/` (`scorecard.md`, `verdict.md`). |
| 2026-11-19 | **Hidden bottoms and the top row** (A5; one round; branch `wip/detector-bottom`) | Of the 62 boxes drawn on home + campus none takes its bottom from the top row. One rule, `cap_seen_bottom`: home 27 → 28 of 29 (`cluster_01` left orange), nothing else moves, 0 boxes change on 337 recorded frames. |
| 2026-11-18 | **Camera calibration from the ruler set** (TODO A4; pre-registered, two rounds; branch `wip/calibration`; nothing adopted) | The 12 ruler frames fit only with a lower camera: tilt 20.4°, height 40.2 mm (not 43.47), horizon row 91, 3 px rms against 14 for the camera in use. On the train boxes that camera fails the rule (bottoms from +4.4 / +5.4 px low to −8.1 / −6.7 high on home / campus, sizes 5–7 % large, home loses a barrel). Round 2 (height 40.2, tilt 20.95° read off home + campus): bottoms within 1 px, sizes within 2 %, home `cluster` 6 → 7 but home `occl` 4 → 3, so never-regress fails. Each session wants a tilt about 0.3° from the others. Camera unchanged. A bottom inferred from the box width is right to 1–2 px with any camera. Results on the branch: `results/2026-11-19_calibration/`. |
| 2026-11-18 | **Side occlusion and the misses left on good masks** (TODO A2 + A3; pre-registered, two rounds; branch `wip/detector-side`, awaiting walkthrough) | `side_hidden`: a partly seen stripe is placed by what is seen of the barrel, and a side counts as hidden only for a reason (frame edge, a found nearer barrel, body and stripe ending apart). Campus 34 → 35 of 35 (`occl_02`, overlap 0.82), home 27 of 29 unchanged, no row worse, nothing on a negative frame; medium damage 64 → 99 of 145 with false boxes 22 → 1; the campus clips gain 4 boxes, all real. `seam_height` passes and changes no real frame. `cluster_01`: the wedge barrel is not measurable; the second miss is the bottom predicted 10 px low. Results on the branch: `results/2026-11-19_det_side/`. |
| 2026-11-18 | **The detector given good segmentation** (pre-registered, two rounds; merged 2026-11-18) | Perfect home masks: 25 of 29 found; medium simulated damage 36 of 145; black with label thresholds 17 of 26. Two new switches, `cap_behind` (a barrel behind a found barrel, from its visible top) and `stripe_join` (a stripe in pieces): 28 of 29, 64 of 145, 19 of 26; eval-table home 25 → 27 of 29 with no false box, campus unchanged. No arm passes the rule by the letter (one box 7 px below a hand-estimated bottom on black `occl_04`; one wrong box in the wood clip, an extreme set); **Tanush decided 2026-11-18 that those two do not block it: both are on by default and merged.** Size check: expected sizes right (ratio 0.95–1.03); bottoms inferred from the top row 4–7 px low (horizon nearer row 80 than 76). Results: `results/2026-11-18_det_given_seg/` (`verdict.md`, `summary.md`, `by_eye.md`, `size_check.md`); method: `HOW-IT-WORKS.md` §3. |
| 2026-11-18 | **Histogram against thresholds: is there a relation?** (TODO F; pre-registered; run 01 is a DRY RUN) | 2 ordinary conditions, 8 needed: no conclusion. The pipeline runs end to end on the box-derived target (no hand labels yet). With the 7 extreme sets added (n = 9, optimistic: six are one wood table) the blue hue floor follows the whole-histogram hue shift (rho 0.91, Holm p 0.016) and the blue S floor is predicted better than both baselines; orange is not. Rules fit mostly on wood lose the ordinary sets (36 of 64 found vs 59 fixed). The box-derived thresholds used as a model find 53 of 64 on home + campus vs 59 fixed: a doubtful stand-in for hand labels. Rule, features, criteria: `experiments/2026-11-18_hs_relation/PREREG.md`; numbers: `results/2026-11-18_hs_relation/summary.md`. |
| 2026-11-16 | **Ceiling check: per-frame thresholds read from the frame's own labels** (not a method) | With perfect per-frame thresholds today's detector finds 17 of 26 on the black table and 36 of 126 on bright wood (cool lamp 24 of 42, mid 10 of 42, warm 2 of 42), with 31 false boxes on wood; base 2 and 7. Per-image thresholds can lift black and cool light to about two thirds and do nothing under mid and warm lamps, where the orange range paints the table. Remaining misses: stripes in pieces (refused for width / height / area). |
| 2026-11-16 | **The hs model fit on all train tables** (pre-registered; 3 arms, 2 runs) | **No arm passes.** Ranges wide enough to paint the barrels on wood paint the table too and cost home (0.93 → 0.66) ; ranges that keep home (0.89) and campus (0.93) leave wood unpainted. Best case found on black + bright wood: 28 of 152 (base 9). One fixed range for every table does not exist with this recipe. Nothing adopted. |
| 2026-11-16 | **Today's detector on the new train frames** (baseline, `tools/report.py --base-model default --out detector_on_new_sets`; no entry below, the table is `results/2026-11-16_detector_on_new_sets/report.md`) | Wood, brightness 3 and 6 (60 frames): 7 of 126 barrels found, 3 false boxes. Brightness 1 (30 frames): 0 of 63. Black table (10 frames): 2 of 26. Home 0.93, campus 0.99, Dave 0.47 unchanged. |
| 2026-11-16 | **Hue × saturation histograms** (TODO 8; a look, nothing tuned) | On wood the fixed hs model misses the barrels rather than painting the table: it keeps 46–73 % of the orange body and 30–48 % of the blue, floods 0.3–2.5 %. Hue drifts half a sector (orange 9 → 11–14, blue 110 → 99–106), on the black table too; blue S falls to ~100 under the warm lamp. Ceiling of any H × S lookup at 1 % flood: blue 99–100 % everywhere, orange on wood 66–91 % (warm worst). Brightness 1 dies on the V ≥ 40 gate. |
| 2026-11-11 | **A barrel hidden at the side: narrow stripe + hidden side from the body** (pre-registered; branch `wip/occlusion`) | `stripe_w_min` 0.4 → 0.25 with switch (h) finds campus `occl_02` (campus 34 → 35 of 35 found, IoU 0.68), +1 on Dave, 4 real edge barrels in the recordings, nothing lost, no false box on home / campus / Dave. But 2 false boxes on the 25 wood frames → condition 4 fails → **not adopted**, defaults unchanged, switches off. Tanush decides. |
| 2026-11-11 | **Occlusion attribution** (branch `wip/occlusion`) | 37 train frames: 5 misses, all occluded (5 of 10 occluded barrels found). 1 = hidden at the side by a non-barrel, stripe refused by the width test (16 px vs 21.4 needed; the live miss); 4 = behind a barrel of the other color, stripe merges with the front body, refused for height (step 9). |
| 2026-11-11 | **Eval report: one table** (TODO 6; branch `wip/eval-report`) | `tools/report.py`: set × scenario, candidate vs baseline with the delta. Reproduces home 0.93, campus 0.99, Dave 0.47; v1 + today's detector 0.39, v1 + 2026-11-05 detector 0.41. Every home / campus miss is in an `occl` or `cluster` row. |
| 2026-11-09 | **Close-up under a far barrel got no box** (hardening (g); branch `wip/redesign`) | Live run with Dave, `live/snapshots/robot_snap0.png`: the stripeless close-up was dropped as "covered" by a far barrel in the same columns. `cover_rows=True`: cover needs shared rows too. Candidate unchanged (campus 0.99, home 0.93, 0 FD; Dave 0.44 → 0.47). With the *old* finder + v1 pixels the same change lets clutter pieces through (5 FD on campus negatives), so the baseline arm pins `cover_rows=False` |
| 2026-11-09 | **Box width from the body, not the stripe** (hardening (f); branch `wip/redesign`) | Tanush saw thin boxes on `core_02`; the IoU ≥ 0.5 match passes a box 15 % too narrow. Box edges now from the body columns joined to the stripe (`body_width=1.2`), never into another stripe's columns. Campus train median width ratio **0.90 → 0.96**, worst 0.74 → 0.88; v2 score unchanged (0.99 / home 0.93). `width_ratio` added to the eval |
| 2026-11-08 | **The hs model scored on Tanush's campus boxes, per-class S floors** (18 configs; branch `wip/redesign`) | campus train v2: **v1 0.41 → hs 0.99** (`o5 b15 h5-95 m2`: orange 1.00, blue 0.97), home LOSO 0.93 = v1, nothing drawn on the campus negatives or Dave's desk; Dave 0.44 (indicative). First run with `held_01` unboxed: 0.97 and the proposed rule returned no winner (the found held barrel counted as a false detection); re-run after Tanush boxed it the same evening: the rule picks `o5 b15 h5-95 m2`. Remaining miss: `occl_02`, stripe hidden. Decision = Tanush's |
| 2026-11-08 | **Recordings replayed with the hs front end** | the detector now finds the barrels in every clip (static: 1 orange + 2 blue every frame — the second blue is blue clutter at the right frame edge, a persistent false box); 7 one-frame blips, all suppressed; every new track shown after 2 frames (the 3-of-4 rule); the hand clip loses and re-acquires the covered barrel as designed |
| 2026-11-08 | **The hs color model, pre-registered sweep** (24 configs; branch `wip/redesign`) | home LOSO v2 0.93–0.95 at the 15th–20th-percentile S floor (v1 0.93), 0.65–0.69 at the 5th (the bluish home wall); campus 14–19 of 21 right (v1 8); nothing on any negative except two 5th-percentile configs. **The pre-registered rule picked the 5th-percentile config (campus 19/21, home 0.69): the rule ignored the home score — a flaw in the rule.** Runner-up `s15 h5-95 m4`: home 0.93, campus 17/21, Dave 0.53. Not adopted: labels + walkthrough first |
| 2026-11-08 | **Detector hardening** (a–d, later (e); branch `wip/redesign`) | v1 pixels: home 0.91 → **0.93**, campus 7 → 8; hue pixels: home 0.57 → **0.78**, Dave 0.31 → 0.40, campus 12 → **15** / 21, extra-box frames 5 → 1, negatives clean. The dark-gap path back on makes every number worse |
| 2026-11-07 | **Segmentation probe: hue sector + HSV-saturation floor** (two iterations) | plain percentile boxes on hue wrap (orange 2–168) → boxes everywhere; done properly (hue shifted, S floor from the 10th percentile, 5–95 hue): campus 12 / 21 right (v1 7), Dave 0.31 (v1 0), negatives clean, **but home 0.57** — the bluish home wall (S ≤ 110) enters the blue class at an S floor of 92 and the old finder boxes its dark gaps. Led to the hardening and the sweep |
| 2026-11-07 | **Recordings replayed** (4 clips, detector vs the 3-of-4 view) | the detector as it stands finds almost nothing in the clips (room + clutter behind): 0 raw boxes in the static and enter/leave clips, 7 one-frame blips in the pan and hand clips, all 7 suppressed by the tracker, one track shown after 2 frames. **The clips cannot judge the tracker until the front end is replaced**; re-run then |
| 2026-11-07 | **Campus attribution** (21 train frames of the campus session, count-level truth) | 7 right, 9 segmentation-only, 5 segmentation + detector, 0 detector-only. The two top-row stages (background prior, saturation floor) and the RGB boxes remove the blue bodies and the shaded orange faces in a real room; where bodies survive the stripe step works, and its one failure is the pre-registered 'glued shadow'. **Segmentation first** |
| 2026-11-06 | **First live run** (Tanush's screenshots; a diagnosis, approximate) | the stripe step took a dark gap under a false orange smear for a *shadowed* stripe (the floating box) and dropped the real stripe (band + glued shadow 92 rows, 83 allowed); the blue barrel right in every frame; the segmentation labels the laptop lid's edge, a barrel's glow and skin orange. Raw frames needed |
| 2026-11-03 eve | **Detector step 2 (the stripe) vs steps 1–3 vs the floor**, Tanush's boxes | v2 rule: floor 0.43 → steps 1–3 0.71 → **stripe 0.91**; overlap rule 0.48 / 0.86 / 0.97; misses = hidden stripes. Re-run 2026-11-05: identical |
| 2026-11-03 | **Dave's 20 snapshots** (outside check) | **0 barrel pixels on all 20**: the per-image floor and wall model assume plain top rows; the pink desk floods orange. The front end is the bottleneck |
| 2026-11-03 | Detector step 1 vs the CC floor (auto instances; provisional) | 0.78 vs 0.46 mean F1; bottoms within 1 px |
| 2026-11-03 | Camera re-fit from labeled boxes | the October preset put bottoms ≈ 20 px low; boxes pin horizon row ≈ 76 (tilt 22.25° at f 400), not f and tilt separately → `AIM_4A8B6118_BOXFIT` |
| 2026-10-28 | Pixel cleanup flags (LOSO CV) | tie (best +0.010); v1 unchanged |
| 2026-10-28 | Detection floor: CC reference detector (provisional) | 0.63 with perfect pixels, 0.45 with v1's: touching barrels merge |
| 2026-10-22 | Where v1's errors come from | 21 % of blue lost to the saturation floor (shadowed faces); orange FPs = lid reflections + the hand; table prior off is right |
| 2026-10-20 | Per-image saturation floor vs fixed; synthetic shift probe; second test run | tie on real data (0.809 vs 0.810); under a cool cast the fixed floor floods negatives (7.7 %), the band floor stays at 0; test 0.843 / 0.813 |
| 2026-10-20 | v1.5 arms: barrel-referenced re-fit, YUV chroma box | no gain with one light (re-fit −0.07, YUV tie); kept behind flags |
| 2026-10-20 | v1 on the held-out test set (once) | orange IoU 0.844, blue 0.811, 0 false pixels on the negative |
| 2026-10-20 | v1 RGB box: ablations and sweeps (LOSO CV) | final `ee36a1e9`, CV 0.810; floor + wall prior do the work; box alone 0.04; horizon 90 rejected (hand); table prior off |
| 2026-10-20 | Barrel color distribution in RGB | brightness-elongated smears; a box alone admits 55–86 % of table/wall |
| 2026-10-19 | Camera geometry of AIM-4A8B6118 | f 355–405 px, tilt 21.5–25.5°, horizon row 55–100; gate at 50 |
| 2026-10-07 | Color baselines: fixed HSV vs lighting | fails under warm light (blue stripe 17 % recall, wood 70 % flagged orange); adaptation needed |
| 2026-10-07 | Lab 6: aivision + world-map accuracy | map ≈ 1 cm at 9–14 cm; aivision returns no box for close barrels |

---

## Experiment-log entry, ready to paste into `docs/EXPERIMENTS.md`

### 2026-11-27 — The barrels' colors as peaks of the frame's own histogram (branch `wip/exp-peaks`)

Tanush's idea: barrels show up as peaks in the histogram; read their colors from the peaks. Plan: `experiments/2026-11-27_peaks/PREREG.md`, committed before any judged run; one round plus two report-only diagnostics (dated addendum). Train frames only. Nothing adopted. Written from the agent's report (its harness refused report files).

- **Do barrels show up as peaks?** Yes, as their own small peak in 96 of 97 orange frames and 87 of 92 blue frames (hue × saturation). It is the biggest peak in its hue region in only 28 of 97 (orange) and 53 of 92 (blue): the floor or the wall is bigger. The barrel peak is clean: 88–100 % of the pixels near it lie inside a hand box.
- **Which finder picks the barrel peak** (in-sample; within 3 hue units / fooled by 5 or more):

| finder | orange (97) | blue (92) | extreme orange (35) |
|---|---|---|---|
| every pixel | 38 / 56 | 68 / 22 | 7 / 26 |
| saturation-weighted | 75 / 21 | 83 / 9 | 9 / 25 |
| rows below the horizon | 45 / 50 | 69 / 22 | 7 / 26 |
| barrel-sized regions | 68 / 27 | 56 / 36 | 8 / 25 |
| only pixels in a stripe sandwich of the two colors ("pair") | 82 / 11 | 88 / 4 | 28 / 2 |
| pair + barrel-sized | 89 / 4 | 88 / 3 | 29 / 2 |

- **Judged, leave one place out** (baseline 133.8 of 172 placements, 211 of 307 per frame, 1.93 boxes off a barrel):

| candidate | verdict | placements | per frame | gained / lost | boxes off a barrel |
|---|---|---|---|---|---|
| pair + barrel-sized (primary) | FAIL (pale wood −2) | 131.8 | 209 | 0 / 2 | 1.93 |
| **pair** | **PASS (+14.0)** | **147.8** | **242** | **32 / 1** | **3.45** |
| saturation-weighted | FAIL (pale wood) | 142.7 | 230 | 21 / 2 | 3.53 |
| every pixel | FAIL | 131.3 | 207 | 0 / 4 | 4.53 |
| primary, then self-calibration | FAIL (pale wood) | 146.6 | 249 | 40 / 2 | 2.43 |
| pair, then self-calibration (diagnostic) | FAIL (boxes) | 152.8 | 261 | 51 / 1 | 5.37 |

- **Why the primary failed:** one frame and one hue unit. On `overheaddim_palewood_clutter_01` the primary's blue range moved its lower edge from 103 to 100 and both barrels there were lost; the pair finder moved it to 101 and kept them. The finder itself is as good (+12.3 with the pair's setting); the detector's fragility decided it.
- **What it fixes:** the ottoman (orange at hue 14–17, the range widens to reach it), the gray table (orange at hue 1–2), and in the report-only wood lamp ladder 2 → 30 barrels per frame. **Cannot:** the bathroom under the mid and warm lamp (+1): the blue there is no longer blue (saturation 40–80). New boxes off a barrel: the glass jar's blue and red label (3 frames), one too-high box on wood, a bathroom floor edge, a second box on a home barrel.
- **Takeaway.** Barrels are peaks, but small ones; a peak counted only over the stripe pattern is the barrel's color in about 9 of 10 frames. As a color step it passes (+14.0), level with near-miss and self-calibration and below stripe by contrast (+21.5). It wins at the ottoman and the gray table, where self-calibration wins at the bathroom; stacked they find more but fail on clutter boxes.
- **Next.** Nothing on its own; stripe by contrast already covers these barrels. The pair finder is a cheap check of a frame's colors if one is ever wanted.

## 2026-11-27 — White balance in memory, then the fixed colors (an experiment the standing rule forbids; branch `wip/exp-whitebalance`; nothing adoptable without Dave)

> **This tests something the standing rule forbids.** Dave, 2026-10-07: "never white-balance or otherwise correct
> the image". Tanush, 2026-11-27: "we can try correction too, like white balancing, worth a shot". Run as an
> experiment only, to give Tanush and Dave numbers. **Nothing here may be adopted without Dave.** No corrected image
> was written anywhere; the correction lives in memory inside the candidate and is dropped after the frame.

Plan: `experiments/2026-11-27_whitebalance/PREREG.md`, committed before part B and before any judged run. One round.
Nothing that runs by default was changed. `detector.py` and `pipeline.py` were not edited.

##### Hypothesis

1. Per frame, read the light's color from the frame, divide it out (one gain per channel), and today's fixed colors
   and detector find more barrels, held out, without boxes on things that are not barrels.
2. Written before the runs, from the color review: it helps blue under the warm lamp; it cannot fix the ottoman's
   orange (that follows the surface, not the lamp); and a full correction that brings blue back pushes orange out of
   its range under the same lamp, because the two paints move in opposite directions.

##### Method

- **The correction.** An estimator reads the light L = (R, G, B). Gains g = (mean(L) / L) ^ alpha, each held in
  [0.25, 4]. The photo times the gains, held in 0..255. Then `pipeline.segment` with the adopted model (`eb863d84`)
  and `detector.detect` with defaults. Dark (< 40) and clipped (≥ 250) pixels are never read.
- **Five estimators.** Gray world (mean of the frame). White patch (brightest 5 %). `without_loose` (brightest 5 %
  after taking out anything barrel-like; the best light reading of `wip/exp-light`). Gray world above the horizon
  (rows 0–49). Shades of gray (p-norm, p = 6).
- **Candidates.** F1–F5: full correction (alpha 1), nothing chosen. P1–P5: alpha chosen inside each fold from
  {0.25, 0.5, 0.75, 1}, no correction as the fallback; P3 (`without_loose`) the primary. U3: today's mask kept, the
  corrected paint added only where today paints nothing.
- **How alpha is chosen.** The light experiment's rule: on the other seven places, a setting the pass rule calls FAIL
  is out; the highest (Δ found − Δ boxes not on their barrel) wins; ties go to the smaller alpha.
- Code: `wb.py` (correction, estimators, callables), `measure.py` (part B), `candidates.py`, `run.py`, `sheets.py`,
  `compare.py`.

##### Data

Train frames only. Judged: 154 ordinary frames, 17 conditions, 8 places, 172 placements (307 barrels counted per
frame). Part B also on the 77 extreme and 30 excluded frames. Extreme frames printed, never judged. No test frame
was loaded, viewed, scored or listed.

##### Results

###### B. What the correction does to the paint, before any judging (`results/2026-11-27_whitebalance/measure.md`)

Share of the paint pixels the fixed model paints the right class (percent). Before → after, full correction.

| condition | orange, gray world | blue, gray world | orange, `without_loose` | blue, `without_loose` |
|---|---|---|---|---|
| bathroom, warm lamp | 99 → **4** | 0 → **98** | 99 → **9** | 0 → **95** |
| bathroom, mid 6 | 99 → 93 | 5 → 99 | 99 → 96 | 5 → 97 |
| bathroom, mid 3 | 97 → 92 | 2 → 97 | 97 → 96 | 2 → 93 |
| bathroom, cool | 96 → 97 | 38 → 99 | 96 → 98 | 38 → 98 |
| ottoman, warm | 32 → 15 | 0 → 84 | 32 → 27 | 0 → 84 |
| ottoman, mid 6 | 26 → 14 | 56 → 85 | 26 → 22 | 56 → 84 |
| ottoman, cool | 13 → 13 | 65 → 86 | 13 → 25 | 65 → 86 |
| gray table (ABP) | 31 → 43 | 95 → 96 | 31 → 32 | 95 → 95 |
| pale wood | 95 → 82 | 95 → 97 | 95 → 95 | 95 → 95 |

Over the 17 ordinary conditions (mean of the condition shares):

| setting | orange paint in | blue paint in | non-barrel painted, orange / blue | pale wood | bathroom (4 lamps) |
|---|---|---|---|---|---|
| no correction (today) | 81 | 67 | 1.3 / 0.8 | 8.8 | 2.2 |
| gray world, full | 73 | 96 | 0.3 / 1.1 | 0.8 | 0.7 |
| white patch, full | 71 | 97 | 0.6 / 11.5 | 7.8 | 6.4 |
| `without_loose`, full | 76 | 95 | 0.9 / 1.3 | 10.3 | 0.5 |
| gray above the horizon, full | 74 | 95 | 0.4 / 1.2 | 2.5 | 0.7 |
| shades of gray, full | 72 | 94 | 0.4 / 3.7 | 1.9 | 0.6 |
| gray world, half | 80 | 87 | 0.6 / 0.8 | 1.3 | 1.3 |
| `without_loose`, half | 81 | 85 | 1.4 / 0.8 | 9.5 | 2.5 |

- **The expectation holds.** Blue comes back almost everywhere (67 % → 94–97 % of blue paint). Orange goes out:
  under the warm bathroom lamp the full correction turns the orange body pink (hue 8 → −3 to −6, 99 % → 4–9 %).
- **The ottoman's orange is not fixed.** Its hue stays 15–18 after every correction (the range ends at 13).
- **Half a correction keeps both** in the warm bathroom (gray world: orange 96 %, blue 65 %).
- **Gray world takes the orange flood off the pale wood** (8.6 % → 0.2 % of the non-barrel pixels): the wood becomes
  gray. `without_loose` does not (it reads the white things on that table, so it barely corrects there).
- **The dark ottoman turns blue.** Under the warm lamp `without_loose` paints 8.3 % of the fabric blue (gray world
  2.4 %). On the very dark ottoman (extreme) gray world paints 25 % of it blue.
- **The 2026-10-07 failure, seen again:** on the orange wood desk (extreme) gray world paints 2.8–4.8 % of the
  background blue (it was 0 %).
- The home wall above the horizon: 0 % painted before and after, for every estimator.

###### C. The judged candidates (baseline 133.8 of 172 placements, 211 of 307 per frame, 1.93 boxes not on their barrel)

| candidate | verdict | found, placements | found, per frame | barrels gained / lost | boxes not on their barrel (per frame) | empty frames: clean / with clutter | places that moved |
|---|---|---|---|---|---|---|---|
| F1 gray world, full | FAIL | 141.8 (+8.0) | 239 | 39 / 11 | 4.52 (9) | 0 / 2.00 | bathroom +7.5, gray +2.0, ABP white +2.0, ottoman −1.7, campus −1, pale wood −1 |
| F2 white patch, full | FAIL | 137.0 (+3.2) | 228 | 34 / 17 | 6.97 (18) | 0 / 2.25 | bathroom +6.5, ottoman −1.7, campus −1, glass −0.6 |
| F3 `without_loose`, full | FAIL | 144.3 (+10.5) | 254 | 50 / 7 | 5.88 (14) | 0 / 1.98 | bathroom +9.0, ottoman +2.3, campus −1 |
| F4 gray above the horizon, full | FAIL | 141.6 (+7.8) | 246 | 46 / 11 | 6.42 (18) | 0 / 1.12 | bathroom +9.5, gray +1, home −1, pale wood −1, ottoman −0.7 |
| F5 shades of gray, full | FAIL | 138.2 (+4.5) | 232 | 32 / 11 | 4.85 (12) | 0 / 2.20 | bathroom +7.2, ottoman −3.0 (worse than its margin), campus −1 |
| **P1 gray world, partial** | **PASS** | **143.0 (+9.2)** | **243** | **38 / 6** | **1.05 (5)** | 0 / 0.20 | bathroom +8.0, gray +2.0, glass +0.2, ottoman −1.0 |
| P2 white patch, partial | NO CLEAR DIFFERENCE | 133.1 (−0.7) | 208 | 7 / 10 | 2.67 (8) | 0 / 0.00 | glass −0.4, ottoman −0.3 |
| P3 `without_loose`, partial (primary) | FAIL | 134.8 (+1.0) | 215 | 6 / 2 | 4.65 (7) | 0 / 2.00 | bathroom +1.0 |
| P4 gray above the horizon, partial | PASS (WEAK) | 138.5 (+4.7) | 234 | 30 / 7 | 2.47 (10) | 0 / 0.20 | bathroom +6.5, gray +1, home −1, pale wood −1, ottoman −1 |
| P5 shades of gray, partial | NO CLEAR DIFFERENCE | 132.7 (−1.1) | 208 | 3 / 6 | 0.80 (4) | 0 / 0.20 | glass +0.2, ottoman −1.3 |
| U3 `without_loose` added to today's mask | FAIL | 135.5 (+1.7) | 217 | 7 / 1 | 5.43 (10) | 0 / 2.00 | bathroom +1.0, ottoman +0.7 |

Margins: found better above +4.0; boxes not on their barrel worse above +1.85; empty frames with clutter worse above
+1.0; any box on a clean empty frame fails. No candidate put a box on a clean empty frame.

- **P1** picked alpha 0.5 in every fold, so it is one fixed setting: `wb.detect_frame_gray_world_half` (checked with
  `tools/judge.py --cand-callable`: the same PASS, 143.0, 243). Per frame: bathroom mid 6 1 → 15 of 15, warm 1 → 11,
  mid 3 1 → 7, cool 13 → 15; gray table 10 → 12; window glass 14 → 15; warm ottoman 0 → 3; ottoman mid 6 6 → 2,
  cool 3 → 1. All 6 barrels it loses are on the ottoman.
- **The primary, P3, failed** because of the pale wood. With the pale wood among the training places every alpha
  above 0.25 is FAIL there, so seven folds took 0.25 (+1.3, almost nothing). With the pale wood held out, the fold
  took 0.75, and on the pale wood that drew boxes on the orange-flooded wood (one on an empty frame with clutter).
- All five full corrections FAIL, three of them with found well above the margin (+8.0, +10.5, +7.8): the boxes
  sink them.
- Extreme conditions, report only (P1, per frame): wood under the lamp 7 → 64 of 126 (cool 6 2 → 16, mid 6 1 → 17,
  warm 6 0 → 13); very dark ottoman 1 → 0; black table no change.

###### What the pictures show (`results/2026-11-27_whitebalance/sheets/`, all looked at)

- **Gained**: real barrels. Blue barrels and blue stripes in the bathroom, painted solid blue after correction; the
  gray table's orange barrels; a blue barrel behind a purple figure on the glass table.
- **Lost (P1, all ottoman)**: orange barrels whose orange sits at hue 13–15. A small blue gain (1.08 to 1.17) pushes
  it out of the range. The orange under the warm bathroom lamp under the full corrections turns pink and is lost
  (`lampwarm6_bathtile_close_01`).
- **New boxes not on a barrel**: (1) the dark woven ottoman under the warm lamp turns blue in patches and gets boxes
  (F3, F1); (2) the orange-flooded pale wood gets a box when the gains move by only 2–4 % (F3, P3, U3); (3) the jar
  with an orange body and a blue band on the glass table (several candidates; it is a barrel to the detector); (4)
  P1's three: the jar (`window_glass_clutter_01`, `lampcool6_glass_neg_02`) and a wrong-color box on two touching
  barrels in the warm bathroom.

###### D. Against the ideas that change no pixel (`results/2026-11-27_whitebalance/compare.md`)

Barrels counted per frame, judged frames. "None of the three" = not gained by contrast C1, near-miss or self-calibration AB.

| candidate | gained | also by contrast | also by near-miss | also by self-cal | none of the three | lost |
|---|---|---|---|---|---|---|
| P1 gray world, partial | 38 | 33 | 15 | 18 | 4 | 6 |
| F3 `without_loose`, full | 50 | 41 | 24 | 26 | 7 | 7 |
| stripe by contrast C1 (+21.5) | 64 | | | | | 0 |
| near-miss (+13.7) | 38 | | | | | 0 |
| self-calibration AB (+13.8) | 37 | | | | | 0 |
| blue follows the light B1 (+3.9) | 14 | | | | | 0 |

- 34 of P1's 38 gains are gained by at least one idea that changes no pixel; 33 of them by the stripe by contrast
  alone. The 4 that are not: a gray-table barrel whose box was off, two half-hidden bathroom barrels, the blue barrel
  behind the purple figure.
- P1 loses 6 barrels; none of the other four loses any.

##### Takeaway

- **Correction does what the physics said.** Blue comes back under the warm lamp (bathroom blue paint 0–5 % → 95–99 %
  in range). Orange cannot be fixed on the ottoman, and under the same warm lamp a full correction pushes the orange
  out (99 % → 4–9 %).
- **Only half a correction works, and only gray world.** P1 passes (+9.2, boxes down by 0.9); gray world above the
  horizon passes weakly (+4.7). Full corrections find more (up to +10.5) and all fail on boxes on the dark fabric and
  the wood. The primary (`without_loose`) fails: the reading that is best for the light is not best for correction,
  because the pale wood's problem is the table, not the light, and only gray world sees the table.
- **It buys almost nothing the pixel-free ideas do not.** Contrast gains 64 barrels with none lost, and covers 33 of
  P1's 38. P1 costs 6 ottoman barrels.

##### For Tanush and Dave, in plain words

**Does correcting the image help?** A little, and only gently. Halfway gray-world correction finds 9 more placements
than today held out, with fewer stray boxes. Full correction finds about as many and draws boxes on the dark ottoman
and the wood.

**Does it buy anything the ideas that leave the image alone do not?** Hardly. The stripe-by-contrast idea finds 64
more barrels (counted per frame) without touching a pixel, and those include 33 of the 38 the correction finds. The
correction also loses 6 ottoman barrels that today finds. Only 4 of its barrels are new to the pixel-free ideas, so the rule "never correct the image" costs at most 4
barrels here. Not enough to argue against it.

**Why is it not more?** The two paints move in opposite directions under a lamp. Pulling the blue back pushes the
orange out. And the ottoman's orange is not a light problem at all.

**One useful thing it shows.** Gray world takes the orange flood off the pale wood table. That is the table's color,
not the light's. If that flood ever matters, it is a reason to look at the table color, not at correction.

##### Not done

- No second round. The obvious next tries (correct for blue only, keep orange from the photo; combine with contrast)
  would need an addendum first.
- No walkthrough with Tanush. `TODO.md`, `STATUS.md`, `EXPERIMENTS.md`, `DECISIONS.md` were not edited.
- The run's own date stamp in `summary.md` and `chosen.json` reads 2026-11-26 (the machine's clock).

## 2026-11-27 — The winners together (TODO E8, branch `wip/exp-combined`; pre-registered, one round plus one dated addendum; nothing adopted)

**Question.** Three color-step ideas passed the standard pass rule on 2026-11-26, each alone: near-miss colors
(`nearmiss`), the barrel as its own color reference (`selfcal`) and the stripe by color difference (`contrast`).
Put together, do they find more than the best one alone, without more boxes off a barrel? The owner wants the
simplest thing that works.

**Answer.** **Contrast alone.** It does most of the work. Nothing added to it is above the noise.

- Contrast alone: 133.8 → **155.3** of 172 placements (+21.5, PASS), 211 → 275 of 307 per frame, 64 barrels gained, 0
  lost. Boxes off a barrel 1.93 → 2.83. No box on an empty frame. 90 ms per frame (today 46).
- The best mix of the first two (`mask_union`): 152.8. Below contrast alone by 2.5.
- Contrast plus anything: at most +2.7 placements over contrast alone (all three together, boxes merged). The judge
  calls that NO CLEAR DIFFERENCE. Four of the six mixes with contrast FAIL against today on boxes off a barrel.

**Method.**

- Branch `wip/exp-combined`, from `barrels` after the collapse. The three winners merged in.
- `src/barrels/combined.py` (called by nothing by default; 30 unit tests). It holds twelve ways to run the winners on
  one frame. None has a number of its own.
- **Every number** is each winner's own, picked by that winner's own rule on the training places, for that winner
  alone. The mixes are never scored while fitting. Judged leave one place out, by the standard judge.
- **Step A first.** Each winner alone on the collapsed detector gives exactly its judged pages: totals, places,
  conditions, every changed barrel and box, every fold's pick. Near-miss 147.47, self-calibration 147.55, contrast
  155.30. Zero differences. Three unit tests were ported (`detector._stripe_geometry` is now
  `detector.BarrelAt.from_stripe_row`). No module needed a change.
- `PREREG.md` was committed before any mix ran (7347008). Contrast came in later, by a dated addendum, committed
  before it ran on this branch (a52f0b1).

**Data.** Train frames only. 154 ordinary frames, 8 places, 172 placements. 77 extreme frames reported, never
judged. No test frame was loaded, viewed, scored or listed.

**Results: the first two winners together** (against today's detector).

| candidate | verdict | found, placements | per frame | gained / lost | boxes off a barrel | ms per frame |
|---|---|---|---|---|---|---|
| today | | 133.8 | 211 | | 1.93 | 47 |
| `nearmiss` alone | PASS | 147.5 | 249 | 38 / 0 | 3.57 | 83 |
| `selfcal` alone | PASS | 147.6 | 248 | 37 / 0 | 2.18 | 88 |
| near-miss, then self-calibration on its mask | FAIL (boxes +2.63) | 151.9 | 260 | 49 / 0 | 4.57 | 162 |
| self-calibration, then near-miss on its mask | FAIL (boxes +2.38) | 153.1 | 262 | 51 / 0 | 4.32 | 161 |
| **the two masks together (`mask_union`)** | **PASS** | **152.8** | 261 | 50 / 0 | 3.32 | 138 |
| the two box lists merged | PASS | 152.8 | 261 | 50 / 0 | 3.57 | 160 |
| a new box only when both draw it | PASS | 143.2 | 237 | 26 / 0 | 2.18 | 160 |

`mask_union` against each winner alone: PASS (+5.3 and +5.2, weak). So the two are worth having together. But
contrast alone beats the pair.

**Results: with contrast** (against today, and against contrast alone).

| candidate | against today | found | per frame | boxes off a barrel | against contrast alone | ms per frame |
|---|---|---|---|---|---|---|
| **contrast alone** | **PASS** | **155.3** | 275 | 2.83 | | 90 |
| contrast on top of near-miss | FAIL (boxes +2.28) | 157.0 | 278 | 4.22 | no clear difference (+1.7) | 155 |
| contrast on top of self-calibration | PASS | 155.5 | 275 | 3.58 | no clear difference (+0.2) | 131 |
| contrast on top of `mask_union` (all three) | FAIL (boxes +2.78) | 157.7 | 278 | 4.72 | FAIL (boxes +1.88) | 180 |
| contrast and near-miss, boxes merged | FAIL (boxes +2.28) | 156.6 | 277 | 4.22 | no clear difference (+1.3) | 205 |
| contrast and self-calibration, boxes merged | PASS | 155.7 | 276 | 2.83 | no clear difference (+0.4) | 177 |
| contrast and `mask_union`, boxes merged | FAIL (boxes +2.03) | 158.0 | 279 | 3.97 | no clear difference (+2.7) | 229 |
| `nearmiss` / `selfcal` / `mask_union` | | 147.5 / 147.6 / 152.8 | | | FAIL / FAIL / FAIL (−7.8, −7.8, −2.5) | |

By place, contrast alone: gray table 10 → 15 of 16, bathroom floor 4.0 → 13.5 of 15, ottoman 3.0 → 10.0 of 15. The
other five places do not move.

**C. Who finds what** (barrels today misses, counted per frame). All three: 24. Contrast only: 20. Contrast and
self-calibration: 11. Contrast and near-miss: 9. Near-miss only: 4. Near-miss and self-calibration: 1. Self-
calibration only: 1. None: 26. Of the 50 the first two gain, contrast finds 44. The 6 it misses: two cut by the
frame edge (no stripe in the frame), two blue barrels touching another blue barrel (one band two barrels wide), two
half-hidden barrels its "one body" guard refuses. Near-miss and self-calibration overlap too: 25 in common, 13 and 12
alone. Near-miss reaches body hues just past the range (ottoman); self-calibration reaches what no ladder level
reaches (the gray-olive warm-lamp stripe, the red-orange gray-table bodies).

**D. Every box off a barrel, contrast alone** (9 per frame, 2.83 counted once per arrangement). Five are today's own
boxes: the jar on the glass table (3 frames), orange glints of the ottoman under a close-up box, pale wood grain under
a 329 px close-up box. Four are new:

- `lampmid3_bathtile_core_01`: a second box on the upper half of an orange barrel (all three winners draw it).
  Check: one box per barrel (a box inside a surer same-colored box).
- `lampwarm6_bathtile_core_01`: an orange box on a blue barrel that also has its blue box. Check: self-calibration's
  seed rule (no box of the other color on a found barrel).
- `lampwarm6_glass_occl_02`: two small boxes stacked on the red jar (label read as a stripe between jar and lid).
  Check: two boxes stacked in the same columns are one thing; or a second reading (no other winner draws them).
No rule was tuned on these frames.

**E. Frames nobody judged on** (the extreme ones). **Not blind**: all three authors saw counts on them while shaping
their methods (near-miss: in-sample tables and color readings; self-calibration: four in-sample tables with a row
per extreme condition; contrast: its finder measured on all 261 train frames). No number was chosen on them. Found
per frame, of 167: today 13, near-miss 58, self-calibration 60, contrast **85**, `mask_union` 72. Boxes off a barrel:
4, 4, 5, 6, 6. No box on an empty frame. Wood desk (6 lamp settings, 21 placements): 1.2, 7.2, 8.5, **13.2**, 9.8. Black
table (26): 5, 14, 8, **5**, 12 (contrast gains nothing there). Very dark ottoman (15): 1 for all. Dave's 12 office
frames (indicative): today 13 of 34, near-miss 26, self-calibration 19, contrast 23, `mask_union` 28.

**F. Against the vendor** (six places with vendor files: 117 frames, 108 placements). Found: today 70.8, near-miss
84.5, self-calibration 84.5, `mask_union` 89.8, **contrast 92.3**, vendor 83.3. Per frame 148, 186, 185, 198, **212**,
177. Missed: 36.0, 21.0, 22.0, 16.4, **14.5**, 16.5. Boxes off a barrel: 1.93, 3.57, 2.18, 3.32, **2.83**, 3.00 (on
nothing per frame: 5, 9, 5, 9, **7**, 7). Contrast beats the vendor by 9.0 placements. It still loses at the gray
table (15 against 16) and the ottoman (10.0 against 12.3). It wins at the bathroom (13.5 against 7.0), the glass
table (14.8 against 12.0), pale wood (13 against 12) and the ABP white table (26 against 24). This is train data. Our
methods were shaped on it; the vendor's was not.

**G. What is left after contrast alone** (ordinary conditions): 32 barrels per frame, 16.7 placements.

- Hidden or cut by the frame: 27 (15.0 placements). ABP occlusion set 6, ottoman 10, bathroom 6, pale wood 2, others 3.
- Neither color painted: 2 (warm ottoman, blue barrels touching each other).
- Touching another barrel: 3 (blue barrels side by side on the ottoman; one, `lampwarm6_ottoman_core_01` #2, is really
  blocked by today's false close-up box below it, which holds its stripe point).
- A guard refused it: 0. The detector refused a well-painted barrel: 0.

So what is left is almost all hidden and frame-cut barrels, plus touching blue barrels. That matches the
place-ceiling oracle (163.2: its 13 misses were all hidden or cut).

**Takeaway.**

1. One idea does the work: the stripe by color difference. It needs no strict color, so it reaches what the other two
   reach and 20 barrels more.
2. Adding the others gains 1 to 3 placements and brings their clutter boxes. Inside the noise. Not worth it.
3. Without contrast, near-miss and self-calibration are complementary: together (the two masks laid over each other)
   +5 placements over either.
4. Contrast's weak spots: frame-cut close-ups, touching same-colored barrels, half-hidden barrels, the black table.
5. Caution, as for all three: each method's structure (contrast's guard thresholds included) was shaped on all eight
   places. Only the settings in the folds are held out. A new place, or the test frames, is the clean check.

**Next.** (1) Walk Tanush through contrast; it is main code if adopted. (2) Judge it on the next place Tanush shoots.
(3) Touching same-colored barrels: cut a band two barrels wide (also self-calibration's open point). (4) The
one-box-per-barrel and other-color-on-a-found-barrel checks for the new boxes (D), judged on their own.

**Repeat.** `python barrels/experiments/2026-11-26_combined/repro.py`, `cn_picks.py`, `run.py`, `run3.py`,
`analysis.py all cn_alone`, `cb_sheets.py`, with `PYTHONPATH=barrels/src`. The answer as the judge's command:
`python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_contrast/table.py:fit` (held out); fixed
numbers: `barrels/experiments/2026-11-26_contrast/candidate.py:detect_frame` (in-sample when judged).
Pages: `results/2026-11-26_combined/` (`summary.md`, `summary3.md`, `overlap.md`, `overlap3.md`, `*_cn_alone.md`,
`*_mask_union.md`).

## 2026-11-26/27 — The detector has no slack (branch `wip/exp-slack`; pre-registered, two rounds; not adopted, awaiting Tanush)

**Question.** One pixel shaved off every painted region loses 40 of the 211 barrels the detector finds on the ordinary train frames (12 of 63 on the two white tables by the audit; 11 of 63 with the stored model). Can one rule keep those barrels without a single new false box?

**Where they die.** Looked at barrel by barrel on the white tables before the plan (`look_white*.py`). A stripe 5 rows tall becomes 3. The floor is 3.6 to 4.7. The existing second reading at the seams would pass it (6.5 to 8.0 against 8.1 to 10.3). It is not asked: after the pixel the stripe is 0.65 to 0.73 of a barrel wide, under the 0.8 it needs. One pixel moves several readings at once.

**Method.** One experiment flag, `DetConfig.slack`, off by default (letters A B C D). The proof harness at defaults: IDENTICAL BOXES ON EVERY INPUT (5435 masks, 6152 boxes). Each arm against today's detector on the same mask. Train frames only.

- **A**: the stripe's area floor scales with the barrel (18 % of the predicted stripe, never above 20 px; it changes only beyond 50 cm).
- **B**: a stripe too thin or too small is read at the seams when the barrel is seen whole, by its width (eaten pixels given back) or by the rest of the barrel (top and bottom where the row predicts them, not against the other color, one side ending with the stripe).
- **C**: one size floor missed by one pixel per edge is forgiven when the top and bottom are seen, body is above and below, the box is half filled.
- **D** (round 2, addendum committed first): B, but a stripe too *small* is read again only when the rest of the barrel supports it with its edges as seen.

**Results** (per frame; "back" = of the barrels lost to the harm, found by the arm).

| arm | (a) 1 px, back of 40 | (a) 2 px, back of 107 | (b) typical / bad day, back of 42 / 51 | (c) unharmed, judge | (e) hand colors: unharmed boxes not on barrel; 1 px back of 61; 2 px back of 150 | (d) new boxes not on a barrel, 5435 harness masks; empty frames |
|---|---|---|---|---|---|---|
| A | 0 | 0 | 0 / 0 | NO CLEAR DIFFERENCE, 211 → 211 | 3 → 3; 0; 0 | 0; none |
| B | 11 | 58 | 18 / 20 | NO CLEAR DIFFERENCE, 211 → 214 | **3 → 7**; 22; 69 | **4** (hand 2, pool 1, scene 1); **1 on an empty frame** |
| C | 6 | 1 | 15 / 15 | NO CLEAR DIFFERENCE, 211 → 213 | 3 → 3; 7; 1 | 0; none (loses 2 scene barrels) |
| **D** | **11** | **55** | **18 / 20** | **NO CLEAR DIFFERENCE, 211 → 214** (133.8 → 135.4 placements) | **3 → 3; 22; 66** | **0; none** |
| CD | 11 | 55 | 18 / 20 | NO CLEAR DIFFERENCE, 211 → 215 | 3 → 3; 22; 66 | 0; none |

- No arm loses a found barrel on any real mask. On the eroded masks every arm lowers the boxes not on their barrel.
- B's four false boxes (hand colors: bathroom tile under the mid and dim lamp, an empty bathroom frame, the warm ottoman) all came from a stripe under 20 px called "seen whole" by its width alone. D removes all four and keeps 11 of 11 at one pixel.
- Contact sheets: every box that appears or disappears on a real frame (252 in round 1, all looked at). D's new boxes are all on a barrel. 186 are strict hits; 12 sit on their barrel with the box off. One of those straddles two touching blue barrels (`lampmid6_ottoman_touch_01`, one pixel off). D removes 4 boxes of the wrong color.
- The cliffs: `height_max` 1.5 → 1.2 changes nothing with or without D. `min_width_px` 12.8 and `min_stripe_px` 4.8 are refused by the code's own assertion. D does not touch them.

**Takeaway.** The pre-registered success line was one in three at one pixel. **D brings back 11 of 40 (27 %): under the line.** It breaks no hard limit and is the arm the rule picks. At two pixels it brings back half (55 of 107), with hand colors 66 of 150. The barrels it cannot save die through caps (7), side occlusion (4), and stripes under 20 px whose barrel edges do not agree (about 15). Slack in the stripe's size tests helps, and nothing else in the chain moves.

**Next.** Tanush decides whether D becomes plain code. If yes: the `DETECTOR-MAP.md` changes listed in the report. The caps and the small far stripes are separate experiments.

## 2026-11-26 — A barrel hidden at the side by a thing that is not a barrel (TODO E7, map B9): the own side by its bulge. Not adopted

**Branch** `wip/exp-sidecut`. **Scripts** `experiments/2026-11-26_sidecut/` (`PREREG.md`, `lib.py`, `explore_dev.py`, `sim.py`, `real.py`, `harness_on.py`, `r3.py`, `photo_cue.py`). **Results** `results/2026-11-26_sidecut/` (`summary.md` first).

**Why.** Today a barrel cut at the side by a box has a cliff. Half hidden, the simulated scenes find most of them, many by a box centred on what is seen, a quarter of a width off. At 60 % the stripe is under 0.4 W and nothing is drawn. The two real frames of this kind (`occlx_02`, `occlx_03`, about 60 % hidden) are missed. Tanush: "we can still work with 60 %, if we see the stripe and the bulge and the top or bottom edge."

**Hypothesis.** A barrel's own side bulges. A side cut by a box is straight. So the side that bulges says where the barrel is, and the box can be drawn W wide from it, with no cliff and no centred guess.

**The rule** (behind one flag, `DetConfig.side_cut`, default `centred` = today). For a partly seen stripe that no reason and no outline places, with its top and bottom seen: per row, the left and right edge of the seen part. A ruler from the edge's place in the top sixth of the rows to its place in the bottom sixth. The bulge = how far the middle rows stick out past the ruler. A lean cancels. A side is the barrel's own when it bulges by at least a quarter of what the barrel's outline bulges in the same rows, and by at least 1 px. One own side: the box is W wide from it. Two: centred, as today. None: no box (`own_side`), or today's centred guess (`own_side+centred`, the comparison arm).

**Numbers.** Chosen on HOME and ABP white only (bands of a sixth; a quarter of the outline's bulge, halfway between a cut, 0, and a real own side, about half). CAMPUS was held out.

**Results** (all train; `summary.md`).

- Default: the proof harness says IDENTICAL BOXES ON EVERY INPUT (5435 masks, 6152 boxes). Tests 969 pass (17 new).
- Simulated side cuts, edge and slant, 312 scenes per cell, found / placed (centre within 10 % of the width):

| | 50 % | 60 % | 65 % | 75 % |
|---|---|---|---|---|
| plain, today | 279 / 216 | 151 / 150 | 103 / 103 | 28 / 28 |
| plain, own side | 289 / 277 | 269 / 263 | 259 / 253 | 195 / 193 |
| stripe ends 6 px early, today | 254 / 238 | 156 / 156 | 90 / 90 | 9 / 9 |
| stripe ends 6 px early, own side | 292 / 282 | 255 / 253 | 231 / 231 | 94 / 94 |

- Held-out CAMPUS is weaker than the two tables the numbers came from: at 60 %, plain 118 of 156 (HOME + ABP white: 151 of 156).
- No simulated box of the rule lies off the barrel. More boxes touch the barrel but fail the strict rule (14 → 35): a slanted cut hides a bottom corner and the seen bottom is 6 to 9 px high (map B8).
- Other kinds of scene: `both` (cut from both sides) 103 → 28 of 156 with `own_side`: no side is the barrel's own, and today's centred guess is right there by the symmetry of the simulation. `own_side+centred` keeps every other kind.
- Real occlusion set: 9 → 11 of 15 hidden barrels found (`occlx_02`, `occlx_03`; both seen during development, so not a test). None lost.
- All 261 real train frames: 9 frames change. Right: `occlx_02`, `occlx_03`, `palewood_occl_02` (new, found), `black_occl_03` (extreme, found), `lampmid6_glass_clutter_01` (a false box goes). Wrong: `lampwarm6_glass_occl_02` (a NEW box on a tin's label: the hard limit), `lampcool6_ottoman_occl_02` (a box on the WRONG side of a real barrel: the dark shaded side was read as straight), `lampwarm6_glass_clutter_01` (today's false box moves onto a real barrel as a second box), `light_far_02` (`own_side` loses a small whole barrel with narrow paint).
- Judge: both arms NO CLEAR DIFFERENCE (+2.0 and +3.0 placements; the margin is 4.0).
- Damaged masks: one new box on nothing (both arms).

**Takeaway.** The bulge does tell the own side from a straight cut in the simulation, and the cliff is mostly gone there. It is not adopted: it failed four of its pre-registered clauses (no cliff on held-out CAMPUS and with the stripe ending early, `both`, the damaged masks) and it drew one new false box and one wrong-side box on real frames. Both real failures are at the edge of the mask: a shaded side or a patterned tin changes the painted outline by the 1 to 3 px the rule reads.

**The photo at the cut** (an analysis, no rule). The color just beside a seen end, compared with the table just below the barrel, does not separate a side hidden by a thing from a free side: the smallest difference at a hidden side is 17 (`occlx_02`), and 249 of 295 free sides are at least that. Beside a barrel at stripe height the camera usually sees the far background, not the table. A photo cue would need another comparison.

**Next.** If tried again (a dated addendum): the own side only where the cut side is also seen to be straight over the whole height, and never on a side whose painted edge is ragged; a test on more real side cuts than two.

**The map change the rule would need** (`DETECTOR-MAP.md`, section 3, stage 3, the tree of `place_sides`, non-thin branch). After "own_end_by_outline: exactly one end has a barrel's rounded corners?" — no:

```
O -- no --> E{"top and bottom both seen?"}
E -- yes --> S{"own_side_by_bulge: which sides bulge
              by ≥ max(1 px, 0.25 × the outline's bulge)?"}
S -- "exactly one" --> B8["box = W wide from that side. rule: own_side"]
S -- "both" --> C{"stripe at least 0.4 W wide?"} -- yes --> B4["centred. rule: two_sides"]
S -- "neither, or not measurable" --> N2["no box: side_unexplained"]
E -- no --> N2
```

and in the thin branch, after `thin_outline` — no: "exactly one side bulges (top and bottom seen by construction)? → W wide from it, rule `thin_own_side`; else outline_unknown". `drop_single_reading` is unchanged (the rule needs a seen top and bottom, so it never asks it).

## 2026-11-26 — The stripe by color difference, then the barrel's own colors (branch `wip/exp-contrast`)

Branch `wip/exp-contrast`. TODO item C4 and part of C6. Ready to paste into `docs/EXPERIMENTS.md`.
Plan: `experiments/2026-11-26_contrast/PREREG.md`, committed (66a747d) before any judged run. One round was run.
Nothing that runs by default was changed. `detector.py` was not edited.

#### Hypothesis

1. A barrel's stripe can be found without knowing its color: it is a band that is bluer (or redder) than what is
   right above it AND right below it, by a margin, at the size its row predicts.
2. Once it is found, that barrel's own two colors, read at that place, can paint it well enough for today's
   detector to box it.
3. Added to today's boxes, this finds the barrels the fixed colors miss, by more than the noise, on places the
   numbers were not chosen on, without drawing boxes on clutter.

#### Method

- **The finder** (`src/barrels/contrast.py`, 22 unit tests, called by nothing that runs). The channel is
  `log((R + 8) / (B + 8))`. For each row taken as a stripe's middle, the camera model gives the stripe band and the
  two body bands. Per pixel: the smaller of (upper minus stripe) and (lower minus stripe) when both have one sign.
  A candidate is a place where half of the predicted width passes a margin of 0.5, and the mean difference over the
  width (the *strength*) is above a floor. The sign gives the barrel's color. No pixel is changed.
- **From candidate to box.** The barrel's body color and stripe color are read from its own bands. Inside the box
  the geometry predicts (grown 8 %), a pixel is painted body or stripe when that is the nearest of (body, stripe,
  what is around the box). Only where the fixed model painted nothing. Then `detector.detect` runs on the mask.
- **Guards**, each on or off: the part that should be orange reads reddish at all (the absolute check); what is
  above the top and below the bottom differs from the body (extent); body and stripe are far apart (own colors
  apart); the two body bands are one color (one body).
- **Three ways to use it.** *Add*: today's boxes stay, candidates inside them are left alone, new boxes are added.
  *Merge*: everything is painted into the fixed mask and the detector runs once. *Alone*: fixed colors off.
- **How the numbers are chosen.** Inside each fold, on the other seven places: every setting is run and counted;
  a setting the pass rule calls FAIL there is out; the highest (found minus boxes not on their barrel) wins; a tie
  goes to the most cautious. The folds choose the strength floor (1.0, 1.15, 1.3) and which guards are on.
- **Said plainly:** the four guard thresholds (1.1, 0.8, 0.42, 0.15) and the three floors were read off an
  in-sample table of all eight places. The folds choose which guards are on, not where their thresholds sit.

#### Data

Train frames only. 154 ordinary frames, 17 conditions, 8 places, 172 placements. 77 extreme frames are printed,
never judged. The finder was also measured on the 30 frames at lamp brightness 1. No test frame was loaded, viewed,
scored or listed.

#### Results

##### A. The finder against the hand boxes (no detector; `results/2026-11-26_contrast/finder.md`)

Margin 0.5, half the width, no guard, at most 20 candidates a frame. A barrel counts when a candidate of its color
sits on its stripe.

| frames | clean barrels with a candidate: among the 3 strongest | among the 5 | among the 20 | of | of those the fixed colors miss | partly hidden, among the 20 | candidates on no barrel, per frame |
|---|---|---|---|---|---|---|---|
| ordinary, 154 | 196 | 211 | 211 | 211 | 63 of 63 | 60 of 88 | 1.03 (2.8 per empty frame) |
| extreme, 77 | 85 | 98 | 98 | 108 | 95 of 105 | 16 of 44 | 0.68 |
| lamp brightness 1, 30 | 0 | 0 | 0 | 42 | 0 of 42 | 0 of 15 | 0.90 |

- Every clean barrel in every ordinary condition has a candidate, among the 5 strongest of its frame.
- The predicted box fits the hand box: overlap median 0.87; 210 of 211 at 0.5 or more.
- **Where it breaks.** The very dark ottoman: 1 of 10 (the pixels are under the brightness floor). Lamp brightness
  1: none. Close-ups whose stripe is below the frame: none of 14 (no stripe, no candidate). Barrels hidden from
  below or behind another barrel: 28 of 88 have no candidate. The black table: 13 of 14.
- Far barrels were not a problem here: the smallest clean barrels (29 px tall, stripe about 5 px) are found. Rows where
  the stripe would be under 4 px are not searched.
- The channel hardly matters: log ratio with offset 1, 8 or 16 and (R - B)/(R + G + B) all keep 211 of 211
  (`finder_grid.md`). A higher margin cuts the candidates on nothing and costs hidden barrels.

##### D. The judged candidates (leave one place out; baseline 133.8 of 172 placements, 211 of 307 per frame)

| candidate | verdict | found, placements | found, per frame | boxes not on their barrel, per arrangement (per frame) | boxes on empty frames: clean / with clutter | places that moved | barrels gained / lost |
|---|---|---|---|---|---|---|---|
| **C1** today's boxes plus the contrast path, guards chosen in the fold (primary) | **PASS** | 155.3 (+21.5) | 275 | 1.93 → 2.83 (5 → 9) | 0 / 0.0 | gray table 10 → 15 of 16; bathroom 4.0 → 13.5 of 15; ottoman 3.0 → 10.0 of 15 | 64 / 0 |
| **C2** painted into the fixed mask, one detector run | **FAIL** | 142.3 (+8.5) | 248 | 1.93 → 4.83 (5 → 15) | 0 / 0.0 | bathroom 4.0 → 13.5; pale wood 13 → 12 | 38 / 1 |
| **C3** as C1 with no guard | **FAIL** | 152.1 (+18.3) | 262 | 1.93 → 5.18 (5 → 9) | 0 / 2.0 | gray table 10 → 15; bathroom 4.0 → 12.2; ottoman 3.0 → 7.0; ABP white 26 → 27 | 51 / 0 |
| **C4** as C1 without the absolute check | **FAIL** | 155.6 (+21.8) | 276 | 1.93 → 4.93 (5 → 11) | 0 / 1.0 | gray table 10 → 15; bathroom 4.0 → 13.8; ottoman 3.0 → 10.0 | 65 / 0 |
| **C5** the contrast path alone, fixed colors off (report only) | FAIL | 138.2 (+4.4) | 253 | 1.93 → 4.20 (5 → 9) | 0 / 0.0 | home 28 → 24; campus 35 → 31; gray table 10 → 14; bathroom 4.0 → 12.5; glass 14.8 → 14.0; ottoman 3.0 → 10.7; pale wood 13 → 11; ABP white 26 → 21 | 68 / 26 |

Margins: found better above +4.00, boxes worse above +1.85, cluttered empty frames worse above +1.00, a box on a
clean empty frame fails. C1's gain is 17.5 placements above the margin: not a weak pass.

**C1, place by place** (found per placement; per frame; boxes not on their barrel per frame):

| place | found | per frame | boxes |
|---|---|---|---|
| home white | 28 → 28 of 29 | 28 → 28 | 0 → 0 |
| campus | 35 → 35 of 35 | 35 → 35 | 0 → 0 |
| ABP gray table | 10 → 15 of 16 | 10 → 15 | 0 → 0 |
| bathroom floor | 4.0 → 13.5 of 15 | 16 → 54 of 60 | 0 → 2 |
| glass | 14.8 → 14.8 of 15 | 74 → 74 of 75 | 3 → 5 |
| ottoman | 3.0 → 10.0 of 15 | 9 → 30 of 45 | 1 → 1 |
| pale wood | 13 → 13 of 15 | 13 → 13 | 1 → 1 |
| ABP white | 26 → 26 of 32 | 26 → 26 | 0 → 0 |

- By light at the bathroom: cool 13 → 15, mid 1 → 13, dim 1 → 13, warm 1 → 13 of 15. At the ottoman: cool 3 → 12,
  mid 6 → 10, warm 0 → 8 of 15.
- Of the 64 barrels gained, 58 are clean and 6 are partly hidden.
- **The named traps.** No box on any of them, for any of the five candidates: `lampmid3_bathtile_neg_02`,
  `lampmid6_bathtile_neg_02`, `lampwarm6_bathtile_neg_02`, `lampwarm6_glass_neg_02`, `lampmid6_glass_neg_02`.
  The red jar with the teal label has a candidate of strength 1.09; the floor of 1.15 stops it. The blue tin has an
  "orange body" that is not reddish; the absolute check stops it.
- **C1's four new boxes that are not on their barrel** (seen on the sheets): a second, smaller box on an orange
  barrel (`lampmid3_bathtile_core_01`); an orange box on a far blue barrel beside its right blue box
  (`lampwarm6_bathtile_core_01`); two boxes on the jar with the orange lid and the blue label on glass under the
  warm lamp (`lampwarm6_glass_occl_02`). The jar is orange above and below a blue band, at the size of a barrel
  for its row. Nothing here tells it from a barrel.
- **What the folds picked.** Five of eight: floor 1.15, the absolute check, the extent guard. The other three add
  "own colors apart" (two of them with floor 1.0, one with "one body" too). The absolute check and the extent guard
  were picked in every fold.
- **The extreme conditions, C1, report only.** Orange wood under the lamp: 7 → 79 of 126 found per frame, boxes
  not on their barrel 4 → 6. The very dark ottoman 1 → 1 of 15. The black table 5 → 5 of 26.

##### One guard at a time (in-sample, all eight places, not a verdict; `insample.md`)

Around the setting the rule picks on all eight places (floor 1.15, absolute check, extent):

| change | found, placements | boxes not on their barrel | on empty frames with clutter |
|---|---|---|---|
| the pick | +23.17 | +0.50 | 0.0 |
| no absolute check | +23.17 | +2.50 | 1.0 |
| no extent guard | +23.17 | +1.50 | 1.0 |
| no guard at all | +23.17 | +5.70 | 4.2 |
| floor 1.0 instead of 1.15 | +24.42 | +5.65 | 3.0 |
| floor 1.3 | +21.25 | +0.50 | 0.0 |
| plus own colors apart | +22.50 | +0.50 | 0.0 |
| plus one body | +22.17 | +0.50 | 0.0 |
| the pick, merged into the fixed mask | +23.17 | +3.17 | 0.0 |
| the pick, alone | +6.03 | +2.07 | 0.0 |

- **The absolute check helps.** It costs no barrel and removes 2 boxes per arrangement. Judged blind, C4 (without
  it) fails on boxes where C1 passes.
- The strength floor is the sharpest number: 1.0 to 1.15 costs 1.25 placements and removes 5 boxes.
- "Own colors apart" and "one body" cost barrels and remove nothing more here.

##### Time per frame (`timing.md`, one thread, 26 frames)

Today's path: 82 ms median (fixed colors 23, detector 58). With the contrast path added: 139 ms median, 165 mean,
355 at most. The response map is 47 ms; candidates, own colors and paint are 10 ms together. The second detector
run is needed only when a candidate was painted: 4 of 26 frames.

#### Takeaway

- **Relative color works as a finder.** Every clean barrel of the ordinary conditions has a candidate on its
  stripe, including all 63 the fixed colors miss.
- **Added to today's detector it passes the standard rule, leave one place out**, by a wide margin: +21.5
  placements, 64 barrels gained, none lost, 4 more boxes that are not on their barrel, none on an empty frame.
  The bathroom goes from 4 to 13.5 of 15, the ottoman from 3 to 10 of 15, the gray table from 10 to 15 of 16.
- **It needs its guards.** Without any, it draws boxes on clutter (C3). The absolute check and the extent guard
  carry that weight.
- **It must be added, not merged.** Painting into barrels that are already found adds second boxes and boxes on
  the glass table's jar (C2).
- **By itself it is not a detector.** With the fixed colors off it finds 253 per frame against 211, but loses 26
  barrels that have no visible stripe: close-ups, tipped barrels, barrels hidden from below.
- **What it cannot do.** A barrel with no visible stripe. Very dark scenes. A thing that really is orange with a
  blue band at barrel size (the jar). A barrel inside a wrong box of today's detector is left alone (the large
  orange barrel on the ottoman).
- **Caveats.** The guard thresholds saw all eight places. Two places have warm light. The gain sits at three
  places; five did not move.

#### What surprised me

- A barrel's own body bands are sandwiches of the other sign (table, body, stripe). The finder needs the rule
  "the stronger candidate owns its box".
- The first version put every candidate about 3 rows too high: the response is flat over a few rows and the first
  of them was taken. Fixed before the plan was written.
- On orange wood, parked as extreme, the path finds 79 of 126 where today finds 7.
- The same paint that passes when added fails when merged.

#### What next

1. **A place with warm light that the thresholds have never seen.** That is the blind test this run could not be.
2. **Use the response inside the detector's own stripe test** as soft evidence, in place of paint and a second
   run. It would also let a found stripe ask for its body.
3. **Grow the body from the stripe** by likeness to the barrel's own color, stopping at the predicted size. The
   box paint fills dark table on the ottoman.
4. **Let a candidate replace a wrong box of today's detector**, not only add where there is none.
5. **A guard for the jar**: nothing in two colors and one size separates it. The outline (a jar has a neck) or
   the side profile of the stripe might.
6. If this is adopted: the walkthrough for Tanush first, then the noise floor measured again.

#### Not done

- No second round. The margin itself (0.5) and the share of the width (0.5) were fixed after the finder table;
  the folds varied the strength floor instead.
- The opponent channel was compared in the finder only, not judged.
- The side-flank guard was measured (`explore_guards.md`) and left out of the families: touching barrels and the
  dark ottoman fail it.
- `docs/ARCHITECTURE.md`: a row for the new module was added (same commit as this entry).

#### Files

- Code: `src/barrels/contrast.py`, `tests/test_contrast.py`.
- Experiment: `experiments/2026-11-26_contrast/` (`PREREG.md`, `finder.py`, `explore_guards.py`, `candidate.py`,
  `table.py`, `run.py`, `insample.py`, `timing.py`, `sheets.py`).
- Results: `results/2026-11-26_contrast/` (`summary.md`, `chosen.json`, `judge_C1_add_guards/` and four more,
  `finder.md`, `finder_grid.md`, `explore_guards.md`, `insample.md`, `timing.md`).
- To judge it again: `python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_contrast/table.py:fit`
  (leave one place out, the judged candidate) or `--cand-callable .../candidate.py:detect_frame` (one setting,
  in-sample: found +23.2 placements, 278 per frame, boxes +0.5).

## 2026-11-26 — The bottom edge: "more paint, box disappears" (map B8, TODO D1 and K2)

**Branch** `wip/exp-bottom` (from `barrels` at `337f04c`). **Scripts** `experiments/2026-11-26_bottom/` (`PREREG.md` with addendum 1, `yardstick.py`, `run.py`, `lib.py`). **Results** `results/2026-11-26_bottom/` (`yardstick.md`, `summary.md`, `judge/`, `judge_cli/`; contact sheets in `sheets/`, not committed).

**The flaw.** The detector keeps a seen bottom when it is within 15 % of the height of the predicted one. The scorer allows 10 % from the true one. Paint a shadow or a reflection under a barrel and the box follows it down by 10 to 15 %. The barrel then counts as a miss plus a false box, and the distance read off the bottom is wrong.

**Step A, the yardstick** (today's detector, no change; 154 ordinary train frames, 172 placements). Boxes that are on their barrel and fail the strict rule because of the bottom edge:

| color step | found, placements | the bottom edge is the cause: too low / too high |
|---|---|---|
| fixed colors | 133.8 | 1 / 1 |
| saturation floors −20 | 133.6 | 4 / 3 |
| saturation floors −40 | 125.4 | 8 / 5 |
| hue ranges ±3 | 142.1 | 2 / 2 |
| mask dilated 1 px | 136.6 | 2 / 5 |
| hand thresholds | 156.8 | 1 / 3 |

- The flaw is real and small on these frames: 37 boxes over six color steps. Only half end too low.
- Of five ways to read the bottom, the stripe's row is the steadiest: outside the scorer's tolerance for 2 to 4 % of near barrels and 0 % of far ones, at every color step. The raw seen bottom: 8 to 22 %. The seen top plus a height, or the box's width: worse than both. So no candidate uses the top or the width.

**Candidates** (pre-registered; all change the bottom edge only, at the five places a bottom is decided: `resolve_bottom`, `read_edges`, `_cap_box`, `_full_slice`, `half_stripes`):

- `low`: a seen bottom more than the scorer's tolerance (10 %, at least 3 px) BELOW the predicted one: draw the predicted one. Above stays as today.
- `both`: the same in both directions.
- `predicted`: always draw the predicted bottom.
- `rows`: a row under the body counts only when the body's color fills half of the columns.
- `rows+low`: both of these.
- Round 2 (addendum 1, written after round 1): `low_uncut` = `low`, except for a stripe cut by the left or right frame edge.

**Results.** Each is judged by the standard pass rule on the same masks as today's detector. "Yardstick" and "found" are summed over the five "more paint" steps; today's are 35 and 694.5.

| candidate | fixed colors: found (gained / lost), verdict | the five more-paint steps: verdicts | yardstick | found | works |
|---|---|---|---|---|---|
| `low` | 132.7 (1 / 2), NO CLEAR DIFFERENCE | all NO CLEAR DIFFERENCE | 29 | 696.2 (+1.7) | yes |
| `both` | 132.0 (2 / 5), NO CLEAR DIFFERENCE | all NO CLEAR DIFFERENCE | 27 | 695.8 (+1.4) | yes |
| `predicted` | 131.0 (2 / 6), NO CLEAR DIFFERENCE | all NO CLEAR DIFFERENCE | 30 | 692.7 (−1.7) | no: found lower; median error near 1 → 2 px |
| `rows` | 126.7 (2 / 11), **FAIL** | 2 FAIL | 59 | 677.2 | no |
| `rows+low` | 127.7 (2 / 10), NO CLEAR DIFFERENCE | 1 FAIL, 1 PASS | 53 | 681.6 | no |
| **`low_uncut`** (round 2) | **133.7 (1 / 1)**, NO CLEAR DIFFERENCE | all NO CLEAR DIFFERENCE | **24** | **700.4 (+5.9)** | **yes** |

- `low_uncut` per step: found +0.6, +3.5, +1.2, −0.1, +0.8 placements; yardstick 7 → 4, 13 → 7, 4 → 2, 7 → 7, 4 → 4; no new box anywhere.
- `tools/judge.py --cand-det bottom_rule=low_uncut` gives the same numbers (133.8 → 133.7, NO CLEAR DIFFERENCE).
- **Bottom-edge error against the labels** (median / 90th percentile; share outside the scorer's tolerance), `low_uncut` against today. Fixed colors: near 1.0 / 3.0 px both, far 1.0 / 1.3 px both. Saturation −40: near 6.0 % → 3.8 % outside, far 3.6 → 2.3 px at the 90th percentile and 11.1 % → 0 % outside. Saturation −20: near 3.9 % → 2.2 % outside. Nowhere worse at the median.
- No verdict is PASS. The pass rule sees a gain only above +4.0 placements, and the whole flaw is 2 to 13 boxes per step. This was expected and is written in the PREREG.

**What the contact sheets show.**
- `low` fixes what it is for. 15 boxes on 8 barrels come back, on the glass table, the white tables and the gray table. Each bottom goes from 5 to 7 px low to within 2 px.
- `low` also loses 5 barrels (10 boxes) where the seen bottom was right and the prediction was wrong. Three are barrels cut by the frame side.
- Why the frame side matters: a stripe is an arc, higher at the barrel's sides than at its middle (16 px at 10 cm). With the middle cut away, the stripe reads high. So the barrel reads farther than it is, and its predicted bottom is too high. `low_uncut` leaves those boxes as they are today.
- `both` also undoes the cap's deliberate seen bottom (home `cluster_01`, lost under five color steps). It also trusts a prediction that is too low on the ottoman.
- `rows` moves clean near bottoms up, because the base's rim is an arc.

**Takeaway.** Recommended: `--cand-det bottom_rule=low_uncut`. It is the only candidate that brings the "box off" count down at every step that has the flaw, and raises found summed over the five steps by 5.9 placements. With today's colors it changes one barrel each way, and it makes the bottom no worse anywhere. Caveat: the frame-side exception was chosen after seeing round 1. Three barrels support it. The geometry is its real evidence.

**What it does not fix.**
- A very near barrel (the ottoman, 145 px tall), where the camera model's prediction is 13 % too high. That costs one barrel under three color steps.
- The bathroom barrel whose stripe is badly painted (one case).
- Boxes that are too HIGH because the lower body is not painted: about half of the yardstick.
- Bottoms of half stripes on the bathroom floor, where the seam itself is wrong.
- A camera tilt that differs between places. Every candidate leans on the predicted bottom, so a better camera model (the self-calibration) helps all of them.

**The map change on adoption** (`DETECTOR-MAP.md`; not edited here).
- Section 2, test 10, and stage 3, step 1: "a seen end within the edge tolerance is the edge" becomes "a seen end within the edge tolerance counts as seen. Its row is drawn, unless it lies more than the scorer's tolerance (10 %, at least 3 px) below the predicted row and the stripe does not touch the frame side; then the predicted row is drawn".
- The same sentence in stage 1 (`resolve_bottom`), stage 6, checks 6 and 7, stage 7 (`_full_slice`) and stage 8 (box line).
- Section 4.3, the last row ("the seen edge agrees"): the detector now has two numbers. 15 % decides whether an edge is seen. 10 % below decides where the bottom is drawn.
- B8 in section 6 is then done.
- In code, the two `DetConfig` fields go. `bottom_rows` and the rules `both`, `predicted` and `rows` are deleted. `drawn_bottom` keeps only the `low_uncut` branch. The proof harness then shows exactly the boxes this run shows.

**Next.** One look at the recommended rule with the next color-step candidate (C2 or C4), since it matters only when more is painted. Judge it again once the camera self-calibration is in.

## 2026-11-26: near-miss colors count next to strong evidence of a barrel (TODO C2, branch `wip/exp-nearmiss`)

**Hypothesis (Tanush).** The detector needs both colors of a barrel. Most clean misses have one color at full
strength and the other just under the threshold. So: keep the fixed ranges as they are, and let a pixel just
outside the range count only where the barrel's other color says it should be. Loosening everywhere floods
(false boxes 7 → 80); loosening beside a barrel should not.

**Method.** `src/barrels/nearmiss.py` (called by nothing by default; 24 unit tests). Every mask is the fixed mask
plus added paint. No pixel is changed, strict paint is never changed, `detector.py` is not touched.

- *Stripe direction.* Loose stripe-colored pixels are painted in a gap of stripe height between two strict body
  pieces in the same column.
- *Body direction.* A strict piece of stripe color with stripe size for its row is a "band". Loose body-colored
  pixels joined to it are painted inside the box that row predicts. Four rules say "not a barrel": the band has
  its own color above or below; the band is the body of a barrel of its own color; the body color runs on above
  the predicted top (it is the wall behind); the paint does not complete half a body on that side.
- *Edges.* Loose body paint never passes the top and bottom the stripe's row predicts (`pred`), or stops at the
  strict body where there is some (`strict`). `free` (predicted row plus the detector's tolerance) is the control.
- *Loose levels.* A ladder set before any run: level 1 = hue ± 3, S − 20; level 2 = ± 6, − 40, V ≥ 25; … level 5 =
  ± 25, − 100, V ≥ 15 (blue S ≥ 13, almost gray). Past the ranges: stripe level 6 = anything that is not body
  color; body level 6 = darker than 0.6 × the ground beside the barrel; body level 7 = anything.
- *Reference.* Plain two-level thresholds: a loose pixel counts when it touches strict pixels of its own color.
- *Chosen in each fold* (the other seven places only): the two levels and the edge mode, by found − 2 × boxes not
  on their barrel, with no new box on a clean empty frame and no training place below its margin.

**Data and rule.** The standard judge (`barrels.judge`), train frames only: 154 ordinary frames, 8 places, 172
placements; extreme conditions printed, never judged. `PREREG.md` was committed (c648d95) before the first judged
run. 28 candidates, all reported in `results/2026-11-26_nearmiss/summary.md`. No second round.

**What was looked at first (in-sample, all places).** Three rounds of tables and 9 contact sheets while the four
rules of the body direction were written; one table of body, stripe and ground color per condition. So the
structure of the method was shaped on train frames of all eight places. Leave one place out guards only the two
levels and the edge mode.

**Results.** Baseline (fixed model): 133.8 of 172 placements, 211 of 307 per frame, 1.9 boxes not on their
barrel, none on a clean empty frame.

| candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel | clean empty | places that moved |
|---|---|---|---|---|---|---|---|
| plain two-level, level 1 (`A_hyst1`) | FAIL | 143.7 (+9.8) | 234 | +30 / −7 | 6.7 (+4.8) | 0 | home −2.0, pale wood −1.0, gray +5.0, ottoman +7.0 |
| plain two-level, level 2 / 3 | FAIL / FAIL | 138.1 / 133.2 | 219 / 210 | +30 / −22, +32 / −33 | 14.5 / 23.4 | 1 / 1 | home −2.0 / −6.0, glass −2.2 / −3.6 |
| plain two-level, level chosen in fold (`A_hyst_fit`) | FAIL | 131.8 (−2.0) | 209 | +0 / −2 | 4.9 (+3.0) | 0 | home −2.0 (every other fold kept the fixed model) |
| the same with the bottom guard | FAIL | 131.8 (−2.0) | 209 | +0 / −2 | 5.9 (+4.0) | 0 | home −2.0 |
| **partner-conditioned, chosen in fold (`B_partner_fit`)** | **PASS** | **147.5 (+13.7)** | **249** | **+38 / −0** | **3.6 (+1.6)** | **0** | gray +2.0, bathroom +5.0, ottoman +4.7, ABP white +2.0 |
| the same, edges unprotected (`D_partner_free_fit`) | FAIL | 132.2 (−1.6) | 214 | +13 / −10 | 2.7 (+0.7) | 0 | campus −4.0, home −1.0, ABP white −1.0 |
| the same, levels past the ranges allowed (`C_wide_fit`) | PASS | 147.5 (+13.7) | 249 | +38 / −0 | 3.6 | 0 | identical: no fold chose a level past the ranges |
| stripe direction alone, level 1 … 5 | no clear difference, PASS (weak), PASS (weak), PASS, PASS | 137.3, 139.0, 139.7, 140.2, 141.0 | 218 … 232 | none lost | 1.9, 2.2, 2.2, 2.2, 2.2 | 0 | gray +2.0, bathroom +0.5 … +3.5, ottoman +1.0 … +1.7 |
| stripe direction alone, level 6 (anything) | FAIL | 144.1 (+10.3) | 243 | +33 / −1 | 5.1 (+3.2) | 0 | bathroom +5.5 |
| body direction alone, level 1 … 5 | PASS (weak), then PASS | 138.5, 141.0, 143.9, 146.2, 147.3 | 219 … 239 | −2 at level 1, then none | 1.9, 2.2, 1.9, 2.3, 3.3 | 0 | gray +3.0 … +5.0, ottoman +1.7 … +5.0 |
| body direction alone, level 6 (darker than the ground) | FAIL | 148.7 (+14.9) | 245 | +34 / −0 | 5.6 (+3.7) | 0 | bathroom +3.2 |
| body direction alone, level 7 (anything) | FAIL | 142.3 (+8.5) | 242 | +38 / −7 | 45.9 (+44.0) | 3 | home −2.0 |
| both directions, level 1 … 5 | PASS each | 142.0, 144.8, 148.1, 151.0, 152.8 | 226 … 257 | −1 at level 1, then none | 1.9, 2.5, 2.9, 2.9, 3.2 | 0 | at level 5: gray +6.0, bathroom +5.0, ottoman +6.0, ABP white +2.0 |
| both directions, stripe 6 with body 6 | FAIL | 156.4 (+22.6) | 271 | +61 / −1 | 8.5 (+6.6) | 0 | bathroom +8.5 |
| both directions, stripe 6 with body 7 | FAIL | 151.0 (+17.2) | 269 | +66 / −8 | 50.0 | 3 | home −2.0 |

`B_partner_fit` is 9.7 placements above the gain margin (+4.0): not a weak pass. Its boxes not on their barrel
rose by 1.6 against a margin of 1.85: one more such box would have failed it. Six folds chose both directions at
level 5 with `pred`; the gray table's fold chose `strict`; the ottoman's fold chose body level 4.

**Paint, bottom edges, extreme conditions.**

| candidate | paint outside the hand boxes | bottoms moved, of the 211 barrels the fixed model finds | lost | extreme, found per frame (of 167) |
|---|---|---|---|---|
| plain two-level, level 1 | × 2.58 | 99 | 7 | 13 → 29 |
| partner-conditioned, chosen in fold | × 1.04 | 19 | 0 | 13 → 58 |
| the same, edges unprotected | × 1.06 | 99 | 10 (8 with the box still on the barrel) | 13 → 47 |
| stripe direction alone, level 5 | × 1.00 | 3 | 0 | 13 → 30 |
| both directions, stripe 6 with body 6 | × 1.09 | 20 | 1 | 13 → 86 |

**The named clutter traps.** The cluttered empty frames `lampmid3_bathtile_neg_02`, `lampmid6_bathtile_neg_02`,
`lampwarm6_bathtile_neg_02` get no box from any candidate except the two with body level 7 (one box on
`lampmid6_bathtile_neg_02`). The fixed mask has no blue there, so nothing has a partner. The trap fires on the
glass table instead: the jar with a blue label on red gets a new orange box in three frames of the main candidate
(`lampcool6_glass_neg_02`, `lampmid3_glass_neg_02`, `lampcool6_glass_occl_02`). The fixed model already boxes the
same jar in three other frames (`lampmid3_glass_occl_02`, `lampmid6_glass_clutter_01`,
`lampwarm6_glass_clutter_01`): it is clutter that has both colors at full strength under some lights.

**What the pictures show** (`contact.py`, `sheets.py`; PNGs in `results/2026-11-26_nearmiss/contact/`, not in git).

- *Gained by the stripe direction:* blue barrels on the gray table whose orange stripe reads red (hue 0 to 1);
  orange barrels in the bathroom whose blue stripe reads hue 101 under the cool lamp (the range starts at 103)
  and hue 90 to 101 with S 46 to 72 under the mid lamp. The added paint is a thin band exactly in the gap.
- *Gained by the body direction:* orange barrels on the ottoman whose body sits on the top edge of the orange
  range (median hue 12 to 13, the limit is 13), around a strict blue stripe; blue barrels under the mid bathroom
  lamp whose body is dark and pale (hue 83 to 93, S 23 to 51); two barrels of the ABP occlusion set.
- *The 7 new boxes that are not on a barrel:* 3 on the jar label above; a blue box on clutter beside that jar
  (`lampmid6_glass_clutter_01`); a second box on the upper half of an orange barrel
  (`lampmid3_bathtile_core_01`); an orange box on a blue barrel in front of a tin
  (`lampmid6_bathtile_clutter_01`); a second blue box beside a barrel on the ottoman
  (`lampmid6_ottoman_core_01`). Counted once per arrangement they are the +1.6.
- *Plain two-level thresholds:* the blue wall behind the home table is loose blue, and it touches the strict blue
  stripe of an orange barrel. The whole wall is painted and the barrel gets a blue box. That is the home loss.
- *Edges unprotected:* loose paint under the base (shadow, reflection) moves the bottom down. The box stays on
  the barrel and fails the bottom rule: three barrels of `campus_light_far_01` alone.
- *Stripe level 6 (anything):* gaps that are not stripes get painted: between the letters on a blue tin, in a
  printed marker, between two blue barrels and a blue jacket behind them.

**Takeaway.**

1. The idea works. Conditioned on the partner, the loose level can go to the loosest color range (hue ± 25,
   blue S down to 13) and still add only 1.6 boxes. Unconditioned, level 1 already adds 4.8 and loses home.
2. The stripe direction costs nothing: no barrel lost, no paint outside the hand boxes, 0.2 more boxes.
3. Keeping loose paint inside the predicted top and bottom is what makes the body direction pass. Without it
   the same grid fails (campus −4.0, 99 bottoms moved against 19).
4. False boxes start where the color test stops: stripe level 6 (+3.2 boxes), body level 6 (+3.7), body level 7
   (+44 and 3 boxes on clean empty frames). No fold chose one of them.
5. **What it cannot reach:** a barrel with neither color inside the strict ranges. Under the warm bathroom lamp
   the blue reads gray-olive (hue 24, S 40 to 61) and nothing strict is blue: 1 of 15 before, 1 of 15 after. On
   the ottoman under the warm lamp: 0 → 1 of 15. Levels 6 do reach them (bathroom warm 10 of 15, ottoman warm 7
   of 15, with stripe 6 and body 6) but fail on false boxes. It also cannot fix clutter that has both colors.

**Next.**

- The setting the rule gives on all eight places is both directions at level 5 with `pred`
  (`experiments/2026-11-26_nearmiss/candidates.py:detect_frame`; in-sample 152.8, held out 147.5). It is a
  candidate for E8 (the winners together), not a default: `detector.py` is being restructured.
- The warm lamp needs a strict partner first. "Blue follows the light" (C3) or the stripe by contrast (C4) could
  supply it; this method then completes the barrel. Worth one combined run.
- The jar label: a body test on both sides of the band (it has orange on one side only at full height) is the
  obvious rule to try. Not done here: it would have been tuned on the four frames it fails on.
- The four body rules were written from train frames of all places. A new place is the real check.

## 2026-11-26 — The barrel as its own color reference (TODO E6, first idea; pre-registered, one round; branch `wip/exp-selfcal`; nothing adopted)

- **Hypothesis:** The fixed colors fail when the light or the table changes. Whole-frame statistics cannot say what the
  right colors are, because barrels are 4 % of the pixels. A barrel that is found, or half found, can: its place is
  known, so its two colors can be read from the photo there. Of 63 clean missed barrels, 49 have one color at full
  strength (review, detector audit 3.3). Per frame, nothing carried between frames, no pixel changed.
- **Method / params:** `src/barrels/selfcal.py` (new; nothing that runs by default calls it; 27 unit tests).
  `experiments/2026-11-26_selfcal/`: `PREREG.md` (committed before any judged run), `candidates.py`, `run.py`.
  - Pass 1 is today's detector. Then seeds: a found box; a strict body color with a stripe-sized gap (`body`); a
    strict stripe-sized band with no body (`stripe`).
  - The guard: three bands (upper body, stripe, lower body) are read from the photo. Kept only if both body bands
    differ from the stripe band in log(R/B) by a margin with the right sign, and a part that was read does not look
    like what is around the box.
  - A kept seed paints its own missing color inside its own box (`local`), and its two readings widen the frame's
    ranges (`frame`), bounded: only wider, a hue end at most 6 or 10, saturation floor never under 60, readings must
    agree, a flood limit.
  - Pass 2: the same detector on the new mask. Every first-pass box stays; second-pass boxes fill in.
  - Three numbers are chosen leave one place out (`rel_margin`, `hue_move_max`, `flood_max`). The rest was fixed
    before the judged runs, but shaped while looking at all eight places (the list is in `PREREG.md`).
- **Data / split:** Train frames only. Judged on the 154 ordinary frames (17 conditions, 8 places, 172 placements,
  307 barrels counted per frame), by the standard pass rule, leave one place out. Extreme conditions report only. No
  test frame opened.
- **Results** (`results/2026-11-26_selfcal/summary.md`; every candidate, also the one that lost):

  | candidate | verdict | found, placements | found, per frame | boxes not on their barrel | boxes on empty frames | places that moved |
  |---|---|---|---|---|---|---|
  | fixed colors (baseline) | | 133.8 | 211 | 1.9 | 0 | |
  | `A_found`: found boxes set the frame's ranges | PASS (+7.2) | 141.0 | 223 | 2.1 | 0 | gray +5.0, ottoman +2.0, bathroom +0.2 |
  | `B_local`: a half-found barrel completes itself | PASS (+12.2) | 146.0 | 243 | 2.2 | 0 | gray +5.0, bathroom +5.5, ottoman +1.7 |
  | `B_frame`: half-found barrels set the frame's ranges | PASS (+9.3) | 143.1 | 230 | 1.9 | 0 | gray +5.0, ottoman +3.0, bathroom +1.2 |
  | **`AB`: all of it (the main candidate)** | **PASS (+13.8)** | **147.6** | **248** | 2.2 | 0 | gray +5.0, bathroom +5.8, ottoman +3.0 |
  | `AB_noguard`: the same with every guard off | FAIL | 152.6 | 261 | 29.2 | 7 (cluttered) | ottoman +7.0, gray +5.0, bathroom +5.8, ABP white +1.0 |

  - No candidate lost a barrel. The gain margin is +4.0; none of the four passes is weak (all above +6.0).
  - `AB` by condition, per frame of 15: bathroom mid 3: 1 → 10, mid 6: 1 → 9, warm: 1 → 6, cool: 13 → 14. Ottoman
    cool: 3 → 11, mid 6: 6 → 7, warm: 0 → 0. Gray table: 10 → 15 of 16. Five places do not move.
  - The one new box of `AB` that is not on its barrel: a second orange box on an orange barrel
    (`lampmid3_bathtile_core_01`). No kept seed on any empty frame. No kept seed off a hand box.
  - The folds agree: every fold picked `rel_margin` 1.0 and, for `AB`, `hue_move_max` 6; `flood_max` 0.03 in 9 of 10,
    0.01 when the ottoman was held out (which cost it 4 barrels there: `A_found` gets 11 on ottoman mid 6, `AB` 7).
  - A usable seed exists in 87 of the 132 ordinary frames with barrels. A sure found box alone exists in 65, and in
    none on the bathroom floor under the mid and warm lamp or on the ottoman under the cool and warm lamp. Warm
    ottoman: no seed of any kind in 6 frames.
  - Painted pixels outside the hand boxes, ordinary frames: 634 216 → 664 143 (+4.7 %).
  - Extreme conditions, report only: wood under the lamp 7 → 51 of 126, black table 5 → 8 of 26, dark ottoman 1 → 1.
  - Report only, colors carried across the frames of one condition: 147.6 → 150.4 placements (248 → 253), boxes not on
    their barrel 2.2 → 3.8. Black table 8 → 16 of 26.
  - What it gains (37 barrels, counted per frame): 32 through a kept seed of their own (15 had the body painted and
    no stripe, 15 the stripe and no body, 2 other); 5 had no kept seed and were found through the frame's ranges.
  - What it still misses (59 per frame; `results/2026-11-26_selfcal/misses.md`): 31 are hidden or cut. The 28 that
    are not: warm ottoman 10 (all 15 barrels there stay missed), warm bathroom 7, bathroom mid 6: 4, mid 3: 3,
    ottoman mid 6: 3, cool: 1. By what happened to their seed: 15 refused by a guard, 9 had no seed candidate, 4 had
    a kept seed and the detector still drew no good box.
    - Warm ottoman: neither color is painted at full strength, and the blue body reads like the dark fabric, so
      the surround guard refuses it. With the guards off these frames get boxes of the wrong color.
    - Two blue barrels touching under the bathroom lamp (4 of the 9): their orange stripes run into one band two
      barrels wide. That is not a one-barrel band, so there is no seed.
- **Takeaway:** It works, per frame, with no new box on an empty frame. Most of the gain is the plainest part: a
  barrel with one strict color finishes itself (+12.2). Sharing the colors with the rest of the frame adds little on
  top (+1.6), because under the warm lamp the blue is not a color any more (saturation under 60) and cannot be a
  range. The guards are what make it usable: off, it finds 5 more placements and draws 27 more boxes on things that
  are not barrels. Caution: the method was shaped on all eight places and only three numbers are held out, so the
  verdict is optimistic by an unknown amount. A new place, or the test frames, is the clean check.
- **Next:** (1) Walk Tanush through it; it touches the color step, so it is main code if adopted. (2) Judge it on a
  place it has never seen (the next shoot). (3) Cut a band wider than a barrel into barrel widths (the two touching
  blue barrels). (4) The warm ottoman needs something else: no strict color is there to start from; the relative
  test without a strict seed (TODO C4) is the candidate. (5) Read the ottoman's size, not only its colors: barrels
  there are 0.6 to 0.7 of the size their row predicts.


## 2026-11-26 — The collapse of the detector (TODO K1): no switches, ten stages, the same boxes

**Branch** `wip/collapse` (from `barrels` at `d86fc3c`, tagged `pre-collapse-2026-11-26`). **Script** `experiments/2026-11-26_collapse/` (`build_inputs.py`, `run_detect.py`, `diff.py`, `rule_counts.py`, `README.md`). **Results** `results/2026-11-26_collapse/` (`before_boxes.json.gz`, `rule_counts.md`).

**Why.** `detector.py` had 30 on/off switches read at 63 places, 7 of them off with their dead code between the live lines, and the same idea coded several times. Nobody could predict what it would do. The map of 2026-11-26 (`docs/archive/DETECTOR-MAP-before-collapse-2026-11-26.md`, section 8a) listed nine changes that cannot change a box.

**Hypothesis.** All nine can be made, one at a time, with the detector drawing exactly the same boxes after each.

**Method.** The detector is a pure function of the class mask and the camera. So 5435 masks were fixed before the first change, and the boxes the detector at the tag draws on them (6152) were stored. After every step: run the detector on all 5435, compare box for box (color, box, flags, source, confidence, order), and run the test suite. A step that changes a box is taken back.

**Data.** Train frames only; every stem is checked against the "test" list of `splits.json`. 261 train frames as the fixed color model paints them, each with one pixel eroded and dilated (522), the 45 frames with hand-set thresholds, the 53 masks the occlusion scorecard is built from, 666 damaged masks (every level of `degrade.py`, seeds 0 to 2), all 3888 simulated occlusion scenes.

**Results.**

| step | what | boxes that differ (of 6152, on 5435 masks) | inputs whose reason log differs | tests |
|---|---|---|---|---|
| tag | the detector before | | | 930 |
| A1 | the 7 off switches, the "bands" finder and their code deleted | 0 | 0 | 911 |
| A2 | the 23 on switches are plain code; `DetConfig` keeps the 20 numbers; step 1 alone and `--step1` gone | 0 | 0 | 905 |
| A3 | `detect` is ten named stages; the partly seen branch is small functions; `Piece`, `Found` | 0 | 0 | 905 |
| A4 | helpers: `edge_tol`, `same_rows`, `same_barrel`, `ends_against`, `standing_nearer`, `widest_barrel`, `sandwiches` | 0 | 0 | 905 |
| A5 | `BarrelAt`, built once per stripe | 0 | 0 | 905 |
| A6 | each box carries its evidence; the verify stages no longer search the reason log | 0 | 0 | 906 |
| A7 | the horizon fact is a check (`above_horizon`); the far branch says what it leans on | 0 | 224 | 906 |
| A8 | three clauses that never decide removed | 0 | 224 (as A7) | 907 |
| A9 | the history out of the comments (`docs/archive/DETECTOR-HISTORY.md`) | 0 | 224 (as A7) | 907 |

- **Identical boxes on every input after every step.** A6 and A7 were the two steps where a difference was possible; neither showed one.
- **The 224 log differences have one cause** (A7): a piece with its top above the horizon is now refused as `piece:above_horizon`, where the log said `piece:height` (473 notes) or `piece:width` (22 notes). The same pieces, refused one check earlier.
- `detector.py`: 1904 lines → 1825. About 420 lines of switches and dead code went; the docstrings that say what each check asks came in.
- `DetConfig`: 51 fields → 20, all numbers: `min_area_px`, `close_px`, `bottom_tol`, `bottom_tol_min_px`, `width_min`, `width_max`, `split_search`, `min_width_px`, `stripe_h_min`, `stripe_h_max`, `band_h_max`, `stripe_w_min`, `stripe_merge`, `stripe_full`, `min_stripe_px`, `height_min`, `height_max`, `body_min`, `body_width`, `pin_good`.
- The eval table (`tools/report.py`) is the table at the tag, number for number. `report.py --gate`: PASS.
- Which rule draws the boxes (`results/2026-11-26_collapse/rule_counts.md`): on the 261 real train masks, 239 boxes; 201 from a stripe (137 whole, 27 the body shows the width, 30 one hidden side, 5 centred, 1 outline, 1 thin at the frame), 28 close-ups, 6 caps, 4 half stripes, no pair.

**Found on the way** (in `docs/DETECTOR-MAP.md`, section 6; none changed):

- The "too far for a stripe" half of the close-up rule takes no piece at all: tried for every top row and every seen bottom row, stage 1 lets nothing through that reaches it (B1).
- With the horizon check in place, `height_max` can refuse nothing, and `height_min` only a short piece with its top in rows 427 to 479. On the 5435 masks `piece:height` no longer occurs (B13).
- One case differs from the tag in theory: a piece that touches the frame top skipped the height check before and could pass; now the horizon check refuses it. The color step paints nothing above row 50, and no golden mask has such a piece.

**Tests: 930 → 907.** The tests were rewritten to state what the detector does with its defaults, without the switch arms. 30 test names went, 7 came.

| removed test | file | step | why it went |
|---|---|---|---|
| `test_barrel_hidden_at_the_side_narrow_stripe_and_hidden_side_from_the_body` | `test_detector.py` | A1 | its subject is `occl_body_side` (off, deleted) on the older side rule |
| `test_three_quarters_hidden_by_a_straight_edge_gets_the_cover_box` | `test_detector_occl.py` | A1 | `slice_box` (off, deleted): the cover box |
| `test_narrow_piece_not_seen_from_top_to_bottom_gives_no_box` | `test_detector_occl.py` | A1 | `slice_box`. The live rule (a thin piece must be a full slice) is tested in `test_detector_pin.py` |
| `test_small_piece_with_a_reason_for_its_side_still_needs_the_full_slice` | `test_detector_occl.py` | A1 | `slice_box`. Its live meaning is kept as the new `test_thin_slice_at_the_frame_that_is_not_full_gives_no_box` |
| `test_both_sides_cut_gets_the_cover_box_around_what_is_seen` | `test_detector_occl.py` | A1 | `slice_box`: the cover box |
| `test_piece_at_the_frame_edge_is_placed_by_its_seen_edge` | `test_detector_occl.py` | A1 | `slice_box`. The live rule (a thin slice at the frame) is tested in `test_detector_sliver.py` |
| `test_cover_unpinned_widens_a_half_seen_barrel_that_was_centred` | `test_detector_occl.py` | A1 | `cover_unpinned` (off, deleted) |
| `test_two_pieces_of_one_stripe_left_and_right_of_a_post_are_one_barrel` | `test_detector_occl.py` | A1 | `slice_box`. The live rule (pairs) is tested in `test_detector_vertical.py` |
| `test_slice_box_changes_nothing_for_barrels_seen_whole` | `test_detector_occl.py` | A1 | `slice_box` |
| `test_joined_stripe_of_two_overlapping_same_colored_barrels_is_two_barrels` | `test_detector_occl.py` | A1 | `stripe_two` (off, deleted). The live rule is `test_stripe_wide_cuts_a_joined_stripe_with_body_right_above_and_below` |
| `test_stripe_two_leaves_one_barrel_and_a_touching_pair_alone` | `test_detector_occl.py` | A1 | `stripe_two`. The live twin is `test_stripe_wide_leaves_one_barrel_and_a_touching_pair_alone` |
| `test_one_barrel_larger_than_its_row_predicts_is_not_cut_in_two` | `test_detector_occl.py` | A1 | **kept**: moved to `test_detector_vertical.py` (the guard is live code) |
| `test_closure_is_large_at_the_own_end_and_small_at_a_straight_cut` | `test_detector_sliver.py` | A1 | `own_close` (off, deleted) |
| `test_closure_says_nothing_when_both_sides_are_cut` | `test_detector_sliver.py` | A1 | `own_close` |
| `test_own_close_places_a_slice_that_the_outline_leaves` | `test_detector_sliver.py` | A1 | `own_close` |
| `test_narrow_slice_beside_a_found_nearer_barrel_is_a_barrel` | `test_detector_vertical.py` | A1 | `slice_behind` (off, deleted) |
| `test_narrow_slice_with_no_found_barrel_beside_it_gets_no_box` | `test_detector_vertical.py` | A1 | `slice_behind` |
| `test_slice_behind_needs_the_full_slice` | `test_detector_vertical.py` | A1 | `slice_behind` |
| `test_slice_at_the_frame_edge_is_placed_by_its_seen_edge` | `test_detector_vertical.py` | A1 | `slice_behind` |
| `test_a_piece_of_a_found_barrels_own_stripe_is_not_a_slice_behind_it` | `test_detector_vertical.py` | A1 | `slice_behind`. **Kept** for the live rule as `test_a_piece_of_a_found_barrels_own_stripe_is_not_half_of_a_pair` |
| `test_pin_thin_does_not_take_a_narrow_slice_away_from_slice_behind` | `test_detector_combined.py` | A1 | `slice_behind` |
| `test_the_test_arms_are_what_they_say` | `test_detector_combined.py` | A2 | it checked the switch arms of the test files; there are no arms |
| `test_two_slices_behind_a_post_are_one_barrel_with_pin_thin_too` | `test_detector_combined.py` | A2 | with one detector it is `test_two_slices_left_and_right_of_a_post_are_one_barrel` |
| `test_a_thin_slice_the_outline_places_gets_one_box_with_everything_on` | `test_detector_combined.py` | A2 | with one detector it is `test_thin_slice_with_a_corner_is_a_barrel` |
| `test_each_branchs_own_cases_come_out_the_same_in_the_combination` | `test_detector_combined.py` | A2 | it compared switch arms with each other; with one detector it compares a result with itself |
| `test_the_finder_hands_over_the_same_pieces_with_or_without_the_lower_floor` | `test_detector_combined.py` | A2 | **kept**: as `test_a_thin_piece_is_a_stripe_and_a_left_over_piece_and_is_handed_over_once` in `test_detector_pin.py` (the file `test_detector_combined.py` is gone) |
| `test_pin_outline_and_pin_thin_are_on_by_default_and_pin_thin_needs_pin_outline` | `test_detector_pin.py` | A2 | "this switch is on by default" |
| `test_defaults_after_the_verdict` | `test_detector_sliver.py` | A2 | "these switches are on by default" |
| `test_the_verify_step_is_on_by_default` | `test_detector_verify.py` | A2 | "these switches are on by default" |
| `test_every_new_switch_is_off_by_default_or_named_in_the_tests` | `test_detector_vertical.py` | A2 | bookkeeping of the switch arms |

So 27 tests are gone for good (19 on deleted off paths, 4 on switch defaults or arms, 4 comparisons between arms) and 3 of the 30 names live on under another name or in another file. No test of the step-1-alone mode was deleted: those tests now call stage 1 (`find_pieces`) directly.

| added test | file | step | what it holds |
|---|---|---|---|
| `test_one_barrel_larger_than_its_row_predicts_is_not_cut_in_two` | `test_detector_vertical.py` | A1 | moved (see above) |
| `test_a_piece_of_a_found_barrels_own_stripe_is_not_half_of_a_pair` | `test_detector_vertical.py` | A1 | the live half of a `slice_behind` test |
| `test_a_thin_piece_is_a_stripe_and_a_left_over_piece_and_is_handed_over_once` | `test_detector_pin.py` | A2 | the finder hand-over test under a true name |
| `test_thin_slice_at_the_frame_that_is_not_full_gives_no_box` | `test_detector_sliver.py` | A2 | a reason for a side does not make a barrel (kept from a `slice_box` test) |
| `test_a_removed_detector_switch_gives_a_clear_error` | `test_report.py` | A2 | `--cand-det` with a removed switch, or with 0 for a number whose 0 meant "off", names the tag |
| `test_a_box_carries_what_it_was_read_from` | `test_detector.py` | A6 | `Found.evidence_box`, `Found.rule` |
| `test_a_barrel_on_the_table_has_a_stripe_tall_enough_to_resolve` | `test_detector.py` | A8 | the fact behind `on_the_table`, for the three camera presets |

Renamed, same test: `test_dark_gap_alone_is_not_a_stripe_unless_asked` → `test_dark_gap_alone_is_not_a_stripe`; `test_the_switch_off_changes_nothing_and_a_single_barrel_is_untouched` → `test_a_single_barrel_is_untouched`; `test_a_thin_line_of_stripe_counts_only_with_half_thin` → `test_a_thin_line_of_stripe_counts`.

**Everything that uses the detector.** `tools/detect_image.py`: `--step1` stops with a message that names the tag. `report.py --cand-det`: takes the 20 numbers; a removed switch, or 0 for `body_min` / `body_width` / `height_max` (0 meant "check off"), stops with a message. `worldmap_bridge.py`, `hsrange.py`, `tools/hs_slider.py`, `live/`: they call `detect(mask, DetConfig(), cam)` and need no change. Experiments dated before 2026-11-26 that name switches run at the tag (`experiments/README.md`); the scripts `run_all.py` starts do not name any.

**Takeaway.** The detector reads as ten stages now, and it is provably the same detector. What is still not clean would change boxes: list (b) of `docs/DETECTOR-MAP.md`, section 6 (B1 to B15). Each is an experiment of its own.

**Next.** B8 (the detector and the scorer agree on the bottom edge; agreed as K2), then B1 and B13 (rules that take nothing today), then B9 (one rule for a barrel cut at the side).

**After merging `barrels` (the measurement work of 2026-11-26) into `wip/collapse`** (merge commit `b3d674c`). One conflict, in `tests/test_gate.py`: their new test, with a number (`min_width_px=20`) in place of the removed switch. Four examples on their side named a removed switch and were changed to a number (`tools/judge.py`, `README.md`, `tests/test_judge.py`, the judge and gate paragraphs of the two HOW-IT-WORKS files). `judge.py`, `counting.py`, `gate.py` and `report.py` needed no code change. On the merged tree:

| check | result |
|---|---|
| the test suite | 952 pass (975 on `barrels`, minus the 30 removed, plus the 7 added) |
| the proof harness | IDENTICAL BOXES ON EVERY INPUT (the 224 log differences of A7, nothing else) |
| `report.py --gate` (the check with margins) | PASS: all 6 protected sets "same", the 19 other sets unchanged, no box on an empty frame |
| `judge.py --cand-det bottom_tol=0.15 --no-save` (a candidate that changes nothing) | NO CLEAR DIFFERENCE: 0 barrels gained, 0 lost, 0 boxes changed (exit code 3) |
| the eval table at the end of the test run | the HOME, CAMPUS and ALL rows are those of the tag |

## 2026-11-26 — What a color setting made per place can reach, without sliders (`experiments/2026-11-26_place_ceiling`; C1, C7, E6)

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

## 2026-11-26 — What to read the light from; blue follows the light, a clean try (branch `wip/exp-light`)

Branch `wip/exp-light`. TODO items C3 and the light part of E6. Ready to paste into `docs/EXPERIMENTS.md`.
Plan: `experiments/2026-11-26_light/PREREG.md`, committed before any judged run. One round was run. No second round.
Nothing that runs by default was changed.

### Hypothesis

1. The color of the light can be read from one frame without knowing where a barrel is, and some places in the frame
   are better to read it from than others.
2. If the blue thresholds follow that reading, the detector finds more barrels under warm light, by more than the
   noise, on places the numbers were not chosen on.
3. The review's expectation for orange: no reading of the light predicts the orange hue the ottoman needs.

### Method

- **Part A, the readings.** Thirteen ways to pick pixels (`src/barrels/lightread.py`, unit-tested, imported by nothing
  that runs). Each gives the warmth of its pixels: the median of (R - B) / (R + G + B). Compared with the labelled
  paint inside the hand boxes (body and stripe bands of free-standing barrels). `measure.py`, `table.py`, `extra.py`.
- **Part B, blue follows the light.** The blue S floor (113) and the low end of the blue hue range (103) go down
  along a ramp as the reading goes from w0 to w1. Four numbers, a grid of 54 settings, the same grid for three
  readings (B1, B2, B3). B4 adds "bluer than the light": where the light reads warm, a pixel under the S floor is also
  blue when its own warmth is at least delta below the lower of the light and the scene. One more number.
- **Part C, orange.** The high end of the orange hue range (13) widens to 16, 19 or 22: with the light (O1), with how
  dark the scene is (O2), or everywhere it does not flood the frame (O3).
- **How the numbers are chosen.** Inside each fold, on the other seven places: every setting is run through the
  detector and the judge's counting; a setting the pass rule calls FAIL there is out; the highest (found minus boxes
  not on their barrel) wins; a tie goes to the most cautious; no gain means the fixed model.
- **The judge.** The standard pass rule, leave one place out, against today's default. `run.py`.

### Data

Train frames only. 154 ordinary frames, 17 conditions, 8 places, 172 placements. The 77 extreme frames are printed,
never judged. No test frame was loaded, viewed, scored or listed. Only two places have warm light: the bathroom floor
and the ottoman.

### Results

#### A. The readings (in-sample unless it says leave one place out; the full table is `results/2026-11-26_light/readings.md`)

| reading | frames it speaks on | r with the blue paint's S | leave one place out, a line: skill | spread between conditions / inside one | largest shift on a close-up | other frames as warm as the warm ones | what fools it |
|---|---|---|---|---|---|---|---|
| `without_loose`: brightest 5 % after taking out anything barrel-like, 15 px margin | 154 | -0.96 | 0.89 | 12.5 | 0.05 | 0 of 119 | nothing in the ordinary set. On the dark ottoman it has only the wall behind to read. |
| `above_gate20`: brightest 20 % of rows 0-49 | 154 | -0.96 | 0.83 | 6.7 | 0.05 | 0 of 119 | what stands behind the table. A lamp-lit yellow note on an empty glass frame reads 0.13. The home wall reads -0.10. |
| `above_gate`: brightest 5 % of rows 0-49 | 154 | -0.95 | 0.83 | 5.3 | 0.03 | 1 of 119 | the same note reads 0.20. |
| `whole_frame`: brightest 5 % (the existing rule) | 154 | -0.95 | 0.70 | 2.1 | 0.42 | 3 of 119 | a close orange barrel (0.50 under the cool lamp), barrels on the black ottoman (0.40), the yellow note. |
| `without_barrels`: the same after taking out what the fixed model paints | 154 | -0.96 | 0.90 | 3.6 | 0.35 | 1 of 119 | the ottoman's orange, which the fixed model does not paint, so it is not taken out (0.38). |
| `max_rgb`: 99th percentile of each channel | 154 | -0.96 | 0.90 | 4.0 | 0.12 | 3 of 119 | close orange barrels, less than `whole_frame`. |
| `tiles`: lower quartile over 4 x 4 tiles | 148 | -0.94 | 0.76 | 7.3 | 0.03 | 0 of 117 | a colored table (pale wood 0.06). Says nothing on 6 dark frames. |
| `least_colored`: least colored 10 % | 154 | -0.88 | 0.65 | 6.6 | 0.02 | 7 of 119 | under a warm lamp it picks the blue barrels themselves. Reads 0.07 on the warm ottoman. |
| `gray_world`: everything below the gate | 154 | -0.84 | 0.20 | 7.2 | 0.04 | 14 of 119 | the table's own color: pale wood reads 0.18 under neutral light. |
| `above_all`: all of rows 0-49 | 154 | -0.86 | 0.70 | 6.9 | 0.05 | 13 of 119 | room content. |
| `near_strip`: bottom 80 rows | 153 | -0.70 | -0.41 | 2.5 | 0.06 | 64 of 118 | the table's own color (pale wood 0.21, black ottoman 0.00 to 0.05 under the warm lamp), a hand. |
| `highlights`: nearly clipped pixels | 116 | -0.58 | -0.18 | 2.1 | 0.29 | 20 of 92 | orange lids and the yellow note are the highlights. Nothing on the ottoman. |
| `neutral`: pixels with S under 40 | 143 | -0.35 | -0.04 | 1.9 | 0.03 | 90 of 117 | everything. Under a yellow lamp nothing white is colorless. It reads 0.01 everywhere. |

- No reading predicts the orange hue: leave-one-place-out skill between -1.07 and +0.10.
- With the parked places counted as well (wood desk, black table, very dark ottoman), `without_loose` drops to
  r -0.78 and skill 0.55. On the wood desk under the cool lamp the light reads 0.04 (neutral) and the blue paint is
  washed out anyway (S 67 to 114). `readings_extra.md`.
- The blue paint under the warm bathroom lamp: median hue 38, S 44. Under the mid lamp: hue 100, S 48 to 82.

#### B and C. The judged candidates (leave one place out; baseline 133.8 of 172 placements, 211 of 307 per frame)

| candidate | verdict | found, placements | found, per frame | boxes not on their barrel, per arrangement (per frame) | boxes on empty frames: clean / with clutter | bathroom (of 15) | ottoman (of 15) | barrels gained / lost |
|---|---|---|---|---|---|---|---|---|
| **B1** blue ramp, `without_loose` (primary) | **NO CLEAR DIFFERENCE** | 137.72 (+3.92) | 225 | 1.93 → 2.68 (5 → 8) | 0 / 0.0 | 4.0 → 6.25 | 3.0 → 4.67 | 14 / 0 |
| **B2** blue ramp, `above_gate20` | **NO CLEAR DIFFERENCE** | 136.22 (+2.42) | 219 | 1.93 → 2.63 (5 → 8) | 0 / 0.2 | 4.0 → 4.75 | 3.0 → 4.67 | 8 / 0 |
| **B3** blue ramp, `whole_frame` | **NO CLEAR DIFFERENCE** | 136.97 (+3.17) | 222 | 1.93 → 2.18 (5 → 6) | 0 / 0.0 | 4.0 → 5.5 | 3.0 → 4.67 | 11 / 0 |
| **B4** = B1 plus "bluer than the light" | **FAIL** | 145.72 (+11.92) | 257 | 1.93 → 6.68 (5 → 24) | 0 / 1.25 | 4.0 → 14.25 | 3.0 → 4.67 | 46 / 0 |
| **O1** orange follows the light | **FAIL** | 133.30 (-0.50) | 209 | 1.93 → 3.93 (5 → 13) | 0 / 0.25 | 4.0 → 3.5 | 3.0 → 3.0 | 0 / 2 |
| **O2** orange follows the scene's darkness | **NO CLEAR DIFFERENCE** | 133.80 (0) | 211 | 1.93 → 1.93 | 0 / 0.0 | no change | no change | 0 / 0 |
| **O3** wide orange with a flood guard | **NO CLEAR DIFFERENCE** | 133.80 (0) | 211 | 1.93 → 3.43 (5 → 8) | 0 / 0.0 | no change | no change | 0 / 0 |

The six places without warm light did not move in found for any candidate. No candidate put a box on a clean empty
frame. Margins: found better above +4.00, boxes worse above +1.85, cluttered empty frames worse above +1.00.

- **B1 misses the gain margin by 0.08 placements.** It is "at the margin". Per frame: bathroom mid 3 lamp 1 → 3 of 15,
  mid 6 1 → 8, warm ottoman 0 → 5. The warm bathroom stays at 1 of 15.
- **B4 finds nearly every bathroom barrel** (mid 3 1 → 15 of 15, mid 6 1 → 15, warm 6 1 → 14) and fails on boxes: 16
  more boxes on nothing, and new boxes on all three cluttered empty bathroom frames.

**Traps, by name.**
- Clean empty frames: no box, any candidate.
- Empty frames with clutter: B4 boxes `lampmid3_`, `lampmid6_` and `lampwarm6_bathtile_neg_02`. O1 boxes
  `lampmid3_bathtile_neg_02`. B1 and B3: none.
- Warm-lit white objects: B2 (the reading above the gate) boxes `lampwarm6_glass_neg_02`, the frame the 2026-11-25
  round failed on. The yellow note stands above the gate and reads 0.13. B1 and B3 read 0.03 and 0.09 there and draw
  nothing. `lampmid6_glass_neg_02`: no box, any candidate.
- The glass table's reflections: found 14.8 → 14.8 and boxes 0.6 → 0.6 for every candidate but B2 (0.6 → 0.8, the
  frame above).

**What the contact sheets show** (`results/2026-11-26_light/sheets/`, every gained and lost barrel and every new box
looked at).
- B1, B2, B3 gained: real barrels. The blue stripe of an orange barrel gets painted, or the body of a blue one.
- Their new boxes are small second boxes on real barrels (a cap boxed apart from its body; a box across two touching
  barrels). None is on the floor or on clutter.
- B4 gained: bathroom barrels painted solid. Its new boxes sit on three clutter things: the red jar with a teal
  label (orange with a blue band, which is what a barrel is to the detector), the blue tin, the small figure.
- O1: the wider orange paints the whole bathroom floor. Two close-up barrels drown in it. Boxes on floor patches.
- O3: a box on the pale wood table and on the cool bathroom floor.

#### Why the folds failed where the idea works (in-sample, `insample.md`; never a verdict)

| setting | found, all places | bathroom | boxes |
|---|---|---|---|
| B1's ramp picked on all eight places (0.08 → 0.18, S to 30, hue low to 88) | +7.42 | +5.75 | +0.75 |
| B1's ramp picked without the bathroom (0.11 → 0.30, S to 45) | +3.92 | +2.25 | +0.42 |
| B4 picked on all eight places (delta 0.25) | +11.42 | +9.75 | +1.00 |
| B4 picked without the bathroom (delta 0.15) | +13.25 | +10.25 | +4.75 |

- Without the bathroom, the only warm place left to learn from is the ottoman. Its blue fades more slowly, so it
  teaches a slow ramp. Its black lid has no clutter that looks blue, so it teaches the loosest delta.
- All 54 ramp settings gain in-sample (+0.92 to +6.67). All three readings give the same best in-sample result
  (+7.42). The reading is not what limits the rule. The warm end of the ramp is.
- In-sample, delta 0.30 and 0.25 pass and 0.20 and 0.15 fail on boxes.

### Takeaway

- **What to read the light from:** the bright pixels that are not barrel-like, or the rows above the gate. Both
  separate every warm frame from every other frame. The whole frame is fooled by close orange barrels. Colorless
  pixels do not work.
- **"Blue follows the light" did not pass.** +3.92 placements against a margin of +4.00, no barrel lost, no box on any
  empty frame. With the 2026-11-25 version (+5.9, weak pass), every variant lands between +2.4 and +5.9. The gain is
  real at barrel level and too small for this judge to call.
- **The gray-olive blue needs more than the two numbers, and one more number reaches it.** "Bluer than the light"
  finds 14.25 of 15 bathroom placements held out. It fails because the margin was chosen on the ottoman alone.
- **Orange: no.** The light does not predict the ottoman's orange. Following it floods the bathroom floor (FAIL).
  Darkness of the scene tells the two apart, but one dark place cannot teach itself. One hint from a place never
  trained on: on the parked black table the darkness rule picked on the ottoman finds 5 → 8 of 26, with no new box on
  nothing.
- **The limit is the data, not the idea.** Two warm places that need different numbers.

### Open point for Tanush and Dave

"Bluer than the light" changes no pixel. But comparing a pixel with the light's color is the same arithmetic as
correcting the pixel and then thresholding it. Whether that is inside "no image correction" is their call.

### What next

1. Shoot a third warm-light place before any further round (below).
2. Then one more round of B4 with the margin chosen on two warm places.
3. The same idea made local is C4 (the stripe by contrast): bluer than what is above and below it, not than the light.
4. For orange: O2 again once a second dark place exists.

### Not done

- No second round. The addendum would have had to fix the margin after seeing which one works at the bathroom.
- The local-surround form of the relative rule; blue and orange together (E8); choosing the ramp from the paint
  instead of from the detector's count; the other ten readings as detector inputs.
- No walkthrough with Tanush yet. `TODO.md`, `STATUS.md`, `EXPERIMENTS.md`, `DECISIONS.md` were not edited.

### For Tanush, in plain words

**What is the best thing to read the light from, and why?** The bright things in the picture that are not
barrel-colored. Bright things are mostly white or pale, so they show the lamp's color. Leaving out anything orange or
blue stops a close barrel from being mistaken for the lamp. Your idea, the rows above the horizon, works about as
well and is simpler. Its weak point is that it reads whatever stands behind the table: a yellow note under the lamp
made it draw a box on an empty glass frame. At the detector the three readings ended within 1.5 placements of each
other, which is inside the noise.

**What can a light-following rule fix?** Blue paint that has lost its strength under a yellow lamp but still looks
bluish (the bathroom under the mid lamp, the ottoman under the warm lamp). With one more rule, "bluer than the light",
also the blue that has gone gray-olive under the warm bathroom lamp.

**What can it not fix?** Orange on the dark ottoman: that follows the surface, not the lamp. Blue that is washed out
while the light reads white (the wood desk under the cool lamp). A scene with nothing pale in it: on the ottoman the
reading has only the wall behind. Clutter that is orange with a blue band: once blue is loosened, the jar is a barrel.

**What data would settle it?** One or two more places, three frames each (`core_01`, `neg_01`, then `clutter_01`
last):
1. **The warm lamp on a pale table or floor that is not the bathroom**, lamp at warm and at mid. This is the one that
   matters most. It gives a third warm place, so the ramp's end and the margin are no longer taught by one place. Put
   the blue tin and the red jar in the clutter frame: they are where the false boxes were.
2. **A dark table or a dark cloth under ordinary white light** (window or ceiling). It says whether the orange shift
   comes with a dark surface. Today only the ottoman says so, and the parked black table hints at it.

## 2026-11-26 — M1: every placement counted once, a misplaced box counted once (`experiments/2026-11-26_measure`)

- **Question.** The review found that one arrangement shot under five lamp settings counts as five times as many
  barrels, and that a box on a real barrel that fails the strict rule is charged as a miss plus a false box. What do
  the numbers say when both are fixed? The strict rule itself is not changed.
- **Method** (PREREG written first). A placement = one barrel in one arrangement; it counts the share of its lights in
  which it is found. Second accounting: each barrel found / found with the box off / missed; each box on its barrel /
  wrong color / second box / on nothing; "on a barrel" = at least half of the smaller of the two boxes lies inside the
  other. The vendor is assumed to find every barrel on the two white tables without vendor files (Tanush, 2026-11-26);
  those rows are marked ASSUMED. Code: `src/barrels/counting.py`, `report.py --places`.
  `python barrels/experiments/2026-11-26_measure/run.py`.
- **Data.** Train frames. Measured: the 15 new ordinary conditions with vendor files, 117 frames, 243 barrels = 108
  placements in 47 arrangements at 6 places. Assumed: home and campus, 37 frames, 64 placements.
- **Checks, all pass.** Found equals the v2 rule's hits on all 285 frame × arm pairs. The old numbers are reproduced
  exactly: ours 148 and the vendor 177 of 243; HOME 28 of 29; CAMPUS 35 of 35. Per-frame counts equal the old table's.
- **Result** (found = strict, per placement; in brackets per frame):

| place | placements (lights) | ours found | ours box off | ours on nothing | vendor found | vendor box off | vendor on nothing |
|---|---:|---:|---:|---:|---:|---:|---:|
| ABP gray | 16 (1) | 10.0 (10) | 1.0 | 0 | 16.0 (16) | 0.0 | 0 |
| bathroom floor | 15 (4) | 4.0 (16) | 0.0 | 0 | 7.0 (28) | 0.8 | 0 |
| glass table | 15 (5) | 14.8 (74) | 0.2 | 3 | 12.0 (60) | 2.8 | 6 |
| ottoman | 15 (3) | 3.0 (9) | 0.0 | 1 | 12.3 (37) | 0.7 | 0 |
| pale wood | 15 (1) | 13.0 (13) | 0.0 | 1 | 12.0 (12) | 1.0 | 0 |
| ABP white (occlusion set) | 32 (1) | 26.0 (26) | 0.0 | 0 | 24.0 (24) | 3.0 | 1 |
| **measured, 6 places** | **108 (15)** | **70.8 (148)** | **1.2** | **5** | **83.3 (177)** | **8.2** | **7** |
| campus, vendor ASSUMED | 35 (1) | 35.0 (35) | 0.0 | 0 | 35.0* | | |
| home, vendor ASSUMED | 29 (1) | 28.0 (28) | 0.0 | 0 | 29.0* | | |
| **measured + ASSUMED** | **172 (17)** | **133.8 (211)** | **1.2** | **5** | **147.3\*** | **8.2** | **7** |

- **Takeaway.**
  - Per placement the vendor is ahead on the measured places, 83.3 against 70.8 of 108. Found either way (strict, or
    with the box off): 91.5 against 72.0.
  - The vendor's 30 "false boxes" were 23 boxes on a barrel that fail the strict rule and 7 boxes on nothing; all 7
    are on empty frames. Ours: 2 and 5, none on an empty frame.
  - The glass table is 15 placements, not 75 barrels. "74 against 60" is 14.8 against 12.0, and the vendor has 2.8
    more with the box off.
  - No winner is named for a single condition.
  - The test for "on a barrel" does not matter on today's frames: with the audit's "position" rule not one frame
    changes; with "overlap", 5 of the vendor's 23 fall back to "miss plus a box on nothing".
- **Caveat.** The assumption (vendor perfect on white) is an assumption. The one white table with vendor files, the
  ABP occlusion set, has the vendor at 24 of 32.
- **Next.** Tanush's word on the definition (decision record below). Shoot the home white table with vendor files.

## 2026-11-26 — M2: the noise floor of the counts (`experiments/2026-11-26_noise_floor`)

- **Question.** How much do the counts move under a change that means nothing? The answer is the margin of the
  never-regress check and of the pass rule.
- **Method** (PREREG first; one addendum, dated, before any candidate was judged). The fixed color model with one of
  its seven numbers moved one step (hue edges ±1, saturation floors ±3, brightness floor ±2): 14 neighbours (set A).
  12 seeded moves of several numbers at once (set B). 12 more that are never used for a margin (set C). Today's
  detector, every train frame, HOME with the model as it is. `python barrels/experiments/2026-11-26_noise_floor/run.py`
  (2 minutes). It writes `results/baseline/margins.json`.
- **Data.** 261 train frames, 28 conditions, 10 places. The ordinary conditions: 154 frames, 172 placements, 8 places.
- **Result** (absolute change in found: median / 90th percentile / maximum):

| level | one step (14) | several at once (12) |
|---|---|---|
| one ordinary condition, barrels | 0 / 0 / 6 | 0 / 2 / 6 |
| one place, placements | 0 / 0.33 / 6 | 0.22 / 1.33 / 6 |
| the ordinary conditions together, placements | 0.67 / 3.58 / 6.20 | 4.59 / 8.78 / 10.92 |
| boxes not on their barrel, together | 0.2 / 1.0 / 1.25 | 0.77 / 1.27 / 1.85 |

- **Takeaway.**
  - One barrel flipping "for no reason" is the normal case at a condition. Six can flip: the ABP gray table sits on a
    hue edge (orange hue low 3 → 4 costs it 6 of 16 placements, 3 → 2 gains it 4).
  - Over everything, a change that means nothing moves found by up to 10.92 placements down and 4.00 up. It is
    one-sided: 15 of 26 neighbours lose, 8 gain. The fixed model was picked for scoring well.
  - Small changes add up: with margins from one step alone, 6 of 12 joint moves were called FAIL. So the margins are
    taken over sets A and B (the registered rule 3).
  - No neighbour, of 38, puts a box on a clean empty frame. The zero for clean empty frames can stay.
  - On the 12 unseen moves (set C) the pass rule called 2 (one PASS at +5.4, one FAIL on boxes); the never-regress
    check failed none.
- **The addendum, stated plainly.** The PREREG said: a margin is the largest *absolute* change. The first run showed
  the one-sidedness. The addendum, written before any candidate was judged, takes one margin per direction (a gain
  against the largest gain, a loss against the largest loss). Both versions are stored, and the sanity checks give the
  verdict under both. It changes one verdict: see the next entry.
- **Next.** Re-run the script whenever the default color model or detector changes.

## 2026-11-26 — M3: the standard pass rule and its sanity checks (`experiments/2026-11-26_judge`)

- **Question.** Does one written rule with measured margins say sensible things about cases we know?
- **Method** (PREREG first). The rule: `docs/EVAL.md`, "The standard pass rule (2026-11-26)"; code `src/barrels/judge.py`,
  command `tools/judge.py`. Baseline: today's default. `python barrels/experiments/2026-11-26_judge/run.py`.
- **Data.** The ordinary train conditions: 154 frames, 172 placements, 8 places. One judge run: 25 s.
- **Result.**

| candidate | found, placements | per frame | boxes not on their barrel | verdict | with the margins as first registered |
|---|---|---|---|---|---|
| today against itself | 133.8 → 133.8 | 211 → 211 | 1.9 → 1.9 | NO CLEAR DIFFERENCE, nothing changed | the same |
| 14 one-step changes, 12 joint moves | −10.9 to +4.0 | | | 26 of 26 NO CLEAR DIFFERENCE (by construction) | |
| 12 unseen joint moves | −9.3 to +5.4 | | | 10 of 12 NO CLEAR DIFFERENCE; 1 PASS, 1 FAIL | 11 of 12 |
| hand thresholds per condition (in-sample) | 133.8 → 156.8 | 211 → 281 | 1.9 → 1.5 | **PASS** | PASS |
| blue follows the light, whole frame (C2), leave one place out | 133.8 → 139.7 | 211 → 233 | 1.9 → 3.1 | **PASS** | NO CLEAR DIFFERENCE |
| blue follows the light, above the horizon (C2b), leave one place out | 133.8 → 137.0 | 211 → 222 | 1.9 → 2.9 | NO CLEAR DIFFERENCE | NO CLEAR DIFFERENCE |

- **Takeaway.**
  - The two required answers hold: today against itself changes nothing; the hand thresholds pass (the old rule failed
    them on all three clauses). 71 barrels gained, 1 lost (pale wood, at its margin).
  - The light rule C2 passes under the rule as used: +5.9 placements, all at the bathroom floor (+4.2 of 15) and the
    ottoman (+1.7 of 15), 22 barrels gained, none lost, boxes not on their barrel +1.2 (margin 1.85), one more box on
    an empty frame with clutter (0.2, margin 1.00). **This PASS is close to the margin and should be read as weak:** it
    is 1.9 placements above it, one unseen change that means nothing gained 5.4 and passed too, and with the margins
    as first registered it is NO CLEAR DIFFERENCE. The fold that held out the bathroom floor picked another setting
    than the other seven.
  - C2b (the round-2 version) gains 3.2 placements: no clear difference.
- **Next.** Every later experiment is judged with `tools/judge.py`. C3 (a fresh try of the light rule) can start from
  the C2 pages in `results/2026-11-26_judge/blue_follows_the_light__c2/`.

## 2026-11-16 — Ceiling check: per-frame thresholds set from the frame's own labels

**Question** (script header, before the run). Before designing a per-image threshold estimator: if every frame's thresholds were perfect, how many barrels would today's detector find? Hypothesis: black + bright wood go from 9 of 152 to well over half.

**Method.** `experiments/2026-11-16_hs_oracle/run.py`. Per frame and per color with an unoccluded box, the range is re-made from that frame's labeled pixels: `hue` (sector from the frame, S floor as adopted), `hue+sat` (the adopted recipe on the frame alone), `hue+sat+stripes` (added after the first run: a color's pixels include its stripes on the other color's barrels; without it a frame with only blue barrels kept the adopted orange range). Same detector. Not a method: the thresholds read the answer.

**Data.** Train frames only (HOME 16, CAMPUS 21, BLACK 10, wood bright 60, wood dark 30).

**Results** (`results/2026-11-16_hs_oracle/summary.md`; found / barrels (false boxes)).

| set | base | hue | hue+sat | hue+sat+stripes |
|---|---|---|---|---|
| HOME (stored model, not LOSO) | 25 / 29 (1) | 25 / 29 (1) | 25 / 29 (5) | 25 / 29 (5) |
| CAMPUS | 34 / 35 (0) | 33 / 35 (0) | 27 / 35 (0) | 30 / 35 (1) |
| BLACK | 2 / 26 (0) | 6 / 26 (5) | 14 / 26 (1) | 17 / 26 (1) |
| wood cool 3 + 6 | 4 / 42 (2) | 5 / 42 (2) | 20 / 42 (4) | 24 / 42 (7) |
| wood mid 3 + 6 | 2 / 42 (0) | 3 / 42 (0) | 6 / 42 (9) | 10 / 42 (12) |
| wood warm 3 + 6 | 1 / 42 (1) | 1 / 42 (1) | 3 / 42 (8) | 2 / 42 (12) |
| wood brightness 1 | 0 / 63 | 0 / 63 | 0 / 63 | 0 / 63 |

Misses left on black + bright wood with `hue+sat+stripes` (reason log): stripe too narrow 31, too flat or tall 16, no body right above and below 13, stripe not painted 11, too small 10, wrong place 9, body not painted 8.

**Takeaway.** The hypothesis is wrong: the ceiling is 53 of 152, about a third. Per-image thresholds can at best bring the black table and the cool lamp to about two thirds; under the mid and warm lamps even label-perfect thresholds find almost nothing, because the orange range that fits the barrels there paints the wood table (sheets), and a blue barrel needs its orange stripe to be found. Moving the hue alone does almost nothing (9 → 15 of 152): the saturation floor matters more. Tight per-frame ranges cost a little on campus (34 → 30). Most remaining misses are stripes that come out in pieces, which is the detector's side.

**Next.** Decide with Tanush: a per-image estimator is worth building for black + cool light only together with a detector that tolerates a stripe in pieces; mid / warm wood needs a way to find a blue barrel without its orange stripe (the blue body is separable everywhere).

---

## 2026-11-16 — The hs model fit on all train tables instead of home only (pre-registered)

**Hypothesis** (`experiments/2026-11-16_hs_pooled/PREREG.md`, committed before the run, bb65914). The same recipe fit on all tables recovers blue and the black table without losing home or campus; orange on wood expected to cause trouble, hence an arm that widens blue only.

**Method.** `experiments/2026-11-16_hs_pooled/run.py`. Arms: `base` (adopted), `all` (fit on home + campus + black + bright wood), `nowood` (home + campus + black), `blue` (orange from home, blue from all). Fit labels: home masks; elsewhere box cores at the class's hue peak. New arms scored leave-one-scene-tag-out over all sets; same detector. Acceptance: home ≥ 0.91 and campus ≥ 0.97; no box on a clean negative; then most barrels found on black + bright wood. **Two runs:** run 1 had a label flaw (in 20 wood frames the peak inside the blue cores was the orange stripe, so the pooled blue range came out as hue 12–113); run 2 looks for the peak on the class's side of the hue circle only. Both kept (`results/2026-11-16_hs_pooled/run1/`).

**Data.** Train frames only: HOME 16, CAMPUS 21, BLACK 10, wood bright 60 (brightness 1: 30 frames, reported, never fit); Dave 12 indicative.

**Results, run 2** (found / barrels (false boxes), score).

| set | base | all | nowood | blue |
|---|---|---|---|---|
| ranges | o 3–13 S≥140; b 103–119 S≥113 | o 4–18 S≥126; b 95–113 S≥65 | o 4–17 S≥140; b 97–115 S≥131 | o 3–13 S≥140; b 95–113 S≥65 |
| HOME | 25 / 29 (0), 0.93 | 20 / 29 (12), 0.66 | 24 / 29 (1), 0.89 | 21 / 29 (12), 0.68 |
| CAMPUS | 34 / 35 (0), 0.99 | 33 / 35 (2), 0.94 | 32 / 35 (2), 0.93 | 33 / 35 (1), 0.96 |
| BLACK | 2 / 26 (0), 0.12 | 10 / 26 (3), 0.46 | 4 / 26 (3), 0.23 | 2 / 26 (0), 0.12 |
| WOOD bright | 7 / 126 (3), 0.10 | 18 / 126 (13), 0.23 | 10 / 126 (4), 0.14 | 19 / 126 (6), 0.25 |
| DAVE* | 11 / 34 (2), 0.47 | 8 / 34 (3), 0.37 | 8 / 34 (1), 0.40 | 8 / 34 (3), 0.37 |

Run 1: `all` 21 / 126 on bright wood with 204 false boxes, `blue` 21 / 126 with 134 (the blue label flaw); `nowood` identical to run 2.

**Takeaway.** No arm passes condition 1, in either run; nothing is proposed. A blue floor low enough for the warm lamp (S ≥ 65) brings the bluish home wall back (12 false boxes at home); an orange sector wide enough for wood (to hue 18) paints the table. The reason log on the misses (`by_eye.md`): on the black table the barrels are painted but the stripe comes out in pieces, because the pale window highlight on the barrel tops is not body color and the stripe is accepted only where body sits right above and below it; on wood it is unpainted bodies and stripes. So a fixed range per color cannot serve every table, which is what the transfer tables of the histogram look said. H "pooled fit recovers blue and black": wrong.

**Next.** Thresholds set per image from the frame's own histogram (Tanush's proposal, 2026-11-16), pre-registered, scored with the same table; the detector's "body right above and below the stripe" test against highlights is a second, separate lead.

---

## 2026-11-16 — Hue × saturation histograms: what moves between lights and tables (TODO 8)

**Hypotheses** (in the script header, before the run). H1: the barrels' hue moves little between lights, their saturation a lot. H2: the wood table overlaps the orange body in H × S, so no H × S threshold separates them under at least the warm lamp. H3: at brightness 1 the fixed model fails on the V ≥ 40 gate, not on H or S.

**Method.** `experiments/2026-11-16_hs_hist/run.py`, `src/barrels/hshist.py`, `tools/hs_hist.py`. Per set one fine histogram (hue 180 × S 128 × V 32) of the pixels below row 50, split by the hand-drawn boxes into orange body, blue body (the inner 0.6 × 0.8 of each unoccluded box, pixels within ±12 hue of the class's tallest peak) and the rest (outside every box + 4 px). HOME also from the masks, as a check of the box shortcut. Fixed model = adopted `eb863d84`. Ceiling = the best lookup in 36 × 32 H × S bins (and 36 × 32 × 8 with V) at 1 % of the non-barrel pixels painted, in-sample. Nothing tuned, nothing adopted.

**Data.** Train frames only: HOME 16, CAMPUS 21, BLACK 10, wood ladder 90 (10 arrangements × 9 lamp settings). Splits assigned before the run; the 47 test frames are refused.

**Results** (`results/2026-11-16_hs_hist/summary.md`; medians; "keeps" = share of the bright body pixels the fixed model labels; "ceiling" = best H × S / best H × S × V).

| set | orange hue / S | keeps | ceiling | blue hue / S | keeps | ceiling (H × S) | rest hue / S | flood orange / blue |
|---|---|---|---|---|---|---|---|---|
| HOME (masks) | 9 / 213 | 93 % | 100 / 100 | 110 / 225 | 80 % | 92 | 57 / 31 | 0.1 / 0.0 % |
| HOME (box cores) | 9 / 217 | 99 % | 100 / 100 | 110 / 231 | 97 % | 100 | 57 / 31 | 0.1 / 0.0 % |
| CAMPUS | 9 / 217 | 98 % | 100 / 100 | 106 / 217 | 98 % | 100 | 66 / 19 | 0.3 / 0.3 % |
| BLACK | 14 / 197 | 43 % | 99 / 100 | 99 / 149 | 16 % | 100 | 13 / 13 | 0.1 / 0.1 % |
| wood warm 3 | 13 / 207 | 46 % | 66 / 80 | 105 / 97 | 43 % | 100 | 18 / 181 | 2.0 / 0.0 % |
| wood warm 6 | 11 / 215 | 69 % | 72 / 76 | 106 / 111 | 46 % | 100 | 17 / 207 | 2.5 / 0.0 % |
| wood mid 3 | 13 / 199 | 48 % | 82 / 89 | 103 / 103 | 33 % | 100 | 19 / 151 | 0.8 / 0.0 % |
| wood mid 6 | 12 / 215 | 73 % | 80 / 90 | 101 / 133 | 30 % | 100 | 19 / 189 | 1.6 / 0.0 % |
| wood cool 3 | 13 / 203 | 46 % | 89 / 95 | 103 / 161 | 48 % | 100 | 22 / 133 | 0.3 / 0.0 % |
| wood cool 6 | 13 / 213 | 52 % | 91 / 97 | 101 / 195 | 31 % | 99 | 22 / 147 | 0.3 / 0.0 % |
| wood brightness 1 (×3) | 11–12 / 207–215 | 87–93 % of the 18–30 % bright enough | 100 | too dark (1 % bright enough) | 0 % | — | 7–9 % bright enough | 0.1–0.2 / 0.0 % |

Transfer (best H × S lookup of one set used on another): the home lookup on warm wood keeps 82–87 % of orange and paints 29–48 % of the rest; the warm-3 lookup at home keeps 46 %. The model's own percentile recipe re-fit per wood light would paint 36–87 % of the rest under warm and mid light (it never looks at the table).

**Takeaway.** H1 half right: hue drifts 3–5 units (orange) and 4–11 (blue), both toward yellow/green, about the body's own spread and enough to leave a sector fit at home; S collapses for blue under warm light, not for orange. The black table under window light shifts the colors as much as the lamp does, so the camera's own exposure / white balance is a likely cause (untested). H2 holds: the orange ceiling is under 90 % in five of six bright wood settings; blue and the black table are a pure threshold-placement problem (ceiling 99–100 %). H3 holds. On wood the fixed model's failure is missed barrel pixels, not a flooded table (clutter aside: cardboard and wrappers are painted orange). The box-core shortcut reads a few points high (HOME 99 / 97 % against 93 / 80 % from the masks).

**Next.** Note for Tanush: `docs/HS-HISTOGRAMS-2026-11-16.md` (pictures in `docs/img/hs_hist/`). Leads for the adaptive model, each to be pre-registered: the frame's own blue peak as the hue-shift estimate; the table peak as the scene reference; a brightness gate that follows the frame; and measuring where the detector stands on the wood train frames today (`tools/report.py`).

---

## 2026-11-11 — A barrel hidden at the side: narrow stripe + hidden side from the body (pre-registered; branch `wip/occlusion`)

**Hypothesis** (`experiments/2026-11-11_occl_narrow_stripe/PREREG.md`, committed before the run, 194bc1c). The side-occlusion miss is the width floor: `stripe_w_min` 0.4 → 0.25 finds it without new false boxes (a stripe is about a quarter barrel-width tall and "not taller than wide" already binds below that). With the lower floor the box needs a better side rule: (h) `occl_body_side`, the hidden side read from the body columns joined to the stripe.

**Method.** `experiments/2026-11-11_occl_narrow_stripe/run.py`; configs base, w25, w25h, h; report-only w35, w30, w20. Adopted hs model `eb863d84`, camera `AIM_4A8B6118_BOXFIT`, v2 rule. Acceptance: (1) no found barrel lost on HOME / CAMPUS, (2) no false box added there, (3) Dave not lower, (4) every box added on unlabeled frames is a real barrel by eye, (5) `occl_02` found. Prefer w25h, then w25; if neither passes, nothing is adopted.

**Data.** Train frames only: HOME 16 (adopted model on its own fit frames, so not the LOSO headline; for comparing configs only), CAMPUS 21, DAVE 12 (indicative). Unlabeled: WOOD 25, REC 238 frames, LIVE 1. Test frames never loaded.

**Results** (`results/2026-11-11_occl_narrow_stripe/`: `summary.md`, `changes.csv`, `by_eye.md`).

| config | HOME found / false / missed | CAMPUS | Dave | mean IoU of found, HOME / CAMPUS | `occl_02` | added on WOOD / REC |
|---|---|---|---|---|---|---|
| base | 25 / 1 / 4 (0.91) | 34 / 0 / 1 (0.99) | 0.47 | 0.878 / 0.865 | missed | — |
| w25 | 25 / 1 / 4 | 35 / 0 / 0 (1.00) | 0.49 | 0.878 / 0.855 | found, IoU 0.51 | 2 / 4 |
| **w25h** | 25 / 1 / 4 | 35 / 0 / 0 (1.00) | 0.49 | 0.888 / 0.859 | found, IoU 0.68 | 2 / 4 |
| h | 25 / 1 / 4 | 34 / 0 / 1 | 0.47 | 0.888 / 0.864 | missed | 0 / 0 |
| w35, w30 | as base | as base | 0.49 | | missed | 0 / 0, 2 / 1 |
| w20 | 25 / **2** / 4 (0.89) | 35 / 0 / 0 | 0.49 | | found | 2 / 7 |

(h) moves 18 WOOD boxes (median largest-edge shift 8 px, max 38) and 72 REC boxes (median 2 px, max 12), removes none.

By eye, the 8 boxes w25 / w25h add: 6 real (campus `occl_02`; Dave `speckle_snap_10`; `r2_pan` 034, 035; `r3_enter_leave` 014, 047: barrels entering at the right frame edge), **2 false, both on wood** (`atwarm_wood_core_01`: a second box on half of an orange barrel where the table segments as orange; `upmid_wood_core_01`: an orange box on a far blue barrel).

**Takeaway.** Conditions 1, 2, 3, 5 pass; **4 fails** on two wood frames. By the pre-registered rule nothing is adopted: `stripe_w_min` stays 0.4, `occl_body_side` stays off, the code is on `wip/occlusion` behind the switches. Wherever the color model works the change only adds real barrels; on wood the front end already fails (61 boxes on 25 frames at base). One labeled frame carries the gain, so the evidence is thin both ways.

**Next.** Tanush decides: keep off until the wood front end exists, or adopt now. Re-run on the step-3 `occl` 25 / 50 / 75 % shots. The other-color occlusion is step 9.

---

## 2026-11-11 — Occlusion attribution: which test refuses each missed barrel (branch `wip/occlusion`)

**Hypothesis** (in the script header, before the run). The misses are occluded barrels and die in one of three places: no stripe candidate, a candidate refused by a proportion test or `body_min`, or a box drawn in the wrong place.

**Method.** `experiments/2026-11-11_occl_attribution/run.py`. The detector got an optional reason log (`detect(..., log=[])`; answers unchanged, tested). For every truth barrel left unmatched under the v2 rule: the log entries overlapping its box and the pixels inside it; cause by a fixed order.

**Data.** HOME 16 + CAMPUS 21 train frames, adopted model. Test frames never loaded (so campus `occl_01` and `cluster_01`, which are test frames, are not in this).

**Results** (`results/2026-11-11_occl_attribution/`).

| set | frames | barrels | found | missed | false | occluded | occluded found |
|---|---|---|---|---|---|---|---|
| HOME | 16 | 29 | 25 | 4 | 1 | 6 | 2 |
| CAMPUS | 21 | 35 | 34 | 1 | 0 | 4 | 3 |

| missed barrel | cause | numbers |
|---|---|---|
| campus `occl_02` blue, behind the robot | stripe refused: `width` | stripe 16 px wide, barrel 53.6 px, floor 0.4 → 21.4 px |
| home `occl_01` blue, `occl_02` orange | stripe refused: `height` | the stripe joins the front barrel's body of the same color: 28–29 px tall, 15 expected |
| home `cluster_01`, two orange | stripe refused: `height` (19 px vs 11); a blue sliver between them passes as a stripe and gives the one false box | |

**Takeaway.** Two failures, not one. Side occlusion by a non-barrel is a width-floor problem (step 7; "half a barrel showing" is right at the 0.4 floor because a stripe is ~15 % narrower than its barrel). Occlusion by a barrel of the other color is the mixed-color stacking of step 9: 4 of the 5 misses. No miss is a segmentation failure. `live/snapshots/robot_snap0.png` is the close-up case (g), not an occlusion case; no frame of the live occlusion miss was saved.

**Next.** The narrow-stripe experiment above; step 9 for the stacking.

---

## 2026-11-11 — Eval report: one table (TODO 6; branch `wip/eval-report`)

**Purpose.** No new method. Many sets and many per-experiment tables made it hard to see what is better where. One command shows data set × scenario rows with a candidate and a baseline side by side, and its per-set headline numbers must reproduce the published ones. Metrics unchanged (EVAL.md v2 rule, `eval_det`).

**Method.** `src/barrels/report.py` + `tools/report.py`; script `experiments/2026-11-11_eval_report/run.py`. Candidate = hs `eb863d84` + `DetConfig()`. Baseline = v1 `afd85483` + the same detector; second table = v1 + the 2026-11-05 detector (`stripe_mode=bands,body_min=0,height_max=0,body_width=0,cover_rows=false`). Home scored leave-one-scene-out (model re-fit per fold); other sets with the stored model.

**Data.** Train frames only: HOME 16, CAMPUS 21; DAVE 12 (indicative, in no split). Test frames refused by the tool, never opened.

**Results** (`results/2026-11-11_eval_report/`): found / missed / false, score.

| Set | Candidate (hs + today) | v1 + today's detector | v1 + 2026-11-05 detector |
|---|---|---|---|
| HOME (LOSO) | 25 / 4 / 0, **0.93** | 25 / 4 / 0, 0.93 | 25 / 4 / 0, 0.93 |
| CAMPUS | 34 / 1 / 0, **0.99** | 9 / 26 / 1, 0.39 | 10 / 25 / 1, 0.41 |
| DAVE* | 11 / 23 / 2, **0.47** | 0 / 34 / 0, 0.00 | 0 / 34 / 0, 0.00 |

False boxes on negative frames: 0 for every arm and set. Candidate median width ratio 0.98 / 0.96 / 0.96, median bottom error 1.0 / 2.0 / 1.0 px (home / campus / Dave).

**Takeaway.** The published numbers reproduce (0.93, 0.99, 0.47; "v1 0.41" is v1 with the 2026-11-05 detector, v1 with today's detector is 0.39, both as logged 2026-11-08). Every candidate miss on home and campus is in an occlusion or cluster scenario, and v1 misses the same home barrels, so the front end is not the cause. Edge frames give wide boxes (width ratio 1.29 home, 1.50 campus). Scenario rows are one or two frames each: they show where, not how much.

**Next.** `tools/report.py --cand-det ... --base-model default` is the standard comparison from here on; NEW sessions appear as their own row group once they have box labels and a split.

---

## 2026-11-09 (later) — The close-up under a far barrel got no box (hardening (g); branch `wip/redesign`)

- **Setting:** live run with Dave (`BARRELS_MODEL` = the hs candidate). A close-up orange barrel filling the bottom of the frame was segmented but got no box; a barrel touching the kicker likewise (no frame saved for that one). Frame saved: `live/snapshots/robot_snap0.png` (not in git: contains Dave's desk, import later if wanted).
- **Diagnosis:** the close-up's stripe is cut by the frame bottom (34 × 19 px of blue at rows 461–480), so it rightly takes the stripeless step-1 route (`detect`: "stripe below the frame"), and step 1 finds it (x 128–394, y 250–480, truncated). `detect` then drops a stripeless piece when a stripe barrel "already accounts for it", testing **column** overlap only (`_x_overlap > 0.3`). The far blue barrel on the table behind (x 149–207, y 123–184) stands directly above the close-up in the picture: overlap 1.0, piece dropped. Erasing the far barrel from the mask gives the close-up its box. The detector on `barrels` has the same test.
- **Change:** `DetConfig.cover_rows=True`: a stripe barrel covers a piece only if their boxes also share rows. Test: a far barrel above a close truncated one → both boxes; `cover_rows=False` → the old loss. Sweep re-run (`experiments/2026-11-08_seg_hs_v2/run.py`), the old-detector arm pinned to `body_width=0, cover_rows=False` so "barrels today" stays what runs on `barrels`:

| arm | home LOSO v2 | campus v2 | campus neg FD | Dave |
|---|---|---|---|---|
| v1 + old detector (`barrels` today) | 0.93 | 0.41 | 0 | 0.00 |
| hs `o5 b15 h5-95 m2` + hardened (a–g) | 0.93 | 0.99 | 0 | 0.47 (was 0.44) |
| v1 + old finder but with (g) on (the un-pinned first re-run) | 0.84 | 0.79 | **5** | 0.27 |

- **Takeaway:** (1) the close-up case is fixed on the saved frame (`detect_image.py` draws the orange box 128–394 × 250–480 and the blue one behind it). (2) The column-only test had been masking clutter pieces by accident: with the old finder and v1 pixels, (g) lets five false boxes onto campus negatives. With the hardened finder and the hs pixels nothing changes but the close-up, so (g) is safe only together with (a)–(f) — recorded here so nobody back-ports it alone. (3) The kicker case needs a saved frame before it is called the same bug.
- **Next:** TODO item "fix close-ups" closes when Tanush confirms live; "touching the kicker" waits for a `tm save`.

## 2026-11-09 — Box width from the body, not the stripe (hardening (f); branch `wip/redesign`)

- **Setting:** Tanush ran the candidate front end on the campus frames with `detect_image.py` and found the boxes "too thin" (`core_02`, most frames). Measured: box width / his label width 0.83–0.85 on the big barrels, because `barrel_from_stripe` copied the box's left and right edges from the stripe's columns, and a stripe's outermost pixels curve away from the camera and go dark. The segmentation itself reached the body's edge (columns 62–181 vs label 59–186 on `core_02`'s big orange barrel). Today's detector on `barrels` has the same flaw; it was invisible at home because the barrels were small. The v2 rule did not see it either: an IoU ≥ 0.5 match passes a box 15 % too thin.
- **Hypothesis (stated before the change):** taking the box edges from the body-colored columns joined to the stripe lifts the median width ratio on the 21 campus train frames from about 0.85 to above 0.95 without changing the v2 score or adding a false detection.
- **Method:** `detector._body_columns` (walk outward from the stripe while a column holds ≥ 2 body pixels in the box's rows outside the stripe rows, gaps of 2 columns allowed; columns under another found stripe are never added; at most `body_width` = 1.2 × the expected width, trimmed evenly). Only for a "full" stripe; the partly-hidden path keeps the geometry's width. `eval_det.Match.width_ratio` and `width_ratio` columns in `per_barrel.csv` / the summary table / `score()` so the quantity is reported from now on. Before/after from `experiments/2026-11-08_seg_hs_v2/run.py` (`--body-width 0` = before → `results/2026-11-08_seg_hs_v2_bw0/`). Two tests (a stripe with dark outer columns gives the full box; a touching same-color pair stays one barrel wide each).
- **Results** (`hs o5 b15 h5-95 m2`, 21 campus train frames, 34 matched barrels):

| | width ratio median | worst | campus v2 | home LOSO v2 | neg FD |
|---|---|---|---|---|---|
| before (`body_width=0`, the stripe's width) | 0.90 | 0.74 | 0.99 | 0.93 | 0 |
| **after (`body_width=1.2`)** | **0.96** | **0.88** | 0.99 | 0.93 | 0 |
| v1 + old detector (`barrels` today), for reference | 0.95 (on the 8 it finds) | 0.57 | 0.41 | 0.93 | 0 |

  The median was 0.90, not the 0.85 I quoted from four frames (the far barrels were already close to right; the big ones were the 0.83s). The residual 4 % is the shaded edge the segmentation does not label (about 4 px per side on a 120 px barrel); the partly-hidden path's boxes come out 1.09–1.12 wide, which is the provisional camera's expected width running large (calibration, P1).
- **Takeaway:** (1) the flaw was in the box rule, not the pixels, and it is in the detector on `barrels` today as well; (2) the score could not see it, so the eval now reports the width ratio next to the score; (3) an eyeball on the pictures found in a minute what two weekends of scores did not — every result from now on gets its contact sheet looked at before it is reported.
- **Next:** Tanush's live run with Dave with `BARRELS_MODEL` set (RUNBOOK); the walkthrough acknowledgement covers (f) too.

## 2026-11-08 (later) — The hs model with per-class S floors, scored on Tanush's campus boxes (branch `wip/redesign`)

- **Setting:** Tanush boxed all 31 campus frames (`data/labels/4A8B_campus_light_*_boxes.json`; his counts matched the eyeball counts of the attribution except `held_01`, which he left without a box at first and boxed later the same evening as a blue barrel without the `held` flag; the sweep was re-run after that, and the table below is the re-run, with the first run's difference noted). The 21 train frames are now scored under the v2 rule like the home frames; the 10 test frames are untouched. The hardened detector gained (e): a stripe cut by the frame edge is hidden on that side, so the full box is drawn into the edge (`edge_01` had been widened leftward onto the table).
- **Hypothesis:** a per-class S floor — orange at the 5th–10th percentile (the far blue barrels' orange stripes), blue at the 15th–20th (the bluish home wall) — keeps home ≥ 0.91, draws nothing on any negative of either session, and beats the single-percentile runner-up on the campus v2 score.
- **Method / params:** `experiments/2026-11-08_seg_hs_v2/run.py`; `pipeline.Config(color_model="hs", hs_s_pct=(orange, blue), hs_h_pct=(5, 95), hs_h_margin=m)`, orange ∈ {5, 10, 15} × blue ∈ {10, 15, 20} × m ∈ {2, 4} = 18; baselines v1 + old detector (= `barrels`), v1 + hardened, and the count-level runner-up `s15 h5-95 m4`. Home = LOSO over the 16 train frames (v2 + pixel IoU); campus = one model fit on all 16 home frames, v2 on the 21 train frames (`held_01`: a negative in the first run, a positive in the re-run); Dave indicative. **Proposed rule** (`archive/OVERNIGHT-2026-11-08.md`, accepted 2026-11-09): home ≥ 0.91, zero false detections on every negative of both sessions, then campus v2, then home v2, then the lower blue percentile.
- **Results** (mean F1 under the v2 rule):

| config | home LOSO (o / b) | **campus train** (o / b) | campus neg FD | Dave |
|---|---|---|---|---|
| v1 + old detector (`barrels` today) | 0.93 (0.90 / 0.96) | **0.41** (0.62 / 0.20) | 0 | 0.00 |
| v1 + hardened detector | 0.93 (0.90 / 0.96) | 0.39 (0.50 / 0.29) | 0 | 0.00 |
| hs s15 h5-95 m4 (single percentile) | 0.93 (0.90 / 0.96) | 0.94 (0.97 / 0.91) | 0 | 0.53 |
| **hs o5 b15 h5-95 m2** | **0.93** (0.90 / 0.96) | **0.99** (1.00 / 0.97) | 0 | 0.44 |
| hs o5 b15 h5-95 m4 | 0.91 (0.87 / 0.96) | 0.99 (1.00 / 0.97) | 0 | 0.58 |
| hs o10 b15 h5-95 m4 | 0.93 (0.90 / 0.96) | 0.97 (1.00 / 0.94) | 0 | 0.56 |
| hs o10 b15 h5-95 m2 | 0.95 (0.93 / 0.96) | 0.94 (0.94 / 0.94) | 0 | 0.44 |
| blue at the 10th percentile (6 configs) | 0.78–0.80 (blue 0.67–0.69: the wall) | 0.91–0.97 | 0 | 0.33–0.59 |
| blue at the 20th percentile (6 configs) | 0.91–0.93 | 0.89–0.95 (blue 0.85–0.91) | 0 | 0.43–0.58 |

  First run (`held_01` unboxed): every hs config scored 0.02–0.03 lower on campus and had exactly one "false detection" — the barrel in the kicker, which every hs config finds — so the proposed rule returned no winner; `o5 b15 h5-95 m2` was 0.97 (1.00 / 0.94). Re-run with Tanush's box on that barrel: the detector's box matches it at IoU 0.96 and **the proposed rule picks `o5 b15 h5-95 m2`** (home ≥ 0.91, no false detection anywhere, highest campus v2; `o5 b15 m4` ties on campus at 0.99 and loses on home 0.91). Fitted: orange hue 3–13 (OpenCV), S ≥ 140; blue hue 103–119, S ≥ 113. Its one campus error: `occl_02` (the blue barrel behind the marker: its stripe is fully hidden, the known limit). Bottom edges: median error 2 px on campus.
- **Takeaway:** (1) On the frames that broke the live run the candidate front end plus the hardened detector score **0.99 against 0.41** for what runs on `barrels` today, with the home score unchanged and nothing drawn on the real negatives of either session or on Dave's pink desk. (2) The per-class floor does what the first sweep predicted: orange low (the far stripes), blue at the 15th percentile (the wall); the 10th lets the wall in (home blue 0.67), the 20th starts losing campus blue bodies (0.81–0.87). (3) What is left is not the pixels: a hidden stripe and Dave's per-group boxes. (4) The held barrel is settled by Tanush's box (a blue barrel, no `held` flag, so it is an ordinary positive); one label question stays: `clean` is `true` on `neg_05` / `clutter_02`, which contain an orange cap and a glue stick — stricter than the definition, left as he set it.
- **Next:** Tanush's decision (walkthrough, rule); then `DEFAULT_MODEL` → `eb863d84`-class config saved to `results/`, the live programs follow; one look at the 10 campus test frames and the 5 home test frames afterwards, once, logged.

---

## 2026-11-08 (later) — Recordings replayed with the hs front end and the hardened detector

- **Method / params:** `experiments/2026-11-07_rec_replay/run.py --front hs --hs o5,b15,m2 --out 2026-11-08_rec_replay_hs` (the candidate model fit on the 16 home train masks; tracker defaults).
- **Results:** r1 static: raw **1 orange / 2 blue in all 54 frames**, 0 blips — the second blue box is a blue object at the right frame edge, above the table edge (persistent, so the tracker shows it: a real false positive, not a blip). r2 pan: raw stable (1 / 1–2), 1 blip, suppressed; shown count changes twice. r3 enter/leave: the sliding orange barrel appears and disappears with 2 frames of lag, 0 blips. r4 hand: raw count changes 16 times, 6 blips all suppressed, shown changes 10 times, every re-acquired track shown after 2 frames — the hand covers a barrel for more than 4 frames at a time, so the track is forgotten and re-shown by design.
- **Takeaway:** with a working front end the 3-of-4 rule does what it was built for: no one-frame box reaches the screen, a steady barrel is steady, lag is 2 frames (≈ 0.3 s at 6 frames a second). What it cannot do is hide a *persistent* false box: blue clutter at the horizon edge is the new failure to watch (the stripeless-far path, as the jacket was; the height check passed it). Tanush's live impressions (TODO P0) now have numbers to compare with.
- **Next:** try `BarrelTracker` live with the new front end; consider refusing stripeless far pieces that touch a side edge of the frame, pre-registered, after the live try.

---

## 2026-11-08 — The hs color model: pre-registered sweep of its three fit parameters (branch `wip/redesign`)

- **Hypothesis:** a per-class hue sector plus a floor on HSV saturation, both read off the labeled home frames, with no top-row stage, finds the bodies v1 loses in a real room while the hardened detector keeps false boxes at zero. Open from the probe: how high the S floor must be to keep the bluish home wall (S ≤ 110 in the blue hue sector) out without losing shaded blue bodies (S 60–130 on the far campus barrels), and how much hue slack orange needs (home labels 5–10, campus daylight 7–13).
- **Method / params:** `experiments/2026-11-08_seg_hs/run.py`; `pipeline.Config(color_model="hs")` with `hs_s_pct ∈ {5, 10, 15, 20}` × `hs_h_pct ∈ {(2, 98), (5, 95)}` × `hs_h_margin ∈ {0, 2, 4}` = 24 configs; detector `DetConfig()` (hardened, below), camera `AIM_4A8B6118_BOXFIT`. Home = leave-one-scene-out over the 16 train frames (fit on the other scenes; v2 rule on Tanush's boxes; pixel IoU on the masks); campus = one model fit on all 16 home frames, count-level on the 21 train frames (`expected.json`) and boxes on the 4 negatives; Dave = the same model on his 12 labeled frames (indicative only: his boxes group touching barrels). **Selection rule, fixed before the run:** 0 home false detections (LOSO) and 0 boxes on the campus negatives, then most campus frames right, then home v2, then the lower S percentile. No test frame loaded. Results: `results/2026-11-08_seg_hs/summary.md`.
- **Results** (home v2 / campus right of 21 / campus negative boxes / Dave v2; v1 row = frozen `afd85483` with the same hardened detector):

| config | home LOSO v2 (o / b) | campus right | campus neg boxes | Dave v2 |
|---|---|---|---|---|
| v1 `afd85483` + hardened detector | 0.93 (0.90 / 0.96) | 8 | 0 | 0.00 |
| hs s5 h5-95 m2 **(the rule's pick)** | **0.69** (0.90 / 0.48) | **19** | 0 | 0.34 |
| hs s5 h5-95 m4 | 0.68 (0.87 / 0.50) | 19 | 0 | 0.54 |
| hs s10 h5-95 m4 | 0.78 (0.90 / 0.67) | 18 | 0 | 0.51 |
| hs s15 h5-95 m4 (runner-up) | **0.93** (0.90 / 0.96) | **17** | 0 | **0.53** |
| hs s15 h2-98 m0 | **0.95** (0.93 / 0.96) | 16 | 0 | 0.43 |
| hs s15 h5-95 m2 | 0.95 (0.93 / 0.96) | 16 | 0 | 0.44 |
| hs s20 … (6 configs) | 0.91–0.95 | 14–16 | 0 | 0.40–0.55 |
| hs s5 h2-98 m0/m2/m4 | 0.65–0.67 | 14–15 | 1–4 | 0.36–0.53 |

  Fitted numbers, `s15 h5-95 m4`: orange hue 1–14 (OpenCV 0–179), S ≥ 174; blue hue 101–121, S ≥ 113. Its four campus misses: `edge_01` (the barrel half out of the frame, its stripe cut), `occl_02` (a barrel behind the marker, no stripe visible), `room_01` (the small blue barrel at 25 cm: its orange stripe falls under the orange S floor of 174; the 5th-percentile floor, 140, keeps it) and `room_03` (an extra blue box: the blue chair in the room). The 5th-percentile configs get those but let the home wall into the blue class (S floor 64): false blue boxes on the home *positive* frames (cluster, core, far scenes), which the two home negatives do not show.
- **Takeaway:** (1) The model works where v1 does not: at the 15th-percentile floor it matches v1 at home (0.93 vs 0.93) and gets 17 of 21 campus frames right against v1's 8, with nothing on any negative; on Dave's frames the pink desk stays unlabeled and the bodies are found (the detection numbers there are limited by his per-group boxes and his camera, not the pixels). (2) The S floor is the whole blue story: 64 lets the wall in, 113 keeps it out; orange needs 2–4 units of hue slack toward yellow for daylight. (3) **The pre-registered selection rule was wrong**: it optimised the campus count and only tie-broke on the home score, so it picked a config that is a regression at home. Reported as the rule said, not adopted. (4) The orange and blue floors want different percentiles (orange lower, for the far blue barrels' stripes; blue higher, for the wall): a per-class percentile is the obvious next sweep, and it needs Tanush's box labels on the campus frames to be judged properly instead of by counts.
- **Next:** Tanush boxes the 31 campus frames (`box_tool.py --filter campus_light`); then one sweep with per-class S percentiles under a rule written with him first (proposed: home LOSO v2 ≥ 0.91, 0 boxes on every negative, then the campus v2 score); walkthrough of `pipeline.py`'s hs branch and the detector hardening; adoption decision in `DECISIONS.md`; then `DEFAULT_MODEL` changes and the live programs follow for free.

---

## 2026-11-08 — Detector hardening (a–d), on the pre-registered flaws (branch `wip/redesign`)

- **Hypothesis:** on the 16 home train frames with the frozen v1 pixels the hardened detector scores within 0.02 of the old one under the v2 rule; on the campus train frames it fixes the five "seg+det" frames whose bodies are labeled and removes the wrong-color box; under the hue segmentation it removes the false boxes on the home wall and lifts blue.
- **Method / params:** `experiments/2026-11-08_det_hardening/run.py`. `DetConfig` fields, each reversible: (a) `dark_stripe=False` — a gap with no stripe-colored pixel is not a stripe; (b) `stripe_mode="cores"` — a stripe is a connected component of the other color whose every pixel has body color within 3 stripe heights above and below (the old `"bands"` finder kept for comparison); (c) `body_min=0.1` — in the stripe's columns, outside the stripe rows, the box must hold more body color than stripe color and at least 10 % body; (d) `height_min/max = 0.5/1.5` — a stripeless piece must be barrel-tall as well as barrel-wide (added after the hue model's `core_01` sheet showed a blue jacket above the table edge boxed as a far barrel; post hoc, flagged as such). Arms old / new / new+dark under two front ends (v1; the probe's hue model). Home train (v2), Dave 12 (v2), campus train (counts). Tests: 5 new synthetic cases in `tests/test_detector.py` (183 tests pass).
- **Results:**

| front end | detector | home train v2 (o / b) | Dave 12 v2 | campus right / 21 | campus neg boxes | frames with an extra box |
|---|---|---|---|---|---|---|
| v1 | old (bands) | 0.91 (0.87 / 0.96) | 0.00 | 7 | 0 | 0 |
| v1 | **new** | **0.93** (0.90 / 0.96) | 0.00 | 8 | 0 | 0 |
| v1 | new + dark gaps | 0.93 (0.93 / 0.92) | 0.00 | 8 | 0 | 1 |
| hue (probe) | old (bands) | 0.57 (0.81 / 0.33) | 0.31 | 12 | 0 | 5 |
| hue (probe) | **new** | **0.78** (0.93 / 0.63) | **0.40** | **15** | 0 | 1 |
| hue (probe) | new + dark gaps | 0.67 (0.90 / 0.44) | 0.37 | 10 | 1 | 8 |

- **Takeaway:** every change pays or is neutral; the dark-gap path is harmful under both front ends and stays off. With v1 pixels the gain is small because v1 rarely labels enough body for a stripe to be sandwiched at all (the attribution's point); with the hue pixels it is large: the glued-shadow cases (`plain_01`, `close_01`, `window_01`, the pair in `core_01`) come back and the wall's dark gaps stop being barrels. The residual blue loss at home under the hue model (0.63) is the wall entering the blue class, a segmentation matter settled by the S floor in the sweep above.
- **Next:** walkthrough (`HOW-IT-WORKS.md` §3 "The hardening"); merge with the hs decision.

---

## 2026-11-07 — Segmentation probe: hue sector + HSV-saturation floor per class, no top-row stages (two iterations)

- **Hypothesis:** the three stages that lose the barrels in a real room — the background prior, the per-image saturation floor (both from the top 50 rows) and the RGB boxes — are all brightness-bound; hue and HSV saturation ((max − min)/max) are not. Fit per-class boxes in (hue, S) on the home train masks, keep only the horizon and brightness gates.
- **Method / params:** `experiments/2026-11-07_seg_hs_probe/run.py`, two iterations, both committed. **First** (git 9563b50): plain 1–99 / 2–98 percentile boxes on (H, S) → orange hue 2–168, blue 5–170 — hue is circular and dark labeled pixels have random hue, so the sectors covered most of the circle and blue boxes appeared everywhere (22 on the 4 campus negatives, home 0.52). **Second**: hue shifted by +30 for orange so its sector does not wrap, S floor = a percentile (5 / 10) of the labeled pixels' S, hue sector = percentiles (2–98 / 5–95) of the pixels above that floor. Detector of the day (bands), camera BOXFIT; home train v2, Dave 12 v2, campus train counts; no test frame.
- **Results (second iteration):**

| arm | home train v2 (o / b) | home neg FD | Dave 12 v2 | campus right / 21 | campus neg boxes |
|---|---|---|---|---|---|
| v1 | 0.91 (0.87 / 0.96) | 0 | 0.00 | 7 | 0 |
| S floor 5th pct, hue 2–98 | 0.42 (0.83 / 0.01) | 25 | 0.28 | 10 | 12 |
| S floor 10th pct, hue 2–98 | 0.50 (0.86 / 0.14) | 4 | 0.24 | 10 | 2 |
| **S floor 10th pct (orange ≥ 163, blue ≥ 92), hue 5–95 (orange 5–10, blue 104–118)** | 0.57 (0.81 / 0.33) | 0 | **0.31** | **12** | **0** |

  Pixel distributions behind it (home labels, V ≥ 40): orange hue 5–95 % = 4–11, S median 212; blue hue 5–95 % = 87–124 (central half 108–112), S median 224, 5th percentile 64; home *background* pixels in the blue hue sector with S ≥ 80: 8.9 % of all background pixels (the bluish-gray wall), with S ≥ 100: 1.4 %; campus negatives in the orange sector with S ≥ 100: 0.6 %, in the blue sector: 0.3 %. Campus barrel bodies: blue S 129–221, orange shaded S 223, far orange S 198, skin S 149 (hue 13).
- **Takeaway:** the direction is right (campus 12 vs 7, Dave above zero for the first time, negatives clean), the home score is not: the wall enters the blue class at an S floor of 92 and the old stripe finder then boxes its dark gaps (flaw a) while glued shadow vetoes real stripes (flaw b) — the band logs on `core_01` and `touch_02` show exactly these two. So the hardening had to come first, and the S floor had to be swept. Both done the next day (above).
- **Next:** done — see the two 2026-11-08 entries.

---

## 2026-11-07 — The four recordings replayed: per-frame detector vs the 3-of-4 view

- **Hypothesis:** the one-frame boxes Tanush saw live are removed by `tracker.Tracker` (3 of the last 4 frames) and real barrels stay shown through a missed frame.
- **Method / params:** `experiments/2026-11-07_rec_replay/run.py`: every frame of the four clips (`data/recordings/2026-11-07_campus/`, 54–63 frames each at ≈ 6 a second) through the detector as it stands (frozen v1 → stripe step, BOXFIT camera) = "raw", and through the tracker (`TrackConfig()` defaults) = "shown". Raw blip = a raw box matched (same color, IoU ≥ 0.3) to nothing in the frame before or after. Count-level; no labels.
- **Results:** r1 static (two barrels, nothing moves): **0 raw boxes in all 54 frames**. r2 pan: raw 0–1 per color, 6 count changes, 2 blips, 0 shown; one track shown after 2 frames. r3 enter/leave: 0 raw boxes. r4 hand: raw 0–1, 9 count changes, 5 blips, all suppressed, nothing shown.
- **Takeaway:** the clips were shot with the room and the clutter box behind the barrels, where the attribution says the front end finds nothing — so they say nothing about the tracker yet, except that it suppressed all 7 blips offered. Keep the folders; replay again once the front end is replaced (the script is ready).
- **Next:** re-run after the hs decision; add the lag and stickiness numbers to the `BarrelTracker` report (TODO P0-5).

---

## 2026-11-07 — Campus attribution: segmentation or detector, on the real frames (count-level truth)

- **Setting:** the 31 frames of the campus session (`DATA.md` → Session 2026-11-07) imported as `4A8B_campus_light_*`, split at import (10 test, 21 train); only the 21 train frames are used here. No box labels yet, so the truth is count-level: the barrels of each body color in the frame, counted by eye (`experiments/2026-11-07_campus_attribution/expected.json`). The detector as it stands (frozen v1 model afd85483 → stripe step, camera `AIM_4A8B6118_BOXFIT`) on each frame; per frame the segmentation's own numbers (the saturation floor it chose, the background prior's rejection rate, barrel pixels), the stripe finder's verdict on every band, a four-panel sheet (raw, tint, boxes + stripes, pixels in a color box that the floor removed), and one diagnostic arm with the floor fixed at 40. Hand verdicts per frame in `judgments.json`, merged into `results/2026-11-07_campus_attribution/summary.md`. Hand-picked barrel rectangles were also pushed through the stages one at a time (numbers below; the probe script is in the chat log, the mechanism is the same as the per-frame table).
- **Result:** 21 frames: **7 right** (the 4 negatives, `hand_02`, the two lid-only shots), **9 segmentation only**, **5 segmentation + detector**, **0 detector only**.

| frame | expected O/B | floor | orange px | blue px | boxes O/B | verdict |
|---|---|---|---|---|---|---|
| room_01 | 1/1 | 86 | 505 | 0 | 0/0 | seg: blue body 0 % labeled |
| room_03 | 1/1 | 83 | 111 | 0 | 0/0 | seg |
| plain_01 / plain_02 | 1/1 | 49 / 50 | 7306 / 3205 | 5112 / 2313 | 1/0 | seg+det: blue body 41–69 % labeled; its stripe's band 67 rows vs 62 allowed |
| core_01 | 2/2 | 73 | 2573 | 4883 | 2/0 | seg+det: big blue band 97 vs 72; far orange outside the box; a wrong-color box on the pair |
| far_01 | 2/2 | 71 | 1553 | 823 | 2/1 | seg: the 4th barrel's body 34–47 % labeled |
| cluster_02, touch_02, occl_02, edge_01, clutter_02, held_01 | | 68–120 | | 0–132 | 0/0 | seg: blue bodies 0–7 % labeled |
| close_01, window_01 | 1/0, 1/1 | 67, 49 | | | 0/0 | seg+det: shaded faces unlabeled, bands too tall (72 vs 55; 35 vs 27) |
| neg_02–05 | 0/0 | 33–120 | 0–1255 | 0 | 0/0 | ok: orange clutter labeled in neg_05, no band, no box |

- **Where the pixels go** (hand-picked rectangles, fraction surviving each stage: in the RGB box → + horizon / brightness / saturation floor → + background prior): room_01 blue body **0.80 → 0.00 → 0.00** (floor 86 against a body saturation of 52–71); cluster_02 blue **0.98 → 0.69 → 0.05**, touch_02 blue **1.00 → 0.58 → 0.05**, far_01 blue **0.95 → 0.75 → 0.40**; cluster_02 orange lit half **0.89 → 0.88 → 0.85** vs its shaded half **0.99 → 0.96 → 0.17**; core_01 far small orange (RGB 225/128/50) **0.20** in the box at all. The background prior's band statistics on these frames: median ≈ (40–60, 40–65, 35–50), scale 35–52 per channel (home: ≈ 16–22), i.e. with a dark room in the top 50 rows it rejects everything within about ±100–130 of dark gray at k 2.5 — 30–71 % of each frame, navy blue and shaded orange included. The saturation floor from the same rows is 67–120 here (home 44–55; 120 is its clamp, hit when clutter or the laptop sits in those rows).
- **The detector's share:** where a body was labeled above and below its stripe, the stripe step found it (far_01 3 of 3 anchored, hand_02 2 of 2, plain_01's orange). Every detector-level failure is pre-registered flaw (b): unlabeled shadow glued to the stripe makes its band taller than 3 × the expected stripe height (core_01 ×2, plain_01, close_01, window_01's orange), plus one flaw-(c) case (core_01: an orange box on the blue barrel of the touching pair, its band blue pixels between the orange stripe below and the orange neighbour above) and one marginal width miss (window_01 blue: 25 px vs 26 required). Flaw (a) — a dark gap taken for a stripe — did not fire on these frames; it did in the 2026-11-06 screenshots. No box on any negative; the orange clutter (a cap, a glue stick) is labeled orange and correctly left unboxed.
- **Takeaway:** the front end is most of it. Every stage that made v1 "adaptive" assumes the top 50 rows are a plain wall and the barrels are the only saturated thing: in a real room both are false, and the stages then remove the barrels themselves. The two detector flaws are real but secondary and already pre-registered. **Order: segmentation redesign first (P0-4), detector hardening (b) and (c) alongside.**
- **Next:** the segmentation probe below (hue + HSV-saturation boxes, no top-row stages); the pre-registered rule for adopting a new front end is in that entry.

---

## 2026-11-06 — First live run: the detector off the training table, from Tanush's screenshots (a diagnosis, not a tuning run)

- **Setting:** Tanush ran `live/BarrelViewer.fsm` on campus: a white table, barrels ≈ 7–15 cm away, first with the room and his hand and laptop behind them, then with the back of his laptop as a plain backdrop (the `board_*` screenshot names mean the laptop lid). He sent screenshots of the window (hand-cropped and scaled): one raw frame of the hand scene, its `seg` view, three `both` views with the board. No raw frames exist yet, so this is a diagnosis: `experiments/2026-11-06_live_first_run/run.py` resizes each screenshot to 640×480, rebuilds the class mask from the overlay tint, runs the stripe finder's tests on it band by band (the same tests as `detector.find_stripes`), then `detector.detect`. Results: `results/2026-11-06_live_first_run/summary.md`; the screenshots are in `screens/`.
- **What the window showed:** with the laptop lid behind them, the blue barrel boxed correctly in all three frames; the orange barrel boxed correctly in one (`board_b`), and in the other two a small yellow box floating above and left of it, the barrel itself unboxed. The segmentation tint: false orange along the edge where the laptop lid meets the table, on the glow the orange barrel throws on the table, on a metal rack and, in the room scene, on skin and the laptop edge; the orange barrel's shaded side and lid highlight unlabeled; the navy end of its blue stripe unlabeled.
- **What the rebuilt masks say** (`board_a`; approximate):

| band between orange above and below | size | stripe-colored px | unlabeled px | verdict |
|---|---|---|---|---|
| the dark gap under the smear at the laptop lid's edge, above the barrel's lid | 37×23 | 0 | 707 | kept as a *shadowed* stripe → the floating box (x 294–372, y 134–222; the screenshot's box sits at ≈ 295–373, 143–229) |
| the real blue stripe, with the unlabeled shadow glued to it | 162×92 | 3645 | 2758 | dropped: band 92 rows, 83 allowed (3 × the expected stripe height) |

  `board_c` the same (band 111 rows, 75 allowed). `board_b`'s rebuilt mask gives no orange box where the live run gave a correct one, so the reconstruction is not exact — one more reason for raw frames. The hand-scene screenshot run through the real live path segments to **nothing**: the crop moved the hand into the top 50 rows, the per-image saturation floor taken from those rows came out at its clamp (120 for both classes) and no pixel passed — while the live window had segmented that scene. Not what the robot saw, but a clean demonstration of the top-row dependence the Dave-frames entry found.
- **Takeaway:** two detector flaws, both fit to the 16 train frames: (1) a band with no stripe-colored pixels counts as a shadowed stripe (added 2026-11-03 for stripes too dark to label), so any dark gap between orange above and orange below is a barrel; (2) the band is one connected component of everything non-body between body above and body below, so unlabeled shadow touching a real stripe makes its band too tall and the stripe is rejected. And two segmentation flaws the committed frames do not contain: false orange on the edge of a laptop lid used as a backdrop, on a barrel's glow and on skin; shaded barrel faces unlabeled. The geometry did its job: it drew the box a barrel with *that* stripe would have.
- **Next:** raw frames (session 2026-11-07, `DATA.md`); the same analysis on real masks (`TODO.md` P0-2); then the pre-registered hardening (P0-3) and the segmentation redesign (P0-4). The multi-frame program built the same day (`BarrelTracker`) removes one-frame boxes but not these: the floating box is there frame after frame.

---

## 2026-11-03 (evening) — Detector step 2, the stripe anchor, vs step 1 vs the floor, on Tanush's reviewed boxes

- **Hypothesis (stated first):** anchoring on the stripe recovers the barrels step 1 lost to same-color occlusion and removes the hand's false boxes, without losing the touching rows step 1 already splits.
- **Method / params:** `experiments/2026-11-03_det_step2/run.py`; `detector.DetConfig(require_stripe=True)` with the stripe numbers written down first (core height 0.45–1.6 × expected, band ≤ 3 ×, width ≥ 0.4 barrel, merge > 1.4, full < 0.8, min stripe 4 px); same pixels (frozen `afd85483`) and camera (`AIM_4A8B6118_BOXFIT`) for all arms. **Ground truth = Tanush's hand-fixed `_boxes.json`** (11 of 21 files changed from the automatic split). Rules: v1 (IoU ≥ 0.5, occluded/truncated GT ignored) and v2 (`EVAL.md`; implemented in `eval_det.py` the same evening). Results: `results/2026-11-03_det_step2/` (sheets: boxes yellow/green, truth white, stripes found in magenta).
- **Data / split:** the 16 train frames. No test frames touched.
- **Results:**

| arm | primary (mean F1) | F1 orange / blue | mean IoU | bottom err (median px) | neg false det |
|---|---|---|---|---|---|
| floor (one box per blob) | 0.484 | 0.368 / 0.600 | 0.734 | 1 | 0 |
| step 1 (width + top row) | 0.862 | 0.824 / 0.900 | 0.857 | 1 | 0 |
| **step 2 (stripe)** | **0.971** | 0.941 / 1.000 | 0.829 | 1 | 0 |

**Under the v2 rule** (every barrel counts, bottom edge within max(3 px, 10 % of height); `results/2026-11-03_det_step2_v2/`):

| arm | primary (mean F1) | F1 orange / blue | mean IoU | bottom err seen · estimated (median px, n) | neg false det |
|---|---|---|---|---|---|
| floor | 0.427 | 0.292 / 0.562 | 0.753 | 1 | 0 |
| step 1 | 0.709 | 0.600 / 0.818 | 0.879 | 1 (16) · 0 (2) | 0 |
| **step 2** | **0.913** | 0.867 / 0.960 | 0.829 | 1 (23) · 0 (2) | 0 |

Per scene under v2, step 2: every scene perfect except `cluster` (orange 2 of 4, one false) and `occl` (one of two in each frame) — the barrels whose stripe is entirely hidden. 23 of 25 matched bottoms are within 1 px; the two `bottom_estimated` boxes (`top_01`, `topstripe_01`, cut by the frame) are exact.

Two intermediate versions scored 0.72: the band around a stripe includes the unlabeled shadow below it, so testing the *band's* height against the expected stripe height rejected most real stripes; measuring the stripe's colored core (10th–90th percentile rows) and taking its median row as the stripe's centre fixed that. Step 1 against the same fixed boxes: 0.862 (was 0.780 against the automatic boxes — Tanush's edits mostly fixed boxes the detector had right).
- **Takeaway:** as predicted for touching rows (`touch_02`, `cluster_02`: all found, no width rule needed), the hand (`far_02`, `core_03`: no false boxes left) and partial occlusion where the back barrel's stripe shows (`occl_01`, `occl_02`: one of the pair each). Not solved: a barrel whose stripe is entirely hidden (`cluster_01`: 2 of 4 missed + 1 false; one each in `occl_01`/`occl_02`) — those are ignored under the v1 rule, so the 0.97 flatters; the v2 rule will count them. Same-color occlusion is therefore half-solved: visible stripe → found with a full box; hidden stripe → nothing.
- **2026-11-05 follow-up:** walkthrough acknowledged; **the stripe step is the default** (`DetConfig.require_stripe=True`; `detect_image.py --step1` = steps 1–3 alone; the step-1 and Dave-snapshot experiments pinned to `require_stripe=False`). Both rules re-run at the new commit — every number identical (`results/2026-11-03_det_step2/`, `_v2/` regenerated; the old files differed only by the columns the v2 evaluator added).
- **Next:** ~~a walkthrough of step 2 for Tanush; then make it the default (it beats step 1 under both rules)~~ done 2026-11-05. For hidden stripes: a body-only candidate is allowed when it sits directly above a found barrel of the same color and is barrel-sized for its row (the "behind" case), to be pre-registered before trying.

---

## 2026-11-03 — Dave's 20 snapshots (his robot, his office): the v1 segmentation finds nothing — the front end is the bottleneck on a new scene

- **Hypothesis:** on frames from a different robot and tables never seen, segmentation + step 1 still box the mid-range barrels; the close-ups and the dark table are where it breaks.
- **Method / params:** `tools/import_dave_zip.py` (20 `DAVE_office_{speckle,dark}_snap_NN` frames; Dave's 12 drawn ground-truth boxes recovered as the pixels that differ between his `_ground_truth.png` and the raw snapshot, yellow = orange barrel, green = blue); `experiments/2026-11-03_dave_snaps/run.py`: frozen v1 `afd85483` + `detector.detect` (and the CC floor), scored with `eval_boxes.py --gt-boxes` (IoU ≥ 0.5 rule). **Outside check: no split, nothing tuned.** Results: `results/2026-11-03_dave_snaps/` (`boxes/` = the drawn output for all 20, `overlay/` = the segmentation, `2026-11-03_dave_snaps_step1/` = the score).
- **Results:** **0 barrels on all 20 frames**, 0 of 34 ground-truth barrels found. The segmentation outputs **zero orange and zero blue pixels** on every frame. Cause: the per-image saturation floor is derived from rows 0–50 ("guaranteed background"), and in Dave's office those rows hold a cluttered shelf with colorful objects, so the floor comes out at 96–120 (the clamp) instead of ≈ 50; the wall model, fit on the same rows, rejects the rest.
- **Diagnostic (not a tuning run; 12 labeled frames, step 1 on top):**

| segmentation variant | floor | barrel px (o / b) | hits o / b of 20 / 10 | false boxes | primary |
|---|---|---|---|---|---|
| v1 as is (band floor + wall model) | 96–120 | 0 / 0 | 0 / 0 | 0 | 0.00 |
| fixed floor 50 (the v1 fallback option) | 50 | 13 k / 80 k | 2 / 1 | 13 | 0.13 |
| fixed floor 50, wall model off | 50 | 262 k / 284 k | 8 / 7 | 67 | 0.30 |
| band floor, wall model off | 96–120 | 170 k / 127 k | 11 / 2 | 38 | 0.29 |

Even with the adaptive parts switched off the pink speckled desk floods the orange class (262 k orange pixels in 12 frames): the fixed RGB boxes do not separate Dave's desk from barrel orange either.
- **Takeaway:** the v1 front end does not transfer to Dave's office at all, for two reasons the v1 data could not show: (1) "rows above the horizon are plain background" is false in a cluttered room — both adaptive stages are built on it; (2) the RGB boxes admit his desk. The detector logic cannot be judged on these frames until the segmentation is redone. This is exactly Dave's 2026-10-30 condition for going back to the segmentation ("only if its flaws actually cost detections"): they cost all of them. His close-up frames (lid filling the frame, bottom far below it) and his dark warm-lit table are additional cases our data does not have.
- **Next:** decide the segmentation redesign with Dave (v2.1 pulled forward): background statistics that do not rely on the top rows; barrel-referenced color rather than fixed boxes; test on Dave's 12 + our frames. Keep Dave's frames as an outside check, not tuning data.

---

## 2026-11-03 — Detector step 1 (blobs → count by expected width → bottom from the top row) vs the CC floor — PROVISIONAL

- **Hypothesis (stated first):** counting barrels by the expected width and filling hidden bottoms from the top row lifts detection F1 well above the connected-components floor on the same pixels, because the floor's losses were merged touching barrels and shadow-shortened boxes, not misplaced edges.
- **Method / params:** `experiments/2026-11-03_det_step1/run.py`; `detector.DetConfig()` defaults (close 3 px, min blob 20 px, bottom tolerance 15 % / 4 px, width window 0.4–1.6×, min expected width 16 px; none tuned); camera `AIM_4A8B6118_BOXFIT` (below). Both arms run the frozen v1 model `afd85483` on each frame; arm `cc` = `detect_cc`, arm `step1` = `detector.detect`. Scored with the existing `eval_det` (IoU ≥ 0.5, VOC-style ignores; the v2 bottom-edge rule is M2) against the **unreviewed auto-split instances**. Results: `results/2026-11-03_det_step1/` (sheets: boxes in class color, truth in white).
- **Data / split:** the 16 train frames. No test frames touched.
- **Results:**

| arm | primary (mean F1) | F1 orange / blue | mean IoU of matches | bottom-row err (median px) | neg false det |
|---|---|---|---|---|---|
| cc (floor) | 0.461 | 0.341 / 0.581 | 0.750 | 1.0 | 0 |
| step 1 | **0.780** | 0.833 / 0.727 | 0.868 | 1.0 | 0 |

With the old preset camera (f 404 / tilt 23.3) step 1 scored 0.519 and its bottom edges were 21 px off (median): the geometry, not the detector logic, was the limit — see the next entry.
- **Takeaway:** as predicted. Touching rows (`touch_02`, `cluster_02`) now split correctly; shadow-shortened boxes are extended to the right bottom. What remains: same-color occlusion (`occl_01`, `occl_02`: the blob holds two barrels one behind the other, width says one) and `cluster_01` (4 bunched barrels → 2 found). The hand in `far_02`/`core_03` leaves one false box each (barrel-sized skin blobs). Provisional ×3: the camera was fit on these frames, the pixels come from a model fit on these frames, the instances are unreviewed.
- **Next:** step 2 = the stripe anchor (one barrel per stripe inside merged blobs; "barrel" ≠ "orange thing"); M2 eval under the v2 rule on Tanush's box labels; the calib session replaces the box-fit camera.

---

## 2026-11-03 — Camera re-fit from labeled boxes: the preset put bottoms ≈ 20 px too low

- **Hypothesis:** the preset `AIM_4A8B6118` (f 404, tilt 23.3°, horizon 66) is inconsistent with the labeled barrels; one (f, tilt) makes both the barrel height and the barrel width per row consistent with the known barrel (24 × 25.5 mm) and camera height (43.47 mm).
- **Method / params:** `experiments/2026-11-03_geo_boxfit/run.py`: the 24 unflagged (fully visible) GT instances on the train frames; for each, the model must reproduce the bottom row from the top row and the width at the bottom row; grid over f 280–460, tilt 15–32°; also tilt alone with f held at the two independently measured values (356 from widths, 400 from aim_fsm). Results: `results/2026-11-03_geo_boxfit/fit.json`.
- **Results (predicted − measured, px):**

| camera | f | tilt | horizon | bottom err mean / |med| / p90 | width err mean / |med| / p90 |
|---|---|---|---|---|---|
| preset 4A8B | 404 | 23.30 | 66.0 | +13.5 / 19.6 / 27.7 | +7.4 / 7.4 / 22.8 |
| nominal | 400 | 23.00 | 70.2 | +7.7 / 13.7 / 21.9 | +5.3 / 5.7 / 20.7 |
| free fit | 298 | 29.00 | 74.8 | 0.0 / 6.2 / 14.2 | +0.1 / 3.0 / 16.5 |
| f = 356 | 356 | 24.75 | 75.9 | −0.5 / 5.6 / 13.7 | +1.5 / 2.7 / 17.1 |
| **f = 400 (adopted)** | 400 | 22.25 | 76.4 | −0.8 / 5.3 / 13.4 | +2.3 / 3.1 / 17.7 |

The cost surface is flat along a ridge (everything from f 280 to 460 is within 10 % of the best with the matching tilt): **the boxes pin the horizon row (≈ 75–76), not f and tilt separately.**
- **Takeaway:** the October preset's horizon (66) is 10 rows too high for these frames; every fit agrees on ≈ 76, inside the measured 55–100 band. Adopted as the **provisional** preset `AIM_4A8B6118_BOXFIT` (f 400 kept — Dave: f ≈ 400, varies little between robots — tilt 22.25°). The p90 of 13–17 px is the unreviewed instance boxes as much as the camera.
- **Next:** the 12-frame `calib` session (known distances) fixes f and tilt independently; then retire the box fit.

---

## 2026-10-28 — Pixel cleanup flags on v1 (LOSO CV): a tie, v1 unchanged

- **Hypothesis (stated first):** a tie — v1's false pixels are hundreds-of-pixel lid reflections and edge halos, its misses are shadowed faces; speck removal and hole filling touch neither.
- **Method / params:** `experiments/2026-10-28_v1_cleanup/run.py`: `min_blob_px` ∈ {10, 25, 50, 100}, `open_px` ∈ {3, 5}, `fill_holes`, two pairs, on the v1 final `afd85483`, same folds and rule. Results: `results/2026-10-28_v1_cleanup/`.
- **Results:** base 0.809; small-blob removal +0.000 to +0.003; opening −0.006 (3) / −0.024 (5): it eats the thin far barrels; hole filling +0.009; best pair (blobs 25 + holes) +0.010. All within the 0.02 band → **v1 stays at `afd85483`**; the flags remain in `Config` (default off, hash-preserving).
- **Takeaway:** as predicted. Hole filling's +0.009 is real but tiny (the stripe edge and the VEX logo); worth re-checking once detection, not IoU, is the metric.

---

## 2026-10-28 — Detection floor: connected-components reference detector (BASELINE, not v2) — PROVISIONAL

- **Hypothesis:** the harness works end to end; with perfect pixels the floor is limited by touching barrels merging; with v1's pixels it is also limited by fragmentation of shadowed faces.
- **Method / params:** `experiments/2026-10-28_det_baseline/run.py`. Arm A: ground-truth class mask → CC → boxes; arm B: v1 LOSO-CV predicted mask → CC → boxes. Scored with `eval_det` (greedy IoU ≥ 0.5, VOC-style ignore flags, loose = projected ground position within 15 mm) against per-barrel instances. **Instances are the automatic split, not yet reviewed by Tanush**, so the numbers are provisional (`results/2026-10-28_det_baseline_PROVISIONAL/`); the entry will be replaced after the review.
- **Results (in-scope frames, 16 pool):**

| arm | primary (mean F1) | F1 orange / blue | loose F1 o / b | mean IoU of matches | bottom-row err (median px) | projected ground err (median mm) | neg false det |
|---|---|---|---|---|---|---|---|
| A: GT mask → CC | 0.633 | 0.600 / 0.667 | 0.600 / 0.762 | 0.959 | 0.0 | 0.0 | 0 |
| B: v1 mask → CC | 0.448 | 0.333 / 0.562 | 0.429 / 0.710 | 0.750 | 1.0 | 2.7 | 0 |

Geometry sensitivity (arm B, projected ground error): median 2.2–3.8 mm, p90 32–82 mm across the camera range corners — the p90 is merged boxes, not the camera.
- **Takeaway:** the harness runs: GT instances → eval → tables → re-scorable `det.json`. Even with perfect pixels a CC detector finds only ~63 % of barrels (every touching pair becomes one box, often the wrong color), which is exactly the gap v2 is for: splitting by expected width per row and the stripe structure. With v1's pixels the floor is 0.45 F1; matched boxes are good (IoU 0.75, bottom edge within 1 px), so the loss is in *which* blobs exist, not where their edges are. Zero false detections on negatives.
- **Next:** Tanush reviews the instances (`tools/instance_tool.py`); re-run without `--allow-unreviewed` → the non-provisional floor; measured set.

---

## 2026-10-22 — Where v1's errors come from (attribution), and the table prior on non-close frames

- **Hypothesis:** blue misses are shadowed faces removed by the saturation floor; orange false pixels are the hand and the reflections next to close barrels; the table prior is harmless-but-useless on frames without a close barrel.
- **Method / params:** `experiments/2026-10-22_error_attribution/run.py` on the final config `afd85483` LOSO-CV predictions (16 pool frames). Each missed pixel is attributed to the first stage that removed it (horizon → brightness → saturation floor → wall prior → class box → tie); each false pixel is "boundary halo" (≤ 4 px from a true barrel) or "elsewhere", split by hand frame. Then the table prior switched back on at k = 1.5–3. Results: `results/2026-10-22_error_attribution/`.
- **Results:**

| | orange (≈ 132 k labeled px) | blue (41 k labeled px) |
|---|---|---|
| missed: saturation floor | 2.3 % | **21.0 %** |
| missed: outside class box | 2.5 % | 3.7 % |
| missed: wall prior / brightness / tie | 0.0 / 0.2 / 0.0 % | 2.0 / 1.0 / 0.5 % |
| false: boundary halo | 1.1 % | 0.5 % |
| false: elsewhere | 3.9 % — **all of it in `top_01`/`topstripe_01`**: the lid's reflection in the glossy table next to it, median RGB (120, 102, 70), saturation 45–47, i.e. just above those frames' floor (44) and inside the orange box | 0.0 % |
| false: hand frames | 0.6 % (841 px, RGB ≈ (100, 65, 48), sat 50–55) | 0.0 % |

| table prior (band-floor config) | primary (non-close frames) | top/topstripe orange IoU |
|---|---|---|
| off | 0.809 | 0.918 |
| k 1.5 | 0.809 | 0.762 |
| k 2.0 | 0.808 | 0.297 |
| k 2.5 | 0.806 | 0.076 |
| k 3.0 | 0.800 | 0.009 |

- **Takeaway:** (1) The dominant error is blue recall: one fifth of true blue pixels are shadowed faces below the floor; lowering the floor is not the fix (the wall is right there in saturation), so recovering them needs something other than saturation — a shape/adjacency cue or a hue test. (2) Orange's false pixels are reflections on the glossy table next to close barrels (the "known confuser" from `constraints.md`; geometry can reject them later because they are below the contact row) and skin. (3) The table prior costs 0.000–0.009 on the non-close frames and gains nothing — the saturation floor already removed the table — while on the close frames it goes from harmless (k 1.5) to catastrophic (k 3). It is correctly off on this table; on a colored table it must be re-tested, with a scale cap. (4) Per-frame precision is 0.91–0.99; IoU looks low mainly because of recall on shadows and edges, and because a 1-px edge error on a 28-px barrel is ~10 %.
- **Next:** label the 10/7 wood-desk set; test the prior (with a cap) and the floor there.

---

## 2026-10-20 — Per-image saturation floor (band-derived) vs fixed; synthetic lighting-shift probe; second test evaluation

- **Hypothesis:** (Tanush) the saturation floor should not be a constant learned from training frames; the image's own known-non-barrel rows can set it. Expectation: a tie on this single-light set (the floor it derives should land near 50), and better behaviour when the background gets more colorful or the exposure changes.
- **Method / params:** `experiments/2026-10-20_v1_adaptive/run.py`. `Config.s_min_mode="band"`: floor = the `s_band_q` percentile of the saturation of the rows above the horizon (`bg_rows`, optionally plus the bottom table rows) + `s_band_margin`, clamped to [20, 120]; computed per image, nothing in the image is changed. (1) LOSO CV grid vs the fixed v1 final (`ee36a1e9`): q ∈ {99, 99.5, 99.9} × margin ∈ {5, 10, 15, 20} × source ∈ {bg, both}. (2) **Synthetic** lighting shifts applied to the *held-out* frames only (train frames untouched): gain ×0.5 / ×0.75 / ×1.25, warm cast (R×1.2, B×0.8), cool cast (R×0.8, B×1.2); fixed vs band floor, each also with the YUV chroma box and/or the re-fit. Not real data — a probe of which parts of the method depend on the lighting. (3) The adopted config evaluated once more on the test set (`final_test.py --allow-rerun`, reason recorded in its config.json). Results: `results/2026-10-20_v1_adaptive_cv/`, `_v1_adaptive_shift/`, `_v1_test_adaptive/`, overlays in `_v1_viz_adaptive/` (sheet copied to `experiments/2026-10-20_v1_adaptive/figures/`).
- **Data / split:** 16 pool frames (CV, shift), 5 test frames (once).
- **Results:**

| | fixed floor 50 (`ee36a1e9`) | band floor, bg rows, q 99.5, margin 10 (`afd85483`) |
|---|---|---|
| LOSO CV primary (orange / blue IoU) | 0.810 (0.829 / 0.791) | 0.809 (0.825 / 0.793) — tie |
| floor actually used per frame | 50 everywhere | **44–55**, derived from each frame's own wall rows (negatives 47–48, top-only 44) |
| band source "both" (adds the table rows) | | 0.81 on in-scope frames but the top-only frames drop to 0.63 / 0.00: the lid sits in the table band and drives the floor to 120 → **use the above-horizon rows only** (they can never contain barrel) |
| **test set, evaluated once each** | orange **0.844**, blue **0.811**, neg FP 0 | orange **0.843**, blue **0.813**, neg FP 0 |

Synthetic shifts on held-out frames (primary; neg FP where non-zero):

| shift | fixed floor | band floor | band + YUV box | band + re-fit (margin 3) |
|---|---|---|---|---|
| none | 0.810 | 0.809 | 0.814 | 0.816 |
| gain ×0.5 (dark) | 0.534 | 0.630 | **0.770** | 0.512 |
| gain ×0.75 | 0.760 | 0.786 | **0.824** | 0.810 |
| gain ×1.25 (clipping) | 0.558 | 0.564 | 0.491 | **0.673** |
| warm cast | 0.443 (neg FP 3.1 %) | 0.421 (1.3 %) | 0.158 (20 %) | **0.569** (1.3 %) |
| cool cast | 0.417, **blue precision 0.05, neg FP 7.7 % → disqualified** | 0.564 (neg FP 0) | 0.422 | **0.602** (neg FP 0) |

- **Takeaway:** (1) The floor does not need to be a learned constant: derived from the image's own above-horizon rows it lands at 44–55 and scores identically on real data, so **v1 adopts the band floor** (Tanush's intent; no cost). (2) Under a cool cast the fixed floor lets the bluish wall through and the method fails its own disqualification rule (7.7 % of empty-frame pixels flagged blue); the band floor rises with the wall's saturation and keeps negatives at zero. The floor is the *false-positive* guard, and adapting it is what makes that guard follow the scene. (3) What does *not* adapt is the per-class RGB boxes, and they are what breaks under casts and gain: recall collapses because the barrel colors move out of the box. The YUV chroma box fixes brightness changes (gain ×0.5: 0.53 → 0.77) but is the worst under casts; the re-fit is the only thing that helps under casts (0.44 → 0.57, 0.42 → 0.60), i.e. the barrel-side adaptation is v1.5's real job and it needs real multi-light data, not this probe. (4) The ×1.25 case clips channels; nothing recovers that, and it is a camera-exposure problem, not a thresholding one.
- **Next:** label the 10/7 wood-desk frames (3 lamp warmths × 3 directions) — that is the real version of this probe; re-run `analyze.py`, the v1 CV, `v15/run.py` and this script there, with leave-one-*light*-out folds.

---

## 2026-10-20 — v1.5 arms vs v1 final: barrel-referenced re-fit, YUV chroma box (LOSO CV only)

- **Hypothesis:** (a) re-fitting each class box to the image's own high-confidence barrel pixels (PROBLEM.md v1.5) recovers shadowed faces the train-fold box misses; (b) a box in the YUV chroma plane (brightness dropped) beats the RGB box because the clusters are brightness-elongated.
- **Method / params:** `experiments/2026-10-20_v15/run.py`: 11 re-fit variants (`pipeline.RefitConfig`: inner box 10–90 % defines "confident", new box = percentile box of those pixels ± margin·MAD, clipped to the 0.1–99.9 % train box, fallback to v1 below `min_px`) and 6 YUV-chroma variants, all starting from the v1 final config `ee36a1e9`, scored under the same leave-one-scene-out folds. **No test-set run.** Results: `results/2026-10-20_v15/`.
- **Data / split:** 16 pool frames, one table, one light.
- **Results:**

| arm | primary | Δ vs v1 | orange IoU | blue IoU (P / R) | note |
|---|---|---|---|---|---|
| v1 final | 0.810 | — | 0.829 | 0.791 (0.99 / 0.80) | |
| re-fit, default (margin 1·MAD) | 0.739 | −0.071 | 0.744 | 0.734 (0.99 / 0.74) | engaged on 12/16 (orange) and 11/16 (blue) frames; negatives never re-fit. The re-fit box is *tighter* than the train box, so it loses more shadowed pixels |
| re-fit, margin 0.5 | 0.659 | −0.151 | | | worse still |
| re-fit, margin 2 / 3 | 0.807 / 0.819 | −0.003 / +0.009 | 0.830 | 0.808 (0.99 / 0.82) | ties with v1; margin 3 ≈ the v1 box re-centered |
| re-fit, inner 25–75 | 0.434 | −0.376 | | | too few confident pixels → tiny boxes |
| YUV chroma box 1–99 | 0.805 | −0.005 | 0.842 | 0.767 (0.94 / 0.81) | tie: orange up, blue precision down (gray wall is near the blue chroma box) |
| YUV chroma box 0.5–99.5 | 0.815 | +0.005 | 0.846 | 0.785 (0.95 / 0.82) | tie |
| YUV + re-fit | 0.806 | −0.004 | 0.848 | 0.763 | tie |

- **Takeaway:** neither arm beats v1 on this data, and that is the expected result rather than a failure: with one table and one light there is **no per-image color shift for a re-fit to correct** — the only thing it can do is shrink the box toward the bright faces, which is what it did. The chroma box is a genuinely different shape at the same score (orange better, blue slightly worse); its case is generalization across lighting, which this set cannot test. Both stay implemented behind flags (`Config.refit`, `Config.box_space`) and go back on the table once a second lighting condition is labeled (the wood-desk warm/cool frames are the obvious next set). v1 config unchanged.
- **Next:** label a second light/table; re-run `analyze.py`, the v1 CV, and this script there. Separately: the table prior needs a scale cap before it is trusted on dark tables; skin vs orange needs a hue-angle test (both out of v1).

---

## 2026-10-20 — v1 on the held-out test set (single run)

- **Hypothesis:** the CV estimate (primary 0.810) transfers to the 5 untouched test frames.
- **Method / params:** `experiments/2026-10-20_v1_rgbbox/final_test.py --config .../ee36a1e9.json`, fit on all 16 pool frames, predicted the 5 test frames exactly once. Independently re-scored from the saved `pred/*.png` with `tools/eval_masks.py --split test` — identical numbers. Results: `results/2026-10-20_v1_test/` (summary.md/csv, per_image.csv, sheets, PROBLEM.md output images, predicted masks, config.json with the fitted boxes).
- **Data / split:** test = `core_04, edge_02, far_01, neg_03, touch_01`.
- **Results:**

| frame | orange IoU (P / R) | blue IoU (P / R) | neg FP o / b |
|---|---|---|---|
| **ALL (4 pos + 1 neg)** | **0.844** (0.960 / 0.875) | **0.811** (0.982 / 0.823) | **0.000 / 0.000** |
| core_04 (hand in frame) | 0.874 (0.993 / 0.880) | 0.848 (0.990 / 0.855) | |
| edge_02 | 0.791 (0.971 / 0.810) | 0.915 (0.983 / 0.929) | |
| far_01 | 0.771 (0.910 / 0.835) | 0.732 (0.948 / 0.763) | |
| touch_01 | 0.875 (0.972 / 0.898) | 0.776 (0.993 / 0.780) | |
| neg_03 | — | — | 0.000 / 0.000 |

- **Takeaway:** test ≥ CV (orange 0.844 vs 0.829, blue 0.811 vs 0.791), so the CV selection did not overfit the pool; the strawman target of IoU ≥ 0.8 per class on this table is met. Precision is ≥ 0.91 everywhere; the remaining error is recall: shadowed lower faces (both classes) and the far barrels' blurred edges. The hand in `core_04` was not flagged (it sits mostly above row 50 and at the frame edge). Negative frame: zero pixels flagged.
- **Next:** v1.5 arms (re-fit, YUV chroma) under CV only; more surfaces/lights before anything else is believed.

---

## 2026-10-20 — v1 RGB box: default config, stage ablations, parameter sweeps (LOSO CV)

- **Hypothesis:** with the saturation floor and the wall prior doing the separating, an axis-aligned RGB box is sufficient on the white table; blue is the weak class; the horizon gate changes nothing measurable (no barrel pixel is above row 105 in any frame).
- **Method / params:** `experiments/2026-10-20_v1_rgbbox/` (`config.py` BASE = the PROBLEM.md defaults; `run.py`; `sweep.py --mode ablation|coord|pair`). Leave-one-scene-out CV over the 16 pool frames (10 folds); every pool frame predicted once by a model that never saw its scene. Score per the pre-registered rule (`DECISIONS.md` 2026-10-19): primary = mean pooled orange/blue IoU over in-scope positive frames; neg FP > 0.5 % disqualifies; < 0.02 = tie → simplest. Test set untouched. Results: `results/2026-10-20_v1_base/`, `_v1_ablation/`, `_v1_sweep1/`, `_v1_sweep2_pair/`, `_v1_sweep2_coord/` (each has `sweep.csv`/`summary.md`, `configs/<id>.json`).
- **Data / split:** 16 pool frames (`window_light`), 3 of them with a hand in view.
- **Results:**

| step | config | primary | orange IoU (P/R) | blue IoU (P/R) | neg FP | note |
|---|---|---|---|---|---|---|
| BASE (PROBLEM.md defaults) | `5f1a692b` | 0.775 | 0.766 (0.87/0.87) | 0.785 (0.99/0.79) | 0 / 0 | fold std orange 0.18 (the `far` fold: 0.34), blue 0.05; top/topstripe IoU **0.00** |
| ablation: no saturation floor | | 0.046 | | | 25 % / 12 % | collapses; disqualified |
| ablation: no wall (bg) prior | | 0.551 | 0.758 | **0.344** (P 0.37) | 0 / 0 | the wall floods blue — the prior is essential |
| ablation: box only | | 0.039 | | | 25 % / 21 % | the RGB box alone is useless, as the data analysis predicted |
| ablation: no horizon gate | | 0.773 | | | | −0.002: no effect, as predicted |
| ablation: no brightness gate | | 0.775 | | | | +0.000: no effect on this table |
| ablation: **no table prior** | `6c993aa0` | **0.783** | 0.780 | 0.785 | 0 / 0 | tie with base, one stage fewer → chosen; top/topstripe IoU 0.00 → **0.87 / 0.37** |
| ablation: prior fit "all" | | 0.781 | | 0.801 | | tie; lowsat kept (safer by construction) |
| ablation: no per-image cap | | 0.749 | 0.714 | | | −0.026: the two lids dominate the box fit, as predicted |
| ablation: tie → blue | | 0.756 | | 0.723 | | R > B rule is right |
| sweep 1 around `6c993aa0` | | | | | | s_min 50: +0.019 (orange 0.828); k_bg 2.5: +0.010 (blue 0.812); k_table/table_rows: no effect (prior off); v_min 0–40 identical; box 2–98: −0.020, 5–95: −0.113; **horizon_row 90: +0.022** |
| pass-2 candidate (s_min 50 + k_bg 2.5) | `ee36a1e9` | **0.810** | **0.829** (0.99/0.84) | **0.791** (0.99/0.80) | 0 / 0 | +0.027 over `6c993aa0` → adopted (joint move exceeds the band) |
| pass-2 pair s_min_blue × k_bg | | ≤ 0.814 | | | | s_min_blue 50 / k_bg 1.5–2.0 tie with the candidate; s_min_blue ≤ 30 collapses blue precision |
| pass-2 coordinate | | ≤ 0.819 | | | | box 0.5–99.5: +0.009 (tie); everything else a tie or worse → stop (two passes max) |

- **Why the table prior lost:** on the two top-only frames the bottom band mixes bright table with the barrel's dark shadow, so the MAD scale balloons (38–55 vs 13–19 on a normal frame) and the k = 3 rejection box swallows the lid (100 % of lid pixels rejected, `median [123 146 124] scale [38 38 55]`). On every other frame the saturation floor had already removed the table, so the prior did nothing. The prior is therefore both redundant and fragile on a white table; it stays in the code (flag) for dark tables, where the analysis says it will matter, but needs a scale cap or a mode-seeking fit before it can be trusted.
- **Why horizon_row = 90 was NOT adopted** despite +0.022: the gain is entirely on the two hand frames (`far_02`, `core_03`): rows 50–90 there contain the hand, not barrels, and gating them out removes skin false positives. That is tuning to where Tanush's hand happened to be, and row 90 is inside the measured horizon range (55–100), so on other data it could cut real far barrels (a barrel at 300 mm has its top at row ≈ 99). Gate stays at 50. Logged in `DECISIONS.md`.
- **The hand is the orange error:** BASE orange IoU is 0.766 with the hand frames and **0.840 without them** (precision 0.87 → 0.96, recall unchanged). Skin sits inside the orange RGB box (the a* separation noted in constraints.md is not available to an RGB box). `s_min` 50 recovers part of this because shadowed skin is less saturated than the barrel.
- **Blue:** recall 0.80 at precision 0.99 — the misses are shadowed lower faces (sat < 50) and the wall-prior rejections (k_bg 2.5 trades 1 % precision for 3 % recall vs k = 3). Lower `s_min_blue` or higher `k_bg` floods blue with wall.
- **Takeaway:** v1 final config `ee36a1e9`: horizon gate 50, saturation floor 50 (both classes), brightness gate 40 (no effect here, kept for dark tables), table prior off, wall prior k = 2.5 on rows 0–50 (low-sat fit), RGB box 1–99 % fit after the gates with a 3000-px/frame cap, R > B tie rule. CV estimate: primary 0.810 (orange 0.829, blue 0.791), neg FP 0.
- **Next:** single test-set evaluation (same day); v1.5 barrel-referenced re-fit and the YUV chroma arm under the same folds.

---

## 2026-10-20 — Barrel color distribution in RGB (pool frames): box vs diagonal

- **Hypothesis:** (Dave 10/7, navigator K-2) the orange cluster is a brightness-elongated smear and blue is not compact, so an axis-aligned RGB box alone will swallow table/wall; the saturation floor and the band priors have to do the separating.
- **Method / params:** `experiments/2026-10-19_data_analysis/analyze.py`. Pool = the 16 train frames only (test untouched). Barrel pixels capped at 3000/image for fits (the two top-only frames hold ~70 % of all orange pixels); table band = rows 400–480, wall band = rows 0–50, "wall 50–150" = the rows between the horizon and the table edge. Boxes = per-channel percentiles; fullness = occupied voxels / box voxels; PCA on the capped sample; prior curves = median/MAD fit on low-sat (< 40) band pixels, rejection at `k` scales, averaged over frames. Full tables: `results/2026-10-20_data_analysis/stats.md` (copy in the experiment folder), figures there + `figures/`.
- **Data / split:** 16 pool frames, `window_light`.
- **Results:**

| finding | numbers |
|---|---|
| Orange cluster is elongated along brightness | PCA var fraction 0.69 / 0.29 / 0.02 (capped), linearity 0.59, cos(axis1, gray) 0.85; 1–99 box fullness 0.14 (voxel 4) / 0.30 (8) / 0.42 (16) |
| Blue is even less compact | var fraction 0.64 / 0.34 / 0.02, linearity 0.47, cos 0.80; fullness 0.14 / 0.29 / 0.42 |
| A 1–99 RGB box alone cannot separate | table band inside orange box **61 %**, inside blue box **55 %**; wall band inside blue box **86 %**; all "other" inside: 34 % / 40 % |
| The two boxes overlap heavily | overlap = 45 % of the orange box volume; 10 % of orange and 15 % of blue labeled pixels sit in it; the R > B tie rule resolves 97 % of those orange but only 62 % of those blue |
| Saturation floor does the heavy lifting | sat ≥ 40: orange 98.5 %, blue 82.6 % kept; table 1.2 %, wall band 3.2 %, all other 6.1 % kept. sat ≥ 60: orange 93 %, blue 72 %; table/wall ≈ 0 |
| The wall between horizon and table edge is the hard non-barrel region | at sat ≥ 40 it keeps **25.6 %** (vs 3.2 % for rows 0–50): it is bluish, and the blue box contains 67 % of it |
| Brightness gate buys little here | val ≥ 40 keeps ≥ 96 % of everything; it only matters for near-black pixels (none on this table) |
| Table prior (k = 2–3) | rejects 53–88 % of the saturated non-barrel pixels at the cost of 9–18 % orange / 9–16 % blue — the cost is high because shadowed barrel faces are near the (gray) table color |
| Wall prior (k = 2–3) | rejects 82–85 % of saturated non-barrel at the cost of 0.4–2.4 % orange / **4–13 % blue**. Guard never tripped. |
| Non-v1 extra: YUV chroma plane | orange box fullness 0.57, blue 0.47 (better than RGB) but both clouds run along the gray-ward diagonal (= saturation), and the blue chroma box contains **99.7 %** of other pixels. A chroma *box* is the wrong shape; a hue/saturation (polar) split would be natural. Parked for v1.5. |

- **Takeaway:** confirmed — box-shaped it is not. v1's RGB box must be fit **after** the gates (so its percentiles aren't spent on dark/desaturated pixels the gates remove anyway) and the saturation floor + wall prior are the real separators; blue recall vs wall rejection is the central trade-off (`s_min_blue` and `k_bg` must be swept jointly). Resolves `constraints.md` unknowns #4/#5 for this table/light.
- **Next:** v1 pipeline + LOSO CV (same day).

---

## 2026-10-19 — Camera geometry of AIM-4A8B6118 (focal length, tilt, horizon)

- **Hypothesis:** `camera.py`'s f = 400 and Dave's 23° tilt are close; the 70°×50° FOV figures are not.
- **Method / params:** `experiments/2026-10-19_camera_geometry/measure.py`. f from barrel silhouette width at 5 ruler distances (`calib_01..05`, D = 22 mm, camera 3 mm behind the front edge + 11 mm radius). Tilt by least squares on the image rows of the 4–10 cm marks of a tape measure laid from the front edge (`ruler_01`, rows read by eye from an upscaled crop), f fixed, principal point fixed at (320, 240).
- **Data / split:** `data/raw/4A8B_upcool_wood_{calib,ruler}_*.png` (wood desk, cool lamp; geometry only, not a segmentation set).
- **Results:**

| quantity | value | notes |
|---|---|---|
| focal length | **404 px** (400, 404, 410, 409, 400 at 64–314 mm) | consistent across all distances, so D = 22 mm + the offsets are self-consistent (but f and D are not separable from widths alone) |
| tilt | **23.3°** | rms 3.8 px over 7 marks; the 6–10 cm marks fit within 2 px, the 4–5 cm reads are the noisy ones |
| horizon row | **≈ 66** | 240 − 404·tan(23.3°) |
| bottom row ↔ ground | 31.6 mm from the camera | |

- **Takeaway:** f = 400 was a good guess; use 404. Tilt 23.3° matches Dave's "assume 23°". Freeing the principal point only trades off against tilt (cy 220 ↔ 20.7°), so it is not identifiable here; keep (320, 240). The 70°×50° FOV in `camera.py` is wrong. Horizon gate for this robot: row 60.
- **Update (same day, after Tanush measured the barrel):** the barrel is **24 mm tall, 18 mm at the ends, ≈ 25.5 mm at the bulge** (circumference 80 mm), 6 mm stripe — not 25 × 22. Re-deriving with D = 25.5: widths give **f ≈ 356** (347–358, still very consistent across distances, which also confirms the 3 mm camera-behind-front-edge offset). But the ruler-mark fit prefers f ≈ 405–420 with the tape zero at the front edge (rms 3.2 px), and only accepts f ≈ 350 if the tape zero was ~8 mm off (rms 2.6 px). A third estimate from the barrel bottom rows (contact at the near edge of the 18 mm base) gives tilt 21.5°, f 388, horizon 88 (rms 0.8 px, but the contact-point assumption is soft). **Honest summary: f ≈ 355–405, tilt ≈ 21.5–25.5°, horizon row 55–100.** Horizon gate set at row 50, which is below every fit.
- **Next:** a direct horizon measurement (mark at camera height 43.47 mm on a far wall) resolves this independently of f and barrel size; optionally a cleaner ruler frame with the tape's zero line visibly at the front edge. Re-run for any other robot.

---

## 2026-10-07 — Color baselines: fixed HSV vs. lighting (pre-labels, probe-based)

- **Hypothesis:** fixed color thresholds survive home-lighting variation well enough to segment barrels.
- **Method / params:** probe-based metrics (hand-picked probe regions, no full labels). Fixed HSV thresholds; also tried gray-world white balance as a diagnostic. Code: `experiments/2026-10-07_baselines/` (`methods.py`, `grid.py`, `fig.py`); figure `comparison.png`.
- **Data / split:** 19 home frames, warm wood desk, 3 lamp directions × 3 warmths (`{up,at,away}{cool,mid,warm}`); `color_data/` at the repo root (see `DATA.md`). No train/test split (no labels yet) — **directional findings only, small data.**
- **Results:**

| finding | numbers |
|---|---|
| Camera does NOT fully auto-white-balance | warm light shifts the whole image: mean blue channel 134 → 73 |
| Orange barrel body is robust | H ≈ 2–7, S ≈ 225 under all 9 settings |
| Blue stripe is fragile under warm light | S 236 → 103, V ≈ 60; fixed HSV catches only **17%** of it |
| Wood looks "orange" under warm light | H ≈ 15, S ≈ 170; fixed HSV flags **70%** of wood as orange |
| Lab a* separates orange from wood | barrel orange ≈ 50 vs wood ≈ 15–20; skin ≈ 29, orange cardboard ≈ 33 |
| Gray-world WB (diagnostic only) | wood FP 70% → 8%, stripe recall 17% → 100%, but over-corrects when wood dominates (grays go blue) |

- **Takeaway:** fixed thresholds fail under warm light (blue stripe recall collapses; wood floods orange). Per-image adaptation is necessary; a global "average is gray" assumption fails on a dominant table color — consistent with Dave's no-image-correction mandate (see `DECISIONS.md` 2026-10-07). New failure modes spotted for later: barrel reflections on glossy tables, shadowed barrel faces, glare on lids.
- **Next:** labeled data + real eval harness (`EVAL.md`), then v1 adaptive RGB-box thresholds with table/background rejection; plot the RGB clusters (box vs. diagonal, unknown #4 in `constraints.md`).

---

## 2026-10-07 — Lab 6: aivision + world-map accuracy (context, not a segmentation experiment)

- **Method:** barrels at measured distances; compare `show objects` world-map positions vs. ruler.
- **Results:** map distance accuracy ~1 cm at 9–14 cm (blue: real 87.5 mm vs map ~95; orange: 137.5 vs ~137). A few mm decides reachable vs. GoalCollides. **aivision consistently returns no box for close-range barrels** (occasional flicker) — the planner is blind right next to the robot. Untested: clustering/adjacency.
- **Takeaway:** the close-range blindness is a concrete, reproducible vendor failure our detector should eventually fix; world-map math is decent when a box exists.

---

## Template

```
## YYYY-MM-DD — <name>
- **Hypothesis:**
- **Method / params:** (script + config path)
- **Data / split:**
- **Results:** (table)
- **Takeaway:**
- **Next:**
```

