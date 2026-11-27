"""Where in one frame the color of the light can be read from (2026-11-26, experiment ``2026-11-26_light``).

Nothing here runs by default: no module of the detector imports this one. It is the measuring kit of the experiment
"what in the frame can the light be read from" (``experiments/2026-11-26_light/PREREG.md``), kept here so the
readings have unit tests and one definition.

A *reading* picks some pixels of the frame without knowing where a barrel is, and says what color they have. If the
pixels are things that have no color of their own (a white wall, a gray table, a highlight), their color is the
light's. Each reading is two steps: ``<name>_mask`` says WHICH pixels (H x W bool), ``read`` says what color they
have, always the same numbers (``Reading``):

- ``warmth``: the median of (R - B) / (R + G + B + 1) over the pixels read. 0 = neutral, positive = yellow, negative
  = blue. The same number ``lightcolor.light_warmth`` gives; ``whole_frame`` with ``top`` = 5 IS that function.
- ``log_rg``, ``log_bg``: the medians of log((R + 1) / (G + 1)) and log((B + 1) / (G + 1)) (the review's units).
- ``n``: how many pixels were read. A reading that found fewer than ``MIN_PX`` says nothing: its numbers are nan.

The readings:

==================  =================================================================================================
``whole_frame``     the brightest 5 % of the whole frame (the existing rule: the "white patch")
``above_gate``      the brightest 5 % of the rows above the horizon gate (rows 0-49), where no barrel can be
``without_barrels`` the brightest 5 % of what is left after everything a color model paints as barrel is taken out,
                    with a margin around it
``neutral``         pixels with almost no color and middle brightness (S under a limit): white and gray things
``least_colored``   the least colored tenth of the middle-bright pixels (a relative version of ``neutral``: under a
                    yellow lamp nothing white is under a fixed S limit)
``highlights``      nearly clipped pixels: the brightest channel just under the clip level, no channel clipped
``near_strip``      the strip of table nearest the robot (the bottom rows)
``gray_world``      every pixel below the gate that is not dark (the whole scene's cast)
``max_rgb``         the 99th percentile of each channel on its own (the classic "max RGB"; it has no mask)
``tiles``           the frame cut in tiles; each bright tile's brightest pixels give a warmth; the answer is a LOW
                    quantile over the tiles. A light colors every tile; an orange thing colors one.
==================  =================================================================================================

Also here: ``ramp`` (the straight line with two ends that every light-following threshold in the experiment uses) and
``pixel_warmth`` (the per-pixel warmth, for a rule that compares a pixel with the light). A pixel is never changed.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

MIN_PX = 200            # a reading from fewer pixels than this says nothing (nan)
GATE_ROW = 50           # the horizon gate: rows above it are never barrel
NAN = float("nan")


@dataclass(frozen=True)
class Reading:
    warmth: float       # median (R - B) / (R + G + B + 1) of the pixels read; nan when fewer than MIN_PX
    log_rg: float       # median log((R + 1) / (G + 1))
    log_bg: float       # median log((B + 1) / (G + 1))
    n: int              # pixels read
    v_med: float        # their median brightness (the brightest channel)

    @property
    def ok(self) -> bool:
        return self.n >= MIN_PX and np.isfinite(self.warmth)


def _f(rgb: np.ndarray) -> np.ndarray:
    a = np.asarray(rgb)
    if a.ndim != 3 or a.shape[2] != 3:
        raise ValueError(f"rgb must be H x W x 3, got shape {a.shape}")
    return a.astype(np.float32)


def pixel_warmth(rgb: np.ndarray) -> np.ndarray:
    """(R - B) / (R + G + B + 1) for every pixel (H x W float32)."""
    x = _f(rgb)
    return (x[..., 0] - x[..., 2]) / (x.sum(-1) + 1.0)


def hsv_s(rgb: np.ndarray) -> np.ndarray:
    """HSV saturation 0-255 per pixel: 255 * (max - min) / max; 0 for a black pixel."""
    x = _f(rgb)
    mx = x.max(-1)
    return np.where(mx > 0, 255.0 * (mx - x.min(-1)) / np.maximum(mx, 1.0), 0.0).astype(np.float32)


def summarize(px: np.ndarray) -> Reading:
    """The numbers of a set of pixels (N x 3, R G B). Fewer than ``MIN_PX`` pixels: their count and nan."""
    px = np.asarray(px, np.float32).reshape(-1, 3)
    if len(px) < MIN_PX:
        return Reading(NAN, NAN, NAN, int(len(px)), NAN)
    w = float(np.median((px[:, 0] - px[:, 2]) / (px.sum(1) + 1.0)))
    rg = float(np.median(np.log((px[:, 0] + 1.0) / (px[:, 1] + 1.0))))
    bg = float(np.median(np.log((px[:, 2] + 1.0) / (px[:, 1] + 1.0))))
    return Reading(w, rg, bg, int(len(px)), float(np.median(px.max(1))))


def read(rgb: np.ndarray, mask: np.ndarray) -> Reading:
    """The color of the pixels of ``rgb`` where ``mask`` is True."""
    return summarize(_f(rgb)[np.asarray(mask, bool)])


# ---------------------------------------------------------------- which pixels

def brightest_mask(rgb: np.ndarray, top: float = 5.0, keep: np.ndarray | None = None) -> np.ndarray:
    """The brightest ``top`` % (by the brightest channel; ties at the threshold included) of the pixels where ``keep``
    is True (None = every pixel). No pixel kept: an empty mask."""
    v = _f(rgb).max(-1)
    keep = np.ones(v.shape, bool) if keep is None else np.asarray(keep, bool)
    if not keep.any():
        return np.zeros(v.shape, bool)
    return keep & (v >= np.percentile(v[keep], 100.0 - top))


def whole_frame_mask(rgb: np.ndarray, top: float = 5.0) -> np.ndarray:
    return brightest_mask(rgb, top)


def rows_mask(shape, lo: int, hi: int) -> np.ndarray:
    m = np.zeros(tuple(shape[:2]), bool)
    m[max(0, lo):max(0, hi)] = True
    return m


def above_gate_mask(rgb: np.ndarray, rows: int = GATE_ROW, top: float = 5.0) -> np.ndarray:
    return brightest_mask(rgb, top, rows_mask(np.shape(rgb), 0, rows))


def grow(mask: np.ndarray, margin: int) -> np.ndarray:
    """A mask grown by ``margin`` pixels in every direction (a square)."""
    if margin <= 0:
        return np.asarray(mask, bool)
    k = 2 * int(margin) + 1
    return cv2.dilate(np.asarray(mask, np.uint8), np.ones((k, k), np.uint8)) > 0


def without_barrels_mask(rgb: np.ndarray, barrel_mask: np.ndarray, margin: int = 15, top: float = 5.0) -> np.ndarray:
    return brightest_mask(rgb, top, ~grow(np.asarray(barrel_mask) > 0, margin))


def neutral_mask(rgb: np.ndarray, s_max: float = 40.0, v_lo: float = 60.0, v_hi: float = 230.0) -> np.ndarray:
    x = _f(rgb)
    v = x.max(-1)
    return (hsv_s(x) < s_max) & (v >= v_lo) & (v < v_hi)


def least_colored_mask(rgb: np.ndarray, share: float = 10.0, v_lo: float = 60.0, v_hi: float = 230.0) -> np.ndarray:
    x = _f(rgb)
    v = x.max(-1)
    mid = (v >= v_lo) & (v < v_hi)
    if not mid.any():
        return mid
    s = hsv_s(x)
    return mid & (s <= np.percentile(s[mid], share))


def highlights_mask(rgb: np.ndarray, v_lo: float = 225.0, clip: float = 250.0) -> np.ndarray:
    v = _f(rgb).max(-1)
    return (v >= v_lo) & (v < clip)


def near_strip_mask(rgb: np.ndarray, rows: int = 80, v_min: float = 40.0) -> np.ndarray:
    x = _f(rgb)
    return rows_mask(x.shape, x.shape[0] - rows, x.shape[0]) & (x.max(-1) >= v_min)


def gray_world_mask(rgb: np.ndarray, from_row: int = GATE_ROW, v_min: float = 40.0) -> np.ndarray:
    x = _f(rgb)
    return rows_mask(x.shape, from_row, x.shape[0]) & (x.max(-1) >= v_min)


# ---------------------------------------------------------------- the readings

def whole_frame(rgb: np.ndarray, top: float = 5.0) -> Reading:
    """The brightest ``top`` % of the whole frame. With ``top`` = 5 its warmth is ``lightcolor.light_warmth``."""
    return read(rgb, whole_frame_mask(rgb, top))


def above_gate(rgb: np.ndarray, rows: int = GATE_ROW, top: float = 5.0) -> Reading:
    """The brightest ``top`` % of rows 0 .. ``rows`` - 1: above the horizon gate, where no barrel can be."""
    return read(rgb, above_gate_mask(rgb, rows, top))


def without_barrels(rgb: np.ndarray, barrel_mask: np.ndarray, margin: int = 15, top: float = 5.0) -> Reading:
    """The brightest ``top`` % of the frame after every pixel that ``barrel_mask`` marks (what a color model painted
    orange or blue), grown by ``margin`` px, is taken out."""
    return read(rgb, without_barrels_mask(rgb, barrel_mask, margin, top))


def neutral(rgb: np.ndarray, s_max: float = 40.0, v_lo: float = 60.0, v_hi: float = 230.0) -> Reading:
    """Pixels with almost no color: HSV saturation under ``s_max`` and brightness in [``v_lo``, ``v_hi``)."""
    return read(rgb, neutral_mask(rgb, s_max, v_lo, v_hi))


def least_colored(rgb: np.ndarray, share: float = 10.0, v_lo: float = 60.0, v_hi: float = 230.0) -> Reading:
    """The least colored ``share`` % (by HSV saturation) of the pixels with brightness in [``v_lo``, ``v_hi``)."""
    return read(rgb, least_colored_mask(rgb, share, v_lo, v_hi))


def highlights(rgb: np.ndarray, v_lo: float = 225.0, clip: float = 250.0) -> Reading:
    """Nearly clipped pixels: the brightest channel in [``v_lo``, ``clip``), so no channel is clipped and the color
    is still there."""
    return read(rgb, highlights_mask(rgb, v_lo, clip))


def near_strip(rgb: np.ndarray, rows: int = 80, v_min: float = 40.0) -> Reading:
    """The strip of table nearest the robot: the bottom ``rows`` rows, pixels at least ``v_min`` bright."""
    return read(rgb, near_strip_mask(rgb, rows, v_min))


def gray_world(rgb: np.ndarray, from_row: int = GATE_ROW, v_min: float = 40.0) -> Reading:
    """Every pixel from row ``from_row`` down that is at least ``v_min`` bright: the cast of the whole scene."""
    return read(rgb, gray_world_mask(rgb, from_row, v_min))


def max_rgb(rgb: np.ndarray, q: float = 99.0) -> Reading:
    """The ``q``-th percentile of each channel on its own, read as one color (the classic "max RGB")."""
    x = _f(rgb).reshape(-1, 3)
    if len(x) < MIN_PX:
        return Reading(NAN, NAN, NAN, int(len(x)), NAN)
    r, g, b = (float(np.percentile(x[:, i], q)) for i in range(3))
    return Reading((r - b) / (r + g + b + 1.0), float(np.log((r + 1) / (g + 1))), float(np.log((b + 1) / (g + 1))), int(len(x)), max(r, g, b))


def tile_votes(rgb: np.ndarray, grid: tuple[int, int] = (4, 4), top: float = 20.0, v_min: float = 100.0) -> list[tuple[tuple[slice, slice], Reading]]:
    """The tiles that vote: ``grid`` (rows, columns) tiles; a tile votes when the brightest ``top`` % of its pixels
    have a median brightness of at least ``v_min``. -> [((row slice, column slice), that tile's reading)]."""
    x = _f(rgb)
    h, w = x.shape[:2]
    out = []
    for i in range(grid[0]):
        for j in range(grid[1]):
            sl = (slice(i * h // grid[0], (i + 1) * h // grid[0]), slice(j * w // grid[1], (j + 1) * w // grid[1]))
            r = read(x[sl], brightest_mask(x[sl], top))
            if r.ok and r.v_med >= v_min:
                out.append((sl, r))
    return out


def tiles(rgb: np.ndarray, grid: tuple[int, int] = (4, 4), top: float = 20.0, v_min: float = 100.0, q: float = 25.0,
          min_tiles: int = 3) -> Reading:
    """The ``q``-th percentile (a LOW one) over the voting tiles of each tile's warmth: a light colors every tile, an
    orange thing colors one. (``log_bg`` takes the mirrored quantile, since blue falls where warmth rises.) Fewer
    than ``min_tiles`` votes: nan."""
    votes = [r for _, r in tile_votes(rgb, grid, top, v_min)]
    if len(votes) < min_tiles:
        return Reading(NAN, NAN, NAN, 0, NAN)
    return Reading(float(np.percentile([r.warmth for r in votes], q)), float(np.percentile([r.log_rg for r in votes], q)),
                   float(np.percentile([r.log_bg for r in votes], 100.0 - q)), sum(r.n for r in votes), float(np.median([r.v_med for r in votes])))


def tiles_mask(rgb: np.ndarray, grid: tuple[int, int] = (4, 4), top: float = 20.0, v_min: float = 100.0) -> np.ndarray:
    """The pixels of the voting tiles that were read (for a picture)."""
    x = _f(rgb)
    m = np.zeros(x.shape[:2], bool)
    for sl, _ in tile_votes(x, grid, top, v_min):
        m[sl] = brightest_mask(x[sl], top)
    return m


# ---------------------------------------------------------------- the line every light-following threshold uses

def ramp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    """``y0`` at x <= x0, ``y1`` at x >= x1, a straight line between. A nan reading gives ``y0`` (nothing moves)."""
    if x1 <= x0:
        raise ValueError(f"x1 must be above x0, got x0={x0}, x1={x1}")
    if not np.isfinite(x) or x <= x0:
        return float(y0)
    if x >= x1:
        return float(y1)
    return float(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
