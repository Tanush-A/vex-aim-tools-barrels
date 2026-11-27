#!/usr/bin/env python3
"""Contact sheets of the contrast experiment: per frame (or per barrel, cropped) five panels side by side:

    photo + hand boxes | the contrast response + candidates | the fixed mask | the mask the detector saw | the boxes

    python barrels/experiments/2026-11-26_contrast/sheets.py --stems 4A8B_lampwarm6_bathtile_core_01,... [--name look]
    python barrels/experiments/2026-11-26_contrast/sheets.py --judge results/2026-11-26_contrast/judge_C1/judge.json

Response panel: red where a band is bluer than what is above and below it (an orange barrel's stripe), blue where it
is redder (a blue barrel's stripe), brighter = a larger difference. Candidates: the predicted box in the barrel's
color; a thin gray box = a candidate a guard refused or that was left alone (the reason is written on it).
Boxes panel: white = the hand boxes, green = today's boxes, magenta = boxes the contrast path added (or, in merge and
alone mode, every box). Train frames only. PNGs are not committed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidate as cd  # noqa: E402
import common as cm  # noqa: E402

from barrels import contrast_c4 as cn  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

BGR = {ORANGE: (0, 140, 255), BLUE: (255, 120, 0)}
WHITE, GREEN, MAGENTA, GRAY = (255, 255, 255), (0, 220, 0), (255, 0, 255), (150, 150, 150)


def _mask_img(mask: np.ndarray) -> np.ndarray:
    out = np.zeros(mask.shape + (3,), np.uint8)
    out[mask == ORANGE] = BGR[ORANGE]
    out[mask == BLUE] = BGR[BLUE]
    return out


def _response_img(resp: cn.Response) -> np.ndarray:
    s = resp.score
    out = np.zeros(s.shape + (3,), np.uint8)
    out[..., 2] = np.clip(np.maximum(s, 0) / 2.5 * 255, 0, 255)
    out[..., 0] = np.clip(np.maximum(-s, 0) / 2.5 * 255, 0, 255)
    out[..., 1] = np.where(resp.good, 0, 40)                  # unusable pixels (dark or clipped): a dim green
    return out


def _rect(img, box, color, thick=1):
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), color, thick)


def panels(stem: str, st: cd.Setting) -> list[np.ndarray]:
    frame = jg.load_frame(stem)
    lab = io.load_boxes(stem, check_image=False)
    fw = cd.FrameWork(frame)
    resp = fw.response(st.params())
    mask, cands = fw.masks(st)
    final = fw.detect(st)
    today = fw.base_boxes
    photo = frame.bgr.copy()
    for b in lab["barrels"]:
        _rect(photo, b["bbox"], WHITE)
    rimg = _response_img(resp)
    for i, c in enumerate(cands):
        why = ",".join(c.info.get("reasons", []))
        col = GRAY if (why or not c.info.get("painted")) else BGR[c.color]
        _rect(rimg, c.box, col, 1)
        cv2.circle(rimg, (c.x, c.row), 2, col, -1)
        cv2.putText(rimg, f"{i}:{c.strength:.1f}{' ' + why if why else ''}", (int(c.box[0]), max(10, int(c.box[1]) - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, col, 1, cv2.LINE_AA)
    fixed = _mask_img(cm.fixed_mask(frame))
    seen = _mask_img(mask)
    boxes = frame.bgr.copy()
    for b in lab["barrels"]:
        _rect(boxes, b["bbox"], WHITE)
    for b in final:
        is_today = any(o.bbox == b.bbox and o.color == b.color for o in today)
        _rect(boxes, b.bbox, GREEN if is_today else MAGENTA, 2)
        cv2.putText(boxes, "O" if b.color == ORANGE else "B", (b.bbox[0] + 2, b.bbox[1] + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, GREEN if is_today else MAGENTA, 1, cv2.LINE_AA)
    return [photo, rimg, fixed, seen, boxes]


def row(stem: str, st: cd.Setting, crop=None, scale: float = 1.0, title: str = "") -> np.ndarray:
    ps = panels(stem, st)
    if crop is not None:
        x0, y0, x1, y1 = crop
        ps = [p[y0:y1, x0:x1] for p in ps]
    if scale != 1.0:
        ps = [cv2.resize(p, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST) for p in ps]
    gap = np.full((ps[0].shape[0], 4, 3), 60, np.uint8)
    body = np.concatenate([x for p in ps for x in (p, gap)][:-1], axis=1)
    head = np.full((16, body.shape[1], 3), 30, np.uint8)
    cv2.putText(head, (title or stem.replace("4A8B_", ""))[: body.shape[1] // 7], (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1, cv2.LINE_AA)
    return np.concatenate([head, body], axis=0)


def crop_around(bbox, pad: float = 0.8, min_side: int = 90, shape=(480, 640)) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    px, py = max(pad * w, (min_side - w) / 2), max(pad * h, (min_side - h) / 2)
    return (max(0, int(x0 - px)), max(0, int(y0 - py)), min(shape[1], int(x1 + px)), min(shape[0], int(y1 + py)))


def stack(rows: list[np.ndarray]) -> np.ndarray:
    w = max(r.shape[1] for r in rows)
    return np.concatenate([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows], axis=0)


def save(rows: list[np.ndarray], path: Path, per_sheet_px: int = 1800) -> list[Path]:
    """Write the rows as sheets no taller than ``per_sheet_px`` each."""
    out, cur, hgt, n = [], [], 0, 0
    for r in rows + [None]:
        if r is None or (cur and hgt + r.shape[0] > per_sheet_px):
            p = path.with_name(f"{path.stem}_{n:02d}.png")
            cv2.imwrite(str(p), stack(cur))
            out.append(p)
            cur, hgt, n = [], 0, n + 1
        if r is not None:
            cur.append(r)
            hgt += r.shape[0]
    return out


setting_from = cd.setting_from


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stems", default="")
    ap.add_argument("--judge", default="", help="a judge.json: crops of every barrel gained and lost and of every frame with a new box")
    ap.add_argument("--setting", default="", help="mode=add,margin=1,... (default: candidate.BEST)")
    ap.add_argument("--settings-json", default="", help="chosen.json of run.py with --family: the setting of each held-out place")
    ap.add_argument("--family", default="")
    ap.add_argument("--name", default="look")
    ap.add_argument("--scale", type=float, default=0.5)
    a = ap.parse_args()
    st = setting_from(a.setting) if a.setting else cd.BEST
    per_place = {}
    if a.settings_json:
        ch = json.loads(Path(a.settings_json).read_text())["folds"][a.family]
        per_place = {p: (setting_from(v["spec"]) if v["spec"] else None) for p, v in ch.items()}

    def st_for(stem: str):
        return per_place.get(ct.place_of(stem), st) if per_place else st
    out_dir = cm.OUT / "sheets"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    if a.stems:
        for s in a.stems.split(","):
            s = s if s.startswith("4A8B_") else "4A8B_" + s
            if st_for(s) is not None:
                rows.append(row(s, st_for(s), scale=a.scale))
    if a.judge:
        j = json.loads(Path(a.judge).read_text())
        for c in j["changes"]:
            if st_for(c["stem"]) is None:
                continue
            crop = crop_around(c["bbox"])
            sc = max(1.0, min(4.0, 220 / max(1, crop[3] - crop[1])))
            rows.append(row(c["stem"], st_for(c["stem"]), crop, sc, f"{c['kind'].upper()} {c['stem'].replace('4A8B_', '')} #{c['index'] + 1} {c['color']} {c['before']}->{c['after']}{'' if c['judged'] else ' (report only)'}"))
        for x in j["box_changes"]:
            if sum(x["after"].values()) > sum(x["before"].values()) and st_for(x["stem"]) is not None:
                for col, bb in x["boxes_after"]:
                    crop = crop_around(bb)
                    sc = max(1.0, min(4.0, 220 / max(1, crop[3] - crop[1])))
                    rows.append(row(x["stem"], st_for(x["stem"]), crop, sc, f"BOX NOT ON ITS BARREL {x['stem'].replace('4A8B_', '')} {col} {list(bb)}{' [empty frame]' if x['empty'] else ''}{'' if x['judged'] else ' (report only)'}"))
    if not rows:
        print("nothing to draw")
        return 1
    for p in save(rows, out_dir / f"{a.name}.png"):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
