"""The vendor detector's answer saved with a frame (TODO B, 2026-11-18): reading it from a (fake) robot, the
coordinate conversion, the files `tm save` writes, the importer carrying them along, the loader."""
import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from barrels import capture, io
from barrels.detect_types import Barrel

BARRELS_DIR = Path(__file__).resolve().parents[1]

CLASSNAMES = {"count": 4, "items": [{"index": 0, "name": "SportsBall"}, {"index": 1, "name": "BlueBarrel"},
                                    {"index": 2, "name": "OrangeBarrel"}, {"index": 3, "name": "Robot"}]}
# the placeholder the vex library holds while no status has arrived (vex/aim.py, WSStatusThread._empty_status)
EMPTY_STATUS = {"robot": {"battery": 0}, "aivision": {"classnames": CLASSNAMES, "objects": {"count": 0, "items": [
    {"type": 0, "id": 0, "type_str": "0", "originx": 0, "originy": 0, "width": 0, "height": 0, "score": 0, "name": "0"}]}}}


def aiobj(name, cid, x, y, w, h, score=90):
    return {"type": 4, "id": cid, "type_str": "aiobj", "originx": x, "originy": y, "width": w, "height": h, "score": score, "name": name}


ORANGE_ITEM = aiobj("OrangeBarrel", 2, 100, 60, 25, 30)
BLUE_ITEM = aiobj("BlueBarrel", 1, 10, 20, 30, 40, score=75)
BALL_ITEM = aiobj("SportsBall", 0, 200, 100, 20, 20)
TAG_ITEM = {"type": 8, "id": 3, "type_str": "tag", "originx": 150, "originy": 50, "width": 20, "height": 20,
            "x0": 150, "y0": 50, "x1": 170, "y1": 50, "x2": 170, "y2": 70, "x3": 150, "y3": 70}


def status(*items, count=None):
    return {"robot": {"battery": 80}, "aivision": {"classnames": CLASSNAMES,
                                                    "objects": {"count": len(items) if count is None else count, "items": list(items)}}}


class FakeStatusThread:
    def __init__(self, current):
        self._empty_status = EMPTY_STATUS
        self.current_status = current


class FakeVex:
    """Stands in for vex.Robot: the status thread and the ``status`` property that reads it."""
    def __init__(self, current):
        self._ws_status_thread = FakeStatusThread(current)

    @property
    def status(self):
        return self._ws_status_thread.current_status


class FakeRobot:
    """Stands in for aim_fsm's Robot: ``robot0`` is the vex robot; ``status`` is only the 'robot' part (no aivision)."""
    def __init__(self, current):
        self.robot0 = FakeVex(current)
        self.status = current.get("robot", {})
        self.frame_count = 41


def rgb(seed=0):
    return np.random.default_rng(seed).integers(0, 256, (480, 640, 3), dtype=np.uint8)


def record_for(*items, **kw):
    return capture.vendor_record(capture.grab_vendor(FakeRobot(status(*items)), clock=lambda: 123.5), **kw)


# ---------------------------------------------------------------- the coordinate conversion

def test_vendor_bbox_doubles_corner_and_size_into_half_open_ints():
    assert capture.vendor_bbox({"originx": 10, "originy": 20, "width": 30, "height": 40}) == [20, 40, 80, 120]
    assert capture.vendor_bbox({"originx": 0, "originy": 0, "width": 320, "height": 240}) == [0, 0, 640, 480]    # the whole frame
    bb = capture.vendor_bbox({"originx": 10.0, "originy": 20.0, "width": 30.0, "height": 40.0})
    assert bb == [20, 40, 80, 120] and all(type(v) is int for v in bb)


def test_vendor_bbox_agrees_with_the_projects_aivision_conversion():
    b = Barrel.from_aivision_spec(ORANGE_ITEM)                  # detect_types: the same x2 the world map uses
    assert tuple(capture.vendor_bbox(ORANGE_ITEM)) == b.bbox == (200, 120, 250, 180)


def test_vendor_bbox_clips_to_the_frame_and_drops_what_is_outside_or_malformed():
    assert capture.vendor_bbox({"originx": 300, "originy": 230, "width": 40, "height": 40}) == [600, 460, 640, 480]
    assert capture.vendor_bbox({"originx": -5, "originy": -5, "width": 10, "height": 10}) == [0, 0, 10, 10]
    assert capture.vendor_bbox({"originx": 330, "originy": 10, "width": 10, "height": 10}) is None     # right of the frame
    assert capture.vendor_bbox({"originx": 10, "originy": 10, "width": 0, "height": 10}) is None       # no width
    assert capture.vendor_bbox({"originx": 10, "originy": 10, "width": 5}) is None                     # a field missing
    assert capture.vendor_bbox({"originx": "x", "originy": 10, "width": 5, "height": 5}) is None


def test_vendor_bbox_scales_by_image_over_source():
    item = {"originx": 10, "originy": 20, "width": 30, "height": 40}
    assert capture.vendor_bbox(item, image_size=(320, 240)) == [10, 20, 40, 60]                        # a frame in the vendor's own size
    assert capture.vendor_bbox(item, image_size=(1280, 960)) == [40, 80, 160, 240]


# ---------------------------------------------------------------- reading from the robot

def test_record_from_a_fake_robot_has_every_object_and_the_raw_fields_untouched():
    rec = record_for(ORANGE_ITEM, BLUE_ITEM, BALL_ITEM, TAG_ITEM, frame_count=41)
    assert rec["version"] == 1 and rec["available"] is True and rec["error"] == ""
    assert rec["time"] == 123.5 and rec["frame_count"] == 41 and rec["read_at"] == "frame"
    assert rec["image_size"] == [640, 480] and rec["source_size"] == [320, 240]
    assert rec["classnames"] == ["SportsBall", "BlueBarrel", "OrangeBarrel", "Robot"]
    assert [(o["name"], o["class_id"], o["bbox"]) for o in rec["objects"]] == [
        ("OrangeBarrel", 2, [200, 120, 250, 180]), ("BlueBarrel", 1, [20, 40, 80, 120]),
        ("SportsBall", 0, [400, 200, 440, 240]), ("", 3, [300, 100, 340, 140])]
    assert [o["raw"] for o in rec["objects"]] == [ORANGE_ITEM, BLUE_ITEM, BALL_ITEM, TAG_ITEM]
    assert json.loads(json.dumps(rec)) == rec                   # plain JSON
    io.validate_vendor(rec)


def test_grab_is_a_reference_to_that_moments_status_and_the_record_is_a_copy():
    robot = FakeRobot(status(ORANGE_ITEM))
    grab = capture.grab_vendor(robot)
    robot.robot0._ws_status_thread.current_status = status(BLUE_ITEM, BALL_ITEM)     # the next status packet arrives
    rec = capture.vendor_record(grab)
    assert [o["name"] for o in rec["objects"]] == ["OrangeBarrel"]                  # still what was there with the frame
    rec["objects"][0]["raw"]["originx"] = -1
    assert ORANGE_ITEM["originx"] == 100                                            # the robot's own dict is not touched


def test_grab_works_on_a_bare_vex_robot_too():
    rec = capture.vendor_record(capture.grab_vendor(FakeVex(status(BLUE_ITEM))))
    assert rec["available"] and [o["name"] for o in rec["objects"]] == ["BlueBarrel"]


def test_count_limits_the_items_and_nothing_seen_is_available_with_no_objects():
    rec = capture.vendor_record(capture.grab_vendor(FakeRobot(copy.deepcopy(EMPTY_STATUS))))    # count 0 + one dummy item
    assert rec["available"] is True and rec["objects"] == []
    rec = capture.vendor_record(capture.grab_vendor(FakeRobot(status(ORANGE_ITEM, BLUE_ITEM, count=1))))
    assert [o["name"] for o in rec["objects"]] == ["OrangeBarrel"]


def test_name_falls_back_to_the_class_list_for_a_model_object():
    item = {k: v for k, v in BLUE_ITEM.items() if k != "name"}
    assert record_for(item)["objects"][0]["name"] == "BlueBarrel"


def test_an_object_without_a_usable_box_is_kept_with_a_null_bbox():
    rec = record_for(aiobj("OrangeBarrel", 2, 50, 50, 0, 0), ORANGE_ITEM)
    assert [o["bbox"] for o in rec["objects"]] == [None, [200, 120, 250, 180]]
    io.validate_vendor(rec)


@pytest.mark.parametrize("robot, text", [
    (FakeRobot(EMPTY_STATUS), "no status from the robot"),              # the library's placeholder itself: nothing received
    (object(), "AttributeError"),                                       # not a robot at all
    (FakeRobot({"robot": {}}), "KeyError"),                             # a status without the aivision part
    (FakeRobot({"aivision": {"objects": None}}), "TypeError"),
    (None, "AttributeError"),
])
def test_unreadable_vendor_data_gives_available_false_with_the_reason_and_never_raises(robot, text):
    grab = capture.grab_vendor(robot)
    assert grab["aivision"] is None and text in grab["error"]
    rec = capture.vendor_record(grab, frame_count=7)
    assert rec["available"] is False and text in rec["error"] and rec["objects"] == [] and rec["frame_count"] == 7
    io.validate_vendor(rec)
    assert "NOT available" in capture.vendor_summary(rec)


def test_record_never_raises_on_garbage():
    for grab in (None, {}, {"aivision": 5}, {"aivision": {"objects": {"items": 3}}}, {"aivision": {"objects": {"items": [1, "a"]}}}):
        rec = capture.vendor_record(grab)
        assert rec["version"] == 1 and isinstance(rec["available"], bool)
        io.validate_vendor(rec)
    assert capture.vendor_record({"aivision": {"objects": {}}}, image_size=None)["available"] is False


def test_summary_line():
    assert capture.vendor_summary(record_for(ORANGE_ITEM, BLUE_ITEM)) == "vendor: 2 objects (OrangeBarrel, BlueBarrel)"
    assert capture.vendor_summary(record_for()) == "vendor: 0 objects"


# ---------------------------------------------------------------- what `tm save` writes

def test_save_writes_the_raw_frame_untouched_plus_the_vendor_json_and_a_preview(tmp_path):
    cap = capture.FrameCapture(folder=tmp_path / "snapshots")
    image, rec = rgb(1), record_for(ORANGE_ITEM, BLUE_ITEM)
    before = image.copy()
    p = cap.save(image, vendor=rec)
    assert p.name == "robot_snap0.png" and cap.vendor_error == ""
    assert sorted(q.name for q in p.parent.iterdir()) == ["robot_snap0.png", "robot_snap0_vendor.json", "robot_snap0_vendor.png"]
    assert (image == before).all() and (io.load_image(p)[..., ::-1] == before).all()        # the frame is the frame
    assert json.loads(capture.vendor_file(p).read_text()) == rec
    preview = io.load_image(capture.vendor_file(p, ".png"))[..., ::-1]
    assert (preview[120, 200:250] == capture.VENDOR_COLORS_RGB["OrangeBarrel"]).all()       # top edge of the orange box
    assert (preview[119, 40:79] == capture.VENDOR_COLORS_RGB["BlueBarrel"]).all()           # bottom edge of the blue box (row y1 - 1)
    assert (preview[300:] == before[300:]).all()                                            # nothing drawn elsewhere
    assert cap.save(rgb(2), vendor=rec).name == "robot_snap1.png"
    assert cap.save(rgb(3)).name == "robot_snap2.png" and not capture.vendor_file(p.with_name("robot_snap2.png")).exists()
    assert cap.save(rgb(4), vendor=rec, preview=False).name == "robot_snap3.png"
    assert not (p.parent / "robot_snap3_vendor.png").exists() and (p.parent / "robot_snap3_vendor.json").exists()


def test_save_still_saves_the_frame_when_the_vendor_data_is_missing_or_cannot_be_written(tmp_path, monkeypatch):
    cap = capture.FrameCapture(folder=tmp_path / "snapshots")
    rec = capture.vendor_record(capture.grab_vendor(object()))
    p = cap.save(rgb(1), vendor=rec)
    assert p.exists() and json.loads(capture.vendor_file(p).read_text())["available"] is False

    def boom(*a, **k):
        raise OSError("disk full")
    monkeypatch.setattr(capture, "write_vendor", boom)
    image = rgb(2)
    p2 = cap.save(image, vendor=record_for(ORANGE_ITEM))
    assert p2.name == "robot_snap1.png" and (io.load_image(p2)[..., ::-1] == image).all()
    assert "disk full" in cap.vendor_error and not capture.vendor_file(p2).exists()


def test_draw_vendor_returns_a_copy():
    image = rgb(5)
    before = image.copy()
    out = capture.draw_vendor(image, record_for(ORANGE_ITEM, aiobj("OrangeBarrel", 2, 5, 5, 0, 0)))
    assert (image == before).all() and out is not image and (out != before).any()
    assert (capture.draw_vendor(image, capture.vendor_record(None)) != before).any()         # "not available" is written on it


def test_snap_numbering_skips_past_leftover_vendor_files(tmp_path):
    (tmp_path / "robot_snap4_vendor.json").write_text("{}")
    (tmp_path / "robot_snap6_vendor.png").write_bytes(b"")
    (tmp_path / "robot_asnap9.png").write_bytes(b"")             # the camera viewer's annotated snapshot: another series
    assert capture.next_snap_index(tmp_path) == 7


def test_recording_keeps_the_vendor_answer_per_frame(tmp_path):
    t = [0.0]
    cap = capture.FrameCapture(folder=tmp_path / "snapshots", rec_seconds=1.0, clock=lambda: t[0])
    d = cap.start_recording(stamp="v")
    robot = FakeRobot(status(ORANGE_ITEM))
    cap.on_frame(rgb(0), frame_count=1, vendor=capture.grab_vendor(robot))
    t[0] = 0.5
    cap.on_frame(rgb(1), frame_count=2)                          # without: the entry simply has no vendor key
    cap.stop_recording()
    frames = json.loads((d / "frames.json").read_text())["frames"]
    assert frames[0]["vendor"]["available"] and frames[0]["vendor"]["objects"][0]["bbox"] == [200, 120, 250, 180]
    assert frames[0]["vendor"]["frame_count"] == 1 and "vendor" not in frames[1]


# ---------------------------------------------------------------- io: path, loader, barrels

def test_vendor_path_and_side_files_are_never_images(tmp_path):
    assert io.vendor_path("4A8B_window_white_core_01") == io.VENDOR_DIR / "4A8B_window_white_core_01_vendor.json"
    assert io.vendor_path(tmp_path / "a_01.png", tmp_path).name == "a_01_vendor.json"
    for n in ("a_01.png", "a_01_vendor.png", "a_01_vendor.json", "robot_snap0_vendor.png"):
        (tmp_path / n).write_bytes(b"")
    assert [p.name for p in io.list_images(tmp_path)] == ["a_01.png"]


def test_load_vendor_round_trip_and_missing(tmp_path):
    rec = record_for(ORANGE_ITEM, BALL_ITEM)
    io.vendor_path("s_01", tmp_path).write_text(json.dumps(rec))
    assert io.load_vendor("s_01", tmp_path) == rec
    assert io.load_vendor(tmp_path / "s_01.png", tmp_path) == rec
    with pytest.raises(FileNotFoundError):
        io.load_vendor("s_02", tmp_path)


@pytest.mark.parametrize("change, text", [
    ({"version": 2}, "version"),
    ({"available": "yes"}, "available"),
    ({"image_size": [640]}, "image_size"),
    ({"objects": None}, "objects"),
    ({"objects": [{"name": "OrangeBarrel", "bbox": [10, 10, 10, 50]}]}, "empty or outside"),
    ({"objects": [{"name": "OrangeBarrel", "bbox": [600, 10, 660, 50]}]}, "empty or outside"),
    ({"objects": [{"name": "OrangeBarrel", "bbox": [1.5, 2, 30, 40]}]}, "four ints"),
    ({"objects": [{"bbox": None}]}, "name"),
    ({"available": False, "error": "x"}, "no objects"),
    ({"available": False, "objects": [], "error": ""}, "say why"),
])
def test_load_vendor_rejects_bad_content(tmp_path, change, text):
    io.vendor_path("s_01", tmp_path).write_text(json.dumps(record_for(ORANGE_ITEM) | change))
    with pytest.raises(ValueError, match=text):
        io.load_vendor("s_01", tmp_path)


def test_vendor_barrels_keeps_the_two_barrel_classes_and_counts_the_rest():
    rec = record_for(ORANGE_ITEM, BLUE_ITEM, BALL_ITEM, TAG_ITEM, aiobj("Robot", 3, 5, 5, 50, 50), aiobj("BlueBarrel", 1, 9, 9, 0, 0))
    barrels, counts = io.vendor_barrels(rec)
    assert [(b.color, b.bbox, b.source) for b in barrels] == [(io.BLUE, (20, 40, 80, 120), "aivision"),
                                                               (io.ORANGE, (200, 120, 250, 180), "aivision")]   # left to right
    assert all(isinstance(b, Barrel) for b in barrels) and counts == {"other": 3, "no_box": 1}
    assert io.vendor_barrels(record_for()) == ([], {"other": 0, "no_box": 0})                 # the vendor saw nothing


def test_vendor_barrels_refuses_a_record_that_was_not_measured():
    with pytest.raises(ValueError, match="not available"):
        io.vendor_barrels(capture.vendor_record(capture.grab_vendor(object())))


# ---------------------------------------------------------------- the importer carries the file along

def load_tool(name):
    spec = importlib.util.spec_from_file_location(f"tool_{name}", BARRELS_DIR / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def shoot(tmp_path):
    """Three snapshots as `tm save` leaves them: 0 and 2 with the vendor files, 1 (say, from the camera viewer) without."""
    cap = capture.FrameCapture(folder=tmp_path / "snapshots")
    recs = {0: record_for(ORANGE_ITEM), 2: record_for(BLUE_ITEM, BALL_ITEM)}
    for k in range(3):
        cap.save(rgb(k), vendor=recs.get(k))
    return tmp_path, recs


def run_import(tmp_path, *extra):
    args = ["--src", str(tmp_path / "snapshots"), "--dst", str(tmp_path / "data" / "raw"),
            "--light", "window", "--surface", "white", "--scenes", "neg,core,core", *extra]
    return load_tool("import_snaps").main(args)


def test_import_dry_run_shows_the_vendor_files_and_moves_nothing(shoot, capsys):
    tmp_path, _ = shoot
    before = sorted(p.name for p in (tmp_path / "snapshots").iterdir())
    assert run_import(tmp_path, "--dry-run") == 0
    out = capsys.readouterr().out
    assert "4A8B_window_white_neg_01_vendor.json" in out and "4A8B_window_white_core_02_vendor.json" in out
    assert "vendor files: 2 of 3; none for robot_snap1.png" in out and "(no vendor file)" in out and "dry run" in out
    assert sorted(p.name for p in (tmp_path / "snapshots").iterdir()) == before and not (tmp_path / "data").exists()


def test_import_moves_each_vendor_file_under_the_frames_new_stem(shoot, capsys):
    tmp_path, recs = shoot
    assert run_import(tmp_path) == 0
    raw, vendor = tmp_path / "data" / "raw", tmp_path / "data" / "vendor"
    assert sorted(p.name for p in raw.iterdir()) == ["4A8B_window_white_core_01.png", "4A8B_window_white_core_02.png",
                                                     "4A8B_window_white_neg_01.png"]
    assert [p.name for p in io.list_images(raw)] == sorted(p.name for p in raw.iterdir())      # only frames in data/raw
    assert sorted(p.name for p in vendor.iterdir()) == ["4A8B_window_white_core_02_vendor.json", "4A8B_window_white_neg_01_vendor.json"]
    assert io.load_vendor("4A8B_window_white_neg_01", vendor) == recs[0]                       # snapshot 0 was the neg
    assert io.load_vendor("4A8B_window_white_core_02", vendor) == recs[2]                      # snapshot 2 the second core
    assert (io.load_image(raw / "4A8B_window_white_core_02.png")[..., ::-1] == rgb(2)).all()
    with pytest.raises(FileNotFoundError):
        io.load_vendor("4A8B_window_white_core_01", vendor)                                    # snapshot 1 had none: not an error
    assert [p.name for p in (tmp_path / "snapshots").iterdir()] == ["vendor_previews"]      # the snapshot folder is empty again
    assert len(list((tmp_path / "snapshots" / "vendor_previews").glob("4A8B_window_white_*_vendor.png"))) == 2
    assert "2 vendor files" in capsys.readouterr().out


def test_import_refuses_to_overwrite_a_vendor_file_and_moves_nothing(shoot, capsys):
    tmp_path, _ = shoot
    existing = io.vendor_path("4A8B_window_white_neg_01", tmp_path / "data" / "vendor")
    existing.parent.mkdir(parents=True)
    existing.write_text("kept")
    assert run_import(tmp_path) == 1
    assert existing.read_text() == "kept" and (tmp_path / "snapshots" / "robot_snap0.png").exists()
    assert not (tmp_path / "data" / "raw").exists() and "exists" in capsys.readouterr().out


def test_import_vendor_dst_option(shoot):
    tmp_path, recs = shoot
    assert run_import(tmp_path, "--vendor-dst", str(tmp_path / "elsewhere")) == 0
    assert io.load_vendor("4A8B_window_white_neg_01", tmp_path / "elsewhere") == recs[0]


# ---------------------------------------------------------------- the live program (cannot run without a robot)

def test_the_live_base_compiles_and_saves_through_the_vendor_path():
    src = (BARRELS_DIR / "live" / "barrel_live.py").read_text()
    compile(src, "barrel_live.py", "exec")
    assert "capture.grab_vendor(self.robot)" in src and "cap.save(image, vendor=record)" in src
