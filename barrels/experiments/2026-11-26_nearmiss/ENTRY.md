# Experiment-log entry, ready to paste into `docs/EXPERIMENTS.md`

## 2026-11-26: near-miss colors count next to strong evidence of a barrel (TODO C2, branch `wip/exp-nearmiss`)

**Hypothesis (Tanush).** The detector needs both colors of a barrel. Most clean misses have one color at full
strength and the other just under the threshold. So: keep the fixed ranges as they are, and let a pixel just
outside the range count only where the barrel's other color says it should be. Loosening everywhere floods
(false boxes 7 → 80); loosening beside a barrel should not.

**Method.** `src/barrels/nearmiss.py` (called by nothing by default; 24 unit tests). Every mask is the fixed mask
plus added paint. No pixel is changed, strict paint is never changed, `detector.py` is not touched.

- *Stripe direction.* Loose stripe-colored pixels are painted in a gap of stripe height between two strict body
  pieces in the same column.
- *Body direction.* A strict piece of stripe color with stripe size for its row is a "band". Loose body-colored
  pixels joined to it are painted inside the box that row predicts. Four rules say "not a barrel": the band has
  its own color above or below; the band is the body of a barrel of its own color; the body color runs on above
  the predicted top (it is the wall behind); the paint does not complete half a body on that side.
- *Edges.* Loose body paint never passes the top and bottom the stripe's row predicts (`pred`), or stops at the
  strict body where there is some (`strict`). `free` (predicted row plus the detector's tolerance) is the control.
- *Loose levels.* A ladder set before any run: level 1 = hue ± 3, S − 20; level 2 = ± 6, − 40, V ≥ 25; … level 5 =
  ± 25, − 100, V ≥ 15 (blue S ≥ 13, almost gray). Past the ranges: stripe level 6 = anything that is not body
  color; body level 6 = darker than 0.6 × the ground beside the barrel; body level 7 = anything.
- *Reference.* Plain two-level thresholds: a loose pixel counts when it touches strict pixels of its own color.
- *Chosen in each fold* (the other seven places only): the two levels and the edge mode, by found − 2 × boxes not
  on their barrel, with no new box on a clean empty frame and no training place below its margin.

**Data and rule.** The standard judge (`barrels.judge`), train frames only: 154 ordinary frames, 8 places, 172
placements; extreme conditions printed, never judged. `PREREG.md` was committed (c648d95) before the first judged
run. 28 candidates, all reported in `results/2026-11-26_nearmiss/summary.md`. No second round.

**What was looked at first (in-sample, all places).** Three rounds of tables and 9 contact sheets while the four
rules of the body direction were written; one table of body, stripe and ground color per condition. So the
structure of the method was shaped on train frames of all eight places. Leave one place out guards only the two
levels and the edge mode.

**Results.** Baseline (fixed model): 133.8 of 172 placements, 211 of 307 per frame, 1.9 boxes not on their
barrel, none on a clean empty frame.

| candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel | clean empty | places that moved |
|---|---|---|---|---|---|---|---|
| plain two-level, level 1 (`A_hyst1`) | FAIL | 143.7 (+9.8) | 234 | +30 / −7 | 6.7 (+4.8) | 0 | home −2.0, pale wood −1.0, gray +5.0, ottoman +7.0 |
| plain two-level, level 2 / 3 | FAIL / FAIL | 138.1 / 133.2 | 219 / 210 | +30 / −22, +32 / −33 | 14.5 / 23.4 | 1 / 1 | home −2.0 / −6.0, glass −2.2 / −3.6 |
| plain two-level, level chosen in fold (`A_hyst_fit`) | FAIL | 131.8 (−2.0) | 209 | +0 / −2 | 4.9 (+3.0) | 0 | home −2.0 (every other fold kept the fixed model) |
| the same with the bottom guard | FAIL | 131.8 (−2.0) | 209 | +0 / −2 | 5.9 (+4.0) | 0 | home −2.0 |
| **partner-conditioned, chosen in fold (`B_partner_fit`)** | **PASS** | **147.5 (+13.7)** | **249** | **+38 / −0** | **3.6 (+1.6)** | **0** | gray +2.0, bathroom +5.0, ottoman +4.7, ABP white +2.0 |
| the same, edges unprotected (`D_partner_free_fit`) | FAIL | 132.2 (−1.6) | 214 | +13 / −10 | 2.7 (+0.7) | 0 | campus −4.0, home −1.0, ABP white −1.0 |
| the same, levels past the ranges allowed (`C_wide_fit`) | PASS | 147.5 (+13.7) | 249 | +38 / −0 | 3.6 | 0 | identical: no fold chose a level past the ranges |
| stripe direction alone, level 1 … 5 | no clear difference, PASS (weak), PASS (weak), PASS, PASS | 137.3, 139.0, 139.7, 140.2, 141.0 | 218 … 232 | none lost | 1.9, 2.2, 2.2, 2.2, 2.2 | 0 | gray +2.0, bathroom +0.5 … +3.5, ottoman +1.0 … +1.7 |
| stripe direction alone, level 6 (anything) | FAIL | 144.1 (+10.3) | 243 | +33 / −1 | 5.1 (+3.2) | 0 | bathroom +5.5 |
| body direction alone, level 1 … 5 | PASS (weak), then PASS | 138.5, 141.0, 143.9, 146.2, 147.3 | 219 … 239 | −2 at level 1, then none | 1.9, 2.2, 1.9, 2.3, 3.3 | 0 | gray +3.0 … +5.0, ottoman +1.7 … +5.0 |
| body direction alone, level 6 (darker than the ground) | FAIL | 148.7 (+14.9) | 245 | +34 / −0 | 5.6 (+3.7) | 0 | bathroom +3.2 |
| body direction alone, level 7 (anything) | FAIL | 142.3 (+8.5) | 242 | +38 / −7 | 45.9 (+44.0) | 3 | home −2.0 |
| both directions, level 1 … 5 | PASS each | 142.0, 144.8, 148.1, 151.0, 152.8 | 226 … 257 | −1 at level 1, then none | 1.9, 2.5, 2.9, 2.9, 3.2 | 0 | at level 5: gray +6.0, bathroom +5.0, ottoman +6.0, ABP white +2.0 |
| both directions, stripe 6 with body 6 | FAIL | 156.4 (+22.6) | 271 | +61 / −1 | 8.5 (+6.6) | 0 | bathroom +8.5 |
| both directions, stripe 6 with body 7 | FAIL | 151.0 (+17.2) | 269 | +66 / −8 | 50.0 | 3 | home −2.0 |

`B_partner_fit` is 9.7 placements above the gain margin (+4.0): not a weak pass. Its boxes not on their barrel
rose by 1.6 against a margin of 1.85: one more such box would have failed it. Six folds chose both directions at
level 5 with `pred`; the gray table's fold chose `strict`; the ottoman's fold chose body level 4.

**Paint, bottom edges, extreme conditions.**

| candidate | paint outside the hand boxes | bottoms moved, of the 211 barrels the fixed model finds | lost | extreme, found per frame (of 167) |
|---|---|---|---|---|
| plain two-level, level 1 | × 2.58 | 99 | 7 | 13 → 29 |
| partner-conditioned, chosen in fold | × 1.04 | 19 | 0 | 13 → 58 |
| the same, edges unprotected | × 1.06 | 99 | 10 (8 with the box still on the barrel) | 13 → 47 |
| stripe direction alone, level 5 | × 1.00 | 3 | 0 | 13 → 30 |
| both directions, stripe 6 with body 6 | × 1.09 | 20 | 1 | 13 → 86 |

**The named clutter traps.** The cluttered empty frames `lampmid3_bathtile_neg_02`, `lampmid6_bathtile_neg_02`,
`lampwarm6_bathtile_neg_02` get no box from any candidate except the two with body level 7 (one box on
`lampmid6_bathtile_neg_02`). The fixed mask has no blue there, so nothing has a partner. The trap fires on the
glass table instead: the jar with a blue label on red gets a new orange box in three frames of the main candidate
(`lampcool6_glass_neg_02`, `lampmid3_glass_neg_02`, `lampcool6_glass_occl_02`). The fixed model already boxes the
same jar in three other frames (`lampmid3_glass_occl_02`, `lampmid6_glass_clutter_01`,
`lampwarm6_glass_clutter_01`): it is clutter that has both colors at full strength under some lights.

**What the pictures show** (`contact.py`, `sheets.py`; PNGs in `results/2026-11-26_nearmiss/contact/`, not in git).

- *Gained by the stripe direction:* blue barrels on the gray table whose orange stripe reads red (hue 0 to 1);
  orange barrels in the bathroom whose blue stripe reads hue 101 under the cool lamp (the range starts at 103)
  and hue 90 to 101 with S 46 to 72 under the mid lamp. The added paint is a thin band exactly in the gap.
- *Gained by the body direction:* orange barrels on the ottoman whose body sits on the top edge of the orange
  range (median hue 12 to 13, the limit is 13), around a strict blue stripe; blue barrels under the mid bathroom
  lamp whose body is dark and pale (hue 83 to 93, S 23 to 51); two barrels of the ABP occlusion set.
- *The 7 new boxes that are not on a barrel:* 3 on the jar label above; a blue box on clutter beside that jar
  (`lampmid6_glass_clutter_01`); a second box on the upper half of an orange barrel
  (`lampmid3_bathtile_core_01`); an orange box on a blue barrel in front of a tin
  (`lampmid6_bathtile_clutter_01`); a second blue box beside a barrel on the ottoman
  (`lampmid6_ottoman_core_01`). Counted once per arrangement they are the +1.6.
- *Plain two-level thresholds:* the blue wall behind the home table is loose blue, and it touches the strict blue
  stripe of an orange barrel. The whole wall is painted and the barrel gets a blue box. That is the home loss.
- *Edges unprotected:* loose paint under the base (shadow, reflection) moves the bottom down. The box stays on
  the barrel and fails the bottom rule: three barrels of `campus_light_far_01` alone.
- *Stripe level 6 (anything):* gaps that are not stripes get painted: between the letters on a blue tin, in a
  printed marker, between two blue barrels and a blue jacket behind them.

**Takeaway.**

1. The idea works. Conditioned on the partner, the loose level can go to the loosest color range (hue ± 25,
   blue S down to 13) and still add only 1.6 boxes. Unconditioned, level 1 already adds 4.8 and loses home.
2. The stripe direction costs nothing: no barrel lost, no paint outside the hand boxes, 0.2 more boxes.
3. Keeping loose paint inside the predicted top and bottom is what makes the body direction pass. Without it
   the same grid fails (campus −4.0, 99 bottoms moved against 19).
4. False boxes start where the color test stops: stripe level 6 (+3.2 boxes), body level 6 (+3.7), body level 7
   (+44 and 3 boxes on clean empty frames). No fold chose one of them.
5. **What it cannot reach:** a barrel with neither color inside the strict ranges. Under the warm bathroom lamp
   the blue reads gray-olive (hue 24, S 40 to 61) and nothing strict is blue: 1 of 15 before, 1 of 15 after. On
   the ottoman under the warm lamp: 0 → 1 of 15. Levels 6 do reach them (bathroom warm 10 of 15, ottoman warm 7
   of 15, with stripe 6 and body 6) but fail on false boxes. It also cannot fix clutter that has both colors.

**Next.**

- The setting the rule gives on all eight places is both directions at level 5 with `pred`
  (`experiments/2026-11-26_nearmiss/candidates.py:detect_frame`; in-sample 152.8, held out 147.5). It is a
  candidate for E8 (the winners together), not a default: `detector.py` is being restructured.
- The warm lamp needs a strict partner first. "Blue follows the light" (C3) or the stripe by contrast (C4) could
  supply it; this method then completes the barrel. Worth one combined run.
- The jar label: a body test on both sides of the band (it has orange on one side only at full height) is the
  obvious rule to try. Not done here: it would have been tuned on the four frames it fails on.
- The four body rules were written from train frames of all places. A new place is the real check.
