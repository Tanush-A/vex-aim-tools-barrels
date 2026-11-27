# The stripe by contrast adopted: the proof

Made by `experiments/2026-11-27_adopt_contrast/prove.py`. Train frames only.

## A. The new default against the judged code, every train frame

Reference: `contrast.py` at 5ea663a (wip/exp-combined), `candidate.py` / `common.py` at d27e489 (wip/exp-contrast), `candidate.detect_frame` (BEST: add mode, strength floor 1.15, absolute check 0.8, extent 0.15). Both on today's detector.

- frames: 231 (154 ordinary, 77 extreme, 0 unlisted)
- boxes of the new default: 392, of them added by the contrast stage: 149
- frames whose boxes differ: 0
- time, all frames: judged code 20.9 s, new default 19.5 s

RESULT A: IDENTICAL BOXES ON EVERY FRAME

## B. The judged numbers, on the detector the experiment was judged on

`detector.py` at c6b39ab (before the seam reading). Ordinary train conditions, the standard judge.

| | found, placements | per frame | boxes not on their barrel |
|---|---:|---:|---:|
| previous default (no contrast) | 133.80 | 211 | 1.93 |
| new default | 156.97 | 278 | 2.43 |
| expected (the experiment's insample.md, 'the pick') | 133.8 -> 156.97 | 211 -> 278 | 1.93 -> 2.43 |

Bathroom / ottoman / gray table: 13.5 / 10.7 / 15.0 (expected 13.5 / 10.7 / 15.0).

Verdict PASS; 67 barrels gained, 0 lost.

RESULT B: THE JUDGED NUMBERS, EXACTLY

## C. The judge as it runs now (today's detector, with the seam reading)

| | found, placements | per frame | boxes not on their barrel |
|---|---:|---:|---:|
| previous default (no contrast) | 135.38 | 214 | 1.93 |
| new default | 156.63 | 277 | 2.43 |

Verdict **PASS**; 63 barrels gained, 0 lost. Pages: `judge_vs_previous/`.

RESULT C: PASS

## D. The seam reading and the contrast stage together (report only)

The new default on today's detector (C) against the new default on the detector before the seam reading (B), ordinary train frames: every frame whose barrels change state.

- `4A8B_lampmid6_ottoman_edge_01`: barrels ['found', 'found'] -> ['off', 'found']; boxes ['found', 'found'] -> ['off', 'found']

1 frames differ.

ALL: PASS
