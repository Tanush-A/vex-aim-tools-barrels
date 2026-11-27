"""The box-level rules of the fusion experiment (``barrels.fusion``): infrastructure, not a method."""
from barrels import fusion as fu
from barrels.detect_types import Barrel
from barrels.io import BLUE, ORANGE


def it(method, bbox, color=ORANGE, **m):
    return fu.Item(Barrel(color, bbox), method, dict(m))


def test_checks_remove_speckle_and_labels_only():
    assert fu.removes({"solid": 0.3}, fu.STRONG) and not fu.removes({"solid": 0.45}, fu.STRONG)
    assert fu.removes({"solid": 0.5, "stripe_h_ratio": 1.4, "body_fill": 0.3}, fu.STRONG)
    assert not fu.removes({"solid": 0.5, "stripe_h_ratio": 1.4, "body_fill": 0.7}, fu.STRONG)
    assert not fu.removes({"solid": 0.5, "stripe_h_ratio": 1.4, "body_fill": 0.3}, fu.MILD)       # 1.4 < 1.5
    assert not fu.removes({}, fu.STRONG) and not fu.removes({"solid": float("nan")}, fu.STRONG)
    assert not fu.removes({"solid": 0.0}, fu.OFF)


def test_proposals_are_boxes_on_no_kept_box_of_any_color():
    kept = [it("FX", (0, 0, 20, 20))]
    props = fu.proposals([it("SC", (2, 2, 20, 20)), it("SC", (2, 2, 20, 20), BLUE), it("SC", (50, 0, 70, 20))], kept)
    assert [p.bbox for p in props] == [(50, 0, 70, 20)]


def test_clusters_join_same_color_boxes_once_per_method():
    by = {"SC": [it("SC", (0, 0, 20, 20))], "P2": [it("P2", (1, 1, 21, 21)), it("P2", (0, 0, 19, 19))],
          "NM": [it("NM", (0, 0, 20, 20), BLUE)]}
    cl = fu.clusters(by, ("SC", "P2", "NM"))
    assert [[x.method for x in c] for c in cl] == [["SC", "P2"], ["P2"], ["NM"]]
    assert cl[0][0].method == "SC"                                  # the first method in the order is drawn


def test_vote_adds_a_cluster_with_enough_votes_and_passing_checks():
    kept = [it("FX", (100, 0, 120, 20))]
    by = {"SC": [it("SC", (0, 0, 20, 20), solid=0.9)], "P2": [it("P2", (1, 0, 21, 20))], "NM": [it("NM", (50, 0, 70, 20))]}
    order = ("SC", "P2", "NM")
    assert [x.bbox for x in fu.vote(kept, by, order, 2)] == [(100, 0, 120, 20), (0, 0, 20, 20)]
    assert len(fu.vote(kept, by, order, 1)) == 3
    assert fu.vote(kept, by, order, None) == kept
    assert len(fu.vote(kept, by, order, 3)) == 1
    assert len(fu.vote(kept, by, order, 3, extra_vote=lambda x: x.bbox[0] == 0)) == 2    # the outside vote
    by["SC"] = [it("SC", (0, 0, 20, 20), solid=0.1)]
    assert len(fu.vote(kept, by, order, 2, fu.STRONG)) == 1                               # the drawn box fails K1


def test_tidy_removes_a_second_box_and_an_other_color_box_on_a_fixed_barrel():
    big = it("FX", (0, 0, 40, 40))
    inner = it("C1", (5, 5, 25, 25))
    other = it("C1", (2, 2, 38, 38), BLUE)
    lone = it("C1", (100, 0, 120, 20))
    out = fu.tidy([big, inner, other, lone])
    assert out == [big, lone]
    assert fu.tidy([it("FX", (5, 5, 25, 25)), big]) == [it("FX", (5, 5, 25, 25)), big]    # fixed boxes are never removed


def test_a_box_the_checks_removed_blocks_proposals_on_it():
    trap = it("C1", (0, 0, 20, 20))
    by = {"SC": [it("SC", (0, 0, 20, 20))], "P2": [it("P2", (1, 0, 21, 20))], "NM": [it("NM", (50, 0, 70, 20))],
          "B4": [it("B4", (50, 0, 70, 20))]}
    order = ("SC", "P2", "NM", "B4")
    assert len(fu.vote([], by, order, 2)) == 2
    assert [x.bbox for x in fu.vote([], by, order, 2, blocked=[trap])] == [(50, 0, 70, 20)]
