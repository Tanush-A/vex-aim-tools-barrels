#!/usr/bin/env python3
"""Assign every labeled image in data/raw to train/dev/test (append-only, seeded).

    python barrels/tools/make_splits.py            # assigns unassigned labeled images
    python barrels/tools/make_splits.py --show     # print current splits

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
    args = ap.parse_args(argv)

    current = sp.load_splits()
    if args.show:
        for s in sp.SPLIT_NAMES:
            print(f"{s} ({len(current[s])}):")
            for x in current[s]:
                print("  ", x)
        return 0
    labeled = [p.stem for p in io.list_images() if io.mask_path(p).exists()]
    before = {x for v in current.values() for x in v}
    new = sp.assign(labeled, current, seed=args.seed)
    path = sp.save_splits(new)
    added = [x for v in new.values() for x in v if x not in before]
    print(f"{len(added)} newly assigned, {sum(len(v) for v in new.values())} total -> {path}")
    for s in sp.SPLIT_NAMES:
        print(f"  {s}: {len(new[s])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
