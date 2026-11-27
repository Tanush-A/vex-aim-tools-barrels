#!/usr/bin/env python3
"""Contact sheets for experiment 2026-11-26_nearmiss: one picture per frame with four panels.

    top left      the photo with the hand boxes (white)
    top right     the photo with the candidate's boxes (thick, in the barrel's color) and the fixed model's (thin, gray)
    bottom left   the fixed mask (orange / blue on dark)
    bottom right  the candidate's mask; paint the candidate ADDED is bright (yellow = added orange, cyan = added blue)

    python barrels/experiments/2026-11-26_nearmiss/sheets.py --spec pc:5,0,strict --changed [--extreme] [--limit 40]
    python barrels/experiments/2026-11-26_nearmiss/sheets.py --spec pc:5,0,strict --stems STEM [STEM ...] [--zoom]

``--changed``: every ordinary train frame where a barrel's state or a box that is not on its barrel differs from the
fixed model. ``--zoom``: crop to the hand boxes (and the boxes not on a barrel), enlarged. Train frames only
(``judge.load_frame`` refuses anything else). The PNGs go to results/2026-11-26_nearmiss/sheets/<spec>/ (not in git).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nm_common as cm  # noqa: E402

from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import nearmiss as nm  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

BGR = {ORANGE: (0, 140, 255), BLUE: (255, 120, 0)}
ADDED = {ORANGE: (0, 255, 255), BLUE: (255, 255, 0)}


def mask_picture(mask: np.ndarray, strict: np.ndarray | None = None) -> np.ndarray:
    out = np.full(mask.shape + (3,), 30, np.uint8)
    for c in (ORANGE, BLUE):
        out[mask == c] = BGR[c]
        if strict is not None:
            out[(mask == c) & (strict != c)] = ADDED[c]
    return out


def sheet(stem: str, spec: str, zoom: bool = False) -> np.ndarray:
    frame = jg.load_frame(stem)
    gts = dtp.barrels_from_boxes(io.load_boxes(stem, check_image=False))
    strict = nm.strict_mask(frame, cm.model())
    mask = cm.mask_of(spec, frame, strict)
    base = det.detect(strict, cm.DET, cm.CAM)
    cand = det.detect(mask, cm.DET, cm.CAM)
    photo = np.ascontiguousarray(frame.bgr)
    a, b = photo.copy(), photo.copy()
    for g in gts:
        cv2.rectangle(a, g.bbox[:2], (g.bbox[2] - 1, g.bbox[3] - 1), (255, 255, 255), 1)
    for p in base:
        cv2.rectangle(b, p.bbox[:2], (p.bbox[2] - 1, p.bbox[3] - 1), (170, 170, 170), 1)
    for p in cand:
        cv2.rectangle(b, (p.bbox[0] - 1, p.bbox[1] - 1), (p.bbox[2], p.bbox[3]), BGR[p.color], 2)
    panels = [a, b, mask_picture(strict), mask_picture(mask, strict)]
    if zoom:
        boxes = [g.bbox for g in gts] + [p.bbox for p in cand] + [p.bbox for p in base]
        if boxes:
            x0 = max(0, min(bx[0] for bx in boxes) - 25); y0 = max(0, min(bx[1] for bx in boxes) - 25)
            x1 = min(640, max(bx[2] for bx in boxes) + 25); y1 = min(480, max(bx[3] for bx in boxes) + 25)
            k = max(1, min(4, int(640 / max(1, x1 - x0)), int(480 / max(1, y1 - y0))))
            panels = [cv2.resize(p[y0:y1, x0:x1], None, fx=k, fy=k, interpolation=cv2.INTER_NEAREST) for p in panels]
    top = np.hstack(panels[:2])
    bottom = np.hstack(panels[2:])
    out = np.vstack([top, bottom])
    bar = np.full((22, out.shape[1], 3), 255, np.uint8)
    cv2.putText(bar, f"{stem}   {spec}   white = hand boxes, gray = fixed model's boxes, thick = candidate's; yellow / cyan = added paint",
                (4, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1, cv2.LINE_AA)
    return np.vstack([bar, out])


def changed_stems(spec: str, stems, jobs: int = 8) -> list[str]:
    recs = cm.ensure(["fixed", spec], stems, jobs)
    b, c = cm.counts_of(recs["fixed"]), cm.counts_of(recs[spec])
    return [s for s in stems if b[s].gt != c[s].gt or sorted(x for x in b[s].boxes if x in ("wrong_color", "second", "nothing"))
            != sorted(x for x in c[s].boxes if x in ("wrong_color", "second", "nothing"))]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--changed", action="store_true")
    ap.add_argument("--extreme", action="store_true", help="with --changed: the report-only conditions instead of the ordinary ones")
    ap.add_argument("--zoom", action="store_true")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args(argv)
    stems = list(a.stems)
    if a.changed:
        stems += changed_stems(a.spec, cm.report_only() if a.extreme else cm.ordinary(), a.jobs)
    jg.require_train(stems)
    out_dir = cm.RESULTS / "sheets" / a.spec.replace(":", "_").replace(",", "-")
    out_dir.mkdir(parents=True, exist_ok=True)
    for s in stems[:a.limit]:
        p = out_dir / f"{s}{'_zoom' if a.zoom else ''}.png"
        cv2.imwrite(str(p), sheet(s, a.spec, a.zoom))
        print(p)
    if len(stems) > a.limit:
        print(f"({len(stems) - a.limit} more not written: --limit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
