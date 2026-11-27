#!/usr/bin/env python3
"""The adoption of the stripe by contrast (2026-11-27): the proof that the default now does what was judged.

    python barrels/experiments/2026-11-27_adopt_contrast/prove.py [--skip-judge]

Not an experiment: nothing is chosen here. Train frames only (``judge.train_frames``, ``judge.load_frame``, which refuse
a test frame before it is opened). Three parts; exit 0 when all three hold.

A. **Same boxes as the judged code.** The experiment's own code, read from git (``contrast.py`` at REF_MODULE and
   ``candidate.py`` / ``common.py`` at REF_EXPERIMENT, the judged ``candidate.py:detect_frame``), and the new default
   ``pipeline.detect_frame`` are run on every train frame (ordinary, extreme and unlisted). Their boxes (color and box,
   in order) must be identical on every frame. Both run on today's detector.

B. **The judged numbers.** The judge of the new default against the default before it, with ``detector.detect``
   replaced by the detector as it was when the contrast experiment was judged (``detector.py`` at PRE_SLACK: the
   collapsed detector, before the seam reading was adopted the same day). Expected, from the experiment's in-sample
   line for this setting (its ``insample.md``, "the pick"; ENTRY.md: "in-sample: found +23.2 placements, 278 per
   frame, boxes +0.5"): 133.80 -> 156.97 of 172 placements (+23.17), 211 -> 278 per frame, boxes not on their
   barrel 1.93 -> 2.43, bathroom / ottoman / gray table 13.5 / 10.7 / 15.0.

C. **The judge as it runs now**: the new default against the previous default (the same color model and DetConfig,
   no contrast stage), today's detector. Pages in results/2026-11-27_adopt_contrast/judge_vs_previous/.

D. (report only) every ordinary frame where the new default on today's detector (C) differs from the new default on
   the pre-seam-reading detector (B): what the two rules adopted on 2026-11-27 do together.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BARRELS = Path(__file__).resolve().parents[2]
REPO = BARRELS.parent
sys.path.insert(0, str(BARRELS / "src"))
from barrels import conditions as cnd  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

OUT = BARRELS / "results" / "2026-11-27_adopt_contrast"
REF_MODULE = "5ea663a"          # wip/exp-combined: contrast.py ported to the collapsed detector (its two tests); the code that reproduced 155.3
REF_EXPERIMENT = "d27e489"      # wip/exp-contrast: the experiment folder with candidate.py (BEST) and common.py
PRE_SLACK = "c6b39ab"           # barrels just before the merge of wip/adopt-slack
# the experiment's in-sample line for its setting ("the pick", results/2026-11-26_contrast/insample.md on wip/exp-contrast):
# today 133.8 of 172 placements, 211 per frame, boxes 1.93; the pick +23.17, 278 per frame, boxes +0.50; bathroom /
# ottoman / gray table 13.5 / 10.7 / 15.0
EXPECTED_B = {"baseline": (133.8, 211, 1.93), "candidate": (156.97, 278, 2.43)}
EXPECTED_B_PLACES = {"home_bathtile": 13.5, "home_ottoman": 10.7, "abp_gray": 15.0}
assert str(Path(jg.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {jg.__file__}, not from this checkout"


def git_show(rev: str, path: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{rev}:{path}"], check=True, capture_output=True, text=True).stdout


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def reference(tmp: Path):
    """The judged ``candidate.detect_frame``, its imports pointed at the experiment's own contrast module."""
    src = git_show(REF_MODULE, "barrels/src/barrels/contrast.py")
    src = src.replace("from . import geometry as geo", "from barrels import geometry as geo").replace("from .io import", "from barrels.io import")
    (tmp / "contrast_ref.py").write_text(src)
    common = git_show(REF_EXPERIMENT, "barrels/experiments/2026-11-26_contrast/common.py")
    common = common.replace("from barrels import contrast as cn", "import contrast_ref as cn")
    common = common.replace('assert str(Path(cn.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {cn.__file__}, not from this checkout"', "")
    (tmp / "common.py").write_text(common)
    cand = git_show(REF_EXPERIMENT, "barrels/experiments/2026-11-26_contrast/candidate.py")
    assert "from barrels import contrast as cn" in cand
    (tmp / "candidate.py").write_text(cand.replace("from barrels import contrast as cn", "import contrast_ref as cn"))
    sys.path.insert(0, str(tmp))
    load("contrast_ref", tmp / "contrast_ref.py")
    load("common", tmp / "common.py")
    return load("candidate_ref", tmp / "candidate.py")


def key(boxes) -> list:
    return [(int(b.color), tuple(int(v) for v in b.bbox)) for b in boxes]


def part_a(ref, frames: dict) -> tuple[bool, list[str]]:
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    diff, n_boxes, added, t_ref, t_new = [], 0, 0, 0.0, 0.0
    for s in stems:
        f = jg.load_frame(s)
        t0 = time.perf_counter(); a = key(ref.detect_frame(s, f)); t1 = time.perf_counter()
        nb = pl.detect_frame(f); t2 = time.perf_counter()
        t_ref += t1 - t0; t_new += t2 - t1
        b = key(nb)
        n_boxes += len(b)
        added += sum(1 for x in nb if x.source == "contrast")
        if a != b:
            diff.append(f"  - {s}: judged code {a}, new default {b}")
    ok = not diff
    lines = ["## A. The new default against the judged code, every train frame", "",
             f"Reference: `contrast.py` at {REF_MODULE} (wip/exp-combined), `candidate.py` / `common.py` at {REF_EXPERIMENT} (wip/exp-contrast), "
             f"`candidate.detect_frame` (BEST: add mode, strength floor 1.15, absolute check 0.8, extent 0.15). Both on today's detector.", "",
             f"- frames: {len(stems)} ({len(frames[cnd.ORDINARY])} ordinary, {len(frames[cnd.EXTREME])} extreme, {len(frames[cnd.UNLISTED])} unlisted)",
             f"- boxes of the new default: {n_boxes}, of them added by the contrast stage: {added}",
             f"- frames whose boxes differ: {len(diff)}", *diff[:30],
             f"- time, all frames: judged code {t_ref:.1f} s, new default {t_new:.1f} s", "",
             f"RESULT A: {'IDENTICAL BOXES ON EVERY FRAME' if ok else 'DIFFERENT'}", ""]
    return ok, lines


def tally(j) -> dict:
    b, c = j.total
    return {"baseline": (round(b.found_w, 2), b.found, round(b.extra_w, 2)), "candidate": (round(c.found_w, 2), c.found, round(c.extra_w, 2)),
            "verdict": j.result, "gained": sum(1 for x in j.changes if x.judged and x.kind == "gained"),
            "lost": sum(1 for x in j.changes if x.judged and x.kind == "lost")}


def part_b(frames: dict, truth) -> tuple[bool, list[str], dict]:
    path = Path(tempfile.mkdtemp(prefix="preslack_")) / "detector_preslack.py"
    path.write_text(git_show(PRE_SLACK, "barrels/src/barrels/detector.py"))
    old = load("barrels._detector_preslack", path)
    today = det.detect
    det.detect = old.detect                         # what pipeline.detect_frame and contrast.add_boxes call
    try:
        j = jg.judge(jg.fixed_detector(), jg.previous_detector(), frames=frames, truth=truth, report_only=False,
                     out_dir=OUT / "judge_preslack_detector", name="new default", base_name="previous default")
    finally:
        det.detect = today
    t = tally(j)
    places = {p: round(j.places[p][1].found_w, 1) for p in EXPECTED_B_PLACES}
    t["places"] = places
    ok = all(t[k] == EXPECTED_B[k] for k in EXPECTED_B) and places == EXPECTED_B_PLACES
    b, c = t["baseline"], t["candidate"]
    lines = ["## B. The judged numbers, on the detector the experiment was judged on", "",
             f"`detector.py` at {PRE_SLACK} (before the seam reading). Ordinary train conditions, the standard judge.", "",
             "| | found, placements | per frame | boxes not on their barrel |", "|---|---:|---:|---:|",
             f"| previous default (no contrast) | {b[0]:.2f} | {b[1]} | {b[2]:.2f} |",
             f"| new default | {c[0]:.2f} | {c[1]} | {c[2]:.2f} |",
             f"| expected (the experiment's insample.md, 'the pick') | {EXPECTED_B['baseline'][0]} -> {EXPECTED_B['candidate'][0]} | "
             f"{EXPECTED_B['baseline'][1]} -> {EXPECTED_B['candidate'][1]} | {EXPECTED_B['baseline'][2]} -> {EXPECTED_B['candidate'][2]} |", "",
             f"Bathroom / ottoman / gray table: {places['home_bathtile']} / {places['home_ottoman']} / {places['abp_gray']} "
             f"(expected {EXPECTED_B_PLACES['home_bathtile']} / {EXPECTED_B_PLACES['home_ottoman']} / {EXPECTED_B_PLACES['abp_gray']}).", "",
             f"Verdict {t['verdict']}; {t['gained']} barrels gained, {t['lost']} lost.", "",
             f"RESULT B: {'THE JUDGED NUMBERS, EXACTLY' if ok else 'DIFFERENT FROM THE JUDGED NUMBERS'}", ""]
    t["_judgement"] = j
    return ok, lines, t


def part_d(jb, jc, frames: dict) -> list[str]:
    """Where the new default on today's detector differs from the new default on the detector the experiment was
    judged on: the seam reading and the contrast stage together (report only, nothing is decided here)."""
    out = ["## D. The seam reading and the contrast stage together (report only)", "",
           "The new default on today's detector (C) against the new default on the detector before the seam reading (B), "
           "ordinary train frames: every frame whose barrels change state.", ""]
    n = 0
    for s in frames[cnd.ORDINARY]:
        a, b = jb.candidate.counts[s], jc.candidate.counts[s]
        if a.gt != b.gt or a.boxes != b.boxes:
            n += 1
            out.append(f"- `{s}`: barrels {list(a.gt)} -> {list(b.gt)}; boxes {list(a.boxes)} -> {list(b.boxes)}")
    out += ["", f"{n} frames differ.", ""]
    return out


def part_c(frames: dict, truth) -> tuple[bool, list[str], dict]:
    j = jg.judge(jg.fixed_detector(), jg.previous_detector(), frames=frames, truth=truth,
                 out_dir=OUT / "judge_vs_previous", name="new default", base_name="previous default")
    t = tally(j)
    b, c = t["baseline"], t["candidate"]
    lines = ["## C. The judge as it runs now (today's detector, with the seam reading)", "",
             "| | found, placements | per frame | boxes not on their barrel |", "|---|---:|---:|---:|",
             f"| previous default (no contrast) | {b[0]:.2f} | {b[1]} | {b[2]:.2f} |",
             f"| new default | {c[0]:.2f} | {c[1]} | {c[2]:.2f} |", "",
             f"Verdict **{t['verdict']}**; {t['gained']} barrels gained, {t['lost']} lost. Pages: `judge_vs_previous/`.", "",
             f"RESULT C: {t['verdict']}", ""]
    t["_judgement"] = j
    return t["verdict"] == jg.PASS, lines, t


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-judge", action="store_true", help="part A only")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    frames = jg.train_frames()
    ref = reference(Path(tempfile.mkdtemp(prefix="contrast_ref_")))
    ok_a, lines = part_a(ref, frames)
    print("\n".join(lines), flush=True)
    ok, summary = ok_a, {"A": ok_a}
    if not args.skip_judge:
        truth = jg.load_truth(frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED])
        ok_b, lb, tb = part_b(frames, truth)
        print("\n".join(lb), flush=True)
        ok_c, lc, tc = part_c(frames, truth)
        print("\n".join(lc), flush=True)
        ld = part_d(tb.pop("_judgement"), tc.pop("_judgement"), frames)
        print("\n".join(ld), flush=True)
        lines += lb + lc + ld
        ok = ok and ok_b and ok_c
        summary.update({"B": ok_b, "B_numbers": tb, "C": ok_c, "C_numbers": tc})
    head = ["# The stripe by contrast adopted: the proof", "", f"Made by `experiments/2026-11-27_adopt_contrast/prove.py`. Train frames only.", ""]
    (OUT / "prove.md").write_text("\n".join(head + lines + [f"ALL: {'PASS' if ok else 'NOT ALL HOLD'}", ""]))
    (OUT / "prove.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    print("ALL:", "PASS" if ok else "NOT ALL HOLD")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
