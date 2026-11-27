# PREREG — correct the image's color (white balance), then use the fixed colors (2026-11-27)

> **This experiment tests something the standing rule forbids.** Dave's decision of 2026-10-07 (`docs/DECISIONS.md`):
> "never white-balance or otherwise correct the image". Tanush, 2026-11-27: "we can try correction too, like white
> balancing, worth a shot". It is run as an EXPERIMENT ONLY, to give Tanush and Dave numbers for that conversation.
> **Nothing here may be adopted without Dave.** No corrected image is ever written to `data/`; the correction happens
> in memory, inside the candidate's `detect_frame`, and is thrown away after the frame.

Branch `wip/exp-whitebalance`. Folder `experiments/2026-11-27_whitebalance/`. Outputs `results/2026-11-27_whitebalance/`.
Written and committed before any judged run and before part B was run.

## Question

Per frame, estimate the color of the light, divide it out of the photo (a gain per channel), and run today's fixed
color model (`eb863d84`, through `pipeline.segment`) and today's detector on the corrected photo. Does that find more
barrels than today, by more than the noise, held out, without boxes on things that are not barrels? Where does it
help, and where can it not?

Expectation written now, from `docs/review-2026-11-26/color_physics.md`: correction helps blue under warm light (the
bathroom floor, the ottoman under the warm and mid lamp: the blue paint is gray-olive, R G B within 10 counts); it
cannot fix the ottoman's orange (hue 13 to 17 under every lamp, it follows the surface, not the light); and because the
two paints move in opposite directions in 15 of 17 conditions (Q4), a full correction that pulls blue back will push
orange out of its range under the same lamp (orange under the warm bathroom lamp is hue 8, inside the range today).
One von Kries shift explains 41 % of the color movement, so the best possible correction leaves most of it.

## The correction (fixed now, the same for every candidate)

- An *estimator* reads the light L = (L_R, L_G, L_B) from the frame's own pixels. Pixels with the brightest channel
  under 40 or any channel at 250 or more are never read (dark pixels carry noise, clipped pixels carry no color).
  Fewer than 200 pixels to read: no correction on that frame.
- Gains g_c = (m / L_c) ^ alpha, with m = (L_R + L_G + L_B) / 3, so a gray under the estimated light keeps its mean
  brightness. Each gain is held inside [0.25, 4]. alpha = 1 is the full correction, alpha = 0 is none.
- The corrected photo: each channel of the camera values times its gain, rounded, held inside 0..255, as uint8. Then
  `pipeline.Frame.from_image`, `pipeline.segment(frame, adopted model)`, `detector.detect(mask, DetConfig())`. The
  gains act on the camera values as they are (gamma-encoded); a diagonal gain there is a diagonal gain on linear
  values too, only with another exponent, so this is a von Kries transform.
- No other change: same horizon gate, same brightness floor 40 (on the corrected value), same ranges, same detector.

## The estimators

| name | what it reads |
|---|---|
| `gray_world` | the mean color of every readable pixel of the frame |
| `white_patch` | the mean color of the brightest 5 % (by the brightest channel) of the readable pixels |
| `without_loose` | the mean color of the brightest 5 % of the readable pixels after taking out anything barrel-like under the loose model of the light experiment (orange hue −10..25 with S ≥ 120, blue hue 90..125 with S ≥ 60, below the gate, V ≥ 40), grown 15 px. The best reading of the light there (`wip/exp-light`). |
| `gray_above` | the mean color of the readable pixels of rows 0–49 (above the horizon gate, where no barrel can be) |
| `shades_of_gray` | the Minkowski p-norm per channel, (mean x_c^p)^(1/p), over the readable pixels, p = 6 (Finlayson and Trezzi's best) |

## The candidates (every one is judged and reported)

Full correction, no chosen number (judged as a plain `detect_frame`):

- **F1** `gray_world`, alpha 1. **F2** `white_patch`. **F3** `without_loose`. **F4** `gray_above`. **F5** `shades_of_gray`.

Partial correction, alpha chosen inside each fold (leave one place out) from {0.25, 0.5, 0.75, 1.0} (the most
cautious first), with "no correction" as the fallback:

- **P1** .. **P5**: the same five estimators. **P3** (`without_loose`, partial) is the **primary** candidate.

One more, pre-registered because the physics says the two paints want different corrections:

- **U3** today's mask, plus: where today's mask paints nothing, the class the `without_loose`-corrected photo paints
  (alpha chosen in the fold from the same list). So today's paint is never taken away.

**How alpha is chosen inside a fold** (the rule of the light experiment, unchanged): every setting and the fixed
model are run on every ordinary train frame of the seven training places; a setting the standard pass rule
(`judge.decide`, stored margins) calls FAIL against the fixed model on those places is out; among the rest the highest
gain = (Δ found per placement) − (Δ boxes not on their barrel per arrangement) wins; a tie goes to the smaller alpha;
no allowed setting with a gain above zero = no correction.

## The measurements first (part B, before any judging)

On every train frame of every class (ordinary, extreme, excluded), for each estimator at alpha 1 and 0.5:

- **Paint into the ranges.** The pixels that should be each paint (the body and stripe bands of free-standing upright
  barrels from the hand boxes, `expected_regions` of 2026-11-25), per condition: the share the fixed model paints the
  right class, before and after; the median hue and S after.
- **Flood.** The non-barrel pixels (rows ≥ 50, outside every hand box grown 4 px, V ≥ 40): the share painted orange or
  blue, before and after, per condition; named: pale wood, the bathroom floor, home (white table) and, for the home
  wall, rows 0–49 of the home frames as if the horizon gate were not there.
- **The gains** per condition (median), to see what each estimator thinks the light is.

These are descriptions, not verdicts; they choose nothing.

## The judge and the success line

- `jg.judge(candidate)` for F1–F5; `jg.judge(fit=fit)` (leave one place out) for P1–P5 and U3. Train frames only;
  154 ordinary frames, 17 conditions, 8 places, 172 placements; extreme frames printed, never judged.
- **Success line:** the standard pass rule says PASS. A PASS under +6 placements is WEAK. Margins: found better above
  +4.0, boxes not on their barrel worse above +1.85, any box on a clean empty frame fails.
- Compared with what changes no pixel (from their entries, all held out): stripe by contrast +21.5, near-miss +13.7,
  self-calibration +13.8, blue follows the light +3.9 (NO CLEAR DIFFERENCE).
- Contact sheets of every gained and lost barrel and every new box not on its barrel, for every candidate, looked at.

## What I looked at before writing this (honest list)

- The color-physics review tables (Q1 paint colors per condition, Q4 the von Kries fit, Q5 flood), the light
  experiment's entry (readings, B1–B4, O1–O3), the self-calibration, near-miss and contrast entries, the 2026-10-07
  decision. No corrected image of any frame has been made or looked at. No detector run on a corrected frame.
- The choices fixed above (gain normalised to the mean, the [0.25, 4] cap, clipped and dark pixels not read, p = 6,
  the alpha list) were made from first principles and the literature, not from a run.

## A second round

Only with a dated addendum committed first.
