#!/usr/bin/env python3
"""Every barrel and box the checks change in the judgements (plan: PREREG.md). Reads judge_*/judge.json of
results/2026-11-27_checks/ and writes changes.md: per judgement of an arm against the same color step without the
checks, every true barrel whose state changed (judged and report-only) and every frame whose boxes not on their
barrel changed.

    cd barrels && python experiments/2026-11-27_checks/changes.py"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "results" / "2026-11-27_checks"
L = ["# Every change the paint checks make in the judgements", "",
     "Per judgement of an arm against the same color step without the checks. Barrels: index in the label file, color, box, "
     "before → after (found / off / missed); [report only] = an extreme or unlisted condition. Boxes: the boxes that are not on "
     "their barrel (W wrong color, S second, N on nothing), before → after.", ""]
for d in sorted(OUT.glob("judge_*_vs_*")):
    cand, base = d.name[len("judge_"):].split("_vs_")
    if not cand.startswith(base + "_"):
        continue
    j = json.loads((d / "judge.json").read_text())
    L.append(f"## {cand} against {base}: {j['verdict']}")
    L.append("")
    for c in j["changes"]:
        L.append(f"- barrel `{c['stem']}` #{c['index'] + 1} {c['color']} {tuple(c['bbox'])}: {c['before']} → {c['after']}{'' if c['judged'] else ' [report only]'}")
    for b in j["box_changes"]:
        bf = ", ".join(f"{k[0].upper()} {v}" for k, v in b["before"].items() if v)
        af = ", ".join(f"{k[0].upper()} {v}" for k, v in b["after"].items() if v)
        L.append(f"- boxes `{b['stem']}`{' (empty frame)' if b['empty'] else ''}{'' if b['judged'] else ' [report only]'}: {bf or 'none'} → {af or 'none'}")
    L.append("")
(OUT / "changes.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
