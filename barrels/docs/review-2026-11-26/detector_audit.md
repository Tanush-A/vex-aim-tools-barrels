# Detector logic audit (`barrels/src/barrels/detector.py`, snapshot `final/barrels`)

Audit only; nothing in the snapshot or the repo was changed. Scripts and raw outputs: `/private/tmp/claude-502/-Users-tanush-Desktop-Celeste-vex-aim-tools-barrels/bc194f8a-459b-4746-98d1-b23688f2f947/scratchpad/work_detector/` (`common.py`, `build_masks.py`, `attrib.py`, `ablation.py`, `killchain.py`, `census.py`, `brittle.py`, `soft.py`, `routes.py`, `oracle.py`, `stencil_real.py`, `viz.py`; results in the `.json` / `.csv` files beside them; three picture sheets in `viz/`).

## Method and caveats

- **Train frames only.** Every script asserts each stem is in `splits.json` "train" and not in "test" before an image is opened. No test frame was loaded, scored or viewed.
- **Scoring is the project's**: `eval_det.evaluate_frame(rule="v2")` exactly as `report.score_boxes` calls it (same colour, IoU >= 0.5, bottom within 10 % / 3 px). Imports verified to come from the snapshot.
- **Baseline reproduced**: HOME 28 of 29 (leave one scene out with a re-fit model, as `report.run_arm` does; the stored model gives the same 28), CAMPUS 35 of 35, no false box, nothing on a negative frame.
- **Sets.** A = HOME (leave one scene out) + CAMPUS, 37 frames, 64 barrels. B = every train frame with box labels in the 15 non-extreme conditions (gray, ABP white, pale wood, ottoman warm / mid / cool 6, glass x 5, bathroom x 4), fixed model `eb863d84`: 117 frames, 243 barrels. C = the 45 frames with hand-set slider thresholds, segmented with those thresholds: 135 barrels.
- **C is not neutral "good colour".** The slider tool shows the detector's boxes while the thresholds are moved, and the stated criterion is "as much barrel painted as needed to detect it". C's thresholds are fit to this detector frame by frame; its 115 of 135 is an upper bound.
- **Label copies.** The lamp-ladder conditions of one place share copied boxes, so per-condition geometry numbers within a place are not independent.
- **"Clean" barrel** = a label with no flag (not occluded, truncated, held or bottom-estimated).
- No timing is reported: the machine was heavily loaded during the runs (the project's own figure is 19 ms median per frame).
- The detector's occlusion numbers in the docs come from simulated scenes (`occlude.py`) and synthetically damaged masks (`degrade.py`). Nothing here uses them; where I quote them I say so.

## 1. Inventory

### 1.1 Counts

| what | count |
|---|---|
| `DetConfig` fields | **51** |
| boolean switches | **30** (23 on, 7 off) |
| numeric thresholds | **20** |
| mode strings | 1 (`stripe_mode`, 2 values) |
| numeric literals in `detector.py` outside `DetConfig` (AST count, docstrings excluded) | 643; **131** other than 0 / 1 / -1 / 2 |
| distinct hard-coded decision constants outside `DetConfig` (curated, list in 1.4) | **about 30** |
| box-making rules (each its own function or branch) | 9: stripe whole, stripe partly seen (5 sub-branches), stripeless close-up, cap, post pair, slice behind (off), half stripe, plus 2 verify drops |
| reason-log codes | 45 (40 rejections, 5 "kept") |

So the detector has about 80 knobs, not 50. And the 51 understate the coupling: a handful of numbers are reused for unrelated tests (uses in code: `close_px` 18, `stripe_full` 16, `body_width` 13, `bottom_tol` 11, `bottom_tol_min_px` 9, `min_area_px` 7), so they cannot be tuned for one purpose without moving five others.

### 1.2 Data flow, in the order `detect` runs

0. (outside the detector) colour step: pixel is orange / blue when row >= 50, V >= 40, hue in the class sector, S >= the class floor.
1. **Blobs and pieces** (`find_blobs`, `split_blob`, `resolve_bottom`, `_step1_pieces`): union of both colours, 3x3 close, components >= 20 px; width / expected width rounded = number of barrels, cut at waists; bottom = seen or predicted from the top row; keep pieces 0.4-1.6 W wide, 0.5-1.5 H tall, nearer than 64 cm.
2. **Stripe finder** (`_find_stripes_cores`): per body colour, other-colour pixels sandwiched between body above and below within 3 stripe heights; components joined (`stripe_join`, `stripe_bridge`); tests area, distance, height (`seam_height` second reading), width floor; wide regions cut (`stripe_merge`, `stripe_wide`); narrow pieces set aside.
3. **Stripe step** (`barrel_from_stripe`, `_partly_seen`), whole stripes first, then partly seen ones nearest first: row -> distance -> predicted box; seen top / bottom kept when within tolerance; `edge_check`; a stripe under 0.8 W goes to `side_hidden` -> reasons -> `pin_outline` -> `pin_thin` / `thin_span` / `thin_frame` -> centred or nothing; `body_min`; duplicate resolution by confidence.
4. **Stripeless pieces**: step-1 pieces not covered by a stripe barrel (`cover_rows`), kept only as close-ups (`closeup_stripe`, `closeup_side`) or "too far for a stripe" (cannot fire for a correctly shaped barrel, see 4c).
5. **Verify pass 1** (`verify_front`) on the boxes so far.
6. **Caps** (`caps_behind` with `cap_same`, `cap_low`, `cap_seen_bottom`).
7. **Left-overs**: `post_pairs`, then `slices_behind` (off).
8. **Half stripes** (`half_stripes`, `half_thin`); may replace a stripe-step box.
9. **Verify pass 2** (`verify_front` again on everything), then `verify_readings`.

### 1.3 Every switch and threshold

Evidence column: **R** = motivated and checked on real frames or recordings; **S** = its evidence is the simulated occlusion scorecard (`occlude.py`) and / or synthetically damaged masks (`degrade.py`); **R+S** = one real case plus simulation. "Real effect" is my measurement on sets A + B + C (section 2): frames whose boxes change when the switch is flipped.

**Numeric thresholds (20)**

| name | default | meaning | stage | interacts with | motivating case | evidence |
|---|---|---|---|---|---|---|
| `min_area_px` | 20 | speck floor | 1, 2, 6, 8, 9 | reused as: blob floor, stripe floor, cap floor, half-band floor, `verify_front`'s "own evidence" floor | v1.5 constant, "never tuned" | none stated |
| `close_px` | 3 | 3x3 morphological close; and (unrelated) how many pixels beside an end to look for a nearer barrel | 1, 2, 3, 6, 8 | step function: values 1 and 2 mean "no closing", 4 means 5 | speckled faces | none stated |
| `bottom_tol` | 0.15 | seen edge trusted within this share of predicted height | 1, 3, 4, 6, 7, 8 | also the horizontal "body and stripe end apart" tolerance (x W), the cap bottom window, `closeup_side`, `own_close`'s closure limit | camera "good to 5-10 %" | R (home frames) |
| `bottom_tol_min_px` | 4 | floor of the above | same | same | labelling precision | R |
| `width_min` | 0.4 | piece narrower than this x W dropped | 1, 6 | also the cap width floor, and (with `cap_low`) the cap HEIGHT floor | slivers | R |
| `width_max` | 1.6 | piece wider than this x W dropped | 1 | one of four "wider than a barrel" constants (1.2, 1.4, 1.5, 1.6) | "slack" | none |
| `split_search` | 0.25 | waist search window | 1 | `split_blob` | touching rows | R (home) |
| `min_width_px` | 16 | W below this = beyond the table (64 cm) | 1, 2, 6, 8 | makes `min_stripe_px` unreachable | hand at the horizon, home `far_02` | R |
| `stripe_h_min` | 0.45 | stripe core height floor (x expected) | 2, 8 | also the thin-piece WIDTH floor (x stripe height) | erosion at far range | R |
| `stripe_h_max` | 1.6 | stripe core height ceiling | 2, 8 | also the join shape test | upper body read as band | R |
| `band_h_max` | 3.0 | how far body may be from a stripe pixel (sandwich reach) | 2, 8 | | shadow under a stripe | R |
| `stripe_w_min` | 0.4 | under this a partly seen stripe needs a reason | 2, 3, 7 | finder floor only when `side_hidden` off; post-pair piece limit | campus `occl_02` | R |
| `stripe_merge` | 1.4 | stripe region wider than this = several barrels | 2 | overlaps `stripe_wide` (1.2) and `stripe_two` | touching same-colour barrels (home `touch`) | R |
| `stripe_full` | 0.8 | stripe narrower than this = partly hidden | 2, 3, 6, 7, 8, 9 | 16 uses: partly-seen switch, `seam_height` gate, half-stripe column shares (0.8 and 1 - 0.8), cap "whole width", pair span, `thin_span`, `verify_readings` | "free stripe is 0.85-1.05 W" | R |
| `min_stripe_px` | 4.0 | stripe thinner than this cannot be resolved | 2, 4, 8 | **cannot fire for a real barrel**: a stripe < 4 px needs d > 688 mm, `min_width_px` already refuses d > 638 mm; at 4.8 it fires on mis-shaped pieces (+43 false boxes) | far barrels | none |
| `height_min` / `height_max` | 0.5 / 1.5 | stripeless piece height window | 1 | written for a far jacket; today it is the only guard on `closeup_stripe` and on the far branch (off: B 7 -> 105 false boxes) | blue jacket, campus `core_01` | R (one frame) |
| `body_min` | 0.1 | box must hold body colour in the stripe columns | 3 | | campus `core_01` pair | R |
| `body_width` | 1.2 | box at most this x W; also: join span, trusted-body limit, cap max width, half-stripe and pair span, `stripe_wide` limit | 2, 3, 6, 7, 8, 9 | 13 uses | boxes 15 % narrow on campus | R |
| `pin_good` | 0.05 | outline cost under which an end is "the barrel's own side" | 3 | `pin_outline`, `pin_thin` | `end_census.md` on scorecard scenes | S |

**Boolean switches (30) and the mode**

| name | default | meaning | stage | needs / interacts | motivating case | evidence |
|---|---|---|---|---|---|---|
| `require_stripe` | on | stripe step is the detector; off = step 1 alone | all | everything below | home frames 0.71 -> 0.91 | R |
| `stripe_mode` | cores | stripe from its own pixels vs non-body gap (`bands`) | 2 | `bands` ignores most later switches | campus `core_01`, `plain_01`, `close_01`, `window_01` | R |
| `dark_stripe` | off | a gap with no stripe pixel counts as a stripe | 2 | cores only | floating boxes, first live run | R |
| `cover_rows` | on | stripe barrel covers a piece only if rows overlap too | 4 | | live run with Dave: close-up vanished | R |
| `occl_body_side` | off | old side rule reads the body columns | 3 | only when `side_hidden` is off: **dead** | campus `occl_02` | R (superseded) |
| `stripe_join` | on | stripe pieces in one barrel's width are one stripe | 2 | `stripe_bridge` | damaged masks: 85 -> 125 of 145 | S |
| `cap_behind` | on | upper body above a found nearer barrel is a barrel | 6 | `cap_same`, `cap_low`, `cap_seen_bottom`; leans on stage 3-5 boxes | home `occl_01`, `cluster_01`; black table | R |
| `side_hidden` | on | partly seen stripe placed by what is seen; side hidden only for a reason | 2, 3 | gate for `pin_*`, `thin_*`, `slice_box`, `own_close`; lowers the finder floor | campus `occl_02` (the live miss) | R+S |
| `seam_height` | on | thin far stripe read again as mean of own height and body gap | 2 | `stripe_full` | home `far_02` with 2 px eroded | S |
| `cap_seen_bottom` | on | narrow cap's bottom from its own colour beside the front barrel | 6 | `cap_behind` | home `cluster_01` (27 -> 28) | R (one barrel) |
| `slice_box` | off | cover box where nothing pins a slice | 2, 3 | `side_hidden`, `cover_unpinned` | scorecard 75 % rows | S (rejected) |
| `cover_unpinned` | off | cover box also for wide unpinned stripes | 3 | `slice_box` | scorecard | S (rejected) |
| `stripe_two` | off | stripe wider than 1.2 W = two barrels | 2 | superseded by `stripe_wide` | scorecard "same colour beside" | S (rejected) |
| `edge_check` | on | (a) both edges inferred and top against other colour -> refuse; (b) seen bottom against other colour -> lower of seen / predicted | 3 | hard-coded 4 rows, half the columns | 18 scorecard boxes, "none on HOME, CAMPUS or the recordings" | S |
| `cap_same` | on | cap test also on parts outside found same-colour boxes | 6 | `cap_behind` | scorecard "same colour in front" | S |
| `half_stripe` | on | band with body on one side only = barrel hidden from above / below | 8 | `half_thin`; can replace a stage-3 box | scorecard "from above / below" 2 -> 40 of 50 | S |
| `half_thin` | on | drop the half-stripe height floor | 8 | `half_stripe` | scorecard | S |
| `post_pair` | on | two slices one barrel apart = one barrel behind a post | 7 | `_full_slice`, narrow / unplaced lists | scorecard "post" 9 -> 41 | S |
| `stripe_wide` | on | `stripe_two` only with body above and below | 2 | `stripe_merge`, `_partly_seen` cut sides | home `core_02` with a pasted barrel | S |
| `slice_behind` | off | narrow full slice beside a nearer barrel / frame edge | 7 | | scorecard; 7 false boxes on damaged masks | S (rejected) |
| `cap_low` | on | cap height floor 0.4 instead of 0.5 | 6 | reuses `width_min` as a height floor | scorecard "straight in front" 17 -> 22 | S |
| `pin_outline` | on | unpinned partly seen stripe placed by rounded-corner fit | 3 | `side_hidden`, `pin_good`; duplicate fallback re-runs the rule with it off | scorecard straight / slanted edge | S |
| `pin_thin` | on | thin slices admitted, need full slice + outline | 2, 3 | `side_hidden`, `pin_outline`; changes finder floor | scorecard 75 % rows | S |
| `stripe_bridge` | on | join non-stripe-shaped pieces across a body-bridged gap | 2 | `stripe_join`; **failed its own pre-registered rule**, switched on by hand | damaged masks "bad day" | S |
| `thin_frame` | on | thin full slice at the frame edge is W wide from the other end | 3 | `pin_thin`; **failed its own rule** ("too big"), switched on by hand | scorecard frame edge 29 -> 88 | S |
| `own_close` | off | end where the body closes on the stripe is the own side | 3 | | scorecard; +1 false on damaged | S (rejected) |
| `thin_span` | on | thin slice whose body shows full width gets that width | 3 | `pin_thin`, `_body_crosses` | scorecard stripe-colour block 3 -> 77; black-table clip | S (+ one recording) |
| `closeup_side` | on | side-cut close-up must be seen down to its stripe | 4 | `closeup_stripe` | printed fruit on empty frame `occlx_15` | R (one frame) |
| `closeup_stripe` | on | piece whose stripe runs past the frame bottom is a close-up | 4 | | palewood `close_01` | R (one frame) |
| `verify_front` | on | box read from a nearer barrel's own picture is dropped | 5, 9 | reads the reason log; runs twice | ABP `occlx_17`, gray `clutter_01`, 9 recording frames | R |
| `verify_readings` | on | partly seen stripe box with both edges inferred dropped | 9 | reads the reason log | glass `neg_02` tin, sticky note | R |

Tally of the 23 switches that are on: **14 rest on simulation only** (`stripe_join`, `seam_height`, `edge_check`, `cap_same`, `half_stripe`, `half_thin`, `post_pair`, `stripe_wide`, `cap_low`, `pin_outline`, `pin_thin`, `stripe_bridge`, `thin_frame`, `thin_span`); 3 rest on one real frame or one real barrel each (`cap_seen_bottom`, `closeup_side`, `closeup_stripe`); 6 on several real frames (`require_stripe`, `cover_rows`, `cap_behind`, `side_hidden`, `verify_front`, `verify_readings`). Two (`stripe_bridge`, `thin_frame`) were switched on by hand after failing the rule written for them. The docs say it themselves for five: "`half_stripe`, `post_pair`, `stripe_wide`, `pin_outline` and `pin_thin` change no box on any real frame or recording so far".

### 1.4 Hard-coded constants that are not in `DetConfig`

| where | constant | what it decides |
|---|---|---|
| `find_blobs`, `_closed`, finders, caps, half | 8-connectivity; "close only if `close_px` >= 3, bump even to odd" | what is one blob |
| `_step1_pieces` | ties go to orange (`n_o >= n_b`) | piece colour |
| `_split_merged`, bands finder | 0.25 | when the stripe centre is the median of its coloured rows |
| cores / bands / bridge / half | 10th-90th percentile of rows, + 1 | "the stripe's height" |
| `_join_shaped`, `_join_bridged`, `_piece_of_found`, `post_pairs` | overlap >= half the shorter height | "same rows" |
| `_join_*`, finder | height <= width | "stripe-shaped" |
| `_join_bridged` | middles within 1/2 stripe height; gap <= 1/2 joined span; body in EVERY gap column | bridge |
| `seam_height` | equal weights 1/2, 1/2 | second height reading |
| `_body_extent`, `_seen_lines` | gaps of 3 rows | where the body ends vertically |
| `_body_columns`, `_body_span` | >= 2 body pixels per column, gaps of 2 columns | where the body ends sideways |
| `Outline` | lid half-width 0.353; side curve 1 - sqrt(1 - t) | the barrel's silhouette |
| `_end_costs` | columns within 0.353 W of the end; worst of three lines; median removed; >= 2 columns | own-side test |
| `CLOSE_ZONE`, `CLOSE_CUT` | 0.05, 0.1 | `own_close` (off) |
| `_body_crosses`, `seen_edge` | 0.5 | body crossing the stripe; edge against barrel colour |
| `edge_check`, `_full_slice`, `half_stripes` | 4 rows beyond the edge, half the columns | "ends against barrel colour" |
| `_partly_seen` | horizontal tolerance = `bottom_tol` x W | body and stripe "end apart" |
| `barrel_from_stripe` | confidence 0.5 + 0.5 x labelled share; body count >= stripe count | duplicate winner; `body_min`'s second clause |
| `detect` and 6 other places | IoU > 0.5 | "the same barrel" |
| `detect` | x-overlap > 0.3 | a stripe barrel "covers" a piece |
| `caps_behind` | half the pixels inside own-colour boxes; half the predicted box under nearer boxes; 3 empty rows end a bottom; confidence 0.5 | cap tests |
| `half_stripes` | 0.8 / 0.2 column shares (from `stripe_full`); seams at 15 and 9 mm | band orientation, distance |
| `verify_front` | seam band of half a stripe height counts as either colour; "nearer" = strictly lower bottom | what a front barrel explains |
| `_stripe_geometry`, caps | d <= 12.75 + 1 mm | impossible distance |
| four places | four different tests for "a nearer barrel" (bottom lower than: predicted bottom / cap's bottom / box bottom / other's bottom) | depth order |

## 2. Real-frame ablation

Each change is applied alone to `DetConfig()` and the three sets are re-scored. Full machine-readable results: `work_detector/ablation.json`.

### 2.1 Reading the tables

**Which switches change nothing.** Of the 30 switches, flipping **9 changes no box on any of the 199 frame-runs**: on by default `cap_same`, `edge_check`, `post_pair`, `cap_low`, `thin_span`; off by default `stripe_two`, `occl_body_side`, `cover_unpinned`, `own_close`. **17 of 30 change at most one frame.** 8 change 2 to 5 frames. Only 5 change more: `require_stripe` (179), `dark_stripe` (112, off), `side_hidden` (73), `stripe_join` (15), `slice_box` (12, off).

**Which matter** (found barrels lost when switched off, A / B / C; false boxes added):

| switch | found lost | false boxes |
|---|---|---|
| `require_stripe` | 30 / 57 / 45 (and +16 / +10 gained) | +49 / +525 / +166 |
| `side_hidden` | 1 / 8 / 17 | 0 / +1 / +4 |
| `stripe_join` | 0 / 6 / 0 | 0 |
| `cap_behind` | 3 / 2 / 0 | 0 |
| `seam_height` | 0 / 3 / 0 | 0 |
| `verify_readings` | 0 | 0 / +3 (2 on empty frames) / 0 |
| `verify_front` | 0 | 0 / +2 / 0 |
| `stripe_bridge` | 0 / 2 / 0 | 0 / -1 / +1 |
| `half_stripe` | 0 / 2 / 1 | 0 / 0 / -1 |
| `stripe_wide`, `pin_outline`, `pin_thin`, `thin_frame`, `half_thin`, `closeup_stripe` | 1 barrel each, all in B | 0 |
| `cap_seen_bottom` | 1 (HOME `cluster_01`) | 0 |
| `closeup_side` | 0 | +1 on an empty frame |

`side_hidden` is the only occlusion-era switch with weight, and section 3.6 shows why: it boxes 50 clean barrels whose stripe came out narrow. It is a segmentation-repair rule filed under occlusion.

**Net harmful on real train frames.**
- `cover_rows` (on): switching it off removes one false box (the wood-grain "close-up" on `palewood_core_01`, which the old columns-only test happened to suppress) and loses nothing. Its motivating case was a live run, not a frame in the set.
- Every off-switch stays harmful when turned on: `dark_stripe` finds 30 more barrels (22 in B) and loses 9, at +89 false boxes, 20 on empty frames; `slice_box` +2 / -2 found and +3 false; `slice_behind` +1 false. Note what `dark_stripe` shows: "two body pieces with a stripe-sized gap" is real evidence for 30 barrels, and as a yes / no rule it is unusable.
- `half_stripe` is close to break-even on real frames: 3 barrels found, 1 false box drawn (bottom 12 px short).

**Redundant pairs.** 231 pairs of on-switches were turned off together. Only 10 pairs behave differently from the two single effects added up, each by 1 or 2 barrels, nearly all involving `stripe_join` or `side_hidden` (e.g. `stripe_join` + `side_hidden` off: 16 lost on B where the singles lose 14: each covers two barrels for the other; `thin_span` matters only once `stripe_join` is off). The rules are almost perfectly additive. That is the signature of a patched list: each rule catches its own few frames and no rule generalises into another's territory.

**Groups.**

| what is switched off | found A / B / C (of 63 / 148 / 115) | false A / B / C (of 0 / 7 / 3) |
|---|---|---|
| the outline machinery: `pin_outline`, `pin_thin`, `thin_span`, `thin_frame` (with `Outline`, `_seen_lines`, `_end_costs`, `pin_good`) | 63 / 147 / 115 | 0 / 7 / 3 |
| `half_stripe`, `half_thin`, `post_pair`, `stripe_wide` | 63 / 145 / 114 | 0 / 7 / 2 |
| the 13 on-switches whose only evidence is simulation | 63 / 139 / 114 | 0 / 6 / 2 |
| the verify step | 63 / 148 / 115 | 0 / 12 / 3 |
| everything added after 2026-11-18 (19 switches) | 61 / 131 / 96 | 0 / 10 / 6 |
| everything added after 2026-11-09 (21 switches: hardening a-g only) | 59 / 126 / 94 | 0 / 10 / 6 |

- The 13 simulation-only switches together find **10 barrels of 326** and add 2 false boxes. The four outline switches together are worth **one barrel**.
- All 19 switches added after 2026-11-18 together find 38 more barrels and remove 6 false boxes (5 of the 6 are the verify step); `side_hidden` alone is 26 of the 38.
- The detector of 2026-11-09, with 21 fewer switches, finds 279 of today's 326 on these frames.

**Greedy removal** (newest first): `thin_span`, `cap_low`, `post_pair`, `cap_same`, `edge_check` can all be off at once with every box on every frame identical. Adding `cover_rows` to the list loses no barrel and removes a false box.

**Numeric thresholds, +-20 %.** 16 of the 40 changes move no box. The ones that matter, and the cliffs:

| threshold | effect |
|---|---|
| `stripe_full` 0.8 | 0.64: +6 found on B, +4 false; 0.96: -11 found. 37 and 79 frames change |
| `body_width` 1.2 | 0.96: 86 frames change, -5 found, +3 false; off: 107 frames, -9 found, +4 false |
| `min_width_px` 16 | 12.8: **+66 false boxes** (B 7 -> 64); 19.2: nothing |
| `min_stripe_px` 4 | 4.8: **+43 false boxes**; 3.2: nothing |
| `height_max` 1.5 | off: **+107 false boxes**, 23 on empty frames; 1.8: +1 |
| `close_px` 3 | 1 (no closing): -8 found; 5: +8 false, 1 on an empty frame |
| `stripe_h_min` 0.45 | 0.54: -7 found (2 on HOME + CAMPUS) |
| `bottom_tol` 0.15 | 0.18: -2 found, +6 false (2 on empty frames) |
| `stripe_h_max`, `band_h_max`, `width_min`, `stripe_w_min` | 1 to 4 barrels or false boxes each |
| `min_area_px`, `bottom_tol_min_px`, `width_max`, `split_search`, `height_min`, `body_min` (also off), `stripe_merge` -20 %, `pin_good` | nothing, or one frame |

Three thresholds sit right at a cliff on the false-box side (`min_width_px`, `min_stripe_px`, `height_max`), and none of the three was placed there on purpose (section 4c).

**The gate cannot see most of this.** HOME + CAMPUS is the protected set of the never-regress check. Flipping **23 of the 30 switches changes no box on A**; only 5 change A's score (`require_stripe`, `side_hidden`, `cap_behind`, `cap_seen_bottom`, `dark_stripe`). A rule can be added or removed without the gate noticing, which is how 14 simulation-only switches came to be on.

### 2.2 Tables

Baseline (defaults): A 63 found / 0 false on 37 frames; B 148 / 7 on 117; C 115 / 3 on 45; boxes on negative frames 0 / 0 / 0.

**Boolean switches, each flipped alone** (on -> off, or off -> on). found (+gained/-lost barrels) | false boxes (change) | boxes on negative frames | frames whose boxes changed.

| change | A found | A false | A neg | A frames | B found | B false | B neg | B frames | C found | C false | C neg | C frames | frames changed, all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `require_stripe` on->off | 33 (+0/-30) | 49 (+49) | 7 (+7) | 26 | 107 (+16/-57) | 532 (+525) | 91 (+91) | 108 | 80 (+10/-45) | 169 (+166) | 0 | 45 | 179 |
| `dark_stripe` off->ON | 63 | 5 (+5) | 3 (+3) | 11 | 167 (+22/-3) | 69 (+62) | 17 (+17) | 70 | 117 (+8/-6) | 25 (+22) | 0 | 31 | 112 |
| `side_hidden` on->off | 62 (+0/-1) | 0 | 0 | 11 | 140 (+0/-8) | 8 (+1) | 0 | 34 | 98 (+0/-17) | 7 (+4) | 0 | 28 | 73 |
| `stripe_join` on->off | 63 | 0 | 0 | 0 | 142 (+0/-6) | 7 | 0 | 12 | 115 | 3 | 0 | 3 | 15 |
| `slice_box` off->ON | 63 | 0 | 0 | 2 | 148 (+2/-2) | 9 (+2) | 0 | 7 | 115 | 4 (+1) | 0 | 3 | 12 |
| `cap_behind` on->off | 60 (+0/-3) | 0 | 0 | 3 | 146 (+0/-2) | 7 | 0 | 2 | 115 | 3 | 0 | 0 | 5 |
| `stripe_bridge` on->off | 63 | 0 | 0 | 0 | 146 (+0/-2) | 6 (-1) | 0 | 3 | 115 | 4 (+1) | 0 | 2 | 5 |
| `half_stripe` on->off | 63 | 0 | 0 | 0 | 146 (+0/-2) | 7 | 0 | 2 | 114 (+0/-1) | 2 (-1) | 0 | 2 | 4 |
| `stripe_wide` on->off | 63 | 0 | 0 | 1 | 147 (+0/-1) | 7 | 0 | 3 | 115 | 3 | 0 | 0 | 4 |
| `seam_height` on->off | 63 | 0 | 0 | 0 | 145 (+0/-3) | 7 | 0 | 3 | 115 | 3 | 0 | 0 | 3 |
| `pin_outline` on->off | 63 | 0 | 0 | 0 | 147 (+0/-1) | 7 | 0 | 2 | 115 | 3 | 0 | 1 | 3 |
| `verify_readings` on->off | 63 | 0 | 0 | 0 | 148 | 10 (+3) | 2 (+2) | 3 | 115 | 3 | 0 | 0 | 3 |
| `verify_front` on->off | 63 | 0 | 0 | 0 | 148 | 9 (+2) | 0 | 2 | 115 | 3 | 0 | 0 | 2 |
| `cap_seen_bottom` on->off | 62 (+0/-1) | 0 | 0 | 1 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 1 |
| `cover_rows` on->off | 63 | 0 | 0 | 0 | 148 | 6 (-1) | 0 | 1 | 115 | 3 | 0 | 0 | 1 |
| `half_thin` on->off | 63 | 0 | 0 | 0 | 147 (+0/-1) | 7 | 0 | 1 | 115 | 3 | 0 | 0 | 1 |
| `slice_behind` off->ON | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 4 (+1) | 0 | 1 | 1 |
| `closeup_stripe` on->off | 63 | 0 | 0 | 0 | 147 (+0/-1) | 7 | 0 | 1 | 115 | 3 | 0 | 0 | 1 |
| `pin_thin` on->off | 63 | 0 | 0 | 0 | 147 (+0/-1) | 7 | 0 | 1 | 115 | 3 | 0 | 0 | 1 |
| `thin_frame` on->off | 63 | 0 | 0 | 0 | 147 (+0/-1) | 7 | 0 | 1 | 115 | 3 | 0 | 0 | 1 |
| `closeup_side` on->off | 63 | 0 | 0 | 0 | 148 | 8 (+1) | 1 (+1) | 1 | 115 | 3 | 0 | 0 | 1 |
| `cap_same` on->off | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `stripe_two` off->ON | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `edge_check` on->off | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `occl_body_side` off->ON | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `cover_unpinned` off->ON | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `post_pair` on->off | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `cap_low` on->off | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `own_close` off->ON | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `thin_span` on->off | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `stripe_mode` cores->bands | 58 (+0/-5) | 4 (+4) | 2 (+2) | 16 | 121 (+6/-33) | 33 (+26) | 6 (+6) | 56 | 92 (+3/-26) | 8 (+5) | 0 | 35 | 107 |

**Groups**

| change | A found | A false | A neg | A frames | B found | B false | B neg | B frames | C found | C false | C neg | C frames | frames changed, all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_pin/thin(pin_outline,pin_thin,thin_span,thin_frame) | 63 | 0 | 0 | 0 | 147 (+0/-1) | 7 | 0 | 2 | 115 | 3 | 0 | 1 | 3 |
| no_half/post/wide | 63 | 0 | 0 | 1 | 145 (+0/-3) | 7 | 0 | 5 | 114 (+0/-1) | 2 (-1) | 0 | 2 | 8 |
| no_verify(front+readings) | 63 | 0 | 0 | 0 | 148 | 12 (+5) | 2 (+2) | 5 | 115 | 3 | 0 | 0 | 5 |
| detector_of_2026-11-18(all later switches off) | 61 (+0/-2) | 0 | 0 | 12 | 131 (+0/-17) | 10 (+3) | 1 (+1) | 39 | 96 (+0/-19) | 6 (+3) | 0 | 29 | 80 |
| detector_of_2026-11-09(hardening a-g only) | 59 (+0/-4) | 0 | 0 | 14 | 126 (+0/-22) | 10 (+3) | 1 (+1) | 42 | 94 (+0/-21) | 6 (+3) | 0 | 29 | 85 |
| step1_only(require_stripe off) | 33 (+0/-30) | 49 (+49) | 7 (+7) | 26 | 107 (+16/-57) | 532 (+525) | 91 (+91) | 108 | 80 (+10/-45) | 169 (+166) | 0 | 45 | 179 |
| no_caps(cap_behind) | 60 (+0/-3) | 0 | 0 | 3 | 146 (+0/-2) | 7 | 0 | 2 | 115 | 3 | 0 | 0 | 5 |
| no_closeup(side+stripe) | 63 | 0 | 0 | 0 | 147 (+0/-1) | 8 (+1) | 1 (+1) | 2 | 115 | 3 | 0 | 0 | 2 |
| no_join(stripe_join+bridge) | 63 | 0 | 0 | 0 | 142 (+0/-6) | 7 | 0 | 12 | 115 | 3 | 0 | 3 | 15 |
| scorecard_only_rules_off | 63 | 0 | 0 | 1 | 139 (+0/-9) | 6 (-1) | 0 | 13 | 114 (+0/-1) | 2 (-1) | 0 | 3 | 17 |

**Numeric thresholds, -20 % and +20 %** (and three 'off' values)

| change | A found | A false | A neg | A frames | B found | B false | B neg | B frames | C found | C false | C neg | C frames | frames changed, all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `min_area_px=16` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `min_area_px=24` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `close_px=1` | 63 | 0 | 0 | 0 | 144 (+0/-4) | 7 | 0 | 11 | 111 (+0/-4) | 4 (+1) | 0 | 5 | 16 |
| `close_px=5` | 63 | 1 (+1) | 0 | 4 | 149 (+1/-0) | 11 (+4) | 1 (+1) | 21 | 114 (+0/-1) | 6 (+3) | 0 | 7 | 32 |
| `bottom_tol=0.12` | 63 | 0 | 0 | 0 | 148 (+1/-1) | 7 | 0 | 8 | 115 (+1/-1) | 3 | 0 | 7 | 15 |
| `bottom_tol=0.18` | 62 (+0/-1) | 1 (+1) | 0 | 2 | 148 | 11 (+4) | 2 (+2) | 7 | 114 (+0/-1) | 4 (+1) | 0 | 2 | 11 |
| `bottom_tol_min_px=3` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `bottom_tol_min_px=5` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `width_max=1.28` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `width_max=1.92` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `width_min=0.32` | 63 | 1 (+1) | 0 | 1 | 149 (+1/-0) | 11 (+4) | 0 | 4 | 115 | 3 | 0 | 0 | 5 |
| `width_min=0.48` | 63 | 0 | 0 | 0 | 148 | 6 (-1) | 0 | 1 | 115 | 3 | 0 | 0 | 1 |
| `split_search=0.2` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `split_search=0.3` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `min_width_px=12.8` | 63 | 4 (+4) | 0 | 3 | 148 | 64 (+57) | 2 (+2) | 28 | 115 | 8 (+5) | 0 | 5 | 36 |
| `min_width_px=19.2` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `band_h_max=2.4` | 63 | 0 | 0 | 0 | 145 (+0/-3) | 8 (+1) | 0 | 8 | 115 | 4 (+1) | 0 | 2 | 10 |
| `band_h_max=3.6` | 63 | 0 | 0 | 0 | 148 | 8 (+1) | 0 | 3 | 115 | 4 (+1) | 0 | 3 | 6 |
| `stripe_w_min=0.32` | 63 | 0 | 0 | 0 | 149 (+1/-0) | 7 | 0 | 1 | 116 (+1/-0) | 3 | 0 | 1 | 2 |
| `stripe_w_min=0.48` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 113 (+0/-2) | 3 | 0 | 2 | 2 |
| `stripe_h_min=0.36` | 63 | 0 | 0 | 0 | 149 (+1/-0) | 7 | 0 | 1 | 115 | 3 | 0 | 0 | 1 |
| `stripe_h_min=0.54` | 61 (+0/-2) | 0 | 0 | 2 | 146 (+0/-2) | 7 | 0 | 2 | 112 (+0/-3) | 3 | 0 | 3 | 7 |
| `stripe_h_max=1.28` | 63 | 0 | 0 | 0 | 145 (+0/-3) | 6 (-1) | 0 | 4 | 115 (+1/-1) | 2 (-1) | 0 | 2 | 6 |
| `stripe_h_max=1.92` | 63 | 0 | 0 | 1 | 148 | 10 (+3) | 0 | 3 | 115 | 4 (+1) | 0 | 1 | 5 |
| `min_stripe_px=3.2` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `min_stripe_px=4.8` | 63 | 1 (+1) | 1 (+1) | 1 | 148 | 35 (+28) | 3 (+3) | 22 | 115 | 17 (+14) | 0 | 8 | 31 |
| `stripe_merge=1.12` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `stripe_merge=1.68` | 63 | 0 | 0 | 0 | 148 | 5 (-2) | 0 | 2 | 115 | 3 | 0 | 0 | 2 |
| `stripe_full=0.64` | 63 | 2 (+2) | 1 (+1) | 5 | 154 (+6/-0) | 8 (+1) | 0 | 18 | 115 | 4 (+1) | 0 | 14 | 37 |
| `stripe_full=0.96` | 62 (+0/-1) | 0 | 0 | 18 | 142 (+0/-6) | 7 | 0 | 36 | 111 (+0/-4) | 2 (-1) | 0 | 25 | 79 |
| `height_min=0.4` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `height_min=0.6` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `height_max=1.2` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `height_max=1.8` | 63 | 0 | 0 | 0 | 148 | 8 (+1) | 0 | 1 | 115 | 3 | 0 | 0 | 1 |
| `body_min=0.08` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `body_min=0.12` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `body_width=0.96` | 62 (+0/-1) | 1 (+1) | 0 | 15 | 145 (+0/-3) | 9 (+2) | 0 | 44 | 114 (+0/-1) | 3 | 0 | 27 | 86 |
| `body_width=1.44` | 63 | 0 | 0 | 5 | 149 (+2/-1) | 9 (+2) | 1 (+1) | 22 | 116 (+1/-0) | 3 | 0 | 14 | 41 |
| `pin_good=0.04` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 1 | 1 |
| `pin_good=0.06` | 63 | 0 | 0 | 1 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 1 | 2 |
| `body_min=0(off)` | 63 | 0 | 0 | 0 | 148 | 7 | 0 | 0 | 115 | 3 | 0 | 0 | 0 |
| `body_width=0(off)` | 62 (+0/-1) | 1 (+1) | 0 | 22 | 144 (+0/-4) | 10 (+3) | 0 | 54 | 111 (+0/-4) | 3 | 0 | 31 | 107 |
| `height_max=0(off)` | 63 | 7 (+7) | 0 | 5 | 148 | 105 (+98) | 23 (+23) | 29 | 115 | 5 (+2) | 0 | 2 | 36 |

Switches whose flip changes **no box on any of the 199 frame-runs**: 9 of 30: `cap_same`, `stripe_two`, `edge_check`, `occl_body_side`, `cover_unpinned`, `post_pair`, `cap_low`, `own_close`, `thin_span`. Of these, on by default: 5: `cap_same`, `edge_check`, `post_pair`, `cap_low`, `thin_span`.

Numeric changes with no box changed anywhere: 17: `min_area_px=16`, `min_area_px=24`, `bottom_tol_min_px=3`, `bottom_tol_min_px=5`, `width_max=1.28`, `width_max=1.92`, `split_search=0.2`, `split_search=0.3`, `min_width_px=19.2`, `min_stripe_px=3.2`, `stripe_merge=1.12`, `height_min=0.4`, `height_min=0.6`, `height_max=1.2`, `body_min=0.08`, `body_min=0.12`, `body_min=0(off)`.

**Greedy removal, newest switch first, keeping a switch off only if EVERY box on every frame stays identical:** removed 5 of 22: `thin_span`, `cap_low`, `post_pair`, `cap_same`, `edge_check`. Kept: `verify_readings`, `verify_front`, `closeup_stripe`, `closeup_side`, `thin_frame`, `stripe_bridge`, `pin_thin`, `pin_outline`, `stripe_wide`, `half_thin`, `half_stripe`, `cap_seen_bottom`, `seam_height`, `side_hidden`, `cap_behind`, `stripe_join`, `cover_rows`. Result: A 63 / 0, B 148 (+0/-0) / 7, C 115 (+0/-0) / 3; frames changed 0.

**Greedy removal, keeping a switch off if no found barrel is lost and no false box is added in any set:** removed 6 of 22: `thin_span`, `cap_low`, `post_pair`, `cap_same`, `edge_check`, `cover_rows`. Kept: `verify_readings`, `verify_front`, `closeup_stripe`, `closeup_side`, `thin_frame`, `stripe_bridge`, `pin_thin`, `pin_outline`, `stripe_wide`, `half_thin`, `half_stripe`, `cap_seen_bottom`, `seam_height`, `side_hidden`, `cap_behind`, `stripe_join`. Result: A 63 / 0, B 148 (+0/-0) / 6, C 115 (+0/-0) / 3; frames changed 1.

**Greedy removal, keeping a switch off if net found does not drop and false boxes do not rise in any set:** removed 6 of 22: `thin_span`, `cap_low`, `post_pair`, `cap_same`, `edge_check`, `cover_rows`. Kept: `verify_readings`, `verify_front`, `closeup_stripe`, `closeup_side`, `thin_frame`, `stripe_bridge`, `pin_thin`, `pin_outline`, `stripe_wide`, `half_thin`, `half_stripe`, `cap_seen_bottom`, `seam_height`, `side_hidden`, `cap_behind`, `stripe_join`. Result: A 63 / 0, B 148 (+0/-0) / 6, C 115 (+0/-0) / 3; frames changed 1.

**Pairs of on-switches turned off together: 231 pairs; 10 whose joint effect is not the sum of the two single effects.**

| pair | set | lost: both off vs union of singles | gained: both off vs union | false change: both off vs sum |
|---|---|---|---|---|
| `stripe_join` + `side_hidden` | B | 16 vs 14 | 0 vs 0 | +0 vs +1 |
| `stripe_join` + `side_hidden` | C | 19 vs 17 | 0 vs 0 | +4 vs +4 |
| `stripe_join` + `pin_outline` | B | 8 vs 7 | 0 vs 0 | +0 vs +0 |
| `stripe_join` + `pin_outline` | C | 1 vs 0 | 0 vs 0 | +0 vs +0 |
| `stripe_join` + `pin_thin` | B | 8 vs 7 | 0 vs 0 | +0 vs +0 |
| `stripe_join` + `pin_thin` | C | 1 vs 0 | 0 vs 0 | +0 vs +0 |
| `stripe_join` + `stripe_bridge` | B | 6 vs 6 | 0 vs 0 | +0 vs -1 |
| `stripe_join` + `stripe_bridge` | C | 0 vs 0 | 0 vs 0 | +0 vs +1 |
| `stripe_join` + `thin_span` | C | 1 vs 0 | 0 vs 0 | +0 vs +0 |
| `stripe_join` + `verify_readings` | B | 6 vs 6 | 0 vs 0 | +2 vs +3 |
| `cap_behind` + `side_hidden` | C | 18 vs 17 | 0 vs 0 | +4 vs +4 |
| `side_hidden` + `cap_same` | C | 18 vs 17 | 0 vs 0 | +4 vs +4 |
| `side_hidden` + `verify_readings` | B | 8 vs 8 | 0 vs 0 | +2 vs +4 |
| `seam_height` + `stripe_bridge` | C | 0 vs 0 | 0 vs 0 | +0 vs +1 |

## 3. Kill chain

### 3.1 What a clean, free-standing, fully visible barrel must pass to get a box

Colour step first (not the detector): for the body AND for the stripe, every pixel needs row >= 50, V >= 40, hue inside the class sector, S >= the class floor. Then, in order:

| # | test | where | kills when |
|---|---|---|---|
| 1 | stripe pixels survive the 3x3 close of both classes (`om = closed(other) & ~closed(body)`) | finder | a thin stripe is swallowed by the closed body |
| 2 | **sandwich**: body colour above AND below in the same column, within 3 stripe heights | finder | either body part is unpainted in the stripe's columns |
| 3 | pieces of the stripe join only if stripe-shaped or bridged | finder | a cut stripe stays in pieces |
| 4 | area >= 20 px | finder | `stripe:area` |
| 5 | its row gives a distance (below the horizon) | finder | `no_geometry` |
| 6 | expected W >= 16 px and stripe >= 4 px | finder | `too_far` (beyond 64 cm) |
| 7 | core height (10th-90th percentile rows) in 0.45-1.6 x expected | finder | `stripe:height` |
| 8 | width >= 0.45 stripe heights | finder | `stripe:width` |
| 9 | not wider than 1.4 W (or 1.2 W with body above and below): else cut into 2+ barrels | finder | a near barrel is split |
| 10 | if narrower than one stripe height: must be a full slice with exactly one "own" corner | stripe step | `slice_not_full`, `outline_unknown` |
| 11 | seen top and bottom vs predicted, 15 % / 4 px; both inferred and top against the other colour | stripe step | `top_against_barrel` |
| 12 | if stripe < 0.8 W: body span >= 0.8 W, or exactly one side with a reason, or exactly one own corner, or stripe >= 0.4 W | stripe step | `side_unexplained` |
| 13 | box at least 2 x 2 | stripe step | `empty_box` |
| 14 | body colour >= 10 % and >= stripe colour in the stripe's columns | stripe step | `body_min` |
| 15 | not IoU > 0.5 with a surer same-colour box | detect | `duplicate` |
| 16 | >= 20 evidence pixels not explained by a nearer kept barrel | verify | `verify:front` |
| 17 | if flagged occluded with both edges inferred: seen span >= 0.8 W | verify | `verify:readings` |
| 18 | scoring: IoU >= 0.5 and bottom within 10 % / 3 px | eval | box drawn but counted as a miss plus a false box |

Seventeen sequential tests, each a hard yes / no, each able to end the barrel. No test can make up for another. There is no path for "everything else fits perfectly but one test is marginal".

### 3.2 Recall on real train frames

| set | frames | barrels | clean (no label flag) found | flagged found | false boxes | on negative frames |
|---|---|---|---|---|---|---|
| A: HOME (leave one scene out) + CAMPUS | 37 | 64 | 51 of 51 | 12 of 13 | 0 | 0 |
| B: 15 non-extreme conditions, fixed model | 117 | 243 | **102 of 165 (62 %)** | 46 of 78 (59 %) | 7 | 0 |
| C: 45 slider frames, hand thresholds | 45 | 135 | **87 of 98 (89 %)** | 28 of 37 (76 %) | 3 | 0 |
| C: the same 45 frames, fixed model | 45 | 135 | 51 of 98 (52 %) | 18 of 37 | 8 | 0 |

Baseline reproduced exactly: HOME 28 of 29 (leave one scene out; the stored model gives the same 28), CAMPUS 35 of 35, no false box.

Caveat on C: the slider tool shows the detector's boxes live while the thresholds are set, and the labelling criterion is "as much barrel painted as needed to detect it". The C thresholds are therefore tuned *to this detector*, frame by frame. 89 % is an upper bound for "good colour", not a neutral one.

### 3.3 Attribution of every missed clean barrel

"Painted" is measured inside the hand box. Reference: the 51 clean barrels found on A have body colour on a median 0.57 of the box (5th percentile 0.49) and stripe colour on 0.16 (5th percentile 0.085). "Not painted" = under a quarter of the median (body < 0.14, stripe < 0.04 or < 20 px). "Partly" = above that, under the 5th percentile. The killing test is read from `detect(..., log=[])`.

**Set B, fixed model: 63 clean barrels missed**

| paint state | n | killed by (reason log) |
|---|---|---|
| body not painted | 29 | no candidate at all, stripe pixels have no body above / below (the sandwich, test 2): 15; `stripe:width` 4; `stripe:area` 4; `cap:*` 4; `stripe:height` 1; `slice_not_full` 1 |
| stripe not painted | 28 | `stripe:area` 13; `cap:width` 4; `stripe:height` 3; `cap:not_hidden` 3; `cap:narrow` 3; no stripe pixel 2 |
| partly painted | 6 | `stripe:height` 3; `stripe:area` 2; `slice_not_full` 1 |
| well painted | 0 | |

By condition: bathroom tile warm 6 / mid 6 / mid 3: 12 each; ottoman warm 6: 10, cool 6: 7, mid 6: 4; gray table: 5; bathroom cool 6: 1.

**Set C, hand thresholds: 11 clean barrels missed** (6 on `lampmid3_ottoman`, 5 on `lampwarm6_bathtile`)

| paint state | n | killed by |
|---|---|---|
| body not painted | 5 | `stripe:width` 3; `cap:width` 1; no sandwich 1 |
| stripe not painted | 5 | `stripe:area` 3; `cap:not_hidden` 2 |
| partly painted | 1 | a box was drawn (IoU 0.70) with the bottom 12 px short |

**Headline.** Not painted by the colour step: **57 of 63** on B, **10 of 11** on C. Painted and then refused by a detector test: **6 of 63** on B, **1 of 11** on C. No well-painted clean barrel was refused on any real train frame. On real frames the rule list is not what loses clean barrels; the colour step is.

But read the middle rows again, because that is where the detector's design shows:

- **49 of the 63** missed clean barrels on B have ONE of the two colours at full strength: 23 have the body painted (>= 0.3 of the box) and no stripe; 26 have the stripe painted at full strength (>= 0.085) and no body. In the picture each is a barrel-shaped, barrel-sized thing at the right row. The detector needs both colours, in the same columns, touching. Half the evidence scores zero.
- In those 63, the unpainted part was mostly just under the threshold. With the thresholds loosened (hue +-6, S -40, V >= 25) the painted share of the body region goes from a median 0.37 to 0.81 and of the stripe region from 0.09 to 0.62. The image had the evidence; the hard mask rounded it to nothing before the detector saw it. (On C this does not help: 0.41 -> 0.50 and 0.49 -> 0.59. There the hand thresholds are already at the limit: blue reads gray under the warm lamp, and `lampmid3_ottoman` is nearly black.)
- Seen by eye (`work_detector/viz/c_hand_miss.png`): `lampwarm6_bathtile_core_01` has three barrels each with a clean orange band of exactly stripe size at exactly the right row, and a clear dark body around it. `lampmid3_ottoman_core_01` has orange bodies in two pieces with a gap of exactly one stripe height between them. A person boxes all of them in a second. The detector's answers: `stripe:width`, `cap:not_hidden`.

### 3.4 The real occlusion frames (ABP white table, `occlx_*`, 17 train frames)

The only real occlusion set. Colour is fine there (clean barrels 17 of 17). Flagged barrels: **9 of 15 found**. The six misses:

| frame | scene | reason log |
|---|---|---|
| `occlx_02` | half behind a black box, straight edge | `outline_unknown` |
| `occlx_03` | half behind the box, other side | `side_unexplained` |
| `occlx_06` | lower third behind a low notebook | `slice_not_full` |
| `occlx_14` | at the frame edge | `slice_not_full` |
| `occlx_10` | same-colour barrel straight in front | one box around both, 1.45 x too wide, 1.58 x too tall, **no flag set** |
| `occlx_19` | behind a book with a blue cover | `cap:width` (the book is "blue barrel colour") |

The simulated scorecard says "a straight upright edge, half hidden: 90 of 100". The two real straight-edge frames are both missed. In `occlx_02` and `occlx_03` the mask shows a clean half barrel with a ruler-straight cut; the black box that cuts it is, to the detector, table.

### 3.5 What the false boxes are (B + C: 10)

| what | n |
|---|---|
| a box on a real barrel, misplaced or with the bottom wrong (partly-seen path 4, half-stripe 1, whole stripe 1) | 6 |
| a box of the wrong colour on a real barrel (blue barrel's top read as an orange barrel's stripe) | 1 |
| a "close-up" box on a fragment of a fully visible barrel (ottoman `core_01`) | 1 |
| a "close-up" box 330 px wide on wood-grain speckle (palewood `core_01`) | 1 |
| a whole-stripe box on a jar with an orange and blue label (glass `occl_02`) | 1 |

Eight of ten sit on a real barrel. The detector's false boxes are mostly its own geometric guesses landing in the wrong place, not things that look like barrels.

### 3.6 Which rule actually draws the boxes on real frames

| route | A (63 found) | B (148) | C (115) |
|---|---|---|---|
| stripe seen whole | 40 | 91 | 70 |
| stripe partly seen (`side_hidden` and its branches) | 15 | 41 | 44 |
| stripeless close-up piece | 5 | 12 | 0 |
| `cap_behind` | 3 | 2 | 0 |
| `half_stripe` | 0 | 2 | 1 (+1 false) |
| `post_pair` | 0 | 0 | 0 |
| `pin_outline` (calls / placed a box) | 3 / 0 | 14 / 1 | 8 / 1 |

- The "partly seen" occlusion path boxes **8 of 51, 17 of 102 and 25 of 87 clean, unoccluded barrels**. Its real job on real frames is repairing stripes the colour step left narrow, not occlusion. Those barrels come out flagged `occluded` with a side that was guessed.
- On found clean barrels the geometry overruled a seen top or bottom in 6 of 51 (A), 26 of 102 (B), 9 of 87 (C).

## 4. Brittleness probes (real train frames; A = 37 frames / 64 barrels, B = 117 / 243, C = 45 / 135)

Baseline: A 63 found, 0 false; B 148, 7; C 115, 3; no box on a negative frame. Cells: found (+gained / -lost against the baseline), false boxes, [boxes on negative frames if any].

### 4a. Camera constants

| change | A | B | C |
|---|---|---|---|
| tilt -0.9 deg | 61 (+0/-2), 0 | 149 (+5/-4), 16 [1] | 113 (+2/-4), 7 |
| tilt -0.6 | 61 (+0/-2), 0 | 148 (+3/-3), 13 | 113 (+1/-3), 7 |
| tilt -0.3 | 63 (+0/-0), 0 | 147 (+1/-2), 10 | 113 (+1/-3), 6 |
| **baseline 22.25** | 63, 0 | 148, 7 | 115, 3 |
| tilt +0.3 | 62 (+0/-1), 0 | 145 (+0/-3), 7 | 113 (+0/-2), 4 |
| tilt +0.6 | 61 (+0/-2), 0 | 143 (+0/-5), 6 | 114 (+1/-2), 7 |
| tilt +0.9 | 61 (+0/-2), 0 | 142 (+1/-7), 7 | 108 (+1/-8), 6 |
| height -2 mm | 62 (+0/-1), 0 | 144 (+1/-5), 7 | 115 (+2/-2), 3 |
| height +2 mm | 61 (+0/-2), 1 | 146 (+3/-5), 16 [1] | 113 (+1/-3), 7 |
| f -20 px (5 %) | 61 (+0/-2), 0 | 148 (+6/-6), 15 [1] | 113 (+3/-5), 7 |
| f +20 px | 60 (+0/-3), 1 | 138 (+1/-11), 10 | 105 (+2/-12), 8 |

- Found counts move by 1 to 3 % per 0.3 deg; the churn is larger than the net (B at -0.9: five barrels gained, four lost).
- **False boxes are the sensitive side**: B goes 7 -> 10 -> 13 -> 16 as the tilt drops by 0.3, 0.6, 0.9 deg, and +2 mm of camera height doubles them (7 -> 16) and puts a box on an empty frame. C's false boxes double at -0.3 deg (3 -> 6).
- No single tilt is best. Found per place as the tilt moves (-0.9 ... +0.9): HOME 26, 26, 28, **28**, 27, 27, 27; ABP white 27, 27, 27, **26**, 26, 25, 24; bathroom (hand thresholds) 27, 28, 28, **29**, 27, 27, 26; ottoman (hand) 23, 23, 23, **25**, 25, 26, 26; pale wood (hand) 9, 8, 8, **7**, 7, 7, 7; glass (hand) 45 until +0.9, then 40.
- From the hand boxes alone (no colour, no detector; 366 clean barrels): the bottom predicted from the labelled top row is a median **+4.0 px** too low; the best-fit tilt offset per place is -0.70 (wood), -0.50 (bathroom), -0.45 (HOME), -0.35 (CAMPUS), -0.40 (gray), -0.20 (pale wood), -0.15 (ottoman), +0.10 (glass, black), +0.20 (ABP white). A spread of 0.9 deg. With the default camera, **15 % of perfectly labelled barrels have a true bottom outside the detector's own "agrees" tolerance** (so a correct seen bottom is overruled), and for **37 %** the bottom the geometry would draw instead is outside the scorer's tolerance.
- What 0.3 deg is worth, analytically: 2.2 px of row at every distance; that reads as a size error of 3 % at 20 cm, 5 % at 30 cm, 8 % at 50 cm, 10 % at 60 cm. At 40 cm the stripe is 6.8 px tall and its floor (0.45 x) is 3.0 px; the edge tolerance is 4.2 px. The far half of the table runs on 2 to 4 pixel margins while the camera uncertainty is 2 px.

### 4b. Mask perturbation and non-monotonicity

| change to the class mask | A | B | C | frames whose boxes change |
|---|---|---|---|---|
| **erode by 1 px** | **51 (+0/-12)**, 2 | **121 (+2/-29)**, 1 | **86 (+2/-31)**, 7 | 31 / 73 / 41 |
| **dilate by 1 px** (strictly more paint) | 62 (+0/-1), 3 | 155 (+10/-3), 23 [3] | 113 (+4/-6), 13 | 31 / 79 / 42 |
| S floor -20 (strict superset; 9-12 % more paint) | 62 (+0/-1), 3 | 147 (+6/-7), 21 [3] | 115 (+2/-2), 7 | 31 / 72 / 38 |
| hue +-3 (superset; 6-29 % more) | 63 (+0/-0), 0 | 167 (+21/-2), 15 [3] | 111 (+0/-4), 5 | 13 / 48 / 26 |
| S -20 and hue +-3 (19-54 % more) | 61 (+0/-2), 3 | 174 (+31/-5), 24 [4] | 109 (+2/-8), 12 | 31 / 86 / 40 |
| S -40 and hue +-6 (1.7-2.8 x) | 59 (+0/-4), 7 [1] | 158 (+31/-21), 80 [19] | 102 (+1/-14), 29 | 32 / 103 / 40 |
| S floor +20 (strict subset) | 60 (+0/-3), 1 | 143 (+2/-7), 5 | 107 (+1/-9), 7 | 30 / 68 / 38 |

(Home is segmented with the stored model in the three S / hue rows; same 28 of 29 as leave-one-scene-out.)

- **One pixel of erosion removes 19 % of the found barrels on HOME + CAMPUS (63 -> 51), 18 % on B, 25 % on C.** Through: `stripe:height` 31, `stripe:area` 15, a box with the bottom now off 5, `cap:*` 6, `stripe:width` 3, `verify:readings` 3, others 9. The published 28 of 29 and 35 of 35 sit one pixel from 51 of 64.
- **More paint loses found barrels.** With every base pixel kept and paint only added: dilation loses 10 found barrels (1 + 3 + 6), S -20 loses 10 (1 + 7 + 2), hue +-3 loses 6, both lose 15, the larger step 39. That is 2 to 5 % of the found barrels per small step, and on C (the hand-set thresholds) the losses equal or outnumber the gains in every row. Through which test: **the box is still drawn but its bottom moved outside the scorer's tolerance** (extra paint under the base is "a seen bottom that agrees", 15 %, while the scorer wants 10 %): 8 of 10 for dilation, 6 of 10 for S -20, 6 of 15 for both; then `stripe:height` (the stripe got fatter or was eaten by body paint), `verify:readings`, `side_unexplained`, `slice_not_full`, `top_against_barrel`.
- **More paint buys false boxes fast**: B 7 -> 21 (S -20), -> 23 (dilate 1 px), -> 80 with 19 on empty frames (S -40, hue +-6).
- **The hand thresholds sit on a knife edge.** On C, S -20 changes four barrels (+2/-2) and adds 4 false boxes; S +20 loses 9. The labeller found a point; there is no plateau around it. This is also the honest reading of "the detector finds 89 % given good colour": given colour tuned frame by frame to this detector, within about +-20 of saturation.
- Almost every frame's boxes change under every perturbation (31 of 37 on A for one pixel either way). The answer is not stable; the score is.
- **Mirror test** (flip the mask left-right, detect, flip the boxes back; the camera model is symmetric): boxes differ on 1 / 3 / 2 frames; on B one more barrel found and one more false box, on C one barrel lost. The left-to-right greedy joins are visible in the output, though small.
- **Order test** (the finder's stripes handed to `detect` in reverse): no box changes on any frame.

### 4c. Duplicated logic: the same idea, encoded several times with different constants

| idea | encodings |
|---|---|
| **"wider than one barrel"** | `round(width / W) >= 2`, i.e. 1.5 W (`split_blob`); `width_max` 1.6 W (pieces); `stripe_merge` 1.4 W (stripe region); `body_width` 1.2 x `W_two` (`stripe_wide`, `stripe_two`); `body_width` 1.2 W (caps, joins, "trusted" body, pairs, half stripes). Four constants: 1.2, 1.4, 1.5, 1.6 |
| **"too narrow to be whole"** | `width_min` 0.4 W (pieces, caps); `stripe_w_min` 0.4 W (stripes; same value, separate knob); `stripe_full` 0.8 W (partly seen); 0.45 x stripe height and 1 x stripe height (the two finder floors); "taller than wide" |
| **"the seen edge agrees with the prediction"** | `bottom_tol` 15 % of H, min 4 px (step 1, stripe step, caps, full slice, half stripe, close-up); the same number times **W** for a horizontal test in `_partly_seen`; `pin_good` 5 % of H for the outline; `CLOSE_CUT` 10 % of H and `bottom_tol` again for `own_close`; and the scorer's 10 % / 3 px. A box the detector calls "agrees" can be outside what the scorer accepts |
| **"this edge ends against something"** | `edge_check`: other colour in >= half the columns of the 4 rows beyond; `_full_slice`: the same, both ends; `half_stripes`: any barrel colour, same 4 rows / half; `_closed_end.seen_edge`: any barrel colour in under half the rows of `close_px` columns; `_partly_seen.nearer`: a found box holds one of `close_px` pixels; `caps_behind.hidden`: a found box holds the 1 pixel beside; old side rule: the mask pixel at x0 - 1. Seven implementations |
| **"a barrel standing nearer"** | found box bottom > this barrel's *predicted* bottom (`_partly_seen`, `slices_behind`); > the cap's *seen* bottom (`caps_behind.hidden`); > the cap box's *drawn* bottom (`caps_behind` test 3); > the other box's bottom, strictly (`verify_front`). Four definitions of depth order |
| **"the same rows"** | overlap >= half the shorter height (`_join_shaped`, `_join_bridged`, `_piece_of_found`, `post_pairs`); middles within half a stripe height (`_join_bridged` round 2); any overlap at all (`cover_rows`) |
| **"this is the same barrel as that one"** | IoU > 0.5, same colour: 7 places (`detect` twice, caps, pairs, slices, half stripes, the pin fallback); x-overlap > 0.3 plus shared rows (stripeless pieces); half the pixels inside found boxes (caps, half stripes); stripe middle inside a found box at its stripe rows (`_piece_of_found`); `stencil.same_barrel` (a fifth). Two boxes at IoU 0.45 on one barrel pass all of them: `lampmid6_glass_clutter_01` gets two orange boxes on one orange barrel |
| **"distance of this barrel"** | from the top row (step 1, caps, close-ups); from the stripe's middle row (stripe step); from a seam row (half stripes); from the width (cap bottoms, `outline_layout`); from the bottom row (expected width in step 1). Five estimators. No rule combines two into one estimate; each picks one and uses another as a veto. With the camera bias of section 4a they disagree by a median 4 px even on perfect hand boxes |
| **"the body joined to the stripe"** | `_body_extent` (rows; gaps of 3), `_body_columns` (columns outward; gaps of 2; capped), `_body_span` (columns as runs; gaps of 2; may stop short), `_seen_lines` (per-column rows; gaps of 3; clipped), `_end_closure` (per-column first / last body pixel). Five walkers over the same pixels |
| **"a stripe in pieces is one stripe"** | `stripe_join`, `stripe_bridge`, `_piece_of_found`, `post_pair`, `half_stripes`' corner replacement |
| **"where the hidden side is"** | old rule (barrel pixel beside), `occl_body_side`, `side_hidden` (a)(b)(c), `pin_outline`, `own_close`, `thin_frame`, `slice_behind`, `stripe_wide`'s cut side, the cap's `hidden()`. Nine |
| **the stripe finder itself** | `_find_stripes_cores` and `_find_stripes_bands` (kept "for comparison"), and `half_stripes` re-implements the sandwich one-sided |
| **the outline** | `Outline` (analytic), `outline_layout` (the same, rescaled to a box), `stencil.render` (fit on HOME masks: `rim`, `rim_top`, `rim_bottom`). Two of the three were fit or designed separately and predict different corners |

Dead or unreachable at the default settings (verified):

- **The "too far to resolve a stripe" branch of stage 4** (`hs < min_stripe_px`) cannot accept a real far barrel. A stripe under 4 px needs a barrel beyond 688 mm; `min_width_px` already refuses everything beyond 638 mm; no image row satisfies both (checked for every row). The branch can fire only because it reads the stripe height at the piece's *middle* row and the width at its *bottom* row, i.e. only for a piece that is too tall for its row: a non-barrel. At the defaults it never fires on a real frame (of the 19 stripeless pieces kept, 18 reach the frame bottom and 1 is a `closeup_stripe` piece). Nudge a neighbouring constant and it does: `min_stripe_px` 4 -> 4.8 gives +43 false boxes (A 1, B 28, C 14).
- **`height_min` / `height_max`** (hardening d, written for a blue jacket at the far end) now do a job nobody assigned them: they are the only thing holding back that branch and `closeup_stripe`. With `height_max` off, B goes from 7 to 105 false boxes, 23 on empty frames (77 with `closeup_stripe` also off).
- **`body_min`** (hardening c): at 0.08, 0.12 and switched off it changes no box on any of the 199 frame-runs.
- **`occl_body_side`**: read only in the branch taken when `side_hidden` is off.
- **`cover_unpinned`**, **`stripe_two`**, **`slice_box`**, **`slice_behind`**, **`own_close`**, **`dark_stripe`**: off, with their code still interleaved in the live path (`slices_behind`, `_end_closure`, `_closed_end`, the cover-box and `stripe_two` branches, the dark-gap candidate, the pre-`side_hidden` side rule, and the whole `bands` finder: roughly 200 of the 1900 lines).

One more thing that is not a duplicate but a hazard: the reason log's docstring says "the answer never depends on it", and since 2026-11-24 it does. `verify_front` and `verify_readings` find a box's evidence by searching the log for a "kept" entry whose box tuple equals the box (`_evidence`), and silently fall back to the whole box when none matches. Diagnostics became control flow, joined by tuple equality.

## 5. Design critique

### 5a. Naive or wrong assumptions baked into the rules

| # | assumption (rule) | a real scene that breaks it | measured |
|---|---|---|---|
| 1 | **Both colours must be painted, in the same columns, touching** (the sandwich in `_find_stripes_cores`). A barrel is defined as stripe-between-body, so a barrel with one colour lost does not exist. | Warm lamp on bathroom tile: orange stripes are perfect bands, the blue body reads gray. Dark ottoman: orange bodies in two pieces with a stripe-sized gap, blue stripe unpainted. | 49 of the 63 clean barrels missed on B have one colour at full strength and the other missing; 10 of 11 on C |
| 2 | **Unpainted = empty table.** Every occlusion rule that asks "is there a reason for this side to be hidden" can only accept the frame edge or an already-found barrel as a reason. | A barrel half behind a black box (`occlx_02`, `occlx_03`), behind a notebook (`occlx_06`), behind a book (`occlx_19`). | real occluded barrels on the ABP set: 9 of 15; both straight-edge frames missed while the scorecard says 90 of 100 |
| 3 | **A narrow stripe means an occluded barrel** (`stripe_full` 0.8 -> `side_hidden`). | Any stripe the colour step leaves short: a highlight, a dark end, a warm cast. | 8 of 51 (A), 17 of 102 (B), 25 of 87 (C) clean barrels are boxed through the occlusion path and flagged `occluded`; 5 of the 10 false boxes on B + C come from it |
| 4 | **A stripe proves a barrel** (step 4's premise: other colour sandwiched at the right scale). | A jar with an orange lid and a blue label on glass (`lampmid3_glass_occl_02`: whole-stripe box on no barrel). A blue barrel's top between orange things: read as an orange barrel's stripe (`palewood_clutter_01`: orange box on a blue barrel). | 2 of 10 false boxes; `verify_front` and `body_min` exist only to patch this |
| 5 | **The top row of a piece is the top of a barrel**, so it gives the distance (step 1 bottoms, caps, close-ups). | The lower-body fragment of a fully visible, over-exposed barrel on the ottoman (`lampwarm6_ottoman_core_01`): its top row "predicts" a base below the frame, so it becomes a "close-up" box running to the frame bottom. A hand above a barrel. | bottom predicted from the *hand-labelled* top row of 366 clean barrels: median +4.0 px low; outside the detector's own tolerance for 15 %, outside the scorer's for 37 % |
| 6 | **A piece that reaches the frame bottom and is barrel-wide is a close barrel** (stage 4). No test of how full the box is. | Wood grain at the bottom of the pale wood table: a 330 px wide speckle field gets a box (`palewood_core_01`). | fill of the box: the 17 true close-up pieces 0.64-0.88; the 2 false ones 0.10 and 0.28. One number separates all 19 and is not looked at |
| 7 | **The camera pose is one fixed number.** Every size test hangs on tilt 22.25 deg. | The robot pitches when it starts or stops; another robot; a table that is not level; a session where the head sits 0.3 deg differently. | best-fit tilt per place from the labels: -0.70 (wood) to +0.20 (ABP white), a spread of 0.9 deg; 0.3 deg = 2.2 px of row = 5 % size error at 30 cm, 10 % at 60 cm; see section 4a |
| 8 | **Barrels stand upright on the table plane.** Row -> distance -> size is the only size model. | A barrel held by the gripper or lifted (`held` is a label flag: it happens), on its side, on a book, on a second level. | the `held` frames are found only as frame-bottom close-ups |
| 9 | **A seen edge within 15 % of the prediction is this barrel's edge.** | A same-colour barrel standing right behind: its top is 12 px above the front barrel's and inside the tolerance band around the predicted top, so it becomes the front barrel's top (`occlx_10`). One box around both, 1.58 x a barrel tall, **no flag**, counted as a hit; the back barrel is lost silently. | 1 of 15 real occluded barrels |
| 10 | **"Nearer" = lower bottom edge of the box**, with four different comparisons in four rules, on bottoms that are themselves often inferred. | Any barrel whose bottom was replaced by the prediction (26 of 102 clean barrels on B had an edge overruled). | not isolated |
| 11 | **Two barrels cannot both have a stripe inside one barrel width at the same rows** (`stripe_join`, `stripe_bridge`, `_piece_of_found`, `post_pair`). True for equal distance; "same rows" is "overlap of half the shorter", so two barrels 1/4 of a barrel apart in depth qualify. | Barrels in a tight bunch, one slightly behind. | not isolated on real frames |
| 12 | **Confidence means something.** Duplicates are resolved by `0.5 + 0.5 x labelled share of the stripe box`; every occlusion rule returns exactly 0.5. | Two candidate boxes for one barrel, the wrong one has the cleaner stripe. | no score reaches the tracker or the user |

### 5b. Information the detector throws away, and what it then has to guess

The detector's whole input is a 640 x 480 array of {0, 1, 2}. Everything else in the photo is gone before the first rule runs.

| thrown away | the guess it forces | rules that exist only to make that guess |
|---|---|---|
| **How close a pixel was to the threshold.** A stripe pixel with S = 110 against a floor of 113 is the same as bare table. | Whether a stripe-sized gap between two body parts is a stripe. | `dark_stripe` (off: it boxed wall gaps), `seam_height`, `stripe_join`, `stripe_bridge`, `stripe_h_min`. Measured: on the 63 clean misses of B the stripe region is painted 0.09 (median) and 0.62 once the thresholds are loosened; body 0.37 -> 0.81 |
| **Whether an unpainted pixel is table or a thing.** A black box, a notebook, a hand, a post are all 0. | Which side of a partly seen barrel is hidden, and whether anything hides it at all. | `side_hidden` reasons (a), (b), (c); `pin_outline`; `pin_thin`; `thin_span`; `thin_frame`; `own_close`; `slice_box`; `cover_unpinned`; `slice_behind`; `post_pair`; `half_stripe`; `half_thin`; `verify_readings`. Thirteen switches for one missing bit |
| **Edges.** The barrel's outline against the table is in the image even when its colour fails (dark ottoman, warm lamp). | Where the top, the bottom and the sides are. Read from paint with 3-row and 2-column gap walks, then overruled by the geometry when they disagree. | `resolve_bottom`, `_body_extent`, `_body_columns`, `body_width`, `edge_check`, `cap_seen_bottom`. On B an edge was overruled on 26 of 102 found clean barrels |
| **The occluder's own edge.** A cut by a box is a long straight intensity edge with a different surface on one side; a barrel's own side is a curved edge with table beyond. | Own side or cut side. | `pin_outline` reads it from the rounding of the *painted* corners: 1 to 3 px on a 50 px barrel, threshold 0.05 H = 2.7 rows. On real frames it was called 25 times and placed 2 boxes |
| **Texture and solidity.** A barrel face is a filled, smooth region; wood grain is speckle. | Whether a wide blob at the frame bottom is a close barrel. | `closeup_side`, `height_min / max`; nothing catches the wood grain |
| **Brightness structure**: highlight on the lid, shadow under the base, mirror image on glass. | Whether a hole in the body is a highlight or occlusion; whether colour below the base is the barrel. | bottoms inferred; `stripe_join` |
| **Any graded output.** The detector emits boxes, not scores. | The tracker (3 of 4 frames) and the user cannot tell a 17-test pass from a guessed side. | flags only |

The project knows the first two rows. The stencil verdict says "in the mask a thing that hides a barrel looks like bare table ... the gray image can in principle" and files it as "lead, not built". The stencil PREREG said it on 2026-11-19. Sixteen of the 30 switches are dated 2026-11-20 or later, all on the mask side of that wall.

### 5c. Structural smell

**Is it a decision list patched case by case?** Yes, and the file says so: its docstring is a changelog of 14 dated layers in three weeks; "round 2" appears 14 times in the code as the marker of an exception added after a rule misfired; almost every switch names the frame or the scorecard cell it was written for. Measured:

- The rules are additive and narrow: 221 of 231 switch pairs do not interact at all (section 2). Each rule owns a few frames. A model generalises; a list of exceptions does not.
- 17 of 30 switches change at most one real frame-run of 199. 9 change none.
- The acceptance procedure is a ratchet. A rule gets in if it finds more scorecard cells and does not move HOME + CAMPUS; the gate set is blind to 23 of 30 switches; nothing is ever removed. Two switches (`stripe_bridge`, `thin_frame`) failed the rule written for them and were switched on anyway.

**Rules whose only evidence is the simulated scorecard.** 14 of the 23 that are on. On real frames 5 of them do nothing, and 13 of them together find 10 barrels and add 2 false boxes. The simulator and reality disagree where it can be checked: the scorecard says 90 of 100 for a straight edge hiding half; the two real frames of that kind are both missed; real occluded barrels on the one real occlusion set are 9 of 15. The scorecard erases or pastes mask pixels on barrels cut from the frames the rules were tuned on; a real occluder also changes exposure, casts a shadow, and (the book in `occlx_19`) can be barrel-coloured itself.

**Is rule order doing hidden work?** Less than I expected in one sense, more in another.
- Stripe processing order: handing the stripes to `detect` in reverse changes no box on any frame. A left-right mirror of the mask changes 6 of 199 frames. So the ordering inside the stripe step is not fragile.
- The hidden work is done by *shared constants and stage order*, not stripe order:
  - `height_max`, written on 2026-11-08 for a jacket, is today the only guard on `closeup_stripe` (2026-11-23) and on the far branch. Off: B 7 -> 105 false boxes.
  - `min_width_px` 16 and `min_stripe_px` 4 are set so that one silences the other's branch; +20 % on the second re-opens it: +43 false boxes.
  - `cover_rows` (2026-11-09) removed a columns-only test that had been hiding false close-up pieces "by accident" (the docs' own words for the v1 front end); on today's frames the accident would still remove one.
  - `stripe_full` 0.8 is read in 16 places; +-20 % changes 37 and 79 frames.
  - `cap_low` uses `width_min` as a height floor because the number happened to be 0.4.
  - `verify_front` runs twice so that caps lean only on verified boxes and a cap can replace a dropped stripe box; `half_stripes` may replace a stage-3 box; the pin fallback re-runs `barrel_from_stripe` with two switches forced off. Each is an order dependency written as a comment.
  - The verify step reads the *diagnostic log* to find each box's evidence.

**Verify steps are a tell.** `verify_front` and `verify_readings` are a second pass that deletes boxes the first pass should not have made. They work (5 false boxes fewer on B, 2 on empty frames, nothing lost). They are also an admission that acceptance is decided in nine separate places with nine separate ideas of "enough".

### 5d. What could replace most of the list

**One formulation: hypothesise, render, score.**

1. *Hypotheses from the geometry.* A barrel is (ground position x, y; colour). The camera turns that into a full outline, stripe band included. This is what `Outline`, `outline_layout` and `stencil.py` already compute; the rules compute pieces of it six times over (`barrel_rows` from a top row, a stripe row, a seam, a width, a bottom row).
2. *One continuous score per hypothesis*, a sum of evidence terms, each graded, none a veto: body colour likelihood in the body regions, stripe colour likelihood in the stripe band (soft, from distance to the colour model, not the 0 / 1 mask), an edge term along the predicted outline, a penalty for the wrong colour inside and for the same colour continuing outside.
3. *Visibility by depth order, not by rule.* Sort hypotheses near to far. A pixel covered by an accepted nearer barrel, or outside the frame, is "explained: not expected to show" and drops out of the farther barrel's score. That one mechanism is `cap_behind`, `cap_same`, `cap_low`, `cap_seen_bottom`, `verify_front`, `thin_frame`, reason (a) and reason (b) of `side_hidden`, and "the frame edge counts as a hidden side".
4. *A non-barrel occluder is a third pixel state*, "something else is here", from the image: not table-like, not barrel-coloured, with an edge at the cut. Then "hidden" and "absent" differ, and `side_hidden` (c), `pin_outline`, `pin_thin`, `thin_span`, `post_pair`, `half_stripe`, `half_thin`, `edge_check`, `verify_readings` reduce to: score the visible part, require that the missing part is explained.
5. *Uncertain pose as a search range*, not a constant: let each hypothesis slide a few rows (the stencil's `dy_range`) or fit one tilt offset per frame from the confident barrels.
6. Accept by one threshold; non-maximum suppression replaces the seven "IoU > 0.5 is a duplicate" checks. The score is the confidence the tracker lacks.

A second, smaller formulation if the first is too big a step: keep the stripe as the proposal generator, but make everything after the proposal a single graded verification of the full-barrel hypothesis (the same score as above), instead of seventeen vetoes plus thirteen rescue branches.

**Was the stencil experiment a fair trial of this idea?** It was a fair and correct rejection of *that stencil as a drop-in replacement*. I re-ran it, untouched and with its calibrated numbers, on the real sets it never saw (they were shot after 2026-11-20):

| | rules | stencil alone | rules + stencil (`union1`) |
|---|---|---|---|
| A (64 barrels) | 63 found, 0 false | 58, 1 | 63, 0 |
| B (243) | 148, 7 | 108, 10 | 148, 7 |
| C (135) | 115, 3 | 96, 3 | 116, 3 |

So the ranking holds on real frames, and the union adds one barrel in 442. But as a trial of the *idea* it was not fair, for reasons that are in its own pre-registration:

1. **Same starved input.** It scored the same hard mask. Its PREREG states before any run that "the mask cannot tell hidden from absent" and lists reading the gray image under "Not built". It tested a second way of reading the mask and found the mask's ceiling.
2. **Its score was a veto in disguise.** A column is worth its *worst* band (a `min`), so one highlight on the lid zeroes every column under it. That is the sequential-kill structure of the rules again, and it is the whole "medium damage 37 vs 99" loss. The softer variant was dropped after one calibration pass.
3. **Operating point chosen for zero false boxes on HOME's own masks, plus a margin**, then judged on recall.
4. **Judged by never-regress against rules that had been iterated on those same frames** to 28 of 29 and 35 of 35, and on a scorecard the rules had been tuned against for many rounds; the stencil got four numbers, HOME-only calibration and "at most two rounds".
5. **The damage level that sank it is one the docs call "far harsher than anything measured"**; on stripe damage, which is what my kill chain finds on real frames (`stripe:area`, `stripe:height`, `stripe:width`), the stencil beat the rules (stripe breaks 141 vs 133, edges eaten 2 px 130 vs 110 of 145).
6. Its largest win (two same-colour barrels side by side, 36 -> 83) was unusable in the union and so did not count.

**A caution from my own probe, so the formulation is not oversold** (`work_detector/oracle.py`; a separability probe at given places, not a detector). One crude template score (body share + stripe share - wrong colour), evaluated at the hand boxes of clean barrels and at 180 000 geometry-generated places with no barrel:

| set B, 165 clean barrels | found |
|---|---|
| rule detector | 102 |
| template score on the hard mask, threshold above every no-barrel place | 90 |
| same score on naive soft colour, threshold above every no-barrel place | 77 |
| same, letting two trap frames alarm | 102 |

A single score on colour layout alone does **not** beat the rules. What sets the threshold are the trap frames with orange and blue packaging on the glass table and the printed fruit. So: the unifying formulation will collapse the rule list and remove the order dependence and the non-monotonicity, but it will not raise recall unless it is fed evidence the mask does not carry (edges along the outline, solidity, the occluder state). Formulation fixes the edge cases; evidence fixes the misses. They are separate problems and the project has been spending its rules on the second one.

### 5e. What the detector does not consider at all

- The image: edges, gradients, shading, texture, anything but the class of each pixel.
- How strongly a pixel matched its colour; neighbouring hues; the colour of the table (there is no model of "table", only "not barrel colour").
- What an occluder is; that an occluder has a surface, an edge and a colour of its own.
- Solidity or fill of a region (measured in 5a row 6).
- A confidence or score for any box.
- Uncertainty in the camera pose: per-frame pitch, per-session tilt, another robot, lens distortion (pure pinhole).
- Barrels not standing on the table plane: held, lifted, tipped, on a second level.
- Mutual consistency of the answer: two boxes may overlap up to IoU 0.5; nothing checks that the set of boxes could be one physical scene (only `verify_front`, pairwise, one direction).
- Reflections as reflections (the glass table mirrors every barrel; it works today because the mirror image is not saturated enough to be painted).
- Time: the robot knows how it moved; each frame is answered from nothing, and the tracker only votes on finished boxes.
- Things that are orange and blue and not barrels, except through the stripe proportions.
- The vendor detector's answer, which is saved with every new frame and scores higher on the new sets (99 against 59 of 123 per STATUS.md).
- Its own failure: no rule ever says "this frame's colour is off" (e.g. many stripe-sized bands with no body: the warm-lamp frames), so there is no signal to trigger a fallback.

## 6. Top ten findings, most consequential first

1. **Clean barrels are lost to colour, and the detector's all-or-nothing design makes that loss total.** On real frames no well-painted clean barrel was refused by any rule. 57 of 63 clean misses on B and 10 of 11 on C have one colour unpainted; 49 of the 63 have the *other* colour at full strength in a barrel-sized region and still score zero, because a barrel exists only as stripe-between-body in the same columns. `dark_stripe` proves the half-evidence is real (+30 barrels) and that a yes / no rule cannot use it (+89 false boxes). *Evidence: 3.3, 2.1, `viz/c_hand_miss.png`.*

2. **The detector has no margin. One pixel of erosion removes 19 % of found barrels on HOME + CAMPUS (63 -> 51), 18 % on B, 25 % on C.** Adding paint also loses barrels (10 per one-pixel dilation or 20 points of saturation floor) and multiplies false boxes (B 7 -> 21 -> 80). The hand-set thresholds have no plateau: +-20 S changes 4 to 10 barrels. *Evidence: 4b.*

3. **Most of the rule list does nothing on real frames.** 9 of 30 switches change no box on 199 frame-runs; 17 change at most one frame. The 13 simulation-only switches together: 10 barrels of 326, +2 false. The four outline switches and their ~200 lines: one barrel. Everything since 2026-11-18 other than `side_hidden`: 12 barrels. The detector of 2026-11-09 finds 279 of today's 326. *Evidence: 2.1.*

4. **The occlusion rules were built and judged on a simulator that reality does not confirm.** 14 of 23 on-switches have simulation-only evidence. Real occluded barrels on the one real occlusion set: 9 of 15. Straight edge, half hidden: scorecard 90 of 100, real 0 of 2. Two switches are on after failing their own pre-registered rule. *Evidence: 1.3, 3.4, 5c, `viz/occl_real.png`.*

5. **The 3-class mask is the wall, and thirteen switches are attempts to climb it from the wrong side.** Hidden and absent are the same value; near-threshold colour is rounded away (stripe region of clean misses on B: 0.09 painted, 0.62 with loosened thresholds); edges, solidity and the occluder are never seen. The project wrote this down on 2026-11-19 and then added sixteen more mask-side switches. *Evidence: 5b, 3.3.*

6. **The "partly seen" occlusion path is really the stripe-damage repair path.** It boxes 50 of the 240 clean barrels found across A, B and C, flags them `occluded` with a guessed side, and produces 5 of the 10 false boxes. It is the only post-hardening rule with real weight (26 barrels). The naming hides what the detector actually depends on. *Evidence: 3.6, 2.1.*

7. **Geometry is used as a hard veto with a camera known to be off.** From hand boxes alone: bottoms predicted from the top row are a median 4 px low; best tilt differs by 0.9 deg across places; 15 % of perfectly labelled bottoms fall outside the detector's own tolerance and 37 % of geometry-drawn bottoms outside the scorer's. False boxes double with +2 mm of camera height or -0.9 deg. Far-range tests run on 2 to 4 px margins against a 2 px pose uncertainty. *Evidence: 4a.*

8. **The never-regress gate is blind to the rules it is supposed to police.** 23 of 30 switches change no box on HOME + CAMPUS; 5 change its score. "No false box" is a property of that set (0 on A; 7 and 3 on B and C; 105 one threshold away). *Evidence: 2.1, 2.2.*

9. **Accidental and dead logic is load-bearing.** `height_max` (for a jacket) is the only guard on two later branches (off: +98 false on B). The far-barrel stripeless branch cannot accept a real far barrel, only a mis-shaped piece, and wakes up at `min_stripe_px` +20 % (+43 false). `body_min` changes nothing even when off. `occl_body_side` is unreachable. The diagnostic log is now control flow. About 200 lines belong to switches that are off. *Evidence: 4c, 2.1.*

10. **The same idea is encoded many times with different constants, and the obvious single checks are missing.** Four constants for "wider than a barrel", seven tests for "ends against something", four definitions of "nearer", five distance estimators never fused, seven duplicate checks that still let two boxes sit on one barrel (`lampmid6_glass_clutter_01`). Missing: any fill / solidity test (it separates all 19 kept close-up pieces: true >= 0.64, false <= 0.28), any flag when one box swallows two barrels (`occlx_10`), any confidence. *Evidence: 4c, 5a, 3.5.*

**On replacing the list** (5d): one hypothesise-render-score formulation with visibility by depth order would absorb the caps, the verify step, the frame-edge cases and the duplicate checks, and remove the non-monotonicity. The stencil experiment was a correct rejection of that stencil (it loses on the new real frames too: B 108 vs 148) and not a fair trial of the idea (same mask, a `min` score, HOME-only zero-false calibration, judged against rules tuned on the judging frames). My own crude one-score probe on colour layout does not beat the rules either (90 vs 102 of 165 clean barrels on B at zero false places). The formulation will remove edge cases; only new evidence (soft colour, edges, an occluder state) will remove misses.
