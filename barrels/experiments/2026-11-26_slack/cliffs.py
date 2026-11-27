#!/usr/bin/env python3
"""Report only (PREREG.md, "The cliffs"): the three numbers on the false-box side moved by 20 %, with and without
slack=D, on the ordinary train frames with fixed colors. Found and boxes not on their barrel. A value the code
refuses is reported as refused.

    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/cliffs.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import conditions as cnd, counting as ct, judge as jg  # noqa: E402

frames = jg.train_frames()
stems = frames[cnd.ORDINARY]
truth = jg.load_truth(stems)
runs = {}
for slack in ("", "D"):
    for ov in ({}, {"min_width_px": 12.8}, {"min_stripe_px": 4.8}, {"height_max": 1.2}):
        name = f"slack={slack or 'off'} " + (", ".join(f"{k}={v}" for k, v in ov.items()) or "defaults")
        d = jg.model_detector(det_overrides={**ov, **({"slack": slack} if slack else {})})
        try:
            runs[name] = jg.run_many({name: d}, stems, truth)[name]
        except AssertionError as e:
            runs[name] = f"refused: {str(e)[:90]}"
lines = ["| arm | found (per frame) | boxes not on their barrel (per frame / per arrangement) | boxes on empty frames |", "|---|---|---|---|"]
for name, r in runs.items():
    if isinstance(r, str):
        lines.append(f"| {name} | {r} | | |")
        continue
    t = ct.tally(r.counts, stems, truth.placements)
    lines.append(f"| {name} | {t.found} ({t.found_w:.1f} placements) | {t.extra} / {t.extra_w:.2f} | {t.empty} |")
out = Path(__file__).resolve().parents[2] / "results" / "2026-11-26_slack" / "round2" / "cliffs.md"
out.write_text("# The cliffs, with and without slack=D (report only)\n\n" + "\n".join(lines) + "\n")
print("\n".join(lines))
