#!/usr/bin/env python3
"""How close are Claude's box proposals to Tanush's hand-drawn boxes? (the box-proposal decision, 2026-11-24)

    python barrels/experiments/2026-11-24_box_proposals/compare.py [--proposals DIR] [--out DIR]

Reads every <stem>_boxes_proposed.json in --proposals (default results/2026-11-24_box_proposals/proposals: the 12
proposals written blind, by looking at the frames with tools/box_look.py, BEFORE his labels were read) and the
matching data/labels/<stem>_boxes.json. Train frames only (a test stem stops the script). Per frame: barrels found /
missed / extra (one-to-one match, greedy by IoU, IoU >= 0.3, colors ignored for the match), per matched barrel the IoU,
the four edge errors in px (proposal - label), color right or wrong, and the flags occluded / bottom_estimated /
no_stripe / held (truncated is set automatically from the box, so it is left out); per frame clean and negative.
Writes summary.json and summary.md to --out. Nothing here runs a detector.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from barrels import io, splits as sp  # noqa: E402

RES = ROOT / "results" / "2026-11-24_box_proposals"
FLAGS = ("occluded", "bottom_estimated", "no_stripe", "held")
MIN_IOU = 0.3


def iou(a, b) -> float:
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    area = lambda r: (r[2] - r[0]) * (r[3] - r[1])  # noqa: E731
    return inter / (area(a) + area(b) - inter) if inter else 0.0


def match(props: list[dict], labels: list[dict]) -> list[tuple[int, int, float]]:
    pairs = sorted(((iou(p["bbox"], l["bbox"]), i, j) for i, p in enumerate(props) for j, l in enumerate(labels)), reverse=True)
    used_p, used_l, out = set(), set(), []
    for v, i, j in pairs:
        if v < MIN_IOU or i in used_p or j in used_l:
            continue
        used_p.add(i); used_l.add(j); out.append((i, j, v))
    return out


def compare_frame(prop: dict, lab: dict) -> dict:
    P, L = prop["barrels"], lab["barrels"]
    m = match(P, L)
    rows = []
    for i, j, v in m:
        p, l = P[i], L[j]
        d = [p["bbox"][k] - l["bbox"][k] for k in range(4)]
        fp, fl = set(p.get("flags", ())) & set(FLAGS), set(l.get("flags", ())) & set(FLAGS)
        rows.append({"label_bbox": l["bbox"], "proposal_bbox": p["bbox"], "iou": round(v, 3), "edge_err": d,
                     "color_ok": p["color"] == l["color"], "label_flags": sorted(fl), "proposal_flags": sorted(fp),
                     "flag_diff": sorted(fp ^ fl), "label_note": l.get("note", ""), "proposal_note": p.get("note", "")})
    return {"n_label": len(L), "n_prop": len(P), "found": len(m), "missed": [L[j]["bbox"] for j in range(len(L)) if j not in {b for _, b, _ in m}],
            "extra": [P[i]["bbox"] for i in range(len(P)) if i not in {a for a, _, _ in m}], "barrels": rows,
            "clean_ok": bool(prop.get("clean", True)) == bool(lab.get("clean", True)), "label_clean": bool(lab.get("clean", True)),
            "proposal_clean": bool(prop.get("clean", True)), "negative_ok": bool(prop["negative"]) == bool(lab["negative"])}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proposals", type=Path, default=RES / "proposals")
    ap.add_argument("--out", type=Path, default=RES)
    args = ap.parse_args(argv)
    splits = sp.load_splits()
    frames = {}
    for pf in sorted(args.proposals.glob("*_boxes_proposed.json")):
        stem = pf.name[:-len("_boxes_proposed.json")]
        if stem not in splits["train"]:
            raise SystemExit(f"{stem}: not a train frame; refusing")
        prop = io.load_proposal(stem, args.proposals)
        lab = io.load_boxes(stem)
        frames[stem] = compare_frame(prop, lab)
    allb = [b for f in frames.values() for b in f["barrels"]]
    errs = [abs(e) for b in allb for e in b["edge_err"]]
    bottoms = [abs(b["edge_err"][3]) for b in allb]
    tot = {"frames": len(frames), "label_barrels": sum(f["n_label"] for f in frames.values()),
           "found": sum(f["found"] for f in frames.values()), "missed": sum(len(f["missed"]) for f in frames.values()),
           "extra": sum(len(f["extra"]) for f in frames.values()),
           "iou_median": round(statistics.median(b["iou"] for b in allb), 3) if allb else None,
           "iou_min": round(min(b["iou"] for b in allb), 3) if allb else None,
           "iou_ge_0.8": sum(b["iou"] >= 0.8 for b in allb), "iou_ge_0.9": sum(b["iou"] >= 0.9 for b in allb),
           "edge_err_median_px": statistics.median(errs) if errs else None, "edge_err_max_px": max(errs) if errs else None,
           "edges_within_3px": sum(e <= 3 for e in errs), "edges": len(errs),
           "bottom_err_median_px": statistics.median(bottoms) if bottoms else None, "bottom_err_max_px": max(bottoms) if bottoms else None,
           "color_mistakes": sum(not b["color_ok"] for b in allb), "flag_mistakes": sum(len(b["flag_diff"]) for b in allb),
           "clean_mistakes": sum(not f["clean_ok"] for f in frames.values()),
           "negative_mistakes": sum(not f["negative_ok"] for f in frames.values())}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "summary.json").write_text(json.dumps({"totals": tot, "frames": frames}, indent=1) + "\n")
    L = ["# Claude's box proposals vs Tanush's boxes (12 train frames, proposals written blind)", "",
         "Generated by `experiments/2026-11-24_box_proposals/compare.py`. Edge error = proposal minus label, px, "
         "[left, top, right, bottom]. Flags compared: occluded, bottom_estimated, no_stripe, held.", "",
         "| frame | his | found | missed | extra | IoU per barrel | worst edge (px) | color | flags differ | clean |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for stem, f in frames.items():
        ious = ", ".join(f"{b['iou']:.2f}" for b in f["barrels"]) or "—"
        worst = max((max(abs(e) for e in b["edge_err"]) for b in f["barrels"]), default=0)
        fd = "; ".join(f"{'+' if fl in b['proposal_flags'] else '-'}{fl}" for b in f["barrels"] for fl in b["flag_diff"]) or "—"
        col = "ok" if all(b["color_ok"] for b in f["barrels"]) else "WRONG"
        cl = "ok" if f["clean_ok"] else f"his {str(f['label_clean']).lower()}, mine {str(f['proposal_clean']).lower()}"
        L.append(f"| `{stem[5:]}` | {f['n_label']} | {f['found']} | {len(f['missed'])} | {len(f['extra'])} | {ious} | {worst} | {col} | {fd} | {cl} |")
    L += ["", "**Totals:** " + ", ".join(f"{k} {v}" for k, v in tot.items()), "", "## Per barrel", "",
          "| frame | his box | my box | IoU | edge err [l, t, r, b] | his flags | my flags |", "|---|---|---|---|---|---|---|"]
    for stem, f in frames.items():
        for b in f["barrels"]:
            L.append(f"| `{stem[5:]}` | {b['label_bbox']} | {b['proposal_bbox']} | {b['iou']:.2f} | {b['edge_err']} | "
                     f"{', '.join(b['label_flags']) or '—'} | {', '.join(b['proposal_flags']) or '—'} |")
        for mb in f["missed"]:
            L.append(f"| `{stem[5:]}` | {mb} | MISSED | | | | |")
        for eb in f["extra"]:
            L.append(f"| `{stem[5:]}` | — | {eb} EXTRA | | | | |")
    (args.out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
