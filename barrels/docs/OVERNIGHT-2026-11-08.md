# Overnight block, 2026-11-07 → 2026-11-08 — what happened while you were away

Written for Tanush. Plain English first, the code walkthrough after, the email draft at the end. Everything here is backed by a committed script and a `results/` folder; the lab-notebook entries are in `EXPERIMENTS.md` (2026-11-07 and 2026-11-08).

## The short version

1. **Your 31 frames and 4 recordings are in.** Imported as `4A8B_campus_light_*`, split at import into 10 test and 21 train frames. I never looked at the 10 test frames. The recordings are in `barrels/data/recordings/2026-11-07_campus/` (not in git, too big).
2. **Why the live run failed — now measured, not guessed.** On the 21 train frames: 7 right, 9 wrong because of the color segmentation alone, 5 wrong because of segmentation and detector together, 0 wrong because of the detector alone. **So the segmentation is the problem**, and the detector mostly does its job once it is given barrel pixels.
3. **What exactly goes wrong in the segmentation.** Two of v1's "adaptive" stages read the top 50 rows of the image to learn what the background looks like. On your home table those rows are a plain wall, so that worked. In the campus room those rows are chairs, people, windows: the "background color" they learn is a wide dark gray, and the saturation floor they set is 67 to 120 instead of about 50. Both then throw away the navy-blue barrel bodies and the shaded orange faces as "background". In nine frames the blue barrels had 0 to 7 % of their pixels labeled. No body pixels → no stripe can be sandwiched → no box.
4. **I built a replacement and measured it, but did NOT switch it on.** It is called the **hs model**. It describes each barrel color by two numbers that do not change with brightness: hue (where on the color circle) and HSV saturation (how far from gray, relative to brightness). Both are read once from your 16 labeled home frames; nothing is estimated from the image being processed. On the home frames it scores the same as v1 (0.93 vs 0.93). On the campus frames it gets 17 of 21 right against v1's 8, draws nothing on any negative frame, and on Dave's office frames it leaves his pink desk alone and finds the barrel bodies for the first time.
5. **I also hardened the detector**, exactly the three things we pre-registered after the first live run plus one more: a dark gap is no longer a stripe; the stripe is measured from its own pixels so glued shadow cannot veto it; a box must contain body color; a blob without a stripe must be barrel-tall, not just barrel-wide. With the old pixels: home 0.91 → 0.93. With the new pixels: 0.57 → 0.78. 183 tests pass.
6. **Both changes sit on a branch, `wip/redesign`, not on `barrels`.** The rule is that main code gets explained to you before it is committed to `barrels`. Read the walkthrough below, tell me what is unclear, then we merge (it is one commit on top of `barrels`, a clean fast-forward).
7. **One honest mistake to know about.** Before running the 24-config sweep I wrote down the rule for picking the winner: "no boxes on any negative frame, then the most campus frames right, then the home score as a tie-break". That rule picked a config that gets 19 of 21 campus frames right **but drops the home score from 0.93 to 0.69**, because it lets your bluish home wall into the blue class and the two home negatives did not show that (the wall only shows up on frames with barrels). The rule was wrong, not the data. I report it as the rule said and adopt nothing. The runner-up (`hs s15 h5-95 m4`: home 0.93, campus 17/21, Dave 0.53) is the honest candidate. We write the next rule together.
8. **The recordings cannot judge the tracker yet.** The current front end finds nothing in them (room and clutter behind the barrels). The tracker suppressed all 7 one-frame blips it was offered. The replay script is ready; we re-run it after the front end changes.

## What you do next (≈ 30 min)

1. `git pull`, then `python barrels/tools/box_tool.py --filter campus_light` (31 frames, ≈ 30 s each) and commit `barrels/data/labels/`. This turns every campus count into a proper v2 score.
2. Read "The walkthrough" below. Reply with what is unclear, or "understood".
3. Decide with me: (a) merge the detector hardening; (b) the selection rule for the final hs sweep — my proposal: home leave-one-scene-out v2 ≥ 0.91, zero boxes on every negative frame of both sessions, then the campus v2 score from your new labels; and the grid gets separate saturation percentiles for orange and blue (orange wants a lower floor, for the far blue barrels' orange stripes; blue wants a higher one, for your wall).
4. Send Dave the email (draft at the end).

## The walkthrough

### A. The hs color model (`src/barrels/pipeline.py`, `Config(color_model="hs")`)

**What v1 does, in one line:** a pixel is barrel if it is below row 50, bright enough, more saturated than a floor *computed from the top rows of this image*, not similar to the *background color computed from the top rows of this image*, and inside a fixed RGB box for orange or blue.

**What the hs model does:** a pixel is barrel if it is below row 50, bright enough (V ≥ 40, same as before), its **hue is inside the class's sector**, and its **HSV saturation is above the class's floor**. That is all. The two italic parts of v1 are gone.

*Hue* is the angle on the color circle (OpenCV counts it 0–179): orange barrels sit at about 5–12, blue at about 104–118, under your home light and under campus daylight alike, because hue comes from the *ratios* of R, G, B, which do not change when the light gets dimmer. One wrinkle: orange sits right next to the wrap-around point (0 = 180 = red), so before taking percentiles its hue is rotated by +30 (a sector "3 to 13" would otherwise read "3 to 168"; my first probe made exactly that mistake and drew blue boxes everywhere — it is recorded).

*HSV saturation* is (max − min) / max, scaled 0–255. v1 used max − min, which shrinks with brightness: a navy-blue shaded face (RGB 12, 45, 85) has max − min = 73 (below a floor of 86) but HSV saturation 219 — it is a very pure blue, just dark. A bluish-gray wall (about 160, 150, 140) has HSV saturation under 110 however bright it is. That is the number that separates a dark barrel from a gray wall, and it is why the floor can be a fixed number learned once instead of a per-image guess.

*How the numbers are learned* (`fit_hs`): for each class, take all pixels you labeled as that class in the 16 home train frames (below row 50, V ≥ 40). The **S floor** is a percentile of their saturation (`hs_s_pct`; 15 means "the 15 % least-saturated labeled pixels are given up"). The **hue sector** is two percentiles of the hue of the pixels above that floor (`hs_h_pct`, e.g. 5–95), widened by `hs_h_margin` units on each side because campus daylight pushes orange toward yellow (hue 13 vs 10 at home). With `s15 h5-95 m4`: orange hue 1–14, S ≥ 174; blue hue 101–121, S ≥ 113.

*The tie rule is unchanged:* a pixel in both sectors (rare) is orange if R > B.

*What the sweep showed:* the blue S floor is the whole story at home — at 64 (5th percentile) your wall enters the blue class and produces false blue boxes on the frames with barrels; at 113 (15th) it is gone and the campus barrels are still found. Orange needs 2–4 hue units of slack for daylight. The four campus misses of the runner-up: `edge_01` (half out of frame, stripe cut), `occl_02` (stripe hidden behind the marker), `room_01` (the small blue barrel at 25 cm: its orange stripe is below the orange floor of 174 — the reason for per-class percentiles), `room_03` (an extra blue box: the blue chair in the room).

*What can still go wrong:* a bright blue object in the room (chair, jacket) is labeled blue; only the detector's stripe and size checks stop it from becoming a barrel. Skin has orange hue (13) and saturation 149, so it is kept out by the orange floor (174), not by hue. Wood has orange hue too (out of scope).

*Where in the code:* `Config` has four new fields (`color_model`, `hs_s_pct`, `hs_h_pct`, `hs_h_margin`), omitted from the config hash at their defaults so `afd85483` is unchanged (a test checks that). `Frame.hs(shift)` computes and caches the hue/saturation planes. `fit` calls `fit_hs` when `color_model == "hs"`. `segment` has an `if cfg.color_model == "hs":` branch at the top that skips the floor and the priors. Nothing else in the file changed; v1 is byte-for-byte the same path.

### B. The detector hardening (`src/barrels/detector.py`)

Four changes, each a `DetConfig` field so the old behaviour is one flag away.

**(a) A dark gap is not a stripe** (`dark_stripe`, default off). The old finder accepted a band with *zero* stripe-colored pixels as "a stripe lost to shadow". That is what drew the floating box above your orange barrel on 2026-11-06 (the dark gap under a false orange smear), and under the hs model it drew boxes in the gaps of your patchily labeled wall. Off by default. `dark_stripe=True` gives the old behaviour back.

**(b) The stripe is found from its own pixels** (`stripe_mode="cores"`). Old: a "band" was *everything that is not body color* between body above and body below, so if the segmentation left a shadow unlabeled right under a stripe, the band was stripe + shadow, taller than allowed, and the stripe was thrown away (this killed `plain_01`, `close_01`, `window_01` and the pair in `core_01`). New: a stripe is a connected patch of the *other* color, and every pixel of it must have body color within 3 stripe heights **above and below** — checked pixel by pixel, so a stripe that touches the neighbouring barrel's body is cut away from that body. Then the same proportion checks as before, on the patch itself: height 0.45–1.6 × the stripe height the geometry expects at that row, at least 0.4 barrels wide, not taller than wide; wider than 1.4 barrels → cut evenly into several stripes (touching same-color barrels). Shadow around the stripe is simply never part of the patch. `stripe_mode="bands"` is the old finder, kept for comparison.

**(c) A box must hold body color** (`body_min=0.1`). In the stripe's own columns, outside the stripe rows, the box must contain *more* body-colored pixels than stripe-colored ones, and at least 10 % body color. This removed the orange box drawn on the *blue* barrel of the touching pair in `core_01` — its blue body happened to lie between its own orange stripe and the orange neighbour's bulge.

**(d) A blob without a stripe must be barrel-tall** (`height_min=0.5, height_max=1.5`). Step 3 only checked width. A blue jacket above the table edge, 24 wide and 45 tall, passed as "a far barrel whose stripe is too thin to see". Now the height must also be 0.5–1.5 × the barrel height the geometry expects at the blob's bottom row (skipped for blobs cut by the frame edge). This one was not pre-registered — I added it after seeing the jacket box, and said so in the notebook.

*Numbers* (`experiments/2026-11-08_det_hardening/`): with v1's pixels home 0.91 → 0.93, campus 7 → 8 right; with the hs pixels home 0.57 → 0.78, Dave 0.31 → 0.40, campus 12 → 15 right, frames with an extra box 5 → 1, nothing on the negatives. Turning the dark-gap path back on makes every number worse.

*Tests:* five new synthetic cases (a dark gap alone is not a stripe unless asked; shadow glued to a stripe does not veto it; a box must hold body color; a jacket-shaped blob is not a far barrel; the old finder still reproduces its old answers).

## Things you asked

**Talking to me from your phone.** Claude Code's Remote Control links this session to the Claude app. In the VS Code extension type `/remote-control` (or `/rc`) in the prompt box; the session then appears under **Code** in the Claude app on your phone (computer icon with a green dot) and you can send it messages. Needs a Pro/Max/Team plan with claude.ai login; the laptop must stay awake and VS Code open. In a terminal the equivalent is `claude remote-control` in the repo folder (it shows a URL and a QR code). Verified against code.claude.com/docs/en/remote-control.

**Closing the lid.** A MacBook sleeps when closed unless it is plugged in with an external display, and a sleeping Mac pauses me (the session resumes when you open it; nothing is lost). Options: leave the lid open, plugged in, brightness at zero, and run `caffeinate -dimsu` in a terminal so it never sleeps; or an external display + power for closed-lid mode. The alternative that truly survives a closed laptop is Claude Code on the web (cloud sessions): the repo is on GitHub so a cloud session can run experiments, but it cannot talk to the robot and would not have this conversation's context.

## Email draft to Dave (one task finished: the attribution)

Subject: Barrel detector — why the live view failed, and a candidate fix

Hi Dave,

Quick update. I shot 31 frames and four short recordings on a campus table on Friday (room, hand, laptop lid, window, the standard arrangement list) and ran the attribution on the 21 non-test frames: 7 right, 9 wrong in the color segmentation alone, 5 in segmentation + detector, none in the detector alone. The cause is the two stages of the v1 segmentation that read the top rows of the image to estimate the background: in a real room they learn a wide dark gray and a high saturation floor and throw away the navy-blue barrel bodies and the shaded orange faces. The detector itself holds up once it gets barrel pixels.

Candidate fix, measured but not yet adopted: describe each barrel color by hue and HSV saturation (both brightness-invariant), learned once from the labeled frames, with no per-image estimation at all. It matches v1 on the home frames (0.93 vs 0.93 under the v2 rule), gets 17 of 21 campus frames right against v1's 8 (count-level until I finish boxing them), draws nothing on any empty frame, and on your office frames it leaves the pink desk alone and finds the barrel bodies for the first time. The detector also got the hardening we had pre-registered (a dark gap is not a stripe; shadow glued to a stripe cannot veto it; a box must hold body color).

One question: your ground-truth boxes on the office snapshots enclose two touching barrels in one box (e.g. snap_05). Was that your detector's design, or a labeling shortcut? It decides how I score your frames.

Next: box labels on the campus frames, a final sweep under a rule fixed in advance, then the live view with the new front end.

Tanush


---

# Part 2 — after your labels (2026-11-08, second block)

## The short version

1. **Your boxes are committed** (31 files). Your counts matched mine on every train frame except `held_01`, where you drew nothing for the barrel in the kicker. Two small label questions below.
2. **With real labels the campus number is now a proper v2 score.** On the 21 campus train frames the detector running on `barrels` today scores **0.41**. The candidate front end plus the hardened detector scores **0.97** (orange 1.00, blue 0.94). The home score is unchanged (0.93, leave-one-scene-out). Nothing is drawn on any real negative frame of either session, nor on Dave's pink desk.
3. **The candidate is `hs o5 b15 h5-95 m2`**: orange saturation floor at the 5th percentile of the labeled pixels (S ≥ 140), blue at the 15th (S ≥ 113), hue sectors 3–13 and 103–119. The per-class floor was the follow-up I proposed in part 1, and it did what it was supposed to: a low orange floor keeps the orange stripes of the far blue barrels, a higher blue floor keeps your bluish home wall out.
4. **What it still misses:** the barrel behind the marker in `occl_02` (its stripe is fully hidden; the known limit) and the barrel in the kicker in `held_01`, which it finds and you did not box — so it counts as a false detection. That one frame is why my proposed selection rule returns "no winner" as labeled; with `held_01` boxed (press `h` on it) or set aside, the rule picks the candidate above.
5. **One more detector fix, (e):** `edge_01`'s half-visible barrel was boxed to the *left* of the barrel, onto the empty table, because the "partly hidden stripe" rule only knew about barrel-colored neighbours as the hidden side, not the frame edge. Now the frame edge counts as the hidden side. Test added; this is what lifted campus orange to 1.00.
6. **The recordings, replayed with the candidate front end:** barrels found in every clip; all 7 one-frame blips suppressed; a new barrel is shown after 2 frames (the 3-of-4 rule needs three sightings); in the hand clip the covered barrel is dropped and re-shown as designed. One real problem: a blue object at the right frame edge just above the table is boxed as a blue barrel in *every* frame of the static clip, so the tracker shows it steadily. Persistent false boxes are not the tracker's job; that one needs a detector rule (likely: refuse a stripeless far piece touching a side edge). I have not added it — it should be pre-registered after you see it live.

## Two label questions

- **`held_01`.** Box the barrel in the kicker with the `h` (held) flag, or we write "held barrels are out of scope" into `PROBLEM.md` through `DECISIONS.md`. Either is fine; the eval needs one of them.
- **`clean`.** You left `clean = true` on `neg_05` and `clutter_02`, which contain an orange cap and a glue stick. By the definition in `DATA.md` those frames are not clean (orange/blue clutter present). It only makes the standard stricter (a false box there would disqualify a config), so I left it as you set it. Say if you want it changed.

## What I need from you

1. The walkthrough (part 1 above; nothing in it changed except (e), which is one paragraph in `HOW-IT-WORKS.md` §3).
2. Yes or no on the selection rule as proposed, and the `held_01` call.
3. Then I adopt: fit once, save the config, point the default at it, and the live programs run it. Then you try `BarrelTracker` on campus and we look at the test frames exactly once.

## Email to Dave — one sentence to add

After "17 of 21 campus frames right against v1's 8 (count-level until I finish boxing them)": replace with "0.97 mean F1 on the 21 campus development frames against 0.41 for the current detector, under our v2 rule with my own box labels; the home-table score is unchanged at 0.93."
