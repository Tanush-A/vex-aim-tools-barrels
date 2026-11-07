"""Saving raw frames from the live programs (Tanush, 2026-11-06: the first live run showed failures the committed
frames do not contain, so the frames must be captured where they happen).

``tm save`` writes the current frame as ``snapshots/robot_snapN.png``, the name the camera viewer's ``s`` key uses,
so ``tools/import_snaps.py`` takes them unchanged (``--src barrels/live/snapshots``); N continues from the files
already there, so nothing is overwritten. ``tm rec`` writes every frame for ten seconds (at most ten a second) into
``snapshots/rec_<stamp>/frame_NNN.png`` plus ``frames.json`` (time and frame count per file): the material for
replaying the multi-frame view offline. ``snapshots/`` is gitignored; import what is worth keeping.

Frames arrive in RGB (``robot.camera_image``); files are written in OpenCV's BGR so they load like every other frame.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

SNAP_RE = re.compile(r"^robot_snap(\d+)\.png$")


def next_snap_index(folder: Path) -> int:
    """One past the highest robot_snapN.png in ``folder`` (0 when there is none)."""
    n = -1
    if folder.is_dir():
        for p in folder.iterdir():
            m = SNAP_RE.match(p.name)
            if m:
                n = max(n, int(m.group(1)))
    return n + 1


def write_rgb(path: Path, image_rgb: np.ndarray) -> Path:
    """Write an RGB array as a PNG in OpenCV's BGR order (what ``io.load_image`` reads back)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), cv2.cvtColor(np.ascontiguousarray(image_rgb), cv2.COLOR_RGB2BGR)):
        raise OSError(f"could not write {path}")
    return path


@dataclass
class FrameCapture:
    """``save`` for single frames, ``start_recording`` + ``on_frame`` for a timed sequence."""
    folder: Path = Path("snapshots")        # relative to where simple_cli was started (barrels/live/)
    rec_seconds: float = 10.0
    max_fps: float = 10.0
    clock: Callable[[], float] = time.monotonic
    _rec_dir: Path | None = field(default=None, repr=False)
    _rec_seconds: float = field(default=0.0, repr=False)
    _rec_start: float = field(default=0.0, repr=False)
    _rec_last: float = field(default=-1e9, repr=False)
    _rec_frames: list[dict] = field(default_factory=list, repr=False)
    _report: str | None = field(default=None, repr=False)

    def save(self, image_rgb: np.ndarray) -> Path:
        """One frame → snapshots/robot_snapN.png, N continuing from the files already there."""
        folder = Path(self.folder)
        return write_rgb(folder / f"robot_snap{next_snap_index(folder)}.png", image_rgb)

    @property
    def recording(self) -> bool:
        return self._rec_dir is not None

    def start_recording(self, seconds: float | None = None, stamp: str | None = None) -> Path:
        """Begin a recording into snapshots/rec_<stamp>/; ``on_frame`` writes the frames until ``seconds`` pass."""
        if self.recording:
            self.stop_recording()
        stamp = stamp or time.strftime("%Y-%m-%d_%H%M%S")
        self._rec_dir = Path(self.folder) / f"rec_{stamp}"
        self._rec_dir.mkdir(parents=True, exist_ok=True)
        self._rec_seconds = seconds or self.rec_seconds
        self._rec_start = self.clock()
        self._rec_last = -1e9
        self._rec_frames = []
        return self._rec_dir

    def on_frame(self, image_rgb: np.ndarray, frame_count: int | None = None) -> Path | None:
        """Call with every camera frame. While recording, writes the frame (at most ``max_fps`` a second) and
        returns its path; when the time is up, writes frames.json, stops, and leaves a line in ``pop_report``."""
        if not self.recording:
            return None
        now = self.clock()
        if now - self._rec_start >= self._rec_seconds:
            self.stop_recording()
            return None
        if now - self._rec_last < 0.999 / self.max_fps:       # a hair under, so a stream at exactly max_fps is kept whole
            return None
        self._rec_last = now
        path = self._rec_dir / f"frame_{len(self._rec_frames):03d}.png"
        write_rgb(path, image_rgb)
        self._rec_frames.append({"file": path.name, "t": round(now - self._rec_start, 3), "frame_count": frame_count})
        return path

    def stop_recording(self) -> Path | None:
        """Write frames.json for what was recorded and stop. None when nothing was recording."""
        if not self.recording:
            return None
        path = self._rec_dir / "frames.json"
        path.write_text(json.dumps({"seconds": self._rec_seconds, "max_fps": self.max_fps, "frames": self._rec_frames}, indent=1))
        n = len(self._rec_frames)
        self._report = f"recorded {n} frame{'s' if n != 1 else ''} in {self._rec_seconds:g} s -> {self._rec_dir}"
        self._rec_dir = None
        return path

    def pop_report(self) -> str | None:
        """The line to print once a recording has finished (once; None otherwise)."""
        r, self._report = self._report, None
        return r
