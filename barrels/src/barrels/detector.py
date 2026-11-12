"""The v2 detector: class mask -> one Barrel per barrel, with hidden bottoms filled in by the geometry.
Plain-English guide: docs/HOW-IT-WORKS.md section 3. Built in explained steps:

  step 1 (2026-11-03)  barrel-colored blobs -> how many barrels, from the width the geometry expects at
                       that row -> the bottom edge: the seen one if it agrees with the top row, else the
                       one the top row predicts (shadow, occlusion), clipped to the frame.
  step 2 (2026-11-03)  the stripe as the barrel anchor: a band that is not the body color, sandwiched between
                       body color above and below, of the height the geometry expects at that row, proves
                       "barrel" and gives one barrel per stripe — inside merged blobs too. Stripeless pieces
                       survive only where a stripe cannot be seen (below the frame, or too far to resolve).
  hardening (2026-11-08, from the campus attribution)  the stripe is found from its own colored pixels
                       (``stripe_mode="cores"``), so unlabeled shadow glued to it cannot make it "too tall"; a
                       dark gap with no stripe-colored pixel is not a stripe unless ``dark_stripe`` is on; and
                       a box must hold enough body color in the stripe's columns (``body_min``), so a blue
                       barrel's body between two orange things is not an orange barrel; a stripeless piece must
                       be barrel-tall; a stripe cut by the frame edge is hidden on that side, so its full box is
                       drawn into the edge, not into the frame. ``stripe_mode="bands"`` is the 2026-11-03 finder,
                       kept for comparison.

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
    # step 2: the stripe
    require_stripe: bool = True  # step 2 (the stripe) is the detector since 2026-11-05: it beat step 1 under both rules (experiment 2026-11-03_det_step2); False = step 1 alone
    stripe_h_min: float = 0.45   # a band counts as a stripe when its height is between these multiples ...
    stripe_h_max: float = 1.6    # ... of the stripe height the geometry expects at that row (6 of the 24 mm)
    band_h_max: float = 3.0      # the band around it (stripe + unlabeled shadow) may be at most this x the expected stripe height
    stripe_w_min: float = 0.4    # ... and it is at least this fraction of a barrel width wide
    stripe_merge: float = 1.4    # a band wider than this x one barrel is the merged stripes of touching same-color barrels
    stripe_full: float = 0.8     # a stripe narrower than this x the barrel width is partly hidden -> box widened to a full barrel
    min_stripe_px: float = 4.0   # when the expected stripe is thinner than this, a stripe cannot be resolved -> stripeless allowed
    # hardening (2026-11-08)
    stripe_mode: str = "cores"   # "cores": the stripe = a component of stripe-colored pixels with body above and below (default);
                                 # "bands": the 2026-11-03 finder (a non-body gap between body above and below), for comparison
    dark_stripe: bool = False    # cores mode: also accept a gap with no stripe-colored pixel at all (a stripe lost to shadow) — off:
                                 # on the first live run such gaps under false orange were the floating boxes
    height_min: float = 0.5      # a stripeless piece (step 1) must also be between these multiples of the barrel height the geometry
    height_max: float = 1.5      # expects at its row (added 2026-11-08 after a blue jacket above the table edge passed the width check; 0 = off)
    body_min: float = 0.1        # in the stripe's columns, outside the stripe rows, the box must hold more body-colored pixels than
                                 # stripe-colored ones and at least this fraction of body color; else the stripe belongs to something
                                 # else (a blue barrel's body between two orange things is not an orange barrel). 0 = off
    cover_rows: bool = True      # (g) 2026-11-09: a stripe barrel "covers" a stripeless piece only if their boxes share rows as well as
                                 # columns (a far barrel above a close-up hid the close-up). False = columns only (before 2026-11-09)
    body_width: float = 1.2      # (f) 2026-11-09: the box is as wide as the body pixels joined to the stripe above and below it, at
                                 # most this x the expected width; the stripe alone ran ~15 % narrow on big barrels. 0 = stripe width

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


def _note(log: list | None, stage: str, why: str, bbox, **values) -> None:
    """Diagnostics only: when a caller passes a list as ``log``, every candidate the detector drops (and every
    one it keeps, why="kept") is appended to it as a dict. With log=None (the default everywhere) nothing happens;
    the answer never depends on it. Used by the attribution experiments to say *which* test refused a barrel."""
    if log is not None:
        log.append({"stage": stage, "why": why, "bbox": tuple(int(v) for v in bbox), **values})


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

def detect_step1(mask: np.ndarray, cfg: DetConfig = DetConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
                 log: list | None = None) -> list[Barrel]:
    """Step 1 alone: class mask (0 other / 1 orange / 2 blue / 255 ignore) -> barrels, one per barrel-shaped piece."""
    h, w = mask.shape
    out = []
    for blob in find_blobs(mask, cfg):
        for piece in split_blob(blob, mask, cam, cfg):
            x0, y0, x1, y1 = piece.bbox
            y1, flags = resolve_bottom(piece.bbox, cam, h, cfg)
            W = cam.expected_barrel_width_px(bottom_row=y1) if y1 < h else expected_width_px((x0, y0, x1, h), cam, h)
            if not math.isfinite(W) or W < cfg.min_width_px:
                _note(log, "piece", "too_far", (x0, y0, x1, y1), expected_w=W)
                continue                                   # above the horizon or too far to be on the table
            if not (cfg.width_min * W <= (x1 - x0) <= cfg.width_max * W):
                _note(log, "piece", "width", (x0, y0, x1, y1), expected_w=W)
                continue                                   # a sliver, or too wide to be one barrel
            if cfg.height_max > 0 and y1 < h and y0 > 0:
                H = cam.expected_barrel_height_px(bottom_row=y1)
                if math.isfinite(H) and not (cfg.height_min * H <= (y1 - y0) <= cfg.height_max * H):
                    _note(log, "piece", "height", (x0, y0, x1, y1), expected_h=H)
                    continue                               # barrel-wide but not barrel-tall: not a barrel (a jacket, a strip of wall)
            if x0 == 0 or x1 == w or y0 == 0:
                flags.add("truncated")
            n_o, n_b = piece.n_orange, piece.n_blue
            color = ORANGE if n_o >= n_b else BLUE
            out.append(Barrel(color=color, bbox=(x0, y0, x1, y1), confidence=max(n_o, n_b) / (n_o + n_b),
                              flags=frozenset(flags), area=int(piece.pixels.sum()), source="det1"))
    return sorted(out, key=lambda b: b.bbox[0])


# ---------------------------------------------------------------- step 2: the stripe is the barrel

@dataclass(frozen=True)
class Stripe:
    body: int                            # ORANGE | BLUE: the color found above and below the band
    bbox: tuple[int, int, int, int]      # the band, half-open
    n_other: int                         # band pixels labeled the other barrel color (a proper stripe)
    n_dark: int                          # band pixels labeled nothing (a shadowed stripe)
    center_row: float                    # the stripe's middle row: the median row of its other-colored pixels when there
                                         # are enough of them (the band also holds unlabeled shadow), else the band's middle


def _stripe_geometry(cam: geo.CameraModel, center_row: float):
    """(axis distance, BarrelRows) for a barrel whose stripe centre sits at ``center_row``; None if impossible."""
    d = cam._d_axis_from_point_row(center_row, geo.BARREL_HEIGHT_MM / 2, -geo.BARREL_BULGE_DIAMETER_MM / 2)
    if not math.isfinite(d) or d <= geo.BARREL_BULGE_DIAMETER_MM / 2 + 1:
        return None
    return d, cam.barrel_rows(d)


def _closed(bm: np.ndarray, cfg: DetConfig) -> np.ndarray:
    """A class mask with gaps up to close_px filled, as bool."""
    bm = bm.astype(np.uint8)
    if cfg.close_px >= 3:
        k = cfg.close_px if cfg.close_px % 2 else cfg.close_px + 1
        bm = cv2.morphologyEx(bm, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    return bm.astype(bool)


def _split_merged(sel: np.ndarray, mask: np.ndarray, other: int, body: int, x: int, bw: int, W: float, cfg: DetConfig,
                  n_dark_of) -> list[Stripe]:
    """One Stripe per barrel from a stripe region ``sel``: a region wider than stripe_merge x one barrel is the
    merged stripes of touching same-color barrels and is cut into equal parts."""
    k = int(round(bw / W)) if bw > cfg.stripe_merge * W else 1
    edges = [x + round(j * bw / k) for j in range(k + 1)]
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        part = sel.copy(); part[:, :a] = False; part[:, b:] = False
        ys, xs = np.where(part)
        if len(xs) == 0:
            continue
        ys_o = np.where(part & (mask == other))[0]
        center = float(np.median(ys_o)) + 0.5 if len(ys_o) >= 0.25 * part.sum() else (ys.min() + ys.max() + 1) / 2
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        out.append(Stripe(body, bbox, int((mask[part] == other).sum()), n_dark_of(part, bbox), center))
    return out


def find_stripes(mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(), log: list | None = None) -> list[Stripe]:
    """The stripes in the mask, one per barrel, found as ``cfg.stripe_mode`` says: ``"cores"`` (default since
    2026-11-08) anchors on the stripe-colored pixels themselves, ``"bands"`` (2026-11-03) on the non-body gap."""
    if cfg.stripe_mode == "bands":
        return _find_stripes_bands(mask, cam, cfg)
    if cfg.stripe_mode != "cores":
        raise ValueError(f"stripe_mode must be 'cores' or 'bands', got {cfg.stripe_mode!r}")
    return _find_stripes_cores(mask, cam, cfg, log)


def _reach_by_row(cam: geo.CameraModel, h: int, cfg: DetConfig) -> np.ndarray:
    """For every image row: how far (in rows) the body color may be from a stripe centred there and still be
    "right above / right below" it — band_h_max x the stripe height the geometry expects at that row; -1 where
    no barrel can have its stripe (at or above the horizon)."""
    reach = np.full(h, -1.0)
    for r in range(h):
        g = _stripe_geometry(cam, r + 0.5)
        if g is not None:
            reach[r] = cfg.band_h_max * (g[1].stripe_bottom - g[1].stripe_top)
    return reach


def _find_stripes_cores(mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, log: list | None = None) -> list[Stripe]:
    """A stripe is a connected component of the *other* color whose every pixel has body color above AND below it
    within band_h_max x the expected stripe height for its row (the sandwich, pixel by pixel — so a stripe that
    touches a neighbouring barrel's body is cut from it), with stripe proportions for its row: height between
    stripe_h_min and stripe_h_max x the expected stripe height, at least stripe_w_min of a barrel wide, not taller
    than wide. Only the stripe's own pixels are measured, so shadow the segmentation left unlabeled around it
    changes nothing. With ``dark_stripe`` on, a gap with no stripe-colored pixel at all but body above and below
    at the right spacing also counts (the 2026-11-03 'shadowed stripe')."""
    h, w = mask.shape
    out: list[Stripe] = []
    rows_idx = np.arange(h)[:, None]
    reach = _reach_by_row(cam, h, cfg)[:, None]
    for body in (ORANGE, BLUE):
        other = BLUE if body == ORANGE else ORANGE
        bm = _closed(mask == body, cfg)
        om = _closed(mask == other, cfg) & ~bm
        up = np.maximum.accumulate(np.where(bm, rows_idx, -10 ** 6), axis=0)              # last body row at or above
        dn = np.minimum.accumulate(np.where(bm, rows_idx, 10 ** 6)[::-1], axis=0)[::-1]   # first body row at or below
        sandwich = ((rows_idx - up) <= reach) & ((dn - rows_idx) <= reach)
        cands = [om & sandwich]
        if cfg.dark_stripe:
            cands.append((mask == 0) & ~bm & ~om & sandwich)
        for ci, cand in enumerate(cands):
            n, lab, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), connectivity=8)
            for i in range(1, n):
                x, y, bw, bh, area = (int(v) for v in st[i])
                sb = (x, y, x + bw, y + bh)
                if area < cfg.min_area_px:
                    _note(log, "stripe", "area", sb, body=body, area=area)
                    continue
                sel = lab == i
                ys = np.where(sel)[0]
                g = _stripe_geometry(cam, float(np.median(ys)) + 0.5)
                if g is None:
                    _note(log, "stripe", "no_geometry", sb, body=body)
                    continue
                d, rows = g
                W, Hs = rows.width_px, rows.stripe_bottom - rows.stripe_top
                if W < cfg.min_width_px or Hs < cfg.min_stripe_px:
                    _note(log, "stripe", "too_far", sb, body=body, expected_w=W, expected_stripe_h=Hs)
                    continue
                core_h = np.percentile(ys, 90) - np.percentile(ys, 10) + 1
                if not (cfg.stripe_h_min * Hs <= core_h <= cfg.stripe_h_max * Hs):
                    _note(log, "stripe", "height", sb, body=body, core_h=float(core_h), expected_stripe_h=Hs)
                    continue
                if bw < cfg.stripe_w_min * W or bw < core_h:
                    _note(log, "stripe", "width", sb, body=body, core_h=float(core_h), expected_w=W)
                    continue
                if ci == 1 and (mask[sel] == other).any():
                    continue                                   # a dark gap touching real stripe pixels is handled by them

                def n_dark_of(part, bbox, _ci=ci):
                    if _ci == 1:
                        return int(part.sum())                 # the whole dark gap is the 'stripe'
                    x0, y0, x1, y1 = bbox                      # unlabeled pixels inside the stripe's own box (its shadowed part)
                    return int((mask[y0:y1, x0:x1] == 0).sum())
                parts = _split_merged(sel, mask, other, body, x, bw, W, cfg, n_dark_of)
                if ci == 1:
                    parts = [Stripe(s.body, s.bbox, 0, s.n_dark, s.center_row) for s in parts]
                out.extend(parts)
    return sorted(out, key=lambda s: s.bbox[0])


def _find_stripes_bands(mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig()) -> list[Stripe]:
    """The 2026-11-03 finder (``stripe_mode="bands"``). Bands that are not the body color, with body color above
    AND below them in every column, whose height is what the geometry expects of a stripe at that row and whose
    width is at least a good part of a barrel. Found once with orange as the body (blue or dark band = an orange
    barrel's stripe) and once with blue. A band wider than one barrel is the merged stripes of touching same-color
    barrels and is cut evenly. Its two known flaws (a dark gap alone counts; shadow glued to a stripe makes its
    band too tall) are why ``"cores"`` replaced it."""
    h, w = mask.shape
    out: list[Stripe] = []
    for body in (ORANGE, BLUE):
        other = BLUE if body == ORANGE else ORANGE
        bm = (mask == body).astype(np.uint8)
        if cfg.close_px >= 3:
            k = cfg.close_px if cfg.close_px % 2 else cfg.close_px + 1
            bm = cv2.morphologyEx(bm, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
        bm = bm.astype(bool)
        above = np.maximum.accumulate(bm, axis=0)                  # body seen somewhere above, per column
        below = np.maximum.accumulate(bm[::-1], axis=0)[::-1]      # body seen somewhere below, per column
        band = (~bm) & above & below
        n, lab, st, _ = cv2.connectedComponentsWithStats(band.astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, bw, bh, area = (int(v) for v in st[i])
            if area < cfg.min_area_px:
                continue
            g = _stripe_geometry(cam, y + bh / 2)
            if g is None:
                continue
            d, rows = g
            W, Hs = rows.width_px, rows.stripe_bottom - rows.stripe_top
            if W < cfg.min_width_px or Hs < cfg.min_stripe_px:
                continue
            sel = lab == i
            n_other, n_dark = int((mask[sel] == other).sum()), int((mask[sel] == 0).sum())
            if n_other + n_dark < 0.5 * area:                         # mostly 'ignore' or the body color: not a band
                continue
            # the band = the stripe plus whatever shadow around it the segmentation left unlabeled, so measure the
            # stripe's own height from the rows its other-colored pixels occupy (10th-90th percentile) when there are
            # enough of them; a dark (shadowed) stripe falls back to the band's height
            ys_other = np.where(sel & (mask == other))[0]
            core_h = (np.percentile(ys_other, 90) - np.percentile(ys_other, 10) + 1) if len(ys_other) >= 0.25 * area else bh
            if not (cfg.stripe_h_min * Hs <= core_h <= cfg.stripe_h_max * Hs) or bh > cfg.band_h_max * Hs:
                continue
            if bw < cfg.stripe_w_min * W or bw < core_h:              # a partly hidden stripe is narrow but never taller than wide
                continue
            k = int(round(bw / W)) if bw > cfg.stripe_merge * W else 1
            edges = [x + round(j * bw / k) for j in range(k + 1)]
            for a, b in zip(edges[:-1], edges[1:]):
                part = sel.copy(); part[:, :a] = False; part[:, b:] = False
                ys, xs = np.where(part)
                if len(xs) == 0:
                    continue
                ys_o = np.where(part & (mask == other))[0]
                center = float(np.median(ys_o)) + 0.5 if len(ys_o) >= 0.25 * part.sum() else (ys.min() + ys.max() + 1) / 2
                out.append(Stripe(body, (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1),
                                  int((mask[part] == other).sum()), int((mask[part] == 0).sum()), center))
    return sorted(out, key=lambda s: s.bbox[0])


def _body_extent(mask: np.ndarray, body: int, x0: int, x1: int, y0: int, y1: int, max_gap: int = 3) -> tuple[int, int]:
    """Seen top and bottom of the body color in columns x0..x1, walking up from row y0 and down from row y1
    while body pixels keep appearing (gaps of up to max_gap rows allowed): the barrel this stripe belongs to."""
    col = (mask[:, x0:x1] == body).any(axis=1)
    top, gap, r = y0, 0, y0 - 1
    while r >= 0 and gap <= max_gap:
        if col[r]:
            top, gap = r, 0
        else:
            gap += 1
        r -= 1
    bottom, gap, r = y1, 0, y1
    while r < len(col) and gap <= max_gap:
        if col[r]:
            bottom, gap = r + 1, 0
        else:
            gap += 1
        r += 1
    return top, bottom


def _body_columns(mask: np.ndarray, body: int, x0: int, x1: int, top: int, bottom: int, y0: int, y1: int,
                  cap_px: float, others: tuple = (), min_px: int = 2, max_gap: int = 2) -> tuple[int, int]:
    """Left and right edge of the body color joined to the stripe: starting from the stripe's columns x0..x1, walk
    outward while columns in rows top..bottom (the stripe rows y0..y1 excluded) hold at least min_px body pixels,
    allowing gaps of max_gap columns. Columns under another found stripe (`others`, their x-ranges) are never
    added: they are a touching same-color neighbour's. The result is at most cap_px wide (trimmed evenly around the
    stripe)."""
    rows = np.ones(bottom - top, bool); rows[max(0, y0 - top):max(0, y1 - top)] = False
    cols = ((mask[top:bottom] == body) & rows[:, None]).sum(axis=0) >= min_px
    for ox0, ox1 in others:
        cols[max(0, ox0):max(0, ox1)] = False
    w = len(cols)
    bx0, gap, c = x0, 0, x0 - 1
    while c >= 0 and gap <= max_gap:
        if cols[c]:
            bx0, gap = c, 0
        else:
            gap += 1
        c -= 1
    bx1, gap, c = x1, 0, x1
    while c < w and gap <= max_gap:
        if cols[c]:
            bx1, gap = c + 1, 0
        else:
            gap += 1
        c += 1
    if bx1 - bx0 > cap_px:
        cx = (x0 + x1) / 2
        bx0, bx1 = max(bx0, int(round(cx - cap_px / 2))), min(bx1, int(round(cx + cap_px / 2)))
    return bx0, bx1


def barrel_from_stripe(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                       others: tuple = (), log: list | None = None) -> Barrel | None:
    """One barrel from its stripe. The stripe's row gives the distance; the distance gives the full box the
    geometry predicts (top, bottom, width). The seen body extent above and below the stripe is used for an
    edge when it agrees with the prediction, otherwise the prediction is drawn and the edge flagged. A stripe
    much narrower than a barrel is partly hidden: the box is widened to a full barrel around it."""
    h, w = mask.shape
    g = _stripe_geometry(cam, s.center_row)
    if g is None:
        _note(log, "barrel", "no_geometry", s.bbox, body=s.body)
        return None
    d, rows = g
    x0, y0, x1, y1 = s.bbox
    W = rows.width_px
    flags: set[str] = set()
    if (x1 - x0) < cfg.stripe_full * W:
        # partly hidden: widen to a full barrel on the side where something barrel-colored (the occluder)
        # borders the stripe; if neither or both sides are bordered, centre the full width on what is seen
        row = int(s.center_row)
        # the hidden side: something barrel-colored borders the stripe there, or the frame edge cuts it (2026-11-08, (e))
        left_hidden = x0 <= 0 or mask[row, x0 - 1] in (ORANGE, BLUE)
        right_hidden = x1 >= w or mask[row, x1] in (ORANGE, BLUE)
        Wi = int(round(W))
        if left_hidden and not right_hidden:
            bx0, bx1 = x1 - Wi, x1
        elif right_hidden and not left_hidden:
            bx0, bx1 = x0, x0 + Wi
        else:
            cx = (x0 + x1) / 2
            bx0, bx1 = int(round(cx - W / 2)), int(round(cx + W / 2))
        flags.add("occluded")
    else:
        bx0, bx1 = x0, x1
    top_seen, bottom_seen = _body_extent(mask, s.body, x0, x1, y0, y1)
    H = rows.bottom - rows.top
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
    top = top_seen
    if abs(top_seen - rows.top) > tol:
        top = int(round(rows.top)); flags.add("top_inferred")
    bottom = bottom_seen
    if abs(bottom_seen - rows.bottom) > tol and not (bottom_seen >= h and rows.bottom >= h):
        bottom = int(round(rows.bottom)); flags.add("bottom_inferred")
    top, bottom = max(0, top), min(h, bottom)
    if "occluded" not in flags and cfg.body_width > 0 and bottom - top >= 2:
        # (f) 2026-11-09: the stripe's outermost pixels curve away from the camera and go dark, so a box as wide as the
        # stripe runs ~15 % narrow on big barrels; the body pixels joined to the stripe give the barrel's real extent
        bx0, bx1 = _body_columns(mask, s.body, x0, x1, top, bottom, y0, y1, cap_px=cfg.body_width * W, others=others)
    bx0, bx1 = max(0, bx0), min(w, bx1)
    if bx1 - bx0 < 2 or bottom - top < 2:
        _note(log, "barrel", "empty_box", s.bbox, body=s.body)
        return None
    if cfg.body_min > 0:
        # hardening (c), 2026-11-08: in the stripe's own columns, outside the stripe rows, the box must hold more body
        # color than stripe color and at least body_min of body color — a stripe-colored thing with the other barrel
        # color above and below it is not this body's barrel
        cols = mask[top:bottom, x0:x1]
        outside = np.ones(cols.shape[0], bool); outside[max(0, y0 - top):max(0, y1 - top)] = False
        region = cols[outside]
        other = BLUE if s.body == ORANGE else ORANGE
        if region.size and ((region == s.body).sum() < (region == other).sum() or (region == s.body).mean() < cfg.body_min):
            _note(log, "barrel", "body_min", s.bbox, body=s.body, box=(bx0, top, bx1, bottom),
                  body_frac=float((region == s.body).mean()), other_frac=float((region == other).mean()))
            return None
    if bx0 == 0 or bx1 == w or top == 0 or bottom == h:
        flags.add("truncated")
    conf = 0.5 + 0.5 * s.n_other / max(1, s.n_other + s.n_dark)   # a labeled stripe is surer than a dark band
    return Barrel(color=s.body, bbox=(bx0, top, bx1, bottom), confidence=conf, flags=frozenset(flags),
                  area=s.n_other + s.n_dark, source="det2")


def _x_overlap(a: tuple, b: tuple) -> float:
    """Fraction of the narrower box's width that the two boxes share horizontally."""
    inter = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    return inter / max(1, min(a[2] - a[0], b[2] - b[0]))


def detect(mask: np.ndarray, cfg: DetConfig = DetConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
           log: list | None = None) -> list[Barrel]:
    """Class mask (0 other / 1 orange / 2 blue / 255 ignore) -> barrels. Same signature as detect_cc.detect.

    Step 2: every stripe is a barrel. Step-1 pieces (barrel-colored, barrel-sized) are then only kept where
    no stripe barrel already covers them AND a stripe could not have been seen: the piece reaches the frame
    bottom (the stripe is below the frame) or the expected stripe is too thin to resolve at that distance.
    With cfg.require_stripe=False this is step 1 alone (the detector before 2026-11-05; ``detect_image.py --step1``)."""
    h, w = mask.shape
    pieces = detect_step1(mask, cfg, cam, log)
    if not cfg.require_stripe:
        return pieces
    out: list[Barrel] = []
    stripes = find_stripes(mask, cam, cfg, log)
    for s in stripes:
        b = barrel_from_stripe(s, mask, cam, cfg, others=tuple((o.bbox[0], o.bbox[2]) for o in stripes if o is not s), log=log)
        if b is None:
            continue
        _note(log, "barrel", "kept", s.bbox, body=s.body, box=b.bbox)
        dup = next((o for o in out if o.color == b.color and box_iou(o.bbox, b.bbox) > 0.5), None)
        if dup is not None:
            _note(log, "barrel", "duplicate", s.bbox, body=s.body, box=b.bbox)
            if b.confidence > dup.confidence:
                out.remove(dup); out.append(b)
            continue
        out.append(b)
    for p in pieces:
        # (g) 2026-11-09: a stripe barrel accounts for a piece only if the two boxes share rows as well as columns — a far
        # barrel standing above a close one in the picture used to "cover" it (live run with Dave: the close-up got no box)
        if any(_x_overlap(p.bbox, o.bbox) > 0.3 and (not cfg.cover_rows or min(p.bbox[3], o.bbox[3]) > max(p.bbox[1], o.bbox[1])) for o in out):
            _note(log, "piece", "covered", p.bbox, body=p.color)
            continue                                         # the stripe barrels already account for this piece
        g = _stripe_geometry(cam, (p.bbox[1] + p.bbox[3]) / 2)
        hs = (g[1].stripe_bottom - g[1].stripe_top) if g else math.inf
        if p.bbox[3] >= h or hs < cfg.min_stripe_px:
            out.append(p)                                    # stripe below the frame, or too far to resolve one
        else:
            _note(log, "piece", "stripeless", p.bbox, body=p.color, expected_stripe_h=hs)
    return sorted(out, key=lambda b: b.bbox[0])


def box_iou(a: tuple, b: tuple) -> float:
    ax0, ay0, ax1, ay1 = a; bx0, by0, bx1, by1 = b
    iw = max(0, min(ax1, bx1) - max(ax0, bx0)); ih = max(0, min(ay1, by1) - max(ay0, by0))
    inter = iw * ih
    union = (ax1 - ax0) * (ay1 - ay0) + (bx1 - bx0) * (by1 - by0) - inter
    return inter / union if union else 0.0


BOX_COLOR_BGR = {ORANGE: (0, 255, 255), BLUE: (0, 255, 0)}   # yellow = orange barrel, green = blue barrel (Dave's convention)


def draw(image_bgr: np.ndarray, barrels: list[Barrel], thickness: int = 1) -> np.ndarray:
    """The v2 output image: the input with one 1-px rectangle per barrel — yellow for an orange barrel, green
    for a blue one, so the lines stand out from the barrels themselves — and nothing else."""
    out = image_bgr.copy()
    for b in barrels:
        x0, y0, x1, y1 = b.bbox
        cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), BOX_COLOR_BGR[b.color], thickness)
    return out
