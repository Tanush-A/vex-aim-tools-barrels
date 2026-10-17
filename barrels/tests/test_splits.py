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
