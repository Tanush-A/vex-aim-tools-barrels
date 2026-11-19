"""2026-11-19 (A5), the mechanics of ``cap_seen_bottom`` on synthetic masks (its quality is judged by eval numbers): a
narrow cap's bottom estimate comes from its top row; its own color seen ending beside the front barrel is the bottom
also when it is further from that estimate than the tolerance, inside two limits."""
import dataclasses

import numpy as np

from barrels import detector as det, io
from barrels.detect_types import Barrel
from test_detector import CAM, CAP, _behind, _cap, paint_barrel

OFF = dataclasses.replace(CAP, cap_seen_bottom=False)
ON = dataclasses.replace(CAP, cap_seen_bottom=True)


def _scene(seen=0.55, front_below=20):
    """A narrow blue cap (the left `seen` of a barrel 22 cm away) and a found orange barrel over its right side whose
    bottom edge is `front_below` px under the bottom the cap's top row predicts. Returns the numbers a test needs."""
    mask, r, x0, n = _cap(seen)
    top, bottom, H = int(round(r.top)), int(round(r.bottom)), r.bottom - r.top
    front = Barrel(color=io.ORANGE, bbox=(x0 + n - 5, top + 2, x0 + n + 60, bottom + front_below))
    tol = max(CAP.bottom_tol_min_px, CAP.bottom_tol * H)
    return mask, r, x0, n, top, bottom, front, tol


def test_seen_end_beside_the_front_barrel_is_the_bottom_when_the_top_row_estimate_is_off():
    """Home cluster_01 in small: the lower body shows beside the front barrel and ends further above the top-row bottom
    than the tolerance. Before: the top-row bottom is drawn. Now: the seen end."""
    mask, r, x0, n, top, bottom, front, tol = _scene()
    end = bottom - int(tol) - 3
    mask[int(round(r.stripe_bottom)):end, x0:x0 + 8] = io.BLUE
    old = det.caps_behind(mask, [front], [], CAM, OFF)
    assert len(old) == 1 and abs(old[0].bbox[3] - bottom) <= 1
    out = det.caps_behind(mask, [front], [], CAM, ON)
    assert len(out) == 1 and out[0].bbox[3] == end and out[0].bbox[:3] == old[0].bbox[:3]      # only the bottom moves


def test_cap_dropped_because_the_front_barrel_no_longer_stood_nearer_is_found():
    """The front barrel's bottom is at the row the top row predicts for the cap, so with that bottom nothing "stands
    nearer" and the cap is dropped. With the seen end as the bottom the front barrel stands nearer."""
    mask, r, x0, n, top, bottom, front, tol = _scene(front_below=0)
    end = bottom - int(tol) - 3
    mask[int(round(r.stripe_bottom)):end, x0:x0 + 8] = io.BLUE
    log = []
    assert det.caps_behind(mask, [front], [], CAM, OFF, log) == [] and "not_hidden" in [e["why"] for e in log]
    out = det.caps_behind(mask, [front], [], CAM, ON)
    assert len(out) == 1 and out[0].bbox[3] == end and {"occluded", "bottom_inferred"} <= out[0].flags


def test_color_inside_the_front_barrels_box_is_not_this_barrels_bottom():
    """The same color ending at the same row, but in columns inside the front barrel's box (its stripe): not read."""
    mask, r, x0, n, top, bottom, front, tol = _scene()
    end = bottom - int(tol) - 3
    mask[int(round(r.stripe_bottom)):end, front.bbox[0]:x0 + n] = io.BLUE
    out = det.caps_behind(mask, [front], [], CAM, ON)
    assert len(out) == 1 and abs(out[0].bbox[3] - bottom) <= 1


def test_seen_end_above_the_smallest_barrel_that_shows_this_width_is_not_used():
    """0.75 of the width shows, so the barrel is at least 0.75 of its height tall; color ending above that is not its bottom."""
    mask, r, x0, n, top, bottom, front, tol = _scene(seen=0.75)
    front = Barrel(color=io.ORANGE, bbox=(x0 + n // 3, top + 2, x0 + n + 60, bottom + 20))     # in front of most of it, so the cap is kept
    least = top + CAM.expected_barrel_height_px(d_axis_mm=CAM.f * det.geo.BARREL_BULGE_DIAMETER_MM / n)
    start, end = int(round(r.stripe_top)) + 5, int(least) - 3            # a patch of the color under the cap (not joined to it), ending too high
    assert end - start >= 3 and end < bottom - tol
    mask[start:end, x0:x0 + 8] = io.BLUE
    out = det.caps_behind(mask, [front], [], CAM, ON)
    assert len(out) == 1 and abs(out[0].bbox[3] - bottom) <= 1


def test_color_running_on_below_the_estimate_is_not_used():
    mask, r, x0, n, top, bottom, front, tol = _scene()
    mask[int(round(r.stripe_bottom)):bottom + 40, x0:x0 + 8] = io.BLUE
    out = det.caps_behind(mask, [front], [], CAM, ON)
    assert out == [] or abs(out[0].bbox[3] - bottom) <= 1


def test_a_seen_end_that_agrees_and_a_cap_seen_whole_are_untouched():
    mask, r, x0, n, top, bottom, front, tol = _scene()
    mask[int(round(r.stripe_bottom)):bottom - 5, x0:x0 + 8] = io.BLUE              # inside the tolerance: today's test takes it
    assert det.caps_behind(mask, [front], [], CAM, ON) == det.caps_behind(mask, [front], [], CAM, OFF)
    for dx in (0, 15, 30):                                                          # a barrel behind another, its cap seen whole
        scene = _behind(dx)[0]
        assert det.detect(scene, ON, CAM) == det.detect(scene, OFF, CAM)
    one = np.zeros((480, 640), np.uint8); paint_barrel(one, 150, 320)
    assert det.detect(one, ON, CAM) == det.detect(one, OFF, CAM)
