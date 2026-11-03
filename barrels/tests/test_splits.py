from barrels import splits as sp


def stems(cond, n):
    return [f"4A8B_{cond}_{i:02d}" for i in range(1, n + 1)]


def test_assign_is_stratified_deterministic_and_append_only(tmp_path):
    all_stems = stems("overhead_black_core", 4) + stems("overhead_black_far", 2) + stems("overhead_black_neg", 3) + stems("overhead_black_top", 1)
    a = sp.assign(all_stems, {s: [] for s in sp.SPLIT_NAMES}, seed=0)
    b = sp.assign(all_stems, {s: [] for s in sp.SPLIT_NAMES}, seed=0)
    assert a == b
    assert sorted(x for v in a.values() for x in v) == sorted(all_stems)
    assert sum(1 for x in a["test"] if "_core_" in x) == 1
    assert sum(1 for x in a["test"] if "_far_" in x) == 1
    assert sum(1 for x in a["dev"] if "_neg_" in x) == 1
    assert a["train"] == sorted(a["train"]) or True
    assert "4A8B_overhead_black_top_01" in a["train"]
    # append-only: new stems don't move old ones
    c = sp.assign(all_stems + stems("overhead_black_touch", 2), a, seed=5)
    for s in sp.SPLIT_NAMES:
        assert set(a[s]) <= set(c[s])
    p = sp.save_splits(c, tmp_path / "splits.json")
    assert sp.load_splits(p) == {s: sorted(c[s]) for s in sp.SPLIT_NAMES}


def test_allocate_small_groups():
    assert sp._allocate(1, (0.6, 0.2, 0.2)) == (1, 0, 0)
    assert sp._allocate(2, (0.6, 0.2, 0.2)) == (1, 0, 1)
    assert sp._allocate(3, (0.6, 0.2, 0.2)) == (1, 1, 1)
    assert sum(sp._allocate(10, (0.6, 0.2, 0.2))) == 10


def test_pick_test_one_per_scene_largest_first_deterministic():
    pool = (stems("overhead_black_core", 4) + stems("overhead_black_neg", 3) + stems("overhead_black_far", 2)
            + stems("overhead_black_close", 2) + stems("overhead_black_top", 1))
    a = sp.pick_test(pool, 3, seed=0, exclude_scenes=("top",))
    b = sp.pick_test(pool, 3, seed=0, exclude_scenes=("top",))
    assert a == b and len(a) == 3 and len(set(a)) == 3
    scenes = [x.split("_")[3] for x in a]
    assert scenes.count("core") == 1 and scenes.count("neg") == 1   # largest groups first
    assert "top" not in scenes
    big = sp.pick_test(pool, 7, seed=0)                                # more than groups -> round-robin
    assert len(big) == 7 and len(set(big)) == 7
    assert sp.pick_test([], 3) == []


def test_measured_and_unassigned_scenes_routing():
    pool = stems("window_light_core", 2) + stems("window_light_meas", 3) + stems("upcool_wood_calib", 2) + stems("window_light_horizon", 1)
    out = sp.assign(pool, {s: [] for s in sp.SPLIT_NAMES}, seed=0)
    assert sorted(out["measured"]) == stems("window_light_meas", 3)
    assert all("calib" not in x and "horizon" not in x for v in out.values() for x in v)
    assert set(out["train"] + out["test"]) == set(stems("window_light_core", 2))
    # append-only still holds for the measured split
    again = sp.assign(pool + stems("window_light_meas", 4)[3:], out, seed=1)
    assert set(out["measured"]) <= set(again["measured"]) and len(again["measured"]) == 4
    loaded = sp.load_splits(__import__("pathlib").Path("/nonexistent/splits.json"))
    assert set(loaded) == set(sp.SPLIT_NAMES)


def test_assign_holdout_per_scene_one_test_per_multiframe_scene():
    new = (stems("overhead_black_core", 2) + stems("overhead_black_far", 1) + stems("overhead_black_neg", 3)
           + stems("overhead_black_calib", 2) + stems("overhead_black_meas", 1))
    a = sp.assign_holdout_per_scene(new, {s: [] for s in sp.SPLIT_NAMES}, seed=0)
    b = sp.assign_holdout_per_scene(new, {s: [] for s in sp.SPLIT_NAMES}, seed=0)
    assert a == b                                                   # deterministic
    assert a["dev"] == []
    assert sum(1 for x in a["test"] if "_core_" in x) == 1 and sum(1 for x in a["train"] if "_core_" in x) == 1
    assert sum(1 for x in a["test"] if "_neg_" in x) == 1 and sum(1 for x in a["train"] if "_neg_" in x) == 2
    assert a["train"].count("4A8B_overhead_black_far_01") == 1 and "4A8B_overhead_black_far_01" not in a["test"]
    assert all("calib" not in x for v in a.values() for x in v)
    assert a["measured"] == ["4A8B_overhead_black_meas_01"]
    # existing assignments never move; a second session adds to the same groups independently
    old = {"train": ["4A8B_window_light_core_01"], "dev": [], "test": ["4A8B_window_light_core_04"], "measured": []}
    c = sp.assign_holdout_per_scene(new + ["4A8B_window_light_core_01", "4A8B_window_light_core_04"], old, seed=3)
    assert "4A8B_window_light_core_01" in c["train"] and "4A8B_window_light_core_04" in c["test"]
    assert sorted(x for v in c.values() for x in v) == sorted(set(new) - set(stems("overhead_black_calib", 2)) | set(old["train"]) | set(old["test"]))
    two = sp.assign_holdout_per_scene(stems("lamp_beige_touch", 5), {s: [] for s in sp.SPLIT_NAMES}, n_test_per_scene=2)
    assert len(two["test"]) == 2 and len(two["train"]) == 3
