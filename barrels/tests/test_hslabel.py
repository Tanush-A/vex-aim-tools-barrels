import dataclasses
import json

import cv2
import numpy as np
import pytest

from barrels import boxfit as bf, hslabel as hl, io, pipeline as pl, splits as sp
from barrels.io import BLUE, ORANGE

ADOPTED = {"orange": {"h_lo": 3, "h_hi": 13, "s_lo": 140}, "blue": {"h_lo": 103, "h_hi": 119, "s_lo": 113}}


def _thr(o=(3, 13, 140), b=(103, 119, 113)) -> dict:
    return {"orange": dict(zip(io.HS_KEYS, o)), "blue": dict(zip(io.HS_KEYS, b))}


def _oracle(bgr: np.ndarray, thr: dict, cfg: pl.Config) -> np.ndarray:
    """The class mask written out independently of pipeline: real (unshifted) hue, the wrap handled by hand."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    keep = v >= cfg.v_min
    keep[:cfg.horizon_row] = False
    cand = {}
    for name, c in (("orange", ORANGE), ("blue", BLUE)):
        t = thr[name]
        in_sector = ((h >= t["h_lo"]) & (h <= t["h_hi"])) | ((h - 180 >= t["h_lo"]) & (h - 180 <= t["h_hi"]))
        cand[c] = keep & in_sector & (s >= t["s_lo"])
    both = cand[ORANGE] & cand[BLUE]
    redder = bgr[..., 2].astype(int) > bgr[..., 0].astype(int)
    mask = np.zeros(h.shape, np.uint8)
    mask[cand[ORANGE] & (~both | redder)] = ORANGE
    mask[cand[BLUE] & (~both | ~redder)] = BLUE
    return mask


def test_adopted_model_gives_the_adopted_numbers_and_round_trips():
    base = hl.adopted_model()
    assert base.cfg.short_hash() == "eb863d84" and (base.cfg.v_min, base.cfg.horizon_row, base.cfg.tie) == (40, 50, "rb_sign")
    assert hl.thresholds_from_model(base) == ADOPTED
    again = hl.model_from_thresholds(base, ADOPTED)
    assert again.boxes == base.boxes and again.cfg is base.cfg and again.inner == base.inner and again.outer == base.outer
    assert again is not base and base.boxes[ORANGE] == bf.Box((33.0, 140.0), (43.0, 255.0))     # the base is not changed


def test_io_hue_ranges_match_the_pipeline_shift():
    assert io.HS_HUE_MIN == {name: -pl.HUE_SHIFT[c] for name, c in hl.CLASS_OF.items()}


def test_model_from_thresholds_writes_shifted_boxes_and_inverts():
    base = hl.adopted_model()
    thr = _thr(o=(-3, 5, 90), b=(98, 125, 60))
    m = hl.model_from_thresholds(base, thr)
    assert m.boxes[ORANGE] == bf.Box((27.0, 90.0), (35.0, 255.0)) and m.boxes[BLUE] == bf.Box((98.0, 60.0), (125.0, 255.0))
    assert hl.thresholds_from_model(m) == thr
    for extreme in (_thr(o=(-30, 149, 0), b=(0, 179, 0)), _thr(o=(-30, -30, 255), b=(179, 179, 255))):
        assert hl.thresholds_from_model(hl.model_from_thresholds(base, extreme)) == extreme


def test_orange_sector_across_the_red_wrap_labels_177_to_5():
    base = hl.adopted_model()
    hues = np.array([170, 176, 177, 178, 179, 0, 1, 5, 6, 12], np.uint8)
    hsv = np.zeros((60, len(hues), 3), np.uint8)
    hsv[..., 0], hsv[..., 1], hsv[..., 2] = hues[None, :], 220, 220
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    seen = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[55, :, 0].astype(int)      # the hue OpenCV reads back from the pixels
    mask, _ = pl.segment(pl.Frame.from_image(bgr), hl.model_from_thresholds(base, _thr(o=(-3, 5, 140))))
    want = np.isin(seen, [177, 178, 179, 0, 1, 2, 3, 4, 5])
    assert ((mask[55] == ORANGE) == want).all() and want.any() and not want.all()
    assert (mask[:50] == 0).all()                                           # the horizon gate is the base model's
    only_wrap, _ = pl.segment(pl.Frame.from_image(bgr), hl.model_from_thresholds(base, _thr(o=(-10, -1, 140))))
    assert ((only_wrap[55] == ORANGE) == (seen >= 170)).all()


@pytest.mark.parametrize("thr", [
    ADOPTED,
    _thr(o=(-3, 5, 100), b=(90, 130, 80)),
    _thr(o=(-30, -1, 0), b=(60, 150, 0)),
    _thr(o=(0, 60, 30), b=(100, 106, 200)),
    _thr(o=(-30, 149, 0), b=(0, 179, 0)),          # every pixel in both sectors: the tie rule decides
    _thr(o=(-20, 40, 50), b=(10, 120, 50)),        # overlapping sectors
])
def test_segmentation_with_hand_thresholds_matches_an_independent_computation(thr):
    base = hl.adopted_model()
    rng = np.random.default_rng(3)
    bgr = rng.integers(0, 256, (120, 160, 3), dtype=np.uint8)
    bgr[60:, :80] = cv2.cvtColor(np.dstack([rng.integers(0, 180, (60, 80)), rng.integers(100, 256, (60, 80)),
                                            rng.integers(30, 256, (60, 80))]).astype(np.uint8), cv2.COLOR_HSV2BGR)
    mask, _ = pl.segment(pl.Frame.from_image(bgr), hl.model_from_thresholds(base, thr))
    want = _oracle(bgr, thr, base.cfg)
    assert (mask == want).all()
    assert (want == ORANGE).any() and (want == BLUE).any()


@pytest.mark.parametrize("bad", [
    _thr(o=(13, 3, 140)),                      # low above high
    _thr(o=(-31, 13, 140)),                    # below orange's line
    _thr(o=(3, 150, 140)),                     # above orange's line
    _thr(b=(-1, 119, 113)),                    # blue has no negative hues
    _thr(b=(103, 180, 113)),
    _thr(o=(3, 13, 256)),
    _thr(b=(103, 119, -1)),
    _thr(o=(3.0, 13, 140)),                    # not an int
    _thr(o=(True, 13, 140)),
    {"orange": {"h_lo": 3, "h_hi": 13}, "blue": ADOPTED["blue"]},
    {"orange": ADOPTED["orange"]},
    [3, 13, 140, 103, 119, 113],
])
def test_bad_thresholds_are_rejected(bad):
    with pytest.raises(ValueError):
        io.validate_hs_thresholds(bad)
    with pytest.raises(ValueError):
        hl.model_from_thresholds(hl.adopted_model(), bad)


def test_models_the_six_numbers_cannot_express_are_rejected():
    base = hl.adopted_model()
    v1 = dataclasses.replace(base, cfg=dataclasses.replace(base.cfg, color_model="rgb_box"))
    with pytest.raises(ValueError):
        hl.model_from_thresholds(v1, ADOPTED)
    with pytest.raises(ValueError):
        hl.thresholds_from_model(v1)
    frac = dataclasses.replace(base, boxes={**base.boxes, ORANGE: bf.Box((33.5, 140.0), (43.0, 255.0))})
    with pytest.raises(ValueError):
        hl.thresholds_from_model(frac)
    capped = dataclasses.replace(base, boxes={**base.boxes, BLUE: bf.Box((103.0, 113.0), (119.0, 200.0))})
    with pytest.raises(ValueError):
        hl.thresholds_from_model(capped)


def test_describe_shows_the_real_hue_of_a_negative_one():
    assert hl.hue_text(-3) == "-3 (=177)" and hl.hue_text(12) == "12"
    assert hl.describe(_thr(o=(-3, 13, 140))) == "orange hue -3..13 (=177..13) S>=140   blue hue 103..119 S>=113"
    assert hl.describe(ADOPTED) == "orange hue 3..13 S>=140   blue hue 103..119 S>=113"


# ---------------------------------------------------------------- frame selection

SPLITS = {"train": ["4A8B_sun_white_core_01", "4A8B_sun_white_occl_01", "4A8B_sun_white_touch_01", "4A8B_sun_white_core_02"],
          "dev": ["4A8B_sun_white_far_01"], "test": ["4A8B_sun_white_clutter_01", "4A8B_sun_white_neg_01"], "measured": []}
STEMS = SPLITS["train"] + SPLITS["dev"] + SPLITS["test"] + ["4A8B_sun_white_calib_01", "4A8B_dim_gray_core_01", "robot_snap3"]


def test_select_default_scenes_keeps_train_frames_and_refuses_the_test_frame():
    sel = hl.select_frames(STEMS, SPLITS)
    assert sel.stems == ["4A8B_sun_white_core_01", "4A8B_sun_white_occl_01"]
    assert sel.refused == {hl.REFUSE_TEST: ["4A8B_sun_white_clutter_01"], hl.REFUSE_NO_SPLIT: ["4A8B_dim_gray_core_01"]}
    assert "make_splits.py" in hl.REFUSE_NO_SPLIT


def test_select_all_scenes_refuses_test_geometry_unassigned_and_other_splits():
    sel = hl.select_frames(STEMS, SPLITS, scenes=None)
    assert sel.stems == sorted(SPLITS["train"])
    assert sel.refused[hl.REFUSE_TEST] == ["4A8B_sun_white_clutter_01", "4A8B_sun_white_neg_01"]
    assert sel.refused[hl.REFUSE_GEOMETRY] == ["4A8B_sun_white_calib_01"]
    assert sel.refused[hl.REFUSE_NO_SPLIT] == ["4A8B_dim_gray_core_01"]
    assert sel.refused[hl.REFUSE_NAME] == ["robot_snap3"]
    assert sel.refused["split dev (only train frames are slider-labeled)"] == ["4A8B_sun_white_far_01"]
    assert not set(sel.stems) & set(SPLITS["test"])


def test_select_by_filter_and_scene_list():
    assert hl.select_frames(STEMS, SPLITS, scenes=("core",)).stems == ["4A8B_sun_white_core_01", "4A8B_sun_white_core_02"]
    assert hl.select_frames(STEMS, SPLITS, scenes=("touch_01", "core_02")).stems == ["4A8B_sun_white_touch_01", "4A8B_sun_white_core_02"]   # in the order given
    named = hl.select_frames(STEMS, SPLITS, scenes=None, filter_="4A8B_sun_white_neg_01")       # asking for a test frame by name
    assert named.stems == [] and named.refused == {hl.REFUSE_TEST: ["4A8B_sun_white_neg_01"]}
    assert hl.select_frames(STEMS, SPLITS, filter_="dim_gray").stems == []
    assert hl.parse_scenes("all") is None and hl.parse_scenes("") == hl.DEFAULT_SCENES == ("core_01", "occl_01", "clutter_01")
    assert hl.parse_scenes(" core_01 , occl_02 ") == ("core_01", "occl_02")


def test_require_labelable_raises_for_everything_but_train():
    hl.require_labelable("4A8B_sun_white_core_01", SPLITS)
    for stem in ("4A8B_sun_white_neg_01", "4A8B_sun_white_calib_01", "4A8B_dim_gray_core_01", "robot_snap3", "4A8B_sun_white_far_01"):
        with pytest.raises(hl.RefusedFrame):
            hl.require_labelable(stem, SPLITS)
    with pytest.raises(hl.RefusedFrame):                        # a test frame is refused even with a geometry-style or odd name
        hl.require_labelable("odd", {"train": [], "test": ["odd"]})


def test_on_the_real_split_file_no_test_frame_is_ever_selected():
    splits = sp.load_splits()
    if not splits["test"]:
        pytest.skip("no data/splits.json here")
    stems = sorted({s for v in splits.values() for s in v})          # names only; nothing is opened
    sel = hl.select_frames(stems, splits, scenes=None)
    assert not set(sel.stems) & set(splits["test"]) and set(sel.stems) == set(splits["train"])
    assert set(sel.refused[hl.REFUSE_TEST]) == set(splits["test"])
    default = hl.select_frames(stems, splits)
    assert default.stems and all(hl.scene_matches(s, hl.DEFAULT_SCENES) and s in splits["train"] for s in default.stems)


# ---------------------------------------------------------------- the label

def test_label_meta_saves_and_loads_with_the_schema(tmp_path):
    base = hl.adopted_model()
    thr = _thr(o=(-3, 13, 120))
    meta = hl.label_meta("4A8B_sun_white_core_01", "abc", thr, base, 4, "1234abc", note="glare")
    p = io.save_hs("4A8B_sun_white_core_01", meta, labels_dir=tmp_path)
    raw = json.loads(p.read_text())
    assert list(raw) == ["version", "stem", "image_sha1", "orange", "blue", "hue_units", "v_min", "horizon_row", "base_model",
                         "detector_git", "boxes_drawn", "criterion", "reviewed", "note"]
    assert raw["orange"] == {"h_lo": -3, "h_hi": 13, "s_lo": 120} and raw["blue"] == ADOPTED["blue"]
    assert (raw["v_min"], raw["horizon_row"], raw["base_model"], raw["detector_git"], raw["boxes_drawn"]) == (40, 50, "eb863d84", "1234abc", 4)
    assert raw["reviewed"] is True and raw["note"] == "glare" and raw["criterion"] == io.HS_CRITERION
    back = io.load_hs("4A8B_sun_white_core_01", labels_dir=tmp_path, raw_dir=tmp_path)
    assert hl.copy_thresholds(back) == thr
    assert hl.thresholds_from_model(hl.model_from_thresholds(base, back)) == thr          # a loaded label builds the model directly


def test_detector_git_is_a_hash_or_unknown():
    g = hl.detector_git()
    assert g == "unknown" or (len(g.split("+")[0]) >= 7 and g.split("+")[-1] in (g, "dirty"))
