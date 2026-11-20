#!/usr/bin/env python3
"""The eval table (``barrels.report``: v2 rule, train frames, HOME leave-one-scene-out, CAMPUS; black, the wood lamp
settings and Dave's frames report only) of every arm, against ``stack``; and PREREG clause (a), row by row.

Train frames only; ``report`` refuses a test frame.

    python barrels/experiments/2026-11-20_occl_combined/run_eval.py [--arms before,combined] [--out round1] [--against stack]
Outputs: results/2026-11-20_occl_combined/[<out>/] eval.md, eval.csv, report_<arm>/ (the full table of each arm).
"""
from __future__ import annotations

import argparse
import csv
import dataclasses

import common as C
from barrels import cv as bcv, report as rp, worldmap_bridge as wb

A = C.A
JUDGED = ("HOME", "CAMPUS")


@dataclasses.dataclass(frozen=True)
class CArm(rp.Arm):
    """A ``report.Arm`` whose detector settings are one of this experiment's arms (the name says which)."""

    def det_config(self):
        return A.ARMS[self.name]

    def describe(self) -> str:
        return f"arm `{self.name}` of experiments/2026-11-20_occl_combined/comb_arms.py, adopted color model"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--against", default="stack", help="the arm every other arm is compared with (PREREG: stack)")
    args = ap.parse_args(argv)
    ref = args.against
    arms = [a for a in C.arm_list(args.arms, C.RULE_ARMS) if a != ref]
    out = C.OUT / args.out if args.out else C.OUT
    out.mkdir(parents=True, exist_ok=True)
    A.install()
    cells: dict[tuple, dict] = {}                 # (set label, scene, kind) -> {arm: Cell}
    order = []
    for a in arms:
        rep = rp.make_report(CArm(a, wb.DEFAULT_MODEL), CArm(ref, wb.DEFAULT_MODEL))
        rp.write_all(rep, out / f"report_{a}", title=f"Eval report: `{a}` (candidate) against `{ref}` (baseline)")
        for row in rep.rows:
            key = (row.label, row.scene, row.kind)
            if key not in cells:
                cells[key] = {}; order.append(key)
            cells[key][a] = row.cand
            seen = cells[key].setdefault(ref, row.base)           # the counts only: a Cell with a NaN median is not equal to itself
            assert (seen.frames, seen.barrels, seen.found, seen.missed, seen.false, seen.neg_false) == \
                (row.base.frames, row.base.barrels, row.base.found, row.base.missed, row.base.false, row.base.neg_false), f"`{ref}` differs between two reports at {key}"
    names = [ref] + arms
    with (out / "eval.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "set", "scenario", "kind", "frames", "barrels", "found", "missed", "false", "boxes_on_negatives", "boxes_on_clean_negatives",
                    "width_ratio", "bottom_err_px"])
        for key in order:
            for a in names:
                c = cells[key][a]
                w.writerow([a, key[0], key[1], key[2], c.frames, c.barrels, c.found, c.missed, c.false, c.neg_false, c.clean_neg_false,
                            "" if c.width != c.width else round(c.width, 3), "" if c.bottom != c.bottom else round(c.bottom, 2)])

    L = ["# The eval table of every arm", "",
         f"git {bcv.git_hash()}; v2 rule; train frames only; adopted color model; HOME leave-one-scene-out. Each cell: found / missed / false "
         "(on a set's `all` row: then the boxes on its negative frames). HOME and CAMPUS decide (PREREG clause (a)); the other sets are report only, "
         "except that no set may have a box on a negative frame. `*` = indicative labels.", "",
         "| set | scenario | barrels | " + " | ".join(f"`{a}`" for a in names) + " |", "|---|---|---|" + "---|" * len(names)]
    for key in order:
        label, scene, kind = key
        if kind == "total":
            continue
        def txt(c, sub=(kind == "subtotal")):
            return f"{c.found} / {c.missed} / {c.false}" + (f"; neg {c.neg_false}" if sub else "")
        L.append(f"| {label} | {'**all**' if kind == 'subtotal' else scene} | {cells[key][ref].barrels} | " + " | ".join(txt(cells[key][a]) for a in names) + " |")
    L += ["", f"## Clause (a), each arm against `{ref}`", "",
          "| arm | HOME and CAMPUS rows that lose a found barrel | ... that gain a false box | boxes on negative frames, any set | (a) |", "|---|---|---|---|---|"]
    detail = []
    for a in arms:
        lost, gained, neg = [], [], 0
        for key in order:
            label, scene, kind = key
            c, b = cells[key][a], cells[key][ref]
            if kind == "subtotal":
                neg += c.neg_false
            if kind != "scene":
                continue
            judged = label.rstrip("*").upper() in JUDGED
            if judged and c.found < b.found:
                lost.append(f"{label} {scene}: found {b.found} → {c.found}")
            if judged and c.false > b.false:
                gained.append(f"{label} {scene}: false {b.false} → {c.false}")
            if (c.found, c.missed, c.false) != (b.found, b.missed, b.false):
                detail.append(f"- `{a}`, {label} {scene}: {b.found} / {b.missed} / {b.false} → {c.found} / {c.missed} / {c.false}" + ("" if judged else " (report only)"))
        ok = not lost and not gained and neg == 0
        L.append(f"| `{a}` | {len(lost)} | {len(gained)} | {neg} | {'pass' if ok else '**FAILS**'} |")
    L += ["", f"Every scenario row that differs from `{ref}`:", ""] + (detail or ["- none"])
    (out / "eval.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
