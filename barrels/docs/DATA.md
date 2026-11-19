# DATA.md — the frames, their labels, the splits, what to shoot

**Updated:** 2026-11-19 (first conditions of the week-of-11-18 shoot: the black ottoman lid under four lamp settings, 36 frames with vendor files, split by scene 28 train / 8 test; running table under "Conditions shot this week") · 2026-11-16 (step 3 shot, boxed and **split**: wood ladder by scene 90 train / 27 test, black 10 / 5). Before capturing or using data, read "Now"; new frames are assigned to a split at import, before any method sees them.

## Open shot requests (the data session reads this at the start of EVERY sitting and tells Tanush what is open)

Kept current by the detector work (Claude, main session). The data session: at the start of each sitting, and whenever Tanush says "check requests", read this section and say which requests are still open, in order; tick a request here (date, condition) when its frames are imported. Requests are extra to the 9 shots per condition.

| # | request | why | where | state |
|---|---|---|---|---|
| R1 | **Occlusion extras, 10 shots, once**, names `occlx_01`–`occlx_10`, one free barrel in view in each: (1) a barrel behind a book or box with a straight upright edge, about half hidden; (2) the same, about three quarters hidden; (3) a barrel seen through a gap between two books, both sides hidden; (4) a book lying flat hiding a barrel's lower half; (5) two barrels of the SAME color side by side, the back one half hidden; (6) two of the SAME color, one clearly nearer and half hiding the other; (7) a barrel of the other color straight in front, hiding a quarter to a half of the back one; (8) a pen or marker stand in front of the middle of a barrel; (9) a barrel right next to a plain orange or blue block that is not a barrel; (10) a hand held just above a barrel | every number for these cases is simulated so far (`EXPERIMENTS.md` 2026-11-19, occlusion scorecard); these are the real check | any white or other ordinary table, ordinary light | open |
| R2 | **The same 10 on a second ordinary table or light**, if time allows | so the check does not rest on one table | another ordinary condition | open, optional |

## Now (2026-11-09)

**What we have** (tags as in `TODO.md`): HOME 21 (16 train / 5 test, masks + boxes) · CAMPUS 31 (21 / 10, boxes) · DAVE 20 (12 boxed by Dave, grouped; indicative only) · WOOD 24 unlabeled (5 calib + 19 lamp-color) · REC 4 campus recordings · 1 live frame · **NEW (2026-11-16, step 3): 117 wood lamp-ladder frames (13 scenes × 9 lamp settings), 15 black-table window frames, 12 ruler `calib` frames; all 144 boxed by Tanush 2026-11-16; split 2026-11-16: wood ladder **90 train / 27 test, by scene** (`neg_01`, `occl_03`, `touch_01` under all 9 lights are test), black **10 / 5**, calib in no split; 2 recordings. After the boxing, Claude snapped 29 box edges that stopped 1–3 px short of the frame edge on frame-cut barrels out to the edge (which sets `truncated`) and added the missed `held` flag on the 9 wood `held_01` frames, with Tanush's go.** Test frames are never loaded except in a planned test look. Full table: "Dataset index" below.

**The four commands** (details in "Storage and naming" and "Labels"):

```zsh
python barrels/tools/import_snaps.py --src barrels/live/snapshots --light <tag> --surface <tag> --scenes a,b,c --dry-run   # then without --dry-run
python barrels/tools/make_splits.py --v2 --filter 4A8B_<light>_<surface>     # at once, before any method sees the frames
python barrels/tools/box_tool.py --filter <light>_<surface>                   # draw the boxes (≈ 30 s a frame; `g` = expected size at the cursor)
python barrels/tools/hs_slider.py --filter <light>_<surface>                  # set the six color thresholds by hand on core_01, occl_01, clutter_01 (train frames only; "Slider labels")
```

**Next shoot (week of 2026-11-18): conditions first — shoot from this.** A condition = one table under one light; 9 shots each, in this order, ten or more conditions over the week (list and reasons: `TODO.md`). Names `4A8B_{light}_{surface}_{scene}_{nn}`; pick one short lowercase tag per light and per table, without underscores, and reuse it (`window`, `overhead`, `both`, `sun`, `dim`; `white`, `darkwood`, `gray`, `black`; add a place when two tables would collide, e.g. `campuswhite`). Shots: `neg_01` empty table · `neg_02` clutter only, with one orange and one blue non-barrel · `core_01` four barrels spread near to far, nothing else · `touch_01` two or three touching, mixed colors · `occl_01` a barrel about half hidden behind a barrel of the other color, clutter behind · `occl_02` a barrel about half hidden at the side by a clutter object · `close_01` one barrel about 2 cm from the bumper · `edge_01` one barrel cut by the left or right frame edge, one fully in view · `clutter_01` barrels among clutter, an orange or blue non-barrel next to a barrel. Every shot is saved with the vendor detector's output for the same instant (TODO B; until that is merged, shoot anyway and say so). Splits at import, before any method sees the frames: `make_splits.py --v2 --filter 4A8B_<light>_<surface>` (one of the two `neg` and one of the two `occl` go to test); when the same arrangement is reshot under another light without touching the table, shoot both lights in one session and split them together with `--by-scene`. **Occlusion extras (2026-11-19):** once, on a white table, 8 shots `occlx_01`–`occlx_08` (straight upright edge at a half and at three quarters, both sides hidden, lower half hidden, same-colored pair side by side and one nearer, other color straight in front, a thin post), list in `TODO.md`; one free barrel in view in each. Labels: boxes on every frame (`box_tool.py`); slider labels (`<stem>_hs.json`, TODO D) on `core_01`, `occl_01`, `clutter_01` of each condition, train frames only.

**Conditions shot this week (running table; the data session keeps it current).** A condition = one table under one light, 9 shots. Target: ten or more.

| # | light | surface | shot | frames | vendor files | split (train / test) | boxed | slider labels | note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `lampwarm6` | `ottoman` | 2026-11-19 | 9 | 9 | 7 / 2 | no | no | lamp aimed down at the lid |
| 2 | `lampmid6` | `ottoman` | 2026-11-19 | 9 | 9 | 7 / 2 | no | no | the same arrangements |
| 3 | `lampcool6` | `ottoman` | 2026-11-19 | 9 | 9 | 7 / 2 | no | no | the same arrangements |
| 4 | `lampmid3` | `ottoman` | 2026-11-19 | 9 | 9 | 7 / 2 | no | no | very dark (below); the vendor still reports barrels on it |

**Open for Tanush — the data session reminds him of these at the start of every session until done (2026-11-19):**

1. **Box the 36 ottoman frames.** Not started; he boxes after a later shoot. Draw the nine `lampmid6` frames (`python barrels/tools/box_tool.py --filter lampmid6_ottoman`; `c` = not clean on `neg_02`, `clutter_01` and wherever an orange or blue non-barrel shows), tell the session, which copies the boxes to the other three lights (`python barrels/tools/copy_boxes.py --from-light lampmid6 --surface ottoman --dry-run`, then for real), then check each copy per light in `box_tool.py` (saving marks it reviewed).
2. **Slider labels for the ottoman conditions**, after the boxes: `core_01`, `clutter_01` and, as the third, `occl_02` (`occl_01` is test here): `python barrels/tools/hs_slider.py --filter <light>_ottoman --scenes core_01,clutter_01,occl_02`. On first open, check that a slider knob follows the mouse (the window has never been opened).
3. **The close-up check is still open** (`TODO.md`, Tanush 3): a barrel about 2 cm from the bumper with a far barrel behind it, both should get a box; a barrel seated in the kicker. Seen live on the ottoman only for the close orange barrel, and not conclusive there, because our colors fail on that surface. Repeat on the first surface where our boxes work, and `tm save` it.

*Next shoots (Tanush, 2026-11-19):* at least one more setting on 2026-11-20, which one is open (he tells the session at the start); maybe a few more on Saturday 2026-11-21, such as the glass table (`glass`, lamp) and the bathroom floor (`bathtile`, its overhead light; the kitchen floor is the same tile under the same light and is dropped). A tiled floor under warm overhead light (`tile`) was also mentioned. *Not planned yet, and wanted by `TODO.md`:* the white table (window, overhead, both, dim), which is where the comparison with the vendor counts most and where no frame has a vendor file; dark wood under overhead and window light. *Dropped:* the gray table (its top is curved; the geometry assumes a flat table).

*New tags, 2026-11-19:* surface `ottoman` = the lid of Tanush's ottoman at home: black woven fabric, matte, flat, with a raised rim along the far side. It is a different surface from the black table of 2026-11-16 (`black`). Light tags reuse the lamp ladder names (`lamp{warm,mid,cool}{1,3,6}`: color step 1 / 3 / 6, the digit is the brightness step).

*As shot, 2026-11-19, 18:30–18:40, home, evening; `4A8B_lamp{warm6,mid6,cool6,mid3}_ottoman_*`.* The lamp is the only light and is **aimed down at the lid**, not at the ceiling as in the wood session: with the lamp at the ceiling (mid color, brightness 6) the frames were nearly black (mean gray 24 and 32 of 255) and our detector drew nothing; those two check frames and one with the lamp turned down are kept locally in `live/snapshots/check_2026-11-19_ottoman*/` (not imported). Nine scenes in the shot-list order, the four lights cycled inside each scene in the order `lampwarm6`, `lampmid6`, `lampcool6`, `lampmid3` without touching the robot, the lamp or the lid; 38 saves, of which two (saves 28 and 29, between `close_01` and `edge_01`) were mistakes and were deleted before the import at Tanush's request. The red-to-blue ratio of every scene falls from warm to mid to cool, which confirms the light order; some saves follow the lamp change by only 2–5 s. Brightness: the black lid fills the frame, so the whole-frame mean gray is low at brightness 6 (22–52; `close_01` 75–85) although the barrels are well lit (the brightest 1 % of pixels reaches 110–240). **`lampmid3` is very dark**: mean gray 9–18 (`close_01` 43), brightest 1 % at 25–90 (`close_01` 147), i.e. the barrels sit around the color model's brightness floor of 40, the class of the parked brightness-1 wood frames. Tanush keeps it: the vendor's saved lists still name barrels on every `lampmid3` frame with barrels except `occl_02`. Whether it counts as ordinary or as a report-only row is open. Colors, measured on the lamp-down check frame at `lampmid6`: orange hue 14–19 (adopted range 3–13), blue hue 102–107 with saturation around 117–135 (adopted 103–119, S ≥ 113); our detector drew no box on it, the vendor found both barrels. Vendor files: all 36 present and `available`; the vendor reports nothing on any of the 8 empty frames. `occl_02`: the barrel is about half hidden at the side by an eraser (Tanush). The camera's auto exposure reacts strongly to a hand entering the frame. Split 2026-11-19, at import, by scene (`make_splits.py --v2 --by-scene --filter _ottoman_`): test = `neg_01` and `occl_01` under all four lights (8), train = the other seven arrangements (28). `occl_01` is a test arrangement here, so the slider labels of these conditions use `core_01`, `clutter_01` and, if a third is wanted, `occl_02`. Boxes: not drawn yet. The original saves are kept locally in `live/snapshots/shot_2026-11-19_ottoman/`.

*Record, shot 2026-11-16:* **The multi-setting set (TODO step 3) — re-planned with Tanush 2026-11-15.** Three sessions, in any order; each is imported and checked on a contact sheet before the next starts (`live/snapshots/` must be empty at the start of a session). `tm save` per shot, strictly in the listed order; a bad shot is retaken at once and reported, not deleted. Dropped from the 2026-11-11 plan: the glass table, the white table at home, direct sun, the separate sweep tier (the wood session is the sweep).

**Status 2026-11-16: sessions B and C are shot and imported; session A's scene shots are dropped (Tanush + Claude): the white table is already the best-covered surface (HOME 21, CAMPUS 31) and the graded `occl` and `close` steps now exist on wood and black. What remains is the ruler set only (`calib` ×12 + `horizon` ×1, rows 17–29 of the table below), shot at home on the wood table under `lampmid6` (blinds closed, lamp at the ceiling) → `4A8B_lampmid6_wood_calib_01–12`, `4A8B_lampmid6_wood_horizon_01`, distances in `data/calib.csv`.** The session A plan is kept below as the record.

**Ruler set as shot 2026-11-16, 13:50–14:04: 12 `calib` frames, the step-3 shoot is complete.** Distances (`data/calib.csv`, `stem,distance_mm`): 0 (seated in the kicker), 10, 10, 15, 20, 25, 30, 50, 100, 150, 200, 300 mm. 5 mm is not possible (the magnet seats the barrel); 10 mm was shot twice by accident, eleven minutes apart (`calib_02`, `calib_03`), both kept; no `horizon` frame (the horizon row stays pinned by the boxes). The tape measure stays in frame beside the barrel, base edge visible; its printed numbers (142 down to ≈ 133 away from the robot) are not the distances — those were set by hand from the robot's front edge. Lamp at mid color, brightness 6, but its tilt was adjusted since the morning session and the table reads redder than the morning `lampmid6` frames (lower-left table patch R/G/B ≈ 170/112/53 against ≈ 187/131/38), so do not use these frames as `lampmid6` color data. A person and a blue box are in the background. Barrel widths at 100 / 150 / 200 / 300 mm are within a few pixels of the 2026-10-19 wood calib frames (thumbnail estimate).

*Session A — campus, white table, overhead light (`4A8B_overhead_light_*`; a new spot, not the 2026-11-07 study room). 16 shots + the ruler set + 1 recording:*

| # | scene | shot |
|---|---|---|
| 1 | `neg` | empty table |
| 2 | `neg` | clutter including an orange and a blue object, no barrels |
| 3 | `clutter` | barrels among clutter, nothing else orange or blue |
| 4 | `clutter` | the same, the orange or blue object right next to a barrel of its color |
| 5 | `occl` | a barrel partly hidden behind a clutter object |
| 6–8 | `occl` | a barrel at ≈ 10 cm hiding ≈ 25 / 50 / 75 % of one at ≈ 20 cm |
| 9 | `touch` | three touching in a row at ≈ 15 cm, mixed colors |
| 10 | `touch` | two of the same color touching |
| 11 | `cluster` | all four bunched at 15–25 cm |
| 12 | `far` | all four spread out at 25–30 cm |
| 13–15 | `close` | one barrel, base 0 / 10 / 20 mm past the bumper |
| 16 | `held` | a barrel in the kicker |
| 17–28 | `calib` | one orange barrel on the crosshair, near edge of the base at 0, 5, 10, 15, 20, 25, 30, 50, 100, 150, 200, 300 mm; ruler out of frame (skip if no ruler; distances go in `data/calib.csv`) |
| 29 | `horizon` | a mark 43.47 mm above the table on a wall ≥ 1 m away (skip if none) |
| rec | — | `tm rec`: two barrels at ≈ 15 cm, a slow pan by hand, a hand passing once |

```zsh
python barrels/tools/import_snaps.py --src barrels/live/snapshots --light overhead --surface light --scenes \
neg,neg,clutter,clutter,occl,occl,occl,occl,touch,touch,cluster,far,close,close,close,held,calib,calib,calib,calib,calib,calib,calib,calib,calib,calib,calib,calib,horizon --dry-run   # then without --dry-run; drop what was skipped
```

*Session B — home, wood table, the lamp ladder (`4A8B_lamp{warm,mid,cool}{1,3,6}_wood_*`). 14 scenes × 9 lights = 126 shots + 1 recording.* The lamp is the only light (no ceiling light in the room): curtains closed or after dark, lamp pointed at the ceiling for the whole session; "lamp off" is a dark frame and is not shot. The lamp has 6 color steps and 6 brightness steps; `warm`/`mid`/`cool` = color step 1 / 3 / 6, the digit = brightness step 1 / 3 / 6. **The robot and the scene are not touched while the 9 lights are cycled.** Light order in every scene: `lampwarm1`, `lampwarm3`, `lampwarm6`, `lampmid1`, `lampmid3`, `lampmid6`, `lampcool1`, `lampcool3`, `lampcool6`. Scenes in order: `neg` (empty) · `neg` (clutter incl. orange + blue objects) · `clutter` (barrels added, the orange/blue object next to a barrel of its color) · `occl` (behind a clutter object) · `occl` 25 % · `occl` 50 % · `occl` 75 % · `touch` (three, mixed) · `touch` (two, same color) · `cluster` · `core` · `close` 0 mm · `close` 20 mm · `held`. Recording at `lampwarm6`. Import (Claude, after the session): the files are scene-major, the importer takes one light, so snapshot k (0-based, in order) is scene k // 9, light k % 9; the snapshots are sorted into one folder per light and `import_snaps.py` is run once per light with the 14-scene list. Count must be 126. **As shot 2026-11-16 (daytime, blinds closed): 13 scenes, 117 frames.** On this robot a barrel at 0 mm seats in the kicker, so `close` 0 mm and `held` are one shot: scene 12 is `held_01`, scene 13 is `close_01` (20 mm), the planned scene 14 was skipped. In `occl_02–04` the back barrel is not at 20 cm (placed for the hidden fraction, not the distance). Brightness step 1 is nearly black (mean gray ≈ 20 of 255). The view did not move within a scene (phase correlation of the lit frames, < 0.2 px) except: `neg_02`, `lampwarm3`/`lampwarm6` sit ≈ 8 px left of the other lights (a negative, no boxes); `occl_04`, `lampcool3`/`lampcool6` sit ≈ 4 px right of the earlier lights (`lampcool1` too dark to measure) — check those boxes when copying. A person is in the background of `core_01` cool3/cool6 and `held_01` mid3/mid6. `close_01` looks less orange than the other scenes (the blue lid fills the frame; probably the camera's own white balance). The robot powered off and was restarted more than once during the session (Tanush): that is where the small view shifts come from, and the camera re-settling after the restart before `close_01` is the likely cause of its color change. The `occl_02–04` hidden fractions were eyeballed, not measured. Recording: `rec_2026-11-16_121306` (49 files).

*Session C — home, black table, window daylight, lamp off (`4A8B_window_black_*`). The 16 shots of session A (no ruler set) + 1 recording.* **As shot 2026-11-16 ≈ 13:20: 15 frames.** The 0 mm shot is the barrel seated in the kicker and is named `held_01` (as on wood); `close_01` ≈ 10 mm and `close_02` ≈ 20 mm, distances estimated by eye, not measured. Tanush reported strong glare on the live view: the wall and a white object behind the table are blown out to white in every frame, and the glossy table shows a reflection under each barrel (reflections are not barrel); the barrels themselves are clearly visible. `held_01`, `close_01` and `close_02` also show two barrels cut by the left frame edge (box them, `truncated`). `occl_02–04` hidden fractions eyeballed. Recording: `data/recordings/2026-11-16_black/rec_2026-11-16_131933` (51 files); the wood recording is `data/recordings/2026-11-16_wood/rec_2026-11-16_121306`.

*Labeling.* Sessions A and C: every frame boxed (16 each, + the 13 geometry frames). Session B: the scene is identical under the 9 lights, so Tanush boxes each scene once (12 scenes with barrels) and his boxes are copied to the other 8 lights of that scene (`python barrels/tools/copy_boxes.py --from-light lampmid6 --surface wood --dry-run`, then without; the copies are `reviewed: false` until he has checked each in `box_tool.py`, existing labels are never overwritten), after the contact sheet confirms nothing moved; the two `neg` scenes need only the negative flag. ≈ 57 frames to draw in total. *Splits (open, for the session that assigns them):* session B must be split by scene, not by frame — the same scene under another light in both train and test would leak.

**The 2026-11-11 plan (superseded 2026-11-15, kept as the record).** Purpose: generalize (light, table, clutter, occlusion) and feed the histograms (TODO 8) and the slider labels (TODO 10). Two tiers: **full sessions** (every scenario, for the detector work and the test look at 9b) and **sweep sessions** (three frames each, for the hue/saturation spread). One import per (light, surface) session, same scene tags everywhere, so every set scores per scenario.

| full sessions (16 shots + 1 recording each) | surface `light` (white): `window`, `overhead`, `sun` if available · `wood`: `lampwarm7`, `lampcool7`, `lampwarm1` · `glass`: `lampwarm7`, `lampcool1` · `black`: `window`, `sun` if available. ≈ 15 min to shoot, 8 min to box, each |
|---|---|
| per full session, 16 shots | `close` ×3 (base at ≈ 0, 10, 20 mm past the bumper — the kicker/close-up cases), `occl` ×3 (a barrel hiding ≈ 25 / 50 / 75 % of one behind it), `occl` ×1 (behind clutter), `touch` ×2 (mixed; same color), `cluster` ×1, `clutter` ×2 (one with orange/blue non-barrels), `neg` ×2 (empty; clutter incl. orange + blue objects), `held` ×1, `far` ×1 |
| per full session, 1 recording | `tm rec`, a slow pan with a hand passing once |
| sweep sessions (3 shots each, no recording) | the lamp ladder on `wood` and on `glass`: temperatures lowest / middle / highest × brightness lowest / middle / highest = 9 settings per surface (the lamp has 6–7 steps of each; adjacent steps barely move the histogram). Shots: `core` (orange + blue touching ≈ 15 cm, one far, one close), `clutter`, `neg`. ≈ 90 s to box a setting |
| light tags | `window`, `overhead`, `sun`, and `lamp{warm,mid,cool}{1,4,7}` for the ladder (`1` = dimmest, `7` = brightest; use the real step number if the lamp has 6). No underscores inside a tag |
| once, any session with a ruler | `calib` ×12 (0, 5, 10, 15, 20, 25, 30, 50, 100, 150, 200, 300 mm to the base's near edge, one orange barrel on the crosshair, ruler out of frame) + `horizon` ×1 (a mark 43.47 mm above the table on a wall ≥ 1 m away); distances in `data/calib.csv` (`stem,distance_mm`). Why: labeled boxes pin only the horizon row; f and tilt separately need known distances, and the close-zone numbers the close-up fix relies on were computed, never measured |
| glass | the barrel's reflection and whatever is under the table both show; box rule unchanged: reflections are not barrel |
| then | import → `make_splits --v2` → box → commit `data/raw`, `data/labels`, `data/splits.json`. Full sessions first (they unblock 6, 7, 9b), sweeps after |

Everything below is the reference: naming, label formats and rules, splits, the dataset index, and the record of past sessions.

---

## Storage and naming

Small hand-taken sets, **committed to git**: images in `barrels/data/raw/`, labels in `barrels/data/labels/`, the vendor detector's answers in `barrels/data/vendor/` (since 2026-11-18, below), the split assignment in `barrels/data/splits.json`.

`{robot}_{light}_{surface}_{scene}_{nn}.png` — e.g. `4A8B_window_light_touch_02.png`. Use exact tags.

- **robot:** short id, e.g. `4A8B` (= AIM-4A8B6118); `DAVE` for Dave's snapshots.
- **light:** the source — `window`, `overhead`, `lamp`, `bounce` (indirect), `dim`, `side`, `mixed`, or the home-lamp tags `{up,at,away}{cool,mid,warm}`.
- **surface:** `light` (the white matte table), `beige`, `black`, `wood`, `floor`, `paper`, `ottoman` (a black woven-fabric lid, since 2026-11-19), … (extend as needed).
- **scene:** `core` (orange + blue touching ~15 cm, one far, one close) · `far` · `close` · `top` (lid only) · `topstripe` (lid + stripe, bottom below the frame) · `touch` · `occl` · `cluster` · `edge` · `glare` · `shadow` · `clutter` · `held` (in the kicker) · `neg` (no barrels) · `calib` (one barrel straight ahead at a measured distance) · `ruler` · `horizon` (a mark at camera height on a far wall) · backdrop scenes since 2026-11-06: `room` (the open room behind the barrels), `hand` (a hand and laptop behind), `plain` (a plain flat backdrop right behind the barrels, e.g. the back of a laptop), `window` (a bright window or lamp behind).
- **nn:** two-digit counter per (robot, light, surface, scene).

**Capture:** `tm save` in the live programs (`RUNBOOK.md`), or the camera viewer's key `s`; both write `snapshots/robot_snapN.png` (under `barrels/live/` for the live programs). **Import right away** with `tools/import_snaps.py --src barrels/live/snapshots --scenes …` (it renames in shooting order; the viewer's counter restarts each session and would overwrite, so use one or the other in a session). `tm rec` writes ten-second sequences to `snapshots/rec_<stamp>/` for replaying the multi-frame view offline; they are not frames to label unless imported one by one.

**Vendor detections** (2026-11-18, TODO B; **checked on the robot 2026-11-19**: the files are written and `available`, read at the frame, the boxes sit tight on the right barrels in the look-at picture, `score` runs 0–100 (98 and 99 seen), an empty frame gives `0 objects`; the moving-barrel timing and the stream-speed checks of `RUNBOOK.md` were not done): `tm save` also writes `snapshots/robot_snapN_vendor.json`, what the robot's built-in detector reported when that frame arrived, and `import_snaps.py` moves it to `barrels/data/vendor/<stem>_vendor.json` under the frame's new stem (`io.vendor_path`, `io.load_vendor`; frames shot earlier, or with the camera viewer's `s`, have none, which the importer lists and does not treat as an error). It is a measurement of the vendor, committed with the frame, and **never a label**: boxes are still drawn by hand without looking at it. Schema, version 1:

```json
{"version": 1, "available": true, "error": "", "time": 1763480000.1, "frame_count": 412, "read_at": "frame",
 "image_size": [640, 480], "source_size": [320, 240], "classnames": ["SportsBall", "BlueBarrel", "OrangeBarrel", "Robot"],
 "objects": [{"name": "OrangeBarrel", "class_id": 2, "bbox": [200, 120, 250, 180], "raw": {"type": 4, "id": 2, "type_str": "aiobj", "originx": 100, "originy": 60, "width": 25, "height": 30, "score": 90, "name": "OrangeBarrel"}}]}
```

`bbox` is `[x0, y0, x1, y1]` in our 640×480 pixels, half-open ints like `*_boxes.json` (the vendor's corner and size in 320×240 units, times 2, clipped to the frame; `null` when the item has no usable box); `raw` is the vendor's item untouched; `objects` lists everything the vendor reported (balls, robots, tags too). `available: false` with the reason in `error` (and no objects) means the vendor data could not be read: the frame is saved all the same, and such a frame is "not measured", not "the vendor saw nothing". `read_at` is `frame` (the list current when the frame arrived) or `save` (read at the keypress). `io.vendor_barrels(record)` gives the two barrel classes as `Barrel`s (color + box) and counts the rest. `robot_snapN_vendor.png` (the frame with those boxes drawn) is for looking only and is not imported. `python barrels/tools/report.py --vendor` scores these boxes next to our detector's, by the same rule against the same hand-drawn labels, on the train frames that have a vendor file.

## Labels

Four label kinds exist next to each frame. **Boxes are the truth the detector is scored against**; slider labels (since 2026-11-18) are the color thresholds Tanush set by hand on a frame; masks are the segmentation's truth; instances are superseded.

### Box labels — `<stem>_boxes.json` (v2, since 2026-11-02)

```json
{"version": 1, "stem": "4A8B_window_light_touch_01", "image_sha1": "…", "reviewed": true,
 "negative": false, "clean": true,
 "barrels": [
   {"id": 1, "color": "orange", "bbox": [212, 160, 290, 262],
    "flags": ["occluded", "bottom_estimated"], "note": ""}
 ]}
```

- `bbox` = `[x0, y0, x1, y1]`, half-open, in the 640×480 frame, **clipped to the frame**. `color` = the body color (an orange barrel has a blue stripe).
- `negative` = true when the frame has no barrels. `clean` = true when nothing orange or blue is in the frame besides barrels; a false box on a clean frame disqualifies a config (`EVAL.md`).
- `flags` ⊆ {`occluded` (something hides part of it), `truncated` (the frame edge cuts it; set automatically), `held` (in the kicker), `bottom_estimated` (you could not see where the base meets the table), `no_stripe` (the stripe is not visible)}.
- `source` = `manual` | `from_inst` | `from_inst+manual` | `dave_gt`. The 21 v1 frames were converted from their instances on 2026-11-03 and then fixed by hand by Tanush (11 files changed); all are `reviewed: true`.

**Rules.** Draw the **full barrel**: lid top to where the base meets the table, bulge to bulge; the stripe is inside. Draw **through occluders** as if they were transparent and flag `occluded`; if the bottom cannot be seen, estimate it from the barrel's size and flag `bottom_estimated`. A barrel cut by the frame gets a box that **stops at the edge**. A shadowed bottom you can still see is the bottom, no flag. Reflections are not barrel. Other orange/blue objects get no box; set `clean: false`. A held barrel is boxed normally, flag `held`. 1–2 px precision is enough; the eval tolerance is a tenth of the box height.

**Tool:** `python barrels/tools/box_tool.py [--filter <light>_<surface>] [--unlabeled]`. Drag on empty space to draw (takes the color of the last box); click inside a box to select; drag an edge or corner to move just that edge. `o`/`b` color; `x`/`h`/`e`/`s` toggle occluded / held / bottom_estimated / no_stripe; `c` toggles `clean`; `d` deletes; `u` undoes; `g` shows the barrel size the geometry expects at the cursor row (a check — draw what you see first); `v` raw view; `w` saves; `n`/`p` save and move; `q` saves and quits. ≈ 30 s per frame.

### Slider labels — `<stem>_hs.json` (hand-set color thresholds, since 2026-11-18; TODO D, E, F)

The six numbers of the hs color model, set by hand on one frame: per color a hue range and a saturation floor. They are label data: later a script checks whether something in the frame's histogram predicts them (TODO F), so each file also records what the numbers were set against.

```json
{"version": 1, "stem": "4A8B_window_black_core_01", "image_sha1": "…",
 "orange": {"h_lo": -3, "h_hi": 16, "s_lo": 120}, "blue": {"h_lo": 100, "h_hi": 122, "s_lo": 90},
 "hue_units": "opencv 0-179; h_lo may be negative across the red wrap (-3 = 177)",
 "v_min": 40, "horizon_row": 50, "base_model": "eb863d84", "detector_git": "2b6ca83", "boxes_drawn": 4,
 "criterion": "as much barrel painted as needed to detect it, as little else as possible",
 "reviewed": true, "note": ""}
```

- `h_lo`, `h_hi` = the hue range, OpenCV units (0–179), **both ends included**; `s_lo` = the floor on HSV saturation (a pixel needs S ≥ `s_lo`; 0–255). All ints.
- **Orange and the red wrap.** Hue is a circle and orange sits where it closes (0 = 180). Orange's hue is therefore written on a line from −30 to 149: **−3 means 177**, and "−3 to 16" is the range 177, 178, 179, 0, … 16. Blue's line is 0 to 179. Always `h_lo ≤ h_hi`.
- `v_min`, `horizon_row`, `base_model` = the fixed parts of the adopted model the numbers were set against (brightness V ≥ 40, rows from 50 down, config `eb863d84`); the tie rule is that model's. `detector_git` = the code version whose detector drew the boxes on screen (`+dirty` if `src/barrels` had uncommitted changes); `boxes_drawn` = how many boxes it drew with these numbers. `image_sha1` as in the box labels: `io.load_hs` refuses the label if the image changed.
- To get the segmentation a label stands for: `pipeline.segment(frame, hslabel.model_from_thresholds(hslabel.adopted_model(), io.load_hs(stem)))`.

**Criterion** (what "best" means when setting them): **as much barrel painted as needed to detect it, as little else as possible.** Watch both the paint and the boxes; when two settings draw the same boxes, take the one that paints less of the table and the room.

**Which frames:** three per condition, `core_01`, `occl_01`, `clutter_01` (the tool's default selection), **train frames only**. The tool always refuses test frames (there is no flag to include them), geometry-only frames (`calib`, `ruler`, `horizon`) and frames that are in no split yet, so run `make_splits.py` first.

**Tool:** `python barrels/tools/hs_slider.py [--filter <light>_<surface>] [--scenes core_01,occl_01,clutter_01 | all] [--unlabeled] [--scale 1]`; `--list` prints the frames that would open and stops. The window (1280 × 658 at scale 1): left the raw frame; right the frame with every unlabeled pixel dimmed, the labeled pixels painted orange / blue, and the boxes today's detector draws from exactly that segmentation (yellow = orange barrel, green = blue); below, six sliders (the small tick under each is the adopted value) and the status lines with the six numbers and the box count. A frame opens with its saved label, else with the adopted values (orange 3–13, S ≥ 140; blue 103–119, S ≥ 113). Drag a slider, or select one with `1`–`6` and step it with `-` / `=` (by 1) or `[` / `]` (by 5). `b` detector boxes on/off; `t` your own truth boxes on/off (thin white); `m` painted pixels flat or in their own color; `r` reset to the adopted values; `c` copy the thresholds saved for the previous frame; `u` back to what was loaded or last saved; `w` saves; `n` / `p` next / previous; `q` quits. **Nothing is saved without `w`**: with unsaved changes, `n`, `p` and `q` ask first, and pressing the same key again discards them. `--selftest out.png` writes the picture without opening a window. The picture is `pipeline.segment` with a model built from the six numbers (`src/barrels/hslabel.py`), not a second implementation.

### Pixel masks — `<stem>_mask.png` (v1)

Single-channel PNG: **0** other, **1** barrel orange (orange body or the orange stripe of a blue barrel), **2** barrel blue, **255** ignore (glare / uncertain; excluded from pixel eval). Painted with `tools/label_tool.py` (scribble `1`/`2`/`3`/`4`, `g` grows along image edges, `n` saves; `<stem>_strokes.png` keeps the strokes). Rules: stroke every barrel incl. its stripe; `3` on table, wall and every other object; `4` only on blown-out glare; reflections are `3`; shadowed barrel faces are barrel; the VEX logo is the lid's color. All 21 v1 frames are masked; masks are not needed for v2 frames (optional on two frames per table as a segmentation check).

### Instances — `<stem>_inst.png` + `.json` (v1.5; superseded 2026-11-02)

Per-barrel ids derived from the masks by an automatic split (`src/barrels/instances.py`, stripe-seeded watershed) plus click edits (`tools/instance_tool.py`). Kept in the repo because the box labels were converted from them; no longer edited or needed. `io.load_instances` refuses stale files.

## Splits

Fixed **train / test**; dev is empty by design; test is **never used for tuning** (`EVAL.md`). `data/splits.json` is written by `tools/make_splits.py` (seeded, append-only — a stem never moves once assigned).

| split | images |
|---|---|
| test (5, locked 2026-10-19) | `window_light_core_04`, `window_light_edge_02`, `window_light_far_01`, `window_light_neg_03`, `window_light_touch_01` |
| train (16) | all other `4A8B_window_light_*`: close 01–02, cluster 01–02, core 01–03, edge_01, far_02, neg 01–02, occl 01–02, top_01, topstripe_01, touch_02 — tuned by leave-one-scene-out CV |
| v2.0 frames | assigned at import by `make_splits.py --v2`: one frame per scene tag with ≥ 2 frames → test, the rest → train |
| a set shot under several lights with nothing moved (the wood lamp ladder) | `make_splits.py --v2 --by-scene`: the unit is the arrangement `{surface}_{scene}_{nn}`; all its lights share a split; one arrangement per scene tag with ≥ 2 arrangements → test. Wood ladder: test = `neg_01`, `occl_03`, `touch_01` × 9 lights |
| totals 2026-11-16 | train 137 (HOME 16, CAMPUS 21, wood ladder 90, black 10) · test 47 (HOME 5, CAMPUS 10, wood ladder 27, black 5) |
| totals 2026-11-19 | train 165 (the 137 above + ottoman 28) · test 55 (the 47 above + ottoman 8: `neg_01`, `occl_01` × 4 lights) |
| not in any split | `calib`, `ruler`, `horizon` (geometry only); Dave's 20 frames (outside check); the 19 wood-desk frames (unlabeled) |
| `measured` | defined 2026-10-28 for mm positions, never shot; parked with the world map (`DECISIONS.md` 2026-11-02) |

## Dataset index

| set | location | count | status |
|---|---|---|---|
| v1 base set (2026-10-19, CMU) | `data/raw/4A8B_window_light_*.png` | 21 frames + masks + instances + **boxes** | labeled and reviewed; splits locked; the training and test data |
| wood-desk geometry frames (2026-10-19) | `data/raw/4A8B_upcool_wood_{calib_01–05,ruler_01}.png` | 6 | camera measurement only (`EXPERIMENTS.md` 2026-10-19); distances below |
| home color baselines (2026-10-07) | `data/raw/4A8B_*_wood_*.png` | 19, wood desk, 3 lamp directions × 3 warmths | unlabeled; probe-based baselines only; later stress tests |
| Dave's barrels.zip (2026-09-28) | `data/raw/DAVE_office_*_snap_NN.png` + 12 `_boxes.json` | 20 | outside check, no split |
| **campus session 2026-11-07** | `data/raw/4A8B_campus_light_*.png` (light tag `campus`: a glass-walled campus study room, daylight + ceiling lights, white table) | 31 frames: part A 12 (`room` 3, `hand` 2, `plain` 3, `window` 2, `neg` 2), part B 19 (`core` 2, `far`, `close`, `topstripe`, `top`, `touch` 2, `occl` 2, `cluster` 2, `edge`, `clutter` 2, `neg` 3, `held`) | split at import (`make_splits.py --v2`): **10 test, 21 train**; **boxed by Tanush 2026-11-08** (incl. `held_01`); four barrels (two orange-bodied, two blue-bodied) |
| live frame 2026-11-09 | `live/snapshots/robot_snap0.png` (local; Dave's desk) | 1 | the close-up-under-a-far-barrel case; import if wanted |
| **NEW, session B — wood lamp ladder (2026-11-16, home)** | `data/raw/4A8B_lamp{warm,mid,cool}{1,3,6}_wood_*.png` | 117 = 13 scenes × 9 lights (`neg` 2, `clutter` 1, `occl` 4, `touch` 2, `cluster` 1, `core` 1, `held` 1, `close` 1 per light) + 1 recording | imported 2026-11-16; **boxed by Tanush 2026-11-16** (drawn under `lampmid6`, copied to the other 8 lights with `tools/copy_boxes.py`, each copy checked; all `reviewed`); **split by scene 2026-11-16** (`make_splits.py --v2 --by-scene --filter 4A8B_lamp`): test = `neg_01`, `occl_03`, `touch_01` under all 9 lights (27), train = the other 10 arrangements (90); as-shot notes under "Next shoot", session B |
| **NEW, session C — black table, window light (2026-11-16, home)** | `data/raw/4A8B_window_black_*.png` | 15 (`neg` 2, `clutter` 2, `occl` 4, `touch` 2, `cluster` 1, `far` 1, `held` 1, `close` 2) + 1 recording | imported 2026-11-16; **boxed by Tanush 2026-11-16** (all `reviewed`); **split 2026-11-16** (`make_splits.py --v2 --filter 4A8B_window_black`): test = `close_01`, `clutter_01`, `neg_02`, `occl_01`, `touch_01` (5), train 10; as-shot notes under "Next shoot", session C |
| **NEW, ruler set (2026-11-16, home; replaces session A, whose campus scene shots were dropped)** | `data/raw/4A8B_lampmid6_wood_calib_01–12.png`, distances in `data/calib.csv` | 12: 0, 10, 10, 15, 20, 25, 30, 50, 100, 150, 200, 300 mm (no 5 mm, no `horizon`) | imported 2026-11-16; geometry only, no split; **boxed by Tanush 2026-11-16** (`clean` left true although a blue box is in the background: no effect, the frames are in no split); as-shot notes under "Next shoot" |
| **week of 2026-11-18, conditions 1–4: black ottoman lid, lamp aimed down (2026-11-19, home)** | `data/raw/4A8B_lamp{warm6,mid6,cool6,mid3}_ottoman_*.png` + `data/vendor/<stem>_vendor.json` for every frame | 36 = 9 scenes × 4 lights (`neg` 2, `core`, `touch`, `occl` 2, `close`, `edge`, `clutter` per light) | imported 2026-11-19 with the vendor's answers; **split by scene 2026-11-19**: test = `neg_01`, `occl_01` under all four lights (8), train 28; **not boxed yet**; as-shot notes under "Conditions shot this week" |
| recordings 2026-11-07 | `data/recordings/2026-11-07_campus/{r1_static,r2_pan,r3_enter_leave,r4_hand_occlusion}/` (gitignored, local to Tanush's laptop) | 54 / 63 / 60 / 61 frames at ≈ 6 a second, `frames.json` each | for replaying the multi-frame view (`experiments/2026-11-07_rec_replay/`); the room and the clutter box behind the barrels |

**Wood-desk calib distances** (front edge → barrel near edge, measured 2026-10-19): `calib_01` 50 mm (138 px wide), `calib_02` 100 (78), `calib_03` 150 (55), `calib_04` 200 (42), `calib_05` 300 (28). The camera sits ≈ 3 mm behind the front edge (`aim_kin.py`); with the 25.5 mm bulge these widths give f ≈ 356, the ruler marks ≈ 405: `constraints.md` #2.

## Dave's snapshots (barrels.zip, 2026-09-28; imported 2026-11-03)

20 frames from Dave's robot in his office: `DAVE_office_speckle_snap_00–11` (speckled gray-pink desk, window + room light; 12 frames with his ground-truth boxes) and `DAVE_office_dark_snap_12–19` (dark table, warm dim light, 5–7 barrels, a hand; no truth). `tools/import_dave_zip.py ~/Downloads/barrels.zip`; his boxes (yellow = orange barrel, green = blue, drawn in `<snap>_ground_truth.png`) are recovered pixel-exactly as the difference from the raw snapshot → `_boxes.json` with `source: "dave_gt"`, `clean: false`. His notes: `DAVE-barrels-zip-notes.md`. **Outside check only: in no split, never tuned on.** The v1 segmentation finds nothing on them (`EXPERIMENTS.md` 2026-11-03).

## Record: the v2.0 one-table shot list (2026-11-03; shot on campus 2026-11-07; superseded by the multi-setting plan above)

Decided 2026-11-03 (timeline): one table and one background, not wood (wood in scope since 2026-11-09), whatever light is there, tagged honestly. Variety comes from arrangements, positions and clutter. Shoot the list **once at minimum, twice if time** (second pass: different clutter, positions, distances). Clutter is Tanush's own, mostly not orange/blue, with a few orange/blue distractors. Barrels upright. Shoot in this order in one session:

| # | scene | shot |
|---|---|---|
| 1–2 | `core` | orange + blue touching ~15 cm, one far ~30 cm, one close ~7 cm; vary the layout |
| 3 | `far` | all barrels 25–30 cm, spread out |
| 4 | `close` | one barrel ~5 cm, full body visible |
| 5 | `topstripe` | one barrel ~2–3 cm: lid + stripe visible, bottom below the frame |
| 6 | `top` | one barrel against the bumper: lid only |
| 7–8 | `touch` | three touching in a row ~15 cm, mixed colors; then two of the same color side by side |
| 9–10 | `occl` | a barrel ~10 cm partly hiding one ~20 cm behind it; then a barrel partly hidden behind a clutter object |
| 11–12 | `cluster` | all barrels bunched 15–25 cm, some touching |
| 13 | `edge` | a barrel half out of frame at the side |
| 14–15 | `clutter` | barrels among varied clutter; the second with an orange or blue object right next to a barrel of the same color |
| 16–18 | `neg` | empty table; clutter only (nothing orange/blue); clutter including an orange and a blue object |
| 19 | `held` | a barrel in the kicker, if the robot can hold one |

```zsh
python barrels/tools/import_snaps.py --light <light> --surface <light|beige|black> --scenes \
core,core,far,close,topstripe,top,touch,touch,occl,occl,cluster,cluster,edge,clutter,clutter,neg,neg,neg,held --dry-run   # then without --dry-run
python barrels/tools/make_splits.py --v2 --filter 4A8B_<light>_<surface>     # right away, before any method sees the frames
python barrels/tools/box_tool.py --filter <light>_<surface>                   # then label
```

If a shot is bad, retake it immediately and delete the bad `robot_snapN.png` before importing; the tool pairs files with the scene list in order, so the counts must match. Commit `data/raw/`, `data/labels/` and `data/splits.json`.

**Calibration session** (once per robot until Dave says otherwise; his "lookup table"): one **orange** barrel centred on the vertical crosshair, ruler zero at the robot's front edge, distance to the **near edge of the base at table level** (the bulge overhangs it by ≈ 3.75 mm — slide the ruler under): **0, 5, 10, 15, 20, 25, 30, 50, 100, 150, 200, 300 mm** → 12 `calib` frames in that order, ruler out of frame before `s`. Plus one `horizon` frame if a wall ≥ 1 m away is available: a mark **43.47 mm** above the table, centred. Import with `--scenes` listing `calib` twelve times, then `horizon` (the importer takes no repeat count); the distances go in `data/calib.csv` (`stem, d_ruler_mm`). Geometry-only, no split. **Box the calib frames too** (`box_tool.py --filter calib`): their top row, bottom row and width are what the calibration fits f and tilt from (`TODO.md`, P1).

## Record: session 2026-11-07 (campus), the plan as shot

**Shot as planned, 2026-11-07, 13:27–14:51** — all 31 frames and the four recordings, in order, imported the same day as `4A8B_campus_light_*` (light tag `campus`), split 10 test / 21 train; the recordings moved to `data/recordings/2026-11-07_campus/` (ignored). Four barrels were available (two of each body color), so the "three" and "all" shots have three or four. The `hand` shots are the laptop open and facing the robot with a hand resting on its keyboard edge (shot 4) and flat on the table by the orange barrel (shot 5). Box labels are the next step (`box_tool.py --filter campus_light`). The plan below is kept as the record of what each frame is.

**Why.** The first live run (2026-11-06) failed in ways the committed frames cannot show: a plain backdrop (the back of the laptop) right behind the barrels, the open room, a hand, harsh light. These frames are the dev set for the segmentation redesign and the detector hardening; part B is the standard 19-shot list agreed on 2026-11-03, never shot until now; the recordings test the multi-frame view. **No calibration this session** (no ruler): the calibration paragraph above stays for a day with one. ≈ 45 min on campus plus the import.

**Take:** the robot (charged) and its cable; laptop + charger (its lid is the plain backdrop); every barrel you have; a handful of clutter objects, mostly not orange or blue, plus one orange and one blue object that are not barrels (pen, cap, notebook, fruit); your phone for one photo of each part's layout.

**Before the first shot.** `source setup.zsh`, `cd vex-aim-tools/barrels/live`, `simple_cli BarrelViewer`; `barrels/live/snapshots/` must be empty. Keep the table, the light and the robot fixed for the whole session. One photo per line below, in this order, `tm save` each; retake a bad shot at once and delete its `robot_snapN.png` before importing; do not use the camera viewer's `s` key in the same session. Glance at `tm seg` if you like, but shoot the list as written: never choose a shot by what the detector does with it. With only two barrels, do the "three" and "all" shots with two.

**Part A — the scenes that broke the live run** (the open room behind unless said; one orange and one blue barrel are enough)

| # | scene | shot |
|---|---|---|
| 1 | `room` | orange and blue about 15 cm away, a hand's width apart, the open room behind |
| 2 | `room` | the same two, one at about 8 cm, the other at about 25 cm |
| 3 | `room` | the same two side by side at about 25 cm |
| 4 | `hand` | yesterday's scene: a hand and the laptop behind the barrels |
| 5 | `hand` | the same, the hand resting on the table right next to a barrel |
| 6 | `plain` | the laptop lid right behind the barrels as yesterday, barrels at about 8 cm |
| 7 | `plain` | the same, barrels at about 15 cm |
| 8 | `plain` | the same, barrels at about 25 cm |
| 9 | `window` | a bright window or lamp behind the barrels (skip if there is none) |
| 10 | `window` | the same at another distance (skip if none) |
| 11 | `neg` | no barrels, the room behind |
| 12 | `neg` | no barrels, the laptop lid behind |

**Part B — the standard dataset list** (the 19 shots of the v2.0 table above; the room behind, normal light)

| # | scene | shot |
|---|---|---|
| 13 | `core` | an orange and a blue barrel touching at about 15 cm; one more far at about 30 cm; one close at about 7 cm |
| 14 | `core` | the same idea rearranged: swap which colors are near and far |
| 15 | `far` | all barrels 25–30 cm away, spread out |
| 16 | `close` | one barrel about 5 cm away, whole body visible |
| 17 | `topstripe` | one barrel 2–3 cm away: lid and stripe visible, bottom below the frame |
| 18 | `top` | one barrel against the bumper: lid only |
| 19 | `touch` | three barrels touching in a row at about 15 cm, mixed colors |
| 20 | `touch` | two barrels of the same color touching, side by side |
| 21 | `occl` | a barrel at about 10 cm partly hiding one at about 20 cm behind it |
| 22 | `occl` | a barrel partly hidden behind a clutter object |
| 23 | `cluster` | all barrels bunched 15–25 cm away, some touching |
| 24 | `cluster` | the same, rearranged |
| 25 | `edge` | one barrel half out of the frame at the left or right edge |
| 26 | `clutter` | barrels among varied clutter, nothing else orange or blue |
| 27 | `clutter` | barrels among clutter, an orange or blue object right next to a barrel of the same color |
| 28 | `neg` | the empty table |
| 29 | `neg` | clutter only, nothing orange or blue |
| 30 | `neg` | clutter including an orange and a blue object, no barrels |
| 31 | `held` | a barrel in the kicker (skip if the robot cannot hold one) |

**Part C — recordings** (`tm rec`, ten seconds each; `simple_cli BarrelTracker` if you want to watch the persistence rule; note the order)

| | shot |
|---|---|
| r1 static | two barrels at about 15 cm, nothing moves |
| r2 pan | turn the robot slowly by hand, about 30° over the ten seconds, the barrels staying in view |
| r3 enter / leave | slide a barrel into the view from the side and out again |
| r4 occlusion | wave a hand across the barrels twice |

**Then, the same day** (fill in the light tag; drop from `--scenes` anything you skipped, keeping the order of the files):

```zsh
python barrels/tools/import_snaps.py --src barrels/live/snapshots --light <overhead|window|…> --surface light --scenes \
room,room,room,hand,hand,plain,plain,plain,window,window,neg,neg,core,core,far,close,topstripe,top,touch,touch,occl,occl,cluster,cluster,edge,clutter,clutter,neg,neg,neg,held --dry-run
# then without --dry-run
python barrels/tools/make_splits.py --v2 --filter 4A8B_<light>_light      # before any method sees the frames
python barrels/tools/box_tool.py --filter <light>_light                    # ≈ 31 frames, ≈ 30 s each
```

Keep the `rec_<stamp>/` folders out of git (they are ignored) and say which is which. Commit `data/raw/`, `data/labels/`, `data/splits.json`.
