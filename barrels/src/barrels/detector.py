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
  2026-11-18           a stripe in pieces is one stripe (``stripe_join``); a barrel behind a found barrel is found from
                       its visible top (``cap_behind``).
  2026-11-19           a partly seen stripe is placed by what is seen of the barrel, and a side counts as hidden only
                       for a reason: the frame edge, a found nearer barrel, or the body and the stripe ending apart
                       (``side_hidden``); a far stripe eaten at both seams is read at the seams too (``seam_height``).
  2026-11-19 (A5)      a narrow cap's bottom is its own color seen ending beside the front barrel, also when that is
                       further from the top-row estimate than the tolerance (``cap_seen_bottom``).
  2026-11-19 (occlusion)  one idea: what is seen fixes the distance, the distance the size; the box is the full barrel
                       placed where the seen part allows, and where nothing pins it, it covers every place the barrel can
                       be (``slice_box``, ``cover_unpinned``); a stripe wider than a barrel is two barrels (``stripe_two``);
                       an edge is seen only against something that is not a barrel (``edge_check``); a top above a found
                       barrel of its own color is a cap too (``cap_same``).
  2026-11-20 (occlusion, up and down)  a stripe with body color on one side only, seen in its whole width, with the body's
                       far edge where the seam predicts it, is a barrel hidden from above or from below (``half_stripe``,
                       ``half_thin``); two slices at the same rows whose outer edges are one barrel apart are one barrel
                       behind a post (``post_pair``); ``stripe_two`` asked only where the body is seen right above and below the
                       stripe (``stripe_wide``); a narrow full slice beside a found nearer barrel (``slice_behind``); the cap's
                       height floor at 0.4 of an upper body (``cap_low``).
  2026-11-20 (pin)     where a cut barrel is, sideways: the barrel's outline (top line, stripe arc, bottom line) is known
                       once its distance is known; an end of the seen part whose corners follow it is the barrel's own
                       side, and a partly seen stripe that no side reason places is a barrel W wide from that end
                       (``pin_outline``); a thin piece of stripe is a barrel only as a full slice with such an end
                       (``pin_thin``).
  2026-11-20 (combined)  the two branches of 2026-11-20 together (experiments/2026-11-20_occl_combined): on by default
                       are half_stripe, half_thin, post_pair, stripe_wide, cap_low, pin_outline and pin_thin; slice_behind
                       is off (false boxes on damaged masks), as are slice_box, cover_unpinned and stripe_two. A piece under
                       the finder's old width floor is handed to the left-over rules whether or not the lower floor of
                       pin_thin also lets it into the stripe step.

Everything here is a pure function of the mask and the camera: nothing is fit per image.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, replace

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
    occl_body_side: bool = False # (h) 2026-11-11: a partly hidden stripe says where the barrel is, not which side of it is hidden; with
                                 # this on, the body color joined to the stripe decides (see barrel_from_stripe). False = before
    stripe_join: bool = True     # 2026-11-18: stripe pieces of one body color that share rows and together span no more than one barrel
                                 # (body_width x the expected width) are one stripe: a highlight or a shadow line cut it. False = each piece alone
    cap_behind: bool = True      # 2026-11-18: a body-colored top, barrel-wide and as tall as an upper body for its row, cut off by a found
                                 # barrel standing nearer, is a barrel behind that one (see caps_behind). False = found from a stripe only
    side_hidden: bool = True     # 2026-11-19: a partly seen stripe (narrower than stripe_full x a barrel) is placed by what is seen of the
                                 # barrel (stripe + the body joined to it), and a side counts as hidden only for a reason: the frame edge, a
                                 # found barrel standing nearer, or the body and the stripe ending at different columns there (see
                                 # _partly_seen). The finder's width floor becomes one stripe height; a stripe under stripe_w_min with no
                                 # such reason gives no box. False = widen toward a barrel-colored pixel beside the stripe, else centre
    seam_height: bool = True     # 2026-11-19: a stripe refused as too thin, and seen whole (at least stripe_full x a barrel wide), is read a
                                 # second time as the mean of its own height and of the gap between the body above and below it (mixed
                                 # pixels at the two seams make the one thinner and the other taller by the same amount). False = the
                                 # stripe's own rows only
    cap_seen_bottom: bool = True  # 2026-11-19 (A5): a narrow cap's bottom estimate comes from its top row (4 to 7 px low at mid and far range
                                 # with this camera). When no seen end agrees with it: the cap's color, read beside the nearer found barrels,
                                 # seen ending between the bottom of a barrel only as wide as the seen cap and the estimate + the tolerance,
                                 # is the bottom (see caps_behind). False = the top-row bottom
    # occlusion (2026-11-19, experiments/2026-11-19_det_occl): what is seen fixes the distance, the distance the size; the box is the
    # full barrel placed where the seen part allows, and where nothing pins it, it covers every place the barrel can be
    slice_box: bool = False      # with side_hidden: a stripe piece counts from stripe_h_min x a stripe height wide (before: one stripe
                                 # height, not taller than wide); a piece under the old floor is a barrel only as a full slice (neither
                                 # its top nor its bottom inferred). A stripe under stripe_w_min wide with no reason on either side, or one
                                 # on both, gets the cover box, from (seen right end - W) to (seen left end + W), if it is a full slice; a
                                 # wider one with a reason on both sides gets it too. A partly seen piece that shares rows with a found
                                 # same-colored barrel's stripe, inside that barrel's box, is that stripe's
    cover_unpinned: bool = False  # with slice_box: no reason on either side and stripe_w_min wide or more: the cover box too (False = W
                                 # wide, centred on what is seen, as before)
    stripe_two: bool = False     # a stripe region wider than body_width x W is two (or more) same-colored barrels' stripes run together:
                                 # max(2, round(width / W)) equal parts (before: only above stripe_merge, round(width / W) parts). W here
                                 # is the larger of the width the stripe's row gives and the width of a barrel as tall as the body seen
                                 # above and below it. A part is hidden on the side where it was cut; two parts are never duplicates
    edge_check: bool = True      # an edge is seen only against something that is not a barrel: (a) a stripe with neither edge seen where
                                 # its row predicts it, whose body above ends against the OTHER barrel color, is not a barrel (what stands
                                 # behind cannot hide a top); (b) a kept seen bottom with the other barrel color right under it becomes the
                                 # lower of itself and the predicted bottom
    cap_same: bool = True        # caps_behind: a piece with half its pixels inside found boxes of its color is not skipped whole: the
                                 # parts of it outside those boxes are tested as caps, so a top showing above a found barrel of its OWN
                                 # color can be a barrel behind it (False = skipped)
    # occlusion from above and from below, a post, same color beside (2026-11-20, experiments/2026-11-20_occl_vertical). Every box
    # these make shows the barrel's whole width or is pinned by a found barrel: no side is guessed
    half_stripe: bool = True     # a band of stripe color with body color on ONE side only (right above it in stripe_full of its columns
                                 # and right below it in at most 1 - stripe_full, or the reverse), stripe_full to body_width x a barrel
                                 # wide and not taller than a stripe, is a barrel hidden from below or from above when the body's far
                                 # edge is where the seam between band and body predicts it and is a seen edge (see half_stripes)
    half_thin: bool = True       # with half_stripe: the band may be thinner than stripe_h_min x a stripe height (any band of min_area_px;
                                 # a barrel half hidden from below shows a few rows of its stripe)
    post_pair: bool = True       # two stripe pieces that give no box alone, of one body color, at the same rows, each a full slice (its
                                 # body ends where its row predicts the top and the bottom), outer edges stripe_full to body_width x a
                                 # barrel apart: one barrel behind a post (see post_pairs)
    stripe_wide: bool = True     # stripe_two, asked only where body color is seen right above AND right below the stripe region (else
                                 # nothing but the row says how big the barrel is, and a near barrel runs wider than its row predicts)
    slice_behind: bool = False   # a stripe piece under the finder's width floor that is a full slice, with exactly one side hidden by a
                                 # found barrel standing nearer or by the frame edge: a barrel wide from the seen edge of the other side.
                                 # OFF since 2026-11-20 (experiments/2026-11-20_occl_combined): on damaged masks it boxes the wrong side of
                                 # a slice left beside a found barrel in a bunch (medium damage, 20 seeds: 7 false boxes against 3)
    cap_low: bool = True         # caps_behind: a top counts from width_min (0.4) x an upper body tall (False = height_min, 0.5)
    # occlusion, the sideways position (2026-11-20, experiments/2026-11-20_occl_pin): the barrel's outline is known once its distance
    # is known; an end of the seen part whose corners follow it is the barrel's own side, and the barrel is W wide from there
    pin_outline: bool = True     # with side_hidden: a partly seen stripe that no side reason places (no reason, or one on both sides) is
                                 # placed by the outline when exactly one end of what is seen is the barrel's own side (see
                                 # _outline_place): the box is W wide from that end. When the outline does not know, and with False: as
                                 # before (centred on what is seen, or no box). A box placed this way never replaces a found barrel's box
    pin_thin: bool = True        # (on since 2026-11-20, experiments/2026-11-20_occl_combined: no false box added anywhere, no cell lower)
                                 # with pin_outline: a stripe piece counts from stripe_h_min x a stripe height wide and may be taller than
                                 # wide (the floor of slice_box). A piece under the old floor ("thin") is a barrel only when it is a full
                                 # slice (neither its top nor its bottom inferred) AND the outline knows; its box is where the outline
                                 # puts it. It never changes another barrel's box, and a thin piece that shares rows with a found
                                 # same-colored barrel's stripe inside that barrel's box is that stripe's
    pin_good: float = 0.05       # an end of the seen part is the barrel's own side when, with the outline's side put on it, each of the
                                 # three lines (top, stripe, bottom) lies within this x the barrel's height of the seen one, on average
                                 # over the columns within half a lid's width of that end
    # a stripe cut through, a sliver with stripe and body in view (2026-11-20, experiments/2026-11-20_occl_sliver, PREREG.md)
    stripe_bridge: bool = False  # with stripe_join: two pieces that share rows and fit in one barrel's width are one stripe, gap included,
                                 # also when one fails the stripe-shape test, if each is no taller than stripe_h_max stripe heights by the
                                 # finder's height measure, body color is right above and right below in EVERY column of the gap, and the
                                 # gap is at most half the joined span (see _join_pieces)
    thin_frame: bool = False     # with pin_thin: a thin full slice whose seen part touches the frame edge on exactly one side is W wide
                                 # from its other end (the frame is a hidden side that is known)
    own_close: bool = False      # with side_hidden: a partly seen full slice that no side reason and no outline places is W wide from the
                                 # end where the body closes on the stripe (top and bottom both bottom_tol x H in, over the last 0.05 W),
                                 # when at the other end at least one of them stands (at most 0.1 x H in) (see _closed_end)
    thin_span: bool = False      # with pin_thin: a thin full slice whose body joined to it is seen stripe_full to body_width x W wide gets
                                 # that span as its box (the barrel's whole width is seen, only its stripe is hidden)

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
    merged: tuple | None = None          # when this stripe is a part cut from a wider stripe region: that region's box
    small: bool = False                  # slice_box: a piece the finder's floor refused before (narrower than a stripe is tall, or
                                         # taller than wide); it is a barrel only as a full slice (see barrel_from_stripe)
    narrow: bool = False                 # post_pair, slice_behind: a piece under the finder's width floor. Never a barrel by itself:
                                         # kept aside as one of a pair, or as a slice beside a found nearer barrel


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
                  n_dark_of, W_two: float | None = None) -> list[Stripe]:
    """One Stripe per barrel from a stripe region ``sel``: a region wider than stripe_merge x one barrel is the
    merged stripes of touching same-color barrels and is cut into equal parts. With ``stripe_two`` (2026-11-19) a
    region wider than body_width x one barrel already is (a stripe cannot be wider than its barrel), and it is cut into
    at least two: two same-colored barrels that overlap by half have a joined stripe under 1.5 barrels wide. The
    barrel width it is compared with there is ``W_two``: the larger of the width the stripe's row gives and the width
    of a barrel as tall as the body seen above and below the stripe (round 2: a near barrel can be 1.3 x the width its
    row predicts, but then it is taller by as much; two barrels side by side are not taller than one)."""
    k = int(round(bw / W)) if bw > cfg.stripe_merge * W else 1
    Wt = W_two or W
    # stripe_wide (2026-11-20): the same, but only when the caller could read the barrel's size off the body (W_two given)
    if (cfg.stripe_two or (cfg.stripe_wide and W_two is not None)) and bw > max(cfg.body_width, 1.0) * Wt:
        k = max(2, int(round(bw / Wt)))
    edges = [x + round(j * bw / k) for j in range(k + 1)]
    whole = None
    if k > 1:
        ys_all = np.where(sel)[0]
        whole = (x, int(ys_all.min()), x + bw, int(ys_all.max()) + 1)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        part = sel.copy(); part[:, :a] = False; part[:, b:] = False
        ys, xs = np.where(part)
        if len(xs) == 0:
            continue
        ys_o = np.where(part & (mask == other))[0]
        center = float(np.median(ys_o)) + 0.5 if len(ys_o) >= 0.25 * part.sum() else (ys.min() + ys.max() + 1) / 2
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        out.append(Stripe(body, bbox, int((mask[part] == other).sum()), n_dark_of(part, bbox), center, whole))
    return out


def find_stripes(mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(), log: list | None = None,
                 narrow: list | None = None) -> list[Stripe]:
    """The stripes in the mask, one per barrel, found as ``cfg.stripe_mode`` says: ``"cores"`` (default since
    2026-11-08) anchors on the stripe-colored pixels themselves, ``"bands"`` (2026-11-03) on the non-body gap.
    ``narrow`` (2026-11-20): when a list is passed, the pieces the cores finder refuses for their width alone are
    appended to it (``Stripe.narrow``); the returned stripes are the same with or without it."""
    if cfg.stripe_mode == "bands":
        return _find_stripes_bands(mask, cam, cfg)
    if cfg.stripe_mode != "cores":
        raise ValueError(f"stripe_mode must be 'cores' or 'bands', got {cfg.stripe_mode!r}")
    return _find_stripes_cores(mask, cam, cfg, log, narrow)


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


CLOSE_ZONE = 0.05      # own_close: the end zone, in barrel widths (the last twentieth of the barrel; census_ends.md)
CLOSE_CUT = 0.1        # own_close: an end "stands" when the top or the bottom is at most this x H in from the predicted row


def _join_pieces(st: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, lab: np.ndarray | None = None,
                 sand: np.ndarray | None = None) -> list[list[int]]:
    if cfg.stripe_bridge and lab is not None and sand is not None:
        return _join_bridged(st, cam, cfg, lab, sand)
    return _join_shaped(st, cam, cfg)


def _join_bridged(st: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, lab: np.ndarray, sand: np.ndarray) -> list[list[int]]:
    """``stripe_bridge`` (2026-11-20): ``_join_shaped``, and in addition a piece may join the group to its left when the GAP
    between them is bridged: each of the two is no taller than stripe_h_max x the expected stripe height by the finder's height
    measure (10th to 90th percentile of its rows), body color is right above and right below the stripe rows in every column of
    the gap (``sand``, the finder's sandwich), and the gap is at most half the joined span. Two barrels' stripes never pass that
    (census_pairs.md: 0 of 59 two-barrel pairs on the patched masks are bridged; the pairs on no barrel are pieces a whole gap
    apart). A piece that is not stripe-shaped joins only by a bridge. ``lab`` = the pieces' label image."""
    def core(i):
        x, y, bw, bh = (int(v) for v in st[i][:4])
        ys = np.where(lab[y:y + bh, x:x + bw] == i)[0] + y
        return float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)

    groups: list[list] = []                                      # [ids, x0, x1, y0, y1, all shaped, all cores ok]
    for i in sorted(range(1, len(st)), key=lambda i: (int(st[i][0]), int(st[i][1]))):
        x, y, bw, bh = (int(v) for v in st[i][:4])
        g = _stripe_geometry(cam, y + bh / 2)
        if g is None:
            groups.append([[i], x, x + bw, y, y + bh, False, False])
            continue
        hs = g[1].stripe_bottom - g[1].stripe_top
        shaped = bh <= bw and bh <= cfg.stripe_h_max * hs
        core_ok = core(i) <= cfg.stripe_h_max * hs
        span = max(cfg.body_width, 1.0) * g[1].width_px
        for grp in reversed(groups):
            ids, gx0, gx1, gy0, gy1, gsh, gco = grp
            shared = min(gy1, y + bh) - max(gy0, y)
            if 2 * shared < min(bh, gy1 - gy0) or max(gx1, x + bw) - min(gx0, x) > span:
                continue
            joined = max(gx1, x + bw) - min(gx0, x)
            ok = shaped and gsh
            if not ok and core_ok and gco:
                a, b = gx1, x                                    # the gap's columns
                ya, yb = max(gy0, y), min(gy1, y + bh)
                level = abs((y + bh / 2) - (gy0 + gy1) / 2) <= hs / 2            # round 2: at the same rows (a stripe is level)
                ok = level and (b <= a or (b - a <= joined / 2 and bool(sand[ya:yb, a:b].any(axis=0).all())))
            if ok:
                grp[:] = [ids + [i], min(gx0, x), max(gx1, x + bw), min(gy0, y), max(gy1, y + bh), gsh and shaped, gco and core_ok]
                break
        else:
            groups.append([[i], x, x + bw, y, y + bh, shaped, core_ok])
    return [grp[0] for grp in groups]


def _join_shaped(st: np.ndarray, cam: geo.CameraModel, cfg: DetConfig) -> list[list[int]]:
    """``stripe_join`` (2026-11-18): which connected pieces of sandwiched stripe color are one stripe. ``st`` is the
    stats table of the pieces (row 0 = background). Going left to right, a piece joins the nearest group to its left
    when (1) they share rows: the overlap is at least half the height of the shorter of the two, and (2) together they
    span no more than one barrel: body_width x the width a barrel has at that row. Two barrels cannot both have their
    stripe inside one barrel's width at the same rows, so such pieces are one stripe that a highlight, a shadow line or
    a washed-out upper body cut. A piece joins only if it has a shape a stripe can have: not taller than stripe_h_max
    x the expected stripe height and not taller than wide (round 2: slivers of a barrel's own upper body between specks
    are tall, and joined they passed for a stripe). Any other piece stays alone and is judged alone, as before.
    Returns the groups as lists of piece numbers."""
    groups: list[list] = []                                      # [ids, x0, x1, y0, y1]
    alone: list[list[int]] = []
    for i in sorted(range(1, len(st)), key=lambda i: (int(st[i][0]), int(st[i][1]))):
        x, y, bw, bh = (int(v) for v in st[i][:4])
        g = _stripe_geometry(cam, y + bh / 2)
        if g is None or bh > bw or bh > cfg.stripe_h_max * (g[1].stripe_bottom - g[1].stripe_top):
            alone.append([i])
            continue
        span = max(cfg.body_width, 1.0) * g[1].width_px
        for grp in reversed(groups):
            ids, gx0, gx1, gy0, gy1 = grp
            shared = min(gy1, y + bh) - max(gy0, y)
            if 2 * shared >= min(bh, gy1 - gy0) and max(gx1, x + bw) - min(gx0, x) <= span:
                grp[:] = [ids + [i], min(gx0, x), max(gx1, x + bw), min(gy0, y), max(gy1, y + bh)]
                break
        else:
            groups.append([[i], x, x + bw, y, y + bh])
    return [grp[0] for grp in groups] + alone


def _find_stripes_cores(mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, log: list | None = None,
                        narrow: list | None = None) -> list[Stripe]:
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
            # one candidate per connected piece; with stripe_join, pieces that share rows and fit in one barrel's width are one candidate
            groups = _join_pieces(st, cam, cfg, lab, sandwich) if (cfg.stripe_join and ci == 0) else [[i] for i in range(1, n)]
            for ids in groups:
                x, y = int(min(st[i][0] for i in ids)), int(min(st[i][1] for i in ids))
                bw, bh = int(max(st[i][0] + st[i][2] for i in ids)) - x, int(max(st[i][1] + st[i][3] for i in ids)) - y
                area = int(sum(st[i][4] for i in ids))
                sb = (x, y, x + bw, y + bh)
                if area < cfg.min_area_px:
                    _note(log, "stripe", "area", sb, body=body, area=area)
                    continue
                sel = np.isin(lab, ids) if len(ids) > 1 else lab == ids[0]
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
                h_ok = cfg.stripe_h_min * Hs <= core_h <= cfg.stripe_h_max * Hs
                seam_h = None
                if cfg.seam_height and ci == 0 and core_h < cfg.stripe_h_min * Hs and bw >= cfg.stripe_full * W:
                    # 2026-11-19: too thin by its own rows. Mixed pixels at the two seams are neither color: the stripe is thinner
                    # and the gap between the two body parts taller by the same amount, so the middle of the two is the stripe's height.
                    # Asked only of a stripe seen whole (round 2): thin because eaten, or short because partly hidden, not both
                    # (a blue sliver between two fingers is thin and short)
                    gap = float(np.median((dn - up - 1)[sel]))
                    seam_h = (core_h + gap) / 2
                    h_ok = cfg.stripe_h_min * Hs <= seam_h <= cfg.stripe_h_max * Hs
                if not h_ok:
                    _note(log, "stripe", "height", sb, body=body, core_h=float(core_h), expected_stripe_h=Hs,
                          **({} if seam_h is None else {"seam_h": float(seam_h)}))
                    continue
                # the width floor: stripe_w_min of a barrel; with side_hidden, one stripe height (a narrow stripe is then judged in
                # barrel_from_stripe); with slice_box too, stripe_h_min of a stripe height, and a piece may be taller than wide (a
                # barrel three quarters hidden shows a piece about as wide as a stripe is tall)
                slices = cfg.side_hidden and (cfg.slice_box or (cfg.pin_outline and cfg.pin_thin))      # pin_thin: the same floor
                floor = cfg.stripe_h_min * Hs if slices else (Hs if cfg.side_hidden else cfg.stripe_w_min * W)
                if bw < floor or (bw < core_h and not slices):
                    _note(log, "stripe", "width", sb, body=body, core_h=float(core_h), expected_w=W)
                    if narrow is not None and ci == 0:             # 2026-11-20: kept aside for post_pair / slice_behind, never a barrel alone
                        narrow.append(Stripe(body, sb, int((mask[sel] == other).sum()), 0, float(np.median(ys)) + 0.5, narrow=True))
                    continue
                if ci == 1 and (mask[sel] == other).any():
                    continue                                   # a dark gap touching real stripe pixels is handled by them

                def n_dark_of(part, bbox, _ci=ci):
                    if _ci == 1:
                        return int(part.sum())                 # the whole dark gap is the 'stripe'
                    x0, y0, x1, y1 = bbox                      # unlabeled pixels inside the stripe's own box (its shadowed part)
                    return int((mask[y0:y1, x0:x1] == 0).sum())
                W_two = None
                if cfg.stripe_two or cfg.stripe_wide:
                    top_s, bot_s = _body_extent(mask, body, x, x + bw, y, y + bh)      # the body seen above and below the whole region
                    # stripe_wide (2026-11-20): only where body IS seen right above and right below the stripe. With none there (the walk
                    # allows 3 empty rows), the seen height says nothing, and a near barrel's stripe can be 1.26 x the width its row gives
                    if cfg.stripe_two or (top_s < y and bot_s > y + bh):
                        W_two = max(W, (bot_s - top_s) * W / (rows.bottom - rows.top))
                parts = _split_merged(sel, mask, other, body, x, bw, W, cfg, n_dark_of, W_two)
                if ci == 1:
                    parts = [Stripe(s.body, s.bbox, 0, s.n_dark, s.center_row, s.merged) for s in parts]
                if slices and (bw < Hs or bw < core_h):
                    parts = [replace(s, small=True) for s in parts]                     # under the floor of before slice_box
                    if narrow is not None and ci == 0:
                        # 2026-11-20 (occl_combined): the lower floor lets this piece into the stripe step as a thin stripe. The left-over
                        # rules (post_pair, slice_behind) are still handed it, exactly as when the finder refuses it for its width: the
                        # floor is lowered for the stripe step only (without this, pin_thin took every narrow slice away from them)
                        narrow.append(Stripe(body, sb, int((mask[sel] == other).sum()), 0, float(np.median(ys)) + 0.5, narrow=True))
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


def _body_span(mask: np.ndarray, body: int, x0: int, x1: int, top: int, bottom: int, y0: int, y1: int,
               others: tuple = (), min_px: int = 2, max_gap: int = 2) -> tuple[int, int] | None:
    """Left and right end of the body color joined to the stripe, where the body may also stop short of the stripe's
    end (``_body_columns`` only walks outward). Columns in rows top..bottom (the stripe rows y0..y1 excluded) that hold
    at least min_px body pixels form runs (gaps of max_gap columns allowed); the runs that reach the stripe's columns
    x0..x1 are the body joined to it. Columns under another found stripe (`others`) never count. None = no such column."""
    rows = np.ones(bottom - top, bool); rows[max(0, y0 - top):max(0, y1 - top)] = False
    cols = ((mask[top:bottom] == body) & rows[:, None]).sum(axis=0) >= min_px
    for ox0, ox1 in others:
        cols[max(0, ox0):max(0, ox1)] = False
    idx = np.flatnonzero(cols)
    if len(idx) == 0:
        return None
    cut = np.flatnonzero(np.diff(idx) > max_gap + 1)
    runs = zip(np.r_[idx[0], idx[cut + 1]], np.r_[idx[cut], idx[-1]] + 1)
    joined = [(int(a), int(b)) for a, b in runs if b >= x0 - max_gap and a <= x1 + max_gap]
    if not joined:
        return None
    return min(a for a, _ in joined), max(b for _, b in joined)


# ---------------------------------------------------------------- the outline (2026-11-20): where a cut barrel is, sideways

LID_HALF = geo.BARREL_END_DIAMETER_MM / geo.BARREL_BULGE_DIAMETER_MM / 2     # half the width of the lid (and of the base), in barrel widths: 0.353


@dataclass(frozen=True)
class Outline:
    """The outline of a barrel standing at axis distance d, as the camera sees it: three lines, each a row for every
    column, with u = (column - the barrel's centre column) / the barrel's width W (so u runs from -0.5 to +0.5).

    ``top``     the far rim of the lid: an arc over the lid's width (|u| <= 0.353), ``top_apex`` at the centre and
                ``top_end`` at the lid's two ends; from there the shoulder runs down to ``mid`` (the side at the widest
                part, mid-height) at |u| = 0.5.
    ``bottom``  the near rim of the base: the same upside down, ``bot_apex`` at the centre, ``bot_end`` at its ends.
    ``stripe``  the stripe's middle: an arc over the whole width, ``stripe_apex`` (the nearest point of the bulge) at
                the centre, ``mid`` at the two sides.

    The rims are circles seen from above (ellipse arcs). Between a rim's end and the widest part the side is a curve:
    the barrel's radius falls off with the square of the height above its middle (9 mm at the lid, 12.75 mm at the
    middle); a straight side predicts the shoulder twice as deep as it is seen (shape census, part A). Every row comes
    from the camera model and the barrel's sizes; nothing is fit."""
    W: float
    top_apex: float
    top_end: float
    mid: float
    stripe_apex: float
    bot_apex: float
    bot_end: float

    @classmethod
    def at(cls, cam: geo.CameraModel, d_axis_mm: float) -> "Outline":
        r = cam.barrel_rows(d_axis_mm)
        return cls(r.width_px, r.top, cam.point_row(d_axis_mm, geo.BARREL_HEIGHT_MM), cam.point_row(d_axis_mm, geo.BARREL_HEIGHT_MM / 2),
                   r.stripe_center, r.bottom, cam.point_row(d_axis_mm, 0.0))

    @staticmethod
    def _arc(u, half: float):
        return 1.0 - np.sqrt(np.clip(1.0 - (np.asarray(u, float) / half) ** 2, 0.0, 1.0))       # 0 at the centre, 1 at |u| = half

    def _rim(self, u, apex: float, end: float):
        a = np.abs(np.asarray(u, float))
        t = np.clip((a - LID_HALF) / (0.5 - LID_HALF), 0.0, 1.0)                              # 0 at the rim's end, 1 at the barrel's side
        return np.where(a <= LID_HALF, apex + (end - apex) * self._arc(u, LID_HALF), end + (self.mid - end) * (1.0 - np.sqrt(1.0 - t)))

    def top(self, u):
        return self._rim(u, self.top_apex, self.top_end)

    def bottom(self, u):
        return self._rim(u, self.bot_apex, self.bot_end)

    def stripe(self, u):
        return self.stripe_apex + (self.mid - self.stripe_apex) * self._arc(u, 0.5)


def _seen_lines(mask: np.ndarray, body: int, x0: int, x1: int, y0: int, y1: int, lim_top: int, lim_bot: int,
                max_gap: int = 3) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The three lines as they are seen, per column x0..x1: the top row of the body color joined to the stripe from
    above (walking up from the stripe's top row ``y0`` while body pixels keep appearing, gaps of ``max_gap`` rows
    allowed, not above ``lim_top``), the row after its last pixel below the stripe's bottom row ``y1`` (not below
    ``lim_bot``), and the middle row of the stripe-colored pixels in rows y0..y1 (NaN where the column holds none). A
    column with no body above (below) the stripe has its top (bottom) at the stripe: the outline is at the stripe there."""
    other = BLUE if body == ORANGE else ORANGE
    h = mask.shape[0]
    n = x1 - x0
    top, bot, mid = np.full(n, float(y0)), np.full(n, float(y1)), np.full(n, np.nan)
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
            mid[i] = y0 + ys.mean() + 0.5
    return top, bot, mid


def _outline_place(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, sx0: int, sx1: int) -> tuple[int, int] | None:
    """``pin_outline`` (2026-11-20): left and right edge of a box one barrel wide, placed by the barrel's outline, or
    None when the outline does not know where the barrel is. ``sx0``, ``sx1`` = the columns seen of the barrel.

    If an end of the seen part is the barrel's own side, the barrel is W wide from that end. So each end is asked by
    itself, and only in the columns near it (what the other end looks like, straight, slanted or a neighbour, cannot
    matter):

    1. The stripe's row gives the distance, the distance the outline (``Outline``): top line, stripe arc, bottom line.
    2. The same three lines as they are seen in the columns sx0..sx1 (``_seen_lines``).
    3. Put the outline with its side on the end. Over the columns within half a lid's width (LID_HALF x W) of the end,
       the end's cost = the LARGEST of the three lines' mean distances in rows between seen and predicted, after
       taking out each line's own up-down offset (its median): the top corner, the stripe and the bottom corner must
       each follow the outline.
    4. The end is the barrel's own side when its cost is at most pin_good x H. Exactly one such end: the box is W wide
       from it. Neither, or both: None.

    A barrel's own side has rounded corners (the top runs down and the bottom runs up over the last 0.15 W); a side
    cut by a straight edge has square ones; a slanted cut imitates one rounded corner and never both (round 1 slid the
    whole outline and took the mean of the lines: a slanted cut fooled it). A piece from the middle of a barrel has no
    such end and gets no box from here."""
    costs = _end_costs(s, mask, cam, cfg, sx0, sx1)
    if costs is None:
        return None
    left, right = costs[0] <= cfg.pin_good, costs[1] <= cfg.pin_good
    if left == right:
        return None                                                  # no end, or both ends, look like a barrel's own side
    Wi = int(round(_stripe_geometry(cam, s.center_row)[1].width_px))
    return (sx0, sx0 + Wi) if left else (sx1 - Wi, sx1)


def _end_costs(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, sx0: int, sx1: int) -> tuple[float, float] | None:
    """(cost of "the left end of the seen columns sx0..sx1 is the barrel's own side", the same for the right end), in
    barrel heights; None when the stripe's row gives no barrel. Steps 1 to 3 of ``_outline_place``. inf = no line could
    be compared at that end."""
    g = _stripe_geometry(cam, s.center_row)
    if g is None or sx1 - sx0 < 2:
        return None
    d, rows = g
    W, H = rows.width_px, rows.bottom - rows.top
    ol = Outline.at(cam, d)
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
    x0, y0, x1, y1 = s.bbox
    lines = _seen_lines(mask, s.body, sx0, sx1, y0, y1, int(rows.top - tol), int(rows.bottom + tol) + 1)
    xs = np.arange(sx0, sx1) + 0.5

    def cost(left: bool) -> float:
        centre = sx0 + W / 2 if left else sx1 - W / 2                # where the barrel's centre is if this end is its own side
        near = (xs - sx0 <= LID_HALF * W) if left else (sx1 - xs <= LID_HALF * W)
        u = (xs[near] - centre) / W
        worst = math.inf
        for seen, line in zip(lines, (ol.top, ol.bottom, ol.stripe)):
            v = seen[near]
            ok = ~np.isnan(v)
            if ok.sum() < 2:
                continue
            r = v[ok] - line(u[ok])
            c = float(np.mean(np.abs(r - np.median(r))))
            worst = c if math.isinf(worst) else max(worst, c)
        return worst / H

    return cost(True), cost(False)


def _end_closure(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, sx0: int, sx1: int) -> tuple[float, float] | None:
    """For ``own_close``: (closure of the left end of the seen columns sx0..sx1, closure of the right end), in barrel heights;
    None when the stripe's row gives no barrel. Closure = the smaller of (how far the body's top has come down from the top row the
    stripe's row predicts) and (how far its bottom has come up from the predicted bottom row), each the mean over the columns within
    CLOSE_ZONE x W of the end (at least 2). The body is looked for from the predicted rows less the edge tolerance to the stripe; a
    column with none has its top (bottom) at the stripe. At a barrel's own side both close (its corners are round); at a straight or
    slanted cut, the frame edge or a block, at least one stands (census_ends.md)."""
    g = _stripe_geometry(cam, s.center_row)
    if g is None:
        return None
    rows = g[1]
    h = mask.shape[0]
    W, H = rows.width_px, rows.bottom - rows.top
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
    x0, y0, x1, y1 = s.bbox
    lim_top, lim_bot = max(0, int(rows.top - tol)), min(h, int(rows.bottom + tol) + 1)
    n = max(2, int(round(CLOSE_ZONE * W)))
    out = []
    for cols in (range(sx0, min(sx1, sx0 + n)), range(max(sx0, sx1 - n), sx1)):
        tg, bg = [], []
        for x in cols:
            up = np.flatnonzero(mask[lim_top:y0, x] == s.body)
            dn = np.flatnonzero(mask[y1:lim_bot, x] == s.body)
            tg.append(((lim_top + up[0]) if len(up) else y0) - rows.top)
            bg.append(rows.bottom - ((y1 + dn[-1] + 1) if len(dn) else y1))
        out.append(min(float(np.mean(tg)), float(np.mean(bg))) / H if len(tg) else 0.0)
    return out[0], out[1]


def _body_crosses(mask: np.ndarray, s: Stripe, sx0: int, sx1: int) -> bool:
    """``thin_span`` (round 2): does the body color cross the stripe's rows in some column of sx0..sx1 (more than half of the
    rows y0..y1 of the stripe)? A barrel's body never crosses its own stripe; a body-colored thing in front of it does."""
    y0, y1 = s.bbox[1], s.bbox[3]
    if y1 <= y0 or sx1 <= sx0:
        return False
    return bool(((mask[y0:y1, sx0:sx1] == s.body).mean(axis=0) > 0.5).any())


def _closed_end(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, sx0: int, sx1: int) -> tuple[int, int] | None:
    """``own_close``: left and right edge of a box one barrel wide from the end of the seen part where the body has closed on the
    stripe (closure at least bottom_tol), when the other end stands (closure at most CLOSE_CUT); else None."""
    c = _end_closure(s, mask, cam, cfg, sx0, sx1)
    if c is None:
        return None
    h, w = mask.shape
    y0, y1 = s.bbox[1], s.bbox[3]
    barrel = np.isin(mask, (ORANGE, BLUE))

    def seen_edge(cols) -> bool:                                     # round 2: not against barrel color (a barrel in front is round too)
        cols = [c for c in cols if 0 <= c < w]
        return not cols or float(barrel[y0:y1, cols].any(axis=1).mean()) < 0.5
    left = c[0] >= cfg.bottom_tol and c[1] <= CLOSE_CUT and seen_edge(range(sx0 - cfg.close_px, sx0))
    right = c[1] >= cfg.bottom_tol and c[0] <= CLOSE_CUT and seen_edge(range(sx1, sx1 + cfg.close_px))
    if left == right:
        return None
    Wi = int(round(_stripe_geometry(cam, s.center_row)[1].width_px))
    return (sx0, sx0 + Wi) if left else (sx1 - Wi, sx1)


def _partly_seen(s: Stripe, mask: np.ndarray, W: float, top: int, bottom: int, pred_bottom: float, cfg: DetConfig,
                 others: tuple = (), found: tuple = (), full_slice: bool = False,
                 cam: geo.CameraModel | None = None) -> tuple[int, int] | None:
    """``side_hidden`` (2026-11-19): left and right edge of the box for a stripe narrower than stripe_full x the barrel
    width W, or None when nothing says where the rest of the barrel is. ``top``, ``bottom`` = the box's rows;
    ``pred_bottom`` = the bottom row the stripe's row predicts; ``found`` = the barrels found so far.

    1. What is seen of the barrel = the stripe's columns joined with the columns of body color above and below it
       (``_body_span``). A body wider than body_width x W holds a same-colored neighbour: only the stripe counts.
    2. Seen span >= stripe_full x W: that span is the box. The barrel is all there, only its stripe was cut.
    3. Otherwise a side counts as hidden only for a reason: (a) the seen span touches the frame edge there; (b) a found
       barrel standing nearer is there (its box holds one of the close_px pixels beside the seen span at the stripe's
       middle row, and its bottom edge is lower than pred_bottom); (c) the outline is cut there: the body and the stripe
       end at different columns, further apart than the edge tolerance (bottom_tol of W, at least bottom_tol_min_px).
       At a barrel's own edge the stripe and the body end together. (c) is asked of an untrusted body too: its far end
       is not this barrel's edge, but where it runs past the stripe the stripe is cut, and where it ends with the stripe
       that is this barrel's edge.
    4. Exactly one side hidden: W wide from the seen edge of the other side.
    5. No side or both: a stripe at least stripe_w_min x W wide is centred on what is seen; a narrower one gives None.

    ``slice_box`` (2026-11-19) changes step 5. Nothing pins the box, but the barrel holds what is seen, so it lies
    between (seen right end - W) and (seen left end + W): that span, "the cover box", holds the whole barrel wherever
    it is, and overlaps its true box by 1 / (2 - seen share) of the width, never under half. It is drawn (a) for a
    stripe stripe_w_min x W or wider: when both sides have a reason, and with ``cover_unpinned`` also when neither has
    (else centred as before); (b) for a narrower stripe (no side or both): only if ``full_slice``, i.e. the body above
    and below the stripe ends where the stripe's row predicts the top and the bottom (a slice of a barrel seen from top
    to bottom; round 2: also asked when both sides have a reason). ``stripe_two``: a part cut from a wider stripe is
    hidden on the side where it was cut.

    ``pin_outline`` (2026-11-20, needs ``cam``) also changes step 5, and comes first: with no reason on either side,
    or one on both, each end of the seen part is asked whether it is the barrel's own side (``_outline_place``); with
    exactly one such end the box is W wide from it. Otherwise step 5 is as above. ``pin_thin``: a thin piece (under the
    finder's old floor) is placed by the outline or gets no box, whatever its span and whatever reasons its sides have."""
    h, w = mask.shape
    x0, y0, x1, y1 = s.bbox
    span = _body_span(mask, s.body, x0, x1, top, bottom, y0, y1, others) if bottom - top >= 2 else None
    trusted = span is not None and max(span[1], x1) - min(span[0], x0) <= cfg.body_width * W
    sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if trusted else (x0, x1)
    thin = cfg.pin_outline and cfg.pin_thin and s.small              # pin_thin: placed by the outline, or no box
    if sx1 - sx0 >= cfg.stripe_full * W and (not thin or (cfg.thin_span and trusted and full_slice and not _body_crosses(mask, s, sx0, sx1))):
        return sx0, sx1                                              # 2. the whole width is seen (thin_span: for a thin full slice too)
    row, tol = int(s.center_row), max(cfg.bottom_tol_min_px, cfg.bottom_tol * W)
    # (c) the outline is cut where the body and the stripe end apart. Asked of every body, trusted or not (round 2): a body
    # running on into a same-colored neighbour still runs past the end of the stripe on the side where the stripe is cut
    left_cut = span is not None and abs(span[0] - x0) > tol
    right_cut = span is not None and abs(span[1] - x1) > tol
    if (cfg.stripe_two or cfg.stripe_wide) and s.merged is not None:   # a part cut from a wider stripe: its neighbour is where it was cut
        left_cut = left_cut or x0 > s.merged[0]
        right_cut = right_cut or x1 < s.merged[2]
    if span is not None and not trusted:                             # the body's far end is not this barrel's; an end shared with the stripe is
        sx0 = x0 if left_cut else min(span[0], x0)
        sx1 = x1 if right_cut else max(span[1], x1)

    def nearer(pixels) -> bool:                                      # (b) a found barrel standing nearer holds one of these pixels
        return any(b.bbox[3] > pred_bottom and b.bbox[1] <= row < b.bbox[3] and any(b.bbox[0] <= px < b.bbox[2] for px in pixels)
                   for b in found)

    Wi = int(round(W))
    if thin:
        if cfg.thin_frame and full_slice and (sx0 <= 0) != (sx1 >= w):
            # 2026-11-20 (A8): the frame edge is a hidden side that is known; a thin full slice cut by it is W wide from its other end
            return (sx1 - Wi, sx1) if sx0 <= 0 else (sx0, sx0 + Wi)
        placed = _outline_place(s, mask, cam, cfg, sx0, sx1) if cam is not None else None
        if placed is None and cfg.own_close and full_slice and cam is not None:
            placed = _closed_end(s, mask, cam, cfg, sx0, sx1)
        return placed
    left = sx0 <= 0 or nearer(range(sx0 - cfg.close_px, sx0)) or left_cut
    right = sx1 >= w or nearer(range(sx1, sx1 + cfg.close_px)) or right_cut
    if left and not right:
        return sx1 - Wi, sx1
    if right and not left:
        return sx0, sx0 + Wi
    if cfg.pin_outline and cam is not None:
        # 2026-11-20: nothing pins the box (no reason, or one on both sides). The outline does, when it fits in one place only
        placed = _outline_place(s, mask, cam, cfg, sx0, sx1)
        if placed is not None:
            return placed
    if cfg.own_close and full_slice and cam is not None:
        # 2026-11-20 (A8): the body closes on the stripe at the barrel's own side and stands at a cut one (asked of full slices only)
        placed = _closed_end(s, mask, cam, cfg, sx0, sx1)
        if placed is not None:
            return placed
    wide = (x1 - x0) >= cfg.stripe_w_min * W
    if cfg.slice_box and (((left and right) or cfg.cover_unpinned) if wide else full_slice):
        return sx1 - Wi, sx0 + Wi                                    # the cover box: every place a barrel holding the seen part can be
    if wide:
        cx = (sx0 + sx1) / 2
        return int(round(cx - W / 2)), int(round(cx + W / 2))
    return None


def barrel_from_stripe(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                       others: tuple = (), log: list | None = None, found: tuple = (), unplaced: list | None = None) -> Barrel | None:
    """One barrel from its stripe. The stripe's row gives the distance; the distance gives the full box the
    geometry predicts (top, bottom, width). The seen body extent above and below the stripe is used for an
    edge when it agrees with the prediction, otherwise the prediction is drawn and the edge flagged. A stripe
    much narrower than a barrel is partly hidden: the box is widened to a full barrel around it.
    ``unplaced`` (2026-11-20): when a list is passed, a stripe that gets no box because nothing says where the rest
    of the barrel is (``side_unexplained``) is appended to it (``post_pair`` pairs such pieces)."""
    h, w = mask.shape
    g = _stripe_geometry(cam, s.center_row)
    if g is None:
        _note(log, "barrel", "no_geometry", s.bbox, body=s.body)
        return None
    d, rows = g
    x0, y0, x1, y1 = s.bbox
    W = rows.width_px
    flags: set[str] = set()
    top_seen, bottom_seen = _body_extent(mask, s.body, x0, x1, y0, y1)
    H = rows.bottom - rows.top
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
    top = top_seen
    if abs(top_seen - rows.top) > tol:
        top = int(round(rows.top)); flags.add("top_inferred")
    bottom = bottom_seen
    if abs(bottom_seen - rows.bottom) > tol and not (bottom_seen >= h and rows.bottom >= h):
        bottom = int(round(rows.bottom)); flags.add("bottom_inferred")
    if cfg.edge_check:
        # 2026-11-19: an edge is seen only against something that is not a barrel. "Against the other barrel color" = that color in
        # at least half of the stripe's columns, in the rows right beyond the seen end (the 3-row gap the body walk allows, + 1)
        other_c = BLUE if s.body == ORANGE else ORANGE

        def against(r0: int, r1: int) -> bool:
            band = mask[max(0, r0):max(0, min(h, r1)), x0:x1]
            return band.size > 0 and float((band == other_c).any(axis=0).mean()) >= 0.5
        if {"top_inferred", "bottom_inferred"} <= flags and against(top_seen - 4, top_seen):
            # (a) neither edge is where the stripe's row predicts it, and the body above ends against barrel color inside this
            # barrel's own box: that thing stands behind and cannot hide a top. The "stripe" is a piece of another barrel
            _note(log, "barrel", "top_against_barrel", s.bbox, body=s.body)
            return None
        if "bottom_inferred" not in flags and int(round(rows.bottom)) > bottom_seen and against(bottom_seen, bottom_seen + 4):
            # (b) the seen bottom ends against another barrel: the barrel may go on behind it. The lower of the two bottoms
            bottom = int(round(rows.bottom)); flags.add("bottom_inferred")
    thin = cfg.pin_outline and cfg.pin_thin and s.small
    if (cfg.slice_box or thin) and s.small and ({"top_inferred", "bottom_inferred"} & flags):
        # round 2: a piece under the floor of before slice_box is a barrel only as a slice seen from top to bottom, with or
        # without a reason for a side (a reason says where a barrel would be, not that there is one). pin_thin asks the same
        _note(log, "barrel", "slice_not_full", s.bbox, body=s.body, expected_w=W)
        return None
    if (x1 - x0) < cfg.stripe_full * W and cfg.side_hidden:
        # 2026-11-19: partly seen. The box comes from what is seen of the barrel; a side is hidden only for a reason
        sides = _partly_seen(s, mask, W, max(0, top), min(h, bottom), rows.bottom, cfg, others, found,
                             full_slice=not ({"top_inferred", "bottom_inferred"} & flags), cam=cam)
        if sides is None:
            _note(log, "barrel", "outline_unknown" if thin else "side_unexplained", s.bbox, body=s.body, expected_w=W)
            if unplaced is not None and not s.small:         # a thin piece was handed over by the finder already (its ``narrow`` twin)
                unplaced.append(s)
            return None
        bx0, bx1 = sides
        flags.add("occluded")
    elif (x1 - x0) < cfg.stripe_full * W:
        # partly hidden: widen to a full barrel on the side where something barrel-colored (the occluder)
        # borders the stripe; if neither or both sides are bordered, centre the full width on what is seen
        row = int(s.center_row)
        # the hidden side: something barrel-colored borders the stripe there, or the frame edge cuts it (2026-11-08, (e))
        left_hidden = x0 <= 0 or mask[row, x0 - 1] in (ORANGE, BLUE)
        right_hidden = x1 >= w or mask[row, x1] in (ORANGE, BLUE)
        Wi = int(round(W))
        sx0, sx1 = x0, x1                                  # what is seen of the barrel, left to right
        if cfg.occl_body_side and min(h, bottom) - max(0, top) >= 2:
            # (h) 2026-11-11: the body above and below the stripe often shows more of the barrel than the stripe does
            # (an occluder with a slanted edge, a stripe end lost to shadow). Take the body columns joined to the
            # stripe; a span wider than a barrel can be is a same-color neighbour's body and is not trusted.
            cx0, cx1 = _body_columns(mask, s.body, x0, x1, max(0, top), min(h, bottom), y0, y1, cap_px=math.inf, others=others)
            if cx1 - cx0 <= cfg.body_width * W:
                sx0, sx1 = min(cx0, x0), max(cx1, x1)
        if (sx1 - sx0) >= cfg.stripe_full * W:
            bx0, bx1 = sx0, sx1                            # the body shows (nearly) the whole width: that is the box
        elif left_hidden and not right_hidden:
            bx0, bx1 = sx1 - Wi, sx1
        elif right_hidden and not left_hidden:
            bx0, bx1 = sx0, sx0 + Wi
        else:
            cx = (sx0 + sx1) / 2
            bx0, bx1 = int(round(cx - W / 2)), int(round(cx + W / 2))
        flags.add("occluded")
    else:
        bx0, bx1 = x0, x1
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


def _piece_of_found(s: Stripe, made: list) -> bool:
    """``slice_box`` (2026-11-19): is the partly seen stripe ``s`` a second piece of the stripe of a barrel already
    found? Yes when it shares rows with that barrel's stripe (half the height of the shorter of the two, as in
    ``_join_pieces``), has its body color, and its middle column is inside that barrel's box: two barrels cannot both
    have their stripe at the same rows inside one barrel's box. ``made`` = the (stripe, barrel) pairs so far."""
    x0, y0, x1, y1 = s.bbox
    mid = (x0 + x1) / 2
    for o, b in made:
        shared = min(y1, o.bbox[3]) - max(y0, o.bbox[1])
        if o.body == s.body and 2 * shared >= min(y1 - y0, o.bbox[3] - o.bbox[1]) and b.bbox[0] <= mid < b.bbox[2]:
            return True
    return False


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
    aside = cfg.post_pair or cfg.slice_behind                # 2026-11-20: pieces that give no box alone are kept for these two
    narrows: list[Stripe] = []                               # ... refused by the finder for their width
    unplaced: list[Stripe] = []                              # ... or left without a box because no side has a reason
    stripes = find_stripes(mask, cam, cfg, log, narrow=narrows if aside else None)
    used: list[Stripe] = []                                  # the stripes that gave a barrel
    made: list[tuple[Stripe, Barrel]] = []                   # ... each with the barrel it gave (the ones in ``out``)
    order = stripes

    def partly(s: Stripe) -> bool:
        g = _stripe_geometry(cam, s.center_row)
        return g is not None and (s.bbox[2] - s.bbox[0]) < cfg.stripe_full * g[1].width_px
    if cfg.side_hidden:
        # 2026-11-19: the barrels whose stripe is seen whole first, then the partly seen ones, nearest first: a partly seen
        # stripe may be hidden by a barrel already found
        order = [s for s in stripes if not partly(s)] + sorted((s for s in stripes if partly(s)), key=lambda s: -s.center_row)
    # 2026-11-20, pin_thin: the thin pieces the lower floor lets in. They never change another barrel's box: they are not among
    # the "other stripes" whose columns a barrel's body may not take, and they never replace a box as its duplicate
    thin_on = cfg.side_hidden and cfg.pin_outline and cfg.pin_thin
    for s in order:
        if (cfg.side_hidden and s.merged is None and partly(s) and (cfg.slice_box or cfg.stripe_bridge or (thin_on and s.small))
                and _piece_of_found(s, made)):
            _note(log, "barrel", "stripe_piece", s.bbox, body=s.body)
            continue                                         # a second piece of a found barrel's stripe, not another barrel
        others = tuple((o.bbox[0], o.bbox[2]) for o in stripes if o is not s and not (thin_on and not cfg.slice_box and o.small))
        b = barrel_from_stripe(s, mask, cam, cfg, others=others, log=log, found=tuple(out), unplaced=unplaced if aside else None)
        if b is None:
            continue
        if (cfg.pin_outline or cfg.own_close) and any(o.color == b.color and box_iou(o.bbox, b.bbox) > 0.5 for o in out):
            # 2026-11-20 (round 2): a box the outline places never takes the place of a box that is already there. If this
            # one would be a found barrel's duplicate, the piece is treated as before the switch (a thin piece: no box)
            if thin_on and s.small:
                _note(log, "barrel", "duplicate", s.bbox, body=s.body, box=b.bbox)
                continue
            b = barrel_from_stripe(s, mask, cam, replace(cfg, pin_outline=False, own_close=False), others=others, found=tuple(out),
                                   unplaced=unplaced if aside else None)      # ... and may wait for post_pair, as before the switch
            if b is None:
                continue
        used.append(s)
        _note(log, "barrel", "kept", s.bbox, body=s.body, box=b.bbox)

        def sibling(o: Barrel) -> bool:                      # stripe_two: o came from another part of the same wide stripe
            return (cfg.stripe_two or cfg.stripe_wide) and s.merged is not None and any(mb is o and ms.merged == s.merged for ms, mb in made)
        dup = next((o for o in out if o.color == b.color and box_iou(o.bbox, b.bbox) > 0.5 and not sibling(o)), None)
        if dup is not None:
            _note(log, "barrel", "duplicate", s.bbox, body=s.body, box=b.bbox)
            if b.confidence > dup.confidence and not (thin_on and s.small):
                out.remove(dup); out.append(b)
                made = [(ms, mb) for ms, mb in made if mb is not dup] + [(s, b)]
            continue
        out.append(b); made.append((s, b))
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
    if cfg.cap_behind:
        out += caps_behind(mask, out, used, cam, cfg, log)
    # 2026-11-20: what is left over, after everything above (so nothing above changes, and no cap leans on these boxes)
    if aside:
        left = narrows + unplaced
        if cfg.post_pair:
            pairs, paired = post_pairs(left, mask, out, cam, cfg, log, made=tuple(made))
            out += pairs
            left = [s for s in left if not any(s is p for p in paired)]
        if cfg.slice_behind:
            out += slices_behind([s for s in left if s.narrow], mask, out, cam, cfg, log, made=tuple(made))
    if cfg.half_stripe:
        new, replaced = half_stripes(mask, out, made, cam, cfg, log)
        out = [b for b in out if not any(b is r for r in replaced)] + new
    return sorted(out, key=lambda b: b.bbox[0])


def caps_behind(mask: np.ndarray, found: list[Barrel], used: list[Stripe], cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                log: list | None = None) -> list[Barrel]:
    """``cap_behind`` (2026-11-18): barrels standing behind a found barrel. Such a barrel shows its upper body (its
    "cap") above the front barrel; its stripe has melted into the front barrel's body of the same color, or is
    hidden, so the stripe step cannot find it. ``found`` = the barrels found so far, ``used`` = the stripes that gave
    them. Per color: take that color's pixels without the boxes of the used stripes; a connected piece is a cap when

    1. it is not a found barrel's own body (fewer than half of its pixels inside found boxes of its color);
    2. its top row gives the distance, hence the expected width W, height H and upper-body height (top row to the
       top of the stripe), and the piece is barrel-wide (width_min to body_width x W) and as tall as an upper body,
       not more (height_min x the upper body, to the upper body + the usual edge tolerance);
    3. what hides the rest is a barrel: at least half of the predicted box below the cap lies inside boxes of
       found barrels whose bottom edge is lower than this barrel's (they stand nearer).

    The box: top = the cap's top row; sides = the cap's columns. A cap narrower than stripe_full x W is kept only
    when exactly one side is hidden by a nearer found barrel or the frame edge, and is widened to W toward that side.
    Bottom = top + the height of a barrel as wide as the cap when the whole width shows, else the bottom the top row
    predicts; the cap's own color seen ending near that estimate (the usual tolerance) replaces it. No new threshold.

    ``cap_seen_bottom`` (2026-11-19, A5), for a narrow cap with no such seen end: the top-row estimate is 4 to 7 px
    low at mid and far range with this camera, so a seen end can be refused for the estimate's error. Then the cap's
    color is read in the cap's columns outside the boxes of the nearer found barrels (inside them that color is the
    front barrel's stripe); seen ending between the bottom of a barrel only as wide as the seen cap (the barrel is at
    least that big, whatever the tilt) and the estimate + the tolerance, that end is the bottom."""
    h, w = mask.shape
    out: list[Barrel] = []
    for c in (ORANGE, BLUE):
        cm = _closed(mask == c, cfg)
        for s in used:
            if s.body != c:                                  # a stripe of this color, on a barrel of the other color
                x0, y0, x1, y1 = s.bbox
                cm[y0:y1, x0:x1] = False
        own = np.zeros(mask.shape, bool)
        for b in found:
            if b.color == c:
                own[b.bbox[1]:b.bbox[3], b.bbox[0]:b.bbox[2]] = True
        n, lab, st, _ = cv2.connectedComponentsWithStats(cm.astype(np.uint8), connectivity=8)
        cands = []                                           # (x, y, width, height, area) of the pieces to test
        for i in range(1, n):
            if int(st[i][4]) < cfg.min_area_px:
                continue
            if 2 * int((own & (lab == i)).sum()) < int(st[i][4]):
                cands.append(tuple(int(v) for v in st[i]))
            elif cfg.cap_same:
                # 1. a found barrel's own body was skipped whole. cap_same (2026-11-19): what of it lies OUTSIDE the found boxes of
                # its color is tested, each connected part by itself (the top of a barrel behind a found barrel of its own color)
                n2, _, st2, _ = cv2.connectedComponentsWithStats(((lab == i) & ~own).astype(np.uint8), connectivity=8)
                cands += [tuple(int(v) for v in st2[j]) for j in range(1, n2)]
        for x, y, bw, bh, area in cands:
            if area < cfg.min_area_px or y <= 0:
                continue                                     # a speck, or the top is cut by the frame: no top row to read
            d = cam._d_axis_from_point_row(y, geo.BARREL_HEIGHT_MM, +geo.BARREL_END_DIAMETER_MM / 2)
            if not math.isfinite(d) or d <= geo.BARREL_BULGE_DIAMETER_MM / 2 + 1:
                continue
            rows = cam.barrel_rows(d)
            W, H, upper = rows.width_px, rows.bottom - rows.top, rows.stripe_top - rows.top
            cb = (x, y, x + bw, y + bh)
            if W < cfg.min_width_px:
                continue                                     # above the table's far end
            tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
            if not (cfg.width_min * W <= bw <= max(cfg.body_width, 1.0) * W):
                _note(log, "cap", "width", cb, body=c, expected_w=W)
                continue                                     # 2. not barrel-wide for its row
            # cap_low (2026-11-20): the floor is width_min ("narrower than this is a sliver") instead of height_min: a barrel three
            # quarters hidden by one straight in front shows 0.55 of an upper body, less the rows lost at the seam
            if not ((cfg.width_min if cfg.cap_low else cfg.height_min) * upper <= bh <= upper + tol):
                _note(log, "cap", "height", cb, body=c, expected_upper_h=upper)
                continue                                     # 2. not as tall as an upper body (taller: body color where the stripe must be)
            bx0, bx1 = x, x + bw
            if bw >= cfg.stripe_full * W:
                bottom = y + cam.expected_barrel_height_px(d_axis_mm=cam.f * geo.BARREL_BULGE_DIAMETER_MM / bw)   # the whole width shows: size from width
            else:
                # a narrow cap must be explained (round 2): exactly one side hidden, by a found barrel standing nearer (its box
                # holds the pixel next to the cap at the cap's middle row) or by the frame edge. Neither side: the narrowness has
                # no cause, not a cap. Both sides: a wedge between two barrels, neither its width nor its place can be measured.
                row, Wi = y + bh // 2, int(round(W))

                def hidden(px: int) -> bool:
                    return px < 0 or px >= w or any(b.bbox[0] <= px < b.bbox[2] and b.bbox[1] <= row < b.bbox[3] and b.bbox[3] > y + bh
                                                    for b in found)
                left_hidden, right_hidden = hidden(x - 1), hidden(x + bw)
                if left_hidden == right_hidden:
                    _note(log, "cap", "both_sides" if left_hidden else "narrow", cb, body=c, expected_w=W)
                    continue
                bottom = rows.bottom                         # size from the top row
                if left_hidden:
                    bx0 = bx1 - Wi
                else:
                    bx1 = bx0 + Wi
            # the seen bottom is used when it agrees (as in step 3): the cap's own color, in the cap's columns, ending near the estimate
            col = (mask[:, x:x + bw] == c).any(axis=1)
            near = [r for r in range(max(y + bh, int(round(bottom - tol))), min(h, int(round(bottom + tol)) + 1)) if col[r]]
            if near and not col[near[-1] + 1:near[-1] + 4].any():
                bottom = near[-1] + 1
            elif cfg.cap_seen_bottom and bw < cfg.stripe_full * W:
                # 2026-11-19 (A5): a narrow cap's estimate is the top-row bottom, 4 to 7 px low at mid and far range, so a seen end
                # can be refused for the estimate's error. Read the cap's color only beside the nearer found barrels (inside their
                # boxes it is their stripe). The barrel is at least as wide as what is seen of it, so its bottom is not above that
                # of a barrel bw wide (a bound that does not depend on the tilt), and not below the estimate + the tolerance
                beside = np.ones(bw, bool)
                for b in found:
                    if b.bbox[3] > y + bh:
                        beside[max(0, b.bbox[0] - x):max(0, b.bbox[2] - x)] = False
                least = y + cam.expected_barrel_height_px(d_axis_mm=cam.f * geo.BARREL_BULGE_DIAMETER_MM / bw)
                col = (mask[:, x:x + bw][:, beside] == c).any(axis=1)
                seen = [r for r in range(max(y + bh, int(round(least))), min(h, int(round(bottom + tol)) + 1)) if col[r]]
                if seen and not col[seen[-1] + 1:seen[-1] + 4].any():
                    bottom = seen[-1] + 1
            bx0, bx1, bottom = max(0, bx0), min(w, bx1), min(h, int(round(bottom)))
            below = np.zeros((max(0, bottom - (y + bh)), bx1 - bx0), bool)       # where the rest of this barrel should be
            for b in found:
                if b.bbox[3] > bottom:                       # a found barrel standing nearer
                    below[max(0, b.bbox[1] - (y + bh)):max(0, b.bbox[3] - (y + bh)), max(0, b.bbox[0] - bx0):max(0, b.bbox[2] - bx0)] = True
            if below.size == 0 or below.mean() < 0.5:
                _note(log, "cap", "not_hidden", cb, body=c, hidden_frac=float(below.mean()) if below.size else 0.0)
                continue                                     # 3. nothing found stands in front of it
            box = (bx0, y, bx1, bottom)
            if any(o.color == c and box_iou(o.bbox, box) > 0.5 for o in found + out):
                _note(log, "cap", "duplicate", cb, body=c, box=box)
                continue
            flags = {"occluded", "bottom_inferred"}
            if bx0 == 0 or bx1 == w or bottom == h:
                flags.add("truncated")
            _note(log, "cap", "kept", cb, body=c, box=box)
            out.append(Barrel(color=c, bbox=box, confidence=0.5, flags=frozenset(flags), area=area, source="det3"))
    return out


# ---------------------------------------------------------------- 2026-11-20: hidden from above or below, a post, a slice beside a barrel

def _full_slice(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig):
    """For a narrow stripe piece: (W, rows, top, bottom, sx0, sx1) when it is a FULL SLICE of a barrel, else None. A full
    slice: the body color above and below the piece ends where the piece's row predicts the barrel's top and bottom
    (the usual edge tolerance: bottom_tol of the height, at least bottom_tol_min_px), and neither end lies against the
    other barrel color. ``top``, ``bottom`` = those seen ends; ``sx0``, ``sx1`` = the piece's columns joined with the body
    joined to it (``_body_span``)."""
    g = _stripe_geometry(cam, s.center_row)
    if g is None:
        return None
    rows = g[1]
    x0, y0, x1, y1 = s.bbox
    top, bottom = _body_extent(mask, s.body, x0, x1, y0, y1)
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * (rows.bottom - rows.top))
    if abs(top - rows.top) > tol or abs(bottom - rows.bottom) > tol:
        return None
    # round 2: both ends are seen edges, i.e. not against the other barrel color (edge_check's test: that color in at least half
    # of the piece's columns in the 4 rows beyond the end). A strip of a barrel's upper body between a finger and its own stripe
    # is "a full slice" of a barrel of the other color whose bottom is that barrel's lower body
    other = BLUE if s.body == ORANGE else ORANGE
    for band in (mask[max(0, top - 4):max(0, top), x0:x1], mask[bottom:bottom + 4, x0:x1]):
        if band.size and float((band == other).any(axis=0).mean()) >= 0.5:
            return None
    span = _body_span(mask, s.body, x0, x1, max(0, top), min(mask.shape[0], bottom), y0, y1) if bottom - top >= 2 else None
    sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if span else (x0, x1)
    return rows.width_px, rows, top, bottom, sx0, sx1


def post_pairs(pieces: list[Stripe], mask: np.ndarray, found: list[Barrel], cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
               log: list | None = None, made: tuple = ()) -> tuple[list[Barrel], list[Stripe]]:
    """``post_pair`` (2026-11-20): one barrel behind a post. ``pieces`` = the stripe pieces that gave no box alone (under
    the finder's width floor, or left without a box because no side has a reason); a piece of a found barrel's own stripe
    (``_piece_of_found`` with ``made``, the stripe step's (stripe, barrel) pairs) is left out. Two of them are one barrel when

    1. each is under stripe_w_min x the barrel width W wide (a wider piece is placed alone);
    2. they have one body color and share rows: the overlap is at least half the height of the shorter (as ``stripe_join``);
    3. each is a full slice (``_full_slice``): its body ends where its row predicts the top and the bottom;
    4. their outer body edges are stripe_full to body_width x W apart, the left piece wholly left of the right one.

    Two barrels at one distance cannot have their outer edges within 1.2 W of each other, so the two slices are one
    barrel with something upright in front of its middle (or with its stripe and body cut by a highlight). The box runs
    from outer edge to outer edge; top and bottom are the seen ones. No new number.
    Returns (the barrels, the pieces they used)."""
    h, w = mask.shape
    info = []
    for s in sorted(pieces, key=lambda s: s.bbox[0]):
        f = None if _piece_of_found(s, made) else _full_slice(s, mask, cam, cfg)
        if f is not None and (s.bbox[2] - s.bbox[0]) < cfg.stripe_w_min * f[0]:
            info.append((s, *f))
    out: list[Barrel] = []
    paired: list[Stripe] = []
    for i, (l, Wl, _, tl, bl, lx0, _) in enumerate(info):
        for r, Wr, _, tr, br, _, rx1 in info[i + 1:]:
            if any(l is p or r is p for p in paired) or l.body != r.body or r.bbox[0] < l.bbox[2]:
                continue
            shared = min(l.bbox[3], r.bbox[3]) - max(l.bbox[1], r.bbox[1])
            if 2 * shared < min(l.bbox[3] - l.bbox[1], r.bbox[3] - r.bbox[1]):
                continue
            W = (Wl + Wr) / 2
            if not (cfg.stripe_full * W <= rx1 - lx0 <= max(cfg.body_width, 1.0) * W):
                continue
            box = (max(0, lx0), max(0, min(tl, tr)), min(w, rx1), min(h, max(bl, br)))
            if any(o.color == l.body and box_iou(o.bbox, box) > 0.5 for o in found + out):
                _note(log, "pair", "duplicate", l.bbox, body=l.body, box=box)
                continue
            flags = {"occluded"} | ({"truncated"} if box[0] == 0 or box[2] == w or box[1] == 0 or box[3] == h else set())
            out.append(Barrel(color=l.body, bbox=box, confidence=0.5, flags=frozenset(flags), area=l.n_other + r.n_other, source="det2"))
            paired += [l, r]
            _note(log, "pair", "kept", l.bbox, body=l.body, box=box, other=r.bbox, expected_w=W, outer_span=rx1 - lx0)
    return out, paired


def slices_behind(pieces: list[Stripe], mask: np.ndarray, found: list[Barrel], cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                  log: list | None = None, made: tuple = ()) -> list[Barrel]:
    """``slice_behind`` (2026-11-20): a barrel of which only a narrow slice shows beside a found barrel standing nearer.
    ``pieces`` = the stripe pieces the finder refused for their width (narrower than a stripe is tall, or taller than
    wide); a piece of a found barrel's own stripe (``_piece_of_found`` with ``made``) is left out.
    Such a piece is a barrel when it is a full slice (``_full_slice``) and exactly one of its sides is hidden for a
    reason that can be seen: the frame edge, or a found barrel standing nearer (its box holds one of the close_px pixels
    beside the seen span at the piece's middle row, and its bottom edge is lower than the bottom the piece's row
    predicts). The box is a barrel wide from the seen edge of the other side; top and bottom as seen. A body wider than
    body_width x W holds a same-colored neighbour: then only the piece's own columns count as seen. No new number."""
    h, w = mask.shape
    out: list[Barrel] = []
    for s in sorted(pieces, key=lambda s: -s.center_row):            # nearest first, as the partly seen stripes
        if _piece_of_found(s, made):
            _note(log, "slice", "stripe_piece", s.bbox, body=s.body)
            continue
        f = _full_slice(s, mask, cam, cfg)
        if f is None:
            _note(log, "slice", "not_full", s.bbox, body=s.body)
            continue
        W, rows, top, bottom, sx0, sx1 = f
        if sx1 - sx0 > cfg.body_width * W:
            sx0, sx1 = s.bbox[0], s.bbox[2]
        row = int(s.center_row)

        def nearer(pixels) -> bool:
            return any(b.bbox[3] > rows.bottom and b.bbox[1] <= row < b.bbox[3] and any(b.bbox[0] <= px < b.bbox[2] for px in pixels)
                       for b in found + out)
        left = sx0 <= 0 or nearer(range(sx0 - cfg.close_px, sx0))
        right = sx1 >= w or nearer(range(sx1, sx1 + cfg.close_px))
        if left == right:
            _note(log, "slice", "both_sides" if left else "no_reason", s.bbox, body=s.body)
            continue
        Wi = int(round(W))
        bx0, bx1 = (sx1 - Wi, sx1) if left else (sx0, sx0 + Wi)
        box = (max(0, bx0), max(0, top), min(w, bx1), min(h, bottom))
        if box[2] - box[0] < 2 or box[3] - box[1] < 2:
            continue
        if any(o.color == s.body and box_iou(o.bbox, box) > 0.5 for o in found + out):
            _note(log, "slice", "duplicate", s.bbox, body=s.body, box=box)
            continue
        flags = {"occluded"} | ({"truncated"} if box[0] == 0 or box[2] == w or box[1] == 0 or box[3] == h else set())
        out.append(Barrel(color=s.body, bbox=box, confidence=0.5, flags=frozenset(flags), area=s.n_other, source="det2"))
        _note(log, "slice", "kept", s.bbox, body=s.body, box=box, expected_w=W, seen=(sx0, sx1), hidden_side="left" if left else "right",
              predicted_top=rows.top, predicted_bottom=rows.bottom)
    return out


def half_stripes(mask: np.ndarray, found: list[Barrel], made: list, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                 log: list | None = None) -> tuple[list[Barrel], list[Barrel]]:
    """``half_stripe`` (2026-11-20): barrels hidden from above or from below by something that is not a barrel, found from
    a stripe that has body color on ONE side only. ``found`` = the barrels found so far; ``made`` = the (stripe, barrel)
    pairs of the stripe step.

    A band = a connected piece (min_area_px or more) of one barrel color. "Body right above" a column of it = the other
    barrel color within band_h_max stripe heights above the band there (the stripe finder's sandwich, one side). The
    band is "bottom hidden" when it has body right above in at least stripe_full of its columns and right below in at
    most 1 - stripe_full of them (the upper body and the stripe show), "top hidden" in the reverse case (the stripe and
    the lower body show). The seam between band and body gives the distance: the stripe's top edge is 15 mm above the
    table and its bottom edge 9 mm, at the bulge. From it: the barrel's width W, its top and bottom rows, the stripe
    height. The band is a barrel's stripe when

    1. it is not taller than a stripe (stripe_h_max x the stripe height) and, unless ``half_thin``, at least stripe_h_min of it;
    2. the whole width shows: the band is stripe_full to body_width x W wide;
    3. the second reading agrees: the body's far edge (its top when the bottom is hidden, its bottom when the top is) is
       where the seam predicts it, within the usual edge tolerance, and inside the frame;
    4. the body joined to the band is stripe_full to body_width x W wide;
    5. the open side is clear: barrel color in the 4 rows beyond the band in fewer than half of its columns;
    6. the body's far edge is a seen edge: not against barrel color (the same test beyond that edge). An ordinary barrel's
       upper body and stripe pass 1 to 5 as the "stripe and lower body" of a smaller barrel of the other color; its
       "bottom" ends against the real barrel's lower body;
    7. it is not a found barrel's: fewer than half of the band's pixels inside found boxes, and no found box of its color
       overlapping the new box by more than half;
    8. (round 2) it is the thinner band: less tall than the body part beside it (seam to far edge). A stripe is 6 mm, a body
       part 9 mm or more; a barrel hidden from below whose stripe shows whole would otherwise also pass as a smaller barrel
       of the other color hidden from above (its upper body as the stripe, its stripe as the lower body).

    The box: sides = the seen band and body; the seen far edge; the hidden edge where the seam's distance predicts it
    (flags occluded and bottom_inferred or top_inferred). A box the stripe step made from a narrow, partly seen piece of
    this same band (its stripe lies inside the band's box) is replaced by this one: the band shows the whole width, the
    piece was a corner of it; such a box is not "found" in test 7. No new number.
    Returns (the barrels, the found barrels they replace)."""
    h, w = mask.shape
    rows_idx = np.arange(h)[:, None]
    reach = _reach_by_row(cam, h, cfg)[:, None]
    barrel = np.isin(mask, (ORANGE, BLUE))
    bulge_r = geo.BARREL_BULGE_DIAMETER_MM / 2
    z_top, z_bottom = (geo.BARREL_HEIGHT_MM + geo.STRIPE_HEIGHT_MM) / 2, (geo.BARREL_HEIGHT_MM - geo.STRIPE_HEIGHT_MM) / 2
    out: list[Barrel] = []
    replaced: list[Barrel] = []
    for body in (ORANGE, BLUE):
        other = BLUE if body == ORANGE else ORANGE
        bm = _closed(mask == body, cfg)
        om = _closed(mask == other, cfg) & ~bm
        up = np.maximum.accumulate(np.where(bm, rows_idx, -10 ** 6), axis=0)              # last body row at or above
        dn = np.minimum.accumulate(np.where(bm, rows_idx, 10 ** 6)[::-1], axis=0)[::-1]   # first body row at or below
        above, below = (rows_idx - up) <= reach, (dn - rows_idx) <= reach
        n, lab, st, _ = cv2.connectedComponentsWithStats(om.astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, bw, bh, area = (int(v) for v in st[i])
            if area < cfg.min_area_px:
                continue
            sel = lab[y:y + bh, x:x + bw] == i                                             # the band, in its own box
            cols = np.flatnonzero(sel.any(axis=0))
            fa = float((sel & above[y:y + bh, x:x + bw]).any(axis=0)[cols].mean())
            fb = float((sel & below[y:y + bh, x:x + bw]).any(axis=0)[cols].mean())
            if fb >= cfg.stripe_full and fa <= 1 - cfg.stripe_full:
                top_hidden = True
            elif fa >= cfg.stripe_full and fb <= 1 - cfg.stripe_full:
                top_hidden = False
            else:
                continue                                                                   # body on both sides (a stripe) or on neither
            sb = (x, y, x + bw, y + bh)
            first = y + np.argmax(sel[:, cols], axis=0)                                    # first and last band row, per column
            last = y + bh - 1 - np.argmax(sel[::-1][:, cols], axis=0)
            if top_hidden:
                seams = dn[last, x + cols]; seams = seams[seams < 10 ** 5]                 # first body row under the band
                seam, z = (float(np.median(seams)) if len(seams) else math.nan), z_bottom
            else:
                seams = up[first, x + cols]; seams = seams[seams > -10 ** 5]               # one past the last body row above it
                seam, z = (float(np.median(seams)) + 1 if len(seams) else math.nan), z_top
            d = cam._d_axis_from_point_row(seam, z, -bulge_r) if math.isfinite(seam) else math.inf
            if not math.isfinite(d) or d <= bulge_r + 1:
                continue
            rows = cam.barrel_rows(d)
            W, H, Hs = rows.width_px, rows.bottom - rows.top, rows.stripe_bottom - rows.stripe_top
            if W < cfg.min_width_px or Hs < cfg.min_stripe_px:
                continue
            ys = np.where(sel)[0]
            core_h = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
            if core_h > cfg.stripe_h_max * Hs or (core_h < cfg.stripe_h_min * Hs and not cfg.half_thin):
                _note(log, "half", "height", sb, body=body, core_h=core_h, expected_stripe_h=Hs)
                continue                                                                   # 1.
            if not (cfg.stripe_full * W <= bw <= max(cfg.body_width, 1.0) * W):
                _note(log, "half", "width", sb, body=body, expected_w=W)
                continue                                                                   # 2.
            tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
            top_s, bottom_s = _body_extent(mask, body, x, x + bw, y, y + bh)
            if top_hidden:
                agrees, r0, r1 = abs(bottom_s - rows.bottom) <= tol and bottom_s < h, y, bottom_s
            else:
                agrees, r0, r1 = abs(top_s - rows.top) <= tol and top_s > 0, top_s, y + bh
            if not agrees:
                _note(log, "half", "far_edge", sb, body=body, seen=bottom_s if top_hidden else top_s, predicted=rows.bottom if top_hidden else rows.top)
                continue                                                                   # 3.
            if core_h >= ((bottom_s - seam) if top_hidden else (seam - top_s)):
                # round 2: the stripe is the thinner band (6 mm against a body part of 9 mm or more). A barrel hidden from below whose
                # stripe shows whole passes 1 to 6 the other way round too: its upper body as "a stripe", its stripe as "a lower body"
                _note(log, "half", "thicker_than_body", sb, body=body, core_h=core_h)
                continue
            span = _body_span(mask, body, x, x + bw, r0, r1, y, y + bh) if r1 - r0 >= 2 else None
            sx0, sx1 = (min(span[0], x), max(span[1], x + bw)) if span else (x, x + bw)
            if span is None or not (cfg.stripe_full * W <= sx1 - sx0 <= max(cfg.body_width, 1.0) * W):
                _note(log, "half", "body_width", sb, body=body, expected_w=W)
                continue                                                                   # 4.
            beyond = [(max(0, f - 4), f) for f in first] if top_hidden else [(l + 1, min(h, l + 5)) for l in last]
            if float(np.mean([barrel[a:b, x + c].any() for (a, b), c in zip(beyond, cols)])) >= 0.5:
                _note(log, "half", "open_side", sb, body=body)
                continue                                                                   # 5.
            far = barrel[bottom_s:min(h, bottom_s + 4), x:x + bw] if top_hidden else barrel[max(0, top_s - 4):max(0, top_s), x:x + bw]
            if far.size and float(far.any(axis=0).mean()) >= 0.5:
                _note(log, "half", "far_edge_against_barrel", sb, body=body)
                continue                                                                   # 6.
            box = (max(0, sx0), max(0, int(round(rows.top))) if top_hidden else top_s, min(w, sx1), bottom_s if top_hidden else min(h, int(round(rows.bottom))))
            if box[2] - box[0] < 2 or box[3] - box[1] < 2:
                continue
            # boxes the stripe step made from a narrow, partly seen piece of this same band
            corners = [b for s, b in made if s.body == body and "occluded" in b.flags and x <= s.bbox[0] and s.bbox[2] <= x + bw
                       and y <= s.bbox[1] and s.bbox[3] <= y + bh and any(b is o for o in found)]
            others = [b for b in found + out if not any(b is c for c in corners)]
            inside = np.zeros(sel.shape, bool)
            for b in others:
                inside[max(0, b.bbox[1] - y):max(0, b.bbox[3] - y), max(0, b.bbox[0] - x):max(0, b.bbox[2] - x)] = True
            if 2 * int((sel & inside).sum()) >= area or any(o.color == body and box_iou(o.bbox, box) > 0.5 for o in others):
                _note(log, "half", "found", sb, body=body, box=box)
                continue                                                                   # 7.
            flags = {"occluded", "top_inferred" if top_hidden else "bottom_inferred"}
            if box[0] == 0 or box[2] == w or box[1] == 0 or box[3] == h:
                flags.add("truncated")
            out.append(Barrel(color=body, bbox=box, confidence=0.5, flags=frozenset(flags), area=area, source="det2"))
            replaced += corners
            _note(log, "half", "kept", sb, body=body, box=box, hidden="top" if top_hidden else "bottom", seam=seam, distance_mm=d, expected_w=W,
                  expected_h=H, expected_stripe_h=Hs, core_h=core_h, predicted_top=rows.top, predicted_bottom=rows.bottom, tol=tol,
                  seen_far_edge=bottom_s if top_hidden else top_s, body_span=(sx0, sx1))
    return out, replaced


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
