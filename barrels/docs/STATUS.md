# STATUS.md — current state

**Updated:** 2026-11-03 15:55 (box tool + first detector built for Tanush's 16:15–18:00 window). Plain-English code guide: `docs/HOW-IT-WORKS.md`.

## Where we are

- **v1 (per-pixel segmentation) done, frozen at `afd85483`:** test orange IoU 0.843, blue 0.813, zero false pixels on the negative frame. Details: `EXPERIMENTS.md` 2026-10-20/22, `Post-v1-SUMMARY.md`.
- **v1.5 (detection scaffolding) done:** `geometry.py`, instances, `Barrel` type, `eval_det.py`, CC reference detector (floor), world-map bridge stub. The measured set and the instance review were superseded on 2026-11-02 by box labels.
- **v2.0 spec (2026-11-02, `PROBLEM.md`):** one still image in, the same image with one box per barrel out, on the laptop; bottom edge first; hidden bottoms from the geometry; clip to the frame. **Cut to one table / one background on 2026-11-03** (timeline); generalisation is v2.1.
- **2026-11-03, committed (7d0787e):** M1 — `_boxes.json` format + validator (`io.py`), `tools/box_tool.py` (drag / edit edges / flags / `--from-inst`), the 21 v1 frames converted to provisional boxes (`reviewed: false`), `make_splits.py --v2`.
- **2026-11-03, built, awaiting Tanush's walkthrough before commit (main code):** `detector.py` step 1 (blobs → how many barrels by the expected width → bottom edge from the top row, clipped), `tools/detect_image.py image.png → <stem>_boxes.png`, the provisional camera `AIM_4A8B6118_BOXFIT` (the preset put bottoms ≈ 20 px too low). On the 16 train frames: mean F1 **0.78** vs the floor's 0.46, bottom edge within 1 px, nothing drawn on empty frames (`EXPERIMENTS.md` 2026-11-03, provisional ×3: camera fit on these frames, pixels from a model fit on these frames, unreviewed instances).

- **2026-11-03, Dave's 20 snapshots imported** (`tools/import_dave_zip.py`, his 12 ground-truth box sets recovered exactly, `DATA.md`). **Outside check result: the v1 segmentation outputs zero barrel pixels on all 20** — both adaptive stages assume the rows above the horizon are plain background, and his office shelf is cluttered and colorful (floor 96–120 instead of ≈ 50); with the adaptive parts off, his pink desk floods the orange class. The front end, not the detector logic, is the bottleneck on a new scene (`EXPERIMENTS.md` 2026-11-03). Meeting brief: `docs/MEETING-2026-11-03.md`.

## Today (16:15–18:00): something to show that Tanush fully understands

1. Tanush reads `HOW-IT-WORKS.md` §1–§3 (≈ 25 min) and runs `python barrels/tools/detect_image.py barrels/data/raw/4A8B_window_light_touch_02.png` (and `far_02`, `cluster_02`, `close_01`, `neg_01`).
2. Walkthrough in chat: questions until he can explain the three steps and the camera fix himself; then the commit.
3. If time: fix the 21 converted box labels (`box_tool.py --filter window_light`, ≈ 15 min) — stretch occluded boxes to the full barrel, flag `bottom_estimated`.
4. Not today: shooting, the test split (evaluated once, later, with one pre-chosen config).

## Next — two tracks in parallel (Tanush's data is the bottleneck)

| track | step | who | needs |
|---|---|---|---|
| T1 | **Shoot** one table / one background: the 19-shot list in `DATA.md`, twice if time (≈ 45 min), + 12 `calib` + `horizon`; import; `make_splits.py --v2 --filter 4A8B_<light>_<surface>`; commit | Tanush | — |
| T2 | **Label boxes** on the new frames + the calib frames (≈ 30 s/frame); fix the 21 converted frames | Tanush | M1 (done) |
| C2 | **Eval under the v2 rule** (box GT, bottom-edge condition, every GT counts, clean-negative disqualification, per-scene report); re-score the floor and step 1. **Walkthrough.** | Claude | T2 for the 21 frames |
| C3 | **Detector step 2 — the stripe anchor:** one barrel per stripe inside merged blobs; "barrel" ≠ "orange thing" (fixes `occl_*`, `cluster_01`, the hand). Scene-held-out CV on train. **Walkthrough.** | Claude | — (starts now) |
| C4 | **Geometry calibration** from the `calib` frames → replaces `AIM_4A8B6118_BOXFIT`; update `constraints.md` #2/#3/#7. **Walkthrough.** | Claude | T1 |
| C5 | Segmentation check on the new frames (overlays; the one re-fit only if needed) | Claude | T1 |
| C6 | Retune step 2 with the new train frames (same CV); **one test run** (5 locked + new test frames); `EXPERIMENTS.md`; recap; short email to Dave | Claude drafts, Tanush sends | T2, C2–C5 |

## Open questions for Dave (v2)

- **Segmentation redesign (pulled forward from v2.1):** on Dave's frames the v1 front end finds nothing. Redo the background statistics without the "top rows are plain wall" assumption, and the color model without fixed RGB boxes? Which of his scenes matter most (cluttered shelf, pink desk, dark warm table, lid filling the frame)?
- **Knocked-over barrels:** upright only in v2; does a barrel on its side ever need detecting?
- **Per-robot calibration:** one (f, tilt) for every robot, or the 12 `calib` frames per robot? (Dave 2026-10-30: f should not differ much.) Today's finding: the labeled barrels pin the horizon row (≈ 76), not f and tilt separately.
- **"Drawn correctly" tolerance:** bottom edge within a tenth of the barrel height; fine, or tighter?

## Parked until the world map comes back (not v2)

Integration route (display vs replace aivision), latency, worldmap's 22 mm / 11 mm / `1.1·w` pad vs the measured barrel, ground-position targets in mm, the `measured` split, the skin-vs-orange hue test, Dave's `detect.py` / Lab 6 material, the `openvocab` / `depthmap` branches. v2.1: more tables, the unseen-table hold-out.

## Navigator requests

N-001…N-004 and the 2026-10-14 review notes: all done. Nothing open.

## Blockers

Tanush's walkthrough acknowledgement → commit of `detector.py` / `geometry.py` / `detect_image.py`.
