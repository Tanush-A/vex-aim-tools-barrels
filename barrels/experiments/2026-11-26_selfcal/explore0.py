"""Exploration 0 (in-sample, before PREREG): what pass 1 finds per frame, with which flags. Train frames only."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
MODEL = hl.adopted_model()
fr = jg.train_frames()
stems = fr["ordinary"] + fr["extreme"]
truth = jg.load_truth(stems)
flagc = collections.Counter()
per = collections.defaultdict(collections.Counter)
for s in stems:
    f = jg.load_frame(s)
    mask, _ = pl.segment(f, MODEL)
    boxes = det.detect(mask, det.DetConfig(), CAM)
    fc = ct.classify_frame(s, boxes, truth.gts[s], truth.clean[s])
    c = ct.condition_of(s)
    sure = [b for b in boxes if not b.flags]
    sure_bad = [(b, st) for b, st in zip(boxes, fc.boxes) if not b.flags and st != ct.FOUND]
    for b, st in zip(boxes, fc.boxes):
        flagc[(tuple(sorted(b.flags)), b.source, st)] += 1
    per[c]["frames"] += 1
    per[c]["frames_with_barrels"] += bool(truth.gts[s])
    per[c]["gt"] += len(truth.gts[s])
    per[c]["found"] += fc.n_gt(ct.FOUND)
    per[c]["frames_with_sure"] += bool(sure) and bool(truth.gts[s])
    per[c]["sure_on_empty"] += len(sure) if not truth.gts[s] else 0
    per[c]["sure_bad"] += len(sure_bad)
    print(s, "gt", "".join(x[0] for x in fc.gt), "clean" if truth.clean[s] else "CLUTTER", "| boxes",
          [(dtp.COLOR_NAMES[b.color][0], sorted(b.flags), st[:2]) for b, st in zip(boxes, fc.boxes)])
print()
for k, v in sorted(flagc.items(), key=lambda kv: -kv[1]):
    print(v, k)
print()
for c, v in per.items():
    print(f"{c:24s} frames {v['frames']:3d} with barrels {v['frames_with_barrels']:3d} gt {v['gt']:3d} found {v['found']:3d} "
          f"frames with a sure box {v['frames_with_sure']:3d} sure boxes on empty {v['sure_on_empty']} sure not-found {v['sure_bad']}")
