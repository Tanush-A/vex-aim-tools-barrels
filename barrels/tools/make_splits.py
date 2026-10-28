#!/usr/bin/env python3
"""Assign every labeled image in data/raw to train/dev/test (append-only, seeded).

    python barrels/tools/make_splits.py            # assigns unassigned labeled images
    python barrels/tools/make_splits.py --show     # print current splits
    python barrels/tools/make_splits.py --test-only 5 --exclude-scenes top,topstripe
        # lock a test set (one labeled image per scene, largest scenes first) and put every
        # other labeled image in train; dev stays empty (tuning uses leave-one-scene-out CV,
        # see EVAL.md). Refuses if a test set already exists.

Only images that have a mask in data/labels are assigned, and once assigned a stem never
moves (docs/EVAL.md: the test set is fixed and never tuned on).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import io, splits as sp  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--test-only", type=int, metavar="N", help="lock N test images, rest -> train, dev empty")
    ap.add_argument("--exclude-scenes", default="", help="comma-separated scene tags never used for test")
    args = ap.parse_args(argv)

    current = sp.load_splits()
    if args.test_only:
        if current["test"]:
            print(f"refusing: a test set already exists ({len(current['test'])} images). It is fixed (EVAL.md).")
            return 1
        labeled = [p.stem for p in io.list_images() if io.mask_path(p).exists() and sp._scene(p.stem) not in sp.MEASURED_SCENES + sp.UNASSIGNED_SCENES]
        excl = tuple(x for x in args.exclude_scenes.split(",") if x)
        test = sp.pick_test(labeled, args.test_only, seed=args.seed, exclude_scenes=excl)
        new = {"train": sorted(set(labeled) - set(test)), "dev": [], "test": test, "measured": list(current.get("measured", []))}
        path = sp.save_splits(new)
        print(f"test ({len(test)}): {test}\ntrain ({len(new['train'])}), dev (0) -> {path}")
        return 0
    if args.show:
        for s in sp.SPLIT_NAMES:
            print(f"{s} ({len(current[s])}):")
            for x in current[s]:
                print("  ", x)
        return 0
    labeled = [p.stem for p in io.list_images() if io.mask_path(p).exists()]
    before = {x for v in current.values() for x in v}
    new = sp.assign(labeled, current, seed=args.seed)      # 'meas' frames go to the measured split, calib/ruler/horizon nowhere
    path = sp.save_splits(new)
    added = [x for v in new.values() for x in v if x not in before]
    print(f"{len(added)} newly assigned, {sum(len(v) for v in new.values())} total -> {path}")
    for s in sp.SPLIT_NAMES:
        print(f"  {s}: {len(new[s])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
