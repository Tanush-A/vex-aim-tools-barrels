"""The never-regress check (src/barrels/gate.py, TODO I): a stored baseline against a run, row by row. Plain
numbers in, pass / fail and the rows that changed out; no image is opened."""
import copy
import json

import pytest

from barrels import gate as gt, report as rp
from test_vendor import load_tool

H, C, K, D = "4A8B_window_light", "4A8B_campus_light", "4A8B_window_black", "DAVE_office_speckle"
LABEL = {H: "HOME", C: "CAMPUS", K: K, D: "DAVE*"}


def row(set_key, scene, frames, barrels, found, false=0, neg_false=0):
    return {"set": set_key, "label": LABEL.get(set_key, set_key), "scene": scene, "frames": frames, "barrels": barrels,
            "found": found, "missed": barrels - found, "false": false, "neg_false": neg_false}


def snap(rows, **head):
    return {"version": 1, "made": "2026-11-18", "git": "abc1234", "arm": "today", "rows": copy.deepcopy(rows)} | head


BASE = [row(H, "cluster", 2, 8, 6), row(H, "neg", 2, 0, 0), row(H, "", 4, 8, 6),
        row(C, "core", 1, 4, 4), row(C, "occl", 1, 1, 0), row(C, "", 2, 5, 4),
        row(K, "close", 1, 3, 1), row(K, "neg", 1, 0, 0), row(K, "", 2, 3, 1),                 # an extreme set: shown, never fails
        row(D, "snap", 12, 34, 12, false=2), row(D, "", 12, 34, 12, false=2)]


def changed(set_key, scene, **new):
    """BASE with one scenario row changed (``missed`` follows ``found``)."""
    rows = copy.deepcopy(BASE)
    for r in rows:
        if (r["set"], r["scene"]) == (set_key, scene):
            r.update(new); r["missed"] = r["barrels"] - r["found"]
    return rows


def check(rows, protected=gt.DEFAULT_PROTECTED):
    res = gt.compare(snap(BASE), snap(rows, git="def5678", arm="candidate"), protected)
    return res, gt.format_gate(res)


# ---------------------------------------------------------------- the rule

def test_a_candidate_equal_to_the_baseline_passes():
    res, text = check(BASE)
    assert res.passed and res.failures == [] and all(r.status == "same" for r in res.rows)
    assert text.splitlines()[-1].startswith("RESULT: PASS") and "GOT WORSE in a protected set: none" in text
    assert "HOME" in text and "found 6 -> 6 of 8" in text and "[protected]" in text and "[information only]" in text


def test_losing_a_barrel_in_one_home_scenario_fails_and_names_the_row():
    res, text = check(changed(H, "cluster", found=4))
    assert not res.passed and [r.name for r in res.failures] == ["HOME cluster"]
    assert "GOT WORSE in a protected set: 1 row(s)" in text and "found 6 -> 4 of 8 (lost 2)" in text
    last = text.splitlines()[-1]
    assert last.startswith("RESULT: FAIL") and "HOME cluster" in last


def test_gaining_a_false_box_in_campus_fails_even_with_one_more_barrel_found():
    res, text = check(changed(C, "occl", found=1, false=1))
    assert not res.passed and [r.name for r in res.failures] == ["CAMPUS occl"]
    assert "false boxes 0 -> 1 (1 more)" in text and "(gained 1)" in text


def test_a_gain_passes_and_is_listed():
    res, text = check(changed(C, "occl", found=1))
    assert res.passed and [r.name for r in res.rows if r.status == "better"] == ["CAMPUS occl"]
    assert "GOT BETTER in a protected set: 1 row(s)" in text and "found 0 -> 1 of 1 (gained 1)" in text
    res, _ = check(changed(D, "snap", false=0))                     # fewer false boxes is better too
    assert res.passed and [r.status for r in res.rows if r.set == D] == ["better"]


def test_a_drop_on_an_extreme_set_is_shown_and_does_not_fail():
    res, text = check(changed(K, "close", found=0))
    assert res.passed and [r.name for r in res.rows if r.status == "worse"] == [f"{K} close"]
    assert "Other sets, for information only: got worse: 1 row(s)" in text and "found 1 -> 0 of 3 (lost 1)" in text
    assert "GOT WORSE in a protected set: none" in text
    res, _ = check(changed(D, "snap", found=5, false=9))            # Dave's set neither
    assert res.passed


def test_a_new_set_is_reported_as_new_and_does_not_fail():
    new = "4A8B_overhead_gray"
    rows = BASE + [row(new, "core", 1, 4, 1, false=2), row(new, "neg", 2, 0, 0), row(new, "", 3, 4, 1, false=2)]
    res, text = check(rows)
    assert res.passed and [r.status for r in res.rows if r.set == new] == ["new", "new"]
    assert "NEW since the baseline (not compared, cannot fail): 1 row(s)" in text and f"{new} (whole set)" in text
    # a new scenario inside a protected set is new too, not a failure
    res, text = check(BASE + [row(C, "window", 1, 2, 0)])
    assert res.passed and "CAMPUS window" in text


def test_a_box_on_an_empty_frame_of_any_set_fails():
    for set_key, name in ((K, f"{K} neg"), (H, "HOME neg")):
        res, text = check(changed(set_key, "neg", false=1, neg_false=1))
        assert not res.passed and name in [r.name for r in res.failures]
        assert "NEW BOX ON AN EMPTY FRAME (any set): 1 row(s)" in text and "a new box on an empty frame" in text.splitlines()[-1]
    new = "4A8B_overhead_gray"                                      # ... a set the baseline has never seen included
    res, _ = check(BASE + [row(new, "neg", 2, 0, 0, false=1, neg_false=1), row(new, "", 2, 0, 0, false=1, neg_false=1)])
    assert not res.passed and [r.name for r in res.failures] == [f"{new} neg"]
    # a box the baseline already had is not a NEW box
    had = copy.deepcopy(BASE); had[7].update(false=1, neg_false=1)
    assert gt.compare(snap(had), snap(had)).passed


def test_a_protected_row_that_cannot_be_compared_fails_and_says_why():
    res, text = check(changed(H, "cluster", frames=3, barrels=12, found=10))        # frames added: 10 found is not "better"
    assert not res.passed and res.failures[0].status == "changed"
    assert "CANNOT BE COMPARED" in text and "2 frames, 8 barrels -> 3 frames, 12 barrels" in text
    res, text = check([r for r in BASE if (r["set"], r["scene"]) != (C, "occl")])  # a protected row vanished
    assert not res.passed and res.failures[0].status == "gone" and "CAMPUS occl" in text.splitlines()[-1]
    res, _ = check(changed(K, "close", frames=2, barrels=5, found=0))               # the same on an extreme set: information
    assert res.passed


# ---------------------------------------------------------------- the protected list

def test_protecting_a_new_condition(tmp_path):
    assert gt.load_protected(tmp_path / "missing.json") == ("HOME", "CAMPUS")
    assert gt.load_protected() == ("HOME", "CAMPUS")                # the committed list
    p = tmp_path / "protected.json"
    p.write_text(json.dumps({"protected": ["HOME", "CAMPUS", K.lower()]}))
    protected = gt.load_protected(p)
    res, text = check(changed(K, "close", found=0), protected)
    assert not res.passed and [r.name for r in res.failures] == [f"{K} close"]
    p.write_text(json.dumps({"protected": []}))
    with pytest.raises(ValueError):
        gt.load_protected(p)
    res, text = check(BASE, ("HOME", "CAMPUS", "4A8B_overhead_gray"))               # listed, but no baseline rows yet
    assert res.passed and "4A8B_overhead_gray is on the protected list but has no rows in the stored baseline" in text


# ---------------------------------------------------------------- the stored file

def test_snapshot_of_a_report_and_the_file_round_trip(tmp_path):
    from test_report import make_rep
    s = gt.snapshot(make_rep(), made="2026-11-18")
    assert (s["version"], s["made"], s["git"], s["split"], s["home_protocol"]) == (1, "2026-11-18", "abc1234", "train", "loso")
    assert [(r["label"], r["scene"]) for r in s["rows"]] == [("HOME", "core"), ("HOME", "neg"), ("HOME", ""),
                                                             ("CAMPUS", "core"), ("CAMPUS", "occl"), ("CAMPUS", "")]     # no ALL row
    campus = s["rows"][-1]
    assert (campus["frames"], campus["barrels"], campus["found"], campus["missed"], campus["false"], campus["neg_false"]) == (2, 3, 2, 1, 0, 0)
    assert s["det"]["body_width"] == 1.2 and "a/config.json" in s["arm"]
    path = gt.save_baseline(s, tmp_path / "baseline" / "baseline.json")
    assert gt.load_baseline(path) == s
    assert len(path.read_text().splitlines()) > len(s["rows"])     # one row per line: a change is a one-line diff
    path.write_text(json.dumps(s | {"version": 2}))
    with pytest.raises(ValueError, match="version"):
        gt.load_baseline(path)
    with pytest.raises(ValueError, match="lacks"):
        gt.validate(snap([{"set": H, "scene": ""}]))


# ---------------------------------------------------------------- the command

def swapped(rep):
    """The synthetic report with its two arms exchanged: the 'candidate' now misses a campus barrel, draws a
    false box there and a box on the clean empty home frame."""
    return rp.Report([rp.Row(r.set_key, r.label, r.scene, r.kind, r.base, r.cand, r.indicative) for r in rep.rows],
                     rep.baseline, rep.candidate, rep.selection, rep.home_protocol, rep.git, rep.seconds)


def test_command_save_baseline_then_gate(tmp_path, monkeypatch, capsys):
    from test_report import make_rep
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

    current["rep"] = swapped(make_rep())                            # a worse candidate
    assert tool.main(["--gate", "--cand-det", "min_width_px=20"] + args) == 1
    assert calls[-1][0].det_overrides == {"min_width_px": 20.0}
    out = capsys.readouterr().out
    assert "CAMPUS core" in out and "HOME neg" in out and out.rstrip().splitlines()[-1].startswith("RESULT: FAIL")

    before = path.read_text()                                       # a worse baseline is not saved by accident
    assert tool.main(["--save-baseline"] + args) == 1 and path.read_text() == before
    assert "NOT SAVED" in capsys.readouterr().out
    assert tool.main(["--save-baseline", "--force"] + args) == 0 and path.read_text() != before


def test_command_gate_refuses_options_that_would_change_what_is_compared():
    tool = load_tool("report")
    for bad in (["--gate", "--sets", "HOME"], ["--gate", "--split", "test"], ["--save-baseline", "--home-protocol", "fixed"],
                ["--gate", "--cand-model", "vendor"], ["--gate", "--save-baseline"]):
        with pytest.raises(SystemExit):
            tool.main(bad)
