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

## Index (newest first; the headline of each entry)

| date | experiment | headline |
|---|---|---|
| 2026-11-08 | **The hs color model, pre-registered sweep** (24 configs; branch `wip/redesign`) | home LOSO v2 0.93–0.95 at the 15th–20th-percentile S floor (v1 0.93), 0.65–0.69 at the 5th (the bluish home wall); campus 14–19 of 21 right (v1 8); nothing on any negative except two 5th-percentile configs. **The pre-registered rule picked the 5th-percentile config (campus 19/21, home 0.69): the rule ignored the home score — a flaw in the rule.** Runner-up `s15 h5-95 m4`: home 0.93, campus 17/21, Dave 0.53. Not adopted: labels + walkthrough first |
| 2026-11-08 | **Detector hardening** (a–d; branch `wip/redesign`) | v1 pixels: home 0.91 → **0.93**, campus 7 → 8; hue pixels: home 0.57 → **0.78**, Dave 0.31 → 0.40, campus 12 → **15** / 21, extra-box frames 5 → 1, negatives clean. The dark-gap path back on makes every number worse |
| 2026-11-07 | **Segmentation probe: hue sector + HSV-saturation floor** (two iterations) | plain percentile boxes on hue wrap (orange 2–168) → boxes everywhere; done properly (hue shifted, S floor from the 10th percentile, 5–95 hue): campus 12 / 21 right (v1 7), Dave 0.31 (v1 0), negatives clean, **but home 0.57** — the bluish home wall (S ≤ 110) enters the blue class at an S floor of 92 and the old finder boxes its dark gaps. Led to the hardening and the sweep |
| 2026-11-07 | **Recordings replayed** (4 clips, detector vs the 3-of-4 view) | the detector as it stands finds almost nothing in the clips (room + clutter behind): 0 raw boxes in the static and enter/leave clips, 7 one-frame blips in the pan and hand clips, all 7 suppressed by the tracker, one track shown after 2 frames. **The clips cannot judge the tracker until the front end is replaced**; re-run then |
| 2026-11-07 | **Campus attribution** (21 train frames of the campus session, count-level truth) | 7 right, 9 segmentation-only, 5 segmentation + detector, 0 detector-only. The two top-row stages (background prior, saturation floor) and the RGB boxes remove the blue bodies and the shaded orange faces in a real room; where bodies survive the stripe step works, and its one failure is the pre-registered 'glued shadow'. **Segmentation first** |
| 2026-11-06 | **First live run** (Tanush's screenshots; a diagnosis, approximate) | the stripe step took a dark gap under a false orange smear for a *shadowed* stripe (the floating box) and dropped the real stripe (band + glued shadow 92 rows, 83 allowed); the blue barrel right in every frame; the segmentation labels the laptop lid's edge, a barrel's glow and skin orange. Raw frames needed |
| 2026-11-03 eve | **Detector step 2 (the stripe) vs steps 1–3 vs the floor**, Tanush's boxes | v2 rule: floor 0.43 → steps 1–3 0.71 → **stripe 0.91**; overlap rule 0.48 / 0.86 / 0.97; misses = hidden stripes. Re-run 2026-11-05: identical |
| 2026-11-03 | **Dave's 20 snapshots** (outside check) | **0 barrel pixels on all 20**: the per-image floor and wall model assume plain top rows; the pink desk floods orange. The front end is the bottleneck |
| 2026-11-03 | Detector step 1 vs the CC floor (auto instances; provisional) | 0.78 vs 0.46 mean F1; bottoms within 1 px |
| 2026-11-03 | Camera re-fit from labeled boxes | the October preset put bottoms ≈ 20 px low; boxes pin horizon row ≈ 76 (tilt 22.25° at f 400), not f and tilt separately → `AIM_4A8B6118_BOXFIT` |
| 2026-10-28 | Pixel cleanup flags (LOSO CV) | tie (best +0.010); v1 unchanged |
| 2026-10-28 | Detection floor: CC reference detector (provisional) | 0.63 with perfect pixels, 0.45 with v1's: touching barrels merge |
| 2026-10-22 | Where v1's errors come from | 21 % of blue lost to the saturation floor (shadowed faces); orange FPs = lid reflections + the hand; table prior off is right |
| 2026-10-20 | Per-image saturation floor vs fixed; synthetic shift probe; second test run | tie on real data (0.809 vs 0.810); under a cool cast the fixed floor floods negatives (7.7 %), the band floor stays at 0; test 0.843 / 0.813 |
| 2026-10-20 | v1.5 arms: barrel-referenced re-fit, YUV chroma box | no gain with one light (re-fit −0.07, YUV tie); kept behind flags |
| 2026-10-20 | v1 on the held-out test set (once) | orange IoU 0.844, blue 0.811, 0 false pixels on the negative |
| 2026-10-20 | v1 RGB box: ablations and sweeps (LOSO CV) | final `ee36a1e9`, CV 0.810; floor + wall prior do the work; box alone 0.04; horizon 90 rejected (hand); table prior off |
| 2026-10-20 | Barrel color distribution in RGB | brightness-elongated smears; a box alone admits 55–86 % of table/wall |
| 2026-10-19 | Camera geometry of AIM-4A8B6118 | f 355–405 px, tilt 21.5–25.5°, horizon row 55–100; gate at 50 |
| 2026-10-07 | Color baselines: fixed HSV vs lighting | fails under warm light (blue stripe 17 % recall, wood 70 % flagged orange); adaptation needed |
| 2026-10-07 | Lab 6: aivision + world-map accuracy | map ≈ 1 cm at 9–14 cm; aivision returns no box for close barrels |

---

## 2026-11-08 — The hs color model: pre-registered sweep of its three fit parameters (branch `wip/redesign`)

- **Hypothesis:** a per-class hue sector plus a floor on HSV saturation, both read off the labeled home frames, with no top-row stage, finds the bodies v1 loses in a real room while the hardened detector keeps false boxes at zero. Open from the probe: how high the S floor must be to keep the bluish home wall (S ≤ 110 in the blue hue sector) out without losing shaded blue bodies (S 60–130 on the far campus barrels), and how much hue slack orange needs (home labels 5–10, campus daylight 7–13).
- **Method / params:** `experiments/2026-11-08_seg_hs/run.py`; `pipeline.Config(color_model="hs")` with `hs_s_pct ∈ {5, 10, 15, 20}` × `hs_h_pct ∈ {(2, 98), (5, 95)}` × `hs_h_margin ∈ {0, 2, 4}` = 24 configs; detector `DetConfig()` (hardened, below), camera `AIM_4A8B6118_BOXFIT`. Home = leave-one-scene-out over the 16 train frames (fit on the other scenes; v2 rule on Tanush's boxes; pixel IoU on the masks); campus = one model fit on all 16 home frames, count-level on the 21 train frames (`expected.json`) and boxes on the 4 negatives; Dave = the same model on his 12 labeled frames (indicative only: his boxes group touching barrels). **Selection rule, fixed before the run:** 0 home false detections (LOSO) and 0 boxes on the campus negatives, then most campus frames right, then home v2, then the lower S percentile. No test frame loaded. Results: `results/2026-11-08_seg_hs/summary.md`.
- **Results** (home v2 / campus right of 21 / campus negative boxes / Dave v2; v1 row = frozen `afd85483` with the same hardened detector):

| config | home LOSO v2 (o / b) | campus right | campus neg boxes | Dave v2 |
|---|---|---|---|---|
| v1 `afd85483` + hardened detector | 0.93 (0.90 / 0.96) | 8 | 0 | 0.00 |
| hs s5 h5-95 m2 **(the rule's pick)** | **0.69** (0.90 / 0.48) | **19** | 0 | 0.34 |
| hs s5 h5-95 m4 | 0.68 (0.87 / 0.50) | 19 | 0 | 0.54 |
| hs s10 h5-95 m4 | 0.78 (0.90 / 0.67) | 18 | 0 | 0.51 |
| hs s15 h5-95 m4 (runner-up) | **0.93** (0.90 / 0.96) | **17** | 0 | **0.53** |
| hs s15 h2-98 m0 | **0.95** (0.93 / 0.96) | 16 | 0 | 0.43 |
| hs s15 h5-95 m2 | 0.95 (0.93 / 0.96) | 16 | 0 | 0.44 |
| hs s20 … (6 configs) | 0.91–0.95 | 14–16 | 0 | 0.40–0.55 |
| hs s5 h2-98 m0/m2/m4 | 0.65–0.67 | 14–15 | 1–4 | 0.36–0.53 |

  Fitted numbers, `s15 h5-95 m4`: orange hue 1–14 (OpenCV 0–179), S ≥ 174; blue hue 101–121, S ≥ 113. Its four campus misses: `edge_01` (the barrel half out of the frame, its stripe cut), `occl_02` (a barrel behind the marker, no stripe visible), `room_01` (the small blue barrel at 25 cm: its orange stripe falls under the orange S floor of 174; the 5th-percentile floor, 140, keeps it) and `room_03` (an extra blue box: the blue chair in the room). The 5th-percentile configs get those but let the home wall into the blue class (S floor 64): false blue boxes on the home *positive* frames (cluster, core, far scenes), which the two home negatives do not show.
- **Takeaway:** (1) The model works where v1 does not: at the 15th-percentile floor it matches v1 at home (0.93 vs 0.93) and gets 17 of 21 campus frames right against v1's 8, with nothing on any negative; on Dave's frames the pink desk stays unlabeled and the bodies are found (the detection numbers there are limited by his per-group boxes and his camera, not the pixels). (2) The S floor is the whole blue story: 64 lets the wall in, 113 keeps it out; orange needs 2–4 units of hue slack toward yellow for daylight. (3) **The pre-registered selection rule was wrong**: it optimised the campus count and only tie-broke on the home score, so it picked a config that is a regression at home. Reported as the rule said, not adopted. (4) The orange and blue floors want different percentiles (orange lower, for the far blue barrels' stripes; blue higher, for the wall): a per-class percentile is the obvious next sweep, and it needs Tanush's box labels on the campus frames to be judged properly instead of by counts.
- **Next:** Tanush boxes the 31 campus frames (`box_tool.py --filter campus_light`); then one sweep with per-class S percentiles under a rule written with him first (proposed: home LOSO v2 ≥ 0.91, 0 boxes on every negative, then the campus v2 score); walkthrough of `pipeline.py`'s hs branch and the detector hardening; adoption decision in `DECISIONS.md`; then `DEFAULT_MODEL` changes and the live programs follow for free.

---

## 2026-11-08 — Detector hardening (a–d), on the pre-registered flaws (branch `wip/redesign`)

- **Hypothesis:** on the 16 home train frames with the frozen v1 pixels the hardened detector scores within 0.02 of the old one under the v2 rule; on the campus train frames it fixes the five "seg+det" frames whose bodies are labeled and removes the wrong-color box; under the hue segmentation it removes the false boxes on the home wall and lifts blue.
- **Method / params:** `experiments/2026-11-08_det_hardening/run.py`. `DetConfig` fields, each reversible: (a) `dark_stripe=False` — a gap with no stripe-colored pixel is not a stripe; (b) `stripe_mode="cores"` — a stripe is a connected component of the other color whose every pixel has body color within 3 stripe heights above and below (the old `"bands"` finder kept for comparison); (c) `body_min=0.1` — in the stripe's columns, outside the stripe rows, the box must hold more body color than stripe color and at least 10 % body; (d) `height_min/max = 0.5/1.5` — a stripeless piece must be barrel-tall as well as barrel-wide (added after the hue model's `core_01` sheet showed a blue jacket above the table edge boxed as a far barrel; post hoc, flagged as such). Arms old / new / new+dark under two front ends (v1; the probe's hue model). Home train (v2), Dave 12 (v2), campus train (counts). Tests: 5 new synthetic cases in `tests/test_detector.py` (183 tests pass).
- **Results:**

| front end | detector | home train v2 (o / b) | Dave 12 v2 | campus right / 21 | campus neg boxes | frames with an extra box |
|---|---|---|---|---|---|---|
| v1 | old (bands) | 0.91 (0.87 / 0.96) | 0.00 | 7 | 0 | 0 |
| v1 | **new** | **0.93** (0.90 / 0.96) | 0.00 | 8 | 0 | 0 |
| v1 | new + dark gaps | 0.93 (0.93 / 0.92) | 0.00 | 8 | 0 | 1 |
| hue (probe) | old (bands) | 0.57 (0.81 / 0.33) | 0.31 | 12 | 0 | 5 |
| hue (probe) | **new** | **0.78** (0.93 / 0.63) | **0.40** | **15** | 0 | 1 |
| hue (probe) | new + dark gaps | 0.67 (0.90 / 0.44) | 0.37 | 10 | 1 | 8 |

- **Takeaway:** every change pays or is neutral; the dark-gap path is harmful under both front ends and stays off. With v1 pixels the gain is small because v1 rarely labels enough body for a stripe to be sandwiched at all (the attribution's point); with the hue pixels it is large: the glued-shadow cases (`plain_01`, `close_01`, `window_01`, the pair in `core_01`) come back and the wall's dark gaps stop being barrels. The residual blue loss at home under the hue model (0.63) is the wall entering the blue class, a segmentation matter settled by the S floor in the sweep above.
- **Next:** walkthrough (`HOW-IT-WORKS.md` §3 "The hardening"); merge with the hs decision.

---

## 2026-11-07 — Segmentation probe: hue sector + HSV-saturation floor per class, no top-row stages (two iterations)

- **Hypothesis:** the three stages that lose the barrels in a real room — the background prior, the per-image saturation floor (both from the top 50 rows) and the RGB boxes — are all brightness-bound; hue and HSV saturation ((max − min)/max) are not. Fit per-class boxes in (hue, S) on the home train masks, keep only the horizon and brightness gates.
- **Method / params:** `experiments/2026-11-07_seg_hs_probe/run.py`, two iterations, both committed. **First** (git 9563b50): plain 1–99 / 2–98 percentile boxes on (H, S) → orange hue 2–168, blue 5–170 — hue is circular and dark labeled pixels have random hue, so the sectors covered most of the circle and blue boxes appeared everywhere (22 on the 4 campus negatives, home 0.52). **Second**: hue shifted by +30 for orange so its sector does not wrap, S floor = a percentile (5 / 10) of the labeled pixels' S, hue sector = percentiles (2–98 / 5–95) of the pixels above that floor. Detector of the day (bands), camera BOXFIT; home train v2, Dave 12 v2, campus train counts; no test frame.
- **Results (second iteration):**

| arm | home train v2 (o / b) | home neg FD | Dave 12 v2 | campus right / 21 | campus neg boxes |
|---|---|---|---|---|---|
| v1 | 0.91 (0.87 / 0.96) | 0 | 0.00 | 7 | 0 |
| S floor 5th pct, hue 2–98 | 0.42 (0.83 / 0.01) | 25 | 0.28 | 10 | 12 |
| S floor 10th pct, hue 2–98 | 0.50 (0.86 / 0.14) | 4 | 0.24 | 10 | 2 |
| **S floor 10th pct (orange ≥ 163, blue ≥ 92), hue 5–95 (orange 5–10, blue 104–118)** | 0.57 (0.81 / 0.33) | 0 | **0.31** | **12** | **0** |

  Pixel distributions behind it (home labels, V ≥ 40): orange hue 5–95 % = 4–11, S median 212; blue hue 5–95 % = 87–124 (central half 108–112), S median 224, 5th percentile 64; home *background* pixels in the blue hue sector with S ≥ 80: 8.9 % of all background pixels (the bluish-gray wall), with S ≥ 100: 1.4 %; campus negatives in the orange sector with S ≥ 100: 0.6 %, in the blue sector: 0.3 %. Campus barrel bodies: blue S 129–221, orange shaded S 223, far orange S 198, skin S 149 (hue 13).
- **Takeaway:** the direction is right (campus 12 vs 7, Dave above zero for the first time, negatives clean), the home score is not: the wall enters the blue class at an S floor of 92 and the old stripe finder then boxes its dark gaps (flaw a) while glued shadow vetoes real stripes (flaw b) — the band logs on `core_01` and `touch_02` show exactly these two. So the hardening had to come first, and the S floor had to be swept. Both done the next day (above).
- **Next:** done — see the two 2026-11-08 entries.

---

## 2026-11-07 — The four recordings replayed: per-frame detector vs the 3-of-4 view

- **Hypothesis:** the one-frame boxes Tanush saw live are removed by `tracker.Tracker` (3 of the last 4 frames) and real barrels stay shown through a missed frame.
- **Method / params:** `experiments/2026-11-07_rec_replay/run.py`: every frame of the four clips (`data/recordings/2026-11-07_campus/`, 54–63 frames each at ≈ 6 a second) through the detector as it stands (frozen v1 → stripe step, BOXFIT camera) = "raw", and through the tracker (`TrackConfig()` defaults) = "shown". Raw blip = a raw box matched (same color, IoU ≥ 0.3) to nothing in the frame before or after. Count-level; no labels.
- **Results:** r1 static (two barrels, nothing moves): **0 raw boxes in all 54 frames**. r2 pan: raw 0–1 per color, 6 count changes, 2 blips, 0 shown; one track shown after 2 frames. r3 enter/leave: 0 raw boxes. r4 hand: raw 0–1, 9 count changes, 5 blips, all suppressed, nothing shown.
- **Takeaway:** the clips were shot with the room and the clutter box behind the barrels, where the attribution says the front end finds nothing — so they say nothing about the tracker yet, except that it suppressed all 7 blips offered. Keep the folders; replay again once the front end is replaced (the script is ready).
- **Next:** re-run after the hs decision; add the lag and stickiness numbers to the `BarrelTracker` report (TODO P0-5).

---

## 2026-11-07 — Campus attribution: segmentation or detector, on the real frames (count-level truth)

- **Setting:** the 31 frames of the campus session (`DATA.md` → Session 2026-11-07) imported as `4A8B_campus_light_*`, split at import (10 test, 21 train); only the 21 train frames are used here. No box labels yet, so the truth is count-level: the barrels of each body color in the frame, counted by eye (`experiments/2026-11-07_campus_attribution/expected.json`). The detector as it stands (frozen v1 model afd85483 → stripe step, camera `AIM_4A8B6118_BOXFIT`) on each frame; per frame the segmentation's own numbers (the saturation floor it chose, the background prior's rejection rate, barrel pixels), the stripe finder's verdict on every band, a four-panel sheet (raw, tint, boxes + stripes, pixels in a color box that the floor removed), and one diagnostic arm with the floor fixed at 40. Hand verdicts per frame in `judgments.json`, merged into `results/2026-11-07_campus_attribution/summary.md`. Hand-picked barrel rectangles were also pushed through the stages one at a time (numbers below; the probe script is in the chat log, the mechanism is the same as the per-frame table).
- **Result:** 21 frames: **7 right** (the 4 negatives, `hand_02`, the two lid-only shots), **9 segmentation only**, **5 segmentation + detector**, **0 detector only**.

| frame | expected O/B | floor | orange px | blue px | boxes O/B | verdict |
|---|---|---|---|---|---|---|
| room_01 | 1/1 | 86 | 505 | 0 | 0/0 | seg: blue body 0 % labeled |
| room_03 | 1/1 | 83 | 111 | 0 | 0/0 | seg |
| plain_01 / plain_02 | 1/1 | 49 / 50 | 7306 / 3205 | 5112 / 2313 | 1/0 | seg+det: blue body 41–69 % labeled; its stripe's band 67 rows vs 62 allowed |
| core_01 | 2/2 | 73 | 2573 | 4883 | 2/0 | seg+det: big blue band 97 vs 72; far orange outside the box; a wrong-color box on the pair |
| far_01 | 2/2 | 71 | 1553 | 823 | 2/1 | seg: the 4th barrel's body 34–47 % labeled |
| cluster_02, touch_02, occl_02, edge_01, clutter_02, held_01 | | 68–120 | | 0–132 | 0/0 | seg: blue bodies 0–7 % labeled |
| close_01, window_01 | 1/0, 1/1 | 67, 49 | | | 0/0 | seg+det: shaded faces unlabeled, bands too tall (72 vs 55; 35 vs 27) |
| neg_02–05 | 0/0 | 33–120 | 0–1255 | 0 | 0/0 | ok: orange clutter labeled in neg_05, no band, no box |

- **Where the pixels go** (hand-picked rectangles, fraction surviving each stage: in the RGB box → + horizon / brightness / saturation floor → + background prior): room_01 blue body **0.80 → 0.00 → 0.00** (floor 86 against a body saturation of 52–71); cluster_02 blue **0.98 → 0.69 → 0.05**, touch_02 blue **1.00 → 0.58 → 0.05**, far_01 blue **0.95 → 0.75 → 0.40**; cluster_02 orange lit half **0.89 → 0.88 → 0.85** vs its shaded half **0.99 → 0.96 → 0.17**; core_01 far small orange (RGB 225/128/50) **0.20** in the box at all. The background prior's band statistics on these frames: median ≈ (40–60, 40–65, 35–50), scale 35–52 per channel (home: ≈ 16–22), i.e. with a dark room in the top 50 rows it rejects everything within about ±100–130 of dark gray at k 2.5 — 30–71 % of each frame, navy blue and shaded orange included. The saturation floor from the same rows is 67–120 here (home 44–55; 120 is its clamp, hit when clutter or the laptop sits in those rows).
- **The detector's share:** where a body was labeled above and below its stripe, the stripe step found it (far_01 3 of 3 anchored, hand_02 2 of 2, plain_01's orange). Every detector-level failure is pre-registered flaw (b): unlabeled shadow glued to the stripe makes its band taller than 3 × the expected stripe height (core_01 ×2, plain_01, close_01, window_01's orange), plus one flaw-(c) case (core_01: an orange box on the blue barrel of the touching pair, its band blue pixels between the orange stripe below and the orange neighbour above) and one marginal width miss (window_01 blue: 25 px vs 26 required). Flaw (a) — a dark gap taken for a stripe — did not fire on these frames; it did in the 2026-11-06 screenshots. No box on any negative; the orange clutter (a cap, a glue stick) is labeled orange and correctly left unboxed.
- **Takeaway:** the front end is most of it. Every stage that made v1 "adaptive" assumes the top 50 rows are a plain wall and the barrels are the only saturated thing: in a real room both are false, and the stages then remove the barrels themselves. The two detector flaws are real but secondary and already pre-registered. **Order: segmentation redesign first (P0-4), detector hardening (b) and (c) alongside.**
- **Next:** the segmentation probe below (hue + HSV-saturation boxes, no top-row stages); the pre-registered rule for adopting a new front end is in that entry.

---

## 2026-11-06 — First live run: the detector off the training table, from Tanush's screenshots (a diagnosis, not a tuning run)

- **Setting:** Tanush ran `live/BarrelViewer.fsm` on campus: a white table, barrels ≈ 7–15 cm away, first with the room and his hand and laptop behind them, then with the back of his laptop as a plain backdrop (the `board_*` screenshot names mean the laptop lid). He sent screenshots of the window (hand-cropped and scaled): one raw frame of the hand scene, its `seg` view, three `both` views with the board. No raw frames exist yet, so this is a diagnosis: `experiments/2026-11-06_live_first_run/run.py` resizes each screenshot to 640×480, rebuilds the class mask from the overlay tint, runs the stripe finder's tests on it band by band (the same tests as `detector.find_stripes`), then `detector.detect`. Results: `results/2026-11-06_live_first_run/summary.md`; the screenshots are in `screens/`.
- **What the window showed:** with the laptop lid behind them, the blue barrel boxed correctly in all three frames; the orange barrel boxed correctly in one (`board_b`), and in the other two a small yellow box floating above and left of it, the barrel itself unboxed. The segmentation tint: false orange along the edge where the laptop lid meets the table, on the glow the orange barrel throws on the table, on a metal rack and, in the room scene, on skin and the laptop edge; the orange barrel's shaded side and lid highlight unlabeled; the navy end of its blue stripe unlabeled.
- **What the rebuilt masks say** (`board_a`; approximate):

| band between orange above and below | size | stripe-colored px | unlabeled px | verdict |
|---|---|---|---|---|
| the dark gap under the smear at the laptop lid's edge, above the barrel's lid | 37×23 | 0 | 707 | kept as a *shadowed* stripe → the floating box (x 294–372, y 134–222; the screenshot's box sits at ≈ 295–373, 143–229) |
| the real blue stripe, with the unlabeled shadow glued to it | 162×92 | 3645 | 2758 | dropped: band 92 rows, 83 allowed (3 × the expected stripe height) |

  `board_c` the same (band 111 rows, 75 allowed). `board_b`'s rebuilt mask gives no orange box where the live run gave a correct one, so the reconstruction is not exact — one more reason for raw frames. The hand-scene screenshot run through the real live path segments to **nothing**: the crop moved the hand into the top 50 rows, the per-image saturation floor taken from those rows came out at its clamp (120 for both classes) and no pixel passed — while the live window had segmented that scene. Not what the robot saw, but a clean demonstration of the top-row dependence the Dave-frames entry found.
- **Takeaway:** two detector flaws, both fit to the 16 train frames: (1) a band with no stripe-colored pixels counts as a shadowed stripe (added 2026-11-03 for stripes too dark to label), so any dark gap between orange above and orange below is a barrel; (2) the band is one connected component of everything non-body between body above and body below, so unlabeled shadow touching a real stripe makes its band too tall and the stripe is rejected. And two segmentation flaws the committed frames do not contain: false orange on the edge of a laptop lid used as a backdrop, on a barrel's glow and on skin; shaded barrel faces unlabeled. The geometry did its job: it drew the box a barrel with *that* stripe would have.
- **Next:** raw frames (session 2026-11-07, `DATA.md`); the same analysis on real masks (`TODO.md` P0-2); then the pre-registered hardening (P0-3) and the segmentation redesign (P0-4). The multi-frame program built the same day (`BarrelTracker`) removes one-frame boxes but not these: the floating box is there frame after frame.

---

## 2026-11-03 (evening) — Detector step 2, the stripe anchor, vs step 1 vs the floor, on Tanush's reviewed boxes

- **Hypothesis (stated first):** anchoring on the stripe recovers the barrels step 1 lost to same-color occlusion and removes the hand's false boxes, without losing the touching rows step 1 already splits.
- **Method / params:** `experiments/2026-11-03_det_step2/run.py`; `detector.DetConfig(require_stripe=True)` with the stripe numbers written down first (core height 0.45–1.6 × expected, band ≤ 3 ×, width ≥ 0.4 barrel, merge > 1.4, full < 0.8, min stripe 4 px); same pixels (frozen `afd85483`) and camera (`AIM_4A8B6118_BOXFIT`) for all arms. **Ground truth = Tanush's hand-fixed `_boxes.json`** (11 of 21 files changed from the automatic split). Rules: v1 (IoU ≥ 0.5, occluded/truncated GT ignored) and v2 (`EVAL.md`; implemented in `eval_det.py` the same evening). Results: `results/2026-11-03_det_step2/` (sheets: boxes yellow/green, truth white, stripes found in magenta).
- **Data / split:** the 16 train frames. No test frames touched.
- **Results:**

| arm | primary (mean F1) | F1 orange / blue | mean IoU | bottom err (median px) | neg false det |
|---|---|---|---|---|---|
| floor (one box per blob) | 0.484 | 0.368 / 0.600 | 0.734 | 1 | 0 |
| step 1 (width + top row) | 0.862 | 0.824 / 0.900 | 0.857 | 1 | 0 |
| **step 2 (stripe)** | **0.971** | 0.941 / 1.000 | 0.829 | 1 | 0 |

**Under the v2 rule** (every barrel counts, bottom edge within max(3 px, 10 % of height); `results/2026-11-03_det_step2_v2/`):

| arm | primary (mean F1) | F1 orange / blue | mean IoU | bottom err seen · estimated (median px, n) | neg false det |
|---|---|---|---|---|---|
| floor | 0.427 | 0.292 / 0.562 | 0.753 | 1 | 0 |
| step 1 | 0.709 | 0.600 / 0.818 | 0.879 | 1 (16) · 0 (2) | 0 |
| **step 2** | **0.913** | 0.867 / 0.960 | 0.829 | 1 (23) · 0 (2) | 0 |

Per scene under v2, step 2: every scene perfect except `cluster` (orange 2 of 4, one false) and `occl` (one of two in each frame) — the barrels whose stripe is entirely hidden. 23 of 25 matched bottoms are within 1 px; the two `bottom_estimated` boxes (`top_01`, `topstripe_01`, cut by the frame) are exact.

Two intermediate versions scored 0.72: the band around a stripe includes the unlabeled shadow below it, so testing the *band's* height against the expected stripe height rejected most real stripes; measuring the stripe's colored core (10th–90th percentile rows) and taking its median row as the stripe's centre fixed that. Step 1 against the same fixed boxes: 0.862 (was 0.780 against the automatic boxes — Tanush's edits mostly fixed boxes the detector had right).
- **Takeaway:** as predicted for touching rows (`touch_02`, `cluster_02`: all found, no width rule needed), the hand (`far_02`, `core_03`: no false boxes left) and partial occlusion where the back barrel's stripe shows (`occl_01`, `occl_02`: one of the pair each). Not solved: a barrel whose stripe is entirely hidden (`cluster_01`: 2 of 4 missed + 1 false; one each in `occl_01`/`occl_02`) — those are ignored under the v1 rule, so the 0.97 flatters; the v2 rule will count them. Same-color occlusion is therefore half-solved: visible stripe → found with a full box; hidden stripe → nothing.
- **2026-11-05 follow-up:** walkthrough acknowledged; **the stripe step is the default** (`DetConfig.require_stripe=True`; `detect_image.py --step1` = steps 1–3 alone; the step-1 and Dave-snapshot experiments pinned to `require_stripe=False`). Both rules re-run at the new commit — every number identical (`results/2026-11-03_det_step2/`, `_v2/` regenerated; the old files differed only by the columns the v2 evaluator added).
- **Next:** ~~a walkthrough of step 2 for Tanush; then make it the default (it beats step 1 under both rules)~~ done 2026-11-05. For hidden stripes: a body-only candidate is allowed when it sits directly above a found barrel of the same color and is barrel-sized for its row (the "behind" case), to be pre-registered before trying.

---

## 2026-11-03 — Dave's 20 snapshots (his robot, his office): the v1 segmentation finds nothing — the front end is the bottleneck on a new scene

- **Hypothesis:** on frames from a different robot and tables never seen, segmentation + step 1 still box the mid-range barrels; the close-ups and the dark table are where it breaks.
- **Method / params:** `tools/import_dave_zip.py` (20 `DAVE_office_{speckle,dark}_snap_NN` frames; Dave's 12 drawn ground-truth boxes recovered as the pixels that differ between his `_ground_truth.png` and the raw snapshot, yellow = orange barrel, green = blue); `experiments/2026-11-03_dave_snaps/run.py`: frozen v1 `afd85483` + `detector.detect` (and the CC floor), scored with `eval_boxes.py --gt-boxes` (IoU ≥ 0.5 rule). **Outside check: no split, nothing tuned.** Results: `results/2026-11-03_dave_snaps/` (`boxes/` = the drawn output for all 20, `overlay/` = the segmentation, `2026-11-03_dave_snaps_step1/` = the score).
- **Results:** **0 barrels on all 20 frames**, 0 of 34 ground-truth barrels found. The segmentation outputs **zero orange and zero blue pixels** on every frame. Cause: the per-image saturation floor is derived from rows 0–50 ("guaranteed background"), and in Dave's office those rows hold a cluttered shelf with colorful objects, so the floor comes out at 96–120 (the clamp) instead of ≈ 50; the wall model, fit on the same rows, rejects the rest.
- **Diagnostic (not a tuning run; 12 labeled frames, step 1 on top):**

| segmentation variant | floor | barrel px (o / b) | hits o / b of 20 / 10 | false boxes | primary |
|---|---|---|---|---|---|
| v1 as is (band floor + wall model) | 96–120 | 0 / 0 | 0 / 0 | 0 | 0.00 |
| fixed floor 50 (the v1 fallback option) | 50 | 13 k / 80 k | 2 / 1 | 13 | 0.13 |
| fixed floor 50, wall model off | 50 | 262 k / 284 k | 8 / 7 | 67 | 0.30 |
| band floor, wall model off | 96–120 | 170 k / 127 k | 11 / 2 | 38 | 0.29 |

Even with the adaptive parts switched off the pink speckled desk floods the orange class (262 k orange pixels in 12 frames): the fixed RGB boxes do not separate Dave's desk from barrel orange either.
- **Takeaway:** the v1 front end does not transfer to Dave's office at all, for two reasons the v1 data could not show: (1) "rows above the horizon are plain background" is false in a cluttered room — both adaptive stages are built on it; (2) the RGB boxes admit his desk. The detector logic cannot be judged on these frames until the segmentation is redone. This is exactly Dave's 2026-10-30 condition for going back to the segmentation ("only if its flaws actually cost detections"): they cost all of them. His close-up frames (lid filling the frame, bottom far below it) and his dark warm-lit table are additional cases our data does not have.
- **Next:** decide the segmentation redesign with Dave (v2.1 pulled forward): background statistics that do not rely on the top rows; barrel-referenced color rather than fixed boxes; test on Dave's 12 + our frames. Keep Dave's frames as an outside check, not tuning data.

---

## 2026-11-03 — Detector step 1 (blobs → count by expected width → bottom from the top row) vs the CC floor — PROVISIONAL

- **Hypothesis (stated first):** counting barrels by the expected width and filling hidden bottoms from the top row lifts detection F1 well above the connected-components floor on the same pixels, because the floor's losses were merged touching barrels and shadow-shortened boxes, not misplaced edges.
- **Method / params:** `experiments/2026-11-03_det_step1/run.py`; `detector.DetConfig()` defaults (close 3 px, min blob 20 px, bottom tolerance 15 % / 4 px, width window 0.4–1.6×, min expected width 16 px; none tuned); camera `AIM_4A8B6118_BOXFIT` (below). Both arms run the frozen v1 model `afd85483` on each frame; arm `cc` = `detect_cc`, arm `step1` = `detector.detect`. Scored with the existing `eval_det` (IoU ≥ 0.5, VOC-style ignores; the v2 bottom-edge rule is M2) against the **unreviewed auto-split instances**. Results: `results/2026-11-03_det_step1/` (sheets: boxes in class color, truth in white).
- **Data / split:** the 16 train frames. No test frames touched.
- **Results:**

| arm | primary (mean F1) | F1 orange / blue | mean IoU of matches | bottom-row err (median px) | neg false det |
|---|---|---|---|---|---|
| cc (floor) | 0.461 | 0.341 / 0.581 | 0.750 | 1.0 | 0 |
| step 1 | **0.780** | 0.833 / 0.727 | 0.868 | 1.0 | 0 |

With the old preset camera (f 404 / tilt 23.3) step 1 scored 0.519 and its bottom edges were 21 px off (median): the geometry, not the detector logic, was the limit — see the next entry.
- **Takeaway:** as predicted. Touching rows (`touch_02`, `cluster_02`) now split correctly; shadow-shortened boxes are extended to the right bottom. What remains: same-color occlusion (`occl_01`, `occl_02`: the blob holds two barrels one behind the other, width says one) and `cluster_01` (4 bunched barrels → 2 found). The hand in `far_02`/`core_03` leaves one false box each (barrel-sized skin blobs). Provisional ×3: the camera was fit on these frames, the pixels come from a model fit on these frames, the instances are unreviewed.
- **Next:** step 2 = the stripe anchor (one barrel per stripe inside merged blobs; "barrel" ≠ "orange thing"); M2 eval under the v2 rule on Tanush's box labels; the calib session replaces the box-fit camera.

---

## 2026-11-03 — Camera re-fit from labeled boxes: the preset put bottoms ≈ 20 px too low

- **Hypothesis:** the preset `AIM_4A8B6118` (f 404, tilt 23.3°, horizon 66) is inconsistent with the labeled barrels; one (f, tilt) makes both the barrel height and the barrel width per row consistent with the known barrel (24 × 25.5 mm) and camera height (43.47 mm).
- **Method / params:** `experiments/2026-11-03_geo_boxfit/run.py`: the 24 unflagged (fully visible) GT instances on the train frames; for each, the model must reproduce the bottom row from the top row and the width at the bottom row; grid over f 280–460, tilt 15–32°; also tilt alone with f held at the two independently measured values (356 from widths, 400 from aim_fsm). Results: `results/2026-11-03_geo_boxfit/fit.json`.
- **Results (predicted − measured, px):**

| camera | f | tilt | horizon | bottom err mean / |med| / p90 | width err mean / |med| / p90 |
|---|---|---|---|---|---|
| preset 4A8B | 404 | 23.30 | 66.0 | +13.5 / 19.6 / 27.7 | +7.4 / 7.4 / 22.8 |
| nominal | 400 | 23.00 | 70.2 | +7.7 / 13.7 / 21.9 | +5.3 / 5.7 / 20.7 |
| free fit | 298 | 29.00 | 74.8 | 0.0 / 6.2 / 14.2 | +0.1 / 3.0 / 16.5 |
| f = 356 | 356 | 24.75 | 75.9 | −0.5 / 5.6 / 13.7 | +1.5 / 2.7 / 17.1 |
| **f = 400 (adopted)** | 400 | 22.25 | 76.4 | −0.8 / 5.3 / 13.4 | +2.3 / 3.1 / 17.7 |

The cost surface is flat along a ridge (everything from f 280 to 460 is within 10 % of the best with the matching tilt): **the boxes pin the horizon row (≈ 75–76), not f and tilt separately.**
- **Takeaway:** the October preset's horizon (66) is 10 rows too high for these frames; every fit agrees on ≈ 76, inside the measured 55–100 band. Adopted as the **provisional** preset `AIM_4A8B6118_BOXFIT` (f 400 kept — Dave: f ≈ 400, varies little between robots — tilt 22.25°). The p90 of 13–17 px is the unreviewed instance boxes as much as the camera.
- **Next:** the 12-frame `calib` session (known distances) fixes f and tilt independently; then retire the box fit.

---

## 2026-10-28 — Pixel cleanup flags on v1 (LOSO CV): a tie, v1 unchanged

- **Hypothesis (stated first):** a tie — v1's false pixels are hundreds-of-pixel lid reflections and edge halos, its misses are shadowed faces; speck removal and hole filling touch neither.
- **Method / params:** `experiments/2026-10-28_v1_cleanup/run.py`: `min_blob_px` ∈ {10, 25, 50, 100}, `open_px` ∈ {3, 5}, `fill_holes`, two pairs, on the v1 final `afd85483`, same folds and rule. Results: `results/2026-10-28_v1_cleanup/`.
- **Results:** base 0.809; small-blob removal +0.000 to +0.003; opening −0.006 (3) / −0.024 (5): it eats the thin far barrels; hole filling +0.009; best pair (blobs 25 + holes) +0.010. All within the 0.02 band → **v1 stays at `afd85483`**; the flags remain in `Config` (default off, hash-preserving).
- **Takeaway:** as predicted. Hole filling's +0.009 is real but tiny (the stripe edge and the VEX logo); worth re-checking once detection, not IoU, is the metric.

---

## 2026-10-28 — Detection floor: connected-components reference detector (BASELINE, not v2) — PROVISIONAL

- **Hypothesis:** the harness works end to end; with perfect pixels the floor is limited by touching barrels merging; with v1's pixels it is also limited by fragmentation of shadowed faces.
- **Method / params:** `experiments/2026-10-28_det_baseline/run.py`. Arm A: ground-truth class mask → CC → boxes; arm B: v1 LOSO-CV predicted mask → CC → boxes. Scored with `eval_det` (greedy IoU ≥ 0.5, VOC-style ignore flags, loose = projected ground position within 15 mm) against per-barrel instances. **Instances are the automatic split, not yet reviewed by Tanush**, so the numbers are provisional (`results/2026-10-28_det_baseline_PROVISIONAL/`); the entry will be replaced after the review.
- **Results (in-scope frames, 16 pool):**

| arm | primary (mean F1) | F1 orange / blue | loose F1 o / b | mean IoU of matches | bottom-row err (median px) | projected ground err (median mm) | neg false det |
|---|---|---|---|---|---|---|---|
| A: GT mask → CC | 0.633 | 0.600 / 0.667 | 0.600 / 0.762 | 0.959 | 0.0 | 0.0 | 0 |
| B: v1 mask → CC | 0.448 | 0.333 / 0.562 | 0.429 / 0.710 | 0.750 | 1.0 | 2.7 | 0 |

Geometry sensitivity (arm B, projected ground error): median 2.2–3.8 mm, p90 32–82 mm across the camera range corners — the p90 is merged boxes, not the camera.
- **Takeaway:** the harness runs: GT instances → eval → tables → re-scorable `det.json`. Even with perfect pixels a CC detector finds only ~63 % of barrels (every touching pair becomes one box, often the wrong color), which is exactly the gap v2 is for: splitting by expected width per row and the stripe structure. With v1's pixels the floor is 0.45 F1; matched boxes are good (IoU 0.75, bottom edge within 1 px), so the loss is in *which* blobs exist, not where their edges are. Zero false detections on negatives.
- **Next:** Tanush reviews the instances (`tools/instance_tool.py`); re-run without `--allow-unreviewed` → the non-provisional floor; measured set.

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
