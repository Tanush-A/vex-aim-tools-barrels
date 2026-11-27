"""Two example candidates for the standard pass rule (``tools/judge.py``, ``src/barrels/judge.py``), to copy from.

    python barrels/tools/judge.py --cand-callable barrels/experiments/2026-11-26_judge/example_candidate.py:detect_frame --no-save
    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_judge/example_candidate.py:fit --no-save

1. ``detect_frame(stem, frame) -> list[Barrel]``: a whole pipeline as one function. This one is today's pipeline
   written out (color step, then the rule detector), so the judge answers NO CLEAR DIFFERENCE with nothing changed.
   Replace either step with your own. ``frame`` is a ``barrels.pipeline.Frame``: ``frame.rgb`` is the picture
   (H x W x 3, R G B, read-only: no step may change a pixel), ``frame.bgr`` the same in OpenCV order.
2. ``fit(train_stems, held_place) -> detect_frame``: a candidate with a fitted number. The judge calls it once per
   place with the ordinary train frames of the OTHER places; what it returns is run on the held-out place only. This
   one picks the blue saturation floor (113, the adopted one, or 100) that finds more barrels on the training frames.
   It is a toy, not a proposal.

Rules for a fit function: read frames with ``judge.load_frame(stem)`` (it refuses anything but train frames) and
labels with ``io.load_boxes(stem)``; use only the stems you were given.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
MODEL = hl.adopted_model()              # the adopted color model (config eb863d84)


def detect_frame(stem: str, frame) -> list:
    """Today's pipeline, written out: the color step, then the rule detector."""
    mask, _ = pl.segment(frame, MODEL)                      # every pixel orange (1), blue (2) or other (0)
    return det.detect(mask, det.DetConfig(), CAM)           # one Barrel (color, box) per barrel


# ---------------------------------------------------------------- a candidate with one fitted number

FLOORS = (113, 100)                     # the blue saturation floor: the adopted value, and a lower one
_found: dict = {}                       # (stem, floor) -> barrels found there; kept between folds, so each frame is run once


def _model(blue_s_lo: int) -> pl.Model:
    t = hl.thresholds_from_model(MODEL)
    t["blue"]["s_lo"] = blue_s_lo
    return hl.model_from_thresholds(MODEL, t)


def _found_on(stem: str, floor: int) -> int:
    if (stem, floor) not in _found:
        frame = jg.load_frame(stem)                         # refuses anything but a train frame
        gts = dtp.barrels_from_boxes(io.load_boxes(stem, check_image=False))
        preds = det.detect(pl.segment(frame, _model(floor))[0], det.DetConfig(), CAM)
        _found[(stem, floor)] = sum(ed.evaluate_frame(stem, preds, gts, rule="v2").tp.values())
    return _found[(stem, floor)]


def fit(train_stems: list[str], held_place: str):
    """Pick the floor on the training places; return the detector that uses it on the held-out place."""
    best = max(FLOORS, key=lambda f: (sum(_found_on(s, f) for s in train_stems), f == FLOORS[0]))      # a tie keeps the adopted value
    model = _model(best)

    def detect(stem: str, frame) -> list:
        return det.detect(pl.segment(frame, model)[0], det.DetConfig(), CAM)
    detect.describe = f"blue saturation floor {best}, picked without {held_place}"
    return detect
