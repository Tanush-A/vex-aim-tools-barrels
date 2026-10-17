import math

import numpy as np

from barrels import eval as ev
from barrels import io


def test_confusion_counts_and_ignore():
    gt = np.array([[1, 1, 0, 255],
                   [2, 0, 0, 2]], np.uint8)
    pred = np.array([[1, 0, 1, 1],
                     [2, 2, 0, 0]], np.uint8)
    c = ev.confusion(pred, gt)
    o, b = c[io.ORANGE], c[io.BLUE]
    assert (o.tp, o.fp, o.fn) == (1, 1, 1)       # the ignore pixel's FP is not counted
    assert (b.tp, b.fp, b.fn) == (1, 1, 1)
    assert o.valid == b.valid == 7
    assert o.precision == 0.5 and o.recall == 0.5 and abs(o.iou - 1 / 3) < 1e-9


def test_metrics_nan_when_undefined():
    c = ev.Counts()
    assert math.isnan(c.precision) and math.isnan(c.recall) and math.isnan(c.iou) and math.isnan(c.fp_rate)


def test_pred_with_ignore_rejected():
    gt = np.zeros((2, 2), np.uint8)
    pred = np.full((2, 2), 255, np.uint8)
    try:
        ev.confusion(pred, gt)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_negative_frame_fp_rate_and_aggregation():
    gt_neg = np.zeros((4, 4), np.uint8)
    pred_neg = np.zeros((4, 4), np.uint8)
    pred_neg[0, :2] = io.ORANGE                       # 2 of 16 flagged
    gt_pos = np.zeros((4, 4), np.uint8)
    gt_pos[:, :2] = io.ORANGE
    pred_pos = gt_pos.copy()
    r_neg = ev.evaluate_image("4A8B_overhead_black_neg_01", pred_neg, gt_neg)
    r_pos = ev.evaluate_image("4A8B_overhead_black_core_01", pred_pos, gt_pos)
    assert r_neg.negative and not r_pos.negative
    assert r_neg.counts[io.ORANGE].fp_rate == 2 / 16
    aggs = ev.aggregate([r_neg, r_pos])
    assert list(aggs)[0] == "ALL"
    a = aggs["ALL"]
    assert a.n_positive == 1 and a.n_negative == 1
    assert a.pos[io.ORANGE].iou == 1.0                  # negative frame kept out of IoU
    assert a.neg[io.ORANGE].fp_rate == 2 / 16
    assert "overhead_black_neg" in aggs and "overhead_black_core" in aggs


def test_aggregate_pools_pixels_not_images():
    g1 = np.zeros((2, 2), np.uint8); g1[0, 0] = io.BLUE
    p1 = g1.copy()
    g2 = np.full((2, 2), io.BLUE, np.uint8)
    p2 = np.zeros((2, 2), np.uint8)
    r = [ev.evaluate_image("a", p1, g1), ev.evaluate_image("b", p2, g2)]
    agg = ev.aggregate(r)["ALL"]
    assert agg.pos[io.BLUE].recall == 1 / 5           # micro: 1 TP of 5 blue pixels


def test_write_results(tmp_path):
    gt = np.zeros((3, 3), np.uint8); gt[0] = io.ORANGE
    r = ev.evaluate_image("4A8B_overhead_black_core_01", gt.copy(), gt)
    md, csv_path = ev.write_results([r], tmp_path / "run", title="t")
    assert md.exists() and csv_path.exists() and (tmp_path / "run" / "summary.csv").exists()
    text = md.read_text()
    assert "| ALL |" in text and "1.000" in text
