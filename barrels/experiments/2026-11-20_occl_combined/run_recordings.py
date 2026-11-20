#!/usr/bin/env python3
"""On the unlabeled recordings (read, never written): which boxes each arm draws that a reference arm does not, and
the reverse. The script of ``2026-11-18_det_given_seg`` is loaded by path and run with this experiment's arms, once
against ``before`` and once against ``stack``. Every changed frame goes on a contact sheet (an appearing box ringed in
red, a disappearing one in magenta); the verdict is written by hand into ``by_eye.md``.

    python barrels/experiments/2026-11-20_occl_combined/run_recordings.py --rec <path to data/recordings> [--arms combined] [--against before,stack]
Outputs: results/2026-11-20_occl_combined/rec_vs_<reference>/ recordings.csv, recordings.md, recordings_by_clip.md;
sheets/rec_<arm>/ there (ignored).
"""
from __future__ import annotations

import argparse
import collections
import csv

import common as C

A = C.A


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rec", required=True)
    ap.add_argument("--arms", default="")
    ap.add_argument("--against", default="before,stack")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    arms = C.arm_list(args.arms, C.RULE_ARMS)
    M = C.load("det_given_seg_recordings", C.SEG / "recordings.py")
    A.install()
    for ref in [r for r in args.against.split(",") if r]:
        out = (C.OUT / args.out if args.out else C.OUT) / f"rec_vs_{ref}"
        out.mkdir(parents=True, exist_ok=True)
        cand = [a for a in arms if a != ref]
        M.ARMS, M.OUT = {"base": A.ARMS[ref], **{a: A.ARMS[a] for a in cand}}, out
        rc = M.main(["--rec", args.rec, "--arms", ",".join(cand)])
        if rc:
            return rc
        rows = list(csv.DictReader((out / "recordings.csv").open()))
        n = collections.Counter((r["arm"], r["frame"].rsplit("/", 1)[0], r["what"]) for r in rows)
        clips = sorted({k[1] for k in n})
        L = [f"# Recordings, per clip: boxes appearing / disappearing against `{ref}` (called `base` in recordings.md)", "",
             "| arm | " + " | ".join(clips) + " |", "|---|" + "---|" * len(clips)]
        for a in cand:
            L.append(f"| {a} | " + " | ".join(f"+{n[(a, c, 'added')]} / -{n[(a, c, 'removed')]}" for c in clips) + " |")
        (out / "recordings_by_clip.md").write_text("\n".join(L) + "\n")
        print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
