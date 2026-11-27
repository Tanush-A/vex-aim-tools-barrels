# 2026-11-26_collapse — the proof that the collapse changed no box

The collapse of `detector.py` (TODO K1; plan in `docs/archive/DETECTOR-MAP-before-collapse-2026-11-26.md`, section 8a)
removes switches and moves code. It must not change one box. This folder is the check.

## What is compared

The detector is a pure function of the class mask and the camera. So the check needs masks and nothing else:
5435 of them, every kind of mask the detector has been asked about.

| group | masks | what |
|---|---|---|
| `real` | 261 | every train frame, segmented by the fixed color model |
| `real_erode`, `real_dilate` | 261 + 261 | the same with one pixel taken off, or added to, each color |
| `hand` | 45 | the train frames with hand-set thresholds, segmented with those |
| `pool` | 53 | the masks the occlusion scorecard cuts its barrels from |
| `damage` | 666 | those masks damaged by `degrade.py`: every level, seeds 0 to 2 |
| `scene` | 3888 | every simulated occlusion scene of the scorecard |

No test frame is in it: `build_inputs.py` checks every stem against the "test" list of `data/splits.json`.

## The files

- `build_inputs.py <barrels/ at the tag> <inputs.pkl>` makes the masks. **It must run at the tag
  `pre-collapse-2026-11-26`**: the scenes and the damaged masks come from `experiments/2026-11-19_det_occl/run.py`,
  which names detector switches that no longer exist after the collapse. `inputs.pkl` (10 MB) is not committed.
  Rebuilt on 2026-11-26 from this script: byte for byte the same as the file the check was run with.
- `run_detect.py <barrels/src> <out.json> [inputs.pkl]` runs that checkout's `detector.detect(mask, log=log)` with
  the defaults on every mask (about 3 minutes) and writes the boxes (color, box, flags, source, confidence) and the
  reason log.
- `diff.py before.json after.json [--log]` compares two such files box for box. It ends with
  `IDENTICAL BOXES ON EVERY INPUT` or `NOT IDENTICAL` (exit code 1). It also counts the inputs whose reason log
  differs while the boxes are the same; `--log` says which reasons changed into which.
- `pack_boxes.py` wrote `results/2026-11-26_collapse/before_boxes.json.gz`: the 6152 boxes the detector at the tag
  draws on the 5435 masks, without the logs. `diff.py` reads it in place of `before.json`.
- `rule_counts.py <barrels/src> <inputs.pkl> [out.md]` counts the final boxes by the rule that drew them, and every reason
  in the logs, per group of masks. It wrote `results/2026-11-26_collapse/rule_counts.md` (the numbers `docs/DETECTOR-MAP.md` quotes).
- `ENTRY.md`: the text for `EXPERIMENTS.md`.

## To repeat it

```zsh
git worktree add /tmp/pre pre-collapse-2026-11-26
python barrels/experiments/2026-11-26_collapse/build_inputs.py /tmp/pre/barrels /tmp/inputs.pkl
python barrels/experiments/2026-11-26_collapse/run_detect.py $PWD/barrels/src /tmp/after.json /tmp/inputs.pkl
python barrels/experiments/2026-11-26_collapse/diff.py barrels/results/2026-11-26_collapse/before_boxes.json.gz /tmp/after.json
```

`run_detect.py` on `/tmp/pre/barrels/src` gives the "before" side with its reason logs. Two runs of the code at the
tag give the same file.

## The rule

After every step of the collapse: the same boxes on all 5435 masks, and the test suite passes. A step that changes a
box is taken back and becomes an experiment of its own (list (b) of `docs/DETECTOR-MAP.md`, section 6).
