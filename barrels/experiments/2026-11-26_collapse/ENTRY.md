# ENTRY.md — the text for `docs/EXPERIMENTS.md` (paste it in; newest first)

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

## Second pass

**2026-11-26, branch `wip/collapse-2`, from `barrels` at `c0019d5`.** The collapse left a list of things it had proved dead or never deciding. This pass takes them out. The rule is the same (after every step the same boxes on the 5435 masks, and the suite passes), with one rule more: a thing goes only when an **argument** says no box can change. "No mask showed a difference" is not enough. One commit per item, with the argument in the commit message.

| item | commit | what went | the argument, in one line | harness after the step |
|---|---|---|---|---|
| B14 | `7a738ce` | `widest_barrel`: "one barrel at most" is `body_width` at all nine sites | it returned the larger of `body_width` and 1, and `body_width` is 1.2 | IDENTICAL BOXES ON EVERY INPUT; the log is the same |
| B13 | `09d239b` | the upper limit of the height check of `find_pieces`, and `height_max` | a piece's bottom is seen or drawn where its top row predicts it, so no piece is too tall: at most 1.09 × for 8 cameras, every top row and bottom row (the limit was 1.5) | IDENTICAL BOXES ON EVERY INPUT; the log is the same |
| B1 | `1954f18` | the "too far for a stripe" half of the close-up rule, the rule name "far_piece", and `min_stripe_px` | the rule asked "is the stripe at its middle row under 4 px?"; for every piece stage 1 lets through that is not a close-up it is at least 4.12 px (8 cameras, every pair of rows) | IDENTICAL BOXES ON EVERY INPUT; the log is the same |
| C1 (new) | `422b1e3` | "does the stripe's row give a distance?" in `find_stripes` (reason "no_geometry") and in `_join_pieces` | sandwich pixels exist only at rows that give a distance; those rows are one unbroken range; a stripe is read at a row between two of its own pixels' rows | IDENTICAL BOXES ON EVERY INPUT; the log is the same |
| B15 | `7a6bf17` | no check: "kept" is written when a box goes into the list, "duplicate" for the box that goes | notes only; the lists are built by the same statements, and the detector does not read its log | IDENTICAL BOXES ON EVERY INPUT; the log differs on 3 inputs (2 "kept" notes of boxes that lost are gone, 1 "duplicate" note moved to the box that went) |

`DetConfig`: 20 → 18 numbers. `detector.py`: 1825 → 1823 lines. The stripe finder has 6 checks (was 7), the close-up stage 3 steps (was 4), and the path of a plain barrel 14 tests (was 15).

**What stays of each removed check.**
- B13: `height_min` stays, because it decides. A piece is under 0.5 × the height for its bottom row exactly when its top row predicts no bottom (top at row 427 or lower: the base would be at or behind the camera) and it still ends inside the frame. A barrel that near runs out of the frame bottom. Without the check such a piece would go on to stage 4 as a close-up.
- B1: the 4 px is now the constant `THINNEST_STRIPE_PX`. `on_the_table` asserts that a barrel on the table has a stripe that tall.
- C1: `find_stripes` and `_join_pieces` assert the fact.
- Each fact has a test that tries every row for the four cameras the repo names.

**How near to breaking** (`second_pass_margins.py`; output in `results/2026-11-26_collapse/second_pass.md`). B13 is far from it: 1.17 × with the edge tolerance at 50 %, 1.28 × with its floor at 12 px. B1 is near: it breaks with `min_width_px` at 14 or with the tolerance floor at 8 px. The removed rule would then have kept far blobs with no stripe; now they are refused as "stripeless". That is a difference at other numbers, and it is the wanted one. C1 holds for any camera.

**Not done, and why.**

| item | why not |
|---|---|
| B7: `drop_single_reading` reads the span `seen_span` measured | not identical. Of the 43 boxes the last stage asks on the 5435 masks, 3 get the other answer and would be kept (`second_pass_b7.py`). It stays an experiment |
| "the box is at least 2 × 2" ("empty_box") | it never fires on the masks, but no argument says it cannot |
| "no_geometry" in `box_from_stripe`, and the same question in the order of `boxes_from_stripes` | dead for a stripe the finder made (C1), but these functions also take a stripe made by hand |
| `_closeup_stripe_rows` for a top above the horizon | stage 1 refuses such a piece first, but the helper is called directly too, and "no distance" must not read as "below the frame" again |
| "a blob holds at least one barrel pixel" (`find_blobs`) | true with the 3 × 3 closing only; it guards a division |
| "does not touch the frame top" in the height check | dead with these cameras (such a piece is above the horizon); kept for a camera whose horizon is above the frame |
| B2 to B6, B8 to B12 | they change boxes: experiments of their own |

**Tests.** 952 before, 955 after. None removed, none weakened.

| test | file | item | what changed |
|---|---|---|---|
| `test_no_piece_is_too_tall_and_only_a_piece_with_no_predicted_bottom_is_too_short` | `test_detector.py` | B13 | added |
| `test_no_piece_is_too_far_away_to_show_a_stripe` | `test_detector.py` | B1 | added |
| `test_a_stripes_row_always_gives_a_distance` | `test_detector.py` | C1 | added |
| `test_a_barrel_on_the_table_has_a_stripe_tall_enough_to_resolve` | `test_detector.py` | B1 | reads `THINNEST_STRIPE_PX`; four cameras, was three |
| `test_a_removed_detector_switch_gives_a_clear_error` | `test_report.py` | B13, B1 | 18 numbers, was 20; `height_max` and `min_stripe_px` must stop with "no longer a number of the detector" |

**Everything that uses the detector.** `report.py --cand-det height_max=…` or `min_stripe_px=…` stops with a message that says why the number is gone (`REMOVED_DET_NUMBERS` in `report.py`). Nothing else named the two numbers. `detect(mask, DetConfig(), cam)` and `detect(mask, log=log)` are unchanged. One reason name is gone from the log ("stripe: no_geometry", which never occurred), one rule name ("far_piece", which no box ever had), and the "stripeless" note no longer carries `expected_stripe_h` (nothing read it).

**At the end**, on the last code commit (`7a6bf17`):

| check | result |
|---|---|
| the test suite | 955 pass |
| the proof harness | IDENTICAL BOXES ON EVERY INPUT: 5435 masks, 6152 boxes, against the boxes before the collapse. Reason logs: the 224 inputs of A7 and the 3 of B15, nothing else |
| `report.py --gate` | PASS: all 6 protected sets "same", the 19 other sets unchanged, no box on an empty frame |
| `judge.py --cand-det bottom_tol=0.15 --no-save` (a candidate that changes nothing) | NO CLEAR DIFFERENCE: 0 barrels gained, 0 lost, 0 frames with a changed box (exit code 3) |
