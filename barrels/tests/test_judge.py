"""The standard pass rule (src/barrels/judge.py, tools/judge.py; TODO M3): which frames are judged, the test-frame
refusal, detectors on frames, leave one place out, the verdict from the clauses and their margins, the pages. Synthetic
boxes and a stand-in for the image reader; the two tests at the end touch committed train frames only."""
import json

import pytest

from barrels import conditions as cnd, counting as ct, io, judge as jg, report as rp
from barrels.detect_types import Barrel
from test_vendor import load_tool

O, B = io.ORANGE, io.BLUE
HOME, CAMPUS, GA, GB, BLACK = "4A8B_window_light", "4A8B_campus_light", "4A8B_lampwarm6_glass", "4A8B_lampmid6_glass", "4A8B_window_black"
M = jg.Margins(found_gain=4.0, found_loss=10.0, extra_rise=2.0, extra_fall=1.0, cluttered_empty=1.0,
               place={"home_white": 1.0, "campus_study": 1.0, "home_glass": 1.5}, source="test")


def bx(color, x0, y0, w, h):
    return Barrel(color=color, bbox=(x0, y0, x0 + w, y0 + h))


def T(found_w, placements=100, **kw):
    return ct.Tally(found_w=found_w, placements=placements, found=int(found_w), barrels=placements, **kw)


def verdict(base, cand, places=None, m=M):
    return jg.decide(base, cand, places or {}, m)


# ---------------------------------------------------------------- the verdict: numbers in, PASS / FAIL / NO CLEAR DIFFERENCE out

def test_nothing_moved_is_no_clear_difference():
    v = verdict(T(60), T(60), {"home_white": (T(20, 29), T(20, 29))})
    assert v.result == jg.NO_CLEAR and [c.state for c in v.clauses] == [jg.WITHIN] * 4
    assert [c.key for c in v.clauses] == ["found", "place", "extra", "empty"] and "no place moved" in v.clauses[1].text


def test_a_gain_must_be_larger_than_the_margin_to_pass():
    assert verdict(T(60), T(64)).result == jg.NO_CLEAR                # exactly the largest gain a meaningless change made
    assert verdict(T(60), T(64 + 1 / 3)).result == jg.PASS
    v = verdict(T(60), T(70))
    assert v.result == jg.PASS and v.state("found") == jg.BETTER and "found is up by more than the noise" in v.reason
    assert "60.0 -> 70.0 of 100 placements (+10.0" in v.clauses[0].text and "Better above +4.0, worse below -10.0" in v.clauses[0].text


def test_a_margin_per_direction():
    """A change that means nothing loses far more than it gains, so the two margins differ."""
    assert verdict(T(60), T(55)).result == jg.NO_CLEAR                # 5 down: inside the loss margin of 10
    assert verdict(T(60), T(65)).result == jg.PASS                    # 5 up: above the gain margin of 4
    assert verdict(T(60), T(50)).result == jg.NO_CLEAR                # exactly the loss margin
    v = verdict(T(60), T(49.5))
    assert v.result == jg.FAIL and v.state("found") == jg.WORSE and "found over all places" in v.reason


def test_one_place_worse_by_more_than_its_margin_fails_whatever_the_total():
    places = {"home_white": (T(28, 29), T(26, 29)), "home_glass": (T(10, 15), T(20, 15)), "campus_study": (T(35, 35), T(34, 35))}
    v = verdict(T(73), T(80), places)                                 # +7 in all, but home lost 2 of 29 (margin 1)
    assert v.result == jg.FAIL and v.state("found") == jg.BETTER and v.state("place") == jg.WORSE
    assert "found at home_white" in v.reason
    text = v.clauses[1].text
    assert "home_white -2.0 of 29 (margin 1.0, WORSE)" in text and "campus_study -1.0 of 35 (margin 1.0)" in text and "home_glass +10.0" in text
    places["home_white"] = (T(28, 29), T(27, 29))                     # one barrel: exactly the margin
    assert verdict(T(73), T(81), places).result == jg.PASS
    v = verdict(T(60), T(60), {"new_place": (T(10, 15), T(8.5, 15))})          # a place the noise run never measured: one unit, and it says so
    assert v.result == jg.FAIL and "not measured at this place" in v.clauses[1].text


def test_boxes_that_are_not_on_their_barrel():
    v = verdict(T(60, extra_w=5.0), T(70, extra_w=7.5))               # found up, but 2.5 more boxes (margin 2)
    assert v.result == jg.FAIL and v.state("extra") == jg.WORSE and "boxes that are not on their barrel" in v.reason
    assert verdict(T(60, extra_w=5.0), T(70, extra_w=7.0)).result == jg.PASS
    v = verdict(T(60, extra_w=5.0), T(60, extra_w=3.5))               # 1.5 fewer boxes, found the same
    assert v.result == jg.PASS and v.state("extra") == jg.BETTER and "found is not lower" in v.reason
    assert verdict(T(60, extra_w=5.0), T(59.5, extra_w=3.5)).result == jg.NO_CLEAR      # fewer boxes bought with a barrel: not a pass
    assert verdict(T(60, extra_w=5.0), T(60, extra_w=4.0)).result == jg.NO_CLEAR        # exactly the margin


def test_empty_frames_clean_ones_have_no_margin():
    v = verdict(T(60), T(75, clean_empty=1))
    assert v.result == jg.FAIL and v.state("empty") == jg.WORSE and "boxes on empty frames" in v.reason
    assert verdict(T(60, clean_empty=1), T(75, clean_empty=1)).result == jg.PASS         # the baseline had it too
    assert verdict(T(60), T(75, cluttered_empty_w=0.6)).result == jg.PASS                # clutter: inside the margin of 1
    assert verdict(T(60), T(75, cluttered_empty_w=1.2)).result == jg.FAIL


def test_margins_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="noise_floor/run.py"):
        jg.load_margins(tmp_path / "missing.json")
    p = tmp_path / "margins.json"
    block = {"found_gain": 4.0, "found_loss": 10.92, "extra_rise": 1.85, "extra_fall": 1.0, "cluttered_empty": 1.0, "clean_empty": 0.0,
             "place": {"abp_gray": 6.0}, "place_default": 1.0}
    p.write_text(json.dumps({"version": 1, "made": "2026-11-26", "git": "abc", "judge": block, "gate": {}}))
    m = jg.load_margins(p)
    assert (m.found_gain, m.found_loss, m.extra_rise, m.extra_fall) == (4.0, 10.92, 1.85, 1.0)
    assert m.for_place("abp_gray") == 6.0 and m.for_place("elsewhere") == 1.0 and "2026-11-26" in m.source
    p.write_text(json.dumps({"version": 2}))
    with pytest.raises(ValueError):
        jg.load_margins(p)
    if jg.MARGINS_PATH.exists():                                      # the committed margins: every ordinary place measured, nothing under one unit
        m = jg.load_margins()
        places = {cnd.info(k).place for k in cnd.load_table() if cnd.info(k).klass == cnd.ORDINARY}
        assert places <= set(m.place) and min(m.place.values()) >= 1.0
        assert min(m.found_gain, m.found_loss, m.extra_rise, m.extra_fall, m.cluttered_empty) >= 1.0 and m.clean_empty == 0


# ---------------------------------------------------------------- which frames; nothing but train frames

SPLITS = {"train": [f"{HOME}_core_01", f"{HOME}_neg_01", f"{CAMPUS}_core_01", f"{GA}_core_01", f"{GB}_core_01", f"{BLACK}_core_01",
                    "4A8B_lampwarm1_wood_core_01", "4A8B_window_shop_core_01", f"{HOME}_calib_01"],
          "dev": [], "test": [f"{HOME}_core_04", f"{GA}_occl_01"], "measured": []}
GTS = {f"{HOME}_core_01": [bx(O, 100, 200, 50, 60), bx(B, 300, 200, 50, 60)], f"{HOME}_neg_01": [], f"{CAMPUS}_core_01": [bx(O, 100, 200, 50, 60)],
       f"{GA}_core_01": [bx(B, 200, 200, 50, 60)], f"{GB}_core_01": [bx(B, 200, 200, 50, 60)], f"{BLACK}_core_01": [bx(O, 100, 200, 50, 60)]}
ORD = [f"{HOME}_core_01", f"{HOME}_neg_01", f"{CAMPUS}_core_01", f"{GA}_core_01", f"{GB}_core_01"]
FRAMES = {cnd.ORDINARY: ORD, cnd.EXTREME: [f"{BLACK}_core_01"], cnd.EXCLUDED: [], cnd.UNLISTED: []}


def truth():
    return jg.Truth(GTS, {s: True for s in GTS}, ct.build_placements(GTS))


def test_train_frames_by_class_and_never_a_test_frame(tmp_path):
    for s in SPLITS["train"] + SPLITS["test"] + ["DAVE_office_speckle_snap_01", "4A8B_sun_light_core_01"]:
        (tmp_path / f"{s}_boxes.json").write_text("{}")
    fr = jg.train_frames(tmp_path, SPLITS)
    assert fr[cnd.ORDINARY] == [f"{HOME}_core_01", f"{HOME}_neg_01", f"{CAMPUS}_core_01", f"{GB}_core_01", f"{GA}_core_01"]
    assert fr[cnd.EXTREME] == [f"{BLACK}_core_01"] and fr[cnd.EXCLUDED] == ["4A8B_lampwarm1_wood_core_01"]
    assert fr[cnd.UNLISTED] == ["4A8B_window_shop_core_01"]            # not in data/conditions.json: reported, never judged
    everything = [s for v in fr.values() for s in v]
    assert not set(everything) & set(SPLITS["test"]) and not any(s.startswith("DAVE") or "calib" in s or "sun" in s for s in everything)


def test_require_train_refuses_test_frames_and_frames_of_no_split():
    jg.require_train(ORD, SPLITS)
    with pytest.raises(rp.TestFrameError):
        jg.require_train(ORD + [f"{GA}_occl_01"], SPLITS)
    with pytest.raises(ValueError, match="not train frames"):
        jg.require_train(["4A8B_sun_light_core_01"], SPLITS)


@pytest.fixture
def no_images(monkeypatch):
    """``judge.load_frame`` without the disk: the train check stays, the frame is a stand-in. Returns the list of
    stems that were opened."""
    opened = []

    def fake(stem, splits=None):
        jg.require_train([stem], splits)
        opened.append(stem)
        return f"frame of {stem}"
    monkeypatch.setattr(jg, "load_frame", fake)
    return opened


def perfect(stem, frame):
    return list(GTS[stem])


def test_run_many_reads_each_frame_once_and_counts_every_detector(no_images):
    seen = []

    def nothing(stem, frame):
        seen.append((stem, frame))
        return []
    runs = jg.run_many({"perfect": perfect, "nothing": nothing}, ORD, truth(), SPLITS)
    assert no_images == ORD and seen == [(s, f"frame of {s}") for s in ORD]
    assert runs["perfect"].counts[f"{HOME}_core_01"].gt == (ct.FOUND, ct.FOUND) and runs["nothing"].counts[f"{HOME}_core_01"].gt == (ct.MISSED, ct.MISSED)
    assert runs["perfect"].boxes[f"{CAMPUS}_core_01"] == GTS[f"{CAMPUS}_core_01"] and runs["nothing"].name == "nothing"


def test_run_many_refuses_a_test_frame_before_anything_is_opened(no_images):
    called = []
    with pytest.raises(rp.TestFrameError):
        jg.run_many({"x": lambda s, f: called.append(s) or []}, ORD + [f"{HOME}_core_04"], truth(), SPLITS)
    assert no_images == [] and called == []
    with pytest.raises(TypeError, match="Barrel"):
        jg.run_many({"bad": lambda s, f: [(1, 2, 3, 4)]}, ORD[:1], truth(), SPLITS)


def test_leave_one_place_out_never_fits_on_the_place_it_scores(no_images):
    fits = []

    def fit(stems, held):
        fits.append((held, sorted(stems)))
        return lambda stem, frame: [bx(O, 1, 1, 5, 5)] if held == "home_glass" else list(GTS[stem])
    d = jg.leave_one_place_out(fit, ORD)
    runs = jg.run_many({"lopo": d}, ORD + [f"{BLACK}_core_01"], truth(), SPLITS)
    assert [h for h, _ in fits] == ["home_white", "campus_study", "home_glass", "home_black"]      # once per place, when its first frame comes up
    for held, stems in fits:
        assert held not in {ct.place_of(s) for s in stems}
    assert dict(fits)["home_glass"] == sorted(ORD[:3]) and dict(fits)["home_black"] == sorted(ORD)   # an extreme place: fitted on all ordinary frames
    assert runs["lopo"].counts[f"{GA}_core_01"].gt == (ct.MISSED,) and runs["lopo"].counts[f"{HOME}_core_01"].gt == (ct.FOUND, ct.FOUND)
    with pytest.raises(TypeError, match="must return"):
        jg.leave_one_place_out(lambda stems, held: None, ORD)(ORD[0], None)


# ---------------------------------------------------------------- two runs -> the judgement

def worse_at_glass(stem, frame):
    """Loses the glass barrel under one of its two lights, draws its box low at campus, and a box on the empty frame."""
    if stem == f"{GA}_core_01":
        return []
    if stem == f"{CAMPUS}_core_01":
        return [bx(O, 100, 200, 50, 75)]
    if stem == f"{HOME}_neg_01":
        return [bx(B, 10, 300, 30, 30)]
    if stem == f"{BLACK}_core_01":
        return []
    return list(GTS[stem])


def test_compare_lists_every_barrel_and_box_that_changed(no_images):
    stems = ORD + [f"{BLACK}_core_01"]
    runs = jg.run_many({"baseline": perfect, "candidate": worse_at_glass}, stems, truth(), SPLITS)
    j = jg.compare(runs["baseline"], runs["candidate"], FRAMES, truth(), M)
    b, c = j.total
    assert (b.placements, b.barrels, b.found_w, c.found_w) == (4, 5, 4.0, 2.5)                 # the glass barrel is one placement under two lights
    assert j.places["home_glass"][1].found_w == 0.5 and j.conditions["lampwarm6_glass"][1].found == 0
    assert [(x.stem, x.before, x.after, x.kind, x.judged) for x in j.changes] == [
        (f"{CAMPUS}_core_01", "found", "off", "lost", True), (f"{GA}_core_01", "found", "missed", "lost", True),
        (f"{BLACK}_core_01", "found", "missed", "lost", False)]
    assert [x["stem"] for x in j.box_changes] == [f"{HOME}_neg_01"] and j.box_changes[0]["after"]["nothing"] == 1 and j.box_changes[0]["clean"]
    assert j.result == jg.FAIL and j.verdict.state("empty") == jg.WORSE and j.verdict.state("place") == jg.WITHIN      # -1.0 at campus, -0.5 at glass
    assert list(j.report_only) == ["window_black"]                     # tabulated, not judged
    text = jg.format_judgement(j)
    assert text.splitlines()[-1].startswith("VERDICT: FAIL.") and "BARRELS THAT CHANGED on the ordinary conditions: 0 gained, 2 lost" in text
    assert f"- {GA}_core_01 #1 blue at [200, 200, 250, 260]: found -> missed" in text and "[empty frame, clean]: nothing 0 -> 1" in text
    assert "REPORT ONLY" in text and "report only: 0 gained, 1 lost" in text and "BY PLACE" in text
    back = jg.compare(runs["candidate"], runs["baseline"], FRAMES, truth(), M)                 # the other way round: 2 gained
    assert [x.kind for x in back.changes if x.judged] == ["gained", "gained"]
    with pytest.raises(ValueError, match="no result for"):
        jg.compare(runs["baseline"], jg.Run("short", counts={ORD[0]: runs["baseline"].counts[ORD[0]]}), FRAMES, truth(), M)


def test_judge_in_one_call_against_itself_and_leave_one_place_out(no_images, tmp_path):
    j = jg.judge(perfect, perfect, frames=FRAMES, truth=truth(), margins=M, splits=SPLITS, out_dir=tmp_path / "out")
    assert j.result == jg.NO_CLEAR and j.changes == [] and j.box_changes == [] and not j.lopo
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["changes.csv", "judge.json", "judge.md"]
    d = json.loads((tmp_path / "out" / "judge.json").read_text())
    assert d["verdict"] == jg.NO_CLEAR and d["total"]["candidate"]["found_w"] == 4.0 and d["margins"]["found_gain"] == 4.0 and len(d["places"]) == 3
    assert (tmp_path / "out" / "judge.md").read_text().rstrip().splitlines()[-2].startswith("VERDICT: NO CLEAR DIFFERENCE")
    j = jg.judge(fit=lambda stems, held: perfect, baseline=lambda s, f: [], frames=FRAMES, truth=truth(), margins=M, splits=SPLITS,
                 report_only=False, name="idea")
    assert j.lopo and j.candidate.name == "idea" and j.report_only == {} and "LEAVE ONE PLACE OUT" in jg.format_judgement(j)
    assert j.result == jg.NO_CLEAR and len([x for x in j.changes if x.kind == "gained"]) == 5      # +4 placements: exactly the gain margin, not above it
    with pytest.raises(ValueError, match="exactly one"):
        jg.judge(perfect, fit=lambda stems, held: perfect, frames=FRAMES, truth=truth(), margins=M, splits=SPLITS)
    with pytest.raises(ValueError, match="exactly one"):
        jg.judge(frames=FRAMES, truth=truth(), margins=M, splits=SPLITS)


# ---------------------------------------------------------------- the command

def test_load_callable(tmp_path):
    p = tmp_path / "idea.py"
    p.write_text("def detect_frame(stem, frame):\n    return []\n\ndef fit(stems, held):\n    return detect_frame\n")
    f = jg.load_callable(f"{p}:detect_frame")
    assert f("x", None) == [] and jg.load_callable(f"{p}:fit")([], "p") is not None
    for bad in (str(p), f"{p}:nope", f"{tmp_path / 'missing.py'}:f"):
        with pytest.raises(ValueError):
            jg.load_callable(bad)


def test_command_says_what_it_needs_and_returns_the_verdict_as_exit_code(tmp_path, monkeypatch, capsys, no_images):
    tool = load_tool("judge")
    for bad in ([], ["--cand-det", "min_width_px=20", "--cand-fit", "x.py:f"], ["--cand-model", "default", "--cand-callable", "x.py:f"]):
        with pytest.raises(SystemExit):
            tool.main(bad)
    p = tmp_path / "idea.py"
    p.write_text("def detect_frame(stem, frame):\n    return []\n")
    calls, real = [], jg.judge

    def fake(cand, base, fit=None, name="candidate", report_only=True):
        calls.append((cand, base, fit, name, report_only))
        return real(perfect, cand, frames=FRAMES, truth=truth(), margins=M, splits=SPLITS, name=name)     # the loaded function as the baseline: 4 placements gained
    monkeypatch.setattr(tool.jg, "judge", fake)
    assert tool.main(["--cand-callable", f"{p}:detect_frame", "--name", "idea", "--no-extreme", "--no-save"]) == 3      # +4.0: not above the margin
    assert calls[-1][1] is None and calls[-1][3:] == ("idea", False) and "the function" in calls[-1][0].describe
    out = capsys.readouterr().out
    assert out.rstrip().splitlines()[-1].startswith("VERDICT: NO CLEAR DIFFERENCE") and "written to" not in out
    assert tool.main(["--cand-callable", f"{p}:detect_frame", "--out", str(tmp_path / "pages")]) == 3
    assert (tmp_path / "pages" / "judge.md").exists() and "written to" in capsys.readouterr().out
    assert tool.EXIT == {jg.PASS: 0, jg.FAIL: 1, jg.NO_CLEAR: 3}


# ---------------------------------------------------------------- committed train frames (skipped when the data is not there)

def real_home_frames():
    try:
        return [s for s in jg.train_frames()[cnd.ORDINARY] if s.startswith(HOME)][:3]
    except Exception:  # noqa: BLE001
        return []


def test_a_frame_is_read_only_and_a_test_frame_is_never_opened(monkeypatch):
    stems = real_home_frames()
    if not stems or io.find_image(stems[0]) is None:
        pytest.skip("no committed frames")
    frame = jg.load_frame(stems[0])
    with pytest.raises(ValueError):
        frame.rgb[0, 0, 0] = 0                                        # no step may change a pixel
    with pytest.raises(ValueError):
        frame.bgr[0, 0, 0] = 0
    from barrels import splits as sp
    test_stem = sp.load_splits()["test"][0]

    def never(*a, **k):
        raise AssertionError("a test frame was opened")
    monkeypatch.setattr(io, "load_image", never)
    monkeypatch.setattr(io, "find_image", never)
    with pytest.raises(rp.TestFrameError):
        jg.load_frame(test_stem)


def test_todays_detector_against_itself_changes_nothing():
    stems = real_home_frames()
    if not stems or io.find_image(stems[0]) is None or not jg.MARGINS_PATH.exists():
        pytest.skip("no committed frames or margins")
    frames = {cnd.ORDINARY: stems, cnd.EXTREME: [], cnd.EXCLUDED: [], cnd.UNLISTED: []}
    j = jg.judge(jg.fixed_detector(), frames=frames)
    assert j.result == jg.NO_CLEAR and j.changes == [] and j.box_changes == [] and j.total[0].found == j.total[1].found > 0
