"""The judged candidates of the experiment (PREREG.md) as importable callables.

    from candidate import detect_frame_slack           # detect_frame(stem, frame) -> list[Barrel]
    python barrels/tools/judge.py --cand-callable barrels/experiments/2026-11-27_occl_photo/candidate.py:detect_frame_slack
    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-27_occl_photo/candidate.py:fit

Each is today's photo-in, boxes-out path (fixed colors, detector, stripe by contrast) with ``DetConfig.side_photo`` on
and the photo handed to both detector runs (``lib.run_frame``).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
from lib import ct, det, jg  # noqa: E402

ARMS = {                                   # in PREREG order: stricter first (a tie in ``fit`` goes to the earlier one)
    "cut": {"side_photo": "cut"},
    "cut+bulge": {"side_photo": "cut+bulge"},
    "slack": {"side_photo": "cut", "photo_slack": 0.1},
    "loose": {"side_photo": "cut", "photo_slack": 0.1, "photo_frac": 0.5, "photo_cross": 0.2},
}
FIT_ORDER = ("cut+bulge", "cut", "slack", "loose")   # strictest first (cut+bulge asks more than cut)


def detector_of(arm: str):
    cfg = det.DetConfig(**ARMS.get(arm, {}))

    def detect_frame(stem: str, frame) -> list:
        return lib.run_frame(frame, cfg=cfg)
    detect_frame.describe = f"today's default + side_photo arm {arm!r} {ARMS.get(arm, {})} (photo to both detector runs)"
    return detect_frame


detect_frame_cut = detector_of("cut")
detect_frame_cut_bulge = detector_of("cut+bulge")
detect_frame_slack = detector_of("slack")
detect_frame_loose = detector_of("loose")

_cache: dict = {}


def _states(stem: str, arm: str):
    """(barrels found strict, boxes not on their barrel) of one training frame under one arm (``off`` = today)."""
    key = (stem, arm)
    if key not in _cache:
        frame = jg.load_frame(stem)
        boxes = lib.run_frame(frame, cfg=det.DetConfig(**ARMS[arm]) if arm != "off" else det.DetConfig())
        gts, clean = lib.truth(stem)
        fc = ct.classify_frame(stem, boxes, gts, clean)
        _cache[key] = (sum(s == ct.FOUND for s in fc.gt), sum(s in (ct.NOTHING, ct.SECOND, ct.WRONG) for s in fc.boxes))
    return _cache[key]


def fit(train_stems, held_place):
    """Leave one place out (PREREG): on the training frames only, the arm with the most barrels found (strict) among the
    arms that add no box that is not on its barrel there (against today); a tie goes to the stricter arm."""
    jg.require_train(list(train_stems))
    base_found = sum(_states(s, "off")[0] for s in train_stems)
    base_bad = sum(_states(s, "off")[1] for s in train_stems)
    best, best_found = "off", base_found      # no arm admissible: today
    for arm in FIT_ORDER:
        found = sum(_states(s, arm)[0] for s in train_stems)
        bad = sum(_states(s, arm)[1] for s in train_stems)
        if bad > base_bad:
            continue
        if found > best_found:
            best, best_found = arm, found
    print(f"fit (held out {held_place}): {best} (found {best_found} vs today {base_found} on {len(train_stems)} training frames)", flush=True)
    d = detector_of(best)
    d.describe = f"fit: {best}"
    return d
