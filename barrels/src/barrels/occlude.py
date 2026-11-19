"""Hide part of a barrel in a class mask, by a measured amount (2026-11-19, the occlusion scorecard).

Used only by the occlusion benchmark (``experiments/2026-11-19_det_occl``), in the spirit of ``degrade.py``: a good
mask of ONE unhidden barrel goes in, a scene comes out in which a stated part of that barrel is hidden by a stated
kind of thing, and the detector is scored against the barrel's FULL box. Nothing here is part of the detector or
of the color model.

A scene is an empty 640 x 480 mask with the barrel's own pixels at their own place (so its row, size and distance
are real), then one occluder. ``amount`` is the hidden share of the barrel's box: of its width W for the kinds that
hide from the side, of its height H for ``top``, ``bottom`` and ``barrel_front``.

Things that are not barrel-colored (they ERASE barrel pixels; the thing itself is "other"):

  ``frame``         the barrel is moved sideways until ``amount`` x W is outside the frame (truth = the box cut at the frame).
  ``edge``          a straight upright edge from the left or the right.
  ``slant``         a straight edge leaning by a quarter of W over the barrel's height; ``amount`` is hidden at mid-height.
  ``both``          both sides at once, ``amount`` / 2 from each.
  ``top``           everything above a level line (an overhang).
  ``bottom``        everything below a level line (a low thing in front): at 0.5 half the stripe is gone too.
  ``post``          an upright post ``amount`` x W wide across the middle.

Barrels (a real barrel's pixels PASTED in front; nearer = lower in the picture and larger, by the camera model;
``same`` = same body color as the hidden barrel, ``other`` = the other body color):

  ``barrel_side``   beside it and a little nearer (its bottom 0.1 H lower): the two stripes are at about the same rows.
  ``barrel_low``    beside it and clearly nearer (its bottom 0.4 H lower): its upper body is where the hidden barrel's
                    stripe is, so with ``other`` the back stripe meets a front body of its own color.
  ``barrel_front``  straight in front: its top row hides the lower ``amount`` of the back barrel's height.

Barrel-colored things that are not barrels (PASTED; a plain block of one color, no stripe, a barrel wide, standing a
little nearer: rows from 0.15 H below the barrel's top to 0.15 H below its bottom):

  ``block``         from the left or the right; ``same`` = the hidden barrel's body color, ``other`` = its stripe color.

Limits, stated plainly: this erases or pastes MASK pixels. A real occluder also throws a shadow on the barrel,
reflects in a glossy table, bleeds its color into the mixed pixels at the seam, and changes the camera's exposure;
none of that is here. A pasted barrel is a scaled copy of a real barrel's pixels, opaque inside its outline.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from . import geometry as geo
from .io import BLUE, ORANGE

FRAME_H, FRAME_W = 480, 640
AMOUNTS = (0.25, 0.5, 0.75)
ERASERS = ("frame", "edge", "slant", "both", "top", "bottom", "post")
BARRELS = ("barrel_side", "barrel_low", "barrel_front")
BLOCKS = ("block",)
KINDS = ERASERS + BARRELS + BLOCKS
SIDED = ("frame", "edge", "slant", "barrel_side", "barrel_low", "block")     # kinds that come from the left ("L") or the right ("R")
COLORED = BARRELS + BLOCKS                                                    # kinds with a "same" / "other" color
SLANT_LEAN = 0.25          # a slanted edge leans by this x W from the barrel's top row to its bottom row
SIDE_LOWER = 0.1           # barrel_side: the front barrel's bottom is this x H below the hidden barrel's
LOW_LOWER = 0.4            # barrel_low: ... this x H below
BLOCK_SHIFT = 0.15         # block: its top and bottom are this x H below the barrel's top and bottom
FRONT_MAX_ROW = 2 * FRAME_H  # barrel_front: the front barrel's bottom may be this far below the frame's top, not further


@dataclass(frozen=True)
class Source:
    """One unhidden barrel cut out of a mask: ``crop`` holds the mask values (0 / ORANGE / BLUE) of the frame from
    the pixel ``origin`` on; ``bbox`` is its hand-drawn box (half-open)."""
    stem: str
    color: int
    bbox: tuple[int, int, int, int]
    crop: np.ndarray
    origin: tuple[int, int]                      # (x, y) of the crop's top-left pixel in the frame
    pool: str = ""

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]


@dataclass
class Scene:
    mask: np.ndarray                                             # the class mask the detector gets
    target: tuple[int, tuple[int, int, int, int]]                # (color, FULL box) of the hidden barrel: the truth
    fronts: list = field(default_factory=list)                   # [(color, box)] of barrels pasted in front (also true barrels)
    clutter: list = field(default_factory=list)                  # [(color, box)] of pasted blocks (NOT barrels)
    hidden: float = 0.0                                          # share of the target's own pixels that no longer show


def cut_source(mask: np.ndarray, bbox, color: int, other_boxes=(), stem: str = "", pool: str = "", pad: int = 3) -> Source:
    """The barrel inside ``bbox``: the mask's barrel pixels in the box grown by ``pad`` px (a hand-drawn box may sit a
    pixel or two inside the paint), minus every pixel that lies in another barrel's box and outside this one."""
    h, w = mask.shape
    x0, y0, x1, y1 = (int(v) for v in bbox)
    cx0, cy0, cx1, cy1 = max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)
    crop = mask[cy0:cy1, cx0:cx1].copy()
    crop[~np.isin(crop, (ORANGE, BLUE))] = 0
    own = np.zeros(crop.shape, bool)
    own[y0 - cy0:y1 - cy0, x0 - cx0:x1 - cx0] = True
    for ox0, oy0, ox1, oy1 in other_boxes:
        theirs = np.zeros(crop.shape, bool)
        theirs[max(0, oy0 - cy0):max(0, oy1 - cy0), max(0, ox0 - cx0):max(0, ox1 - cx0)] = True
        crop[theirs & ~own] = 0
    return Source(stem, color, (x0, y0, x1, y1), crop, (cx0, cy0), pool)


def swap_colors(crop: np.ndarray) -> np.ndarray:
    """The same barrel with the other body color (orange <-> blue everywhere)."""
    out = crop.copy()
    out[crop == ORANGE] = BLUE
    out[crop == BLUE] = ORANGE
    return out


def outline(crop: np.ndarray) -> np.ndarray:
    """The filled outline of a barrel's pixels (their convex hull): what a pasted barrel hides, holes included."""
    pts = cv2.findNonZero((crop > 0).astype(np.uint8))
    out = np.zeros(crop.shape, np.uint8)
    if pts is not None:
        cv2.fillConvexPoly(out, cv2.convexHull(pts), 1)
    return out.astype(bool) | (crop > 0)


def _place(mask: np.ndarray, crop: np.ndarray, x: int, y: int, opaque: bool) -> np.ndarray:
    """Put ``crop`` on ``mask`` with its top-left pixel at (x, y), clipped to the frame. ``opaque``: everything inside
    the crop's outline is replaced (a thing in front); else only the crop's barrel pixels are written. Returns the
    pixels of the frame it replaced, as a bool image."""
    h, w = mask.shape
    ch, cw = crop.shape
    covered = np.zeros(mask.shape, bool)
    ax0, ay0, ax1, ay1 = max(0, x), max(0, y), min(w, x + cw), min(h, y + ch)
    if ax1 <= ax0 or ay1 <= ay0:
        return covered
    part = crop[ay0 - y:ay1 - y, ax0 - x:ax1 - x]
    sel = outline(crop)[ay0 - y:ay1 - y, ax0 - x:ax1 - x] if opaque else part > 0
    mask[ay0:ay1, ax0:ax1][sel] = part[sel]
    covered[ay0:ay1, ax0:ax1] = sel
    return covered


def _clip(box) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    return max(0, int(x0)), max(0, int(y0)), min(FRAME_W, int(x1)), min(FRAME_H, int(y1))


def front_scale(cam: geo.CameraModel, bottom_row: float, front_bottom_row: float) -> float:
    """How much larger a barrel is whose bottom edge is at ``front_bottom_row`` than one whose bottom is at
    ``bottom_row`` (the camera model's width at the two rows; a ratio, so the model's own offset cancels)."""
    return cam.expected_barrel_width_px(bottom_row=front_bottom_row) / cam.expected_barrel_width_px(bottom_row=bottom_row)


def _front_for_top(cam: geo.CameraModel, src: Source, top_row: float) -> float:
    """The bottom row of a front barrel whose top is at ``top_row``: the first row b at or below the hidden barrel's
    bottom with b - (the scaled height at b) >= top_row, searched in quarter-pixel steps down to ``FRONT_MAX_ROW``.
    ValueError when there is none: the hidden barrel is so near that nothing fits between it and the camera."""
    y1, H = src.bbox[3], src.height
    b = float(y1)
    while b <= FRONT_MAX_ROW:
        if b - H * front_scale(cam, y1, b) >= top_row:
            return b
        b += 0.25
    raise ValueError("no room for a barrel in front of this one")


def _paste_barrel(mask: np.ndarray, front: Source, color: int, x_edge: float, toward: str, bottom: float, scale: float):
    """Paste ``front`` scaled by ``scale`` relative to ITS box, recolored to body ``color``, with its box's bottom at
    row ``bottom`` and its box's ``toward`` edge ("L": right edge, "R": left edge, "C": centre) at column ``x_edge``.
    Returns (the pasted barrel's box clipped to the frame, the pixels it covers)."""
    crop = front.crop if front.color == color else swap_colors(front.crop)
    ch, cw = crop.shape
    nw, nh = max(2, int(round(cw * scale))), max(2, int(round(ch * scale)))
    big = cv2.resize(crop, (nw, nh), interpolation=cv2.INTER_NEAREST)
    bx0, by0, bx1, by1 = front.bbox
    ox, oy = front.origin
    W, H = (bx1 - bx0) * scale, (by1 - by0) * scale
    box_x0 = x_edge - W if toward == "L" else (x_edge if toward == "R" else x_edge - W / 2)
    box = (int(round(box_x0)), int(round(bottom - H)), int(round(box_x0 + W)), int(round(bottom)))
    covered = _place(mask, big, int(round(box_x0 - (bx0 - ox) * scale)), int(round(bottom - H - (by0 - oy) * scale)), opaque=True)
    return _clip(box), covered


def make_scene(src: Source, kind: str, amount: float, side: str = "L", color: str = "other", front: Source | None = None,
               cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, lean: int = 1) -> Scene:
    """The scene for one source barrel: ``kind`` hides ``amount`` of it (see the module text). ``side`` ("L" / "R") for
    the kinds in ``SIDED``; ``color`` ("same" / "other") and ``front`` (the barrel pasted, for the barrel kinds) for
    those in ``COLORED``; ``lean`` (+1 / -1) = which way a slanted edge leans. ``amount`` 0 = the barrel alone.
    A pure function of its arguments."""
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}, got {kind!r}")
    if not 0 <= amount < 1:
        raise ValueError("amount must be in [0, 1)")
    if side not in ("L", "R") or color not in ("same", "other"):
        raise ValueError("side is 'L' or 'R'; color is 'same' or 'other'")
    x0, y0, x1, y1 = src.bbox
    W, H = x1 - x0, y1 - y0
    ox, oy = src.origin
    mask = np.zeros((FRAME_H, FRAME_W), np.uint8)
    n_own = int((src.crop > 0).sum())
    if kind == "frame" and amount > 0:
        shift = (-(x0 + int(round(amount * W)))) if side == "L" else (FRAME_W - x1 + int(round(amount * W)))
        _place(mask, src.crop, ox + shift, oy, opaque=False)
        sc = Scene(mask, (src.color, _clip((x0 + shift, y0, x1 + shift, y1))))
        sc.hidden = 1.0 - int((mask > 0).sum()) / max(1, n_own)
        return sc
    _place(mask, src.crop, ox, oy, opaque=False)
    before = mask > 0
    sc = Scene(mask, (src.color, (x0, y0, x1, y1)))
    if amount == 0:
        return sc
    cut = int(round(amount * W))
    rows, cols = np.arange(FRAME_H)[:, None], np.arange(FRAME_W)[None, :]
    covered = np.zeros(mask.shape, bool)                                         # what a pasted thing covers
    if kind == "edge":
        if side == "L":
            mask[:, :x0 + cut] = 0
        else:
            mask[:, x1 - cut:] = 0
    elif kind == "slant":
        off = lean * SLANT_LEAN * W * (rows - (y0 + y1) / 2) / H                 # the edge's column moves with the row
        hide = (cols < x0 + cut + off) if side == "L" else (cols >= x1 - cut + off)
        mask[hide] = 0
    elif kind == "both":
        half = int(round(amount * W / 2))
        mask[:, :x0 + half] = 0
        mask[:, x1 - half:] = 0
    elif kind == "top":
        mask[:y0 + int(round(amount * H))] = 0
    elif kind == "bottom":
        mask[y1 - int(round(amount * H)):] = 0
    elif kind == "post":
        a = int(round((x0 + x1) / 2 - cut / 2))
        mask[:, a:a + cut] = 0
    elif kind in BARRELS:
        if front is None:
            raise ValueError(f"{kind} needs a front barrel")
        fcolor = src.color if color == "same" else (BLUE if src.color == ORANGE else ORANGE)
        if kind == "barrel_front":
            bottom = _front_for_top(cam, src, y1 - amount * H)
            x_edge, toward = (x0 + x1) / 2, "C"
        else:
            bottom = y1 + (SIDE_LOWER if kind == "barrel_side" else LOW_LOWER) * H
            x_edge, toward = (x0 + cut, "L") if side == "L" else (x1 - cut, "R")
        scale = front_scale(cam, y1, bottom) * W / front.width                   # the front barrel's box width in this scene / in its own frame
        box, covered = _paste_barrel(mask, front, fcolor, x_edge, toward, bottom, scale)
        sc.fronts.append((fcolor, box))
    elif kind == "block":
        bcolor = src.color if color == "same" else (BLUE if src.color == ORANGE else ORANGE)
        dy = int(round(BLOCK_SHIFT * H))
        bx0, bx1 = (x0 + cut - W, x0 + cut) if side == "L" else (x1 - cut, x1 - cut + W)
        box = _clip((bx0, y0 + dy, bx1, y1 + dy))
        mask[box[1]:box[3], box[0]:box[2]] = bcolor
        covered[box[1]:box[3], box[0]:box[2]] = True
        sc.clutter.append((bcolor, box))
    # the share of the target's own pixels no longer showing: erased, or covered by a pasted thing
    left = before & ~covered & (mask > 0)
    sc.hidden = 1.0 - int(left.sum()) / max(1, int(before.sum()))
    return sc
