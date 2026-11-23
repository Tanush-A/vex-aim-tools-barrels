#!/usr/bin/env python3
"""Set the color model's six numbers by hand on one frame, watching the segmentation and the boxes (TODO D).

    python barrels/tools/hs_slider.py --filter window_white                 # core_01, occl_01, clutter_01 of that condition
    python barrels/tools/hs_slider.py --filter lampmid6_wood --scenes all   # every train frame of it
    python barrels/tools/hs_slider.py --scenes core_01,touch_01 --unlabeled # only frames without a <stem>_hs.json
    python barrels/tools/hs_slider.py --filter window_white --list          # print which frames would open, and stop
    python barrels/tools/hs_slider.py --filter window_light_core_01 --selftest /tmp/x.png [--thresholds=-3,13,140,103,119,113] [--truth]
    python barrels/tools/hs_slider.py --filter 4A8B_both_abpgray_core_01 --render-grid /tmp/g.png --try adopted --try computed --try "o:-1,6,167;b:102,121,79"
    python barrels/tools/hs_slider.py --filter 4A8B_both_abpgray_core_01 --save-proposal "o:-1,6,167;b:102,121,79" --reasoning "why"

Where the sliders start (2026-11-24). A frame with a saved label opens with it. A frame with no saved label opens with,
in this order: the proposal a Claude session wrote for it (data/labels/<stem>_hs_proposed.json, written with
--save-proposal; its reasoning is shown in the message line), else the COMPUTED proposal (only from the frame and your
hand-drawn boxes: the setting that paints the most barrel minus outside pixels, then the middle of the range of each
slider; it takes a few seconds and appears by itself unless you moved a slider first), else the adopted values. Each
slider shows its feasible range as a shaded band: the values that, with the other five where they are at the start,
still find every barrel of yours found at the start, add no false box and paint at most a little more outside your
boxes (barrels.hsrange). If the start values look right, `w` accepts them. The label records where the start came from
("proposed_by": "claude" | "computed" | null), the start values ("proposal"), whether you moved a slider ("moved") and
the bands ("ranges"). The detector's boxes are never used as truth.

--render-grid OUT.png (no window, for a Claude session choosing a proposal): the raw frame with your boxes, then one
tile per --try setting (painted pixels, your boxes in white, the detector's boxes, and found / false / painted shares).
A --try is "o:h_lo,h_hi,s_lo;b:h_lo,h_hi,s_lo" (either part may be left out: that color keeps the adopted values),
or adopted, computed, claude, saved.

The window: left the raw frame; right the same frame with every pixel the current thresholds do NOT label dimmed
and the labeled pixels painted orange / blue, with the boxes today's detector draws from exactly that segmentation
(yellow = orange barrel, green = blue). Below: eight sliders and the status lines.

The six numbers are the hs color model's: per color a hue range (OpenCV hue 0-179, both ends included) and a floor
on HSV saturation. Orange sits at the red wrap, so its hue sliders run from -30 to 60: -3 means 177. Blue's run
over the whole circle, 0 to 179 (2026-11-25: under a warm lamp the blue paint reads hue 20-60). Two more sliders
(2026-11-25) move the two fixed gates: 7 the brightness floor (a pixel needs V >= it; today 40) and 8 the horizon row
(nothing above it is painted; today 50); they are saved in the label's v_min / horizon_row and start at today's
values, so a label saved before keeps its meaning. The tie rule is the adopted model's. The picture is what
``pipeline.segment`` gives with those numbers; nothing is re-implemented here (``barrels.hslabel``).

Criterion: as much barrel painted as needed to detect it, as little else as possible.

Mouse:
    click / drag on a slider    set it (it becomes the selected slider)
Keys:
    1 .. 8         select a slider (orange hue low, hue high, S floor; blue hue low, hue high, S floor; V gate; horizon row)
    - / =          selected slider one step down / up          [ / ]   five steps down / up
    b              the detector's boxes on / off
    t              your hand-drawn truth boxes on / off (thin white; only if the frame has a _boxes.json)
    m              painted pixels: flat orange / blue, or left in their own color (as `tm seg` shows them)
    r              reset to the adopted values (orange 3..13 S>=140, blue 103..119 S>=113, V >= 40, rows from 50)
    c              copy the thresholds saved for the previous frame
    u              undo: back to what was loaded or last saved for this frame
    w              save        n / p   next / previous frame        q / Esc   quit
Unsaved changes are never dropped silently: with unsaved changes n, p and q ask first; press the same key again to
discard them. Moving on without touching anything writes nothing.

Only train frames open. Test frames are always refused (there is no flag for them), so are geometry-only frames
(calib, ruler, horizon) and frames that are in no split yet (assign splits first: tools/make_splits.py).
Writes data/labels/<stem>_hs.json (docs/DATA.md, "Slider labels").
"""
from __future__ import annotations

import argparse
import dataclasses
import sys
import threading
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import detector as det, geometry as geo, hslabel as hl, hsrange as hx, io, pipeline as pl, splits as sp, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

WIN = "hs slider"
PAINTS = ("flat", "own")
# (class, key, label, slider low end, slider high end)
# 2026-11-25: blue's hue reaches the whole circle (0-179; under a warm lamp the blue paint reads hue 20-60), and two
# gate sliders: the brightness floor (V gate) and the horizon row ("gate" sliders: stored in the label's v_min /
# horizon_row; their defaults are today's fixed values 40 and 50, so every older label means what it meant)
SLIDERS = (("orange", "h_lo", "orange hue low", -30, 60), ("orange", "h_hi", "orange hue high", -30, 60), ("orange", "s_lo", "orange S floor", 0, 255),
           ("blue", "h_lo", "blue hue low", 0, 179), ("blue", "h_hi", "blue hue high", 0, 179), ("blue", "s_lo", "blue S floor", 0, 255),
           ("gate", "v_min", "V gate (brightness)", 0, 150), ("gate", "horizon_row", "horizon row", 0, 150))
N_COLOR = 6                       # the first six sliders are the color thresholds
GATE = "gate"
LIMITS = {f"{c}_{k}": (lo, hi) for c, k, _, lo, hi in SLIDERS if c != GATE}     # the bands' sweep reaches the slider ends
ROW_H = 26                        # one slider row
TRACK_X0, TRACK_RIGHT = 180, 130  # the track starts this far into its column and ends this far before the column's end
TOP_PAD = 18
PANEL_H = TOP_PAD + 4 * ROW_H + 5 * 20 + 2
FONT, FS = cv2.FONT_HERSHEY_SIMPLEX, 0.45
BG, FG, DIMTXT, HILITE, BAND = (32, 32, 32), (235, 235, 235), (150, 150, 150), (0, 255, 255), (60, 105, 60)
HELP = "drag a slider, or 1-8 then - = ([ ] by 5)   b boxes   t truth   m paint   r adopted   c copy previous   u undo   w save/accept   n/p next/prev   q quit"
PROVENANCE = ("proposed", "proposed_by", "moved", "proposal", "ranges")
GUIDE_COARSE = 4         # the tool's range sweep jumps 4 steps, then refines (barrels.hsrange.sweep)
STEPS = {"-": -1, "_": -1, "=": 1, "+": 1, "[": -5, "{": -5, "]": 5, "}": 5}


def track(i: int, w: int, h: int) -> tuple[int, int, int]:
    """(x0, x1, y) of slider i's track in the composite picture: orange in the left column, blue in the right; the
    fourth row holds the V gate (left) and the horizon row (right)."""
    col, row = divmod(i, 3) if i < N_COLOR else (i - N_COLOR, 3)
    return col * w + TRACK_X0, (col + 1) * w - TRACK_RIGHT, h + TOP_PAD + row * ROW_H


def value_to_x(v: int, lo: int, hi: int, x0: int, x1: int) -> int:
    v = min(max(v, lo), hi)
    return x0 + int(round((v - lo) * (x1 - x0) / (hi - lo)))


def x_to_value(x: float, lo: int, hi: int, x0: int, x1: int) -> int:
    return min(max(lo + int(round((x - x0) * (hi - lo) / (x1 - x0))), lo), hi)


def score(mask: np.ndarray, truth: list[dict] | None, row0: int) -> tuple[float, float] | None:
    """(share of the pixels inside the hand-drawn boxes that are painted, share of the pixels outside every box that
    are painted), both from row ``row0`` down (nothing above it is ever painted); None without boxes. The boxes hold
    the barrel plus some table at the corners, so the first number tops out below 100 %."""
    if not truth:
        return None
    inside = np.zeros(mask.shape, bool)
    for b in truth:
        x0, y0, x1, y1 = b["bbox"]
        inside[y0:y1, x0:x1] = True
    painted = mask != 0
    inside[:row0] = False
    outside = ~inside
    outside[:row0] = False
    return float(painted[inside].mean()) if inside.any() else 0.0, float(painted[outside].mean()) if outside.any() else 0.0


def seg_picture(bgr: np.ndarray, mask: np.ndarray, barrels: list, truth: list[dict] | None, show_boxes: bool,
                show_truth: bool, paint: str = "flat") -> np.ndarray:
    """The right-hand picture: the frame with unlabeled pixels dimmed (``worldmap_bridge.seg_views``, as `tm seg`),
    the labeled pixels in flat orange / blue (``paint="flat"``) or untouched (``"own"``), the detector's boxes
    (2 px, yellow / green) and the hand-drawn truth boxes (1 px white)."""
    out = wb.seg_views(bgr, mask)[0]
    if paint == "flat":
        out[mask == ORANGE] = viz.ORANGE_BGR
        out[mask == BLUE] = viz.BLUE_BGR
    if show_boxes:
        out = det.draw(out, barrels, thickness=2)
    if show_truth and truth:
        for b in truth:
            x0, y0, x1, y1 = b["bbox"]
            cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
    return out


def compute_guide(img: np.ndarray, truth: list[dict], base: pl.Model, anchor: dict | None, cam=geo.AIM_4A8B6118_BOXFIT,
                  gates: dict | None = None) -> dict:
    """From the frame and the hand-drawn boxes only: with ``anchor`` None the computed proposal and its ranges
    (``hsrange.propose``), else the ranges around ``anchor`` (reaching the slider ends, ``LIMITS``). ``gates``: the V
    gate and horizon row the ranges are computed at (default the base model's). Returns {"proposal": nested | None,
    "ranges": {t: (lo, hi)}, "source": text}."""
    if gates:
        base = dataclasses.replace(base, cfg=hl.model_from_thresholds(base, hl.thresholds_from_model(base), gates).cfg)
    fe = hx.FrameEval(img, {"barrels": truth}, base, cam=cam)
    if anchor is None:
        p = hx.propose(fe, hl.thresholds_from_model(base), coarse=GUIDE_COARSE)
        return {"proposal": hx.nested(p.thresholds), "ranges": {t: (r.lo, r.hi) for t, r in p.ranges.items()}, "source": p.source}
    r = hx.sweep(fe, hx.flat(anchor), hx.DET, coarse=GUIDE_COARSE, limits=LIMITS)
    return {"proposal": None, "ranges": {t: (x.lo, x.hi) for t, x in r.items()}, "source": "around the start values"}


def ranges_nested(ranges: dict | None) -> dict | None:
    """{t: (lo, hi)} -> the label form {'orange': {'h_lo': [lo, hi], ...}, ...}."""
    if not ranges:
        return None
    return {c: {k: [int(ranges[f"{c}_{k}"][0]), int(ranges[f"{c}_{k}"][1])] for k in io.HS_KEYS if f"{c}_{k}" in ranges} for c in io.HS_CLASSES}


def ranges_flat(ranges: dict | None) -> dict | None:
    if not ranges:
        return None
    return {f"{c}_{k}": tuple(v) for c, per in ranges.items() for k, v in per.items()}


class Session:
    """The tool's whole state and behavior without the window: ``render`` gives the picture, ``on_key`` and
    ``on_mouse`` change the state. A frame is opened only after ``hslabel.require_labelable`` passes."""

    def __init__(self, stems: list[str], splits: dict[str, list[str]], base: pl.Model, raw_dir: Path | str | None = None,
                 labels_dir: Path | str | None = None, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, scale: float = 1.0,
                 git: str = "unknown", propose: bool = True, background: bool = True):
        self.stems, self.splits, self.base, self.cam, self.scale, self.git = list(stems), splits, base, cam, scale, git
        self.propose, self.background = propose, background
        self._guides: dict[tuple, dict] = {}
        self._lock = threading.Lock()
        self.raw_dir, self.labels_dir = Path(raw_dir or io.RAW_DIR), Path(labels_dir or io.LABELS_DIR)
        self.adopted = hl.thresholds_from_model(base)
        self.default_gates = hl.gates_of(base)
        self.det_cfg = det.DetConfig()
        self.show_boxes, self.show_truth, self.paint = True, False, 0
        self.sel, self.grab, self.pending = 0, None, None
        self.last_saved: tuple[str, dict] | None = None
        self.load(0)

    # ---------------------------------------------------------------- state
    @property
    def stem(self) -> str:
        return self.stems[self.idx]

    @property
    def dirty(self) -> bool:
        return self.thr != self.baseline or self.gates != self.gates_baseline

    def value(self, i: int) -> int:
        """Slider i's current value (a color threshold or a gate)."""
        name, key = SLIDERS[i][:2]
        return self.gates[key] if name == GATE else self.thr[name][key]

    def load(self, i: int) -> None:
        self.idx = i % len(self.stems)
        stem = self.stem
        hl.require_labelable(stem, self.splits)             # a test frame stops here, before its image is read
        path = io.find_image(stem, self.raw_dir)
        if path is None:
            raise FileNotFoundError(f"no image for {stem} in {self.raw_dir}")
        self.img = io.load_image(path)
        self.sha = io.file_sha1(path)
        self.frame = pl.Frame.from_image(self.img)
        self.msg, self.note, self.has_label = "", "", False
        self.truth = None
        if io.boxes_path(stem, self.labels_dir).exists():
            try:
                self.truth = io.load_boxes(stem, self.labels_dir, check_image=False)["barrels"]
            except ValueError as e:
                self.msg = f"truth boxes not shown: {e}"
        self.thr = hl.copy_thresholds(self.adopted)
        self.gates = dict(self.default_gates)
        self.start, self.proposal, self.reasoning, self.ranges, self.prov = "adopted", None, "", None, {}
        self.guide_key = None
        if io.hs_path(stem, self.labels_dir).exists():
            try:
                meta = io.load_hs(stem, self.labels_dir, check_image=False)
                self.thr, self.note, self.has_label = hl.copy_thresholds(meta), meta.get("note", ""), True
                self.gates = hl.gates_of(self.base, meta)
                self.start = "saved label"
                self.prov = {k: meta[k] for k in PROVENANCE if k in meta}
                self.ranges = ranges_flat(meta.get("ranges"))
                now = self.base.cfg.short_hash()
                if meta.get("image_sha1") and meta["image_sha1"] != self.sha:
                    self.msg = "the image changed since this label was saved: check it, then w"
                elif meta["base_model"] != now:
                    self.msg = f"this label was set against model {meta['base_model']} (now {now}): check it, then w"
            except ValueError as e:
                self.msg = f"saved label ignored ({e}); starting from the adopted values"
        if not self.has_label:
            self._start_from_proposal(stem)
        self.baseline = hl.copy_thresholds(self.thr)
        self.gates_baseline = dict(self.gates)
        self.grab = self.pending = None
        self._seg = self._view = None
        if self.propose and self.truth and self.ranges is None:
            anchor = None if self.start == "computing" else self.thr
            self.guide_key = (stem, None if anchor is None else hx.key(hx.flat(anchor)))
            self._request(self.guide_key, self.img, self.truth, anchor, dict(self.gates))
        self.poll()

    def _start_from_proposal(self, stem: str) -> None:
        """No saved label: Claude's proposal file, else the computed proposal (asked for in ``load``), else adopted."""
        p = io.hs_proposed_path(stem, self.labels_dir)
        if p.exists():
            try:
                d = io.load_hs_proposed(stem, self.labels_dir)
                self.thr = hl.copy_thresholds(d)
                self.start, self.proposal, self.reasoning = "claude", hl.copy_thresholds(d), d.get("reasoning", "")
                self.msg = "Claude's proposal: " + (self.reasoning or "(no reasoning given)") + "   (w accepts)"
                if self.reasoning:
                    print(f"{stem}: Claude's proposal: {self.reasoning}")
                return
            except ValueError as e:
                self.msg = f"proposal file ignored ({e})"
        if self.propose and self.truth:
            self.start = "computing"
            self.msg = "computing a proposal from your boxes (a few seconds) ..."

    # ---------------------------------------------------------------- the guide (proposal and bands), off the window's thread
    def _request(self, gkey: tuple, img, truth, anchor, gates: dict | None = None) -> None:
        with self._lock:
            if gkey in self._guides:
                return
            self._guides[gkey] = {}                     # empty = being computed
        if self.background:
            threading.Thread(target=self._run, args=(gkey, img, truth, anchor, gates), daemon=True).start()
        else:
            self._run(gkey, img, truth, anchor, gates)

    def _run(self, gkey, img, truth, anchor, gates: dict | None = None) -> None:
        try:
            g = compute_guide(img, truth, self.base, anchor, self.cam, gates if gates != self.default_gates else None)
        except Exception as e:  # noqa: BLE001 - a failed proposal must not take the window down
            g = {"error": f"{type(e).__name__}: {e}"}
        with self._lock:
            self._guides[gkey] = g

    def poll(self) -> None:
        """Apply a finished guide for the current frame: the bands, and (computed start) the proposal itself unless a
        slider was moved meanwhile."""
        if self.guide_key is None:
            return
        with self._lock:
            g = self._guides.get(self.guide_key)
        if not g:
            return
        self.guide_key = None
        self._view = None
        if "error" in g:
            self.msg = f"no proposal: {g['error']}"
            if self.start == "computing":
                self.start = "adopted"
            return
        self.ranges = g["ranges"]
        if self.start == "computing":
            if self.dirty:
                self.start = "adopted"
                self.msg = "a computed proposal arrived after you moved a slider: not applied (bands shown)"
            else:
                self.set_thresholds(g["proposal"])
                self.baseline = hl.copy_thresholds(self.thr)
                self.start, self.proposal = "computed", hl.copy_thresholds(g["proposal"])
                self.msg = f"computed proposal ({g['source']}); the bands are each slider's feasible range   (w accepts)"

    def set_value(self, i: int, v: int) -> None:
        """Set slider i, kept inside its range and with hue low <= hue high."""
        name, key, _, lo, hi = SLIDERS[i]
        v = min(max(int(v), lo), hi)
        if name == GATE:
            if self.gates[key] != v:
                self.gates[key] = v
                self._seg = self._view = None
            return
        t = self.thr[name]
        if key == "h_lo":
            v = min(v, t["h_hi"])
        elif key == "h_hi":
            v = max(v, t["h_lo"])
        if t[key] != v:
            t[key] = v
            self._seg = self._view = None

    def set_gates(self, gates: dict) -> None:
        """The V gate and the horizon row (each kept inside its slider's span)."""
        for i, (name, key, _, lo, hi) in enumerate(SLIDERS):
            if name == GATE and key in gates:
                self.set_value(i, gates[key])

    def set_thresholds(self, thr: dict) -> None:
        io.validate_hs_thresholds(thr)
        self.thr = hl.copy_thresholds(thr)
        self._seg = self._view = None

    def result(self) -> tuple[np.ndarray, list]:
        """(class mask, barrels) for the current thresholds: ``pipeline.segment`` with the model built from them,
        then ``detector.detect`` with ``DetConfig()`` and the project camera. Cached until a number changes."""
        if self._seg is None:
            mask, _ = pl.segment(self.frame, hl.model_from_thresholds(self.base, self.thr, self.gates))
            self._seg = (mask, det.detect(mask, self.det_cfg, self.cam))
        return self._seg

    def save(self) -> Path:
        _, barrels = self.result()
        meta = {**hl.label_meta(self.stem, self.sha, self.thr, self.base, len(barrels), self.git, self.note, self.gates), **self.provenance()}
        p = io.save_hs(self.stem, meta, self.labels_dir)
        self.prov = {k: meta[k] for k in PROVENANCE}
        self.baseline = hl.copy_thresholds(self.thr)
        self.gates_baseline = dict(self.gates)
        self.has_label = True
        self.last_saved = (self.stem, hl.copy_thresholds(self.thr), dict(self.gates))
        self.msg = f"saved {p.name}: {hl.describe(self.thr)}{gates_text(self.gates, self.default_gates)}, {len(barrels)} box(es)"
        print(self.msg)
        return p

    def provenance(self) -> dict:
        """The label's proposal fields: where the start values came from, whether a slider was moved, the bands."""
        if self.prov:                                   # re-saving a label: keep its origin, update moved and the bands
            prop = self.prov.get("proposal")
            return {**{k: self.prov.get(k) for k in PROVENANCE}, "moved": (self.thr != prop) if prop else self.prov.get("moved"),
                    "ranges": ranges_nested(self.ranges) or self.prov.get("ranges")}
        by = self.start if self.start in io.HS_PROPOSED_BY else None
        return {"proposed": by is not None, "proposed_by": by, "moved": (self.thr != self.proposal) if by else None,
                "proposal": self.proposal if by else None, "ranges": ranges_nested(self.ranges)}

    def copy_previous(self) -> None:
        """Take the thresholds saved for the previous frame in the list; failing that, the last ones saved in
        this session."""
        src = None
        if self.idx > 0:
            prev = self.stems[self.idx - 1]
            try:
                meta = io.load_hs(prev, self.labels_dir, check_image=False)
                src = (prev, hl.copy_thresholds(meta), hl.gates_of(self.base, meta))
            except (FileNotFoundError, ValueError):
                src = None
        if src is None and self.last_saved and self.last_saved[0] != self.stem:
            src = self.last_saved
        if src is None:
            self.msg = "nothing to copy: the previous frame has no saved thresholds"
            return
        self.set_thresholds(src[1])
        self.set_gates(src[2])
        self.msg = f"copied from {src[0]} (not saved yet)"

    # ---------------------------------------------------------------- input
    def on_key(self, k: int) -> bool:
        """Handle one key code; False when the tool should close."""
        ch = chr(k) if 0 < k < 128 else ""
        leave = "q" if (ch == "q" or k == 27) else ch if ch in ("n", "p") else None
        if leave:
            if self.dirty and self.pending != leave:
                self.pending = leave
                self.msg = f"UNSAVED changes on this frame: w saves them; press {leave} again to discard them"
                self._view = None
                return True
            if leave == "q":
                return False
            self.load(self.idx + (1 if leave == "n" else -1))
            return True
        if not ch:
            return True
        self.pending = None
        self._view = None
        if ch in "12345678"[:len(SLIDERS)]:
            self.sel = int(ch) - 1
        elif ch in STEPS:
            self.set_value(self.sel, self.value(self.sel) + STEPS[ch])
            self.msg = ""
        elif ch == "b":
            self.show_boxes = not self.show_boxes
        elif ch == "t":
            self.show_truth = not self.show_truth
            if self.truth is None:
                self.msg = "this frame has no hand-drawn boxes (tools/box_tool.py)"
        elif ch == "m":
            self.paint = (self.paint + 1) % len(PAINTS)
        elif ch == "r":
            self.set_thresholds(self.adopted)
            self.set_gates(self.default_gates)
            self.msg = "reset to the adopted values (not saved)"
        elif ch == "c":
            self.copy_previous()
        elif ch == "u":
            self.set_thresholds(self.baseline)
            self.set_gates(self.gates_baseline)
            self.msg = "back to what was loaded / last saved"
        elif ch == "w":
            self.save()
        return True

    def on_mouse(self, event, sx, sy, flags=0, _=None) -> None:
        x, y = sx / self.scale, sy / self.scale
        h, w = self.img.shape[:2]
        if event == cv2.EVENT_LBUTTONDOWN:
            for i, (_, _, _, lo, hi) in enumerate(SLIDERS):
                x0, x1, yc = track(i, w, h)
                if abs(y - yc) <= ROW_H // 2 and x0 - 12 <= x <= x1 + 12:
                    self.sel = self.grab = i
                    self.pending, self.msg, self._view = None, "", None
                    self.set_value(i, x_to_value(x, lo, hi, x0, x1))
                    break
            else:       # say where the click landed, so a window that reports other coordinates shows up at once
                self.msg, self._view = f"click at x {x:.0f}, y {y:.0f}: not on a slider track (tracks: y {h + TOP_PAD}-{h + TOP_PAD + 2 * ROW_H}, x {TRACK_X0}-{w - TRACK_RIGHT} and {w + TRACK_X0}-{2 * w - TRACK_RIGHT})", None
        elif event == cv2.EVENT_MOUSEMOVE and self.grab is not None:
            _, _, _, lo, hi = SLIDERS[self.grab]
            x0, x1, _ = track(self.grab, w, h)
            self.set_value(self.grab, x_to_value(x, lo, hi, x0, x1))
        elif event == cv2.EVENT_LBUTTONUP:
            self.grab = None

    # ---------------------------------------------------------------- render
    def status(self) -> list[str]:
        _, barrels = self.result()
        state = ("UNSAVED *" if self.dirty else "saved") if self.has_label else ("none yet, changed *" if self.dirty else "none yet")
        truth = "none" if self.truth is None else f"{len(self.truth)} ({'shown' if self.show_truth else 'hidden'})"
        cfg = self.base.cfg
        sc = score(self.result()[0], self.truth, cfg.horizon_row)
        scored = ("score: no boxes on this frame" if sc is None else
                  f"score: barrels painted {100 * sc[0]:.1f} % of the inside of your boxes (first: push this up)   "
                  f"painted outside your boxes {100 * sc[1]:.2f} % (second: keep this down)")
        start = {"computing": "computing a proposal ...", "claude": "Claude's proposal", "computed": "computed proposal"}.get(self.start, self.start)
        return [f"[{self.idx + 1}/{len(self.stems)}] {self.stem}   label: {state}   detector boxes={len(barrels)}{'' if self.show_boxes else ' (hidden)'}"
                f"   truth boxes={truth}   paint={PAINTS[self.paint]}   start: {start}",
                hl.describe(self.thr) + f"   V >= {self.gates['v_min']}, rows >= {self.gates['horizon_row']}"
                f"      (today's gates V >= {cfg.v_min}, rows >= {cfg.horizon_row}; model {cfg.short_hash()})",
                scored, self.msg, HELP]

    def render(self) -> np.ndarray:
        self.poll()
        if self._view is not None:
            return self._view
        mask, barrels = self.result()
        h, w = self.img.shape[:2]
        view = np.full((h + PANEL_H, 2 * w, 3), BG, np.uint8)
        view[:h, :w] = self.img
        view[:h, w:] = seg_picture(self.img, mask, barrels, self.truth, self.show_boxes, self.show_truth, PAINTS[self.paint])
        for i, (name, key, label, lo, hi) in enumerate(SLIDERS):
            x0, x1, yc = track(i, w, h)
            col = (x0 // w) * w
            v = self.value(i)
            on = i == self.sel
            cv2.putText(view, f"{i + 1} {label}", (col + 8, yc + 5), FONT, FS, HILITE if on else FG, 1, cv2.LINE_AA)
            if self.ranges and f"{name}_{key}" in self.ranges:                         # the feasible range: a shaded band
                rlo, rhi = self.ranges[f"{name}_{key}"]
                cv2.rectangle(view, (value_to_x(rlo, lo, hi, x0, x1), yc - 6), (value_to_x(rhi, lo, hi, x0, x1), yc + 6), BAND, -1)
            cv2.line(view, (x0, yc), (x1, yc), (110, 110, 110), 2)
            adopted = self.default_gates[key] if name == GATE else self.adopted[name][key]
            ax = value_to_x(adopted, lo, hi, x0, x1)                                     # a tick at the adopted value
            cv2.line(view, (ax, yc + 5), (ax, yc + 10), DIMTXT, 1)
            kx = value_to_x(v, lo, hi, x0, x1)
            knob = viz.ORANGE_BGR if name == "orange" else viz.BLUE_BGR if name == "blue" else (200, 200, 200)
            cv2.rectangle(view, (kx - 3, yc - 8), (kx + 3, yc + 8), HILITE if on else knob, -1)
            text = f">= {v}" if key in ("s_lo", "v_min") else f"from row {v}" if key == "horizon_row" else hl.hue_text(v)
            cv2.putText(view, text, (x1 + 14, yc + 5), FONT, FS, HILITE if on else FG, 1, cv2.LINE_AA)
        y = h + TOP_PAD + 4 * ROW_H + 8
        for j, line in enumerate(self.status()):
            color = HILITE if j == 3 else DIMTXT if j == 4 else FG
            if len(line) > 200:
                line = line[:197] + "..."
            cv2.putText(view, line, (8, y + j * 20), FONT, FS, color, 1, cv2.LINE_AA)
        if self.scale != 1:
            view = cv2.resize(view, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_NEAREST if self.scale > 1 else cv2.INTER_AREA)
        self._view = view
        return view


def gates_text(gates: dict, default: dict) -> str:
    """'' when the gates are today's, else '   V >= 30, rows >= 50'."""
    g = {**default, **(gates or {})}
    return "" if g == default else f"   V >= {g['v_min']}, rows >= {g['horizon_row']}"


def parse_thresholds(text: str) -> dict:
    """'3,13,140,103,119,113' (orange hue low, high, S floor; blue hue low, high, S floor) -> the thresholds dict."""
    try:
        v = [int(x) for x in text.split(",")]
    except ValueError:
        raise ValueError(f"--thresholds needs six whole numbers, got {text!r}") from None
    if len(v) != 6:
        raise ValueError(f"--thresholds needs six numbers (orange hue low, high, S floor; blue hue low, high, S floor), got {len(v)}")
    thr = {"orange": dict(zip(io.HS_KEYS, v[:3])), "blue": dict(zip(io.HS_KEYS, v[3:]))}
    io.validate_hs_thresholds(thr)
    return thr


def parse_try(text: str, adopted: dict) -> dict:
    """'o:-1,6,167;b:102,121,79' -> the thresholds dict; a color left out keeps the adopted values. Optional parts
    'v:30' (the V gate) and 'z:40' (the horizon row) add a "gates" entry (2026-11-25); without them there is none and
    the gates stay today's."""
    thr = hl.copy_thresholds(adopted)
    for part in (x.strip() for x in text.split(";") if x.strip()):
        tag, _, nums = part.partition(":")
        gate = {"v": "v_min", "z": "horizon_row"}.get(tag.strip().lower())
        if gate is not None:
            try:
                thr.setdefault("gates", {})[gate] = int(nums)
            except ValueError:
                raise ValueError(f"--try: one whole number after {tag}:, got {nums!r}") from None
            continue
        name = {"o": "orange", "orange": "orange", "b": "blue", "blue": "blue"}.get(tag.strip().lower())
        if name is None:
            raise ValueError(f"--try: each part is o:... or b:..., got {part!r}")
        try:
            v = [int(x) for x in nums.split(",")]
        except ValueError:
            raise ValueError(f"--try: three whole numbers after {tag}:, got {nums!r}") from None
        if len(v) != 3:
            raise ValueError(f"--try: three numbers (hue low, hue high, S floor) after {tag}:, got {len(v)}")
        thr[name] = dict(zip(io.HS_KEYS, v))
    io.validate_hs_thresholds(thr)
    return thr


def grid_tile(img: np.ndarray, truth: list[dict] | None, base: pl.Model, thr: dict, title: str, fe: hx.FrameEval | None,
              cam=geo.AIM_4A8B6118_BOXFIT) -> np.ndarray:
    """One labelled tile: the painted pixels with ``thr``, the hand boxes (white) and the detector's boxes, under a
    two-line header (the setting; found / false against the hand boxes and the painted shares)."""
    gates = thr.get("gates")
    model = hl.model_from_thresholds(base, thr, gates)
    mask, _ = pl.segment(pl.Frame.from_image(img), model)
    barrels = det.detect(mask, det.DetConfig(), cam)
    pic = seg_picture(img, mask, barrels, truth, True, True, "flat")
    sc = score(mask, truth, model.cfg.horizon_row or 0)
    line2 = f"detector boxes {len(barrels)}"
    if gates:
        fe = hx.FrameEval(img, {"barrels": truth}, dataclasses.replace(base, cfg=model.cfg), cam=cam) if truth else None
    if fe is not None and truth:
        o = fe.evaluate(hx.flat(thr))
        line2 = f"found {len(o.found)}/{len(truth)} of your boxes, false {o.n_false}"
    if sc is not None:
        line2 += f"   painted: inside your boxes {100 * sc[0]:.1f} %, outside {100 * sc[1]:.2f} %"
    head = np.full((44, pic.shape[1], 3), BG, np.uint8)
    cv2.putText(head, f"{title}: {hl.describe(thr)}{gates_text(gates or {}, hl.gates_of(base))}"[:110], (6, 17), FONT, FS, FG, 1, cv2.LINE_AA)
    cv2.putText(head, line2[:110], (6, 37), FONT, FS, HILITE, 1, cv2.LINE_AA)
    return np.vstack([head, pic])


def render_grid(img: np.ndarray, truth: list[dict] | None, base: pl.Model, settings: list[tuple[str, dict]], cols: int = 3,
                cam=geo.AIM_4A8B6118_BOXFIT) -> np.ndarray:
    """The raw frame with the hand boxes, then one tile per (title, thresholds), ``cols`` per row."""
    raw = img.copy()
    for b in truth or []:
        x0, y0, x1, y1 = b["bbox"]
        cv2.rectangle(raw, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
    head = np.full((44, raw.shape[1], 3), BG, np.uint8)
    cv2.putText(head, f"raw frame, your boxes (white): {len(truth or [])}", (6, 17), FONT, FS, FG, 1, cv2.LINE_AA)
    cv2.putText(head, "each tile: painted pixels, your boxes white, detector boxes yellow (orange) / green (blue)", (6, 37), FONT, FS, DIMTXT, 1, cv2.LINE_AA)
    fe = hx.FrameEval(img, {"barrels": truth}, base, cam=cam) if truth else None
    tiles = [np.vstack([head, raw])] + [grid_tile(img, truth, base, thr, title, fe, cam) for title, thr in settings]
    cols = max(1, min(cols, len(tiles)))
    blank = np.full_like(tiles[0], BG)
    rows = [np.hstack(tiles[i:i + cols] + [blank] * (cols - len(tiles[i:i + cols]))) for i in range(0, len(tiles), cols)]
    return np.vstack(rows)


def resolve_try(text: str, s: "Session") -> tuple[str, dict]:
    """A --try value -> (title, thresholds): a keyword (adopted, computed, claude, saved) or numbers."""
    t = text.strip().lower()
    if t == "adopted":
        return "adopted", hl.copy_thresholds(s.adopted)
    if t == "computed":
        if not s.truth:
            raise ValueError("--try computed needs the frame's hand-drawn boxes")
        return "computed", compute_guide(s.img, s.truth, s.base, None, s.cam)["proposal"]
    if t == "claude":
        return "claude", hl.copy_thresholds(io.load_hs_proposed(s.stem, s.labels_dir))
    if t == "saved":
        meta = io.load_hs(s.stem, s.labels_dir, check_image=False)
        g = hl.gates_of(s.base, meta)
        return "saved", {**hl.copy_thresholds(meta), **({"gates": g} if g != s.default_gates else {})}
    return text, parse_try(text, s.adopted)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR)
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--filter", default="", help="only frames whose name contains this")
    ap.add_argument("--scenes", default=",".join(hl.DEFAULT_SCENES),
                    help="comma list of scene_nn (or bare scene tags); 'all' = every scene (default: the three the plan labels per condition)")
    ap.add_argument("--unlabeled", action="store_true", help="only frames without a _hs.json")
    ap.add_argument("--scale", type=float, default=1.0, help=f"window scale (the picture is 1280 x {480 + PANEL_H} at 1)")
    ap.add_argument("--list", action="store_true", help="no window: print the frames that would open and the ones refused")
    ap.add_argument("--selftest", type=Path, default=None, metavar="OUT.png", help="no window: write the picture for the first selected frame")
    ap.add_argument("--thresholds", default="", help="selftest: six numbers 'o_hlo,o_hhi,o_s,b_hlo,b_hhi,b_s' instead of the saved / adopted ones (write --thresholds=-3,... when the first is negative)")
    ap.add_argument("--truth", action="store_true", help="selftest: draw the hand-drawn truth boxes too")
    ap.add_argument("--no-propose", action="store_true", help="no computed proposal and no bands (start from the saved label, Claude's proposal or the adopted values)")
    ap.add_argument("--render-grid", type=Path, default=None, metavar="OUT.png", help="no window: the first selected frame with each --try setting side by side")
    ap.add_argument("--try", dest="tries", action="append", default=[], metavar="SETTING",
                    help="render-grid: 'o:h_lo,h_hi,s_lo;b:h_lo,h_hi,s_lo' or adopted / computed / claude / saved (repeatable; write --try=o:-3,... when a number is negative)")
    ap.add_argument("--save-proposal", default="", metavar="SETTING", help="write data/labels/<stem>_hs_proposed.json for the ONE selected frame (Claude's proposal)")
    ap.add_argument("--reasoning", default="", help="save-proposal: why these numbers (shown in the window)")
    args = ap.parse_args(argv)
    if args.render_grid is not None or args.save_proposal:
        names = {p.stem for p in io.list_images(args.raw)}
        if args.filter in names:            # a whole frame name: that frame, whatever its scene
            args.scenes = "all"

    splits = sp.load_splits()
    sel = hl.select_frames([p.stem for p in io.list_images(args.raw)], splits, hl.parse_scenes(args.scenes), args.filter)
    stems = [s for s in sel.stems if not (args.unlabeled and io.hs_path(s, args.labels).exists())]
    for why, names in sel.refused.items():
        print(f"refused, {why}: {len(names)} frame(s) ({', '.join(names[:4])}{', ...' if len(names) > 4 else ''})")
    if args.list:
        for s in stems:
            print(s + ("   [has _hs.json]" if io.hs_path(s, args.labels).exists() else ""))
        print(f"{len(stems)} frame(s)")
        return 0
    if not stems:
        print("no frames to label match (train frames only; --scenes all for every scene)")
        return 1
    one_shot = args.selftest is not None or args.render_grid is not None or bool(args.save_proposal)
    if args.save_proposal:
        if len(stems) != 1:
            print(f"--save-proposal needs exactly one frame; --filter selects {len(stems)}")
            return 1
        hl.require_labelable(stems[0], splits)
        thr = parse_try(args.save_proposal, hl.thresholds_from_model(hl.adopted_model()))
        p = io.save_hs_proposed(stems[0], thr, args.reasoning, args.labels)
        print(f"wrote {p}: {hl.describe(thr)}")
        return 0
    s = Session(stems, splits, hl.adopted_model(), args.raw, args.labels, scale=args.scale, git=hl.detector_git(),
                propose=not args.no_propose and args.render_grid is None, background=not one_shot)
    if args.render_grid is not None:
        settings = [resolve_try(t, s) for t in (args.tries or ["adopted"])]
        pic = render_grid(s.img, s.truth, s.base, settings, cam=s.cam)
        if not cv2.imwrite(str(args.render_grid), pic):
            raise OSError(f"could not write {args.render_grid}")
        for title, thr in settings:
            print(f"{title}: {hl.describe(thr)}")
        print(f"wrote {args.render_grid} ({s.stem})")
        return 0
    if args.selftest is not None:
        if args.thresholds:
            s.set_thresholds(parse_thresholds(args.thresholds))
        s.show_truth = args.truth
        if not cv2.imwrite(str(args.selftest), s.render()):
            raise OSError(f"could not write {args.selftest}")
        print("\n".join(s.status()[:2]))
        print(f"wrote {args.selftest}")
        return 0
    cv2.namedWindow(WIN, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WIN, s.on_mouse)
    print(__doc__)
    while True:
        s.poll()
        cv2.imshow(WIN, s.render())
        k = cv2.waitKey(20) & 0xFF
        if k == 255:
            continue
        if not s.on_key(k):
            break
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    sys.exit(main())
