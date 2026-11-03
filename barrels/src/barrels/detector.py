"""The v2 detector: class mask -> one Barrel per barrel, with hidden bottoms filled in by the geometry.
Plain-English guide: docs/HOW-IT-WORKS.md section 3. Built in explained steps:

  step 1 (2026-11-03)  barrel-colored blobs -> how many barrels, from the width the geometry expects at
                       that row -> the bottom edge: the seen one if it agrees with the top row, else the
                       one the top row predicts (shadow, occlusion), clipped to the frame.
  step 2 (next)        the stripe as the barrel anchor (color says "orange thing", the stripe says "barrel").

Everything here is a pure function of the mask and the camera: nothing is fit per image.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import cv2
import numpy as np

from . import geometry as geo
from .detect_types import Barrel
from .io import BLUE, ORANGE


@dataclass(frozen=True)
class DetConfig:
    min_area_px: int = 20        # smaller blobs are noise (same constant as the v1.5 auto-split; never tuned)
    close_px: int = 3            # close gaps this small so body + stripe + a speckled face form one blob
    bottom_tol: float = 0.15     # the seen bottom is trusted when within this fraction of the box height of the predicted one
    bottom_tol_min_px: int = 4   # ... and never less than this many pixels
    width_min: float = 0.4       # a piece narrower than this x the expected width is a sliver -> dropped
    width_max: float = 1.6       # a piece wider than this x the expected width after splitting -> dropped (not barrel-shaped)
    split_search: float = 0.25   # when cutting a wide blob, look for the narrowest column within +-this fraction of a width
    min_width_px: float = 16.0   # a barrel this narrow would be > ~60 cm away: beyond the table -> such rows hold no barrels

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Blob:
    bbox: tuple[int, int, int, int]     # x0, y0, x1, y1 half-open
    pixels: np.ndarray                  # bool HxW, the blob's pixels
    n_orange: int
    n_blue: int

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]


# ---------------------------------------------------------------- step 1a: blobs

def find_blobs(mask: np.ndarray, cfg: DetConfig = DetConfig()) -> list[Blob]:
    """Connected blobs of barrel-colored pixels (orange and blue together, so a body and its stripe are one
    blob), after closing small gaps and dropping specks."""
    union = np.isin(mask, (ORANGE, BLUE)).astype(np.uint8)
    if cfg.close_px >= 3:
        k = cfg.close_px if cfg.close_px % 2 else cfg.close_px + 1
        union = cv2.morphologyEx(union, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(union, connectivity=8)
    out = []
    for i in range(1, n):
        x, y, bw, bh, area = (int(v) for v in st[i])
        if area < cfg.min_area_px:
            continue
        sel = lab == i
        n_o, n_b = int((mask[sel] == ORANGE).sum()), int((mask[sel] == BLUE).sum())
        if n_o + n_b == 0:
            continue
        out.append(Blob((x, y, x + bw, y + bh), sel, n_o, n_b))
    return sorted(out, key=lambda b: b.bbox[0])


# ---------------------------------------------------------------- step 1b: how many barrels is this blob?

def expected_width_px(bbox, cam: geo.CameraModel, frame_h: int) -> float:
    """How wide one barrel is at this blob's distance. From the bottom row when the bottom is in the frame,
    else from the top row (a barrel cut by the frame bottom has no bottom row to use)."""
    x0, y0, x1, y1 = bbox
    if y1 < frame_h:
        d = cam.d_axis_from_bottom_row(y1)
    else:
        d = cam._d_axis_from_point_row(y0, geo.BARREL_HEIGHT_MM, +geo.BARREL_END_DIAMETER_MM / 2)
    if not math.isfinite(d) or d <= 0:
        return math.inf
    return cam.f * geo.BARREL_BULGE_DIAMETER_MM / d


def split_blob(blob: Blob, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig()) -> list[Blob]:
    """A blob about n barrel-widths wide is n barrels side by side: cut it at the narrowest columns (the
    waists between bulges) near the n-1 equal-spacing positions, and give each piece its own tight box."""
    W = expected_width_px(blob.bbox, cam, mask.shape[0])
    if not math.isfinite(W) or W <= 0:
        return [blob]
    n = max(1, int(round(blob.width / W)))
    if n == 1:
        return [blob]
    x0, y0, x1, y1 = blob.bbox
    cols = blob.pixels[y0:y1, x0:x1].sum(axis=0)          # how many barrel pixels in each column
    cuts = []
    for k in range(1, n):
        c = x0 + k * blob.width / n
        lo, hi = int(max(x0 + 1, c - cfg.split_search * W)), int(min(x1 - 1, c + cfg.split_search * W))
        if hi <= lo:
            cuts.append(int(round(c))); continue
        seg = cols[lo - x0:hi - x0]
        best = np.flatnonzero(seg == seg.min())              # the narrowest columns ...
        cuts.append(lo + int(best[np.argmin(np.abs(lo + best - c))]))   # ... the one nearest the equal-spacing cut wins ties
    pieces = []
    edges = [x0, *cuts, x1]
    for a, b in zip(edges[:-1], edges[1:]):
        sel = blob.pixels.copy()
        sel[:, :a] = False; sel[:, b:] = False
        ys, xs = np.where(sel)
        if len(xs) == 0:
            continue
        bb = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        pieces.append(Blob(bb, sel, int((mask[sel] == ORANGE).sum()), int((mask[sel] == BLUE).sum())))
    return pieces or [blob]


# ---------------------------------------------------------------- step 1c: the bottom edge

def predicted_bottom(cam: geo.CameraModel, top_row: float) -> float:
    """Where the base must be if the lid's far edge is at ``top_row`` (24 mm tall barrel, base near edge 18 mm
    closer than the lid far edge). inf when the top row puts the base at or behind the camera (below the frame)."""
    d_axis = cam._d_axis_from_point_row(top_row, geo.BARREL_HEIGHT_MM, +geo.BARREL_END_DIAMETER_MM / 2)
    d_base = d_axis - geo.BARREL_END_DIAMETER_MM / 2
    if not math.isfinite(d_axis) or d_base <= 0:
        return math.inf
    return cam.point_row(d_base, 0.0)


def resolve_bottom(bbox, cam: geo.CameraModel, frame_h: int, cfg: DetConfig = DetConfig()) -> tuple[int, set[str]]:
    """The bottom row to draw. The top row says how far away the barrel is, and from that where its base
    must be (`bottom_row_from_top_row`). Keep the seen bottom when it agrees with that prediction; replace it
    when it does not (a shadowed face makes the blob too short, a reflection too tall, an occluder hides the
    base). Always clipped to the frame; a box reaching the frame bottom is 'truncated'."""
    x0, y0, x1, y1 = bbox
    flags: set[str] = set()
    pred = predicted_bottom(cam, y0)
    if math.isfinite(pred):
        tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * (pred - y0))
        if abs(y1 - pred) > tol and not (y1 >= frame_h and pred >= frame_h):
            y1 = int(round(pred)); flags.add("bottom_inferred")
    y1 = min(max(y1, y0 + 1), frame_h)
    if y1 >= frame_h:
        flags.add("truncated")
    return y1, flags


# ---------------------------------------------------------------- the detector

def detect(mask: np.ndarray, cfg: DetConfig = DetConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT) -> list[Barrel]:
    """Class mask (0 other / 1 orange / 2 blue / 255 ignore) -> barrels. Same signature as detect_cc.detect."""
    h, w = mask.shape
    out = []
    for blob in find_blobs(mask, cfg):
        for piece in split_blob(blob, mask, cam, cfg):
            x0, y0, x1, y1 = piece.bbox
            y1, flags = resolve_bottom(piece.bbox, cam, h, cfg)
            W = cam.expected_barrel_width_px(bottom_row=y1) if y1 < h else expected_width_px((x0, y0, x1, h), cam, h)
            if not math.isfinite(W) or W < cfg.min_width_px:
                continue                                   # above the horizon or too far to be on the table
            if not (cfg.width_min * W <= (x1 - x0) <= cfg.width_max * W):
                continue                                   # a sliver, or too wide to be one barrel
            if x0 == 0 or x1 == w or y0 == 0:
                flags.add("truncated")
            n_o, n_b = piece.n_orange, piece.n_blue
            color = ORANGE if n_o >= n_b else BLUE
            out.append(Barrel(color=color, bbox=(x0, y0, x1, y1), confidence=max(n_o, n_b) / (n_o + n_b),
                              flags=frozenset(flags), area=int(piece.pixels.sum()), source="det1"))
    return sorted(out, key=lambda b: b.bbox[0])


BOX_COLOR_BGR = {ORANGE: (0, 255, 255), BLUE: (0, 255, 0)}   # yellow = orange barrel, green = blue barrel (Dave's convention)


def draw(image_bgr: np.ndarray, barrels: list[Barrel], thickness: int = 1) -> np.ndarray:
    """The v2 output image: the input with one 1-px rectangle per barrel — yellow for an orange barrel, green
    for a blue one, so the lines stand out from the barrels themselves — and nothing else."""
    out = image_bgr.copy()
    for b in barrels:
        x0, y0, x1, y1 = b.bbox
        cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), BOX_COLOR_BGR[b.color], thickness)
    return out
