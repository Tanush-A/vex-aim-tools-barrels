"""The vendor arm of the eval report (src/barrels/report.py, TODO H): the robot's built-in detector scored from
its saved files by the same rule against the same labels, on the frames that have a vendor file; the two looser
counts. Synthetic labels and vendor files in a temp folder; no image is opened and no real frame is touched."""
import csv
import json

import pytest

from barrels import capture, io, report as rp
from barrels.detect_types import Barrel
from test_vendor import BALL_ITEM, BLUE_ITEM, ORANGE_ITEM, TAG_ITEM, aiobj, load_tool, record_for

O, B = io.ORANGE, io.BLUE
SET = "4A8B_shop_white"
ORANGE_BOX, BLUE_BOX = [200, 120, 250, 180], [20, 40, 80, 120]        # ORANGE_ITEM / BLUE_ITEM in our 640x480 pixels


def stem(scene, n=1):
    return f"{SET}_{scene}_{n:02d}"


NOT_AVAILABLE = capture.vendor_record(capture.grab_vendor(object()))     # available: false, with the reason
# stem -> (true barrels, what the vendor file holds: a record, None = no file, or a str = the file's raw text)
FRAMES = {
    stem("core", 1): ([("orange", ORANGE_BOX), ("blue", BLUE_BOX)], record_for(ORANGE_ITEM, BLUE_ITEM, BALL_ITEM, TAG_ITEM)),   # the vendor is right
    stem("core", 2): ([("orange", ORANGE_BOX)], record_for(aiobj("OrangeBarrel", 2, 50, 50, 0, 0))),      # saw a barrel with no box: a miss
    stem("neg", 1): ([], record_for(ORANGE_ITEM)),                                                        # a box on an empty table
    stem("occl", 1): ([("blue", BLUE_BOX)], NOT_AVAILABLE),                                               # not measured
    stem("clutter", 1): ([("blue", BLUE_BOX)], record_for(BALL_ITEM, aiobj("Robot", 3, 5, 5, 50, 50))),   # only non-barrel objects: a miss
    stem("touch", 1): ([("orange", ORANGE_BOX)], None),                                                   # no vendor file
    stem("far", 1): ([("orange", ORANGE_BOX)], record_for(aiobj("OrangeBarrel", 2, 105, 65, 15, 20))),    # a tight box in the right place (IoU 0.4)
    stem("far", 2): ([("orange", ORANGE_BOX)], record_for(aiobj("OrangeBarrel", 2, 100, 60, 25, 20))),    # the top two thirds (IoU 0.67, bottom 20 px high)
    stem("edge", 1): ([("orange", ORANGE_BOX)], "{not json"),                                             # an unreadable vendor file
    stem("core", 3): ([("orange", ORANGE_BOX)], record_for(ORANGE_ITEM)),                                 # a TEST frame: never read
}
TEST_STEM = stem("core", 3)
SPLITS = {"train": [s for s in FRAMES if s != TEST_STEM], "dev": [], "test": [TEST_STEM], "measured": []}
MEASURED = [stem("clutter", 1), stem("core", 1), stem("core", 2), stem("far", 1), stem("far", 2), stem("neg", 1)]


@pytest.fixture
def world(tmp_path):
    """(labels_dir, vendor_dir) holding FRAMES."""
    labels, vendor = tmp_path / "labels", tmp_path / "vendor"
    labels.mkdir(); vendor.mkdir()
    for s, (barrels, rec) in FRAMES.items():
        meta = {"version": 1, "stem": s, "negative": not barrels, "clean": True,
                "barrels": [{"id": i + 1, "color": c, "bbox": bb} for i, (c, bb) in enumerate(barrels)]}
        io.boxes_path(s, labels).write_text(json.dumps(meta))
        if rec is not None:
            io.vendor_path(s, vendor).write_text(rec if isinstance(rec, str) else json.dumps(rec))
    return labels, vendor


def selection():
    return rp.select_frames(list(FRAMES), SPLITS)


# ---------------------------------------------------------------- which frames the vendor was measured on

def test_coverage_sorts_frames_and_counts_what_is_ignored(world):
    labels, vendor = world
    cov = rp.vendor_coverage(selection(), SPLITS, vendor)
    assert cov.total == {SET: 9} and cov.measured == {SET: MEASURED} and cov.stems == set(MEASURED)
    assert cov.no_file == [stem("touch", 1)]
    assert cov.not_measured == [stem("occl", 1)]                    # available: false is "not measured", never "saw nothing"
    assert list(cov.unreadable) == [stem("edge", 1)]
    assert cov.other_objects == 4 and cov.no_box == 1               # ball + tag, ball + robot; the barrel without a box
    assert cov.barrels[stem("core", 2)] == [] and cov.barrels[stem("clutter", 1)] == []     # measured, and the vendor has no barrel box
    assert [b.bbox for b in cov.barrels[stem("core", 1)]] == [tuple(BLUE_BOX), tuple(ORANGE_BOX)]


def test_vendor_arm_refuses_test_frames_before_any_file_is_read(world, monkeypatch):
    labels, vendor = world

    def never(*a, **k):
        raise AssertionError("a file of a test frame was opened")
    monkeypatch.setattr(io, "load_vendor", never)
    monkeypatch.setattr(io, "load_boxes", never)
    slipped = rp.Selection({SET: [TEST_STEM]}, split="train")       # a test frame slipped into a train selection
    with pytest.raises(rp.TestFrameError):
        rp.vendor_coverage(slipped, SPLITS, vendor)
    with pytest.raises(rp.TestFrameError):
        rp.run_arm(rp.vendor_arm(), slipped, SPLITS, labels_dir=labels, vendor_dir=vendor)


# ---------------------------------------------------------------- scoring: the same rule, the same labels

def test_vendor_arm_scores_its_boxes_under_the_v2_rule(world):
    labels, vendor = world
    loose = {}
    res = rp.run_arm(rp.vendor_arm(), selection(), SPLITS, loose=loose, labels_dir=labels, vendor_dir=vendor)
    assert sorted(res) == MEASURED and all(r.rule == "v2" for r in res.values())      # left-out frames are not scored at all
    count = lambda s: (sum(res[s].tp.values()), sum(res[s].fn.values()), sum(res[s].fp.values()))  # noqa: E731
    assert count(stem("core", 1)) == (2, 0, 0)                      # right
    assert count(stem("core", 2)) == (0, 1, 0)                      # a miss
    assert count(stem("clutter", 1)) == (0, 1, 0)                   # only a ball and a robot: a miss, no false box
    assert count(stem("neg", 1)) == (0, 0, 1) and res[stem("neg", 1)].negative        # a false box on an empty table
    assert count(stem("far", 1)) == (0, 1, 1) and count(stem("far", 2)) == (0, 1, 1)  # the strict rule refuses both
    assert loose[stem("far", 1)] == {"found_iou": 0, "false_iou": 1, "found_center": 1, "false_center": 0}    # tight box, right place
    assert loose[stem("far", 2)] == {"found_iou": 1, "false_iou": 0, "found_center": 1, "false_center": 0}    # overlap fine, bottom off
    assert loose[stem("neg", 1)] == {"found_iou": 0, "false_iou": 1, "found_center": 0, "false_center": 1}    # false under every count
    cell = rp.summarize([res[s] for s in MEASURED], [loose[s] for s in MEASURED])
    assert (cell.frames, cell.barrels, cell.found, cell.missed, cell.false) == (6, 6, 2, 4, 3)
    assert cell.neg_false == 1 and cell.disqualified                # the box on the clean empty frame disqualifies the vendor too
    assert cell.loose == {"found_iou": 3, "false_iou": 2, "found_center": 4, "false_center": 1}


def test_loose_counts():
    gt = [Barrel(O, (200, 120, 250, 180)), Barrel(B, (300, 120, 350, 180))]
    same = rp.loose_counts(gt, gt)
    assert same == {"found_iou": 2, "false_iou": 0, "found_center": 2, "false_center": 0}
    assert rp.loose_counts([], gt) == {"found_iou": 0, "false_iou": 0, "found_center": 0, "false_center": 0}
    wrong_color = rp.loose_counts([Barrel(B, (200, 120, 250, 180))], gt[:1])
    assert wrong_color == {"found_iou": 0, "false_iou": 1, "found_center": 0, "false_center": 1}
    # the center may be off by half the true width (25 px here), not more
    assert rp.loose_counts([Barrel(O, (225, 120, 275, 180))], gt[:1])["found_center"] == 1
    assert rp.loose_counts([Barrel(O, (226, 120, 276, 180))], gt[:1])["found_center"] == 0
    # two boxes on one barrel: one finds it, the other is false
    two = rp.loose_counts([Barrel(O, (200, 120, 250, 180)), Barrel(O, (204, 120, 254, 180))], gt[:1])
    assert two == {"found_iou": 1, "false_iou": 1, "found_center": 1, "false_center": 1}


# ---------------------------------------------------------------- in the one table

def test_ours_next_to_the_vendor_on_the_same_frames(world):
    labels, vendor = world
    cam = None
    from barrels import detect_types as dtp, geometry as geo
    cam = geo.AIM_4A8B6118_BOXFIT
    vloose, oloose = {}, {}
    vres = rp.run_arm(rp.vendor_arm(), selection(), SPLITS, loose=vloose, labels_dir=labels, vendor_dir=vendor)
    # "ours" = a detector that returns exactly the labels, scored through the same function on the same frames
    ours = {s: rp.score_boxes(s, dtp.barrels_from_boxes(io.load_boxes(s, labels)), cam, oloose, labels) for s in MEASURED}
    rows = rp.build_rows({SET: MEASURED}, ours, vres, oloose, vloose)
    assert [(r.scene, r.kind) for r in rows] == [("clutter", "scene"), ("core", "scene"), ("far", "scene"), ("neg", "scene"), ("", "subtotal")]
    sub = rows[-1]
    assert (sub.cand.found, sub.base.found, sub.delta["found"], sub.delta["false"]) == (6, 2, 4, -3)     # ours minus vendor
    assert sub.cand.loose["found_center"] == 6 and sub.base.loose["found_center"] == 4
    neg = rows[3]
    assert (neg.cand.false, neg.base.false, neg.base.neg_false) == (0, 1, 1)


def test_make_report_keeps_only_frames_with_a_vendor_file_and_says_so(world, tmp_path):
    labels, vendor = world
    rep = rp.make_report(rp.vendor_arm("candidate"), rp.vendor_arm("baseline"), labels_dir=labels, splits=SPLITS, vendor_dir=vendor)
    assert rep.loose and rep.selection.sets == {SET: MEASURED} and TEST_STEM not in rep.selection.stems
    sub = rep.subtotal(SET)
    assert (sub.cand.frames, sub.cand.barrels, sub.cand.found, sub.cand.missed, sub.cand.false) == (6, 6, 2, 4, 3)
    text = rp.format_text(rep)
    assert "VENDOR COMPARISON" in text and f"{SET} 6 of 9" in text and "(6 of 9 frames)" in text
    assert "1 with no vendor file" in text and "1 not measured" in text and "could not be read" in text
    assert "ignored: 4" in text and "ignored: 1" in text and "Caveat" in text
    assert "DQ:cb" in text                                                  # a box on a clean empty frame disqualifies
    lines = text.split("\n")
    at = next(i for i, x in enumerate(lines) if x.startswith("LOOSER COUNTS"))
    row = next(x for x in lines[at:] if x.startswith(f"{SET} all"))
    assert [c.split() for c in row.split("|")[1:]] == [["2/2"], ["3/3", "2/2"], ["4/4", "1/1"]]
    out = rp.write_all(rep, tmp_path / "r", title="t")
    d = json.loads((out / "report.json").read_text())
    assert d["candidate"] == {"name": "candidate", "kind": "vendor", "source": "data/vendor/<stem>_vendor.json"}
    assert d["vendor"]["frames_with_vendor"] == {SET: 6} and d["vendor"]["frames_selected"] == {SET: 9}
    assert d["vendor"]["not_measured"] == [stem("occl", 1)] and d["vendor"]["other_objects_ignored"] == 4
    assert d["rows"][-1]["candidate"]["loose"] == {"found_iou": 3, "false_iou": 2, "found_center": 4, "false_center": 1}
    rows = list(csv.DictReader((out / "report.csv").open()))
    assert (rows[-1]["cand_found"], rows[-1]["cand_found_iou"], rows[-1]["base_found_center"], rows[-1]["cand_false_center"]) == ("2", "3", "4", "1")
    md = (out / "report.md").read_text()
    assert "## Looser counts" in md and f"| **{SET} all** | **6** | **2 / 2** | **3 / 3** | **2 / 2** | **4 / 4** | **1 / 1** |" in md


def test_no_vendor_file_at_all_gives_an_empty_report_not_zeros(world, tmp_path):
    labels, _ = world
    empty = tmp_path / "no_vendor_files"
    empty.mkdir()
    rep = rp.make_report(rp.vendor_arm("candidate"), rp.vendor_arm("baseline"), labels_dir=labels, splits=SPLITS, vendor_dir=empty)
    assert rep.rows == [] and rep.vendor.total == {SET: 9} and len(rep.vendor.no_file) == 9
    assert f"{SET} 0 of 9" in rp.vendor_lines(rep)[0]


def test_reports_without_the_vendor_are_written_exactly_as_before():
    from test_report import make_rep
    rep = make_rep()
    assert rep.vendor is None and not rep.loose
    text = rp.format_text(rep)
    assert "LOOSER" not in text and "VENDOR" not in text
    d = rp.to_json(rep)
    assert "vendor" not in d and "loose" not in d and all("loose" not in r["candidate"] and "loose" not in r["baseline"] for r in d["rows"])
    assert "kind" not in d["candidate"]
    assert "Looser" not in rp.format_markdown(rep)
    assert "loose" not in rp.Cell().to_dict()


# ---------------------------------------------------------------- the command

def test_command_vendor_options(monkeypatch, capsys):
    tool = load_tool("report")
    seen = {}

    def fake(cand, base, **kw):
        seen.update(cand=cand, base=base, kw=kw)
        return rp.Report([], cand, base, rp.Selection({}), vendor=rp.VendorCoverage(measured={SET: []}, total={SET: 9}, no_file=["x"] * 9))
    monkeypatch.setattr(tool.rp, "make_report", fake)
    assert tool.main(["--vendor"]) == 1                             # nothing to compare yet: said in words, not as a table of zeros
    assert seen["base"].is_vendor and not seen["cand"].is_vendor and seen["cand"].model_path == tool.wb.DEFAULT_MODEL
    out = capsys.readouterr().out
    assert "no frame to compare" in out and f"{SET} 0 of 9" in out
    assert tool.main(["--cand-model", "vendor", "--base-model", "default"]) == 1
    assert seen["cand"].is_vendor and not seen["base"].is_vendor
    with pytest.raises(SystemExit):
        tool.main(["--base-model", "vendor", "--base-det", "body_width=1.0"])     # the vendor has no DetConfig
