# Recordings by eye: `strict` against `start` (2026-11-24)

337 unlabeled frames (`data/recordings/`, read only). `strict` draws 516 boxes against 525; **0 boxes appear, 9
disappear**, on 7 frames. Every changed frame was looked at on `rec_vs_start/sheets/rec_strict/sheet_00.png` and
`sheet_01.png` (a disappearing box ringed in magenta).

| frame | box removed | what it was | verdict |
|---|---|---|---|
| campus `r2_pan/frame_057` | blue (274, 111, 316, 160) | a blue box on the upper half of the orange barrel (its blue stripe read with the blue packet behind) | wrong box, right to remove; the orange barrel's own box stays |
| campus `r4_hand_occlusion/frame_011` | blue (274, 105, 307, 142) | the same, on the orange barrel's top | wrong box; the orange box stays |
| campus `r4_hand_occlusion/frame_033` | orange (276, 97, 301, 124), orange (402, 104, 441, 143) | orange boxes on the hand above the orange barrel and above the blue barrel | wrong boxes (two of the "11 wrong boxes on a hand" of 2026-11-20) |
| wood `rec_..._121306` frames 018, 023, 024 (two), 026 | orange boxes 48-52 px wide on the blue barrel's upper half | the hand above read as orange body, the blue upper body as its stripe, the blue barrel's orange stripe as its lower body | wrong boxes (the wood clip's hand boxes of 2026-11-18) |

No right box disappears; both real barrels keep their boxes on every changed frame.
