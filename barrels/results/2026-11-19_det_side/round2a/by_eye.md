# Round 2, part a (correction A on round 1's `side_hidden`), by eye: the unlabeled recordings

337 frames, adopted color model, `base` (today's defaults) draws 499 boxes. Sheets: `round2a/sheets/rec_<arm>/`
(ignored by git); the list of boxes is `recordings.csv`. Looked at 2026-11-18: the one sheet of `side+seam`
(`seam` changes no frame, so it has no sheet).

## Campus clips (these decide, PREREG rule 3)

| arm | appear | disappear | verdict |
|---|---|---|---|
| `seam` (A) | 0 | 0 | **passes.** The two boxes under the hand in `r4_hand_occlusion` (019, 021) are gone: both slivers are under 0.8 of a barrel long and are no longer read a second time. Nothing else changes. |
| `side+seam` (A, round 1's `side_hidden`) | 4 | 0 | **passes.** The same four boxes as round 1's `side`, same coordinates: `r2_pan` 034, 035 (the blue barrel entering at the right frame edge), `r3_enter_leave` 014, 047 (the orange barrel entering at the right frame edge). All on real barrels, from the seen left edge to the frame edge. No right box of round-1 `side` is lost. |

## Black-table clip (described, not judged)

`side+seam`: 1 box appears, `frame_038`, on the blue barrel: right (as round-1 `side`). The three right boxes round 1's
`side+seam` added from a 22 px patch of stripe (016, 017, 031) are not drawn any more: the cost of A written in the
addendum. `seam`: nothing changes.

## Wood clip (described, not judged)

`side+seam`: `frame_006` as in round 1 (two wrong orange boxes on the blue barrel replace one wrong orange box of
`base`). `seam`: nothing changes.
