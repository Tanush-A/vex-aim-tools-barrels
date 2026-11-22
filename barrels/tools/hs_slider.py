#!/usr/bin/env python3
"""Set the color model's six numbers by hand on one frame, watching the segmentation and the boxes (TODO D).

    python barrels/tools/hs_slider.py --filter window_white                 # core_01, occl_01, clutter_01 of that condition
    python barrels/tools/hs_slider.py --filter lampmid6_wood --scenes all   # every train frame of it
    python barrels/tools/hs_slider.py --scenes core_01,touch_01 --unlabeled # only frames without a <stem>_hs.json
    python barrels/tools/hs_slider.py --filter window_white --list          # print which frames would open, and stop
    python barrels/tools/hs_slider.py --filter window_light_core_01 --selftest /tmp/x.png [--thresholds=-3,13,140,103,119,113] [--truth]

The window: left the raw frame; right the same frame with every pixel the current thresholds do NOT label dimmed
and the labeled pixels painted orange / blue, with the boxes today's detector draws from exactly that segmentation
(yellow = orange barrel, green = blue). Below: six sliders and the status lines.

The six numbers are the hs color model's: per color a hue range (OpenCV hue 0-179, both ends included) and a floor
on HSV saturation. Orange sits at the red wrap, so its hue sliders run from -30 to 60: -3 means 177. Everything
else is the adopted model's (pixels from row 50 down, brightness V >= 40, the tie rule). The picture is what
``pipeline.segment`` gives with those numbers; nothing is re-implemented here (``barrels.hslabel``).

Criterion: as much barrel painted as needed to detect it, as little else as possible.

Mouse:
    click / drag on a slider    set it (it becomes the selected slider)
Keys:
    1 .. 6         select a slider (orange hue low, hue high, S floor; blue hue low, hue high, S floor)
    - / =          selected slider one step down / up          [ / ]   five steps down / up
    b              the detector's boxes on / off
    t              your hand-drawn truth boxes on / off (thin white; only if the frame has a _boxes.json)
    m              painted pixels: flat orange / blue, or left in their own color (as `tm seg` shows them)
    r              reset to the adopted values (orange 3..13 S>=140, blue 103..119 S>=113)
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
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import detector as det, geometry as geo, hslabel as hl, io, pipeline as pl, splits as sp, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

WIN = "hs slider"
PAINTS = ("flat", "own")
# (class, key, label, slider low end, slider high end)
SLIDERS = (("orange", "h_lo", "orange hue low", -30, 60), ("orange", "h_hi", "orange hue high", -30, 60), ("orange", "s_lo", "orange S floor", 0, 255),
           ("blue", "h_lo", "blue hue low", 60, 150), ("blue", "h_hi", "blue hue high", 60, 150), ("blue", "s_lo", "blue S floor", 0, 255))
ROW_H = 26                        # one slider row
TRACK_X0, TRACK_RIGHT = 180, 130  # the track starts this far into its column and ends this far before the column's end
TOP_PAD = 18
PANEL_H = TOP_PAD + 3 * ROW_H + 5 * 20 + 2
FONT, FS = cv2.FONT_HERSHEY_SIMPLEX, 0.45
BG, FG, DIMTXT, HILITE = (32, 32, 32), (235, 235, 235), (150, 150, 150), (0, 255, 255)
HELP = "drag a slider, or 1-6 then - = ([ ] by 5)   b boxes   t truth   m paint   r adopted   c copy previous   u undo   w save   n/p next/prev   q quit"
STEPS = {"-": -1, "_": -1, "=": 1, "+": 1, "[": -5, "{": -5, "]": 5, "}": 5}


def track(i: int, w: int, h: int) -> tuple[int, int, int]:
    """(x0, x1, y) of slider i's track in the composite picture: orange in the left column, blue in the right."""
    col, row = divmod(i, 3)
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


class Session:
    """The tool's whole state and behavior without the window: ``render`` gives the picture, ``on_key`` and
    ``on_mouse`` change the state. A frame is opened only after ``hslabel.require_labelable`` passes."""

    def __init__(self, stems: list[str], splits: dict[str, list[str]], base: pl.Model, raw_dir: Path | str | None = None,
                 labels_dir: Path | str | None = None, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, scale: float = 1.0,
                 git: str = "unknown"):
        self.stems, self.splits, self.base, self.cam, self.scale, self.git = list(stems), splits, base, cam, scale, git
        self.raw_dir, self.labels_dir = Path(raw_dir or io.RAW_DIR), Path(labels_dir or io.LABELS_DIR)
        self.adopted = hl.thresholds_from_model(base)
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
        return self.thr != self.baseline

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
        if io.hs_path(stem, self.labels_dir).exists():
            try:
                meta = io.load_hs(stem, self.labels_dir, check_image=False)
                self.thr, self.note, self.has_label = hl.copy_thresholds(meta), meta.get("note", ""), True
                now = (self.base.cfg.short_hash(), self.base.cfg.v_min, self.base.cfg.horizon_row)
                if meta.get("image_sha1") and meta["image_sha1"] != self.sha:
                    self.msg = "the image changed since this label was saved: check it, then w"
                elif (meta["base_model"], meta["v_min"], meta["horizon_row"]) != now:
                    self.msg = f"this label was set against model {meta['base_model']} (now {now[0]}): check it, then w"
            except ValueError as e:
                self.msg = f"saved label ignored ({e}); starting from the adopted values"
        self.baseline = hl.copy_thresholds(self.thr)
        self.grab = self.pending = None
        self._seg = self._view = None

    def set_value(self, i: int, v: int) -> None:
        """Set slider i, kept inside its range and with hue low <= hue high."""
        name, key, _, lo, hi = SLIDERS[i]
        v = min(max(int(v), lo), hi)
        t = self.thr[name]
        if key == "h_lo":
            v = min(v, t["h_hi"])
        elif key == "h_hi":
            v = max(v, t["h_lo"])
        if t[key] != v:
            t[key] = v
            self._seg = self._view = None

    def set_thresholds(self, thr: dict) -> None:
        io.validate_hs_thresholds(thr)
        self.thr = hl.copy_thresholds(thr)
        self._seg = self._view = None

    def result(self) -> tuple[np.ndarray, list]:
        """(class mask, barrels) for the current thresholds: ``pipeline.segment`` with the model built from them,
        then ``detector.detect`` with ``DetConfig()`` and the project camera. Cached until a number changes."""
        if self._seg is None:
            mask, _ = pl.segment(self.frame, hl.model_from_thresholds(self.base, self.thr))
            self._seg = (mask, det.detect(mask, self.det_cfg, self.cam))
        return self._seg

    def save(self) -> Path:
        _, barrels = self.result()
        meta = hl.label_meta(self.stem, self.sha, self.thr, self.base, len(barrels), self.git, self.note)
        p = io.save_hs(self.stem, meta, self.labels_dir)
        self.baseline = hl.copy_thresholds(self.thr)
        self.has_label = True
        self.last_saved = (self.stem, hl.copy_thresholds(self.thr))
        self.msg = f"saved {p.name}: {hl.describe(self.thr)}, {len(barrels)} box(es)"
        print(self.msg)
        return p

    def copy_previous(self) -> None:
        """Take the thresholds saved for the previous frame in the list; failing that, the last ones saved in
        this session."""
        src = None
        if self.idx > 0:
            prev = self.stems[self.idx - 1]
            try:
                src = (prev, hl.copy_thresholds(io.load_hs(prev, self.labels_dir, check_image=False)))
            except (FileNotFoundError, ValueError):
                src = None
        if src is None and self.last_saved and self.last_saved[0] != self.stem:
            src = self.last_saved
        if src is None:
            self.msg = "nothing to copy: the previous frame has no saved thresholds"
            return
        self.set_thresholds(src[1])
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
        if ch in "123456":
            self.sel = int(ch) - 1
        elif ch in STEPS:
            name, key = SLIDERS[self.sel][:2]
            self.set_value(self.sel, self.thr[name][key] + STEPS[ch])
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
            self.msg = "reset to the adopted values (not saved)"
        elif ch == "c":
            self.copy_previous()
        elif ch == "u":
            self.set_thresholds(self.baseline)
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
        return [f"[{self.idx + 1}/{len(self.stems)}] {self.stem}   label: {state}   detector boxes={len(barrels)}{'' if self.show_boxes else ' (hidden)'}"
                f"   truth boxes={truth}   paint={PAINTS[self.paint]}",
                hl.describe(self.thr) + f"      fixed: rows >= {cfg.horizon_row}, V >= {cfg.v_min}, model {cfg.short_hash()}",
                scored, self.msg, HELP]

    def render(self) -> np.ndarray:
        if self._view is not None:
            return self._view
        mask, barrels = self.result()
        h, w = self.img.shape[:2]
        view = np.full((h + PANEL_H, 2 * w, 3), BG, np.uint8)
        view[:h, :w] = self.img
        view[:h, w:] = seg_picture(self.img, mask, barrels, self.truth, self.show_boxes, self.show_truth, PAINTS[self.paint])
        for i, (name, key, label, lo, hi) in enumerate(SLIDERS):
            x0, x1, yc = track(i, w, h)
            col = (i // 3) * w
            v = self.thr[name][key]
            on = i == self.sel
            cv2.putText(view, f"{i + 1} {label}", (col + 8, yc + 5), FONT, FS, HILITE if on else FG, 1, cv2.LINE_AA)
            cv2.line(view, (x0, yc), (x1, yc), (110, 110, 110), 2)
            ax = value_to_x(self.adopted[name][key], lo, hi, x0, x1)                     # a tick at the adopted value
            cv2.line(view, (ax, yc + 5), (ax, yc + 10), DIMTXT, 1)
            kx = value_to_x(v, lo, hi, x0, x1)
            cv2.rectangle(view, (kx - 3, yc - 8), (kx + 3, yc + 8), HILITE if on else (viz.ORANGE_BGR if name == "orange" else viz.BLUE_BGR), -1)
            text = f">= {v}" if key == "s_lo" else hl.hue_text(v)
            cv2.putText(view, text, (x1 + 14, yc + 5), FONT, FS, HILITE if on else FG, 1, cv2.LINE_AA)
        y = h + TOP_PAD + 3 * ROW_H + 8
        for j, line in enumerate(self.status()):
            color = HILITE if j == 3 else DIMTXT if j == 4 else FG
            cv2.putText(view, line, (8, y + j * 20), FONT, FS, color, 1, cv2.LINE_AA)
        if self.scale != 1:
            view = cv2.resize(view, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_NEAREST if self.scale > 1 else cv2.INTER_AREA)
        self._view = view
        return view


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
    args = ap.parse_args(argv)

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
    s = Session(stems, splits, hl.adopted_model(), args.raw, args.labels, scale=args.scale, git=hl.detector_git())
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
