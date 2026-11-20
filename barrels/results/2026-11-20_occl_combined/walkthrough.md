# Occlusion in the detector: one idea, and each rule as a case of it

For Tanush, to say out loud to Dave. Short sentences. Every number is from the code or from a real train frame.
Code: `src/barrels/detector.py`. State: branch `wip/occl-combined`, 2026-11-20. Numbers: `scorecard.md`, `verdict.md`.

## The one idea

> **What is seen fixes the distance. The distance fixes the full size. The box is the full barrel, placed where the
> seen part allows. A rule acts only when what is seen could not be anything else.**

Why this works. The camera is fixed: 43.47 mm above the table, tilted down 22.25°. A barrel is 24 mm tall and 25.5 mm
wide. Its stripe is 6 mm tall, from 9 mm to 15 mm above the table. So one known row of a barrel gives its distance,
and the distance gives everything else: width W, height H, top row, bottom row, stripe rows.

Example. A stripe whose middle is at row 148.5 is 204 mm away. There a barrel is W = 50 px wide and H = 54 px tall.

Every occlusion rule has the same three parts:

1. **A reading.** Something seen that gives the distance: the stripe's row, a seam, a top row.
2. **A second reading that agrees.** A seen edge where the first reading predicts it. This is what makes "it could
   not be anything else". Without it, no box.
3. **A place.** The box is W wide and H tall. It goes where the seen part pins it. If nothing pins it, no box.

A miss is allowed. A box in the wrong place is not.

## The order the data flows

```
class mask
  └─ stripe finder ........... stripes (other color, body above and below)      rules 1, 2
       └─ stripe step ........ one barrel per stripe; partly seen ones last     rules 3, 4, 5, 6, 7
            └─ stripeless pieces (close-ups, far barrels)
                 └─ caps ..... a top behind a found barrel                      rule 8
                      └─ left-over pieces: pairs, then half stripes             rules 9, 10
```

Why this order. A rule runs after everything it leans on. Caps lean on found barrels. The left-over rules take
only what gave no box, and each first asks "is there already a box of this color here". So nothing found earlier
changes.

## The rules, one by one

### 1. A stripe in pieces is one stripe (`stripe_join`, on)

- **Seen:** two or more pieces of stripe color at the same rows.
- **Why it could not be anything else:** two barrels cannot both have their stripe inside one barrel's width. So pieces
  that share rows and together span at most 1.2 W are one stripe.
- **In numbers:** a pale patch 0.15 W wide across every stripe (the damage test): before, each piece failed alone and
  85 of 145 barrels were found; joined, 125 of 145.

### 2. A stripe eaten thin at its seams (`seam_height`, on)

- **Seen:** a stripe too thin by its own rows, but seen whole (0.8 W wide).
- **The second reading:** mixed pixels at the two seams are neither color. The stripe loses them, and the gap between
  the two body parts grows by the same amount. So the mean of stripe height and gap height is the true height.
- **In numbers (HOME `far_02`, 2 px eaten):** stripe rows 120 to 123, 4 rows. Gap rows 116 to 126, 11 rows. Mean
  7.5. Expected at that row 8.3. A stripe.

### 3. A stripe cut at the side: which side is hidden? (`side_hidden`, on)

- **Seen:** a stripe narrower than 0.8 W. Plus the body color joined to it above and below.
- **A side counts as hidden only for a reason:** the frame edge is there; or a found barrel standing nearer is there;
  or the body runs on past the end of the stripe there (at a barrel's own side they end together).
- **The place:** one side hidden → the box is W wide from the seen edge of the other side.
- **In numbers (CAMPUS `occl_02`, the barrel behind the marker stand):** stripe columns 278 to 294, 16 px. Its row
  154 → 188 mm, W 54, H 59. Body seen from 277 to 311. Left: body and stripe end 1 px apart: the barrel's own edge.
  Right: 17 px apart (limit 8): cut. Box from 277 to 277 + 54 = 331: (277, 127, 331, 178). Hand-drawn
  (275, 123, 328, 180). Overlap 0.82.

### 4. An edge is seen only against something that is not a barrel (`edge_check`, on)

- **Seen:** a band with the other color above and below, but neither its top nor its bottom where its row predicts.
  Its top ends against the other barrel color.
- **Why it is not a barrel:** a thing right above a barrel's top, inside its box, stands behind it. It cannot hide
  the top. So this band is a strip of a back barrel, not a barrel.
- **Also:** a seen bottom that ends against another barrel is not the bottom. Take the lower of seen and predicted.
- **In numbers (HOME `core_01`, orange (292, 121, 342, 176), a blue barrel pasted in front):** before, a wrong BLUE
  box (287, 124, 346, 188) and an orange box 9 px short. Now the blue band is refused, and the orange box is
  (293, 121, 340, 174). Overlap 0.91.

### 5. No reason on either side: the barrel's own corner pins it (`pin_outline`, on)

- **Seen:** a partly seen stripe, body and stripe ending together on both sides. So rule 3 has no reason.
- **The reading:** the distance gives the barrel's outline. A barrel's own side has rounded corners: over the last
  8 % of the width the top runs down 10 to 13 px and the bottom runs up 13 to 17 px (55 px barrel). A cut side has
  square corners.
- **The test:** ask each end by itself. Put the outline's side on that end. Compare top line, stripe line and bottom
  line over 0.35 W. The end's cost is the worst of the three. An end that costs at most 0.05 H is the barrel's own.
- **Could not be anything else:** exactly one end must pass. Neither or both: the outline does not know; as before.
- **In numbers (HOME `core_02`, orange (368, 120, 418, 173), left half behind a straight edge):** W 50, H 54, limit
  0.05 × 54 = 2.7 rows. Left end costs 4.6 rows: cut. Right end 1.8: own side. Box 418 − 50 = 368 to 418:
  (368, 120, 418, 172). Overlap 0.98. Before: centred, (380, 120, 431, 172), overlap 0.59.

### 6. A thin slice with one own corner (`pin_thin`, on since 2026-11-20)

- **Seen:** a piece of stripe narrower than a stripe is tall. That is what three quarters hidden leaves.
- **Two readings needed:** the slice is seen from top to bottom where its row predicts (a "full slice"); and exactly
  one end is the barrel's own side (rule 5's test). Then the box is W wide from that end. Otherwise no box.
- **In numbers (HOME `close_01`, orange (302, 143, 390, 235), three quarters behind a straight edge):** piece columns
  368 to 385. Row 194.5 → 124 mm, W 82, H 88. Seen 368 to 389 = 0.26 W. Limit 4.4 rows. Left end 17.7 rows: cut. Right
  end 3.1: own. Box (307, 145, 389, 231). Overlap 0.87.
- **Limit:** it works when the corner is clean: 28 of 100 at a straight edge, 29 at the frame edge, 36 behind a block.
  A ragged corner is a miss, not a wrong box.

### 7. A stripe wider than a barrel is two barrels (`stripe_wide`, on)

- **Seen:** one stripe wider than 1.2 W, with body color right above and right below it.
- **Why:** one barrel's stripe is never that wide for the height of body seen. So two barrels of one color overlap.
  Each is W wide from its own outer edge.
- **In numbers (HOME `core_02`, orange (368, 120, 418, 173), half hidden by an orange barrel at (340, 124, 393, 178)):**
  stripe columns 342 to 416, 74 px, W 50. Before: one box (348, 120, 410, 178). Now (342, 121, 396, 178) and
  (367, 120, 418, 178).

### 8. A top behind a found barrel (`cap_behind`, `cap_seen_bottom`, `cap_same`, `cap_low`, all on)

- **Seen:** a piece of body color, barrel-wide and as tall as an upper body for its row. No stripe: the stripe has
  melted into the front barrel.
- **The reading:** the top row gives the distance. **The second reading:** the piece's width matches W, and what is
  missing below lies inside a found barrel that stands nearer. A top with nothing found in front of it gets no box.
- **In numbers (HOME `occl_01`):** blue cap columns 386 to 430, rows 115 to 135. Top row 115 → W 46.7, upper body
  22.6. The cap is 44 wide and 20 tall. A barrel 44 wide is 47.8 tall → bottom 163; blue seen ending at 160. Box
  (386, 115, 430, 160). Hand-drawn (386, 115, 430, 161).
- `cap_seen_bottom`: a narrow cap's bottom is its own color seen ending beside the front barrel. *HOME `cluster_01`:*
  cap 32 px wide, seen end 162, estimate from the top row 173. Box (315, 118, 366, 162), overlap 0.71. This is the
  barrel that took HOME from 27 to 28 of 29.
- `cap_same`: the same for a top above a barrel of its OWN color. *HOME `cluster_02`:* box (444, 122, 499, 182),
  overlap 0.92.
- `cap_low`: the top may be as short as 0.4 of an upper body (was 0.5). *HOME `core_01`, blue (239, 123, 290, 178), an
  orange barrel in front hiding three quarters:* top row 123 → 178 mm, W 57.3, upper body 28.5. The cap is 46 wide
  (0.80 W) and 13 tall (0.46 of an upper body): refused at 0.5, kept at 0.4. Box (241, 123, 287, 173). Overlap 0.82.

### 9. Two slices behind a post are one barrel (`post_pair`, on)

- **Seen:** two narrow stripe pieces at the same rows. Each gave no box alone.
- **Second reading:** each is a full slice (top and bottom where its row predicts). Their outer edges are 0.8 to
  1.2 W apart.
- **Why:** two barrels at one distance cannot have their outer edges within 1.2 W.
- **In numbers (HOME `core_02`, a post over the middle half):** pieces at columns 368 to 380 and 405 to 416, rows 141
  to 154. W 49.1. Outer edges 50 px apart (1.02 W). Box (368, 120, 418, 173): the hand-drawn box exactly.

### 10. A stripe with body on one side only: hidden from above or below (`half_stripe`, `half_thin`, on)

- **Seen:** a band of stripe color with body color under it and nothing above (top hidden), or the reverse.
- **The reading:** the seam between band and body. The stripe's bottom edge is 9 mm above the table, its top edge
  15 mm. So the seam's row alone gives the distance.
- **The second reading:** the body's far edge is where the seam predicts it, and it ends against table, not against
  barrel color. Also: the band shows the whole width (0.8 to 1.2 W), and it is thinner than the body beside it.
- **In numbers (HOME `core_02`, upper half hidden):** blue band columns 368 to 417, rows 146 to 154. Seam at row 154 →
  205.9 mm: W 49.5, H 53.7, top at 117.1, bottom at 170.9. Orange ends at row 173, 2.1 px from 170.9 (allowed 8.1).
  Box (368, 117, 417, 173). Overlap 0.93. *Lower half hidden:* only 5 rows of stripe show (needs `half_thin`); seam
  142 → top predicted 117.6, seen 120. Box (368, 120, 418, 172). Overlap 0.98.

## Built, and off

| switch | what it would do | why it is off |
|---|---|---|
| `slice_behind` | a narrow full slice beside a found nearer barrel, or at the frame edge, is a barrel W wide from its seen edge. *CAMPUS `hand_02`:* piece columns 172 to 184, found blue barrel at its left; box (128, 125, 184, 184), overlap 0.86 | on damaged masks it boxes the wrong side of a slice left beside a barrel in a bunch: medium damage, 20 seeds, 7 false boxes against 3. The rule allows 6. All 9 wrong boxes measured lean on a found barrel; none of the 129 that lean on the frame edge is wrong (`census_slice.md`): a lead, not built |
| `slice_box`, `cover_unpinned` | where nothing pins the box, draw one that covers every place the barrel can be (up to 1.75 W wide) | boxes nearly two barrels wide; 21 false boxes at medium damage against 3. Tanush, 2026-11-19: stays off |
| `stripe_two` | rule 7 without its guard | 3 false boxes on one large near barrel; rule 7 replaces it |

## What a student should be able to say about each cell of the scorecard

- **Half hidden: found.** From the side by rule 3 or 5. From above or below by rule 10. A post by rule 9. A barrel of
  the other color by rule 3 (a found barrel is a reason). The same color beside by rule 7.
- **Three quarters hidden: found only when something pins it.** A found barrel in front (rules 3 and 8). Or a clean
  own corner (rule 6).
- **Not found, and it cannot be from the painted pixels alone:**
  - both sides cut, a quarter showing: no end is the barrel's own, nothing says where the rest is;
  - a top alone or a base alone (three quarters from above or below): one row and a width; any orange or blue thing
    of that size looks the same;
  - a slanted cut through the corner itself;
  - the reason: **in the class mask a thing in front that is not a barrel is unpainted, exactly like empty table.**
    The mask cannot say "something is here". The gray image could (an edge, a texture). That is the next idea, not
    built.
- **Not found, and it might be done from the mask:** a same-colored barrel straight in front hiding half (one blob,
  one stripe; the back barrel's top is 0.19 H above the front one's, the tolerance is 0.15 H).
