#!/usr/bin/env python3
"""A look helper for a Claude session that proposes box labels (docs/DATA.md, "Box proposals"). No window.

    python barrels/tools/box_look.py <stem> --out /tmp/look.png                       # the whole frame, x2, grid every 40 px
    python barrels/tools/box_look.py <stem> --out /tmp/z.png --zoom 200,150,360,300 --grid 10
    python barrels/tools/box_look.py <stem> --out /tmp/look.png --sizes              # + expected barrel sizes per row (left panel)
    python barrels/tools/box_look.py <stem> --out /tmp/look.png --expect 310,262      # + the expected outline of a barrel whose
                                                                                     #   bottom-middle is at (310, 262)
    python barrels/tools/box_look.py <stem> --out /tmp/check.png --boxes /tmp/draft.json   # draw a draft proposal on top (checked)
    python barrels/tools/box_look.py <stem> --boxes /tmp/draft.json --save           # write data/labels/<stem>_boxes_proposed.json

Writes the raw frame (or a crop of it, enlarged with nearest-neighbour so single pixels stay visible) with a labelled
pixel grid in FRAME coordinates: grid lines every --grid px, the coordinate written in the top and left margins, so
a box edge can be read to a pixel or two. --sizes adds a panel on the left: at each grid row, a bar as wide as a
barrel standing with its bottom edge on that row, per the detector's camera model (geometry.AIM_4A8B6118_BOXFIT, as
box_tool's `g` key), labelled "w x h". --boxes FILE draws a draft proposal (the box label JSON schema: barrels with
color, bbox [x0, y0, x1, y1] half-open, flags, note): dashed, magenta = orange barrel, cyan = blue barrel, with the id;
the file is normalized and validated first (io.normalize_proposal), so a draft that would not save is reported here.
--save writes it as the frame's proposal file, with the image's sha1.

Proposals come from looking at the picture ONLY: never from our detector or the vendor's (they are scored against
these labels). Train frames and frames kept out of every split on purpose only; a test frame, or a frame not split
yet, is refused before its image is read (splits.look_refusal).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import geometry as geo, io, splits as sp  # noqa: E402

MARGIN_TOP, MARGIN_LEFT = 22, 40
GRID_BGR = (0, 255, 255)
TEXT_BGR = (230, 230, 230)
BOX_BGR = {"orange": (255, 0, 255), "blue": (255, 255, 0)}     # magenta / cyan: distinct from the barrels themselves
EXPECT_BGR = (0, 255, 0)


class Refused(Exception):
    pass


def require_lookable(stem: str, splits: dict[str, list[str]]) -> None:
    why = sp.look_refusal(stem, splits)
    if why:
        raise Refused(f"{stem}: {why}")


def parse_box(text: str) -> tuple[int, int, int, int]:
    v = [int(round(float(t))) for t in text.split(",")]
    if len(v) != 4:
        raise argparse.ArgumentTypeError(f"need x0,y0,x1,y1, got {text!r}")
    x0, y0, x1, y1 = v
    x0, x1 = sorted((max(0, x0), min(io.FRAME_W, x1))); y0, y1 = sorted((max(0, y0), min(io.FRAME_H, y1)))
    if x1 - x0 < 2 or y1 - y0 < 2:
        raise argparse.ArgumentTypeError(f"zoom box {text!r} is empty inside the 640x480 frame")
    return x0, y0, x1, y1


def parse_point(text: str) -> tuple[float, float]:
    v = [float(t) for t in text.split(",")]
    if len(v) != 2:
        raise argparse.ArgumentTypeError(f"need x,y, got {text!r}")
    return v[0], v[1]


def _dashed_rect(img, p0, p1, col, thick=1, dash=6):
    (x0, y0), (x1, y1) = p0, p1
    for x in range(x0, x1, dash * 2):
        cv2.line(img, (x, y0), (min(x + dash, x1), y0), col, thick); cv2.line(img, (x, y1), (min(x + dash, x1), y1), col, thick)
    for y in range(y0, y1, dash * 2):
        cv2.line(img, (x0, y), (x0, min(y + dash, y1)), col, thick); cv2.line(img, (x1, y), (x1, min(y + dash, y1)), col, thick)


def _text(img, s, org, scale=0.4, col=TEXT_BGR):
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, scale, col, 1, cv2.LINE_AA)


def auto_scale(crop: tuple[int, int, int, int]) -> int:
    """Enlargement so the crop is about 1280 px wide (whole frame: 2), at most 12."""
    w = crop[2] - crop[0]
    return int(max(1, min(12, 1280 // max(w, 1))))


def render(img: np.ndarray, crop=None, scale: int | None = None, grid: int = 40, cam: geo.CameraModel | None = None,
           sizes: bool = False, boxes: list[dict] | None = None, expects=()) -> np.ndarray:
    """The look picture: the crop of ``img`` enlarged ``scale`` times, a grid in frame pixels every ``grid`` px with
    coordinates in the margins, optionally the size panel (left), the draft boxes and expected outlines."""
    cam = cam or geo.AIM_4A8B6118_BOXFIT
    H, W = img.shape[:2]
    x0, y0, x1, y1 = crop or (0, 0, W, H)
    s = int(scale or auto_scale((x0, y0, x1, y1)))
    view = cv2.resize(img[y0:y1, x0:x1], None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)

    def to_view(x, y):                       # frame pixel boundary -> view pixel (before margins)
        return int(round((x - x0) * s)), int(round((y - y0) * s))

    # grid: thin, half-transparent, every `grid` frame px (lines sit on pixel boundaries)
    overlay = view.copy()
    gx = [g for g in range((x0 // grid) * grid, x1 + 1, grid) if x0 <= g <= x1]
    gy = [g for g in range((y0 // grid) * grid, y1 + 1, grid) if y0 <= g <= y1]
    for g in gx:
        vx = min(to_view(g, y0)[0], view.shape[1] - 1); cv2.line(overlay, (vx, 0), (vx, view.shape[0] - 1), GRID_BGR, 1)
    for g in gy:
        vy = min(to_view(x0, g)[1], view.shape[0] - 1); cv2.line(overlay, (0, vy), (view.shape[1] - 1, vy), GRID_BGR, 1)
    view = cv2.addWeighted(overlay, 0.45, view, 0.55, 0)

    for e in expects:                        # expected outline of a barrel whose bottom-middle is at (ex, ey)
        ex, ey = e
        bw, bh = cam.expected_barrel_width_px(bottom_row=ey), cam.expected_barrel_height_px(bottom_row=ey)
        if np.isfinite(bw) and np.isfinite(bh) and bw > 0:
            p0, p1 = to_view(ex - bw / 2, ey - bh), to_view(ex + bw / 2, ey)
            _dashed_rect(view, p0, (p1[0] - 1, p1[1] - 1), EXPECT_BGR, 1, 4)
            _text(view, f"exp {bw:.0f}x{bh:.0f}", (p0[0] + 2, p1[1] + 14), 0.4, EXPECT_BGR)

    for b in boxes or ():
        bx0, by0, bx1, by1 = b["bbox"]
        col = BOX_BGR.get(b.get("color"), (255, 255, 255))
        p0, p1 = to_view(bx0, by0), to_view(bx1, by1)
        _dashed_rect(view, p0, (p1[0] - 1, p1[1] - 1), col, 2 if s >= 4 else 1, 5)
        tag = f"{b.get('id', '?')}{(b.get('color') or '?')[0]} {bx0},{by0},{bx1},{by1}" + "".join(f" {f[:4]}" for f in b.get("flags", ()))
        ty = p0[1] - 4 if p0[1] > 14 else p1[1] + 14
        _text(view, tag, (max(p0[0], 2), ty), 0.45, col)

    # margins with the frame coordinates
    out = cv2.copyMakeBorder(view, MARGIN_TOP, 0, MARGIN_LEFT, 0, cv2.BORDER_CONSTANT, value=(40, 40, 40))
    step_x = max(1, int(np.ceil(36 / (grid * s))))       # skip labels that would overlap
    for i, g in enumerate(gx):
        if i % step_x == 0:
            _text(out, str(g), (MARGIN_LEFT + to_view(g, y0)[0] - 8, 15), 0.38)
    step_y = max(1, int(np.ceil(14 / (grid * s))))
    for i, g in enumerate(gy):
        if i % step_y == 0:
            _text(out, str(g), (2, MARGIN_TOP + to_view(x0, g)[1] + 4), 0.38)

    if sizes:
        rows = [(g, cam.expected_barrel_width_px(bottom_row=g), cam.expected_barrel_height_px(bottom_row=g)) for g in gy]
        rows = [(g, bw, bh) for g, bw, bh in rows if np.isfinite(bw) and bw >= 1]
        bar_max = int(min(max((bw * s for _, bw, _ in rows), default=0), 700))
        pw = bar_max + 90
        panel = np.full((out.shape[0], pw, 3), 25, np.uint8)
        _text(panel, "expected barrel (bottom on row)", (4, 15), 0.38)
        for g, bw, bh in rows:
            vy = MARGIN_TOP + to_view(x0, g)[1]
            L = int(min(bw * s, bar_max))
            cv2.line(panel, (pw - 2 - L, min(vy, panel.shape[0] - 1)), (pw - 2, min(vy, panel.shape[0] - 1)), EXPECT_BGR, 2)
            _text(panel, f"{bw:.0f}x{bh:.0f}", (2, max(vy - 3, 28)), 0.38, EXPECT_BGR)
        out = np.hstack([panel, out])
    return out


def load_draft(path: Path, stem: str) -> dict:
    """A draft proposal file, normalized and validated (raises ValueError with the reason)."""
    try:
        meta = json.loads(Path(path).read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: not JSON ({e})") from None
    return io.normalize_proposal(meta, stem)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stem", help="frame stem (or a path to it in data/raw)")
    ap.add_argument("--out", type=Path, default=None, help="PNG to write")
    ap.add_argument("--zoom", type=parse_box, default=None, metavar="x0,y0,x1,y1", help="crop (frame px) to enlarge")
    ap.add_argument("--grid", type=int, default=None, help="grid spacing in frame px (default 40, or 10 when zoomed)")
    ap.add_argument("--scale", type=int, default=None, help="enlargement (default: about 1280 px wide)")
    ap.add_argument("--sizes", action="store_true", help="panel with the expected barrel size per grid row")
    ap.add_argument("--expect", type=parse_point, action="append", default=[], metavar="x,y",
                    help="expected outline of a barrel whose bottom-middle is at x,y (repeatable)")
    ap.add_argument("--boxes", type=Path, default=None, help="a draft proposal JSON to draw (checked first)")
    ap.add_argument("--save", action="store_true", help="with --boxes: write it as data/labels/<stem>_boxes_proposed.json")
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR)
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--splits", type=Path, default=None, help="splits file (default data/splits.json)")
    args = ap.parse_args(argv)
    stem = Path(args.stem).stem
    try:
        require_lookable(stem, sp.load_splits(args.splits))       # before the image is read
    except Refused as e:
        print(f"REFUSED {e}"); return 2
    if args.out is None and not args.save:
        ap.error("give --out and/or --boxes ... --save")
    if args.save and args.boxes is None:
        ap.error("--save needs --boxes FILE")
    path = io.find_image(stem, args.raw)
    if path is None:
        print(f"no image for {stem} in {args.raw}"); return 1
    draft = None
    if args.boxes is not None:
        try:
            draft = load_draft(args.boxes, stem)
        except (ValueError, KeyError, TypeError) as e:
            print(f"draft {args.boxes} is not a valid proposal: {e}"); return 1
    if args.out is not None:
        img = io.load_image(path)
        grid = args.grid or (10 if args.zoom else 40)
        pic = render(img, args.zoom, args.scale, grid, sizes=args.sizes, boxes=draft["barrels"] if draft else None, expects=args.expect)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(args.out), pic):
            raise OSError(f"could not write {args.out}")
        print(f"wrote {args.out} ({pic.shape[1]}x{pic.shape[0]})")
    if draft is not None:
        for b in draft["barrels"]:
            print(f"  {b['id']} {b['color']:6s} {b['bbox']}  {' '.join(b['flags'])}  {b['note']}")
        if draft["negative"]:
            print("  (negative: no barrels)")
    if args.save:
        draft["image_sha1"] = io.file_sha1(path)
        p = io.save_proposal(stem, draft, args.labels)
        print(f"saved {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
