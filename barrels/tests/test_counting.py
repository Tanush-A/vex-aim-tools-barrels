"""Counting per placement and a misplaced box counted once (src/barrels/counting.py, TODO M1): the states of one
frame, which label box is which physical barrel, and the placement-weighted tally. Synthetic boxes; the two checks on
the committed data read train label files only (no image, no test frame)."""
import random

import pytest

from barrels import conditions as cd, counting as ct, eval_det as ed, io
from barrels.detect_types import Barrel

O, B = io.ORANGE, io.BLUE
TABLE = {"lampa_glass": {"place": "glass", "light": "lamp"}, "lampb_glass": {"place": "glass", "light": "lamp"},
         "lampc_glass": {"place": "glass", "light": "lamp"}, "window_gray": {"place": "gray", "light": "window"}}


def bx(color, x0, y0, w, h):
    return Barrel(color=color, bbox=(x0, y0, x0 + w, y0 + h))


def stem(light, surface, scene="core", nn=1):
    return f"4A8B_{light}_{surface}_{scene}_{nn:02d}"


# ---------------------------------------------------------------- on a barrel

def test_on_share_is_the_part_of_the_smaller_box_inside_the_other():
    big, small = (0, 0, 100, 100), (10, 10, 30, 30)
    assert ct.on_share(big, small) == 1.0 and ct.on_share(small, big) == 1.0        # a small box inside a big one, either way round
    assert ct.on_share((0, 0, 10, 10), (5, 0, 15, 10)) == pytest.approx(0.5)        # shifted by half its width
    assert ct.on_share((0, 0, 10, 10), (10, 0, 20, 10)) == 0.0                      # beside it
    assert ct.on_share((0, 0, 10, 10), (0, 0, 0, 10)) == 0.0                        # an empty box is on nothing


def test_every_pair_that_passes_the_overlap_clause_is_on_the_barrel():
    rng = random.Random(1)
    n = 0
    for _ in range(20000):
        a = bx(O, rng.randrange(0, 80), rng.randrange(0, 80), rng.randrange(5, 70), rng.randrange(5, 70))
        b = bx(O, rng.randrange(0, 80), rng.randrange(0, 80), rng.randrange(5, 70), rng.randrange(5, 70))
        if ed.box_iou(a.bbox, b.bbox) >= ed.IOU_THR:
            n += 1
            assert ct.is_on(a, b)
    assert n > 100


# ---------------------------------------------------------------- one frame

def test_a_strict_hit_is_found_and_its_box_is_on_its_barrel():
    fc = ct.classify_frame("f", [bx(O, 100, 201, 50, 60)], [bx(O, 100, 200, 50, 60)])
    assert fc.gt == (ct.FOUND,) and fc.boxes == (ct.FOUND,) and fc.extra == 0 and not fc.negative


def test_a_box_with_a_bad_bottom_edge_counts_once_not_as_a_miss_plus_a_false_box():
    gt = [bx(O, 100, 200, 50, 60)]
    low = [bx(O, 100, 200, 50, 70)]                                 # bottom 10 px low: the tolerance is 6
    old = ed.evaluate_frame("f", low, gt, rule="v2")
    assert (sum(old.tp.values()), sum(old.fn.values()), sum(old.fp.values())) == (0, 1, 1)      # strict: charged twice
    fc = ct.classify_frame("f", low, gt)
    assert fc.gt == (ct.OFF,) and fc.boxes == (ct.OFF,) and fc.extra == 0 and fc.n_gt(ct.MISSED) == 0


def test_a_box_around_the_visible_half_is_on_the_barrel():
    gt = [bx(B, 100, 200, 50, 60)]
    half = [bx(B, 100, 200, 22, 60)]                                # IoU 0.44: neither a strict hit nor an overlap hit
    assert ed.box_iou(half[0].bbox, gt[0].bbox) < 0.5
    assert ct.classify_frame("f", half, gt).gt == (ct.OFF,)
    beside = [bx(B, 160, 200, 50, 60)]                              # next to it
    fc = ct.classify_frame("f", beside, gt)
    assert fc.gt == (ct.MISSED,) and fc.boxes == (ct.NOTHING,) and fc.extra == 1


def test_wrong_color_second_box_and_nothing():
    gts = [bx(O, 100, 200, 50, 60), bx(B, 300, 200, 50, 60)]
    preds = [bx(O, 100, 200, 50, 60),           # the orange barrel, right
             bx(O, 105, 205, 40, 40),           # a second orange box on it
             bx(O, 300, 200, 50, 60),           # an orange box on the blue barrel
             bx(B, 500, 300, 40, 40)]           # a blue box on nothing
    fc = ct.classify_frame("f", preds, gts)
    assert fc.gt == (ct.FOUND, ct.MISSED)
    assert fc.boxes == (ct.FOUND, ct.SECOND, ct.WRONG, ct.NOTHING) and fc.extra == 3
    assert (fc.n_box(ct.WRONG), fc.n_box(ct.SECOND), fc.n_box(ct.NOTHING)) == (1, 1, 1)


def test_the_strict_hit_is_taken_first_and_the_better_box_wins_the_barrel():
    gt = [bx(O, 100, 200, 50, 60)]
    preds = [bx(O, 100, 200, 50, 75), bx(O, 100, 201, 50, 60)]      # the first has a bad bottom, the second is right
    fc = ct.classify_frame("f", preds, gt)
    assert fc.gt == (ct.FOUND,) and fc.boxes == (ct.SECOND, ct.FOUND)
    two_off = [bx(O, 100, 200, 50, 75), bx(O, 100, 200, 30, 30)]    # neither is a strict hit: one box is "off", the other a second box
    fc = ct.classify_frame("f", two_off, gt)
    assert fc.gt == (ct.OFF,) and fc.boxes == (ct.OFF, ct.SECOND)


def test_an_empty_frame_has_only_boxes_on_nothing():
    fc = ct.classify_frame("f", [bx(O, 10, 300, 30, 30), bx(B, 100, 300, 30, 30)], [], clean=False)
    assert fc.negative and fc.gt == () and fc.boxes == (ct.NOTHING, ct.NOTHING) and not fc.clean
    assert ct.classify_frame("f", [], []).boxes == ()


def test_found_is_exactly_the_v2_rule_on_random_frames():
    """The second accounting never changes what a strict hit is: found = v2 hits, and every v2 miss and v2 false box
    is accounted for by the other states."""
    rng = random.Random(7)
    for k in range(300):
        def some(n):
            return [bx(rng.choice((O, B)), rng.randrange(0, 500), rng.randrange(60, 380), rng.randrange(20, 90), rng.randrange(20, 100)) for _ in range(n)]
        gts = some(rng.randrange(0, 5))
        preds = some(rng.randrange(0, 4)) + [bx(g.color, g.bbox[0] + rng.randrange(-12, 13), g.bbox[1] + rng.randrange(-12, 13),
                                               max(5, g.width + rng.randrange(-15, 16)), max(5, g.height + rng.randrange(-15, 16)))
                                            for g in gts if rng.random() < 0.8]
        old = ed.evaluate_frame("f", preds, gts, rule="v2")
        fc = ct.classify_frame("f", preds, gts)
        assert fc.n_gt(ct.FOUND) == sum(old.tp.values())
        assert fc.n_gt(ct.OFF) + fc.n_gt(ct.MISSED) == sum(old.fn.values())
        assert len(fc.boxes) - fc.n_box(ct.FOUND) == sum(old.fp.values())
        assert fc.n_box(ct.OFF) == fc.n_gt(ct.OFF) and fc.n_box(ct.FOUND) == fc.n_gt(ct.FOUND)        # one box per barrel
        assert len(fc.gt) == len(gts) and len(fc.boxes) == len(preds)
        assert sorted({m.gt_idx for m in old.matches}) == [i for i, s in enumerate(fc.gt) if s == ct.FOUND]     # the same barrels


def test_frame_count_round_trip_and_assumed():
    fc = ct.classify_frame("f", [bx(O, 100, 200, 50, 75), bx(B, 500, 300, 40, 40)], [bx(O, 100, 200, 50, 60), bx(B, 300, 200, 50, 60)], clean=False)
    d = fc.to_dict()
    assert d == {"stem": "f", "gt": "OM", "boxes": "ON", "clean": False}
    assert ct.FrameCount.from_dict(d) == fc
    with pytest.raises(ValueError):
        ct.FrameCount.from_dict({"stem": "f", "gt": "X", "boxes": ""})
    a = ct.assumed_perfect("g", 3)
    assert a.assumed and a.gt == (ct.FOUND,) * 3 and a.extra == 0 and ct.FrameCount.from_dict(a.to_dict()) == a


# ---------------------------------------------------------------- placements

def glass_gts():
    """One arrangement under three lights (the boxes copied, one light with its two boxes in the other order and a
    2 px shift), a second arrangement under one light, and another place."""
    a, b = bx(O, 100, 200, 50, 60), bx(B, 104, 150, 40, 48)
    return {stem("lampa", "glass"): [a, b],
            stem("lampb", "glass"): [bx(B, 106, 151, 40, 48), bx(O, 101, 200, 50, 60)],
            stem("lampc", "glass"): [a, b],
            stem("lampa", "glass", "touch"): [bx(O, 300, 200, 50, 60)],
            stem("window", "gray"): [bx(O, 100, 200, 50, 60)]}


def test_placements_follow_the_barrel_across_lights_not_the_list_order():
    gts = glass_gts()
    pl = ct.build_placements(gts, TABLE)
    sa, sb, sc = stem("lampa", "glass"), stem("lampb", "glass"), stem("lampc", "glass")
    assert pl.arrangement[sa] == pl.arrangement[sb] == ("4A8B", "glass", "core", "01")
    assert pl.key[(sa, 0)] == pl.key[(sb, 1)] == pl.key[(sc, 0)]           # the orange barrel, whatever its place in the list
    assert pl.key[(sa, 1)] == pl.key[(sb, 0)] != pl.key[(sa, 0)]
    assert pl.count(gts) == (4, 3)                                         # 4 physical barrels in 3 arrangements, not 8
    assert pl.count([sa, sb, sc]) == (2, 1)
    assert ct.place_of(stem("window", "gray"), TABLE) == "gray" and ct.condition_of(sa) == "lampa_glass"


def test_two_lights_of_one_arrangement_with_other_barrels_are_refused():
    gts = glass_gts()
    gts[stem("lampb", "glass")] = [bx(O, 101, 200, 50, 60)]                # a barrel is missing under one light
    with pytest.raises(ct.ArrangementMismatch, match="lampb_glass_core_01"):
        ct.build_placements(gts, TABLE)
    gts[stem("lampb", "glass")] = [bx(O, 101, 200, 50, 60), bx(B, 400, 150, 40, 48)]       # ... or stands somewhere else
    with pytest.raises(ct.ArrangementMismatch):
        ct.build_placements(gts, TABLE)
    gts[stem("lampb", "glass")] = [bx(O, 101, 200, 50, 60), bx(O, 106, 151, 40, 48)]       # ... or has another color
    with pytest.raises(ct.ArrangementMismatch):
        ct.build_placements(gts, TABLE)


# ---------------------------------------------------------------- the tally

def glass_counts(gts):
    """The orange barrel is found under 2 of 3 lights and has a box with a bad bottom under the third; the blue one
    is found under 1 of 3. A tin gets a box under every light; the touch frame's barrel is found."""
    sa, sb, sc = stem("lampa", "glass"), stem("lampb", "glass"), stem("lampc", "glass")
    tin = bx(B, 500, 300, 40, 40)
    preds = {sa: [gts[sa][0], gts[sa][1], tin], sb: [gts[sb][1], tin], sc: [bx(O, 100, 200, 50, 75), tin],
             stem("lampa", "glass", "touch"): gts[stem("lampa", "glass", "touch")], stem("window", "gray"): []}
    return {s: ct.classify_frame(s, preds[s], gts[s]) for s in gts}


def test_a_placement_counts_once_by_the_share_of_its_lights():
    gts = glass_gts()
    pl, counts = ct.build_placements(gts, TABLE), glass_counts(gts)
    core = [stem(x, "glass") for x in ("lampa", "lampb", "lampc")]
    t = ct.tally(counts, core, pl, TABLE)
    assert (t.frames, t.conditions, t.places, t.arrangements, t.placements, t.barrels) == (3, 3, 1, 1, 2, 6)
    assert (t.found, t.off, t.missed) == (3, 1, 2)                         # per frame: the old way of counting
    assert t.found_w == pytest.approx(2 / 3 + 1 / 3) and t.off_w == pytest.approx(1 / 3) and t.missed_w == pytest.approx(2 / 3)
    assert (t.boxes, t.nothing, t.extra, t.strict_false) == (7, 3, 3, 4)   # the strict rule calls the misplaced box false too
    assert t.nothing_w == pytest.approx(1.0) and t.extra_w == pytest.approx(1.0)       # one tin, seen three times
    one = ct.tally(counts, core[:1], pl, TABLE)                            # one light alone: per placement = per frame
    assert (one.placements, one.found, one.found_w, one.nothing_w) == (2, 2, 2.0, 1.0)
    place = ct.tally(counts, [s for s in gts if "glass" in s], pl, TABLE)
    assert (place.placements, place.arrangements) == (3, 2) and place.found_w == pytest.approx(2.0)
    allt = ct.tally(counts, list(gts), pl, TABLE)                          # places add up: no placement spans two places
    gray = ct.tally(counts, [stem("window", "gray")], pl, TABLE)
    assert allt.found_w == pytest.approx(place.found_w + gray.found_w) and allt.placements == 4 and allt.places == 2
    assert ct.tally(counts, [], pl).frames == 0


def test_boxes_on_empty_frames_are_counted_on_their_own_and_clean_ones_apart():
    stems = [stem("lampa", "glass", "neg", 2), stem("lampb", "glass", "neg", 2), stem("lampa", "glass", "neg", 1)]
    gts = {s: [] for s in stems}
    pl = ct.build_placements(gts, TABLE)
    counts = {stems[0]: ct.classify_frame(stems[0], [bx(O, 10, 300, 30, 30)], [], clean=False),
              stems[1]: ct.classify_frame(stems[1], [bx(O, 10, 300, 30, 30), bx(B, 90, 300, 30, 30)], [], clean=False),
              stems[2]: ct.classify_frame(stems[2], [bx(B, 10, 300, 30, 30)], [], clean=True)}
    t = ct.tally(counts, stems, pl, TABLE)
    assert (t.empty_frames, t.clean_empty_frames, t.empty, t.clean_empty, t.nothing) == (3, 1, 4, 1, 4)
    assert t.cluttered_empty_w == pytest.approx(1.5) and t.empty_w == pytest.approx(2.5)        # the clutter scene under two lights: 3 boxes / 2
    assert t.placements == 0 and t.found_w == 0


def test_group_stems_and_the_table_text():
    gts = glass_gts()
    pl, counts = ct.build_placements(gts, TABLE), glass_counts(gts)
    by_place = ct.group_stems(gts, "place", TABLE)
    assert list(by_place) == ["glass", "gray"] and len(by_place["glass"]) == 4
    assert len(ct.group_stems(gts, "condition", TABLE)) == 4
    with pytest.raises(ValueError):
        ct.group_stems(gts, "set")
    rows = [ct.TableRow(p, [ct.tally(counts, ss, pl, TABLE), None]) for p, ss in by_place.items()]
    assumed = {s: ct.assumed_perfect(s, len(g)) for s, g in gts.items()}
    rows.append(ct.TableRow("all", [ct.tally(counts, list(gts), pl, TABLE), ct.tally(assumed, list(gts), pl, TABLE)], "total"))
    text = ct.format_table(rows, ["ours", "vendor"])
    lines = text.split("\n")
    assert "OURS" in lines[0] and "VENDOR" in lines[0] and lines[1].split()[:4] == ["lights", "frames", "brls", "plcm"]
    glass = next(x for x in lines if x.startswith("glass"))
    assert glass.split("|")[0].split() == ["glass", "3", "4", "7", "3"] and glass.split("|")[1].split()[:2] == ["2.0", "4"]
    assert glass.split("|")[2].split() == ["-"] * 8                        # no number for that arm
    total = next(x for x in lines if x.startswith("all"))
    assert total.split("|")[2].split()[:2] == ["4.0*", "8*"]               # an assumed arm is starred and says nothing about boxes
    md = ct.format_table(rows, ["ours", "vendor"], markdown=True, title="t")
    assert md.startswith("### t") and "| **all** |" in md and "ours box off" in md


# ---------------------------------------------------------------- the committed data (train label files only)

def train_stems():
    from barrels import report as rp, splits as sp
    splits = sp.load_splits()
    return rp.select_frames(rp.labeled_stems(), splits).stems if io.LABELS_DIR.exists() else []


def test_every_train_arrangement_holds_the_same_barrels_under_every_light():
    stems = [s for s in train_stems() if not s.startswith("DAVE")]
    if not stems:
        pytest.skip("no committed labels")
    gts, _ = ct.load_gts(stems)
    pl = ct.build_placements(gts)                                          # raises ArrangementMismatch on a bad label
    new = [s for s in stems if io.vendor_path(s).exists() and cd.info(ct.condition_of(s)).klass == cd.ORDINARY]
    if len(new) >= 100:                                                    # the audit's count: 243 barrels are 108 placements
        assert sum(len(gts[s]) for s in new) >= 243 and pl.count(new)[0] >= 108
        assert len({ct.place_of(s) for s in new}) >= 6


def test_condition_classes_match_the_list_the_color_experiment_used():
    """ordinary / extreme / excluded now live in data/conditions.json; they must say what
    experiments/2026-11-25_color/common.py said, so "the ordinary conditions" are the same 17."""
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "experiments" / "2026-11-25_color" / "common.py"
    if not path.exists():
        pytest.skip("the color experiment is not on this branch")
    spec = importlib.util.spec_from_file_location("color_common_under_test", path)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    table = cd.load_table()
    for key in table:
        assert cd.info(key).klass == cm.class_of(key), key
    ordinary = [k for k in table if cd.info(k).klass == cd.ORDINARY]
    assert len(ordinary) == 17 and len({cd.info(k).place for k in ordinary}) == 8
    assert cd.info("not_listed").klass == cd.UNLISTED and not cd.info("not_listed").vendor_assumed
    assert [k for k in table if cd.info(k).vendor_assumed] == ["window_light", "campus_light"]
