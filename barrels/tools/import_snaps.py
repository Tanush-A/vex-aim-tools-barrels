#!/usr/bin/env python3
"""Rename robot_snapN.png files into the DATA.md naming convention and move them to data/raw.

You shoot in a planned order, then pass that order as --scenes. Snapshots are taken in
numeric order (robot_snap0, robot_snap1, ...) and paired with the scenes list; the
two-digit counter per (robot, light, surface, scene) continues from what is already
in data/raw.

    python barrels/tools/import_snaps.py --light overhead --surface black \
        --scenes core,core,core,core,far,far,close,close --dry-run
    python barrels/tools/import_snaps.py --light overhead --surface black --scenes ...   # for real

Refuses to run if the number of snapshots and scenes differ.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import io  # noqa: E402

SNAP_RE = re.compile(r"^robot_snap(\d+)\.png$")


def next_counter(raw_dir: Path, prefix: str) -> int:
    n = 0
    for p in raw_dir.glob(f"{prefix}_*.png"):
        m = re.match(rf"^{re.escape(prefix)}_(\d{{2}})$", p.stem)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=Path("snapshots"), help="folder with robot_snapN.png (default ./snapshots)")
    ap.add_argument("--dst", type=Path, default=io.RAW_DIR, help="destination (default barrels/data/raw)")
    ap.add_argument("--robot", default="4A8B")
    ap.add_argument("--light", required=True)
    ap.add_argument("--surface", required=True)
    ap.add_argument("--scenes", required=True, help="comma-separated scene tags in shooting order")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    snaps = sorted(
        (p for p in args.src.iterdir() if SNAP_RE.match(p.name)),
        key=lambda p: int(SNAP_RE.match(p.name).group(1)),
    )
    scenes = [s.strip() for s in args.scenes.split(",") if s.strip()]
    if len(snaps) != len(scenes):
        print(f"ERROR: {len(snaps)} snapshots in {args.src} but {len(scenes)} scenes given")
        for p in snaps:
            print("  ", p.name)
        return 1
    for tag in (args.robot, args.light, args.surface, *scenes):
        if "_" in tag or not tag:
            print(f"ERROR: tag {tag!r} must be non-empty and contain no underscore")
            return 1

    counters: dict[str, int] = {}
    plan = []
    for p, scene in zip(snaps, scenes):
        prefix = f"{args.robot}_{args.light}_{args.surface}_{scene}"
        if prefix not in counters:
            counters[prefix] = next_counter(args.dst, prefix)
        new = args.dst / f"{prefix}_{counters[prefix]:02d}.png"
        counters[prefix] += 1
        plan.append((p, new))

    for src, dst in plan:
        print(f"{src.name:>20}  ->  {dst.relative_to(dst.parents[2]) if dst.is_relative_to(dst.parents[2]) else dst}")
    if args.dry_run:
        print("(dry run, nothing moved)")
        return 0
    args.dst.mkdir(parents=True, exist_ok=True)
    for src, dst in plan:
        if dst.exists():
            print(f"ERROR: {dst} exists, aborting before moving anything else")
            return 1
        shutil.move(str(src), str(dst))
    print(f"moved {len(plan)} files to {args.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
