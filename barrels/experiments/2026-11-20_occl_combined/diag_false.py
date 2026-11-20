#!/usr/bin/env python3
"""Diagnostics, no number of the verdict comes from here: one damaged HOME mask of ``run_levels.py`` (level, frame,
seed), what a few arms draw on it, which rule drew each box, the slice rule's own notes, and a picture of the mask
around the barrels (true boxes white, right boxes yellow / green, false boxes red).

    python barrels/experiments/2026-11-20_occl_combined/diag_false.py medium cluster_02 12 [more: level frame seed ...] [--arms stack,combined]
Output: text; results/2026-11-20_occl_combined/logs/diag_<level>_<frame>_<seed>_<arm>.png (ignored by git).
"""
from __future__ import annotations

import sys

import cv2
import numpy as np

import common as C
from barrels import degrade as dg, detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io

A = C.A
CAM = geo.AIM_4A8B6118_BOXFIT
NO_PATCH = "bad day without the stripe patch"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    arms = ["stack", "vertical_alone", "combined"]
    if "--arms" in argv:
        i = argv.index("--arms"); arms = argv[i + 1].split(","); del argv[i:i + 2]
    cases = [(argv[k], argv[k + 1], int(argv[k + 2])) for k in range(0, len(argv), 3)]
    G = C.load("det_given_seg_run", C.SEG / "run.py")
    home = [s for s in G.train_sets()["HOME"] if io.mask_path(s).exists()]
    out = C.OUT / "logs"
    out.mkdir(parents=True, exist_ok=True)
    for level, frame, seed in cases:
        i = next(k for k, s in enumerate(home) if s.endswith(frame)); s = home[i]
        gts, clean = G.truth(s)
        hand = io.load_mask(io.mask_path(s))
        d = dg.LEVELS.get(level)
        mask = hand if level == "perfect" else dg.damage(hand, [tuple(g.bbox) for g in gts], d, seed=1000 * seed + i)
        print(f"== {level}, {frame}, seed {seed}; true boxes: " + ", ".join(f"{dtp.COLOR_NAMES[g.color]} {list(g.bbox)}" for g in gts))
        for arm in arms:
            log: list = []
            preds = det.detect(mask, A.rule_config(A.ARMS[arm]), CAM, log=log)
            res = ed.evaluate_frame(s, preds, gts, CAM, rule="v2", clean=clean)
            print(f"  {arm}: " + "; ".join(f"{dtp.COLOR_NAMES[p.color]} {list(p.bbox)} [{C.drawn_by(log, p.bbox)}]{' FALSE' if k in res.unmatched_pred else ''}"
                                          for k, p in enumerate(preds)) + f" | missed {len(res.unmatched_gt)}")
            for e in log:
                if e["stage"] in ("slice", "pair", "half") and e["why"] == "kept":
                    print(f"    {e['stage']} kept:", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items() if k not in ("stage", "why")})
            xs = [v for g in gts for v in (g.bbox[0], g.bbox[2])] + [v for p in preds for v in (p.bbox[0], p.bbox[2])]
            ys = [v for g in gts for v in (g.bbox[1], g.bbox[3])] + [v for p in preds for v in (p.bbox[1], p.bbox[3])]
            x0, x1, y0, y1 = max(0, min(xs) - 15), min(640, max(xs) + 15), max(0, min(ys) - 15), min(480, max(ys) + 15)
            img = np.full((480, 640, 3), 45, np.uint8); img[mask == 1] = (0, 140, 255); img[mask == 2] = (255, 120, 0)
            f = max(2, min(6, 1200 // max(1, x1 - x0)))
            crop = cv2.resize(img[y0:y1, x0:x1], None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST)
            for g in gts:
                cv2.rectangle(crop, ((g.bbox[0] - x0) * f, (g.bbox[1] - y0) * f), ((g.bbox[2] - x0) * f - 1, (g.bbox[3] - y0) * f - 1), (255, 255, 255), 1)
            for k, p in enumerate(preds):
                col = (0, 0, 255) if k in res.unmatched_pred else ((0, 255, 255) if p.color == 1 else (0, 255, 0))
                cv2.rectangle(crop, ((p.bbox[0] - x0) * f, (p.bbox[1] - y0) * f), ((p.bbox[2] - x0) * f - 1, (p.bbox[3] - y0) * f - 1), col, 2)
            name = out / f"diag_{level.split(',')[-1].strip().replace(' ', '-')}_{frame}_{seed}_{arm}.png"
            cv2.imwrite(str(name), crop)
            print("    picture:", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
