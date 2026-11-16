# Pre-registration: the same hs color model, fit on all train tables instead of home only

Written 2026-11-16, before the run. Agreed with Tanush the same day ("yea this looks good").

## Why

Today's color model (hs `eb863d84`: orange hue 3–13, S ≥ 140; blue hue 103–119, S ≥ 113) was fit on the 16 home
frames. On the new train frames today's detector finds 7 of 126 barrels on the bright wood frames and 2 of 26 on
the black table (`results/2026-11-16_detector_on_new_sets/`). The histogram look (`EXPERIMENTS.md` 2026-11-16)
says the barrel colors sit a little outside those ranges there: orange hue 11–14, blue hue 99–106, blue S down
to about 100.

## Hypothesis

Fitting the **same recipe** (S floor = 5th percentile of the orange pixels' S, 15th of the blue; hue sector =
5th–95th percentile above the floor, widened by 2) on the train frames of all tables recovers the blue barrels
and the black table without losing home or campus. I expect trouble for orange on wood: the wood table sits at
hue 13–25 with high saturation, so a wider orange sector will paint table, and that may add false boxes or break
stripes. Hence the third arm.

## Arms

| arm | orange range fit on | blue range fit on |
|---|---|---|
| `base` | home (the adopted model) | home |
| `all` | home + campus + black + wood (brightness 3 and 6) | the same |
| `nowood` | home + campus + black | the same |
| `blue` | home | home + campus + black + wood (brightness 3 and 6) |

Nothing else changes: same recipe parameters, same detector (`DetConfig()` defaults), same camera.

## Labels used for fitting

Home: the hand-made masks, as for the adopted model. Other sets have boxes only: the barrel pixels are the inner
0.6 × 0.8 of every unoccluded box, minus other barrels' boxes, kept where the hue is within ±12 of the tallest
hue peak of that class in that frame (`barrels.hshist.region_masks`; the same shortcut as the histogram look,
which reads a few points optimistic on home). Wood at brightness 1 is never used for fitting and is not a target
(Tanush 2026-11-16: unrealistic); it is reported.

## Scoring

Train frames only; the 47 test frames are never opened. v2 rule (`eval_det`). Every new arm is scored
**leave-one-scene-tag-out over all sets**: for each scene tag (`core`, `occl`, `touch`, ...), the model is fit on
the arm's fit frames of the other tags and scores the frames of that tag. So no frame is scored by a model that
saw it, and no arrangement of the wood ladder is on both sides (an arrangement has one scene tag). `base` is
scored as published (home leave-one-scene-out, other sets with the stored model). Dave's frames: the arm's model
fit on all its fit frames (indicative).

## Acceptance (in this order)

1. Home score ≥ 0.91 and campus score ≥ 0.97 (today 0.93 and 0.99; 0.02 is the noise band used before).
2. No box on a clean negative frame of home, campus, black or bright wood.
3. Among the arms that pass 1 and 2: the most barrels found on black + bright wood (152 barrels). Arms within 3
   barrels of each other count as tied; a tie goes to the simpler arm, in the order `all`, `nowood`, `blue`.
4. By eye, on the contact sheets of the winning arm (black, and wood under three lights): the boxes it adds are
   on barrels.

If no arm passes 1 and 2, nothing is proposed and the write-up says which condition failed and why. A passing
arm is **proposed, not adopted**: changing the default model is Tanush's decision.

## What would make me distrust the result

A winner whose gain comes from one scene tag only; false boxes concentrated on the wood table (the parked orange
case leaking into the general one); a home or campus loss hidden inside the 0.02 band but all in one scenario.
