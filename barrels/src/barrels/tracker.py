"""The multi-frame view: boxes that persist over frames (Tanush's ask, 2026-11-06, after the first live run).

The detector answers one image at a time, as the spec says, and that answer is what the eval scores. This layer sits
on top of it in the live program ``live/BarrelTracker.fsm`` only; it never changes a per-image answer, it decides
which of them to show. The rule, in plain words:

  * a barrel is **shown** once it has been seen in at least ``min_hits`` of the last ``window`` frames (3 of 4);
  * it **stays shown** through a missed frame while that still holds, and is **forgotten** after ``max_misses``
    frames in a row without it;
  * a detection **continues** a track when it has the same color and its box overlaps the track's last box by at
    least ``iou_min`` (best overlap first, each used once); anything unmatched starts a new track;
  * the **box shown** is the per-edge median of the last ``smooth`` matched boxes, so one odd frame cannot move it.

So a one-frame false box never appears, and a real barrel that the segmentation loses for a frame does not blink.
Pure Python over ``Barrel`` lists: no robot, no clock, testable frame by frame.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np

from .detect_types import Barrel
from .detector import box_iou


@dataclass(frozen=True)
class TrackConfig:
    window: int = 4          # the last n frames ...
    min_hits: int = 3        # ... in at least this many of which a barrel must have been seen to be shown
    iou_min: float = 0.3     # a detection continues a track when the boxes overlap at least this much (same color)
    max_misses: int = 4      # a track unseen this many frames in a row is forgotten
    smooth: int = 3          # the shown box is the per-edge median of the last k matched boxes


@dataclass
class Track:
    id: int
    color: int
    last_box: tuple[int, int, int, int]      # the last matched detection, what the next frame is matched against
    boxes: deque                             # the last `smooth` matched boxes
    seen: deque                              # the last `window` frames: True where matched
    confidence: float = 1.0                  # of the last matched detection
    misses: int = 0                          # frames in a row without a match

    @property
    def hits(self) -> int:
        return int(sum(self.seen))

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        med = np.median(np.array(self.boxes, dtype=float), axis=0)
        x0, y0, x1, y1 = (int(round(v)) for v in med)
        return x0, y0, max(x1, x0 + 1), max(y1, y0 + 1)


class Tracker:
    """Feed it the detector's barrels frame by frame; it returns the barrels to show."""

    def __init__(self, cfg: TrackConfig = TrackConfig()):
        self.cfg = cfg
        self.tracks: list[Track] = []
        self.frame = 0
        self._next_id = 1

    def update(self, detections: list[Barrel]) -> list[Barrel]:
        cfg = self.cfg
        self.frame += 1
        pairs = []
        for ti, t in enumerate(self.tracks):
            for di, d in enumerate(detections):
                if d.color != t.color:
                    continue
                iou = box_iou(t.last_box, d.bbox)
                if iou >= cfg.iou_min:
                    pairs.append((iou, ti, di))
        pairs.sort(reverse=True)                                    # best overlap first
        used_t: set[int] = set()
        used_d: set[int] = set()
        for iou, ti, di in pairs:
            if ti in used_t or di in used_d:
                continue
            used_t.add(ti); used_d.add(di)
            t, d = self.tracks[ti], detections[di]
            t.last_box = d.bbox
            t.boxes.append(d.bbox)
            t.seen.append(True)
            t.confidence = d.confidence
            t.misses = 0
        for ti, t in enumerate(self.tracks):
            if ti not in used_t:
                t.seen.append(False)
                t.misses += 1
        for di, d in enumerate(detections):
            if di not in used_d:
                self.tracks.append(Track(id=self._next_id, color=d.color, last_box=d.bbox,
                                         boxes=deque([d.bbox], maxlen=cfg.smooth),
                                         seen=deque([True], maxlen=cfg.window), confidence=d.confidence))
                self._next_id += 1
        self.tracks = [t for t in self.tracks if t.misses < cfg.max_misses]
        return self.visible()

    def visible(self) -> list[Barrel]:
        """The tracks that pass the min_hits-of-window rule, as barrels (confidence = hits / window)."""
        out = [Barrel(color=t.color, bbox=t.bbox, confidence=t.hits / self.cfg.window, source="track")
               for t in self.tracks if t.hits >= self.cfg.min_hits]
        return sorted(out, key=lambda b: b.bbox[0])

    def reset(self) -> None:
        self.tracks = []
        self.frame = 0
