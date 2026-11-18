#!/usr/bin/env python3
"""TODO A2 + A3 (2026-11-19): the misses that remain when the segmentation is good: side occlusion, and what
damage to a stripe does. Same test as ``experiments/2026-11-18_det_given_seg`` (its ``run.py`` is loaded by path
and run with this experiment's arms; nothing is copied): level 1 perfect HOME masks, level 2 the same with
seeded damage, 3a CAMPUS with the adopted colors, 3b BLACK with thresholds read from the labels, 3c wood (report
only). Then, per arm, the eval table (``barrels.report``) against ``base`` and the never-regress check of the
PREREG: no scenario row of HOME or CAMPUS loses a found barrel or gains a false box; no box on a negative frame.

Train frames only; a test frame is never opened (asserted in the loaded script and refused by ``report``).

    python barrels/experiments/2026-11-19_det_side/run.py                       # every arm of side_arms.py
    python barrels/experiments/2026-11-19_det_side/run.py --arms base --out step1_baseline

Outputs: results/2026-11-19_det_side/[<out>/] summary.md, scenarios.csv, per_barrel.csv, config.json,
never_regress.md, report_<arm>/ (committed); sheets/ (ignored).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE.parent / "2026-11-18_det_given_seg"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


R = load("det_given_seg_run", PREV / "run.py")          # the 2026-11-18 test harness
import side_arms  # noqa: E402
from barrels import report as rp, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-19_det_side"
JUDGED = ("HOME", "CAMPUS")                              # the sets whose scenario rows decide (PREREG rule 1)


def never_regress(arm: str, out: Path) -> tuple[bool, list[str]]:
    """The eval table of ``arm`` against ``base`` (both with the adopted color model), written to
    ``out/report_<arm>/``; and the check: every scenario row of HOME and CAMPUS keeps its found barrels and gains
    no false box; no set gains a box on a negative frame, and no clean negative frame of any set has a box.
    Returns (passes, the table lines of the rows that differ from base)."""
    cand = rp.Arm("candidate", wb.DEFAULT_MODEL, rp.parse_det_overrides([side_arms.OVERRIDES[arm]]))
    base = rp.Arm("baseline", wb.DEFAULT_MODEL, rp.parse_det_overrides([side_arms.OVERRIDES["base"]]))
    assert cand.det_config() == side_arms.ARMS[arm] and base.det_config() == side_arms.ARMS["base"], "arms and overrides disagree"
    rep = rp.make_report(cand, base)
    rp.write_all(rep, out / f"report_{arm}", title=f"Eval report: {cand.describe()}  vs  {base.describe()}")
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
            lines.append(f"| {row.label} | {row.scene or 'ALL ROWS'} | {b.found} / {b.missed} / {b.false} | {c.found} / {c.missed} / {c.false} | "
                         f"{b.neg_false} -> {c.neg_false} | {verdict} |")
        ok = ok and not bad
    return ok, lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default=",".join(side_arms.ARMS))
    ap.add_argument("--out", default="", help="sub-folder of the results folder (default: the folder itself)")
    ap.add_argument("--no-sheets", action="store_true")
    ap.add_argument("--no-levels", action="store_true", help="skip levels 1 to 3, only the eval table")
    args = ap.parse_args(argv)
    out = OUT / args.out if args.out else OUT
    out.mkdir(parents=True, exist_ok=True)
    arms = [a for a in args.arms.split(",") if a]
    if not args.no_levels:
        R.ARMS = side_arms.ARMS
        R.main(["--arms", ",".join(arms), "--out", str(out)] + (["--no-sheets"] if args.no_sheets else []))
    L = ["# Never regress: the eval table of each arm against `base` (today's defaults), adopted color model", "",
         "Found / missed / false. Listed: each set's total and every scenario row that differs from `base`. HOME (leave-one-scene-out) "
         "and CAMPUS rows decide; the other sets are report only, except that no set may gain a box on a negative frame.", ""]
    for a in arms:
        ok, lines = never_regress(a, out)
        L += [f"## `{a}`: {'passes' if ok else 'FAILS'}", "", "| set | scenario | base | arm | boxes on negatives | |", "|---|---|---|---|---|---|"] + lines + [""]
    (out / "never_regress.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
