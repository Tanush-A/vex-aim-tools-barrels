import json

import numpy as np

from barrels import cv, eval as ev, io, pipeline as pl
from test_labeling import synthetic_scene


def make_dataset():
    frames, masks, scenes = {}, {}, {}
    specs = [("4A8B_window_light_core_01", "core", 1), ("4A8B_window_light_core_02", "core", 2),
             ("4A8B_window_light_far_01", "far", 3), ("4A8B_window_light_neg_01", "neg", None),
             ("4A8B_window_light_top_01", "top", 4)]
    for stem, scene, seed in specs:
        if seed is None:
            img = np.zeros((120, 160, 3), np.uint8); img[:] = (30, 30, 30); img[:40] = (150, 150, 150)
            truth = np.zeros((120, 160), np.uint8)
        else:
            img, truth = synthetic_scene()
            img = np.clip(img.astype(int) + np.random.default_rng(seed).normal(0, 4, img.shape), 0, 255).astype(np.uint8)
        frames[stem] = pl.Frame.from_image(img); masks[stem] = truth; scenes[stem] = scene
    return cv.Dataset.from_arrays(frames, masks, scenes)


CFG = pl.Config(horizon_row=10, bg_rows=(0, 10), table_rows=20, v_min=20)


def test_loso_folds_hold_each_scene_out_once():
    ds = make_dataset()
    folds = cv.loso_folds(ds.stems, ds.scene)
    assert [f.name for f in folds] == ["core", "far", "neg", "top"]
    held = [s for f in folds for s in f.held_out]
    assert sorted(held) == sorted(ds.stems)
    core = next(f for f in folds if f.name == "core")
    assert set(core.held_out) == {"4A8B_window_light_core_01", "4A8B_window_light_core_02"}
    assert not set(core.held_out) & set(core.train)
    assert folds == cv.loso_folds(list(reversed(ds.stems)), ds.scene)


def test_grouped_kfold_never_splits_a_scene():
    ds = make_dataset()
    folds = cv.grouped_kfold(ds.stems, ds.scene, k=2, seed=0)
    assert sorted(s for f in folds for s in f.held_out) == sorted(ds.stems)
    for f in folds:
        scenes = {ds.scene[s] for s in f.held_out}
        for s in ds.stems:
            if ds.scene[s] in scenes:
                assert s in f.held_out


def test_cross_validate_scores_and_excludes_out_of_scope():
    ds = make_dataset()
    res = cv.cross_validate(ds, CFG)
    assert len(res.results) == 5 and set(res.preds) == set(ds.stems)
    sc = res.score()
    for k in cv.SCORE_KEYS:
        assert k in sc
    assert sc["primary"] > 0.9 and not sc["disqualified"]
    assert sc["neg_fp_o"] == 0.0 and sc["neg_fp_b"] == 0.0
    # pooled IoU over in-scope positives equals ev.aggregate on those results
    in_pos = [r for r in res.results if not r.negative and ds.scene[r.name] != "top"]
    assert abs(sc["iou_o"] - ev.aggregate(in_pos)["ALL"].pos[io.ORANGE].iou) < 1e-12
    assert sc["n_pos_folds"] == 2                                 # core + far; top excluded, neg has no positives
    assert not np.isnan(sc["oos_iou_o"])


def test_write_cv_results_and_run_configs(tmp_path):
    ds = make_dataset()
    folds = cv.loso_folds(ds.stems, ds.scene)
    res = cv.cross_validate(ds, CFG, folds)
    md = cv.write_cv_results(res, tmp_path / "run", title="t")
    assert md.exists() and (tmp_path / "run" / "config.json").exists() and (tmp_path / "run" / "per_image.csv").exists()
    cfgj = json.load((tmp_path / "run" / "config.json").open())
    assert cfgj["config_hash"] == CFG.short_hash() and len(cfgj["folds"]) == 4
    rows = cv.sweep(ds, CFG, {"s_min": [30, 50]}, folds, tmp_path / "sweep.csv", tmp_path / "configs")
    assert [r["axis"] for r in rows] == ["base", "s_min", "s_min"]
    lines = (tmp_path / "sweep.csv").read_text().strip().splitlines()
    assert len(lines) == 4 and lines[0].startswith("id,axis,value,primary")
    assert len(list((tmp_path / "configs").glob("*.json"))) == 3
    # fresh_dir never overwrites
    assert cv.fresh_dir(tmp_path / "run").name == "run_2"


def test_fit_final_and_predict():
    ds = make_dataset()
    pool = cv.Dataset.from_arrays({s: ds.frames[s] for s in ds.stems[:3]}, {s: ds.masks[s] for s in ds.stems[:3]}, {s: ds.scene[s] for s in ds.stems[:3]})
    test = cv.Dataset.from_arrays({s: ds.frames[s] for s in ds.stems[3:]}, {s: ds.masks[s] for s in ds.stems[3:]}, {s: ds.scene[s] for s in ds.stems[3:]})
    model, results, preds, infos = cv.fit_final_and_predict(pool, test, CFG)
    assert [r.name for r in results] == test.stems and set(preds) == set(test.stems)
    assert results[0].negative and results[0].counts[io.ORANGE].fp == 0
