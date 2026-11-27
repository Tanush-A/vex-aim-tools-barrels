"""The verify step (experiments/2026-11-24_occl_strict): a barrel cannot be seen through a nearer barrel, and a box
placed from a guessed side needs a second reading. Mechanics on synthetic masks: the fake of the real false boxes (a
nearer barrel's upper body read as the stripe of a barrel of the other color, with clutter of that color above it) must
be dropped; a real barrel behind a nearer one, whose visible part lies outside the nearer one's outline, must stay.
Quality is judged by the experiment."""
import numpy as np

from barrels import detector as det, io
from barrels.detect_types import Barrel
from test_detector import CAM, paint_barrel, whys


def _shifted_reading():
    """occlx_17 in miniature: a blue barrel (orange stripe) standing alone, and a strip of orange clutter right above it
    (the wall seen past the table's end). Blue upper body between orange clutter above and the orange stripe below is
    "a blue stripe with orange body above and below": a smaller orange barrel standing behind, read from the blue
    barrel's own picture."""
    mask = np.zeros((480, 640), np.uint8)
    box = paint_barrel(mask, 260, 320, body=io.BLUE)
    x0, top, x1, _ = box
    hw = int(0.3 * (x1 - x0))
    mask[top - 12:top + 5, 320 - hw:320 + hw] = io.ORANGE      # orange clutter over the barrel's top rows, 0.6 of its width
    return mask, box


def test_a_nearer_barrels_upper_body_read_as_a_stripe_is_dropped():
    mask, box = _shifted_reading()
    log: list = []
    after = det.detect(mask, cam=CAM, log=log)
    assert len(after) == 1 and after[0].color == io.BLUE and det.box_iou(after[0].bbox, box) > 0.8
    assert any(e["stage"] == "barrel" and e["why"] == "kept" and e["body"] == io.ORANGE for e in log)       # the shifted reading was made ...
    assert any(e["stage"] == "verify" and e["why"] == "front" and e["body"] == io.ORANGE for e in log)      # ... and dropped here


def test_verify_front_drops_evidence_that_is_the_nearer_barrels_own_picture():
    """Directly: B's evidence (its "stripe") is the blue upper body inside the nearer blue barrel F: all of it explained."""
    mask = np.zeros((480, 640), np.uint8)
    fb = paint_barrel(mask, 200, 320, body=io.BLUE)
    F = Barrel(color=io.BLUE, bbox=fb, source="det2")
    r = CAM.barrel_rows(200)
    ev = (fb[0] + 6, fb[1] + 3, fb[2] - 6, int(r.stripe_top))     # the blue upper body, inside F
    B = Barrel(color=io.ORANGE, bbox=(fb[0], fb[1] - 15, fb[2], int(r.stripe_bottom)), source="det2")
    log = [{"stage": "barrel", "why": "kept", "bbox": fb, "box": fb}, {"stage": "barrel", "why": "kept", "bbox": ev, "box": B.bbox}]
    assert det.verify_front(mask, [F, B], log, CAM) == [F]


def test_a_real_barrel_behind_whose_stripe_shows_beside_the_nearer_one_stays():
    """An orange barrel behind and to the left of a nearer blue barrel: its stripe shows outside the blue barrel's
    outline. That is its own evidence; it stays."""
    mask = np.zeros((480, 640), np.uint8)
    back = paint_barrel(mask, 260, 300, body=io.ORANGE)
    front = paint_barrel(mask, 190, 330, body=io.BLUE)
    log: list = []
    on = det.detect(mask, cam=CAM, log=log)
    assert whys(log, "verify") == []
    assert any(b.color == io.ORANGE and det.box_iou(b.bbox, back) > 0.5 for b in on)
    assert any(b.color == io.BLUE and det.box_iou(b.bbox, front) > 0.8 for b in on)


def test_a_box_whose_evidence_is_outside_every_nearer_outline_is_kept_and_order_is_nearest_first():
    mask = np.zeros((480, 640), np.uint8)
    fb = paint_barrel(mask, 200, 200, body=io.BLUE)
    bb = paint_barrel(mask, 300, 420, body=io.ORANGE)
    F = Barrel(color=io.BLUE, bbox=fb, source="det2")
    B = Barrel(color=io.ORANGE, bbox=bb, source="det2")
    log = [{"stage": "barrel", "why": "kept", "bbox": fb, "box": fb}, {"stage": "barrel", "why": "kept", "bbox": bb, "box": bb}]
    assert det.verify_front(mask, [B, F], log, CAM) == [F, B]           # sorted left to right, nothing dropped


def test_a_single_barrel_is_untouched():
    mask = np.zeros((480, 640), np.uint8)
    truth = paint_barrel(mask, 200, 320, body=io.ORANGE)
    log: list = []
    out = det.detect(mask, cam=CAM, log=log)
    assert [b.bbox for b in out] == [truth] and whys(log, "verify") == []


def test_outline_layout_puts_body_and_stripe_where_the_barrel_has_them():
    F = Barrel(color=io.BLUE, bbox=(300, 100, 350, 150), source="det2")
    lay = det.outline_layout(F, CAM, (480, 640))
    assert lay[105, 325] == io.BLUE and lay[145, 325] == io.BLUE         # upper and lower body
    assert lay[125, 325] in (io.ORANGE, -1)                               # the stripe (or a seam row)
    assert lay[101, 300] == 0 and lay[99, 325] == 0 and lay[125, 360] == 0   # a rounded corner, above, beside


def test_a_partly_seen_stripe_with_no_seen_edge_and_a_guessed_side_is_dropped():
    """verify_readings directly: an occluded stripe box W wide, top and bottom inferred, its stripe 0.3 W and no body joined:
    the distance rests on the stripe row alone. With the body joined to the stripe seen across the width, it stays."""
    mask = np.zeros((480, 640), np.uint8)
    r = CAM.barrel_rows(200)
    W = int(round(r.width_px)); s0, s1 = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    mask[s0 - 3:s0, 300:300 + int(0.3 * W)] = io.ORANGE
    mask[s0:s1, 300:300 + int(0.3 * W)] = io.BLUE
    mask[s1:s1 + 3, 300:300 + int(0.3 * W)] = io.ORANGE
    ev = (300, s0, 300 + int(0.3 * W), s1)
    B = Barrel(color=io.ORANGE, bbox=(300, int(r.top), 300 + W, int(r.bottom)), flags=frozenset({"occluded", "top_inferred", "bottom_inferred"}),
               source="det2")
    log = [{"stage": "barrel", "why": "kept", "bbox": ev, "box": B.bbox}]
    assert det.verify_readings(mask, [B], log, CAM) == []
    mask[s0 - 3:s0, 300:300 + W] = io.ORANGE                   # the upper body seen across the whole width: a second reading
    assert det.verify_readings(mask, [B], log, CAM) == [B]
