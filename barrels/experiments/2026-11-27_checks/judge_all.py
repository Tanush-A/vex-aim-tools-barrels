#!/usr/bin/env python3
"""The standard judge with the paint checks on (plan: PREREG.md, yardsticks J1-J3 and the extreme conditions).

    cd barrels && env PYTHONPATH=src python experiments/2026-11-27_checks/judge_all.py <contrast export> [--jobs 8] [--only fixed,hand,contrast]

``<contrast export>``: a folder holding ``contrast.py`` (src/barrels/contrast.py of branch wip/exp-contrast) and
``candidate.py`` + ``common.py`` (its experiments/2026-11-26_contrast/), unchanged, e.g.

    mkdir -p X && for f in src/barrels/contrast.py experiments/2026-11-26_contrast/candidate.py experiments/2026-11-26_contrast/common.py; do
        git show wip/exp-contrast:barrels/$f > X/$(basename $f); done

Every detector is run on every train frame (ordinary, extreme, unlisted) once, in parallel; the judge's own
``compare`` then makes each judgement from those runs (the same tables and verdict as ``judge.judge``).

- J1 the fixed colors: today's default against the default with each arm's switches on.
- J2 the hand thresholds (per condition, the median of its slider labels, as experiments/2026-11-26_judge S3): the hand
  thresholds with DetConfig defaults against the same with each arm on. In-sample by nature, as there.
- J3 the contrast winner (``candidate.detect_frame``, setting BEST): without the checks against with each arm on
  (the checks inside every ``detector.detect`` call it makes); also each against today's default.
The extreme conditions are printed by every judgement (report only).

Outputs: results/2026-11-27_checks/judge_<name>/ (judge.md, judge.json, changes.csv), boxes.json (every box of
every detector on every frame, for the contact sheets), judges.md (one table)."""
from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(HERE))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import hsrange as hx  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
import arms as am  # noqa: E402

assert str(Path(det.__file__).resolve()).startswith(str(BARRELS)), det.__file__
OUT = BARRELS / "results" / "2026-11-27_checks"
CAM = geo.AIM_4A8B6118_BOXFIT
_S: dict = {}


def load_contrast(folder: Path):
    """contrast.py as ``barrels.contrast`` (its relative imports then resolve to this checkout's package), then
    common.py and candidate.py of the contrast experiment."""
    folder = Path(folder).resolve()
    import barrels
    spec = importlib.util.spec_from_file_location("barrels.contrast", folder / "contrast.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["barrels.contrast"] = mod
    spec.loader.exec_module(mod)
    barrels.contrast = mod
    sys.path.insert(0, str(folder))
    import candidate  # noqa: F401
    return candidate


def hand_thresholds(stems: list[str]) -> dict[str, tuple]:
    """condition -> the six numbers: the median of the slider labels of that condition's train frames (as
    experiments/2026-11-26_judge/run.py, S3)."""
    by = defaultdict(list)
    for s in stems:
        if io.hs_path(s).exists():
            d = io.load_hs(s, check_image=False)
            by[ct.condition_of(s)].append([d["orange"]["h_lo"], d["orange"]["h_hi"], d["orange"]["s_lo"], d["blue"]["h_lo"], d["blue"]["h_hi"], d["blue"]["s_lo"]])
    return {c: tuple(int(round(x)) for x in np.median(np.array(v, float), 0)) for c, v in sorted(by.items())}


def cfgs() -> dict[str, det.DetConfig]:
    return {"": det.DetConfig(), **{a: dataclasses.replace(det.DetConfig(), **o) for a, o in am.ARMS.items()}}


def _init(hand: dict, contrast_dir: str | None, which: tuple) -> None:
    import cv2
    cv2.setNumThreads(1)
    base = hl.adopted_model()
    _S["fixed"] = base
    _S["hand"] = {c: hl.model_from_thresholds(base, hx.nested(dict(zip(hx.THRESHOLDS, six)))) for c, six in hand.items()}
    _S["cfgs"] = cfgs()
    _S["which"] = which
    if contrast_dir and "contrast" in which:
        _S["cand"] = load_contrast(Path(contrast_dir))


def _contrast(frame, cfg: det.DetConfig) -> list:
    cand = _S["cand"]

    class FW(cand.FrameWork):
        def _detect(self, mask):
            return det.detect(mask, cfg, CAM)
    return FW(frame).detect(cand.BEST)


def work(stem: str) -> tuple[str, dict]:
    frame = jg.load_frame(stem)
    out: dict = {}
    masks = {"fixed": pl.segment(frame, _S["fixed"])[0]}
    hm = _S["hand"].get(ct.condition_of(stem))
    masks["hand"] = pl.segment(frame, hm)[0] if hm is not None else masks["fixed"]
    for a, cfg in _S["cfgs"].items():
        for src in ("fixed", "hand"):
            if src in _S["which"]:
                out[f"{src}{'_' + a if a else ''}"] = det.detect(masks[src], cfg, CAM)
        if "contrast" in _S["which"]:
            out[f"contrast{'_' + a if a else ''}"] = _contrast(frame, cfg)
    return stem, {k: [[int(b.color), [int(v) for v in b.bbox], sorted(b.flags), b.source, float(b.confidence)] for b in v] for k, v in out.items()}


def to_barrels(rows) -> list:
    return [dtp.Barrel(color=c, bbox=tuple(bb), flags=frozenset(fl), source=src, confidence=cf) for c, bb, fl, src, cf in rows]


DESCRIBE = {"fixed": "today's default (the adopted color model, DetConfig defaults)",
            "hand": "the hand thresholds per condition (median of its slider labels), DetConfig defaults",
            "contrast": "the contrast winner (wip/exp-contrast, candidate.detect_frame, setting BEST), DetConfig defaults"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("contrast_dir")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default="fixed,hand,contrast")
    args = ap.parse_args()
    which = tuple(args.only.split(","))
    OUT.mkdir(parents=True, exist_ok=True)
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    jg.require_train(stems)
    truth = jg.load_truth(stems)
    hand = hand_thresholds(frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED] + frames[cnd.EXCLUDED])
    boxes: dict = {}
    with Pool(args.jobs, initializer=_init, initargs=(hand, args.contrast_dir, which)) as pool:
        for i, (s, r) in enumerate(pool.imap_unordered(work, stems, chunksize=1)):
            boxes[s] = r
            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{len(stems)}", flush=True)
    bpath = OUT / f"boxes_{'_'.join(which)}.json"
    bpath.write_text(json.dumps(boxes) + "\n")
    names = sorted({k for r in boxes.values() for k in r})
    runs = {}
    for n in names:
        src, _, a = n.partition("_")
        r = jg.Run(n, DESCRIBE[src] + (f"; paint checks {a}: {am.DESCRIBE[a]}" if a else ""))
        for s in stems:
            r.boxes[s] = to_barrels(boxes[s][n])
            r.counts[s] = ct.classify_frame(s, r.boxes[s], truth.gts[s], truth.clean[s])
        runs[n] = r
    pairs = []
    for src in which:
        for a in am.ARMS:
            pairs.append((src, f"{src}_{a}"))
        if src != "fixed":
            pairs.append(("fixed", src))
            for a in ("SL", "SLm"):
                pairs.append(("fixed", f"{src}_{a}"))
    L = ["# Every judgement of the checks experiment", "", "Train frames only; the standard pass rule (`judge.compare`, stored margins). Found = placements "
         "(per frame in brackets). Extreme conditions: report only.", "",
         "| baseline | candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel (per frame) | empty: clean / with clutter | places that moved | extreme: found per frame, before → after; lost |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for b, c in pairs:
        j = jg.compare(runs[b], runs[c], frames, truth)
        jg.write(j, OUT / f"judge_{c}_vs_{b}")
        t0, t1 = j.total
        g = sum(1 for x in j.changes if x.judged and x.kind == "gained")
        lo = sum(1 for x in j.changes if x.judged and x.kind == "lost")
        moved = "; ".join(f"{p} {v[0].found_w:g} → {v[1].found_w:g}" for p, v in j.places.items() if abs(v[0].found_w - v[1].found_w) > 1e-9)
        ex0 = sum(v[0].found for v in j.report_only.values())
        ex1 = sum(v[1].found for v in j.report_only.values())
        exl = sum(1 for x in j.changes if not x.judged and x.kind == "lost")
        L.append(f"| {b} | {c} | **{j.verdict.result}** | {t0.found_w:.2f} → {t1.found_w:.2f} | {t0.found} → {t1.found} | {g} / {lo} | "
                 f"{t0.extra_w:.2f} → {t1.extra_w:.2f} ({t0.extra} → {t1.extra}) | {t0.clean_empty} → {t1.clean_empty} / {t0.cluttered_empty_w:.2f} → {t1.cluttered_empty_w:.2f} | {moved} | {ex0} → {ex1}; {exl} |")
        print(L[-1], flush=True)
    (OUT / f"judges_{'_'.join(which)}.md").write_text("\n".join(L) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
