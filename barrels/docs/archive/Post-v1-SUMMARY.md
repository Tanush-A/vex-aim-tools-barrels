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

## Things not tried yet (general ideas on the table)

- **Hue / color-angle test** (Lab a\*, or the angle in the YUV chroma plane): tells skin, cardboard and lid reflections apart from barrel orange regardless of brightness. Measured gap already known (a\* ≈ 29 skin vs 50 barrel).
- **Seed-and-grow (hysteresis):** find sure barrel pixels with strict thresholds, then let them spread into touching pixels that are *almost* barrel-colored. Targets the shadowed lower faces, which are the biggest miss. Same trick the labeling tool uses.
- **Table prior with a cap on its spread**, tested on a colored table (wood), where the saturation floor can't remove the table by itself.
- **Per-image re-fit of the color boxes on real multi-light data.** Tried on one light only, where it had nothing to adapt to.
- **Learned lookup table** over a coarse color grid instead of a box (Dave's CMVision), so the class region can be any shape.
- **Mask cleanup:** remove tiny blobs, bridge small gaps, open/close.
- **Geometry:** reject reflections (they sit below the barrel's contact row); expected barrel size per image row. Needs the horizon/focal-length calibration tightened first.
- **Stripe structure as evidence:** a blue band inside orange (or the reverse) confirms a barrel.
- **Edges/gradients** to split touching barrels (matters for bounding boxes, not pixels).
- **Temporal consistency** across frames (the robot sees video).
- **More data:** other tables, lights, and robot cameras.

## Proposed v2 scope (to confirm with Dave)

1. **Data first:** label the 19 wood-desk frames from 10/7 (three lamp colors × three directions), shoot the warm-light black table, and evaluate holding out whole lighting conditions.
2. **Hue test** added to the per-class test, for skin and reflections.
3. **Seed-and-grow** for shadowed faces.
4. **Table prior with a spread cap**, judged on wood.
5. **Mask cleanup** (tiny blobs).

Everything else above is deferred: lookup tables, geometry rejection, stripe evidence, bounding boxes and the `worldmap.py` drop-in, temporal, glare.

---

## Draft check-in email to Dave

Subject: Barrel detector: v1 done, proposed v2 scope

Hi Dave,

v1 is done. On a white matte table under window light, per-pixel IoU on 5 held-out frames is 0.84 for orange and 0.81 for blue, precision ≥ 0.96, zero pixels flagged on the empty-table frame. The method adapts to each image: the saturation floor and the wall model are both derived from the image's rows above the horizon; the only thing learned from labels is one RGB box per class. Ablations: the saturation floor and the wall model do nearly all the work, an RGB box alone scores 0.04 (the clusters are brightness smears, as you expected), and the horizon gate changes nothing on this table.

The remaining errors are shadowed lower faces (21 % of true blue pixels fall below the saturation floor), skin inside the orange box, and lid reflections on the glossy table next to close barrels.

Proposed v2: (1) label the wood-desk frames (three lamp colors × three directions) and evaluate holding out whole lighting conditions; (2) add a hue test (Lab a*) for skin and reflections; (3) seed-and-grow from confident pixels to recover shadowed faces; (4) the table prior with a cap on its spread, judged on wood; (5) small-blob cleanup. Deferred for now: lookup tables, geometry-based rejection, stripe structure, bounding boxes, temporal. Does that scope look right to you?

Everything is on the `barrels` branch; `docs/EXPERIMENTS.md` has each experiment with its numbers.

Thanks,
Tanush
