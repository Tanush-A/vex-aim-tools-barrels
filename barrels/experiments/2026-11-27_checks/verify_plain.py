#!/usr/bin/env python3
"""The adoption check (plan: PREREG.md): the plain code (the paint checks always on, solid_min 0.40, label 1.5 / 0.6,
the round-2 readings) against the detector before them, on every train frame, with the three color steps.

    cd barrels && env PYTHONPATH=src python experiments/2026-11-27_checks/verify_plain.py <contrast export> [--jobs 8]

"Before" = the boxes of the detector without the checks, stored by round 2 (``results/2026-11-27_checks/round2/
boxes_fixed_hand_contrast.json``: fixed, hand, contrast). "After" = this checkout's ``DetConfig()``. The judge's own
``compare`` makes the judgement for each color step; the expected result is the union of round 2's S (0.40) and Lm
(1.5 / 0.6) removals. Writes results/2026-11-27_checks/plain/verify.md and one judge folder per color step."""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(HERE))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
import judge_all as ja  # noqa: E402

assert not hasattr(det.DetConfig(), "check_solid"), "run this on the plain code (the adoption commit)"
OUT = BARRELS / "results" / "2026-11-27_checks" / "plain"
ROUND2 = BARRELS / "results" / "2026-11-27_checks" / "round2" / "boxes_fixed_hand_contrast.json"
_S: dict = {}


def _init(hand, contrast_dir):
    import cv2
    cv2.setNumThreads(1)
    from barrels import hslabel as hl, hsrange as hx
    base = hl.adopted_model()
    _S["fixed"] = base
    _S["hand"] = {c: hl.model_from_thresholds(base, hx.nested(dict(zip(hx.THRESHOLDS, six)))) for c, six in hand.items()}
    _S["cand"] = ja.load_contrast(Path(contrast_dir))


def work(stem):
    frame = jg.load_frame(stem)
    cfg = det.DetConfig()
    fm = pl.segment(frame, _S["fixed"])[0]
    hm = _S["hand"].get(ct.condition_of(stem))
    out = {"fixed": det.detect(fm, cfg, ja.CAM), "hand": det.detect(pl.segment(frame, hm)[0] if hm is not None else fm, cfg, ja.CAM),
           "contrast": _S["cand"].detect(frame, _S["cand"].BEST)}
    return stem, {k: [[int(b.color), [int(v) for v in b.bbox], sorted(b.flags), b.source, float(b.confidence)] for b in v] for k, v in out.items()}


def main() -> int:
    contrast_dir = sys.argv[1]
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    OUT.mkdir(parents=True, exist_ok=True)
    before = json.loads(ROUND2.read_text())
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    jg.require_train(stems)
    truth = jg.load_truth(stems)
    hand = ja.hand_thresholds(stems + frames[cnd.EXCLUDED])
    after = {}
    with Pool(jobs, initializer=_init, initargs=(hand, contrast_dir)) as pool:
        for s, r in pool.imap_unordered(work, stems, chunksize=1):
            after[s] = r
    L = ["# The plain code against the detector before the paint checks", "",
         "Every train frame (ordinary judged, extreme report only). Expected: the union of round 2's S (0.40) and Lm (1.5 / 0.6).", "",
         "| color step | verdict | found, placements | gained / lost | boxes not on their barrel | frames whose boxes changed | same as expected (round 2 S ∪ Lm) |", "|---|---|---|---|---|---|---|"]
    for src in ("fixed", "hand", "contrast"):
        runs = {}
        for name, box in (("before", lambda s: before[s][src]), ("after", lambda s: after[s][src])):
            r = jg.Run(f"{src}_{name}", f"{src}, {'without' if name == 'before' else 'with'} the paint checks")
            for s in stems:
                r.boxes[s] = ja.to_barrels(box(s))
                r.counts[s] = ct.classify_frame(s, r.boxes[s], truth.gts[s], truth.clean[s])
            runs[name] = r
        j = jg.compare(runs["before"], runs["after"], frames, truth)
        jg.write(j, OUT / f"judge_{src}")
        t0, t1 = j.total
        changed = [s for s in stems if sorted(map(json.dumps, (x[:2] for x in before[s][src]))) != sorted(map(json.dumps, (x[:2] for x in after[s][src])))]
        expect = [s for s in stems if {json.dumps(x[:2]) for x in before[s][src]} - {json.dumps(x[:2]) for x in before[s][f"{src}_S"]}
                  | ({json.dumps(x[:2]) for x in before[s][src]} - {json.dumps(x[:2]) for x in before[s][f"{src}_Lm"]})]
        same = all({json.dumps(x[:2]) for x in after[s][src]} == ({json.dumps(x[:2]) for x in before[s][f"{src}_S"]} & {json.dumps(x[:2]) for x in before[s][f"{src}_Lm"]})
                   for s in stems) if src != "contrast" else "n/a (the contrast path re-runs the detector on a repainted mask)"
        g = sum(1 for x in j.changes if x.judged and x.kind == "gained")
        lo = sum(1 for x in j.changes if x.judged and x.kind == "lost")
        L.append(f"| {src} | **{j.verdict.result}** | {t0.found_w:.2f} → {t1.found_w:.2f} | {g} / {lo} | {t0.extra_w:.2f} → {t1.extra_w:.2f} ({t0.extra} → {t1.extra}) | "
                 f"{len(changed)}: {', '.join(changed) or 'none'} | {same} (expected changes on {len(expect)} frames) |")
        print(L[-1], flush=True)
    (OUT / "verify.md").write_text("\n".join(L) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
