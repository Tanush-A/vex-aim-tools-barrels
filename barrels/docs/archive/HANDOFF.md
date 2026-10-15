# HANDOFF: Celeste Barrel Detection → Claude Code

Everything Claude Code needs to pick up this project. Written 2026-10-14 by the navigator session (claude.ai Project "Celeste Barrel Detection"). **Read this whole file before doing anything.** After the repo docs are created from it, the repo docs become the source of truth and this file gets archived at `barrels/docs/archive/HANDOFF.md`.

---

## 1. Who / what
- **Tanush Aggarwal** (GitHub `Tanush-A`), CMU SCS sophomore (AI major), undergrad researcher with **Prof. David (Dave) Touretzky** (dst@cs.cmu.edu, GHC 9013), ~10 hrs/week, fall 2026. Little prior CV experience; learning fast. Style: casual, direct, wants honest critique, iterates fast. Asks questions mid-task, so **restate the current plan in full when moving to a new step** instead of "see above."
- **Project:** a robust **barrel detector for the VEX AIM robot** to replace the unreliable vendor detector ("aivision"). Unreliable barrel detection is a real problem robot users face right now.
- **Dave's meta-strategy:** use Claude/AI to propose, implement, and evaluate algorithms. That needs (1) a very solid problem spec listing every exploitable constraint, (2) guidance on which algorithms to try, and (3) lots of ground-truth data across lighting, surfaces, and cameras.

## 2. CURRENT SCOPE: v1 = color segmentation only
From the Dave meeting on 10/7 + Tanush's decisions on 10/14.
- **No bounding boxes yet.** Step 1 = color segmentation.
- **Input:** one 640×480 RGB frame from the robot camera.
- **Output:** two images (plus an optional combined debug preview):
  - **Orange image:** every pixel judged *barrel orange* (an orange barrel body OR the orange stripe of a blue barrel) → flat **(255,128,0)**; everything else → flat gray **(128,128,128)**.
  - **Blue image:** every pixel judged *barrel blue* (a blue barrel body OR the blue stripe of an orange barrel) → flat **(0,100,255)**; everything else → flat gray.
  - "Barrel orange/blue" = barrel portions, not just anything orange/blue.
- **Method: adaptive thresholding.** Dave was emphatic: **do not correct/adjust the image (no white balance); adjust the thresholds per image.** The only question is "is this pixel part of a barrel?"
  - **Table prior:** the bottom of the frame is mostly table (unless a barrel is very close) → known non-barrel samples → reject what looks like the table.
  - **Background prior:** the top rows are wall/sky/background, never a barrel → known non-barrel samples.
  - Region choice: compute from camera geometry (horizon ≈ row 70 at 23° tilt with f≈400; **to verify**). Use robust stats (median/MAD) so a barrel inside the band doesn't skew it. Fallback: fixed rows.
  - **Lighting estimation:** an open problem. There's no absolute "ground truth" table color in a new setting (e.g. a lab with one overhead light), so don't rely on a stored table color. Proposed **v1.5**: use the **barrels themselves as the reference**. Their colors are known, so find high-confidence barrel pixels → measure how barrel orange/blue look *in this image* → re-fit the thresholds (iterative). Still adaptive thresholding, no image correction.
- **Threshold shape:** **v1 = an axis-aligned box in RGB.** Plot labeled barrel pixels in 3D RGB. If the cluster is compact, a box works. If it's an elongated diagonal (e.g. along brightness), a box swallows other hues → after v1, try fancier functions or other color spaces (HSV, YUV, Lab).
- **Out of v1:** glare/specular highlights and shadowed barrel faces (eventual goal: detect them); close-range top-only barrels (v2, but think about it early); bounding boxes; geometry-based checks; per-robot calibration; second robot; learned pixel classifiers; white balance.
- **v1 data:** simple scenes on a **black table** at Tanush's home (CA, ordinary home light), no distractors. Then Pittsburgh with different tables. Goal: table-agnostic.
- **Assumption:** no deliberately adversarial objects in view.

## 3. Repo + workflow decisions
- Fork **`touretzkyds/vex-aim-tools`** → **`github.com/Tanush-A/vex-aim-tools`** (public), branch **`barrels`**.
- All barrel work in a **separate subfolder `barrels/`**, independent of `aim_fsm` for now.
- Claude Code runs **locally on Tanush's Mac** (Python venv at `~/Desktop/Celeste/env`, which has OpenCV; macOS, Python 3.13).
- Images are small hand-taken sets → **stored in git** under `barrels/data/`.
- **Before any algorithm code:** write the docs below and send `constraints.md` + `PROBLEM.md` + a general update/directions email to Dave. Then **one email to Dave per finished task.**
- **The repo is the single source of truth.** The claude.ai Project mirrors `CLAUDE.md` + `barrels/docs/` via the GitHub integration (manual Sync). **Commit + push docs at the end of every session.**

## 4. Docs to create (research workflow, not TDD)
**Foundation docs** (the research analog of a spec; the SSOT for the current milestone, agreed with Dave, changed only via a logged decision, re-versioned per milestone):
- `barrels/docs/PROBLEM.md`: the v1 spec. Task, inputs, outputs (exact colors), scope in/out, success criteria, milestones.
- `barrels/docs/constraints.md`: everything known (camera, geometry, barrels, scene assumptions) + **unknowns to measure** (with how to measure each).
- `barrels/docs/EVAL.md`: metrics + protocol (per-pixel P/R/IoU per class, reported per condition; fixed train/dev/test split; never tune on test).

**Running docs:**
- `barrels/docs/EXPERIMENTS.md`: lab notebook. One entry per experiment: date, hypothesis, method/params, data split, results table, takeaway, next.
- `barrels/docs/DECISIONS.md`: short dated records (decision, why, who, alternatives).
- `barrels/docs/STATUS.md`: current state, next steps, open questions for Dave, blockers.
- `barrels/docs/DATA.md`: dataset index, naming convention, label format, splits.
- `barrels/docs/RUNBOOK.md`: robot setup/ops (content in §8).
- `barrels/docs/NOTES-INBOX.md`: decisions/ideas pasted in from phone/browser chats, to be triaged into the right doc.

**`CLAUDE.md`** (put at `barrels/CLAUDE.md`, plus a short pointer in the repo root `CLAUDE.md` if one is allowed): project summary; **how and when to read/update each doc**; the workflow loop **hypothesis → experiment script → run eval → log in EXPERIMENTS.md → decide (DECISIONS.md) → update STATUS.md**; unit tests for infrastructure (IO, label parsing, metrics, geometry math), with algorithms judged by eval numbers; reproducibility (every experiment is a script + config, outputs to `barrels/results/<date>_<name>/`); no tuning on test; end-of-session checklist (update STATUS + EXPERIMENTS, commit, push); the "restate the plan" rule.

Suggested layout:
```
barrels/
  CLAUDE.md
  docs/            (above)
  data/raw/        images: {robot}_{light}_{surface}_{scene}_{nn}.png
  data/labels/     masks: same stem + _mask.png (0=other,1=orange,2=blue,255=ignore)
  src/barrels/     segmentation code (io, priors, thresholds, viz)
  tools/           label tool, contact sheets
  experiments/     one script per experiment
  results/         generated outputs (gitignore big stuff)
  tests/
```

## 5. constraints.md: known facts to include
**Camera / robot**
- VEX AIM camera: **640×480 color**. Height of the camera above the ground: **43.47 mm** (exact).
- Tilt: **18–25° below horizontal; assume 23°** (per Dave). vex-aim-tools `aim_fsm/aim_kin.py` has per-robot measured values: 25.4° (AIM-5A888218), 23.7° (AIM-32A57C18). Its measurement procedure: `camera_tilt = atan2(43.47, d + 3) * 180/pi`.
- Focal length: `aim_fsm/camera.py` hardcodes **(400, 400)**, a guess, not calibrated. **Unknown to measure.**
- The vendor detector (aivision) runs **on the robot at 320×240** (scaled ×2).
- Tanush's robot: **AIM-4A8B6118**. Another seen: AIM-627D8818. Cameras differ between robots (color + possibly geometry).

**Barrels**
- Two types: **orange** (orange body, blue center stripe) and **blue** (blue body, orange stripe). Identical size/shape, always upright on the ground plane. Bulged barrel shape, not a true cylinder. Lid has an embossed "VEX" logo.
- Size (per vex-aim-tools `worldmap.py` + Dave's draft spec): **25 mm tall × 22 mm diameter, 6 mm stripe. Verify with a ruler** (Tanush's rough read: ~1 in × 1⅛ in).

**Geometry (for later, document now)**
- Ground plane + known camera pose → each image row ↔ ground distance → expected barrel pixel size per row. The horizon row is computable. Nothing above the horizon can be a barrel.
- Uses: size check when top + bottom are visible; infer the bottom from the top row + width when the bottom is occluded/off-frame; occlusion reasoning.
- The close/top-only case occurs only when the barrel's top is in the bottom half of the image (Dave, Lab 6).

**Scene assumptions**
- Mostly table in the lower frame; background (wall) in the upper rows. No adversarial objects.

**How barrels feed the robot (context)**
- `aim_fsm/worldmap.py::make_new_aiv_objects()`: per aivision box → **bottom-edge midpoint** assumed to be the floor contact → `robot.kine.project_to_ground(cx, cy)` (tilt + focal length) → + half the diameter → world (x,y) via the odometry pose. Barrel height padded to `max(h, 1.1*w)` (occlusion hack). Detections more than 300 mm away dropped. The path planners (wavefront, RRT) treat barrels as obstacles (r = 26 mm circle in RRT).
- The eventual detector should emit boxes in the same spec shape (`OrangeBarrel`, `originx, originy, width, height`) so it can drop in. **Not v1.**

**Unknowns to measure (each with a method)**
- The true barrel dimensions + stripe height (ruler).
- Focal length / intrinsics of AIM-4A8B6118 (checkerboard, or barrels at known distances).
- The actual tilt of AIM-4A8B6118 (the aim_kin.py procedure).
- The barrel orange/blue RGB distribution under different lights + tables (from labeled data). **Is the cluster box-shaped or diagonal?**
- Table + background color distributions per surface/lighting (from data).
- How much the camera's auto-exposure/auto-white-balance shifts colors (see §6).
- The horizon row in practice.

## 6. Findings so far (directional, small data)
**From Dave's barrels.zip (9/28):** 20 snapshots; snap00–11 have GIMP-drawn GT boxes (baked into the pixels, not machine-readable) + bad results from an old Claude detector. Failures: merged adjacent barrels, background false positives, a huge bogus box on a close-up, missed close barrels. Distant barrels mostly OK. His draft CLAUDE.md had gaps: no horizon gating; `fh = w×25/22` ignores perspective + the visible lid ellipse; no intrinsics. (The zip lacked `detect.py` + the `bounding_boxes*.png` references.)

**Lab 6 (10/7):** map distance accuracy ~1 cm at 9–14 cm (blue real 87.5 mm vs map ~95; orange 137.5 vs ~137). A few mm decides reachable vs. GoalCollides. **aivision failure: close-range barrels consistently get no box** (occasional flicker), so the planner is blind right next to the robot. Untested: clustering/adjacency.

**Color baselines (10/7, 19 home frames on a warm wood desk; 3 lamp directions × 3 warmths; probe-based metrics, no labels):**
- **The camera does NOT fully auto-white-balance.** Warm light shifts the whole image (mean blue channel 134 → 73).
- **The orange barrel body is robust** (H≈2–7, S≈225 under all settings).
- **The blue stripe is fragile under warm light:** S 236 → 103, V ≈ 60. Fixed HSV catches only **17%** of it.
- **Wood looks "orange" under warm light** (H 15, S 170). Fixed HSV flags **70%** of wood. Lab a* separates barrel orange (≈50) from wood (≈15–20); skin ≈29, orange cardboard ≈33.
- Gray-world WB fixed most of it (wood 70% → 8%, stripe 17% → 100%) but over-corrected (wood-dominated scene → grays go blue). **Dave rejected image correction anyway**; the lesson carries over: *per-image adaptation is necessary, and a global "average is gray" assumption fails on a dominant table color.*
- New failure modes: **barrel reflections on glossy tables**; shadowed barrel faces; glare on lids.
- Code: `prior_work/methods.py`, `grid.py`, `fig.py`; figure `prior_work/comparison.png`. Data: `~/Desktop/Celeste/vex-aim-tools/color_data/` (19 PNGs; light tags `{up,at,away}{cool,mid,warm}`, plus `top&stripe` in two filenames → rename to `topstripe`).

## 7. Data + labels
- **Naming:** `{robot}_{light}_{surface}_{scene}_{nn}.png`, e.g. `4A8B_overhead_black_core_01.png`. Use exact tags. Scenes: `core` (orange + blue touching ~15 cm, one far ~30 cm, one close ~7 cm), `far`, `close`, `top`, `topstripe`, `touch`, `occl`, `cluster`, `edge`, `glare`, `shadow`, `neg` (no barrels). Surfaces: `black`, `wood`, `light`, `floor`, `paper`, … Lights: describe the source (e.g. `overhead`, `lamp`, `window`, `dim`, `side`, `mixed`, or the home lamp tags).
- Snapshot capture: camera viewer `s` → `snapshots/robot_snapN.png`. **The counter resets each session**, so rename immediately.
- **Labels: semi-automatic full masks.** Tool (to build; extend `prior_work/label_strokes.py`): user scribbles `1` orange areas (incl. orange stripes), `2` blue areas (incl. blue stripes), `3` table + background, `4` glare/uncertain (ignore) → a key triggers auto-grow (e.g. GrabCut / seeded region growing) → user fixes with more strokes → saves `_mask.png` (0 other, 1 orange, 2 blue, 255 ignore). ~1 min/image.
- Split: a held-out test set is fixed early and never used for tuning.

## 8. Robot runbook (copy to RUNBOOK.md)
```zsh
cd ~/Desktop/Celeste
source setup.zsh                 # venv + sets $ROBOT default 192.168.4.1
export ROBOT=<ip>                # AFTER sourcing
ping -c 3 $ROBOT
cd vex-aim-tools
simple_cli                       # or: simple_cli Celeste / simple_cli Lab6a
```
- **Home wifi:** the robot joins home wifi; the IP is NOT reserved, so check the robot's Settings → Radio → Station each time (was 10.0.0.90). Optional: reserve it in the Xfinity router (10.0.0.1 → Connected Devices → Add Device with Reserved IP; Station MAC starts F4:12:FA).
- **Campus:** `export ROBOT=AIM-4A8B6118.wifi.local.cmu.edu` (worked 9/30, before the home-wifi setup; recheck).
- **AP mode:** robot Settings → Radio → Access Point; join the `AIM-xxxxxxxx` wifi (pw `AIM12345`); `ROBOT=192.168.4.1`; no internet.
- Commands go at the simple_cli `C>` prompt in Terminal (`tm`, `show objects`, `show pose`). Viewers: camera, world, particle, path (`h` for keys).
- **Quit with Ctrl+\\ before powering off the robot** (otherwise: an endless `ws_status reconnecting` loop + a cv2 crash).
- Noise: `ev_poll_posix.cc ... FD from fork parent` gRPC spam is harmless (try `GRPC_VERBOSITY=ERROR`). Occasional `ws_status reconnecting` = wifi flakiness.
- `genfsm X.fsm` → `simple_cli X`. aim_fsm: nodes = actions, transitions = event reactions (`=C=>`, `=S=>`, `=F=>`, `=T(n)=>`, `=TM=>`, `=D=>`).

## 9. Immediate tasks (in order)
1. **Repo setup:** verify the fork + `barrels` branch + remotes (`origin` = Tanush-A fork, `upstream` = touretzkyds). Create the `barrels/` skeleton.
2. **Write the docs** in §4 from this handoff: CLAUDE.md, PROBLEM.md, constraints.md, EVAL.md, DATA.md, DECISIONS.md (backfill decisions from §2–3 with dates 10/7 and 10/14), STATUS.md, EXPERIMENTS.md (backfill the 10/7 baseline entry from §6), RUNBOOK.md, NOTES-INBOX.md. Archive this file to `barrels/docs/archive/HANDOFF.md`. Copy `prior_work/` into `barrels/experiments/2026-10-07_baselines/`.
3. **Tanush reviews the docs** → fix → commit + push.
4. **Draft the email to Dave** (constraints + PROBLEM + update + directions). Tanush sends it.
5. **Build the semi-automatic labeling tool** + tests for mask IO.
6. Tanush shoots ~20–30 black-table frames + labels them.
7. **Eval harness** (per-pixel P/R/IoU per class, per condition) + **v1 experiment**: RGB-box thresholds with table/background rejection. Log, email Dave.
8. Then: plot the RGB clusters (box vs. diagonal) → v1.5 barrel-referenced adaptive thresholds → other color spaces.

## 10. Open questions for Dave (carry in STATUS.md)
- Is the eventual output a drop-in aivision replacement (host-side, same spec into worldmap)? Latency budget?
- How will "good" segmentation be judged (metrics, targets)?
- Close barrels: full predicted (unclipped) boxes later? Is fixing the world-map side (focal length, the 1.1w pad) in scope?
- `detect.py` + `bounding_boxes*.png` from his zip? Lab 6 student submissions / the ChatGPT watershed conversation?
- What's on the vex-aim-tools `openvocab` / `depthmap` branches; anything reusable?
