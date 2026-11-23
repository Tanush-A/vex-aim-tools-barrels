#!/usr/bin/env python3
"""Everything in one go, for a day with new frames and little time (2026-11-23). No arguments.

    python barrels/experiments/run_all.py

In order, each step run as its own command, its exit code recorded, and the next step run whatever happened:

1. the test suite                (BARRELS_NO_REPORT=1 python -m pytest -q, in barrels/)
2. the never-regress check       (python barrels/tools/report.py --gate): PASS / FAIL and the rows that failed it
3. the full eval table           (python barrels/tools/report.py --base-model default), train frames only
4. ours against the vendor       (python barrels/experiments/2026-11-24_vendor/run.py)
5. the adaptive-threshold rule   (python barrels/experiments/2026-11-24_adaptive/run.py), only if that file exists;
                                 exit 0 = the pre-registered rule passed, 1 = it failed
6. thresholds as ranges          (python barrels/experiments/2026-11-24_adaptive_range/run.py), only if that file
                                 exists: the range of each threshold around the slider labels, whether anything
                                 predicts it, and the range rule R2's test; exit 0 = R2 passed, 1 = it failed
7. the color candidates          (python barrels/experiments/2026-11-25_color/test.py), only if that file exists: the
                                 pre-registered leave-one-place-out test of the re-centred constant (C1), the blue box
                                 that follows the light (C2) and both (C3); exit 0 = a family passed, 1 = none did;
                                 writes the chosen family's model file (results/2026-11-25_color/config.json, or
                                 config_best_not_passing.json)
8. ours (candidate) vs vendor    (python barrels/experiments/2026-11-25_color/vendor.py), only if that file exists:
                                 the candidate model next to the fixed one and the vendor, per condition

Then ONE page, results/<today>_run_all/summary.md: at the top what is missing in the data (frames imported but not
boxed, slider labels not set, frames in no split, how many test frames each new condition has: counted from
data/splits.json, never opened); then each step's verdict and the few numbers that matter; last, what needs a
decision. Each step's full output is kept next to it (NN_<step>.txt, not committed).

A "new condition" is a ``{robot}_{light}_{surface}`` set that has at least one vendor file (every frame shot since
2026-11-18 has one), so tomorrow's conditions are picked up with no change here. Nothing in this script opens an
image; it reads file names, data/splits.json, and what the steps print or write.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

BARRELS = Path(__file__).resolve().parents[1]          # barrels/
REPO = BARRELS.parent
VENDOR_SCRIPT = BARRELS / "experiments" / "2026-11-24_vendor" / "run.py"
ADAPTIVE_SCRIPT = BARRELS / "experiments" / "2026-11-24_adaptive" / "run.py"
RANGE_SCRIPT = BARRELS / "experiments" / "2026-11-24_adaptive_range" / "run.py"
COLOR_SCRIPT = BARRELS / "experiments" / "2026-11-25_color" / "test.py"
COLOR_VENDOR_SCRIPT = BARRELS / "experiments" / "2026-11-25_color" / "vendor.py"
COLOR_RESULTS = BARRELS / "results" / "2026-11-25_color"
GEOMETRY_SCENES = ("calib", "ruler", "horizon")
SLIDER_SCENES = ("core_01", "clutter_01")              # plus one occl frame: occl_01, or occl_02 when occl_01 is a test frame
KNOWN_GATE_FAILS = {   # failing gate row -> why it is known (so a known failure is not mistaken for a new one)
    "4A8B_window_abpwhite occlx": "known: the false orange box on the striped-clutter trap `occlx_15` (TODO A9, the old "
                                  "close-up rule det1); fixed on another branch, not yet merged",
}
NAME_RE = re.compile(r"^(?P<robot>[A-Za-z0-9]+)_(?P<light>[A-Za-z0-9]+)_(?P<surface>[A-Za-z0-9]+)_(?P<scene>[A-Za-z]+)_(?P<nn>\d+)$")


# ---------------------------------------------------------------- running the steps

@dataclass
class Step:
    name: str
    cmd: list[str]
    cwd: Path = REPO
    env: dict = field(default_factory=dict)
    requires: Path | None = None          # skip the step (not a failure) when this file does not exist
    timeout: float = 1800.0


@dataclass
class StepResult:
    name: str
    cmd: str
    status: str                           # "ok" | "failed" | "skipped" | "timeout" | "error"
    code: int | None                      # the exit code; None when the step did not run to the end
    seconds: float
    output: str
    log: Path | None = None

    @property
    def ran(self) -> bool:
        return self.status in ("ok", "failed")


def run_step(step: Step) -> StepResult:
    """Run one step; never raises. A missing ``requires`` file -> skipped; a step that runs too long -> timeout; a
    command that cannot start -> error; otherwise ok (exit 0) or failed (any other exit code)."""
    shown = " ".join(step.cmd)
    if step.requires is not None and not Path(step.requires).exists():
        return StepResult(step.name, shown, "skipped", None, 0.0, f"skipped: {step.requires} does not exist")
    t0 = time.time()
    env = {**os.environ, **step.env}
    try:
        p = subprocess.run(step.cmd, cwd=step.cwd, env=env, capture_output=True, text=True, timeout=step.timeout)
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else (e.stdout or b"").decode(errors="replace")
        return StepResult(step.name, shown, "timeout", None, time.time() - t0, out + f"\n[stopped after {step.timeout:.0f} s]")
    except OSError as e:
        return StepResult(step.name, shown, "error", None, time.time() - t0, f"could not start: {e}")
    out = p.stdout + (("\n[stderr]\n" + p.stderr) if p.stderr.strip() else "")
    return StepResult(step.name, shown, "ok" if p.returncode == 0 else "failed", p.returncode, time.time() - t0, out)


def run_steps(steps: list[Step], log_dir: Path | None = None, echo=print) -> list[StepResult]:
    """Every step in order, whatever the one before did. With ``log_dir``, each output goes to NN_<name>.txt."""
    results = []
    for i, step in enumerate(steps, 1):
        echo(f"[{i}/{len(steps)}] {step.name}: {' '.join(step.cmd)}")
        r = run_step(step)
        if log_dir is not None:
            r.log = Path(log_dir) / f"{i:02d}_{step.name}.txt"
            r.log.write_text(f"$ {r.cmd}\n# status {r.status}, exit code {r.code}, {r.seconds:.1f} s\n\n{r.output}")
        echo(f"      -> {r.status}" + (f" (exit {r.code})" if r.code is not None else "") + f", {r.seconds:.0f} s")
        results.append(r)
    return results


def default_steps(py: str = sys.executable) -> list[Step]:
    return [
        Step("tests", [py, "-m", "pytest", "-q"], cwd=BARRELS, env={"BARRELS_NO_REPORT": "1"}),
        Step("gate", [py, "barrels/tools/report.py", "--gate"]),
        Step("eval_table", [py, "barrels/tools/report.py", "--base-model", "default"]),
        Step("vendor", [py, str(VENDOR_SCRIPT.relative_to(REPO))], requires=VENDOR_SCRIPT),
        Step("adaptive", [py, str(ADAPTIVE_SCRIPT.relative_to(REPO))], requires=ADAPTIVE_SCRIPT),
        Step("adaptive_range", [py, str(RANGE_SCRIPT.relative_to(REPO))], requires=RANGE_SCRIPT, timeout=3600.0),
        Step("color", [py, str(COLOR_SCRIPT.relative_to(REPO))], requires=COLOR_SCRIPT, timeout=4 * 3600.0),
        Step("color_vendor", [py, str(COLOR_VENDOR_SCRIPT.relative_to(REPO))], requires=COLOR_VENDOR_SCRIPT),
    ]


# ---------------------------------------------------------------- reading what the steps said

def parse_pytest(out: str) -> str:
    """The last summary line of ``pytest -q`` ("250 passed, 1 failed in 30.1s"), or "" when there is none."""
    for line in reversed(out.strip().splitlines()):
        s = line.strip().strip("=").strip()
        if re.search(r"\b(passed|failed|error|errors|no tests ran)\b", s) and re.search(r"\bin [\d.]+s", s):
            return s
    return ""


def parse_gate(out: str) -> dict:
    """The gate's verdict: ``{"verdict": PASS|FAIL|"", "result_line", "failing": [row names], "known": {row: why},
    "unknown": [rows], "protected": [the protected set total lines]}``."""
    res = {"verdict": "", "result_line": "", "failing": [], "known": {}, "unknown": [], "protected": []}
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("RESULT:"):
            res["result_line"] = s
            res["verdict"] = "PASS" if s.startswith("RESULT: PASS") else "FAIL"
            res["failing"] = [x.strip() for grp in re.findall(r"row\(s\)[^()]*\(([^()]*)\)", s) for x in grp.split(",") if x.strip()]
        elif s.endswith("[protected]"):
            res["protected"].append(re.sub(r"\s+", " ", s.replace("[protected]", "").strip()))
    for row in res["failing"]:
        if row in KNOWN_GATE_FAILS:
            res["known"][row] = KNOWN_GATE_FAILS[row]
        else:
            res["unknown"].append(row)
    return res


def written_dir(out: str) -> Path | None:
    """The folder a step said it wrote ("written to <path>"), if it says so."""
    m = re.findall(r"written to (\S+)", out)
    return Path(m[-1]) if m else None


def summary_path(out: str) -> Path | None:
    """A summary.md the step points at: "written to DIR" -> DIR/summary.md, or any path ending in summary.md."""
    d = written_dir(out)
    if d is not None and (d / "summary.md").exists():
        return d / "summary.md"
    for m in re.findall(r"(\S+summary\.md)", out):
        p = Path(m) if Path(m).is_absolute() else REPO / m
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------- what is missing in the data (names only)

def tags(stem: str) -> dict | None:
    m = NAME_RE.match(stem)
    return m.groupdict() if m else None


def data_gaps(raw_dir: Path, labels_dir: Path, vendor_dir: Path, splits: dict[str, list[str]]) -> dict:
    """Per new condition (a set with at least one vendor file): frames, train / test / in no split, the TRAIN frames not
    boxed, how many TEST frames are not boxed (counted, not named), the slider frames still to set, train frames with
    no vendor file. Reads file names and the split file only."""
    where = {s: k for k, v in splits.items() for s in v}
    stems = sorted(p.stem for p in Path(raw_dir).glob("*.png"))
    vendor = {p.name[:-len("_vendor.json")] for p in Path(vendor_dir).glob("*_vendor.json")}
    sets: dict[str, list[str]] = {}
    for s in stems:
        t = tags(s)
        if t and t["scene"] not in GEOMETRY_SCENES:
            sets.setdefault(f"{t['robot']}_{t['light']}_{t['surface']}", []).append(s)
    out = {}
    for key, ss in sorted(sets.items()):
        if not any(s in vendor for s in ss):
            continue
        train = [s for s in ss if where.get(s) == "train"]
        test = [s for s in ss if where.get(s) == "test"]
        nosplit = [s for s in ss if where.get(s) is None]
        boxed = {s for s in ss if (Path(labels_dir) / f"{s}_boxes.json").exists()}
        names = {tags(s)["scene"] + "_" + tags(s)["nn"]: s for s in ss}
        slider_missing = []
        if any(n.startswith("core_") for n in names):          # a condition shot (the occlusion set has no slider labels)
            want = list(SLIDER_SCENES)
            occl = next((n for n in ("occl_01", "occl_02") if names.get(n) in train), None)
            want += [occl] if occl else []
            for n in want:
                s = names.get(n)
                if s in train and not (Path(labels_dir) / f"{s}_hs.json").exists():
                    slider_missing.append(s)
        out[key] = {"frames": len(ss), "train": len(train), "test": len(test), "no_split": nosplit,
                    "train_not_boxed": [s for s in train if s not in boxed], "test_not_boxed": sum(1 for s in test if s not in boxed),
                    "slider_missing": slider_missing, "train_no_vendor": [s for s in train if s not in vendor]}
    return out


# ---------------------------------------------------------------- the page

def condition(key: str) -> str:
    return key.split("_", 1)[1] if "_" in key else key


def gaps_lines(gaps: dict) -> list[str]:
    L = ["## Missing in the data (file names only; test frames counted, never opened)", ""]
    if not gaps:
        return L + ["No condition with vendor files found.", ""]
    tests = ", ".join(f"{condition(k)} {g['test']}" for k, g in gaps.items())
    L.append(f"{len(gaps)} new conditions (sets with vendor files). Test frames among them, counted from data/splits.json and "
             f"never opened: {sum(g['test'] for g in gaps.values())} ({tests}).")
    open_rows = {k: g for k, g in gaps.items() if g["no_split"] or g["train_not_boxed"] or g["test_not_boxed"] or g["slider_missing"] or g["train_no_vendor"]}
    if open_rows:
        L += ["", "| condition | frames | train / test | in no split | train not boxed | test not boxed | slider labels to set | train without vendor file |",
              "|---|---:|---|---|---|---:|---|---|"]
        for k, g in open_rows.items():
            def names(xs):
                return ", ".join(f"`{x.split('_', 3)[3]}`" for x in xs) if xs else "-"
            L.append(f"| {condition(k)} | {g['frames']} | {g['train']} / {g['test']} | {names(g['no_split'])} | {names(g['train_not_boxed'])} | "
                     f"{g['test_not_boxed'] or '-'} | {names(g['slider_missing'])} | {names(g['train_no_vendor'])} |")
    done = [condition(k) for k in gaps if k not in open_rows]
    if done:
        L += ["", "Complete (split, boxed, slider labels set, a vendor file on every train frame): " + ", ".join(done) + "."]
    todo = [k for k, g in gaps.items() if g["no_split"] or g["train_not_boxed"] or g["slider_missing"] or g["test_not_boxed"]]
    L += (["", ("" if not todo else
               "To do before the numbers below cover everything: " + "; ".join(
                   condition(k) + ": " + ", ".join(x for x in (
                       f"split {len(gaps[k]['no_split'])} frame(s) (make_splits.py)" if gaps[k]["no_split"] else "",
                       f"box {len(gaps[k]['train_not_boxed'])} train frame(s)" if gaps[k]["train_not_boxed"] else "",
                       f"box {gaps[k]['test_not_boxed']} test frame(s) (box_tool; they are scored only in a planned look)" if gaps[k]["test_not_boxed"] else "",
                       f"slider labels on {len(gaps[k]['slider_missing'])} frame(s)" if gaps[k]["slider_missing"] else "") if x)
                   for k in todo) + ". Frames in no split or not boxed are left out of every number below."), ""] if todo else [""])
    return L


def vendor_lines(r: StepResult | None) -> tuple[list[str], dict | None]:
    if r is None or not r.ran:
        return ["## Ours against the vendor", "", f"Did not run ({r.status if r else 'no step'}): see its log.", ""], None
    d = written_dir(r.output)
    js = d / "summary.json" if d else None
    if not (js and js.exists()):
        return ["## Ours against the vendor", "", f"Ran (exit {r.code}) but wrote no summary.json: see its log.", ""], None
    s = json.loads(js.read_text())
    L = ["## Ours against the vendor (train frames with a vendor file)", "",
         "| condition | barrels | ours found / false | vendor found / false | ours / vendor by place |", "|---|---:|---|---|---|"]
    for c, v in s["conditions"].items():
        o, w = v["ours"], v["vendor"]
        L.append(f"| {c} | {o['barrels']} | {o['found']} / {o['false']} | {w['found']} / {w['false']} | {o['found_place']} / {w['found_place']} |")
    tot = {a: sum(v[a]["found"] for v in s["conditions"].values()) for a in ("ours", "vendor")}
    n = sum(v["ours"]["barrels"] for v in s["conditions"].values())
    fx = {a: sum(v[a]["false"] for v in s["conditions"].values()) for a in ("ours", "vendor")}
    miss = s.get("vendor_finds_we_miss", [])
    frames = sorted({b["stem"] for b in miss})
    hidden = [b for b in miss + s.get("vendor_place_only_we_miss", []) if "occluded" in b.get("flags", "")]
    val = s.get("validation", {})
    fit = (val.get("fit_x", {}).get("slope"), val.get("fit_y", {}).get("slope"))
    L += ["", f"Strict v2 rule. All together: ours {tot['ours']} of {n} with {fx['ours']} false; the vendor {tot['vendor']} of {n} with {fx['vendor']} false.",
          f"The vendor finds {len(miss)} barrels we miss, on {len(frames)} frames (list: `{d.relative_to(REPO) if d.is_relative_to(REPO) else d}/summary.md`).",
          (f"Vendor files: conversion checked (center fit slope {fit[0]:.2f} x, {fit[1]:.2f} y; 2 expected), "
           f"free-standing barrels median IoU with the hand box {val.get('free', {}).get('iou', float('nan')):.2f}."
           if None not in fit else "Vendor files: validation numbers missing.")]
    if hidden:
        L.append("Hidden barrels the vendor finds (strict or by place) and we miss: "
                 + ", ".join(f"`{b['stem'].split('_', 1)[1]}` #{b['gt']}" for b in hidden) + ".")
    L.append("")
    return L, s


def range_lines(r: StepResult | None, decide: list[str]) -> list[str]:
    """The range experiment's section: in plain words whether the range version holds, and R2's verdict."""
    L = ["## Thresholds as ranges (and the range rule R2)", ""]
    if r is None or r.status == "skipped":
        return L + ["Not run: `experiments/2026-11-24_adaptive_range/run.py` is not on this branch.", ""]
    d = written_dir(r.output)
    cfg = d / "config.json" if d else None
    if not r.ran or not (cfg and cfg.exists()):
        decide.append("The range experiment gave no verdict: see its log.")
        return L + [f"No verdict ({r.status}, exit {r.code}): see its log.", ""]
    c = json.loads(cfg.read_text())
    parts = c.get("holds_parts", {})
    yn = lambda x: "yes" if x else "no"  # noqa: E731
    L.append(f"**The range version {'HOLDS' if c.get('holds') else 'does not hold'}.** In plain words: "
             + ("a frame has a run of workable values for each threshold, R2 lands in the held-out runs more often than the fixed value, and it passes the detection test."
                if c.get("holds") else
                "the parts that fail are " + ", ".join(x for x, ok in (("the runs do not hold when all six move together (a)", parts.get("a")),
                                                                       ("R2 does not land inside held-out runs more often than fixed (b)", parts.get("b")),
                                                                       ("R2 fails the detection test (c)", parts.get("c"))) if not ok) + "."))
    L.append(f"Parts: (a) ranges hold jointly {yn(parts.get('a'))}; (b) R2 beats fixed on a constrained threshold {yn(parts.get('b'))}"
             + (f" ({', '.join(parts.get('b_thresholds', []))})" if parts.get("b_thresholds") else "") + f"; (c) R2 passes C2-C6 {yn(parts.get('c'))}.")
    fails = [k for k, v in c.get("clauses", {}).items() if not v.get("pass")]
    L.append(f"R2: **{'PASS' if c.get('passed') else 'FAIL'}**" + (f" (failed: {', '.join(fails)})" if fails else "") + "."
             + (f" Its page: `{(d / 'summary.md').relative_to(REPO) if d.is_relative_to(REPO) else d / 'summary.md'}`." if (d / "summary.md").exists() else ""))
    L.append("")
    if c.get("passed"):
        decide.append("The range rule R2 passed its pre-registered test: adopt it (walkthrough first, then the never-regress check)?")
    return L


def color_lines(r: StepResult | None, decide: list[str], results_dir: Path = COLOR_RESULTS) -> list[str]:
    """The 2026-11-25 color test's section: which family was chosen, whether it passed its PREREG, the model file."""
    L = ["## The color candidates (2026-11-25)", ""]
    if r is None or r.status == "skipped":
        return L + ["Not run: `experiments/2026-11-25_color/test.py` is not on this branch.", ""]
    js = results_dir / "test" / "chosen.json"
    if not r.ran or not js.exists():
        decide.append("The color test gave no verdict: see its log.")
        return L + [f"No verdict ({r.status}, exit {r.code}): see its log.", ""]
    c = json.loads(js.read_text())
    pick, passing = c.get("pick"), c.get("passing", [])
    names = {"C1": "re-centred constant", "C2": "blue box follows the light", "C3": "both"}
    L.append(f"**{'PASS' if passing else 'FAIL'}**: chosen family {pick} ({names.get(pick, pick)})"
             + (" passes its pre-registered acceptance." if passing else ", the best of the three, does NOT pass.")
             + f" Model file: `{'config.json' if passing else 'config_best_not_passing.json'}` in `results/2026-11-25_color/`; "
             "page: `results/2026-11-25_color/test/summary.md`.")
    L.append("")
    if passing:
        decide.append(f"The color family {pick} passed its pre-registered test: make it the default (walkthrough first, "
                      "`results/2026-11-25_color/walkthrough.md`; then worldmap_bridge.DEFAULT_MODEL)?")
    return L


def write_summary(out_dir: Path, results: list[StepResult], gaps: dict, today: str) -> str:
    by = {r.name: r for r in results}
    L = [f"# Run all, {today}", "",
         "Steps: " + ", ".join(f"{r.name} {r.status}" + (f" (exit {r.code})" if r.code not in (None, 0) else "") for r in results) + ".", ""]
    L += gaps_lines(gaps)
    decide = []
    t = by.get("tests")
    if t:
        line = parse_pytest(t.output) if t.ran else ""
        L += ["## Tests", "", f"{'Pass' if t.status == 'ok' else 'FAIL'}: {line or t.status}.", ""]
        if t.status != "ok":
            decide.append("Tests fail: read `" + (t.log.name if t.log else "the tests log") + "` before trusting any number.")
    g = by.get("gate")
    if g:
        pg = parse_gate(g.output) if g.ran else {"verdict": ""}
        L += ["## Never-regress check", ""]
        if not pg["verdict"]:
            L += [f"No verdict ({g.status}, exit {g.code}): see `{g.log.name if g.log else 'the gate log'}`.", ""]
            decide.append("The never-regress check gave no verdict.")
        else:
            L.append(f"**{pg['verdict']}**." + ("" if pg["verdict"] == "PASS" else f" Failing rows: {', '.join(pg['failing']) or 'see log'}."))
            for row, why in pg["known"].items():
                L.append(f"- {row}: {why}.")
            for row in pg["unknown"]:
                L.append(f"- {row}: **new failure**, not a known one.")
            L += ["", "Protected sets (baseline -> now): " + "; ".join(pg["protected"]) + "." if pg["protected"] else "", ""]
            if pg["unknown"]:
                decide.append("The never-regress check fails on a row that is not a known failure: " + ", ".join(pg["unknown"]) + ".")
    e = by.get("eval_table")
    if e:
        L += ["## Full eval table", "", f"{e.status} (train frames only): `{e.log.name if e.log else 'eval_table log'}`.", ""]
    vl, vs = vendor_lines(by.get("vendor"))
    L += vl
    if vs:
        worse = [c for c, v in vs["conditions"].items() if v["vendor"]["found"] > v["ours"]["found"]]
        if worse:
            decide.append("The vendor finds more than ours on " + ", ".join(worse) + ": which of these count as ordinary conditions "
                          "(the goal is to match it there)?")
    a = by.get("adaptive")
    L += ["## Adaptive-threshold rule", ""]
    if a is None or a.status == "skipped":
        L += ["Not run: `experiments/2026-11-24_adaptive/run.py` is not on this branch.", ""]
    else:
        verdict = {0: "PASS (the pre-registered rule holds)", 1: "FAIL (the pre-registered rule does not hold)"}.get(a.code, f"no verdict ({a.status}, exit {a.code})")
        sp = summary_path(a.output)
        L += [f"**{verdict}**." + (f" Its page: `{sp.relative_to(REPO) if sp.is_relative_to(REPO) else sp}`." if sp else ""), ""]
        if a.code == 0:
            decide.append("The adaptive rule passed its pre-registered test: adopt it (walkthrough first, then the never-regress check)?")
        elif a.code not in (0, 1):
            decide.append("The adaptive script did not give a verdict: see its log.")
    L += range_lines(by.get("adaptive_range"), decide)
    L += color_lines(by.get("color"), decide)
    cv = by.get("color_vendor")
    if cv is not None and cv.status != "skipped":
        L += ["## Ours (candidate color model) against the vendor", "",
              f"{cv.status}: `results/2026-11-25_color/vendor.md`" + (f" (log `{cv.log.name}`)" if cv.log else "") + ".", ""]
    gaps_todo = [condition(k) for k, x in gaps.items() if x["no_split"] or x["train_not_boxed"] or x["slider_missing"]]
    if gaps_todo:
        decide.insert(0, "Finish the data (top of this page) for: " + ", ".join(gaps_todo) + ".")
    L += ["## Needs your decision", ""] + ([f"- {x}" for x in decide] or ["- Nothing."]) + [""]
    L += [f"Logs: {', '.join('`' + r.log.name + '`' for r in results if r.log)} (in this folder, not committed).", ""]
    text = "\n".join(x for x in L if x is not None)
    (out_dir / "summary.md").write_text(text)
    return text


def fresh_dir(path: Path) -> Path:
    i, p = 2, path
    while p.exists():
        p = path.with_name(f"{path.name}_{i}"); i += 1
    p.mkdir(parents=True)
    return p


def main() -> int:
    today = dt.date.today().isoformat()
    out = fresh_dir(BARRELS / "results" / f"{today}_run_all")
    results = run_steps(default_steps(), log_dir=out)
    splits = json.loads((BARRELS / "data" / "splits.json").read_text())
    gaps = data_gaps(BARRELS / "data" / "raw", BARRELS / "data" / "labels", BARRELS / "data" / "vendor", splits)
    print()
    print(write_summary(out, results, gaps, today))
    print("written to", out)
    return 0 if all(r.status in ("ok", "failed", "skipped") for r in results) else 1     # 1 = a step could not give a verdict


if __name__ == "__main__":
    sys.exit(main())
