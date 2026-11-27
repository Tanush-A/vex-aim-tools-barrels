#!/usr/bin/env python3
"""Yardstick (a) of the side-cut experiment (PREREG.md): simulated scenes.

Part ``sidecut``: every source barrel of the pools, cut at the side by a straight edge and by a slanted edge (both
leans), from the left and from the right, 50, 60, 65 and 75 % of its width hidden; each scene plain and "real-like"
(the stripe ends 6 px before the cut). Scored against the FULL box, twice: ``found`` (the strict rule) and ``placed``
(found, and the box's centre within 10 % of the width of the true centre).

Part ``scorecard``: every scene of the occlusion scorecard (15 kinds x 25, 50, 75 %) on the same source barrels, to show
what else changed: found before and after per kind, and how many scenes have other boxes than today.

Each scene is run with every value of ``DetConfig.side_cut`` (``lib.MODES``): today, the candidate, the comparison arm.

    python barrels/experiments/2026-11-26_sidecut/sim.py --pools HOME "ABP white" --part sidecut --out dev
    python barrels/experiments/2026-11-26_sidecut/sim.py                                  # all pools, both parts

Train frames only. Writes results/2026-11-26_sidecut/[<out>/] sidecut_scenes.csv, sidecut.md, scorecard_scenes.csv,
scorecard.md.
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
from concurrent.futures import ProcessPoolExecutor

import lib
from lib import dtp, ed

DEV_POOLS = ("HOME", "ABP white")          # the numbers of the rule were chosen on these (PREREG.md); CAMPUS was not looked at


def boxes_key(preds) -> tuple:
    return tuple(sorted((int(p.color), tuple(int(v) for v in p.bbox)) for p in preds))


def work_sidecut(src) -> list[dict]:
    rows = []
    for kind, amount, side, lean, short, sc in lib.side_cut_scenes(src):
        base = None
        for mode in lib.MODES:
            preds, log = lib.detect(sc.mask, mode)
            r = lib.score(preds, src.color, src.bbox)
            same = [p for p in preds if p.color == src.color]
            best = max(same, key=lambda p: ed.box_iou(p.bbox, src.bbox)) if same else None
            key = boxes_key(preds)
            base = key if mode == lib.MODES[0] else base
            rows.append({"pool": src.pool, "stem": src.stem, "color": dtp.COLOR_NAMES[src.color], "W": src.width, "kind": kind, "amount": amount,
                         "side": side, "lean": lean if kind == "slant" else 0, "short": short, "mode": mode, **r,
                         "changed": int(key != base), "rule": lib.rule_of(log, best.bbox) if best else "", "why": "" if r["found"] else lib.why_none(log),
                         "box": "" if best is None else list(best.bbox), "truth": list(src.bbox),
                         "off_w": "" if best is None else round(((best.bbox[0] + best.bbox[2]) - (src.bbox[0] + src.bbox[2])) / 2 / src.width, 3)})
    return rows


def work_scorecard(args) -> list[dict]:
    pool, si = args
    rows = []
    for key, amount, variant, src, sc in lib.scorecard_scenes(pool, only=si):
        gts = [dtp.Barrel(color=c, bbox=tuple(b), source="gt") for c, b in [sc.target] + list(sc.fronts) if b[2] > b[0] and b[3] > b[1]]
        base = None
        for mode in lib.MODES:
            preds, log = lib.detect(sc.mask, mode)
            res = ed.evaluate_frame("scene", preds, gts, lib.CAM, rule="v2")
            r = lib.score(preds, *sc.target)
            k = boxes_key(preds)
            base = k if mode == lib.MODES[0] else base
            rows.append({"pool": src.pool, "stem": src.stem, "color": dtp.COLOR_NAMES[src.color], "W": src.width, "row": key, "amount": amount,
                         "variant": variant, "mode": mode, "found": r["found"], "placed": r["placed"], "boxes": len(preds),
                         "not_on_a_barrel": len(res.unmatched_pred), "fronts": len(gts) - 1,
                         "fronts_found": sum(1 for gi in range(1, len(gts)) if gi not in res.unmatched_gt), "changed": int(k != base)})
    return rows


def write_csv(path, rows) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def cell(rs) -> str:
    return f"{sum(r['found'] for r in rs)} / {sum(r['placed'] for r in rs)} / {len(rs)}"


def sidecut_md(rows, pools) -> str:
    L = ["# Simulated side cuts", "",
         f"Source barrels: {', '.join(f'{p} {len({(r['stem'], tuple(r['truth'])) for r in rows if r['pool'] == p})}' for p in pools)}. Each cell: "
         "**found / placed / scenes**. found = the strict rule against the FULL box. placed = found, and the box's centre within 10 % of the "
         "width of the true centre. A box centred on the visible half is a quarter of a width off: found, not placed.", "",
         "`centred` = today. `own_side` = the candidate. `own_side+centred` = the own side first, else today's guess.", ""]
    groups = [("all pools", pools)] + ([("the pools the numbers were chosen on (" + ", ".join(p for p in pools if p in DEV_POOLS) + ")", [p for p in pools if p in DEV_POOLS]),
                                        ("held out (" + ", ".join(p for p in pools if p not in DEV_POOLS) + ")", [p for p in pools if p not in DEV_POOLS])]
                                       if any(p not in DEV_POOLS for p in pools) and any(p in DEV_POOLS for p in pools) else []) + [(p, [p]) for p in pools]
    for name, ps in groups:
        sub = [r for r in rows if r["pool"] in ps]
        if not sub:
            continue
        L += [f"## {name}", ""]
        for short, title in ((0, "plain cut"), (lib.SHORT_PX, f"real-like: the stripe ends {lib.SHORT_PX} px before the cut")):
            L += [f"### {title}", "", "| kind | mode | " + " | ".join(f"{int(round(a * 100))} % hidden" for a in lib.AMOUNTS) + " | boxes that are not the barrel |", "|---|---|" + "---|" * (len(lib.AMOUNTS) + 1)]
            for kind in ("edge", "slant", "edge + slant"):
                for mode in lib.MODES:
                    rs = [r for r in sub if r["short"] == short and r["mode"] == mode and (kind == "edge + slant" or r["kind"] == kind)]
                    L.append(f"| {kind} | `{mode}` | " + " | ".join(cell([r for r in rs if r["amount"] == a]) for a in lib.AMOUNTS) + f" | {sum(r['wrong'] for r in rs)} |")
            L.append("")
    L += ["## Which rule drew the box of the barrel (all pools, plain and real-like together)", ""]
    for mode in lib.MODES:
        for a in lib.AMOUNTS:
            c = collections.Counter((r["rule"] or "no box", "found" if r["found"] else "not found") for r in rows if r["mode"] == mode and r["amount"] == a)
            L.append(f"- `{mode}`, {int(round(a * 100))} %: " + ", ".join(f"{k[0]} ({k[1]}) {v}" for k, v in c.most_common()))
    L += ["", "## Why there is no found box (all pools)", ""]
    for mode in lib.MODES:
        c = collections.Counter(r["why"] if not r["rule"] else f"box by {r['rule']}, not right" for r in rows if r["mode"] == mode and not r["found"])
        L.append(f"- `{mode}`: " + ", ".join(f"{k} {v}" for k, v in c.most_common()))
    return "\n".join(L) + "\n"


def scorecard_md(rows, pools) -> str:
    keys = [k for k, _, _ in lib.ROWS]
    amounts = sorted({r["amount"] for r in rows})
    L = ["# Every kind of scene of the occlusion scorecard: what else changed", "",
         f"The same source barrels ({', '.join(pools)}). Each cell: found under the strict rule, `centred` (today) -> `own_side` -> `own_side+centred`, of n scenes; "
         "in brackets the same for placed (found, centre within 10 % of the width).", "",
         "| kind | " + " | ".join(f"{int(round(a * 100))} % hidden" for a in amounts) + " | scenes whose boxes differ from today: `own_side` / `own_side+centred` | boxes on no barrel: today -> `own_side` -> `own_side+centred` |",
         "|---|" + "---|" * (len(amounts) + 2)]

    def line(name, sub):
        cells = []
        for a in amounts:
            rs = [r for r in sub if r["amount"] == a]
            by = {m: [r for r in rs if r["mode"] == m] for m in lib.MODES}
            cells.append(" -> ".join(str(sum(r["found"] for r in by[m])) for m in lib.MODES) + f" of {len(by[lib.MODES[0]])} (" +
                         " -> ".join(str(sum(r["placed"] for r in by[m])) for m in lib.MODES) + ")")
        ch = " / ".join(str(sum(r["changed"] for r in sub if r["mode"] == m)) for m in lib.MODES[1:])
        fb = " -> ".join(str(sum(r["not_on_a_barrel"] for r in sub if r["mode"] == m)) for m in lib.MODES)
        return f"| {name} | " + " | ".join(cells) + f" | {ch} | {fb} |"

    for k in keys:
        L.append(line(k, [r for r in rows if r["row"] == k]))
    L.append(line("**all kinds**", rows))
    L.append(line("all kinds but edge and slant", [r for r in rows if r["row"] not in ("edge", "slant")]))
    fr = {m: (sum(r["fronts_found"] for r in rows if r["mode"] == m), sum(r["fronts"] for r in rows if r["mode"] == m)) for m in lib.MODES}
    L += ["", "The barrels pasted in front, found: " + " -> ".join(f"{fr[m][0]}" for m in lib.MODES) + f" of {fr[lib.MODES[0]][1]}.", ""]
    for p in pools:
        L += [f"## {p}", "", "| kind | " + " | ".join(f"{int(round(a * 100))} % hidden" for a in amounts) + " | changed | boxes on no barrel |", "|---|" + "---|" * (len(amounts) + 2)]
        for k in keys:
            L.append(line(k, [r for r in rows if r["row"] == k and r["pool"] == p]))
        L.append(line("**all kinds**", [r for r in rows if r["pool"] == p]))
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pools", nargs="+", default=list(lib.POOLS))
    ap.add_argument("--part", choices=("sidecut", "scorecard", "both"), default="both")
    ap.add_argument("--out", default="")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args(argv)
    out = lib.OUT / args.out if args.out else lib.OUT
    out.mkdir(parents=True, exist_ok=True)
    pools = {p: lib.sources(p) for p in args.pools}
    print({p: len(v) for p, v in pools.items()}, "source barrels; widths", {p: sorted(s.width for s in v) for p, v in pools.items()})
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        if args.part in ("sidecut", "both"):
            rows = [r for rs in ex.map(work_sidecut, [s for v in pools.values() for s in v]) for r in rs]
            write_csv(out / "sidecut_scenes.csv", rows)
            md = sidecut_md(rows, list(pools))
            (out / "sidecut.md").write_text(md)
            print(md)
        if args.part in ("scorecard", "both"):
            rows = [r for rs in ex.map(work_scorecard, [(v, i) for v in pools.values() for i in range(len(v))]) for r in rs]
            write_csv(out / "scorecard_scenes.csv", rows)
            md = scorecard_md(rows, list(pools))
            (out / "scorecard.md").write_text(md)
            print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
