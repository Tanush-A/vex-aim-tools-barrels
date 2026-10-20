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
