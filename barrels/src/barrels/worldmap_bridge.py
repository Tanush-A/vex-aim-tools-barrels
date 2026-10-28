"""Bridge from our detections to the robot's world map (NOT WIRED into aim_fsm; v1.5 stub).

What aim_fsm reads: ``worldmap.make_new_aiv_objects`` consumes
``robot.robot0.status['aivision']['objects']['items']``, a list of dicts with exactly the keys
``Barrel.to_aivision_spec`` produces (``type_str='aiobj'``, ``name`` OrangeBarrel/BlueBarrel,
``originx, originy, width, height`` in 320x240 units, optional string ``id``). It projects the
bottom-edge midpoint (height padded to max(h, 1.1·w)) to the ground with a hardcoded tilt/focal
length, steps 11 mm along the bearing, and drops anything farther than 300 mm.

Where a detector can run on the host: ``StateMachineProgram.user_image(image, gray)`` receives
every decoded frame (``robot.camera_image``, 640x480 **RGB**); ``user_annotate(image)`` may return
a drawn-on frame for the camera viewer. Sample program (not part of the package):

    class BarrelDemo(StateMachineProgram):
        def __init__(self):
            super().__init__()
            self.hook = BarrelDetectorHook.load(Path("barrels/results/2026-10-20_v1_test_adaptive/config.json"))
            self.barrels = []
        def user_image(self, image, gray):
            self.barrels = self.hook.on_image(image)
        def user_annotate(self, image):
            return self.hook.annotate(image, self.barrels)

Two integration routes, neither chosen yet (question for Dave, STATUS.md):
  display only  — the program above; the world map keeps using aivision.
  replace       — write ``with_items(robot.robot0.status, barrels_to_aivision_items(barrels))``
                  before ``world_map.update`` runs; bypasses the vendor detector, so latency, the
                  ``check_spec_indicates_held`` box thresholds, and worldmap's 22 mm diameter /
                  1.1·w pad all need agreeing first.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from . import boxfit as bf
from . import detect_cc, geometry as geo, pipeline as pl
from .detect_types import AIVISION_SCALE, Barrel
from .io import BLUE, ORANGE

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
    """Draw the aivision-style boxes. Uses viewer.camera_overlay.draw_aiobj_boxes when the repo root
    is importable (same look as the vendor boxes), else the same rectangles via cv2."""
    items = barrels_to_aivision_items(barrels)
    try:
        from viewer.camera_overlay import draw_aiobj_boxes  # type: ignore
        return draw_aiobj_boxes(image_rgb.copy(), items, scale)
    except Exception:  # noqa: BLE001 — viewer not importable outside the repo
        out = image_rgb.copy()
        for it in items:
            x0, y0 = it["originx"] * scale, it["originy"] * scale
            x1, y1 = x0 + it["width"] * scale, y0 + it["height"] * scale
            cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), BOX_COLORS_RGB.get(it["name"], (255, 255, 255)), 2)
        return out


@dataclass
class BarrelDetectorHook:
    """v1 segmentation + a detector on a live frame. Not wired into aim_fsm (see the module docstring)."""
    model: pl.Model
    cam: geo.CameraModel = geo.AIM_4A8B6118
    detector: object = detect_cc.detect
    det_cfg: object = detect_cc.CCConfig()

    @classmethod
    def load(cls, config_json: Path | str, cam: geo.CameraModel = geo.AIM_4A8B6118) -> "BarrelDetectorHook":
        """From a results config.json that carries a fitted 'model' (as final_test.py writes)."""
        d = json.load(Path(config_json).open())
        m = d["model"]
        cfg = pl.Config.from_dict(m["cfg"])
        boxes = {int(k): bf.Box.from_dict(v) for k, v in m["boxes"].items()}
        model = pl.Model(cfg=cfg, boxes=boxes, inner={int(k): bf.Box.from_dict(v) for k, v in m.get("inner", {}).items()},
                         outer={int(k): bf.Box.from_dict(v) for k, v in m.get("outer", {}).items()}, fit_info=m.get("fit_info", {}))
        return cls(model=model, cam=cam)

    def on_image(self, image_rgb: np.ndarray) -> list[Barrel]:
        frame = pl.Frame.from_image(np.ascontiguousarray(image_rgb[..., ::-1]))     # pipeline expects BGR
        mask, _ = pl.segment(frame, self.model)
        return self.detector(mask, self.det_cfg, cam=self.cam)

    def annotate(self, image_rgb: np.ndarray, barrels: list[Barrel]) -> np.ndarray:
        return draw_boxes(image_rgb, barrels)
