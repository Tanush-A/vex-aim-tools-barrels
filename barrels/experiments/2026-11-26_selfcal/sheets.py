"""Contact sheets for the self-calibration experiment: photo, first-pass mask, second-pass mask, boxes.

Train frames only (``judge.load_frame`` refuses anything else). Images are written where the caller says; the big
ones are not committed.

    python barrels/experiments/2026-11-26_selfcal/sheets.py OUT.png STEM [STEM ...]      # photo | first-pass mask
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

BGR = {ORANGE: (0, 140, 255), BLUE: (255, 120, 0)}


def mask_picture(mask: np.ndarray, bgr: np.ndarray) -> np.ndarray:
    """The class mask in its class colors over the photo dimmed to a quarter (so the place stays readable)."""
    out = (bgr.astype(np.float32) * 0.25).astype(np.uint8)
    for c, col in BGR.items():
        out[mask == c] = col
    return out


def draw_boxes(img: np.ndarray, barrels, thickness: int = 1, color=None, dashed: bool = False) -> np.ndarray:
    for b in barrels:
        x0, y0, x1, y1 = (int(v) for v in b.bbox)
        col = color or BGR[b.color]
        if dashed:
            for x in range(x0, x1, 6):
                cv2.line(img, (x, y0), (min(x + 3, x1), y0), col, thickness)
                cv2.line(img, (x, y1 - 1), (min(x + 3, x1), y1 - 1), col, thickness)
            for y in range(y0, y1, 6):
                cv2.line(img, (x0, y), (x0, min(y + 3, y1)), col, thickness)
                cv2.line(img, (x1 - 1, y), (x1 - 1, min(y + 3, y1)), col, thickness)
        else:
            cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), col, thickness)
    return img


def label(img: np.ndarray, text: str) -> np.ndarray:
    cv2.rectangle(img, (0, 0), (img.shape[1], 13), (0, 0, 0), -1)
    cv2.putText(img, text[:110], (3, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def gt_of(stem: str):
    return dtp.barrels_from_boxes(io.load_boxes(stem, check_image=False))


def row(stem: str, panels: list[tuple[str, np.ndarray]]) -> np.ndarray:
    return np.hstack([label(p.copy(), f"{t}" if i else f"{stem}  {t}") for i, (t, p) in enumerate(panels)])


def save_sheet(path, rows: list[np.ndarray], scale: float = 1.0) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    w = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]
    img = np.vstack(rows)
    if scale != 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(path), img)
    return path


def main(argv) -> int:
    from barrels import detector as det, geometry as geo, hslabel as hl, pipeline as pl
    out, stems = argv[0], argv[1:]
    model = hl.adopted_model()
    rows = []
    for s in stems:
        f = jg.load_frame(s)
        mask, _ = pl.segment(f, model)
        boxes = det.detect(mask, det.DetConfig(), geo.AIM_4A8B6118_BOXFIT)
        photo = draw_boxes(f.bgr.copy(), gt_of(s), 1, (255, 255, 255), dashed=True)
        rows.append(row(s, [("photo, hand boxes dashed", photo), ("first pass: fixed colors, boxes", draw_boxes(mask_picture(mask, f.bgr), boxes, 2))]))
    print(save_sheet(out, rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
