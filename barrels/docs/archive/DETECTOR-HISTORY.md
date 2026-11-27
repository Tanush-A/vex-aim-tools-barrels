# DETECTOR-HISTORY.md — when each rule of the detector was added, and for what

**Archived 2026-11-26.** Until the collapse of that day, `detector.py` carried its own history: a changelog at the top of
the file, and a date, an experiment name or "ON since ..." in the comment of every switch. The collapse (`docs/DETECTOR-MAP.md`,
`experiments/2026-11-26_collapse/`) took the switches out and the history with them: a comment in the code now says what
a check asks and why, not when it was added. This page keeps the "when" and the "for what case".

- "switch" = the name of the `DetConfig` on/off field the rule had until 2026-11-26. Old experiment scripts and
  `EXPERIMENTS.md` use these names. The code with the switches is at the git tag `pre-collapse-2026-11-26`.
- "today" = the function that holds the rule in the collapsed file.
- R = added for a real frame; S = added on simulated scenes (`occlude.py`) or damaged masks (`degrade.py`) only.
- The entries are taken from the comments of the file at the tag and from `docs/archive/DETECTOR-MAP-before-collapse-2026-11-26.md`,
  section 3. They were not re-derived.

## The rules that run today

| rule (today's function) | switch at the tag | added | the case it was added for | experiment |
|---|---|---|---|---|
| blobs of both colors, small gaps closed (`find_blobs`) | none | 2026-11-03 | step 1 of the detector | `2026-11-03_det_step1` |
| a blob n barrels wide is cut at its waists (`split_blob`) | none | 2026-11-03 | HOME `touch_02`: touching barrels of two colors are one blob (R) | `2026-11-03_det_step1` |
| the bottom edge from the top row where the seen one disagrees (`resolve_bottom`) | none | 2026-11-03 | HOME `far_02`: a shaded lower face made the blob short (R) | `2026-11-03_det_step1` |
| a piece must be on the table and barrel-wide (`find_pieces`) | none | 2026-11-03 | the hand at the horizon in HOME `far_02` (R) | `2026-11-03_det_step1` |
| a stripeless piece must be barrel-tall (`find_pieces`, check 4) | `height_max` > 0, hardening (d) | 2026-11-08 | a blue jacket above the table edge, CAMPUS `core_01` (R, one frame) | `2026-11-08_det_hardening` |
| a piece with its top above the horizon is not on the table (`above_horizon`) | none: until 2026-11-26 the height check did this by accident | 2026-11-26 | the same jacket; and 107 boxes on 36 real frame-runs that only the height check held back | `2026-11-26_collapse`, step A7 |
| the stripe is the barrel's anchor: one box per stripe (`find_stripes`, `boxes_from_stripes`) | `require_stripe` | 2026-11-03; the default since 2026-11-05 | it beat step 1 alone under both scoring rules; hands and other orange things have no stripe | `2026-11-03_det_step2` |
| a stripe is found from its own colored pixels, each with body above and below (`find_stripes`, `sandwiches`) | `stripe_mode="cores"`, hardening (b) | 2026-11-08 | shadow glued to a stripe made its band too tall: CAMPUS `core_01`, `plain_01`, `close_01`, `window_01` (R) | `2026-11-07_campus_attribution`, `2026-11-08_det_hardening` |
| a dark gap with no stripe-colored pixel is not a stripe | `dark_stripe` off, hardening (a) | 2026-11-08 | the floating boxes of the first live run were such gaps (R) | `2026-11-06_live_first_run`, `2026-11-08_det_hardening` |
| pieces of one stripe are joined, when stripe-shaped (`_join_pieces`, 3a) | `stripe_join` | 2026-11-18 | a pale patch across a stripe on damaged masks, 85 → 125 of 145 (S). Round 2: only flat pieces join | `2026-11-18_det_given_seg` |
| ... or when body color bridges the gap (`_join_pieces`, 3b) | `stripe_bridge` | 2026-11-20 (A8); on since 2026-11-23 by Tanush's decision | a slit near a stripe's end (S). It failed its written rule by a few boxes (scorecard 45 → 48, medium damage 3 → 4) | `2026-11-20_occl_sliver` |
| a thin stripe seen whole is read a second time at the seams (`find_stripes`, check 4) | `seam_height` | 2026-11-19 | HOME `far_02` with 2 px eaten at the seams (S) | `2026-11-19_det_side` |
| the finder's width floor: 0.45 of a stripe height (`find_stripes`, check 5) | 0.4 W until 2026-11-19; one stripe height with `side_hidden`; 0.45 stripe heights with `pin_thin` | 2026-11-03, 2026-11-19, 2026-11-20 | CAMPUS `occl_02` needed a floor under 0.4 W (R); three quarters hidden (S) | `2026-11-11_occl_narrow_stripe`, `2026-11-19_det_side`, `2026-11-20_occl_pin` |
| a stripe region wider than 1.4 W is cut (`_one_stripe_per_barrel`) | none (`stripe_merge`) | 2026-11-03 | touching same-colored barrels, HOME `touch` frames (R) | `2026-11-03_det_step2` |
| ... and one wider than 1.2 x the barrel its body's height gives, where body is seen right above and below | `stripe_wide` | 2026-11-20 | HOME `core_02` with a same-colored barrel pasted beside: 36 → 88 of 100 (S) | `2026-11-20_occl_vertical` |
| thin pieces enter the stripe step (`Stripe.thin`, `thin_slice`) | `pin_thin` | 2026-11-20; on since the combined experiment | three quarters hidden by a straight edge, the frame or a block: 0–5 → 28–36 of 100 (S) | `2026-11-20_occl_pin`, `2026-11-20_occl_combined` |
| top and bottom: seen where they agree, else predicted (`read_edges`) | none | 2026-11-03 | step 4 of the detector | `2026-11-03_det_step2` |
| an edge is seen only against something that is not a barrel (`read_edges`, a and b) | `edge_check` | 2026-11-19 | a strip of a back barrel between its own stripe and the front barrel, HOME `core_01` with a blue barrel pasted in front (S) | `2026-11-19_det_occl` |
| a thin piece must be a slice seen from top to bottom (`box_from_stripe`) | `pin_outline` and `pin_thin` | 2026-11-19 round 2, 2026-11-20 | a reason for a side says where a barrel would be, not that there is one (S) | `2026-11-19_det_occl`, `2026-11-20_occl_pin` |
| a partly seen stripe is placed by what is seen; a side is hidden only for a reason (`partly_seen`, `seen_span`, `hidden_side`) | `side_hidden` | 2026-11-19 | CAMPUS `occl_02`, the live miss with Dave (R); the rest on simulated scenes (S) | `2026-11-11_occl_attribution`, `2026-11-19_det_side` |
| the frame edge counts as a hidden side | hardening (e), no switch | 2026-11-08 | CAMPUS `edge_01`: the box was drawn into the frame, not into the edge (R) | `2026-11-08_det_hardening` |
| the outline places a stripe that no reason places (`own_end_by_outline`) | `pin_outline`, `pin_good` | 2026-11-20 | half hidden by a straight edge 82 → 90 of 100, slanted 154 → 170 of 200 (S). Round 2: each end is asked by itself | `2026-11-20_occl_pin` |
| a box the outline placed never replaces a found box (`boxes_from_stripes`, step 3) | `pin_outline` | 2026-11-20 round 2 | a piece with a barrel's corner right against a whole barrel (S) | `2026-11-20_occl_pin` |
| a thin slice whose body shows the whole width gets that width (`thin_slice`, 1) | `thin_span` | 2026-11-20 (A8) | a block of the stripe color hiding 75 %: 3 → 77 of 100 (S) | `2026-11-20_occl_sliver` |
| a thin slice cut by the frame is W wide from its other end (`thin_slice`, 2) | `thin_frame` | 2026-11-20 (A8); on since 2026-11-23 by Tanush's decision | frame edge at 75 %: 29 → 88 of 100 (S); it failed its rule on "too big" (boxes 2–3 px past a clipped hand box). One real barrel: ABP `occlx_17` | `2026-11-20_occl_sliver` |
| a second piece of a found barrel's stripe gives no box (`piece_of_found`) | first with `slice_box` (2026-11-19); kept for `stripe_bridge` and thin pieces | 2026-11-19, 2026-11-20 | a highlight leaves a second piece beside the long one (S) | `2026-11-19_det_occl`, `2026-11-20_occl_sliver` |
| the box is as wide as the body joined to the stripe (`place_sides`, `_body_columns`) | `body_width` > 0, hardening (f) | 2026-11-09 | boxes 15 % narrow on big barrels, CAMPUS `core_02` (R) | `2026-11-08_det_hardening` (re-run 2026-11-09) |
| the box must hold body color (`holds_body`) | `body_min` > 0, hardening (c) | 2026-11-08 | a blue barrel's body between two orange things was boxed as orange, CAMPUS `core_01` (R) | `2026-11-08_det_hardening` |
| the surer of two boxes of one barrel stays (`boxes_from_stripes`, step 4) | none | 2026-11-03 | | `2026-11-03_det_step2` |
| a stripeless piece is kept only as a close-up, or too far for a stripe (`closeup_pieces`) | none | 2026-11-03 | HOME `topstripe_01`, `top_01`: the stripe is below the frame (R) | `2026-11-03_det_step2` |
| a box covers a piece only if they share rows (`closeup_pieces`, 1) | `cover_rows`, hardening (g) | 2026-11-09 | live run with Dave: a far barrel above a close-up hid the close-up (R, not a frame of the set) | `2026-11-08_det_hardening` (re-run 2026-11-09) |
| a close-up also cut by the frame's side must be seen down to its stripe (`_seen_to_stripe`) | `closeup_side` | 2026-11-23 (TODO A9) | a printed orange fruit on the empty frame ABP `occlx_15` (R, one frame) | `2026-11-23_closeup_shape` |
| a piece whose stripe the frame bottom cuts is a close-up too (`_closeup_stripe_rows`) | `closeup_stripe` | 2026-11-23 (TODO A9) | palewood `close_01` (R, one frame) | `2026-11-23_closeup_shape` |
| a barrel cannot be seen through a nearer barrel (`drop_seen_through`) | `verify_front` | 2026-11-24 | ABP `occlx_17`, gray `clutter_01`, 9 frames of the recordings: a nearer barrel's upper body read as a stripe (R) | `2026-11-24_occl_strict` |
| a guessed side needs a second reading (`drop_single_reading`) | `verify_readings` | 2026-11-24 | the tin and sticky-note boxes on the glass sets, two of them on empty frames (R) | `2026-11-24_occl_strict` |
| a top above a found nearer barrel is a barrel behind it (`caps_behind`) | `cap_behind` | 2026-11-18 | HOME `occl_01`, `occl_02`, `cluster_01` and the black table: the back barrel's stripe melts into the front barrel's body (R). Round 2: a narrow cap needs exactly one hidden side (HOME `cluster_01`) | `2026-11-18_det_given_seg` |
| a narrow cap's bottom is its color seen ending beside the front barrel (`_cap_box`, 7) | `cap_seen_bottom` | 2026-11-19 (TODO A5) | HOME `cluster_01`, 27 → 28 of 29 (R, one barrel): the top-row bottom is 4 to 7 px low | `2026-11-19_det_bottom` |
| the parts of a found barrel's blob outside its box are cap candidates (`_cap_pieces`) | `cap_same` | 2026-11-19 | a barrel behind one of its own color (S) | `2026-11-19_det_occl` |
| a cap counts from 0.4 of an upper body tall (`_cap_box`, 3) | `cap_low` (0.5, `height_min`, before) | 2026-11-20 | a barrel straight in front hiding three quarters, HOME `core_01` scene: 17 → 22 of 49 (S) | `2026-11-20_occl_vertical` |
| two thin slices one barrel apart are one barrel behind a post (`post_pairs`, `_full_slice`) | `post_pair` | 2026-11-20 | a post over the middle half, HOME `core_02` scene: 9 → 41 of 50 (S). Round 2: a slice that ends against the other barrel color is not a full slice | `2026-11-20_occl_vertical` |
| a stripe with body on one side only is a barrel hidden from above or below (`half_stripes`) | `half_stripe` | 2026-11-20 | HOME `core_02` with the upper or lower half erased: 2 → 40 of 50 (S). Round 2: the stripe is the thinner band | `2026-11-20_occl_vertical` |
| ... with no floor on the band's height | `half_thin` | 2026-11-20 | half hidden from below leaves 2 to 6 rows of stripe (S) | `2026-11-20_occl_vertical` |
| the order of stage 3: whole stripes first, then partly seen ones, nearest first | `side_hidden` | 2026-11-19 | a partly seen stripe may be hidden by a barrel already found | `2026-11-19_det_side` |
| the left-over pieces are handed to the pairs whether or not they also enter the stripe step as thin stripes | `pin_thin` with `post_pair` | 2026-11-20 | with the lower floor a narrow slice was no longer "refused for its width" and never reached the left-over rules | `2026-11-20_occl_combined` |

## Built, switched off, and deleted in the collapse (step A1)

| what | switch | built | why it was off | experiment |
|---|---|---|---|---|
| the first stripe finder: any non-body gap between body above and below | `stripe_mode="bands"` | 2026-11-03 | a dark gap alone counted; shadow glued to a stripe made its band too tall. Replaced by "cores" on 2026-11-08 | `2026-11-03_det_step2` |
| a gap with no stripe-colored pixel is a stripe | `dark_stripe` | 2026-11-03 | the floating boxes of the first live run; on real frames it adds 194 boxes on 112 frame-runs | `2026-11-08_det_hardening` |
| the hidden side read from the body columns, in the older side rule | `occl_body_side` (h) | 2026-11-11 | only useful with a lower `stripe_w_min`, which added 2 false boxes on wood frames. Superseded by `side_hidden` | `2026-11-11_occl_narrow_stripe` |
| a box that covers every place the barrel can be ("the cover box"), and narrow pieces as barrels | `slice_box`, `cover_unpinned` | 2026-11-19 | boxes nearly two barrels wide; 21 false boxes at medium damage, 19 on the scorecard | `2026-11-19_det_occl` |
| a stripe wider than 1.2 W is always two barrels | `stripe_two` | 2026-11-19 | a near barrel cut in two: 3 more false boxes on the scorecard. Replaced by `stripe_wide` | `2026-11-19_det_occl` |
| a narrow full slice beside a found nearer barrel or the frame edge | `slice_behind` | 2026-11-20 | on damaged masks it boxes the wrong side of a slice left in a bunch (medium damage, 20 seeds: 7 false boxes against 3) | `2026-11-20_occl_vertical`, `2026-11-20_occl_combined` |
| the end where the body closes on the stripe is the barrel's own side | `own_close` | 2026-11-20 (A8) | a barrel in front is round too: bad day 5 → 6 false boxes, 3 scorecard scenes lost | `2026-11-20_occl_sliver` |
| step 1 alone (the detector before 2026-11-05) | `require_stripe=False`, `detect_step1`, `detect_image.py --step1` | 2026-11-03 | kept as a comparison mode until the collapse (step A2) | `2026-11-03_det_step1` |

## The collapse itself

2026-11-26, branch `wip/collapse`, nine steps (`experiments/2026-11-26_collapse/ENTRY.md`): the off switches deleted (A1),
the on switches made plain code (A2), `detect` as ten named stages (A3), the helpers (A4), `BarrelAt` (A5), each box
carrying its evidence (A6), the horizon fact written out (A7), three clauses that never decide removed (A8), this page
(A9). After every step the detector drew the same 6152 boxes on the same 5435 masks.
