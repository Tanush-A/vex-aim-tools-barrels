"""The two color-step winners of 2026-11-26 run together on one frame (experiment 2026-11-26_combined, TODO E8).

NOT part of what runs by default: nothing imports this module except that experiment and its tests.

``nearmiss`` paints a pixel just outside the fixed color ranges where a barrel's partner color says it should be.
``selfcal`` lets a found or half-found barrel paint its own missing color inside its own box and widen the frame's
ranges. Each passed the standard pass rule alone. This module holds the ways to use both on one frame. Each way is
a function ``(frame, model, nm_cfg, sc_cfg) -> Combined``; pixels are never changed, nothing is kept between frames,
and ``detector.detect`` is called with the default ``DetConfig``.

    nm_then_sc    near-miss paint first; self-calibration then takes that mask and its boxes as ITS first pass
    sc_then_nm    self-calibration first; near-miss paint is then added on self-calibration's second-pass mask
    mask_union    each on the fixed mask, alone; the two masks are laid over each other; one more detector pass
    box_union     each alone, from start to end; the boxes are merged
    box_agree     each alone; a box the fixed colors did not draw stays only when BOTH drew it

Added 2026-11-27 (PREREG addendum): the third winner, the stripe by color difference (``contrast``), in its own
"add" mode (``contrast_on``), alone (``cn_alone``), added on top of each winner and of ``mask_union`` (``cn_on_*``), and
as a box-level merge with them (``cn_box_*``). ``WAYS3`` holds those; ``ALL_WAYS`` all twelve.

``nm_cfg`` None = the near-miss step is off. ``sc_cfg`` None = the self-calibration step is off. With both off every
way gives today's boxes. No way has a number of its own: every number belongs to one of the two steps.

The building blocks, in the order the data flows: ``fixed_pass`` (today's mask and boxes) -> ``near_miss`` (the
near-miss mask on any mask taken as "strict") and ``calibrate`` (self-calibration's seeds and second pass on any
mask taken as its first pass; with the fixed mask it is ``selfcal.SelfCal.run``, one round) -> the five ways.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

import numpy as np

from . import detector as det
from . import geometry as geo
from . import nearmiss as nm
from . import pipeline as pl
from . import selfcal as sc
from .counting import on_share
from .io import OTHER

ON = 0.5                # "on a box": this share of the smaller of two boxes inside the other (counting.ON_SHARE, selfcal.combine)


@dataclass
class Combined:
    """One frame's answer and what led to it."""
    boxes: list                                 # the answer
    first: list                                 # today's boxes (the fixed colors)
    strict: np.ndarray                          # today's mask
    mask: np.ndarray                            # the mask with everything both steps painted (what the last detector pass saw, where there was one)
    nm_mask: np.ndarray | None = None           # the near-miss step's mask, where it was built on its own
    sc_mask: np.ndarray | None = None           # the self-calibration step's second-pass mask, where it was built on its own
    seeds: list = field(default_factory=list)   # self-calibration's seed candidates with their verdicts
    info: dict = field(default_factory=dict)


# ---------------------------------------------------------------- the building blocks

def fixed_pass(frame: pl.Frame, model: pl.Model, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
               det_cfg: det.DetConfig | None = None) -> tuple[np.ndarray, list]:
    """Today's detector: the fixed model's mask and its boxes."""
    strict = pl.segment(frame, model)[0]
    return strict, det.detect(strict, det_cfg or det.DetConfig(), cam)


def near_miss(frame: pl.Frame, model: pl.Model, nm_cfg: nm.NearMissConfig | None, cam: geo.CameraModel, strict: np.ndarray) -> np.ndarray:
    """``strict`` plus the near-miss paint that ``strict`` calls for (``nearmiss.partner_mask``). With the step off, or
    both of its directions off, ``strict`` itself is returned (the same array, so the caller can tell)."""
    if nm_cfg is None or (nm_cfg.stripe_level == 0 and nm_cfg.body_level == 0):
        return strict
    return nm.partner_mask(frame, model, nm_cfg, cam, strict=strict)[0]


def overlay(top: np.ndarray, under: np.ndarray) -> np.ndarray:
    """``top`` with ``under``'s paint showing where ``top`` has none. Where both paint, ``top`` wins."""
    out = top.copy()
    free = out == OTHER
    out[free] = under[free]
    return out


def seed_rule(boxes: list, kept: list) -> list:
    """Self-calibration's rule: a kept seed says which barrel stands in its box, so a box of the other color on it is
    dropped."""
    return [b for b in boxes if not any(s.body != b.color and on_share(b.bbox, s.bbox) >= ON for s in kept)]


def calibrate(frame: pl.Frame, model: pl.Model, mask1: np.ndarray, boxes1: list, sc_cfg: sc.SelfCalConfig | None,
              cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, det_cfg: det.DetConfig | None = None,
              keep: np.ndarray | None = None, detect: bool = True) -> tuple[np.ndarray, list, list, dict]:
    """Self-calibration's seeds and second pass, with ``mask1`` and ``boxes1`` taken as its first pass.

    The same steps as ``selfcal.SelfCal.run`` (one round): the seeds are looked for on ``mask1`` and checked on the
    photo; the kept ones widen the frame's ranges (bounded, with the flood guard) and paint their own missing color
    inside their own boxes; the detector runs on the new mask; a box of the other color on a kept seed is dropped.
    ``keep``: paint that stays under whatever the frame's ranges paint (the near-miss paint, when ``mask1`` holds
    some: a mask made from widened ranges alone would lose it). ``detect=False``: the mask only, no boxes.

    Returns (the second-pass mask, the second-pass boxes, every seed candidate, info). With the step off (``sc_cfg``
    None) or no kept seed: (``mask1`` itself, ``boxes1``, the seeds, {})."""
    if sc_cfg is None:
        return mask1, boxes1, [], {}
    det_cfg = det_cfg or det.DetConfig()
    seeds = sc.find_seeds(frame, mask1, boxes1, cam, sc_cfg)
    kept = [s for s in seeds if s.ok]
    if not kept:
        return mask1, boxes1, seeds, {}
    new_boxes, shares, rinfo = dict(model.boxes), {}, {}
    if sc_cfg.frame:
        new_boxes, rinfo = sc.frame_ranges(sc.class_readings(kept), model.boxes, sc_cfg)
        new_boxes, shares = sc.flood(frame, model, new_boxes, sc_cfg, kept)
    if new_boxes == model.boxes:
        mask = mask1
    else:
        mask = pl.segment(frame, dataclasses.replace(model, boxes=new_boxes))[0]
        if keep is not None:
            mask = overlay(mask, keep)
    if sc_cfg.local:
        mask = sc.paint_local(frame, mask, kept)
    info = {"ranges": rinfo, "flood": shares, "moved": [sc.NAME[c] for c in pl.CLASSES if new_boxes[c] != model.boxes[c]]}
    if not detect:
        return mask, [], seeds, info
    boxes = det.detect(mask, det_cfg, cam) if mask is not mask1 else boxes1
    if sc_cfg.seed_rules:
        boxes = seed_rule(boxes, kept)
    return mask, boxes, seeds, info


def _kept(seeds: list) -> list:
    return [s for s in seeds if s.ok]


# ---------------------------------------------------------------- the five ways

def nm_then_sc(frame: pl.Frame, model: pl.Model, nm_cfg: nm.NearMissConfig | None, sc_cfg: sc.SelfCalConfig | None,
               cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, det_cfg: det.DetConfig | None = None, cn_p=None) -> Combined:
    """Near-miss paint first, then self-calibration on that mask. The near-miss mask and its boxes are
    self-calibration's first pass: its seeds are looked for there, the near-miss boxes stay as they are, and a
    second-pass box is added where no near-miss box is."""
    det_cfg = det_cfg or det.DetConfig()
    strict, first = fixed_pass(frame, model, cam, det_cfg)
    nm_mask = near_miss(frame, model, nm_cfg, cam, strict)
    nm_boxes = first if nm_mask is strict else det.detect(nm_mask, det_cfg, cam)
    mask2, boxes2, seeds, info = calibrate(frame, model, nm_mask, nm_boxes, sc_cfg, cam, det_cfg, keep=nm_mask)
    boxes = nm_boxes if mask2 is nm_mask else sc.combine(nm_boxes, boxes2, "add")
    return Combined(boxes, first, strict, mask2, nm_mask=nm_mask, seeds=seeds, info=info)


def sc_then_nm(frame: pl.Frame, model: pl.Model, nm_cfg: nm.NearMissConfig | None, sc_cfg: sc.SelfCalConfig | None,
               cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, det_cfg: det.DetConfig | None = None, cn_p=None) -> Combined:
    """Self-calibration first, then near-miss paint on its second-pass mask (that mask is what the near-miss step
    takes as "strict": a color a seed painted can be the partner). Self-calibration's rule for the boxes is kept:
    today's boxes stay as they are, and a box of the last pass is added where none of today's is."""
    det_cfg = det_cfg or det.DetConfig()
    strict, first = fixed_pass(frame, model, cam, det_cfg)
    mask2, boxes2, seeds, info = calibrate(frame, model, strict, first, sc_cfg, cam, det_cfg)
    mask3 = near_miss(frame, model, nm_cfg, cam, mask2)
    if mask3 is mask2:
        boxes3 = boxes2
    else:
        boxes3 = det.detect(mask3, det_cfg, cam)
        if sc_cfg is not None and sc_cfg.seed_rules:
            boxes3 = seed_rule(boxes3, _kept(seeds))
    boxes = first if mask3 is strict else sc.combine(first, boxes3, "add")
    return Combined(boxes, first, strict, mask3, sc_mask=mask2, seeds=seeds, info=info)


def mask_union(frame: pl.Frame, model: pl.Model, nm_cfg: nm.NearMissConfig | None, sc_cfg: sc.SelfCalConfig | None,
               cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, det_cfg: det.DetConfig | None = None, cn_p=None) -> Combined:
    """Each step alone on the fixed mask; then the two masks laid over each other and one detector pass. Where the
    two paint a pixel differently, self-calibration's color stays (its seed passed the photo check). Today's boxes
    stay as they are; a box of the union's pass is added where none of today's is."""
    det_cfg = det_cfg or det.DetConfig()
    strict, first = fixed_pass(frame, model, cam, det_cfg)
    nm_mask = near_miss(frame, model, nm_cfg, cam, strict)
    sc_mask, _, seeds, info = calibrate(frame, model, strict, first, sc_cfg, cam, det_cfg, detect=False)
    if nm_mask is strict and sc_mask is strict:
        return Combined(first, first, strict, strict, nm_mask=nm_mask, sc_mask=sc_mask, seeds=seeds, info=info)
    union = overlay(sc_mask, nm_mask)
    boxes = det.detect(union, det_cfg, cam)
    if sc_cfg is not None and sc_cfg.seed_rules:
        boxes = seed_rule(boxes, _kept(seeds))
    return Combined(sc.combine(first, boxes, "add"), first, strict, union, nm_mask=nm_mask, sc_mask=sc_mask, seeds=seeds, info=info)


def _both_alone(frame, model, nm_cfg, sc_cfg, cam, det_cfg):
    """Each winner alone, exactly as it was judged: (today's mask and boxes, the near-miss mask and its boxes,
    self-calibration's mask, its final boxes, its seeds, info)."""
    strict, first = fixed_pass(frame, model, cam, det_cfg)
    nm_mask = near_miss(frame, model, nm_cfg, cam, strict)
    nm_boxes = first if nm_mask is strict else det.detect(nm_mask, det_cfg, cam)
    sc_mask, second, seeds, info = calibrate(frame, model, strict, first, sc_cfg, cam, det_cfg)
    sc_boxes = first if sc_mask is strict else sc.combine(first, second, sc_cfg.combine)
    return strict, first, nm_mask, nm_boxes, sc_mask, sc_boxes, seeds, info


def merge_boxes(base: list, more: list) -> list:
    """``base`` as it is, plus each box of ``more`` that is not on a box of ``base`` (``selfcal.combine``)."""
    return sc.combine(base, more, "add")


def box_union(frame: pl.Frame, model: pl.Model, nm_cfg: nm.NearMissConfig | None, sc_cfg: sc.SelfCalConfig | None,
              cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, det_cfg: det.DetConfig | None = None, cn_p=None) -> Combined:
    """Each winner alone from start to end, then the boxes merged: every box of self-calibration (which holds every
    box of today's detector) stays as it is; a near-miss box is added where none of those is."""
    det_cfg = det_cfg or det.DetConfig()
    strict, first, nm_mask, nm_boxes, sc_mask, sc_boxes, seeds, info = _both_alone(frame, model, nm_cfg, sc_cfg, cam, det_cfg)
    return Combined(merge_boxes(sc_boxes, nm_boxes), first, strict, overlay(sc_mask, nm_mask), nm_mask=nm_mask, sc_mask=sc_mask, seeds=seeds, info=info)


def box_agree(frame: pl.Frame, model: pl.Model, nm_cfg: nm.NearMissConfig | None, sc_cfg: sc.SelfCalConfig | None,
              cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, det_cfg: det.DetConfig | None = None, cn_p=None) -> Combined:
    """Each winner alone; a second reading decides. Today's boxes stay as they are. A box that self-calibration adds
    stays only when the near-miss step, on its own, drew a box of the same color on it."""
    det_cfg = det_cfg or det.DetConfig()
    strict, first, nm_mask, nm_boxes, sc_mask, sc_boxes, seeds, info = _both_alone(frame, model, nm_cfg, sc_cfg, cam, det_cfg)
    ours = {id(b) for b in first}
    added = [b for b in sc_boxes if id(b) not in ours]
    agreed = [b for b in added if any(n.color == b.color and on_share(b.bbox, n.bbox) >= ON for n in nm_boxes)]
    boxes = sorted(list(first) + agreed, key=lambda b: b.bbox[0])
    return Combined(boxes, first, strict, overlay(sc_mask, nm_mask), nm_mask=nm_mask, sc_mask=sc_mask, seeds=seeds,
                    info={**info, "added_by_selfcal": len(added), "agreed": len(agreed)})


WAYS = {"nm_then_sc": nm_then_sc, "sc_then_nm": sc_then_nm, "mask_union": mask_union, "box_union": box_union, "box_agree": box_agree}


# ---------------------------------------------------------------- the third winner: the stripe by color difference (addendum 2026-11-27)

def contrast_on(frame: pl.Frame, base_mask: np.ndarray, base_boxes: list, cn_p, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
                det_cfg: det.DetConfig | None = None) -> tuple[np.ndarray, list, list]:
    """The contrast path in its own judged "add" mode (``experiments/2026-11-26_contrast/candidate.py``,
    ``FrameWork.detect``), on any base: ``base_boxes`` stay as they are; a candidate whose stripe point lies in one of
    them is left alone; the rest paint their own colors into a copy of ``base_mask`` (only where it is OTHER); the
    detector runs once more and a box of that run is added when it is on none of ``base_boxes``. With the fixed mask
    and today's boxes as the base this is the contrast winner alone. ``cn_p``: a ``contrast.Params``, None = off.
    Returns (the mask, the boxes, the candidates)."""
    if cn_p is None:
        return base_mask, base_boxes, []
    from . import contrast as cn
    from .counting import is_on
    mask, cands = cn.contrast_mask(frame.rgb, base_mask, cam, cn_p, skip_boxes=tuple(b.bbox for b in base_boxes))
    if not any(c.info.get("painted") for c in cands):
        return base_mask, base_boxes, cands
    new = det.detect(mask, det_cfg or det.DetConfig(), cam)
    out = list(base_boxes) + [b for b in new if not any(is_on(b, o) for o in base_boxes)]
    return mask, sorted(out, key=lambda b: b.bbox[0]), cands


def _on_top(base: Combined, frame, cn_p, cam, det_cfg) -> Combined:
    mask, boxes, cands = contrast_on(frame, base.mask, base.boxes, cn_p, cam, det_cfg)
    return Combined(boxes, base.first, base.strict, mask, nm_mask=base.nm_mask, sc_mask=base.sc_mask, seeds=base.seeds,
                    info={**base.info, "contrast_candidates": len(cands), "contrast_painted": sum(1 for c in cands if c.info.get("painted")), "contrast": cands})


def _alone(frame, model, nm_cfg, sc_cfg, cam, det_cfg, which: str) -> Combined:
    """One winner alone, as judged, as a ``Combined`` (``which``: "fixed", "nearmiss", "selfcal", "nm_sc" = mask_union)."""
    det_cfg = det_cfg or det.DetConfig()
    if which == "nm_sc":
        return mask_union(frame, model, nm_cfg, sc_cfg, cam, det_cfg)
    strict, first, nm_mask, nm_boxes, sc_mask, sc_boxes, seeds, info = _both_alone(frame, model, nm_cfg if which == "nearmiss" else None,
                                                                                  sc_cfg if which == "selfcal" else None, cam, det_cfg)
    mask, boxes = {"fixed": (strict, first), "nearmiss": (nm_mask, nm_boxes), "selfcal": (sc_mask, sc_boxes)}[which]
    return Combined(boxes, first, strict, mask, nm_mask=nm_mask, sc_mask=sc_mask, seeds=seeds, info=info)


def cn_alone(frame, model, nm_cfg, sc_cfg, cam=geo.AIM_4A8B6118_BOXFIT, det_cfg=None, cn_p=None) -> Combined:
    """The contrast winner alone: added on top of today's detector (``nm_cfg`` and ``sc_cfg`` are not used)."""
    return _on_top(_alone(frame, model, None, None, cam, det_cfg, "fixed"), frame, cn_p, cam, det_cfg)


def cn_on_nm(frame, model, nm_cfg, sc_cfg, cam=geo.AIM_4A8B6118_BOXFIT, det_cfg=None, cn_p=None) -> Combined:
    """The near-miss winner alone, then the contrast path added on top of its mask and boxes."""
    return _on_top(_alone(frame, model, nm_cfg, None, cam, det_cfg, "nearmiss"), frame, cn_p, cam, det_cfg)


def cn_on_sc(frame, model, nm_cfg, sc_cfg, cam=geo.AIM_4A8B6118_BOXFIT, det_cfg=None, cn_p=None) -> Combined:
    """The self-calibration winner alone, then the contrast path added on top of its second-pass mask and boxes."""
    return _on_top(_alone(frame, model, None, sc_cfg, cam, det_cfg, "selfcal"), frame, cn_p, cam, det_cfg)


def cn_on_all(frame, model, nm_cfg, sc_cfg, cam=geo.AIM_4A8B6118_BOXFIT, det_cfg=None, cn_p=None) -> Combined:
    """All three: the two-way ``mask_union``, then the contrast path added on top of its mask and boxes."""
    return _on_top(_alone(frame, model, nm_cfg, sc_cfg, cam, det_cfg, "nm_sc"), frame, cn_p, cam, det_cfg)


def _box_merge(frame, model, nm_cfg, sc_cfg, cam, det_cfg, cn_p, which: str) -> Combined:
    base = _alone(frame, model, nm_cfg, sc_cfg, cam, det_cfg, which)
    c = cn_alone(frame, model, None, None, cam, det_cfg, cn_p)
    return Combined(merge_boxes(base.boxes, c.boxes), base.first, base.strict, overlay(base.mask, c.mask), nm_mask=base.nm_mask,
                    sc_mask=base.sc_mask, seeds=base.seeds, info={**base.info, "contrast": c.info.get("contrast", [])})


def cn_box_nm(frame, model, nm_cfg, sc_cfg, cam=geo.AIM_4A8B6118_BOXFIT, det_cfg=None, cn_p=None) -> Combined:
    """Near-miss alone and contrast alone, each from start to end; the boxes merged (near-miss first)."""
    return _box_merge(frame, model, nm_cfg, sc_cfg, cam, det_cfg, cn_p, "nearmiss")


def cn_box_sc(frame, model, nm_cfg, sc_cfg, cam=geo.AIM_4A8B6118_BOXFIT, det_cfg=None, cn_p=None) -> Combined:
    """Self-calibration alone and contrast alone; the boxes merged (self-calibration first)."""
    return _box_merge(frame, model, nm_cfg, sc_cfg, cam, det_cfg, cn_p, "selfcal")


def cn_box_all(frame, model, nm_cfg, sc_cfg, cam=geo.AIM_4A8B6118_BOXFIT, det_cfg=None, cn_p=None) -> Combined:
    """``mask_union`` and contrast alone; the boxes merged (``mask_union`` first)."""
    return _box_merge(frame, model, nm_cfg, sc_cfg, cam, det_cfg, cn_p, "nm_sc")


WAYS3 = {"cn_alone": cn_alone, "cn_on_nm": cn_on_nm, "cn_on_sc": cn_on_sc, "cn_on_all": cn_on_all,
         "cn_box_nm": cn_box_nm, "cn_box_sc": cn_box_sc, "cn_box_all": cn_box_all}
ALL_WAYS = {**WAYS, **WAYS3}
