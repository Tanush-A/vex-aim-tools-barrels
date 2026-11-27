#!/usr/bin/env python3
"""The true boxes of the simulated scenes of the collapse harness (yardstick d of PREREG.md).

    python scene_truth.py <barrels/ of a checkout AT THE TAG pre-collapse-2026-11-26> <inputs.pkl> <scene_truth.json>

The harness keeps the scenes' masks only. The scenes come from experiments/2026-11-19_det_occl/run.py, which names
detector switches that no longer exist, so this runs with the code at the tag (for example an export made with
``git archive pre-collapse-2026-11-26 barrels``). It rebuilds every scene exactly as build_inputs.py did, checks
that each mask is byte for byte the one in inputs.pkl, and writes per scene the true boxes: the target barrel first,
then the barrels in front of it. Train frames only (the tagged script selects them; no test frame is opened)."""
import importlib.util
import json
import pickle
import sys
from pathlib import Path

import cv2
import numpy as np

MAIN = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(MAIN / "src"))
sys.path.insert(0, str(MAIN / "experiments" / "2026-11-19_det_occl"))
import barrels  # noqa: E402

assert str(Path(barrels.__file__).resolve()).startswith(str(MAIN)), (barrels.__file__, MAIN)
spec = importlib.util.spec_from_file_location("occl_run", MAIN / "experiments" / "2026-11-19_det_occl" / "run.py")
run = importlib.util.module_from_spec(spec)
sys.modules["occl_run"] = run
spec.loader.exec_module(run)

enc = pickle.load(open(sys.argv[2], "rb"))
segs = run.segmentations(run.train_stems())
pools, _ = run.build_sources(segs)
truth, bad = {}, 0
for pool in run.POOLS:
    for i, (key, amount, variant, src, sc) in enumerate(run.scenes_of(pools[pool])):
        k = f"scene/{pool}/{i:05d}/{key}/{amount}/{variant}"
        same = k in enc and np.array_equal(cv2.imdecode(np.frombuffer(enc[k], np.uint8), cv2.IMREAD_UNCHANGED), sc.mask.astype(np.uint8))
        bad += not same
        truth[k] = {"kind": key, "amount": amount, "hidden": round(float(sc.hidden), 3),
                    "truths": [[int(c), [int(v) for v in b]] for c, b in [sc.target] + list(sc.fronts) if b[2] > b[0] and b[3] > b[1]]}
assert bad == 0 and len(truth) == sum(k.startswith("scene/") for k in enc), (bad, len(truth))
json.dump(truth, open(sys.argv[3], "w"))
print("scenes", len(truth), "every mask the same as in inputs.pkl")
