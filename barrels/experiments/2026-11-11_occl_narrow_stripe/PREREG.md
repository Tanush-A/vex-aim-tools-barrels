# Pre-registration — a barrel hidden at the side (TODO step 7), written 2026-11-11 before the run

## What the attribution showed (results/2026-11-11_occl_attribution/)

Five barrels are missed on the 37 train frames, all flagged `occluded`. They are two different failures:

1. **Hidden at the side by something that is not a barrel** (1 barrel, `campus_light_occl_02`, behind the robot).
   Its stripe is found (16 px wide, 9 px tall) and refused by the width test: the barrel is 53.6 px wide at that
   row, and a stripe must be at least `stripe_w_min` = 0.4 of that (21.4 px). About 30 % of the barrel shows.
   This is the "less extreme" case of step 7 and the one Dave saw live (half a barrel, no box): a stripe is
   narrower than its barrel (its ends curve away and go dark, ~15 %), so "half a barrel showing" leaves a stripe
   of about 0.4 widths, right at the limit.
2. **Behind a barrel of the other color** (4 barrels, `window_light_occl_01/02`, `window_light_cluster_01`). The
   back barrel's stripe has the same color as the front barrel's body, so the two join into one region that is
   too tall to be a stripe (`height`: 28–29 px against 15 expected; 19 against 11). This is step 9
   ("mixed-color stacking"). **Not touched here.**

## Hypothesis

Lowering `stripe_w_min` from 0.4 to **0.25** recovers failure 1 and costs nothing elsewhere.

Why 0.25 and not a value fit to the one frame: the stripe of a barrel is about a quarter as tall as the barrel is
wide, and the finder already refuses a stripe that is taller than wide. So below a quarter width the "not taller
than wide" test is the one that binds; 0.25 is the point where the width test stops adding anything. It is not
tuned on `occl_02` (which would need "just under 0.2986").

A second change is tested because a narrow stripe only tells where the barrel is, not which side of it is hidden:

- **(h) the hidden side from the body.** Today a partly hidden stripe is widened to a full barrel toward the
  side where a barrel-colored neighbour touches it, else centred on the stripe. With (h), the box first takes the
  body-colored columns joined to the stripe (same walk as (f)); if those already span `stripe_full` of a barrel
  the box is that span; else the span is widened to a full barrel by the old rule. If the span is wider than
  `body_width` x a barrel it is not trusted and the old rule applies. Switch: `occl_body_side`.

## Configs

`base` (today), `w25` (`stripe_w_min` 0.25), `w25h` (`w25` + (h)), `h` ((h) alone). For the report only, never
for selection: `stripe_w_min` 0.35, 0.30, 0.20.

## Data (the 15 test frames are never loaded)

HOME 16 + CAMPUS 21 train frames (v2 rule, adopted color model `eb863d84`); Dave's 12 frames (indicative);
unlabeled: the 22 wood frames, the four campus recordings (242 frames), the saved live frame. On unlabeled
frames the measure is boxes added / removed against `base`, each new box looked at on a sheet.

## Acceptance rule (fixed now)

A config is adopted on `wip/occlusion` only if, against `base`:
1. no barrel found by `base` on HOME or CAMPUS is lost;
2. no false box is added on any HOME or CAMPUS frame, negatives included;
3. on Dave's frames the v2 score does not drop;
4. every box it adds on the unlabeled frames is on a real barrel, by eye (the count and the sheets are reported);
5. it finds the `occl_02` barrel under the v2 rule.

Among configs that pass: `w25h` if it passes, else `w25`. If neither passes, nothing is adopted and the write-up
says which condition failed. One recovered barrel is thin evidence either way: the step-3 `occl` shots
(25 / 50 % hidden) are the real check, and the write-up says so.
