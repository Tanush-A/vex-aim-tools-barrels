"""Per-image non-barrel priors (docs/PROBLEM.md, "Table prior" / "Background prior").

A *band* is a set of image rows known to be non-barrel (the bottom rows = table, the rows
above the horizon = wall/background). ``band_stats`` summarises the band's color robustly
(per-channel median and MAD) and ``reject_like`` flags pixels anywhere in the image whose
color is within ``k`` robust scales of that band color — "this pixel looks like the table".

No image correction happens here: the priors scale *distances* to a reference color; pixel
values are never changed.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

MAD_TO_SIGMA = 1.4826   # MAD -> std for a normal distribution


@dataclass(frozen=True)
class BandStats:
    median: np.ndarray    # (C,) band color
    scale: np.ndarray     # (C,) = max(1.4826 * MAD, scale_floor)
    n_used: int           # pixels that went into the fit
    frac_used: float      # n_used / pixels in the band (guard diagnostic)
    enabled: bool         # False when the guard tripped (too few usable pixels)

    def to_dict(self) -> dict:
        return {"median": [float(x) for x in self.median], "scale": [float(x) for x in self.scale],
                "n_used": int(self.n_used), "frac_used": float(self.frac_used), "enabled": bool(self.enabled)}


def band_stats(pixels: np.ndarray, rows: slice, fit_mask: np.ndarray | None = None,
               scale_floor: float = 4.0, min_frac: float = 0.3, min_px: int = 50) -> BandStats:
    """Robust per-channel statistics of ``pixels[rows]`` (HxWxC array, any color space).

    fit_mask: optional HxW bool; only band pixels where it is True are used (e.g. low-saturation
        pixels, so a barrel intruding into the band does not poison the statistics).
    The prior is disabled (``enabled=False``) when fewer than ``min_frac`` of the band pixels (or
    fewer than ``min_px``) are usable — then ``reject_like`` rejects nothing.
    """
    band = pixels[rows]
    px = band.reshape(-1, band.shape[-1])
    n_total = len(px)
    if fit_mask is not None:
        px = px[fit_mask[rows].reshape(-1)]
    n_used = len(px)
    frac = n_used / n_total if n_total else 0.0
    c = band.shape[-1]
    if n_used < min_px or frac < min_frac:
        return BandStats(np.zeros(c, np.float32), np.full(c, scale_floor, np.float32), n_used, frac, False)
    med = np.median(px, axis=0)
    mad = np.median(np.abs(px - med), axis=0)
    scale = np.maximum(MAD_TO_SIGMA * mad, scale_floor)
    return BandStats(med.astype(np.float32), scale.astype(np.float32), n_used, frac, True)


def reject_like(pixels: np.ndarray, stats: BandStats, k: float) -> np.ndarray:
    """HxW bool: True where every channel is within ``k`` scales of the band median
    (a scaled Chebyshev / axis-aligned robust box around the band color)."""
    if not stats.enabled:
        return np.zeros(pixels.shape[:2], bool)
    d = np.abs(pixels.astype(np.float32) - stats.median) / stats.scale
    return d.max(axis=-1) <= k
