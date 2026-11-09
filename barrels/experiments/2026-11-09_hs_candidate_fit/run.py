#!/usr/bin/env python3
"""Fit the hs candidate once and save it as a model file the detector can load.

The candidate chosen by the proposed rule in experiments/2026-11-08_seg_hs_v2 is `hs o5 b15 h5-95 m2`:
pipeline.Config(color_model="hs", hs_s_pct=(5, 15), hs_h_pct=(5, 95), hs_h_margin=2). This script fits it on the
16 home train frames (4A8B_window_light_*, the same frames v1 afd85483 was fit on; the campus frames and every test
frame are NOT used) and writes results/2026-11-09_hs_candidate/config.json in the shape worldmap_bridge.
BarrelDetectorHook.load reads ("model" = cfg + boxes + fit_info), so that

    python barrels/tools/detect_image.py IMAGE --model barrels/results/2026-11-09_hs_candidate/config.json
    BARRELS_MODEL=barrels/results/2026-11-09_hs_candidate/config.json simple_cli BarrelTracker   (from barrels/live)

run the candidate front end. Nothing is adopted by this script: DEFAULT_MODEL still points at v1 until the
walkthrough is acknowledged (TODO P0-1/2). Not an experiment with a claim, so no EXPERIMENTS.md entry;
RUNBOOK.md points here. The numbers it prints are the fitted thresholds, for the record.

    python barrels/experiments/2026-11-09_hs_candidate_fit/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, io, pipeline as pl, splits  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-09_hs_candidate"
CFG = pl.Config(color_model="hs", hs_s_pct=(5, 15), hs_h_pct=(5, 95), hs_h_margin=2)
HOME_PREFIX = "4A8B_window_light"


def main() -> int:
    home = sorted(s for s in splits.load_splits()["train"] if s.startswith(HOME_PREFIX))
    frames = [pl.Frame.from_image(io.load_image(io.find_image(s))) for s in home]
    masks = [io.load_mask(io.mask_path(io.find_image(s))) for s in home]
    model = pl.fit(frames, masks, CFG)
    OUT.mkdir(parents=True, exist_ok=True)
    out = {"name": "hs o5 b15 h5-95 m2 (candidate, not adopted)", "config": CFG.to_dict(), "config_hash": CFG.short_hash(),
           "git": bcv.git_hash(), "fit_frames": home, "model": model.to_dict()}
    json.dump(out, (OUT / "config.json").open("w"), indent=1)
    lines = [f"config {CFG.short_hash()}, git {out['git']}, fit on {len(home)} home train frames"]
    for c, name in ((ORANGE, "orange"), (BLUE, "blue")):
        b = model.boxes[c]; info = model.fit_info.get(str(c), model.fit_info.get(c, {}))
        lines.append(f"{name}: hue sector {b.lo[0]:.0f}-{b.hi[0]:.0f} (shifted; unshifted {info.get('hue_unshifted', '?')}), S >= {b.lo[1]:.0f}")
    (OUT / "summary.md").write_text("# hs candidate fit\n\n" + "\n".join(f"- {l}" for l in lines) + "\n")
    print("\n".join(lines)); print(f"wrote {OUT}/config.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
