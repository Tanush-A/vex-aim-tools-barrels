#!/usr/bin/env python3
"""Ours (fixed colors + stripe by contrast) against the vendor, frame by frame, as pictures and a chart. Side tool.

    python barrels/tools/vs_vendor.py --frame 4A8B_lampmid6_bathtile_core_01      # one frame -> one picture
    python barrels/tools/vs_vendor.py --frame 4A8B_lampcool6_ottoman_core_01 --open
    python barrels/tools/vs_vendor.py --all                                        # every train frame with a vendor file:
                                                                                   # pictures, chart.png, index.html

One picture per frame, three panels side by side:
  1. OURS on the photo: thick boxes in the barrel's color; hand labels thin green.
  2. VENDOR on the photo: thick magenta boxes; hand labels thin green.
  3. SEGMENTATION: what the fixed colors paint (orange / blue) and, in yellow, what stripe by contrast added.
The title says how many labelled barrels each found (strict rule: same color, overlap >= 0.5, bottom within 10 %).

Train frames only (test frames are refused before they are opened). The contrast code is read from the checkout named
by --contrast-from (default: this checkout if it has experiments/2026-11-26_contrast, else the experiment's worktree).
Outputs: results/2026-11-27_vs_vendor/ (pictures are not committed).
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parent
WORKTREE = Path("/Users/tanush/Desktop/Celeste/vex-aim-tools/.claude/worktrees/agent-a97476ecf23649985/barrels")
OUT = BARRELS / "results" / "2026-11-27_vs_vendor"


def load_contrast(src: Path):
    sys.path.insert(0, str(src / "src"))
    exp = src / "experiments" / "2026-11-26_contrast"
    sys.path.insert(0, str(exp))
    spec = importlib.util.spec_from_file_location("contrast_candidate", exp / "candidate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["contrast_candidate"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frame", action="append", default=[], help="a train frame stem (repeatable)")
    ap.add_argument("--all", action="store_true", help="every train frame with a vendor file")
    ap.add_argument("--like", default=None, help="every train frame whose name contains this text (vendor file or not), e.g. window_light or campus_light")
    ap.add_argument("--open", action="store_true", help="open the picture(s) when done (macOS)")
    ap.add_argument("--contrast-from", default=None, help="a barrels/ folder that has experiments/2026-11-26_contrast")
    ap.add_argument("--cand-callable", default=None, metavar="FILE:NAME",
                    help="OURS = this detect_frame(stem, frame) instead of the contrast experiment's BEST (FILE relative to --contrast-from or absolute); "
                         "if FILE also has masks(stem, frame) -> (fixed mask, painted mask), the segmentation panel uses it")
    ap.add_argument("--out", default=None, metavar="DIR", help="write the pictures, chart and index.html here instead of results/2026-11-27_vs_vendor")
    a = ap.parse_args()
    global OUT
    if a.out:
        OUT = Path(a.out)
    src = Path(a.contrast_from) if a.contrast_from else (BARRELS if (BARRELS / "experiments" / "2026-11-26_contrast" / "candidate.py").exists() else WORKTREE)
    cand = load_contrast(src)
    ours_fn = masks_fn = None
    if a.cand_callable:
        f, _, name = a.cand_callable.rpartition(":")
        fp = Path(f) if Path(f).is_absolute() else src / f
        sys.path.insert(0, str(fp.parent))
        spec = importlib.util.spec_from_file_location(fp.stem, fp)
        m = importlib.util.module_from_spec(spec)
        sys.modules[fp.stem] = m
        spec.loader.exec_module(m)
        ours_fn, masks_fn = getattr(m, name), getattr(m, "masks", None)
    from barrels import counting as ct, eval_det as ed, geometry as geo, io, judge as jg
    cam = geo.AIM_4A8B6118_BOXFIT
    splits = json.loads((BARRELS / "data" / "splits.json").read_text())
    test = set(splits["test"])
    if a.all:
        stems = sorted(s for s in splits["train"] if io.vendor_path(s).exists() and io.boxes_path(s).exists())
    elif a.like:
        stems = sorted(s for s in splits["train"] if a.like in s and io.boxes_path(s).exists())
    else:
        stems = a.frame
    if not stems:
        ap.error("give --frame STEM or --all")
    for s in stems:
        if s in test:
            sys.exit(f"{s} is a test frame: refused (test frames are looked at only in a planned look)")
    gts_all, _ = ct.load_gts(stems)
    (OUT / "frames").mkdir(parents=True, exist_ok=True)
    rows = []
    for s in stems:
        frame = jg.load_frame(s)
        if ours_fn is not None:
            ours = ours_fn(s, frame)
            if masks_fn is not None:
                base, mask = masks_fn(s, frame)
            else:
                fw = cand.FrameWork(frame)
                base = mask = fw.base_mask
        else:
            fw = cand.FrameWork(frame)
            ours = fw.detect(cand.BEST)
            mask, _ = fw.masks(cand.BEST)
            base = fw.base_mask
        try:
            vend, _ = io.vendor_barrels(io.load_vendor(s))
        except (FileNotFoundError, ValueError):
            vend = None
        gts = gts_all.get(s, [])

        def hits(preds):
            if preds is None:
                return None
            r = ed.evaluate_frame(s, preds, gts, cam, rule="v2")
            on = sum(1 for g in gts if any(p.color == g.color and ct.is_on(p, g) for p in preds))
            return len(gts) - len(r.unmatched_gt), len(r.unmatched_pred), on
        ho, hv = hits(ours), hits(vend)
        img = io.load_image(io.find_image(s)).copy()          # BGR; load_frame above already refused a test frame

        def panel(preds, col_fn, title):
            p = img.copy()
            for g in gts:
                cv2.rectangle(p, g.bbox[:2], (g.bbox[2] - 1, g.bbox[3] - 1), (0, 200, 0), 1)
            for b in preds or []:
                cv2.rectangle(p, b.bbox[:2], (b.bbox[2] - 1, b.bbox[3] - 1), col_fn(b), 3)
            cv2.putText(p, title, (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3)
            cv2.putText(p, title, (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
            return p
        colour = lambda b: (0, 140, 255) if b.color == 1 else (255, 90, 0)
        n = len(gts)
        p1 = panel(ours, colour, f"OURS {ho[0]}/{n} strict, {ho[2]}/{n} on barrel")
        p2 = panel(vend, lambda b: (255, 0, 255), f"VENDOR {hv[0]}/{n} strict, {hv[2]}/{n} on barrel" if hv else "VENDOR: no file")
        seg = np.zeros_like(img)
        seg[base == 1] = (0, 140, 255)
        seg[base == 2] = (255, 90, 0)
        added = (mask != base) & np.isin(mask, (1, 2))
        seg[added] = (0, 255, 255)
        for g in gts:
            cv2.rectangle(seg, g.bbox[:2], (g.bbox[2] - 1, g.bbox[3] - 1), (0, 200, 0), 1)
        cv2.putText(seg, "SEGMENTATION (yellow = added by contrast)", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        pic = np.hstack([p1, p2, seg])
        path = OUT / "frames" / f"{s}.jpg"
        cv2.imwrite(str(path), pic, [cv2.IMWRITE_JPEG_QUALITY, 85])
        verdict = "same" if hv is None or ho[2] == hv[2] else ("ours" if ho[2] > hv[2] else "vendor")   # judged on "a box on the barrel", so a slightly big box is not a loss
        rows.append({"stem": s, "place": ct.place_of(s), "condition": ct.condition_of(s), "barrels": n,
                     "ours": ho[0], "ours_extra": ho[1], "ours_on": ho[2], "vendor_on": hv[2] if hv else None, "vendor": hv[0] if hv else None, "vendor_extra": hv[1] if hv else None,
                     "better": verdict if hv else "no vendor file", "picture": str(path)})
        print(f"{s:45s} barrels {n}  ours {ho[0]} (+{ho[1]} extra)  vendor {hv[0] if hv else '-'} (+{hv[1] if hv else '-'} extra)  on-barrel {ho[2]} vs {hv[2] if hv else '-'} -> {verdict}")
    if a.all or a.like:
        write_chart(rows, a.like)
    if a.open:
        subprocess.run(["open"] + [r["picture"] for r in rows][:12] + ([str(OUT / "index.html")] if a.all else []))
    return 0


def write_chart(rows: list[dict], like: str | None = None) -> None:
    global OUT
    if like:
        OUT = OUT / like
        OUT.mkdir(parents=True, exist_ok=True)
        import shutil
        for r in rows:
            shutil.copy(r["picture"], OUT / Path(r["picture"]).name)
        rows = [dict(r, vendor=r["vendor"] or 0, vendor_extra=r["vendor_extra"] or 0) for r in rows]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    (OUT / "frames.json").write_text(json.dumps(rows, indent=1))
    conds = sorted({r["condition"] for r in rows})
    tot = {c: [sum(r[k] or 0 for r in rows if r["condition"] == c) for k in ("barrels", "ours_on", "vendor_on")] for c in conds}
    fig, ax = plt.subplots(figsize=(13, 5))
    x = np.arange(len(conds))
    ax.bar(x - 0.27, [tot[c][0] for c in conds], 0.27, label="labelled barrels", color="#9a9a9a")
    ax.bar(x, [tot[c][1] for c in conds], 0.27, label="ours (contrast), box on the barrel", color="#e8831d")
    ax.bar(x + 0.27, [tot[c][2] for c in conds], 0.27, label="vendor, box on the barrel", color="#c026d3")
    ax.set_xticks(x, [c.replace("_", "\n") for c in conds], fontsize=8)
    ax.set_ylabel("barrels with a box on them (per frame)")
    ax.set_title("Ours vs the vendor by condition (train frames with vendor files)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "chart.png", dpi=110)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 6))
    jit = np.random.default_rng(0).uniform(-0.15, 0.15, (len(rows), 2))
    xs = [(r["vendor_on"] or 0) + j[0] for r, j in zip(rows, jit)]
    ys = [r["ours_on"] + j[1] for r, j in zip(rows, jit)]
    colors = ["#16a34a" if r["better"] == "ours" else "#dc2626" if r["better"] == "vendor" else "#64748b" for r in rows]
    ax.scatter(xs, ys, c=colors, s=22)
    m = max(max(xs), max(ys)) + 1
    ax.plot([0, m], [0, m], "k--", lw=0.8)
    ax.set_xlabel("vendor: barrels found in the frame")
    ax.set_ylabel("ours: barrels found in the frame")
    ax.set_title("Each dot is a frame. Green: we find more. Red: vendor finds more.")
    fig.tight_layout()
    fig.savefig(OUT / "scatter.png", dpi=110)
    plt.close(fig)
    n = {k: sum(r["better"] == k for r in rows) for k in ("ours", "same", "vendor")}
    T = [sum(r[k] or 0 for r in rows) for k in ("barrels", "ours", "vendor", "ours_extra", "vendor_extra", "ours_on", "vendor_on")]
    parts = [f"<!doctype html><meta charset=utf-8><title>Ours vs vendor</title><style>body{{font-family:system-ui;margin:16px;background:#fff;color:#111}}"
             "img{max-width:100%}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:12px}"
             ".c{border:1px solid #ddd;padding:6px;border-radius:6px}.ours{border-color:#16a34a}.vendor{border-color:#dc2626}h2{margin-top:28px}</style>",
             f"<h1>Ours (fixed colors + stripe by contrast) vs the vendor</h1><p>Train frames with vendor files ({len(rows)} frames). "
             f"Our methods were shaped on these frames; the vendor's were not.</p>",
             f"<p><b>Totals:</b> {T[0]} labelled barrels. <b>A box on the barrel</b> (what matters for the robot): ours {T[5]}, vendor {T[6]}. "
             f"Strict rule (overlap 0.5, bottom within 10 %): ours {T[1]} with {T[3]} extra boxes; vendor {T[2]} with {T[4]} extra boxes. Frames are grouped by the on-barrel count. "
             f"Frames where we find more: {n['ours']}; the same: {n['same']}; the vendor finds more: {n['vendor']}.</p>",
             "<img src=chart.png><img src=scatter.png style='max-width:520px'>"]
    for key, title in (("vendor", "The vendor finds more"), ("ours", "We find more"), ("same", "The same number")):
        parts.append(f"<h2>{title} ({n[key]} frames)</h2><div class=g>")
        for r in sorted((r for r in rows if r["better"] == key), key=lambda r: r["stem"]):
            parts.append(f"<div class='c {key}'><div><b>{html.escape(r['stem'])}</b><br>barrels {r['barrels']}: on barrel ours {r['ours_on']}, vendor {r['vendor_on']}; strict ours {r['ours']} (+{r['ours_extra']} extra), "
                         f"vendor {r['vendor']} (+{r['vendor_extra']} extra)</div><a href='frames/{r['stem']}.jpg'><img loading=lazy src='frames/{r['stem']}.jpg'></a></div>")
        parts.append("</div>")
    (OUT / "index.html").write_text("\n".join(parts))
    print(f"\nwrote {OUT / 'index.html'}, chart.png, scatter.png; ours better {n['ours']}, same {n['same']}, vendor better {n['vendor']}")


if __name__ == "__main__":
    raise SystemExit(main())
