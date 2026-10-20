# What happened overnight (2026-10-19 → 20), in plain English

Written for Tanush. Everything below is also in `EXPERIMENTS.md`, `DECISIONS.md`, `STATUS.md` and the git log, with the exact numbers and config hashes. This is the version you can read in five minutes.

## The one-paragraph version

v1 works. On the white campus table under window light, the segmentation finds 84 % of the orange barrel area and 81 % of the blue barrel area (per-pixel IoU) on five frames it had never seen, with almost no false pixels (precision ≥ 0.96) and nothing at all flagged on the empty-table frame. The two things that make it work are the saturation floor and the "whatever is above the horizon is background" prior. The RGB box by itself is nearly useless. The horizon gate and brightness gate change nothing on this table. The table prior turned out to be redundant and harmful, so it is off. The two v1.5 ideas (re-fitting the colors per image, and a YUV box) did not beat v1 here, which is expected when there is only one table and one light: there is nothing to adapt to yet.

## What I did, in order

1. **Checked your labels.** All 21 masks are valid. Edges are within a pixel or two, stripes are their own color, negatives are empty, nothing is labeled above row 50. Three frames have your hand in them; it is labeled "other" (correct). You never used the ignore class, which was fine, there was no blown-out glare on the barrels.

2. **Locked the test set.** Five frames were picked by a fixed rule and seed: `core_04, edge_02, far_01, neg_03, touch_01`. They were used exactly once, at the very end. The other 16 frames are the tuning pool. Instead of a single dev split, every tuning decision used "leave one scene out": fit on all scenes but one, predict that one, repeat for all ten scenes, so every pool frame gets predicted once by a model that never saw its scene. I also wrote the selection rule down before running anything: differences under 0.02 don't count, and anything that flags more than 0.5 % of pixels on an empty frame is thrown out.

3. **Built the code.** Four new modules (`priors`, `boxfit`, `pipeline`, `cv`) with 46 passing unit tests on synthetic images. The pipeline is a list of switchable stages, so every ablation is just a config.

4. **Looked at the pixel colors before building anything.** Plots and tables are in `results/2026-10-20_data_analysis/`. The important findings: barrel colors are long smears along the brightness axis, not blobs, so a box around them also covers 60 % of the table and 86 % of the wall. The saturation floor fixes most of that on its own. The blue-gray wall between the horizon and the table edge is the real enemy, and the two top-only frames contain 72 % of all orange pixels, so I capped how many pixels each frame contributes to a fit.

5. **Ran the default v1 config.** Score 0.775 (mean of orange and blue IoU). Negatives perfect. But: the top-only frames scored zero, and the far frame with your hand scored 0.34 for orange.

6. **Ablations (turn each stage off).** Saturation floor off: everything collapses. Wall prior off: blue drops to 0.34. Box alone: 0.04. Horizon gate off: no change. Brightness gate off: no change. **Table prior off: slightly better, and the top-only frames jump from 0 to 0.87.** The table prior fails on those frames because the bottom rows mix bright table with the barrel's dark shadow, which blows up its robust scale and makes it swallow the lid. On every other frame the saturation floor had already removed the table. So the table prior is off in v1. It stays in the code as a flag for dark tables.

7. **Parameter sweeps.** Saturation floor 50 instead of 40 helps orange (it drops more skin). Wall-prior cutoff 2.5 instead of 3 helps blue. Together they got 0.810, which is above the 0.02 band, so they were adopted. A second pass found nothing more. Two things I did *not* adopt even though the numbers said to, both logged in `DECISIONS.md`: gating at row 90 scored +0.022 but only because it masks your hand in two frames, and 90 is inside the measured horizon range, so it could cut real far barrels elsewhere; and turning the brightness gate off tied exactly, but it is a no-op here and predicted to matter on dark tables, so it stays.

8. **Test set, once.** Orange IoU 0.844, blue 0.811, zero false pixels on the negative. Slightly better than the CV estimate, so the tuning did not overfit. I re-scored the saved predictions with the independent command-line tool and got identical numbers.

9. **v1.5.** The barrel-referenced re-fit made things worse (−0.07): with no lighting shift to correct, all it does is shrink the box toward the bright faces and lose shadowed ones. The YUV chroma box tied with RGB (orange a bit better, blue a bit worse). Both are implemented behind flags and should be re-tested the moment there is a second lighting condition.

## What's weak, honestly

- **Shadowed lower faces** of both colors are the main misses (recall around 0.8–0.88). They desaturate toward the wall color, and the saturation floor is what removes them.
- **Skin looks orange to an RGB box.** With the hand frames, orange IoU on the pool is 0.77; without them it is 0.84. A hue test (Lab a*, or chroma angle) would separate them; that is a question for Dave.
- **Everything is one table and one light.** The wall prior is carrying blue, and this wall happens to be blue-gray. None of the numbers should be believed on another surface until it is measured there.
- **Camera geometry is a range, not a number** (f 355–405, tilt 21.5–25.5°, horizon row 55–100), because your barrel diameter measurement changed the width-based estimate and the ruler fit disagrees. The gate at row 50 is safe across the range.

## What I need from you

1. Read `DECISIONS.md` 2026-10-20 and say whether you agree with the two judgment calls (horizon 50 not 90; brightness gate kept).
2. Send the email draft at the bottom of `STATUS.md` to Dave, edited as you like.
3. Next data: a second light or table. The yellow-light black table is the obvious stress set, and the wood-desk frames from 10/7 could be labeled with the tool. Everything from the data analysis onward re-runs with one command each.

## Where things are

- Code: `barrels/src/barrels/`, tests in `barrels/tests/` (`cd barrels && python -m pytest`).
- Experiments: `barrels/experiments/2026-10-19_data_analysis/`, `2026-10-20_v1_rgbbox/` (`run.py`, `sweep.py`, `final_test.py`), `2026-10-20_v15/`.
- Results: `barrels/results/2026-10-20_*` (summaries and CSVs are committed; images are not). The final v1 config is `results/2026-10-20_v1_sweep2_pair/configs/ee36a1e9.json`.
- Docs: `EXPERIMENTS.md` has one entry per experiment with a table; `DECISIONS.md` has the protocol and the final-config decisions; `STATUS.md` has the state, next steps, and the email draft.
- Git: 9 commits on `barrels` since the labels landed, each one a milestone, all pushed.

One cosmetic thing: the data-analysis experiment folder is dated 10-19 and its results folder 10-20, because midnight passed between writing it and running it.
