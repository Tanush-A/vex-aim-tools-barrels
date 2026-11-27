"""Part C: judge every candidate of PREREG.md with the standard pass rule; write the summary and contact sheets.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_peaks/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import candidates as cd  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-27_peaks"
CANDS = [("P1", cd.fit_P1, None), ("P2", cd.fit_P2, None), ("P3", cd.fit_P3, None), ("P0", cd.fit_P0, None),
         ("P5", cd.fit_P5, None), ("S0", None, cd.detect_S0)]


def crop_sheet(items, path, title):
    """items: (stem, bbox to center on, [(bbox, color bgr)]) -> one tiled jpg."""
    tiles = []
    for stem, center, boxes in items[:60]:
        img = jg.load_frame(stem).bgr.copy()
        for b, col in boxes:
            x0, y0, x1, y1 = (int(v) for v in b)
            cv2.rectangle(img, (x0, y0), (x1, y1), col, 2)
        x0, y0, x1, y1 = (int(v) for v in center)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        half = max(60, int(1.2 * max(x1 - x0, y1 - y0)))
        a, b_ = max(0, cy - half), min(img.shape[0], cy + half)
        c, d = max(0, cx - half), min(img.shape[1], cx + half)
        t = cv2.resize(img[a:b_, c:d], (220, 220))
        cv2.putText(t, stem.replace("4A8B_", "")[:34], (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1)
        tiles.append(t)
    if not tiles:
        return
    cols = 6
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    sheet = np.vstack(rows)
    head = np.zeros((24, sheet.shape[1], 3), np.uint8)
    cv2.putText(head, title, (4, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.imwrite(str(path), np.vstack([head, sheet]), [cv2.IMWRITE_JPEG_QUALITY, 85])


def sheets(name, j):
    sd = OUT / "sheets"
    sd.mkdir(parents=True, exist_ok=True)
    W, G, R, Y = (255, 255, 255), (0, 220, 0), (0, 0, 255), (0, 255, 255)

    def boxes(stem):
        gt = [(g.bbox, W) for g in j.truth.gts[stem]]
        base = [(b.bbox, R) for b in j.baseline.boxes[stem]]
        cand = [(b.bbox, G) for b in j.candidate.boxes[stem]]
        return gt + base + cand
    for kind in ("gained", "lost"):
        ch = [c for c in j.changes if c.kind == kind]
        crop_sheet([(c.stem, c.bbox, boxes(c.stem)) for c in ch], sd / f"{name}_{kind}.jpg",
                   f"{name} {kind} ({len(ch)}): white = hand, red = fixed, green = candidate")
    items = []
    for bc in j.box_changes:
        for col, bb in bc["boxes_after"]:
            items.append((bc["stem"], bb, boxes(bc["stem"]) + [(bb, Y)]))
    crop_sheet(items, sd / f"{name}_extra_boxes.jpg", f"{name}: boxes not on their barrel, frames that changed (yellow)")


def row(name, j):
    b, c = j.total
    pl = []
    for p, (pb, pc) in j.places.items():
        if abs(pc.found_w - pb.found_w) > 1e-9:
            pl.append(f"{p} {pb.found_w:.1f} -> {pc.found_w:.1f}")
    return dict(cand=name, verdict=j.result, found_w=round(c.found_w, 2), base_found_w=round(b.found_w, 2),
                delta=round(c.found_w - b.found_w, 2), found=c.found, base_found=b.found,
                gained=sum(x.kind == "gained" and x.judged for x in j.changes),
                lost=sum(x.kind == "lost" and x.judged for x in j.changes),
                extra_w=round(c.extra_w, 2), base_extra_w=round(b.extra_w, 2), extra=c.wrong + c.second + c.nothing,
                base_extra=b.wrong + b.second + b.nothing, clean_empty=c.clean_empty, cluttered_empty_w=round(c.cluttered_empty_w, 2),
                base_cluttered_empty_w=round(b.cluttered_empty_w, 2), places=pl,
                report_only={k: (round(v[0].found_w, 1), round(v[1].found_w, 1), v[0].found, v[1].found) for k, v in j.report_only.items()})


def main(only=None):
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    summ = []
    for name, fit, det in CANDS:
        if only and name not in only:
            continue
        print("judging", name, flush=True)
        j = jg.judge(det, fit=fit, name=name, base_name="fixed", frames=frames, truth=truth,
                     out_dir=OUT / f"judge_{name}")
        r = row(name, j)
        summ.append(r)
        print(json.dumps(r), flush=True)
        sheets(name, j)
    chosen = {f"{k[0]} without {k[1]}": v["setting"] for k, v in cd.CHOSEN.items()}
    tables = {f"{k[0]} without {k[1]}": v["table"] for k, v in cd.CHOSEN.items() if isinstance(v["table"], list)}
    (OUT / "chosen.json").write_text(json.dumps({"chosen": chosen, "tables": tables}, indent=1, default=str))
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1))
    # thresholds used per frame
    with open(OUT / "thresholds.csv", "w") as fh:
        fh.write("cand,stem,place,o_lo,o_hi,o_s,b_lo,b_hi,b_s\n")
        for (c, s), th in sorted(cd.INFO.items()):
            fh.write(",".join([c, s, ct.place_of(s)] + [f"{x:.1f}" for x in th]) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
