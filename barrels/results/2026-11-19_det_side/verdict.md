# Verdict against the pre-registered rule (round 2; round 1 in `round1/`, part a of round 2 in `round2a/`)

Rule: `experiments/2026-11-19_det_side/PREREG.md` and its addendum. Numbers: `summary.md`, `scenarios.csv`,
`never_regress.md`, `report_<arm>/`, `recordings.md`, `by_eye.md`. Found / barrels (false boxes). `base` = the
defaults of 2026-11-18 (`stripe_join`, `cap_behind` on; `stripe_w_min` 0.4).

| | base | side (B) | seam (A) | **side+seam (A, B)** | round-1 side | old_side (report only) |
|---|---|---|---|---|---|---|
| 1 perfect masks | 28 / 29 (0) | 28 (0) | 28 (0) | **28 (0)** | 28 (0) | 28 (0) |
| 2 light | 141 / 145 (0) | 141 (0) | 141 (0) | **141 (0)** | 141 (0) | 141 (0) |
| 2 medium | 64 / 145 (22) | 99 (1) | 64 (22) | **99 (1)** | 99 (1) | 99 (7) |
| 2 heavy | 13 / 145 (2) | 21 (0) | 13 (2) | **21 (0)** | 21 (0) | 20 (0) |
| 3a CAMPUS | 34 / 35 (0) | 35 (0) | 34 (0) | **35 (0)** | 35 (0) | 35 (0) |
| 3b BLACK, label thresholds | 19 / 26 (2) | 19 (2) | 19 (2) | **19 (2)** | 19 (2) | 19 (2) |
| 3c wood cool, label thresholds (report only) | 25 / 42 (7) | 27 (7) | 25 (7) | 27 (7) | 27 (7) | 28 (8) |
| stripe highlight 0.15 alone (report only) | 117 / 145 (16) | 132 (3) | 117 (16) | 132 (3) | 132 (3) | 134 (7) |
| stripe highlight 0.3 alone (report only) | 90 / 145 (38) | 135 (1) | 90 (38) | 135 (1) | 135 (2) | 133 (6) |
| stripe breaks 2 × 0.08 alone (report only) | 93 / 145 (25) | 132 (2) | 93 (25) | 132 (2) | 131 (2) | 135 (8) |
| top highlight 0.7 × 0.4 alone (report only) | 127 / 145 (5) | 132 (8) | 127 (5) | 132 (8) | 131 (11) | 140 (12) |
| edges 2 px alone (report only) | 95 / 145 (0) | 100 (0) | 105 (0) | 110 (0) | 100 (0) | 100 (5) |
| eval table HOME, found / missed / false, score | 27 / 2 / 0, 0.97 | same | same | **27 / 2 / 0, 0.97** | same | same |
| eval table CAMPUS | 34 / 1 / 0, 0.99 | 35 / 0 / 0, 1.00 | 34 / 1 / 0 | **35 / 0 / 0, 1.00** | 35 / 0 / 0 | 35 / 0 / 0 |
| eval table BLACK (report only) | 3 / 23 / 1 | 5 / 21 / 1 | 3 / 23 / 1 | 5 / 21 / 1 | 5 / 21 / 1 | 5 / 21 / 1 |
| eval table wood, brightness 3 and 6 (report only) | 7 / 119 / 4 | same | same | same | same | same |
| eval table wood, brightness 1 (report only) | 0 / 63 / 0 | same | same | same | same | same |
| eval table Dave (indicative) | 12 / 22 / 2 | same | same | same | same | same |
| campus clips: boxes appearing / of them wrong; disappearing | | 4 / 0; 0 | 0 / 0; 0 | **4 / 0; 0** | 4 / 0; 0 | 4 / 0; 0 |
| black clip (report only): appearing / wrong | | 1 / 0 | 0 / 0 | 1 / 0 | 1 / 0 | 3 / 2 |
| wood clip (report only): appearing / wrong; disappearing | | 4 / 4; 2 | 0 / 0; 0 | 4 / 4; 2 | 2 / 2; 1 | 1 / 1; 0 |

| rule | side (B) | seam (A) | side+seam (A, B) |
|---|---|---|---|
| 1 never regress (every HOME and CAMPUS scenario row; no box on any negative frame of any set) | pass | pass | pass |
| 2 level 1 not lower; level 2 not lower at any severity, no more false boxes; 3a, 3b not lower, no more false boxes; campus `occl_02` found | pass | pass (`occl_02` not asked of it) | pass |
| 3 campus clips by eye: no new wrong box, no right box lost | pass | pass | pass |
| addendum: not worse than round-1 `side` on any judged row | pass (equal) | not asked | pass (equal) |

**`side+seam` with corrections A and B passes. By the adoption order of the addendum, `side_hidden` and
`seam_height` are on by default on `wip/detector-side`.**

What each part contributes on the judged rows: `side_hidden` carries all of it (campus `occl_02`; medium 64 → 99
with 22 → 1 false boxes; heavy 13 → 21 with 2 → 0). `seam_height`, limited by correction A to stripes seen whole,
changes no judged row; it adds 10 barrels of 145 when edges are eaten by 2 px and nothing else is damaged, and
changes no frame of the recordings. Round 1's `seam_height` (no limit) found more (edges 2 px 125; Dave 18 of 34;
3b 20 of 26) and drew two wrong boxes under a hand in a campus clip.

What correction B changed against round-1 `side`: nothing on a judged row; under a wide highlight on the upper body
alone 8 false boxes instead of 11 (base 5); one more wrong box on the wood clip.

Not fixed, with the reason:

- A barrel hidden by a straight upright edge with under 0.4 of its stripe showing (no side has a reason).
- The orange barrel of the black clip under glare (`frame_008`, `frame_037`): stripe and body painted on the left
  0.4 only; no box (before: none; `old_side`: a wrong one).
- HOME `cluster_01`, the middle orange barrel (the one miss on the perfect masks): a wedge of its top between two
  blue barrels; no stripe, no side, no bottom. No box on purpose: the size could only come from the top row, whose
  predicted bottom is 4 to 7 px low with the provisional camera.
- HOME `cluster_01`, the left orange barrel on the real segmentation (the second eval-table miss): the cap is
  found, its bottom from the top row is 173 where the seen orange ends at 163 (tolerance 8), and with 173 the blue
  barrel in front no longer stands nearer. `probe.py cluster_01 --set HOME --level loso --tilt 21.8` (horizon row
  80 instead of 76) finds it: (315, 118, 361, 163) against the hand-drawn (313, 115, 356, 164). The calibration's
  miss (TODO A4).
- Heavy damage (21 of 145), the black-table misses of 3b (glare at the left frame edge, a 3 px stripe, a
  reflection painted as body), the 7 px bottom on black `occl_04` against a hand-estimated label.
