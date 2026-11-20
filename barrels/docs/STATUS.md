# STATUS.md — where we are

**Updated:** 2026-11-20. The occlusion work is merged (Tanush: "understood"): side occlusion, hidden bottoms, cut from above or below, a post, same-colored pairs, a cut barrel placed by its own rounded corners. Home 28 of 29, campus 35 of 35, no false box; occlusion scorecard 2153 → 2737 of 3888 (simulated). Running: A8 (fill a cut stripe; a sliver with stripe and body gets a good box). Tanush has shot 36 ottoman frames (4 lamp settings) with vendor detections; boxing and slider labels pending. Plan: `TODO.md`.

## What runs

hs color model `eb863d84` (orange hue 3–13, S ≥ 140; blue hue 103–119, S ≥ 113; fit on the 16 home frames) → stripe detector, hardening a–g, with the reason log, `stripe_join` and `cap_behind` (2026-11-18); side-occlusion fix in the code but switched off → provisional camera `AIM_4A8B6118_BOXFIT`. Live: `BarrelViewer`, `BarrelTracker`, `tm seg` with a second window. Eval: `python barrels/tools/report.py`.

## Numbers (train frames, v2 rule)

| set | found | note |
|---|---|---|
| home (white, window) | 28 of 29 | the miss is the wedge barrel in `cluster_01` |
| campus (white) | 35 of 35 | |
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
