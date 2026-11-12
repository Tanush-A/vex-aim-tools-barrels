"""The one-table eval report (src/barrels/report.py): frame selection, the test-frame refusal, counting,
medians, deltas and the writers — on synthetic boxes, no image is opened."""
import csv
import json
import math

import pytest

from barrels import eval_det as ed, io, report as rp
from barrels.detect_types import Barrel

O, B = io.ORANGE, io.BLUE
SPLITS = {"train": ["4A8B_window_light_core_01", "4A8B_window_light_neg_01", "4A8B_campus_light_core_01", "4A8B_campus_light_occl_01",
                    "4A8B_lampwarm7_wood_core_01", "4A8B_lampwarm7_wood_calib_01"],
          "dev": [], "test": ["4A8B_window_light_core_04", "4A8B_campus_light_core_02"], "measured": []}
LABELED = SPLITS["train"] + SPLITS["test"] + ["DAVE_office_speckle_snap_01", "4A8B_sun_light_core_01", "IMG_1234"]


def bx(color, x0, y0, w, h):
    return Barrel(color=color, bbox=(x0, y0, x0 + w, y0 + h))


def frame(name, preds, gts, clean=True):
    return ed.evaluate_frame(name, preds, gts, rule="v2", clean=clean)


# ---------------------------------------------------------------- which frames

def test_set_key_label_and_order():
    assert rp.set_key("4A8B_campus_light_occl_02") == "4A8B_campus_light"
    keys = ["DAVE_office_speckle", "4A8B_lampwarm7_wood", "4A8B_campus_light", "4A8B_window_light"]
    assert rp.set_order(keys) == ["4A8B_window_light", "4A8B_campus_light", "4A8B_lampwarm7_wood", "DAVE_office_speckle"]
    assert [rp.set_label(k, keys) for k in rp.set_order(keys)] == ["HOME", "CAMPUS", "4A8B_lampwarm7_wood", "DAVE*"]
    assert rp.set_label("DAVE_office_dark", ["DAVE_office_dark", "DAVE_office_speckle"]) == "DAVE_office_dark*"
    assert rp.is_indicative("DAVE_office_speckle") and not rp.is_indicative("4A8B_window_light")


def test_select_frames_train_groups_by_set_and_never_returns_test():
    sel = rp.select_frames(LABELED, SPLITS)
    assert list(sel.sets) == ["4A8B_window_light", "4A8B_campus_light", "4A8B_lampwarm7_wood", "DAVE_office_speckle"]   # a new session is a set by itself
    assert sel.sets["4A8B_window_light"] == ["4A8B_window_light_core_01", "4A8B_window_light_neg_01"]
    assert sel.sets["4A8B_lampwarm7_wood"] == ["4A8B_lampwarm7_wood_core_01"]             # calib is geometry-only
    assert sel.sets["DAVE_office_speckle"] == ["DAVE_office_speckle_snap_01"]             # indicative: in no split, still shown
    assert not set(sel.stems) & set(SPLITS["test"])
    assert sel.skipped["test frame (held out)"] == sorted(SPLITS["test"])
    assert sel.skipped["geometry-only scene"] == ["4A8B_lampwarm7_wood_calib_01"]
    assert sel.skipped["in no split yet (run tools/make_splits.py)"] == ["4A8B_sun_light_core_01"]   # might still become a test frame
    assert sel.skipped["name not {robot}_{light}_{surface}_{scene}_{nn}"] == ["IMG_1234"]


def test_select_frames_only_sets_and_explicit_test():
    assert list(rp.select_frames(LABELED, SPLITS, only_sets=["campus", "DAVE"]).sets) == ["4A8B_campus_light", "DAVE_office_speckle"]
    assert list(rp.select_frames(LABELED, SPLITS, only_sets=["4A8B_lampwarm7_wood"]).sets) == ["4A8B_lampwarm7_wood"]
    t = rp.select_frames(LABELED, SPLITS, split="test")
    assert t.split == "test" and sorted(t.stems) == sorted(SPLITS["test"])
    with pytest.raises(ValueError):
        rp.select_frames(LABELED, SPLITS, split="all")


def test_refuse_test_frames():
    rp.refuse_test_frames(SPLITS["train"], SPLITS)                                         # train frames: fine
    with pytest.raises(rp.TestFrameError, match="4A8B_campus_light_core_02"):
        rp.refuse_test_frames(SPLITS["train"] + ["4A8B_campus_light_core_02"], SPLITS)
    rp.refuse_test_frames(SPLITS["test"], SPLITS, allow_test=True)                         # only when asked for


def test_run_arm_refuses_test_frames_before_opening_anything(tmp_path):
    sel = rp.Selection({"4A8B_campus_light": ["4A8B_campus_light_core_02"]}, split="train")   # a test frame slipped into a train selection
    arm = rp.Arm("x", tmp_path / "does_not_exist.json")                                     # would fail on open — never reached
    with pytest.raises(rp.TestFrameError):
        rp.run_arm(arm, sel, SPLITS)


def test_parse_det_overrides():
    assert rp.parse_det_overrides(["body_width=0", "cover_rows=false,stripe_mode=bands", "min_area_px=30"]) == {
        "body_width": 0.0, "cover_rows": False, "stripe_mode": "bands", "min_area_px": 30}
    assert rp.parse_det_overrides(None) == {}
    arm = rp.Arm("a", "m.json", rp.parse_det_overrides(["dark_stripe=on"]))
    assert arm.det_config().dark_stripe is True and arm.det_config().body_width == 1.2
    for bad in (["no_such_field=1"], ["body_width"], ["cover_rows=maybe"], ["min_area_px=x"]):
        with pytest.raises(ValueError):
            rp.parse_det_overrides(bad)


# ---------------------------------------------------------------- counting, medians, deltas

def synthetic():
    """Two sets. Candidate: finds both campus core barrels (one 10 % narrow, 2 px low) and misses the occluded one;
    baseline: finds one, misses two, and draws a false box. Home: one barrel found by both, a clean negative
    on which only the baseline draws a box."""
    gt_core = [bx(O, 100, 200, 60, 60), bx(B, 300, 200, 60, 60)]
    gt_occl = [bx(B, 200, 150, 40, 40)]
    gt_home = [bx(O, 100, 200, 50, 50)]
    sets = {"4A8B_window_light": ["4A8B_window_light_core_01", "4A8B_window_light_neg_01"],
            "4A8B_campus_light": ["4A8B_campus_light_core_01", "4A8B_campus_light_occl_01"]}
    cand = {"4A8B_window_light_core_01": frame("4A8B_window_light_core_01", [bx(O, 100, 201, 50, 50)], gt_home),
            "4A8B_window_light_neg_01": frame("4A8B_window_light_neg_01", [], []),
            "4A8B_campus_light_core_01": frame("4A8B_campus_light_core_01", [bx(O, 103, 202, 54, 60), bx(B, 300, 200, 60, 60)], gt_core),
            "4A8B_campus_light_occl_01": frame("4A8B_campus_light_occl_01", [], gt_occl)}
    base = {"4A8B_window_light_core_01": frame("4A8B_window_light_core_01", [bx(O, 100, 204, 50, 50)], gt_home),
            "4A8B_window_light_neg_01": frame("4A8B_window_light_neg_01", [bx(B, 10, 300, 30, 30)], []),
            "4A8B_campus_light_core_01": frame("4A8B_campus_light_core_01", [bx(B, 300, 200, 60, 60), bx(O, 500, 300, 40, 40)], gt_core),
            "4A8B_campus_light_occl_01": frame("4A8B_campus_light_occl_01", [], gt_occl)}
    return sets, cand, base


def test_summarize_counts_and_medians():
    sets, cand, base = synthetic()
    c = rp.summarize([cand[s] for s in sets["4A8B_campus_light"]])
    assert (c.frames, c.barrels, c.found, c.missed, c.false) == (2, 3, 2, 1, 0)
    assert c.width == pytest.approx((54 / 60 + 1.0) / 2)                 # median of the two hits
    assert c.bottom == pytest.approx(1.0)                                # |2| and |0| -> median 1
    assert c.score == pytest.approx((1.0 + 2 / 3) / 2)                   # orange F1 1, blue P 1 R 1/2 -> F1 2/3
    assert not c.disqualified and c.neg_false == 0
    b = rp.summarize([base[s] for s in sets["4A8B_campus_light"]])
    assert (b.found, b.missed, b.false) == (1, 2, 1) and b.width == pytest.approx(1.0) and b.bottom == 0.0
    empty = rp.summarize([])
    assert empty.frames == 0 and math.isnan(empty.score) and math.isnan(empty.width)
    neg = rp.summarize([cand["4A8B_window_light_neg_01"]])               # a row with no barrels: no medians, no score, no warning
    assert (neg.frames, neg.barrels, neg.found, neg.false) == (1, 0, 0, 0) and math.isnan(neg.width) and math.isnan(neg.score)


def test_summarize_matches_eval_det_score_and_disqualifier():
    sets, cand, base = synthetic()
    home_b = [base[s] for s in sets["4A8B_window_light"]]
    cell = rp.summarize(home_b)
    s = ed.score(home_b, {}, out_scope=())
    assert cell.score == pytest.approx(s["primary"]) and cell.disqualified is True and s["disqualified"]
    assert cell.neg_false == 1 and cell.clean_neg_false == 1 and cell.false == 1
    # the same false box on a negative that is NOT clean counts but does not disqualify
    cluttered = frame("4A8B_window_light_neg_01", [bx(B, 10, 300, 30, 30)], [], clean=False)
    c2 = rp.summarize([base["4A8B_window_light_core_01"], cluttered])
    assert c2.neg_false == 1 and c2.clean_neg_false == 0 and not c2.disqualified


def test_delta():
    sets, cand, base = synthetic()
    d = rp.delta(rp.summarize([cand[s] for s in sets["4A8B_campus_light"]]), rp.summarize([base[s] for s in sets["4A8B_campus_light"]]))
    assert (d["found"], d["missed"], d["false"]) == (1, -1, -1)
    assert d["width"] == pytest.approx(0.95 - 1.0) and d["bottom"] == pytest.approx(1.0)
    assert d["score"] == pytest.approx((1.0 + 2 / 3) / 2 - (0.0 + 2 / 3) / 2)
    assert rp.delta(rp.summarize([cand["4A8B_campus_light_occl_01"]]), rp.Cell())["width"] is None      # no hits on either side: no number


def test_build_rows_groups_by_set_and_scene():
    sets, cand, base = synthetic()
    rows = rp.build_rows(sets, cand, base)
    assert [(r.label, r.scene, r.kind) for r in rows] == [
        ("HOME", "core", "scene"), ("HOME", "neg", "scene"), ("HOME", "", "subtotal"),
        ("CAMPUS", "core", "scene"), ("CAMPUS", "occl", "scene"), ("CAMPUS", "", "subtotal"), ("ALL", "", "total")]
    occl = rows[4]
    assert (occl.cand.found, occl.cand.missed, occl.base.missed) == (0, 1, 1) and occl.delta["found"] == 0
    sub = rows[5]
    assert sub.cand.found == rows[3].cand.found + rows[4].cand.found and sub.cand.frames == 2
    total = rows[-1]
    assert (total.cand.barrels, total.cand.found, total.base.found, total.base.false) == (4, 3, 2, 2)
    # an indicative set gets its own block and stays out of ALL
    dave = {"DAVE_office_speckle_snap_01": frame("DAVE_office_speckle_snap_01", [], [bx(O, 10, 200, 40, 40)])}
    sets2 = {**sets, "DAVE_office_speckle": list(dave)}
    rows2 = rp.build_rows(sets2, {**cand, **dave}, {**base, **dave})
    assert [r.label for r in rows2 if r.kind != "scene"] == ["HOME", "CAMPUS", "DAVE*", "ALL"]
    assert rows2[-1].cand.barrels == 4 and rows2[-2].indicative and rows2[-2].cand.missed == 1


def make_rep():
    sets, cand, base = synthetic()
    return rp.Report(rp.build_rows(sets, cand, base), rp.Arm("candidate", "results/a/config.json"),
                     rp.Arm("baseline", "results/b/config.json", {"body_width": 0.0}), rp.Selection(sets), "loso", "abc1234", 1.5)


def test_format_text_one_table_about_140_columns():
    rep = make_rep()
    text = rp.format_text(rep)
    lines = text.split("\n")
    assert max(len(x) for x in lines) <= 144 and max(len(x) for x in lines if "DQ:" not in x) <= 140
    assert "CANDIDATE" in lines[0] and "BASELINE" in lines[0] and "DELTA" in lines[0]
    home = next(x for x in lines if x.startswith("HOME all"))
    assert home.rstrip().split("|")[-1].strip() == "0/1 DQ:b"
    campus = next(x for x in lines if x.startswith("CAMPUS all"))
    assert campus.split("|")[3].split() == ["+1", "-1", "-1", "-0.05", "+1.0"]            # the delta block
    assert "leave-one-scene-out" in text and "body_width=0.0" in text
    assert rep.subtotal("CAMPUS").cand.found == 2 and rep.subtotal("4A8B_window_light").label == "HOME"


def test_writers(tmp_path):
    rep = make_rep()
    out = rp.write_all(rep, tmp_path / "r", title="t")
    assert sorted(p.name for p in out.iterdir()) == ["report.csv", "report.json", "report.md"]
    md = (out / "report.md").read_text()
    assert md.startswith("# t") and "| **CAMPUS all** |" in md and "```" in md
    rows = list(csv.DictReader((out / "report.csv").open()))
    assert len(rows) == len(rep.rows)
    sub = next(r for r in rows if r["label"] == "CAMPUS" and r["kind"] == "subtotal")
    assert (sub["cand_found"], sub["base_found"], sub["delta_found"], sub["base_disqualified"]) == ("2", "1", "1", "0")
    neg = next(r for r in rows if r["label"] == "HOME" and r["scene"] == "neg")
    assert neg["cand_width"] == "" and neg["base_false"] == "1"
    d = json.loads((out / "report.json").read_text())
    assert d["rule"] == "v2" and d["baseline"]["det_overrides"] == {"body_width": 0.0} and d["baseline"]["det"]["body_width"] == 0.0
    assert d["sets"]["4A8B_campus_light"]["label"] == "CAMPUS" and len(d["rows"]) == len(rep.rows)
    assert d["rows"][1]["candidate"]["width"] is None                                     # nan is written as null
