"""The tape measure that lies in the ruler frames, as a check that needs no hand-drawn box.

The tape lies on the table beside the barrel, running away from the robot. Two things can be read off it:

1. Its two long edges are parallel on the table, so in the image they meet at a point on the horizon row.
2. Its centimetre lines are 10 mm apart on the table. A camera model turns each line's row into a distance;
   a right model gives 10 mm between neighbours.

Both readings have weak points, stated in the output: the tape is not perfectly flat (the lines bow by 1 to 2 px
across its width), its right edge carries the tick marks, and it lies 35 to 70 px right of the centre column,
so a small roll of the camera shifts its rows by about a pixel. It is a cross-check, not part of the fit.

Frames 09 to 12 only: there the barrel is far and does not cover the tape (the tape did not move between them).
"""
from __future__ import annotations

import math

import cv2
import numpy as np

FRAMES = (9, 10, 11, 12)
LEFT_PRIOR = (333.5 - 150 * 0.207, 0.207)       # x = a + b * row, read off calib_12 by eye; refined below
RIGHT_PRIOR = (352.0 - 150 * 0.512, 0.512)
LINE_GUESS = (402.0, 357.0, 322.5, 296.0, 275.0, 257.0, 243.0, 230.4)   # rows of the cm lines 142, 141, ... at the tape's left edge
LINE_HALF = (4.0, 3.5, 3.0, 3.0, 2.5, 2.5, 2.0, 2.0)                    # search window, px (the lines get closer together)
FIRST_READING = 142


def gradient_edges(B: np.ndarray, lines, rows, win: int) -> np.ndarray:
    """Per row, the sub-pixel column of the steepest dark-to-white step near each prior line (left, right)."""
    (a, b), (c, d) = lines
    G = np.gradient(B, axis=1)
    out = []
    for r in rows:
        res = []
        for x0, sign in ((a + b * r, +1), (c + d * r, -1)):
            lo = int(round(x0)) - win
            g = sign * G[r, lo:lo + 2 * win + 1]
            k = int(np.argmax(g))
            if 0 < k < len(g) - 1 and g[k] > 8:
                den = g[k - 1] - 2 * g[k] + g[k + 1]
                res.append(lo + k + (0.5 * (g[k - 1] - g[k + 1]) / den if den else 0.0))
            else:
                res.append(np.nan)
        out.append(res)
    return np.array(out)


def robust_line(r: np.ndarray, x: np.ndarray, n_iter: int = 5, k: float = 2.5):
    """x = a + b r by least squares, dropping points beyond k sigma. Returns ((a, b), rms)."""
    ok = np.isfinite(x)
    for _ in range(n_iter):
        p = np.polyfit(r[ok], x[ok], 1)
        res = x - np.polyval(p, r)
        ok = np.isfinite(x) & (np.abs(res) < max(k * np.nanstd(res[ok]), 0.3))
    return (float(p[1]), float(p[0])), float(np.sqrt(np.mean(res[ok] ** 2)))


def tape_edges(bgr: np.ndarray, rows: np.ndarray):
    """The tape's left and right edge as lines x = a + b row, from the blue channel (white tape on orange wood)."""
    B = cv2.GaussianBlur(bgr[:, :, 0].astype(float), (0, 0), 0.8)
    lines = (LEFT_PRIOR, RIGHT_PRIOR)
    rms = (math.nan, math.nan)
    for it in range(3):
        E = gradient_edges(B, lines, rows, win=7 if it == 0 else 4)
        (ll, rl), (lr, rr) = robust_line(rows, E[:, 0]), robust_line(rows, E[:, 1])
        lines, rms = (ll, lr), (rl, rr)
    return lines, rms


def vanishing_row(lines) -> tuple[float, float]:
    """(row, column) where the two edge lines meet."""
    (a, b), (c, d) = lines
    r = (a - c) / (d - b)
    return r, a + b * r


def cm_line_rows(gray: np.ndarray, lines, t0: float = 0.03, t1: float = 0.13) -> list[dict]:
    """Row of each centimetre line in the tape's left margin (left of the printed numbers, where the tape's
    edge rests on the table): per column the sub-pixel darkest row of the vertically smoothed profile, then the
    median over the margin's columns."""
    (a, b), (c, d) = lines
    Gs = cv2.sepFilter2D(gray, -1, np.array([[1.0]]), cv2.getGaussianKernel(9, 1.0))
    out = []
    for i, (guess, half) in enumerate(zip(LINE_GUESS, LINE_HALF)):
        xl, xr = a + b * guess, c + d * guess
        rows, cols, depths = [], [], []
        for x in range(int(math.ceil(xl + t0 * (xr - xl))), int(xl + t1 * (xr - xl)) + 1):
            lo = int(round(guess - half))
            p = Gs[lo:int(round(guess + half)) + 1, x]
            k = int(np.argmin(p))
            if 0 < k < len(p) - 1:
                den = p[k - 1] - 2 * p[k] + p[k + 1]
                rows.append(lo + k + (0.5 * (p[k - 1] - p[k + 1]) / den if den > 0 else 0.0))
                cols.append(x); depths.append(0.5 * (p[0] + p[-1]) - p[k])
        if rows:
            out.append({"reading_cm": FIRST_READING - i, "row": float(np.median(rows)), "col": float(np.mean(cols)),
                        "depth": float(np.median(depths)), "n_cols": len(rows)})
    return out


def spacing_mm(cam, rows: list[float]) -> list[float]:
    """Distance between neighbouring lines as this camera reads their rows (10 mm if the camera is right)."""
    d = [cam.row_to_ground_distance(r) for r in rows]
    return [d[i + 1] - d[i] for i in range(len(d) - 1)]


def horizon_scan(rows: np.ndarray, horizons: np.ndarray) -> list[tuple[float, float]]:
    """For a ground point, 1 / (row - horizon) is a straight line in distance, whatever f, tilt and camera
    height are. For each trial horizon: fit that line through the equally spaced lines, return the rms misfit
    in px. The horizon the tape prefers is where it is smallest."""
    k = np.arange(len(rows), dtype=float)
    out = []
    for hz in horizons:
        y = 1.0 / (rows - hz)
        p = np.polyfit(k, y, 1)
        back = hz + 1.0 / np.polyval(p, k)
        out.append((float(hz), float(np.sqrt(np.mean((back - rows) ** 2)))))
    return out


def analyse(raw_path, cams: dict) -> dict:
    """raw_path(k) -> image path of ruler frame k. Returns everything the report prints."""
    imgs = [cv2.imread(str(raw_path(k))) for k in FRAMES]
    vp = {}
    for name, rows in (("rows 250 to 477 (near half)", np.arange(250, 478)), ("rows 170 to 477 (all)", np.arange(170, 478)),
                       ("rows 170 to 329 (far half)", np.arange(170, 330))):
        per = []
        for im in imgs:
            lines, rms = tape_edges(im, rows)
            per.append((vanishing_row(lines)[0], rms[0], rms[1]))
        vp[name] = {"rows": [round(p[0], 1) for p in per], "left_rms": round(float(np.mean([p[1] for p in per])), 2),
                    "right_rms": round(float(np.mean([p[2] for p in per])), 2)}
    edge_lines = np.mean([np.array(tape_edges(im, np.arange(250, 478))[0]) for im in imgs], axis=0)
    gray = np.mean([cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32) for im in imgs], axis=0)
    lines = cm_line_rows(gray, (tuple(edge_lines[0]), tuple(edge_lines[1])))
    rows = np.array([ln["row"] for ln in lines])
    cols = np.array([ln["col"] for ln in lines])
    spacing = {name: spacing_mm(cam, list(rows)) for name, cam in cams.items()}
    scans = {}
    for roll_deg in (-2.0, 0.0, 2.0):
        r_c = rows - math.tan(math.radians(roll_deg)) * (cols - 320.0)     # the rows the centre column would show
        scan = horizon_scan(r_c, np.arange(66.0, 100.01, 0.5))
        best = min(scan, key=lambda t: t[1])
        ok = [hz for hz, rms in scan if rms <= max(2 * best[1], 0.3)]
        scans[roll_deg] = {"best": best, "range": (min(ok), max(ok)), "at": {hz: rms for hz, rms in scan if hz in (76.5, 80.0, 84.0, 88.0, 91.0, 95.0)}}
    return {"frames": list(FRAMES), "vanishing": vp, "lines": lines, "spacing": spacing, "horizon_scan": scans}
