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
- **Next:** measure the barrel with the tape (unknown #1); re-run the script for any other robot.

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
