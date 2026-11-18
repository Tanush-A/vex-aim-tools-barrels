# STATUS.md — where we are

**Updated:** 2026-11-18. New plan for the week in `TODO.md` (agreed with Tanush after the 2026-11-16 meeting with Dave; next meeting Monday 2026-11-23). 2026-11-18 evening: A (barrel behind barrel `cap_behind`, stripe in pieces `stripe_join`; on by default after Tanush's "understood"), B (vendor capture), D (slider tool) and F (histogram ↔ thresholds script) are merged. Started: A2 / A3 (side occlusion, remaining misses), A4 (ruler calibration), H / I (vendor column, never-regress command).

## What runs

hs color model `eb863d84` (orange hue 3–13, S ≥ 140; blue hue 103–119, S ≥ 113; fit on the 16 home frames) → stripe detector, hardening a–g, with the reason log, `stripe_join` and `cap_behind` (2026-11-18); side-occlusion fix in the code but switched off → provisional camera `AIM_4A8B6118_BOXFIT`. Live: `BarrelViewer`, `BarrelTracker`, `tm seg` with a second window. Eval: `python barrels/tools/report.py`.

## Numbers (train frames, v2 rule)

| set | found | note |
|---|---|---|
| home (white, window) | 27 of 29, score 0.97 | the 2 misses are in `cluster_01` |
| campus (white) | 34 of 35, score 0.99 | the miss is the barrel behind the robot |
| black table | 2 of 26 | parked as extreme (glare) |
| wood, bright lamp | 7 of 126 | parked as extreme |
| Dave's office | 11 of 34 (0.47) | indicative, his boxes group barrels |

No false box on any clean empty frame. Test frames (47) untouched.

## What we know (2026-11-16, `EXPERIMENTS.md`)

- Barrel colors move between settings: hue by about half a range, blue loses saturation under a warm lamp; the black table shifts them as much as a lamp does.
- One fixed color range for every table fails (wide paints the wood table and the home wall, tight misses the barrels).
- Thresholds read from each frame's labels reach about two thirds on black and cool-lit wood, almost nothing under mid and warm lamps: thresholds alone are not enough there; many misses are stripes that come out in pieces.
- Given perfect home masks the detector finds 28 of 29; with medium simulated damage 64 of 145. Left on the white tables: 1 hidden at the side (campus `occl_02`; A2) and 2 in home `cluster_01` (A3). Expected sizes are right; bottoms inferred from the top row are 4–7 px low for far barrels (A4).

## Now

`TODO.md`: Claude on A2, A3, A4, H, I now; Tanush shoots and labels as tables come up; F as data arrives; G on Sunday.

## Tanush's part

Shoot and label (E) with the data session (`HANDOFF.md` has its prompt); live-check B and the close-up fix; read A's walkthrough when it is ready.

## Open questions

Can the camera's auto exposure / white balance be locked (not asked yet)? Vendor detector: how its output is saved next to a frame (B).
