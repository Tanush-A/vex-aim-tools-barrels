# Barrel detector: where we are (2026-10-22, plain English)

## What this is

A color segmenter for the VEX AIM robot's camera: given one 640×480 frame, decide for every pixel whether it is part of an orange barrel, a blue barrel, or neither. It is step one toward replacing the vendor detector, which misses close barrels. Dave's rules: adapt thresholds to each image, never "correct" the image, keep it simple first.

## What has been done

- **Docs and setup (10/14).** Spec (`PROBLEM.md`), known facts and unknowns (`constraints.md`), evaluation rules (`EVAL.md`), lab notebook (`EXPERIMENTS.md`), decision log. Dave read the spec and replied: horizon gating is fine in v1, f = 400 was a guess, and frames with no barrels must work.
- **Tooling.** A scribble-and-grow labeling tool, an eval harness (per-pixel precision / recall / IoU per class, per condition, plus a false-positive rate on empty frames), fixed train/test splits, snapshot import, 48 unit tests.
- **Data (10/19).** 21 frames on a white matte table at CMU under window light, all labeled: close, far, touching, occluded, clustered, edge, top-only, and three empty frames. Plus ruler and calibration frames on the wood desk.
- **Camera geometry.** Focal length ≈ 355–405 px, tilt ≈ 21.5–25.5°, horizon between rows 55 and 100 (methods disagree by about 10 %; a mark at camera height on a far wall would settle it). Barrel measured: 24 mm tall, 18 mm at the ends, 25.5 mm at the bulge, 6 mm stripe.
- **v1 algorithm (10/20).** Per image: drop everything above the horizon; drop pixels less saturated than the image's own background rows; drop pixels that match the image's own wall color; keep what falls inside an orange or blue RGB box learned from labeled barrels. The two boxes are the only thing learned from training data.
- **v1 result.** On 5 held-out frames: orange IoU 0.84, blue IoU 0.81, precision ≥ 0.96, zero pixels flagged on the empty frame. Chosen by cross-validation on the other 16 frames with a selection rule written down in advance.
- **Things tried that did not help here.** The bottom-rows "table" prior (redundant on a white table, breaks when a barrel is close); re-fitting the boxes per image; a YUV chroma box. All kept behind switches for the next dataset.

## What the errors are (measured 10/22)

- **Blue misses are shadowed lower faces.** 21 % of true blue pixels fall below the saturation floor; they have faded toward the gray of the wall. That is the single biggest error. Orange loses only 2 % this way.
- **Orange false pixels are two things:** the hand (skin sits inside the orange box) and the barrel's own reflection in the glossy table next to a close barrel (brownish, saturation ≈ 47, inside the box). Everything else is a thin halo at barrel edges.
- **IoU is a harsh number.** A one-pixel error around a far barrel 28 pixels wide costs about 10 %. Precision is 0.91–0.99 on every frame; the gap to 1.0 is mostly recall on shadows and edges.

## Open questions

1. Skin vs orange: an RGB box cannot separate them; a hue test (Lab a*) can. Is that fair game for v1.5?
2. The table prior: redundant on a white table, expected to matter on wood. It needs a cap on its spread before it can be trusted near close barrels.
3. Shadowed faces: chase them now (lower floor + a shape cue), or get a second table and light first?

## Next steps

1. Label the 19 wood-desk frames from 10/7 (nine lighting settings) with the tool. That is the real test of "adapts to the image."
2. Re-run the analysis, the v1 cross-validation, and the v1.5 arms on them, holding out whole lighting conditions.
3. Then the drop-in interface for `worldmap.py` (boxes), once the pixels are right.

---

## Draft check-in email to Dave

Subject: Barrel detector check-in: v1 segmentation results, next steps

Hi Dave,

Quick check-in on the barrel detector since my last note.

Done so far: the spec and constraints docs you read, a labeling tool, an evaluation harness with fixed splits, 21 labeled frames on a white matte table under window light, and a first camera calibration of my robot (f ≈ 355–405 px, tilt ≈ 21.5–25.5°; the two methods disagree by about 10 %, and a mark at camera height on a far wall would settle it). I also measured the barrel: 24 mm tall, 18 mm at the ends, 25.5 mm at the widest point, 6 mm stripe.

v1 result: on 5 held-out frames, per-pixel IoU 0.84 for orange and 0.81 for blue, precision ≥ 0.96, and zero pixels flagged on the empty-table frame. The method, per image: reject everything above the horizon; reject pixels less saturated than the image's own above-horizon rows (that floor comes out at 44–55 on these frames, nothing hand-set); reject pixels matching a median/MAD model of those same rows; then accept what falls in an orange or blue RGB box fit on labeled barrels. The boxes are the only thing learned from training data.

What the ablations said: the saturation floor and the wall model do essentially all of the separating. An RGB box alone scores 0.04 because the barrel clusters are smears along the brightness axis. The horizon gate changes nothing on this table (no barrel pixel is above row 105 in any frame), as you predicted. The bottom-rows table prior was redundant on a white table and harmful when a barrel is close (its shadow inflates the robust scale and the prior swallows the lid), so it is off for now and I'd like to fix it before trying wood.

Where the errors are: 21 % of true blue pixels are shadowed lower faces that fall below the saturation floor; orange false positives are my hand (skin lands inside the orange RGB box) and the barrel's own reflection in the glossy table next to a close barrel. Per-image re-fitting of the boxes and a YUV chroma box did not beat v1 here, which I think is expected with one table and one light.

Questions:
1. Is a hue-angle test (Lab a*, or chroma angle) acceptable for separating skin from barrel orange in v1.5, or do you count that as "another color space" for later?
2. For the table prior, would you rather I cap its spread (so a shadow can't inflate it) or restrict it to the lowest-variance part of the band?
3. Should I chase the shadowed-face recall now, or get a second table and lighting condition first? My instinct is the data first.

Next: label the 19 wood-desk frames from 10/7 (three lamp colors × three directions) and re-run everything on them, holding out whole lighting conditions. Everything is on the `barrels` branch; `docs/EXPERIMENTS.md` has each experiment with its numbers and results folder.

Thanks,
Tanush
