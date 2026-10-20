import numpy as np

from barrels import priors


def band_image(color=(120, 125, 110), noise=5.0, h=60, w=80, seed=0):
    rng = np.random.default_rng(seed)
    img = np.array(color, float) + rng.normal(0, noise, (h, w, 3))
    return np.clip(img, 0, 255).astype(np.int16)


def test_band_stats_recovers_color_and_scale():
    img = band_image()
    st = priors.band_stats(img, slice(0, 60))
    assert st.enabled and st.n_used == 60 * 80 and st.frac_used == 1.0
    assert np.abs(st.median - np.array([120, 125, 110])).max() <= 1.5
    assert np.abs(st.scale - 5.0).max() < 1.5          # 1.4826 * MAD ~ sigma


def test_scale_floor_on_flat_band():
    img = np.full((20, 20, 3), 100, np.int16)
    st = priors.band_stats(img, slice(0, 20), scale_floor=4.0)
    assert st.enabled and (st.scale == 4.0).all()


def test_contamination_below_half_keeps_median_near_band():
    img = band_image()
    img[:, :32] = (255, 128, 0)                           # 40% of the band is barrel-orange
    st = priors.band_stats(img, slice(0, 60))
    # a median is bounded under <50% contamination but biased by up to ~1 sigma (5 here);
    # it must stay near the table, nowhere near the orange
    assert np.abs(st.median - np.array([120, 125, 110])).max() <= 6
    assert st.median[0] < 140 and st.median[2] > 95


def test_fit_mask_and_guard():
    img = band_image()
    img[:, :48] = (255, 128, 0)                           # 60% intrusion
    sat = img.max(-1) - img.min(-1)
    st = priors.band_stats(img, slice(0, 60), fit_mask=sat < 40)
    assert st.enabled and abs(st.frac_used - 0.4) < 0.01 # only the table pixels were used
    assert np.abs(st.median - np.array([120, 125, 110])).max() <= 2
    st2 = priors.band_stats(img, slice(0, 60), fit_mask=sat < 40, min_frac=0.5)
    assert not st2.enabled                                # guard trips below min_frac


def test_reject_like_separates_band_from_far_colors():
    img = band_image(h=100)
    img[80:, :] = (255, 128, 0)
    st = priors.band_stats(img, slice(0, 60))
    rej = priors.reject_like(img, st, k=3.0)
    assert rej[:60].mean() > 0.95                         # the band itself is rejected
    assert not rej[80:].any()                             # orange is kept
    disabled = priors.BandStats(st.median, st.scale, 0, 0.0, False)
    assert not priors.reject_like(img, disabled, 3.0).any()
