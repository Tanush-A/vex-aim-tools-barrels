"""Saving raw frames from the live programs (Tanush, 2026-11-06: the first live run showed failures the committed
frames do not contain, so the frames must be captured where they happen).

``tm save`` writes the current frame as ``snapshots/robot_snapN.png``, the name the camera viewer's ``s`` key uses,
so ``tools/import_snaps.py`` takes them unchanged (``--src barrels/live/snapshots``); N continues from the files
already there, so nothing is overwritten. ``tm rec`` writes every frame for ten seconds (at most ten a second) into
``snapshots/rec_<stamp>/frame_NNN.png`` plus ``frames.json`` (time and frame count per file): the material for
replaying the multi-frame view offline. ``snapshots/`` is gitignored; import what is worth keeping.

Frames arrive in RGB (``robot.camera_image``); files are written in OpenCV's BGR so they load like every other frame.

The vendor detector's answer travels with every saved frame (2026-11-18, TODO B): next to ``robot_snapN.png``,
``tm save`` writes ``robot_snapN_vendor.json`` (what the robot's built-in "aivision" detector reported when that frame
arrived) and ``robot_snapN_vendor.png`` (a copy of the frame with those boxes drawn, for a quick look; the raw frame is
never drawn on). The robot pushes the vendor's object list in its status packets, in 320x240 units, top-left corner +
width + height (``robot.robot0.status['aivision']['objects']``); ``grab_vendor`` takes a reference to it (cheap, called
per frame), ``vendor_record`` turns it into the versioned record with boxes in the frame's own pixels. Neither ever
raises: when the vendor data cannot be read the record says ``available: false`` with the reason, and the frame is
saved all the same. Reading it costs the robot nothing (no request is sent, no mode is switched).
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

SNAP_RE = re.compile(r"^robot_snap(\d+)(?:_vendor)?\.(?:png|json)$")    # a frame, or a vendor side file left behind

VENDOR_JSON_VERSION = 1
VENDOR_SOURCE_SIZE = (320, 240)     # the units of the vendor's boxes (aim_fsm/camera.py: AIVISION_RESOLUTION_SCALE = 2 for 640x480)
VENDOR_COLORS_RGB = {"OrangeBarrel": (255, 128, 0), "BlueBarrel": (0, 100, 255)}     # preview only; anything else is white


def next_snap_index(folder: Path) -> int:
    """One past the highest robot_snapN.png in ``folder`` (0 when there is none). Vendor side files
    (robot_snapN_vendor.json / .png) count too, so a new frame never pairs up with a stale one."""
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


# ---------------------------------------------------------------- the vendor detector's answer for a frame

def vendor_file(snap: Path | str, suffix: str = ".json") -> Path:
    """robot_snapN.png -> robot_snapN_vendor.json (or .png, the preview)."""
    snap = Path(snap)
    return snap.with_name(f"{snap.stem}_vendor{suffix}")


def grab_vendor(robot, clock: Callable[[], float] = time.time) -> dict:
    """What the vendor detector says right now, as cheaply as possible: ``{"time", "aivision", "error"}`` where
    ``aivision`` is a reference to the robot's current status['aivision'] dict (the status thread replaces the whole
    status with every packet, so the reference keeps describing this moment) or None with the reason in ``error``.
    ``robot`` is aim_fsm's Robot (``.robot0`` = the vex.Robot) or a vex.Robot itself. Never raises."""
    out = {"time": None, "aivision": None, "error": ""}
    try:
        out["time"] = clock()
        robot0 = getattr(robot, "robot0", None)
        if robot0 is None:
            robot0 = robot
        thread = getattr(robot0, "_ws_status_thread", None)
        status = thread.current_status if thread is not None else robot0.status
        if thread is not None and status is getattr(thread, "_empty_status", None):
            out["error"] = "no status from the robot (not connected, or status packets lost)"
            return out
        aiv = status["aivision"]
        if not isinstance(aiv, dict) or not isinstance(aiv.get("objects"), dict):
            raise TypeError(f"status['aivision'] has no 'objects' dict: {type(aiv).__name__}")
        out["aivision"] = aiv
    except Exception as e:  # noqa: BLE001 — a save must never fail because of the vendor data
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def vendor_bbox(item: dict, image_size: tuple[int, int] = (640, 480),
                source_size: tuple[int, int] = VENDOR_SOURCE_SIZE) -> list[int] | None:
    """A vendor item's box in the frame's pixels, ``[x0, y0, x1, y1]`` half-open ints (the convention of
    data/labels/*_boxes.json), clipped to the frame. The vendor gives the top-left corner (``originx``, ``originy``)
    and ``width``, ``height`` in ``source_size`` units; each is multiplied by image / source (exactly 2 for a 640x480
    frame). None when a field is missing or nothing of the box is inside the frame."""
    try:
        sx, sy = image_size[0] / source_size[0], image_size[1] / source_size[1]
        x, y, w, h = (float(item[k]) for k in ("originx", "originy", "width", "height"))
        x0, y0 = int(round(x * sx)), int(round(y * sy))
        x1, y1 = int(round((x + w) * sx)), int(round((y + h) * sy))
    except Exception:  # noqa: BLE001 — a malformed item has no box
        return None
    x0, x1 = max(0, x0), min(int(image_size[0]), x1)
    y0, y1 = max(0, y0), min(int(image_size[1]), y1)
    return [x0, y0, x1, y1] if x1 > x0 and y1 > y0 else None


def _vendor_objects(aiv: dict, image_size: tuple[int, int]) -> tuple[list[dict], list[str]]:
    objects = aiv["objects"]
    items = list(objects.get("items") or [])
    count = objects.get("count")
    if isinstance(count, int) and not isinstance(count, bool) and 0 <= count < len(items):
        items = items[:count]               # the library's placeholder status carries one dummy item with count 0
    classnames = []
    try:
        classnames = [str(c.get("name", "")) for c in aiv["classnames"]["items"]]
    except Exception:  # noqa: BLE001 — names are a convenience; every item carries its own
        pass
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        cid = item.get("id")
        cid = cid if isinstance(cid, int) and not isinstance(cid, bool) else None
        name = item.get("name")
        if not (isinstance(name, str) and name):
            is_model = item.get("type_str") == "aiobj" or item.get("type") == 4
            name = classnames[cid] if is_model and cid is not None and 0 <= cid < len(classnames) else ""
        out.append({"name": name, "class_id": cid, "bbox": vendor_bbox(item, image_size),
                    "raw": json.loads(json.dumps(item, default=str))})
    return out, classnames


def vendor_record(grab: dict | None, image_size: tuple[int, int] = (640, 480), frame_count: int | None = None,
                  read_at: str = "frame") -> dict:
    """The versioned record written as robot_snapN_vendor.json, from a ``grab_vendor`` result. Never raises.

    ``objects``: every item the vendor listed (barrels, balls, robots, tags), each with ``name``, ``class_id`` (the
    vendor's ``id``), ``bbox`` in the frame's pixels (``vendor_bbox``; null when the item has no usable box) and
    ``raw`` (the vendor's own fields, untouched). ``read_at``: "frame" when the list was read as the frame arrived,
    "save" when it could only be read at the moment of saving."""
    rec = {"version": VENDOR_JSON_VERSION, "available": False, "error": "", "time": None, "frame_count": None,
           "read_at": str(read_at), "image_size": [640, 480], "source_size": list(VENDOR_SOURCE_SIZE), "classnames": [], "objects": []}
    try:
        w, h = int(image_size[0]), int(image_size[1])
        rec["image_size"] = [w, h]
        rec["frame_count"] = None if frame_count is None else int(frame_count)
        rec["time"] = grab.get("time")
        if grab.get("aivision") is None:
            rec["error"] = str(grab.get("error") or "vendor data not read")
            return rec
        rec["objects"], rec["classnames"] = _vendor_objects(grab["aivision"], (w, h))
        rec["available"] = True
    except Exception as e:  # noqa: BLE001
        rec.update(available=False, error=f"{type(e).__name__}: {e}", objects=[], classnames=[])
    return rec


def vendor_summary(record: dict) -> str:
    """One console line about a record: how many objects and their names, or why there are none."""
    if not record.get("available"):
        return f"vendor NOT available ({record.get('error') or 'no reason given'})"
    names = [o.get("name") or "?" for o in record.get("objects", [])]
    return f"vendor: {len(names)} object{'s' if len(names) != 1 else ''}" + (f" ({', '.join(names)})" if names else "")


def write_vendor(snap: Path | str, record: dict) -> Path:
    """Write the record next to a snapshot as <snap stem>_vendor.json."""
    path = vendor_file(snap)
    path.write_text(json.dumps(record, indent=1) + "\n")
    return path


def draw_vendor(image_rgb: np.ndarray, record: dict) -> np.ndarray:
    """A COPY of the RGB frame with the vendor's boxes on it (1 px; orange barrel orange, blue barrel blue, anything
    else white; the name and score above each), for a quick look. The input is not changed."""
    out = np.ascontiguousarray(image_rgb).copy()
    if not record.get("available"):
        cv2.putText(out, "vendor: not available", (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        return out
    for o in record.get("objects", []):
        if not o.get("bbox"):
            continue
        x0, y0, x1, y1 = o["bbox"]
        color = VENDOR_COLORS_RGB.get(o.get("name"), (255, 255, 255))
        cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), color, 1)
        score = (o.get("raw") or {}).get("score")
        label = f"{o.get('name') or '?'}" + (f" {score}" if score is not None else "")
        cv2.putText(out, label, (x0, max(10, y0 - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
    return out


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
    vendor_error: str = field(default="", repr=False)     # why the last save's vendor files were not written ("" = written, or none asked)

    def save(self, image_rgb: np.ndarray, vendor: dict | None = None, preview: bool = True) -> Path:
        """One frame → snapshots/robot_snapN.png, N continuing from the files already there. With ``vendor`` (a
        ``vendor_record``), also robot_snapN_vendor.json and, with ``preview``, robot_snapN_vendor.png (a copy with the
        vendor boxes drawn). The raw frame is written first and unchanged; a failure writing the vendor files is kept
        in ``vendor_error`` and never raised."""
        folder = Path(self.folder)
        path = write_rgb(folder / f"robot_snap{next_snap_index(folder)}.png", image_rgb)
        self.vendor_error = ""
        if vendor is not None:
            try:
                write_vendor(path, vendor)
                if preview:
                    write_rgb(vendor_file(path, ".png"), draw_vendor(image_rgb, vendor))
            except Exception as e:  # noqa: BLE001 — the frame is saved; the vendor files are extra
                self.vendor_error = f"{type(e).__name__}: {e}"
        return path

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

    def on_frame(self, image_rgb: np.ndarray, frame_count: int | None = None, vendor: dict | None = None) -> Path | None:
        """Call with every camera frame. While recording, writes the frame (at most ``max_fps`` a second) and
        returns its path; when the time is up, writes frames.json, stops, and leaves a line in ``pop_report``.
        ``vendor`` (a ``grab_vendor`` result for this frame) puts the vendor record into the frame's frames.json entry."""
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
        entry = {"file": path.name, "t": round(now - self._rec_start, 3), "frame_count": frame_count}
        if vendor is not None:
            entry["vendor"] = vendor_record(vendor, (image_rgb.shape[1], image_rgb.shape[0]), frame_count)
        self._rec_frames.append(entry)
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
