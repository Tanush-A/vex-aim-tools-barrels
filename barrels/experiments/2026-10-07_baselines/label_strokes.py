#!/usr/bin/env python3
"""
Quick scribble labeler for barrel color segmentation.

Usage:
    python label_strokes.py path/to/snapshots/

Paint rough strokes over each image (you do NOT need to cover everything):
    1 = orange (barrel orange)     2 = blue (barrel blue)
    3 = background (anything else, esp. orange/blue-ish distractors: wood, skin, notebooks)
    4 = specular / washed-out barrel (white glare on a barrel)
    0 = eraser

Keys:
    left-drag   paint with current label
    [ / ]       smaller / bigger brush
    n / p       save + next / previous image
    s           save
    h           toggle overlay (see raw image)
    q / Esc     save + quit

Output: for each foo.png, writes foo_strokes.png next to it (single-channel,
pixel values 0=unlabeled, 1=orange, 2=blue, 3=background, 4=specular).
Existing *_strokes.png files are loaded so you can resume.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

LABELS = {0: "eraser", 1: "orange", 2: "blue", 3: "background", 4: "specular"}
COLORS = {1: (0, 140, 255), 2: (255, 80, 0), 3: (0, 255, 0), 4: (255, 0, 255)}  # BGR
WIN = "label_strokes"


def strokes_path(img_path: Path) -> Path:
    return img_path.with_name(img_path.stem + "_strokes.png")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    folder = Path(sys.argv[1])
    images = sorted(
        p for p in folder.iterdir()
        if p.suffix.lower() in (".png", ".jpg", ".jpeg")
        and not p.stem.endswith(("_strokes", "_ground_truth", "_result", "_gtmask"))
    )
    if not images:
        print(f"No images found in {folder}")
        sys.exit(1)

    state = {"idx": 0, "label": 1, "brush": 6, "drawing": False, "show": True}

    def load(i):
        img = cv2.imread(str(images[i]), cv2.IMREAD_COLOR)
        sp = strokes_path(images[i])
        if sp.exists():
            mask = cv2.imread(str(sp), cv2.IMREAD_GRAYSCALE)
        else:
            mask = np.zeros(img.shape[:2], np.uint8)
        return img, mask

    img, mask = load(0)

    def save():
        cv2.imwrite(str(strokes_path(images[state["idx"]])), mask)

    def on_mouse(event, x, y, flags, _):
        if event == cv2.EVENT_LBUTTONDOWN:
            state["drawing"] = True
        elif event == cv2.EVENT_LBUTTONUP:
            state["drawing"] = False
        if state["drawing"] and event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_MOUSEMOVE):
            cv2.circle(mask, (x, y), state["brush"], state["label"], -1)

    cv2.namedWindow(WIN, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WIN, on_mouse)

    while True:
        view = img.copy()
        if state["show"]:
            overlay = img.copy()
            for lab, col in COLORS.items():
                overlay[mask == lab] = col
            view = cv2.addWeighted(overlay, 0.55, img, 0.45, 0)
        counts = {LABELS[k]: int((mask == k).sum()) for k in (1, 2, 3, 4)}
        hud = (f"[{state['idx']+1}/{len(images)}] {images[state['idx']].name} | "
               f"label={LABELS[state['label']]} brush={state['brush']}")
        cv2.putText(view, hud, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 3)
        cv2.putText(view, hud, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cnt = "  ".join(f"{k}:{v}" for k, v in counts.items())
        cv2.putText(view, cnt, (8, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 3)
        cv2.putText(view, cnt, (8, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.imshow(WIN, view)

        k = cv2.waitKey(20) & 0xFF
        if k == 255:
            continue
        ch = chr(k)
        if ch in "01234":
            state["label"] = int(ch)
        elif ch == "[":
            state["brush"] = max(1, state["brush"] - 2)
        elif ch == "]":
            state["brush"] = min(60, state["brush"] + 2)
        elif ch == "h":
            state["show"] = not state["show"]
        elif ch == "s":
            save()
            print("saved", strokes_path(images[state["idx"]]).name)
        elif ch in "np":
            save()
            step = 1 if ch == "n" else -1
            state["idx"] = (state["idx"] + step) % len(images)
            img, mask = load(state["idx"])
        elif ch == "q" or k == 27:
            save()
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
