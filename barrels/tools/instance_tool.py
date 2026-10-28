#!/usr/bin/env python3
"""Per-barrel instance labels: review the automatic split of each class mask, fix it, save.

    python barrels/tools/instance_tool.py [--filter touch] [--cam 4a8b|nominal] [--scale 2]

Every frame with a <stem>_mask.png is auto-split into barrels (barrels.instances). You fix the
mistakes and press n. Nothing here ever changes a _mask.png.

Mouse:
    left click          select the instance under the cursor (shift+click adds to the selection)
    right click         drop a seed point (for w)
Keys:
    w                   re-split the instance(s) under the seeds, one instance per seed (needs >= 2 seeds)
    m                   merge the selected instances        d   delete the selected instances
    o / b               set the selected instances' color to orange / blue
    t / x / z           toggle flag truncated / occluded / top_only on the selection
    c                   clear seeds + selection
    a                   re-run the auto-split (discards edits on this frame)
    u                   undo
    v                   cycle view: instances+boxes / boxes only / class mask / raw
    n / p               save + next / previous        s   save        q / Esc   save + quit

Overlay: per-instance tint, box in the class color, a tick at the bottom-mid point, a bar as long as
the expected barrel width at that row (one bar = one barrel wide), id/color/flags text, and
'hint: occluded' where the auto-split suspects a partly hidden barrel. HUD shows STALE when the class
mask changed since the instances were saved (the tool then re-splits and replays your edits).

Writes <stem>_inst.png + <stem>_inst.json to the labels folder (docs/DATA.md).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import geometry as geo, instances as ins, io, viz  # noqa: E402

WIN = "instance tool"
VIEWS = ("instances+boxes", "boxes", "class mask", "raw")
FLAG_KEYS = {"t": "truncated", "x": "occluded", "z": "top_only"}
CAMS = {"nominal": geo.NOMINAL, "4a8b": geo.AIM_4A8B6118}


def palette(i: int) -> tuple[int, int, int]:
    rng = np.random.default_rng(i * 7919)
    return tuple(int(x) for x in rng.integers(80, 255, 3))


class Session:
    def __init__(self, images: list[Path], labels_dir: Path, scale: float, cam: geo.CameraModel, cfg: ins.SplitConfig):
        self.images, self.labels_dir, self.scale, self.cam, self.cfg = images, labels_dir, scale, cam, cfg
        self.idx, self.view, self.cursor = 0, 0, (-1, -1)
        self.undo: list[tuple] = []
        self.load(0)

    @property
    def path(self) -> Path:
        return self.images[self.idx]

    # ---------------------------------------------------------------- state
    def load(self, i: int) -> None:
        self.idx = i % len(self.images)
        self.img = io.load_image(self.path)
        self.mask = io.load_mask(io.mask_path(self.path, self.labels_dir))
        self.mask_sha = io.file_sha1(io.mask_path(self.path, self.labels_dir))
        self.selection: set[int] = set(); self.seeds: list[tuple[int, int]] = []; self.undo.clear()
        self.edits: list[dict] = []; self.overrides: dict[int, dict] = {}; self.stale = False; self.failed: list[dict] = []
        js = io.inst_json_path(self.path, self.labels_dir)
        if js.exists():
            try:
                self.inst, meta = io.load_instances(self.path, self.labels_dir, check_mask=False)
                self.edits = list(meta.get("edits", []))
                self.seed_kind = {b["id"]: (b.get("seed", "manual"), None) for b in meta.get("barrels", [])}
                self.overrides = {b["id"]: {"color": b.get("color"), "flags": {f: True for f in b.get("flags", [])}} for b in meta.get("barrels", [])}
                if meta.get("mask_sha1") != self.mask_sha:
                    self.stale = True
                    self.auto(replay=True)
                return
            except ValueError as ex:
                print(f"{js.name}: {ex} -> re-splitting")
        self.auto(replay=False)

    def auto(self, replay: bool) -> None:
        self.inst, recs, self.dropped = ins.split_instances(self.mask, self.cam, self.cfg)
        self.seed_kind = {r["id"]: (r["seed"], None) for r in recs}
        self.overrides = {}
        if replay and self.edits:
            self.inst, self.overrides, self.failed = ins.apply_edits(self.inst, self.mask, self.edits)
            if self.failed:
                print(f"{self.path.stem}: {len(self.failed)} edit(s) could not be replayed: {[f['op'] for f in self.failed]}")
        else:
            self.edits = []

    def records(self) -> list[dict]:
        return ins.records_from_inst(self.inst, self.mask, self.cam, self.seed_kind, self.cfg, self.overrides)

    def push(self) -> None:
        self.undo.append((self.inst.copy(), list(self.edits), json.loads(json.dumps(self.overrides))))
        del self.undo[:-30]

    def pop(self) -> None:
        if self.undo:
            self.inst, self.edits, ov = self.undo.pop()
            self.overrides = {int(k): v for k, v in ov.items()}
            self.selection.clear(); self.seeds.clear()

    def save(self) -> None:
        recs = self.records()
        meta = {"version": io.INSTANCE_JSON_VERSION, "mask_sha1": self.mask_sha,
                "camera": {"f": self.cam.f, "tilt_deg": self.cam.tilt_deg, "cx": self.cam.cx, "cy": self.cam.cy},
                "auto": {"algorithm": "stripe_ws", "params": self.cfg.to_dict()},
                "edits": self.edits, "dropped_px": int(getattr(self, "dropped", 0)),
                "barrels": [{k: r[k] for k in ("id", "color", "flags", "seed", "hints")} for r in recs]}
        io.save_instances(self.path, self.inst, meta, self.labels_dir)
        self.stale = False
        print(f"saved {self.path.stem}: {len(recs)} barrel(s), {len(self.edits)} edit(s)")

    # ---------------------------------------------------------------- edits
    def apply(self, edit: dict) -> None:
        self.push()
        out, ov, failed = ins.apply_edits(self.inst, self.mask, [edit])
        if failed:
            print("edit ignored:", failed[0]["error"]); self.undo.pop(); return
        self.inst = out
        for i, o in ov.items():
            cur = self.overrides.setdefault(i, {"flags": {}})
            if "color" in o:
                cur["color"] = o["color"]
            cur.setdefault("flags", {}).update(o.get("flags", {}))
        self.edits.append(edit)
        self.selection.clear(); self.seeds.clear()

    def point_of(self, i: int) -> tuple[int, int] | None:
        ys, xs = np.where(self.inst == i)
        if len(xs) == 0:
            return None
        return int(np.median(xs)), int(np.median(ys))

    # ---------------------------------------------------------------- render
    def render(self) -> np.ndarray:
        mode = VIEWS[self.view]
        if mode == "raw":
            view = self.img.copy()
        elif mode == "class mask":
            view = viz.overlay(self.img, self.mask, 0.55)
        else:
            view = self.img.copy()
            if mode == "instances+boxes":
                tint = view.copy()
                for i in np.unique(self.inst):
                    if i:
                        tint[self.inst == i] = palette(int(i))
                view = cv2.addWeighted(tint, 0.45, view, 0.55, 0)
            for r in self.records():
                x0, y0, x1, y1 = r["bbox"]
                col = viz.ORANGE_BGR if r["color"] == "orange" else viz.BLUE_BGR
                thick = 3 if r["id"] in self.selection else 1
                cv2.rectangle(view, (x0, y0), (x1 - 1, y1 - 1), col, thick)
                bm = r["bottom_mid"]; W = self.cam.expected_barrel_width_px(bottom_row=y1)
                if np.isfinite(W):
                    cv2.line(view, (int(bm[0] - W / 2), y1 + 3), (int(bm[0] + W / 2), y1 + 3), (255, 255, 255), 1)
                cv2.line(view, (int(bm[0]), y1 - 3), (int(bm[0]), y1 + 3), (255, 255, 255), 1)
                label = f"{r['id']} {r['color'][0]}" + ("".join(f" {f[:3]}" for f in r["flags"])) + (" hint:occl" if r["hints"] else "")
                cv2.putText(view, label, (x0, max(10, y0 - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)
                cv2.putText(view, label, (x0, max(10, y0 - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        for sx, sy in self.seeds:
            cv2.circle(view, (sx, sy), 4, (0, 255, 255), -1)
        if self.scale != 1:
            view = cv2.resize(view, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_NEAREST)
        hud = [f"[{self.idx + 1}/{len(self.images)}] {self.path.name}  view={mode}  sel={sorted(self.selection)}  seeds={len(self.seeds)}  edits={len(self.edits)}"
               + ("  STALE: mask changed, edits replayed" if self.stale else "")]
        if self.failed:
            hud.append(f"{len(self.failed)} edit(s) failed to replay")
        cc = ins.check_consistency(self.mask, self.inst)
        if cc["unassigned_class_px"] > getattr(self, "dropped", 0):
            hud.append(f"WARNING: {cc['unassigned_class_px']} barrel pixels have no instance")
        for k, text in enumerate(hud):
            cv2.putText(view, text, (8, 18 + 20 * k), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
            cv2.putText(view, text, (8, 18 + 20 * k), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return view


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR)
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--filter", default="")
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--cam", choices=sorted(CAMS), default="4a8b")
    args = ap.parse_args(argv)
    images = [p for p in io.list_images(args.raw) if args.filter in p.name and io.mask_path(p, args.labels).exists()]
    if not images:
        print("no labeled images match"); return 1
    s = Session(images, args.labels, args.scale, CAMS[args.cam], ins.SplitConfig())

    def on_mouse(event, x, y, flags, _):
        x, y = int(x / s.scale), int(y / s.scale)
        s.cursor = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            i = ins._id_at(s.inst, (x, y))
            if not (flags & cv2.EVENT_FLAG_SHIFTKEY):
                s.selection.clear()
            if i:
                s.selection ^= {i}
        elif event == cv2.EVENT_RBUTTONDOWN:
            s.seeds.append((x, y))

    cv2.namedWindow(WIN, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WIN, on_mouse)
    print(__doc__)
    while True:
        cv2.imshow(WIN, s.render())
        k = cv2.waitKey(20) & 0xFF
        if k == 255:
            continue
        ch = chr(k)
        pts = [p for p in (s.point_of(i) for i in sorted(s.selection)) if p]
        if ch == "w" and len(s.seeds) >= 2:
            s.apply({"op": "split", "seeds": [list(p) for p in s.seeds]})
        elif ch == "m" and len(pts) >= 2:
            s.apply({"op": "merge", "points": [list(p) for p in pts]})
        elif ch == "d":
            for p in pts:
                s.apply({"op": "delete", "point": list(p)})
        elif ch in ("o", "b"):
            for p in pts:
                s.apply({"op": "color", "point": list(p), "color": "orange" if ch == "o" else "blue"})
        elif ch in FLAG_KEYS:
            for i, p in zip(sorted(s.selection), pts):
                cur = s.overrides.get(i, {}).get("flags", {}).get(FLAG_KEYS[ch])
                if cur is None:
                    cur = FLAG_KEYS[ch] in next((r["flags"] for r in s.records() if r["id"] == i), [])
                s.apply({"op": "flag", "point": list(p), "flag": FLAG_KEYS[ch], "value": not cur})
        elif ch == "c":
            s.selection.clear(); s.seeds.clear()
        elif ch == "a":
            s.push(); s.auto(replay=False); s.selection.clear(); s.seeds.clear()
        elif ch == "u":
            s.pop()
        elif ch == "v":
            s.view = (s.view + 1) % len(VIEWS)
        elif ch == "s":
            s.save()
        elif ch in "np":
            s.save(); s.load(s.idx + (1 if ch == "n" else -1))
        elif ch == "q" or k == 27:
            s.save(); break
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    sys.exit(main())
