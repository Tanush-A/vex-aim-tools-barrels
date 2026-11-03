#!/usr/bin/env python3
"""Import Dave's barrels.zip (2026-09-28): 20 snapshots from his robot in his office, 12 of them with his
ground-truth boxes drawn in a separate <snap>_ground_truth.png (yellow = orange barrel, green = blue barrel).

    python barrels/tools/import_dave_zip.py ~/Downloads/barrels.zip [--dry-run]

Copies snapNN.png -> data/raw/DAVE_office_<speckle|dark>_snap_NN.png (snap00-11: the speckled gray desk;
snap12-19: the dark table) and recovers each drawn box as the pixels that differ between the ground-truth
image and the raw snapshot -> data/labels/<stem>_boxes.json (source "dave_gt", reviewed). Dave's own
notes (the zip's CLAUDE.md) are copied to docs/DAVE-barrels-zip-notes.md. Nothing is assigned to a split:
these frames are an outside check, never tuned on (DATA.md).
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import io  # noqa: E402

SURFACE = {i: ("speckle" if i < 12 else "dark") for i in range(20)}


def stem_for(i: int) -> str:
    return f"DAVE_office_{SURFACE[i]}_snap_{i:02d}"


def drawn_boxes(raw: np.ndarray, gt: np.ndarray) -> list[dict]:
    """Rectangles Dave drew = pixels that differ between the two images; color of the line gives the class."""
    diff = (np.abs(raw.astype(int) - gt.astype(int)).sum(axis=2) > 30).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(diff, connectivity=8)
    out = []
    for k in range(1, n):
        x, y, w, h, a = (int(v) for v in st[k])
        if a < 30:
            continue
        b, g, r = np.median(gt[lab == k].reshape(-1, 3), axis=0)
        color = "orange" if r > 150 else "blue"              # yellow line -> orange barrel, green line -> blue barrel
        bbox = [x, y, min(x + w, io.FRAME_W), min(y + h, io.FRAME_H)]
        out.append({"id": len(out) + 1, "color": color, "bbox": bbox,
                    "flags": ["truncated"] if io.touches_frame(bbox) else [], "note": f"line BGR ({int(b)},{int(g)},{int(r)})"})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zip", type=Path)
    ap.add_argument("--raw", type=Path, default=io.RAW_DIR)
    ap.add_argument("--labels", type=Path, default=io.LABELS_DIR)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(args.zip) as z:
            z.extractall(td)
        snaps = Path(td) / "barrels" / "snapshots"
        notes = Path(td) / "barrels" / "CLAUDE.md"
        n_img = n_gt = 0
        for i in range(20):
            src = snaps / f"snap{i:02d}.png"
            if not src.exists():
                print(f"missing {src.name}"); continue
            stem = stem_for(i)
            dst = args.raw / f"{stem}.png"
            gt_png = snaps / f"snap{i:02d}_ground_truth.png"
            boxes = None
            if gt_png.exists():
                boxes = drawn_boxes(cv2.imread(str(src)), cv2.imread(str(gt_png)))
            print(f"{src.name} -> {dst.name}" + (f"  {len(boxes)} box(es): " + ", ".join(f"{b['color'][0]}{b['bbox']}" for b in boxes) if boxes is not None else "  (no ground truth)"))
            if args.dry_run:
                continue
            args.raw.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst); n_img += 1
            if boxes is not None:
                meta = {"image_sha1": io.file_sha1(dst), "reviewed": True, "clean": False, "source": "dave_gt",
                        "note": "boxes recovered from Dave's snapNN_ground_truth.png (2026-09-28); clean unknown (office clutter)",
                        "barrels": boxes}
                io.save_boxes(stem, meta, args.labels); n_gt += 1
        if not args.dry_run and notes.exists():
            out = io.PKG_ROOT / "docs" / "DAVE-barrels-zip-notes.md"
            out.write_text("<!-- Dave's CLAUDE.md from barrels.zip (2026-09-28), copied verbatim 2026-11-03. Reference only. -->\n\n" + notes.read_text())
            print(f"notes -> {out.relative_to(io.PKG_ROOT)}")
        print(f"{n_img} images, {n_gt} box files" + (" (dry run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
