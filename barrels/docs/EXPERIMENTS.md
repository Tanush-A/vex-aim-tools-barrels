# EXPERIMENTS.md — lab notebook

One entry per experiment, newest first. Template:

```
## YYYY-MM-DD — <name>
- **Hypothesis:**
- **Method / params:** (script + config path)
- **Data / split:**
- **Results:** (table)
- **Takeaway:**
- **Next:**
```

---

## 2026-10-22 — Where v1's errors come from (attribution), and the table prior on non-close frames

- **Hypothesis:** blue misses are shadowed faces removed by the saturation floor; orange false pixels are the hand and the reflections next to close barrels; the table prior is harmless-but-useless on frames without a close barrel.
- **Method / params:** `experiments/2026-10-22_error_attribution/run.py` on the final config `afd85483` LOSO-CV predictions (16 pool frames). Each missed pixel is attributed to the first stage that removed it (horizon → brightness → saturation floor → wall prior → class box → tie); each false pixel is "boundary halo" (≤ 4 px from a true barrel) or "elsewhere", split by hand frame. Then the table prior switched back on at k = 1.5–3. Results: `results/2026-10-22_error_attribution/`.
- **Results:**

| | orange (≈ 132 k labeled px) | blue (41 k labeled px) |
|---|---|---|
| missed: saturation floor | 2.3 % | **21.0 %** |
| missed: outside class box | 2.5 % | 3.7 % |
| missed: wall prior / brightness / tie | 0.0 / 0.2 / 0.0 % | 2.0 / 1.0 / 0.5 % |
| false: boundary halo | 1.1 % | 0.5 % |
| false: elsewhere | 3.9 % — **all of it in `top_01`/`topstripe_01`**: the lid's reflection in the glossy table next to it, median RGB (120, 102, 70), saturation 45–47, i.e. just above those frames' floor (44) and inside the orange box | 0.0 % |
| false: hand frames | 0.6 % (841 px, RGB ≈ (100, 65, 48), sat 50–55) | 0.0 % |

| table prior (band-floor config) | primary (non-close frames) | top/topstripe orange IoU |
|---|---|---|
| off | 0.809 | 0.918 |
| k 1.5 | 0.809 | 0.762 |
| k 2.0 | 0.808 | 0.297 |
| k 2.5 | 0.806 | 0.076 |
| k 3.0 | 0.800 | 0.009 |

- **Takeaway:** (1) The dominant error is blue recall: one fifth of true blue pixels are shadowed faces below the floor; lowering the floor is not the fix (the wall is right there in saturation), so recovering them needs something other than saturation — a shape/adjacency cue or a hue test. (2) Orange's false pixels are reflections on the glossy table next to close barrels (the "known confuser" from `constraints.md`; geometry can reject them later because they are below the contact row) and skin. (3) The table prior costs 0.000–0.009 on the non-close frames and gains nothing — the saturation floor already removed the table — while on the close frames it goes from harmless (k 1.5) to catastrophic (k 3). It is correctly off on this table; on a colored table it must be re-tested, with a scale cap. (4) Per-frame precision is 0.91–0.99; IoU looks low mainly because of recall on shadows and edges, and because a 1-px edge error on a 28-px barrel is ~10 %.
- **Next:** label the 10/7 wood-desk set; test the prior (with a cap) and the floor there.

---

## 2026-10-20 — Per-image saturation floor (band-derived) vs fixed; synthetic lighting-shift probe; second test evaluation

- **Hypothesis:** (Tanush) the saturation floor should not be a constant learned from training frames; the image's own known-non-barrel rows can set it. Expectation: a tie on this single-light set (the floor it derives should land near 50), and better behaviour when the background gets more colorful or the exposure changes.
- **Method / params:** `experiments/2026-10-20_v1_adaptive/run.py`. `Config.s_min_mode="band"`: floor = the `s_band_q` percentile of the saturation of the rows above the horizon (`bg_rows`, optionally plus the bottom table rows) + `s_band_margin`, clamped to [20, 120]; computed per image, nothing in the image is changed. (1) LOSO CV grid vs the fixed v1 final (`ee36a1e9`): q ∈ {99, 99.5, 99.9} × margin ∈ {5, 10, 15, 20} × source ∈ {bg, both}. (2) **Synthetic** lighting shifts applied to the *held-out* frames only (train frames untouched): gain ×0.5 / ×0.75 / ×1.25, warm cast (R×1.2, B×0.8), cool cast (R×0.8, B×1.2); fixed vs band floor, each also with the YUV chroma box and/or the re-fit. Not real data — a probe of which parts of the method depend on the lighting. (3) The adopted config evaluated once more on the test set (`final_test.py --allow-rerun`, reason recorded in its config.json). Results: `results/2026-10-20_v1_adaptive_cv/`, `_v1_adaptive_shift/`, `_v1_test_adaptive/`, overlays in `_v1_viz_adaptive/` (sheet copied to `experiments/2026-10-20_v1_adaptive/figures/`).
- **Data / split:** 16 pool frames (CV, shift), 5 test frames (once).
- **Results:**

| | fixed floor 50 (`ee36a1e9`) | band floor, bg rows, q 99.5, margin 10 (`afd85483`) |
|---|---|---|
| LOSO CV primary (orange / blue IoU) | 0.810 (0.829 / 0.791) | 0.809 (0.825 / 0.793) — tie |
| floor actually used per frame | 50 everywhere | **44–55**, derived from each frame's own wall rows (negatives 47–48, top-only 44) |
| band source "both" (adds the table rows) | | 0.81 on in-scope frames but the top-only frames drop to 0.63 / 0.00: the lid sits in the table band and drives the floor to 120 → **use the above-horizon rows only** (they can never contain barrel) |
| **test set, evaluated once each** | orange **0.844**, blue **0.811**, neg FP 0 | orange **0.843**, blue **0.813**, neg FP 0 |

Synthetic shifts on held-out frames (primary; neg FP where non-zero):

| shift | fixed floor | band floor | band + YUV box | band + re-fit (margin 3) |
|---|---|---|---|---|
| none | 0.810 | 0.809 | 0.814 | 0.816 |
| gain ×0.5 (dark) | 0.534 | 0.630 | **0.770** | 0.512 |
| gain ×0.75 | 0.760 | 0.786 | **0.824** | 0.810 |
| gain ×1.25 (clipping) | 0.558 | 0.564 | 0.491 | **0.673** |
| warm cast | 0.443 (neg FP 3.1 %) | 0.421 (1.3 %) | 0.158 (20 %) | **0.569** (1.3 %) |
| cool cast | 0.417, **blue precision 0.05, neg FP 7.7 % → disqualified** | 0.564 (neg FP 0) | 0.422 | **0.602** (neg FP 0) |

- **Takeaway:** (1) The floor does not need to be a learned constant: derived from the image's own above-horizon rows it lands at 44–55 and scores identically on real data, so **v1 adopts the band floor** (Tanush's intent; no cost). (2) Under a cool cast the fixed floor lets the bluish wall through and the method fails its own disqualification rule (7.7 % of empty-frame pixels flagged blue); the band floor rises with the wall's saturation and keeps negatives at zero. The floor is the *false-positive* guard, and adapting it is what makes that guard follow the scene. (3) What does *not* adapt is the per-class RGB boxes, and they are what breaks under casts and gain: recall collapses because the barrel colors move out of the box. The YUV chroma box fixes brightness changes (gain ×0.5: 0.53 → 0.77) but is the worst under casts; the re-fit is the only thing that helps under casts (0.44 → 0.57, 0.42 → 0.60), i.e. the barrel-side adaptation is v1.5's real job and it needs real multi-light data, not this probe. (4) The ×1.25 case clips channels; nothing recovers that, and it is a camera-exposure problem, not a thresholding one.
- **Next:** label the 10/7 wood-desk frames (3 lamp warmths × 3 directions) — that is the real version of this probe; re-run `analyze.py`, the v1 CV, `v15/run.py` and this script there, with leave-one-*light*-out folds.

---

## 2026-10-20 — v1.5 arms vs v1 final: barrel-referenced re-fit, YUV chroma box (LOSO CV only)

- **Hypothesis:** (a) re-fitting each class box to the image's own high-confidence barrel pixels (PROBLEM.md v1.5) recovers shadowed faces the train-fold box misses; (b) a box in the YUV chroma plane (brightness dropped) beats the RGB box because the clusters are brightness-elongated.
- **Method / params:** `experiments/2026-10-20_v15/run.py`: 11 re-fit variants (`pipeline.RefitConfig`: inner box 10–90 % defines "confident", new box = percentile box of those pixels ± margin·MAD, clipped to the 0.1–99.9 % train box, fallback to v1 below `min_px`) and 6 YUV-chroma variants, all starting from the v1 final config `ee36a1e9`, scored under the same leave-one-scene-out folds. **No test-set run.** Results: `results/2026-10-20_v15/`.
- **Data / split:** 16 pool frames, one table, one light.
- **Results:**

| arm | primary | Δ vs v1 | orange IoU | blue IoU (P / R) | note |
|---|---|---|---|---|---|
| v1 final | 0.810 | — | 0.829 | 0.791 (0.99 / 0.80) | |
| re-fit, default (margin 1·MAD) | 0.739 | −0.071 | 0.744 | 0.734 (0.99 / 0.74) | engaged on 12/16 (orange) and 11/16 (blue) frames; negatives never re-fit. The re-fit box is *tighter* than the train box, so it loses more shadowed pixels |
| re-fit, margin 0.5 | 0.659 | −0.151 | | | worse still |
| re-fit, margin 2 / 3 | 0.807 / 0.819 | −0.003 / +0.009 | 0.830 | 0.808 (0.99 / 0.82) | ties with v1; margin 3 ≈ the v1 box re-centered |
| re-fit, inner 25–75 | 0.434 | −0.376 | | | too few confident pixels → tiny boxes |
| YUV chroma box 1–99 | 0.805 | −0.005 | 0.842 | 0.767 (0.94 / 0.81) | tie: orange up, blue precision down (gray wall is near the blue chroma box) |
| YUV chroma box 0.5–99.5 | 0.815 | +0.005 | 0.846 | 0.785 (0.95 / 0.82) | tie |
| YUV + re-fit | 0.806 | −0.004 | 0.848 | 0.763 | tie |

- **Takeaway:** neither arm beats v1 on this data, and that is the expected result rather than a failure: with one table and one light there is **no per-image color shift for a re-fit to correct** — the only thing it can do is shrink the box toward the bright faces, which is what it did. The chroma box is a genuinely different shape at the same score (orange better, blue slightly worse); its case is generalization across lighting, which this set cannot test. Both stay implemented behind flags (`Config.refit`, `Config.box_space`) and go back on the table once a second lighting condition is labeled (the wood-desk warm/cool frames are the obvious next set). v1 config unchanged.
- **Next:** label a second light/table; re-run `analyze.py`, the v1 CV, and this script there. Separately: the table prior needs a scale cap before it is trusted on dark tables; skin vs orange needs a hue-angle test (both out of v1).

---

## 2026-10-20 — v1 on the held-out test set (single run)

- **Hypothesis:** the CV estimate (primary 0.810) transfers to the 5 untouched test frames.
- **Method / params:** `experiments/2026-10-20_v1_rgbbox/final_test.py --config .../ee36a1e9.json`, fit on all 16 pool frames, predicted the 5 test frames exactly once. Independently re-scored from the saved `pred/*.png` with `tools/eval_masks.py --split test` — identical numbers. Results: `results/2026-10-20_v1_test/` (summary.md/csv, per_image.csv, sheets, PROBLEM.md output images, predicted masks, config.json with the fitted boxes).
- **Data / split:** test = `core_04, edge_02, far_01, neg_03, touch_01`.
- **Results:**

| frame | orange IoU (P / R) | blue IoU (P / R) | neg FP o / b |
|---|---|---|---|
| **ALL (4 pos + 1 neg)** | **0.844** (0.960 / 0.875) | **0.811** (0.982 / 0.823) | **0.000 / 0.000** |
| core_04 (hand in frame) | 0.874 (0.993 / 0.880) | 0.848 (0.990 / 0.855) | |
| edge_02 | 0.791 (0.971 / 0.810) | 0.915 (0.983 / 0.929) | |
| far_01 | 0.771 (0.910 / 0.835) | 0.732 (0.948 / 0.763) | |
| touch_01 | 0.875 (0.972 / 0.898) | 0.776 (0.993 / 0.780) | |
| neg_03 | — | — | 0.000 / 0.000 |

- **Takeaway:** test ≥ CV (orange 0.844 vs 0.829, blue 0.811 vs 0.791), so the CV selection did not overfit the pool; the strawman target of IoU ≥ 0.8 per class on this table is met. Precision is ≥ 0.91 everywhere; the remaining error is recall: shadowed lower faces (both classes) and the far barrels' blurred edges. The hand in `core_04` was not flagged (it sits mostly above row 50 and at the frame edge). Negative frame: zero pixels flagged.
- **Next:** v1.5 arms (re-fit, YUV chroma) under CV only; more surfaces/lights before anything else is believed.

---

## 2026-10-20 — v1 RGB box: default config, stage ablations, parameter sweeps (LOSO CV)

- **Hypothesis:** with the saturation floor and the wall prior doing the separating, an axis-aligned RGB box is sufficient on the white table; blue is the weak class; the horizon gate changes nothing measurable (no barrel pixel is above row 105 in any frame).
- **Method / params:** `experiments/2026-10-20_v1_rgbbox/` (`config.py` BASE = the PROBLEM.md defaults; `run.py`; `sweep.py --mode ablation|coord|pair`). Leave-one-scene-out CV over the 16 pool frames (10 folds); every pool frame predicted once by a model that never saw its scene. Score per the pre-registered rule (`DECISIONS.md` 2026-10-19): primary = mean pooled orange/blue IoU over in-scope positive frames; neg FP > 0.5 % disqualifies; < 0.02 = tie → simplest. Test set untouched. Results: `results/2026-10-20_v1_base/`, `_v1_ablation/`, `_v1_sweep1/`, `_v1_sweep2_pair/`, `_v1_sweep2_coord/` (each has `sweep.csv`/`summary.md`, `configs/<id>.json`).
- **Data / split:** 16 pool frames (`window_light`), 3 of them with a hand in view.
- **Results:**

| step | config | primary | orange IoU (P/R) | blue IoU (P/R) | neg FP | note |
|---|---|---|---|---|---|---|
| BASE (PROBLEM.md defaults) | `5f1a692b` | 0.775 | 0.766 (0.87/0.87) | 0.785 (0.99/0.79) | 0 / 0 | fold std orange 0.18 (the `far` fold: 0.34), blue 0.05; top/topstripe IoU **0.00** |
| ablation: no saturation floor | | 0.046 | | | 25 % / 12 % | collapses; disqualified |
| ablation: no wall (bg) prior | | 0.551 | 0.758 | **0.344** (P 0.37) | 0 / 0 | the wall floods blue — the prior is essential |
| ablation: box only | | 0.039 | | | 25 % / 21 % | the RGB box alone is useless, as the data analysis predicted |
| ablation: no horizon gate | | 0.773 | | | | −0.002: no effect, as predicted |
| ablation: no brightness gate | | 0.775 | | | | +0.000: no effect on this table |
| ablation: **no table prior** | `6c993aa0` | **0.783** | 0.780 | 0.785 | 0 / 0 | tie with base, one stage fewer → chosen; top/topstripe IoU 0.00 → **0.87 / 0.37** |
| ablation: prior fit "all" | | 0.781 | | 0.801 | | tie; lowsat kept (safer by construction) |
| ablation: no per-image cap | | 0.749 | 0.714 | | | −0.026: the two lids dominate the box fit, as predicted |
| ablation: tie → blue | | 0.756 | | 0.723 | | R > B rule is right |
| sweep 1 around `6c993aa0` | | | | | | s_min 50: +0.019 (orange 0.828); k_bg 2.5: +0.010 (blue 0.812); k_table/table_rows: no effect (prior off); v_min 0–40 identical; box 2–98: −0.020, 5–95: −0.113; **horizon_row 90: +0.022** |
| pass-2 candidate (s_min 50 + k_bg 2.5) | `ee36a1e9` | **0.810** | **0.829** (0.99/0.84) | **0.791** (0.99/0.80) | 0 / 0 | +0.027 over `6c993aa0` → adopted (joint move exceeds the band) |
| pass-2 pair s_min_blue × k_bg | | ≤ 0.814 | | | | s_min_blue 50 / k_bg 1.5–2.0 tie with the candidate; s_min_blue ≤ 30 collapses blue precision |
| pass-2 coordinate | | ≤ 0.819 | | | | box 0.5–99.5: +0.009 (tie); everything else a tie or worse → stop (two passes max) |

- **Why the table prior lost:** on the two top-only frames the bottom band mixes bright table with the barrel's dark shadow, so the MAD scale balloons (38–55 vs 13–19 on a normal frame) and the k = 3 rejection box swallows the lid (100 % of lid pixels rejected, `median [123 146 124] scale [38 38 55]`). On every other frame the saturation floor had already removed the table, so the prior did nothing. The prior is therefore both redundant and fragile on a white table; it stays in the code (flag) for dark tables, where the analysis says it will matter, but needs a scale cap or a mode-seeking fit before it can be trusted.
- **Why horizon_row = 90 was NOT adopted** despite +0.022: the gain is entirely on the two hand frames (`far_02`, `core_03`): rows 50–90 there contain the hand, not barrels, and gating them out removes skin false positives. That is tuning to where Tanush's hand happened to be, and row 90 is inside the measured horizon range (55–100), so on other data it could cut real far barrels (a barrel at 300 mm has its top at row ≈ 99). Gate stays at 50. Logged in `DECISIONS.md`.
- **The hand is the orange error:** BASE orange IoU is 0.766 with the hand frames and **0.840 without them** (precision 0.87 → 0.96, recall unchanged). Skin sits inside the orange RGB box (the a* separation noted in constraints.md is not available to an RGB box). `s_min` 50 recovers part of this because shadowed skin is less saturated than the barrel.
- **Blue:** recall 0.80 at precision 0.99 — the misses are shadowed lower faces (sat < 50) and the wall-prior rejections (k_bg 2.5 trades 1 % precision for 3 % recall vs k = 3). Lower `s_min_blue` or higher `k_bg` floods blue with wall.
- **Takeaway:** v1 final config `ee36a1e9`: horizon gate 50, saturation floor 50 (both classes), brightness gate 40 (no effect here, kept for dark tables), table prior off, wall prior k = 2.5 on rows 0–50 (low-sat fit), RGB box 1–99 % fit after the gates with a 3000-px/frame cap, R > B tie rule. CV estimate: primary 0.810 (orange 0.829, blue 0.791), neg FP 0.
- **Next:** single test-set evaluation (same day); v1.5 barrel-referenced re-fit and the YUV chroma arm under the same folds.

---

## 2026-10-20 — Barrel color distribution in RGB (pool frames): box vs diagonal

- **Hypothesis:** (Dave 10/7, navigator K-2) the orange cluster is a brightness-elongated smear and blue is not compact, so an axis-aligned RGB box alone will swallow table/wall; the saturation floor and the band priors have to do the separating.
- **Method / params:** `experiments/2026-10-19_data_analysis/analyze.py`. Pool = the 16 train frames only (test untouched). Barrel pixels capped at 3000/image for fits (the two top-only frames hold ~70 % of all orange pixels); table band = rows 400–480, wall band = rows 0–50, "wall 50–150" = the rows between the horizon and the table edge. Boxes = per-channel percentiles; fullness = occupied voxels / box voxels; PCA on the capped sample; prior curves = median/MAD fit on low-sat (< 40) band pixels, rejection at `k` scales, averaged over frames. Full tables: `results/2026-10-20_data_analysis/stats.md` (copy in the experiment folder), figures there + `figures/`.
- **Data / split:** 16 pool frames, `window_light`.
- **Results:**

| finding | numbers |
|---|---|
| Orange cluster is elongated along brightness | PCA var fraction 0.69 / 0.29 / 0.02 (capped), linearity 0.59, cos(axis1, gray) 0.85; 1–99 box fullness 0.14 (voxel 4) / 0.30 (8) / 0.42 (16) |
| Blue is even less compact | var fraction 0.64 / 0.34 / 0.02, linearity 0.47, cos 0.80; fullness 0.14 / 0.29 / 0.42 |
| A 1–99 RGB box alone cannot separate | table band inside orange box **61 %**, inside blue box **55 %**; wall band inside blue box **86 %**; all "other" inside: 34 % / 40 % |
| The two boxes overlap heavily | overlap = 45 % of the orange box volume; 10 % of orange and 15 % of blue labeled pixels sit in it; the R > B tie rule resolves 97 % of those orange but only 62 % of those blue |
| Saturation floor does the heavy lifting | sat ≥ 40: orange 98.5 %, blue 82.6 % kept; table 1.2 %, wall band 3.2 %, all other 6.1 % kept. sat ≥ 60: orange 93 %, blue 72 %; table/wall ≈ 0 |
| The wall between horizon and table edge is the hard non-barrel region | at sat ≥ 40 it keeps **25.6 %** (vs 3.2 % for rows 0–50): it is bluish, and the blue box contains 67 % of it |
| Brightness gate buys little here | val ≥ 40 keeps ≥ 96 % of everything; it only matters for near-black pixels (none on this table) |
| Table prior (k = 2–3) | rejects 53–88 % of the saturated non-barrel pixels at the cost of 9–18 % orange / 9–16 % blue — the cost is high because shadowed barrel faces are near the (gray) table color |
| Wall prior (k = 2–3) | rejects 82–85 % of saturated non-barrel at the cost of 0.4–2.4 % orange / **4–13 % blue**. Guard never tripped. |
| Non-v1 extra: YUV chroma plane | orange box fullness 0.57, blue 0.47 (better than RGB) but both clouds run along the gray-ward diagonal (= saturation), and the blue chroma box contains **99.7 %** of other pixels. A chroma *box* is the wrong shape; a hue/saturation (polar) split would be natural. Parked for v1.5. |

- **Takeaway:** confirmed — box-shaped it is not. v1's RGB box must be fit **after** the gates (so its percentiles aren't spent on dark/desaturated pixels the gates remove anyway) and the saturation floor + wall prior are the real separators; blue recall vs wall rejection is the central trade-off (`s_min_blue` and `k_bg` must be swept jointly). Resolves `constraints.md` unknowns #4/#5 for this table/light.
- **Next:** v1 pipeline + LOSO CV (same day).

---

## 2026-10-19 — Camera geometry of AIM-4A8B6118 (focal length, tilt, horizon)

- **Hypothesis:** `camera.py`'s f = 400 and Dave's 23° tilt are close; the 70°×50° FOV figures are not.
- **Method / params:** `experiments/2026-10-19_camera_geometry/measure.py`. f from barrel silhouette width at 5 ruler distances (`calib_01..05`, D = 22 mm, camera 3 mm behind the front edge + 11 mm radius). Tilt by least squares on the image rows of the 4–10 cm marks of a tape measure laid from the front edge (`ruler_01`, rows read by eye from an upscaled crop), f fixed, principal point fixed at (320, 240).
- **Data / split:** `data/raw/4A8B_upcool_wood_{calib,ruler}_*.png` (wood desk, cool lamp; geometry only, not a segmentation set).
- **Results:**

| quantity | value | notes |
|---|---|---|
| focal length | **404 px** (400, 404, 410, 409, 400 at 64–314 mm) | consistent across all distances, so D = 22 mm + the offsets are self-consistent (but f and D are not separable from widths alone) |
| tilt | **23.3°** | rms 3.8 px over 7 marks; the 6–10 cm marks fit within 2 px, the 4–5 cm reads are the noisy ones |
| horizon row | **≈ 66** | 240 − 404·tan(23.3°) |
| bottom row ↔ ground | 31.6 mm from the camera | |

- **Takeaway:** f = 400 was a good guess; use 404. Tilt 23.3° matches Dave's "assume 23°". Freeing the principal point only trades off against tilt (cy 220 ↔ 20.7°), so it is not identifiable here; keep (320, 240). The 70°×50° FOV in `camera.py` is wrong. Horizon gate for this robot: row 60.
- **Update (same day, after Tanush measured the barrel):** the barrel is **24 mm tall, 18 mm at the ends, ≈ 25.5 mm at the bulge** (circumference 80 mm), 6 mm stripe — not 25 × 22. Re-deriving with D = 25.5: widths give **f ≈ 356** (347–358, still very consistent across distances, which also confirms the 3 mm camera-behind-front-edge offset). But the ruler-mark fit prefers f ≈ 405–420 with the tape zero at the front edge (rms 3.2 px), and only accepts f ≈ 350 if the tape zero was ~8 mm off (rms 2.6 px). A third estimate from the barrel bottom rows (contact at the near edge of the 18 mm base) gives tilt 21.5°, f 388, horizon 88 (rms 0.8 px, but the contact-point assumption is soft). **Honest summary: f ≈ 355–405, tilt ≈ 21.5–25.5°, horizon row 55–100.** Horizon gate set at row 50, which is below every fit.
- **Next:** a direct horizon measurement (mark at camera height 43.47 mm on a far wall) resolves this independently of f and barrel size; optionally a cleaner ruler frame with the tape's zero line visibly at the front edge. Re-run for any other robot.

---

## 2026-10-07 — Color baselines: fixed HSV vs. lighting (pre-labels, probe-based)

- **Hypothesis:** fixed color thresholds survive home-lighting variation well enough to segment barrels.
- **Method / params:** probe-based metrics (hand-picked probe regions, no full labels). Fixed HSV thresholds; also tried gray-world white balance as a diagnostic. Code: `experiments/2026-10-07_baselines/` (`methods.py`, `grid.py`, `fig.py`); figure `comparison.png`.
- **Data / split:** 19 home frames, warm wood desk, 3 lamp directions × 3 warmths (`{up,at,away}{cool,mid,warm}`); `color_data/` at the repo root (see `DATA.md`). No train/test split (no labels yet) — **directional findings only, small data.**
- **Results:**

| finding | numbers |
|---|---|
| Camera does NOT fully auto-white-balance | warm light shifts the whole image: mean blue channel 134 → 73 |
| Orange barrel body is robust | H ≈ 2–7, S ≈ 225 under all 9 settings |
| Blue stripe is fragile under warm light | S 236 → 103, V ≈ 60; fixed HSV catches only **17%** of it |
| Wood looks "orange" under warm light | H ≈ 15, S ≈ 170; fixed HSV flags **70%** of wood as orange |
| Lab a* separates orange from wood | barrel orange ≈ 50 vs wood ≈ 15–20; skin ≈ 29, orange cardboard ≈ 33 |
| Gray-world WB (diagnostic only) | wood FP 70% → 8%, stripe recall 17% → 100%, but over-corrects when wood dominates (grays go blue) |

- **Takeaway:** fixed thresholds fail under warm light (blue stripe recall collapses; wood floods orange). Per-image adaptation is necessary; a global "average is gray" assumption fails on a dominant table color — consistent with Dave's no-image-correction mandate (see `DECISIONS.md` 2026-10-07). New failure modes spotted for later: barrel reflections on glossy tables, shadowed barrel faces, glare on lids.
- **Next:** labeled data + real eval harness (`EVAL.md`), then v1 adaptive RGB-box thresholds with table/background rejection; plot the RGB clusters (box vs. diagonal, unknown #4 in `constraints.md`).

---

## 2026-10-07 — Lab 6: aivision + world-map accuracy (context, not a segmentation experiment)

- **Method:** barrels at measured distances; compare `show objects` world-map positions vs. ruler.
- **Results:** map distance accuracy ~1 cm at 9–14 cm (blue: real 87.5 mm vs map ~95; orange: 137.5 vs ~137). A few mm decides reachable vs. GoalCollides. **aivision consistently returns no box for close-range barrels** (occasional flicker) — the planner is blind right next to the robot. Untested: clustering/adjacency.
- **Takeaway:** the close-range blindness is a concrete, reproducible vendor failure our detector should eventually fix; world-map math is decent when a box exists.
