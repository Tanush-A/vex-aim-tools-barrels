"""Run one checkout's detector, with its defaults, on every golden input.

    python run_detect.py <path to barrels/src> <out.json> [inputs.pkl]

inputs.pkl (default: next to this script) is made by build_inputs.py. The output holds, per input, the boxes
(color, box, flags, source, confidence) and the reason log (stage, why, box of the candidate)."""
import hashlib
import json
import pickle
import sys
from pathlib import Path

import cv2
import numpy as np

src, out = sys.argv[1], sys.argv[2]
inputs = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).resolve().parent / "inputs.pkl"
sys.path.insert(0, src)
from barrels import detector as det  # noqa: E402

assert det.__file__.startswith(src), (det.__file__, src)
enc = pickle.load(open(inputs, "rb"))
res = {}
for k in sorted(enc):
    m = cv2.imdecode(np.frombuffer(enc[k], np.uint8), cv2.IMREAD_UNCHANGED)
    log = []
    preds = det.detect(m, log=log)
    res[k] = {"boxes": [[int(p.color), [int(v) for v in p.bbox], sorted(p.flags), p.source, round(float(p.confidence), 6)] for p in preds],
              "log": [[str(e.get("stage")), str(e.get("why")), [int(v) for v in e["bbox"]] if e.get("bbox") is not None else None] for e in log]}
json.dump(res, open(out, "w"))
canon = json.dumps({k: v["boxes"] for k, v in res.items()}, sort_keys=True).encode()
print("inputs", len(res), "boxes", sum(len(v["boxes"]) for v in res.values()), "sha256(boxes)", hashlib.sha256(canon).hexdigest()[:16], "from", det.__file__)
