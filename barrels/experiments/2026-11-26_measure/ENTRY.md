# ENTRY.md — text ready to paste (branch `wip/measure`, 2026-11-26)

`TODO.md`, `STATUS.md`, `EXPERIMENTS.md` and `DECISIONS.md` were not edited on this branch (parallel branches edit
them). Below: three entries for `EXPERIMENTS.md`, the decision record for `DECISIONS.md`, and the lines for `TODO.md`
and `STATUS.md`. Everything is train frames only; no test frame was opened, scored or listed.

---

## For `EXPERIMENTS.md`

### 2026-11-26 — M1: every placement counted once, a misplaced box counted once (`experiments/2026-11-26_measure`)

- **Question.** The review found that one arrangement shot under five lamp settings counts as five times as many
  barrels, and that a box on a real barrel that fails the strict rule is charged as a miss plus a false box. What do
  the numbers say when both are fixed? The strict rule itself is not changed.
- **Method** (PREREG written first). A placement = one barrel in one arrangement; it counts the share of its lights in
  which it is found. Second accounting: each barrel found / found with the box off / missed; each box on its barrel /
  wrong color / second box / on nothing; "on a barrel" = at least half of the smaller of the two boxes lies inside the
  other. The vendor is assumed to find every barrel on the two white tables without vendor files (Tanush, 2026-11-26);
  those rows are marked ASSUMED. Code: `src/barrels/counting.py`, `report.py --places`.
  `python barrels/experiments/2026-11-26_measure/run.py`.
- **Data.** Train frames. Measured: the 15 new ordinary conditions with vendor files, 117 frames, 243 barrels = 108
  placements in 47 arrangements at 6 places. Assumed: home and campus, 37 frames, 64 placements.
- **Checks, all pass.** Found equals the v2 rule's hits on all 285 frame × arm pairs. The old numbers are reproduced
  exactly: ours 148 and the vendor 177 of 243; HOME 28 of 29; CAMPUS 35 of 35. Per-frame counts equal the old table's.
- **Result** (found = strict, per placement; in brackets per frame):

| place | placements (lights) | ours found | ours box off | ours on nothing | vendor found | vendor box off | vendor on nothing |
|---|---:|---:|---:|---:|---:|---:|---:|
| ABP gray | 16 (1) | 10.0 (10) | 1.0 | 0 | 16.0 (16) | 0.0 | 0 |
| bathroom floor | 15 (4) | 4.0 (16) | 0.0 | 0 | 7.0 (28) | 0.8 | 0 |
| glass table | 15 (5) | 14.8 (74) | 0.2 | 3 | 12.0 (60) | 2.8 | 6 |
| ottoman | 15 (3) | 3.0 (9) | 0.0 | 1 | 12.3 (37) | 0.7 | 0 |
| pale wood | 15 (1) | 13.0 (13) | 0.0 | 1 | 12.0 (12) | 1.0 | 0 |
| ABP white (occlusion set) | 32 (1) | 26.0 (26) | 0.0 | 0 | 24.0 (24) | 3.0 | 1 |
| **measured, 6 places** | **108 (15)** | **70.8 (148)** | **1.2** | **5** | **83.3 (177)** | **8.2** | **7** |
| campus, vendor ASSUMED | 35 (1) | 35.0 (35) | 0.0 | 0 | 35.0* | | |
| home, vendor ASSUMED | 29 (1) | 28.0 (28) | 0.0 | 0 | 29.0* | | |
| **measured + ASSUMED** | **172 (17)** | **133.8 (211)** | **1.2** | **5** | **147.3\*** | **8.2** | **7** |

- **Takeaway.**
  - Per placement the vendor is ahead on the measured places, 83.3 against 70.8 of 108. Found either way (strict, or
    with the box off): 91.5 against 72.0.
  - The vendor's 30 "false boxes" were 23 boxes on a barrel that fail the strict rule and 7 boxes on nothing; all 7
    are on empty frames. Ours: 2 and 5, none on an empty frame.
  - The glass table is 15 placements, not 75 barrels. "74 against 60" is 14.8 against 12.0, and the vendor has 2.8
    more with the box off.
  - No winner is named for a single condition.
  - The test for "on a barrel" does not matter on today's frames: with the audit's "position" rule not one frame
    changes; with "overlap", 5 of the vendor's 23 fall back to "miss plus a box on nothing".
- **Caveat.** The assumption (vendor perfect on white) is an assumption. The one white table with vendor files, the
  ABP occlusion set, has the vendor at 24 of 32.
- **Next.** Tanush's word on the definition (decision record below). Shoot the home white table with vendor files.

### 2026-11-26 — M2: the noise floor of the counts (`experiments/2026-11-26_noise_floor`)

- **Question.** How much do the counts move under a change that means nothing? The answer is the margin of the
  never-regress check and of the pass rule.
- **Method** (PREREG first; one addendum, dated, before any candidate was judged). The fixed color model with one of
  its seven numbers moved one step (hue edges ±1, saturation floors ±3, brightness floor ±2): 14 neighbours (set A).
  12 seeded moves of several numbers at once (set B). 12 more that are never used for a margin (set C). Today's
  detector, every train frame, HOME with the model as it is. `python barrels/experiments/2026-11-26_noise_floor/run.py`
  (2 minutes). It writes `results/baseline/margins.json`.
- **Data.** 261 train frames, 28 conditions, 10 places. The ordinary conditions: 154 frames, 172 placements, 8 places.
- **Result** (absolute change in found: median / 90th percentile / maximum):

| level | one step (14) | several at once (12) |
|---|---|---|
| one ordinary condition, barrels | 0 / 0 / 6 | 0 / 2 / 6 |
| one place, placements | 0 / 0.33 / 6 | 0.22 / 1.33 / 6 |
| the ordinary conditions together, placements | 0.67 / 3.58 / 6.20 | 4.59 / 8.78 / 10.92 |
| boxes not on their barrel, together | 0.2 / 1.0 / 1.25 | 0.77 / 1.27 / 1.85 |

- **Takeaway.**
  - One barrel flipping "for no reason" is the normal case at a condition. Six can flip: the ABP gray table sits on a
    hue edge (orange hue low 3 → 4 costs it 6 of 16 placements, 3 → 2 gains it 4).
  - Over everything, a change that means nothing moves found by up to 10.92 placements down and 4.00 up. It is
    one-sided: 15 of 26 neighbours lose, 8 gain. The fixed model was picked for scoring well.
  - Small changes add up: with margins from one step alone, 6 of 12 joint moves were called FAIL. So the margins are
    taken over sets A and B (the registered rule 3).
  - No neighbour, of 38, puts a box on a clean empty frame. The zero for clean empty frames can stay.
  - On the 12 unseen moves (set C) the pass rule called 2 (one PASS at +5.4, one FAIL on boxes); the never-regress
    check failed none.
- **The addendum, stated plainly.** The PREREG said: a margin is the largest *absolute* change. The first run showed
  the one-sidedness. The addendum, written before any candidate was judged, takes one margin per direction (a gain
  against the largest gain, a loss against the largest loss). Both versions are stored, and the sanity checks give the
  verdict under both. It changes one verdict: see the next entry.
- **Next.** Re-run the script whenever the default color model or detector changes.

### 2026-11-26 — M3: the standard pass rule and its sanity checks (`experiments/2026-11-26_judge`)

- **Question.** Does one written rule with measured margins say sensible things about cases we know?
- **Method** (PREREG first). The rule: `docs/EVAL.md`, "The standard pass rule (2026-11-26)"; code `src/barrels/judge.py`,
  command `tools/judge.py`. Baseline: today's default. `python barrels/experiments/2026-11-26_judge/run.py`.
- **Data.** The ordinary train conditions: 154 frames, 172 placements, 8 places. One judge run: 25 s.
- **Result.**

| candidate | found, placements | per frame | boxes not on their barrel | verdict | with the margins as first registered |
|---|---|---|---|---|---|
| today against itself | 133.8 → 133.8 | 211 → 211 | 1.9 → 1.9 | NO CLEAR DIFFERENCE, nothing changed | the same |
| 14 one-step changes, 12 joint moves | −10.9 to +4.0 | | | 26 of 26 NO CLEAR DIFFERENCE (by construction) | |
| 12 unseen joint moves | −9.3 to +5.4 | | | 10 of 12 NO CLEAR DIFFERENCE; 1 PASS, 1 FAIL | 11 of 12 |
| hand thresholds per condition (in-sample) | 133.8 → 156.8 | 211 → 281 | 1.9 → 1.5 | **PASS** | PASS |
| blue follows the light, whole frame (C2), leave one place out | 133.8 → 139.7 | 211 → 233 | 1.9 → 3.1 | **PASS** | NO CLEAR DIFFERENCE |
| blue follows the light, above the horizon (C2b), leave one place out | 133.8 → 137.0 | 211 → 222 | 1.9 → 2.9 | NO CLEAR DIFFERENCE | NO CLEAR DIFFERENCE |

- **Takeaway.**
  - The two required answers hold: today against itself changes nothing; the hand thresholds pass (the old rule failed
    them on all three clauses). 71 barrels gained, 1 lost (pale wood, at its margin).
  - The light rule C2 passes under the rule as used: +5.9 placements, all at the bathroom floor (+4.2 of 15) and the
    ottoman (+1.7 of 15), 22 barrels gained, none lost, boxes not on their barrel +1.2 (margin 1.85), one more box on
    an empty frame with clutter (0.2, margin 1.00). **This PASS is close to the margin and should be read as weak:** it
    is 1.9 placements above it, one unseen change that means nothing gained 5.4 and passed too, and with the margins
    as first registered it is NO CLEAR DIFFERENCE. The fold that held out the bathroom floor picked another setting
    than the other seven.
  - C2b (the round-2 version) gains 3.2 placements: no clear difference.
- **Next.** Every later experiment is judged with `tools/judge.py`. C3 (a fresh try of the light rule) can start from
  the C2 pages in `results/2026-11-26_judge/blue_follows_the_light__c2/`.

---

## For `DECISIONS.md`

### 2026-11-26 — How results are counted and judged (proposed on `wip/measure`; needs Tanush's word)

- **Proposed** (each follows a decision Tanush took on 2026-11-26; the numbers and definitions are the new part):
  1. **Counting.** Results are reported per placement and by place, with the placements each number rests on. The
     count per frame stays beside it. The strict v2 rule is unchanged.
  2. **A misplaced box counts once.** A box is on a barrel when at least half of the smaller of the two boxes lies
     inside the other. Strict hits first; then found with the box off; boxes left are wrong color, second box or on
     nothing. The same for ours and for the vendor.
  3. **The vendor on white tables** is shown as an ASSUMED row (home, campus), never inside a measured total.
  4. **Margins are measured, not chosen:** the largest change, per direction, that a change which means nothing (one
     step of one color number, or several at once) produced at that level; never less than one whole unit. Stored in
     `results/baseline/margins.json`; re-measured when the default changes.
  5. **Never-regress with a margin.** Protected sets judged on totals; a set fails only beyond its margin (1 placement
     and 1 box; the cool-lamp bathroom 5 placements); every changed barrel listed; a new box on a clean empty frame
     still fails outright. Protected from now on: HOME, CAMPUS, the glass table, pale wood, the ABP white occlusion
     set, the bathroom under the cool lamp. The stored baseline is not replaced by a lower run without `--force`.
  6. **One pass rule for experiments** (`tools/judge.py`): PASS / FAIL / NO CLEAR DIFFERENCE from the four clauses of
     `EVAL.md`; fitted candidates leave one place out.
- **Why.** The review: sample sizes 3 to 5 times smaller than they looked; a comparison with the vendor that depended
  on a double charge; a gate and pass rules tighter than one hue unit.
- **Alternatives, and what was not taken.**
  - *"On a barrel" by IoU ≥ 0.5:* keeps the double charge for a box around the visible half of a hidden barrel.
    *By center distance:* depends on the true width and is not nested with the strict rule. On today's frames the
    chosen test and the center test agree on every box.
  - *One margin for both directions* (as first registered: 10.92 placements). Not taken, because no change that means
    nothing gained more than 4.00. **This choice changes one verdict** (the light rule C2: PASS instead of NO CLEAR
    DIFFERENCE). If you prefer the cautious version: one line in `margins.json` (`found_gain`), or use the block
    `as_first_registered`.
  - *The 90th percentile instead of the maximum:* a rule with four clauses would then call one or two changes that
    mean nothing in every clause.
  - *Not extending the protected list* (the review's advice: these sets were picked where we beat the vendor under a
    contested rule, and a list that only grows makes every change harder). Extended anyway, as the final report of
    2026-11-25 proposed and as this task asked; the two objections are answered by the form: a set under five lights
    counts 15 placements, not 75 barrels, and a set fails only beyond a margin. To drop a set, delete its line in
    `protected.json`.
- **Known weak points.** 172 placements at 8 places: a gain under 4 placements is invisible. The ABP gray table has a
  margin of 6 of 16. The rule called 2 of 12 unseen changes that mean nothing. The neighbours of the fixed model are
  small real changes, not random noise.
- **Who.** Proposed by Claude (measurement session, 2026-11-26) on the lines Tanush set that day. Awaiting the
  walkthrough.

---

## For `TODO.md` ("Now", section M)

- **M1** done on `wip/measure` (awaits the walkthrough): `counting.py`, `report.py --places`; headline table
  `results/2026-11-26_measure/summary.md`.
- **M2** done on `wip/measure`: noise floor measured (`results/2026-11-26_noise_floor/summary.md`); `--gate` with
  margins; six protected sets; passes on today's defaults.
- **M3** done on `wip/measure`: `tools/judge.py`, `judge.py`; sanity checks `results/2026-11-26_judge/summary.md`.
- **New, for "Data and Dave":** shoot the home white table with vendor files (9 shots; three times each would also
  give a shot-to-shot noise floor), so the ASSUMED rows become measured.
- **New, for C3:** the light rule C2 passes the new rule leave one place out, close to the margin. A fresh try should
  aim to clear the margin by more and to remove the 5 extra boxes.

## For `STATUS.md`

- How results are counted since 2026-11-26: per placement and by place; strict = the v2 rule, unchanged; a misplaced
  box once. Ours 70.8 against the vendor's 83.3 of 108 placements on the six measured places (148 against 177 of 243
  per frame); with the two assumed white tables 133.8 against 147.3* of 172.
- The never-regress check has margins and six protected sets; it passes on today's defaults.
- Experiments are judged by `python barrels/tools/judge.py` (PASS / FAIL / NO CLEAR DIFFERENCE; about 25 s).
- Tests: see the commit message of `wip/measure` for the count.
