# constraints.md — known facts + unknowns to measure

**Version:** v1 (2026-10-14; geometry measured 2026-10-19). Foundation doc — the list of every exploitable constraint. Update when a fact is measured or an unknown resolved; log scope-relevant changes in `DECISIONS.md`.

## Camera / robot

- VEX AIM camera: **640×480 color**.
- Camera height above the ground plane: **43.47 mm** (`aim_fsm/aim_kin.py`). The camera sits **27 mm ahead of the robot's center** (`camera_from_origin`); distances in this doc are horizontal distances from the camera unless stated.
- Tilt of AIM-4A8B6118: **21.5–25.5°** (measured 2026-10-19, three methods disagree; `experiments/2026-10-19_camera_geometry/`). Dave's "18–25°, assume 23°" holds. `aim_kin.py` has other robots: 25.4° (AIM-5A888218), 23.7° (AIM-32A57C18); the design spec says 18°. Measurement procedure used there: abut a ruler to the robot's front edge, read the distance d to the horizontal crosshair on the ruler surface, then `camera_tilt = atan2(43.47, d + 3) * 180/pi`.
- Focal length of AIM-4A8B6118: **≈ 355–405 px** (measured 2026-10-19). Barrel width at 5 distances gives 356 with the measured 25.5 mm diameter (very consistent across distances); the ruler-mark fit prefers 405–420 unless the tape zero was ~8 mm off; barrel bottom rows give 388. `aim_fsm/camera.py`'s hardcoded 400 is in range (Dave: an estimate, likely varies per camera); its 70°×50° FOV figures (f ≈ 457/515) are not. Principal point assumed **(320, 240)**.
- The vendor detector (aivision) runs **on the robot at 320×240**; `worldmap.py` scales its boxes ×2 to the 640×480 frame.
- Tanush's robot: **AIM-4A8B6118**. Another seen: AIM-627D8818. **Cameras differ between robots** (color response, possibly geometry).

## Barrels

- Two types: **orange** (orange body, blue center stripe) and **blue** (blue body, orange stripe). Identical size/shape, always upright on the ground plane. (A barrel held in the robot's kicker is a separate case — unknown #8.)
- Bulged barrel shape, **not a true cylinder**. Lid has an embossed "VEX" logo. In a close-range top-only view the lid shows as a large ellipse filling the lower frame (`color_data/4A8B_upmid_wood_top_01.png`).
- Size (**measured with a tape 2026-10-19**): **24 mm tall; 18 mm diameter at the lid and base; ≈ 25.5 mm at the widest point** (circumference 80 mm, ± ~1 mm); **6 mm stripe**. Dave's draft spec / `worldmap.py` say 25 tall × 22 diameter — the 22 sits between the end and bulge diameters; the planners' obstacle radius should use the bulge (12.7 mm).
- **Barrel height (24 mm) is less than camera height (43.47 mm).** The horizon rule below depends on this.

## Geometry (for later; documented now)

Pinhole model: tilt θ below horizontal, focal length f, principal-point row c_y = 240, camera height h = 43.47 mm, ground plane = the surface the robot drives on.

- **Horizon (definition):** the image row where the ground plane projects at infinite distance — equivalently, the row of exactly horizontal rays: `horizon_row = c_y − f·tan(θ)`. It is a property of the camera pose, **not a visible scene feature.** In particular, **the visible far edge of a table is not the horizon.** The table edge is at a finite distance, so it sits below the horizon row, and a barrel standing near the far edge of the table rises above the edge line and is seen against the wall (visible in `color_data/4A8B_atcool_wood_core_01.png`). Rows above the table edge can contain barrel pixels; rows above the horizon cannot.
- **Nothing above the horizon can be a barrel.** Every point of a barrel standing on the ground plane is at most 24 mm up, i.e. below the camera's 43.47 mm, so it projects below the horizon row at any distance. Assumes the barrel is on the ground plane and the robot is level (not pitched by driving over something).
- **Row ↔ ground distance:** a ground point at distance d appears at row `c_y + f·tan(atan(h/d) − θ)`. A barrel at distance d is ≈ `f·25.5/d` px wide at the bulge, with its top at row `c_y + f·tan(atan((h − 24)/d) − θ)`. So every row has an **expected barrel pixel size.**
- Numbers below use the nominal θ = 23°, f = 400; the measured ranges move them by up to ~10 %:

| | value |
|---|---|
| horizon row | **55–100 measured range** (70 nominal; best single fits 66, 74, 88) |
| bottom row (480) sees the ground at | ≈ 32 mm from the camera |
| barrel at 70 mm (the `close` scene) | rows ≈ 182–302, ≈ 126 px wide |
| barrel at 150 mm (`core`) | rows ≈ 126–192, ≈ 59 px wide |
| barrel at 300 mm (worldmap's max range) | rows ≈ 99–135, ≈ 29 px wide |
| ground at 0.5 m / 2 m | ≈ 40 px / ≈ 10 px below the horizon |

- **Sensitivity:** with f = 400 the horizon row is ≈ 50 at 25.4° tilt and ≈ 110 at 18°. For AIM-4A8B6118 the measured fits put it between rows 55 and 100. **Gate/band at row 50** for this robot (safe across every fit). To tighten: a direct measurement — a mark at camera height (43.47 mm) on a vertical surface ≥ 1 m away lands on the horizon row, independent of f and barrel size.
- Uses: size sanity check when top + bottom are both visible; infer the bottom from the top row + width when the bottom is occluded/off-frame; occlusion reasoning; choosing the prior bands.
- **Close/top-only case (working assumption, not a hard rule):** in Lab 6 Dave observed that the top-only view occurs only when the barrel's top is in the bottom half of the image. Nominal geometry agrees: the bottom edge leaves the frame once the barrel is closer than ≈ 32 mm, and by then its top is at row ≈ 290. Lab 6 was a class homework setting, so re-check this on real frames before relying on it.

## Scene assumptions

- "Table" = the ground plane the robot drives on (a table or a floor). The lower frame is mostly table unless a barrel is very close: under nominal geometry, rows below ~400 are table unless a barrel is within ≈ 45 mm of the camera. The top-only case fills the bottom of the frame with barrel and breaks this prior.
- Rows above the horizon: wall/background, never a barrel. Rows between the horizon and the visible table edge **can** contain barrels (seen against the wall).
- **Frames may contain no barrels** (Dave, 2026-10-14). Every prior and every adaptive step must work on a barrel-free frame; `neg` scenes are in every capture set.
- No deliberately adversarial objects in view. Ordinary clutter (hands, bottle caps, boxes) does appear in the 10/7 frames; "non-adversarial" means nothing placed specifically to fool the detector, not an empty scene.
- v1 data: black table, home lighting, no distractors; later other tables/lighting (goal: table-agnostic).

## Known confusers (from the 10/7 baselines; details in `EXPERIMENTS.md`)

Things that look like barrel colors to naive fixed thresholds. **v1 scenes deliberately exclude similar-looking objects and backgrounds**, so these are constraints for later milestones, not v1 test cases. Which component is expected to handle each one is noted; the table prior covers only what appears in the bottom band.

- **Wood under warm light** falls inside naive orange thresholds (H ≈ 15, S ≈ 170 vs. barrel orange H ≈ 2–7, S ≈ 225; 70% of wood flagged by fixed HSV with no table prior). **This is the case the table prior is designed for.** Open questions are whether the bottom band represents far wood too (lighting gradient, grain) and whether rejection can be tight enough to drop wood without eating barrel orange.
- **Skin** (Lab a* ≈ 29) and **orange cardboard** (a* ≈ 33) sit near barrel orange (a* ≈ 50). Not in the table band, so the table prior says nothing about them; the RGB box has to separate them (a* suggests it can).
- **Barrel reflections on glossy tables** create orange/blue smears *below* the barrel's ground contact. Likely worse on a glossy black table — check the first black-table frames. Geometry can reject them later: they are below the contact row.
- **The blue stripe under warm light** darkens and desaturates (S 236 → 103, V ≈ 60). It is the weakest class.
- **Black table (expected, not yet observed):** the table prior's color will be nearly black, so rejection-by-table-similarity will mostly remove dark pixels and won't touch bright distractors. The saturation floor, background prior, and v1.5 barrel-referenced thresholds do that work. Verify on the first black-table frames.

## How barrels feed the robot (context for the eventual drop-in)

- `aim_fsm/worldmap.py::make_new_aiv_objects()`: per aivision box → **bottom-edge midpoint** assumed to be the floor contact → `robot.kine.project_to_ground(cx, cy)` (uses tilt + focal length) → + half the barrel diameter → world (x, y) via the odometry pose.
- Barrel height padded to `max(h, 1.1*w)` (occlusion hack). Detections more than **300 mm** away are dropped as spurious.
- Path planners (wavefront, RRT) treat barrels as obstacles: RRT uses a circle of radius 11 mm + planner inflation (15 mm "skinny" / 40 mm "fat"), i.e. 26 mm in the skinny setting.
- The eventual detector should emit boxes in the same spec shape (`OrangeBarrel`, `originx, originy, width, height`) so it can drop in. **Not v1.**

## Unknowns to measure

| # | Unknown | How to measure |
|---|---------|----------------|
| 1 | ~~Barrel dimensions~~ **done** (2026-10-19): 24 tall, 18 ends, 25.5 bulge, 6 stripe | — |
| 2 | Focal length: **355–405 px** (2026-10-19, methods disagree). Principal point assumed (320, 240) | Direct horizon measurement (mark at camera height, far wall) + a cleaner ruler frame with the tape zero clearly at the front edge |
| 3 | Camera tilt: **21.5–25.5°** (2026-10-19) | Same as #2 |
| 4 | Barrel RGB distribution — **measured for the white table / window light** (2026-10-20, `EXPERIMENTS.md`): both clusters are brightness-elongated smears (PCA linearity 0.59 orange / 0.47 blue, axis ≈ gray axis), 1–99 box fullness ≈ 0.3 at voxel 8; a box alone admits 55–86 % of table/wall. Still to measure under other lights/tables | Re-run `experiments/2026-10-19_data_analysis/analyze.py` on each new labeled set |
| 5 | Table + background distributions — **measured for white table / window light**: table sat 95th pct 32, wall band 38, but the wall between horizon and table edge keeps 26 % at sat ≥ 40 (bluish); see `EXPERIMENTS.md` 2026-10-20. Other surfaces/lights still open | From labeled data, same script |
| 6 | How much auto-exposure/auto-white-balance shifts colors | Already partially characterized (see `EXPERIMENTS.md` 2026-10-07: camera does NOT fully auto-WB; mean blue 134 → 73 under warm light); extend with new data |
| 7 | Horizon row: **55–100** (2026-10-19); gate at 50 | Direct check: a mark at camera height (43.47 mm) on a vertical surface ≥ 1 m away projects onto the horizon row |
| 8 | Does the robot's own body, kicker, or a held barrel appear in the bottom rows? | Snapshot with the kicker extended / holding a barrel. Affects the table prior. |
