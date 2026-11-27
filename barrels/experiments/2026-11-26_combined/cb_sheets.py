#!/usr/bin/env python3
"""Contact sheets of experiment 2026-11-26_combined: one tile per barrel or per box, read from the judged run.

    python barrels/experiments/2026-11-26_combined/cb_sheets.py gained [WAY]     # barrels WAY finds that a winner alone does not, and the reverse
    python barrels/experiments/2026-11-26_combined/cb_sheets.py missed [WAY]     # barrels WAY does not find: the ones not hidden, then the hidden ones
    python barrels/experiments/2026-11-26_combined/cb_sheets.py boxes [WAY]      # every box of WAY that is not on its barrel (ordinary, then extreme)
    python barrels/experiments/2026-11-26_combined/cb_sheets.py overlap          # barrels one winner gains and the other does not
    python barrels/experiments/2026-11-26_combined/cb_sheets.py frames WAY STEM [STEM ...]     # whole frames

A tile is six crops around the barrel (or the box), left to right:

    1  the photo; hand boxes white, the barrel in question thick
    2  today's mask (the fixed colors); today's boxes
    3  the near-miss step's mask; the paint it ADDED is bright (yellow = added orange, cyan = added blue); its boxes
    4  self-calibration's mask, added paint bright; its boxes; its seeds as thin outlines (green = kept, red = refused)
    5  WAY's mask (for the two box ways: both masks laid over each other), added paint bright; WAY's boxes
    6  the photo with WAY's boxes (thick, in the barrel's color) and today's (thin, gray)

On a mask a box of an orange barrel is drawn white and a box of a blue barrel light green. The boxes are the held-out
boxes of the judged run (boxes.json); the masks are made again with the settings the fold of that frame's place
picked (chosen.json). Train frames only (``judge.load_frame``). PNGs: results/2026-11-26_combined/sheets/ (not in git).
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cb_common as cb  # noqa: E402

an = cb._load("cb_analysis", cb.HERE / "analysis.py")

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels.detect_types import COLOR_NAMES  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

BGR = {ORANGE: (0, 140, 255), BLUE: (255, 120, 0)}
ADDED = {ORANGE: (0, 255, 255), BLUE: (255, 255, 0)}
ON_MASK = {ORANGE: (255, 255, 255), BLUE: (120, 255, 120)}
PW, PH = 200, 150
PER_PAGE = 5
SHEETS = cb.RESULTS / "sheets"
LETTER = {ct.FOUND: "found", ct.OFF: "box off", ct.MISSED: "missed"}


def mask_picture(mask: np.ndarray, strict: np.ndarray) -> np.ndarray:
    out = np.full(mask.shape + (3,), 30, np.uint8)
    for c in (ORANGE, BLUE):
        out[mask == c] = BGR[c]
        out[(mask == c) & (strict != c)] = ADDED[c]
    return out


def draw(img: np.ndarray, barrels, thick: int = 1, color=None, table=BGR) -> np.ndarray:
    for p in barrels:
        x0, y0, x1, y1 = (int(v) for v in p.bbox)
        cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), color or table[p.color], thick)
    return img


@lru_cache(maxsize=24)
def panels(stem: str, way: str):
    _, truth, _, preds = an.data()
    frame, both, c = an.parts(stem, way)
    photo = np.ascontiguousarray(frame.bgr)
    p2 = draw(mask_picture(both.strict, both.strict), preds["fixed"][stem], table=ON_MASK)
    p3 = draw(mask_picture(both.nm_mask, both.strict), preds["nearmiss"][stem], table=ON_MASK)
    p4 = mask_picture(both.sc_mask, both.strict)
    for s in both.seeds:
        if s.why != "duplicate":
            x0, y0, x1, y1 = s.bbox
            cv2.rectangle(p4, (x0 - 1, y0 - 1), (x1, y1), (0, 200, 0) if s.ok else (0, 0, 255), 1)
    draw(p4, preds["selfcal"][stem], table=ON_MASK)
    p5 = draw(mask_picture(c.mask, both.strict), preds[way][stem], table=ON_MASK)
    p6 = draw(photo.copy(), preds["fixed"][stem], 1, (170, 170, 170))
    for p in preds[way][stem]:
        cv2.rectangle(p6, (p.bbox[0] - 1, p.bbox[1] - 1), (p.bbox[2], p.bbox[3]), BGR[p.color], 2)
    return photo, truth.gts[stem], (p2, p3, p4, p5, p6)


def fit_crop(img: np.ndarray, box) -> np.ndarray:
    x0, y0, x1, y1 = box
    crop = img[y0:y1, x0:x1]
    k = min(PW / crop.shape[1], PH / crop.shape[0])
    crop = cv2.resize(crop, (max(1, int(crop.shape[1] * k)), max(1, int(crop.shape[0] * k))), interpolation=cv2.INTER_NEAREST if k > 1 else cv2.INTER_AREA)
    out = np.full((PH, PW, 3), 255, np.uint8)
    out[:crop.shape[0], :crop.shape[1]] = crop
    return out


def tile(stem: str, way: str, bbox, text: str, gt_index: int | None = None, whole: bool = False) -> np.ndarray:
    photo, gts, rest = panels(stem, way)
    a = photo.copy()
    for i, g in enumerate(gts):
        cv2.rectangle(a, g.bbox[:2], (g.bbox[2] - 1, g.bbox[3] - 1), (255, 255, 255), 2 if i == gt_index else 1)
    if whole or bbox is None:
        box = (0, 0, 640, 480)
    else:
        x0, y0, x1, y1 = bbox
        pad = max(24, int(0.7 * max(x1 - x0, y1 - y0)))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        half_w = max(x1 - x0, int((y1 - y0) * PW / PH)) // 2 + pad
        half_h = int(half_w * PH / PW)
        box = (max(0, cx - half_w), max(0, cy - half_h), min(640, cx + half_w), min(480, cy + half_h))
    row = np.hstack([fit_crop(p, box) for p in (a, *rest)])
    bar = np.full((28, row.shape[1], 3), 255, np.uint8)
    cv2.putText(bar, f"{an.short(stem)}   [photo | today | nearmiss | selfcal | {way} mask | {way} boxes]", (3, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(bar, text[:190], (3, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 160), 1, cv2.LINE_AA)
    return np.vstack([bar, row])


def pages(tiles: list[np.ndarray], out: Path, name: str) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for n in range(0, len(tiles), PER_PAGE):
        chunk = tiles[n:n + PER_PAGE]
        sheet = np.vstack([np.vstack([t, np.full((6, t.shape[1], 3), 255, np.uint8)]) for t in chunk])
        p = out / f"{name}_{n // PER_PAGE + 1:02d}.png"
        cv2.imwrite(str(p), sheet)
        paths.append(p)
    print(f"{name}: {len(tiles)} tile(s), {len(paths)} page(s)" + (f", first {paths[0]}" if paths else ""), flush=True)
    return paths


def barrel_text(stem: str, i: int, way: str) -> str:
    _, truth, counts, _ = an.data()
    g = truth.gts[stem][i]
    st = "  ".join(f"{n} {LETTER[counts[k][stem].gt[i]]}" for n, k in (("today", "fixed"), ("nearmiss", "nearmiss"), ("selfcal", "selfcal"), (way, way)))
    return f"#{i + 1} {COLOR_NAMES[g.color]} {list(g.bbox)} {','.join(sorted(g.flags))}:  {st}"


def barrels_where(way: str, test) -> list[tuple[str, int]]:
    frames, truth, counts, _ = an.data()
    out = []
    for s in frames[cnd.ORDINARY]:
        for i, g in enumerate(truth.gts[s]):
            if test({n: counts[n][s].gt[i] for n in ("fixed", "nearmiss", "selfcal", way)}, g):
                out.append((s, i))
    return out


def barrel_pages(way: str, name: str, test) -> list[Path]:
    _, truth, _, _ = an.data()
    sel = barrels_where(way, test)
    return pages([tile(s, way, truth.gts[s][i].bbox, barrel_text(s, i, way), i) for s, i in sel], SHEETS / way, name)


def main(argv) -> int:
    what = argv[0] if argv else "boxes"
    F = ct.FOUND
    if what == "overlap":
        way = "box_union"
        barrel_pages(way, "only_nearmiss", lambda st, g: st["fixed"] != F and st["nearmiss"] == F and st["selfcal"] != F)
        barrel_pages(way, "only_selfcal", lambda st, g: st["fixed"] != F and st["selfcal"] == F and st["nearmiss"] != F)
        return 0
    way = argv[1] if len(argv) > 1 else an.best_way()
    if what == "gained":
        barrel_pages(way, "gained_over_selfcal", lambda st, g: st[way] == F and st["selfcal"] != F)
        barrel_pages(way, "gained_over_nearmiss", lambda st, g: st[way] == F and st["nearmiss"] != F)
        barrel_pages(way, "found_by_a_winner_not_by_it", lambda st, g: st[way] != F and (st["selfcal"] == F or st["nearmiss"] == F))
        barrel_pages(way, "found_today_not_by_it", lambda st, g: st[way] != F and st["fixed"] == F)
    elif what == "missed":
        barrel_pages(way, "missed", lambda st, g: st[way] != F and not (set(g.flags) & an.HIDDEN))
        barrel_pages(way, "missed_hidden", lambda st, g: st[way] != F and bool(set(g.flags) & an.HIDDEN))
    elif what == "boxes":
        frames, _, counts, preds = an.data()
        for klass, name in ((cnd.ORDINARY, "boxes"), (cnd.EXTREME, "boxes_extreme")):
            tiles = []
            for s in frames[klass]:
                fc = counts[way][s]
                for p, st in zip(preds[way][s], fc.boxes):
                    if st in ct.EXTRA_STATES:
                        kind = " [empty frame, clean]" if fc.negative and fc.clean else " [empty frame with clutter]" if fc.negative else ""
                        tiles.append(tile(s, way, p.bbox, f"{COLOR_NAMES[p.color]} box {list(p.bbox)}: {st.replace('_', ' ')}{kind}"))
            pages(tiles, SHEETS / way, name)
    elif what == "frames":
        pages([tile(s, way, None, "whole frame", whole=True) for s in argv[2:]], SHEETS / way, "frames")
    else:
        raise SystemExit(f"unknown kind {what!r}: gained, missed, boxes, overlap, frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
