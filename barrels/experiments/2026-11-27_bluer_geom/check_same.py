#!/usr/bin/env python3
"""``stages.found`` draws exactly what ``detector.detect`` draws, on every input of the proof harness, and every
check of ``checks.py`` at its off setting removes nothing.

    python check_same.py <inputs.pkl>
"""
import pickle
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg  # noqa: E402,F401
import checks as ck  # noqa: E402
import stages as sg  # noqa: E402

from barrels import detector as det  # noqa: E402

enc = pickle.load(open(sys.argv[1], "rb"))
bad = 0
n = 0
for k in sorted(enc):
    m = cv2.imdecode(np.frombuffer(enc[k], np.uint8), cv2.IMREAD_UNCHANGED)
    a = det.detect(m)
    fs = sg.found(m)
    b = [f.barrel for f in fs]
    c = ck.apply(fs, m, ck.OFF)
    n += len(a)
    if a != b or b != c:
        bad += 1
        print("DIFFERS", k)
print(f"inputs {len(enc)} boxes {n}: " + ("IDENTICAL BOXES ON EVERY INPUT" if not bad else f"NOT IDENTICAL on {bad}"))
sys.exit(1 if bad else 0)
