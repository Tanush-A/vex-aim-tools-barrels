"""The photo cues, measured (development copy; the detector's copy is ``detector.cut_by_photo``). No rule here.

Idea 1, the cut line: a thing standing in front of a barrel and hiding its side has a straight, near-vertical edge in
the photo that runs on ABOVE the barrel's top (the thing is taller) and/or BELOW its bottom (it stands nearer, so its
foot is lower in the picture). A barrel's own side ends at its lid and its base. So: in a band of rows above the
barrel and a band below it, look for a strong horizontal step near the seen end, row by row; fit a straight line per
band; ask whether it runs through most of the band, whether it meets the seen end at the stripe's row, and whether the
barrel's own pixels stay on their side of it (a thing in front hides everything beyond its edge; an edge BEHIND the
barrel is crossed by the barrel's bulge).

Idea 2, the photo beside the cut: is the strip just outside the seen end (at the barrel's middle rows) the same as the
strip further out (one W away), or a distinct thing next to the barrel?
"""
from __future__ import annotations

import cv2
import numpy as np

BARREL = (1, 2)


def gradient(photo: np.ndarray) -> np.ndarray:
    """|I(x + 2) - I(x - 2)| summed over R, G, B, of the photo smoothed 3 x 3; float32 H x W (0 in the two columns at
    each side of the frame)."""
    I = cv2.GaussianBlur(photo.astype(np.float32), (3, 3), 0)
    g = np.zeros(photo.shape[:2], np.float32)
    g[:, 2:-2] = np.abs(I[:, 4:] - I[:, :-4]).sum(axis=2)
    return g


def _fit(y: np.ndarray, x: np.ndarray, tol: float):
    """Line x = a + b y through the points, refitted twice on the points within tol px; (a, b, inlier mask)."""
    keep = np.ones(len(y), bool)
    a, b = float(np.median(x)), 0.0
    for _ in range(3):
        if keep.sum() >= 3 and np.ptp(y[keep]) > 0:
            b, a = (float(v) for v in np.polyfit(y[keep], x[keep], 1))
        elif keep.any():
            a, b = float(np.median(x[keep])), 0.0
        keep = np.abs(x - (a + b * y)) <= tol
    return a, b, keep


def band_lines(grad: np.ndarray, mask: np.ndarray, side: str, x_end: int, top: int, bottom: int, W: float, H: float, row: float,
               band: float = 0.5, gap: float = 0.1, reach_in: float = 0.3, reach_out: float = 0.3, strength: float = 60.0,
               tol_px: float = 1.5) -> dict:
    """Idea 1, per band (above the barrel, below it). ``x_end`` = the seen end (first seen column on the left, one past
    the last on the right); ``top``, ``bottom`` = the barrel's rows; ``row`` = the stripe's middle row.

    Band rows: above = [top - band x H, top - gap x H), below = [bottom + gap x H, bottom + band x H), in the frame. In
    each band row, the strongest step (``grad``) from reach_in x W inside the seen end to reach_out x W outside it. Rows
    whose step is at least ``strength`` are fitted with a line (trimmed at tol_px). Per band: ``frac`` = the share of the
    band's rows on the line; ``lean`` (px per row); ``off`` = how far OUTSIDE the seen end the line is at the stripe's
    row (negative: inside); ``cross`` = the share of the barrel's rows in which barrel color lies more than 2 px outside
    the line (within 0.3 W of it)."""
    h, w = grad.shape
    o = -1 if side == "L" else 1                                         # outward
    lo = x_end - o * int(round(reach_in * W))
    hi = x_end + o * int(round(reach_out * W))
    c0, c1 = max(2, min(lo, hi)), min(w - 2, max(lo, hi) + 1)
    g0, b0 = max(1, int(round(gap * H))), max(4, int(round(band * H)))
    bands = {"up": np.arange(max(0, top - b0), max(0, top - g0)), "dn": np.arange(min(h, bottom + g0), min(h, bottom + b0))}
    out = {}
    for k, rows in bands.items():
        n = int(rows.size)
        out[f"{k}_n"] = n
        out[f"{k}_frac"], out[f"{k}_lean"], out[f"{k}_off"], out[f"{k}_cross"], out[f"{k}_s"] = 0.0, None, None, None, None
        if n < 4 or c1 - c0 < 3:
            continue
        win = grad[rows, c0:c1]
        j = win.argmax(axis=1)
        s = win[np.arange(n), j]
        out[f"{k}_s"] = float(np.median(s))
        ok = s >= strength
        if ok.sum() < 3:
            continue
        y, x = (rows[ok] - row).astype(float), (c0 + j[ok]).astype(float)
        a, b, keep = _fit(y, x, tol_px)
        out[f"{k}_frac"] = float(keep.sum() / n)
        out[f"{k}_lean"] = b
        out[f"{k}_off"] = float(o * (a - x_end))
        # barrel color beyond the line (cross), and how far inside the line the barrel's outermost pixel is (touch)
        crossed, counted, gaps = 0, 0, []
        for yy in range(max(0, top), min(h, bottom)):
            xl = a + b * (yy - row)
            if o > 0:
                seg = mask[yy, int(np.ceil(xl + 2)):min(w, int(xl + 0.3 * W) + 1)]
                inner = np.isin(mask[yy, max(0, int(xl - 0.5 * W)):max(0, int(np.ceil(xl + 2)))], BARREL)
                if inner.any():
                    gaps.append(xl - (max(0, int(xl - 0.5 * W)) + np.flatnonzero(inner)[-1] + 1))
            else:
                seg = mask[yy, max(0, int(np.ceil(xl - 0.3 * W))):max(0, int(np.floor(xl - 2)))]
                s0 = max(0, int(np.floor(xl - 2)))
                inner = np.isin(mask[yy, s0:min(w, int(xl + 0.5 * W) + 1)], BARREL)
                if inner.any():
                    gaps.append((s0 + np.flatnonzero(inner)[0]) - xl)
            counted += 1
            crossed += bool(np.isin(seg, BARREL).any())
        out[f"{k}_cross"] = crossed / max(1, counted)
        out[f"{k}_touch"] = float(np.median(gaps)) if gaps else None
    return out


def beside(photo: np.ndarray, side: str, x_end: int, y0: int, y1: int, W: float, near: float = 0.04, width: float = 0.12,
           far: float = 1.0) -> dict:
    """Idea 2. The mean color of the strip just outside the seen end (from near x W out, width x W wide, at least 2 px)
    and of a strip of the same width far x W further out, over the rows y0..y1; and the difference (sum of |dR|, |dG|, |dB|)."""
    h, w = photo.shape[:2]
    sign = -1 if side == "L" else 1
    ww = max(2, int(round(width * W)))

    def strip(off: float):
        a = x_end + sign * int(round(off * W)) + (0 if side == "R" else -1)
        c0, c1 = (a, a + ww) if side == "R" else (a - ww + 1, a + 1)
        c0, c1 = max(0, c0), min(w, c1)
        if c1 - c0 < 1:
            return None
        return photo[y0:y1, c0:c1].reshape(-1, 3).astype(float).mean(axis=0)

    a, b = strip(near), strip(near + far)
    return {"near": None if a is None else a.tolist(), "far": None if b is None else b.tolist(),
            "diff": None if a is None or b is None else float(np.abs(a - b).sum())}
