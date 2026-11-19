# Verdict against the pre-registered rule (one round)

Rule: `experiments/2026-11-19_det_bottom/PREREG.md`. Numbers: `summary.md`, `scenarios.csv`, `never_regress.md`,
`report_bottom/`, `recordings.md`, `by_eye.md`, `bottom_edges.md`. Found / barrels (false boxes). `base` = the
defaults of `wip/detector-side` (`stripe_join`, `cap_behind`, `side_hidden`, `seam_height` on); `bottom` = `base`
+ `cap_seen_bottom`. Baseline alone, run before the PREREG: `step1_baseline/`.

| | base | **bottom** |
|---|---|---|
| eval table HOME, found / missed / false | 27 / 2 / 0 | **28 / 1 / 0** |
| eval table CAMPUS | 35 / 0 / 0 | 35 / 0 / 0 |
| eval table BLACK (report only) | 5 / 21 / 1 | 5 / 21 / 1 |
| eval table wood, 9 lamp settings (report only) | 7 / 182 / 4 | 7 / 182 / 4 |
| eval table Dave (indicative) | 12 / 22 / 2 | 12 / 22 / 2 |
| 1 perfect masks | 28 / 29 (0) | 28 / 29 (0) |
| 2 light | 141 / 145 (0) | **143 / 145 (0)** |
| 2 medium | 99 / 145 (1) | 99 / 145 (1) |
| 2 heavy | 21 / 145 (0) | 21 / 145 (0) |
| 3a CAMPUS | 35 / 35 (0) | 35 / 35 (0) |
| 3b BLACK, label thresholds | 19 / 26 (2) | 19 / 26 (2) |
| 3c wood cool, label thresholds (report only) | 27 / 42 (7) | 27 / 42 (7) |
| edges 1 px alone (report only) | 140 / 145 (0) | 145 / 145 (0) |
| stripe highlight 0.3 alone (report only) | 135 / 145 (1) | 136 / 145 (0) |
| stripe breaks 2 × 0.08 alone (report only) | 132 / 145 (2) | 133 / 145 (1) |
| every other single damage (report only) | | unchanged |
| recordings, 337 frames: boxes appearing; disappearing | 506 boxes | 0; 0 |

| rule | bottom |
|---|---|
| (a) never regress: no HOME or CAMPUS scenario row loses a barrel or gains a false box; no box on any negative frame of any set | **pass** (one row changes: HOME `cluster` 6 / 2 / 0 → 7 / 1 / 0) |
| (b) levels 1, 2 light / medium / heavy, 3a, 3b: found not lower, false boxes not higher | **pass** (light 141 → 143, the rest equal) |
| (c) recordings by eye: no new wrong box, no right box lost | **pass** (no frame changes; nothing to look at) |
| (d) reported: bottom edges, HOME and CAMPUS | median distance from the hand-drawn bottom 1.0 px and 2.0 px, unchanged; boxes inside the v2 bottom tolerance 27 of 27 → 28 of 28 (HOME), 35 of 35 (CAMPUS) |

**`bottom` passes. `cap_seen_bottom` is on by default on `wip/detector-bottom`.**

## What changed, box by box (`per_barrel.csv`)

- HOME `cluster_01`, the left orange barrel (the second eval-table miss): found, box (315, 118, 366, 162) against
  the hand-drawn (313, 115, 356, 164); overlap 0.71, bottom 2 px high (tolerance 4.9). The same barrel is the gain
  on the damaged hand masks: light damage seeds 0 and 3, and all 5 seeds of "edges eaten by 1 px" (one row of
  erosion moves its seen end out of the 8 px tolerance around the top-row bottom).
- Two more, in report-only rows: `far_02` seed 2 under a stripe highlight and the middle barrel of `cluster_01`
  seed 3 under stripe breaks. In both a cap box was drawn with the top-row bottom, 7 to 8 px below the label (a miss
  and a false box under the v2 rule); with the seen end it is counted found.
- Nothing is lost anywhere and no box appears on a recording.

## Does the few-pixel bottom error matter? (`bottom_edges.md`)

- Of the 62 boxes `base` draws on HOME and CAMPUS, 55 have a seen bottom, 5 end at the frame edge and 2 are caps
  seen whole. **No drawn box takes its bottom from the top row** (nor from the stripe row). All 62 are inside the v2
  bottom tolerance.
- On those same boxes the top-row bottom would be a median 7.0 px (HOME) and 5.8 px (CAMPUS) from the hand-drawn
  one, against 1.0 and 2.0 px as drawn. The bias is real; the detector already avoids it by using what it sees.
- It changed **which barrels are found** in one barrel of the 64 on HOME and CAMPUS (found now), and in no frame of
  the 337 recorded ones. It does not change how exact the drawn boxes are.

## Not fixed, with the reason

- HOME `cluster_01`, the middle orange barrel: a wedge of its top between two blue barrels; no side, no stripe, no
  seen end. No box on purpose (unchanged).
- A narrow cap with no seen end of its own color keeps the top-row bottom: nothing better is seen. None occurs on
  HOME, CAMPUS or the recordings.
- `resolve_bottom` (the stripeless pieces of step 3) still replaces a disagreeing bottom with the top-row one. No
  drawn box on HOME or CAMPUS comes from it, so it was left alone.
