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
  2026-11-20 (sliver, experiments/2026-11-20_occl_sliver)  a thin full slice whose body shows the barrel's whole width gets that width
                       (``thin_span``, on). Built and off (each failed one clause of the pre-registered rule): two stripe pieces with
                       body over the whole gap are one stripe (``stripe_bridge``); a thin full slice cut by the frame edge is W wide
                       from its other end (``thin_frame``); the end where the body closes on the stripe is the barrel's own side
                       (``own_close``).
  2026-11-20 (combined)  the two branches of 2026-11-20 together (experiments/2026-11-20_occl_combined): on by default
                       are half_stripe, half_thin, post_pair, stripe_wide, cap_low, pin_outline and pin_thin; slice_behind
                       is off (false boxes on damaged masks), as are slice_box, cover_unpinned and stripe_two. A piece under
                       the finder's old width floor is handed to the left-over rules whether or not the lower floor of
                       pin_thin also lets it into the stripe step.
  2026-11-23 (A9, experiments/2026-11-23_closeup_shape)  the stripeless close-up piece: one cut by the frame's side as well
                       as its bottom must be seen down to where its top row puts the stripe (``closeup_side``); a piece whose
                       predicted stripe runs past the frame bottom is a close-up too (``closeup_stripe``).
  2026-11-24 (experiments/2026-11-24_occl_strict)  a verify step on every rule's box: a barrel cannot be seen through a
                       nearer barrel (``verify_front``); a box needs a second reading besides the stripe's row (``verify_readings``).

  2026-11-26 (the collapse, step A1)  the switches that were off are deleted with the code only they used: dark_stripe,
                       occl_body_side, slice_box, cover_unpinned, stripe_two, slice_behind, own_close and stripe_mode="bands".
                       The lines above that name them are history; the tag pre-collapse-2026-11-26 has that code.

  2026-11-26 (the collapse, step A2)  the 23 switches that were on are plain code: every rule named above always runs.
                       DetConfig keeps the 20 numbers. Step 1 alone (require_stripe off, detect_step1) is gone.

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
    """The detector's numbers. There is no on/off switch: every rule in this file always runs (the collapse of 2026-11-26;
    the detector with its 30 switches is at the tag pre-collapse-2026-11-26). W = the width, H = the height and "a stripe
    height" = the stripe's height that the geometry expects of a barrel at the row in question."""
    min_area_px: int = 20        # a blob, a stripe, a cap piece or a half-stripe band under this many pixels is a speck; and a box needs this many evidence pixels of its own (verify)
    close_px: int = 3            # gaps this small are closed (3 x 3) before pieces are found; also: how many pixels beside a seen end are searched for a nearer barrel
    bottom_tol: float = 0.15     # a seen edge agrees with the predicted one within this share of the height ...
    bottom_tol_min_px: int = 4   # ... and never less than this many pixels
    width_min: float = 0.4       # a piece (or a cap) narrower than this x W is a sliver; also the least height of a cap, x an upper body
    width_max: float = 1.6       # a piece wider than this x W after splitting is not one barrel
    split_search: float = 0.25   # when cutting a wide blob, the narrowest column is looked for within +- this x W of the equal-spacing cut
    min_width_px: float = 16.0   # a barrel this narrow would be beyond the table (about 64 cm): such rows hold no barrels
    stripe_h_min: float = 0.45   # a stripe is between these multiples of a stripe height tall ...
    stripe_h_max: float = 1.6    # ... (stripe_h_min x a stripe height is also the least WIDTH of a stripe piece)
    band_h_max: float = 3.0      # body color counts as "right above / right below" a stripe pixel within this x a stripe height
    stripe_w_min: float = 0.4    # a partly seen stripe at least this x W wide may be centred on what is seen; two slices each under it may be a pair
    stripe_merge: float = 1.4    # a stripe region wider than this x W is the joined stripes of touching same-colored barrels
    stripe_full: float = 0.8     # "the whole width shows": a stripe (a seen span, a cap, a band) at least this x W wide
    min_stripe_px: float = 4.0   # where the expected stripe is thinner than this it cannot be resolved (a stripeless piece is then allowed)
    height_min: float = 0.5      # a stripeless piece is between these multiples of H tall ...
    height_max: float = 1.5      # ... for its bottom row
    body_min: float = 0.1        # in the stripe's columns, outside its rows, the box holds at least this share of body color (and more body than stripe color)
    body_width: float = 1.2      # one barrel is at most this x W wide: the box, the seen span, a joined stripe, a cap, a pair, a half stripe
    pin_good: float = 0.05       # an end of the seen part is the barrel's own side when the outline's three lines lie within this x H of the seen ones

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


@dataclass(frozen=True)
class Piece:
    """A barrel-shaped piece (stage 1): a blob of barrel color, cut to one barrel's width, with its bottom edge resolved."""
    barrel: Barrel                       # its box, color and flags (source "det1")
    seen_bottom: int                     # one past the last row its own pixels reach (the box's bottom may be a predicted one)


@dataclass(frozen=True)
class Stripe:
    """A stripe (stage 2): a band of one barrel color with the other color, the body, right above and right below it."""
    body: int                            # ORANGE | BLUE: the color found above and below the band
    bbox: tuple[int, int, int, int]      # the band, half-open
    n_other: int                         # band pixels labeled the stripe's color
    n_dark: int                          # unlabeled pixels inside the band's box (its shadowed part)
    center_row: float                    # the stripe's middle row: the median row of its colored pixels when they are at least
                                         # a quarter of the part, else the middle of its box
    cut_from: tuple | None = None        # when this stripe is a part cut from a wider stripe region: that region's box
    thin: bool = False                   # narrower than a stripe is tall, or taller than wide. A thin piece is a barrel only as a
                                         # slice seen from top to bottom (see box_from_stripe, thin_slice)
    at: BarrelAt | None = None           # the barrel its centre row predicts (None: that row gives no barrel)


@dataclass(frozen=True)
class Found:
    """A box the detector has drawn, with what it was drawn from."""
    barrel: Barrel
    rule: str                            # which rule drew it: "whole_stripe", "body_span", "hidden_side", "outline", "centred",
                                         # "thin_span", "thin_frame", "thin_outline" (the stripe step); "closeup", "closeup_stripe",
                                         # "far_piece" (stripeless pieces); "cap"; "pair"; "half_stripe"
    stripe: Stripe | None = None         # the stripe it was read from, for a box of the stripe step
    evidence: tuple | None = None        # the box of what it was read from: its stripe, its cap piece, its band (half stripes),
                                         # its two slices together (pairs). None: a stripeless piece is its own evidence

    @property
    def evidence_box(self) -> tuple[int, int, int, int]:
        return tuple(self.evidence) if self.evidence is not None else tuple(self.barrel.bbox)


def _note(log: list | None, stage: str, why: str, bbox, **values) -> None:
    """The reason log: diagnostics only. When a caller passes a list as ``log``, every candidate the detector drops (and
    every one it keeps, why="kept") is appended to it as a dict: the stage, the reason, the candidate's box, and the numbers
    it was compared with. With log=None (the default everywhere) nothing is recorded. The answer never depends on it:
    nothing in this file reads the log."""
    if log is not None:
        log.append({"stage": stage, "why": why, "bbox": tuple(int(v) for v in bbox), **values})


def box_iou(a: tuple, b: tuple) -> float:
    ax0, ay0, ax1, ay1 = a; bx0, by0, bx1, by1 = b
    iw = max(0, min(ax1, bx1) - max(ax0, bx0)); ih = max(0, min(ay1, by1) - max(ay0, by0))
    inter = iw * ih
    union = (ax1 - ax0) * (ay1 - ay0) + (bx1 - bx0) * (by1 - by0) - inter
    return inter / union if union else 0.0


# ================================================================ small helpers: one idea, one place
# Each is called with exactly the number its site used before the helpers existed. Where two sites use different numbers for
# the same idea, the number is an argument and the difference is written at the helper (docs/DETECTOR-MAP.md, section 6).

def _other(color: int) -> int:
    """The other barrel color."""
    return BLUE if color == ORANGE else ORANGE


def _closed(bm: np.ndarray, cfg: DetConfig) -> np.ndarray:
    """A mask with gaps up to close_px filled (a 3 x 3 closing at the default), as bool. A close_px of 1 or 2 means "no
    closing"; an even one is rounded up."""
    bm = bm.astype(np.uint8)
    if cfg.close_px >= 3:
        k = cfg.close_px if cfg.close_px % 2 else cfg.close_px + 1
        bm = cv2.morphologyEx(bm, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    return bm.astype(bool)


def edge_tol(cfg: DetConfig, size: float) -> float:
    """How far a seen edge may be from the predicted one and still "agree": bottom_tol x ``size``, at least
    bottom_tol_min_px. ``size`` is the barrel's HEIGHT at seven sites (the height the piece's top row predicts in
    ``resolve_bottom``, the distance from the top row to the stripe in ``_seen_to_stripe``, H elsewhere) and the barrel's
    WIDTH at one (``seen_span``: how far apart the body's end and the stripe's end may be, sideways)."""
    return max(cfg.bottom_tol_min_px, cfg.bottom_tol * size)


def widest_barrel(cfg: DetConfig) -> float:
    """"One barrel at most", in barrel widths: body_width, and never under 1. Used for a joined stripe, a wide stripe
    region, a cap, a pair and a half stripe. Three other sites use body_width as it is (the box's width in ``place_sides``,
    the trusted body in ``seen_span`` and in ``drop_single_reading``): the same number unless body_width is set under 1."""
    return max(cfg.body_width, 1.0)


def same_rows(a0: int, a1: int, b0: int, b1: int) -> bool:
    """Do the row ranges a0..a1 and b0..b1 share rows: is their overlap at least half the height of the shorter one?
    (Two other places ask about rows in their own way: the bridge in ``_join_pieces`` wants the box middles within half a
    stripe height, and ``closeup_pieces`` any overlap at all.)"""
    return 2 * (min(a1, b1) - max(a0, b0)) >= min(a1 - a0, b1 - b0)


def is_same_barrel(box: tuple, color: int, other: Barrel) -> bool:
    """Is ``box`` (of ``color``) the same barrel as ``other``: same color, and the boxes overlap by more than half (IoU > 0.5)?"""
    return other.color == color and box_iou(other.bbox, box) > 0.5


def same_barrel(box: tuple, color: int, boxes) -> bool:
    """Is ``box`` (of ``color``) the same barrel as one of ``boxes`` (``is_same_barrel``)?"""
    return any(is_same_barrel(box, color, o) for o in boxes)


def ends_against(mask: np.ndarray, colors: tuple, r0: int, r1: int, x0: int, x1: int) -> bool:
    """Does an edge lie against something of ``colors``: do the rows r0..r1 (clipped to the frame; the callers pass the 4
    rows beyond a seen end: the 3-row gap the body walk allows, + 1) hold one of those colors in at least half of the
    columns x0..x1? ``read_edges`` and ``_full_slice`` pass the OTHER barrel color; ``half_stripes`` passes both."""
    band = mask[max(0, r0):max(0, min(mask.shape[0], r1)), x0:x1]
    return band.size > 0 and float(np.isin(band, colors).any(axis=0).mean()) >= 0.5


def standing_nearer(boxes, lower_than: float) -> list:
    """The barrels of ``boxes`` that stand nearer than something whose bottom is at row ``lower_than``: their bottom edge
    is strictly lower in the picture. WHICH bottom is compared differs from site to site, and the caller passes it: the
    bottom the stripe's row predicts (``hidden_side``), the seen bottom of the cap piece and the drawn bottom of the cap's
    box (``_cap_box``); ``drop_seen_through`` compares two boxes' bottoms."""
    return [b for b in boxes if b.bbox[3] > lower_than]


def nearer_beside(boxes, row: int, pixels, lower_than: float) -> bool:
    """Does a barrel standing nearer (``standing_nearer``) hold one of the ``pixels`` (columns) at ``row``? ``hidden_side``
    asks about the close_px pixels beside the seen span, ``_cap_box`` about the one pixel beside the cap."""
    return any(b.bbox[1] <= row < b.bbox[3] and any(b.bbox[0] <= px < b.bbox[2] for px in pixels) for b in standing_nearer(boxes, lower_than))


# ================================================================ the ruler: what the geometry expects of a barrel

def axis_from_top_row(cam: geo.CameraModel, top_row: float) -> float:
    """The distance (mm) of a barrel's axis from the camera when the far edge of its lid is seen at ``top_row``. inf when
    that row is at or above the horizon; zero or less when it puts the barrel at or behind the camera."""
    return cam._d_axis_from_point_row(top_row, geo.BARREL_HEIGHT_MM, +geo.BARREL_END_DIAMETER_MM / 2)


def above_horizon(cam: geo.CameraModel, top_row: float) -> bool:
    """Is ``top_row`` at or above the horizon? Then it is not the top of a barrel on the table. A barrel is 24 mm tall and
    the camera is 43 mm above the table, so the camera looks down on every barrel's lid: the lid's far edge is always
    below the horizon. For a row at or above it the top row gives no distance (``axis_from_top_row`` is inf); a rule that
    reads "no distance" must not take that for "too near to see"."""
    return math.isinf(axis_from_top_row(cam, top_row))


@dataclass(frozen=True)
class BarrelAt:
    """The barrel the geometry expects, from ONE reading of the picture: its distance, and from that its rows and sizes in
    pixels. Every check compares what is seen with one of these. Which reading gives the distance differs by stage, and no
    rule combines two: the stripe's row (``from_stripe_row``: stages 2, 3, 7 and the verify step), the top row
    (``from_top_row``: caps), the seam between a half stripe and its body (``from_seam_row``). Stage 1 uses the bottom row
    and the top row through the camera model directly (``expected_width_px``, ``predicted_bottom``)."""
    d: float                             # the distance of its axis from the camera, mm
    rows: geo.BarrelRows                 # its rows (top, stripe_top, stripe_center, stripe_bottom, bottom) and its width

    @property
    def W(self) -> float:                # its width (at the bulge)
        return self.rows.width_px

    @property
    def H(self) -> float:                # its height: top row to bottom row
        return self.rows.bottom - self.rows.top

    @property
    def Hs(self) -> float:               # its stripe's height
        return self.rows.stripe_bottom - self.rows.stripe_top

    @property
    def upper(self) -> float:            # the height of its upper body: top row to the stripe's top
        return self.rows.stripe_top - self.rows.top

    @property
    def top(self) -> float:
        return self.rows.top

    @property
    def bottom(self) -> float:
        return self.rows.bottom

    def tol(self, cfg: DetConfig) -> float:
        """The edge tolerance for this barrel: ``edge_tol`` of its height."""
        return edge_tol(cfg, self.H)

    @classmethod
    def _at_distance(cls, cam: geo.CameraModel, d: float) -> "BarrelAt | None":
        if not math.isfinite(d) or d <= geo.BARREL_BULGE_DIAMETER_MM / 2 + 1:        # no distance, or nearer than a barrel can stand
            return None
        return cls(d, cam.barrel_rows(d))

    @classmethod
    def from_stripe_row(cls, cam: geo.CameraModel, row: float) -> "BarrelAt | None":
        """The barrel whose stripe centre (12 mm up, at the bulge's near side) sits at ``row``; None if there is none."""
        return cls._at_distance(cam, cam._d_axis_from_point_row(row, geo.BARREL_HEIGHT_MM / 2, -geo.BARREL_BULGE_DIAMETER_MM / 2))

    @classmethod
    def from_top_row(cls, cam: geo.CameraModel, row: float) -> "BarrelAt | None":
        """The barrel whose lid's far edge sits at ``row``; None if there is none."""
        return cls._at_distance(cam, axis_from_top_row(cam, row))

    @classmethod
    def from_seam_row(cls, cam: geo.CameraModel, row: float, z_mm: float) -> "BarrelAt | None":
        """The barrel one of whose stripe edges (``z_mm`` above the table, at the bulge's near side) sits at ``row``; None if
        there is none (``row`` may be nan)."""
        if not math.isfinite(row):
            return None
        return cls._at_distance(cam, cam._d_axis_from_point_row(row, z_mm, -(geo.BARREL_BULGE_DIAMETER_MM / 2)))


def _at(s: "Stripe", cam: geo.CameraModel) -> BarrelAt | None:
    """The barrel a stripe's centre row predicts. It is built once, with the stripe (``Stripe.at``); a stripe made by hand
    (a test) has none, and it is looked up here."""
    return s.at if s.at is not None else BarrelAt.from_stripe_row(cam, s.center_row)


# ================================================================ the detector: ten stages, in this order

def detect(mask: np.ndarray, cfg: DetConfig = DetConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
           log: list | None = None) -> list[Barrel]:
    """Class mask (0 other / 1 orange / 2 blue / 255 ignore) -> one Barrel per barrel, left to right. Same signature as
    detect_cc.detect. ``log``: pass a list to get the reason log (see ``_note``).

    The stages, in order. Stripes come first: the first boxes are drawn from stripes (stage 3), and a stripe already needs
    body color above and below it. Geometry is not a stage: it is the ruler inside every check (a row gives a distance,
    the distance gives the expected width, height and stripe height). Later stages only add boxes, except that the two
    verify stages (5 and 9) delete boxes and a half stripe (8) may replace a box of stage 3. docs/DETECTOR-MAP.md walks
    through every check."""
    layers = sandwiches(mask, cam, cfg)                                        #    per body color: where the other color has it right above / below
    pieces = find_pieces(mask, cam, cfg, log)                                  # 1  blobs of barrel color, barrel-shaped. No box yet
    stripes, leftover = find_stripes(mask, cam, cfg, log, layers)              # 2  stripes: one color with the other right above and below
    found, unplaced, lost = boxes_from_stripes(stripes, mask, cam, cfg, log)   # 3  one box per stripe
    found = found + closeup_pieces(pieces, found, mask, cam, cfg, log)         # 4  a piece with no stripe: only as a close-up
    found = drop_seen_through(found, mask, cam, cfg, log)                      # 5  verify: not read from a nearer barrel's picture
    found = found + caps_behind(found, lost, mask, cam, cfg, log)              # 6  a top showing above a found nearer barrel
    found = found + post_pairs(leftover + unplaced, found, mask, cam, cfg, log)   # 7  two thin slices, one barrel apart
    found = half_stripes(found, mask, cam, cfg, log, layers)                   # 8  a stripe with body on one side only (adds; may replace)
    found = drop_seen_through(found, mask, cam, cfg, log)                      # 9  verify again, on every box
    found = drop_single_reading(found, mask, cam, cfg, log)                    #    verify: a guessed side needs a seen edge
    return sorted((f.barrel for f in found), key=lambda b: b.bbox[0])


# ================================================================ stage 1: pieces

def find_blobs(mask: np.ndarray, cfg: DetConfig = DetConfig()) -> list[Blob]:
    """Connected blobs of barrel-colored pixels (orange and blue together, so a body and its stripe are one
    blob), after closing small gaps and dropping specks."""
    union = _closed(np.isin(mask, (ORANGE, BLUE)), cfg).astype(np.uint8)
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


def expected_width_px(bbox, cam: geo.CameraModel, frame_h: int) -> float:
    """How wide one barrel is at this blob's distance. From the bottom row when the bottom is in the frame,
    else from the top row (a barrel cut by the frame bottom has no bottom row to use)."""
    x0, y0, x1, y1 = bbox
    if y1 < frame_h:
        d = cam.d_axis_from_bottom_row(y1)
    else:
        d = axis_from_top_row(cam, y0)
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


def predicted_bottom(cam: geo.CameraModel, top_row: float) -> float:
    """Where the base must be if the lid's far edge is at ``top_row`` (24 mm tall barrel, base near edge 18 mm
    closer than the lid far edge). inf when the top row puts the base at or behind the camera (below the frame)."""
    d_axis = axis_from_top_row(cam, top_row)
    d_base = d_axis - geo.BARREL_END_DIAMETER_MM / 2
    if not math.isfinite(d_axis) or d_base <= 0:
        return math.inf
    return cam.point_row(d_base, 0.0)


def resolve_bottom(bbox, cam: geo.CameraModel, frame_h: int, cfg: DetConfig = DetConfig()) -> tuple[int, set[str]]:
    """The bottom row to draw. The top row says how far away the barrel is, and from that where its base
    must be (``predicted_bottom``). Keep the seen bottom when it agrees with that prediction; replace it
    when it does not (a shadowed face makes the blob too short, a reflection too tall, an occluder hides the
    base). Always clipped to the frame; a box reaching the frame bottom is 'truncated'."""
    x0, y0, x1, y1 = bbox
    flags: set[str] = set()
    pred = predicted_bottom(cam, y0)
    if math.isfinite(pred):
        tol = edge_tol(cfg, pred - y0)
        if abs(y1 - pred) > tol and not (y1 >= frame_h and pred >= frame_h):
            y1 = int(round(pred)); flags.add("bottom_inferred")
    y1 = min(max(y1, y0 + 1), frame_h)
    if y1 >= frame_h:
        flags.add("truncated")
    return y1, flags


def find_pieces(mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(), log: list | None = None) -> list[Piece]:
    """Stage 1. In: the class mask. Out: the barrel-shaped pieces, left to right. No box is drawn here: a barrel with a
    stripe gets its box from the stripe (stage 3), and a piece is kept only as a close-up (stage 4).

    A piece is a blob of barrel color (``find_blobs``), cut into as many parts as it is barrels wide (``split_blob``),
    with its bottom edge taken from its top row where the seen bottom disagrees (``resolve_bottom``). Per piece, in order:

    1. on the table: the width W one barrel has at its bottom row is at least min_width_px;                   else "too_far"
    2. its top is below the horizon (``above_horizon``): the top of a barrel on the table always is;     else "above_horizon"
    3. barrel-wide: width_min to width_max x W;                                                              else "width"
    4. barrel-tall, when its box ends inside the frame and does not touch the frame top: height_min to height_max x
       the height a barrel has at its bottom row.                                                           else "height"
    Its color is the majority of its pixels (a tie is orange).

    What 4 can still refuse, once 2 has been asked. Where the top row gives a distance, the bottom was either seen
    where that distance predicts it or drawn there (``resolve_bottom``), so the height already fits its bottom row. So 4
    decides only where the top row predicts no bottom: a top in the lowest rows of the frame (the base would be at or
    behind the camera) on a piece that still ends inside the frame. Such a piece is too short. (A piece with its top
    at or above the horizon is always more than height_max x too tall for its bottom row; 2 refuses it first, by the
    fact itself.)"""
    h, w = mask.shape
    out = []
    for blob in find_blobs(mask, cfg):
        for piece in split_blob(blob, mask, cam, cfg):
            x0, y0, x1, y1 = piece.bbox
            y1, flags = resolve_bottom(piece.bbox, cam, h, cfg)
            W = cam.expected_barrel_width_px(bottom_row=y1) if y1 < h else expected_width_px((x0, y0, x1, h), cam, h)
            if not math.isfinite(W) or W < cfg.min_width_px:
                _note(log, "piece", "too_far", (x0, y0, x1, y1), expected_w=W)
                continue                                   # 1. too far to be on the table (or its bottom row gives no distance)
            if above_horizon(cam, y0):
                _note(log, "piece", "above_horizon", (x0, y0, x1, y1), top_row=y0)
                continue                                   # 2. its top is at or above the horizon: nothing on the table looks like that
            if not (cfg.width_min * W <= (x1 - x0) <= cfg.width_max * W):
                _note(log, "piece", "width", (x0, y0, x1, y1), expected_w=W)
                continue                                   # 3. a sliver, or too wide to be one barrel
            if y1 < h and y0 > 0:
                H = cam.expected_barrel_height_px(bottom_row=y1)
                if math.isfinite(H) and not (cfg.height_min * H <= (y1 - y0) <= cfg.height_max * H):
                    _note(log, "piece", "height", (x0, y0, x1, y1), expected_h=H)
                    continue                               # 4. barrel-wide but not barrel-tall for its bottom row
            if x0 == 0 or x1 == w or y0 == 0:
                flags.add("truncated")
            n_o, n_b = piece.n_orange, piece.n_blue
            color = ORANGE if n_o >= n_b else BLUE
            out.append(Piece(Barrel(color=color, bbox=(x0, y0, x1, y1), confidence=max(n_o, n_b) / (n_o + n_b),
                                    flags=frozenset(flags), area=int(piece.pixels.sum()), source="det1"), piece.bbox[3]))
    return sorted(out, key=lambda p: p.barrel.bbox[0])


# ================================================================ stage 2: stripes

def _reach_by_row(cam: geo.CameraModel, h: int, cfg: DetConfig) -> np.ndarray:
    """For every image row: how far (in rows) the body color may be from a stripe centred there and still be
    "right above / right below" it: band_h_max x the stripe height the geometry expects at that row; -1 where
    no barrel can have its stripe (at or above the horizon)."""
    reach = np.full(h, -1.0)
    for r in range(h):
        at = BarrelAt.from_stripe_row(cam, r + 0.5)
        if at is not None:
            reach[r] = cfg.band_h_max * at.Hs
    return reach


@dataclass(frozen=True, eq=False)
class Sandwich:
    """For one body color: where the other barrel color (a stripe's) has that body color right above and right below."""
    body: int
    other: int                           # the stripe's color
    stripe: np.ndarray                   # bool: the pixels of the other color (gaps closed) that are not body color
    up: np.ndarray                       # per pixel: the last body row at or above it in its column (-10 ** 6 = none)
    dn: np.ndarray                       # per pixel: the first body row at or below it (10 ** 6 = none)
    above: np.ndarray                    # bool: body color right above = within the reach of the pixel's row (_reach_by_row)
    below: np.ndarray                    # bool: body color right below


def sandwiches(mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig) -> dict[int, Sandwich]:
    """The ``Sandwich`` of each body color (orange first). Computed once per image: the stripe finder asks for body on
    both sides of a pixel (``above & below``), the half stripes for body on one side only."""
    h = mask.shape[0]
    rows_idx = np.arange(h)[:, None]
    reach = _reach_by_row(cam, h, cfg)[:, None]
    out = {}
    for body in (ORANGE, BLUE):
        other = _other(body)
        bm = _closed(mask == body, cfg)
        om = _closed(mask == other, cfg) & ~bm
        up = np.maximum.accumulate(np.where(bm, rows_idx, -10 ** 6), axis=0)              # last body row at or above
        dn = np.minimum.accumulate(np.where(bm, rows_idx, 10 ** 6)[::-1], axis=0)[::-1]   # first body row at or below
        out[body] = Sandwich(body, other, om, up, dn, (rows_idx - up) <= reach, (dn - rows_idx) <= reach)
    return out


def _join_pieces(st: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, lab: np.ndarray, sand: np.ndarray) -> list[list[int]]:
    """Which connected pieces of sandwiched stripe color are one stripe (a highlight or a shadow line cut it). ``st`` is the
    stats table of the pieces (row 0 = background), ``lab`` their label image, ``sand`` the finder's sandwich. Returns the
    groups as lists of piece numbers.

    Going left to right, a piece joins the nearest group to its left when
    1. they share rows: the overlap is at least half the height of the shorter of the two;
    2. together they span no more than one barrel: body_width x the width a barrel has at that row (two barrels cannot both
       have their stripe inside one barrel's width at the same rows);
    3. (a) both are stripe-shaped: not taller than stripe_h_max x the expected stripe height and not taller than wide (slivers
       of a barrel's own upper body between specks are tall); or (b) the GAP between them is bridged: each of the two is no
       taller than stripe_h_max x the expected stripe height by the finder's height measure (10th to 90th percentile of its
       rows), the two are at the same rows (box middles within half a stripe height), body color is right above and right
       below the stripe rows in every column of the gap, and the gap is at most half the joined span.
    A piece that is not stripe-shaped joins only by a bridge. The join is greedy and goes left to right."""
    def core(i):
        x, y, bw, bh = (int(v) for v in st[i][:4])
        ys = np.where(lab[y:y + bh, x:x + bw] == i)[0] + y
        return float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)

    groups: list[list] = []                                      # [ids, x0, x1, y0, y1, all shaped, all cores ok]
    for i in sorted(range(1, len(st)), key=lambda i: (int(st[i][0]), int(st[i][1]))):
        x, y, bw, bh = (int(v) for v in st[i][:4])
        at = BarrelAt.from_stripe_row(cam, y + bh / 2)               # the row: the middle of the piece's box
        if at is None:
            groups.append([[i], x, x + bw, y, y + bh, False, False])
            continue
        hs = at.Hs
        shaped = bh <= bw and bh <= cfg.stripe_h_max * hs
        core_ok = core(i) <= cfg.stripe_h_max * hs
        span = widest_barrel(cfg) * at.W
        for grp in reversed(groups):
            ids, gx0, gx1, gy0, gy1, gsh, gco = grp
            if not same_rows(y, y + bh, gy0, gy1) or max(gx1, x + bw) - min(gx0, x) > span:
                continue
            joined = max(gx1, x + bw) - min(gx0, x)
            ok = shaped and gsh
            if not ok and core_ok and gco:
                a, b = gx1, x                                    # the gap's columns
                ya, yb = max(gy0, y), min(gy1, y + bh)
                level = abs((y + bh / 2) - (gy0 + gy1) / 2) <= hs / 2            # at the same rows (a stripe is level)
                ok = level and (b <= a or (b - a <= joined / 2 and bool(sand[ya:yb, a:b].any(axis=0).all())))
            if ok:
                grp[:] = [ids + [i], min(gx0, x), max(gx1, x + bw), min(gy0, y), max(gy1, y + bh), gsh and shaped, gco and core_ok]
                break
        else:
            groups.append([[i], x, x + bw, y, y + bh, shaped, core_ok])
    return [grp[0] for grp in groups]


def _one_stripe_per_barrel(sel: np.ndarray, mask: np.ndarray, other: int, body: int, x: int, bw: int, W: float, cam: geo.CameraModel,
                           cfg: DetConfig, W_two: float | None = None) -> list[Stripe]:
    """One Stripe per barrel from a stripe region ``sel`` (``x`` = its left column, ``bw`` = its width, ``W`` = the width of
    one barrel at its row). A stripe cannot be wider than its barrel, so a wide region is the joined stripes of
    same-colored barrels standing side by side, and is cut into equal parts:

    - wider than stripe_merge x W: round(width / W) parts;
    - where the caller could read the barrel's size off the body (``W_two`` given: the larger of W and the width of a
      barrel as tall as the body seen right above and below the region), wider than body_width x W_two: at least two
      parts, round(width / W_two). A near barrel can be 1.3 x the width its row predicts, but then it is taller by as
      much; two barrels side by side are not taller than one.
    Each part remembers the region it was cut from (``Stripe.cut_from``)."""
    k = int(round(bw / W)) if bw > cfg.stripe_merge * W else 1
    Wt = W_two or W
    if W_two is not None and bw > widest_barrel(cfg) * Wt:
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
        x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        n_dark = int((mask[y0:y1, x0:x1] == 0).sum())          # unlabeled pixels inside the part's own box (its shadowed part)
        out.append(Stripe(body, (x0, y0, x1, y1), int((mask[part] == other).sum()), n_dark, center, whole,
                          at=BarrelAt.from_stripe_row(cam, center)))        # the row every later check of this stripe uses
    return out


def find_stripes(mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(), log: list | None = None,
                 layers: dict | None = None) -> tuple[list[Stripe], list[Stripe]]:
    """Stage 2. In: the class mask (and ``layers``, its ``sandwiches``, when the caller has them). Out: (the stripes, left to
    right, one per barrel; the left-over pieces).

    Done twice: orange as the body (blue stripes), then blue as the body. A stripe is a connected piece of the OTHER color
    whose every pixel has body color above AND below it in its own column, within band_h_max x the stripe height expected
    at that pixel's row (the sandwich; so a stripe that touches a neighbouring barrel's body is cut from it). Only the
    stripe's own pixels are measured, so shadow the segmentation left unlabeled around it changes nothing, and a gap with
    no stripe-colored pixel is not a stripe. Pieces a highlight cut apart are joined first (``_join_pieces``). Then, per
    stripe, in this order:

    1. big enough: min_area_px pixels;                                                    else "area"
    2. its row gives a distance (below the horizon);                                      else "no_geometry"
    3. on the table: one barrel is at least min_width_px wide there (and its stripe min_stripe_px tall);   else "too_far"
    4. as tall as a stripe: stripe_h_min to stripe_h_max x the expected stripe height, measured from the 10th to the
       90th percentile of its rows. A stripe that is too thin but seen whole (stripe_full x W wide) is read a second
       time, as the mean of its own height and of the gap between the body above and below it: mixed pixels at the
       two seams make the one thinner and the other taller by the same amount;            else "height"
    5. not a speck sideways: at least stripe_h_min x the expected stripe height wide;     else "width" -> a left-over piece
    6. no wider than one barrel, else it is cut into one stripe per barrel (``_one_stripe_per_barrel``);
    7. thin? Narrower than a stripe is tall, or taller than wide: marked ``Stripe.thin``, and handed out a second time
       as a left-over piece.

    The left-over pieces (5 and 7) are never a barrel alone: stage 7 pairs them."""
    out: list[Stripe] = []
    leftover: list[Stripe] = []
    for body, sw in (layers or sandwiches(mask, cam, cfg)).items():
        other, up, dn = sw.other, sw.up, sw.dn
        sandwich = sw.above & sw.below
        n, lab, st, _ = cv2.connectedComponentsWithStats((sw.stripe & sandwich).astype(np.uint8), connectivity=8)
        for ids in _join_pieces(st, cam, cfg, lab, sandwich):       # one candidate per group of pieces
            x, y = int(min(st[i][0] for i in ids)), int(min(st[i][1] for i in ids))
            bw, bh = int(max(st[i][0] + st[i][2] for i in ids)) - x, int(max(st[i][1] + st[i][3] for i in ids)) - y
            area = int(sum(st[i][4] for i in ids))
            sb = (x, y, x + bw, y + bh)
            if area < cfg.min_area_px:
                _note(log, "stripe", "area", sb, body=body, area=area)
                continue                                                                   # 1.
            sel = np.isin(lab, ids) if len(ids) > 1 else lab == ids[0]
            ys = np.where(sel)[0]
            at = BarrelAt.from_stripe_row(cam, float(np.median(ys)) + 0.5)      # the row: the median row of the candidate's pixels
            if at is None:
                _note(log, "stripe", "no_geometry", sb, body=body)
                continue                                                                   # 2.
            W, Hs = at.W, at.Hs
            if W < cfg.min_width_px or Hs < cfg.min_stripe_px:
                _note(log, "stripe", "too_far", sb, body=body, expected_w=W, expected_stripe_h=Hs)
                continue                                                                   # 3.
            core_h = np.percentile(ys, 90) - np.percentile(ys, 10) + 1
            h_ok = cfg.stripe_h_min * Hs <= core_h <= cfg.stripe_h_max * Hs
            seam_h = None
            if core_h < cfg.stripe_h_min * Hs and bw >= cfg.stripe_full * W:
                # too thin by its own rows, and seen whole: the second reading. Not asked of a short piece: thin because the
                # seams were eaten, or short because partly hidden, not both (a blue sliver between two fingers is thin and short)
                gap = float(np.median((dn - up - 1)[sel]))
                seam_h = (core_h + gap) / 2
                h_ok = cfg.stripe_h_min * Hs <= seam_h <= cfg.stripe_h_max * Hs
            if not h_ok:
                _note(log, "stripe", "height", sb, body=body, core_h=float(core_h), expected_stripe_h=Hs,
                      **({} if seam_h is None else {"seam_h": float(seam_h)}))
                continue                                                                   # 4.
            twin = Stripe(body, sb, int((mask[sel] == other).sum()), 0, float(np.median(ys)) + 0.5, at=at)    # the candidate as a left-over piece
            if bw < cfg.stripe_h_min * Hs:
                _note(log, "stripe", "width", sb, body=body, core_h=float(core_h), expected_w=W)
                leftover.append(twin)
                continue                                                                   # 5.
            # 6. The barrel's size can be read off the body only where body IS seen right above and right below the region
            # (the body walk allows 3 empty rows). With none there the seen height says nothing, and a near barrel's stripe
            # can be 1.26 x the width its row gives
            W_two = None
            top_s, bot_s = _body_extent(mask, body, x, x + bw, y, y + bh)
            if top_s < y and bot_s > y + bh:
                W_two = max(W, (bot_s - top_s) * W / at.H)
            parts = _one_stripe_per_barrel(sel, mask, other, body, x, bw, W, cam, cfg, W_two)
            if bw < Hs or bw < core_h:                                                     # 7.
                parts = [replace(s, thin=True) for s in parts]
                leftover.append(twin)
            out.extend(parts)
    return sorted(out, key=lambda s: s.bbox[0]), leftover


# ================================================================ stage 3: one box per stripe

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


def _body_cols(mask: np.ndarray, body: int, top: int, bottom: int, y0: int, y1: int, others: tuple, min_px: int) -> np.ndarray:
    """Per image column: does it hold at least min_px body pixels in rows top..bottom, the stripe's rows y0..y1 left out?
    Columns under another stripe (``others``, their x-ranges) never do: they are a touching same-colored neighbour's."""
    rows = np.ones(bottom - top, bool); rows[max(0, y0 - top):max(0, y1 - top)] = False
    cols = ((mask[top:bottom] == body) & rows[:, None]).sum(axis=0) >= min_px
    for ox0, ox1 in others:
        cols[max(0, ox0):max(0, ox1)] = False
    return cols


def _body_columns(mask: np.ndarray, body: int, x0: int, x1: int, top: int, bottom: int, y0: int, y1: int,
                  cap_px: float, others: tuple = (), min_px: int = 2, max_gap: int = 2) -> tuple[int, int]:
    """Left and right edge of the body color joined to the stripe: starting from the stripe's columns x0..x1, walk
    outward while columns in rows top..bottom (the stripe rows y0..y1 excluded) hold at least min_px body pixels,
    allowing gaps of max_gap columns. Columns under another found stripe (`others`, their x-ranges) are never
    added: they are a touching same-color neighbour's. The result is at most cap_px wide (trimmed evenly around the
    stripe)."""
    cols = _body_cols(mask, body, top, bottom, y0, y1, others, min_px)
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
    cols = _body_cols(mask, body, top, bottom, y0, y1, others, min_px)
    idx = np.flatnonzero(cols)
    if len(idx) == 0:
        return None
    cut = np.flatnonzero(np.diff(idx) > max_gap + 1)
    runs = zip(np.r_[idx[0], idx[cut + 1]], np.r_[idx[cut], idx[-1]] + 1)
    joined = [(int(a), int(b)) for a, b in runs if b >= x0 - max_gap and a <= x1 + max_gap]
    if not joined:
        return None
    return min(a for a, _ in joined), max(b for _, b in joined)


# ---------------------------------------------------------------- the barrel's outline: which end of a seen part is its own side

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
    middle); a straight side predicts the shoulder twice as deep as it is seen. Every row comes from the camera model
    and the barrel's sizes; nothing is fit."""
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
    other = _other(body)
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


def _end_costs(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, sx0: int, sx1: int) -> tuple[float, float] | None:
    """(cost of "the left end of the seen columns sx0..sx1 is the barrel's own side", the same for the right end), in
    barrel heights; None when the stripe's row gives no barrel. Steps 1 to 3 of ``own_end_by_outline``. inf = no line
    could be compared at that end."""
    at = _at(s, cam)
    if at is None or sx1 - sx0 < 2:
        return None
    W, H = at.W, at.H
    ol = Outline.at(cam, at.d)
    tol = at.tol(cfg)
    x0, y0, x1, y1 = s.bbox
    lines = _seen_lines(mask, s.body, sx0, sx1, y0, y1, int(at.top - tol), int(at.bottom + tol) + 1)
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


def own_end_by_outline(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig, sx0: int, sx1: int) -> tuple[int, int] | None:
    """Left and right edge of a box one barrel wide, placed by the barrel's outline; None when the outline does not know
    where the barrel is. ``sx0``, ``sx1`` = the columns seen of the barrel.

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
    cut by a straight edge has square ones; a slanted cut imitates one rounded corner and never both. A piece from the
    middle of a barrel has no such end and gets no box from here."""
    costs = _end_costs(s, mask, cam, cfg, sx0, sx1)
    if costs is None:
        return None
    left, right = costs[0] <= cfg.pin_good, costs[1] <= cfg.pin_good
    if left == right:
        return None                                                  # no end, or both ends, look like a barrel's own side
    Wi = int(round(_at(s, cam).W))
    return (sx0, sx0 + Wi) if left else (sx1 - Wi, sx1)


def _body_crosses(mask: np.ndarray, s: Stripe, sx0: int, sx1: int) -> bool:
    """Does the body color cross the stripe's rows in some column of sx0..sx1 (more than half of the rows y0..y1 of the
    stripe)? A barrel's body never crosses its own stripe; a body-colored thing in front of it does."""
    y0, y1 = s.bbox[1], s.bbox[3]
    if y1 <= y0 or sx1 <= sx0:
        return False
    return bool(((mask[y0:y1, sx0:sx1] == s.body).mean(axis=0) > 0.5).any())


# ---------------------------------------------------------------- top and bottom

@dataclass(frozen=True)
class Edges:
    """The top and the bottom of a stripe's barrel (``read_edges``)."""
    top: int                             # the row to draw (not yet clipped to the frame)
    bottom: int
    inferred: frozenset                  # "top_inferred" / "bottom_inferred": that edge is the predicted one, not a seen one


def read_edges(s: Stripe, at: BarrelAt, mask: np.ndarray, cfg: DetConfig) -> Edges | None:
    """Where are the top and the bottom of this stripe's barrel? ``at`` = the barrel the stripe's row predicts.

    The body color is walked up and down from the stripe, in the stripe's columns (``_body_extent``). A seen end within
    the edge tolerance (bottom_tol x the height, at least bottom_tol_min_px) of the predicted row is the edge; else the
    predicted row is drawn and the edge is "inferred". This never refuses by itself. Two more questions, because an edge
    is seen only against something that is not a barrel ("against" = the OTHER barrel color in at least half of the
    stripe's columns, in the 4 rows beyond the seen end):

    (a) both edges inferred, and the body above ends against the other barrel color: None, not a barrel. That thing
        stands behind and cannot hide a top; the "stripe" is a piece of another barrel.
    (b) a seen bottom that ends against the other barrel color, with the predicted bottom lower: the barrel may go on
        behind that barrel, so the predicted bottom is drawn (inferred)."""
    h = mask.shape[0]
    x0, y0, x1, y1 = s.bbox
    inferred: set[str] = set()
    top_seen, bottom_seen = _body_extent(mask, s.body, x0, x1, y0, y1)
    tol = at.tol(cfg)
    top = top_seen
    if abs(top_seen - at.top) > tol:
        top = int(round(at.top)); inferred.add("top_inferred")
    bottom = bottom_seen
    if abs(bottom_seen - at.bottom) > tol and not (bottom_seen >= h and at.bottom >= h):
        bottom = int(round(at.bottom)); inferred.add("bottom_inferred")
    other = (_other(s.body),)
    if {"top_inferred", "bottom_inferred"} <= inferred and ends_against(mask, other, top_seen - 4, top_seen, x0, x1):
        return None                                                                        # (a)
    if "bottom_inferred" not in inferred and int(round(at.bottom)) > bottom_seen and ends_against(mask, other, bottom_seen, bottom_seen + 4, x0, x1):
        bottom = int(round(at.bottom)); inferred.add("bottom_inferred")                  # (b)
    return Edges(top, bottom, frozenset(inferred))


# ---------------------------------------------------------------- left and right

@dataclass(frozen=True)
class SeenSpan:
    """What is seen of a partly seen barrel, sideways (``seen_span``)."""
    x0: int                              # the columns seen of the barrel: the stripe joined with its body; or, where the body
    x1: int                              # is not trusted, the stripe's end on a cut side and the body's end on the other
    shows_width: bool                    # the seen span is at least stripe_full x W wide
    trusted: bool                        # the body joined to the stripe is no wider than one barrel (body_width x W)
    left_cut: bool                       # on that side the body and the stripe end apart (further than the tolerance), or the
    right_cut: bool                      # stripe was cut there from a wider stripe


def seen_span(s: Stripe, mask: np.ndarray, W: float, top: int, bottom: int, cfg: DetConfig, others: tuple = ()) -> SeenSpan:
    """What is seen of the barrel of a partly seen stripe. ``top``, ``bottom`` = the box's rows; ``W`` = the barrel's width.

    The seen span is the stripe's columns joined with the columns of body color above and below it (``_body_span``;
    columns under another stripe, ``others``, never count). A body wider than body_width x W holds a same-colored
    neighbour: it is not trusted, and only the stripe counts.

    A side is "cut" when the body's end and the stripe's end there are further apart than the edge tolerance
    (bottom_tol x W, at least bottom_tol_min_px): at a barrel's own edge the stripe and the body end together. Asked of
    an untrusted body too: its far end is not this barrel's, but where it runs past the stripe the stripe is cut, and
    where it ends with the stripe that is this barrel's edge. A part cut from a wider stripe is cut on its cut side."""
    x0, y0, x1, y1 = s.bbox
    span = _body_span(mask, s.body, x0, x1, top, bottom, y0, y1, others) if bottom - top >= 2 else None
    trusted = span is not None and max(span[1], x1) - min(span[0], x0) <= cfg.body_width * W
    sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if trusted else (x0, x1)
    shows_width = sx1 - sx0 >= cfg.stripe_full * W
    tol = edge_tol(cfg, W)                                           # sideways: a share of the WIDTH
    left_cut = span is not None and abs(span[0] - x0) > tol
    right_cut = span is not None and abs(span[1] - x1) > tol
    if s.cut_from is not None:                                       # its neighbour is where it was cut
        left_cut = left_cut or x0 > s.cut_from[0]
        right_cut = right_cut or x1 < s.cut_from[2]
    if span is not None and not trusted:                             # the body's far end is not this barrel's; an end shared with the stripe is
        sx0 = x0 if left_cut else min(span[0], x0)
        sx1 = x1 if right_cut else max(span[1], x1)
    return SeenSpan(sx0, sx1, shows_width, trusted, left_cut, right_cut)


def hidden_side(s: Stripe, seen: SeenSpan, frame_w: int, pred_bottom: float, found: tuple, cfg: DetConfig) -> str | None:
    """Which side of a partly seen barrel is hidden: "left", "right", or None when no side or both have a reason.

    A side counts as hidden only for a reason: (a) the seen span touches the frame edge there; (b) a found barrel
    standing nearer is there: its box holds one of the close_px pixels beside the seen span at the stripe's middle row,
    and its bottom edge is lower than ``pred_bottom``, the bottom this stripe's row predicts; (c) the side is cut
    (``seen_span``). ``found`` = the barrels found so far."""
    row = int(s.center_row)
    left = seen.x0 <= 0 or nearer_beside(found, row, range(seen.x0 - cfg.close_px, seen.x0), pred_bottom) or seen.left_cut
    right = seen.x1 >= frame_w or nearer_beside(found, row, range(seen.x1, seen.x1 + cfg.close_px), pred_bottom) or seen.right_cut
    if left and not right:
        return "left"
    if right and not left:
        return "right"
    return None


def centred(s: Stripe, seen: SeenSpan, W: float, cfg: DetConfig) -> tuple[int, int, str] | None:
    """The last resort for a partly seen stripe that nothing places: a stripe at least stripe_w_min x W wide gets a box W
    wide, centred on what is seen. This is a guess. A narrower stripe gets None."""
    if (s.bbox[2] - s.bbox[0]) >= cfg.stripe_w_min * W:
        cx = (seen.x0 + seen.x1) / 2
        return int(round(cx - W / 2)), int(round(cx + W / 2)), "centred"
    return None


def thin_slice(s: Stripe, seen: SeenSpan, mask: np.ndarray, cam: geo.CameraModel, W: float, cfg: DetConfig,
               full_slice: bool) -> tuple[int, int, str] | None:
    """The sides for a thin piece of stripe (narrower than a stripe is tall, or taller than wide). It skips the reasons
    for a hidden side; in this order:

    1. its body shows the barrel's whole width (trusted, at least stripe_full x W), the piece is a full slice, and no
       column of the span has body color across the stripe's rows (a body-colored thing in front): the span is the box;
    2. a full slice that touches the frame on exactly one side: W wide from its other end (the frame is a hidden side
       that is known);
    3. exactly one end is the barrel's own side by the outline: W wide from that end;
    else None."""
    w = mask.shape[1]
    Wi = int(round(W))
    if seen.shows_width and seen.trusted and full_slice and not _body_crosses(mask, s, seen.x0, seen.x1):
        return seen.x0, seen.x1, "thin_span"
    if full_slice and (seen.x0 <= 0) != (seen.x1 >= w):
        return (seen.x1 - Wi, seen.x1, "thin_frame") if seen.x0 <= 0 else (seen.x0, seen.x0 + Wi, "thin_frame")
    placed = own_end_by_outline(s, mask, cam, cfg, seen.x0, seen.x1)
    return None if placed is None else (*placed, "thin_outline")


def partly_seen(s: Stripe, seen: SeenSpan, mask: np.ndarray, cam: geo.CameraModel, W: float, pred_bottom: float, cfg: DetConfig,
                found: tuple = (), use_outline: bool = True) -> tuple[int, int, str] | None:
    """The sides for a stripe narrower than stripe_full x W that is not thin (hidden or not: the color step can leave a
    stripe narrow). In this order:

    1. the seen span shows the whole width: the span is the box. The barrel is all there, only its stripe was cut;
    2. exactly one side is hidden for a reason (``hidden_side``): W wide from the seen end of the other side;
    3. exactly one end is the barrel's own side by the outline (``own_end_by_outline``): W wide from that end. Left out
       with ``use_outline=False``;
    4. a stripe at least stripe_w_min x W wide: W wide, centred on what is seen (``centred``);
    else None: nothing says where the rest of the barrel is."""
    if seen.shows_width:
        return seen.x0, seen.x1, "body_span"
    Wi = int(round(W))
    side = hidden_side(s, seen, mask.shape[1], pred_bottom, found, cfg)
    if side == "left":
        return seen.x1 - Wi, seen.x1, "hidden_side"
    if side == "right":
        return seen.x0, seen.x0 + Wi, "hidden_side"
    if use_outline:
        placed = own_end_by_outline(s, mask, cam, cfg, seen.x0, seen.x1)
        if placed is not None:
            return (*placed, "outline")
    return centred(s, seen, W, cfg)


def place_sides(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, W: float, top: int, bottom: int, pred_bottom: float,
                cfg: DetConfig, others: tuple = (), found: tuple = (), full_slice: bool = False,
                use_outline: bool = True) -> tuple[int, int, str] | None:
    """Left edge, right edge and the rule that placed them, for one stripe; None when nothing places the box.
    ``top``, ``bottom`` = the box's rows; ``pred_bottom`` = the bottom row the stripe's row predicts; ``others`` = the
    columns of the other stripes; ``found`` = the barrels found so far; ``full_slice`` = neither edge was inferred.

    - A stripe at least stripe_full x W wide is seen whole: the box is as wide as the body joined to it (``_body_columns``:
      the stripe's outermost pixels curve away from the camera and go dark, so the stripe alone runs narrow), at most
      body_width x W.
    - A narrower stripe is partly seen: ``thin_slice`` for a thin piece, ``partly_seen`` for the others."""
    x0, y0, x1, y1 = s.bbox
    if (x1 - x0) >= cfg.stripe_full * W:
        if bottom - top >= 2:
            return (*_body_columns(mask, s.body, x0, x1, top, bottom, y0, y1, cap_px=cfg.body_width * W, others=others), "whole_stripe")
        return x0, x1, "whole_stripe"
    seen = seen_span(s, mask, W, top, bottom, cfg, others)
    if s.thin:
        return thin_slice(s, seen, mask, cam, W, cfg, full_slice)
    return partly_seen(s, seen, mask, cam, W, pred_bottom, cfg, found, use_outline)


# ---------------------------------------------------------------- the box holds body color

def holds_body(s: Stripe, mask: np.ndarray, top: int, bottom: int, cfg: DetConfig) -> tuple[bool, float, float]:
    """Does the box hold the body color? In the stripe's own columns, outside the stripe's rows, the box (rows top..bottom)
    must hold at least as many body-colored pixels as stripe-colored ones, and at least body_min of body color. A
    stripe-colored thing with the other barrel color above and below it is not this body's barrel (a blue barrel's body
    between two orange things is not an orange barrel). Returns (yes or no, the share of body color, the share of stripe
    color)."""
    x0, y0, x1, y1 = s.bbox
    cols = mask[top:bottom, x0:x1]
    outside = np.ones(cols.shape[0], bool); outside[max(0, y0 - top):max(0, y1 - top)] = False
    region = cols[outside]
    other = _other(s.body)
    if not region.size:
        return True, 0.0, 0.0
    body_frac, other_frac = float((region == s.body).mean()), float((region == other).mean())
    ok = not ((region == s.body).sum() < (region == other).sum() or (region == s.body).mean() < cfg.body_min)
    return ok, body_frac, other_frac


# ---------------------------------------------------------------- one stripe, one box

def box_from_stripe(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(), others: tuple = (),
                    found: tuple = (), log: list | None = None, use_outline: bool = True) -> tuple[Found | None, str | None]:
    """One box from one stripe: (the box, None), or (None, the reason there is none).

    The stripe's row gives the distance; the distance gives the full barrel the geometry predicts (top, bottom, width).
    Four steps:
    1. ``read_edges``: top and bottom, seen where they agree with the prediction, else predicted.   "top_against_barrel"
       A thin piece must be a slice seen from top to bottom: neither edge inferred.                 "slice_not_full"
    2. ``place_sides``: left and right. A stripe seen whole: the body joined to it. A partly seen one: what is seen, then
       a reason for a hidden side, then the outline, then centred; the box is flagged "occluded".
                                                                              "side_unexplained" / thin: "outline_unknown"
    3. the box is at least 2 x 2 pixels,                                                             "empty_box"
       and ``holds_body``.                                                                           "body_min"
    ``others`` = the columns of the other stripes; ``found`` = the barrels found so far; ``use_outline=False`` leaves the
    outline out of step 2."""
    h, w = mask.shape
    at = _at(s, cam)
    if at is None:
        _note(log, "barrel", "no_geometry", s.bbox, body=s.body)
        return None, "no_geometry"
    x0, y0, x1, y1 = s.bbox
    W = at.W
    edges = read_edges(s, at, mask, cfg)
    if edges is None:
        _note(log, "barrel", "top_against_barrel", s.bbox, body=s.body)
        return None, "top_against_barrel"
    if s.thin and edges.inferred:
        # a thin piece is a barrel only as a slice seen from top to bottom, with or without a reason for a side (a reason says
        # where a barrel would be, not that there is one)
        _note(log, "barrel", "slice_not_full", s.bbox, body=s.body, expected_w=W)
        return None, "slice_not_full"
    flags = set(edges.inferred)
    top, bottom = max(0, edges.top), min(h, edges.bottom)
    placed = place_sides(s, mask, cam, W, top, bottom, at.bottom, cfg, others, found, full_slice=not edges.inferred, use_outline=use_outline)
    if placed is None:
        why = "outline_unknown" if s.thin else "side_unexplained"
        _note(log, "barrel", why, s.bbox, body=s.body, expected_w=W)
        return None, why
    bx0, bx1, rule = placed
    if rule != "whole_stripe":
        flags.add("occluded")
    bx0, bx1 = max(0, bx0), min(w, bx1)
    if bx1 - bx0 < 2 or bottom - top < 2:
        _note(log, "barrel", "empty_box", s.bbox, body=s.body)
        return None, "empty_box"
    ok, body_frac, other_frac = holds_body(s, mask, top, bottom, cfg)
    if not ok:
        _note(log, "barrel", "body_min", s.bbox, body=s.body, box=(bx0, top, bx1, bottom), body_frac=body_frac, other_frac=other_frac)
        return None, "body_min"
    if bx0 == 0 or bx1 == w or top == 0 or bottom == h:
        flags.add("truncated")
    conf = 0.5 + 0.5 * s.n_other / max(1, s.n_other + s.n_dark)   # the labeled share of the stripe's box
    return Found(Barrel(color=s.body, bbox=(bx0, top, bx1, bottom), confidence=conf, flags=frozenset(flags),
                        area=s.n_other + s.n_dark, source="det2"), rule, stripe=s, evidence=s.bbox), None


def piece_of_found(s: Stripe, found: list) -> bool:
    """Is the stripe piece ``s`` a second piece of the stripe of a barrel already found? Yes when it shares rows with that
    barrel's stripe (the overlap is at least half the height of the shorter of the two), has its body color, and its
    middle column is inside that barrel's box: two barrels cannot both have their stripe at the same rows inside one
    barrel's box. Only boxes of the stripe step (``Found.stripe``) are asked."""
    x0, y0, x1, y1 = s.bbox
    mid = (x0 + x1) / 2
    for f in found:
        if f.stripe is None:
            continue
        o, b = f.stripe, f.barrel
        if o.body == s.body and same_rows(y0, y1, o.bbox[1], o.bbox[3]) and b.bbox[0] <= mid < b.bbox[2]:
            return True
    return False


def boxes_from_stripes(stripes: list[Stripe], mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                       log: list | None = None) -> tuple[list[Found], list[Stripe], list[Stripe]]:
    """Stage 3. In: the stripes. Out: (the boxes; the stripes nothing could place, for stage 7; the stripes that lost to a
    surer box of the same barrel, for stage 6).

    Order: the stripes seen whole (at least stripe_full x W wide) first, left to right; then the partly seen ones, the
    lowest stripe row (the nearest barrel) first, because a partly seen stripe asks about the barrels found so far. Per
    stripe:

    1. A partly seen stripe that was not cut from a wider one: is it a second piece of a found barrel's stripe
       (``piece_of_found``)? Then no box.                                                            "stripe_piece"
    2. ``box_from_stripe``. A thin stripe is never among the "other stripes" whose columns a barrel's body may not take.
    3. Would the box sit on a box already found (same color, IoU over 0.5)? A box the outline placed never takes the place
       of a box that is already there: a thin piece gets no box ("duplicate"); any other is made again without the
       outline (and may then be left for stage 7).
    4. Is it the same barrel as a found box (same color, IoU over 0.5, and not another part cut from the same wide
       stripe)? The surer box stays: the one whose stripe's box holds the larger share of labeled pixels.  "duplicate"
       The stripe of the box that goes is "lost": still a stripe, so stage 6 does not read it as a cap."""
    def partly(s: Stripe) -> bool:
        at = _at(s, cam)
        return at is not None and (s.bbox[2] - s.bbox[0]) < cfg.stripe_full * at.W

    found: list[Found] = []
    unplaced: list[Stripe] = []
    lost: list[Stripe] = []
    order = [s for s in stripes if not partly(s)] + sorted((s for s in stripes if partly(s)), key=lambda s: -s.center_row)
    for s in order:
        if s.cut_from is None and partly(s) and piece_of_found(s, found):
            _note(log, "barrel", "stripe_piece", s.bbox, body=s.body)
            continue                                                                       # 1.
        others = tuple((o.bbox[0], o.bbox[2]) for o in stripes if o is not s and not o.thin)
        boxes = tuple(f.barrel for f in found)
        f, why = box_from_stripe(s, mask, cam, cfg, others, boxes, log)                    # 2.
        if f is not None and same_barrel(f.barrel.bbox, f.barrel.color, boxes):
            if s.thin:                                                                     # 3.
                _note(log, "barrel", "duplicate", s.bbox, body=s.body, box=f.barrel.bbox)
                continue
            f, why = box_from_stripe(s, mask, cam, cfg, others, boxes, use_outline=False)
        if f is None:
            if why == "side_unexplained":
                unplaced.append(s)
            continue
        _note(log, "barrel", "kept", s.bbox, body=s.body, box=f.barrel.bbox, rule=f.rule)
        dup = next((o for o in found if is_same_barrel(f.barrel.bbox, f.barrel.color, o.barrel)
                    and not (s.cut_from is not None and o.stripe.cut_from == s.cut_from)), None)
        if dup is None:
            found.append(f)
            continue
        _note(log, "barrel", "duplicate", s.bbox, body=s.body, box=f.barrel.bbox)         # 4.
        if f.barrel.confidence > dup.barrel.confidence and not s.thin:
            found = [o for o in found if o is not dup] + [f]
            lost.append(dup.stripe)
        else:
            lost.append(s)
    return found, unplaced, lost


# ================================================================ stage 4: a piece with no stripe

def _closeup_stripe_rows(cam: geo.CameraModel, top_row: float) -> tuple[float, float]:
    """(stripe top row, stripe bottom row) of a barrel whose lid's far edge is at ``top_row``. inf where the geometry puts
    them at or behind the camera (far below the frame). -inf for a top row at or above the horizon (``above_horizon``):
    no barrel has its top there, so no stripe is "below the frame". ``find_pieces`` refuses such a piece before it gets
    here."""
    d = axis_from_top_row(cam, top_row)
    if math.isinf(d):
        return -math.inf, -math.inf
    if d <= 0:
        return math.inf, math.inf
    try:
        r = cam.barrel_rows(d)
    except ValueError:
        return math.inf, math.inf
    return r.stripe_top, r.stripe_bottom


def _seen_to_stripe(cam: geo.CameraModel, cfg: DetConfig, top_row: int, seen_bottom: int, h: int) -> bool:
    """Is the piece's body seen from ``top_row`` down to where that row puts the stripe's top (or to the frame bottom,
    when that is higher), within max(bottom_tol_min_px, bottom_tol x that height)?"""
    target = min(float(h), _closeup_stripe_rows(cam, top_row)[0])
    tol = edge_tol(cfg, target - top_row)
    return seen_bottom >= target - tol


def _x_overlap(a: tuple, b: tuple) -> float:
    """Fraction of the narrower box's width that the two boxes share horizontally."""
    inter = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    return inter / max(1, min(a[2] - a[0], b[2] - b[0]))


def closeup_pieces(pieces: list[Piece], found: list[Found], mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                   log: list | None = None) -> list[Found]:
    """Stage 4. In: the pieces of stage 1 and the boxes so far. Out: the boxes of the pieces that are barrels without a
    stripe in view. Per piece, left to right:

    1. Does a box already account for it? They share more than 0.3 of the narrower one's width, and they share rows (a
       far barrel standing above a close-up in the picture must not hide it). A piece kept here counts too.   "covered"
    2. Is it a close-up, with its stripe below the frame? Either its box reaches the frame bottom (seen there, or drawn
       there because its top row predicts a base below the frame), or its top row puts the stripe's bottom edge at or
       below the frame bottom (the frame cuts the stripe: no body is seen below it, so it cannot be found as a stripe).
    3. A close-up that the left or right frame side also cuts shows neither its width nor its stripe: its body must be
       seen from its top row down to where that row puts the stripe (or to the frame bottom).            "closeup_side"
    4. Keep it if it is a close-up. Keep it also if the stripe expected at its MIDDLE row is under min_stripe_px tall:
       too far to resolve a stripe (rule "far_piece").                                               else "stripeless"

    Two facts these rules lean on. Both are settled in stage 1 (``find_pieces``):
    - every piece here has its top below the horizon (its check 2). So its top row gives a distance, and "no stripe
      row" in 2 and 3 can only mean "at or behind the camera", which is below the frame;
    - every piece here is on the table by its BOTTOM row (its check 1: nearer than about 637 mm with this camera, where
      a stripe is 4.3 px tall). The "too far" half of 4 asks about the MIDDLE row (a stripe under 4 px: beyond about
      687 mm). With this camera and these numbers no piece that stage 1 lets through can pass it: tried for every top
      row and every bottom row. It is kept as it is, for other numbers."""
    h, w = mask.shape
    new: list[Found] = []
    for piece in pieces:
        p = piece.barrel
        boxes = [f.barrel for f in found + new]
        if any(_x_overlap(p.bbox, o.bbox) > 0.3 and min(p.bbox[3], o.bbox[3]) > max(p.bbox[1], o.bbox[1]) for o in boxes):
            _note(log, "piece", "covered", p.bbox, body=p.color)
            continue                                                                       # 1.
        at = BarrelAt.from_stripe_row(cam, (p.bbox[1] + p.bbox[3]) / 2)                 # the row: the middle of the piece's box
        hs = at.Hs if at else math.inf
        rule = "closeup" if p.bbox[3] >= h else None                                       # 2.
        if rule is None and _closeup_stripe_rows(cam, p.bbox[1])[1] >= h:
            rule = "closeup_stripe"
        if rule is not None and (p.bbox[0] == 0 or p.bbox[2] == w) and not _seen_to_stripe(cam, cfg, p.bbox[1], piece.seen_bottom, h):
            _note(log, "piece", "closeup_side", p.bbox, body=p.color, seen_bottom=piece.seen_bottom)
            continue                                                                       # 3.
        if rule is None and hs < cfg.min_stripe_px:
            rule = "far_piece"                                                            # see the docstring: no piece gets here today
        if rule is not None:
            new.append(Found(p, rule))                                                     # 4.
        else:
            _note(log, "piece", "stripeless", p.bbox, body=p.color, expected_stripe_h=hs)
    return new


# ================================================================ stages 5 and 9: the verify step

def outline_layout(F: Barrel, cam: geo.CameraModel, shape) -> np.ndarray:
    """What a barrel whose box is F.bbox shows at each pixel, by its own layout: F's body color in its body rows, the other
    color in its stripe rows, 0 outside its outline, -1 within half a stripe height of a seam (either color).

    The outline is the box with the rounded corners of ``Outline`` (the top line runs down and the bottom line up toward the
    sides), at the distance the box's width gives, scaled to the box's height; the stripe's rows are the camera model's
    stripe rows for that distance, scaled the same way. Nothing is fit: the camera model and the barrel's sizes."""
    h, w = shape
    out = np.zeros(shape, np.int8)
    x0, y0, x1, y1 = F.bbox
    Wf = x1 - x0
    if Wf < 2 or y1 - y0 < 2:
        return out
    d = cam.f * geo.BARREL_BULGE_DIAMETER_MM / Wf
    try:
        ol = Outline.at(cam, d)
        r = cam.barrel_rows(d)
    except ValueError:
        return out
    scale = (y1 - y0) / max(1e-6, ol.bot_apex - ol.top_apex)
    H = r.bottom - r.top
    s0 = y0 + (y1 - y0) * (r.stripe_top - r.top) / H
    s1 = y0 + (y1 - y0) * (r.stripe_bottom - r.top) / H
    m = (s1 - s0) / 2
    other = _other(F.color)
    rows = np.arange(h) + 0.5
    lay = np.where((rows >= s0) & (rows < s1), other, F.color).astype(np.int8)
    lay[(np.abs(rows - s0) <= m) | (np.abs(rows - s1) <= m)] = -1
    cx = (x0 + x1) / 2
    for x in range(max(0, x0), min(w, x1)):
        u = (x + 0.5 - cx) / Wf
        t = y0 + scale * (float(ol.top(u)) - ol.top_apex)
        bt = y1 - scale * (ol.bot_apex - float(ol.bottom(u)))
        r0, r1 = max(0, int(math.ceil(t))), min(h, int(math.floor(bt)))
        out[r0:r1, x] = lay[r0:r1]
    return out


def drop_seen_through(found: list[Found], mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                      log: list | None = None) -> list[Found]:
    """Stages 5 and 9. A barrel cannot be seen through a nearer barrel. In: the boxes. Out: the boxes that pass, left to
    right (fewer than two boxes: nothing to do).

    Inside the outline of a barrel standing nearer (its bottom edge strictly lower in the picture), every pixel is that
    barrel's own picture: its body color in its body rows, its stripe color in its stripe rows (``outline_layout``;
    within half a stripe height of a seam, either color). A nearer barrel explains only where it is SEEN: between the
    top and the bottom of its body as walked from its evidence, not where its box was inferred.

    The boxes are taken nearest first, so only boxes that passed explain a farther one. Each box's evidence
    (``Found.evidence_box``: the box of the stripe, cap piece, band or slices it was read from; a piece is its own) is split into the
    barrel-colored pixels a nearer barrel explains and the rest, its OWN pixels. A box with a nearer barrel and fewer than
    min_area_px own pixels was read from the nearer barrel's picture: dropped ("verify", "front"). A real barrel behind
    another always shows its visible part outside the nearer one's outline.

    It runs twice. Stage 5, before the caps: the stages after it lean only on boxes that passed, and a dropped box's
    stripe is cap material again. Stage 9: once more on every box, whatever rule drew it."""
    if len(found) < 2:
        return found
    barrel = np.isin(mask, (ORANGE, BLUE))
    h, w = mask.shape
    kept: list[Found] = []
    seen_rows: dict[int, tuple[int, int]] = {}
    for f in sorted(found, key=lambda f: -f.barrel.bbox[3]):       # nearest first (lowest bottom edge)
        b = f.barrel
        ex0, ey0, ex1, ey1 = f.evidence_box
        ex0, ey0, ex1, ey1 = max(0, ex0), max(0, ey0), min(w, ex1), min(h, ey1)
        ev = barrel[ey0:ey1, ex0:ex1]
        n = int(ev.sum())
        nearer = [F for F in kept if F.barrel.bbox[3] > b.bbox[3]]   # bottoms equal: neither is nearer
        own, share = n, 0.0
        if n and nearer:
            ok = np.zeros((ey1 - ey0, ex1 - ex0), bool)
            for F in nearer:
                lay = outline_layout(F.barrel, cam, mask.shape)
                t, bt = seen_rows[id(F)]
                lay[:t] = 0; lay[bt:] = 0                          # F explains only where it is seen
                lay = lay[ey0:ey1, ex0:ex1]
                ok |= (lay == -1) | ((lay > 0) & (lay == mask[ey0:ey1, ex0:ex1]))
            own = int((ev & ~ok).sum())
            share = 1.0 - own / n
        if nearer and own < cfg.min_area_px:
            _note(log, "verify", "front", b.bbox, body=b.color, evidence=(ex0, ey0, ex1, ey1), explained=round(share, 3), own_px=own)
            continue
        if ex1 > ex0 and ey1 > ey0:
            t, bt = _body_extent(mask, b.color, ex0, ex1, ey0, ey1)
            seen_rows[id(f)] = (max(b.bbox[1], t), min(b.bbox[3], bt))
        else:
            seen_rows[id(f)] = (b.bbox[1], b.bbox[3])
        kept.append(f)
    return sorted(kept, key=lambda f: f.barrel.bbox[0])


def drop_single_reading(found: list[Found], mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                        log: list | None = None) -> list[Found]:
    """The last stage. A box placed from a guessed side needs a second reading that agrees with its distance. In: the
    boxes. Out: the boxes that pass, in the same order.

    The stripe step reads the distance off the stripe's row. A second reading is a seen edge where that distance puts
    it: the top, the bottom, or both sides (the body joined to the stripe seen stripe_full x W wide). A partly seen
    stripe's box (flag "occluded") with its top AND its bottom inferred, whose seen span is under stripe_full x W, has
    none: only the stripe's row. It is dropped ("verify", "readings"). Every other rule's box has a seen edge by the way
    it is made (a cap its top, a half stripe its far edge, pairs and thin pieces top and bottom).

    It measures the span again, a little differently from ``seen_span``: W comes from the middle row of the stripe's box
    (not the stripe's centre row), and the columns of other stripes are not left out."""
    out = []
    for f in found:
        b = f.barrel
        if b.source == "det2" and "occluded" in b.flags and {"top_inferred", "bottom_inferred"} <= b.flags:
            ex0, ey0, ex1, ey1 = f.evidence_box
            at = BarrelAt.from_stripe_row(cam, (ey0 + ey1) / 2)      # the row: the middle of the stripe's box, not its centre row
            if at is not None:
                W = at.W
                span = _body_span(mask, b.color, ex0, ex1, b.bbox[1], b.bbox[3], ey0, ey1) if b.bbox[3] - b.bbox[1] >= 2 else None
                trusted = span is not None and max(span[1], ex1) - min(span[0], ex0) <= cfg.body_width * W
                seen = (max(span[1], ex1) - min(span[0], ex0)) if trusted else (ex1 - ex0)
                if seen < cfg.stripe_full * W:
                    _note(log, "verify", "readings", b.bbox, body=b.color, evidence=(ex0, ey0, ex1, ey1), seen_w=seen, expected_w=W)
                    continue
        out.append(f)
    return out


# ================================================================ stage 6: caps

def _cap_pieces(mask: np.ndarray, c: int, boxes: list[Barrel], spent: list[Stripe], cfg: DetConfig) -> list[tuple]:
    """(x, y, width, height, area) of the pieces of color ``c`` that may be the top of a barrel behind a found one.

    Take that color's pixels (gaps closed) without the boxes of the stripes already read (``spent``: a stripe of this
    color sits on a barrel of the other color). A connected piece of min_area_px or more is a candidate when fewer than
    half of its pixels lie inside found boxes of its color (it is not a found barrel's own body). Of a piece that is half
    or more inside them, the parts OUTSIDE those boxes are candidates, each connected part by itself: the top of a barrel
    behind a found barrel of its own color."""
    cm = _closed(mask == c, cfg)
    for s in spent:
        if s.body != c:                                      # a stripe of this color, on a barrel of the other color
            x0, y0, x1, y1 = s.bbox
            cm[y0:y1, x0:x1] = False
    own = np.zeros(mask.shape, bool)
    for b in boxes:
        if b.color == c:
            own[b.bbox[1]:b.bbox[3], b.bbox[0]:b.bbox[2]] = True
    n, lab, st, _ = cv2.connectedComponentsWithStats(cm.astype(np.uint8), connectivity=8)
    cands = []
    for i in range(1, n):
        if int(st[i][4]) < cfg.min_area_px:
            continue
        if 2 * int((own & (lab == i)).sum()) < int(st[i][4]):
            cands.append(tuple(int(v) for v in st[i]))
        else:
            n2, _, st2, _ = cv2.connectedComponentsWithStats(((lab == i) & ~own).astype(np.uint8), connectivity=8)
            cands += [tuple(int(v) for v in st2[j]) for j in range(1, n2)]
    return cands


def _cap_box(piece: tuple, c: int, mask: np.ndarray, boxes: list[Barrel], caps: list[Barrel], cam: geo.CameraModel, cfg: DetConfig,
             log: list | None) -> Found | None:
    """The box of the barrel whose top is ``piece`` (x, y, width, height, area; color ``c``), or None. ``boxes`` = the found
    barrels, ``caps`` = the caps made before this one. The checks, in order (the numbers are those of ``caps_behind``):"""
    h, w = mask.shape
    x, y, bw, bh, area = piece
    if area < cfg.min_area_px or y <= 0:
        return None                                          # 1. a speck, or the top is cut by the frame: no top row to read
    at = BarrelAt.from_top_row(cam, y)
    if at is None:
        return None
    W, H, upper = at.W, at.H, at.upper
    cb = (x, y, x + bw, y + bh)
    if W < cfg.min_width_px:
        return None                                          # above the table's far end
    tol = edge_tol(cfg, H)
    if not (cfg.width_min * W <= bw <= widest_barrel(cfg) * W):
        _note(log, "cap", "width", cb, body=c, expected_w=W)
        return None                                          # 2. not barrel-wide for its row
    if not (cfg.width_min * upper <= bh <= upper + tol):
        _note(log, "cap", "height", cb, body=c, expected_upper_h=upper)
        return None                                          # 3. not as tall as an upper body (taller: body color where the stripe must be)
    bx0, bx1 = x, x + bw
    if bw >= cfg.stripe_full * W:
        bottom = y + cam.expected_barrel_height_px(d_axis_mm=cam.f * geo.BARREL_BULGE_DIAMETER_MM / bw)   # 4. the whole width shows: size from width
    else:
        # 5. a narrow cap must be explained: exactly one side hidden, by a found barrel standing nearer (its box holds the
        # pixel next to the cap at the cap's middle row, and its bottom is lower than the cap's) or by the frame edge.
        # Neither side: the narrowness has no cause. Both sides: a wedge between two barrels, neither its width nor its
        # place can be measured
        row, Wi = y + bh // 2, int(round(W))

        def hidden(px: int) -> bool:
            return px < 0 or px >= w or nearer_beside(boxes, row, (px,), y + bh)
        left_hidden, right_hidden = hidden(x - 1), hidden(x + bw)
        if left_hidden == right_hidden:
            _note(log, "cap", "both_sides" if left_hidden else "narrow", cb, body=c, expected_w=W)
            return None
        bottom = at.bottom                                   # size from the top row
        if left_hidden:
            bx0 = bx1 - Wi
        else:
            bx1 = bx0 + Wi
    # 6. the seen bottom is used when it agrees: the cap's own color, in the cap's columns, ending near the estimate
    col = (mask[:, x:x + bw] == c).any(axis=1)
    near = [r for r in range(max(y + bh, int(round(bottom - tol))), min(h, int(round(bottom + tol)) + 1)) if col[r]]
    if near and not col[near[-1] + 1:near[-1] + 4].any():
        bottom = near[-1] + 1
    elif bw < cfg.stripe_full * W:
        # 7. a narrow cap's estimate is the top-row bottom, 4 to 7 px low at mid and far range with this camera, so a seen end
        # can be refused for the estimate's error. Read the cap's color only beside the nearer found barrels (inside their
        # boxes it is their stripe). The barrel is at least as wide as what is seen of it, so its bottom is not above that
        # of a barrel bw wide (a bound that does not depend on the tilt), and not below the estimate + the tolerance
        beside = np.ones(bw, bool)
        for b in standing_nearer(boxes, y + bh):
            beside[max(0, b.bbox[0] - x):max(0, b.bbox[2] - x)] = False
        least = y + cam.expected_barrel_height_px(d_axis_mm=cam.f * geo.BARREL_BULGE_DIAMETER_MM / bw)
        col = (mask[:, x:x + bw][:, beside] == c).any(axis=1)
        seen = [r for r in range(max(y + bh, int(round(least))), min(h, int(round(bottom + tol)) + 1)) if col[r]]
        if seen and not col[seen[-1] + 1:seen[-1] + 4].any():
            bottom = seen[-1] + 1
    bx0, bx1, bottom = max(0, bx0), min(w, bx1), min(h, int(round(bottom)))
    below = np.zeros((max(0, bottom - (y + bh)), bx1 - bx0), bool)       # where the rest of this barrel should be
    for b in standing_nearer(boxes, bottom):
        below[max(0, b.bbox[1] - (y + bh)):max(0, b.bbox[3] - (y + bh)), max(0, b.bbox[0] - bx0):max(0, b.bbox[2] - bx0)] = True
    if below.size == 0 or below.mean() < 0.5:
        _note(log, "cap", "not_hidden", cb, body=c, hidden_frac=float(below.mean()) if below.size else 0.0)
        return None                                          # 8. nothing found stands in front of it
    box = (bx0, y, bx1, bottom)
    if same_barrel(box, c, boxes + caps):
        _note(log, "cap", "duplicate", cb, body=c, box=box)
        return None                                          # 9.
    flags = {"occluded", "bottom_inferred"}
    if bx0 == 0 or bx1 == w or bottom == h:
        flags.add("truncated")
    _note(log, "cap", "kept", cb, body=c, box=box)
    return Found(Barrel(color=c, bbox=box, confidence=0.5, flags=frozenset(flags), area=area, source="det3"), "cap", evidence=cb)


def caps_behind(found: list[Found], lost: list[Stripe], mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                log: list | None = None) -> list[Found]:
    """Stage 6. Barrels standing behind a found barrel. In: the boxes so far and the stripes that lost to a surer box
    (``boxes_from_stripes``). Out: the new boxes (source "det3", flags occluded and bottom_inferred, confidence 0.5).

    Such a barrel shows its upper body (its "cap") above the front barrel; its stripe has melted into the front
    barrel's body of the same color, or is hidden, so the stripe step cannot find it. The distance comes from the cap's
    TOP ROW: it gives the expected width W, the height H and the height of an upper body (top row to the stripe's top).
    Per color, per candidate piece (``_cap_pieces``), the checks of ``_cap_box``:

    1. its top row can be read (not at the frame top) and is on the table (W at least min_width_px);     no note
    2. barrel-wide: width_min to body_width x W;                                                         "width"
    3. as tall as an upper body, not more: width_min x the upper body, to the upper body + the edge tolerance;  "height"
    4. the whole width shows (stripe_full x W): the bottom is the top + the height of a barrel as wide as the cap;
    5. a narrower cap: exactly one side hidden, by the frame edge or by a found barrel beside it whose bottom is lower
       than the cap's. It is widened to W toward that side; the bottom is the one the top row predicts.
                                                                                       "narrow" / "both_sides"
    6. the cap's own color seen ending within the edge tolerance of that bottom (and 3 empty rows after it) is the bottom;
    7. else, for a narrow cap: its color seen ending beside the nearer found barrels, between the bottom of a barrel
       only as wide as the seen cap and the estimate + the tolerance, is the bottom;
    8. what hides the rest is a barrel: at least half of the box below the cap lies inside found boxes whose bottom
       edge is lower than this box's;                                                                    "not_hidden"
    9. not the same barrel as a found box or an earlier cap (same color, IoU over 0.5).                  "duplicate\""""
    boxes = [f.barrel for f in found]
    spent = [f.stripe for f in found if f.stripe is not None] + list(lost)
    new: list[Found] = []
    for c in (ORANGE, BLUE):
        for piece in _cap_pieces(mask, c, boxes, spent, cfg):
            cap = _cap_box(piece, c, mask, boxes, [f.barrel for f in new], cam, cfg, log)
            if cap is not None:
                new.append(cap)
    return new


# ================================================================ stage 7: pairs

def _full_slice(s: Stripe, mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig):
    """For a narrow stripe piece: (W, top, bottom, sx0, sx1) when it is a FULL SLICE of a barrel, else None. A full
    slice: the body color above and below the piece ends where the piece's row predicts the barrel's top and bottom
    (the usual edge tolerance: bottom_tol of the height, at least bottom_tol_min_px), and neither end lies against the
    other barrel color (that color in at least half of the piece's columns in the 4 rows beyond the end: a strip of a
    barrel's upper body between a finger and its own stripe is not a slice of a barrel of the other color). ``top``,
    ``bottom`` = those seen ends; ``sx0``, ``sx1`` = the piece's columns joined with the body joined to it
    (``_body_span``)."""
    at = _at(s, cam)
    if at is None:
        return None
    x0, y0, x1, y1 = s.bbox
    top, bottom = _body_extent(mask, s.body, x0, x1, y0, y1)
    tol = at.tol(cfg)
    if abs(top - at.top) > tol or abs(bottom - at.bottom) > tol:
        return None
    other = (_other(s.body),)
    if ends_against(mask, other, top - 4, top, x0, x1) or ends_against(mask, other, bottom, bottom + 4, x0, x1):
        return None
    span = _body_span(mask, s.body, x0, x1, max(0, top), min(mask.shape[0], bottom), y0, y1) if bottom - top >= 2 else None
    sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if span else (x0, x1)
    return at.W, top, bottom, sx0, sx1


def post_pairs(pieces: list[Stripe], found: list[Found], mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
               log: list | None = None) -> list[Found]:
    """Stage 7. One barrel behind a post. In: the stripe pieces that gave no box alone (the finder's left-over pieces,
    and the stripes stage 3 could not place) and the boxes so far. Out: the new boxes (flag occluded, confidence 0.5).

    A piece counts when it is not a second piece of a found barrel's stripe (``piece_of_found``), is a full slice
    (``_full_slice``: its body ends where its row predicts the top and the bottom), and is under stripe_w_min x W wide (a
    wider piece is placed alone). Two such pieces, the left one wholly left of the right one, are one barrel when

    1. they have one body color and share rows: the overlap is at least half the height of the shorter;
    2. their outer body edges are stripe_full to body_width x W apart (W = the mean of the two);
    3. the box is not the same barrel as a found box or an earlier pair (same color, IoU over 0.5).       "duplicate"

    Two barrels at one distance cannot have their outer edges within 1.2 W of each other, so the two slices are one
    barrel with something upright in front of its middle (or with its stripe and body cut by a highlight). The box runs
    from outer edge to outer edge; top and bottom are the seen ones."""
    h, w = mask.shape
    info = []
    for s in sorted(pieces, key=lambda s: s.bbox[0]):
        f = None if piece_of_found(s, found) else _full_slice(s, mask, cam, cfg)
        if f is not None and (s.bbox[2] - s.bbox[0]) < cfg.stripe_w_min * f[0]:
            info.append((s, *f))
    boxes = [f.barrel for f in found]
    out: list[Found] = []
    paired: list[Stripe] = []
    for i, (l, Wl, tl, bl, lx0, _) in enumerate(info):
        for r, Wr, tr, br, _, rx1 in info[i + 1:]:
            if any(l is p or r is p for p in paired) or l.body != r.body or r.bbox[0] < l.bbox[2]:
                continue
            if not same_rows(l.bbox[1], l.bbox[3], r.bbox[1], r.bbox[3]):
                continue                                                                   # 1.
            W = (Wl + Wr) / 2
            if not (cfg.stripe_full * W <= rx1 - lx0 <= widest_barrel(cfg) * W):
                continue                                                                   # 2.
            box = (max(0, lx0), max(0, min(tl, tr)), min(w, rx1), min(h, max(bl, br)))
            if same_barrel(box, l.body, boxes + [f.barrel for f in out]):
                _note(log, "pair", "duplicate", l.bbox, body=l.body, box=box)
                continue                                                                   # 3.
            flags = {"occluded"} | ({"truncated"} if box[0] == 0 or box[2] == w or box[1] == 0 or box[3] == h else set())
            out.append(Found(Barrel(color=l.body, bbox=box, confidence=0.5, flags=frozenset(flags), area=l.n_other + r.n_other,
                                    source="det2"), "pair",
                             evidence=(min(l.bbox[0], r.bbox[0]), min(l.bbox[1], r.bbox[1]), max(l.bbox[2], r.bbox[2]), max(l.bbox[3], r.bbox[3]))))
            paired += [l, r]
            _note(log, "pair", "kept", l.bbox, body=l.body, box=box, other=r.bbox, expected_w=W, outer_span=rx1 - lx0)
    return out


# ================================================================ stage 8: half stripes

def half_stripes(found: list[Found], mask: np.ndarray, cam: geo.CameraModel, cfg: DetConfig = DetConfig(),
                 log: list | None = None, layers: dict | None = None) -> list[Found]:
    """Stage 8. Barrels hidden from above or from below by something that is not a barrel, found from a stripe that has
    body color on ONE side only. In: the boxes so far. Out: the boxes, with the new ones added (flags occluded and
    top_inferred or bottom_inferred, confidence 0.5) and the boxes they replace taken out.

    Done per body color (``layers`` = the image's ``sandwiches``, when the caller has them). A band = a connected piece
    (min_area_px or more) of the other barrel color. "Body right above"
    a column of it = the body color within band_h_max stripe heights above the band there (the stripe finder's
    sandwich, one side). The checks, in order:

     1. body right below in at least stripe_full of its columns and right above in at most 1 - stripe_full: "top
        hidden" (the stripe and the lower body show). The reverse: "bottom hidden". Else not a half stripe.   no note
     2. the SEAM between band and body gives the distance: the stripe's top edge is 15 mm above the table and its bottom
        edge 9 mm, at the bulge. The barrel is on the table (W at least min_width_px, stripe min_stripe_px).    no note
     3. the band is not taller than a stripe (stripe_h_max x the stripe height). There is no floor: a barrel half hidden
        from below shows a few rows of its stripe.                                                        "height"
     4. the whole width shows: the band is stripe_full to body_width x W wide.                            "width"
     5. the second reading agrees: the body's far edge (its bottom when the top is hidden, its top when the bottom is)
        is where the seam predicts it, within the edge tolerance, and inside the frame.                   "far_edge"
     6. it is the thinner band: less tall than the body part beside it (seam to far edge). A stripe is 6 mm, a body
        part 9 mm or more; else a barrel hidden from below whose stripe shows whole would also pass as a smaller barrel
        of the other color hidden from above.                                                    "thicker_than_body"
     7. the body joined to the band is stripe_full to body_width x W wide.                                "body_width"
     8. the open side is clear: barrel color in the 4 rows beyond the band in fewer than half of its columns.  "open_side"
     9. the body's far edge is a seen edge: not against barrel color (the same test beyond that edge). An ordinary
        barrel's upper body and stripe pass 1 to 8 as the "stripe and lower body" of a smaller barrel of the other
        color; its "bottom" ends against the real barrel's lower body.                    "far_edge_against_barrel"
    10. it is not a found barrel's: fewer than half of the band's pixels inside found boxes, and no found box of its
        color overlapping the new box by more than half.                                                  "found"

    The box: sides = the seen band and body; the seen far edge; the hidden edge where the seam's distance puts it. A box
    the stripe step made from a narrow, partly seen piece of this same band (flag occluded, its stripe inside the band's
    box) is a corner of it: it does not count as "found" in 10, and the new box REPLACES it."""
    h, w = mask.shape
    barrel = np.isin(mask, (ORANGE, BLUE))
    z_top, z_bottom = (geo.BARREL_HEIGHT_MM + geo.STRIPE_HEIGHT_MM) / 2, (geo.BARREL_HEIGHT_MM - geo.STRIPE_HEIGHT_MM) / 2
    new: list[Found] = []
    replaced: list[Found] = []
    for body, sw in (layers or sandwiches(mask, cam, cfg)).items():
        up, dn, above, below = sw.up, sw.dn, sw.above, sw.below
        n, lab, st, _ = cv2.connectedComponentsWithStats(sw.stripe.astype(np.uint8), connectivity=8)
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
                continue                                                                   # 1. body on both sides (a stripe) or on neither
            sb = (x, y, x + bw, y + bh)
            first = y + np.argmax(sel[:, cols], axis=0)                                    # first and last band row, per column
            last = y + bh - 1 - np.argmax(sel[::-1][:, cols], axis=0)
            if top_hidden:
                seams = dn[last, x + cols]; seams = seams[seams < 10 ** 5]                 # first body row under the band
                seam, z = (float(np.median(seams)) if len(seams) else math.nan), z_bottom
            else:
                seams = up[first, x + cols]; seams = seams[seams > -10 ** 5]               # one past the last body row above it
                seam, z = (float(np.median(seams)) + 1 if len(seams) else math.nan), z_top
            at = BarrelAt.from_seam_row(cam, seam, z)
            if at is None:
                continue                                                                   # 2.
            W, H, Hs = at.W, at.H, at.Hs
            if W < cfg.min_width_px or Hs < cfg.min_stripe_px:
                continue
            ys = np.where(sel)[0]
            core_h = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
            if core_h > cfg.stripe_h_max * Hs:
                _note(log, "half", "height", sb, body=body, core_h=core_h, expected_stripe_h=Hs)
                continue                                                                   # 3.
            if not (cfg.stripe_full * W <= bw <= widest_barrel(cfg) * W):
                _note(log, "half", "width", sb, body=body, expected_w=W)
                continue                                                                   # 4.
            tol = edge_tol(cfg, H)
            top_s, bottom_s = _body_extent(mask, body, x, x + bw, y, y + bh)
            if top_hidden:
                agrees, r0, r1 = abs(bottom_s - at.bottom) <= tol and bottom_s < h, y, bottom_s
            else:
                agrees, r0, r1 = abs(top_s - at.top) <= tol and top_s > 0, top_s, y + bh
            if not agrees:
                _note(log, "half", "far_edge", sb, body=body, seen=bottom_s if top_hidden else top_s, predicted=at.bottom if top_hidden else at.top)
                continue                                                                   # 5.
            if core_h >= ((bottom_s - seam) if top_hidden else (seam - top_s)):
                _note(log, "half", "thicker_than_body", sb, body=body, core_h=core_h)
                continue                                                                   # 6.
            span = _body_span(mask, body, x, x + bw, r0, r1, y, y + bh) if r1 - r0 >= 2 else None
            sx0, sx1 = (min(span[0], x), max(span[1], x + bw)) if span else (x, x + bw)
            if span is None or not (cfg.stripe_full * W <= sx1 - sx0 <= widest_barrel(cfg) * W):
                _note(log, "half", "body_width", sb, body=body, expected_w=W)
                continue                                                                   # 7.
            beyond = [(max(0, f - 4), f) for f in first] if top_hidden else [(l + 1, min(h, l + 5)) for l in last]
            if float(np.mean([barrel[a:b, x + c].any() for (a, b), c in zip(beyond, cols)])) >= 0.5:
                _note(log, "half", "open_side", sb, body=body)
                continue                                                                   # 8.
            e0 = bottom_s if top_hidden else top_s - 4                                     # the 4 rows beyond the far edge
            if ends_against(mask, (ORANGE, BLUE), e0, e0 + 4, x, x + bw):
                _note(log, "half", "far_edge_against_barrel", sb, body=body)
                continue                                                                   # 9.
            box = (max(0, sx0), max(0, int(round(at.top))) if top_hidden else top_s, min(w, sx1), bottom_s if top_hidden else min(h, int(round(at.bottom))))
            if box[2] - box[0] < 2 or box[3] - box[1] < 2:
                continue
            # boxes the stripe step made from a narrow, partly seen piece of this same band
            corners = [f for f in found if f.stripe is not None and f.stripe.body == body and "occluded" in f.barrel.flags
                       and x <= f.stripe.bbox[0] and f.stripe.bbox[2] <= x + bw and y <= f.stripe.bbox[1] and f.stripe.bbox[3] <= y + bh]
            others = [f.barrel for f in found + new if not any(f is c for c in corners)]
            inside = np.zeros(sel.shape, bool)
            for b in others:
                inside[max(0, b.bbox[1] - y):max(0, b.bbox[3] - y), max(0, b.bbox[0] - x):max(0, b.bbox[2] - x)] = True
            if 2 * int((sel & inside).sum()) >= area or same_barrel(box, body, others):
                _note(log, "half", "found", sb, body=body, box=box)
                continue                                                                   # 10.
            flags = {"occluded", "top_inferred" if top_hidden else "bottom_inferred"}
            if box[0] == 0 or box[2] == w or box[1] == 0 or box[3] == h:
                flags.add("truncated")
            new.append(Found(Barrel(color=body, bbox=box, confidence=0.5, flags=frozenset(flags), area=area, source="det2"), "half_stripe",
                             evidence=sb))
            replaced += corners
            _note(log, "half", "kept", sb, body=body, box=box, hidden="top" if top_hidden else "bottom", seam=seam, distance_mm=at.d, expected_w=W,
                  expected_h=H, expected_stripe_h=Hs, core_h=core_h, predicted_top=at.top, predicted_bottom=at.bottom, tol=tol,
                  seen_far_edge=bottom_s if top_hidden else top_s, body_span=(sx0, sx1))
    return [f for f in found if not any(f is r for r in replaced)] + new


# ================================================================ the output image

BOX_COLOR_BGR = {ORANGE: (0, 255, 255), BLUE: (0, 255, 0)}   # yellow = orange barrel, green = blue barrel (Dave's convention)


def draw(image_bgr: np.ndarray, barrels: list[Barrel], thickness: int = 1) -> np.ndarray:
    """The v2 output image: the input with one 1-px rectangle per barrel, yellow for an orange barrel and green
    for a blue one, so the lines stand out from the barrels themselves, and nothing else."""
    out = image_bgr.copy()
    for b in barrels:
        x0, y0, x1, y1 = b.bbox
        cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), BOX_COLOR_BGR[b.color], thickness)
    return out
