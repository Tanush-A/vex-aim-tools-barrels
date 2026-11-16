#!/usr/bin/env python3
"""Hue x saturation histogram pictures of a set of labeled frames (TODO step 8).

    python barrels/tools/hs_hist.py --filter lampwarm3_wood                 # one light of the wood ladder
    python barrels/tools/hs_hist.py --filter campus_light --bins 32 32
    python barrels/tools/hs_hist.py --filter _wood_ --scene core --out /tmp/x

Writes ``hist_<name>.png`` (counts in gray + each bin in its own color, for all pixels / orange bodies / blue
bodies / the rest; dashed boxes = what the fixed hs model accepts) and ``bars_<name>.png`` (the 3-D bar plot)
and prints where the body colors sit. Frames need hand-drawn boxes. Test frames are refused; geometry-only
frames (calib / ruler / horizon) are skipped. Code: ``src/barrels/hshist.py``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import hshist as hh, io, splits as sp, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402


def pick(filter_: str, scene: str = "") -> list[str]:
    test = set(sp.load_splits()["test"])
    out = []
    for p in io.list_images():
        s = p.stem
        if filter_ not in s or not io.boxes_path(s).exists():
            continue
        try:
            tags = io.parse_name(s)
        except ValueError:
            continue
        if tags["scene"] in sp.UNASSIGNED_SCENES or (scene and tags["scene"] != scene):
            continue
        if s in test:
            continue
        out.append(s)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--filter", required=True, help="frames whose name contains this")
    ap.add_argument("--scene", default="", help="only this scene tag")
    ap.add_argument("--bins", type=int, nargs=2, default=(16, 16), metavar=("HUE", "SAT"))
    ap.add_argument("--out", default="", help="folder for the pictures (default results/hs_hist_<filter>)")
    args = ap.parse_args(argv)
    stems = pick(args.filter, args.scene)
    if not stems:
        print("no labeled non-test frames match"); return 1
    model = wb.BarrelDetectorHook.load(wb.default_model_path()).model
    name = args.filter.strip("_") + (f"_{args.scene}" if args.scene else "")
    sh = hh.SetHist(name)
    for s in stems:
        sh.add(s, io.load_image(io.find_image(s)), io.load_boxes(s)["barrels"], model)
    out = Path(args.out) if args.out else io.PKG_ROOT / "results" / f"hs_hist_{name}"
    out.mkdir(parents=True, exist_ok=True)
    hh.figure_set(sh, model, out / f"hist_{name}.png", tuple(args.bins))
    hh.figure_bars(sh, out / f"bars_{name}.png", tuple(args.bins))
    print(f"{len(stems)} frames (test frames left out) -> {out}")
    for c in (ORANGE, BLUE):
        st = sh.stats(c)
        print(f"  {hh.NAMES[c]:6s} body: hue {st['h50']:.0f} ({st['h5']:.0f} to {st['h95']:.0f}), S {st['s50']:.0f} ({st['s5']:.0f} to {st['s95']:.0f}), "
              f"{st['n']:,} px, the fixed model labels {100 * st['pass']:.0f} % of it")
    r = sh.rest_stats()
    print(f"  not a barrel: hue {r['h50']:.0f}, S {r['s50']:.0f} (95th pct {r['s95']:.0f}); the model paints {100 * r['flood_orange']:.1f} % orange, {100 * r['flood_blue']:.1f} % blue")
    return 0


if __name__ == "__main__":
    sys.exit(main())
