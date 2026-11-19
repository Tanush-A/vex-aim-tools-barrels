# By eye: boxes that differ from the rule detector's on the unlabeled recordings

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model; `rules` draws 506 boxes.
Sheets: `sheets/rec_<arm>/` (ignored by git), made by `experiments/2026-11-20_stencil/run_recordings.py`; the list of
boxes is `recordings.csv`, the counts `recordings.md` and `recordings_by_clip.md`. Looked at 2026-11-20: `rec_stencil`
sheets 00 to 03 (every campus and black frame, the first wood frames) and `rec_veto` sheet 00.
"Appears" = a box the arm draws where `rules` has no box of that color overlapping it by half; "disappears" = the reverse.

| arm | boxes | appear | disappear |
|---|---|---|---|
| `stencil` | 452 | 0 | 54 (campus 16, black 1, wood 37) |
| `union`, `union1` (round 2) | 506 | 0 | 0 |
| `veto`, `veto+union` | 473 | 0 | 33 (campus 3, black 1, wood 29) |

**No arm draws a box on the recordings that the rule detector does not draw.**

## Campus clips (these decide, PREREG rule 3)

`stencil`, the 16 boxes it does not draw:

| frame | the rule detector's box | what it is | verdict |
|---|---|---|---|
| `r2_pan` 034, 035 | blue, at the right frame edge, 16 to 18 px wide | a blue barrel entering the picture, a sliver | **right box lost** (2) |
| `r2_pan` 052, 056, 057 | blue (269..321, 110, .., 160) | sits on the upper left of the ORANGE barrel and the blue chair behind it; the orange barrel has its own box | wrong box gone (3) |
| `r3_enter_leave` 047 | orange, at the right frame edge, 26 px wide | an orange barrel leaving, a sliver | **right box lost** (1) |
| `r4_hand_occlusion` 011 | blue (274, 105, 307, 142) | above the orange barrel, on the chair behind | wrong box gone (1) |
| `r4` 017 | orange (404, 101, 439, 133) | on the fingers; the barrel under them is blue | wrong box gone (1) |
| `r4` 020 | orange (265, 112, 316, 159) | the orange barrel seen between the fingers of a hand lying over it | **right box lost** (1) |
| `r4` 033 | orange (276, 97, 301, 124); orange (402, 104, 441, 143) | a small box above the orange barrel; an orange box on the BLUE barrel (the stencil draws the blue box there) | wrong boxes gone (2) |
| `r4` 042 | blue (400, 114, 436, 158) | the blue barrel with a fingertip over its right side | **right box lost** (1) |
| `r4` 047, 051, 052, 053 | orange (399..411, 103..110, .., 143) | an orange box on the upper part of the BLUE barrel under the hand; the stencil draws the blue box | wrong boxes gone (4) |

- **`stencil` alone: no new box; 11 wrong boxes of the rule detector are gone; 5 right boxes are lost** (three slivers
  at the frame edge, two barrels under a hand). The rule says a box that disappears must have been wrong: **fails
  on those 5**, and passes "no new wrong box".
- **`union` and `union1`: no frame changes (the same 506 boxes as `rules`, checked again after round 2). Pass.**
- **`veto`, `veto+union`: 3 boxes gone, all three wrong** (`r2_pan` 052, `r4` 017, `r4` 053). **Pass.**

## Black-table clip (described, not judged)

Frame 038: the blue barrel's box (156, 143, 233, 224), a right box, is not drawn by `stencil` and is removed by
`veto`: the barrel's body is only partly painted under the window glare and no stencil place reaches the line. One
right box lost in 50 frames; nothing appears.

## Wood clip (described, not judged; the orange table is parked as extreme)

`stencil` does not draw 37 of the rule detector's boxes, `veto` removes 29. On the frames looked at (000 to 007) each
is a box on the upper half of the blue barrel only: the table-colored light paints the barrel's lower half orange, so
the rule box stops at the stripe. Half-barrel boxes, gone. Nothing appears.
