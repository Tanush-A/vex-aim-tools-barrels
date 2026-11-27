# Pre-registration: what can a color setting made per place reach, without hand sliders?

Written 2026-11-26 on branch `wip/exp-place-ceiling` (TODO C1, C7, the third idea of E6). Committed before any stage
of `run.py` was run. Train frames only. No test frame is loaded, viewed, scored or listed. No pixel is changed. No
learned model. Nothing that runs by default is changed.

## The question

The fixed colors find 133.8 of 172 placements on the ordinary train conditions (211 of 307 per frame). Tanush's hand
thresholds per condition find 156.8 (281). That ceiling is in-sample and was set while watching the detector.

1. **A.** Under the warm bathroom lamp the hand thresholds find 6 of 15, because the blue slider stopped at hue 60.
   With the full hue range: does blue at hue 26 to 44 paint the barrels, or the floor? What does the ceiling become?
2. **B.** If ONE frame of a condition and its boxes set the six numbers (what a calibration shot would give), with no
   slider, how much of the hand ceiling is reached on the OTHER frames of that condition?
3. **C.** What is the best a rectangle pair per condition can do at all (an oracle, in-sample)?
4. **D.** How much of the gap to the vendor does knowing the place close?

## What I looked at before writing this (honesty)

- The review documents, `EVAL.md`, the judge's sanity checks (`results/2026-11-26_judge/summary.md`): the hand
  thresholds PASS with +23.0 placements; "blue follows the light" +5.9; per-condition numbers of the forensic report.
- The slider labels of every ordinary train condition (the six numbers; printed by a listing script).
- **Home train frames with masks** (`explore/zone_geometry.py`): where the body and the stripe sit inside a box. It
  fixed the zones of `src/barrels/placecal.py` (body rows 12-35 % and 72-90 %, stripe rows 50-60 %, the central half
  of the width).
- **Bathroom train frames, all four lamps** (the place of question A):
  - raw pictures: `core_01` of the four lamps; `clutter_01`, `occl_02`, `neg_02` of the warm lamp;
  - `explore/bath_hist.py`: hue and saturation of the barrel pixels and of the floor, per lamp, pooled over frames;
  - `explore/bath_props.py` on the 12 slider-labelled frames (`core_01`, `clutter_01`, `occl_02` × 4 lamps): the hand
    label, the frame's net setting (outside weights 1 and 0.25), the condition's pooled net setting and the frame's
    "mid" setting, **each with what the detector finds on that same frame**, and nine of the twelve pictures;
  - one `hs_slider.py --render-grid` picture of the warm `core_01` with five blue settings.
  - So I know, in-sample: on the warm `core_01` the hand label finds 1 of 4 and the net and mid settings 4 of 4; on
    the warm `clutter_01` 2 of 4 against 4 of 4; a frame whose only barrel is half hidden (`occl_02`) gives no
    setting; a pooled setting finds fewer on some single frames (dim lamp `clutter_01`: 2 of 4) than that frame's own.
- A listing of the file names of the home label folder, which showed the names of home test frames. No test file
  was opened.
- **Not seen:** any setting applied to a frame other than the one it was computed from, except the pooled bathroom
  setting on the 12 bathroom frames above; any calibration at any other place; any oracle search; any judge run of
  this experiment.

The bathroom is 1 of the 8 places (15 of 172 placements). The two computations below were written while looking at
it. They have no number that was tuned on it: the zones come from the home masks, the outside weights and the range
recipe are the slider tool's own (`hsrange.NET_WEIGHTS`, `hsrange.propose`).

## The computations (fixed here; code: `src/barrels/placecal.py`, unit tests `tests/test_placecal.py`)

A setting is six numbers: per color a hue range and a saturation floor. The two fixed gates stay (rows from 50,
V ≥ 40). All of them use one frame and its hand boxes, nothing else.

- **net** (no detector). Per color: the barrel pixels are the body rows of that color's free-standing boxes and the
  stripe rows of the other color's. The must-not pixels are everything 4 px outside every box, plus the other color's
  barrel pixels. The setting is the hue range and S floor that paint the most barrel pixels minus the must-not
  pixels (outside weight 1), searched exactly over the full slider span (orange hue −30 to 60, blue hue 0 to 179).
  A color with nothing to gain keeps the fixed values. Boxes flagged occluded, truncated, held or no_stripe give no
  barrel pixels.
- **mid** (PRIMARY). The slider tool's recipe on top of net: among the net settings at outside weights 1, 0.5, 0.25,
  0.1 and the fixed values, take the one with which today's detector finds the most of that frame's boxes (then the
  fewest false boxes). Around it, per number, the run of values that work as well on that frame. The setting is the
  middle of each run that does not hit an end of the slider. It uses the detector, on the calibration frame only.
- **tool** (reference). `hsrange.propose` exactly as the slider tool computes it today (blue hue limited to 60-150,
  every pixel in a box core counted for both colors).

A frame **can calibrate** when it has at least one free-standing box. The **calibration frame** of a condition is
`core_01`; where there is none (the ABP white occlusion set), the first frame by name that can calibrate. Its
**backup** is the next frame by name that can calibrate.

## The candidates (every one is judged and reported, winners and losers)

Baseline everywhere: today's default. Judge: `barrels.judge` on the 154 ordinary train frames (`run_many` +
`compare`, as `judge.judge` does), margins from `results/baseline/margins.json`. The extreme conditions are not run.

| name | what | kind |
|---|---|---|
| `cal_core_mid` | **PRIMARY.** Every frame is scored with the mid setting of its condition's calibration frame. The calibration frame itself is scored with the backup frame's setting. | held out |
| `cal_core_net` | the same with the net setting | held out |
| `cal_core_tool` | the same with the tool's proposal | held out |
| `cal_rot1_mid` … `cal_rot4_mid` | each frame in turn: rotation r scores every frame with the mid setting of the frame k places after it among its condition's frames that can calibrate, k = ((r − 1) mod (n − 1)) + 1 (never itself); a frame that cannot calibrate gets the r-th one. "Each frame in turn, averaged" is the mean of the four. | held out |
| `cal_otherlight_mid` | one LIGHT sets the place: every frame is scored with the mid setting of the calibration frame of the next light (by name) of the same place. Places with one light keep the fixed colors. | held out |
| `cal_otherplace_mid` | CONTROL: every frame is scored with the mid setting of the calibration frame of the next place (by name; its first condition by name). | control |
| `cal_all_net` | every frame of the condition at once: the net setting of all its barrel pixels pooled | in-sample |
| `hand` | Tanush's hand thresholds per condition (median of the slider labels), as the judge's sanity check built them | in-sample |
| `relabel` | `hand`, with the four bathroom conditions replaced by the median of the 12 proposals of `write_proposals.py` | in-sample |
| `relabel_blue` | `hand`; in the bathroom his orange numbers and the proposals' blue numbers (only the blue slider widened) | in-sample |
| `oracle` | per condition the best rectangle pair found by search on its own frames (below) | in-sample |

**The proposals (A).** `write_proposals.py` holds them. A frame with free-standing barrels gets its net setting
(outside weight 1). `occl_02`, whose one barrel is half hidden, gets the net setting of its condition's frames
pooled. One number was changed by hand after looking at the picture: warm `core_01`, blue hue high 174 → 110 (the
median of the three warm proposals is the same either way). They were made on the frames they are scored on, so
`relabel` is a ceiling, like `hand`.

**The oracle (C).** Per condition, score = found (strict, per frame) minus boxes that are not on their barrel, over
its ordinary train frames. Seeds: the fixed values, the hand median, the proposals' median, the pooled net setting,
and the mid and net settings of every frame that can calibrate. From the best seed: move one number by ±1, 2, 4, 8
(hue) or ±4, 8, 16, 32 (S) to the best-scoring neighbour while the score rises, at most 12 moves. It is a search, so
it is a lower bound on the true best.

**Also computed, not judged** (`run.py cross`, counted per frame): every frame that can calibrate, applied to the
other frames of its condition (the full table behind "each frame in turn", and the same by the kind of calibration
shot); the calibration frame of every condition applied to every condition (the full table behind "another light"
and "another place").

## What counts as success

- **B, primary (`cal_core_mid`).** The judge's verdict is the pass rule. A PASS with less than +6.0 placements is
  WEAK and is called so.
  - "One calibration frame is enough": PASS and found ≥ 152.2 placements (80 % of the way from the fixed 133.8 to
    the hand 156.8).
  - "It helps but one frame is not enough": PASS below 152.2.
  - "It does not help": NO CLEAR DIFFERENCE or FAIL.
- **Which frame.** "It does not matter which frame": all four rotations PASS and their found counts span at most 8.0
  placements. Otherwise the frame matters, and the per-shot table says which kind of shot is worst.
- **Another light.** Expected: clearly worse than the same light at the bathroom and the ottoman (the lamp moves
  blue), about the same at the glass table. No pass line; the verdict and the full table are reported.
- **Another place (control).** Expected: NO CLEAR DIFFERENCE or FAIL. If it PASSes, "knowing the place" is not what
  helps, and the primary result is read as "a setting made from any barrel helps".
- **A.** Expected: `relabel` finds more than 6 of 15 under the warm lamp. Reported: found per lamp for `hand`,
  `relabel`, `relabel_blue`; the answer to "barrels or floor" from the pixel tables and the pictures.
- **C, D.** Ceilings and the table. No pass line.

15 comparisons are judged. Only `cal_core_mid` carries the main claim; the others are variants, controls and
ceilings, and with 15 of them a single PASS near the margin means little.

## What I will look at afterwards

Contact sheets (`results/2026-11-26_place_ceiling/sheets/`, not committed): the barrels the primary candidate gains
and loses against the fixed colors; the barrels the hand thresholds find and it misses; the barrels the oracle
still misses; the warm bathroom under `hand` and `relabel`; the barrels lost when another light sets the numbers.

## Outputs

`results/2026-11-26_place_ceiling/`: `summary.md`, `settings.json`, `oracle.json`, `judged.json`, `cross.json`,
`thresholds.json`, `judge/<candidate>/` (the judge's pages). `ENTRY.md` in this folder. A second round, if any, gets
a dated addendum here before it runs.

---

# Addendum, 2026-11-26: round 2

Written after round 1 was run, committed (`6671255`) and looked at. Committed before round 2 ran.

## One change to the code of round 1, and why

`run.py` first read the proposals back from the label folder. A static guard in the tests
(`test_box_proposals.py`: experiment code never names the proposal files) failed on that. `run.py` now takes the
same numbers from `write_proposals.py`. The numbers are identical; no result depends on it. The change was made
before the judge stage ran.

## What round 1 said

- The primary, `cal_core_mid`: **FAIL**. Found +8.0 placements (133.8 → 141.8; per frame 211 → 269). The clause that
  fails is one place: campus, 35 → 21 of 35.
- All four rotations FAIL, on campus, home and the ABP white table.
- Where the fixed colors fail (bathroom, ottoman, gray table) one frame reaches the hand thresholds: 42 of 46
  placements against the hand's 40.8 and the fixed 17.
- Where the fixed colors already work (campus, home, ABP white, pale wood) one frame loses barrels. In the pictures
  the lost barrels have their blue left unpainted: the blue hue range of one frame ends at 106, the barrels of other
  frames read 107 and more.
- The control fails as it should (−52.9). Another light of the same place passes (+15.1), because places with one
  light keep the fixed colors there.

## What I looked at before writing this

Everything of round 1: every table of `summary.md`, the clauses of every judge page, and these contact sheets:
both `cal_core_lost`, `hand_finds_cal_core_misses_01`, `oracle_still_missed_01`, `warm_bathroom_hand_vs_relabel_01`,
`otherlight_lost_01`, `cal_core_gained_01`.

## The question of round 2

Can a calibration shot be made safe, with a rule that has no number: never worse than the fixed colors beyond the
noise, and still the gain where the fixed colors fail?

## The candidates

| name | what |
|---|---|
| `cal_core_keep` | **Primary of round 2.** The calibration frame first tests the fixed colors. If today's detector with the fixed colors finds every free-standing box of the calibration frame (strict rule) and draws no box that is not on its barrel, every frame it calibrates keeps the fixed colors. Otherwise they get its mid setting, as in round 1. The calibration frame itself is scored by the same rule applied to the backup frame. |
| `cal_rot1_keep` … `cal_rot4_keep` | the same rule with each frame in turn (the rotations of round 1) |
| `cal_core_wide` | the calibration may only widen: per color the hue low is the lower of fixed and mid, the hue high the higher, the S floor the lower |

Free-standing boxes only, because they are the boxes the calibration is computed from; a half-hidden barrel is
missed for reasons that are not color.

## What it is worth, said before it runs

These candidates were designed after seeing where round 1 lost. They have no tuned number, but which rule to try
was chosen with the judged frames in view, and much of the outcome can be predicted from round 1 (campus keeps the
fixed colors, so its 35 come back). **A PASS here is a hypothesis for the next places that are shot, not a held-out
result.**

Called "safe on these frames": `cal_core_keep` PASS with at least 152.2 placements, and all four rotations PASS.
Reported either way, with the conditions that kept the fixed colors. 21 comparisons are judged in all.

Also added to the report, from files round 1 already wrote: how wide the hue ranges of a one-frame setting are
next to the fixed and the hand ranges.
