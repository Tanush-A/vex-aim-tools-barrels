"""Render masks as the PROBLEM.md output images and debug previews."""
from __future__ import annotations

import cv2
import numpy as np

from .io import BLUE, IGNORE, ORANGE

# PROBLEM.md colors are RGB; OpenCV images are BGR.
ORANGE_BGR = (0, 128, 255)    # RGB (255, 128, 0)
BLUE_BGR = (255, 100, 0)      # RGB (0, 100, 255)
GRAY_BGR = (128, 128, 128)
IGNORE_BGR = (255, 0, 255)


def render_outputs(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(orange_image, blue_image): flat class color on flat gray, per PROBLEM.md."""
    h, w = mask.shape
    orange = np.full((h, w, 3), GRAY_BGR, np.uint8)
    blue = np.full((h, w, 3), GRAY_BGR, np.uint8)
    orange[mask == ORANGE] = ORANGE_BGR
    blue[mask == BLUE] = BLUE_BGR
    return orange, blue


def overlay(image_bgr: np.ndarray, mask: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """Image blended with class colors (ignore in magenta)."""
    color = image_bgr.copy()
    color[mask == ORANGE] = ORANGE_BGR
    color[mask == BLUE] = BLUE_BGR
    color[mask == IGNORE] = IGNORE_BGR
    return cv2.addWeighted(color, alpha, image_bgr, 1 - alpha, 0)


def debug_sheet(image_bgr: np.ndarray, pred: np.ndarray, gt: np.ndarray | None = None) -> np.ndarray:
    """Side by side: image | prediction overlay | ground-truth overlay (if given)."""
    panels = [image_bgr, overlay(image_bgr, pred)]
    if gt is not None:
        panels.append(overlay(image_bgr, gt))
    return np.concatenate(panels, axis=1)
