# The seam reading adopted (rule D of 2026-11-26_slack): what changed

Branch `wip/adopt-slack`. Not an experiment: the proof that the plain code does what the experiment's flag `slack="D"` did,
and the list of every box it changes. Train frames only. *Awaiting Tanush's "understood".*

## The collapse harness (5435 masks; `experiments/2026-11-26_collapse/`)

Three runs of the same masks (`run_detect.py`, defaults):

| run | boxes | sha256 of the boxes (first 16) |
|---|---:|---|
| `barrels` before the adoption (= `before.json` of the collapse: IDENTICAL BOXES ON EVERY INPUT) | 6152 | `fdc177f96ad13efa` |
| branch `wip/exp-slack`, `DetConfig(slack="D")` | 6207 | `4211c205a6a6d456` |
| this branch, defaults | 6207 | `4211c205a6a6d456` |

`diff.py` of the experiment's D against this branch: IDENTICAL BOXES ON EVERY INPUT. The reason logs differ on 3 inputs
(damage 1, real_dilate 1, scene 1): as many as step B15 of the collapse's second pass changed ("kept" and "duplicate"
written at another moment), which the experiment's branch, made before it, does not have.

Against `before.json`: **54 inputs change** (round-2 harness of the experiment, D: the same 54).

| group | inputs whose boxes change |
|---|---:|
| damage | 27 of 666 |
| hand | 1 of 45 |
| pool | 0 of 53 |
| real | 7 of 261 |
| real_dilate | 4 of 261 |
| real_erode | 9 of 261 |
| scene | 6 of 3888 |

New boxes not on a barrel: none in any group (the experiment's `harness.md`, D; the boxes are the same).

## Every change on the real train frames (`real/`: fixed colors; `hand/`: hand-set colors)

Scored with `counting.classify_frame` against the hand boxes. "found" = a strict hit; "off" = on its barrel, the box off.

| frame | boxes | what it is |
|---|---|---|
| real `4A8B_both_abpgray_touch_01` | + blue (249, 125, 302, 180) found; blue (294, 124, 351, 178) → (297, 124, 351, 178), found both | a barrel gained; its neighbour's box moves 3 px |
| real `4A8B_lampcool6_bathtile_clutter_01` | + orange (411, 110, 441, 141) found | a barrel gained (protected set BATH-COOL) |
| real `4A8B_lampcool6_bathtile_core_01` | orange (224, 115, 267, 166) → (220, 115, 267, 166), found both | a box moves 4 px |
| real `4A8B_lampcool6_ottoman_touch_01` | blue (243, 131, 324, 197) → (243, 128, 324, 197), found both | a box moves 3 px |
| real `4A8B_lampmid6_ottoman_core_01` | + blue (78, 136, 150, 203) found | a barrel gained |
| real `4A8B_lampmid6_ottoman_edge_01` | + blue (0, 149, 36, 219) off | on its barrel (cut by the frame side), the box off; it was missed |
| real `4A8B_lampmid6_ottoman_touch_01` | blue (242, 131, 320, 195) → (242, 129, 320, 195), found both | a box moves 2 px |
| hand `4A8B_lampwarm6_bathtile_clutter_01` | + orange (410, 110, 440, 141) found | a barrel gained |

Real: 3 found more (224 → 227 by the harness count), 1 box off where there was none, 0 lost, boxes not on their barrel
unchanged. Hand: 1 found more. The experiment measured the same for D (`results/2026-11-26_slack/round2/harness.md`:
real 7 / 261, +8 −4, found 224 → 227; hand 1 / 45, +1, found 115 → 116).

## The judge (fixed colors, ordinary train conditions)

`python barrels/tools/judge.py --cand-model default --base-callable <scratch>/base_detector.py:detect_frame`, run from
this branch: the candidate is this branch's default; the baseline is `detector.py` of `barrels` (2482c39) loaded as a
module beside it, with the same color model.

NO CLEAR DIFFERENCE. Found 133.8 → 135.4 of 172 placements (+1.6; per frame 211 → 214 of 307); 3 gained
(`both_abpgray_touch_01` #2, `lampcool6_bathtile_clutter_01` #3, `lampmid6_ottoman_core_01` #1), 0 lost, 1 moved missed →
off (`lampmid6_ottoman_edge_01` #1); boxes not on their barrel 1.9 → 1.9 per arrangement (5 → 5 per frame); empty
frames 0 → 0. The experiment's judge for D: the same (`round2/judge_unharmed_D/`).

## The never-regress check

`python barrels/tools/report.py --gate`: PASS. BATH-COOL 13 → 14 of 15 (better); every other protected set the same; no
clean empty frame gained a box. Information only: abp gray +1, lampmid6 ottoman +1 (and one missed → off),
DAVE office speckle 13 → 17 of 34 (4 barrels found that were missed; boxes not on their barrel 4 → 4).

## Rule counts

`rule_counts.md` in this folder: the final boxes by the rule that drew them and every note of the reason log, per group,
after the adoption (`results/2026-11-26_collapse/rule_counts.md`: before). Real masks: 243 boxes (239 before).
