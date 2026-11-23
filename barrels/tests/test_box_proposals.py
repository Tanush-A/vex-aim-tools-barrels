"""Claude's box proposals (docs/DATA.md "Box proposals"): the proposal file, box_tool.py opening and saving it,
box_look.py, the test-frame refusals, and that nothing that scores reads a proposal."""
import importlib.util
import json
import re
from pathlib import Path

import cv2
import numpy as np
import pytest

from barrels import geometry as geo, io, report as rp, splits as sp

ROOT = Path(__file__).resolve().parents[1]


def _tool(name):
    spec = importlib.util.spec_from_file_location(f"{name}_tool", ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


box_tool, box_look, eval_boxes = _tool("box_tool"), _tool("box_look"), _tool("eval_boxes")

A, B, T, NEW = "4A8B_sun_white_core_01", "4A8B_sun_white_occl_01", "4A8B_sun_white_touch_01", "4A8B_sun_white_edge_01"
SPLITS = {"train": [A, B], "dev": [], "test": [T], "measured": []}
DRAFT = {"clean": False, "note": "a blue cup at the left",
         "barrels": [{"color": "blue", "bbox": [300.4, 120, 360, 200], "flags": ["occluded"], "note": "behind the orange one"},
                     {"color": "orange", "bbox": [100, 150, 180, 260], "flags": [], "note": ""},
                     {"color": "orange", "bbox": [600, 300, 700, 480], "flags": [], "note": "cut by the right edge"}]}


@pytest.fixture
def dirs(tmp_path):
    raw, labels = tmp_path / "raw", tmp_path / "labels"
    raw.mkdir(); labels.mkdir()
    img = np.full((480, 640, 3), 128, np.uint8)
    for stem in (A, B, T):
        cv2.imwrite(str(raw / f"{stem}.png"), img)
    sfile = tmp_path / "splits.json"
    sfile.write_text(json.dumps(SPLITS))
    return raw, labels, sfile


# ---------------------------------------------------------------- the proposal file

def test_normalize_sorts_clips_flags_and_marks_it_claude():
    p = io.normalize_proposal(DRAFT, A)
    assert p["proposed_by"] == "claude" and "reviewed" not in p and p["stem"] == A and not p["negative"] and not p["clean"]
    assert [b["bbox"] for b in p["barrels"]] == [[100, 150, 180, 260], [300, 120, 360, 200], [600, 300, 640, 480]]
    assert [b["id"] for b in p["barrels"]] == [1, 2, 3]
    assert p["barrels"][2]["flags"] == ["truncated"] and p["barrels"][1]["flags"] == ["occluded"]
    assert p["barrels"][1]["note"] == "behind the orange one" and p["note"] == "a blue cup at the left"


def test_proposal_roundtrip_and_refusals(tmp_path):
    path = io.save_proposal(A, DRAFT, tmp_path)
    assert path.name == f"{A}_boxes_proposed.json"
    assert io.load_proposal(A, tmp_path)["barrels"] == io.normalize_proposal(DRAFT, A)["barrels"]
    neg = io.normalize_proposal({"barrels": []}, A)
    assert neg["negative"] and neg["barrels"] == []
    good = io.normalize_proposal(DRAFT, A)
    with pytest.raises(ValueError, match="reviewed"):
        io.validate_proposal(good | {"reviewed": True})
    with pytest.raises(ValueError, match="proposed_by"):
        io.validate_proposal({k: v for k, v in good.items() if k != "proposed_by"})
    with pytest.raises(ValueError, match="flags"):
        io.normalize_proposal({"barrels": [{"color": "orange", "bbox": [1, 1, 50, 50], "flags": ["hidden"]}]}, A)
    with pytest.raises(ValueError, match="color"):
        io.normalize_proposal({"barrels": [{"color": "red", "bbox": [1, 1, 50, 50]}]}, A)
    (tmp_path / f"{B}_boxes_proposed.json").write_text(json.dumps(good))
    with pytest.raises(ValueError, match="holds the proposal"):
        io.load_proposal(B, tmp_path)


# ---------------------------------------------------------------- nothing that scores reads a proposal

def test_eval_and_report_ignore_proposals(tmp_path):
    io.save_proposal(A, DRAFT, tmp_path)
    assert rp.labeled_stems(tmp_path) == []                                  # the report's label list
    assert eval_boxes.load_gt(A, tmp_path, geo.NOMINAL, boxes=True) is None  # the eval's ground truth
    with pytest.raises(FileNotFoundError):
        io.load_boxes(A, tmp_path)
    io.save_boxes(A, {"barrels": [], "reviewed": True}, tmp_path)
    assert rp.labeled_stems(tmp_path) == [A] and io.load_boxes(A, tmp_path)["barrels"] == []


def test_side_suffixes_list_the_proposals(tmp_path):
    assert {"_boxes_proposed", "_hs_proposed"} <= set(io.SIDE_SUFFIXES)
    for name in (f"{A}.png", f"{A}_boxes_proposed.png", f"{A}_hs_proposed.png"):
        cv2.imwrite(str(tmp_path / name), np.zeros((4, 4, 3), np.uint8))
    assert [p.name for p in io.list_images(tmp_path)] == [f"{A}.png"]


def test_only_the_proposal_tools_name_the_proposal_files():
    """A static guard: the eval, report, splits, experiments and analysis code never mention the proposal files."""
    allowed = {"src/barrels/io.py", "tools/box_tool.py", "tools/box_look.py"}
    hits = []
    for folder in ("src", "tools", "experiments", "live"):
        for p in (ROOT / folder).rglob("*.py"):
            rel = p.relative_to(ROOT).as_posix()
            if rel not in allowed and re.search(r"_proposed|proposal_path|load_proposal", p.read_text(errors="ignore")):
                hits.append(rel)
    assert hits == []


# ---------------------------------------------------------------- which frames Claude may look at

def test_look_refusal():
    assert sp.look_refusal(A, SPLITS) is None
    assert "test frame" in sp.look_refusal(T, SPLITS)
    assert "no split yet" in sp.look_refusal(NEW, SPLITS)
    assert sp.look_refusal("4A8B_lampmid6_wood_calib_03", SPLITS) is None      # geometry-only, never split
    assert sp.look_refusal("DAVE_office_desk_snap_01", SPLITS) is None          # Dave's: an outside check
    assert "dev" in sp.look_refusal(A, {"train": [], "dev": [A], "test": [], "measured": []})


def test_box_look_refuses_a_test_frame_before_reading_it(dirs, tmp_path, capsys):
    raw, labels, sfile = dirs
    (raw / f"{T}.png").unlink()                       # if the tool tried to read it, it would say "no image"
    out = tmp_path / "look.png"
    rc = box_look.main([T, "--out", str(out), "--raw", str(raw), "--labels", str(labels), "--splits", str(sfile)])
    assert rc == 2 and "REFUSED" in capsys.readouterr().out and not out.exists()
    rc = box_look.main([NEW, "--out", str(out), "--raw", str(raw), "--labels", str(labels), "--splits", str(sfile)])
    assert rc == 2 and not out.exists()


def test_box_look_draws_and_saves(dirs, tmp_path):
    raw, labels, sfile = dirs
    draft = tmp_path / "draft.json"
    draft.write_text(json.dumps(DRAFT))
    out = tmp_path / "look.png"
    common = ["--raw", str(raw), "--labels", str(labels), "--splits", str(sfile)]
    assert box_look.main([A, "--out", str(out), "--sizes", "--expect", "320,300", "--boxes", str(draft)] + common) == 0
    pic = cv2.imread(str(out))
    assert pic.shape[0] == 480 * 2 + box_look.MARGIN_TOP and pic.shape[1] > 640 * 2 + box_look.MARGIN_LEFT
    assert box_look.main([A, "--out", str(out), "--zoom", "100,100,260,220"] + common) == 0
    assert cv2.imread(str(out)).shape[:2] == (120 * 8 + box_look.MARGIN_TOP, 160 * 8 + box_look.MARGIN_LEFT)
    assert not io.proposal_path(A, labels).exists()
    assert box_look.main([A, "--boxes", str(draft), "--save"] + common) == 0
    saved = io.load_proposal(A, labels, raw_dir=raw)
    assert saved["image_sha1"] == io.file_sha1(raw / f"{A}.png") and len(saved["barrels"]) == 3
    draft.write_text(json.dumps({"barrels": [{"color": "green", "bbox": [1, 1, 9, 9]}]}))
    assert box_look.main([B, "--boxes", str(draft), "--save"] + common) == 1 and not io.proposal_path(B, labels).exists()


def test_render_grid_lines_sit_on_pixel_boundaries():
    img = np.zeros((480, 640, 3), np.uint8)
    pic = box_look.render(img, (100, 100, 200, 200), scale=4, grid=10)
    # frame column 150 starts at view x (150-100)*4 = 200 (+ margin); the grid line is drawn there, not one px off
    col = pic[box_look.MARGIN_TOP + 50, box_look.MARGIN_LEFT + 200]
    assert col.any() and not pic[box_look.MARGIN_TOP + 50, box_look.MARGIN_LEFT + 202].any()


# ---------------------------------------------------------------- box_tool.py with a proposal (no window)

def _session(dirs, stems=(A,)):
    raw, labels, _ = dirs
    return box_tool.Session([raw / f"{s}.png" for s in stems], labels, 1.0, geo.AIM_4A8B6118_BOXFIT, splits=SPLITS)


def test_box_tool_opens_a_proposal_dashed_and_does_not_save_it_untouched(dirs):
    raw, labels, _ = dirs
    io.save_proposal(A, DRAFT | {"image_sha1": io.file_sha1(raw / f"{A}.png")}, labels)
    s = _session(dirs)
    assert s.pending_proposal and s.from_proposal and len(s.barrels) == 3 and s.meta["source"] == "claude_proposal"
    assert not s.meta["reviewed"] and s.frame_note == "a blue cup at the left"
    s.selection = 2
    assert s.note_of(s.selected()) == "behind the orange one"
    assert s.render().shape == (480, 640, 3)
    assert not s.leave_ok() and not io.boxes_path(A, labels).exists()      # n / p / q do not take it


def test_box_tool_accept_records_source_reviewed_and_moved(dirs):
    raw, labels, _ = dirs
    io.save_proposal(A, DRAFT, labels)
    s = _session(dirs)
    s.accept()
    lab = io.load_boxes(A, labels, raw_dir=raw)
    assert lab["reviewed"] and lab["source"] == "claude_proposal" and not lab["clean"]
    assert [b["moved"] for b in lab["barrels"]] == [False, False, False]
    assert lab["barrels"][0]["proposed_bbox"] == [100, 150, 180, 260] and lab["barrels"][0]["proposed_color"] == "orange"
    assert lab["proposal"] | {"note": ""} == {"by": "claude", "proposed": 3, "kept": 3, "moved": 0, "deleted": 0, "added": 0, "note": ""}
    assert lab["barrels"][2]["flags"] == ["truncated"]


def test_box_tool_edit_delete_add(dirs):
    raw, labels, _ = dirs
    io.save_proposal(A, DRAFT, labels)
    s = _session(dirs)
    s.selection = 1                                            # move the bottom edge of the orange one by dragging it
    s.on_mouse(cv2.EVENT_LBUTTONDOWN, 140, 260, 0, None)
    assert not s.pending_proposal
    s.on_mouse(cv2.EVENT_MOUSEMOVE, 140, 266, 0, None); s.on_mouse(cv2.EVENT_LBUTTONUP, 140, 266, 0, None)
    s.selection = 3; s.delete_selected()
    s.add_box([400, 300, 450, 360])
    assert s.leave_ok()
    s.save()
    lab = io.load_boxes(A, labels)
    by = {tuple(b["bbox"]): b for b in lab["barrels"]}
    assert by[(100, 150, 180, 266)]["moved"] and by[(100, 150, 180, 266)]["proposed_bbox"] == [100, 150, 180, 260]
    assert not by[(300, 120, 360, 200)]["moved"]
    assert by[(400, 300, 450, 360)]["moved"] and "proposed_bbox" not in by[(400, 300, 450, 360)]
    assert {k: lab["proposal"][k] for k in ("kept", "moved", "deleted", "added")} == {"kept": 1, "moved": 1, "deleted": 1, "added": 1}
    assert lab["source"] == "claude_proposal"
    s2 = _session(dirs)                                        # reopened: the saved label, not the proposal
    assert not s2.pending_proposal and s2.meta["reviewed"] and len(s2.barrels) == 3


def test_box_tool_reject_all_and_redraw_is_manual(dirs):
    raw, labels, _ = dirs
    io.save_proposal(A, DRAFT, labels)
    s = _session(dirs)
    s.reject_proposal()
    assert s.barrels == [] and not s.pending_proposal
    s.pop()
    assert len(s.barrels) == 3                                # undo brings them back
    s.reject_proposal(); s.add_box([10, 200, 60, 260]); s.save()
    lab = io.load_boxes(A, labels)
    assert lab["source"] == "manual" and lab["proposal"]["deleted"] == 3 and lab["barrels"][0]["moved"]


def test_box_tool_ignores_a_proposal_on_a_test_frame(dirs):
    raw, labels, _ = dirs
    io.save_proposal(T, DRAFT, labels)
    s = _session(dirs, (T,))
    assert not s.from_proposal and s.barrels == [] and not s.pending_proposal


def test_box_tool_without_a_proposal_is_unchanged(dirs):
    raw, labels, _ = dirs
    s = _session(dirs, (B,))
    assert not s.from_proposal and s.leave_ok()
    s.add_box([10, 10, 60, 90]); s.save()
    lab = io.load_boxes(B, labels)
    assert lab["source"] == "manual" and "proposal" not in lab and "moved" not in lab["barrels"][0]
