"""The bottom-edge experiment flag (2026-11-26_bottom, rule low_uncut; ported behind DetConfig.bottom_rule for
experiments/2026-11-27_fusion). Off by default: the seen row is drawn."""
import pytest

from barrels import detector as det


def test_off_by_default_draws_the_seen_row():
    assert det.DetConfig().bottom_rule == ""
    assert det.drawn_bottom(120, 100.0, 50.0, det.DetConfig()) == 120


def test_low_uncut_draws_the_predicted_row_for_a_bottom_far_below():
    cfg = det.DetConfig(bottom_rule="low_uncut")
    assert det.drawn_bottom(110, 100.0, 50.0, cfg) == 100          # 10 px below, tolerance 5 px
    assert det.drawn_bottom(104, 100.0, 50.0, cfg) == 104          # within the scorer's tolerance
    assert det.drawn_bottom(90, 100.0, 50.0, cfg) == 90            # above: as today
    assert det.drawn_bottom(110, 100.0, 50.0, cfg, reading_cut=True) == 110   # a stripe cut by the frame side
    assert det.drawn_bottom(103, 100.0, 10.0, cfg) == 103          # the 3 px floor


def test_unknown_rule_is_refused():
    with pytest.raises(ValueError):
        det.DetConfig(bottom_rule="both")
