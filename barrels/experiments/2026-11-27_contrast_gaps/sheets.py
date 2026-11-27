"""Contact sheets of one judged family (default ALL): every barrel gained, every barrel lost, every frame whose boxes
not on their barrel changed. Each tile: the photo around the barrel / the frame's changed boxes, today's boxes thin
white, the candidate's boxes thick in their color, the hand box green. The candidate of a frame is the setting its
fold picked (``judge_<name>/chosen.json``, by place). Pictures in ``results/2026-11-27_contrast_gaps/sheets/``
(not committed).

    python barrels/experiments/2026-11-27_contrast_gaps/sheets.py [NAME | NAME_insample]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gaps as gp  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402

OUT = gp.BARRELS / "results" / "2026-11-27_contrast_gaps"
KEYS = {"e": "edge", "h": "half", "s": "split", "b": "beside", "o": "other"}


def setting(key: str) -> gp.Gaps:
    kw = {}
    for part in key.split("|"):
        if part[1:] != "-":
            kw[KEYS[part[0]]] = float(part[1:])
    return gp.Gaps(**kw)


def tile(stem, focus, g, title):
    f = jg.load_frame(stem)
    img = f.bgr.copy()
    gts, _ = ct.load_gts([stem])
    for x in gts.get(stem, []):
        cv2.rectangle(img, x.bbox[:2], (x.bbox[2] - 1, x.bbox[3] - 1), (0, 200, 0), 1)
    for b in gp.detect(f, gp.Gaps()):
        cv2.rectangle(img, b.bbox[:2], (b.bbox[2] - 1, b.bbox[3] - 1), (255, 255, 255), 1)
    for b in gp.detect(f, g):
        cv2.rectangle(img, b.bbox[:2], (b.bbox[2] - 1, b.bbox[3] - 1), (0, 140, 255) if b.color == 1 else (255, 90, 0), 2)
    x0, y0, x1, y1 = focus
    pad = 50
    crop = img[max(0, y0 - pad):min(480, y1 + pad), max(0, x0 - pad):min(640, x1 + pad)]
    crop = cv2.resize(crop, (300, int(300 * crop.shape[0] / max(1, crop.shape[1]))))
    crop = crop[:300] if crop.shape[0] > 300 else np.vstack([crop, np.zeros((300 - crop.shape[0], 300, 3), np.uint8)])
    cv2.putText(crop, title[:44], (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
    return crop


def sheet(tiles, path):
    if not tiles:
        return
    cols = 4
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(str(path), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])


def main(name="ALL"):
    insample = name.endswith("_insample")
    src = OUT / ("rows_insample.json" if insample else "rows.json")
    rows = {r["name"]: r for r in json.loads(src.read_text())["rows"]}
    r = rows[name.removesuffix("_insample")]
    chosen = {} if insample else r["chosen"]
    best = r["key"] if insample else json.loads((OUT / "rows.json").read_text())["best_in_sample"]

    def g_of(stem):
        c = chosen.get(ct.place_of(stem))
        return setting(c["key"]) if c else setting(best)
    (OUT / "sheets").mkdir(parents=True, exist_ok=True)
    sheet([tile(s, tuple(b), g_of(s), f"GAINED {s[5:]}") for s, b, _ in r["gained_list"]], OUT / "sheets" / f"{name}_gained.jpg")
    sheet([tile(s, tuple(b), g_of(s), f"LOST {s[5:]}") for s, b, _ in r["lost_list"]], OUT / "sheets" / f"{name}_lost.jpg")
    tl = []
    for x in r["box_changes"]:
        boxes = [tuple(b) for _, b in x["boxes_after"]] or [(0, 0, 640, 480)]
        fx = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        tl.append(tile(x["stem"], fx, g_of(x["stem"]), f"BOXES {x['before']}->{x['after']} {x['stem'][5:]}"))
    sheet(tl, OUT / "sheets" / f"{name}_boxes.jpg")
    print(f"{name}: {len(r['gained_list'])} gained, {len(r['lost_list'])} lost, {len(r['box_changes'])} frames with changed boxes -> {OUT / 'sheets'}")


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["ALL"]))
