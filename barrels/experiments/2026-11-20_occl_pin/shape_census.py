#!/usr/bin/env python3
"""A census before the fix (no acceptance number comes from here): what in the seen part of a cut barrel says WHERE
the barrel is, sideways?

The distance is known from the stripe's row, hence the barrel's width W and height H. A barrel cut at the side shows
part of its outline. Seen from the robot's camera (43 mm up, looking 22 degrees down) the outline has a shape the
camera model predicts for that distance:

  the top       the far rim of the lid (18 mm across = 0.71 W): an arc, highest at the centre column, then a
                shoulder running down to the full width at the stripe's height;
  the stripe    a band around the widest part: an arc, lowest at the centre column, rising to the sides;
  the bottom    the near rim of the base: an arc, lowest at the centre, then a corner running up to the full width.

Part A measures how curved those three lines are on the unhidden source barrels of the occlusion scorecard
(``experiments/2026-11-19_det_occl/run.py``; train frames only), against what the camera model predicts.

Part B cuts each barrel with straight upright edges so that a window of 75, 50 or 25 % of its width shows, and asks
each cue for the barrel's centre column. Error = (estimate - the centre of the hand-drawn box) / the box's width. Cues:

  ``centred``     the middle of what is seen (what the detector does today when no side has a reason);
  ``top apex``    the middle of the columns where the seen top is highest;
  ``top fit``     the predicted top line (lid arc + shoulders) slid sideways to where it fits the seen top best;
  ``stripe fit``  the predicted stripe arc slid to where it fits the stripe's middle line best;
  ``bottom fit``  the predicted bottom line slid to where it fits the seen bottom best;
  ``all fit``     the three together (one sideways position; each line may sit a few rows off).

Part C: when does the outline KNOW? The positions that fit nearly as well as the best one form a range; the census
counts, for several limits, how often that range is narrow, and how wrong the centre is when it is.

Part D: the corners alone (the share of body color in the corner squares of the seen part's end), on a barrel's own
sides against straight-cut and slanted-cut sides.

Part E: the real partly hidden barrels of the HOME and CAMPUS train frames (hand-drawn full boxes): the centre the
outline gives against the centre of the box.

    python barrels/experiments/2026-11-20_occl_pin/shape_census.py
Output: results/2026-11-20_occl_pin/shape_census.md, shape_census.csv (part B and C, one row per scene), corner_census.csv,
real_census.csv; sheets/curves.pkl (ignored by git).
"""
from __future__ import annotations

import csv
import dataclasses
import importlib.util
import pickle
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OCCL = HERE.parent / "2026-11-19_det_occl"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(OCCL))
spec = importlib.util.spec_from_file_location("det_occl_run", OCCL / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
from barrels import detect_types as dtp, detector as det, geometry as geo, io, occlude as oc  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_occl_pin"
CAM = R.CAM
LID = geo.BARREL_END_DIAMETER_MM / geo.BARREL_BULGE_DIAMETER_MM / 2      # half the lid's width in barrel widths: 0.353
CORNER = 0.5 - LID                                                        # how far in the lid ends from the side: 0.147 W
FIND = dataclasses.replace(R.occl_arms.BASE, slice_box=True)              # the finder with the low width floor, so a quarter-barrel piece is seen
# part C: the limits tried, as shares of the barrel. A position "fits" when its cost is within ``near`` x H of the best one's; the
# outline "knows" when the fitting positions span at most ``span`` x W and the best cost is at most ``good`` x H
LIMITS = [(near, span, good) for near in (0.005, 0.01, 0.02) for span in (0.15, 0.3) for good in (0.03, 0.05, 99.0)]
CHOSEN = (0.01, 0.3, 0.05)                                                # the limits the PREREG takes (read off part C): fitting = within 0.01 H of
                                                                          # the best; every fitting position within 0.15 W of their middle; best cost <= 0.05 H


# ---------------------------------------------------------------- the predicted outline

@dataclasses.dataclass(frozen=True)
class Outline:
    """The three lines for a barrel at axis distance d, as rows; u = (column - centre column) / W."""
    W: float
    top_apex: float       # the lid's far rim at the centre column
    top_end: float        # the lid's rim at its two ends (|u| = LID)
    mid: float            # the side at the widest part, mid-height (|u| = 0.5)
    stripe_apex: float    # the stripe's middle at the centre column (the nearest point of the bulge)
    bot_apex: float       # the base's near rim at the centre column
    bot_end: float        # the base's rim at its two ends

    @classmethod
    def at(cls, cam: geo.CameraModel, d: float) -> "Outline":
        r = cam.barrel_rows(d)
        return cls(r.width_px, r.top, cam.point_row(d, geo.BARREL_HEIGHT_MM), cam.point_row(d, geo.BARREL_HEIGHT_MM / 2),
                   r.stripe_center, r.bottom, cam.point_row(d, 0.0))

    @staticmethod
    def _arc(u, half):
        return 1.0 - np.sqrt(np.clip(1.0 - (u / half) ** 2, 0.0, 1.0))      # 0 at the centre, 1 at |u| = half

    def _rim(self, u, apex, end):
        a = np.abs(u)
        inner = apex + (end - apex) * self._arc(u, LID)
        # between the lid's end and the widest part the side is a curve, not a straight line: the barrel's radius falls off with
        # the square of the height above its middle (18 mm at the lid, 25.5 mm at the middle). A straight side was measured
        # first: it predicts the shoulder twice as deep as it is seen (part A)
        t = np.clip((a - LID) / (0.5 - LID), 0.0, 1.0)
        outer = end + (self.mid - end) * (1.0 - np.sqrt(1.0 - t))
        return np.where(a <= LID, inner, outer)

    def top(self, u):
        return self._rim(u, self.top_apex, self.top_end)

    def bottom(self, u):
        return self._rim(u, self.bot_apex, self.bot_end)

    def stripe(self, u):
        return self.stripe_apex + (self.mid - self.stripe_apex) * self._arc(u, 0.5)


# ---------------------------------------------------------------- the seen outline

def seen_lines(mask: np.ndarray, body: int, x0: int, x1: int, y0: int, y1: int, lim_top: int, lim_bot: int, max_gap: int = 3):
    """Per column x0..x1: the top row of the body color joined to the stripe from above, the row after its last pixel
    below, and the stripe's middle row (NaN where the column holds no stripe pixel). ``y0``, ``y1`` = the stripe's rows.
    A column with no body above (below) the stripe has its top (bottom) at the stripe."""
    other = BLUE if body == ORANGE else ORANGE
    h = mask.shape[0]
    n = x1 - x0
    top, bot, st = np.full(n, float(y0)), np.full(n, float(y1)), np.full(n, np.nan)
    for i, x in enumerate(range(x0, x1)):
        col = mask[:, x] == body
        r, gap = y0 - 1, 0
        while r >= max(0, lim_top) and gap <= max_gap:
            if col[r]:
                top[i], gap = r, 0
            else:
                gap += 1
            r -= 1
        r, gap = y1, 0
        while r < min(h, lim_bot) and gap <= max_gap:
            if col[r]:
                bot[i], gap = r + 1, 0
            else:
                gap += 1
            r += 1
        ys = np.flatnonzero(mask[y0:y1, x] == other)
        if len(ys):
            st[i] = y0 + ys.mean() + 0.5
    return top, bot, st


def slide(xs: np.ndarray, lines: list, W: float, lo: float, hi: float, step: float = 0.25):
    """Slide the predicted lines sideways: for every centre column from lo to hi, the mean distance in rows between each
    seen line and the predicted one (after taking out that line's own up-down offset: its median), averaged over the
    lines. ``lines`` = [(seen rows per column, predicted row as a function of u)]. Returns (centres, cost in px)."""
    cands = np.arange(lo, hi + step, step)
    cost = np.zeros(len(cands))
    for j, cx in enumerate(cands):
        u = (xs + 0.5 - cx) / W
        tot, k = 0.0, 0
        for obs, model in lines:
            ok = ~np.isnan(obs)
            if ok.sum() < 2:
                continue
            r = obs[ok] - model(u[ok])
            tot += float(np.mean(np.abs(r - np.median(r)))); k += 1
        cost[j] = tot / k if k else np.nan
    return cands, cost


def fitting(cands, cost, near: float):
    """(lowest, highest) centre whose cost is within ``near`` px of the best; None when nothing could be fit."""
    if np.all(np.isnan(cost)):
        return None
    ok = cands[cost <= np.nanmin(cost) + near]
    return float(ok.min()), float(ok.max())


def best(cands, cost) -> float:
    """The centre with the lowest cost (the middle one when several tie)."""
    if np.all(np.isnan(cost)):
        return np.nan
    ok = cands[cost <= np.nanmin(cost) + 1e-9]
    return float(ok.mean())


def corner_fill(mask: np.ndarray, body: int, end: int, side: str, top: int, bottom: int, c: int) -> tuple[float, float]:
    """The share of body color in the c x c square at the top corner and at the bottom corner of the seen part's end
    (``end`` = its first column for side "L", the column after its last for "R")."""
    xa, xb = (end, end + c) if side == "L" else (end - c, end)
    xa, xb = max(0, xa), min(mask.shape[1], xb)
    t = mask[max(0, top):top + c, xa:xb] == body
    b = mask[bottom - c:min(mask.shape[0], bottom), xa:xb] == body
    return (float(t.mean()) if t.size else np.nan), (float(b.mean()) if b.size else np.nan)


def measure(mask: np.ndarray, color: int, near_col: float | None = None):
    """Everything the census needs from one scene, or None when no stripe piece of the barrel is found. The piece taken is
    the widest of the body color (with ``near_col``: the one whose middle is nearest that column)."""
    stripes = [s for s in det.find_stripes(mask, CAM, FIND) if s.body == color]
    if not stripes:
        return None
    if near_col is None:
        s = max(stripes, key=lambda s: s.bbox[2] - s.bbox[0])
    else:
        s = min(stripes, key=lambda s: abs((s.bbox[0] + s.bbox[2]) / 2 - near_col))
    return measure_stripe(mask, s)


def measure_stripe(mask: np.ndarray, s: det.Stripe):
    """The seen lines and the predicted outline for the stripe piece ``s``; None when its row gives no barrel."""
    color = s.body
    g = det._stripe_geometry(CAM, s.center_row)
    if g is None:
        return None
    d, rows = g
    W, H = rows.width_px, rows.bottom - rows.top
    tol = max(4, 0.15 * H)
    x0, y0, x1, y1 = s.bbox
    top_box, bot_box = max(0, int(round(rows.top))), min(mask.shape[0], int(round(rows.bottom)))
    span = det._body_span(mask, color, x0, x1, top_box, bot_box, y0, y1)
    sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if span else (x0, x1)
    if sx1 - sx0 > 1.2 * W:
        sx0, sx1 = x0, x1
    top, bot, st = seen_lines(mask, color, sx0, sx1, y0, y1, int(rows.top - tol), int(rows.bottom + tol) + 1)
    return {"s": s, "d": d, "rows": rows, "W": W, "H": H, "sx0": sx0, "sx1": sx1, "top": top, "bot": bot, "st": st,
            "xs": np.arange(sx0, sx1, dtype=float), "ol": Outline.at(CAM, d)}


def estimates(m: dict, mask: np.ndarray, color: int) -> dict:
    W, ol, xs = m["W"], m["ol"], m["xs"]
    sx0, sx1 = m["sx0"], m["sx1"]
    lo, hi = sx1 - 0.65 * W, sx0 + 0.65 * W              # every centre a barrel holding the seen part can have, and 0.15 W more
    if hi < lo:
        lo, hi = (sx0 + sx1) / 2 - 0.15 * W, (sx0 + sx1) / 2 + 0.15 * W
    out = {"centred": (sx0 + sx1) / 2}
    hi_top = m["top"] <= m["top"].min() + 0.5
    out["top apex"] = float(xs[hi_top].mean() + 0.5)
    fits = {"top fit": [(m["top"], ol.top)], "stripe fit": [(m["st"], ol.stripe)], "bottom fit": [(m["bot"], ol.bottom)],
            "all fit": [(m["top"], ol.top), (m["st"], ol.stripe), (m["bot"], ol.bottom)]}
    for name, lines in fits.items():
        cands, cost = slide(xs, lines, W, lo, hi)
        out[name] = best(cands, cost)
        if name == "all fit":
            out["curve"] = (cands, cost)
    c = max(2, int(round(CORNER * W)))
    T, B = int(m["top"].min()), int(m["bot"].max())
    out["fill L"] = corner_fill(mask, color, sx0, "L", T, B, c)
    out["fill R"] = corner_fill(mask, color, sx1, "R", T, B, c)
    return out


# ---------------------------------------------------------------- main

def stat(v, digits=3):
    v = np.asarray([x for x in v if x is not None and not (isinstance(x, float) and np.isnan(x))], float)
    if not len(v):
        return "-"
    return f"{np.median(v):+.{digits}f} ({np.percentile(v, 10):+.{digits}f} to {np.percentile(v, 90):+.{digits}f}; n {len(v)})"


def size_class(W: float) -> str:
    return "under 45 px" if W < 45 else ("45 to 70 px" if W < 70 else "over 70 px")


SIZES = ("under 45 px", "45 to 70 px", "over 70 px")
GROUPS = (("hand masks", ("HOME hand masks",)), ("color model", ("HOME color model", "CAMPUS color model")))
WN = ("one side cut", "both sides, equal", "both sides, unequal")
CUES = ("centred", "top apex", "top fit", "stripe fit", "bottom fit", "all fit")


def windows(seen: float):
    """(name, where the seen window starts, in barrel widths from the barrel's left side) for a window ``seen`` wide."""
    hid = 1 - seen
    return [("one side cut", 0.0), ("one side cut", hid), ("both sides, equal", hid / 2), ("both sides, unequal", hid / 4), ("both sides, unequal", 3 * hid / 4)]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    stems = R.train_stems()
    segs = R.segmentations(stems)
    pools, _ = R.build_sources(segs)
    L = ["# Where is a cut barrel, sideways? (a census; no acceptance number)", "",
         "Source barrels: the 50 unhidden train barrels of the occlusion scorecard. W = the barrel width the stripe's row gives. "
         "`hand masks` = the 12 HOME hand masks; `color model` = the same 12 as the color model segments them + the 26 of CAMPUS.", ""]

    # ---- part A: how curved
    rowsA = []
    for pool in R.POOLS:
        for src in pools[pool]:
            m = measure(oc.make_scene(src, "edge", 0.0).mask, src.color)
            if m is None:
                continue
            cx = (src.bbox[0] + src.bbox[2]) / 2
            u = (m["xs"] + 0.5 - cx) / src.width
            ol, W = m["ol"], m["W"]

            def med(line, a, b):
                sel = (np.abs(u) >= a) & (np.abs(u) < b) & ~np.isnan(line)
                return float(np.median(line[sel])) if sel.any() else np.nan
            rowsA.append({"pool": pool, "size": size_class(W), "W": W, "W_true": src.width,
                          "top_rise": (med(m["top"], 0.25, 0.35) - med(m["top"], 0, 0.1)) / W, "top_rise_pred": float(ol.top(0.3) - ol.top(0.05)) / W,
                          "shoulder": (med(m["top"], 0.42, 0.5) - med(m["top"], 0, 0.1)) / W, "shoulder_pred": float(ol.top(0.46) - ol.top(0.05)) / W,
                          "stripe_sag": (med(m["st"], 0, 0.1) - med(m["st"], 0.35, 0.45)) / W, "stripe_sag_pred": float(ol.stripe(0.05) - ol.stripe(0.4)) / W,
                          "base_rise": (med(m["bot"], 0, 0.1) - med(m["bot"], 0.25, 0.35)) / W, "base_rise_pred": float(ol.bottom(0.05) - ol.bottom(0.3)) / W,
                          "base_corner": (med(m["bot"], 0, 0.1) - med(m["bot"], 0.42, 0.5)) / W, "base_corner_pred": float(ol.bottom(0.05) - ol.bottom(0.46)) / W})
    L += ["## A. How curved is the outline of an unhidden barrel?", "",
          "In barrel widths W; median (10th to 90th percentile; n). `seen` is measured on the mask, `model` is what the camera model predicts for the "
          "barrel's distance. *top rise*: how much lower the top edge is at 0.25 to 0.35 W from the centre than at the centre. *shoulder*: the same at "
          "0.42 to 0.5 W (the last 8 % before the side). *stripe sag*: how much lower the stripe's middle is at the centre than at 0.35 to 0.45 W. "
          "*base rise*, *base corner*: how much higher the bottom edge is at 0.25 to 0.35 W / at 0.42 to 0.5 W than at the centre.", ""]
    for gname, gpools in GROUPS:
        L += [f"### {gname}", "", "| barrel width | | top rise | shoulder | stripe sag | base rise | base corner |", "|---|---|---|---|---|---|---|"]
        for size in SIZES:
            rs = [r for r in rowsA if r["pool"] in gpools and r["size"] == size]
            if not rs:
                continue
            L.append(f"| {size} (n {len(rs)}) | seen | " + " | ".join(stat([r[k] for r in rs]) for k in ("top_rise", "shoulder", "stripe_sag", "base_rise", "base_corner")) + " |")
            L.append("| | model | " + " | ".join(f"{np.median([r[k + '_pred'] for r in rs]):+.3f}" for k in ("top_rise", "shoulder", "stripe_sag", "base_rise", "base_corner")) + " |")
        L.append("")

    # ---- part B and C: the centre from each cue, and when the outline knows; part D: corners
    rowsB, rowsD, curves = [], [], []
    for pool in R.POOLS:
        for src in pools[pool]:
            cx_true = (src.bbox[0] + src.bbox[2]) / 2
            x0, Wt = src.bbox[0], src.width
            whole = oc.make_scene(src, "edge", 0.0).mask
            for seen in (0.75, 0.5, 0.25):
                for wname, a in windows(seen):
                    mask = whole.copy()
                    mask[:, :x0 + int(round(a * Wt))] = 0
                    mask[:, x0 + int(round((a + seen) * Wt)):] = 0
                    row = {"pool": pool, "stem": src.stem, "window": wname, "seen": seen, "from": round(a, 3), "size": size_class(Wt), "W_true": Wt, "piece": 0}
                    m = measure(mask, src.color)
                    if m is None:
                        rowsB.append({**row, **{c: "" for c in CUES}})
                        continue
                    e = estimates(m, mask, src.color)
                    cands, cost = e["curve"]
                    row.update(piece=1, **{c: round((e[c] - cx_true) / Wt, 4) for c in CUES}, cost_min=round(float(np.nanmin(cost)), 3),
                               cost_H=round(float(np.nanmin(cost)) / m["H"], 4))
                    for near in sorted({lim[0] for lim in LIMITS}):
                        lo, hi = fitting(cands, cost, near * m["H"])
                        row[f"span_{near}"] = round((hi - lo) / m["W"], 4)
                        row[f"mid_{near}"] = round(((lo + hi) / 2 - cx_true) / Wt, 4)
                    rowsB.append(row)
                    curves.append({**row, "W": m["W"], "H": m["H"], "u": (cands - cx_true) / Wt, "cost": cost})
            variants = [("none", 0.0, "L", 1)]
            variants += [("edge", a, s, 1) for a in oc.AMOUNTS for s in ("L", "R")]
            variants += [("both", a, "L", 1) for a in oc.AMOUNTS]
            variants += [("slant", a, s, ln) for a in oc.AMOUNTS for s in ("L", "R") for ln in (1, -1)]
            for kind, amount, side, lean in variants:
                sc = oc.make_scene(src, "edge" if kind == "none" else kind, amount, side, lean=lean)
                m = measure(sc.mask, src.color)
                if m is None:
                    continue
                e = estimates(m, sc.mask, src.color)
                ends = {"L": "own", "R": "own"}
                if kind == "both":
                    ends = {"L": "cut straight", "R": "cut straight"}
                elif kind in ("edge", "slant"):
                    ends[side] = "cut straight" if kind == "edge" else "cut slanted"
                for sd in ("L", "R"):
                    ft, fb = e[f"fill {sd}"]
                    rowsD.append({"pool": pool, "stem": src.stem, "kind": kind, "seen": round(1 - amount, 2), "cut_side": side if kind != "none" else "", "end": sd,
                                  "what": ends[sd], "size": size_class(src.width), "W": round(m["W"], 1), "fill_top": round(ft, 3), "fill_bottom": round(fb, 3)})
    (OUT / "sheets").mkdir(exist_ok=True)
    pickle.dump(curves, (OUT / "sheets" / "curves.pkl").open("wb"))          # for looking at; ignored by git
    keys = list(dict.fromkeys(k for r in rowsB for k in r))
    with (OUT / "shape_census.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, restval=""); w.writeheader(); w.writerows(rowsB)
    with (OUT / "corner_census.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rowsD[0].keys())); w.writeheader(); w.writerows(rowsD)

    def err(rs, cue):
        v = np.abs(np.asarray([r[cue] for r in rs if r["piece"] and r[cue] != ""], float))
        if not len(v):
            return "-"
        return f"{np.median(v):.2f} / {np.percentile(v, 90):.2f} / {int((v <= 0.15).sum())} of {len(rs)}"

    L += ["## B. The centre column from each cue, when only part of the width shows", "",
          "The barrel is cut by straight upright edges so that a window of 75, 50 or 25 % of its width shows: `one side cut` (the window starts at the "
          "barrel's left side, or ends at its right side: 2 scenes per barrel), `both sides, equal` (the window is in the middle), `both sides, unequal` "
          "(a quarter of what is hidden is on one side and three quarters on the other: 2 scenes per barrel). Each cell: **median error / 90th-percentile "
          "error / scenes with the centre right to 0.15 W, of all scenes** (error in barrel widths; a scene where no stripe piece is seen counts as not "
          "right). A W-wide box whose centre is 0.15 W off overlaps the true box by 0.74.", ""]
    for gname, gpools in GROUPS:
        for wname in WN:
            L += [f"### {gname}, {wname}", "", "| seen | " + " | ".join(CUES) + " |", "|---|" + "---|" * len(CUES)]
            for seen in (0.75, 0.5, 0.25):
                rs = [r for r in rowsB if r["pool"] in gpools and r["window"] == wname and r["seen"] == seen]
                L.append(f"| {int(seen * 100)} % | " + " | ".join(err(rs, c) for c in CUES) + " |")
            L.append("")
    L += ["### `all fit` by barrel size (both groups, all windows)", "", "| barrel width | 75 % seen | 50 % seen | 25 % seen |", "|---|---|---|---|"]
    for size in SIZES:
        L.append(f"| {size} | " + " | ".join(err([r for r in rowsB if r["size"] == size and r["seen"] == seen], "all fit") for seen in (0.75, 0.5, 0.25)) + " |")
    L.append("")

    # ---- part C
    def cell(rs, near, span, good):
        kn = [r for r in rs if r["piece"] and r[f"span_{near}"] <= span and r["cost_H"] <= good]
        ev = np.abs([r[f"mid_{near}"] for r in kn])
        return f"{len(kn)} / {int((ev > 0.15).sum())} / {ev.max() if len(ev) else 0:.2f}"

    order = [(wn, seen) for wn in (WN[0], WN[2], WN[1]) for seen in (0.75, 0.5, 0.25)]
    head = ["| one side: 75 % seen | 50 % | 25 % | both, unequal: 75 % | 50 % | 25 % | both, equal: 75 % | 50 % | 25 % |", "---|" * 9]
    L += ["## C. When does the outline know where the barrel is?", "",
          "The best position is not enough: a flat piece from the middle of a barrel fits the outline at many positions. The cost of a position = the "
          "mean distance in rows between the seen lines and the predicted ones. A position *fits* when its cost is within `near` x H of the best "
          "position's (H = the barrel's height). The outline *knows* when the fitting positions span at most `span` x W and the best cost is at most "
          "`good` x H; the centre is then the middle of the fitting positions. Each cell: **scenes where it knows / of those, the centre wrong by more "
          "than 0.15 W / the largest error among them** (both groups together: 100 scenes one side, 100 both sides unequal, 50 both sides equal).", "",
          "| near | span | good " + head[0], "|---|---|---|" + head[1]]
    for near, span, good in LIMITS:
        cells = [cell([r for r in rowsB if r["window"] == wn and r["seen"] == seen], near, span, good) for wn, seen in order]
        L.append(f"| {near} H | {span} W | {'any' if good > 50 else f'{good} H'} | " + " | ".join(cells) + " |")
    near, span, good = CHOSEN
    L += ["", f"With the limits taken (near {near} H, span {span} W, good {good} H), by group and by barrel size (scenes where it knows / wrong / largest error; "
          "of the scenes of that kind):", "", "| " + head[0], "|---|" + head[1]]
    for gname, sel in [(g, (lambda r, p=p: r["pool"] in p)) for g, p in GROUPS] + [(s, (lambda r, s=s: r["size"] == s)) for s in SIZES]:
        cells = []
        for wn, seen in order:
            rs = [r for r in rowsB if sel(r) and r["window"] == wn and r["seen"] == seen]
            cells.append(f"{cell(rs, near, span, good)}, of {len(rs)}")
        L.append(f"| {gname} | " + " | ".join(cells) + " |")
    L.append("")

    # ---- part D
    L += ["## D. The corners alone: a barrel's own side against a cut side", "",
          f"`fill` = the share of body color in the square of side {CORNER:.3f} W (how far in the lid ends from the side) at the top corner and at the "
          "bottom corner of the seen part's end. A square corner is full (1.0); a barrel's own corner is rounded off. Median (10th to 90th percentile; n). "
          "`the fuller of the two` = max(top, bottom): low only when BOTH corners are rounded off. (Scenes of the scorecard: an edge, a slanted edge, both sides.)", "",
          "| group | end | top corner | bottom corner | the fuller of the two |", "|---|---|---|---|---|"]
    for gname, gpools in GROUPS:
        for what in ("own", "cut straight", "cut slanted"):
            rs = [r for r in rowsD if r["pool"] in gpools and r["what"] == what]
            L.append(f"| {gname} | {what} | {stat([r['fill_top'] for r in rs], 2)} | {stat([r['fill_bottom'] for r in rs], 2)} | "
                     f"{stat([max(r['fill_top'], r['fill_bottom']) for r in rs], 2)} |")
    L += ["", "How many ends fall under a limit on the fuller of the two (an end under the limit would be called the barrel's own side):", "",
          "| group | end | under 0.6 | under 0.7 | under 0.8 | under 0.9 | n |", "|---|---|---|---|---|---|---|"]
    for gname, gpools in GROUPS:
        for what in ("own", "cut straight", "cut slanted"):
            rs = [max(r["fill_top"], r["fill_bottom"]) for r in rowsD if r["pool"] in gpools and r["what"] == what]
            rs = [v for v in rs if not np.isnan(v)]
            L.append(f"| {gname} | {what} | " + " | ".join(str(sum(v < t for v in rs)) for t in (0.6, 0.7, 0.8, 0.9)) + f" | {len(rs)} |")
    L.append("")

    # ---- part E: the real partly hidden barrels
    rowsE = []
    for set_name, pool in (("HOME hand masks", "HOME hand masks"), ("HOME", "HOME color model"), ("CAMPUS", "CAMPUS color model")):
        for stem, mask in sorted(segs[pool].items()):
            for b in io.load_boxes(stem)["barrels"]:
                if "occluded" not in (b.get("flags") or []):
                    continue
                color = dtp.COLOR_BY_NAME[b["color"]]
                bx0, by0, bx1, by1 = b["bbox"]
                cx_true, Wt = (bx0 + bx1) / 2, bx1 - bx0
                row = {"set": set_name, "frame": stem.replace("4A8B_", ""), "barrel": f"{b['color']} {list(b['bbox'])}"}
                sub = np.zeros_like(mask)
                sub[max(0, by0 - 3):by1 + 3, max(0, bx0 - 3):bx1 + 3] = mask[max(0, by0 - 3):by1 + 3, max(0, bx0 - 3):bx1 + 3]
                m = measure(mask, color, near_col=cx_true) if (sub == color).any() else None
                if m is None or not (bx0 - 3 <= (m["s"].bbox[0] + m["s"].bbox[2]) / 2 <= bx1 + 3 and by0 <= m["s"].center_row <= by1):
                    rowsE.append({**row, "seen": "", "centred": "", "outline": "", "cost_H": "", "span": "", "note": "no stripe piece of it"})
                    continue
                e = estimates(m, mask, color)
                cands, cost = e["curve"]
                lo, hi = fitting(cands, cost, CHOSEN[0] * m["H"])
                cH, sp = float(np.nanmin(cost)) / m["H"], (hi - lo) / m["W"]
                rowsE.append({**row, "seen": round((m["sx1"] - m["sx0"]) / Wt, 2), "centred": round((e["centred"] - cx_true) / Wt, 3),
                              "outline": round(((lo + hi) / 2 - cx_true) / Wt, 3), "cost_H": round(cH, 3), "span": round(sp, 2),
                              "note": "knows" if (sp <= CHOSEN[1] and cH <= CHOSEN[2]) else "does not know"})
    with (OUT / "real_census.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rowsE[0].keys())); w.writeheader(); w.writerows(rowsE)
    L += ["## E. The real partly hidden barrels of the HOME and CAMPUS train frames", "",
          "Every hand-drawn box flagged `occluded` (most are hidden by another barrel, and most show 0.8 of their width or more, where the detector "
          "takes the seen width as the box and the outline is not asked). `seen` = the width of the seen part (stripe + the body joined to it) / the "
          "box's width; errors in box widths; best cost in barrel heights; `span` = how wide the fitting positions are, in W; the last column is the "
          "verdict with the limits taken.", "",
          "| set | frame | barrel | seen | centred: error | outline: error | best cost | span | |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rowsE:
        L.append(f"| {r['set']} | {r['frame'].split('_', 2)[-1]} | {r['barrel']} | {r['seen']} | {r['centred']} | {r['outline']} | {r['cost_H']} | {r['span']} | {r['note']} |")
    (OUT / "shape_census.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
