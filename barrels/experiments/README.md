# experiments/

One folder per experiment, `<date>_<name>/`, with the script that produced a claim. What each one found is in
`docs/EXPERIMENTS.md`; what it wrote is in `results/<date>_<name>/`.

## Experiments dated before 2026-11-26 run at the tag `pre-collapse-2026-11-26`

On 2026-11-26 the detector was collapsed (`2026-11-26_collapse/`, `docs/DETECTOR-MAP.md`): `DetConfig` lost its 30
on/off switches and the `stripe_mode` setting. It keeps the 20 numbers. The switches that were on are plain code now. The
switches that were off are deleted with their code. Step 1 alone (`require_stripe=False`, `detect_step1`,
`detect_image.py --step1`) is gone too.

Many scripts dated before 2026-11-26 name those switches (`dataclasses.replace(det.DetConfig(), side_hidden=False)`,
"arms" that pin every switch, `find_stripes(..., narrow=...)`, `barrel_from_stripe`, `caps_behind(mask, found, used, ...)`).
They were not rewritten. They are the record of what was run. To run one again:

```zsh
git worktree add /tmp/pre pre-collapse-2026-11-26
cd /tmp/pre && PYTHONPATH=/tmp/pre/barrels/src python barrels/experiments/<date>_<name>/run.py
```

A script that only calls `det.detect(mask, det.DetConfig(), cam)` or reads the reason log runs on today's code as
before. That covers everything `run_all.py` starts (`2026-11-24_vendor`, `2026-11-24_adaptive`,
`2026-11-24_adaptive_range`, `2026-11-25_color`).

`report.py --cand-det field=value` still takes the 20 numbers. For a removed switch it stops with a message that names
the tag.
