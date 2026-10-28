# STATUS.md — current state

**Updated:** 2026-10-28. Meeting brief: `docs/MEETING-2026-10-28.md`. Plain-English v1 summary: `docs/Post-v1-SUMMARY.md`.

## Where we are

- **v1 is done and evaluated** (unattended block, night of 2026-10-19→20; plain-English recap in `docs/OVERNIGHT-2026-10-20.md`).
  - Final config `afd85483` (`results/2026-10-20_v1_adaptive_cv/configs/`): horizon gate row 50, **saturation floor derived per image** from the rows above the horizon (99.5th pct + 10; lands at 44–55 here), brightness gate 40, **table prior off**, wall prior k = 2.5 (rows 0–50), RGB box 1–99 % fit after the gates (3000 px/frame cap), R > B tie rule. Chosen by leave-one-scene-out CV on the 16 pool frames under the pre-registered rule (`DECISIONS.md` 2026-10-19/20).
  - **Test set (5 frames): orange IoU 0.843 (P 0.96 / R 0.88), blue IoU 0.813 (P 0.98 / R 0.83), negative frame 0 pixels flagged.** (Evaluated twice — once with the fixed floor, 0.844 / 0.811, once after adopting the per-image floor; both logged.) CV estimate 0.825 / 0.793, so no overfit. Overlays of every frame: `experiments/2026-10-20_v1_adaptive/figures/overlays_sheet.png`.
  - What the ablations showed: the saturation floor and the wall prior are the whole separation (box alone: IoU 0.04; without the wall prior blue drops to 0.34); the horizon gate and brightness gate change nothing on this table; the table prior is redundant here and destroys the top-only frames (shadow inflates its MAD scale) — off for v1, kept as a flag for dark tables.
  - Error attribution (`EXPERIMENTS.md` 2026-10-22): 21 % of true blue pixels are shadowed faces removed by the saturation floor; orange false pixels are reflections next to close barrels and the hand; the table prior is useless-but-harmless on non-close frames (−0.000 to −0.009) and catastrophic on close ones above k 1.5.
  - Known weak spots: shadowed lower faces (both classes, recall ≈ 0.8–0.88); the hand (skin is inside the orange RGB box; orange IoU on the pool is 0.77 with the hand frames vs 0.84 without); far blurred barrels.
- Package: `src/barrels/{io,labeling,eval,splits,viz,priors,boxfit,pipeline,cv}.py`, 46 tests; experiments in `experiments/2026-10-19_data_analysis/`, `experiments/2026-10-20_v1_rgbbox/`; every number in `EXPERIMENTS.md` points to a `results/` folder with its config hash and git commit.

## Next steps (in order)

1. ~~Repo setup~~ ✓ 2. ~~Docs~~ ✓ 3. ~~Review~~ ✓ 4. ~~Email Dave~~ ✓ (reply logged) 5. ~~Labeling tool~~ ✓ 6. ~~Shoot + label v1 set; camera geometry~~ ✓ 7. ~~Eval harness, v1 experiment, test evaluation~~ ✓
8. ~~Send the v1 check-in email to Dave~~ ✓ sent 2026-10-22 (text in `SUMMARY.md`), proposing the v2 scope. **Waiting for his reply; v2 starts with whatever changes he wants.** Still open for Tanush: confirm the two judgment calls in `DECISIONS.md` 2026-10-20.
9a. ~~Per-image saturation floor~~ ✓ adopted (ties on real data; keeps negatives clean under a synthetic cool cast where the fixed floor fails). The synthetic probe also says: the fixed RGB boxes are what break under lighting shifts → v1.5's job, needs real multi-light data.
9. ~~v1.5 arms, CV only~~ ✓ run: the re-fit **hurts** (−0.07; it tightens the box) and the YUV chroma box **ties** (+0.005) — with one table and one light there is nothing for a re-fit to adapt to. Both stay as flags; re-test on the second lighting condition (`EXPERIMENTS.md` 2026-10-20 v1.5).
10. **More data before more tuning:** a second table/light (the warm black table is the obvious stress set), then the Pittsburgh wood desk. Re-run `analyze.py` and the CV on each new set; the v1 config must be re-validated, not assumed.
11. Later: a scale cap / mode-seeking fit for the table prior; hue-based separation of skin from orange (a*/chroma angle) — both out of v1.

## Navigator requests

- N-001 done (2026-10-14): `NAVIGATOR.md` registered in `barrels/CLAUDE.md` (docs table + end-of-session checklist).
- N-004 done (2026-10-14): saturation floor, brightness gate, box-fullness report in `PROBLEM.md`; capture guidance in `DATA.md`; logged in `DECISIONS.md`.
- N-002 done (2026-10-19): tilt + focal length measured (`EXPERIMENTS.md` 2026-10-19; `constraints.md` updated).
- N-003 done (2026-10-14): confusers section in `constraints.md`.
- Review notes applied (2026-10-14): barrel-size provenance, table band default, stripes rule + negative-frame metric in `EVAL.md`. **Deferred:** moving `color_data/` into `barrels/data/raw/` — do it together with the `top&stripe` rename when the labeling tool lands (step 5), so paths change once.

## Housekeeping

- ~~`color_data/` move + `top&stripe` rename~~ ✓ done 2026-10-14, now `barrels/data/raw/`. `snapshots/4A8B_upcool_wood_closeup_01.png` (gitignored folder) is named per convention — move it into `data/raw/` if wanted.
- Geometry tightening (optional, cheap): a mark at camera height (43.47 mm) on a far wall gives the horizon row directly. Worth doing next time the robot is on a table near a wall.

## Open questions for Dave

0. (new, v1) The wall prior is doing most of the work on blue; on a wall that is not blue-gray it may be unnecessary — fine to keep it adaptive? And: skin lands inside the orange RGB box; is a hue-angle (a*/chroma) test acceptable in v1.5, or does he consider that "another color space" for later?

1. Is the eventual output a drop-in aivision replacement (host-side, same spec into worldmap)? Latency budget?
2. How will "good" segmentation be judged (metrics, numeric targets)?
3. Close barrels: full predicted (unclipped) boxes later? Is fixing the world-map side (focal length, the 1.1·w pad) in scope?
4. Can we get `detect.py` + `bounding_boxes*.png` from his zip? Lab 6 student submissions / the ChatGPT watershed conversation?
5. What's on the vex-aim-tools `openvocab` / `depthmap` branches — anything reusable?

## Blockers

None.

## Draft email to Dave (v1 result) — Tanush sends

Subject: Barrel detector: v1 color segmentation results

Hi Dave,

v1 is done and evaluated. Short version: on a white matte table under window light, the adaptive-threshold segmentation gets per-pixel IoU 0.84 (orange) and 0.81 (blue) on a held-out test set, with precision ≥ 0.96 and zero false pixels on the no-barrel frame. The only things learned from labels are the two per-class RGB boxes; every other threshold is derived from the image at hand.

What worked and what didn't, from the ablations (leave-one-scene-out CV on 16 frames, test set touched once):
- The saturation floor and the above-horizon "wall" prior do essentially all of the separating. Both are set from the image itself: the floor is the 99.5th percentile of the saturation of the rows above the horizon plus a margin (it lands at 44–55 on these frames), and the wall prior is a median/MAD model of those same rows. An RGB box alone scores 0.04 IoU: the barrel clusters are smears along the brightness axis (PCA linearity 0.6 / 0.5), so a box that covers shadowed faces also covers the table and wall.
- The horizon gate and the minimum-brightness gate changed nothing on this table (no barrel pixel is above row 105 in any frame; nothing is dark enough to trip the brightness gate). Both stay as flags.
- The bottom-rows "table" prior was redundant here and actively harmful on the close/top-only frames: the barrel's shadow inflates the band's MAD scale and the prior then swallows the lid. It's off in v1; it needs a scale cap before it's trustworthy on a dark table.
- Blue recall (0.82) is the weak spot: shadowed lower faces desaturate toward the blue-gray wall.
- Skin sits inside the orange RGB box. With the three frames that have my hand in them, orange IoU on the pool is 0.77; without them 0.84. A hue-angle test would separate them (Lab a* ≈ 29 vs 50) — is that fair game for v1.5, or does it count as "another color space"?

Camera: f ≈ 355–405 px and tilt ≈ 21.5–25.5° for AIM-4A8B6118 depending on method (barrel-width vs ruler), horizon row 55–100. I measured the barrel: 24 mm tall, 18 mm at the ends, 25.5 mm at the bulge (circumference 80 mm), 6 mm stripe — the 22 mm in worldmap.py is between the two diameters.

Everything is in the repo (branch barrels): docs/EXPERIMENTS.md has every number with a results folder and config hash; docs/STATUS.md has the state. Next: v1.5 (barrel-referenced re-fit, YUV chroma box) under the same CV, then a second table/light before anything else is believed.

Thanks,
Tanush
