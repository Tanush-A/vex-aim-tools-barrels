# check_same.py (2026-11-27)

`python experiments/2026-11-27_bluer_geom/check_same.py <scratchpad>/golden/inputs.pkl` on the 5435 masks of the proof harness (`experiments/2026-11-26_collapse`):

    inputs 5435 boxes 6152: IDENTICAL BOXES ON EVERY INPUT

`stages.found` draws the boxes of `detector.detect`, and `checks.apply` with every check off returns them unchanged. The box count, 6152, is the harness's own.
