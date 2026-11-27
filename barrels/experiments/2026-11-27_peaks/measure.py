"""Parts A and B of the peaks experiment: where are the barrel peaks, and which finder picks them? Descriptive,
no detector, no fitted number. Train frames only (``judge.load_frame`` refuses anything else).

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_peaks/measure.py

Writes ``results/2026-11-27_peaks/measure.csv`` (one row per frame, color, finder) and ``measure.md``.

The barrels' true color in a frame, per color: the pixels in the inner 0.6 x 0.8 of every hand box of that color
that is not flagged occluded and not inside another box, in that color's hue region, S >= 40, V >= 40, row >= 50;
of those the ones within 12 hue units of their tallest hue (the body; drops the stripe and stray pixels).
Its "mode" is the tallest cell of their smoothed hue x S histogram; its "median" the median hue.

A finder's peak "is the barrel" when it lies within 3 hue units of the barrels' mode hue. "Fooled" when 5 or more
units away (the forensic review's line). Ranks: the place of the barrel's peak (the first local peak within 3 hue
units and 40 S units of the mode) among all the local peaks of the finder's histogram in that hue region.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import peaks as pk  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-27_peaks"
CORE = (0.6, 0.8)


def truth_masks(shape, gts):
    H, W = shape
    out = {ORANGE: np.zeros(shape, bool), BLUE: np.zeros(shape, bool)}
    inside = np.zeros(shape, bool)
    for b in gts:
        x0, y0, x1, y1 = b.bbox
        inside[max(0, y0 - 4):min(H, y1 + 4), max(0, x0 - 4):min(W, x1 + 4)] = True
    for i, b in enumerate(gts):
        if "occluded" in b.flags:
            continue
        x0, y0, x1, y1 = b.bbox
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        m = np.zeros(shape, bool)
        m[max(0, int(cy - h * CORE[1] / 2)):max(0, int(cy + h * CORE[1] / 2)),
          max(0, int(cx - w * CORE[0] / 2)):max(0, int(cx + w * CORE[0] / 2))] = True
        for j, o in enumerate(gts):
            if j != i:
                a0, b0, a1, b1 = o.bbox
                m[max(0, b0):max(0, b1), max(0, a0):max(0, a1)] = False
        out[b.color] |= m
    return out, inside


def truth_color(h, s, v, L, core, c):
    lo, hi = pk.REGION[c]
    sel = core & (h >= lo) & (h < hi) & (s >= 40) & (v >= pk.V_MIN)
    sel[:pk.GATE_ROW] = False
    if sel.sum() < 30:
        return None
    hh = np.bincount(h[sel], minlength=180)
    top = int(np.argmax(hh))
    body = sel & (np.abs(h - top) <= 12)
    hs = pk.smooth(pk.hist2d(h, s, body))
    i, j = np.unravel_index(np.argmax(hs), hs.shape)
    hb = h[body] - pk.ROLL
    return dict(mode_h=float(i - pk.ROLL), mode_s=float(j * pk.S_BIN + pk.S_BIN / 2), med_h=float(np.median(hb)),
                p10=float(np.percentile(hb, 10)), p90=float(np.percentile(hb, 90)), med_s=float(np.median(s[body])),
                med_L=float(np.median(L[body])), L10=float(np.percentile(L[body], 10)),
                L90=float(np.percentile(L[body], 90)), n=int(body.sum()), body=body)


def rank_of(peaks, t, dh=3, ds=40):
    for r, (_, hue, sv) in enumerate(peaks):
        if abs(hue - t["mode_h"]) <= dh and abs(sv - t["mode_s"]) <= ds:
            return r + 1
    return 0


def main():
    frames = jg.train_frames()
    stems = frames["ordinary"] + frames["extreme"]
    klass = {s: ("ordinary" if s in set(frames["ordinary"]) else "extreme") for s in stems}
    gts, _ = ct.load_gts(stems)
    rows = []
    for n_, stem in enumerate(stems):
        if not any(b.color in (ORANGE, BLUE) for b in gts[stem]):
            continue
        fr = jg.load_frame(stem)
        bgr = fr.bgr
        h, s, v, sel = pk.selections(bgr)
        L = pk.logrb(bgr)
        cores, inside = truth_masks(h.shape, gts[stem])
        g = pk.gate(h.shape) & (v >= pk.V_MIN)
        for c in (ORANGE, BLUE):
            t = truth_color(h, s, v, L, cores[c], c)
            if t is None:
                continue
            # purity: of the pixels near the barrels' mode (hue +-3, S +-32), the share inside a hand box
            near = g & (np.abs(h - pk.ROLL - t["mode_h"]) <= 3) & (np.abs(s - t["mode_s"]) <= 32)
            purity = float((near & inside).sum() / max(1, near.sum()))
            share = float(t["n"] / max(1, (g & (s >= 40)).sum()))
            base = dict(stem=stem, klass=klass[stem], place=ct.place_of(stem), cond=ct.condition_of(stem),
                        color=pk.NAMES[c], true_mode_h=t["mode_h"], true_mode_s=t["mode_s"], true_med_h=t["med_h"],
                        true_p10=t["p10"], true_p90=t["p90"], true_med_s=t["med_s"], true_L=t["med_L"],
                        n_body=t["n"], body_share=round(share, 4), purity=round(purity, 4))
            for f, d in sel.items():
                m, w = d[c]
                p = pk.peak_of(h, s, m, c, w)
                r = dict(base, finder=f)
                if p is None:
                    r.update(found_h="", found_s="", err="", rank=0, n_peaks=0, n_sel=0, second=0)
                else:
                    r.update(found_h=p.hue, found_s=p.s, err=p.hue - t["mode_h"], rank=rank_of(p.peaks, t),
                             n_peaks=len(p.peaks), n_sel=p.n_sel, second=round(p.second, 3))
                rows.append(r)
            # hue x V version of the naive histogram
            pv = pk.peak_of(h, v, g, c)
            hv = pk.smooth(pk.hist2d(h, v, t["body"]))
            i, j = np.unravel_index(np.argmax(hv), hv.shape)
            tv = dict(mode_h=float(i - pk.ROLL), mode_s=float(j * pk.S_BIN + pk.S_BIN / 2))
            r = dict(base, finder="F0_naive_hv")
            r.update(found_h=pv.hue if pv else "", found_s=pv.s if pv else "", err=(pv.hue - t["mode_h"]) if pv else "",
                     rank=rank_of(pv.peaks, tv) if pv else 0, n_peaks=len(pv.peaks) if pv else 0,
                     n_sel=pv.n_sel if pv else 0, second=0)
            rows.append(r)
            lp = pk.lrb_peak(L, g & (s >= 40), c)
            r = dict(base, finder="F4_logrb")
            inside_rng = lp is not None and t["L10"] <= lp <= t["L90"]
            r.update(found_h="", found_s="", err=(lp - t["med_L"]) if lp is not None else "", rank=1 if inside_rng else 0,
                     n_peaks="", n_sel="", second="")
            rows.append(r)
        if n_ % 20 == 0:
            print(n_, stem, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0].keys())
    with open(OUT / "measure.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, keys)
        wr.writeheader()
        wr.writerows(rows)
    write_md(rows)


def write_md(rows):
    L = ["# Peaks, parts A and B (descriptive; train frames only)", "",
         "Per frame and color: the barrels' own hue (mode of the hand-box cores) against the largest peak each finder "
         "finds. `|err|` = |found - true| in hue units (log R/B for F4). `ok` = within 3, `fooled` = 5 or more. "
         "`rank` = where the barrels' own peak stands among the finder's local peaks (1 = it is the largest; "
         "0 = no separate peak). F4: ok = inside the barrels' own 10-90 % range of log R/B.", ""]
    finders = sorted({r["finder"] for r in rows}, key=lambda f: (f[:2], f))
    for klass in ("ordinary", "extreme"):
        for color in ("orange", "blue"):
            sub = [r for r in rows if r["klass"] == klass and r["color"] == color]
            if not sub:
                continue
            L += [f"## {klass}, {color}: {len({r['stem'] for r in sub})} frames", ""]
            L.append("| finder | ok (<=3) | fooled (>=5) | none | median abs err | rank 1 | rank 2-3 | rank 4+ | no separate peak |")
            L.append("|---|---|---|---|---|---|---|---|---|")
            for f in finders:
                ss = [r for r in sub if r["finder"] == f]
                n = len(ss)
                if f == "F4_logrb":
                    ok = sum(r["rank"] == 1 for r in ss)
                    none = sum(r["err"] == "" for r in ss)
                    errs = [abs(r["err"]) for r in ss if r["err"] != ""]
                    L.append(f"| {f} | {ok}/{n} (inside 10-90 %) | {n - ok - none} | {none} | {np.median(errs):.2f} (log units) | | | | |")
                    continue
                errs = [abs(r["err"]) for r in ss if r["err"] != ""]
                ok = sum(e <= 3 for e in errs)
                fo = sum(e >= 5 for e in errs)
                none = n - len(errs)
                rk = [r["rank"] for r in ss]
                L.append(f"| {f} | {ok}/{n} | {fo} | {none} | {np.median(errs) if errs else float('nan'):.1f} | "
                         f"{sum(x == 1 for x in rk)} | {sum(x in (2, 3) for x in rk)} | {sum(x >= 4 for x in rk)} | {sum(x == 0 for x in rk)} |")
            L.append("")
            # by condition, for the finders
            L.append(f"### {klass}, {color}, by condition: ok / fooled of frames (median true mode hue; median purity; median body share)")
            L.append("")
            conds = sorted({r["cond"] for r in sub})
            show = [f for f in finders if f != "F4_logrb"]
            L.append("| condition | frames | true hue | true S | purity | body share | " + " | ".join(show) + " |")
            L.append("|---|---|---|---|---|---|" + "---|" * len(show))
            for cd in conds:
                cs = [r for r in sub if r["cond"] == cd]
                one = [r for r in cs if r["finder"] == "F0_naive"]
                cells = []
                for f in show:
                    ss = [r for r in cs if r["finder"] == f]
                    errs = [abs(r["err"]) for r in ss if r["err"] != ""]
                    cells.append(f"{sum(e <= 3 for e in errs)}/{sum(e >= 5 for e in errs)} r1={sum(r['rank'] == 1 for r in ss)}")
                L.append(f"| {cd} | {len(one)} | {np.median([r['true_mode_h'] for r in one]):.0f} | "
                         f"{np.median([r['true_mode_s'] for r in one]):.0f} | {np.median([r['purity'] for r in one]):.2f} | "
                         f"{np.median([r['body_share'] for r in one]):.3f} | " + " | ".join(cells) + " |")
            L.append("")
    (OUT / "measure.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
