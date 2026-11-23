"""The nightly runner (``experiments/run_all.py``): every step runs whatever the one before did, its exit code is
kept, a missing script is skipped, the gate's verdict and known failures are read right, and the data gaps are found
from file names and the split file alone (test frames counted, never named). Plus the small pure parts of the vendor
experiment (``experiments/2026-11-24_vendor/run.py``)."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

EXP = Path(__file__).resolve().parents[1] / "experiments"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ra():
    return load(EXP / "run_all.py", "run_all_under_test")


def py(code: str) -> list[str]:
    return [sys.executable, "-c", code]


def test_steps_continue_past_failures_and_keep_exit_codes(ra, tmp_path):
    steps = [ra.Step("one", py("print('a')"), cwd=tmp_path),
             ra.Step("two", py("import sys; print('b'); sys.exit(3)"), cwd=tmp_path),
             ra.Step("three", py("print('c')"), cwd=tmp_path)]
    res = ra.run_steps(steps, log_dir=tmp_path, echo=lambda *_: None)
    assert [r.status for r in res] == ["ok", "failed", "ok"]
    assert [r.code for r in res] == [0, 3, 0]
    assert "c" in res[2].output
    assert (tmp_path / "02_two.txt").read_text().splitlines()[1].startswith("# status failed, exit code 3")


def test_missing_script_is_skipped_not_failed(ra, tmp_path):
    r = ra.run_step(ra.Step("adaptive", py("print(1)"), cwd=tmp_path, requires=tmp_path / "nope.py"))
    assert r.status == "skipped" and r.code is None and not r.ran


def test_timeout_and_unstartable_command_are_recorded(ra, tmp_path):
    r = ra.run_step(ra.Step("slow", py("import time; time.sleep(5)"), cwd=tmp_path, timeout=0.5))
    assert r.status == "timeout" and r.code is None
    r = ra.run_step(ra.Step("bad", [str(tmp_path / "no_such_program")], cwd=tmp_path))
    assert r.status == "error" and r.code is None


def test_step_environment_is_passed(ra, tmp_path):
    r = ra.run_step(ra.Step("env", py("import os; print(os.environ['BARRELS_NO_REPORT'])"), cwd=tmp_path, env={"BARRELS_NO_REPORT": "1"}))
    assert r.output.strip() == "1"


def test_default_steps_order_and_test_env(ra):
    steps = ra.default_steps("python")
    assert [s.name for s in steps] == ["tests", "gate", "eval_table", "vendor", "adaptive"]
    assert steps[0].env == {"BARRELS_NO_REPORT": "1"}
    assert steps[1].cmd[-1] == "--gate" and steps[2].cmd[-2:] == ["--base-model", "default"]
    assert all("test" not in " ".join(s.cmd[2:]) or s.name == "tests" for s in steps)     # no --split test anywhere
    assert steps[4].requires == ra.ADAPTIVE_SCRIPT


def test_parse_pytest(ra):
    assert ra.parse_pytest("....\n250 passed, 2 skipped in 31.20s\n") == "250 passed, 2 skipped in 31.20s"
    assert ra.parse_pytest("F.\n===== 1 failed, 249 passed in 30.1s =====") == "1 failed, 249 passed in 30.1s"
    assert ra.parse_pytest("crash") == ""


GATE_FAIL = """Set totals, baseline -> this run:
  HOME                       found 28 -> 28 of 29; false boxes 0 -> 0; boxes on empty frames 0 -> 0  [protected]
  CAMPUS                     found 35 -> 35 of 35; false boxes 0 -> 0; boxes on empty frames 0 -> 0  [protected]

RESULT: FAIL. a new box on an empty frame in 1 row(s) (4A8B_window_abpwhite occlx). This change must not become the default as it is.
"""


def test_parse_gate_known_failure(ra):
    g = ra.parse_gate(GATE_FAIL)
    assert g["verdict"] == "FAIL"
    assert g["failing"] == ["4A8B_window_abpwhite occlx"]
    assert list(g["known"]) == ["4A8B_window_abpwhite occlx"] and g["unknown"] == []
    assert len(g["protected"]) == 2 and g["protected"][0].startswith("HOME found 28 -> 28 of 29")


def test_parse_gate_new_failure_and_pass(ra):
    g = ra.parse_gate("RESULT: FAIL. 2 protected row(s) got worse (HOME occl, CAMPUS core); a new box on an empty frame in 1 row(s) "
                      "(4A8B_window_abpwhite occlx). This change must not become the default as it is.")
    assert g["failing"] == ["HOME occl", "CAMPUS core", "4A8B_window_abpwhite occlx"]
    assert g["unknown"] == ["HOME occl", "CAMPUS core"]
    assert ra.parse_gate("RESULT: PASS. No scenario row of HOME, CAMPUS lost ...")["verdict"] == "PASS"
    assert ra.parse_gate("Traceback ...")["verdict"] == ""


def test_written_dir_and_summary_path(ra, tmp_path):
    (tmp_path / "summary.md").write_text("x")
    assert ra.written_dir(f"...\nwritten to {tmp_path}\n") == tmp_path
    assert ra.summary_path(f"written to {tmp_path}") == tmp_path / "summary.md"
    assert ra.summary_path("nothing here") is None


def make_data(tmp_path, frames, splits, boxed=(), hs=(), vendor=()):
    raw, lab, ven = tmp_path / "raw", tmp_path / "labels", tmp_path / "vendor"
    for d in (raw, lab, ven):
        d.mkdir()
    for s in frames:
        (raw / f"{s}.png").write_bytes(b"not an image")       # never opened: a real reader would fail on it
    for s in boxed:
        (lab / f"{s}_boxes.json").write_text("{}")
    for s in hs:
        (lab / f"{s}_hs.json").write_text("{}")
    for s in vendor:
        (ven / f"{s}_vendor.json").write_text("{}")
    return raw, lab, ven


def test_data_gaps(ra, tmp_path):
    c = "4A8B_window_white"
    fr = [f"{c}_{x}" for x in ("neg_01", "core_01", "occl_01", "occl_02", "clutter_01", "touch_01", "neg_02")]
    old = ["4A8B_window_light_core_01"]                     # an old set: no vendor file -> not a new condition
    splits = {"train": [f"{c}_core_01", f"{c}_occl_02", f"{c}_clutter_01", f"{c}_touch_01", f"{c}_neg_02"],
              "test": [f"{c}_neg_01", f"{c}_occl_01"], "dev": []}
    raw, lab, ven = make_data(tmp_path, fr + old + [f"{c}_calib_01", "4A8B_window_white_edge_01"], splits,
                              boxed=[f"{c}_core_01", f"{c}_occl_02", f"{c}_neg_02", f"{c}_neg_01"], hs=[f"{c}_core_01"],
                              vendor=fr[:-1])
    g = ra.data_gaps(raw, lab, ven, splits)
    assert list(g) == [c]
    x = g[c]
    assert x["frames"] == 8 and x["train"] == 5 and x["test"] == 2
    assert x["no_split"] == ["4A8B_window_white_edge_01"]
    assert x["train_not_boxed"] == [f"{c}_clutter_01", f"{c}_touch_01"]
    assert x["test_not_boxed"] == 1                         # occl_01: counted, not named
    assert f"{c}_occl_01" not in json.dumps(x)              # no test frame name anywhere
    assert x["slider_missing"] == [f"{c}_clutter_01", f"{c}_occl_02"]       # occl_01 is test -> occl_02
    assert x["train_no_vendor"] == [f"{c}_neg_02"]
    page = "\n".join(ra.gaps_lines(g))
    assert "Test frames among them" in page and ": 2 (window_white 2)" in page
    assert "`clutter_01`, `touch_01`" in page and "occl_01" not in page        # the test frame is never named


def test_summary_page_with_skipped_adaptive_and_known_gate_fail(ra, tmp_path):
    res = [ra.StepResult("tests", "pytest", "ok", 0, 1.0, "250 passed in 3.0s"),
           ra.StepResult("gate", "gate", "failed", 1, 1.0, GATE_FAIL),
           ra.StepResult("eval_table", "t", "ok", 0, 1.0, ""),
           ra.StepResult("vendor", "v", "failed", 2, 1.0, "boom"),
           ra.StepResult("adaptive", "a", "skipped", None, 0.0, "")]
    text = ra.write_summary(tmp_path, res, {}, "2026-11-24")
    assert "250 passed" in text and "**FAIL**" in text and "known" in text and "not on this branch" in text
    assert (tmp_path / "summary.md").read_text() == text


# ---------------------------------------------------------------- the vendor experiment's pure parts

@pytest.fixture(scope="module")
def ve():
    return load(EXP / "2026-11-24_vendor" / "run.py", "vendor_exp_under_test")


def test_center_reading_and_iou(ve):
    raw = {"originx": 100, "originy": 60, "width": 20, "height": 30}
    assert ve.center_reading(raw) == (180.0, 90.0, 220.0, 150.0)
    assert ve.center_reading({"originx": 1}) is None
    assert ve.iou_xyxy((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert ve.iou_xyxy((0, 0, 10, 10), (5, 0, 15, 10)) == pytest.approx(1 / 3)


def test_verdict(ve):
    def c(found, false):
        return {"found": found, "false": false}
    assert ve.verdict(c(3, 0), c(13, 1)) == "vendor (+10 found, +1 false)"
    assert ve.verdict(c(26, 2), c(24, 4)) == "ours (+2 found, -2 false)"
    assert ve.verdict(c(5, 0), c(6, 2)) == "mixed (vendor +1 found, +2 false)"
    assert ve.verdict(c(5, 1), c(5, 1)) == "tie"
    assert ve.verdict(c(5, 1), c(5, 3)) == "ours (same found, 2 fewer false)"


def test_place_found_indices(ve):
    from barrels.detect_types import Barrel
    from barrels.io import BLUE, ORANGE
    gts = [Barrel(color=ORANGE, bbox=(100, 100, 150, 160)), Barrel(color=BLUE, bbox=(300, 100, 350, 160))]
    preds = [Barrel(color=BLUE, bbox=(310, 110, 340, 150)),            # on gt 1 (index 1), small: place yes
             Barrel(color=BLUE, bbox=(100, 100, 150, 160))]            # on gt 0 but wrong color
    assert ve.place_found(preds, gts) == {1}
