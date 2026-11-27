## 2026-11-27 — The color methods fused by what each is good at, not stacked (branch `wip/exp-fusion`; pre-registered, two rounds; nothing adopted)

**Question.** Tanush: can contrast be combined with peaks, bluer-than-the-light and the others in a careful way, so that
together they find more, without false boxes? Yesterday's stacks added 0.2 to 2.7 placements and several failed on
boxes. Here one method proposes, the others are asked only about that box, and the shape checks reject traps.

**Answer.** A careful fusion finds **1.8 placements more than contrast alone** (157.1 against 155.3 of 172, held out).
That is inside the noise (+4.0 is needed). Its real gain is fewer false boxes: **9 per frame become 4**. But most of
that comes from the shape checks alone, not from the fusion. On the black table, which no frame here was judged on,
it finds **12 of 26 where contrast finds 5**.

**Method.**
- Branch `wip/exp-fusion`: `wip/exp-bluer-geom`, `wip/exp-peaks` and `wip/exp-combined` merged in. The seams rule
  (`wip/adopt-slack`'s code) and the bottom rule `low_uncut` (`wip/exp-bottom`) were ported to `detector.py` behind two
  off-by-default flags, `DetConfig.seams` and `DetConfig.bottom_rule`. Proof harness at defaults: IDENTICAL BOXES ON
  EVERY INPUT (5435 masks).
- `src/barrels/fusion.py` (6 tests; nothing calls it by default): the box-level rules. Proposals = boxes on no kept
  box. Clusters = proposals of several methods on the same barrel. Votes = how many methods drew it.
- `experiments/2026-11-27_fusion/`: `methods.py` loads the six methods unchanged; `fuse.py` holds the candidates and
  the fold rule; `run.py` judges them; `analysis.py`, `who.py`, `compare.py`, `timing.py` look closer.
- Each method runs at the setting **its own fold rule** picked for that held-out place (read from each branch's
  committed results). Reproduction first: contrast alone gives 155.30, with the judge's change list identical to
  `wip/exp-contrast`'s, line for line.
- The fusion's own numbers are chosen inside each fold, on the other seven places: which shape checks (off, mild,
  strong) and k, the votes needed (off, 5, 4, 3, 2). A choice must not FAIL against today nor against contrast alone
  there; the highest (found − boxes off) wins.
- `PREREG.md` was committed before any judged run (a0fbc3d). Round 2 by a dated addendum, committed after round 1
  and before round 2 ran (79d3fdb).

**Data.** Train frames only. 154 ordinary frames, 8 places, 172 placements, judged. 77 extreme frames, reported. No
test frame was loaded, viewed, scored or listed.

**The candidates.**
- F0: contrast alone (the baseline).
- F1: contrast + seams + bottom rule + shape checks. F1a: contrast + checks only. F1b: contrast + seams + bottom only.
  F1s / F1u (round 2): checks + one of the two rules.
- F2: F1, then a box of peaks / self-calibration / near-miss / bluer-than-the-light is added when k of those four
  draw it and its box passes the checks.
- F3: as F2, but the contrast response is one more voter: a contrast candidate of that color, strength 1.0 or more,
  orange part reddish, whose stripe point is inside the box. This is a weaker contrast than C1's own guards accept.
- F4: contrast says where, the others say the colors. A contrast candidate with no box gets the others' paint inside
  its predicted box; the detector runs once more.
- F5: F4, then F3's votes. F6: F5 + "tidy" (one box per barrel; no other-color box on a fixed-color barrel).
- Round 2 (F3r, F5r, F6r): a box the checks removed blocks proposals at its place. A trap stays a trap.

**Results** (leave one place out; boxes not on their barrel per arrangement, per frame in brackets).

| candidate | against today | against F0 | found, placements | per frame | gained / lost vs F0 (per frame) | boxes not on their barrel | places that moved vs F0 |
|---|---|---|---|---|---|---|---|
| today | | | 133.80 | 211 | | 1.93 (5) | |
| **F0 contrast alone** | PASS | | **155.30** | 275 | | 2.83 (9) | |
| F1 + seams + bottom + checks | PASS | NO CLEAR DIFFERENCE | 154.83 | 274 | 1 / 2 | **0.83 (3)** | glass 14.8 → 15.0; ottoman 10.0 → 9.3 |
| F1a + checks only | PASS | **PASS** (boxes) | 155.30 | 275 | 0 / 0 | **0.83 (3)** | none |
| F1b + seams + bottom only | PASS | NO CLEAR DIFFERENCE | 154.83 | 274 | 1 / 2 | 2.83 (9) | glass +0.2; ottoman −0.7 |
| F1s checks + seams | PASS | NO CLEAR DIFFERENCE | 154.97 | 274 | 0 / 1 | 0.83 (3) | ottoman −0.3 |
| F1u checks + bottom | PASS | NO CLEAR DIFFERENCE | 155.17 | 275 | 1 / 1 | 0.83 (3) | glass +0.2; ottoman −0.3 |
| F2 votes of the four others | PASS | NO CLEAR DIFFERENCE | 154.83 | 274 | 1 / 2 | 1.83 (4) | as F1 |
| F3 + the contrast response as a voter | PASS | NO CLEAR DIFFERENCE | 157.08 | 281 | 8 / 2 | 2.17 (5) | bathroom +0.2; glass +0.2; ottoman +1.3 |
| F4 contrast where, others' colors | PASS | NO CLEAR DIFFERENCE | 155.17 | 275 | 2 / 2 | 0.83 (3) | glass +0.2; ottoman −0.3 |
| F5 F4 + F3's votes | PASS | NO CLEAR DIFFERENCE | 156.83 | 280 | 7 / 2 | 2.17 (5) | glass +0.2; ottoman +1.3 |
| F6 F5 + tidy | PASS | NO CLEAR DIFFERENCE | 156.83 | 280 | 7 / 2 | 2.17 (5) | as F5 |
| **F3r** F3, removed boxes block (round 2) | PASS | **PASS** (boxes) | **157.08** | **281** | 8 / 2 | **1.17 (4)** | bathroom +0.2; glass +0.2; ottoman +1.3 |
| F5r (round 2) | PASS | PASS (boxes) | 157.08 | 281 | 8 / 2 | 1.17 (4) | as F3r |
| F6r (round 2) | PASS | PASS (boxes) | 157.08 | 281 | 8 / 2 | 1.17 (4) | as F3r |
| F3r against F1a (report only) | | NO CLEAR DIFFERENCE | 157.08 vs 155.30 | 281 vs 275 | 8 / 2 | 1.17 vs 0.83 | ottoman +1.3 |

No candidate put a box on a clean empty frame. Margins: found better above +4.0; boxes worse above +1.85, better
below −1.0. **No fusion passes the pre-registered success line** (found up by more than +4.0 against F0). F3r's PASS
against F0 is by the boxes clause: boxes down 1.66, found not lower.

- **The shape checks do the work against false boxes.** With the mild checks (picked in all 10 folds), contrast's
  9 false boxes per frame become 3: the jar on the glass table (5) and the pale-wood grain under a close-up box are
  gone. No barrel is lost on the ordinary frames. (The bluer-geom experiment's own fold picks left the jar in; its
  wider grid chose a milder label check at the glass table.)
- **Votes among the other four methods add nothing** (F2 picks k = off in 9 of 10 folds). The barrels contrast misses
  are mostly ones the others miss too.
- **The contrast response as a voter is what helps.** With it, k = 2 is picked in 8 of 10 folds: one other method's
  color plus a contrast stripe too weak or too guarded for C1 to box. Of the 8 barrels gained per frame, 7 come from
  the votes, and all 7 had the contrast vote; 4 of them had just one other method besides it (`who_F3r.md`): peaks +
  contrast at the ottoman (3), bluer + contrast at the bathroom (1). The 8th is the bottom rule's (glass).
- **The trap that came back.** In round 1, a box the checks removed (pale-wood grain) came back by votes: all four
  other methods draw today's same box, and measured in their masks it passes. Round 2 blocks it: F3 2.17 → F3r 1.17,
  nothing else changed.
- **F4 (contrast says where, others paint) adds almost nothing**: +0.33 placements over F1, at the ottoman. Where
  contrast finds a stripe but no box, the others' colors mostly do not make a box either.
- **Tidy removes nothing held out.** The second box on the bathroom barrel is not 0.8 inside the larger box, and the
  orange box on the blue bathroom barrel has no fixed-color blue box under it (its blue box came from contrast).
- **Seams and the bottom rule cost one barrel each, gain one.** Bottom rule: the very near ottoman barrel (its predicted
  bottom is 13 % too high, known from its own experiment) goes from found to box-off; a blue barrel beside the purple
  figure on glass goes from box-off to found. Seams: a blue barrel cut by the frame edge on the ottoman goes to box-off. Neither moves false
  boxes. Both are inside the noise.

**Every box not on its barrel, F3r** (ordinary frames, 4 per frame; contrast alone 9):

| frame | box | kind | contrast alone draws it | what it is (contact sheet) |
|---|---|---|---|---|
| `lampmid3_bathtile_core_01` | orange (218, 104, 256, 145) | second box | yes | the upper half of an orange barrel that has its own box |
| `lampwarm6_bathtile_core_01` | orange (465, 104, 495, 134) | wrong color | yes | an orange box on the far blue barrel, next to its blue box |
| `lampwarm6_ottoman_core_01` | orange (166, 248, 282, 480) | on nothing | yes (today too) | today's close-up box on the dark ottoman under a near orange barrel |
| `lampmid6_ottoman_core_01` | blue (120, 139, 186, 203) | second box | **no, new** | between a blue barrel and the near orange barrel: half on the blue barrel (near-miss + contrast voted) |

Gone against contrast alone: the jar with the orange lid on glass (2 frames, 3 boxes), the jar in the glass clutter
(2 frames), the pale-wood grain close-up.

**The extreme conditions** (report only; found per frame; boxes not on their barrel in brackets):

| | today | contrast alone | F1a | F3r |
|---|---|---|---|---|
| wood desk, 6 lamps (126) | 7 (4) | 79 (6) | 77 (5) | **88** (7) |
| black table (26) | 5 (0) | 5 (0) | 5 (0) | **12** (0) |
| very dark ottoman (15) | 1 (0) | 1 (0) | 1 (0) | 1 (0) |

On the black table near-miss voted for all 7 added barrels, peaks for 5, the contrast response for 4. On the wood
desk the label check costs 2 barrels per frame (as in the bluer-geom entry); the votes win back more. Two new false
boxes there: `lampmid6_wood_touch_02` (on nothing, between two touching barrels; bluer + near-miss voted) and
`lampcool3_wood_occl_01` (wrong color, on a blue barrel beside clutter; peaks + contrast voted).

**Against the vendor** (six places with vendor files; found per placement; boxes not on their barrel):

| place | today | contrast alone | F3r | vendor |
|---|---|---|---|---|
| gray table (16) | 10.0 | 15.0 | 15.0 | **16.0** |
| bathroom (15) | 4.0 | 13.5 | **13.8** | 7.0 |
| glass (15) | 14.8 | 14.8 | **15.0** | 12.0 |
| ottoman (15) | 3.0 | 10.0 | 11.3 | **12.3** |
| pale wood (15) | 13.0 | 13.0 | **13.0** | 12.0 |
| ABP white (32) | 26.0 | 26.0 | **26.0** | 24.0 |
| **six places (108)** | 70.8; 1.93 | 92.3; 2.83 | **94.1; 1.17** | 83.3; 3.00 |

F3r closes 1.3 of the 2.3 ottoman gap to the vendor. The gray table does not move (15 against 16). Train frames: our
methods were shaped on them; the vendor's was not.

**What the contact sheets show** (`results/2026-11-27_fusion/sheets/`, looked at): every gained barrel is a real
barrel, mostly ottoman barrels next to the eraser or touching another, and the black-table barrels. The losses are
box-off, not missed (near ottoman barrel, frame edge), plus one wood barrel behind a blue barrel (report only).

**Cost.** F3r runs all six methods: median 389 ms per frame, one thread, against 73 ms for contrast alone (5 times).

**Takeaway.**
1. On these frames, careful fusion does not beat contrast alone on barrels found by more than the noise: +1.8.
   What is left after contrast is mostly hidden and frame-cut barrels, which no color method reaches.
2. The shape checks are the clear win: contrast + checks keeps every barrel and cuts the false boxes from 9 to 3 per
   frame (PASS against contrast alone, on boxes).
3. The one fusion rule that helps is "a weak contrast stripe confirmed by one other method's color". It gains 8 barrels
   per frame (+1.8 placements, ottoman mostly), and 7 per frame on the black table. It costs one new false box.
4. Plain voting among methods does nothing. A trap they all draw comes back unless a removed box blocks it.
5. Caveat: every method, guard and check was shaped on these eight places. The F3r blocking rule was written after
   round 1. A new place is the clean test.

**Next.**
1. Adopt the shape checks (mild) with contrast. They are the safe part.
2. Keep F3r as the candidate to try on the next place Tanush shoots; it is the version that helps on the black table.
3. The near ottoman barrel and the frame-edge barrel: the bottom rule and the seams rule each cost one there; look at
   both before they become plain code.

**Repeat.** `PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_fusion/run.py`, then `analysis.py F3r
--sheets`, `who.py`, `compare.py F3r F1a`, `timing.py`. Held out: `python barrels/tools/judge.py --cand-fit
barrels/experiments/2026-11-27_fusion/fuse.py:fit`. Frozen (in-sample): `fuse.py:detect_frame`.
Pages: `results/2026-11-27_fusion/` (`summary.md`, `chosen.json`, `judge_*`, `vs_F0_*`, `vs_F1a_F3r`,
`analysis_F3r.md`, `analysis_F3.md`, `analysis_F1a.md`, `who_F3r.md`, `timing.md`).
