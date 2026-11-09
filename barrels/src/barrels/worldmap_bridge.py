"""Where our detector meets the robot: the hook the live feed runs, and the world-map route for later.

Live feed (built 2026-11-05, ``barrels/live/BarrelViewer.fsm``): an aim_fsm state machine grabs
``robot.camera_image`` (640x480 **RGB**) once a second and shows ``BarrelDetectorHook.view(image, mode)``
with aim_fsm's PyQt ``imshow``. ``view`` is the whole chain — RGB→BGR, the frozen v1 segmentation, the
detector, ``detector.draw`` (yellow = orange barrel, green = blue), BGR→RGB — so the robot path and the
photo path (``tools/detect_image.py``) run exactly the same code. ``BarrelDetectorHook.default()`` is "the
detector as it stands": the frozen v1 model (config afd85483), ``detector.detect`` with ``DetConfig()``
(the stripe step), camera ``AIM_4A8B6118_BOXFIT``. Modes: ``"boxes"`` (the v2 output image), ``"seg"``
(the class mask blended over the image), ``"both"``. ``render`` is ``view`` with the barrels supplied, for the
multi-frame program ``live/BarrelTracker.fsm`` (``barrels.tracker``) that shows boxes which persist over frames.

Channel order: inside ``barrels`` an image array is BGR (OpenCV's order); the robot and ``imshow`` speak
RGB; this module converts at the boundary and nowhere else.

The world-map route (NOT wired; parked until Dave says so — ``PROBLEM.md`` v2 out of scope):
``worldmap.make_new_aiv_objects`` consumes ``robot.robot0.status['aivision']['objects']['items']``, a list
of dicts with exactly the keys ``Barrel.to_aivision_spec`` produces (``type_str='aiobj'``, ``name``
OrangeBarrel/BlueBarrel, ``originx, originy, width, height`` in 320x240 units, optional string ``id``). It
projects the bottom-edge midpoint (height padded to max(h, 1.1·w)) to the ground with a hardcoded tilt/focal
length, steps 11 mm along the bearing, and drops anything farther than 300 mm. To replace the vendor detector
one would write ``with_items(robot.robot0.status, barrels_to_aivision_items(barrels))`` before
``world_map.update`` runs; latency, the ``check_spec_indicates_held`` thresholds and worldmap's 22 mm
diameter / 1.1·w pad all need agreeing first. ``draw_boxes`` draws in that aivision style (2 px, barrel
colors) for comparing against the vendor boxes in the camera viewer.
"""
from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from . import boxfit as bf
from . import detector as det, geometry as geo, pipeline as pl, viz
from .detect_types import AIVISION_SCALE, Barrel
from .io import BLUE, ORANGE, PKG_ROOT

DEFAULT_MODEL = PKG_ROOT / "results" / "2026-10-20_v1_test_adaptive" / "config.json"   # the frozen v1 model, config afd85483
MODEL_ENV = "BARRELS_MODEL"     # set to another results config.json to try a different front end without editing code


def default_model_path() -> Path:
    """DEFAULT_MODEL, unless the environment variable BARRELS_MODEL names another results config.json (for trying
    a candidate front end in tools/detect_image.py and the live programs before it is adopted)."""
    return Path(os.environ[MODEL_ENV]) if os.environ.get(MODEL_ENV) else DEFAULT_MODEL
VIEWS = ("boxes", "seg", "both")
BOX_COLORS_RGB = {"OrangeBarrel": (255, 128, 0), "BlueBarrel": (0, 100, 255)}


def barrels_to_aivision_items(barrels: list[Barrel], prefix: str = "barrels") -> list[dict]:
    """The list worldmap.make_new_aiv_objects iterates over."""
    return [b.to_aivision_spec(id=f"{prefix}-{i}") for i, b in enumerate(barrels)]


def with_items(status: dict | None, items: list[dict]) -> dict:
    """A copy of the robot status with ['aivision']['objects']['items'] replaced; the input is not mutated."""
    out = copy.deepcopy(status) if status else {}
    out.setdefault("aivision", {}).setdefault("objects", {})["items"] = list(items)
    return out


def draw_boxes(image_rgb: np.ndarray, barrels: list[Barrel], scale: int = AIVISION_SCALE) -> np.ndarray:
    """Draw the aivision-style boxes (2 px, barrel colors). Uses viewer.camera_overlay.draw_aiobj_boxes when
    the repo root is importable (same look as the vendor boxes), else the same rectangles via cv2."""
    items = barrels_to_aivision_items(barrels)
    try:
        from viewer.camera_overlay import draw_aiobj_boxes  # type: ignore
        out = image_rgb.copy()
        draw_aiobj_boxes(out, items, scale)       # draws in place and returns None
        return out
    except Exception:  # noqa: BLE001 — viewer not importable outside the repo
        out = image_rgb.copy()
        for it in items:
            x0, y0 = it["originx"] * scale, it["originy"] * scale
            x1, y1 = x0 + it["width"] * scale, y0 + it["height"] * scale
            cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), BOX_COLORS_RGB.get(it["name"], (255, 255, 255)), 2)
        return out


def _to_bgr(image_rgb: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(image_rgb[..., ::-1])


def _to_rgb(image_bgr: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(image_bgr[..., ::-1])


@dataclass
class BarrelDetectorHook:
    """The detector on a live (RGB) frame: segmentation model + detector + camera, in one object.

    ``default()`` = the detector as it stands (frozen v1 model, the stripe step, the provisional camera).
    ``on_image`` returns the barrels; ``view`` returns the picture to show. Both take and give RGB.
    """
    model: pl.Model
    cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT
    detector: Callable = det.detect
    det_cfg: object = field(default_factory=det.DetConfig)
    last_mask: np.ndarray | None = field(default=None, repr=False)
    last_barrels: list[Barrel] = field(default_factory=list, repr=False)
    _size_warned: bool = field(default=False, repr=False)

    @classmethod
    def load(cls, config_json: Path | str, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, **kw) -> "BarrelDetectorHook":
        """From a results config.json that carries a fitted 'model' (as final_test.py writes)."""
        d = json.load(Path(config_json).open())
        m = d["model"]
        cfg = pl.Config.from_dict(m["cfg"])
        boxes = {int(k): bf.Box.from_dict(v) for k, v in m["boxes"].items()}
        model = pl.Model(cfg=cfg, boxes=boxes, inner={int(k): bf.Box.from_dict(v) for k, v in m.get("inner", {}).items()},
                         outer={int(k): bf.Box.from_dict(v) for k, v in m.get("outer", {}).items()}, fit_info=m.get("fit_info", {}))
        return cls(model=model, cam=cam, **kw)

    @classmethod
    def default(cls, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT) -> "BarrelDetectorHook":
        """The detector as it stands: frozen v1 model afd85483 + detector.detect (DetConfig()) + the given camera;
        with BARRELS_MODEL set in the environment, that model file instead (see default_model_path)."""
        path = default_model_path()
        if path != DEFAULT_MODEL:
            print(f"BarrelDetectorHook: using {MODEL_ENV}={path}")
        return cls.load(path, cam=cam)

    def segment(self, image_rgb: np.ndarray) -> np.ndarray:
        """The class mask (0 other, 1 orange, 2 blue) of an RGB frame; also kept as ``last_mask``."""
        if image_rgb.shape[:2] != (480, 640) and not self._size_warned:
            print(f"BarrelDetectorHook: {image_rgb.shape[1]}x{image_rgb.shape[0]} frame; the model and geometry assume 640x480")
            self._size_warned = True
        frame = pl.Frame.from_image(_to_bgr(image_rgb))       # the pipeline takes BGR (OpenCV order)
        mask, _ = pl.segment(frame, self.model)
        self.last_mask = mask
        return mask

    def on_image(self, image_rgb: np.ndarray) -> list[Barrel]:
        """Segment, then detect. The barrels are also kept as ``last_barrels``."""
        mask = self.segment(image_rgb)
        self.last_barrels = self.detector(mask, self.det_cfg, cam=self.cam)
        return self.last_barrels

    def view(self, image_rgb: np.ndarray, mode: str = "boxes") -> np.ndarray:
        """The picture to show for an RGB frame, as RGB uint8: ``boxes`` (the v2 output image, yellow/green 1-px
        rectangles), ``seg`` (the class mask blended over the image: orange, blue), or ``both``."""
        barrels = self.on_image(image_rgb)
        return self.render(image_rgb, barrels, mode)

    def render(self, image_rgb: np.ndarray, barrels: list[Barrel], mode: str = "boxes",
               raw: list[Barrel] | None = None) -> np.ndarray:
        """The picture for an RGB frame given the barrels to draw: ``view`` passes this frame's answer; the
        multi-frame program (``live/BarrelTracker.fsm``) passes the tracked barrels and, when asked, this frame's
        own answer as ``raw``, drawn in white 1 px so the two can be compared. The segmentation shown for ``seg`` /
        ``both`` is the one ``on_image`` / ``segment`` last computed."""
        if mode not in VIEWS:
            raise ValueError(f"mode must be one of {VIEWS}, got {mode!r}")
        bgr = _to_bgr(image_rgb)
        if mode in ("seg", "both") and self.last_mask is not None:
            bgr = viz.overlay(bgr, self.last_mask)
        if raw:
            for b in raw:
                x0, y0, x1, y1 = b.bbox
                cv2.rectangle(bgr, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        if mode in ("boxes", "both"):
            bgr = det.draw(bgr, barrels)
        return _to_rgb(bgr)

    def annotate(self, image_rgb: np.ndarray, barrels: list[Barrel]) -> np.ndarray:
        """RGB frame with the v2 boxes drawn (``detector.draw``: yellow = orange barrel, green = blue)."""
        return _to_rgb(det.draw(_to_bgr(image_rgb), barrels))
