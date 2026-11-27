"""Shared by the scripts of 2026-11-26_bottom: the "more paint" color steps, which box is on which barrel, the
bottom-edge numbers and the contact sheets. Train frames only: every frame is read through ``judge.load_frame``,
which refuses any other.

    PAINT            the color steps, in order: the fixed model and five versions with more (or better) paint
    masks_for        one frame -> its class mask under every color step
    detect_found     ``detector.detect`` with the rule that drew each box kept (the same boxes; asserted by the callers)
    pair_frame       which box is on which true barrel (the pairing ``counting.classify_frame`` makes, kept)
    why_off          for a "found, box off" barrel: is the bottom edge the only thing wrong?
    stat             median and 90th percentile of the bottom-edge error
    panel, sheet     a contact sheet: the picture and the mask around one barrel, with the boxes drawn
"""
from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

import cv2
import numpy as np

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import hsrange as hx  # noqa: E402
from barrels import io  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

assert Path(det.__file__).resolve().is_relative_to(BARRELS), f"barrels is imported from {det.__file__}, not from this checkout"

CAM = geo.AIM_4A8B6118_BOXFIT
OUT = BARRELS / "results" / "2026-11-26_bottom"
NEAR_H = 40                 # a true box at least this tall is "near" (about 28 cm and nearer), a shorter one "far"

# ---------------------------------------------------------------- the color steps

PAINT = ("fixed", "s20", "s40", "hue3", "dil1", "hand")
PAINT_TEXT = {"fixed": "the fixed color model (what runs today)",
              "s20": "both saturation floors lowered by 20 (orange 140 -> 120, blue 113 -> 93)",
              "s40": "both saturation floors lowered by 40 (orange 100, blue 73)",
              "hue3": "both hue ranges widened by 3 at each end (orange 0-16, blue 100-122)",
              "dil1": "the fixed model's mask with one pixel added around each color (3 x 3 dilation)",
              "hand": "Tanush's hand thresholds: per condition the median of its slider labels (others keep the fixed model)"}
_K3 = np.ones((3, 3), np.uint8)
_models: dict = {}


def dilate1(m: np.ndarray) -> np.ndarray:
    """One pixel added around each color; a pixel that already has a color keeps it (as experiments/2026-11-26_collapse)."""
    out = m.copy()
    for c in (1, 2):
        out[(out == 0) & (cv2.dilate((m == c).astype(np.uint8), _K3) > 0)] = c
    return out


def _shifted(base: pl.Model, ds: int = 0, dh: int = 0) -> pl.Model:
    t = hl.thresholds_from_model(base)
    for c in ("orange", "blue"):
        t[c]["s_lo"] -= ds
        t[c]["h_lo"] -= dh
        t[c]["h_hi"] += dh
    return hl.model_from_thresholds(base, t)


def hand_thresholds(stems) -> dict[str, tuple]:
    """condition -> the six numbers: the median of the slider labels of that condition's frames (as
    experiments/2026-11-26_judge/run.py). ``stems`` must be train frames."""
    by = defaultdict(list)
    for s in stems:
        if io.hs_path(s).exists():
            d = io.load_hs(s, check_image=False)
            by[ct.condition_of(s)].append([d["orange"]["h_lo"], d["orange"]["h_hi"], d["orange"]["s_lo"], d["blue"]["h_lo"], d["blue"]["h_hi"], d["blue"]["s_lo"]])
    return {c: tuple(int(round(x)) for x in np.median(np.array(v, float), 0)) for c, v in sorted(by.items())}


def models(train_stems) -> dict:
    """The color models of the steps (made once per process). "hand" is a dict condition -> model."""
    if not _models:
        base = hl.adopted_model()
        _models.update(fixed=base, s20=_shifted(base, ds=20), s40=_shifted(base, ds=40), hue3=_shifted(base, dh=3),
                       hand={c: hl.model_from_thresholds(base, hx.nested(dict(zip(hx.THRESHOLDS, six)))) for c, six in hand_thresholds(train_stems).items()})
    return _models


def masks_for(stem: str, frame, train_stems) -> dict[str, np.ndarray]:
    """The frame's class mask under every color step. No pixel of the picture is changed: each step is a threshold
    setting, or (dil1) an operation on the mask."""
    m = models(train_stems)
    fixed = pl.segment(frame, m["fixed"])[0]
    hand = m["hand"].get(ct.condition_of(stem))
    return {"fixed": fixed, "s20": pl.segment(frame, m["s20"])[0], "s40": pl.segment(frame, m["s40"])[0], "hue3": pl.segment(frame, m["hue3"])[0],
            "dil1": dilate1(fixed), "hand": fixed if hand is None else pl.segment(frame, hand)[0]}


# ---------------------------------------------------------------- the detector, with the rule of each box

def detect_found(mask: np.ndarray, cfg: det.DetConfig = det.DetConfig(), cam=CAM) -> list:
    """``detector.detect``, stage for stage, returning the ``Found`` objects (the box and the rule that drew it), left
    to right. The boxes are those of ``detect``: the callers assert it on every mask."""
    layers = det.sandwiches(mask, cam, cfg)
    pieces = det.find_pieces(mask, cam, cfg)
    stripes, leftover = det.find_stripes(mask, cam, cfg, None, layers)
    found, unplaced, lost = det.boxes_from_stripes(stripes, mask, cam, cfg)
    found = found + det.closeup_pieces(pieces, found, mask, cam, cfg)
    found = det.drop_seen_through(found, mask, cam, cfg)
    found = found + det.caps_behind(found, lost, mask, cam, cfg)
    found = found + det.post_pairs(leftover + unplaced, found, mask, cam, cfg)
    found = det.half_stripes(found, mask, cam, cfg, None, layers)
    found = det.drop_seen_through(found, mask, cam, cfg)
    found = det.drop_single_reading(found, mask, cam, cfg)
    return sorted(found, key=lambda f: f.barrel.bbox[0])


# ---------------------------------------------------------------- which box is on which barrel

def pair_frame(stem: str, preds: list, gts: list, clean: bool = True) -> tuple[ct.FrameCount, dict[int, int]]:
    """(the frame's count, {true barrel -> the box that is on it}) for the barrels that are ``found`` or ``off``. The
    pairing is the one ``counting.classify_frame`` makes (strict hits first, then same-color boxes that are on a barrel,
    highest overlap first); it is redone here only to keep it, and checked against that function."""
    def iou(p, g) -> float:
        return ed.box_iou(p.bbox, g.bbox)
    fc = ct.classify_frame(stem, preds, gts, clean)
    pair: dict[int, int] = {}
    for pi, gi, _ in ed.match_best_first(preds, gts, iou, ed.IOU_THR, same_class=True, eligible=ed.bottom_within_tol):
        pair[gi] = pi
    taken = set(pair.values())
    rest_p = [i for i in range(len(preds)) if i not in taken]
    rest_g = [i for i in range(len(gts)) if i not in pair]
    for a, b, _ in ed.match_best_first([preds[i] for i in rest_p], [gts[i] for i in rest_g], iou, 0.0, same_class=True, eligible=ct.is_on):
        pair[rest_g[b]] = rest_p[a]
    assert all((gi in pair) == (st != ct.MISSED) for gi, st in enumerate(fc.gt)), stem
    return fc, pair


def why_off(p, g) -> str:
    """For a box ``p`` that is on the true barrel ``g`` and fails the strict rule:

    "bottom"       the overlap passes (IoU >= 0.5) and only the bottom edge is outside the scorer's tolerance;
    "bottom+iou"   both fail, and with the box's bottom put on the true bottom it would be a strict hit: the bottom edge
                   is the one thing wrong;
    "other"        it would still fail with the bottom right (too narrow, too wide, the visible part of a hidden barrel),
                   or the strict matching gave its barrel or its box to another."""
    iou_ok = ed.box_iou(p.bbox, g.bbox) >= ed.IOU_THR
    bot_ok = ed.bottom_within_tol(p, g)
    if iou_ok and not bot_ok:
        return "bottom"
    moved = (p.bbox[0], min(p.bbox[1], g.bbox[3] - 1), p.bbox[2], g.bbox[3])
    if not bot_ok and ed.box_iou(moved, g.bbox) >= ed.IOU_THR:
        return "bottom+iou"
    return "other"


def bottom_err(p, g) -> tuple[float, float]:
    """(px, share of the true height): the box's bottom row minus the true one; positive = the box ends lower."""
    e = p.bottom_row - g.bottom_row
    return float(e), e / g.height


def stat(values) -> dict:
    """n, the median and the 90th percentile of the absolute values, and the median of the signed ones."""
    v = np.asarray(list(values), float)
    if v.size == 0:
        return {"n": 0, "med": float("nan"), "p90": float("nan"), "signed": float("nan")}
    return {"n": int(v.size), "med": float(np.median(np.abs(v))), "p90": float(np.percentile(np.abs(v), 90)), "signed": float(np.median(v))}


def is_near(g) -> bool:
    return g.height >= NEAR_H


def measurable(g, frame_h: int = 480) -> bool:
    """A true bottom that says where the barrel stands: inside the frame, and not flagged as estimated by the labeller."""
    return g.bbox[3] < frame_h and "bottom_estimated" not in g.flags


def as_barrel(d: dict):
    """A box stored by the scripts (color, bbox, flags, source, confidence) as a ``Barrel``."""
    from barrels.detect_types import Barrel
    return Barrel(color=int(d["color"]), bbox=tuple(int(v) for v in d["bbox"]), confidence=float(d.get("confidence", 1.0)),
                  flags=frozenset(d.get("flags", ())), source=d.get("source", ""))


def box_dict(b, **more) -> dict:
    return {"color": int(b.color), "bbox": [int(v) for v in b.bbox], "flags": sorted(b.flags), "source": b.source,
            "confidence": round(float(b.confidence), 6), **more}


# ---------------------------------------------------------------- contact sheets

MASK_BGR = {0: (40, 40, 40), 1: (0, 140, 255), 2: (255, 120, 0)}


def panel(bgr: np.ndarray, mask: np.ndarray, gt_box, boxes: list, text: list[str], scale: int = 4, pad: int = 14,
          rows: list | None = None) -> np.ndarray:
    """One barrel: the picture (left) and the class mask (right) around the true box, enlarged, with the true box in
    white and ``boxes`` = [(bbox, BGR color)] on both. ``rows`` = [(row, BGR color)]: horizontal lines (a predicted
    bottom). ``text``: lines written under the two crops. The crop of the picture is a copy; no pixel of the frame is
    changed."""
    h, w = mask.shape
    xs = [gt_box[0], gt_box[2]] + [v for b, _ in boxes for v in (b[0], b[2])]
    ys = [gt_box[1], gt_box[3]] + [v for b, _ in boxes for v in (b[1], b[3])]
    x0, x1 = max(0, min(xs) - pad), min(w, max(xs) + pad)
    y0, y1 = max(0, min(ys) - pad), min(h, max(ys) + pad)
    left = cv2.resize(bgr[y0:y1, x0:x1].copy(), None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    colored = np.zeros((h, w, 3), np.uint8)
    for c, col in MASK_BGR.items():
        colored[mask == c] = col
    right = cv2.resize(colored[y0:y1, x0:x1], None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

    def draw(img):
        def rect(b, col, t):
            cv2.rectangle(img, ((b[0] - x0) * scale, (b[1] - y0) * scale), ((b[2] - x0) * scale - 1, (b[3] - y0) * scale - 1), col, t)
        rect(gt_box, (255, 255, 255), 1)
        for b, col in boxes:
            rect(b, col, 2)
        for r, col in rows or []:
            yy = int(round((r - y0) * scale))
            if 0 <= yy < img.shape[0]:
                cv2.line(img, (0, yy), (img.shape[1] - 1, yy), col, 1)
    draw(left); draw(right)
    both = np.hstack([left, np.full((left.shape[0], 6, 3), 255, np.uint8), right])
    strip = np.full((16 * len(text) + 6, both.shape[1], 3), 255, np.uint8)
    for i, t in enumerate(text):
        cv2.putText(strip, t, (3, 14 + 16 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    return np.vstack([both, strip])


def sheet(panels: list[np.ndarray], path: Path, width: int = 1900) -> Path:
    """Tile the panels into rows no wider than ``width`` and write one PNG."""
    rows, cur, cur_w = [], [], 0
    for p in panels:
        if cur and cur_w + p.shape[1] + 8 > width:
            rows.append(cur); cur, cur_w = [], 0
        cur.append(p); cur_w += p.shape[1] + 8
    if cur:
        rows.append(cur)
    out_rows = []
    for r in rows:
        hh = max(p.shape[0] for p in r)
        cells = []
        for p in r:
            cells += [np.vstack([p, np.full((hh - p.shape[0], p.shape[1], 3), 255, np.uint8)]), np.full((hh, 8, 3), 255, np.uint8)]
        out_rows.append(np.hstack(cells))
    ww = max(r.shape[1] for r in out_rows) if out_rows else 10
    full = np.vstack([np.vstack([np.hstack([r, np.full((r.shape[0], ww - r.shape[1], 3), 255, np.uint8)]), np.full((8, ww, 3), 255, np.uint8)])
                      for r in out_rows]) if out_rows else np.full((10, 10, 3), 255, np.uint8)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), full)
    return path
