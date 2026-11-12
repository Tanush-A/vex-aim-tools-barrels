#!/usr/bin/env python3
"""ONE TABLE: what is better where (TODO step 6). Rows = data set x scenario; columns = found / missed / false /
width ratio / bottom error for a candidate and a baseline side by side, and the difference.

    python barrels/tools/report.py                                   # what runs today vs the v1 front end
    python barrels/tools/report.py --base-model default --base-det body_width=0      # today vs today without hardening (f)
    python barrels/tools/report.py --cand-det dark_stripe=true --base-model default  # a detector switch vs today
    python barrels/tools/report.py --cand-model results/<x>/config.json --base-model default   # a new color model vs today
    python barrels/tools/report.py --sets CAMPUS,DAVE --out          # fewer sets; also write results/<date>_eval_report/

An arm is a color-model file plus DetConfig overrides. --cand-model / --base-model take a results config.json,
or the words ``default`` (worldmap_bridge.DEFAULT_MODEL, what runs today) or ``v1`` (V1_MODEL). --cand-det /
--base-det take DetConfig fields as field=value (repeat the flag or separate with commas).
Defaults: candidate = default model + DetConfig(); baseline = v1 model + DetConfig().

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
from barrels import cv, io, report as rp, worldmap_bridge as wb  # noqa: E402

MODEL_WORDS = {"default": wb.DEFAULT_MODEL, "v1": wb.V1_MODEL}


def model_path(text: str) -> Path:
    if text in MODEL_WORDS:
        return MODEL_WORDS[text]
    p = Path(text)
    if not p.exists() and (io.PKG_ROOT / text).exists():
        p = io.PKG_ROOT / text
    if not p.exists():
        raise SystemExit(f"no such model file: {text} (a results config.json, or one of: {', '.join(MODEL_WORDS)})")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cand-model", default="default", help="candidate color model: config.json path, 'default' or 'v1' (default: default)")
    ap.add_argument("--base-model", default="v1", help="baseline color model: config.json path, 'default' or 'v1' (default: v1)")
    ap.add_argument("--cand-det", action="append", default=[], metavar="FIELD=VALUE", help="DetConfig override(s) for the candidate")
    ap.add_argument("--base-det", action="append", default=[], metavar="FIELD=VALUE", help="DetConfig override(s) for the baseline")
    ap.add_argument("--sets", default="", help="only these data sets, comma-separated (HOME, CAMPUS, DAVE or a {robot}_{light}_{surface} key)")
    ap.add_argument("--split", choices=("train", "test"), default="train", help="train (default). 'test' opens the held-out frames: only for a planned look")
    ap.add_argument("--home-protocol", choices=("loso", "fixed"), default="loso",
                    help="HOME frames: loso = leave-one-scene-out re-fit of the color model (the published home number; default); fixed = the model file as it is")
    ap.add_argument("--out", nargs="?", const="eval_report", default=None, metavar="NAME",
                    help="also write report.md / .csv / .json to results/<today>_<NAME>/ (NAME defaults to eval_report; an absolute path is used as it is)")
    args = ap.parse_args(argv)
    try:
        cand = rp.Arm("candidate", model_path(args.cand_model), rp.parse_det_overrides(args.cand_det))
        base = rp.Arm("baseline", model_path(args.base_model), rp.parse_det_overrides(args.base_det))
    except ValueError as e:
        raise SystemExit(str(e))
    rep = rp.make_report(cand, base, split=args.split, only_sets=[x for x in args.sets.split(",") if x] or None, home_protocol=args.home_protocol)
    if not rep.rows:
        print("no labeled frames to report on"); return 1
    print(rp.format_text(rep))
    if args.out is not None:
        out = Path(args.out) if Path(args.out).is_absolute() else cv.fresh_dir(io.PKG_ROOT / "results" / f"{dt.date.today().isoformat()}_{args.out}")
        rp.write_all(rep, out, title=f"Eval report: {cand.describe()}  vs  {base.describe()}")
        print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
