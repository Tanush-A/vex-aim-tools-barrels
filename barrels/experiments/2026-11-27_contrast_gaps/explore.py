"""Exploration before the PREREG (in-sample, all train frames, ordinary and extreme): at the loosest setting of each
addition, every box it adds or changes, and whether that box is on a labelled barrel of its color. Not a judged run.

    python barrels/experiments/2026-11-27_contrast_gaps/explore.py [edge half split]
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gaps as gp  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402

OUT = gp.BARRELS / "results" / "2026-11-27_contrast_gaps"
G = gp.Gaps(edge=0.4, half=1.0, split=1.1, beside=0.8)


def one(stem):
    import cv2
    cv2.setNumThreads(1)
    f = jg.load_frame(stem)
    gts, clean = ct.load_gts([stem])
    base = gp.detect(f, gp.Gaps())
    new = gp.detect(f, G)
    rows = []
    for b in new:
        if b in base:
            continue
        on = [g.bbox for g in gts.get(stem, []) if g.color == b.color and ct.is_on(b, g)]
        rows.append({"stem": stem, "bbox": b.bbox, "color": b.color, "source": b.source, "on": on, "clean": clean.get(stem, True),
                     "empty": not gts.get(stem)})
    lost = [b.bbox for b in base if b not in new]
    return rows, ([{"stem": stem, "lost": lost}] if lost else [])


def main():
    fr = jg.train_frames()
    stems = fr["ordinary"] + fr["extreme"]
    rows, lost = [], []
    with Pool(8) as p:
        for r, l in p.imap_unordered(one, stems, chunksize=2):
            rows += r
            lost += l
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "explore.json").write_text(json.dumps({"setting": G.key, "new": rows, "removed": lost}, indent=1, default=str))
    by = {}
    for r in rows:
        k = (r["source"], "on" if r["on"] else ("EMPTY" if r["empty"] else "off"))
        by[k] = by.get(k, 0) + 1
    for k, v in sorted(by.items()):
        print(k, v)
    print("removed:", len(lost))
    for r in rows:
        print(r["stem"], r["source"], r["bbox"], "ON" if r["on"] else ("EMPTY FRAME" if r["empty"] else "off"))


if __name__ == "__main__":
    main()
