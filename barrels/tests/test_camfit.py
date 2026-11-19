"""The ruler calibration fit (barrels.camfit): what a box measures, what the model predicts, and that the
fit gives back the camera that made the data."""
import math

import numpy as np
import pytest

from barrels import camfit as cf
from barrels import geometry as g

TRUE = {"f": 400.0, "tilt_deg": 20.5, "off_mm": 6.0, "height_mm": 40.0, "cy": 240.0, "barrel_h_mm": 24.0}
DISTANCES = (10, 15, 20, 25, 30, 50, 100, 150, 200, 300)


def synth_shots(p=TRUE, distances=DISTANCES):
    """Boxes as the model draws them (not rounded), cut by the frame bottom like the real close shots."""
    shots = []
    for i, d in enumerate(distances):
        top, bottom, w = (cf.predict(p, d, k) for k in ("top", "bottom", "width"))
        y1 = min(bottom, 480.0)
        shots.append(cf.RulerShot(f"s{i:02d}", float(d), (320 - w / 2, top, 320 + w / 2, y1), ("truncated",) if y1 >= 480 else ()))
    return shots


def test_predict_is_the_camera_model_at_the_ruler_distance():
    cam = cf.camera_of(TRUE)
    assert cam.height_mm == 40.0 and cam.f == 400.0 and cam.tilt_deg == 20.5
    d = 100.0
    assert cf.predict(TRUE, d, "bottom") == pytest.approx(cam.point_row(d + 6.0, 0.0))             # base near edge, on the table
    assert cf.predict(TRUE, d, "top") == pytest.approx(cam.point_row(d + 6.0 + 18.0, 24.0))        # lid far edge, 18 mm further, 24 mm up
    assert cf.predict(TRUE, d, "width") == pytest.approx(cam.silhouette_width_px(d + 6.0 + 9.0))   # the axis is 9 mm behind the base's near edge
    with pytest.raises(ValueError):
        cf.predict(TRUE, d, "height")
    assert cf.NOMINAL_OFF_MM == 3.0                                                                # aim_kin: camera 27 mm ahead of the centre, front edge at 30
    assert cf.params_of(g.AIM_4A8B6118_BOXFIT)["off_mm"] == 3.0


def test_observations_leave_out_edges_on_the_frame_border_and_held_shots():
    shots = [cf.RulerShot("a", 100.0, (280, 150, 360, 240)),                    # all three
             cf.RulerShot("b", 20.0, (190, 236, 440, 480), ("truncated",)),      # cut by the frame bottom: no bottom row
             cf.RulerShot("c", 5.0, (0, 300, 640, 480), ("truncated",)),         # cut at the sides too: the top row only
             cf.RulerShot("d", 0.0, (93, 334, 511, 480), ("truncated", "held"))]  # in the kicker: left out
    obs = cf.observations(shots)
    assert [(o.stem, o.kind) for o in obs] == [("a", "top"), ("a", "bottom"), ("a", "width"), ("b", "top"), ("b", "width"), ("c", "top")]
    assert [o.value for o in obs if o.stem == "a"] == [150.0, 240.0, 80.0]
    assert {o.stem for o in cf.observations(shots, skip_flags=())} == {"a", "b", "c", "d"}


def test_sigma_adds_the_placement_error_where_a_millimetre_is_many_pixels():
    near, far = cf.Obs("n", 10.0, "top", 0.0), cf.Obs("f", 300.0, "top", 0.0)
    assert cf.sigma(TRUE, far, 1.5, 1.0) == pytest.approx(1.5, abs=0.05)        # at 30 cm a millimetre is a tenth of a pixel
    assert cf.sigma(TRUE, near, 1.5, 1.0) > 3.0                                 # at 1 cm it is several pixels
    assert cf.sigma(TRUE, near, 1.5, 0.0) == 1.5                                # no placement error asked for
    assert cf.sigma(TRUE, cf.Obs("n", 30.0, "bottom", 0.0), 1.5, 1.0) > cf.sigma(TRUE, cf.Obs("n", 30.0, "top", 0.0), 1.5, 1.0)


def test_fit_gives_back_the_camera_that_made_the_boxes():
    obs = cf.observations(synth_shots())
    start = cf.params_of(g.AIM_4A8B6118_BOXFIT)
    fr = cf.fit(obs, start, free=("tilt_deg", "off_mm", "height_mm"))
    assert fr.params["tilt_deg"] == pytest.approx(20.5, abs=1e-3)
    assert fr.params["off_mm"] == pytest.approx(6.0, abs=1e-2)
    assert fr.params["height_mm"] == pytest.approx(40.0, abs=1e-2)
    assert fr.params["f"] == 400.0 and fr.params["cy"] == 240.0                 # held
    assert fr.rms_px < 1e-3 and fr.dof == len(obs) - 3
    assert fr.camera.horizon_row() == pytest.approx(cf.camera_of(TRUE).horizon_row(), abs=0.01)
    # the focal length too, from a start 10 % off
    fr4 = cf.fit(obs, {**start, "f": 360.0}, free=("f", "tilt_deg", "off_mm", "height_mm"))
    assert fr4.params["f"] == pytest.approx(400.0, abs=0.05) and fr4.params["height_mm"] == pytest.approx(40.0, abs=0.02)


def test_fit_with_nothing_free_is_the_residuals_of_the_start():
    obs = cf.observations(synth_shots())
    fr = cf.fit(obs, TRUE, free=())
    assert fr.rms_px == pytest.approx(0.0, abs=1e-9) and fr.dof == len(obs)
    old = cf.fit(obs, cf.params_of(g.AIM_4A8B6118_BOXFIT), free=())
    assert old.rms_px > 3 and np.allclose(old.res_px, cf.residuals_px(cf.params_of(g.AIM_4A8B6118_BOXFIT), obs))


def test_fit_under_box_noise_stays_within_its_own_error_bars():
    rng = np.random.default_rng(3)
    obs = [cf.Obs(o.stem, o.d_ruler_mm, o.kind, o.value + rng.normal(0, 1.0)) for o in cf.observations(synth_shots())]
    fr = cf.fit(obs, cf.params_of(g.AIM_4A8B6118_BOXFIT), free=("tilt_deg", "off_mm", "height_mm"), sigma_px=1.0, sigma_d_mm=0.0)
    for k, true in (("tilt_deg", 20.5), ("off_mm", 6.0), ("height_mm", 40.0)):
        assert abs(fr.params[k] - true) < 4 * fr.stderr[k] + 1e-6, k
    assert 0.5 < fr.rms_weighted < 1.6
    assert fr.corr.shape == (3, 3) and np.allclose(np.diag(fr.corr), 1.0)


def test_fit_refuses_unknown_parameters_and_too_few_observations():
    obs = cf.observations(synth_shots())
    with pytest.raises(ValueError):
        cf.fit(obs, TRUE, free=("roll",))
    with pytest.raises(ValueError):
        cf.fit(obs[:2], TRUE, free=("f", "tilt_deg", "off_mm"))


def test_leave_one_out_and_jitter_shapes():
    obs = cf.observations(synth_shots())
    loo = cf.leave_one_out(obs, TRUE, ("tilt_deg", "height_mm"))
    assert sorted(loo) == sorted({o.stem for o in obs})
    assert all(len(fr.obs) < len(obs) and fr.params["tilt_deg"] == pytest.approx(20.5, abs=1e-3) for fr in loo.values())
    J = cf.jitter(obs, TRUE, ("tilt_deg", "height_mm"), n=8, seed=1)
    assert J.shape == (8, 2) and 0 < J[:, 0].std() < 1.0
    assert np.array_equal(J, cf.jitter(obs, TRUE, ("tilt_deg", "height_mm"), n=8, seed=1))         # seeded


def test_the_ruler_set_on_disk():
    """data/calib.csv and the 12 box labels: geometry-only frames, in no split."""
    from barrels import splits
    shots = cf.load_ruler_set()
    assert len(shots) == 12 and [s.d_ruler_mm for s in shots] == [0, 10, 10, 15, 20, 25, 30, 50, 100, 150, 200, 300]
    sp = splits.load_splits()
    assert not {s.stem for s in shots} & {x for v in sp.values() for x in v}
    assert [s.stem for s in shots if "held" in s.flags] == ["4A8B_lampmid6_wood_calib_01"]
    obs = cf.observations(shots)
    assert sum(o.kind == "top" for o in obs) == 11 and sum(o.kind == "bottom" for o in obs) == 6 and sum(o.kind == "width" for o in obs) == 11
    assert all(math.isfinite(o.value) for o in obs)
