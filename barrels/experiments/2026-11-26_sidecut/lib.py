"""Shared code of the side-cut experiment (PREREG.md): frames, source barrels, scenes, scoring.

Train frames only. Every frame is read through ``judge.load_frame`` (it refuses anything that is not a train frame,
before the image is opened) and every list of stems goes through ``judge.require_train``. No pixel is changed: the
scenes are made on class MASKS (``barrels.occlude``), as the occlusion scorecard does.
"""
from __future__ import annotations

import dataclasses
import functools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "src"
sys.path.insert(0, str(SRC))
import barrels  # noqa: E402

assert Path(barrels.__file__).resolve().is_relative_to(SRC), f"barrels is imported from {barrels.__file__}, not from {SRC}"
from barrels import detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, judge as jg, occlude as oc  # noqa: E402
from barrels import pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
OUT = io.PKG_ROOT / "results" / "2026-11-26_sidecut"
POOLS = {"HOME": "4A8B_window_light_", "CAMPUS": "4A8B_campus_light_", "ABP white": "4A8B_window_abpwhite_"}
MODES = ("centred", "own_side", "own_side+centred")       # DetConfig.side_cut: today, the candidate, the comparison arm
AMOUNTS = (0.5, 0.6, 0.65, 0.75)                          # the hidden share of the width
SHORT_PX = 6                                              # the "real-like" variant: the stripe ends this many pixels before the cut
CENTRE_TOL = 0.10                                         # "placed": the box's centre column within this x the true width of the true centre
EDGE_MARGIN, OVERLAP_MAX = 3, 2                           # a source barrel: as in the occlusion scorecard (2026-11-19_det_occl)

# every kind of scene of the occlusion scorecard: (key, kind, color)
ROWS = [("frame", "frame", None), ("edge", "edge", None), ("slant", "slant", None), ("both", "both", None), ("top", "top", None),
        ("bottom", "bottom", None), ("post", "post", None), ("barrel_side/other", "barrel_side", "other"),
        ("barrel_low/other", "barrel_low", "other"), ("barrel_front/other", "barrel_front", "other"),
        ("barrel_side/same", "barrel_side", "same"), ("barrel_low/same", "barrel_low", "same"),
        ("barrel_front/same", "barrel_front", "same"), ("block/same", "block", "same"), ("block/other", "block", "other")]
SEED = 0


def cfg_of(mode: str) -> det.DetConfig:
    return dataclasses.replace(det.DetConfig(), side_cut=mode)


@functools.lru_cache(maxsize=1)
def model():
    return wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model


def train_stems(prefix: str = "", contains: str = "") -> list[str]:
    """The train frames that have a box label, by name. Refuses anything else."""
    sp = splits.load_splits()
    stems = sorted(s for s in sp["train"] if s.startswith(prefix) and contains in s and io.boxes_path(s).exists())
    jg.require_train(stems, sp)
    return stems


def mask_of(stem: str) -> np.ndarray:
    """The class mask of a TRAIN frame, as the fixed color model paints it."""
    return pl.segment(jg.load_frame(stem), model())[0]


def eligible(b: dict, others: list[dict]) -> bool:
    x0, y0, x1, y1 = b["bbox"]
    if b.get("flags") or x0 < EDGE_MARGIN or y0 < EDGE_MARGIN or x1 > oc.FRAME_W - EDGE_MARGIN or y1 > oc.FRAME_H - EDGE_MARGIN:
        return False
    for o in others:
        ox0, oy0, ox1, oy1 = o["bbox"]
        if min(x1, ox1) - max(x0, ox0) > OVERLAP_MAX and min(y1, oy1) > max(y0, oy0):
            return False
    return True


def score(preds, color: int, box) -> dict:
    """One scene with one true barrel. ``found`` = the project's strict rule (same color, IoU >= 0.5, bottom edge within
    max(3 px, 10 % of the height)). ``placed`` = found by a box whose centre column is within CENTRE_TOL x the true width
    of the true centre column (a box centred on the visible half is a quarter of a width off and is not placed).
    ``wrong`` = the boxes that are not the found barrel."""
    g = dtp.Barrel(color=color, bbox=tuple(box), source="gt")
    found = not ed.evaluate_frame("scene", preds, [g], CAM, rule="v2").unmatched_gt
    cx, W = (box[0] + box[2]) / 2, box[2] - box[0]
    right = [p for p in preds if p.color == color and ed.box_iou(p.bbox, box) >= ed.IOU_THR and ed.bottom_within_tol(p, g)]
    assert bool(right) == found
    placed = any(abs((p.bbox[0] + p.bbox[2]) / 2 - cx) <= CENTRE_TOL * W for p in right)
    return {"found": int(found), "placed": int(placed), "boxes": len(preds), "wrong": len(preds) - int(found)}


def sources(pool: str) -> list[oc.Source]:
    """The source barrels of a pool: no flag, 3 px inside the frame, not overlapping another barrel's box, and found by
    today's detector when standing alone and unhidden (so a scene measures the hiding and nothing else)."""
    out = []
    for stem in train_stems(POOLS[pool]):
        mask = mask_of(stem)
        bs = io.load_boxes(stem)["barrels"]
        for i, b in enumerate(bs):
            others = [o for j, o in enumerate(bs) if j != i]
            if not eligible(b, others):
                continue
            src = oc.cut_source(mask, b["bbox"], dtp.COLOR_BY_NAME[b["color"]], [o["bbox"] for o in others], stem=stem, pool=pool)
            if score(det.detect(oc.make_scene(src, "edge", 0.0).mask, det.DetConfig(), CAM), src.color, src.bbox)["found"]:
                out.append(src)
    return out


def shorten_stripe(mask: np.ndarray, src: oc.Source, kind: str, amount: float, side: str, lean: int, px: int) -> None:
    """The "real-like" variant, in place: the STRIPE ends ``px`` pixels before the cut while the body runs up to it (in
    the real frames occlx_02 and occlx_03 it ends 5 to 6 px before). Per row: the stripe-colored pixels in the ``px``
    columns next to the cut become "other"."""
    x0, y0, x1, y1 = src.bbox
    W, H = x1 - x0, y1 - y0
    cut = int(round(amount * W))
    other = oc.BLUE if src.color == oc.ORANGE else oc.ORANGE
    for r in range(mask.shape[0]):
        off = lean * oc.SLANT_LEAN * W * (r - (y0 + y1) / 2) / H if kind == "slant" else 0.0
        if side == "L":
            b = int(np.ceil(x0 + cut + off))                             # the first column that still shows
            seg = mask[r, max(0, b):max(0, b + px)]
        else:
            b = int(np.ceil(x1 - cut + off))                             # the first hidden column
            seg = mask[r, max(0, b - px):max(0, b)]
        seg[seg == other] = 0


def cut_scene(src: oc.Source, kind: str, amount: float, side: str, lean: int = 1, short: int = 0) -> oc.Scene:
    sc = oc.make_scene(src, kind, amount, side, cam=CAM, lean=lean)
    if short:
        shorten_stripe(sc.mask, src, kind, amount, side, lean, short)
    return sc


def side_cut_scenes(src: oc.Source):
    """The scenes of yardstick (a): a straight edge and a slanted edge (both leans), from the left and from the right,
    hiding AMOUNTS of the width; each plain and "real-like". Yields (kind, amount, side, lean, short, Scene)."""
    for kind in ("edge", "slant"):
        for amount in AMOUNTS:
            for side in "LR":
                for lean in ((1, -1) if kind == "slant" else (1,)):
                    for short in (0, SHORT_PX):
                        yield kind, amount, side, lean, short, cut_scene(src, kind, amount, side, lean, short)


def scorecard_scenes(pool: list[oc.Source], only: int | None = None):
    """Every scene of the occlusion scorecard for one pool, made as ``experiments/2026-11-19_det_occl/run.py`` makes
    them (same rows, same seeded choice of the barrel pasted in front): (row key, amount, variant, source, Scene).
    ``only`` = the scenes of that one source barrel."""
    for si, src in enumerate(pool):
        if only is not None and si != only:
            continue
        for ki, (key, kind, color) in enumerate(ROWS):
            rng = np.random.default_rng([SEED, si, ki])
            front = pool[int(rng.integers(len(pool)))] if kind in oc.BARRELS else None
            for amount in oc.AMOUNTS:
                for side in (("L", "R") if kind in oc.SIDED else ("L",)):
                    for lean in ((1, -1) if kind == "slant" else (1,)):
                        try:
                            sc = oc.make_scene(src, kind, amount, side, color or "other", front, CAM, lean)
                        except ValueError:
                            continue
                        yield key, amount, (side if kind in oc.SIDED else "") + ({1: "+", -1: "-"}[lean] if kind == "slant" else ""), src, sc


def detect(mask: np.ndarray, mode: str):
    """(boxes, reason log) of the detector with DetConfig.side_cut = ``mode``."""
    log: list = []
    return det.detect(mask, cfg_of(mode), CAM, log=log), log


def rule_of(log: list, box) -> str:
    """The rule that drew ``box`` (from the reason log's "kept" notes), or ""."""
    for e in log:
        if e.get("why") == "kept" and tuple(e.get("box", ())) == tuple(box):
            return e.get("rule", e["stage"])
    return ""


def why_none(log: list) -> str:
    """The last reason a stripe got no box."""
    rs = [e["why"] for e in log if e.get("stage") in ("barrel", "stripe", "verify") and e.get("why") != "kept"]
    return rs[-1] if rs else "nothing"


def measure(mask: np.ndarray, bands=(det.SIDE_BAND,)) -> list[dict]:
    """For every stripe of a mask: what the side rule would measure (diagnostics; the detector does not use this)."""
    cfg = det.DetConfig()
    stripes, _ = det.find_stripes(mask, CAM, cfg)
    out = []
    for s in stripes:
        at = det._at(s, CAM)
        e = det.read_edges(s, at, mask, cfg) if at is not None else None
        if e is None:
            continue
        top, bottom = max(0, e.top), min(mask.shape[0], e.bottom)
        others = tuple((o.bbox[0], o.bbox[2]) for o in stripes if o is not s and not o.thin)
        x0, y0, x1, y1 = s.bbox
        whole = (x1 - x0) >= cfg.stripe_full * at.W
        if whole:
            sx0, sx1 = det._body_columns(mask, s.body, x0, x1, top, bottom, y0, y1, cap_px=cfg.body_width * at.W, others=others)
        else:
            seen = det.seen_span(s, mask, at.W, top, bottom, cfg, others)
            sx0, sx1 = seen.x0, seen.x1
        out.append({"stripe": s, "W": at.W, "H": at.H, "inferred": sorted(e.inferred), "top": top, "bottom": bottom, "sx0": sx0, "sx1": sx1,
                    "whole": whole, "thin": s.thin,
                    "bulges": {b: det.side_bulges(s, mask, CAM, top, bottom, sx0, sx1, band=b) for b in bands}})
    return out
