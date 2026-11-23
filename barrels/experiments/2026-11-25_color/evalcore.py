"""One frame, one setting -> what the detector does with it, judged against the hand boxes (2026-11-25 color work).

A setting is a flat dict: the six slider numbers (``orange_h_lo`` .. ``blue_s_lo``, the slider's units) plus the two
gates ``v_min`` (brightness floor, default 40) and ``horizon_row`` (default 50). The mask is ``pipeline.segment`` with
the adopted model's config and those numbers (nothing re-implemented); the detector is today's ``DetConfig()``; the
score is the v2 rule against the hand boxes. A setting that floods the frame (paints far more outside the hand boxes
than the reference setting) is not run through the detector: it is marked ``flood`` and counts as not working (the
detector is very slow on flooded masks, and a flooded frame is never a usable setting).
"""
from __future__ import annotations

import dataclasses
import hashlib
from dataclasses import dataclass, field

import numpy as np

from barrels import detect_types as dtp
from barrels import detector as det
from barrels import eval_det as ed
from barrels import geometry as geo
from barrels import hslabel as hl
from barrels import hsrange as hx
from barrels import pipeline as pl

SIX = hx.THRESHOLDS
GATES = {"v_min": 40, "horizon_row": 50}
CAM = geo.AIM_4A8B6118_BOXFIT
FLOOD_MIN = 30000       # outside paint above max(FLOOD_MIN, FLOOD_REL * the reference's) -> flood, no detector run
FLOOD_REL = 4.0


def full(setting: dict) -> dict:
    """A setting with the gates filled in at their defaults."""
    s = hx.flat({k: setting[k] for k in SIX}) if not all(k in setting for k in SIX) else {k: int(setting[k]) for k in SIX}
    for g, d in GATES.items():
        s[g] = int(setting.get(g, d))
    return s


def model_for(base: pl.Model, setting: dict) -> pl.Model:
    s = full(setting)
    m = hl.model_from_thresholds(base, hx.nested(s))
    cfg = dataclasses.replace(m.cfg, v_min=s["v_min"], horizon_row=s["horizon_row"])
    return dataclasses.replace(m, cfg=cfg)


def key(setting: dict) -> tuple:
    s = full(setting)
    return tuple(s[k] for k in (*SIX, *GATES))


@dataclass(frozen=True)
class Result:
    found: frozenset = frozenset()      # hand boxes matched (v2)
    n_false: int = 0
    n_boxes: int = 0
    core: dict = field(default_factory=dict)   # color -> share of the cores of his boxes of that color painted that color
    out: int = 0                        # px painted (either color) outside his padded boxes, rows >= 50
    flood: bool = False
    empty: bool = False                 # a hue range with lo > hi
    best_iou: tuple = ()                # per hand box: best IoU with a same-color detector box (0 = none)


class Judge:
    """A frame with its hand boxes. ``run(setting)`` -> Result (cached); ``log(setting)`` -> (barrels, the detector's
    reason log)."""

    def __init__(self, stem: str, bgr: np.ndarray, label: dict, base: pl.Model | None = None, det_cfg=None):
        self.stem, self.base = stem, base or hl.adopted_model()
        self.frame = pl.Frame.from_image(bgr)
        self.det_cfg = det_cfg or det.DetConfig()
        self.boxes = list(label.get("barrels", []))
        self.clean = bool(label.get("clean", True))
        self.core, _, self.outside = hx.regions(bgr.shape, self.boxes, 50)
        self.gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes({"barrels": self.boxes})]
        self._cache: dict = {}
        self._det: dict = {}
        self.ref_out: int | None = None
        self.calls = 0

    def mask(self, setting: dict) -> np.ndarray:
        return pl.segment(self.frame, model_for(self.base, setting))[0]

    def set_reference(self, setting: dict) -> Result:
        self.ref_out = None
        r = self.run(setting, guard=False)
        self.ref_out = r.out
        return r

    def flood_cap(self) -> float:
        return max(FLOOD_MIN, FLOOD_REL * (self.ref_out or 0))

    def run(self, setting: dict, guard: bool = True) -> Result:
        s = full(setting)
        k = key(s)
        if k in self._cache:
            return self._cache[k]
        if s["orange_h_lo"] > s["orange_h_hi"] or s["blue_h_lo"] > s["blue_h_hi"]:
            r = Result(empty=True)
            self._cache[k] = r
            return r
        m = self.mask(s)
        core = {c: (float((m[self.core[c]] == hx.CLASS_ID[c]).mean()) if self.core[c].any() else float("nan")) for c in hx.CLASS_NAMES}
        out = int((m[self.outside] != 0).sum())
        if guard and self.ref_out is not None and out > self.flood_cap():
            r = Result(core=core, out=out, flood=True)
            self._cache[k] = r
            return r
        h = hashlib.blake2b(m.tobytes(), digest_size=16).digest()
        if h not in self._det:
            self.calls += 1
            preds = det.detect(m, self.det_cfg, CAM)
            ev = ed.evaluate_frame(self.stem, preds, self.gts, CAM, rule="v2", clean=self.clean)
            best = []
            for g in self.gts:
                ious = [ed.box_iou(p.bbox, g.bbox) for p in preds if p.color == g.color]
                best.append(round(max(ious), 3) if ious else 0.0)
            self._det[h] = (frozenset(mm.gt_idx for mm in ev.matches), int(sum(ev.fp.values())), len(preds), tuple(best))
        found, nf, nb, best = self._det[h]
        r = Result(found, nf, nb, core, out, False, False, best)
        self._cache[k] = r
        return r

    def log(self, setting: dict) -> tuple[list, list]:
        m = self.mask(setting)
        log: list = []
        preds = det.detect(m, self.det_cfg, CAM, log=log)
        return preds, log


def overlap(a, b) -> float:
    """Share of box b covered by box a."""
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    area = max(1, (b[2] - b[0]) * (b[3] - b[1]))
    return inter / area


def why_lost(judge: Judge, setting: dict, gt_idx: int) -> dict:
    """Why hand box ``gt_idx`` is not found at ``setting``: the detector's boxes near it (IoU, bottom error) and the
    dropped candidates whose box overlaps it, by stage and test."""
    preds, log = judge.log(setting)
    g = judge.boxes[gt_idx]
    gb = tuple(g["bbox"])
    near = []
    for p in preds:
        iou = ed.box_iou(p.bbox, gb)
        if iou > 0.1:
            near.append({"color": "orange" if p.color == 1 else "blue", "bbox": tuple(int(v) for v in p.bbox), "iou": round(iou, 2),
                         "bottom_err": int(p.bbox[3] - gb[3]), "flags": list(getattr(p, "flags", ()))})
    drops = []
    for e in log:
        if e.get("why") == "kept":
            continue
        if overlap(e["bbox"], gb) > 0.3 or overlap(gb, e["bbox"]) > 0.3:
            drops.append(f"{e['stage']}:{e['why']}")
    return {"near_boxes": near, "drops": sorted(set(drops))}
