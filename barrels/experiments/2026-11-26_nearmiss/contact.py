#!/usr/bin/env python3
"""Contact sheets of a JUDGED candidate of experiment 2026-11-26_nearmiss: one tile per barrel gained, per barrel
lost, and per box that is not on a barrel, read from the judge's own pages (results/2026-11-26_nearmiss/<name>/).

    python barrels/experiments/2026-11-26_nearmiss/contact.py NAME [--kinds gained lost boxes] [--extreme] [--stems STEM ...]

A tile is four crops around the barrel (or the box), left to right:
    the photo with the hand boxes (white; the barrel in question thicker)
    the photo with the fixed model's boxes (thin gray) and the candidate's (thick, in the barrel's color)
    the fixed mask
    the candidate's mask; the paint it ADDED is bright (yellow = added orange, cyan = added blue)
Each frame is drawn with the setting that scored it (for a candidate chosen in folds: the one chosen without that
frame's place). ``--stems``: whole-frame tiles of these frames instead (the named clutter traps). Train frames only
(``judge.load_frame``). PNGs: results/2026-11-26_nearmiss/contact/ (not in git).
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nm_common as cm  # noqa: E402
import sheets as sh  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import nearmiss as nm  # noqa: E402

PW, PH = 176, 132           # one crop
PER_ROW, ROWS = 2, 7


@lru_cache(maxsize=64)
def panels(stem: str, spec: str):
    frame = jg.load_frame(stem)
    gts = dtp.barrels_from_boxes(io.load_boxes(stem, check_image=False))
    strict = nm.strict_mask(frame, cm.model())
    mask = cm.mask_of(spec, frame, strict)
    base, cand = det.detect(strict, cm.DET, cm.CAM), det.detect(mask, cm.DET, cm.CAM)
    photo = np.ascontiguousarray(frame.bgr)
    b = photo.copy()
    for p in base:
        cv2.rectangle(b, p.bbox[:2], (p.bbox[2] - 1, p.bbox[3] - 1), (170, 170, 170), 1)
    for p in cand:
        cv2.rectangle(b, (p.bbox[0] - 1, p.bbox[1] - 1), (p.bbox[2], p.bbox[3]), sh.BGR[p.color], 2)
    return photo, gts, b, sh.mask_picture(strict), sh.mask_picture(mask, strict)


def fit_crop(img: np.ndarray, box) -> np.ndarray:
    x0, y0, x1, y1 = box
    crop = img[y0:y1, x0:x1]
    k = min(PW / crop.shape[1], PH / crop.shape[0])
    crop = cv2.resize(crop, (max(1, int(crop.shape[1] * k)), max(1, int(crop.shape[0] * k))), interpolation=cv2.INTER_NEAREST if k > 1 else cv2.INTER_AREA)
    out = np.full((PH, PW, 3), 255, np.uint8)
    out[:crop.shape[0], :crop.shape[1]] = crop
    return out


def tile(stem: str, spec: str, bbox, text: str, gt_index: int | None = None, whole: bool = False) -> np.ndarray:
    photo, gts, b, m0, m1 = panels(stem, spec)
    a = photo.copy()
    for i, g in enumerate(gts):
        cv2.rectangle(a, g.bbox[:2], (g.bbox[2] - 1, g.bbox[3] - 1), (255, 255, 255), 2 if i == gt_index else 1)
    if whole:
        box = (0, 0, 640, 480)
    else:
        x0, y0, x1, y1 = bbox
        pad = max(24, int(0.7 * max(x1 - x0, y1 - y0)))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        half_w = max(x1 - x0, int((y1 - y0) * PW / PH)) // 2 + pad
        half_h = int(half_w * PH / PW)
        box = (max(0, cx - half_w), max(0, cy - half_h), min(640, cx + half_w), min(480, cy + half_h))
    row = np.hstack([fit_crop(p, box) for p in (a, b, m0, m1)])
    bar = np.full((28, row.shape[1], 3), 255, np.uint8)
    cv2.putText(bar, stem.replace("4A8B_", ""), (3, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(bar, text, (3, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 0, 160), 1, cv2.LINE_AA)
    return np.vstack([bar, row])


def pages(tiles: list[np.ndarray], out: Path, name: str) -> list[Path]:
    paths = []
    per = PER_ROW * ROWS
    for n in range(0, len(tiles), per):
        chunk = tiles[n:n + per]
        h, w = chunk[0].shape[:2]
        sheet = np.full((ROWS * (h + 6), PER_ROW * (w + 10), 3), 255, np.uint8)
        for i, t in enumerate(chunk):
            r, c = divmod(i, PER_ROW)
            sheet[r * (h + 6):r * (h + 6) + h, c * (w + 10):c * (w + 10) + w] = t
        used = (len(chunk) + PER_ROW - 1) // PER_ROW
        p = out / f"{name}_{n // per + 1:02d}.png"
        cv2.imwrite(str(p), sheet[:used * (h + 6)])
        paths.append(p)
    return paths


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name")
    ap.add_argument("--kinds", nargs="*", default=["gained", "lost", "boxes"])
    ap.add_argument("--extreme", action="store_true", help="the report-only conditions instead of the ordinary ones")
    ap.add_argument("--stems", nargs="*", default=[])
    a = ap.parse_args(argv)
    d = cm.RESULTS / a.name
    j, x = json.loads((d / "judge.json").read_text()), json.loads((d / "extras.json").read_text())

    def spec_of(stem: str) -> str:
        if x["spec"]:
            return x["spec"]
        folds = x["folds"]
        place = ct.place_of(stem)
        return folds[place]["spec"] if place in folds else next(iter(folds.values()))["spec"]
    out = cm.RESULTS / "contact"
    out.mkdir(parents=True, exist_ok=True)
    judged = not a.extreme
    if a.stems:
        jg.require_train(a.stems)
        tiles = [tile(s, spec_of(s), None, spec_of(s), whole=True) for s in a.stems]
        for p in pages(tiles, out, f"{a.name}_frames"):
            print(p)
        return 0
    for kind in a.kinds:
        tiles = []
        if kind in ("gained", "lost"):
            for c in j["changes"]:
                if c["kind"] == kind and bool(c["judged"]) == judged:
                    tiles.append(tile(c["stem"], spec_of(c["stem"]), c["bbox"], f"#{c['index'] + 1} {c['color']}: {c['before']} -> {c['after']}   {spec_of(c['stem'])}", c["index"]))
        else:
            for c in j["box_changes"]:
                if bool(c["judged"]) != judged:
                    continue
                more = {k: c["after"][k] - c["before"][k] for k in c["after"] if c["after"][k] != c["before"][k]}
                where = " [empty frame]" if c["empty"] else ""
                for color, bbox in c["boxes_after"]:
                    tiles.append(tile(c["stem"], spec_of(c["stem"]), bbox, f"{color} box at {list(bbox)}{where}; frame: {more}   {spec_of(c['stem'])}"))
        for p in pages(tiles, out, f"{a.name}_{kind}{'_extreme' if a.extreme else ''}"):
            print(p)
        print(f"{a.name} {kind}: {len(tiles)} tile(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
