# Pre-registration: near-miss colors count next to strong evidence of a barrel (TODO C2)

Written 2026-11-26 on branch `wip/exp-nearmiss`, **before any candidate was run through the judge**. Committed
before the first judged run. Nothing here changes what runs by default: `detector.py` and the default color model
are not touched. Every candidate builds its own mask (`src/barrels/nearmiss.py`, called by nothing else) and then
calls `detector.detect(mask)` with the default `DetConfig`.

## The question

The fixed color step paints a pixel only when its hue and saturation are inside fixed ranges. The detector needs
both colors of a barrel. Of 63 clean barrels missed on the new conditions, 57 have one color unpainted and 49 have
the other color at full strength; the missing part was mostly just under the threshold. Loosening the ranges
everywhere floods the picture (false boxes 7 → 21 → 80).

Tanush's idea: **a pixel just outside the range counts when it sits next to strong evidence of a barrel.**

1. Does painting loose pixels only beside the partner color find more barrels than the noise, without more boxes
   that are not on a barrel? (B)
2. How does that compare with plain two-level thresholds, where a loose pixel counts when it touches strict pixels
   of its own color? (A)
3. How loose can the loose level be when it is conditioned on the partner? Where do false boxes start? Does it
   reach the gray-olive blue of the warm bathroom lamp and the dark stripes of the ottoman? (C)
4. What is it worth to keep loose paint from moving the bottom edge? (D)

## The method (`src/barrels/nearmiss.py`)

Every mask is the fixed mask plus added paint. Strict paint is never changed. Pixels are never changed.

**Loose levels (the ladder), set before any run from the numbers in the brief, never tuned:**

| level | hue, each side | saturation floor | brightness floor |
|---|---|---|---|
| 0 | off | | |
| 1 | ± 3 | − 20 | 40 |
| 2 | ± 6 | − 40 | 25 |
| 3 | ± 10 | − 60 | 25 |
| 4 | ± 15 | − 80 | 20 |
| 5 | ± 25 | − 100 (orange S ≥ 40, blue S ≥ 13) | 15 |

Past the color ranges: the stripe direction has level 6, **anything** that is clearly not the body color (not
inside the body color's level-2 range). The body direction has level 6, **darker than the ground** (the level-5
range, or any pixel that is not stripe-colored and darker than 0.6 × the ground beside the barrel), and level 7,
**anything** that is not stripe-colored, in the band's own columns.

**A, plain two-level thresholds (`hysteresis_mask`).** A loose pixel is painted when it is connected to strict
pixels of its own color. With the guard: not when it lies below the lowest strict pixel of the piece it joins.

**B, partner-conditioned (`partner_mask`), two directions, both barrel colors:**

- *Stripe direction.* Loose stripe-colored pixels are painted in a gap between two strict body pieces in the same
  column. The gap is at most 2.0 × the stripe height its row predicts. Each body piece is at least 0.75 × that
  height tall. A slot under 3 columns wide is dropped.
- *Body direction.* A strict piece of stripe color is a "band" when it has stripe size for its row (0.45 to 1.6 ×
  the stripe height, 0.5 to 1.2 × the barrel width, at least 20 px). Loose body-colored pixels are painted when
  they are joined to the band, start within 3 rows above or below it, and lie inside the box the band's row
  predicts (sideways: every place a barrel holding the band can be, plus 0.1 of a width).
- *Rules of the body direction that say "this is not a barrel":* (1) a band with more than a quarter of its own
  color in the body rows above or below it is not a stripe; (2) a band that is one of the two pieces around a
  stripe slot of its own color is the body of a barrel of that color, not a stripe; (3) when the body color runs
  on above the predicted top (it fills the rows from two tolerances to one tolerance above it in half of the
  band's columns), it is what stands behind the barrel: nothing is painted above the band; (4) a side is painted
  only when strict and loose body color together then cover half of that side's predicted body.

**D, the edges (`NearMissConfig.bottom`).** `strict`: where strict body color is seen below the band, loose paint
stops at its lowest row; where there is none, at the bottom the stripe's row predicts. The top is treated the same
way. `pred`: always the predicted top and bottom. `free`: the predicted rows plus the detector's own tolerance
(15 % of the height, at least 4 px): no protection.

## What was looked at before this was written (honesty)

All on TRAIN frames (`judge.load_frame` refuses anything else; no test frame was loaded, scored, viewed or
listed). All in-sample: every place at once, counted as the judge counts (`explore.py`).

1. **Three rounds of in-sample tables**, because the rules of the body direction were written after looking:
   - Round 1 (the first version: rule (1) only, top not protected). Hysteresis level 1: found 133.8 → 143.7
     placements, 30 gained and 7 lost per frame, boxes not on their barrel 1.9 → 6.7. Stripe direction alone,
     levels 1 to 5: +3.5 to +7.2 placements, **no barrel lost, boxes 1.9 → 2.2**, no extra paint outside the hand
     boxes. Body direction alone: boxes not on their barrel 4.3 at level 1 and 10.0 at level 2; home lost 2 to 4.
   - I then looked at 9 contact sheets of the body direction at level 2 (`sheets.py`): `window_light_cluster_01`,
     `window_light_core_03`, `window_light_occl_02`, `lampcool6_glass_neg_02`, `overheaddim_palewood_clutter_01`,
     `lampcool6_bathtile_clutter_01`, `lampmid6_bathtile_core_01` (some twice, zoomed). Seen: the blue wall behind
     the home table painted as a "blue body" above the top of an orange barrel; a gold jar lid painted as orange
     body above a barrel; a red extinguisher painted as orange above a blue piece; a jar label with both colors.
   - Round 2 added rule (2) and the top protection. Round 3 added rules (3) and (4). After round 3, in-sample:
     body direction alone at levels 2 to 5 with `pred`: +7.2 to +13.5 placements, no barrel lost, boxes 1.9 to
     3.3. Both directions at level 5 with `pred`: 133.8 → 152.8, 46 gained, none lost, boxes 3.2. With `free`:
     3 to 7 barrels lost. With `strict`: fewer gained than `pred` (138.3 against 141.0 at level 2).
   - Rules (1) to (4) off, both directions at level 5, in-sample: all on 152.8 / 3.2 boxes; rule (2) off 152.4 /
     3.2; rule (3) off 148.1 / 9.0; rule (4) off 153.0 / 5.9; all three off 148.0 / 14.1.
2. **`look_body.py`**: body, stripe and ground color at the hand boxes, per condition. Under the warm and mid
   bathroom lamp the blue body reads hue 24 to 93, S 23 to 61, V 45 to 55, and the ground V 158 to 182: the body
   is 0.28 to 0.33 × as bright as the ground. On the white tables a blue body is 0.8 to 1.0 × the ground. The
   "darker than the ground" level and its number 0.6 come from this table (all places, in-sample). It is one
   hand-set number and it is not chosen in any fold.
3. In-sample with the "darker" and "anything" levels: body level 6 alone 148.7 / 5.6 boxes; body level 7 alone
   142.3 / 45.9 boxes and 3 boxes on clean empty frames; stripe 6 with body 6: 156.4 / 8.5 boxes.
4. The extreme conditions in-sample for the same settings (found per frame 13 → 58 at both level 5).

So: **the structure of the method was shaped on train frames of all eight places.** Leave one place out guards
only the numbers chosen in a fold (the two levels and the edge mode). The fixed constants (2.0, 0.75, 0.5, 0.25,
0.5, 0.5, 0.6, 3 rows) were set by reasoning or copied from `DetConfig`; none was swept. The in-sample result of
every ladder candidate below is already known to me, and for a candidate with nothing chosen the judged result is
that same number.

## Data and the judge

`barrels.judge.judge` against today's default: the ordinary train conditions (154 frames, 8 places, 172
placements), the extreme ones printed and never judged. The judge's clauses and margins as they stand in
`results/baseline/margins.json` (found better above +4.0, worse below −10.92; a place worse below its margin;
boxes not on their barrel worse above +1.85; any new box on a clean empty frame fails; cluttered empty frames
worse above +1.0). No rule of my own.

## The candidates (28; every one is reported, whatever it does)

Candidates with a chosen number are judged leave one place out (`judge(fit=...)`).

| name | what | chosen in the fold |
|---|---|---|
| `A_hyst1`, `A_hyst2`, `A_hyst3` | plain two-level thresholds, loose level 1, 2, 3 | nothing |
| `A_hyst_fit` | the same | the loose level, 1 to 5 |
| `A_hyst_guard_fit` | the same with the bottom guard | the loose level, 1 to 5 |
| **`B_partner_fit`** | **partner-conditioned, both directions: the main candidate** | stripe level 0 to 5, body level 0 to 5, edges `strict` or `pred` (65 settings) |
| `D_partner_free_fit` | the same with the edges unprotected (`free`) | stripe level 0 to 5, body level 0 to 5 (35 settings) |
| `C_wide_fit` | partner-conditioned, levels past every color range allowed | stripe level 0 to 6, body level 0 to 7, edges `strict` or `pred` (104 settings) |
| `C_stripe1` … `C_stripe6` | the stripe direction alone at each level (6 = anything) | nothing |
| `C_body1` … `C_body7` | the body direction alone at each level, edges `pred` (6 = darker than the ground, 7 = anything) | nothing |
| `C_both1_1` … `C_both5_5`, `C_both6_6`, `C_both6_7` | both directions at the same level, edges `pred` | nothing |

## How a level is chosen (inside each fold, on the training places only; `nm_common.choose`)

1. A setting is **eligible** when, on the training frames: it draws no more boxes on clean empty frames than the
   fixed model; and no training place finds fewer placements than under the fixed model by more than that place's
   judge margin.
2. Among the eligible settings: the highest **J = found − 2 × boxes that are not on their barrel** (found per
   placement, boxes once per arrangement, as the judge counts).
3. Ties: the setting closest to the fixed model (smallest sum of the two levels, then the smaller body level,
   then `strict` before `pred`), then the first in the list.

The fixed model is always in the list and always eligible.

## What counts as success

- **The idea works** if `B_partner_fit` gets PASS from the judge. A PASS with found less than 2 placements above
  the gain margin (under +6.0) is called WEAK. NO CLEAR DIFFERENCE or FAIL: the idea does not beat the noise as
  built here, and is reported so.
- **Conditioning beats plain two-level thresholds** if B's boxes that are not on their barrel stay inside the
  margin where A's do not, or B finds more at the same number of such boxes.
- **How loose (C):** the ladders are read as a dose-response. "False boxes start" at the first level where the
  judge's clause on boxes not on their barrel or on empty frames says worse. Whether the gray-olive blue is
  reached is read off the bathroom place (found there, of 15 placements) and from the pictures.
- **The bottom edge (D):** `D_partner_free_fit` against `B_partner_fit`: found, and of the barrels the fixed
  model finds, how many get another bottom row and how many are lost with the box still on the barrel.
- **Clutter with both colors is the named trap.** Reported by name for every candidate: the boxes on the
  cluttered empty frames `lampmid3_bathtile_neg_02`, `lampmid6_bathtile_neg_02`, `lampwarm6_bathtile_neg_02`.

## Also reported for every judged candidate

- Paint outside the hand boxes (grown by 4 px) against the fixed model, and paint inside them.
- The extreme conditions (report only): found per frame, boxes not on their barrel.
- Contact sheets (photo with hand boxes; photo with the fixed and the candidate's boxes; fixed mask; candidate's
  mask with the added paint bright) of gained and lost barrels and of every new box that is not on a barrel, for
  the main candidate and for the levels where false boxes start. Looked at, and described.

## The setting offered at the end

The selection rule above, applied once to all eight places, gives one setting. It is offered as an importable
`detect_frame` for the next experiment (`candidates.py`). Its own judged number would be in-sample; the number
that counts is `B_partner_fit`'s, held out.

## Outputs

`results/2026-11-26_nearmiss/<candidate>/` (the judge's pages and `extras.json`), `summary.md`, `summary.json`;
`ENTRY.md` in this folder. A second round, if any, gets a dated addendum here, committed before it runs.
