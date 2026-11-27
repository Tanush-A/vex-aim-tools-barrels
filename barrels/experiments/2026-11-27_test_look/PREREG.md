# The planned look at the test frames, 2026-11-27, written before any test frame is opened

Written 2026-11-27 by Claude Code (agent on branch `wip/adopt-contrast`), committed and pushed before the run. Tanush (2026-11-27): "I want to see what stripe by contrast does on the test set". The model is the previous look, `experiments/2026-11-25_test_look/PREREG.md` (results `results/2026-11-25_test_look_summary.md`).

## What is scored, chosen now

- **One configuration:** the default of `barrels` at **125aed7** (the merge of `wip/adopt-contrast`): `pipeline.detect_frame(frame)` = the fixed color model `eb863d84` (orange hue 3–13 S ≥ 140, blue hue 103–119 S ≥ 113), `detector.detect` with `DetConfig()` (the collapsed detector with the seam reading), then the stripe by contrast (`contrast.add_boxes`, `ContrastConfig()`: strength floor 1.15, absolute check 0.8, extent 0.15). Called **now**.
- **For comparison, report only:** the default before the contrast stage, the same code with `contrast=False` (= the default of `barrels` at bb9fc23; `results/2026-11-27_adopt_contrast/prove.md`). Called **before**.
- **The vendor:** the robot's own detector, its boxes as saved with each frame (`data/vendor/<stem>_vendor.json`), on every test frame that has a usable vendor file, scored by the same rule against the same hand boxes. Where there is no vendor file nothing is assumed (no ASSUMED rows in this look).
- **Frames:** every frame of the test split in `data/splits.json` at 125aed7: 78 frames. They are the same 78 frames as the look of 2026-11-25.
- **Code:** `experiments/2026-11-27_test_look/run.py` (one run, no argument) then `tables.py` (reads only the numbers). `run.py --rehearse` was run on the **train** frames before this file was committed, to check the code; it opened no test frame.

## Numbers

- **Strict v2 rule** (`docs/EVAL.md`): a box matches a barrel of its color with overlap ≥ 0.5 and the bottom edge within a tenth of the height. Per barrel, per frame: found / found with the box off (a box on its barrel that fails the strict rule) / missed (`counting.classify_frame`).
- **Per placement where possible:** each physical barrel once, counting the share of its lights in which it is found (`counting.build_placements`; if two lights of one arrangement do not hold the same barrels, per frame only, and this is said).
- **Boxes that are not on their barrel** (wrong color, a second box, on nothing), per frame and once per arrangement.
- **Boxes on empty frames**, clean and with clutter.
- **By data set, by place (ordinary conditions; report-only conditions apart), by condition, and in total.** Each on every test frame (before, now), and on the frames with a vendor file (before, now, vendor side by side).
- HOME and CAMPUS also as the standard eval table (`report.py`, with the v2 score), as in the previous look.

## What is reported

`results/2026-11-27_test_look/summary.md`: the table by set and place, ours-before, ours-now, vendor; the totals; boxes not on their barrel and on empty frames; then a short reading, including where now is worse than before or than the vendor, and how the test numbers compare with the train numbers. Plus `tables.md`, `numbers.json`, `frames.json` (every frame's boxes and states, no pictures) and the two standard tables (`now_vs_before/`, `now_vs_vendor/`).

## Rules

- The test frames are opened only by `run.py`, to run the three arms. No picture of a test frame is looked at, written or shown, before or after the numbers.
- **Nothing is changed afterwards because of these numbers.** No threshold, no number of `ContrastConfig` or `DetConfig`, no rule. If a problem shows, it is reported as found on the test set; a fix would need new train-frame evidence and new test frames.
- The result is reported as it comes, including where it is worse.

## What was seen before (honesty)

- These 78 frames were looked at once before, on 2026-11-25, with the detector of that day (before the collapse, with the verify step): home 9 of 9, campus 22 of 24, the new conditions ours 14 of 32 against the vendor's 23 of 32 (4 against 5 false), the glass table 6 of 10 against 74 of 75 on train. Those numbers are known; the frames themselves (pictures) were not viewed.
- Nothing in the contrast stage was chosen on them: its numbers come from the train frames only (`experiments/2026-11-26_contrast`, leave one place out; judged 155.3 of 172 placements against 133.8). The collapse and the seam reading were also proved and judged on train frames only.
- So this look is not blind in the sense that the frames are fresh: it is the second look at the same test set. It is blind in the sense that nothing was tuned on it.
