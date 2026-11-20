# Pre-registration: a stripe cut through, and a sliver with stripe and body in view (A8)

Written 2026-11-20 on branch `wip/occl-sliver` (= `barrels` with the combined occlusion work merged, plus this
experiment's measurement scripts), **before any detector code is changed**. What had been run when this was written:
the measurement scripts of this folder (`diag_stripe.py`, `diag_cells.py`, `census_pairs.py`, `census_ends.py`,
`census_ends_damaged.py`), and the scorecard for the starting defaults (`results/.../check_start/`: 2737 found, 45
boxes where no barrel is, the published numbers; the gate passes on the defaults). No arm with a new rule has been run:
the rules below do not exist in code yet.

The user's two asks: (1) "a stripe cut through should be solvable: a strong enough sense of a stripe on the same rows
with a gap in the middle → fill it in"; (2) "when ANY stripe is shown (a sliver of body and stripe), good bounding".
And "no false positives at all"; never regress on HOME or CAMPUS.

## What the measurements say (the numbers the rules are built on)

### Part 1: why a cut stripe costs barrels (`results/2026-11-20_occl_sliver/stripe_before/stripe.md`, 20 seeds, 580 barrels)

The starting detector: perfect masks 28 / 29; stripe patch 0.03–0.3 W: 538–547 found, 5–15 false; one break 0.03 W:
560 (0 false), 0.06–0.3 W: 535–553 (2–18 false); two breaks: 465–560 (1–13 false); bad day 547 (5); medium 400 (3).
20 of the misses at every level are the one perfect-mask miss (the wedge of `cluster_01`) × 20 seeds.

Reason log, the rest: the false boxes are almost all **"stripe step, misplaced box of a missed barrel"**: the patch cuts
the stripe into two pieces; `stripe_join` does not join them because one piece fails its stripe-shape test (taller
than wide, or its box taller than 1.6 stripe heights: a piece at the end of a stripe cut by a patch is narrow, and a
piece touching a neighbour's body picks up a sliver of it); the larger piece alone is a partly seen stripe, one side has
a "reason" (body and stripe end apart where the patch cut it, or a found barrel beside it in a bunch) and the box is
drawn a barrel wide toward the wrong side. Example: HOME `cluster_02`, orange (390, 116, 432, 163), patch 0.06 W, seed 1:
pieces (391, 121, 410, 146) (19 wide, 25 tall: it holds two columns of the blue front barrel's edge) and (413, 135, 429,
147); not joined; box (371, 116, 413, 161), overlap 0.37 → one miss and one false box. The other misses: the same pieces
left without a box (`side_unexplained`, `outline_unknown`), e.g. `edge_01` at the frame edge: pieces (0, 159, 20, 177)
and (23, 154, 30, 173) (7 wide, 19 tall), not joined.

### Part 1: what separates one stripe from two (`census_pairs.md`, seeds 0–4)

A pair = two pieces of sandwiched stripe color sharing rows, together at most 1.2 W ("fits"). "Bridged" = both pieces
no taller than `stripe_h_max` (1.6) stripe heights **by the finder's own height measure** (10th to 90th percentile of
the rows) **and** body color right above and right below in **every** column of the gap.

| masks | bridged pairs on one barrel | on two barrels | one on no barrel | both on no barrel |
|---|---|---|---|---|
| real (HOME hand, HOME l.o.s.o., CAMPUS) | 3 | 0 | 0 | 0 |
| black, wood (report only) | 10 | 1 | 0 | 2 |
| stripe patch, all widths | 556 | 0 | 2 | 0 |
| one stripe break | 548 | 0 | 0 | 0 |
| two stripe breaks | 843 | 0 | 0 | 0 |
| bad day / medium | 90 / 86 | 0 / 0 | 0 / 0 | 0 / 0 |

The bridged pairs not on one barrel: on HOME two, pieces of 5 px and 1 px a barrel apart (gap 1.06 W over a span of
1.1 W); on wood one two-barrel pair (gap 0.21 W over 0.39 W) and two nested pairs (a 2 px and a 26 px piece inside the
columns of a big orange patch on the wood, gap < 0; joining them adds no column to it). Adding "the gap is at most half
the joined span" removes every pair that is not nested and keeps 1850 of 2123 bridged pairs on one barrel (87 %) on the
damaged masks, 1 of 3 on the real masks; the two nested wood pairs stay (report only). Without the bridge, "the gap at most one stripe height" would join 49 of 59
two-barrel pairs (patch): **the gap's size alone is not a strong enough sense; body over the whole gap is.**

### Part 2: own end or cut end (`census_ends.md`, `census_ends_damaged.md`)

`closed` at an end = min(top gap, bottom gap) over the columns within 0.05 W of the end, in barrel heights (how far
BOTH the top and the bottom have come in from where the stripe's row predicts them). Own ends: median 0.21 / 0.18
(hand / color-model masks); straight cut 0.01 / 0.02; frame edge 0.004 / 0.011; slanted cut 0.05; block 0.06–0.08.
The rule "one end closed ≥ 0.15, the other ≤ 0.1" asked of **full slices** (the body above and below ends where the
stripe's row predicts top and bottom, the test `pin_thin` already uses):

| where | calls | wrong |
|---|---|---|
| scorecard, every side kind × 25 / 50 / 75 %, full slices under 0.8 W seen | 1330 | **0** |
| ... 75 %: frame 63 of 91, straight edge 63 of 91, slanted 97 of 153, body block 31 of 53, stripe block 1 of 13, both sides 0 of 49 | | 0 |
| real and damaged masks (patch, breaks, bad day, light, medium; black and wood), full slices | 177 | **0** |
| the same masks, pieces that are NOT full slices | 183 | 8 (why the rule asks for a full slice) |
| full slices with the looser cut ≤ 0.15 | 194 | 4 (why the line is 0.1) |

"Both sides cut" at 75 %: no end of any of the 49 scenes is closed; the mask cannot say which way the barrel extends.

The frame edge at 75 %: 60 of the 71 misses are `outline_unknown`: the piece is thin, and a thin piece is placed by the
outline only, so the frame edge (a known hidden side) is never asked. `census_slice.md` (combined experiment): of 129
boxes `slices_behind` drew leaning on the frame edge, 0 were wrong; all 9 wrong ones leaned on a found barrel.

A block of the stripe color at 75 %: in 86 of 100 scenes the barrel's upper body shows in its whole width above the
block (the block starts 0.15 H below the barrel's top), so what is seen of the barrel is ≥ 0.8 W; but the piece of
stripe is thin, and a thin piece is placed by the outline only, "whatever its span".

## The rules (each one sentence; switches in `DetConfig`, every number a proportion of the barrel or an existing parameter)

1. **`stripe_bridge`** (Part 1, in `_join_pieces`): two pieces of stripe color that share rows and fit in one barrel's
   width (as `stripe_join`) are one stripe, gap included, also when one of them fails the stripe-shape test, if each is
   no taller than `stripe_h_max` stripe heights by the finder's height measure, the body color is right above and right
   below the stripe in every column of the gap (the finder's sandwich), and the gap is at most half the joined span.
2. **`thin_frame`** (Part 2, frame edge, in `_partly_seen`): a thin piece that is a full slice and whose seen part
   touches the frame edge on exactly one side is a barrel W wide from its other end (the frame-edge half of
   `slice_behind`, asked in the stripe step).
3. **`own_close`** (Part 2, own side, in `_partly_seen`): a partly seen stripe that is a full slice and that neither a
   side reason nor the outline places is a barrel W wide from an end where the body has closed on the stripe (both
   the top and the bottom at least `bottom_tol` (0.15) H in from the predicted rows over the last 0.05 W), when the
   other end stands (at most 0.1 H). Asked after the outline; thin pieces included.
4. **`thin_span`** (Part 2, a painted block in front): a thin piece that is a full slice and whose body joined to it is
   seen 0.8 to 1.2 W wide (the same "trusted span" every partly seen stripe uses) gets the span as its box, as a wider
   stripe would.

Not built: anything for "both sides cut" (nothing in the mask), the cover box (off, user's decision), `slice_behind`'s
found-barrel half (its wrong boxes), anything using the image.

## Arms (`sliver.py`, each spelled out from `start`)

`start` (today's defaults, checked field by field), `bridge`, `frame`, `close`, `span` (each switch alone),
**`sliver`** (all four: the candidate default), and report only `start+behind`, `start+cover`.

## Battery (combined experiment's scripts by path, `battery.py`), and `diag_stripe.py`, `diag_cells.py`

Gate (`report.py --gate --cand-det ...`), eval table, scorecard (3888 scenes), damage levels (5 and 20 seeds; judged on
20), real occluded barrels, campus recordings by eye (black and wood described), `diag_stripe.py` at every width.

## Acceptance (against `start`)

- No false positive added: the gate passes; scorecard boxes where no barrel is ≤ 45 and no cell (found, v2) lower;
  false boxes not higher on perfect, typical, bad day, bad day without the stripe patch, light, medium, heavy (judged on
  20 seeds, 5 reported); campus clips: no new wrong box (every box appearing or disappearing judged on a sheet).
- Part 1 (`stripe_bridge`): bad day and medium find more with no more false boxes, and the stripe patch and one and two
  stripe breaks improve (found up, false not up) at every width tested (0.03 0.06 0.1 0.15 0.2 0.3 W; a width already at
  its ceiling, i.e. found equal to the perfect-mask count × 20 with 0 false, counts as passing unchanged).
- Part 2, cell by cell (every 75 % cell, and every other cell that changes): the switch's change is kept if found and
  right place rise and too big and boxes where no barrel is do not.
- Each switch is judged alone against `start` and in `sliver`; what passes both is on by default; what fails stays off
  and is named.

At most two rounds. If a round fails by boxes a rule drew, the boxes are attributed with the reason log, a dated
addendum below names the change (pre-named now: `own_close` with cut ≤ 0.05, the census's next line with 0 wrong;
`stripe_bridge` with the gap at most a third of the span) **before** its code, and the battery is run once more.
Train frames only; no camera constant changed; no image correction; no temporal information.
