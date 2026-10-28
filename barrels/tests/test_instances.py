import cv2
import numpy as np

from barrels import geometry as geo, instances as ins, io

CAM = geo.NOMINAL


def draw_barrel(mask, cx, d_axis, body, stripe=True):
    """Draw a synthetic barrel silhouette (ellipse) with its stripe band at nominal geometry."""
    r = CAM.barrel_rows(d_axis)
    cy = (r.top + r.bottom) / 2
    axes = (int(round(r.width_px / 2)), int(round((r.bottom - r.top) / 2)))
    cv2.ellipse(mask, (int(round(cx)), int(round(cy))), axes, 0, 0, 360, int(body), -1)
    if stripe:
        band = np.zeros(mask.shape, np.uint8)
        cv2.ellipse(band, (int(round(cx)), int(round(cy))), axes, 0, 0, 360, 1, -1)
        band[: int(round(r.stripe_top))] = 0
        band[int(round(r.stripe_bottom)):] = 0
        mask[band > 0] = io.BLUE if body == io.ORANGE else io.ORANGE
    return r


def scene(*barrels, stripe=True):
    m = np.full((480, 640), io.OTHER, np.uint8)
    rows = [draw_barrel(m, cx, d, body, stripe) for cx, d, body in barrels]
    return m, rows


def test_single_barrel():
    m, (r,) = scene((320, 150, io.ORANGE))
    inst, recs, dropped = ins.split_instances(m, CAM)
    assert dropped == 0 and len(recs) == 1
    rec = recs[0]
    assert rec["color"] == "orange" and rec["seed"] == "stripe" and rec["flags"] == []
    assert abs(rec["bbox"][3] - round(r.bottom)) <= 1 and abs(rec["bbox"][1] - round(r.top)) <= 1
    assert ins.check_consistency(m, inst) == {"unassigned_class_px": 0, "outside_mask_px": 0, "ids": [1]}


def test_touching_mixed_colors_and_same_colors():
    W = CAM.barrel_rows(150).width_px
    m, _ = scene((300, 150, io.ORANGE), (300 + W, 150, io.BLUE))
    inst, recs, _ = ins.split_instances(m, CAM)
    assert [r["color"] for r in recs] == ["orange", "blue"] and len(recs) == 2
    m2, _ = scene((300, 150, io.ORANGE), (300 + W, 150, io.ORANGE))       # dumbbell stripe
    inst2, recs2, _ = ins.split_instances(m2, CAM)
    assert len(recs2) == 2 and all(r["color"] == "orange" for r in recs2)
    assert recs2[0]["bbox"][2] <= recs2[1]["bbox"][0] + 3                  # split near the touching line
    # three in a row, left to right ids
    m3, _ = scene((200, 150, io.BLUE), (200 + W, 150, io.ORANGE), (200 + 2 * W, 150, io.ORANGE))
    inst3, recs3, _ = ins.split_instances(m3, CAM)
    assert [r["color"] for r in recs3] == ["blue", "orange", "orange"]
    assert [r["id"] for r in recs3] == [1, 2, 3] and recs3[0]["bbox"][0] < recs3[1]["bbox"][0] < recs3[2]["bbox"][0]


def test_far_barrel_without_stripe_and_noise():
    m, _ = scene((320, 300, io.BLUE), stripe=False)
    m[10:12, 10:12] = io.ORANGE                                            # 4-px speck: label noise
    inst, recs, dropped = ins.split_instances(m, CAM)
    assert len(recs) == 1 and recs[0]["seed"] == "dt" and "no_stripe" in recs[0]["flags"] and recs[0]["color"] == "blue"
    assert dropped == 4 and (inst[10:12, 10:12] == 0).all()


def test_occluded_hint_and_ignore_pixels_belong():
    # hint logic: a short instance touching a tall one is flagged as a possible occlusion
    m, (r,) = scene((320, 100, io.ORANGE))
    inst, recs, _ = ins.split_instances(m, CAM)
    top, bottom = int(r.top), int(r.bottom)
    inst2 = inst.copy(); m2 = m.copy()
    sliver_rows = slice(top - 12, top)                      # a 12-row blue sliver sitting on top of the barrel
    m2[sliver_rows, 300:340] = io.BLUE; inst2[sliver_rows, 300:340] = 2
    recs2 = ins.records_from_inst(inst2, m2, CAM, {1: ("stripe", io.ORANGE), 2: ("dt", None)})
    back = next(x for x in recs2 if x["id"] == 2)
    assert back["color"] == "blue" and ins.HINT_OCCLUDED in back["hints"]
    assert ins.HINT_OCCLUDED not in next(x for x in recs2 if x["id"] == 1)["hints"]
    # a fully hidden barrel leaves no separable sliver: the auto-split merges it (manual fix territory)
    m3 = np.full((480, 640), io.OTHER, np.uint8)
    draw_barrel(m3, 320, 130, io.BLUE); draw_barrel(m3, 320, 100, io.ORANGE)
    assert len(ins.split_instances(m3, CAM)[1]) >= 1
    # ignore (glare) pixels inside a barrel are part of its instance
    m4, (r4,) = scene((320, 100, io.ORANGE))
    m4[int(r4.top) + 5:int(r4.top) + 9, 315:325] = io.IGNORE
    inst4, recs4, _ = ins.split_instances(m4, CAM)
    assert len(recs4) == 1 and (inst4[int(r4.top) + 5:int(r4.top) + 9, 315:325] == 1).all()


def test_empty_truncated_and_deterministic():
    empty = np.full((480, 640), io.OTHER, np.uint8)
    inst, recs, dropped = ins.split_instances(empty, CAM)
    assert recs == [] and inst.max() == 0 and dropped == 0
    m, _ = scene((20, 150, io.BLUE))                                       # half out of the left edge
    _, recs, _ = ins.split_instances(m, CAM)
    assert "truncated" in recs[0]["flags"]
    m2, _ = scene((320, 150, io.ORANGE), (420, 200, io.BLUE))
    a = ins.split_instances(m2, CAM)[0]; b = ins.split_instances(m2, CAM)[0]
    assert (a == b).all()


def test_edit_ops_and_replay():
    W = CAM.barrel_rows(150).width_px
    m, rows = scene((300, 150, io.ORANGE), (300 + W, 150, io.ORANGE))
    inst, recs, _ = ins.split_instances(m, CAM)
    assert len(recs) == 2
    y = int((rows[0].top + rows[0].bottom) / 2)
    p1, p2 = (300, y), (int(300 + W), y)
    merged = ins.merge(inst, [p1, p2])
    assert len(np.unique(merged)) == 2 and merged[y, 300] == merged[y, int(300 + W)]
    split = ins.split_seeded(merged, m, [p1, p2])
    assert len(np.unique(split)) == 3 and split[y, 300] != split[y, int(300 + W)]
    gone = ins.delete(split, p1)
    assert gone[y, 300] == 0 and gone[y, int(300 + W)] > 0
    edits = [{"op": "merge", "points": [p1, p2]}, {"op": "split", "seeds": [p1, p2]},
             {"op": "color", "point": p2, "color": "blue"}, {"op": "flag", "point": p1, "flag": "occluded", "value": True},
             {"op": "delete", "point": (5, 5)}]
    out, overrides, failed = ins.apply_edits(inst, m, edits)
    assert len(failed) == 1 and failed[0]["op"] == "delete"
    assert len(np.unique(out)) == 3
    recs2 = ins.records_from_inst(out, m, CAM, overrides=overrides)
    right = next(r for r in recs2 if r["bbox"][0] > 300)
    left = next(r for r in recs2 if r["bbox"][0] <= 300)
    assert right["color"] == "blue" and "occluded" in left["flags"]
    # replay after an eroded mask still finds the instances by point
    m_er = m.copy(); m_er[cv2.erode(np.isin(m, (1, 2)).astype(np.uint8), np.ones((3, 3), np.uint8)) == 0] = io.OTHER
    inst_er = ins.split_instances(m_er, CAM)[0]
    out2, _, failed2 = ins.apply_edits(inst_er, m_er, edits[:2])
    assert failed2 == [] and len(np.unique(out2)) == 3
