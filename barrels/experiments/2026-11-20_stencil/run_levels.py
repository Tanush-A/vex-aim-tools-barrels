#!/usr/bin/env python3
"""The earlier tests with this experiment's arms: the levels of ``2026-11-18_det_given_seg`` (perfect HOME masks;
light / medium / heavy damage, seeds 0 to 4; CAMPUS; BLACK with label thresholds), then the eval table of each
arm against ``rules`` (``barrels.report``: HOME leave-one-scene-out, CAMPUS, and report-only black, wood, Dave)
and the never-regress check. The 2026-11-18 harness is loaded by path; nothing is copied.

Train frames only; a test frame is never opened (asserted in the loaded script and refused by ``report``).

    python barrels/experiments/2026-11-20_stencil/run_levels.py [--arms stencil,union] [--no-levels]
Outputs: results/2026-11-20_stencil/levels/ summary.md, scenarios.csv, per_barrel.csv, config.json;
results/2026-11-20_stencil/never_regress.md, report_<arm>/ (committed); sheets/ (ignored).
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
import stencil_arms as A  # noqa: E402
from barrels import report as rp, worldmap_bridge as wb  # noqa: E402

JUDGED = ("HOME", "CAMPUS")


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


@dataclasses.dataclass(frozen=True)
class StArm(rp.Arm):
    """A ``report.Arm`` whose detector settings are one of this experiment's arms (the name says which)."""

    def det_config(self):
        return A.ARMS[self.name]

    def describe(self) -> str:
        return f"arm `{self.name}` of experiments/2026-11-20_stencil/stencil_arms.py, adopted color model"


def never_regress(arm: str, out: Path) -> tuple[bool, list[str]]:
    """The eval table of ``arm`` against ``rules``, written to ``out/report_<arm>/``; and the check of
    ``2026-11-19_det_side/run.py``, word for word: every scenario row of HOME and CAMPUS keeps its found barrels
    and gains no false box; no set gains a box on a negative frame, and no clean negative frame has a box."""
    rep = rp.make_report(StArm(arm, wb.DEFAULT_MODEL), StArm("rules", wb.DEFAULT_MODEL))
    rp.write_all(rep, out / f"report_{arm}", title=f"Eval report: `{arm}` (candidate) against `rules` (baseline)")
    ok, lines = True, []
    for row in rep.rows:
        if row.kind == "total":
            continue
        c, b = row.cand, row.base
        judged = row.label.rstrip("*").upper() in JUDGED
        bad = []
        if judged and c.found < b.found:
            bad.append(f"found {b.found} -> {c.found}")
        if judged and c.false > b.false:
            bad.append(f"false {b.false} -> {c.false}")
        if c.clean_neg_false > 0 or c.neg_false > b.neg_false:
            bad.append(f"boxes on negative frames {b.neg_false} -> {c.neg_false} (on clean ones: {c.clean_neg_false})")
        if bad or row.kind == "subtotal" or (c.found, c.missed, c.false) != (b.found, b.missed, b.false):
            verdict = "**FAILS**: " + ", ".join(bad) if bad else ("ok" if judged else "report only")

            def n(x, fmt):
                return "-" if x != x else f"{x:{fmt}}"
            lines.append(f"| {row.label} | {row.scene or 'ALL ROWS'} | {b.found} / {b.missed} / {b.false} | {c.found} / {c.missed} / {c.false} | "
                         f"{n(b.width, '.2f')} -> {n(c.width, '.2f')} | {n(b.bottom, '.1f')} -> {n(c.bottom, '.1f')} | {b.neg_false} -> {c.neg_false} | {verdict} |")
        ok = ok and not bad
    return ok, lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default=",".join(A.METHODS))
    ap.add_argument("--no-levels", action="store_true")
    ap.add_argument("--no-table", action="store_true")
    ap.add_argument("--no-sheets", action="store_true")
    args = ap.parse_args(argv)
    arms = [a for a in args.arms.split(",") if a]
    A.install()
    A.OUT.mkdir(parents=True, exist_ok=True)
    if not args.no_levels:
        R = load("det_given_seg_run", HERE.parent / "2026-11-18_det_given_seg" / "run.py")
        R.ARMS = A.ARMS
        R.main(["--arms", ",".join(arms), "--out", str(A.OUT / "levels")] + (["--no-sheets"] if args.no_sheets else []))
    if not args.no_table:
        L = ["# Never regress: the eval table of each arm against `rules` (today's rule detector), adopted color model", "",
             "Found / missed / false; width = median box width / true width, bottom = median bottom-edge error in px, over the found barrels. Listed: each "
             "set's total and every scenario row that differs from `rules`. HOME (leave one scene out) and CAMPUS rows decide; the other sets are "
             "report only, except that no set may gain a box on a negative frame.", ""]
        for a in arms:
            if a == "rules":
                continue
            ok, lines = never_regress(a, A.OUT)
            L += [f"## `{a}`: {'passes' if ok else 'FAILS'}", "", "| set | scenario | rules | arm | width | bottom px | boxes on negatives | |", "|---|---|---|---|---|---|---|---|"] + lines + [""]
        (A.OUT / "never_regress.md").write_text("\n".join(L) + "\n")
        print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
