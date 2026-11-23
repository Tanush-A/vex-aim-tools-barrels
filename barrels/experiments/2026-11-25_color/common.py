"""Shared helpers of the 2026-11-25 color experiment (gates, sweep, relation, candidates, vendor).

Frame selection is train-only: every list is built from ``data/splits.json`` "train" and the box labels, and any
test frame raises before an image is read. Nothing here changes the image.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))

from barrels import conditions as cond  # noqa: E402
from barrels import io  # noqa: E402
from barrels import report as rp  # noqa: E402
from barrels import splits as sp  # noqa: E402

RESULTS = BARRELS / "results" / "2026-11-25_color"

# condition classes (DECISIONS 2026-11-24 + the parked sets)
EXTREME = {"window_black", "lampmid3_ottoman"}
_WOOD_LAMP = re.compile(r"^lamp[a-z]+\d_wood$")
_DIM1 = re.compile(r"^lamp[a-z]+1_")
INDICATIVE_PREFIX = ("DAVE",)


def condition_of(stem: str) -> str:
    t = io.parse_name(stem)
    return f"{t['light']}_{t['surface']}"


def class_of(key: str) -> str:
    """ordinary / extreme / excluded (lamp brightness 1)."""
    if _DIM1.match(key):
        return "excluded"
    if key in EXTREME or _WOOD_LAMP.match(key):
        return "extreme"
    return "ordinary"


def place_of(key: str) -> str:
    return cond.info(key).place


def light_of(key: str) -> str:
    return cond.info(key).light


def train_stems_with_boxes() -> list[str]:
    """Every train frame with a box label (Dave's frames and geometry frames left out). Raises on a test frame."""
    splits = sp.load_splits()
    train = set(splits["train"])
    test = set(splits["test"])
    out = []
    for s in rp.labeled_stems():
        if s in test:
            continue
        if s not in train:
            continue
        try:
            t = io.parse_name(s)
        except ValueError:
            continue
        if t["scene"] in sp.UNASSIGNED_SCENES or t["robot"].upper().startswith(INDICATIVE_PREFIX):
            continue
        out.append(s)
    assert not (set(out) & test)
    return sorted(out)


def slider_stems() -> list[str]:
    """Train frames with both a slider label and a box label."""
    train = set(train_stems_with_boxes())
    return sorted(s for s in train if io.hs_path(s).exists())


def require_train(stem: str) -> None:
    splits = sp.load_splits()
    if stem in splits["test"] or stem not in splits["train"]:
        raise RuntimeError(f"{stem}: not a train frame; refused before reading")


def load(stem: str):
    """(bgr image, box label) of a TRAIN frame."""
    require_train(stem)
    return io.load_image(io.find_image(stem)), io.load_boxes(stem, check_image=False)


# ---------------------------------------------------------------- where a barrel's colors are in its box

STRIPE = (0.42, 0.58)      # the stripe's inner rows, as a share of the box height from the bottom (stripe 9-15 mm of 24)
BODY = ((0.15, 0.30), (0.70, 0.85))   # body rows (below and above the stripe), inside the core
CORE_X = 0.15              # columns: the box minus this share at each side


def expected_regions(box: dict, shape, cam=None) -> dict[str, np.ndarray]:
    """{'body': mask, 'stripe': mask} of one hand box: the pixels that should be the body color and the stripe color
    (the other color). Columns: the core. Rows: where the camera geometry puts the stripe for a barrel whose base is
    at the box's bottom row, as shares of the predicted height applied to the box (so a box a little taller or shorter
    than predicted is followed); the stripe's middle half, and the body from 15 % below the top to a quarter stripe
    above the stripe and from a quarter stripe below it to 10 % above the bottom."""
    from barrels import geometry as geo
    cam = cam or geo.AIM_4A8B6118_BOXFIT
    h, w = shape[:2]
    x0, y0, x1, y1 = (int(v) for v in box["bbox"])
    bh, bw = y1 - y0, x1 - x0
    dx = int(round(CORE_X * bw))
    r = cam.barrel_rows(cam.d_axis_from_bottom_row(y1))
    ph = r.bottom - r.top
    fr = lambda row: (row - r.top) / ph  # noqa: E731
    st, sb = fr(r.stripe_top), fr(r.stripe_bottom)
    q = (sb - st) / 4
    bands = {"stripe": ((st + q, sb - q),), "body": ((0.15, st - q), (sb + q, 0.90))}
    out = {}
    for name, bb in bands.items():
        m = np.zeros((h, w), bool)
        for lo, hi in bb:
            ya, yb = int(round(y0 + lo * bh)), int(round(y0 + hi * bh))
            if yb > ya:
                m[max(0, ya):max(0, yb), max(0, x0 + dx):max(0, x1 - dx)] = True
        out[name] = m
    return out


OTHER_COLOR = {"orange": "blue", "blue": "orange"}
