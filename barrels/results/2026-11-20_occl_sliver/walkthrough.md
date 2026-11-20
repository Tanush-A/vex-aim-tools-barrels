# Walkthrough: the four rules of A8 as instances of the one idea

*What is seen fixes the distance; the distance fixes the full size; the box is the full barrel placed where the seen part
allows; a rule only acts when what is seen could not be anything else.*

Each rule below is one sentence, then the three parts (the reading that gives the distance, the second reading that
agrees, what pins the place), then one example in numbers (`examples.md`).

## `thin_span` — ON

**Rule.** A thin piece of stripe that is a full slice, and whose body joined to it is seen a whole barrel wide (0.8 to 1.2 W),
gets that width as its box, unless body color crosses the stripe's rows somewhere in it.

- Distance: the stripe piece's row. Second reading: the body above and below ends where that row predicts the top and the
  bottom (full slice). Place: the body itself shows both sides of the barrel.
- Why "could not be anything else": a barrel's body never crosses its own stripe; a body-colored thing in front does, and
  then the rule is silent.
- *HOME `close_01`, orange (302, 143, 390, 235), a stripe-colored block hiding 75 % from the right:* piece (306, 182, 324,
  204), 18 px; row 192.5 → W 80.7, H 86.7; the upper body above the block shows the whole width → (305, 143, 384, 231),
  overlap 0.86. Before: no box.

## `stripe_bridge` — off (Part 1)

**Rule.** Two pieces of stripe color at the same rows that fit in one barrel's width are one stripe, gap included, when the
body color is right above and right below the stripe in every column of the gap and the gap is at most half the span.

- Distance: the joined stripe's row. Second reading: the body over the whole gap (a highlight or a slit removed the stripe
  there, not the barrel). Place: the joined stripe, then the usual rules.
- Why "could not be anything else": two barrels cannot have their stripes inside one barrel's width at the same rows, and
  between two barrels the body does not run over the gap (0 of 114 two-barrel pairs in `census_pairs.md`).
- *HOME `edge_01`, blue (0, 133, 34, 198), one slit 0.1 W through the stripe (seed 12):* pieces (0, 160, 14, 177) and (17,
  154, 30, 175), the second 13 wide and 21 tall (not stripe-shaped); W 64. Before: no box. Bridged: (0, 154, 30, 177) → box
  (0, 133, 34, 198), the hand-drawn box.
- Off because: 3 scorecard boxes on one campus scene with a same-colored barrel beside, 1 at medium damage.

## `thin_frame` — off

**Rule.** A thin full slice that touches the frame edge on exactly one side is a barrel W wide from its other end.

- Distance: the piece's row. Second reading: full slice. Place: the frame edge is the hidden side, so the far end of the
  seen part is the barrel's own side.
- *HOME `cluster_02`, orange, 75 % outside the frame on the left:* piece (0, 141, 11, 154); row 147.5 → W 49.4 → (0, 120,
  11, 169), overlap 0.96. Before: no box.
- Off because: "too big" 3 → 8 in the frame cell (five boxes 2 to 3 px wider than a hand box clipped at the frame).

## `own_close` — off

**Rule.** A partly seen full slice that nothing else places is W wide from the end where the body closes on the stripe (top
and bottom both 0.15 H in over the last 0.05 W), when at the other end one of them stands (at most 0.1 H) and the own end is
not against barrel color.

- Distance: the stripe's row. Second reading: full slice. Place: a barrel's own side has round corners; a cut by an upright
  or slanted edge, the frame or a block leaves at least one of top and bottom standing.
- *HOME `cluster_02`, blue (443, 122, 500, 179), 75 % behind a straight edge from the left:* piece (486, 147, 496, 159);
  W 53.6, H 58.1; closure left −0.001 H, right 0.174 H → (445, 124, 499, 179), overlap 0.91. Before: no box.
- Off because: a barrel standing in front is round too; bad day +1 false box, 3 scorecard scenes lost.

## Where the one idea says "no box"

Three quarters hidden on both sides: no end closes (0 of 49), so nothing pins the place; any box would be a guess or the
cover box (nearly two barrels wide). Hidden from above or below at 75 %: no stripe is seen at all.
