# STATUS.md — where we are

**Updated:** 2026-11-08, evening (Tanush's campus boxes are in, `held_01` included; the redesign candidate scores 0.99 on the campus train frames against 0.41 for what runs today and the proposed selection rule picks it; everything waits on branch `wip/redesign` for his walkthrough acknowledgement). One screen by design: history lives in `EXPERIMENTS.md` and `DECISIONS.md`, the task list in `TODO.md`, the code guide in `HOW-IT-WORKS-SHORT.md`, the plain-English account of the overnight block in `OVERNIGHT-2026-11-08.md`.

## State

- **Data.** The campus session of 2026-11-07 is complete and **boxed by Tanush** (2026-11-08): 31 frames (`4A8B_campus_light_*`, four barrels, a glass-walled study room), 10 test / 21 train, four recordings kept locally (`DATA.md`). `held_01` (a barrel in the kicker) is boxed as a blue barrel, no `held` flag, so it is an ordinary positive.
- **Why the live run failed (attribution, 21 train frames):** 7 right, 9 fail in the segmentation alone, 5 in segmentation + detector, 0 in the detector alone. The two v1 stages that adapt to the image — the saturation floor and the wall model, both read from rows 0–50 — assume a plain wall there; in a real room they remove the blue bodies (0–7 % labeled in nine frames) and the shaded orange faces, and the RGB boxes miss bright orange. Where bodies survive, the stripe step works; its one real flaw is shadow glued to a stripe making its band "too tall" (pre-registered on 2026-11-06, confirmed).
- **On branch `wip/redesign` (not on `barrels`, awaiting the walkthrough):**
  - *Detector hardening*, four reversible `DetConfig` fields: stripes found from their own pixels with body color required right above and below (`stripe_mode="cores"`), no dark-gap stripes (`dark_stripe=False`), a box must hold body color (`body_min`), stripeless pieces must be barrel-tall (`height_min/max`). Home train v2 **0.91 → 0.93** with the old pixels; **0.57 → 0.78** with the new ones. 183 tests pass.
  - *The "hs" color model* (`pipeline.Config(color_model="hs")`): per class a hue sector and a floor on HSV saturation, both read off the labeled home frames once; no stage estimated from the image. **Scored on Tanush's boxes** (`EXPERIMENTS.md` 2026-11-08 later): the candidate `hs o5 b15 h5-95 m2` (orange S floor at the 5th percentile, blue at the 15th) gets **0.99** mean F1 on the 21 campus train frames against **0.41** for the detector on `barrels`, with the home score unchanged (0.93 leave-one-scene-out) and nothing drawn on any real negative of either session or on Dave's pink desk. Its one miss: a barrel whose stripe is fully hidden (`occl_02`). The proposed selection rule picks it (first run, before `held_01` was boxed: 0.97 and no winner). An earlier count-level sweep's rule picked a regressing config (home 0.69); recorded as a rule flaw in `DECISIONS.md`.
- **The detector on `barrels` is unchanged:** frozen v1 → stripe step (2026-11-05), `DEFAULT_MODEL` afd85483; home train v2 0.91; the live programs run it.
- **Recordings:** replayed with the candidate front end (`results/2026-11-08_rec_replay_hs/`): barrels found in every clip, all 7 one-frame blips suppressed, new tracks shown after 2 frames, the covered barrel in the hand clip dropped and re-acquired by design. One persistent false blue box on blue clutter at the right frame edge near the horizon — the next thing to pre-register against.
- **Camera:** still the provisional `AIM_4A8B6118_BOXFIT`; calibration waits for a ruler.

## Now (proposed order; `TODO.md` P0)

1. **Walkthrough and decision on `wip/redesign`** (`OVERNIGHT-2026-11-08.md` §6, then `HOW-IT-WORKS.md` §1 last subsection and §3 "The hardening"): merge the hardening (a–e); accept the selection rule (it picks `hs o5 b15 h5-95 m2`) or amend it; confirm the `clean` flags on `neg_05` / `clutter_02`.
2. **Adopt**: fit the chosen config once on the 16 home train frames, save it under `results/`, point `DEFAULT_MODEL` at it; the live programs follow for free; `HOW-IT-WORKS` §1 rewritten with hs as the front end.
3. **Both live programs on campus with the new front end**; two more recordings there; replay. Pre-register a rule for the blue-clutter-at-the-edge false box if it shows up live.
4. **One test run** on the 10 campus test frames and the 5 home test frames, once, logged.
5. **Email to Dave** (draft in `OVERNIGHT-2026-11-08.md`; add the live result).

## Tanush's part

Read the overnight doc and say which parts of the hs model and the hardening are unclear (walkthrough rule); decide the selection rule; confirm the `clean` flags; try both live programs once the front end is swapped; send Dave the update; the calibration frames on a day with a ruler.

## Open questions for Dave

His 12 ground-truth boxes group touching barrels into one box (`snap_05`): by design of his detector, or a labeling shortcut? (It decides how his frames can be scored.) Which of his scenes to handle first; calibration once or per robot; knocked-over barrels ever; is "bottom within a tenth of the height" the right tolerance; does his `detect.py` from the zip still exist; is a display-only persistence rule in the live view fine for the demo.

## Parked (not v2.0)

World-map integration, ground positions in mm and the `measured` split, more tables and the unseen-table hold-out (v2.1), the `openvocab` / `depthmap` branches. Navigator requests: none open.

## Blockers

None. The walkthrough gates the merge and the adoption.
