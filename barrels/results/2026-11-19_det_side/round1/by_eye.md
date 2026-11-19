# Round 1, by eye: boxes that appear or disappear on the unlabeled recordings

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model, `base` (today's defaults)
draws 499 boxes. Sheets: `sheets/rec_<arm>/` (ignored by git), made by
`experiments/2026-11-19_det_side/recordings.py`; the list of boxes is `recordings.csv`. Looked at 2026-11-18: every
sheet of `side`, `seam` and `side+seam`, and frame 010 of r4 (no hand yet) for where the barrels stand.

## Campus clips (these decide, PREREG rule 3)

| arm | appear | disappear | verdict |
|---|---|---|---|
| `side` | 4 | 0 | **passes.** `r2_pan` 034, 035: the blue barrel entering at the right frame edge; `r3_enter_leave` 014, 047: the orange barrel entering at the right frame edge. Each box starts at the barrel's seen left edge and ends at the frame edge (`old_side` drew the same four, 21 to 15 px wider on the table side). |
| `seam` | 2 | 0 | **fails.** `r4_hand_occlusion` 019: an orange box (391, 115, 439, 167) where the **blue** barrel stands (400 to 442 in frame 010). What it took for a stripe is the blue barrel's body seen through the gap between two fingers, 30 px wide and 4 rows tall, between skin above and below (skin is painted orange). 021: an orange box (256, 112, 300, 159) on the orange barrel (272 to 312), a third off it to the left; the "stripe" is 18 px of its real stripe seen through the same gap. |
| `side+seam` | 6 | 0 | **fails**, for the two boxes of `seam`; the other four are those of `side`. |
| `old_side` (report only) | 4 | 0 | the four frame-edge barrels. |

## Black-table clip (described, not judged)

- `side`: 1 box appears, `frame_038`, on the blue barrel: right. The two boxes `old_side` draws half off the orange
  barrel (`frame_008`, `frame_037`) are **not drawn**: its stripe is painted on the left 0.36 to 0.40 of the
  barrel, the body ends within the tolerance of the stripe on both sides, so no side has a reason and the stripe is
  under 0.4 of a barrel: no box. A miss, not a wrong box.
- `side+seam`: 4 boxes appear (`frame_016`, `017`, `031`, `038`), all on the blue barrel, all right. In 016, 017
  and 031 the orange stripe is painted as a patch 22 px wide and 5 rows tall at its left end; `seam` reads it as a
  stripe and `side` takes the blue body, which shows the whole width, for the box.
- `seam` alone: nothing changes.

## Wood clip (described, not judged; the orange table is parked as extreme)

- `side` and `side+seam`: `frame_006`, two orange boxes on the upper half of the blue barrel replace one wrong
  orange box that `base` draws beside it. All three are wrong: on this table the barrel's blue reads partly orange.
- `seam` alone: nothing changes.
