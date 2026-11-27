#!/usr/bin/env python3
"""ONE TABLE: what is better where (TODO step 6). Rows = data set x scenario; columns = found / missed / false /
width ratio / bottom error for a candidate and a baseline side by side, and the difference.

    python barrels/tools/report.py                                   # what runs today vs the v1 front end
    python barrels/tools/report.py --base-model default --base-det body_width=1.0    # today vs today with boxes at most one barrel wide
    python barrels/tools/report.py --cand-det stripe_merge=1.68 --base-model default # a detector number vs today
    python barrels/tools/report.py --cand-model results/<x>/config.json --base-model default   # a new color model vs today
    python barrels/tools/report.py --sets CAMPUS,DAVE --out          # fewer sets; also write results/<date>_eval_report/

    python barrels/tools/report.py --vendor                          # today vs the robot's built-in (vendor) detector
    python barrels/tools/report.py --gate                            # the never-regress check on today's defaults
    python barrels/tools/report.py --gate --cand-det stripe_merge=1.68  # ... on a candidate, before it becomes the default
    python barrels/tools/report.py --save-baseline                   # store today's numbers as the baseline the check compares with

An arm is a color-model file plus DetConfig overrides. --cand-model / --base-model take a results config.json,
or the words ``default`` (worldmap_bridge.DEFAULT_MODEL, what runs today), ``v1`` (V1_MODEL) or ``vendor``.
--cand-det / --base-det take DetConfig fields as field=value (repeat the flag or separate with commas). DetConfig holds the
detector's 20 numbers; its on/off switches were removed on 2026-11-26 (naming one stops with a message; the detector with
switches is at the git tag pre-collapse-2026-11-26).
Defaults: candidate = default model + DetConfig(); baseline = v1 model + DetConfig().

The vendor arm (``--vendor`` = ``--base-model vendor``) runs nothing: it reads the boxes the robot's own detector
reported for each frame (data/vendor/<stem>_vendor.json, saved by ``tm save``) and scores them by the same rule
against the same labels. Both arms are then scored only on the frames that have a vendor file; the footer says
how many of each set do. Under the table it prints two looser counts (found by overlap alone, found by position),
because the vendor may not draw its boxes the way our labels are drawn. ``--loose`` prints them for any two arms.

The never-regress check (``--gate``) runs the candidate, compares it row by row with the stored baseline
(results/baseline/baseline.json) and exits 1 when a scenario row of a protected set (results/baseline/protected.json:
HOME, CAMPUS) lost a found barrel or gained a false box, or when any set gained a box on an empty frame. Other sets
are listed for information; rows that are not in the baseline are "new" and never fail. Exit 0 = pass, 2 = no
baseline. ``--save-baseline`` stores the candidate's numbers (normally today's defaults, right after a merge); it
refuses to replace a baseline with a worse one unless ``--force`` is given. Code: src/barrels/gate.py.

Data sets are found by themselves: every ``{robot}_{light}_{surface}`` group that has box labels
(data/labels/*_boxes.json) is a block of rows — HOME (4A8B_window_light), CAMPUS (4A8B_campus_light), DAVE*
(indicative), and any new session. Train frames only: test frames are refused unless ``--split test`` is given
(a planned look, EVAL.md rule 5). The metrics are eval_det's v2 rule, unchanged; this is presentation.
Code: src/barrels/report.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import cv, gate as gt, io, report as rp, worldmap_bridge as wb  # noqa: E402

MODEL_WORDS = {"default": wb.DEFAULT_MODEL, "v1": wb.V1_MODEL}
VENDOR_WORD = "vendor"


def model_path(text: str) -> Path:
    if text in MODEL_WORDS:
        return MODEL_WORDS[text]
    p = Path(text)
    if not p.exists() and (io.PKG_ROOT / text).exists():
        p = io.PKG_ROOT / text
    if not p.exists():
        raise SystemExit(f"no such model file: {text} (a results config.json, or one of: {', '.join(MODEL_WORDS)}, {VENDOR_WORD})")
    return p


def make_arm(name: str, model: str, det_items: list[str]) -> rp.Arm:
    """A detector arm from a model word / file and DetConfig overrides, or the vendor arm for the word ``vendor``."""
    if model == VENDOR_WORD:
        if det_items:
            raise SystemExit(f"the vendor arm reads saved boxes and has no DetConfig: drop the --{name[:4]}-det option")
        return rp.vendor_arm(name)
    return rp.Arm(name, model_path(model), rp.parse_det_overrides(det_items))


def run_gate(args, cand: rp.Arm) -> int:
    """--gate and --save-baseline: the candidate arm alone, on every data set, against the stored baseline."""
    if args.gate and args.save_baseline:
        raise SystemExit("--gate checks against the stored baseline, --save-baseline replaces it: give one of the two")
    if args.sets or args.split != "train" or args.home_protocol != "loso" or cand.is_vendor:
        raise SystemExit("--gate and --save-baseline always use every data set, the train frames, the leave-one-scene-out home "
                         "protocol and a detector arm: drop --sets / --split / --home-protocol / the vendor arm")
    path = Path(args.baseline) if args.baseline else gt.BASELINE_PATH
    protected = gt.load_protected(path.parent / gt.PROTECTED_PATH.name)
    old = gt.load_baseline(path) if path.exists() else None
    if args.gate and old is None:
        print(f"no stored baseline at {path}: save one first with  python barrels/tools/report.py --save-baseline")
        return 2
    rep = rp.make_report(cand, cand)            # the same arm twice = it runs once
    if not rep.rows:
        print("no labeled frames to check"); return 2
    now = gt.snapshot(rep, made=dt.date.today().isoformat())
    if args.gate:
        res = gt.compare(old, now, protected)
        print(gt.format_gate(res))
        return 0 if res.passed else 1
    if old is not None:
        res = gt.compare(old, now, protected)
        print(gt.format_gate(res, title="NEW BASELINE against the one it replaces"))
        if not res.passed and not args.force:
            print(f"\nNOT SAVED: the new numbers are worse than the stored baseline. {path} is unchanged. "
                  "If this is intended (frames or labels changed, and the table was checked by eye), repeat with --force.")
            return 1
        print()
    gt.save_baseline(now, path)
    home = next((r for r in now["rows"] if r["label"] == "HOME" and not r["scene"]), None)
    print(f"baseline saved to {path} (git {now['git']}, {now['made']}; {len(now['rows'])} rows"
          + (f"; HOME found {home['found']} of {home['barrels']}" if home else "") + "). Commit it.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cand-model", default="default", help="candidate color model: config.json path, 'default', 'v1', or 'vendor' (default: default)")
    ap.add_argument("--base-model", default="v1", help="baseline color model: config.json path, 'default', 'v1', or 'vendor' (default: v1)")
    ap.add_argument("--cand-det", action="append", default=[], metavar="FIELD=VALUE", help="DetConfig override(s) for the candidate")
    ap.add_argument("--base-det", action="append", default=[], metavar="FIELD=VALUE", help="DetConfig override(s) for the baseline")
    ap.add_argument("--vendor", action="store_true",
                    help="compare the candidate with the robot's built-in detector: the same as --base-model vendor (frames with a vendor file only)")
    ap.add_argument("--loose", action="store_true",
                    help="also print the two looser counts (found by overlap alone; found by position) for any two arms; always on with a vendor arm")
    ap.add_argument("--sets", default="", help="only these data sets, comma-separated (HOME, CAMPUS, DAVE or a {robot}_{light}_{surface} key)")
    ap.add_argument("--split", choices=("train", "test"), default="train", help="train (default). 'test' opens the held-out frames: only for a planned look")
    ap.add_argument("--home-protocol", choices=("loso", "fixed"), default="loso",
                    help="HOME frames: loso = leave-one-scene-out re-fit of the color model (the published home number; default); fixed = the model file as it is")
    ap.add_argument("--out", nargs="?", const="eval_report", default=None, metavar="NAME",
                    help="also write report.md / .csv / .json to results/<today>_<NAME>/ (NAME defaults to eval_report; an absolute path is used as it is)")
    ap.add_argument("--gate", action="store_true",
                    help="the never-regress check: run the candidate and compare it with the stored baseline, row by row; exit 1 when a protected row got worse")
    ap.add_argument("--save-baseline", action="store_true", help="store the candidate's numbers (normally today's defaults) as the baseline --gate compares with")
    ap.add_argument("--force", action="store_true", help="with --save-baseline: replace the stored baseline even when the new numbers are worse")
    ap.add_argument("--baseline", default=None, metavar="PATH", help=f"the baseline file for --gate / --save-baseline (default: {gt.BASELINE_PATH})")
    args = ap.parse_args(argv)
    try:
        cand = make_arm("candidate", args.cand_model, args.cand_det)
        if args.gate or args.save_baseline:
            return run_gate(args, cand)
        base = make_arm("baseline", VENDOR_WORD if args.vendor else args.base_model, args.base_det)
    except ValueError as e:
        raise SystemExit(str(e))
    rep = rp.make_report(cand, base, split=args.split, only_sets=[x for x in args.sets.split(",") if x] or None,
                         home_protocol=args.home_protocol, loose=args.loose)
    if not rep.rows:
        if rep.vendor is not None:
            print(f"no frame to compare: none of the {sum(rep.vendor.total.values())} selected frames has a usable vendor file in {io.VENDOR_DIR}")
            for line in rp.vendor_lines(rep)[:2]:
                print(line)
        else:
            print("no labeled frames to report on")
        return 1
    print(rp.format_text(rep))
    if args.out is not None:
        out = Path(args.out) if Path(args.out).is_absolute() else cv.fresh_dir(io.PKG_ROOT / "results" / f"{dt.date.today().isoformat()}_{args.out}")
        rp.write_all(rep, out, title=f"Eval report: {cand.describe()}  vs  {base.describe()}")
        print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
