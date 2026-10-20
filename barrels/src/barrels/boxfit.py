"""Axis-aligned color boxes: fitting from labeled pixels, membership, and shape diagnostics
(box fullness = 3-D "extent", PCA elongation). Dimension-agnostic: works for RGB (3) or a
chroma plane (2).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Box:
    lo: tuple[float, ...]
    hi: tuple[float, ...]   # inclusive

    @property
    def dims(self) -> int:
        return len(self.lo)

    def volume(self) -> float:
        return float(np.prod(np.array(self.hi) - np.array(self.lo) + 1))

    def shrink(self, frac: float) -> "Box":
        """Shrink every side by ``frac`` of its length (toward the center)."""
        lo, hi = np.array(self.lo, float), np.array(self.hi, float)
        d = (hi - lo) * frac / 2
        return Box(tuple((lo + d).tolist()), tuple((hi - d).tolist()))

    def clip_to(self, outer: "Box") -> "Box":
        return Box(tuple(np.maximum(self.lo, outer.lo).tolist()), tuple(np.minimum(self.hi, outer.hi).tolist()))

    def to_dict(self) -> dict:
        return {"lo": [float(x) for x in self.lo], "hi": [float(x) for x in self.hi]}

    @classmethod
    def from_dict(cls, d: dict) -> "Box":
        return cls(tuple(d["lo"]), tuple(d["hi"]))


def sample_class_pixels(pixels: np.ndarray, mask: np.ndarray, cls: int, keep: np.ndarray | None = None,
                        max_px: int | None = None, rng: np.random.Generator | None = None) -> np.ndarray:
    """(n, C) pixels of ``pixels`` (HxWxC) where ``mask == cls`` (and ``keep`` if given),
    randomly capped at ``max_px`` so no single image dominates a pooled fit."""
    sel = mask == cls
    if keep is not None:
        sel &= keep
    px = pixels[sel]
    if max_px is not None and len(px) > max_px:
        rng = rng or np.random.default_rng(0)
        px = px[rng.choice(len(px), max_px, replace=False)]
    return px


def fit_box(pixels: np.ndarray, p_lo: float = 1.0, p_hi: float = 99.0) -> Box:
    """Per-channel percentile bounds of an (n, C) pixel array."""
    if len(pixels) == 0:
        raise ValueError("cannot fit a box to zero pixels")
    lo = np.floor(np.percentile(pixels, p_lo, axis=0))
    hi = np.ceil(np.percentile(pixels, p_hi, axis=0))
    return Box(tuple(lo.tolist()), tuple(hi.tolist()))


def in_box(pixels: np.ndarray, box: Box) -> np.ndarray:
    """Bool array over the leading dims: all channels within [lo, hi]."""
    lo = np.array(box.lo); hi = np.array(box.hi)
    return ((pixels >= lo) & (pixels <= hi)).all(axis=-1)


def fullness(pixels: np.ndarray, box: Box, voxel: float = 8.0) -> float:
    """Fraction of the box's voxels (side ``voxel``) that contain at least one pixel — the 3-D
    analogue of regionprops "extent". Pixels outside the box are ignored."""
    lo = np.array(box.lo, float); hi = np.array(box.hi, float)
    inside = in_box(pixels, box)
    if not inside.any():
        return 0.0
    q = np.floor((pixels[inside] - lo) / voxel).astype(np.int64)
    n_per_axis = np.floor((hi - lo) / voxel).astype(np.int64) + 1
    q = np.minimum(q, n_per_axis - 1)
    occupied = len(np.unique(np.ravel_multi_index(q.T, n_per_axis)))
    return occupied / float(np.prod(n_per_axis))


def pca(pixels: np.ndarray) -> dict:
    """Eigen-decomposition of the pixel covariance. Returns eigvals (desc), var_fraction,
    linearity = (l1-l2)/l1, axis1 (unit), cos_to_gray = |axis1 . (1,..,1)/sqrt(C)|."""
    x = pixels.astype(np.float64)
    cov = np.cov(x.T)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    vals = np.maximum(vals, 0)
    total = vals.sum() or 1.0
    axis1 = vecs[:, 0]
    gray = np.ones(len(axis1)) / np.sqrt(len(axis1))
    return {
        "eigvals": [float(v) for v in vals],
        "var_fraction": [float(v / total) for v in vals],
        "linearity": float((vals[0] - vals[1]) / vals[0]) if vals[0] > 0 else 0.0,
        "axis1": [float(v) for v in axis1],
        "cos_to_gray": float(abs(axis1 @ gray)),
    }


def box_overlap(a: Box, b: Box) -> Box | None:
    lo = np.maximum(a.lo, b.lo); hi = np.minimum(a.hi, b.hi)
    if (hi < lo).any():
        return None
    return Box(tuple(lo.tolist()), tuple(hi.tolist()))
