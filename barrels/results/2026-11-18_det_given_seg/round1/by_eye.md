# Round 1, by eye: boxes that appear or disappear on the unlabeled recordings

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model. Sheets:
`sheets/rec_<arm>/` (ignored by git), made by `experiments/2026-11-18_det_given_seg/recordings.py`. Looked at
2026-11-18: every sheet of `cap`, `side` and `join`.

| arm | appear | disappear | verdict |
|---|---|---|---|
| `cap` | 3 | 0 | **fails.** None of the 3 is a right box. campus `r4_hand_occlusion/frame_040`: a blue box above the orange barrel, under the hand, on a 15 px patch of blue (no barrel there). wood `frame_006`: an orange box on the background above the blue barrel. wood `frame_022`: an orange box on the top half of the blue barrel, above a wrong orange box that `base` already draws. All three caps are narrower than a barrel with nothing hiding their sides. |
| `side` | 5 | 0 | passes. campus `r2_pan` 034, 035 (the blue barrel entering at the right frame edge), `r3_enter_leave` 014, 047 (the orange barrel at the right edge), black `frame_038` (the blue barrel, full box): all real barrels. The same four campus boxes as on 2026-11-11. |
| `join` | 13 | 3 | **fails.** Wrong: campus `r2_pan` 054, 059, 062 (a second, blue box inside the orange barrel: two tall slivers of its upper body were joined into a "stripe"); `r4` 000 (an orange box on the hand over the blue barrel); black 013, 014, 018, 034 (the orange barrel's stripe shows on its left half only, and the box is drawn half off the barrel to the left); wood 002, 006 (orange boxes on the blue barrel, moved). Right: black 021, 031 (the orange barrel), 046 (the blue barrel). The 3 that disappear were wrong boxes (`r4` 011, wood 006, 007). |
| `cap+join`, `cap+join+side` | 16, 31 | 3, 3 | not judged frame by frame: both arms already fail rule 1 (4 false boxes on the HOME frames, from `join`), and their changes are the union of the rows above. |
