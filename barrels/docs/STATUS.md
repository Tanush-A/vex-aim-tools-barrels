# STATUS.md — where we are

**Updated:** 2026-11-18. New plan for the week in `TODO.md` (agreed with Tanush after the 2026-11-16 meeting with Dave; next meeting Monday 2026-11-23). 2026-11-18 evening: B (vendor capture), D (slider tool) and F (histogram ↔ thresholds script) are merged; A (detector given good segmentation: barrel behind barrel, stripe in pieces) is built on `wip/detector-given-seg`, switches off, waiting on Tanush's walkthrough and decision. What runs is unchanged.

## What runs

hs color model `eb863d84` (orange hue 3–13, S ≥ 140; blue hue 103–119, S ≥ 113; fit on the 16 home frames) → stripe detector, hardening a–g, with the reason log; side-occlusion fix in the code but switched off → provisional camera `AIM_4A8B6118_BOXFIT`. Live: `BarrelViewer`, `BarrelTracker`, `tm seg` with a second window. Eval: `python barrels/tools/report.py`.

## Numbers (train frames, v2 rule)

| set | found | note |
|---|---|---|
| home (white, window) | 25 of 29, score 0.93 | the 4 misses are occluded barrels |
| campus (white) | 34 of 35, score 0.99 | the miss is the barrel behind the robot |
| black table | 2 of 26 | parked as extreme (glare) |
| wood, bright lamp | 7 of 126 | parked as extreme |
| Dave's office | 11 of 34 (0.47) | indicative, his boxes group barrels |

No false box on any clean empty frame. Test frames (47) untouched.

## What we know (2026-11-16, `EXPERIMENTS.md`)

- Barrel colors move between settings: hue by about half a range, blue loses saturation under a warm lamp; the black table shifts them as much as a lamp does.
- One fixed color range for every table fails (wide paints the wood table and the home wall, tight misses the barrels).
- Thresholds read from each frame's labels reach about two thirds on black and cool-lit wood, almost nothing under mid and warm lamps: thresholds alone are not enough there; many misses are stripes that come out in pieces.
- The 5 white-table misses: 1 hidden at the side (width limit; fix exists, off), 4 behind a barrel of the other color (no fix yet; item A).

## Now

`TODO.md`: A → D → (Tanush: E as tables come up) → F as data arrives → G on Sunday. B before the first shoot.

## Tanush's part

Shoot and label (E) with the data session (`HANDOFF.md` has its prompt); live-check B and the close-up fix; read A's walkthrough when it is ready.

## Open questions

Can the camera's auto exposure / white balance be locked (not asked yet)? Vendor detector: how its output is saved next to a frame (B).
