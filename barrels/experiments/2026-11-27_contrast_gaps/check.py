"""With every addition off, ``gaps.detect`` gives exactly ``pipeline.detect_frame`` (today's default) on every train
frame. Exit 0 = identical.

    python barrels/experiments/2026-11-27_contrast_gaps/check.py
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gaps as gp  # noqa: E402

from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402


def one(stem):
    import cv2
    cv2.setNumThreads(1)
    f = jg.load_frame(stem)
    a = [(b.color, b.bbox, b.source) for b in pl.detect_frame(f)]
    b = [(b.color, b.bbox, b.source) for b in gp.detect(f, gp.Gaps())]
    return stem, a == b


def main() -> int:
    stems = [s for v in jg.train_frames().values() for s in v]
    with Pool(8) as p:
        res = dict(p.imap_unordered(one, stems, chunksize=2))
    bad = [s for s, ok in res.items() if not ok]
    print(f"{len(stems)} train frames: {'IDENTICAL BOXES ON EVERY FRAME' if not bad else f'{len(bad)} differ: {bad}'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
