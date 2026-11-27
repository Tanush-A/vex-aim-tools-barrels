#!/usr/bin/env python3
"""THE STANDARD PASS RULE: is a candidate better than a baseline, worse, or neither? (TODO M3, 2026-11-26)

    python barrels/tools/judge.py --cand-det stripe_merge=1.68                        # a detector number changed, against today's default
    python barrels/tools/judge.py --cand-model results/<x>/config.json                 # a color model file against today's default
    python barrels/tools/judge.py --cand-callable path/to/idea.py:detect_frame         # anything: a function (stem, frame) -> list[Barrel]
    python barrels/tools/judge.py --cand-fit path/to/idea.py:fit                       # anything with fitted numbers: leave one place out
    python barrels/tools/judge.py --cand-model default --base-model default            # today against itself: NO CLEAR DIFFERENCE, nothing changed

Both sides are run on the ordinary train conditions (data/conditions.json; today 17 conditions at 8 places). Extreme
conditions are run and printed, never judged (``--no-extreme`` skips them, about a third faster). Test frames are
refused before any image is opened. It prints and saves: per place and over all places, found under the strict rule
(every placement once, and counted per frame), found with the box off, the boxes that are not on their barrel, the
boxes on empty frames, and every barrel gained and lost; then the clauses with their margins and the verdict.

    VERDICT: PASS                  found is up by more than the noise and nothing is worse by more than the noise
    VERDICT: FAIL                  something is worse by more than the noise
    VERDICT: NO CLEAR DIFFERENCE   nothing moved by more than a change that means nothing moves it

The clauses and their margins: docs/EVAL.md, "The standard pass rule (2026-11-26)". The margins are measured
(results/baseline/margins.json, written by experiments/2026-11-26_noise_floor/run.py).

The candidate is ONE of:
  --cand-model / --cand-det   a color-model file (a results config.json, or ``default`` / ``v1``) and/or DetConfig
                              fields as field=value (repeat or separate with commas), as in tools/report.py
  --cand-callable FILE:NAME   a Python function ``NAME(stem, frame) -> list[barrels.detect_types.Barrel]``; ``frame``
                              is a ``barrels.pipeline.Frame`` (``frame.rgb``: the picture, read-only)
  --cand-fit FILE:NAME        a Python function ``NAME(train_stems, held_place) -> detect_frame``. It is called once
                              per place with the ordinary train frames of the OTHER places (read them with
                              ``barrels.judge.load_frame(stem)`` and ``barrels.io.load_boxes(stem)``), and what it
                              returns is run on the held-out place only. The verdict rests on held-out results.
The baseline is today's default unless --base-model / --base-det / --base-callable say otherwise.

Exit code: 0 = PASS, 1 = FAIL, 3 = NO CLEAR DIFFERENCE (2 = a usage error). The pages go to
results/<today>_judge_<name>/ (judge.md, judge.json, changes.csv); ``--no-save`` only prints.
Code: src/barrels/judge.py (the rule), src/barrels/counting.py (the counting).
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from barrels import cv, io, judge as jg, report as rp, worldmap_bridge as wb  # noqa: E402

MODEL_WORDS = {"default": wb.DEFAULT_MODEL, "v1": wb.V1_MODEL}
EXIT = {jg.PASS: 0, jg.FAIL: 1, jg.NO_CLEAR: 3}


def model_path(text: str) -> Path:
    if text in MODEL_WORDS:
        return MODEL_WORDS[text]
    p = Path(text)
    if not p.exists() and (io.PKG_ROOT / text).exists():
        p = io.PKG_ROOT / text
    if not p.exists():
        raise SystemExit(f"no such model file: {text} (a results config.json, or one of: {', '.join(MODEL_WORDS)})")
    return p


def side(model: str | None, det_items: list[str], call: str | None, what: str):
    """One side from its options: a detect_frame, or None when nothing was said."""
    if call and (model or det_items):
        raise SystemExit(f"give the {what} either as a model file / DetConfig fields or as a function, not both")
    if call:
        fn = jg.load_callable(call)
        try:
            fn.describe = getattr(fn, "describe", "") or f"the function {call}"
        except AttributeError:
            pass
        return fn
    if model or det_items:
        return jg.model_detector(model_path(model or "default"), rp.parse_det_overrides(det_items))
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cand-model", default=None, help="candidate color model: a results config.json, 'default' or 'v1'")
    ap.add_argument("--cand-det", action="append", default=[], metavar="FIELD=VALUE", help="DetConfig override(s) for the candidate")
    ap.add_argument("--cand-callable", default=None, metavar="FILE:NAME", help="candidate = a function NAME(stem, frame) -> list[Barrel] in FILE")
    ap.add_argument("--cand-fit", default=None, metavar="FILE:NAME",
                    help="candidate with fitted numbers = a function NAME(train_stems, held_place) -> detect_frame; judged leave one place out")
    ap.add_argument("--base-model", default=None, help="baseline color model (default: today's)")
    ap.add_argument("--base-det", action="append", default=[], metavar="FIELD=VALUE", help="DetConfig override(s) for the baseline")
    ap.add_argument("--base-callable", default=None, metavar="FILE:NAME", help="baseline = a function NAME(stem, frame) -> list[Barrel] in FILE")
    ap.add_argument("--name", default="candidate", help="what to call the candidate in the pages and in the results folder name")
    ap.add_argument("--no-extreme", action="store_true", help="skip the extreme conditions (they are report only; about a third faster)")
    ap.add_argument("--no-save", action="store_true", help="print only; do not write results/<today>_judge_<name>/")
    ap.add_argument("--out", default=None, metavar="DIR", help="write the pages to this folder instead")
    args = ap.parse_args(argv)
    try:
        fit = jg.load_callable(args.cand_fit) if args.cand_fit else None
        cand = side(args.cand_model, args.cand_det, args.cand_callable, "candidate")
        base = side(args.base_model, args.base_det, args.base_callable, "baseline")
    except ValueError as e:
        raise SystemExit(str(e))
    if (cand is None) == (fit is None):
        raise SystemExit("say what the candidate is: exactly one of --cand-model / --cand-det, --cand-callable, --cand-fit (see --help)")
    j = jg.judge(cand, base, fit=fit, name=args.name, report_only=not args.no_extreme)
    print(jg.format_judgement(j))
    if not args.no_save:
        out = Path(args.out) if args.out else cv.fresh_dir(io.PKG_ROOT / "results" / f"{dt.date.today().isoformat()}_judge_{args.name}")
        jg.write(j, out)
        print("written to", out)
    return EXIT[j.result]


if __name__ == "__main__":
    sys.exit(main())
