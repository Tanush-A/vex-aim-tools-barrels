"""Reference detector: class mask -> connected components -> one Barrel per blob.

THIS IS A BASELINE, NOT v2. It exists to exercise the detection evaluation end to end and to set
the floor a real detector must beat. By design it merges touching barrels into one box and knows
nothing about barrel size or geometry.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from . import geometry as geo
from .detect_types import Barrel
from .io import BLUE, ORANGE


@dataclass(frozen=True)
class CCConfig:
    min_area_px: int = 20     # fixed a priori (same as the auto-split); never tuned
    close_px: int = 0         # optional closing of the orange|blue union before components

    def to_dict(self) -> dict:
        return asdict(self)


def detect(mask: np.ndarray, cfg: CCConfig = CCConfig(), cam: geo.CameraModel | None = None) -> list[Barrel]:
    union = np.isin(mask, (ORANGE, BLUE)).astype(np.uint8)
    if cfg.close_px >= 3:
        k = cfg.close_px if cfg.close_px % 2 else cfg.close_px + 1
        union = cv2.morphologyEx(union, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(union, connectivity=8)
    h, w = mask.shape
    out = []
    for i in range(1, n):
        x, y, bw, bh, area = st[i]
        if area < cfg.min_area_px:
            continue
        sel = lab == i
        n_o, n_b = int((mask[sel] == ORANGE).sum()), int((mask[sel] == BLUE).sum())
        if n_o + n_b == 0:
            continue
        color = ORANGE if n_o >= n_b else BLUE
        flags = set()
        if x == 0 or y == 0 or x + bw == w or y + bh == h:
            flags.add("truncated")
        if bw > 0.5 * w and y + bh == h:
            flags.add("top_only")
        b = Barrel(color=color, bbox=(int(x), int(y), int(x + bw), int(y + bh)), confidence=max(n_o, n_b) / (n_o + n_b),
                   flags=frozenset(flags), area=int(area), source="cc")
        out.append(b.with_ground(cam) if cam is not None else b)
    return sorted(out, key=lambda b: b.bbox[0])


def write_detections(out_dir: Path | str, stem: str, barrels: list[Barrel]) -> Path:
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{stem}_det.json"
    p.write_text(json.dumps([b.to_dict() for b in barrels], indent=1))
    return p
