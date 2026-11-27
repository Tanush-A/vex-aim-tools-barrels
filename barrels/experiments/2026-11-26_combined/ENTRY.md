# Experiment-log entry, ready to paste into `docs/EXPERIMENTS.md`

## 2026-11-27 — The winners together (TODO E8, branch `wip/exp-combined`; pre-registered, one round plus one dated addendum; nothing adopted)

**Question.** Three color-step ideas passed the standard pass rule on 2026-11-26, each alone: near-miss colors
(`nearmiss`), the barrel as its own color reference (`selfcal`) and the stripe by color difference (`contrast`).
Put together, do they find more than the best one alone, without more boxes off a barrel? The owner wants the
simplest thing that works.

**Answer.** **Contrast alone.** It does most of the work. Nothing added to it is above the noise.

- Contrast alone: 133.8 → **155.3** of 172 placements (+21.5, PASS), 211 → 275 of 307 per frame, 64 barrels gained, 0
  lost. Boxes off a barrel 1.93 → 2.83. No box on an empty frame. 90 ms per frame (today 46).
- The best mix of the first two (`mask_union`): 152.8. Below contrast alone by 2.5.
- Contrast plus anything: at most +2.7 placements over contrast alone (all three together, boxes merged). The judge
  calls that NO CLEAR DIFFERENCE. Four of the six mixes with contrast FAIL against today on boxes off a barrel.

**Method.**

- Branch `wip/exp-combined`, from `barrels` after the collapse. The three winners merged in.
- `src/barrels/combined.py` (called by nothing by default; 30 unit tests). It holds twelve ways to run the winners on
  one frame. None has a number of its own.
- **Every number** is each winner's own, picked by that winner's own rule on the training places, for that winner
  alone. The mixes are never scored while fitting. Judged leave one place out, by the standard judge.
- **Step A first.** Each winner alone on the collapsed detector gives exactly its judged pages: totals, places,
  conditions, every changed barrel and box, every fold's pick. Near-miss 147.47, self-calibration 147.55, contrast
  155.30. Zero differences. Three unit tests were ported (`detector._stripe_geometry` is now
  `detector.BarrelAt.from_stripe_row`). No module needed a change.
- `PREREG.md` was committed before any mix ran (7347008). Contrast came in later, by a dated addendum, committed
  before it ran on this branch (a52f0b1).

**Data.** Train frames only. 154 ordinary frames, 8 places, 172 placements. 77 extreme frames reported, never
judged. No test frame was loaded, viewed, scored or listed.

**Results: the first two winners together** (against today's detector).

| candidate | verdict | found, placements | per frame | gained / lost | boxes off a barrel | ms per frame |
|---|---|---|---|---|---|---|
| today | | 133.8 | 211 | | 1.93 | 47 |
| `nearmiss` alone | PASS | 147.5 | 249 | 38 / 0 | 3.57 | 83 |
| `selfcal` alone | PASS | 147.6 | 248 | 37 / 0 | 2.18 | 88 |
| near-miss, then self-calibration on its mask | FAIL (boxes +2.63) | 151.9 | 260 | 49 / 0 | 4.57 | 162 |
| self-calibration, then near-miss on its mask | FAIL (boxes +2.38) | 153.1 | 262 | 51 / 0 | 4.32 | 161 |
| **the two masks together (`mask_union`)** | **PASS** | **152.8** | 261 | 50 / 0 | 3.32 | 138 |
| the two box lists merged | PASS | 152.8 | 261 | 50 / 0 | 3.57 | 160 |
| a new box only when both draw it | PASS | 143.2 | 237 | 26 / 0 | 2.18 | 160 |

`mask_union` against each winner alone: PASS (+5.3 and +5.2, weak). So the two are worth having together. But
contrast alone beats the pair.

**Results: with contrast** (against today, and against contrast alone).

| candidate | against today | found | per frame | boxes off a barrel | against contrast alone | ms per frame |
|---|---|---|---|---|---|---|
| **contrast alone** | **PASS** | **155.3** | 275 | 2.83 | | 90 |
| contrast on top of near-miss | FAIL (boxes +2.28) | 157.0 | 278 | 4.22 | no clear difference (+1.7) | 155 |
| contrast on top of self-calibration | PASS | 155.5 | 275 | 3.58 | no clear difference (+0.2) | 131 |
| contrast on top of `mask_union` (all three) | FAIL (boxes +2.78) | 157.7 | 278 | 4.72 | FAIL (boxes +1.88) | 180 |
| contrast and near-miss, boxes merged | FAIL (boxes +2.28) | 156.6 | 277 | 4.22 | no clear difference (+1.3) | 205 |
| contrast and self-calibration, boxes merged | PASS | 155.7 | 276 | 2.83 | no clear difference (+0.4) | 177 |
| contrast and `mask_union`, boxes merged | FAIL (boxes +2.03) | 158.0 | 279 | 3.97 | no clear difference (+2.7) | 229 |
| `nearmiss` / `selfcal` / `mask_union` | | 147.5 / 147.6 / 152.8 | | | FAIL / FAIL / FAIL (−7.8, −7.8, −2.5) | |

By place, contrast alone: gray table 10 → 15 of 16, bathroom floor 4.0 → 13.5 of 15, ottoman 3.0 → 10.0 of 15. The
other five places do not move.

**C. Who finds what** (barrels today misses, counted per frame). All three: 24. Contrast only: 20. Contrast and
self-calibration: 11. Contrast and near-miss: 9. Near-miss only: 4. Near-miss and self-calibration: 1. Self-
calibration only: 1. None: 26. Of the 50 the first two gain, contrast finds 44. The 6 it misses: two cut by the
frame edge (no stripe in the frame), two blue barrels touching another blue barrel (one band two barrels wide), two
half-hidden barrels its "one body" guard refuses. Near-miss and self-calibration overlap too: 25 in common, 13 and 12
alone. Near-miss reaches body hues just past the range (ottoman); self-calibration reaches what no ladder level
reaches (the gray-olive warm-lamp stripe, the red-orange gray-table bodies).

**D. Every box off a barrel, contrast alone** (9 per frame, 2.83 counted once per arrangement). Five are today's own
boxes: the jar on the glass table (3 frames), orange glints of the ottoman under a close-up box, pale wood grain under
a 329 px close-up box. Four are new:

- `lampmid3_bathtile_core_01`: a second box on the upper half of an orange barrel (all three winners draw it).
  Check: one box per barrel (a box inside a surer same-colored box).
- `lampwarm6_bathtile_core_01`: an orange box on a blue barrel that also has its blue box. Check: self-calibration's
  seed rule (no box of the other color on a found barrel).
- `lampwarm6_glass_occl_02`: two small boxes stacked on the red jar (label read as a stripe between jar and lid).
  Check: two boxes stacked in the same columns are one thing; or a second reading (no other winner draws them).
No rule was tuned on these frames.

**E. Frames nobody judged on** (the extreme ones). **Not blind**: all three authors saw counts on them while shaping
their methods (near-miss: in-sample tables and color readings; self-calibration: four in-sample tables with a row
per extreme condition; contrast: its finder measured on all 261 train frames). No number was chosen on them. Found
per frame, of 167: today 13, near-miss 58, self-calibration 60, contrast **85**, `mask_union` 72. Boxes off a barrel:
4, 4, 5, 6, 6. No box on an empty frame. Wood desk (6 lamp settings, 21 placements): 1.2, 7.2, 8.5, **13.2**, 9.8. Black
table (26): 5, 14, 8, **5**, 12 (contrast gains nothing there). Very dark ottoman (15): 1 for all. Dave's 12 office
frames (indicative): today 13 of 34, near-miss 26, self-calibration 19, contrast 23, `mask_union` 28.

**F. Against the vendor** (six places with vendor files: 117 frames, 108 placements). Found: today 70.8, near-miss
84.5, self-calibration 84.5, `mask_union` 89.8, **contrast 92.3**, vendor 83.3. Per frame 148, 186, 185, 198, **212**,
177. Missed: 36.0, 21.0, 22.0, 16.4, **14.5**, 16.5. Boxes off a barrel: 1.93, 3.57, 2.18, 3.32, **2.83**, 3.00 (on
nothing per frame: 5, 9, 5, 9, **7**, 7). Contrast beats the vendor by 9.0 placements. It still loses at the gray
table (15 against 16) and the ottoman (10.0 against 12.3). It wins at the bathroom (13.5 against 7.0), the glass
table (14.8 against 12.0), pale wood (13 against 12) and the ABP white table (26 against 24). This is train data. Our
methods were shaped on it; the vendor's was not.

**G. What is left after contrast alone** (ordinary conditions): 32 barrels per frame, 16.7 placements.

- Hidden or cut by the frame: 27 (15.0 placements). ABP occlusion set 6, ottoman 10, bathroom 6, pale wood 2, others 3.
- Neither color painted: 2 (warm ottoman, blue barrels touching each other).
- Touching another barrel: 3 (blue barrels side by side on the ottoman; one, `lampwarm6_ottoman_core_01` #2, is really
  blocked by today's false close-up box below it, which holds its stripe point).
- A guard refused it: 0. The detector refused a well-painted barrel: 0.

So what is left is almost all hidden and frame-cut barrels, plus touching blue barrels. That matches the
place-ceiling oracle (163.2: its 13 misses were all hidden or cut).

**Takeaway.**

1. One idea does the work: the stripe by color difference. It needs no strict color, so it reaches what the other two
   reach and 20 barrels more.
2. Adding the others gains 1 to 3 placements and brings their clutter boxes. Inside the noise. Not worth it.
3. Without contrast, near-miss and self-calibration are complementary: together (the two masks laid over each other)
   +5 placements over either.
4. Contrast's weak spots: frame-cut close-ups, touching same-colored barrels, half-hidden barrels, the black table.
5. Caution, as for all three: each method's structure (contrast's guard thresholds included) was shaped on all eight
   places. Only the settings in the folds are held out. A new place, or the test frames, is the clean check.

**Next.** (1) Walk Tanush through contrast; it is main code if adopted. (2) Judge it on the next place Tanush shoots.
(3) Touching same-colored barrels: cut a band two barrels wide (also self-calibration's open point). (4) The
one-box-per-barrel and other-color-on-a-found-barrel checks for the new boxes (D), judged on their own.

**Repeat.** `python barrels/experiments/2026-11-26_combined/repro.py`, `cn_picks.py`, `run.py`, `run3.py`,
`analysis.py all cn_alone`, `cb_sheets.py`, with `PYTHONPATH=barrels/src`. The answer as the judge's command:
`python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_contrast/table.py:fit` (held out); fixed
numbers: `barrels/experiments/2026-11-26_contrast/candidate.py:detect_frame` (in-sample when judged).
Pages: `results/2026-11-26_combined/` (`summary.md`, `summary3.md`, `overlap.md`, `overlap3.md`, `*_cn_alone.md`,
`*_mask_union.md`).
