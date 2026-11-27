"""The golden inputs of the collapse check: every class mask the detector is asked about.

    python build_inputs.py <path to barrels/ of a checkout at the tag pre-collapse-2026-11-26> <inputs.pkl>

Built ONCE, with the code as it was before the collapse (the occlusion scenes and the damaged masks come from
experiments/2026-11-19_det_occl/run.py and degrade.py, which name detector switches that no longer exist after it).
Train frames only: every stem is checked against the "test" list of data/splits.json and no test frame is opened.
Output: {key: PNG bytes of a uint8 class mask}. The groups:

    real/         every train frame, segmented by the fixed color model
    real_erode/   the same with one pixel eroded from each color
    real_dilate/  the same with one pixel added to each color
    hand/         the train frames that have hand-set thresholds (slider labels), segmented with those
    pool/         the masks the occlusion scorecard cuts its barrels from
    damage/       those masks damaged by degrade.py, every level, seeds 0 to 2
    scene/        all simulated occlusion scenes of the scorecard
"""
import importlib.util
import pickle
import sys
from pathlib import Path

import cv2
import numpy as np

MAIN = Path(sys.argv[1]).resolve()
OUT = sys.argv[2]
sys.path.insert(0, str(MAIN / "src"))
sys.path.insert(0, str(MAIN / "experiments" / "2026-11-19_det_occl"))
from barrels import degrade as dg, geometry as geo, hslabel as hl, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402

spec = importlib.util.spec_from_file_location("occl_run", MAIN / "experiments" / "2026-11-19_det_occl" / "run.py")
run = importlib.util.module_from_spec(spec)
sys.modules["occl_run"] = run
spec.loader.exec_module(run)

CAM = geo.AIM_4A8B6118_BOXFIT
sp = splits.load_splits()
TEST, TRAIN = set(sp["test"]), sorted(sp["train"])
assert not (TEST & set(TRAIN))
model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
inputs = {}
K = np.ones((3, 3), np.uint8)


def erode(m):
    out = np.zeros_like(m)
    for c in (1, 2):
        out[cv2.erode((m == c).astype(np.uint8), K) > 0] = c
    return out


def dilate(m):
    out = m.copy()
    for c in (1, 2):
        out[(out == 0) & (cv2.dilate((m == c).astype(np.uint8), K) > 0)] = c
    return out


n_real = 0
for s in TRAIN:
    assert s not in TEST
    try:
        img = io.load_image(io.find_image(s))
    except Exception as e:  # noqa: BLE001
        print("no image", s, type(e).__name__)
        continue
    fr = pl.Frame.from_image(img)
    m = pl.segment(fr, model)[0]
    inputs[f"real/{s}"] = m
    inputs[f"real_erode/{s}"] = erode(m)
    inputs[f"real_dilate/{s}"] = dilate(m)
    n_real += 1
    if io.LABELS_DIR.joinpath(f"{s}_hs.json").exists():
        meta = io.load_hs(s)
        t = hl.copy_thresholds(meta)
        inputs[f"hand/{s}"] = pl.segment(fr, hl.model_from_thresholds(model, t, hl.gates_of(model, meta)))[0]
print("real train frames", n_real, "hand", sum(k.startswith("hand/") for k in inputs))

stems = run.train_stems()
segs = run.segmentations(stems)
for pool, d in segs.items():
    for s, m in d.items():
        assert s not in TEST
        inputs[f"pool/{pool}/{s}"] = m
        if pool != "HOME color model":
            boxes = [tuple(b["bbox"]) for b in io.load_boxes(s)["barrels"]]
            for level, dmg in dg.LEVELS.items():
                for seed in range(3):
                    inputs[f"damage/{level}/{seed}/{pool}/{s}"] = dg.damage(m, boxes, dmg, seed)
pools, dropped = run.build_sources(segs)
n = 0
for pool in run.POOLS:
    for i, (key, amount, variant, src, sc) in enumerate(run.scenes_of(pools[pool])):
        inputs[f"scene/{pool}/{i:05d}/{key}/{amount}/{variant}"] = sc.mask
        n += 1
print("scenes", n, "sources", {p: len(v) for p, v in pools.items()})

enc = {k: cv2.imencode(".png", v.astype(np.uint8))[1].tobytes() for k, v in inputs.items()}
pickle.dump(enc, open(OUT, "wb"))
groups = {}
for k in enc:
    groups[k.split("/")[0]] = groups.get(k.split("/")[0], 0) + 1
print("inputs", len(enc), groups, "bytes", sum(map(len, enc.values())))
