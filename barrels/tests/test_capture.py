import json

import numpy as np

from barrels import capture, io


def rgb(seed):
    return np.random.default_rng(seed).integers(0, 256, (480, 640, 3), dtype=np.uint8)


def test_save_names_like_the_camera_viewer_and_never_overwrites(tmp_path):
    cap = capture.FrameCapture(folder=tmp_path / "snapshots")
    a = rgb(1)
    p0, p1 = cap.save(a), cap.save(rgb(2))
    assert p0.name == "robot_snap0.png" and p1.name == "robot_snap1.png"
    assert (io.load_image(p0)[..., ::-1] == a).all()            # written in BGR, so it loads back as the RGB we gave
    (tmp_path / "snapshots" / "robot_snap7.png").write_bytes(p0.read_bytes())
    assert cap.save(rgb(3)).name == "robot_snap8.png"           # continues past whatever is there


def test_recording_keeps_at_most_max_fps_for_the_given_seconds(tmp_path):
    t = [0.0]
    cap = capture.FrameCapture(folder=tmp_path / "snapshots", rec_seconds=1.0, max_fps=10.0, clock=lambda: t[0])
    assert not cap.recording and cap.on_frame(rgb(0)) is None and cap.pop_report() is None
    d = cap.start_recording(stamp="x")
    assert d == tmp_path / "snapshots" / "rec_x" and cap.recording
    written = []
    for k in range(30):                                          # a 20 fps stream for 1.45 s
        t[0] = k * 0.05
        p = cap.on_frame(rgb(k), frame_count=100 + k)
        if p:
            written.append(p)
    assert not cap.recording
    assert [p.name for p in written] == [f"frame_{i:03d}.png" for i in range(10)]   # 10 fps for 1 s
    meta = json.loads((d / "frames.json").read_text())
    assert meta["seconds"] == 1.0 and [f["file"] for f in meta["frames"]] == [p.name for p in written]
    assert [f["frame_count"] for f in meta["frames"]] == list(range(100, 120, 2))
    assert meta["frames"][3]["t"] == 0.3
    assert (io.load_image(written[2])[..., ::-1] == rgb(4)).all()
    line = cap.pop_report()
    assert line.startswith("recorded 10 frames in 1 s") and cap.pop_report() is None
    assert cap.on_frame(rgb(99)) is None                         # stopped: nothing more is written


def test_stop_recording_early_keeps_what_was_recorded(tmp_path):
    t = [5.0]
    cap = capture.FrameCapture(folder=tmp_path / "snapshots", clock=lambda: t[0])
    d = cap.start_recording(seconds=30, stamp="y")
    for k in range(3):
        t[0] = 5.0 + k * 0.5
        cap.on_frame(rgb(k))
    js = cap.stop_recording()
    assert js == d / "frames.json" and not cap.recording and cap.stop_recording() is None
    assert len(json.loads(js.read_text())["frames"]) == 3 and "3 frames" in cap.pop_report()
    d2 = cap.start_recording(stamp="z")                          # a fresh recording starts clean
    assert d2 != d and cap.recording and cap.on_frame(rgb(7)).name == "frame_000.png"
