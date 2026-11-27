"""Shared code of the occlusion-by-a-thing experiment (PREREG.md): frames, the two detectors, contact sheets.

Train frames only: every frame is read through ``judge.load_frame`` (it refuses anything that is not a train frame,
before the image is opened) and every list of stems goes through ``judge.require_train``. No pixel is changed.
"""
from __future__ import annotations

import dataclasses
import functools
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "src"
sys.path.insert(0, str(SRC))
import barrels  # noqa: E402

assert Path(barrels.__file__).resolve().is_relative_to(SRC), f"barrels is imported from {barrels.__file__}, not from {SRC}"
from barrels import contrast as cn, counting as ct, detect_types as dtp, detector as det, eval_det as ed  # noqa: E402
from barrels import geometry as geo, io, judge as jg, pipeline as pl, splits  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
OUT = io.PKG_ROOT / "results" / "2026-11-27_occl_photo"


@functools.lru_cache(maxsize=1)
def model():
    return pl.default_model()


def train_stems(contains=("",), labelled: bool = True) -> list[str]:
    """Train frames whose name contains any of ``contains`` (and that have an image and, by default, a box label)."""
    sp = splits.load_splits()
    stems = sorted(s for s in sp["train"] if any(c in s for c in contains) and io.find_image(s) is not None
                   and (not labelled or io.boxes_path(s).exists()))
    jg.require_train(stems, sp)
    return stems


def cfg_of(mode: str, **fields) -> det.DetConfig:
    return dataclasses.replace(det.DetConfig(), side_photo=mode, **fields)


def run_frame(frame, mode: str = "off", log: list | None = None, cfg: det.DetConfig | None = None) -> list:
    """Today's photo-in, boxes-out path (``pipeline.detect_frame``) with ``DetConfig.side_photo = mode`` (or the whole
    ``cfg``); the photo is handed to both runs of the detector (the first, and the one on the contrast-painted mask).
    With side_photo "off" this is ``pipeline.detect_frame`` exactly."""
    cfg = cfg if cfg is not None else cfg_of(mode)
    mask = pl.segment(frame, model())[0]
    photo = frame.rgb if cfg.side_photo != "off" else None
    boxes = det.detect(mask, cfg, CAM, log, photo=photo)
    painted, cands = cn.contrast_mask(frame.rgb, mask, CAM, cn.ContrastConfig(), skip_boxes=tuple(b.bbox for b in boxes))
    if not any(c.info.get("painted") for c in cands):
        return list(boxes)
    new = det.detect(painted, cfg, CAM, log, photo=photo)
    out = list(boxes) + [dataclasses.replace(b, source=cn.SOURCE) for b in new if not any(ct.is_on(b, o) for o in boxes)]
    return sorted(out, key=lambda b: b.bbox[0])


def detector_for(mode: str):
    def detect_frame(stem: str, frame) -> list:
        return run_frame(frame, mode)
    detect_frame.describe = (f"today's default (color step, detector, stripe by contrast) with DetConfig.side_photo={mode!r}, "
                             "the photo passed to both detector runs")
    return detect_frame


def truth(stem: str):
    label = io.load_boxes(stem)
    return dtp.barrels_from_boxes(label), label.get("clean", True)


def rule_of(log: list, box) -> str:
    for e in log:
        if e.get("why") == "kept" and tuple(e.get("box", ())) == tuple(box):
            return e.get("rule", e["stage"])
    return ""


def seg_image(mask: np.ndarray) -> np.ndarray:
    seg = np.full(mask.shape + (3,), 45, np.uint8)
    seg[mask == io.ORANGE] = (0, 140, 255)
    seg[mask == io.BLUE] = (255, 120, 0)
    return seg


def sheet(bgr, mask, gts, arms: dict, focus=None, pad: int = 30, scale: int = 3, title: str = "") -> np.ndarray:
    """One contact-sheet row: per arm the photo crop with the labels (thin green) and that arm's boxes (thick), then
    the mask. ``arms`` = {name: (boxes, BGR color)}. ``focus`` = the boxes to centre the crop on (default: all)."""
    boxes = focus or ([g.bbox for g in gts] + [p.bbox for bs, _ in arms.values() for p in bs]) or [(0, 0, 640, 480)]
    x0, y0 = max(0, min(b[0] for b in boxes) - pad), max(0, min(b[1] for b in boxes) - pad)
    x1, y1 = min(640, max(b[2] for b in boxes) + pad), min(480, max(b[3] for b in boxes) + pad)
    sc = scale if (x1 - x0) * scale <= 700 else max(1, 700 // (x1 - x0))
    panels = []
    names = list(arms)
    for name, (bs, color) in list(arms.items()) + [("mask", ([], None))]:
        img = seg_image(mask) if name == "mask" else bgr.copy()
        crop = cv2.resize(np.ascontiguousarray(img[y0:y1, x0:x1]), None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)

        def box(b, c, t=1):
            cv2.rectangle(crop, ((b[0] - x0) * sc, (b[1] - y0) * sc), ((b[2] - x0) * sc - 1, (b[3] - y0) * sc - 1), c, t)
        for g in gts:
            box(g.bbox, (0, 255, 0))
        for p in bs:
            box(p.bbox, color, 2)
        head = np.zeros((16, crop.shape[1], 3), np.uint8)
        label = (title + "  " + name) if (title and name == names[0]) else name
        cv2.putText(head, label, (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
        panels.append(np.vstack([head, crop]))
        panels.append(np.zeros((panels[-1].shape[0], 4, 3), np.uint8))
    return np.hstack(panels[:-1])


def stack(rows: list[np.ndarray]) -> np.ndarray:
    if not rows:
        return np.zeros((10, 10, 3), np.uint8)
    w = max(r.shape[1] for r in rows)
    return np.vstack([np.pad(r, ((0, 6), (0, w - r.shape[1]), (0, 0))) for r in rows])
