#!/usr/bin/env python3
"""Every candidate of PREREG.md, judged leave one place out against today's detector and against F0 (contrast alone).

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_fusion/run.py [--only F0,F1] [--jobs 8]

Writes results/2026-11-27_fusion/: judge_<name>/ (against today), vs_F0_<name>/ (against F0), summary.md,
summary.json, chosen.json. Train frames only (``judge.load_frame`` refuses anything else).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fuse  # noqa: E402
import methods as M  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import judge as jg  # noqa: E402

ORDER = ["F0", "F1", "F1a", "F1b", "F2", "F3", "F4", "F5", "F6", "F1s", "F1u", "F3r", "F5r", "F6r"]


def row(name: str, j: jg.Judgement, vs: str) -> dict:
    b, c = j.total
    judged = [x for x in j.changes if x.judged]
    gained = sum(1 for x in judged if x.kind == "gained")
    lost = sum(1 for x in judged if x.kind == "lost")
    moved = [f"{p} {pb.found_w:.1f} -> {pc.found_w:.1f}" for p, (pb, pc) in j.places.items() if abs(pc.found_w - pb.found_w) > 1e-9]
    return {"name": name, "vs": vs, "verdict": j.result, "reason": j.verdict.reason, "clauses": [f"{k.key}: {k.state}" for k in j.verdict.clauses],
            "found_w": round(c.found_w, 2), "found_w_base": round(b.found_w, 2), "found": c.found, "found_base": b.found, "barrels": c.barrels,
            "placements": c.placements, "gained": gained, "lost": lost, "extra_w": round(c.extra_w, 2), "extra_w_base": round(b.extra_w, 2),
            "extra_frame": c.wrong + c.second + c.nothing, "extra_frame_base": b.wrong + b.second + b.nothing,
            "clean_empty": c.clean_empty, "cluttered_empty_w": round(c.cluttered_empty_w, 2), "places_moved": moved}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    names = [n for n in ORDER if not a.only or n in a.only.split(",")]
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    fuse.prepare(stems, a.jobs)
    F = fuse.fitter()
    truth = F.truth
    f0 = jg.leave_one_place_out(F.fit("F0"), frames[cnd.ORDINARY], fuse.TITLES["F0"])
    out = fuse.OUT
    rows = []
    for n in names:
        j = jg.judge(fit=F.fit(n), name=n, base_name="today", frames=frames, truth=truth, out_dir=out / f"judge_{n}")
        rows.append(row(n, j, "today"))
        print(f"{n} vs today: {j.result}  found {j.total[1].found_w:.2f} ({j.total[1].found})  extra {j.total[1].extra_w:.2f}", flush=True)
        if n != "F0":
            j2 = jg.judge(fit=F.fit(n), baseline=f0, name=n, base_name="F0", frames=frames, truth=truth, out_dir=out / f"vs_F0_{n}")
            rows.append(row(n, j2, "F0"))
            print(f"{n} vs F0: {j2.result}  found {j2.total[1].found_w:.2f} vs {j2.total[0].found_w:.2f}  extra {j2.total[1].extra_w:.2f} vs {j2.total[0].extra_w:.2f}", flush=True)
    prev = json.loads((out / "summary.json").read_text()) if (out / "summary.json").exists() and a.only else {"rows": []}
    keep = [r for r in prev["rows"] if r["name"] not in names]
    allrows = sorted(keep + rows, key=lambda r: (ORDER.index(r["name"]), r["vs"] != "today"))
    (out / "summary.json").write_text(json.dumps({"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "rows": allrows}, indent=1) + "\n")
    chosen = {n: F.chosen[n] for n in names if F.chosen.get(n)}
    old = json.loads((out / "chosen.json").read_text()) if (out / "chosen.json").exists() and a.only else {}
    old.update(chosen)
    (out / "chosen.json").write_text(json.dumps(old, indent=1, default=str) + "\n")
    write_summary(allrows)


def write_summary(rows) -> None:
    head = ("| candidate | against | verdict | found, placements | per frame | gained / lost | boxes not on their barrel, per arrangement "
            "(per frame) | clean / cluttered empty | places that moved |")
    lines = ["# Fusion: every candidate, judged leave one place out", "", "Made by `run.py`. Baseline columns: the arm named under 'against'.",
             "", head, "|" + "---|" * 9]
    for r in rows:
        lines.append(f"| {fuse.TITLES[r['name']]} | {r['vs']} | {r['verdict']} | {r['found_w_base']:.2f} -> **{r['found_w']:.2f}** of {r['placements']} "
                     f"| {r['found_base']} -> {r['found']} of {r['barrels']} | {r['gained']} / {r['lost']} | {r['extra_w_base']:.2f} -> {r['extra_w']:.2f} "
                     f"({r['extra_frame_base']} -> {r['extra_frame']}) | {r['clean_empty']} / {r['cluttered_empty_w']:.2f} | {'; '.join(r['places_moved']) or 'none'} |")
    (fuse.OUT / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
