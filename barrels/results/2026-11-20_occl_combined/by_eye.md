# By eye: boxes that appear or disappear on the unlabeled recordings

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model, read-only. `before` draws 499
boxes, `stack` 506. Sheets: `round2/rec_vs_before/sheets/rec_<arm>/`, `round2/rec_vs_stack/sheets/rec_<arm>/`,
`verify*/rec_vs_*/sheets/` (ignored by git), made by `experiments/2026-11-20_occl_combined/run_recordings.py`; the lists of
boxes are the `recordings.csv` next to them. Looked at 2026-11-20: both sheets of `combined` and of `reduced+thin`
against `before`, the sheet of `combined` against `stack`, sheets 00, 01, 02 and 05 of `combined+verify`, sheet 01 of
`combined+cover` against `stack`. An appearing box is ringed in red, a disappearing one in magenta.

## Campus clips (these decide: PREREG clause (c))

Against `before` (the defaults of `barrels`):

| arm | appear | disappear | what they are |
|---|---|---|---|
| `stack`, `reduced`, `reduced+thin` | 4 | 0 | `r2_pan` 034 and 035: the blue barrel entering at the right frame edge, (622, 123, 640, 170) and (624, 123, 640, 171). `r3_enter_leave` 014 and 047: the orange barrel at the right frame edge, (611, 138, 640, 216) and (614, 141, 640, 220). **All four on real barrels** (from `side_hidden`, 2026-11-19). |
| `combined`, `combined+thin` | 5 | 0 | the same four, and `r3_enter_leave` 013: the same orange barrel one frame earlier, (619, 142, 640, 215), a sliver 21 px wide at the frame edge, on the barrel (from `slice_behind`). **Right.** |

Against `stack`:

| arm | appear (wrong) | disappear | verdict |
|---|---|---|---|
| `reduced`, `reduced+thin` | 0 | 0 | **pass.** No frame of any clip changes. |
| `combined`, `combined+thin` (round 2) | 1 (0) | 0 | **pass.** `r3_enter_leave` 013, on the barrel. In round 1 `combined+thin` did not draw it (`pin_thin` had taken the slice away from `slices_behind`); with the hand-over fix it does. |
| `combined+cover` (report only) | 1 (0) | 0 | the same box. |

Nothing is drawn on the hand over the barrels in `r4_hand_occlusion` by any switch of this work.

**Wrong boxes that were there before and are still there.** Looking at what the verifier removes showed 11 boxes on
the campus clips that are wrong and that every arm draws, `before` included: `r2_pan` 052, 056, 057: a blue box on the
upper left of the ORANGE barrel and the blue chair behind it (the orange barrel has its own box); `r4_hand_occlusion`
011: a blue box above the orange barrel, on the chair; 017: an orange box on the fingers; 033: a small orange box
above the orange barrel and an orange box on the BLUE barrel; 047, 051, 052, 053: an orange box on the upper part of
the BLUE barrel under the hand. None of the occlusion switches adds or removes one of them. 11 wrong boxes in the 238
campus frames: that is the false-positive count on real video today, and it comes from the stripe step on a hand or a
chair behind a barrel, not from the occlusion rules.

## The verifier (limit 0.16; `verify_calibration.md`)

On `combined`: 14 campus boxes dropped, none added. On `reduced` and on `reduced+thin`: 13 (the same without
`r3_enter_leave` 013, which those arms do not draw).

| frame | the box | what it is | |
|---|---|---|---|
| `r2_pan` 035 | blue (624, 123, 640, 171) | the blue barrel entering at the frame edge, a sliver | **right box lost** |
| `r2_pan` 052, 056, 057 | blue (269..281, 110, .., 160) | on the orange barrel and the chair behind | wrong box gone (3) |
| `r3_enter_leave` 013 (`combined` only) | orange (619, 142, 640, 215) | the orange barrel at the frame edge | **right box lost** |
| `r4` 011 | blue (274, 105, 307, 142) | above the orange barrel, on the chair | wrong box gone |
| `r4` 017 | orange (404, 101, 439, 133) | on the fingers | wrong box gone |
| `r4` 020 | orange (265, 112, 316, 159) | the orange barrel seen between the fingers of the hand lying over it (a judgment call: its stripe shows) | **right box lost** |
| `r4` 033 | orange (276, 97, 301, 124); orange (402, 104, 441, 143) | above the orange barrel; on the blue barrel | wrong boxes gone (2) |
| `r4` 047, 051, 052, 053 | orange (399..411, 103..110, .., 143) | on the upper part of the blue barrel under the hand | wrong boxes gone (4) |

**11 wrong boxes gone and 2 right ones lost (3 on `combined`): the verifier fails "loses no right box on the campus
recordings".** (`r2_pan` 034, the same sliver one frame earlier, is kept.) `combined+verify2` lists the same boxes.

## Black-table clip (described, not judged)

Against `before`, every arm from `stack` on: 1 box appears, frame 038, on the blue barrel: right. Against `stack`:
nothing changes for `combined`, `reduced`, `reduced+thin`, `combined+thin`. `combined+cover` (report only): 24 boxes
appear: 18 on the blue barrel, tight; 6 on the orange barrel, of which five (frames 029, 031, 032, 034, 036) are cover
boxes that hold the barrel and run a barrel's width over the empty table to its left. The verifier removes the right
box of frame 038 (the barrel is only partly painted under the window glare).

## Wood clip (described, not judged; the orange table is parked as extreme)

Against `before`, every arm from `stack` on: 4 boxes appear and 2 disappear, all of them wrong orange boxes on the
BLUE barrel (the table-colored light paints its lower half orange): frame 006 two replace one, 019 one moved 21 px,
024 one more beside a wrong box `before` already draws. Against `stack` nothing changes (`combined+cover`: one wrong
box gone). The verifier removes 37 boxes there, each a box on the upper half of the blue barrel only.
