"""The never-regress check with a margin (src/barrels/gate.py, TODO M2): a stored run against this run, protected
sets judged on their totals against a margin, every changed barrel listed. Plain data in, pass / fail out; no image
is opened."""
import copy
import json

import pytest

from barrels import counting as ct, gate as gt, io
from barrels.detect_types import Barrel
from test_vendor import load_tool

H, C, K, D = "4A8B_window_light", "4A8B_campus_light", "4A8B_window_black", "DAVE_office_speckle"
GA, GB = "4A8B_lampa_glass", "4A8B_lampb_glass"                    # one table under two lights: one protected set
GLASS = gt.Group("GLASS", (GA, GB))
PROTECTED = gt.DEFAULT_PROTECTED + (GLASS,)


def fr(stem, gt_states="", boxes=None, clean=True, arr=None):
    """One frame of a snapshot. ``gt_states``: a letter per true barrel (F found, O box off, M missed). ``boxes``: a
    letter per box; by default the one box of every found or box-off barrel. ``arr``: the arrangement, by default
    the frame's own; two lights of one arrangement share it."""
    t = io.parse_name(stem)
    return {"stem": stem, "set": f"{t['robot']}_{t['light']}_{t['surface']}", "arr": arr or f"{t['robot']}/{t['light']}{t['surface']}/{t['scene']}/{t['nn']}",
            "pl": list(range(len(gt_states))), "gt": gt_states, "boxes": gt_states.replace("M", "") if boxes is None else boxes, "clean": clean}


def snap(frames, **head):
    return {"version": 2, "made": "2026-11-26", "git": "abc1234", "arm": "today", "frames": copy.deepcopy(frames)} | head


BASE = [fr(f"{H}_cluster_01", "FFFM"), fr(f"{H}_cluster_02", "FFFM"), fr(f"{H}_neg_01"),                  # home: 6 of 8, a clean empty frame
        fr(f"{C}_core_01", "FFFF"), fr(f"{C}_occl_01", "M"),                                             # campus: 4 of 5
        fr(f"{GA}_core_01", "FF", arr="4A8B/glass/core/01"), fr(f"{GB}_core_01", "FM", arr="4A8B/glass/core/01"),     # glass: 2 placements, 1.5 found
        fr(f"{GA}_neg_02", clean=False, arr="4A8B/glass/neg/02"), fr(f"{GB}_neg_02", clean=False, arr="4A8B/glass/neg/02"),
        fr(f"{K}_close_01", "FMM"), fr(f"{K}_neg_01"),                                                   # an extreme set: shown, never fails
        fr(f"{D}_snap_01", "FFM", boxes="FFNN")]


def changed(stem, **new):
    """BASE with one frame changed."""
    frames = copy.deepcopy(BASE)
    for f in frames:
        if f["stem"] == stem:
            f.update(new)
            if "gt" in new and "boxes" not in new:
                f["boxes"] = new["gt"].replace("M", "")
            f["pl"] = list(range(len(f["gt"])))
    return frames


def check(frames, protected=PROTECTED, margins=None):
    res = gt.compare(snap(BASE), snap(frames, git="def5678", arm="candidate"), protected, margins)
    return res, gt.format_gate(res)


def group(res, name):
    return next(g for g in res.groups + res.others if g.name == name)


# ---------------------------------------------------------------- the rule

def test_a_run_equal_to_the_baseline_passes():
    res, text = check(BASE)
    assert res.passed and res.failures == [] and res.lower == [] and all(g.status == gt.SAME for g in res.groups + res.others)
    assert text.splitlines()[-1].startswith("RESULT: PASS")
    home = next(x for x in text.splitlines() if x.strip().startswith("HOME"))
    assert "found 6.0 -> 6.0 of 8 placements" in home and home.endswith("[protected]")
    assert "unchanged: 2 set(s)" in text and "clean empty frames with a new box: none" in text


def test_one_barrel_lost_is_inside_the_margin_and_is_still_listed():
    res, text = check(changed(f"{H}_cluster_01", gt="FFMM"))
    g = group(res, "HOME")
    assert res.passed and g.status == gt.LOWER and not g.fails and res.lower == ["HOME"]
    assert g.barrels == [f"{H}_cluster_01 #3: found -> missed"] and f"barrel  {H}_cluster_01 #3: found -> missed" in text
    assert "found 6.0 -> 5.0 of 8 placements (-1.0)" in text and "margins 1.0 / 1.0: lower, within the margin" in text
    last = text.splitlines()[-1]
    assert last.startswith("RESULT: PASS") and "Lower inside the margin: HOME" in last


def test_a_drop_larger_than_the_margin_fails_and_names_the_set():
    res, text = check(changed(f"{H}_cluster_01", gt="FMMM"))
    assert not res.passed and [g.name for g in res.failures] == ["HOME"] and group(res, "HOME").status == gt.WORSE
    assert len(group(res, "HOME").barrels) == 2
    last = text.splitlines()[-1]
    assert last.startswith("RESULT: FAIL") and "1 protected set(s) worse by more than the margin (HOME)" in last


def test_a_set_is_judged_on_its_total_not_on_single_rows():
    frames = changed(f"{H}_cluster_01", gt="FFMM")                  # one barrel lost in one frame ...
    frames[1].update(gt="FFFF", boxes="FFFF")                       # ... one gained in another
    res, text = check(frames)
    g = group(res, "HOME")
    assert res.passed and g.status == gt.SAME and res.lower == []
    assert len(g.barrels) == 2 and "missed -> found" in text and "found -> missed" in text       # both are shown all the same


def test_a_box_on_its_barrel_that_fails_the_strict_rule_is_not_a_false_box():
    res, _ = check(changed(f"{C}_core_01", gt="FFFO"))              # the box is still on the barrel, its bottom is off
    g = group(res, "CAMPUS")
    assert g.status == gt.LOWER and g.cand.found_w == 3 and g.cand.extra == 0 and g.barrels == [f"{C}_core_01 #4: found -> off"]


def test_boxes_that_are_not_on_their_barrel_have_a_margin_too():
    res, text = check(changed(f"{C}_core_01", boxes="FFFFN"))
    assert res.passed and group(res, "CAMPUS").status == gt.LOWER and f"boxes   {C}_core_01: nothing 0 -> 1" in text
    res, _ = check(changed(f"{C}_core_01", boxes="FFFFNS"))
    assert not res.passed and group(res, "CAMPUS").status == gt.WORSE
    res, _ = check(changed(f"{D}_snap_01", boxes="FF"))            # fewer boxes on nothing is better
    assert res.passed and group(res, D).status == gt.BETTER


def test_a_placement_under_two_lights_counts_once():
    res, text = check(changed(f"{GA}_core_01", gt="FM"))           # one barrel lost under one of two lights: half a placement
    g = group(res, "GLASS")
    assert res.passed and g.status == gt.LOWER and g.base.found_w == 1.5 and g.cand.found_w == 1.0 and g.cand.placements == 2
    assert "found 1.5 -> 1.0 of 2 placements (-0.5) [per frame 3 -> 2 of 4]" in text
    res, _ = check(changed(f"{GA}_core_01", gt="MM"))              # a whole placement: exactly the margin, not more
    assert res.passed
    frames = changed(f"{GA}_core_01", gt="MM")
    frames[6].update(gt="MM", boxes="")
    res, _ = check(frames)                                          # 1.5 placements gone
    assert not res.passed and group(res, "GLASS").status == gt.WORSE


def test_the_margins_come_from_the_file_and_default_to_one_unit():
    m = gt.Margins({"HOME": {"found": 2.0, "extra": 0.5}}, cluttered_empty=2.0, source="test")
    assert m.of("HOME") == (2.0, 0.5) and m.of("CAMPUS") == (1.0, 1.0)
    res, text = check(changed(f"{H}_cluster_01", gt="FMMM"), margins=m)
    assert res.passed and "margins 2.0 / 0.5" in text and "Margins (found / boxes): test." in text
    res, _ = check(changed(f"{H}_cluster_01", boxes="FFFN"), margins=m)
    assert not res.passed


def test_a_new_box_on_a_clean_empty_frame_fails_in_any_set():
    for stem in (f"{K}_neg_01", f"{H}_neg_01"):
        res, text = check(changed(stem, boxes="N"))
        assert not res.passed and res.clean_empty == [f"{stem}: 0 -> 1 box(es)"]
        assert "a new box on a clean empty frame in 1 frame(s)" in text.splitlines()[-1] and stem in text.splitlines()[-1]
    new = "4A8B_overhead_gray"                                      # ... a set the baseline has never seen included
    res, _ = check(BASE + [fr(f"{new}_neg_01", boxes="N")])
    assert not res.passed and res.clean_empty == [f"{new}_neg_01: 0 -> 1 box(es)"]
    had = changed(f"{K}_neg_01", boxes="N")                         # a box the baseline already had is not a NEW box
    assert gt.compare(snap(had), snap(had), PROTECTED).passed
    assert gt.compare(snap(had), snap(BASE), PROTECTED).passed      # and losing it is fine


def test_boxes_on_empty_frames_with_clutter_have_a_margin_and_count_once_per_arrangement():
    res, text = check(changed(f"{GA}_neg_02", boxes="N"))           # the clutter scene boxed under one of its two lights
    assert res.passed and res.cluttered == (0.0, 0.5) and res.cluttered_frames == [f"{GA}_neg_02: 0 -> 1 box(es)"]
    assert "boxes on empty frames with clutter, once per arrangement: 0.0 -> 0.5 (margin 1.0)" in text
    assert "boxes on empty frames with clutter" in res.lower
    frames = changed(f"{GA}_neg_02", boxes="NN")
    frames[8].update(boxes="N")
    res, text = check(frames)                                       # three boxes over two lights: 1.5
    assert not res.passed and res.cluttered_fails and "up by more than the margin" in text.splitlines()[-1]
    assert group(res, "GLASS").status == gt.WORSE                   # they are boxes on nothing of the glass set as well
    assert check(frames, margins=gt.Margins({"GLASS": {"found": 1.0, "extra": 1.5}}, cluttered_empty=1.5))[0].passed


def test_other_sets_are_shown_and_cannot_fail():
    res, text = check(changed(f"{K}_close_01", gt="MMM"))
    g = group(res, K)
    assert res.passed and not g.protected and g.status == gt.LOWER and not g.fails and res.lower == []
    assert "OTHER SETS, for information only" in text and f"barrel  {K}_close_01 #1: found -> missed" in text
    assert check(changed(f"{D}_snap_01", gt="MMM", boxes="NNNNN"))[0].passed       # Dave's set neither


def test_a_new_set_is_reported_as_new_and_does_not_fail():
    new = "4A8B_overhead_gray"
    res, text = check(BASE + [fr(f"{new}_core_01", "FMMM", boxes="FNN")])
    assert res.passed and group(res, new).status == gt.NEW and "[information only, new]" in text
    res, text = check(BASE, PROTECTED + (gt.Group("GRAY", (new,)),))                # on the list, but no frames anywhere
    assert res.passed and "GRAY is on the protected list but has no frames" in text
    res, text = check(BASE + [fr(f"{new}_core_01", "FMMM")], PROTECTED + (gt.Group("GRAY", (new,)),))
    assert res.passed and "not protected until a new baseline is saved" in text


def test_a_protected_set_that_cannot_be_compared_fails_and_says_why():
    res, text = check(BASE + [fr(f"{H}_core_01", "FF")])           # a frame added: more found is not "better"
    g = group(res, "HOME")
    assert not res.passed and g.status == gt.CHANGED and "3 frames -> 4 frames" in g.why and "HOME" in text.splitlines()[-1]
    res, _ = check(changed(f"{H}_cluster_01", gt="FFFMF"))         # a label changed
    assert not res.passed and "the labels of 1 frame(s) changed" in group(res, "HOME").why
    res, text = check([f for f in BASE if not f["stem"].startswith(C)])            # a protected set vanished
    assert not res.passed and group(res, "CAMPUS").status == gt.GONE and "cannot be compared (CAMPUS)" in text.splitlines()[-1]
    assert check(BASE + [fr(f"{K}_core_01", "F")])[0].passed       # the same on an extreme set: information


# ---------------------------------------------------------------- the protected list and the margins

def test_the_protected_list(tmp_path):
    assert gt.load_protected(tmp_path / "missing.json") == gt.DEFAULT_PROTECTED
    names = [g.name for g in gt.load_protected()]                   # the committed list
    assert names[:2] == ["HOME", "CAMPUS"] and len(names) == 6
    glass = next(g for g in gt.load_protected() if g.name == "GLASS")
    assert len(glass.sets) == 5 and all(s.endswith("_glass") for s in glass.sets)                 # one table, five lights, one set
    p = tmp_path / "protected.json"
    p.write_text(json.dumps({"protected": ["HOME", "campus", K, {"name": "GLASS", "sets": [GA, GB]}]}))
    got = gt.load_protected(p)
    assert got[0] == gt.Group("HOME", (H,)) and got[1].sets == (C,) and got[2] == gt.Group(K, (K,)) and got[3] == GLASS
    assert not check(changed(f"{K}_close_01", gt="MMM", boxes="NN"), got)[0].passed
    for bad in ({"protected": []}, {"protected": [{"name": "X"}]}, {"protected": ["HOME", "HOME"]}, {"protected": [3]}):
        p.write_text(json.dumps(bad))
        with pytest.raises(ValueError):
            gt.load_protected(p)


def test_the_margins_file(tmp_path):
    assert gt.load_margins(tmp_path / "missing.json").of("HOME") == (1.0, 1.0)
    p = tmp_path / "margins.json"
    p.write_text(json.dumps({"version": 1, "made": "2026-11-26", "git": "abc", "judge": {},
                             "gate": {"groups": {"HOME": {"found": 1.0, "extra": 1.0}, "BATH": {"found": 4.0, "extra": 1.0}}, "cluttered_empty": 1.2, "clean_empty": 0}}))
    m = gt.load_margins(p)
    assert m.of("BATH") == (4.0, 1.0) and m.cluttered_empty == 1.2 and m.clean_empty == 0 and "2026-11-26" in m.source
    p.write_text(json.dumps({"version": 1}))
    with pytest.raises(ValueError):
        gt.load_margins(p)
    if gt.MARGINS_PATH.exists():                                    # the committed margins cover every protected set, none below one unit
        m = gt.load_margins()
        for g in gt.load_protected():
            assert g.name in m.groups and min(m.of(g.name)) >= 1.0
        assert m.clean_empty == 0


# ---------------------------------------------------------------- the stored file

O, B = io.ORANGE, io.BLUE


def bx(color, x0, y0, w, h):
    return Barrel(color=color, bbox=(x0, y0, x0 + w, y0 + h))


def make_rep(worse=False, lower=False):
    """The synthetic report of test_report with the per-frame counts a real ``make_report`` adds. ``lower``: one
    campus barrel is lost (inside the margin). ``worse``: two are lost and a box sits on the clean empty home frame."""
    from test_report import make_rep as base_rep
    rep = base_rep()
    gts = {"4A8B_window_light_core_01": [bx(O, 100, 200, 50, 50)], "4A8B_window_light_neg_01": [],
           "4A8B_campus_light_core_01": [bx(O, 100, 200, 60, 60), bx(B, 300, 200, 60, 60)], "4A8B_campus_light_occl_01": [bx(B, 200, 150, 40, 40)]}
    preds = {s: list(g) for s, g in gts.items()}
    if lower or worse:
        preds["4A8B_campus_light_occl_01"] = []
    if worse:
        preds["4A8B_campus_light_core_01"] = [gts["4A8B_campus_light_core_01"][0]]
        preds["4A8B_window_light_neg_01"] = [bx(B, 10, 300, 30, 30)]
    rep.gts, rep.cand_boxes = gts, preds
    rep.cand_counts = rep.base_counts = {s: ct.classify_frame(s, preds[s], gts[s]) for s in gts}
    rep.placements = ct.build_placements(gts)
    return rep


def test_snapshot_of_a_report_and_the_file_round_trip(tmp_path):
    s = gt.snapshot(make_rep(), made="2026-11-26")
    assert (s["version"], s["made"], s["git"], s["split"], s["home_protocol"]) == (2, "2026-11-26", "abc1234", "train", "loso")
    assert [f["stem"].split("_", 2)[2] for f in s["frames"]] == ["light_core_01", "light_neg_01", "light_core_01", "light_occl_01"]
    core = s["frames"][2]
    assert core == {"stem": "4A8B_campus_light_core_01", "set": "4A8B_campus_light", "arr": "4A8B/campus_study/core/01", "pl": [0, 1], "gt": "FF", "boxes": "FF", "clean": True}
    assert s["det"]["body_width"] == 1.2 and "a/config.json" in s["arm"]
    path = gt.save_baseline(s, tmp_path / "baseline" / "baseline.json")
    assert gt.load_baseline(path) == s
    assert len(path.read_text().splitlines()) > len(s["frames"])   # one frame per line: a change is a one-line diff
    assert gt.compare(s, gt.snapshot(make_rep(lower=True))).groups[1].barrels == ["4A8B_campus_light_occl_01 #1: found -> missed"]
    path.write_text(json.dumps(s | {"version": 1}))
    with pytest.raises(ValueError, match="save a new one"):
        gt.load_baseline(path)
    with pytest.raises(ValueError, match="lacks"):
        gt.validate(snap([{"stem": "x", "set": H}]))
    from test_report import make_rep as bare
    with pytest.raises(ValueError, match="no per-frame counts"):
        gt.snapshot(bare())                                         # a report that was not made by make_report


# ---------------------------------------------------------------- the command

def test_command_save_baseline_then_gate(tmp_path, monkeypatch, capsys):
    tool = load_tool("report")
    path = tmp_path / "baseline.json"
    calls = []
    current = {"rep": make_rep()}

    def fake(cand, base, **kw):
        calls.append((cand, base, kw))
        return current["rep"]
    monkeypatch.setattr(tool.rp, "make_report", fake)
    args = ["--baseline", str(path)]

    assert tool.main(["--gate"] + args) == 2 and "no stored baseline" in capsys.readouterr().out      # nothing saved yet
    assert calls == []                                                                              # and nothing was run
    assert tool.main(["--save-baseline"] + args) == 0 and path.exists()
    assert calls[-1][0] is calls[-1][1] and calls[-1][2] == {}                                      # one arm, every set, train, loso
    assert "baseline saved" in capsys.readouterr().out
    assert tool.main(["--gate"] + args) == 0
    assert capsys.readouterr().out.rstrip().splitlines()[-1].startswith("RESULT: PASS")

    current["rep"] = make_rep(lower=True)                           # one barrel lost: inside the margin
    assert tool.main(["--gate", "--cand-det", "cap_behind=false"] + args) == 0
    assert calls[-1][0].det_overrides == {"cap_behind": False}
    out = capsys.readouterr().out
    assert "4A8B_campus_light_occl_01 #1: found -> missed" in out and "Lower inside the margin: CAMPUS" in out
    before = path.read_text()                                       # ... the check passes, but the reference does not slide down
    assert tool.main(["--save-baseline"] + args) == 1 and path.read_text() == before
    assert "NOT SAVED" in capsys.readouterr().out

    current["rep"] = make_rep(worse=True)                           # two lost and a box on the clean empty frame
    assert tool.main(["--gate"] + args) == 1
    out = capsys.readouterr().out
    assert "CAMPUS" in out.rstrip().splitlines()[-1] and "4A8B_window_light_neg_01" in out and out.rstrip().splitlines()[-1].startswith("RESULT: FAIL")
    assert tool.main(["--save-baseline"] + args) == 1 and path.read_text() == before
    capsys.readouterr()
    assert tool.main(["--save-baseline", "--force"] + args) == 0 and path.read_text() != before

    path.write_text(json.dumps({"version": 1, "rows": []}))        # a baseline of the first version
    capsys.readouterr()
    assert tool.main(["--gate"] + args) == 2 and "cannot be used" in capsys.readouterr().out
    assert tool.main(["--save-baseline"] + args) == 0 and gt.load_baseline(path)["version"] == 2


def test_command_gate_refuses_options_that_would_change_what_is_compared():
    tool = load_tool("report")
    for bad in (["--gate", "--sets", "HOME"], ["--gate", "--split", "test"], ["--save-baseline", "--home-protocol", "fixed"],
                ["--gate", "--cand-model", "vendor"], ["--gate", "--save-baseline"]):
        with pytest.raises(SystemExit):
            tool.main(bad)
