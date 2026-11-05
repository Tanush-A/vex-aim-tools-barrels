# What happened on 2026-10-28, in plain English (v1.5 build)

Written for Tanush. Numbers and details are in `EXPERIMENTS.md` and `DECISIONS.md`.

## One paragraph

v1.5 is the scaffolding for barrel detection, and most of it is built: a camera-geometry module, per-barrel ground truth made automatically from your masks (right barrel count on 20 of 21 frames) with a click-to-fix tool, a detection scorer, the output type the robot's world map reads, a bridge stub for running on the robot, and a deliberately dumb reference detector that sets the floor v2 must beat. Pixel cleanup was tried and made no difference, so v1 is unchanged. Two things wait on you: reviewing the auto-split instances (~45 minutes of clicking) and shooting the ten measured frames.

## What got built

- **Geometry** (`geometry.py`): where the horizon is, how far away each image row is, how wide and tall a barrel should look at any row, where its bottom must be if you only see its top or its stripe, and image point → ground position reproducing the robot's own `project_to_ground` to a thousandth of a millimetre. Tested against the numbers in `constraints.md`, whose table is now generated from this module (the old table used the 25 × 22 mm barrel).
- **Instances** (`instances.py`, `tools/instance_tool.py`): the class masks don't say which pixels belong to which barrel. The auto-split finds each barrel's stripe (a band of one color sandwiched in the other), uses it as a seed, cuts side-by-side barrels along a vertical line at the narrowest column, and falls back to distance-transform peaks for barrels without a visible stripe. On the real frames it gets the count right everywhere except `occl_01`, where the hidden barrel leaves no separable sliver. Your edits in the tool are saved by image point, so they replay if a mask ever changes. All 21 provisional files are committed with `reviewed: false`.
- **Detection eval** (`eval_det.py`, `tools/eval_boxes.py`): boxes matched by overlap, precision/recall/F1 per color, a looser "within 15 mm on the ground" criterion, bottom-edge error in pixels, ground error in mm, and a hard rule: one false barrel on an empty frame disqualifies. Occluded or edge-cut barrels are ignored, not punished.
- **Output type + bridge** (`detect_types.py`, `worldmap_bridge.py`): a `Barrel` converts to exactly the five fields `worldmap.py` reads. The bridge shows the two ways to run on the robot (display only, or replacing the vendor detector) without wiring either.
- **Cleanup flags**: small-blob removal, opening, hole filling as switches. All tied with v1 (best +0.010, under the 0.02 band), opening hurt. v1 stays as it was; its config hash is preserved by a test.
- **Reference detector** (`detect_cc.py`): connected components → one box per blob. With perfect pixels it scores mean F1 0.63; with v1's masks 0.45. The boxes it does find are accurate (bottom edge within 1 px, position within ~3 mm median); it loses by merging touching barrels. That gap is v2's job. These numbers are provisional until you review the instances.
- **Measured set prep**: `data/measured.csv` template, the shot list and ruler convention in `DATA.md`, `tools/attach_measured.py` to attach the truth, a fourth split `measured` that can never be tuned on.
- **Docs**: v2 proposal at the end of `PROBLEM.md` (pending Dave), detection metrics in `EVAL.md`, instance-label format in `DATA.md`, decisions logged, a draft email in `STATUS.md`.

## What I need from you

1. **Review the instances:** `python barrels/tools/instance_tool.py`. Click a barrel to select, shift-click to add, `m` merges, right-click two seeds then `w` splits, `o`/`b` fixes a color, `x` marks occluded, `n` saves and moves on. Look hardest at `occl_01`, `touch_02`, `cluster_01`, `cluster_02`. Then commit `barrels/data/labels` and tell me; I re-run the floor without the provisional flag.
2. **Shoot the measured set** (shot list in `DATA.md`, ten frames plus the horizon mark), import with `--scenes meas,...,horizon`, label masks and instances, fill in `data/measured.csv`, run `attach_measured.py`.
3. Send the v2 email once those two exist, or earlier if Dave asks.

## Caveats

- The 0.45 / 0.63 floor numbers come from unreviewed instances; expect them to move a little.
- Nothing is wired to the robot; the bridge is code plus a docstring.
- 104 tests pass; every commit is one milestone.
