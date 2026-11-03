<!-- Dave's CLAUDE.md from barrels.zip (2026-09-28), copied verbatim 2026-11-03. Reference only. -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goal

Detect two types of plastic VEX robotics barrels (blue and orange) in color images. Input: a color image. Output: a set of bounding boxes with class labels (blue barrel, orange barrel) for each detected barrel instance.

## Reference Data

- `bounding_boxes.png` — example showing multiple barrels at mid-range distance; bounding boxes are tight around each barrel cylinder
- `bounding_boxes2.png` — example showing two barrels close-up; one blue, one orange

The barrels are short squat cylinders: **25 mm high, 22 mm diameter**. Two types:
- **Orange barrel**: orange body with a 6 mm blue stripe around the middle
- **Blue barrel**: blue body with a 6 mm orange stripe around the middle

They are always upright and resting on the ground plane. Bounding boxes are therefore always portrait-oriented (taller than wide). The vertical position of the top or bottom edge in the image is a monotonic function of distance from the camera — useful both for filtering false positives and for depth estimation if camera intrinsics are known.

## Camera Geometry

- **Camera height**: 43.47 mm above ground plane (known exactly)
- **Camera tilt**: 18–25° below horizontal (unknown within this range)

With camera height `h = 43.47 mm` and tilt angle `θ`, a ground point at horizontal distance `d` from the camera projects to a known pixel row. The tilt uncertainty introduces a bounded error in ground-plane distance estimates. Because barrel height (25 mm) is comparable to camera height (43.47 mm), the top and bottom edges of near barrels will appear at substantially different depths — the bottom edge lies on the ground plane and the top edge is at 25 mm height, which is above the camera's ground contact point but below the lens.

## Known Detection Challenges

1. **Occlusion**: Barrels can partially occlude each other, producing overlapping bounding boxes. A detector must handle this rather than suppressing overlapping detections via NMS.

2. **Color adjacency**: The blue stripe of an orange barrel can touch the blue body of an adjacent blue barrel (and vice versa). Simple connected-components labeling on color masks will merge distinct barrels into one blob. Detection must use shape/geometry cues (expected aspect ratio, stripe position within the blob) to split merged regions.

4. **Lighting variation**: Must operate under a wide range of conditions — dim soft indoor light, bright fluorescent, and direct sunlight. Color thresholds must be robust to large shifts in overall intensity and color temperature. Relying on raw RGB values or narrow HSV ranges will fail; consider illumination-normalized color representations or adaptive thresholding.

3. **Close-range partial visibility**: When a barrel is very close to the camera, the bottom and middle stripe may fall below the image frame entirely. Only the upper band and circular top are visible. The top surface can appear nearly white due to specular reflection, making it unreliable for color classification. For these cases the detector must classify barrel type from the upper body color band alone, and must not require the stripe to be visible. Because the barrel has fixed physical dimensions and the camera height is known, the full bounding box can be recovered from partial observations. Two complementary cues:
- **Close barrels**: bottom/stripe may be off-screen, but the full barrel width is visible and pins the distance.
- **Distant barrels**: full width may be hidden by occlusion, but the bottom edge rests on the ground plane and its vertical pixel position gives distance via the camera geometry.

The output bounding box should reflect the full predicted extent even when part of the barrel is out of frame. Clipping to image bounds is acceptable if necessary, but prefer the unclipped box.

## Implementation

**Language/library**: Python + OpenCV.

**Function signature**:
```python
def detect_barrels(image: np.ndarray) -> list[dict]:
    """
    Args:
        image: 640x480x3 uint8 numpy array (RGB)
    Returns:
        List of dicts, each with:
            'bbox': (x, y, w, h) in pixels  # top-left origin; coords may extend outside [0,640)x[0,480)
            'label': 'orange' | 'blue'
    """
```

Code is in `detect.py`. Entry point: `detect_barrels(image)`.

**Algorithm summary (`detect.py`):**
1. Convert RGB → BGR → HSV.
2. Build orange and blue binary masks with loose S/V thresholds (robust to lighting); close small intra-blob gaps with a 5×5 morphological close.
3. For each body color, find external contours, then **merge vertically adjacent blobs** that represent the two halves of the same barrel body split by the stripe gap. Merge criteria: ≥60 % horizontal overlap of the narrower blob's width AND vertical gap ≤ 1.5 × expected stripe height at that scale.
4. For each (merged) blob, select detection mode:
   - **Standard** (bounding-rect area ≤ 15 % of image): require ≥18 % stripe-color fill in the expected stripe band, plus ≥20 % body-color fill in the body bands.
   - **Close-up** (bounding-rect area > 15 % of image): stripe is off-screen or hidden by near-overhead viewing angle; require only ≥28 % body-color fill. Body fill uses only in-frame pixels so off-screen bands don't penalise the score.
   - Infer full barrel height from width: `fh = round(w × H_mm/D_mm)` — valid at any distance (focal length cancels).
   - Emit `{'bbox': (x, y, w, fh), 'label': ...}` — `fh` may extend below y=480.

**Validated on reference images** (`bounding_boxes.png`, `bounding_boxes2.png`):
- Mid-range scene: 3 of 4 barrels detected; the orange barrel directly adjacent to the blue barrel (colour-adjacency case) is missed.
- Close-up scene: both barrels correctly detected and labelled; blue bounding box is somewhat wider than ideal because the blue barrel body and the adjacent orange barrel's blue stripe merge into one blob.

**Known limitation:** when an orange barrel's blue stripe is in direct contact with a blue barrel's body, their colour blobs merge and the detector may produce one wide detection instead of two. A fix would require splitting wide blobs using a column-wise stripe-colour profile to identify individual barrel centres.
