#!/usr/bin/env python3
"""Draw the v2 ground truth: one box per barrel — the full barrel, through occluders, clipped to the frame
(docs/DATA.md, "Box labels" + "Box labeling rules").

    python barrels/tools/box_tool.py [--filter window] [--unlabeled | --proposed] [--scale 2]
    python barrels/tools/box_tool.py --from-inst      # no GUI: a provisional _boxes.json from every _inst.json that has none

Frames that already have a <stem>_boxes.json open with it; frames without one but with Claude's proposal
(<stem>_boxes_proposed.json, docs/DATA.md "Box proposals") open with the proposed boxes DASHED and Claude's note
for the selected box at the bottom; frames with only a <stem>_inst.json open with the converted instances (boxes
around the visible pixels — stretch occluded ones to the full barrel); other frames open empty. A proposal is never
taken without a key from you: on an untouched proposal n / p / q move on WITHOUT saving; `a` accepts it.

Mouse:
    drag on empty space     draw a new box (same color as the last box you drew; o/b changes it)
    click inside a box      select it (the smallest box under the cursor)
    drag an edge / corner   move that edge / corner of the selected box (grab within 6 px)
Keys:
    o / b          color orange / blue (selected box)
    x / h / e / s  toggle occluded / held / bottom_estimated / no_stripe (selected box)
                   (truncated is set automatically: the box touches a frame edge)
    c              toggle clean — true when nothing orange/blue is in the frame besides barrels (default true)
    d              delete the selected box        u   undo
    g              size guide on/off: the barrel width/height the geometry expects for a barrel whose BOTTOM EDGE is at the
                   cursor row (so point at where the barrel meets the table); camera = the detector's (--cam)
    v              cycle view: boxes / raw
    w              save        n / p   save + next / previous        q / Esc   save + quit
  on a frame opened from Claude's proposal:
    a              accept: save the boxes as they stand now (each box you did not touch is taken as proposed)
    r              reject the whole proposal: delete every proposed box (u undoes); then draw your own
    (fix single boxes with the usual mouse and keys; a box you change turns solid)

Saving marks the frame reviewed. Writes data/labels/<stem>_boxes.json. A label started from a proposal records
source "claude_proposal" (or "manual" when no proposed box survived), per barrel "moved" (false = taken exactly as
proposed; true = an edge moved, or a box you drew) and "proposed_bbox" / "proposed_color" (where the proposal had it),
and a "proposal" summary (proposed / kept / moved / deleted / added).
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import geometry as geo, io, splits as sp, viz  # noqa: E402

WIN = "box tool"
VIEWS = ("boxes", "raw")
FLAG_KEYS = {"x": "occluded", "h": "held", "e": "bottom_estimated", "s": "no_stripe"}
GRAB_PX = 6          # image pixels within which an edge/corner is grabbed
MIN_BOX_PX = 4       # smaller drags count as clicks
EDGE_SNAP_PX = 2     # a cursor this close to the right or bottom frame edge snaps onto it
SHAPE = (io.FRAME_H, io.FRAME_W)


def _flags_with_truncated(bbox, flags: set[str]) -> list[str]:
    f = set(flags) - {"truncated"}
    if io.touches_frame(bbox, SHAPE):
        f.add("truncated")
    return [x for x in io.BOX_FLAGS if x in f]


def _clip(bbox) -> list[int]:
    x0, y0, x1, y1 = bbox
    x0, x1 = sorted((int(round(x0)), int(round(x1)))); y0, y1 = sorted((int(round(y0)), int(round(y1))))
    return [max(0, x0), max(0, y0), min(SHAPE[1], x1), min(SHAPE[0], y1)]


def proposal_summary(meta: dict) -> dict:
    """What became of the proposal in a label started from one (box_tool.py): counts, recomputed at every save."""
    n = int(meta.get("proposal", {}).get("proposed", 0))
    from_p = [b for b in meta["barrels"] if b.get("proposed_bbox") is not None]
    moved = sum(1 for b in from_p if b.get("moved"))
    return {"by": io.PROPOSAL_BY, "proposed": n, "kept": len(from_p) - moved, "moved": moved,
            "deleted": n - len(from_p), "added": len(meta["barrels"]) - len(from_p),
            "note": meta.get("proposal", {}).get("note", "")}


def finalize_proposal_fields(meta: dict) -> None:
    """Before saving a label that started from a proposal: per barrel ``moved`` (bbox differs from ``proposed_bbox``,
    or a box the labeler drew), the ``proposal`` summary, and ``source`` = claude_proposal unless no proposed box
    survived a non-empty proposal (then manual)."""
    if "proposal" not in meta:
        return
    for b in meta["barrels"]:
        pb = b.get("proposed_bbox")
        b["moved"] = pb is None or [int(v) for v in b["bbox"]] != [int(v) for v in pb]
    summ = proposal_summary(meta)
    meta["proposal"] = summ
    survived = summ["kept"] + summ["moved"] > 0
    meta["source"] = io.PROPOSAL_SOURCE if survived or (summ["proposed"] == 0 and not meta["barrels"]) else "manual"


def meta_from_proposal(prop: dict, sha: str) -> dict:
    """The editable label a proposal opens as (unreviewed until saved)."""
    barrels = [{"id": b["id"], "color": b["color"], "bbox": list(b["bbox"]), "flags": list(b.get("flags", ())), "note": "",
                "proposed_bbox": list(b["bbox"]), "proposed_color": b["color"]} for b in prop["barrels"]]
    return {"version": io.BOXES_JSON_VERSION, "stem": prop.get("stem", ""), "image_sha1": sha, "reviewed": False,
            "negative": not barrels, "clean": bool(prop.get("clean", True)), "source": io.PROPOSAL_SOURCE,
            "proposal": {"by": io.PROPOSAL_BY, "proposed": len(barrels), "note": prop.get("note", "")}, "barrels": barrels}


class Session:
    def __init__(self, images: list[Path], labels_dir: Path, scale: float, cam: geo.CameraModel,
                 splits: dict[str, list[str]] | None = None):
        self.images, self.labels_dir, self.scale, self.cam = images, labels_dir, scale, cam
        self.splits = splits if splits is not None else sp.load_splits()
        self.idx, self.view, self.cursor, self.guide = 0, 0, (-1, -1), False
        self.last_color = "orange"
        self.undo: list[dict] = []
        self.drag: dict | None = None
        self.load(0)

    @property
    def path(self) -> Path:
        return self.images[self.idx]

    # ---------------------------------------------------------------- state
    def load(self, i: int) -> None:
        self.idx = i % len(self.images)
        self.img = io.load_image(self.path)
        self.sha = io.file_sha1(self.path)
        self.selection: int | None = None
        self.undo.clear(); self.drag = None
        self.dirty = False
        self.pending_proposal = False          # a proposal on screen that you have neither accepted nor edited
        self.pnotes: dict[tuple, str] = {}     # proposed bbox -> Claude's note for that box
        self.frame_note = ""
        bp = io.boxes_path(self.path, self.labels_dir)
        if bp.exists():
            self.meta = io.load_boxes(self.path, self.labels_dir, check_image=False)
            if self.meta.get("image_sha1") and self.meta["image_sha1"] != self.sha:
                print(f"{bp.name}: the image changed since these boxes were drawn — check them")
            self._load_notes()
            return
        if io.proposal_path(self.path, self.labels_dir).exists():
            why = sp.look_refusal(self.path.stem, self.splits)
            if why:
                print(f"{self.path.stem}: proposal ignored ({why})")
            else:
                try:
                    prop = io.load_proposal(self.path, self.labels_dir, check_image=False)
                except ValueError as e:
                    print(f"{self.path.stem}: proposal ignored ({e})")
                else:
                    if prop.get("image_sha1") and prop["image_sha1"] != self.sha:
                        print(f"{self.path.stem}: the image changed since the proposal was made — check it")
                    self.meta = meta_from_proposal(prop, self.sha)
                    self.pending_proposal = True
                    self._load_notes(prop)
                    print(f"{self.path.stem}: Claude's proposal, {len(self.barrels)} box(es) — a accepts, r rejects all")
                    return
        if io.inst_json_path(self.path, self.labels_dir).exists():
            inst, imeta = io.load_instances(self.path, self.labels_dir, check_mask=False)
            self.meta = io.boxes_from_instances(imeta, self.sha)
            self.dirty = True
            return
        self.meta = {"version": io.BOXES_JSON_VERSION, "stem": self.path.stem, "image_sha1": self.sha, "reviewed": False,
                     "negative": True, "clean": True, "source": "manual", "barrels": []}

    def _load_notes(self, prop: dict | None = None) -> None:
        """Claude's notes, by proposed box, to show while checking (also after the label was saved)."""
        if prop is None:
            if "proposal" not in self.meta or sp.look_refusal(self.path.stem, self.splits):
                return
            try:
                prop = io.load_proposal(self.path, self.labels_dir, check_image=False)
            except (FileNotFoundError, ValueError):
                return
        self.pnotes = {tuple(b["bbox"]): b.get("note", "") for b in prop["barrels"]}
        self.frame_note = prop.get("note", "")

    def note_of(self, b: dict | None) -> str:
        if not b or b.get("proposed_bbox") is None:
            return ""
        return self.pnotes.get(tuple(b["proposed_bbox"]), "")

    @property
    def barrels(self) -> list[dict]:
        return self.meta["barrels"]

    @property
    def from_proposal(self) -> bool:
        return "proposal" in self.meta

    def push(self) -> None:
        self.undo.append(copy.deepcopy(self.meta))
        del self.undo[:-50]
        self.dirty = True
        self.pending_proposal = False          # an edit means you are working on the frame

    def accept(self) -> None:
        """`a`: take the boxes as they stand and save (only meaningful on a proposal; elsewhere the same as w)."""
        self.pending_proposal = False
        self.save()

    def reject_proposal(self) -> None:
        """`r`: delete every box that came from the proposal (undo restores them)."""
        if not any(b.get("proposed_bbox") is not None for b in self.barrels):
            return
        self.push()
        self.meta["barrels"] = [b for b in self.barrels if b.get("proposed_bbox") is None]
        self.meta["negative"] = not self.barrels
        self.selection = None

    def leave_ok(self) -> bool:
        """n / p / q save first, except on an untouched proposal: that is never taken without a key."""
        if self.pending_proposal:
            print(f"{self.path.stem}: proposal NOT saved (press a to accept it, or edit it)")
            return False
        return True

    def pop(self) -> None:
        if self.undo:
            self.meta = self.undo.pop(); self.selection = None; self.dirty = True

    def save(self) -> None:
        for b in self.barrels:
            b["bbox"] = _clip(b["bbox"]); b["flags"] = _flags_with_truncated(b["bbox"], set(b.get("flags", ())))
        self.meta["image_sha1"] = self.sha; self.meta["reviewed"] = True
        if self.meta.get("source") == "from_inst":
            self.meta["source"] = "from_inst+manual"
        finalize_proposal_fields(self.meta)
        self.pending_proposal = False
        p = io.save_boxes(self.path, self.meta, self.labels_dir)
        self.meta = io.load_boxes(self.path, self.labels_dir, check_image=False)      # renumbered ids
        self.selection = None; self.dirty = False
        n = len(self.barrels)
        if self.from_proposal:
            pr = self.meta["proposal"]
            print(f"  proposal: {pr['kept']} kept, {pr['moved']} moved, {pr['deleted']} deleted, {pr['added']} added; source={self.meta['source']}")
        print(f"saved {p.name}: {n} barrel(s)" + ("" if self.meta["clean"] else ", clean=false") + (" (negative)" if n == 0 else ""))

    # ---------------------------------------------------------------- edits
    def selected(self) -> dict | None:
        if self.selection is None:
            return None
        return next((b for b in self.barrels if b["id"] == self.selection), None)

    def box_at(self, x: int, y: int) -> dict | None:
        inside = [b for b in self.barrels if b["bbox"][0] <= x < b["bbox"][2] and b["bbox"][1] <= y < b["bbox"][3]]
        return min(inside, key=lambda b: (b["bbox"][2] - b["bbox"][0]) * (b["bbox"][3] - b["bbox"][1]), default=None)

    def grab(self, b: dict, x: int, y: int) -> tuple[bool, bool, bool, bool] | None:
        """Which of (left, top, right, bottom) edges of box b are within GRAB_PX of (x, y); None if none."""
        x0, y0, x1, y1 = b["bbox"]
        near_x = x0 - GRAB_PX <= x <= x1 + GRAB_PX; near_y = y0 - GRAB_PX <= y <= y1 + GRAB_PX
        left = abs(x - x0) <= GRAB_PX and near_y; right = abs(x - x1) <= GRAB_PX and near_y
        top = abs(y - y0) <= GRAB_PX and near_x; bottom = abs(y - y1) <= GRAB_PX and near_x
        if left and right:
            left, right = (True, False) if abs(x - x0) <= abs(x - x1) else (False, True)
        if top and bottom:
            top, bottom = (True, False) if abs(y - y0) <= abs(y - y1) else (False, True)
        return (left, top, right, bottom) if (left or top or right or bottom) else None

    def add_box(self, bbox) -> None:
        bbox = _clip(bbox)
        if bbox[2] - bbox[0] < MIN_BOX_PX or bbox[3] - bbox[1] < MIN_BOX_PX:
            return
        self.push()
        nid = max((b["id"] for b in self.barrels), default=0) + 1
        self.barrels.append({"id": nid, "color": self.last_color, "bbox": bbox, "flags": _flags_with_truncated(bbox, set()), "note": ""})
        self.meta["negative"] = False
        self.selection = nid

    def delete_selected(self) -> None:
        b = self.selected()
        if b:
            self.push(); self.barrels.remove(b); self.selection = None
            self.meta["negative"] = not self.barrels

    def set_color(self, color: str) -> None:
        b = self.selected()
        self.last_color = color
        if b and b["color"] != color:
            self.push(); b["color"] = color

    def toggle_flag(self, flag: str) -> None:
        b = self.selected()
        if b:
            self.push()
            f = set(b.get("flags", ()))
            f ^= {flag}
            b["flags"] = _flags_with_truncated(b["bbox"], f)

    # ---------------------------------------------------------------- mouse
    def on_mouse(self, event, sx, sy, flags, _):
        x, y = int(sx / self.scale), int(sy / self.scale)
        x = min(max(x, 0), SHAPE[1]); y = min(max(y, 0), SHAPE[0])
        # the window never reports the last column/row + 1, so the right and bottom frame edges (640, 480) were
        # unreachable and a cut barrel never got `truncated`: within EDGE_SNAP_PX of them counts as on them
        if x >= SHAPE[1] - EDGE_SNAP_PX:
            x = SHAPE[1]
        if y >= SHAPE[0] - EDGE_SNAP_PX:
            y = SHAPE[0]
        self.cursor = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            b = self.selected()
            g = self.grab(b, x, y) if b else None
            if b and g:
                pending = self.pending_proposal
                self.push()
                self.drag = {"kind": "edge", "id": b["id"], "edges": g, "orig": list(b["bbox"]), "pending": pending}
            else:
                hit = self.box_at(x, y)
                if hit is not None:
                    self.selection = hit["id"]; self.drag = {"kind": "select", "id": hit["id"], "start": (x, y)}
                else:
                    self.drag = {"kind": "new", "start": (x, y), "bbox": [x, y, x, y]}
        elif event == cv2.EVENT_MOUSEMOVE and self.drag:
            if self.drag["kind"] == "new":
                sx0, sy0 = self.drag["start"]; self.drag["bbox"] = [sx0, sy0, x, y]
            elif self.drag["kind"] == "edge":
                b = next(bb for bb in self.barrels if bb["id"] == self.drag["id"])
                left, top, right, bottom = self.drag["edges"]
                x0, y0, x1, y1 = b["bbox"]
                if left:
                    x0 = min(x, x1 - 1)
                if right:
                    x1 = max(x, x0 + 1)
                if top:
                    y0 = min(y, y1 - 1)
                if bottom:
                    y1 = max(y, y0 + 1)
                b["bbox"] = _clip([x0, y0, x1, y1]); b["flags"] = _flags_with_truncated(b["bbox"], set(b["flags"]))
        elif event == cv2.EVENT_LBUTTONUP and self.drag:
            d, self.drag = self.drag, None
            if d["kind"] == "new":
                sx0, sy0 = d["start"]
                if abs(x - sx0) < MIN_BOX_PX and abs(y - sy0) < MIN_BOX_PX:
                    self.selection = None                   # a click on empty space deselects
                else:
                    self.add_box([sx0, sy0, x, y])
            elif d["kind"] == "edge":
                b = next(bb for bb in self.barrels if bb["id"] == d["id"])
                if b["bbox"] == d["orig"]:
                    self.undo.pop()                         # nothing moved
                    self.pending_proposal = d.get("pending", False)

    # ---------------------------------------------------------------- render
    def render(self) -> np.ndarray:
        view = self.img.copy()
        if VIEWS[self.view] == "boxes":
            for b in self.barrels:
                x0, y0, x1, y1 = b["bbox"]
                col = viz.ORANGE_BGR if b["color"] == "orange" else viz.BLUE_BGR
                sel = b["id"] == self.selection
                if b.get("proposed_bbox") is not None and list(b["bbox"]) == list(b["proposed_bbox"]):
                    # a box as Claude proposed it: dashed until you change it
                    for x in range(x0, x1 - 1, 8):
                        cv2.line(view, (x, y0), (min(x + 4, x1 - 1), y0), col, 2 if sel else 1)
                        cv2.line(view, (x, y1 - 1), (min(x + 4, x1 - 1), y1 - 1), col, 2 if sel else 1)
                    for y in range(y0, y1 - 1, 8):
                        cv2.line(view, (x0, y), (x0, min(y + 4, y1 - 1)), col, 2 if sel else 1)
                        cv2.line(view, (x1 - 1, y), (x1 - 1, min(y + 4, y1 - 1)), col, 2 if sel else 1)
                else:
                    cv2.rectangle(view, (x0, y0), (x1 - 1, y1 - 1), col, 2 if sel else 1)
                if sel:
                    for px, py in ((x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)):
                        cv2.rectangle(view, (px - 2, py - 2), (px + 2, py + 2), (255, 255, 255), -1)
                label = f"{b['id']} {b['color'][0]}" + "".join(f" {f[:4]}" for f in b.get("flags", ()))
                if b.get("proposed_bbox") is not None:
                    label += " (proposed)" if list(b["bbox"]) == list(b["proposed_bbox"]) else " (moved)"
                ty = y0 - 4 if y0 > 14 else y1 + 12
                cv2.putText(view, label, (x0, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)
                cv2.putText(view, label, (x0, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            if self.drag and self.drag["kind"] == "new":
                x0, y0, x1, y1 = _clip(self.drag["bbox"])
                if x1 > x0 and y1 > y0:
                    cv2.rectangle(view, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
            if self.guide and 0 <= self.cursor[1] < SHAPE[0]:
                cx, cy = self.cursor
                W = self.cam.expected_barrel_width_px(bottom_row=cy); H = self.cam.expected_barrel_height_px(bottom_row=cy)
                if np.isfinite(W) and np.isfinite(H) and W > 0:
                    gx0, gx1, gy0 = int(cx - W / 2), int(cx + W / 2), int(cy - H)
                    for x in range(gx0, gx1, 6):
                        cv2.line(view, (x, gy0), (min(x + 3, gx1), gy0), (0, 255, 255), 1); cv2.line(view, (x, cy - 1), (min(x + 3, gx1), cy - 1), (0, 255, 255), 1)
                    for y in range(gy0, cy, 6):
                        cv2.line(view, (gx0, y), (gx0, min(y + 3, cy - 1)), (0, 255, 255), 1); cv2.line(view, (gx1, y), (gx1, min(y + 3, cy - 1)), (0, 255, 255), 1)
        if self.scale != 1:
            view = cv2.resize(view, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_NEAREST)
        n = len(self.barrels)
        hud = (f"[{self.idx + 1}/{len(self.images)}] {self.path.name}  boxes={n}" + ("  NEGATIVE" if n == 0 else "")
               + ("" if self.meta.get("clean", True) else "  clean=FALSE") + ("" if self.meta.get("reviewed") else "  [unreviewed]")
               + ("  *" if self.dirty else "") + f"  src={self.meta.get('source', 'manual')}  view={VIEWS[self.view]}" + ("  guide" if self.guide else ""))
        cv2.putText(view, hud, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        cv2.putText(view, hud, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        if self.from_proposal:
            top = ("CLAUDE'S PROPOSAL (dashed = as proposed): a accept, r reject all, or fix boxes" if self.pending_proposal
                   else "from Claude's proposal (dashed = as proposed)")
            bottom = []
            if self.frame_note:
                bottom.append(f"frame: {self.frame_note}")
            note = self.note_of(self.selected())
            if note:
                bottom.append(f"box {self.selection}: {note}")
            wrap = max(40, int(view.shape[1] / 8.5))          # characters per line at this font size
            chunks = [ln[j:j + wrap] for ln in bottom for j in range(0, len(ln), wrap)][-6:]
            placed = [(top, 40)] + [(c, view.shape[0] - 10 - 18 * (len(chunks) - 1 - i)) for i, c in enumerate(chunks)]
            for text, y in placed:
                cv2.putText(view, text, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 3)
                cv2.putText(view, text, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        return view


def convert_from_inst(images: list[Path], labels_dir: Path) -> int:
    """Write a provisional _boxes.json for every image that has an _inst.json and no _boxes.json."""
    n = 0
    for p in images:
        if io.boxes_path(p, labels_dir).exists() or not io.inst_json_path(p, labels_dir).exists():
            continue
        inst, imeta = io.load_instances(p, labels_dir, check_mask=False)
        meta = io.boxes_from_instances(imeta, io.file_sha1(p))
        io.save_boxes(p, meta, labels_dir)
        n += 1
        print(f"{p.stem}: {len(meta['barrels'])} box(es) from instances" + (" (negative)" if not meta["barrels"] else ""))
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR)
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--filter", default="", help="only images whose name contains this")
    ap.add_argument("--unlabeled", action="store_true", help="only images without a _boxes.json")
    ap.add_argument("--proposed", action="store_true", help="only images without a _boxes.json that have Claude's proposal")
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--cam", choices=("boxfit", "4a8b", "nominal"), default="boxfit",
                    help="camera for the size guide (default boxfit = the detector's camera since 2026-11-03; 4a8b = the October preset, ~20 px low)")
    ap.add_argument("--from-inst", action="store_true", help="no GUI: convert _inst.json files to provisional _boxes.json")
    args = ap.parse_args(argv)
    images = [p for p in io.list_images(args.raw) if args.filter in p.name]
    if args.from_inst:
        n = convert_from_inst(images, args.labels)
        print(f"wrote {n} provisional box file(s) (reviewed=false) to {args.labels}")
        return 0
    if args.unlabeled:
        images = [p for p in images if not io.boxes_path(p, args.labels).exists()]
    if args.proposed:
        images = [p for p in images if not io.boxes_path(p, args.labels).exists() and io.proposal_path(p, args.labels).exists()]
    if not images:
        print("no images match"); return 1
    cams = {"boxfit": geo.AIM_4A8B6118_BOXFIT, "4a8b": geo.AIM_4A8B6118, "nominal": geo.NOMINAL}
    s = Session(images, args.labels, args.scale, cams[args.cam])
    cv2.namedWindow(WIN, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WIN, s.on_mouse)
    print(__doc__)
    while True:
        cv2.imshow(WIN, s.render())
        k = cv2.waitKey(20) & 0xFF
        if k == 255:
            continue
        ch = chr(k)
        if ch in ("o", "b"):
            s.set_color("orange" if ch == "o" else "blue")
        elif ch in FLAG_KEYS:
            s.toggle_flag(FLAG_KEYS[ch])
        elif ch == "c":
            s.push(); s.meta["clean"] = not s.meta.get("clean", True)
        elif ch == "d":
            s.delete_selected()
        elif ch == "u":
            s.pop()
        elif ch == "g":
            s.guide = not s.guide
        elif ch == "v":
            s.view = (s.view + 1) % len(VIEWS)
        elif ch == "w":
            s.save()
        elif ch == "a":
            s.accept()
        elif ch == "r":
            s.reject_proposal()
        elif ch in ("n", "p"):
            if s.leave_ok():
                s.save()
            s.load(s.idx + (1 if ch == "n" else -1))
        elif ch == "q" or k == 27:
            if s.leave_ok():
                s.save()
            break
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    sys.exit(main())
