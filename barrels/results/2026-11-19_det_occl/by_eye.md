# Round 2, by eye: boxes that appear or disappear on the unlabeled recordings

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model, `base` draws 506 boxes.
Sheets: `sheets/rec_<arm>/` (ignored by git), made by `experiments/2026-11-19_det_occl/recordings.py`; the list of
boxes is `recordings.csv`, the counts `recordings.md`. Looked at 2026-11-19: all four sheets of `all` (22 changed
frames). `slice`, `slice+cover` and `all-cover` list the same 26 boxes as `all` (`recordings.csv`); `two`, `edge`,
`cap` and `edge+cap` change no frame. Round 1 is in `round1/by_eye.md`.

## Campus clips (these decide, PREREG rule 3)

| arm | appear | disappear | verdict |
|---|---|---|---|
| `edge`, `cap`, `edge+cap`, `two` | 0 | 0 | **pass.** No frame of any clip changes. The cap box on the hand of round 1 (`r4` 020) is not drawn. |
| `slice`, `slice+cover`, `all`, `all-cover` | 1 | 0 | **pass.** `r3_enter_leave` 013: the orange barrel entering at the right frame edge, box (619, 142, 640, 215), on the barrel. The 18 wrong boxes of round 1 are gone; so are the two right ones on the blue sliver at the frame edge in `r2_pan` 036 and 037 (its top is not where its row predicts). |

## Black-table clip (described, not judged)

`all`: 24 boxes appear, none disappears. 18 are the blue barrel, boxed tightly where it had no box (frames 013, 024
to 030, 032, 033, 036, 040 to 044, 046, 048, 049). 6 are on the orange barrel, whose stripe is painted on one part
only under the window glare: frame 030 a tight box; frames 029, 031, 032, 034, 036 the cover box: it holds the
whole barrel and runs about a barrel's width over the empty table to its left. The three boxes of round 1 that lay
on the empty table beside the barrel (002, 005, 013) are gone.

## Wood clip (described, not judged; the orange table is parked as extreme)

`all`: nothing appears; 1 wrong orange box on the blue barrel disappears (frame 006).
