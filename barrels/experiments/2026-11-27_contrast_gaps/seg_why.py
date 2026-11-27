"""Tanush's question: "on the warm bathroom tile there's no blue, on the ottoman the orange is specks. Why?"

For three frames: the photo, what the fixed colors paint, what the contrast stage paints on top, and a map of WHY each
pixel of a barrel's body and stripe is not painted by the fixed colors: the first gate it fails, in the order the color
step asks them (brightness V >= 40, the hue range, the saturation floor). Per barrel, the body (the wall above the
stripe) and the stripe (from the geometry of the hand box's bottom row): median H, S, V against the thresholds, and
the share of the pixels stopped at each gate. Pictures in ``results/2026-11-27_contrast_gaps/seg_why/`` (not
committed); the table in ``seg_why.md``.

    python barrels/experiments/2026-11-27_contrast_gaps/seg_why.py [STEM ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dark  # noqa: E402  (regions: body and stripe rows from the hand box's bottom row)
import gaps as gp  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402

OUT = gp.BARRELS / "results" / "2026-11-27_contrast_gaps"
FRAMES = ("4A8B_lampwarm6_bathtile_core_01", "4A8B_lampcool6_ottoman_core_01", "4A8B_lampmid6_ottoman_close_01")
RANGE = {1: (3, 13, 140), 2: (103, 119, 113)}      # hue lo, hue hi, S floor (the adopted model)
V_GATE = 40
NAMES = {1: "orange", 2: "blue"}
REASON_BGR = {"painted": (0, 200, 0), "V": (60, 60, 255), "hue": (255, 0, 255), "S": (255, 255, 0)}


def why(frame, color: int) -> np.ndarray:
    """Per pixel, for a pixel that should be ``color``: 'painted' / 'V' / 'hue' / 'S' (the first gate it fails)."""
    hsv = cv2.cvtColor(np.ascontiguousarray(frame.bgr), cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    lo, hi, smin = RANGE[color]
    out = np.full(h.shape, "painted", object)
    out[s < smin] = "S"
    out[(h < lo) | (h > hi)] = "hue"
    out[v < V_GATE] = "V"
    return out, h, s, v


def main(stems) -> None:
    (OUT / "seg_why").mkdir(parents=True, exist_ok=True)
    lines = ["# Why the fixed colors miss parts of these barrels (Tanush's question)", "",
             "Fixed colors: orange hue 3-13 with S >= 140, blue hue 103-119 with S >= 113, and V (brightest channel) >= 40. Per barrel the body "
             "(the wall above the stripe) and the stripe, middle 60 % of the columns, rows from the geometry of the hand box's bottom row. "
             "'painted' = the fixed colors paint it its right color; then the share stopped first by V, by the hue range, by the saturation floor; "
             "'contrast' = the share the contrast stage paints its right color on top.", "",
             "| frame | barrel | part | should be | median H | median S | median V | painted | stopped by V | by hue | by S | contrast paints |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for stem in stems:
        f = jg.load_frame(stem)
        tr = gp.Trace()
        gp.detect(f, gp.Gaps(), tr)
        gts, _ = ct.load_gts([stem])
        reason_img = f.bgr.copy() // 3
        for k, g in enumerate(gts.get(stem, [])):
            reg = dark.regions(g.bbox)
            if reg is None:
                continue
            (cx0, cx1), srows, urows = reg
            for part, rows, col in (("body", urows, g.color), ("stripe", srows, 3 - g.color)):
                r0, r1 = max(0, rows[0]), min(480, rows[1])
                if r1 <= r0:
                    continue
                rs, h, s, v = why(f, col)
                sub = rs[r0:r1, cx0:cx1]
                fixed = tr.base_mask[r0:r1, cx0:cx1]
                painted = tr.painted[r0:r1, cx0:cx1]
                n = sub.size
                ok = fixed == col
                rsn = np.where(ok, "painted", np.where(sub == "painted", "hue", sub))   # in range but cleaned away: count with hue
                share = {k2: float((rsn == k2).sum()) / n for k2 in ("painted", "V", "hue", "S")}
                cpaint = float(((painted == col) & ~ok).sum()) / n
                hh = (h[r0:r1, cx0:cx1] + (10 if col == 1 else 0)) % 180 - (10 if col == 1 else 0)
                lines.append(f"| {stem[5:]} | {k} {NAMES[g.color]} {g.bbox} | {part} | {NAMES[col]} | {np.median(hh):.0f} | {np.median(s[r0:r1, cx0:cx1]):.0f} | "
                             f"{np.median(v[r0:r1, cx0:cx1]):.0f} | {share['painted']:.2f} | {share['V']:.2f} | {share['hue']:.2f} | {share['S']:.2f} | {cpaint:.2f} |")
                for k2, bgr in REASON_BGR.items():
                    m = np.zeros(rs.shape, bool)
                    m[r0:r1, cx0:cx1] = rsn == k2
                    reason_img[m] = bgr
            x0, y0, x1, y1 = g.bbox
            cv2.rectangle(reason_img, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        seg = np.zeros_like(f.bgr)
        seg[tr.base_mask == 1] = (0, 140, 255)
        seg[tr.base_mask == 2] = (255, 90, 0)
        cseg = seg.copy()
        add = tr.painted != tr.base_mask
        cseg[add & (tr.painted == 1)] = (0, 255, 255)
        cseg[add & (tr.painted == 2)] = (255, 255, 0)
        for img, title in ((seg, "fixed colors"), (cseg, "+ contrast paint (yellow = orange, cyan = blue)"),
                           (reason_img, "why not painted: red V<40, magenta hue, cyan S, green painted")):
            cv2.putText(img, title, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        photo = f.bgr.copy()
        for g in gts.get(stem, []):
            cv2.rectangle(photo, g.bbox[:2], (g.bbox[2] - 1, g.bbox[3] - 1), (0, 200, 0), 1)
        pic = np.vstack([np.hstack([photo, seg]), np.hstack([cseg, reason_img])])
        cv2.imwrite(str(OUT / "seg_why" / f"{stem}.jpg"), pic, [cv2.IMWRITE_JPEG_QUALITY, 88])
    (OUT / "seg_why.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:] or FRAMES)
