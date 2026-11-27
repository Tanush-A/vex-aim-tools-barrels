#!/usr/bin/env python3
"""The judged round (PREREG.md): every candidate against today's default (fixed colors, detector, stripe by contrast)
by the standard pass rule. Four fixed arms in-sample, and ``fit`` leave one place out.

    python barrels/experiments/2026-11-27_occl_photo/judge_all.py

Writes results/2026-11-27_occl_photo/judge_<name>/ (judge.md, judge.json, changes.csv) and judge_summary.md.
"""
from __future__ import annotations

import candidate as cd
import lib
from lib import jg


def main() -> int:
    frames = jg.train_frames()
    stems = frames["ordinary"] + frames["extreme"] + frames["unlisted"]
    truth = jg.load_truth(stems)
    lines = ["# The judged round", "", "| candidate | verdict | found (placements) base -> cand | per frame | boxes not on their barrel | gained / lost |",
             "|---|---|---|---|---|---|"]
    jobs = [("cut", dict(candidate=cd.detect_frame_cut)), ("cut+bulge", dict(candidate=cd.detect_frame_cut_bulge)),
            ("slack", dict(candidate=cd.detect_frame_slack)), ("loose", dict(candidate=cd.detect_frame_loose)), ("fit", dict(fit=cd.fit))]
    for name, kw in jobs:
        j = jg.judge(name=name, base_name="today", frames=frames, truth=truth, out_dir=lib.OUT / f"judge_{name.replace('+', '_')}", **kw)
        js = jg.to_json(j)
        print(name, j.verdict.result, flush=True)
        txt = jg.format_judgement(j)
        print(txt, flush=True)
        lines.append(f"| `{name}` | {j.verdict.result} | see judge_{name.replace('+', '_')}/judge.md | | | {sum(1 for c in j.changes if c.judged)} barrels changed |")
    (lib.OUT / "judge_summary.md").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
