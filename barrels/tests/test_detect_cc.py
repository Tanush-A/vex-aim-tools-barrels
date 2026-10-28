import json

import cv2
import numpy as np

from barrels import detect_cc, geometry as geo, io


def test_detect_separated_touching_and_specks(tmp_path):
    m = np.full((480, 640), io.OTHER, np.uint8)
    cv2.circle(m, (150, 250), 30, int(io.ORANGE), -1); m[245:255, 120:180] = io.BLUE     # orange barrel + stripe
    cv2.circle(m, (400, 250), 30, int(io.BLUE), -1); m[245:255, 370:430] = io.ORANGE     # blue barrel + stripe
    m[10:12, 10:12] = io.ORANGE                                                            # speck
    out = detect_cc.detect(m, cam=geo.NOMINAL)
    assert [b.color for b in out] == [io.ORANGE, io.BLUE] and all(b.source == "cc" for b in out)
    assert out[0].bbox == (120, 220, 181, 281) and out[0].confidence > 0.5 and out[0].ground_xy_mm is not None
    # touching -> one box, by design
    m2 = m.copy(); cv2.circle(m2, (210, 250), 30, int(io.ORANGE), -1)
    out2 = detect_cc.detect(m2)
    assert len(out2) == 2 and out2[0].width > 100
    assert detect_cc.detect(np.full((480, 640), io.OTHER, np.uint8)) == []
    p = detect_cc.write_detections(tmp_path, "x", out)
    assert len(json.load(p.open())) == 2


def test_flags_and_closing():
    m = np.full((480, 640), io.OTHER, np.uint8)
    m[400:480, 100:500] = io.ORANGE                                                        # wide, touches the bottom
    b = detect_cc.detect(m)[0]
    assert {"truncated", "top_only"} <= b.flags
    m2 = np.full((480, 640), io.OTHER, np.uint8); m2[200:240, 100:150] = io.BLUE; m2[200:240, 152:200] = io.BLUE
    assert len(detect_cc.detect(m2)) == 2 and len(detect_cc.detect(m2, detect_cc.CCConfig(close_px=5))) == 1
