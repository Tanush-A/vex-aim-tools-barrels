# ENTRY.md — the text for `docs/EXPERIMENTS.md` (paste it in; newest first)

## 2026-11-26 — The bottom edge: "more paint, box disappears" (map B8, TODO D1 and K2)

**Branch** `wip/exp-bottom` (from `barrels` at `337f04c`). **Scripts** `experiments/2026-11-26_bottom/` (`PREREG.md` with addendum 1, `yardstick.py`, `run.py`, `lib.py`). **Results** `results/2026-11-26_bottom/` (`yardstick.md`, `summary.md`, `judge/`, `judge_cli/`; contact sheets in `sheets/`, not committed).

**The flaw.** The detector keeps a seen bottom when it is within 15 % of the height of the predicted one. The scorer allows 10 % from the true one. Paint a shadow or a reflection under a barrel and the box follows it down by 10 to 15 %. The barrel then counts as a miss plus a false box, and the distance read off the bottom is wrong.

**Step A, the yardstick** (today's detector, no change; 154 ordinary train frames, 172 placements). Boxes that are on their barrel and fail the strict rule because of the bottom edge:

| color step | found, placements | the bottom edge is the cause: too low / too high |
|---|---|---|
| fixed colors | 133.8 | 1 / 1 |
| saturation floors −20 | 133.6 | 4 / 3 |
| saturation floors −40 | 125.4 | 8 / 5 |
| hue ranges ±3 | 142.1 | 2 / 2 |
| mask dilated 1 px | 136.6 | 2 / 5 |
| hand thresholds | 156.8 | 1 / 3 |

- The flaw is real and small on these frames: 37 boxes over six color steps. Only half end too low.
- Of five ways to read the bottom, the stripe's row is the steadiest: outside the scorer's tolerance for 2 to 4 % of near barrels and 0 % of far ones, at every color step. The raw seen bottom: 8 to 22 %. The seen top plus a height, or the box's width: worse than both. So no candidate uses the top or the width.

**Candidates** (pre-registered; all change the bottom edge only, at the five places a bottom is decided: `resolve_bottom`, `read_edges`, `_cap_box`, `_full_slice`, `half_stripes`):

- `low`: a seen bottom more than the scorer's tolerance (10 %, at least 3 px) BELOW the predicted one: draw the predicted one. Above stays as today.
- `both`: the same in both directions.
- `predicted`: always draw the predicted bottom.
- `rows`: a row under the body counts only when the body's color fills half of the columns.
- `rows+low`: both of these.
- Round 2 (addendum 1, written after round 1): `low_uncut` = `low`, except for a stripe cut by the left or right frame edge.

**Results.** Each is judged by the standard pass rule on the same masks as today's detector. "Yardstick" and "found" are summed over the five "more paint" steps; today's are 35 and 694.5.

| candidate | fixed colors: found (gained / lost), verdict | the five more-paint steps: verdicts | yardstick | found | works |
|---|---|---|---|---|---|
| `low` | 132.7 (1 / 2), NO CLEAR DIFFERENCE | all NO CLEAR DIFFERENCE | 29 | 696.2 (+1.7) | yes |
| `both` | 132.0 (2 / 5), NO CLEAR DIFFERENCE | all NO CLEAR DIFFERENCE | 27 | 695.8 (+1.4) | yes |
| `predicted` | 131.0 (2 / 6), NO CLEAR DIFFERENCE | all NO CLEAR DIFFERENCE | 30 | 692.7 (−1.7) | no: found lower; median error near 1 → 2 px |
| `rows` | 126.7 (2 / 11), **FAIL** | 2 FAIL | 59 | 677.2 | no |
| `rows+low` | 127.7 (2 / 10), NO CLEAR DIFFERENCE | 1 FAIL, 1 PASS | 53 | 681.6 | no |
| **`low_uncut`** (round 2) | **133.7 (1 / 1)**, NO CLEAR DIFFERENCE | all NO CLEAR DIFFERENCE | **24** | **700.4 (+5.9)** | **yes** |

- `low_uncut` per step: found +0.6, +3.5, +1.2, −0.1, +0.8 placements; yardstick 7 → 4, 13 → 7, 4 → 2, 7 → 7, 4 → 4; no new box anywhere.
- `tools/judge.py --cand-det bottom_rule=low_uncut` gives the same numbers (133.8 → 133.7, NO CLEAR DIFFERENCE).
- **Bottom-edge error against the labels** (median / 90th percentile; share outside the scorer's tolerance), `low_uncut` against today. Fixed colors: near 1.0 / 3.0 px both, far 1.0 / 1.3 px both. Saturation −40: near 6.0 % → 3.8 % outside, far 3.6 → 2.3 px at the 90th percentile and 11.1 % → 0 % outside. Saturation −20: near 3.9 % → 2.2 % outside. Nowhere worse at the median.
- No verdict is PASS. The pass rule sees a gain only above +4.0 placements, and the whole flaw is 2 to 13 boxes per step. This was expected and is written in the PREREG.

**What the contact sheets show.**
- `low` fixes what it is for. 15 boxes on 8 barrels come back, on the glass table, the white tables and the gray table. Each bottom goes from 5 to 7 px low to within 2 px.
- `low` also loses 5 barrels (10 boxes) where the seen bottom was right and the prediction was wrong. Three are barrels cut by the frame side.
- Why the frame side matters: a stripe is an arc, higher at the barrel's sides than at its middle (16 px at 10 cm). With the middle cut away, the stripe reads high. So the barrel reads farther than it is, and its predicted bottom is too high. `low_uncut` leaves those boxes as they are today.
- `both` also undoes the cap's deliberate seen bottom (home `cluster_01`, lost under five color steps). It also trusts a prediction that is too low on the ottoman.
- `rows` moves clean near bottoms up, because the base's rim is an arc.

**Takeaway.** Recommended: `--cand-det bottom_rule=low_uncut`. It is the only candidate that brings the "box off" count down at every step that has the flaw, and raises found summed over the five steps by 5.9 placements. With today's colors it changes one barrel each way, and it makes the bottom no worse anywhere. Caveat: the frame-side exception was chosen after seeing round 1. Three barrels support it. The geometry is its real evidence.

**What it does not fix.**
- A very near barrel (the ottoman, 145 px tall), where the camera model's prediction is 13 % too high. That costs one barrel under three color steps.
- The bathroom barrel whose stripe is badly painted (one case).
- Boxes that are too HIGH because the lower body is not painted: about half of the yardstick.
- Bottoms of half stripes on the bathroom floor, where the seam itself is wrong.
- A camera tilt that differs between places. Every candidate leans on the predicted bottom, so a better camera model (the self-calibration) helps all of them.

**The map change on adoption** (`DETECTOR-MAP.md`; not edited here).
- Section 2, test 10, and stage 3, step 1: "a seen end within the edge tolerance is the edge" becomes "a seen end within the edge tolerance counts as seen. Its row is drawn, unless it lies more than the scorer's tolerance (10 %, at least 3 px) below the predicted row and the stripe does not touch the frame side; then the predicted row is drawn".
- The same sentence in stage 1 (`resolve_bottom`), stage 6, checks 6 and 7, stage 7 (`_full_slice`) and stage 8 (box line).
- Section 4.3, the last row ("the seen edge agrees"): the detector now has two numbers. 15 % decides whether an edge is seen. 10 % below decides where the bottom is drawn.
- B8 in section 6 is then done.
- In code, the two `DetConfig` fields go. `bottom_rows` and the rules `both`, `predicted` and `rows` are deleted. `drawn_bottom` keeps only the `low_uncut` branch. The proof harness then shows exactly the boxes this run shows.

**Next.** One look at the recommended rule with the next color-step candidate (C2 or C4), since it matters only when more is painted. Judge it again once the camera self-calibration is in.
