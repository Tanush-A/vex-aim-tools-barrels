# STATUS.md — where we are

**Updated:** 2026-11-08, early morning (the campus frames are in and attributed; the redesign candidate and the detector hardening are built and measured on branch `wip/redesign`, waiting for Tanush). One screen by design: history lives in `EXPERIMENTS.md` and `DECISIONS.md`, the task list in `TODO.md`, the code guide in `HOW-IT-WORKS-SHORT.md`, the plain-English account of the overnight block in `OVERNIGHT-2026-11-08.md`.

## State

- **Data.** The campus session of 2026-11-07 is complete: 31 frames (`4A8B_campus_light_*`, four barrels, a glass-walled study room) split at import into 10 test / 21 train, plus four ten-second recordings kept locally (`DATA.md`). **No box labels yet** — every campus number below is count-level (barrels per color, counted by eye).
- **Why the live run failed (attribution, 21 train frames):** 7 right, 9 fail in the segmentation alone, 5 in segmentation + detector, 0 in the detector alone. The two v1 stages that adapt to the image — the saturation floor and the wall model, both read from rows 0–50 — assume a plain wall there; in a real room they remove the blue bodies (0–7 % labeled in nine frames) and the shaded orange faces, and the RGB boxes miss bright orange. Where bodies survive, the stripe step works; its one real flaw is shadow glued to a stripe making its band "too tall" (pre-registered on 2026-11-06, confirmed).
- **On branch `wip/redesign` (not on `barrels`, awaiting the walkthrough):**
  - *Detector hardening*, four reversible `DetConfig` fields: stripes found from their own pixels with body color required right above and below (`stripe_mode="cores"`), no dark-gap stripes (`dark_stripe=False`), a box must hold body color (`body_min`), stripeless pieces must be barrel-tall (`height_min/max`). Home train v2 **0.91 → 0.93** with the old pixels; **0.57 → 0.78** with the new ones. 183 tests pass.
  - *The "hs" color model* (`pipeline.Config(color_model="hs")`): per class a hue sector and a floor on HSV saturation, both read off the labeled home frames once; no stage estimated from the image. Sweep of 24 configs: at the 15th-percentile S floor it matches v1 at home (**0.93** leave-one-scene-out, v1 0.93) and gets **17 of 21** campus frames right (v1 8), nothing on any negative; Dave's pink desk stays unlabeled and his barrels' bodies are found for the first time. The pre-registered selection rule picked a 5th-percentile config instead (campus 19 of 21 but home 0.69, the bluish home wall) — the rule ignored the home score; recorded as a rule flaw in `DECISIONS.md`, nothing adopted.
- **The detector on `barrels` is unchanged:** frozen v1 → stripe step (2026-11-05), `DEFAULT_MODEL` afd85483; home train v2 0.91; the live programs run it.
- **Recordings:** replayed offline (`experiments/2026-11-07_rec_replay/`); the old front end finds nothing in them, so they cannot judge the tracker yet (it suppressed all 7 one-frame blips it was offered). The script is ready for a re-run.
- **Camera:** still the provisional `AIM_4A8B6118_BOXFIT`; calibration waits for a ruler.

## Now (proposed order; `TODO.md` P0)

1. **Tanush boxes the 31 campus frames** (`box_tool.py --filter campus_light`, ≈ 15 min) — turns every campus count into a v2 score and lets the test frames be used once, later.
2. **Walkthrough and decision on `wip/redesign`** (`OVERNIGHT-2026-11-08.md`, then `HOW-IT-WORKS.md` §1 last subsection and §3 "The hardening"): merge the hardening; agree the selection rule for the final hs sweep (proposed: home LOSO v2 ≥ 0.91, zero boxes on every negative of both sessions, then the campus v2 score; per-class S percentiles in the grid).
3. **Final hs sweep under that rule**, then `DEFAULT_MODEL` → the chosen config; the live programs follow for free.
4. **Both live programs on campus with the new front end**; two more recordings there; replay.
5. **Email to Dave** (draft in `OVERNIGHT-2026-11-08.md`).

## Tanush's part

Box the campus frames; read the overnight doc and say which parts of the hs model and the hardening are unclear (walkthrough rule); decide the selection rule with Claude; try both live programs once the front end is swapped; send Dave the update; the calibration frames on a day with a ruler.

## Open questions for Dave

His 12 ground-truth boxes group touching barrels into one box (`snap_05`): by design of his detector, or a labeling shortcut? (It decides how his frames can be scored.) Which of his scenes to handle first; calibration once or per robot; knocked-over barrels ever; is "bottom within a tenth of the height" the right tolerance; does his `detect.py` from the zip still exist; is a display-only persistence rule in the live view fine for the demo.

## Parked (not v2.0)

World-map integration, ground positions in mm and the `measured` split, more tables and the unseen-table hold-out (v2.1), the `openvocab` / `depthmap` branches. Navigator requests: none open.

## Blockers

None. The campus box labels gate the proper evaluation; the walkthrough gates the merge.
