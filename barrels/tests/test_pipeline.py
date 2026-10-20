import numpy as np

from barrels import boxfit as bf
from barrels import io, pipeline as pl, viz
from test_labeling import synthetic_scene


def frames_and_masks(n=2):
    fr, ms = [], []
    for i in range(n):
        img, truth = synthetic_scene()
        rng = np.random.default_rng(i)
        img = np.clip(img.astype(int) + rng.normal(0, 4, img.shape), 0, 255).astype(np.uint8)
        fr.append(pl.Frame.from_image(img)); ms.append(truth)
    return fr, ms


def negative_frame():
    neg = np.zeros((120, 160, 3), np.uint8); neg[:] = (30, 30, 30); neg[:40] = (150, 150, 150)
    return pl.Frame.from_image(neg)


def iou(pred, gt, c):
    return ((pred == c) & (gt == c)).sum() / ((pred == c) | (gt == c)).sum()


SMALL = dict(horizon_row=10, bg_rows=(0, 10), table_rows=20, v_min=20)


def test_fit_and_segment_recover_discs():
    fr, ms = frames_and_masks()
    model = pl.fit(fr, ms, pl.Config(**SMALL))
    mask, info = pl.segment(fr[0], model)
    assert set(np.unique(mask)) <= {io.OTHER, io.ORANGE, io.BLUE}
    assert iou(mask, ms[0], io.ORANGE) > 0.95 and iou(mask, ms[0], io.BLUE) > 0.95
    assert info["after_fixed_gates"] > 0 and info["table"]["enabled"] and info["bg"]["enabled"]


def test_negative_frame_is_all_other_and_gray():
    fr, ms = frames_and_masks()
    model = pl.fit(fr, ms, pl.Config(**SMALL))
    mask, _ = pl.segment(negative_frame(), model)
    assert (mask == io.OTHER).all()
    o, b = viz.render_outputs(mask)
    assert (o == 128).all() and (b == 128).all()


def test_horizon_gate_and_all_flags_off():
    fr, ms = frames_and_masks()
    img = fr[0].bgr.copy(); img[:20] = (0, 128, 255)      # paint orange above the horizon
    f = pl.Frame.from_image(img)
    base = pl.Config(bg_rows=(0, 10), table_rows=20, v_min=20, bg_prior=False)
    on = pl.fit(fr, ms, pl.with_overrides(base, horizon_row=25))
    assert not (pl.segment(f, on)[0][:25] == io.ORANGE).any()
    off = pl.fit(fr, ms, pl.with_overrides(base, horizon_row=None))
    assert (pl.segment(f, off)[0][:20] == io.ORANGE).any()
    allflags = pl.Config(horizon_row=None, table_prior=False, bg_prior=False, s_min=0, v_min=0,
                         fit_after_gates=False, fit_max_px_per_image=None)
    m = pl.segment(fr[0], pl.fit(fr, ms, allflags))[0]
    assert set(np.unique(m)) <= {0, 1, 2}


def test_barrel_in_table_band_lowsat_vs_all_and_guard():
    fr, ms = frames_and_masks()
    model = pl.fit(fr, ms, pl.Config(horizon_row=10, bg_rows=(0, 10), table_rows=30, v_min=20, prior_min_frac=0.2))
    img, truth = synthetic_scene()
    img[90:, 20:140] = (0, 128, 255)                      # orange slab = 75 % of the bottom-30 band
    f = pl.Frame.from_image(img)
    m_low, info_low = pl.segment(f, model)
    assert info_low["table"]["enabled"] and abs(info_low["table"]["frac_used"] - 0.25) < 0.03
    assert (m_low[95:, 30:130] == io.ORANGE).mean() > 0.95   # low-sat fit ignores the intrusion
    m_all, info_all = pl.segment(f, pl.Model(pl.with_overrides(model.cfg, prior_fit="all"), model.boxes))
    assert info_all["table"]["enabled"]
    assert (m_all[95:, 30:130] == io.ORANGE).mean() < 0.5     # 'all' fit is poisoned by the slab
    m_g, info_g = pl.segment(f, pl.Model(pl.with_overrides(model.cfg, prior_min_frac=0.5), model.boxes))
    assert not info_g["table"]["enabled"]                    # guard trips: only 25 % of the band usable
    assert (m_g[95:, 30:130] == io.ORANGE).mean() > 0.95


def test_tie_rule():
    fr, ms = frames_and_masks()
    cfg = pl.Config(horizon_row=None, table_prior=False, bg_prior=False, v_min=0, s_min=0)
    model = pl.fit(fr, ms, cfg)
    full = bf.Box((0, 0, 0), (255, 255, 255))
    big = pl.Model(cfg, {io.ORANGE: full, io.BLUE: full})
    img = np.zeros((2, 2, 3), np.uint8); img[0, 0] = (0, 50, 200); img[0, 1] = (200, 50, 0)   # BGR: reddish, bluish
    m, info = pl.segment(pl.Frame.from_image(img), big)
    assert info["both"] == 4 and m[0, 0] == io.ORANGE and m[0, 1] == io.BLUE
    m2, _ = pl.segment(pl.Frame.from_image(img), pl.Model(pl.with_overrides(cfg, tie="blue"), big.boxes))
    assert m2[0, 0] == io.BLUE


def test_config_roundtrip_and_hash():
    cfg = pl.Config(s_min_blue=30, refit=pl.RefitConfig(min_px=10))
    back = pl.Config.from_dict(cfg.to_dict())
    assert back == cfg and back.short_hash() == cfg.short_hash()
    assert pl.Config().short_hash() != cfg.short_hash()
    assert cfg.s_min_for(io.BLUE) == 30 and cfg.s_min_for(io.ORANGE) == 40


def test_refit_engages_on_barrels_and_not_on_negatives():
    fr, ms = frames_and_masks()
    cfg = pl.Config(**SMALL, refit=pl.RefitConfig(min_px=50))
    model = pl.fit(fr, ms, cfg)
    assert model.inner and model.outer
    m, info = pl.segment(fr[0], model)
    # refit with a 1-MAD margin tightens the box on a low-noise synthetic disc (loses anti-aliased
    # edge pixels); whether that helps on real frames is M8's question, not a unit-test question
    assert info["refit"][str(io.ORANGE)]["used"] and iou(m, ms[0], io.ORANGE) > 0.75
    mn, info_n = pl.segment(negative_frame(), model)
    assert (mn == io.OTHER).all() and not info_n["refit"][str(io.ORANGE)]["used"]
    assert info_n["refit"][str(io.ORANGE)]["box"] == model.boxes[io.ORANGE].to_dict()


def test_yuv_chroma_space_runs():
    fr, ms = frames_and_masks()
    model = pl.fit(fr, ms, pl.Config(**SMALL, box_space="yuv_chroma"))
    assert model.boxes[io.ORANGE].dims == 2
    m, _ = pl.segment(fr[1], model)
    assert iou(m, ms[1], io.ORANGE) > 0.9 and iou(m, ms[1], io.BLUE) > 0.9
