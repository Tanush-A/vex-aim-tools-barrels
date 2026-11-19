# Round 2, part b (corrections A and B), by eye: boxes that appear or disappear on the unlabeled recordings

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model, `base` (the defaults of
2026-11-18) draws 499 boxes. Sheets: `sheets/rec_<arm>/` (ignored by git), made by
`experiments/2026-11-19_det_side/recordings.py`; the list of boxes is `recordings.csv`. Looked at 2026-11-18: both
sheets of `side+seam`; `side` lists exactly the same boxes (`recordings.csv`), `seam` changes no frame. Round 1 is in
`round1/by_eye.md`, part a of round 2 in `round2a/by_eye.md`.

## Campus clips (these decide, PREREG rule 3)

| arm | appear | disappear | verdict |
|---|---|---|---|
| `side` (B) | 4 | 0 | **passes.** `r2_pan` 034, 035: the blue barrel entering at the right frame edge, box (622, 123, 640, 170) and (624, 123, 640, 171); `r3_enter_leave` 014, 047: the orange barrel entering at the right frame edge, (611, 138, 640, 216) and (614, 141, 640, 220). The same four boxes, to the pixel, as round 1's `side`. All on real barrels. |
| `seam` (A) | 0 | 0 | **passes.** Nothing changes; the two boxes under the hand of round 1 are gone. |
| `side+seam` (A and B) | 4 | 0 | **passes.** The four boxes of `side`. No right box of round-1 `side` is lost; nothing under the hand in `r4_hand_occlusion`. |
| `old_side` (report only) | 4 | 0 | the same four barrels, boxes 15 to 21 px wider on the table side. |

## Black-table clip (described, not judged)

`side`, `side+seam`: 1 box appears, `frame_038`, on the blue barrel: right. The orange barrel in `frame_008` and
`frame_037` (stripe and body painted on its left 0.4 only, under the window glare) gets no box: `old_side` drew one
there half off the barrel, on empty table. A miss instead of a wrong box.

## Wood clip (described, not judged; the orange table is parked as extreme)

`side`, `side+seam`: 4 boxes appear, 2 disappear, all of them wrong orange boxes on the blue barrel (on this table
the blue reads partly orange and the hand reads orange). `frame_006`: two replace one of `base`. `frame_019`: one
replaces one, 21 px to the left. `frame_024`: one more beside the wrong box `base` already draws. Against round 1
this is one more wrong box (024) and one moved (019). `seam`: nothing changes.
