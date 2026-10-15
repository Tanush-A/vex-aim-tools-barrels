#!/usr/bin/env python3
"""Semi-automatic barrel labeler: scribble strokes, grow them into a full mask, fix, save.

Usage (from the venv):
    python barrels/tools/label_tool.py                 # all images in barrels/data/raw/
    python barrels/tools/label_tool.py --filter black  # only filenames containing "black"
    python barrels/tools/label_tool.py --raw DIR --labels DIR --scale 2

Workflow per image (target ~1 min):
    1. Scribble a few strokes: 1 orange, 2 blue, 3 table/background, 4 glare/uncertain.
       Include the stripes (orange stripe -> 1, blue stripe -> 2). Put at least one
       background stroke on the table AND on the wall; the top rows are auto-seeded
       as background.
    2. Press g to grow. Every pixel gets a class.
    3. Fix mistakes by painting more strokes (they override the grown mask at once),
       press g again if the fill needs redoing.
    4. n saves and moves on.

Keys:
    1 2 3 4     stroke class        0  eraser
    [ / ]       brush smaller / bigger
    left-drag   paint
    g           grow strokes -> mask
    r           drop the grown mask (keep strokes)
    c           clear strokes for this image (and the mask)
    u           undo last stroke
    v           cycle view: mask overlay / strokes only / raw
    n / p       save + next / previous image
    s           save
    q / Esc     save + quit

Writes to the labels folder: <stem>_strokes.png (your strokes, for resuming) and
<stem>_mask.png (0 other, 1 orange, 2 blue, 255 ignore — docs/DATA.md).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # works without pip install -e
from barrels import io  # noqa: E402
from barrels import labeling as lab  # noqa: E402

WIN = "barrel labeler"
# BGR display colors
MASK_COLORS = {io.ORANGE: (0, 128, 255), io.BLUE: (255, 100, 0), io.IGNORE: (255, 0, 255)}
STROKE_COLORS = {1: (0, 90, 255), 2: (255, 40, 0), 3: (0, 220, 0), 4: (255, 0, 255)}
VIEWS = ("mask", "strokes", "raw")


class Session:
    def __init__(self, images: list[Path], labels_dir: Path, scale: float, auto_bg_rows: int):
        self.images = images
        self.labels_dir = labels_dir
        self.scale = scale
        self.auto_bg_rows = auto_bg_rows
        self.idx = 0
        self.label = 1
        self.brush = 6
        self.view = 0
        self.drawing = False
        self.cursor = (-1, -1)
        self.undo: list[tuple[np.ndarray, np.ndarray | None]] = []
        self.load(0)

    # ---- per-image state
    @property
    def path(self) -> Path:
        return self.images[self.idx]

    def load(self, i: int) -> None:
        self.idx = i % len(self.images)
        self.img = io.load_image(self.path)
        sp = io.strokes_path(self.path, self.labels_dir)
        mp = io.mask_path(self.path, self.labels_dir)
        self.strokes = io.load_strokes(sp) if sp.exists() else np.zeros(self.img.shape[:2], np.uint8)
        self.mask = io.load_mask(mp) if mp.exists() else None
        self.undo.clear()

    def save(self) -> None:
        io.save_strokes(io.strokes_path(self.path, self.labels_dir), self.strokes)
        if self.mask is not None:
            io.save_mask(io.mask_path(self.path, self.labels_dir), self.mask)
            print(f"saved {self.path.stem}: strokes + mask")
        else:
            print(f"saved {self.path.stem}: strokes only (no mask yet — press g)")

    def grow(self) -> None:
        self.mask = lab.grow(self.img, self.strokes, auto_bg_rows=self.auto_bg_rows)

    def push_undo(self) -> None:
        self.undo.append((self.strokes.copy(), None if self.mask is None else self.mask.copy()))
        del self.undo[:-30]

    def pop_undo(self) -> None:
        if self.undo:
            self.strokes, self.mask = self.undo.pop()

    def paint(self, x: int, y: int) -> None:
        cv2.circle(self.strokes, (x, y), self.brush, self.label, -1)
        if self.mask is not None:
            if self.label == 0:
                pass  # eraser clears the stroke only; regrow (g) to refill that area
            else:
                cv2.circle(self.mask, (x, y), self.brush, lab.STROKE_TO_MASK[self.label], -1)

    # ---- rendering
    def render(self) -> np.ndarray:
        view = self.img.copy()
        mode = VIEWS[self.view]
        if mode == "mask" and self.mask is not None:
            overlay = self.img.copy()
            for v, col in MASK_COLORS.items():
                overlay[self.mask == v] = col
            view = cv2.addWeighted(overlay, 0.5, self.img, 0.5, 0)
        if mode in ("mask", "strokes"):
            for v, col in STROKE_COLORS.items():
                view[self.strokes == v] = col
        if self.scale != 1:
            view = cv2.resize(view, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_NEAREST)
        cx, cy = self.cursor
        if cx >= 0:
            cv2.circle(view, (int(cx * self.scale), int(cy * self.scale)), int(self.brush * self.scale), (255, 255, 255), 1)
        self.hud(view)
        return view

    def hud(self, view: np.ndarray) -> None:
        lines = [
            f"[{self.idx + 1}/{len(self.images)}] {self.path.name}   stroke={lab.STROKE_NAMES[self.label]}  brush={self.brush}  view={VIEWS[self.view]}",
        ]
        if self.mask is None:
            lines.append("mask: none (press g to grow)")
        else:
            counts = {io.CLASS_NAMES[v]: int((self.mask == v).sum()) for v in (io.ORANGE, io.BLUE, io.IGNORE)}
            lines.append("mask: " + "  ".join(f"{k}={v}" for k, v in counts.items()))
        if not (self.strokes == lab.STROKE_BG).any():
            lines.append("WARNING: no background stroke yet (3)")
        y = 18
        for text in lines:
            cv2.putText(view, text, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
            cv2.putText(view, text, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 20


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR, help="folder of images (default barrels/data/raw)")
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR, help="folder for masks/strokes (default barrels/data/labels)")
    ap.add_argument("--filter", default="", help="only images whose filename contains this text")
    ap.add_argument("--scale", type=float, default=2.0, help="display zoom (default 2)")
    ap.add_argument("--auto-bg-rows", type=int, default=10, help="top rows auto-seeded as background (default 10)")
    args = ap.parse_args(argv)

    images = [p for p in io.list_images(args.raw) if args.filter in p.name]
    if not images:
        print(f"no images in {args.raw} matching {args.filter!r}")
        return 1
    s = Session(images, args.labels, args.scale, args.auto_bg_rows)

    def on_mouse(event, x, y, flags, _):
        x, y = int(x / s.scale), int(y / s.scale)
        s.cursor = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            s.push_undo()
            s.drawing = True
        elif event == cv2.EVENT_LBUTTONUP:
            s.drawing = False
        if s.drawing and event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_MOUSEMOVE):
            s.paint(x, y)

    cv2.namedWindow(WIN, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WIN, on_mouse)
    print(__doc__)

    while True:
        cv2.imshow(WIN, s.render())
        k = cv2.waitKey(20) & 0xFF
        if k == 255:
            continue
        ch = chr(k)
        if ch in "01234":
            s.label = int(ch)
        elif ch == "[":
            s.brush = max(1, s.brush - 2)
        elif ch == "]":
            s.brush = min(60, s.brush + 2)
        elif ch == "g":
            s.push_undo()
            s.grow()
        elif ch == "r":
            s.push_undo()
            s.mask = None
        elif ch == "c":
            s.push_undo()
            s.strokes[:] = 0
            s.mask = None
        elif ch == "u":
            s.pop_undo()
        elif ch == "v":
            s.view = (s.view + 1) % len(VIEWS)
        elif ch == "s":
            s.save()
        elif ch in "np":
            s.save()
            s.load(s.idx + (1 if ch == "n" else -1))
        elif ch == "q" or k == 27:
            s.save()
            break
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    sys.exit(main())
