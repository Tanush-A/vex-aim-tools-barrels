## 2026-11-27 — White balance in memory, then the fixed colors (an experiment the standing rule forbids; branch `wip/exp-whitebalance`; nothing adoptable without Dave)

> **This tests something the standing rule forbids.** Dave, 2026-10-07: "never white-balance or otherwise correct
> the image". Tanush, 2026-11-27: "we can try correction too, like white balancing, worth a shot". Run as an
> experiment only, to give Tanush and Dave numbers. **Nothing here may be adopted without Dave.** No corrected image
> was written anywhere; the correction lives in memory inside the candidate and is dropped after the frame.

Plan: `experiments/2026-11-27_whitebalance/PREREG.md`, committed before part B and before any judged run. One round.
Nothing that runs by default was changed. `detector.py` and `pipeline.py` were not edited.

#### Hypothesis

1. Per frame, read the light's color from the frame, divide it out (one gain per channel), and today's fixed colors
   and detector find more barrels, held out, without boxes on things that are not barrels.
2. Written before the runs, from the color review: it helps blue under the warm lamp; it cannot fix the ottoman's
   orange (that follows the surface, not the lamp); and a full correction that brings blue back pushes orange out of
   its range under the same lamp, because the two paints move in opposite directions.

#### Method

- **The correction.** An estimator reads the light L = (R, G, B). Gains g = (mean(L) / L) ^ alpha, each held in
  [0.25, 4]. The photo times the gains, held in 0..255. Then `pipeline.segment` with the adopted model (`eb863d84`)
  and `detector.detect` with defaults. Dark (< 40) and clipped (≥ 250) pixels are never read.
- **Five estimators.** Gray world (mean of the frame). White patch (brightest 5 %). `without_loose` (brightest 5 %
  after taking out anything barrel-like; the best light reading of `wip/exp-light`). Gray world above the horizon
  (rows 0–49). Shades of gray (p-norm, p = 6).
- **Candidates.** F1–F5: full correction (alpha 1), nothing chosen. P1–P5: alpha chosen inside each fold from
  {0.25, 0.5, 0.75, 1}, no correction as the fallback; P3 (`without_loose`) the primary. U3: today's mask kept, the
  corrected paint added only where today paints nothing.
- **How alpha is chosen.** The light experiment's rule: on the other seven places, a setting the pass rule calls FAIL
  is out; the highest (Δ found − Δ boxes not on their barrel) wins; ties go to the smaller alpha.
- Code: `wb.py` (correction, estimators, callables), `measure.py` (part B), `candidates.py`, `run.py`, `sheets.py`,
  `compare.py`.

#### Data

Train frames only. Judged: 154 ordinary frames, 17 conditions, 8 places, 172 placements (307 barrels counted per
frame). Part B also on the 77 extreme and 30 excluded frames. Extreme frames printed, never judged. No test frame
was loaded, viewed, scored or listed.

#### Results

##### B. What the correction does to the paint, before any judging (`results/2026-11-27_whitebalance/measure.md`)

Share of the paint pixels the fixed model paints the right class (percent). Before → after, full correction.

| condition | orange, gray world | blue, gray world | orange, `without_loose` | blue, `without_loose` |
|---|---|---|---|---|
| bathroom, warm lamp | 99 → **4** | 0 → **98** | 99 → **9** | 0 → **95** |
| bathroom, mid 6 | 99 → 93 | 5 → 99 | 99 → 96 | 5 → 97 |
| bathroom, mid 3 | 97 → 92 | 2 → 97 | 97 → 96 | 2 → 93 |
| bathroom, cool | 96 → 97 | 38 → 99 | 96 → 98 | 38 → 98 |
| ottoman, warm | 32 → 15 | 0 → 84 | 32 → 27 | 0 → 84 |
| ottoman, mid 6 | 26 → 14 | 56 → 85 | 26 → 22 | 56 → 84 |
| ottoman, cool | 13 → 13 | 65 → 86 | 13 → 25 | 65 → 86 |
| gray table (ABP) | 31 → 43 | 95 → 96 | 31 → 32 | 95 → 95 |
| pale wood | 95 → 82 | 95 → 97 | 95 → 95 | 95 → 95 |

Over the 17 ordinary conditions (mean of the condition shares):

| setting | orange paint in | blue paint in | non-barrel painted, orange / blue | pale wood | bathroom (4 lamps) |
|---|---|---|---|---|---|
| no correction (today) | 81 | 67 | 1.3 / 0.8 | 8.8 | 2.2 |
| gray world, full | 73 | 96 | 0.3 / 1.1 | 0.8 | 0.7 |
| white patch, full | 71 | 97 | 0.6 / 11.5 | 7.8 | 6.4 |
| `without_loose`, full | 76 | 95 | 0.9 / 1.3 | 10.3 | 0.5 |
| gray above the horizon, full | 74 | 95 | 0.4 / 1.2 | 2.5 | 0.7 |
| shades of gray, full | 72 | 94 | 0.4 / 3.7 | 1.9 | 0.6 |
| gray world, half | 80 | 87 | 0.6 / 0.8 | 1.3 | 1.3 |
| `without_loose`, half | 81 | 85 | 1.4 / 0.8 | 9.5 | 2.5 |

- **The expectation holds.** Blue comes back almost everywhere (67 % → 94–97 % of blue paint). Orange goes out:
  under the warm bathroom lamp the full correction turns the orange body pink (hue 8 → −3 to −6, 99 % → 4–9 %).
- **The ottoman's orange is not fixed.** Its hue stays 15–18 after every correction (the range ends at 13).
- **Half a correction keeps both** in the warm bathroom (gray world: orange 96 %, blue 65 %).
- **Gray world takes the orange flood off the pale wood** (8.6 % → 0.2 % of the non-barrel pixels): the wood becomes
  gray. `without_loose` does not (it reads the white things on that table, so it barely corrects there).
- **The dark ottoman turns blue.** Under the warm lamp `without_loose` paints 8.3 % of the fabric blue (gray world
  2.4 %). On the very dark ottoman (extreme) gray world paints 25 % of it blue.
- **The 2026-10-07 failure, seen again:** on the orange wood desk (extreme) gray world paints 2.8–4.8 % of the
  background blue (it was 0 %).
- The home wall above the horizon: 0 % painted before and after, for every estimator.

##### C. The judged candidates (baseline 133.8 of 172 placements, 211 of 307 per frame, 1.93 boxes not on their barrel)

| candidate | verdict | found, placements | found, per frame | barrels gained / lost | boxes not on their barrel (per frame) | empty frames: clean / with clutter | places that moved |
|---|---|---|---|---|---|---|---|
| F1 gray world, full | FAIL | 141.8 (+8.0) | 239 | 39 / 11 | 4.52 (9) | 0 / 2.00 | bathroom +7.5, gray +2.0, ABP white +2.0, ottoman −1.7, campus −1, pale wood −1 |
| F2 white patch, full | FAIL | 137.0 (+3.2) | 228 | 34 / 17 | 6.97 (18) | 0 / 2.25 | bathroom +6.5, ottoman −1.7, campus −1, glass −0.6 |
| F3 `without_loose`, full | FAIL | 144.3 (+10.5) | 254 | 50 / 7 | 5.88 (14) | 0 / 1.98 | bathroom +9.0, ottoman +2.3, campus −1 |
| F4 gray above the horizon, full | FAIL | 141.6 (+7.8) | 246 | 46 / 11 | 6.42 (18) | 0 / 1.12 | bathroom +9.5, gray +1, home −1, pale wood −1, ottoman −0.7 |
| F5 shades of gray, full | FAIL | 138.2 (+4.5) | 232 | 32 / 11 | 4.85 (12) | 0 / 2.20 | bathroom +7.2, ottoman −3.0 (worse than its margin), campus −1 |
| **P1 gray world, partial** | **PASS** | **143.0 (+9.2)** | **243** | **38 / 6** | **1.05 (5)** | 0 / 0.20 | bathroom +8.0, gray +2.0, glass +0.2, ottoman −1.0 |
| P2 white patch, partial | NO CLEAR DIFFERENCE | 133.1 (−0.7) | 208 | 7 / 10 | 2.67 (8) | 0 / 0.00 | glass −0.4, ottoman −0.3 |
| P3 `without_loose`, partial (primary) | FAIL | 134.8 (+1.0) | 215 | 6 / 2 | 4.65 (7) | 0 / 2.00 | bathroom +1.0 |
| P4 gray above the horizon, partial | PASS (WEAK) | 138.5 (+4.7) | 234 | 30 / 7 | 2.47 (10) | 0 / 0.20 | bathroom +6.5, gray +1, home −1, pale wood −1, ottoman −1 |
| P5 shades of gray, partial | NO CLEAR DIFFERENCE | 132.7 (−1.1) | 208 | 3 / 6 | 0.80 (4) | 0 / 0.20 | glass +0.2, ottoman −1.3 |
| U3 `without_loose` added to today's mask | FAIL | 135.5 (+1.7) | 217 | 7 / 1 | 5.43 (10) | 0 / 2.00 | bathroom +1.0, ottoman +0.7 |

Margins: found better above +4.0; boxes not on their barrel worse above +1.85; empty frames with clutter worse above
+1.0; any box on a clean empty frame fails. No candidate put a box on a clean empty frame.

- **P1** picked alpha 0.5 in every fold, so it is one fixed setting: `wb.detect_frame_gray_world_half` (checked with
  `tools/judge.py --cand-callable`: the same PASS, 143.0, 243). Per frame: bathroom mid 6 1 → 15 of 15, warm 1 → 11,
  mid 3 1 → 7, cool 13 → 15; gray table 10 → 12; window glass 14 → 15; warm ottoman 0 → 3; ottoman mid 6 6 → 2,
  cool 3 → 1. All 6 barrels it loses are on the ottoman.
- **The primary, P3, failed** because of the pale wood. With the pale wood among the training places every alpha
  above 0.25 is FAIL there, so seven folds took 0.25 (+1.3, almost nothing). With the pale wood held out, the fold
  took 0.75, and on the pale wood that drew boxes on the orange-flooded wood (one on an empty frame with clutter).
- All five full corrections FAIL, three of them with found well above the margin (+8.0, +10.5, +7.8): the boxes
  sink them.
- Extreme conditions, report only (P1, per frame): wood under the lamp 7 → 64 of 126 (cool 6 2 → 16, mid 6 1 → 17,
  warm 6 0 → 13); very dark ottoman 1 → 0; black table no change.

##### What the pictures show (`results/2026-11-27_whitebalance/sheets/`, all looked at)

- **Gained**: real barrels. Blue barrels and blue stripes in the bathroom, painted solid blue after correction; the
  gray table's orange barrels; a blue barrel behind a purple figure on the glass table.
- **Lost (P1, all ottoman)**: orange barrels whose orange sits at hue 13–15. A small blue gain (1.08 to 1.17) pushes
  it out of the range. The orange under the warm bathroom lamp under the full corrections turns pink and is lost
  (`lampwarm6_bathtile_close_01`).
- **New boxes not on a barrel**: (1) the dark woven ottoman under the warm lamp turns blue in patches and gets boxes
  (F3, F1); (2) the orange-flooded pale wood gets a box when the gains move by only 2–4 % (F3, P3, U3); (3) the jar
  with an orange body and a blue band on the glass table (several candidates; it is a barrel to the detector); (4)
  P1's three: the jar (`window_glass_clutter_01`, `lampcool6_glass_neg_02`) and a wrong-color box on two touching
  barrels in the warm bathroom.

##### D. Against the ideas that change no pixel (`results/2026-11-27_whitebalance/compare.md`)

Barrels counted per frame, judged frames. "None of the three" = not gained by contrast C1, near-miss or self-calibration AB.

| candidate | gained | also by contrast | also by near-miss | also by self-cal | none of the three | lost |
|---|---|---|---|---|---|---|
| P1 gray world, partial | 38 | 33 | 15 | 18 | 4 | 6 |
| F3 `without_loose`, full | 50 | 41 | 24 | 26 | 7 | 7 |
| stripe by contrast C1 (+21.5) | 64 | | | | | 0 |
| near-miss (+13.7) | 38 | | | | | 0 |
| self-calibration AB (+13.8) | 37 | | | | | 0 |
| blue follows the light B1 (+3.9) | 14 | | | | | 0 |

- 34 of P1's 38 gains are gained by at least one idea that changes no pixel; 33 of them by the stripe by contrast
  alone. The 4 that are not: a gray-table barrel whose box was off, two half-hidden bathroom barrels, the blue barrel
  behind the purple figure.
- P1 loses 6 barrels; none of the other four loses any.

#### Takeaway

- **Correction does what the physics said.** Blue comes back under the warm lamp (bathroom blue paint 0–5 % → 95–99 %
  in range). Orange cannot be fixed on the ottoman, and under the same warm lamp a full correction pushes the orange
  out (99 % → 4–9 %).
- **Only half a correction works, and only gray world.** P1 passes (+9.2, boxes down by 0.9); gray world above the
  horizon passes weakly (+4.7). Full corrections find more (up to +10.5) and all fail on boxes on the dark fabric and
  the wood. The primary (`without_loose`) fails: the reading that is best for the light is not best for correction,
  because the pale wood's problem is the table, not the light, and only gray world sees the table.
- **It buys almost nothing the pixel-free ideas do not.** Contrast gains 64 barrels with none lost, and covers 33 of
  P1's 38. P1 costs 6 ottoman barrels.

#### For Tanush and Dave, in plain words

**Does correcting the image help?** A little, and only gently. Halfway gray-world correction finds 9 more placements
than today held out, with fewer stray boxes. Full correction finds about as many and draws boxes on the dark ottoman
and the wood.

**Does it buy anything the ideas that leave the image alone do not?** Hardly. The stripe-by-contrast idea finds 64
more barrels (counted per frame) without touching a pixel, and those include 33 of the 38 the correction finds. The
correction also loses 6 ottoman barrels that today finds. Only 4 of its barrels are new to the pixel-free ideas, so the rule "never correct the image" costs at most 4
barrels here. Not enough to argue against it.

**Why is it not more?** The two paints move in opposite directions under a lamp. Pulling the blue back pushes the
orange out. And the ottoman's orange is not a light problem at all.

**One useful thing it shows.** Gray world takes the orange flood off the pale wood table. That is the table's color,
not the light's. If that flood ever matters, it is a reason to look at the table color, not at correction.

#### Not done

- No second round. The obvious next tries (correct for blue only, keep orange from the photo; combine with contrast)
  would need an addendum first.
- No walkthrough with Tanush. `TODO.md`, `STATUS.md`, `EXPERIMENTS.md`, `DECISIONS.md` were not edited.
- The run's own date stamp in `summary.md` and `chosen.json` reads 2026-11-26 (the machine's clock).
