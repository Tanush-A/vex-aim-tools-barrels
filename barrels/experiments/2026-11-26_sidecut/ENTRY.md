# ENTRY.md — the text for `docs/EXPERIMENTS.md` (paste it in; newest first)

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
