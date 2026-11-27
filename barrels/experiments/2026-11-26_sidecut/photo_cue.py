#!/usr/bin/env python3
"""Analysis (P) of the side-cut experiment (PREREG.md): the photo at the cut. NOT a rule; nothing in the detector reads it.

In the mask a thing that hides a barrel looks like bare table. In the photo it does not. For every labelled barrel of
the train frames that has a stripe in the mask, and for each of its two sides:

    D = the largest difference, over blue, green and red, between
        the median color of the strip just beside the seen end (max(3, 12 % of W) columns, the stripe's rows) and
        the median color of the table just below the barrel (as many rows under the seen bottom, the seen columns).

A side is "hidden by a thing" when the label is flagged occluded, the seen end is more than 15 % of W inside the
label's box on that side, no other barrel's box covers the hidden part, and the box does not touch the frame there.
A side of a barrel with no flag is "free". Reported: the two distributions, per place, and how many free sides lie at
or above the smallest D of a hidden side. No threshold is set.

    python barrels/experiments/2026-11-26_sidecut/photo_cue.py

Train frames only; the photo is read through ``judge.load_frame`` (read-only arrays). Writes
results/2026-11-26_sidecut/photo_cue.md and photo_cue.csv.
"""
from __future__ import annotations

import csv

import numpy as np

import lib
from lib import dtp, io, jg, pl
from barrels import conditions as cnd, counting as ct

STRIP = 0.12
INSIDE = 0.15


def diff(a: np.ndarray, b: np.ndarray) -> float | None:
    if a.size == 0 or b.size == 0:
        return None
    return float(np.max(np.abs(np.median(a.reshape(-1, 3), axis=0) - np.median(b.reshape(-1, 3), axis=0))))


def main() -> int:
    stems = lib.train_stems()
    rows, skipped = [], {"no stripe": 0, "bottom not seen": 0}
    for stem in stems:
        frame = jg.load_frame(stem)
        mask = pl.segment(frame, lib.model())[0]
        bgr = frame.bgr
        gts = dtp.barrels_from_boxes(io.load_boxes(stem))
        ms = lib.measure(mask)
        cond = ct.condition_of(stem)
        for gi, g in enumerate(gts):
            x0, y0, x1, y1 = g.bbox
            mine = [m for m in ms if m["stripe"].body == g.color and x0 <= (m["stripe"].bbox[0] + m["stripe"].bbox[2]) / 2 < x1
                    and y0 <= m["stripe"].center_row < y1]
            if not mine:
                skipped["no stripe"] += 1; continue
            m = max(mine, key=lambda m: m["stripe"].bbox[2] - m["stripe"].bbox[0])
            if "bottom_inferred" in m["inferred"]:
                skipped["bottom not seen"] += 1; continue
            s, W = m["stripe"], m["W"]
            sx0, sx1, bottom = m["sx0"], m["sx1"], m["bottom"]
            n = max(3, int(round(STRIP * W)))
            sy0, sy1 = s.bbox[1], s.bbox[3]
            table = bgr[bottom + 2:bottom + 2 + (sy1 - sy0), sx0:sx1]
            others = [o.bbox for j, o in enumerate(gts) if j != gi]
            for side in ("left", "right"):
                beside = bgr[sy0:sy1, max(0, sx0 - n):sx0] if side == "left" else bgr[sy0:sy1, sx1:min(640, sx1 + n)]
                d = diff(beside.astype(float), table.astype(float))
                if d is None:
                    continue
                gap = (sx0 - x0) if side == "left" else (x1 - sx1)                  # how far the seen end is inside the label's box
                hx0, hx1 = (x0, sx0) if side == "left" else (sx1, x1)                # the hidden part
                barrel_there = any(min(hx1, o[2]) > max(hx0, o[0]) and min(y1, o[3]) > max(y0, o[1]) for o in others)
                at_frame = x0 <= 0 if side == "left" else x1 >= 640
                bx0, bx1 = (sx0 - n, sx0) if side == "left" else (sx1, sx1 + n)      # the strip beside
                barrel_beside = any(min(bx1, o[2]) > max(bx0, o[0]) and min(sy1, o[3]) > max(sy0, o[1]) for o in others)
                if "occluded" in g.flags and gap > INSIDE * g.width and not barrel_there and not at_frame:
                    kind = "hidden by a thing"
                elif not g.flags:
                    kind = "free"
                else:
                    kind = "other"                                                # the free side of a flagged barrel, a barrel in front, the frame
                rows.append({"frame": stem, "place": cnd.info(cond).place, "class": cnd.info(cond).klass, "barrel": dtp.COLOR_NAMES[g.color], "truth": list(g.bbox),
                             "flags": "+".join(sorted(g.flags)), "side": side, "kind": kind, "D": round(d, 1), "seen": [sx0, sx1], "W": round(W, 1),
                             "barrel_beside": int(barrel_beside)})
    out = lib.OUT
    with (out / "photo_cue.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    hid = [r for r in rows if r["kind"] == "hidden by a thing"]
    free = [r for r in rows if r["kind"] == "free"]
    free_clear = [r for r in free if not r["barrel_beside"]]
    low = min(r["D"] for r in hid) if hid else float("nan")

    def stats(rs):
        v = np.array([r["D"] for r in rs])
        return "-" if not len(v) else f"{len(v)} | {np.median(v):.0f} | {np.percentile(v, 90):.0f} | {np.percentile(v, 99):.0f} | {v.max():.0f} | {int((v >= low).sum())}"
    L = ["# The photo at the cut (analysis P; not a rule)", "",
         f"{len(stems)} labelled train frames. D = the largest difference over blue, green and red (0 to 255) between the strip just beside a barrel's seen end and the "
         f"table just below the barrel. Left out: {skipped['no stripe']} barrels with no stripe in the mask, {skipped['bottom not seen']} whose bottom is not seen.", "",
         f"## The sides hidden by a thing that is not a barrel: {len(hid)}", "", "| frame | barrel | side | D |", "|---|---|---|---|"]
    L += [f"| {r['frame'].replace('4A8B_', '')} | {r['barrel']} {r['truth']} | {r['side']} | {r['D']:.0f} |" for r in hid]
    L += ["", f"The smallest D of a hidden side: **{low:.0f}**.", "", "## The free sides (barrels with no flag), by place", "",
          f"| place | sides | median D | 90 % | 99 % | max | at or above {low:.0f} |", "|---|---|---|---|---|---|---|"]
    for place in sorted({r["place"] for r in free}):
        L.append(f"| {place} | " + stats([r for r in free if r["place"] == place]) + " |")
    L.append("| **all places** | " + stats(free) + " |")
    L.append("| all places, no other barrel beside | " + stats(free_clear) + " |")
    L.append("| ordinary places only | " + stats([r for r in free if r["class"] == cnd.ORDINARY]) + " |")
    L.append("| ordinary places, no other barrel beside | " + stats([r for r in free_clear if r["class"] == cnd.ORDINARY]) + " |")
    oth = [r for r in rows if r["kind"] == "other" and "occluded" in r["flags"]]
    L += ["", f"## The other sides of the flagged barrels: {len(oth)} (the free side of a hidden barrel, a barrel in front, the frame)", "",
          "| frame | barrel | flags | side | D | another barrel beside |", "|---|---|---|---|---|---|"]
    L += [f"| {r['frame'].replace('4A8B_', '')} | {r['barrel']} {r['truth']} | {r['flags']} | {r['side']} | {r['D']:.0f} | {'yes' if r['barrel_beside'] else ''} |"
          for r in oth if "occlx" in r["frame"]]
    (out / "photo_cue.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
