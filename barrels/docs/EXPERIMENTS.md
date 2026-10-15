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
