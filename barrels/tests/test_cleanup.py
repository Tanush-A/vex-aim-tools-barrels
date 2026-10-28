import json

import cv2
import numpy as np

from barrels import cleanup, io, pipeline as pl


def scene():
    m = np.full((60, 80), io.OTHER, np.uint8)
    cv2.circle(m, (30, 30), 15, int(io.ORANGE), -1)        # big disc
    m[5:7, 70:73] = io.ORANGE                                # 6-px speck
    m[40:42, 60:75] = io.BLUE                                # a 2-px-thick blue bar (opening removes it)
    m[28:31, 28:33] = io.OTHER                               # hole inside the disc
    return m


def test_remove_small_blobs():
    m = scene()
    out = cleanup.remove_small_blobs(m, 10)
    assert (out[5:7, 70:73] == io.OTHER).all() and (out == io.ORANGE).sum() == (m == io.ORANGE).sum() - 6
    assert (cleanup.remove_small_blobs(m, 0) == m).all()


def test_open_mask_removes_thin_bridge_keeps_disc():
    m = scene()
    out = cleanup.open_mask(m, 5)
    assert not (out == io.BLUE).any()                        # the 2-px bar is gone
    assert (out == io.ORANGE).sum() > 0.9 * (m == io.ORANGE).sum()
    assert (cleanup.open_mask(m, 1) == m).all()


def test_fill_holes_only_enclosed_pure_holes():
    m = scene()
    out = cleanup.fill_holes(m)
    assert (out[28:31, 28:33] == io.ORANGE).all()
    m2 = scene(); m2[29, 30] = io.BLUE                       # hole containing the other class stays
    assert (cleanup.fill_holes(m2)[28, 28] == io.OTHER)
    m3 = np.full((20, 20), io.ORANGE, np.uint8); m3[0:5, 8:12] = io.OTHER   # notch touching the border
    assert (cleanup.fill_holes(m3)[0:5, 8:12] == io.OTHER).all()


def test_apply_and_config_hash_preserved():
    m = scene()
    assert (cleanup.apply(m, pl.Config()) == m).all()        # all off = identity
    cfg = pl.Config(min_blob_px=10, fill_holes=True)
    out = cleanup.apply(m, cfg)
    assert (out[5:7, 70:73] == io.OTHER).all() and (out[28:31, 28:33] == io.ORANGE).all()
    # the v1 final config's hash must survive the new fields
    p = io.PKG_ROOT / "results" / "2026-10-20_v1_adaptive_cv" / "configs" / "afd85483.json"
    assert pl.Config.from_dict(json.load(p.open())).short_hash() == "afd85483"
    assert pl.Config(min_blob_px=10).short_hash() != pl.Config().short_hash()
