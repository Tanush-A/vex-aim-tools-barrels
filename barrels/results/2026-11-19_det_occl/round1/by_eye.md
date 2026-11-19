# Round 1, by eye: boxes that appear or disappear on the unlabeled recordings

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model, `base` draws 506 boxes.
Sheets: `sheets/rec_<arm>/` (ignored by git), made by `experiments/2026-11-19_det_occl/recordings.py --out round1`;
the list of boxes is `recordings.csv`. Looked at 2026-11-19: `rec_slice` sheets 00, 01, 03 and 05 (every campus
frame that changes, and a part of the black clip) and `rec_cap` sheet 00; the other arms from `recordings.csv`.

## Campus clips (these decide, PREREG rule 3)

| arm | appear | disappear | verdict |
|---|---|---|---|
| `edge` | 0 | 0 | **passes.** No frame changes. |
| `two` | 0 | 0 | **passes.** No campus frame changes. |
| `cap` | 1 | 0 | **fails.** `r4_hand_occlusion` 020: an orange cap box on the hand, above an orange box `base` already draws on the pen under the hand. Not a barrel. |
| `slice`, `slice+cover` | 21 | 0 | **fails.** Right, 3: `r3_enter_leave` 013, the orange barrel entering at the right frame edge; `r2_pan` 036 and 037, the blue barrel entering at the right edge (a sliver 10 to 13 px wide). Wrong, 18: `r2_pan` 054, 059, 061, 062 and `r4_hand_occlusion` 002, 003, 005, 006, 012, 013, 014, 023, 024, 043: a BLUE box on the upper half of the orange barrel in front of the marker box (the top of its blue stripe under the lid: a piece taller than wide, its top not where its row predicts); `r4` 000: an orange box on the hand; `r4` 046, 049, 050: an ORANGE box on the upper half of the blue barrel under the hand. |
| `all`, `all-cover` | 22 | 0 | **fails**, for the boxes of `slice` and of `cap`. |

## Black-table clip (described, not judged)

`slice`: 29 boxes appear. Right: the blue barrel (frames 013, 030, 032, 033, 036). On the orange barrel, whose
stripe is painted on one part only under the window glare: in frames 031, 032, 034, 036 the box is the cover box,
which holds the barrel and runs up to a barrel's width over the empty table beside it; in frames 002, 005, 013 the
box is a barrel wide and lies on the empty table to the LEFT of the barrel, touching only its left edge. Wrong.

## Wood clip (described, not judged; the orange table is parked as extreme)

`slice`: 16 boxes appear, 1 disappears, nearly all with an inferred edge, on the blue barrel or the hand; `two`: 1
more wrong box; `cap`: 1 wrong cap box disappears (frame 022).
