#!/usr/bin/env python3
"""PREREG rule 3: on the unlabeled recordings, which boxes appear or disappear against `base` (today's defaults)
for each arm. The 2026-11-18 script is loaded by path and run with this experiment's arms and output folder.

    python barrels/experiments/2026-11-19_det_side/recordings.py --rec <path to data/recordings> --arms side
Outputs: results/2026-11-19_det_side/recordings.csv, recordings.md, recordings_by_clip.md; sheets/rec_<arm>/ (ignored).
"""
from __future__ import annotations

import collections
import csv
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE.parent / "2026-11-18_det_given_seg"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location("det_given_seg_recordings", PREV / "recordings.py")
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
import side_arms  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-19_det_side"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--arms" not in argv:
        argv += ["--arms", ",".join(a for a in side_arms.ARMS if a != "base")]
    out = OUT
    if "--out" in argv:                                   # a sub-folder of the results folder (round2a, ...)
        i = argv.index("--out")
        out = OUT / argv[i + 1]
        del argv[i:i + 2]
    out.mkdir(parents=True, exist_ok=True)
    M.ARMS, M.OUT = side_arms.ARMS, out
    rc = M.main(argv)
    if rc:
        return rc
    rows = list(csv.DictReader((out / "recordings.csv").open()))
    n = collections.Counter((r["arm"], r["frame"].rsplit("/", 1)[0], r["what"]) for r in rows)
    clips = sorted({k[1] for k in n})
    L = ["# Recordings, per clip: boxes appearing / disappearing against `base`", "",
         "| arm | " + " | ".join(clips) + " |", "|---|" + "---|" * len(clips)]
    for a in sorted({k[0] for k in n}):
        L.append(f"| {a} | " + " | ".join(f"+{n[(a, c, 'added')]} / -{n[(a, c, 'removed')]}" for c in clips) + " |")
    (out / "recordings_by_clip.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
