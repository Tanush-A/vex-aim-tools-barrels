#!/usr/bin/env python3
"""Copy hand-drawn box labels from one light of a fixed-scene session to the other lights of the same scene.

For sessions where the robot and the scene stay put while only the light changes (the wood lamp ladder,
2026-11-16): box each scene once under one light with box_tool.py, then

    python barrels/tools/copy_boxes.py --from-light lampmid6 --surface wood --dry-run
    python barrels/tools/copy_boxes.py --from-light lampmid6 --surface wood   # for real

writes <stem>_boxes.json for every other lamp{warm,mid,cool}N light that has the same {scene}_{nn} frame.
The copies carry the target image's own sha1 and reviewed=false, so they still have to be checked in
box_tool.py. Existing label files are never overwritten without --overwrite. --shift LIGHT:DX,DY moves
the boxes for one light (the robot was nudged). The boxes are the labeler's; nothing here runs the detector.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import io  # noqa: E402

# only the lamp-ladder tags: older wood frames (upcool, atmid, ...) reuse scene names for other scenes
LADDER_RE = re.compile(r"^lamp(warm|mid|cool)\d$")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-light", required=True)
    ap.add_argument("--surface", required=True)
    ap.add_argument("--robot", default="4A8B")
    ap.add_argument("--scene", default=None, help="only this scene, e.g. occl_02 (default: every labeled scene)")
    ap.add_argument("--to-lights", default=None,
                    help="comma-separated (default: every other lamp{warm,mid,cool}N light on this surface)")
    ap.add_argument("--shift", action="append", default=[], metavar="LIGHT:DX,DY")
    ap.add_argument("--raw-dir", type=Path, default=io.RAW_DIR)
    ap.add_argument("--labels-dir", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    shifts = {}
    for s in args.shift:
        light, d = s.split(":")
        shifts[light] = tuple(int(v) for v in d.split(","))

    src_prefix = f"{args.robot}_{args.from_light}_{args.surface}_"
    sources = sorted(p for p in args.raw_dir.glob(src_prefix + "*.png")
                     if io.boxes_path(p, args.labels_dir).exists()
                     and (args.scene is None or p.stem == src_prefix + args.scene))
    if not sources:
        print(f"no labeled frames match {src_prefix}{args.scene or '*'}")
        return 1
    if args.to_lights:
        lights = [t.strip() for t in args.to_lights.split(",") if t.strip()]
    else:
        lights = sorted({io.parse_name(p.stem)["light"] for p in args.raw_dir.glob(f"{args.robot}_*_{args.surface}_*.png")
                         if p.stem.count("_") == 4} - {args.from_light})
        lights = [t for t in lights if LADDER_RE.match(t)]

    wrote = skipped = 0
    for src in sources:
        meta = io.load_boxes(src, args.labels_dir, raw_dir=args.raw_dir)
        if not meta.get("reviewed"):
            print(f"SKIP {src.stem}: source label is not reviewed")
            skipped += 1
            continue
        scene = src.stem[len(src_prefix):]
        for light in lights:
            dst_img = args.raw_dir / f"{args.robot}_{light}_{args.surface}_{scene}.png"
            if not dst_img.exists():
                continue
            dst = io.boxes_path(dst_img, args.labels_dir)
            if dst.exists() and not args.overwrite:
                print(f"keep {dst.name} (exists)")
                skipped += 1
                continue
            dx, dy = shifts.get(light, (0, 0))
            barrels = []
            for b in meta["barrels"]:
                x0, y0, x1, y1 = b["bbox"]
                bb = [min(max(x0 + dx, 0), io.FRAME_W), min(max(y0 + dy, 0), io.FRAME_H),
                      min(max(x1 + dx, 0), io.FRAME_W), min(max(y1 + dy, 0), io.FRAME_H)]
                barrels.append({"color": b["color"], "bbox": bb, "flags": list(b.get("flags", ())),
                                "note": f"copied from {args.from_light}" + (f" shifted {dx:+d},{dy:+d}" if (dx or dy) else "")})
            out = {"image_sha1": io.file_sha1(dst_img), "reviewed": False, "clean": meta.get("clean", True),
                   "source": meta.get("source", "manual"), "barrels": barrels}
            io.validate_boxes(out)
            shifted = f", shift {dx:+d},{dy:+d}" if (dx or dy) else ""
            print(f"{'would write' if args.dry_run else 'write'} {dst.name}  ({len(barrels)} boxes{shifted})")
            if not args.dry_run:
                io.save_boxes(dst_img, out, args.labels_dir)
            wrote += 1
    print(f"{'would write' if args.dry_run else 'wrote'} {wrote}, skipped {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
