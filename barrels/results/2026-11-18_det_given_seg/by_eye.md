# Round 2, by eye: boxes that appear or disappear on the unlabeled recordings

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model, `base` draws 499 boxes.
Sheets: `sheets/rec_<arm>/` (ignored by git), made by `experiments/2026-11-18_det_given_seg/recordings.py`; the
list of boxes is `recordings.csv`. Looked at 2026-11-18: every sheet of every arm (19 changed frames in all).
Round 1's verdict is in `round1/by_eye.md`.

| arm | appear | disappear | verdict |
|---|---|---|---|
| `cap` | 1 | 0 | **fails by the letter.** wood `frame_022`: an orange box to the right of the blue barrel's top, on the hand above it. Not a barrel. It leans on a wrong orange box that `base` already draws on that blue barrel (on the wood table the table and the hand read orange; that table is parked as extreme), but rule 5 has no exception for the wood clip. The 3 wrong boxes of round 1 on campus and wood are gone except this one. Nothing appears in the four campus clips or the black clip. |
| `join` | 0 | 1 | passes. The box that disappears (wood `frame_007`, an orange box on the blue barrel) was wrong. |
| `cap+join` | 1 | 1 | **fails by the letter**, for the same single box as `cap` (wood `frame_022`); the box that disappears was wrong. |
| `side` | 5 | 0 | passes, as in round 1 (not changed by round 2): campus `r2_pan` 034, 035, `r3_enter_leave` 014, 047, black 038, all real barrels. |
| `cap+join+side` | 9 | 1 | **fails.** Right: the 5 of `side`. Wrong: black `frame_008` and `frame_037` (the orange barrel's stripe shows on its left half only, under the window highlight; the box is drawn a barrel wide but half off the barrel to the left, on empty table); wood `frame_006` (an orange box on the right half of the blue barrel); wood `frame_022` (as `cap`). |

What the two black-table boxes show: with the lower width floor a half-visible stripe is accepted, and the rule
that decides which side of it is hidden ("the side where something barrel-colored borders the stripe") takes
the barrel's own body for an occluder. `occl_body_side` does not help there because the body on the visible
side is washed out too. A lead for later, not done here: a side counts as hidden only when a found barrel or
the frame edge is there (the test `cap_behind` uses since round 2).
