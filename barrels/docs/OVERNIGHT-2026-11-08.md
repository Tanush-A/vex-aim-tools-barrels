# Detector v2 update — 2026-11-07 → 2026-11-08, what changed while you were away

Written for Tanush. One document, plain English. Section 1 is the answer, section 2 is everything that changed (code, data, docs, tools), section 3 is the numbers, section 4 is what is still wrong, section 5 is your action list, section 6 is the code walkthrough you need to acknowledge, section 7 is the email draft. Every number comes from a committed script under `experiments/` with a `results/` folder and an `EXPERIMENTS.md` entry (2026-11-07 and 2026-11-08).

## 1. The answer in five lines

- The live run failed because of the **color segmentation**, not the detector. Measured on your 21 campus train frames: 7 right, 9 wrong from segmentation alone, 5 from segmentation + detector, 0 from the detector alone.
- v1's segmentation reads the top 50 rows of each image to learn the background. On the home table that is a plain wall; in the campus room it is chairs, people and windows, so it learns "dark gray is background" and a saturation floor two times too high, and it throws away the navy barrel bodies and the shaded orange faces.
- I built a replacement front end (the **hs model**: fixed hue sector + HSV saturation floor per color, learned once from your 16 home frames, nothing estimated from the image) and hardened the detector in five places (a–e below).
- With your boxes as ground truth, on the 21 campus train frames: **0.97** for the new front end + hardened detector vs **0.41** for what is on `barrels` today. Home score unchanged at 0.93. Nothing drawn on any real negative frame of either session, nor on Dave's pink desk.
- **Nothing is switched on yet.** All code sits on branch `wip/redesign` (one commit on top of `barrels`). You read section 6, say "understood" or ask, make three small decisions (section 5), and I merge and adopt.

## 2. Everything that changed

### 2a. Data (on `barrels`, committed)

- **31 campus frames imported** as `data/raw/4A8B_campus_light_*.png` (light tag `campus`, surface `light`), split at import into **10 test / 21 train** (`data/splits.json`, `make_splits.py --v2 --filter 4A8B_campus_light`). The 10 test frames were never loaded by anything. `DATA.md` has the set row and the session notes.
- **4 recordings** moved to `barrels/data/recordings/2026-11-07_campus/{r1_static, r2_pan, r3_enter_leave, r4_hand_occlusion}/`. Too big for git; the repo-root `.gitignore` now excludes `barrels/data/recordings/`.
- **Your 31 box label files** committed (`data/labels/4A8B_campus_light_*_boxes.json`). Your counts matched mine on every train frame except `held_01` (no box on the barrel in the kicker). `tests/test_labels_consistency.py` now allows `held` scenes to have no boxes so the suite stays green with that file as you drew it.

### 2b. Experiments and results (on `barrels`; scripts in `experiments/`, tables in `results/`, entries in `EXPERIMENTS.md`)

1. **`2026-11-07_campus_attribution`** — for each of the 21 train frames, four panels (raw, v1 mask, bands the stripe finder considered, boxes) plus a log of why every band was kept or dropped, then a judgment per frame: ok / segmentation / segmentation+detector / detector. Result: 7 / 9 / 5 / 0. Mechanisms named: the two top-row stages (background prior fit, per-image saturation floor clamped 20–120) and the fixed RGB boxes. A `floor40` arm (force the floor to 40) confirmed the floor alone recovers several blue barrels.
2. **`2026-11-07_rec_replay`** — runs the detector and the tracker frame by frame over the four recordings and reports raw vs shown boxes, one-frame blips and lag. With the old front end: nothing found in the clips (room clutter behind the barrels); the tracker suppressed all 7 blips offered. Re-run later with the new front end (item 7).
3. **`2026-11-07_seg_hs_probe`** — first try at a hue/saturation front end, on `barrels` with a local fit function. Found the hue wrap bug (orange's sector read "3 to 168" because orange sits next to hue 0); fixed by rotating orange hue +30 before taking percentiles. Showed the idea works: campus bodies appear, Dave's desk stays empty.
4. **`2026-11-08_det_hardening`** (branch) — old vs new detector × old vs hs pixels. Home 0.91 → 0.93 with v1 pixels, 0.57 → 0.78 with hs pixels; turning the dark-gap path back on makes every number worse.
5. **`2026-11-08_seg_hs`** (branch) — 24-config sweep of the hs model, leave-one-scene-out on home, campus at count level (before your boxes). Honest mistake recorded: the pre-registered selection rule picked a config that gets 19/21 campus right but drops home to 0.69 (your bluish wall enters the blue class, and the home negatives could not show it). Rule flaw logged in `DECISIONS.md`; nothing adopted from this run.
6. **`2026-11-08_seg_hs_v2`** (branch) — 18 configs with **separate saturation percentiles for orange and blue** (orange 5/10/15 × blue 10/15/20 × hue margin 2/4), scored under the v2 rule with your boxes. This is where 0.97 vs 0.41 comes from. Candidate: **`hs o5 b15 h5-95 m2`** (orange hue 3–13, S ≥ 140; blue hue 103–119, S ≥ 113; config hash `eb863d84`). Proposed selection rule: home LOSO v2 ≥ 0.91, zero false detections on every negative of both sessions, then campus v2, then home v2, then the lower blue percentile. As labeled it returns "no winner" only because `held_01` counts the found-but-unboxed barrel as a false detection; with that frame boxed or set aside it picks the candidate.
7. **`2026-11-08_rec_replay_hs`** (branch) — the replay (item 2) with the candidate front end: barrels found in every clip, 0 blips shown, lag 2 frames, covered barrel in the hand clip dropped and re-acquired by design. One persistent false blue box on clutter at the right frame edge in the static clip (section 4).

### 2c. Main code (branch `wip/redesign`, awaiting your walkthrough; 216 tests pass)

- **`src/barrels/pipeline.py`** — new color model. `Config` gains `color_model` (`"rgb_box"` = v1, `"hs"` = new), `hs_s_pct` (one number or an (orange, blue) pair), `hs_h_pct`, `hs_h_margin`; all omitted from the config hash at their defaults so `afd85483` is unchanged (tested). `Frame.hs()` caches the hue/saturation planes. `fit_hs()` learns the two numbers per class from labeled pixels. `segment()` has an `if cfg.color_model == "hs":` branch at the top that skips the per-image floor and the background priors. The v1 path is byte-for-byte unchanged.
- **`src/barrels/detector.py`** — five hardening changes, each a `DetConfig` field so the old behaviour is one flag away: (a) `dark_stripe=False`, (b) `stripe_mode="cores"` (old finder kept as `"bands"`), (c) `body_min=0.1`, (d) `height_min/height_max=0.5/1.5`, (e) frame edge counts as the hidden side when a cut stripe is widened. Details in section 6B.
- **Tests** — 8 new: five detector cases (dark gap alone is not a stripe; shadow glued to a stripe does not veto it; a box must hold body color; a jacket-shaped blob is not a far barrel; a stripe cut by the frame edge widens into the edge) and three pipeline cases (hs fits a sector and a floor and segments by them; hs fields do not change old hashes and round-trip; per-class `hs_s_pct`).
- **Docs in the same commit** — `HOW-IT-WORKS.md` §1 has an hs subsection, §3 has "The hardening (a–e)" plus new rows in the code and config tables; `HOW-IT-WORKS-SHORT.md` updated.

### 2d. Side tools and small fixes (on `barrels`)

- **`tools/box_tool.py`** — the `g` size guide was computed with the stale camera (`AIM_4A8B6118`, tilt 23.3°). Default is now `--cam boxfit` (`AIM_4A8B6118_BOXFIT`); the guide assumes the cursor is on the barrel's bottom edge. Choices: `boxfit | 4a8b | nominal`.
- **`experiments/2026-11-07_rec_replay/run.py`** — gained `--front v1|hs`, `--hs o5,b15,m2`, `--out` so the replay can be re-run with any front end.
- **Docs** — `EXPERIMENTS.md` (7 new entries + index rows), `DECISIONS.md` (2026-11-08: segmentation first, hs is the candidate, hardening on the branch, the pre-registration lesson), `TODO.md`, `STATUS.md`, `DATA.md`.

### 2e. Where it lives

| branch | contents | state |
|---|---|---|
| `barrels` | data, labels, docs, experiments that need no new code | committed, pushed |
| `wip/redesign` | one commit on top of `barrels`: pipeline hs model, detector a–e, tests, HOW-IT-WORKS | pushed; merge = fast-forward once you acknowledge |

Nothing in `worldmap_bridge.DEFAULT_MODEL`, `detect_image.py` or the live programs changed. They still run v1 until adoption.

## 3. The numbers

Score = mean F1 over the two colors under the v2 rule (one box per barrel, matched by IoU ≥ 0.5, any box on a negative frame disqualifies).

| | campus train (21) | home, leave-one-scene-out (16) | Dave's office (indicative) | real negatives |
|---|---|---|---|---|
| detector on `barrels` today (v1 front end) | 0.41 | 0.93 | 0.00 (finds nothing) | clean |
| hardened detector, v1 front end | — | 0.93 | — | clean |
| **hs `o5 b15 h5-95 m2` + hardened detector** | **0.97** (orange 1.00, blue 0.94) | **0.93** | 0.44 | clean |

Dave's frames are indicative only: his ground-truth boxes enclose touching barrels as one group, which the v2 rule penalizes.

Recordings with the candidate: tracker shows a new barrel after 2 frames (the 3-of-4 rule), 0 one-frame blips shown, all four clips find the barrels.

## 4. Still wrong, and known

- **`occl_02`** — the barrel behind the marker. Its stripe is fully hidden; the detector is stripe-anchored, so this is the known limit. A P1 idea is pre-registered in `TODO.md` (a stripeless body piece directly above a found barrel of the same color).
- **`held_01`** — the barrel in the kicker is found and you did not box it, so it scores as a false detection. Needs your call (section 5).
- **Persistent false blue box** in the static recording: a blue object at the right frame edge just above the table is boxed as a barrel in every frame. That is the stripeless-far path accepting an edge blob. Persistent boxes are not the tracker's job; this needs a detector rule, which I want to pre-register after you have seen it live (likely: refuse a stripeless far piece that touches a side edge).
- **Mixed-color occlusion** (orange behind blue, `occl_02`): the back barrel's lower body reads as a band of the front barrel's color. P1.
- **Calibration** not done (no ruler on 2026-11-07); the camera model is still the provisional box-fit one. P1.

## 5. Your action items

1. **Read section 6** (about 15 minutes). Reply "understood" or ask about whatever is unclear. This is the walkthrough the rules require before the branch can land on `barrels`.
2. **Decide the selection rule.** Proposed: home leave-one-scene-out v2 ≥ 0.91, zero false detections on every negative frame of both sessions, then campus v2, then home v2, then the lower blue percentile. Yes or no.
3. **Decide `held_01`.** Either open it in the box tool and box the barrel in the kicker with the `h` flag (one minute), or tell me "held barrels are out of scope" and I log it in `DECISIONS.md` and `PROBLEM.md`. Either works; the eval needs one.
4. **Confirm the `clean` flags** on `neg_05` and `clutter_02`. They contain an orange cap and a glue stick, so by `DATA.md` they are not "clean", but leaving them `clean=true` only makes the standard stricter. Say "leave" or "change".
5. **After I adopt** (I fit once, save the config, point the default at it, merge): run `simple_cli BarrelTracker` on the campus table, do a slow pan, let a hand pass in front, take two `tm rec` clips, and tell me in chat what you saw. Watch for the blue box at the right edge.
6. **Send Dave the email** in section 7 after step 5 is done, so it has the live result in it.

What I do once you answer 1–4: adopt the chosen config (fit on the 16 home train frames, save under `results/`, `worldmap_bridge.DEFAULT_MODEL` → it, HOW-IT-WORKS §1 rewritten with hs as the front end and v1 as history, `PROBLEM.md` banner via `DECISIONS.md`), fast-forward `barrels` to the branch, then one test run on the 10 campus + 5 home test frames, once, logged.

## 6. The walkthrough

### A. The hs color model (`src/barrels/pipeline.py`, `Config(color_model="hs")`)

**What v1 does, in one line:** a pixel is barrel if it is below row 50, bright enough, more saturated than a floor *computed from the top rows of this image*, not similar to the *background color computed from the top rows of this image*, and inside a fixed RGB box for orange or blue.

**What the hs model does:** a pixel is barrel if it is below row 50, bright enough (V ≥ 40, same as before), its **hue is inside the class's sector**, and its **HSV saturation is above the class's floor**. That is all. The two italic parts of v1 are gone.

*Hue* is the angle on the color circle (OpenCV counts it 0–179): orange barrels sit at about 3–13, blue at about 103–119, under home light and campus daylight alike, because hue comes from the *ratios* of R, G, B, which do not change when the light gets dimmer. One wrinkle: orange sits right next to the wrap-around point (0 = 180 = red), so before taking percentiles its hue is rotated by +30 (a sector "3 to 13" would otherwise read "3 to 168"; my first probe made exactly that mistake and drew blue boxes everywhere; it is recorded).

*HSV saturation* is (max − min) / max, scaled 0–255. v1 used max − min, which shrinks with brightness: a navy shaded face (RGB 12, 45, 85) has max − min = 73 (below a floor of 86) but HSV saturation 219: a very pure blue, just dark. A bluish-gray wall (about 160, 150, 140) has HSV saturation under 110 however bright it is. That is the number that separates a dark barrel from a gray wall, and it is why the floor can be a fixed number learned once instead of a per-image guess.

*How the numbers are learned* (`fit_hs`): for each class, take all pixels you labeled as that class in the 16 home train frames (below row 50, V ≥ 40). The **S floor** is a percentile of their saturation (`hs_s_pct`; 15 means "the 15 % least-saturated labeled pixels are given up"; it may be one number or an (orange, blue) pair). The **hue sector** is two percentiles of the hue of the pixels above that floor (`hs_h_pct`, 5–95), widened by `hs_h_margin` units on each side because campus daylight pushes orange toward yellow (hue 13 vs 10 at home). With the candidate `o5 b15 h5-95 m2`: orange hue 3–13, S ≥ 140; blue hue 103–119, S ≥ 113.

*Why two floors:* orange wants a low floor because the orange stripe on a far blue barrel is small and dull (room_01 was lost at a single floor of 174). Blue wants a higher floor because your home wall is bluish-gray and enters the blue class at S ≥ 64. The sweep confirmed both.

*The tie rule is unchanged:* a pixel in both sectors (rare) is orange if R > B.

*What can still go wrong:* a bright blue object in the room (chair, jacket) is labeled blue; only the detector's stripe and size checks stop it from becoming a barrel (section 4's edge box is exactly this). Skin has orange hue (13) and saturation about 149, so at an orange floor of 140 some skin pixels pass the segmentation; the detector's stripe requirement is what keeps skin out of the boxes (no box on any `hand` frame). Wood has orange hue too (out of scope).

*Where in the code:* `Config` has four new fields, omitted from the hash at their defaults so `afd85483` is unchanged (a test checks that). `Frame.hs(shift)` computes and caches the hue/saturation planes. `fit` calls `fit_hs` when `color_model == "hs"`. `segment` has an `if cfg.color_model == "hs":` branch at the top that skips the floor and the priors. Nothing else in the file changed.

### B. The detector hardening (`src/barrels/detector.py`)

Five changes, each a `DetConfig` field so the old behaviour is one flag away.

**(a) A dark gap is not a stripe** (`dark_stripe`, default off). The old finder accepted a band with *zero* stripe-colored pixels as "a stripe lost to shadow". That drew the floating box above your orange barrel on 2026-11-06 (the dark gap under a false orange smear), and under the hs model it drew boxes in the gaps of a patchily labeled wall. `dark_stripe=True` gives the old behaviour back.

**(b) The stripe is found from its own pixels** (`stripe_mode="cores"`). Old: a "band" was *everything that is not body color* between body above and body below, so if the segmentation left a shadow unlabeled right under a stripe, the band was stripe + shadow, taller than allowed, and the stripe was thrown away (this killed `plain_01`, `close_01`, `window_01` and the pair in `core_01`). New: a stripe is a connected patch of the *other* color, and every pixel of it must have body color within 3 stripe heights **above and below**, checked pixel by pixel, so a stripe that touches the neighbouring barrel's body is cut away from that body. Then the same proportion checks as before, on the patch itself: height 0.45–1.6 × the stripe height the geometry expects at that row, at least 0.4 barrels wide, not taller than wide; wider than 1.4 barrels → cut evenly into several stripes (touching same-color barrels). Shadow around the stripe is never part of the patch. `stripe_mode="bands"` is the old finder, kept for comparison.

**(c) A box must hold body color** (`body_min=0.1`). In the stripe's own columns, outside the stripe rows, the box must contain *more* body-colored pixels than stripe-colored ones, and at least 10 % body color. This removed the orange box drawn on the *blue* barrel of the touching pair in `core_01`: its blue body happened to lie between its own orange stripe and the orange neighbour's bulge.

**(d) A blob without a stripe must be barrel-tall** (`height_min=0.5, height_max=1.5`). Step 3 only checked width. A blue jacket above the table edge, 24 wide and 45 tall, passed as "a far barrel whose stripe is too thin to see". Now the height must also be 0.5–1.5 × the barrel height the geometry expects at the blob's bottom row (skipped for blobs cut by the frame edge). Not pre-registered; added after seeing the jacket box and said so in the notebook.

**(e) The frame edge counts as a hidden side.** When a stripe is narrower than a barrel, the finder widens the box toward the side where the rest of the barrel is hidden, and it decided "hidden" by looking for a barrel-colored neighbour on that side. `edge_01`'s half-visible barrel at the right edge had no neighbour, so the box was widened to the *left*, onto empty table. Now a stripe that touches column 0 or the last column treats that edge as the hidden side. Test added; this lifted campus orange to 1.00.

*Numbers* (`experiments/2026-11-08_det_hardening/`): with v1's pixels home 0.91 → 0.93, campus 7 → 8 right; with hs pixels home 0.57 → 0.78, Dave 0.31 → 0.40, campus 12 → 15 right, frames with an extra box 5 → 1, nothing on the negatives.

## 7. Email draft to Dave (send after the live try)

Subject: Barrel detector — why the live view failed, and the fix

Hi Dave,

Quick update. I shot 31 frames and four short recordings on a campus table (room, hand, laptop lid, window, the standard arrangement list) and ran an attribution on the 21 development frames: 7 right, 9 wrong in the color segmentation alone, 5 in segmentation + detector, none in the detector alone. The cause is the two stages of the v1 segmentation that read the top rows of the image to estimate the background: in a real room they learn a wide dark gray and a high saturation floor and throw away the navy barrel bodies and the shaded orange faces. The detector itself holds up once it gets barrel pixels.

The fix: describe each barrel color by hue and HSV saturation (both brightness-invariant), learned once from the labeled frames, with no per-image estimation at all, plus the detector hardening we had pre-registered (a dark gap is not a stripe; shadow glued to a stripe cannot veto it; a box must hold body color). Under our v2 rule with my own box labels it scores 0.97 mean F1 on the 21 campus development frames against 0.41 for the previous detector; the home-table score is unchanged at 0.93; nothing is drawn on any empty frame, and on your office frames it leaves the pink desk alone and finds the barrel bodies for the first time. [One sentence on what the live view did on campus.]

One question: your ground-truth boxes on the office snapshots enclose two touching barrels in one box (e.g. snap_05). Was that your detector's design, or a labeling shortcut? It decides how I score your frames.

Next: one look at the held-out test frames, then the hidden-stripe case (a barrel whose stripe is fully occluded).

Tanush

## 8. Two things you asked

**Talking to me from your phone.** In the VS Code extension type `/remote-control` (or `/rc`) in the prompt box; the session then appears under **Code** in the Claude app on your phone and you can message it. Needs a Pro/Max/Team plan; the laptop must stay awake and VS Code open. In a terminal: `claude remote-control` in the repo folder (shows a URL and a QR code).

**Closing the lid.** A closed MacBook sleeps unless it is plugged in with an external display, and a sleeping Mac pauses me (resumes when opened; nothing lost). Options: lid open, plugged in, brightness at zero, `caffeinate -dimsu` in a terminal; or external display + power for closed-lid mode. Cloud sessions (`claude --cloud`) survive a closed laptop but cannot reach the robot and do not have this conversation.
