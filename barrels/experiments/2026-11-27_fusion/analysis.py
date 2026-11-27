#!/usr/bin/env python3
"""After run.py: the held-out boxes of a candidate beside F0 and today, looked at closely.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_fusion/analysis.py F5 [--sheets]

Writes results/2026-11-27_fusion/analysis_<name>.md (and .json):
- every box not on its barrel (ordinary frames), by frame, with whether F0 draws a box there;
- every barrel gained or lost against F0;
- the extreme conditions (report only): wood desk, black table, very dark ottoman;
- the vendor comparison on the six places with vendor files (the accounting of ``report.py --vendor --places``).
With ``--sheets``: contact sheets in results/2026-11-27_fusion/sheets/ (not committed).
Train frames only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fuse  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import report as rp  # noqa: E402
from barrels import splits as splits_mod  # noqa: E402
from barrels.detect_types import COLOR_NAMES  # noqa: E402

OUT = fuse.OUT


def held_out_boxes(names, frames):
    F = fuse.fitter()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    out = {}
    for n in names:
        if n == "today":
            out[n] = {s: fuse.fu.barrels(fuse.today(fuse.record(s))) for s in stems}
            continue
        d = jg.leave_one_place_out(F.fit(n), frames[cnd.ORDINARY])
        out[n] = {s: d(s, None) for s in stems}
    return F, out


def table(head, rows):
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows] + [""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--sheets", action="store_true")
    a = ap.parse_args()
    frames = jg.train_frames()
    names = ["today", "F0", a.name]
    F, B = held_out_boxes(names, frames)
    truth = F.truth
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    C = {n: {s: ct.classify_frame(s, B[n][s], truth.gts[s], truth.clean[s]) for s in stems} for n in names}
    md = [f"# Fusion: `{a.name}` held out, beside F0 (contrast alone) and today", "",
          "Made by `analysis.py`. Every box is the held-out one (leave one place out). Train frames only.", ""]
    js: dict = {}

    # 1. boxes not on their barrel
    rows, jrows = [], []
    for s in frames[cnd.ORDINARY]:
        fc = C[a.name][s]
        for b, st in zip(B[a.name][s], fc.boxes):
            if st not in ct.EXTRA_STATES:
                continue
            by_f0 = any(o.color == b.color and ct.is_on(o, b) for o, st0 in zip(B["F0"][s], C["F0"][s].boxes) if st0 == st or st0 in ct.EXTRA_STATES)
            by_today = any(o.color == b.color and ct.is_on(o, b) for o in B["today"][s])
            rows.append([s, COLOR_NAMES[b.color], b.bbox, st, "yes" if by_f0 else "**no (new)**", "yes" if by_today else "no"])
            jrows.append({"stem": s, "color": COLOR_NAMES[b.color], "bbox": list(b.bbox), "state": st, "F0": by_f0, "today": by_today})
    gone = []
    for s in frames[cnd.ORDINARY]:
        for b, st in zip(B["F0"][s], C["F0"][s].boxes):
            if st in ct.EXTRA_STATES and not any(o.color == b.color and ct.is_on(o, b) for o in B[a.name][s]):
                gone.append([s, COLOR_NAMES[b.color], b.bbox, st])
    md += [f"## 1. Every box not on its barrel, `{a.name}` (ordinary frames, per frame: {len(rows)}; F0: "
           f"{sum(C['F0'][s].extra for s in frames[cnd.ORDINARY])})", ""]
    md += table(["frame", "color", "box", "kind", "F0 draws it", "today draws it"], rows)
    md += [f"F0's boxes not on their barrel that `{a.name}` does not draw: {len(gone)}", ""] + (table(["frame", "color", "box", "kind"], gone) if gone else [])
    js["false_boxes"] = jrows
    js["removed_from_F0"] = gone

    # 2. barrels gained / lost against F0
    ch = []
    for s in stems:
        for i, (x, y) in enumerate(zip(C["F0"][s].gt, C[a.name][s].gt)):
            if x != y:
                g = truth.gts[s][i]
                ch.append([s, i, COLOR_NAMES[g.color], tuple(g.bbox), x, y, "judged" if s in frames[cnd.ORDINARY] else "report only"])
    md += [f"## 2. Barrels whose state differs from F0 ({len(ch)})", ""] + table(["frame", "#", "color", "label box", "F0", a.name, ""], ch)
    js["changes_vs_F0"] = [dict(zip(["stem", "i", "color", "bbox", "F0", "cand", "kind"], r)) for r in ch]

    # 3. extreme conditions
    ex = frames[cnd.EXTREME]
    rows = []
    groups = list(ct.group_stems(ex, "condition").items())
    for cond, ss in groups + [("**all extreme**", ex)]:
        t = {n: ct.tally(C[n], ss, truth.placements) for n in names}
        rows.append([cond, f"{t['today'].barrels}"] + [f"{t[n].found} ({t[n].wrong + t[n].second + t[n].nothing})" for n in names])
    md += ["## 3. The extreme conditions (report only; found per frame, boxes not on their barrel in brackets)", ""]
    md += table(["condition", "barrels per frame"] + names, rows)
    by_place = {}
    for p, ss in ct.group_stems(ex, "place").items():
        by_place[p] = {n: ct.tally(C[n], ss, truth.placements) for n in names}
    md += table(["extreme frames by place", "placements (per frame)"] + names,
                [[p, f"{t['today'].placements} ({t['today'].barrels})"] + [f"{t[n].found_w:.1f} ({t[n].found}); {t[n].wrong + t[n].second + t[n].nothing} off" for n in names]
                 for p, t in by_place.items()])
    js["extreme"] = {p: {n: t[n].found for n in names} for p, t in by_place.items()}

    # 4. the vendor
    splits = splits_mod.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), splits)
    cov = rp.vendor_coverage(sel, splits)
    vs = [s for s in frames[cnd.ORDINARY] if s in cov.barrels]
    arms = {n: C[n] for n in names}
    arms["vendor"] = {s: ct.classify_frame(s, cov.barrels[s], truth.gts[s], truth.clean[s]) for s in vs}
    gr = list(ct.group_stems(vs, "place").items()) + [("**six places**", vs)]
    tal = {p: {n: ct.tally(arms[n], ss, truth.placements) for n in arms} for p, ss in gr}
    md += ["## 4. Against the vendor (the six places with vendor files; found per placement (per frame); boxes not on their barrel per arrangement)", "",
           "Train frames: our methods were shaped on them; the vendor's was not.", ""]
    md += table(["place", "placements (per frame)"] + list(arms),
                [[p, f"{t['today'].placements} ({t['today'].barrels})"] + [f"{t[n].found_w:.1f} ({t[n].found}); {t[n].extra_w:.2f}" for n in arms] for p, t in tal.items()])
    js["vendor"] = {p: {n: {"found_w": round(t[n].found_w, 2), "found": t[n].found, "extra_w": round(t[n].extra_w, 2)} for n in arms} for p, t in tal.items()}

    (OUT / f"analysis_{a.name}.md").write_text("\n".join(md) + "\n")
    (OUT / f"analysis_{a.name}.json").write_text(json.dumps(js, indent=1, default=list) + "\n")
    print("\n".join(md))
    if a.sheets:
        sheets(a.name, B, C, truth, frames)


def _crop(stem, boxes, label_boxes=(), pad=0.6):
    img = jg.load_frame(stem).bgr.copy()
    for g in label_boxes:
        cv2.rectangle(img, tuple(map(int, g[:2])), tuple(map(int, g[2:])), (0, 255, 0), 1)
    for b, col in boxes:
        cv2.rectangle(img, (int(b[0]), int(b[1])), (int(b[2]) - 1, int(b[3]) - 1), col, 2)
    x0 = min(b[0] for b, _ in boxes); y0 = min(b[1] for b, _ in boxes); x1 = max(b[2] for b, _ in boxes); y1 = max(b[3] for b, _ in boxes)
    w, h = x1 - x0, y1 - y0
    xa, ya = max(0, int(x0 - pad * w - 20)), max(0, int(y0 - pad * h - 20))
    xb, yb = min(img.shape[1], int(x1 + pad * w + 20)), min(img.shape[0], int(y1 + pad * h + 20))
    c = img[ya:yb, xa:xb]
    s = 200 / max(1, c.shape[0])
    return cv2.resize(c, (max(1, int(c.shape[1] * s)), 200))


def _sheet(tiles, path):
    if not tiles:
        return
    rows, cur, cw = [], [], 0
    for im, cap in tiles:
        im = cv2.copyMakeBorder(im, 0, 22, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        cv2.putText(im, cap[:60], (2, im.shape[0] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 1)
        if cw + im.shape[1] > 1600 and cur:
            rows.append(cur); cur, cw = [], 0
        cur.append(im); cw += im.shape[1]
    rows.append(cur)
    W = max(sum(i.shape[1] for i in r) for r in rows)
    out = np.full((sum(r[0].shape[0] for r in rows), W, 3), 255, np.uint8)
    y = 0
    for r in rows:
        x = 0
        for im in r:
            out[y:y + im.shape[0], x:x + im.shape[1]] = im; x += im.shape[1]
        y += r[0].shape[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), out)


def sheets(name, B, C, truth, frames):
    d = OUT / "sheets"
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME]
    red, cyan, gray = (0, 0, 255), (255, 255, 0), (160, 160, 160)
    fb, gained, lost = [], [], []
    for s in stems:
        for b, st in zip(B[name][s], C[name][s].boxes):
            if st in ct.EXTRA_STATES:
                new = not any(o.color == b.color and ct.is_on(o, b) for o in B["F0"][s])
                fb.append((_crop(s, [(b.bbox, red)]), f"{'NEW ' if new else ''}{st} {s[5:]}"))
        for i, (x, y) in enumerate(zip(C["F0"][s].gt, C[name][s].gt)):
            if x == y:
                continue
            g = truth.gts[s][i].bbox
            mine = [(o.bbox, cyan) for o in B[name][s] if on_any(o.bbox, g)] or [(g, gray)]
            tile = (_crop(s, mine, [g]), f"{x}->{y} {s[5:]}")
            (gained if y == ct.FOUND else lost).append(tile)
    _sheet(fb, d / f"{name}_false_boxes.png")
    _sheet(gained, d / f"{name}_gained_vs_F0.png")
    _sheet(lost, d / f"{name}_lost_vs_F0.png")
    print(f"sheets: {len(fb)} false, {len(gained)} gained, {len(lost)} lost -> {d}")


def on_any(a, g):
    return ct.on_share(a, tuple(g)) >= 0.5


if __name__ == "__main__":
    main()
