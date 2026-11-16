import numpy as np

from barrels import hshist as hh
from barrels.io import BLUE, ORANGE


def test_planes_roll_and_unroll():
    bgr = np.zeros((2, 2, 3), np.uint8)
    bgr[0, 0] = (0, 128, 255)       # orange: hue 15
    bgr[0, 1] = (255, 0, 0)         # blue: hue 120
    bgr[1, 0] = (40, 0, 255)        # red just below the wrap: hue 175
    h, s, v = hh.planes(bgr)
    assert h[0, 0] == 45 and h[0, 1] == 150 and h[1, 0] == (175 + 30) % 180
    assert s[0, 0] == 255 and v[0, 1] == 255 and s[1, 1] == 0
    assert list(hh.unroll([45, 150, 25, 27, 0])) == [15, 120, -5, -3, -30]      # 175 reads as -5, 177 as -3


def test_fine_hist_and_rebin_keep_every_pixel():
    rng = np.random.default_rng(0)
    h, s, v = rng.integers(0, 180, (40, 50)), rng.integers(0, 256, (40, 50)), rng.integers(0, 256, (40, 50))
    sel = rng.random((40, 50)) < 0.7
    a = hh.fine_hist(h, s, v, sel)
    assert a.shape == (hh.NH, hh.NS, hh.NV) and a.sum() == sel.sum()
    assert a[h[3, 4], s[3, 4] >> 1, v[3, 4] >> 3] >= int(sel[3, 4])
    for bins in ((16, 16), (36, 32), (180, 128)):
        assert hh.rebin(a, *bins).shape == bins and hh.rebin(a, *bins).sum() == a.sum()
    b3 = hh.rebin(a, 36, 32, 8)
    assert b3.shape == (36, 32, 8) and b3.sum() == a.sum()
    assert np.array_equal(b3.sum(2), hh.rebin(a, 36, 32))
    one = np.zeros((hh.NH, hh.NS, hh.NV), np.int64); one[179, 127, 31] = 5; one[0, 0, 0] = 2
    r = hh.rebin(one, 16, 16)
    assert r[15, 15] == 5 and r[0, 0] == 2


def test_region_masks_core_rest_and_occluded():
    barrels = [{"color": "orange", "bbox": [10, 10, 30, 50], "flags": []},
               {"color": "blue", "bbox": [26, 10, 46, 50], "flags": []},              # overlaps the orange box by 4 px
               {"color": "blue", "bbox": [60, 10, 80, 50], "flags": ["occluded"]}]
    m = hh.region_masks((60, 100), barrels)
    assert hh.core_of([10, 10, 30, 50]) == (14, 14, 26, 46)
    assert m[ORANGE][20, 20] and not m[ORANGE][20, 12] and not m[ORANGE][12, 20]       # inner 0.6 x 0.8 only
    assert not m[ORANGE][:, 26:].any()                                                 # never inside another box
    assert m[BLUE][20, 36] and not m[BLUE][:, 60:].any()                               # an occluded box gives no core
    assert not m["rest"][20, 70] and not m["rest"][8, 20] and m["rest"][2, 20] and m["rest"][55, 90]   # padded boxes are not rest


def test_wpct_and_recall_at_flood():
    assert hh.wpct(np.array([0, 10, 0, 10, 0]), np.arange(5.0), (5, 50, 95)) == [1.0, 1.0, 3.0]
    assert np.isnan(hh.wpct(np.zeros(4), np.arange(4.0), (50,))[0])
    body, rest = np.zeros((4, 4)), np.zeros((4, 4))
    body[0, 0] = 100; rest[3, 3] = 1000
    assert hh.recall_at_flood(body, rest) == 1.0                                       # disjoint: all of it for free
    body2 = np.full((4, 4), 10.0); rest2 = np.full((4, 4), 1000.0)
    assert hh.recall_at_flood(body2, rest2, flood=0.25) == 0.25                        # same distribution: recall = flood
    mixed = np.zeros((4, 4)); mixed[0, 0] = 60; mixed[1, 1] = 40
    r3 = np.zeros((4, 4)); r3[1, 1] = 500; r3[2, 2] = 500
    assert hh.recall_at_flood(mixed, r3, flood=0.01) == 0.6                            # the shared bin costs too much
    assert hh.best_bins(mixed, r3, 0.6)[1, 1]


def test_sethist_body_window_follows_the_tallest_hue_peak():
    sh = hh.SetHist("t")
    sh.core[ORANGE][38, 100, 20] = 900       # body color at rolled hue 38
    sh.core[ORANGE][140, 100, 20] = 200      # the stripe of the other color inside the core
    sh.core[ORANGE][38, 100, 2] = 100        # too dark for the model (V < 40)
    sh.core_pass[ORANGE][38, 100, 20] = 450
    sh.rest[60, 10, 20] = 1000
    st = sh.stats(ORANGE)
    assert st["n"] == 900 and st["h50"] == 8 and abs(st["pass"] - 0.5) < 1e-9
    assert abs(st["bright"] - 1100 / 1200) < 1e-9
    assert sh.window(ORANGE)[38] and not sh.window(ORANGE)[140]
    assert hh.recall_at_flood(hh.rebin(sh.body(ORANGE), 36, 32), hh.rebin(sh.rest_gated(), 36, 32)) == 1.0
