"""v1 RGB-box experiment: the default config, the ablation list, and the sweep axes.

BASE is the config written in docs/PROBLEM.md before any tuning. Everything else here is a
deviation from it, scored by leave-one-scene-out CV (barrels.cv) and chosen by the
pre-registered rule in docs/DECISIONS.md (2026-10-19).
"""
from __future__ import annotations

from barrels import pipeline as pl

BASE = pl.Config(
    horizon_row=50, bg_rows=(0, 50), table_rows=80,
    s_min=40, s_min_blue=None, v_min=40,
    table_prior=True, bg_prior=True, k_table=3.0, k_bg=3.0, prior_fit="lowsat",
    scale_floor=4.0, prior_min_frac=0.3,
    box_space="rgb", box_pct=(1.0, 99.0), fit_after_gates=True, fit_max_px_per_image=3000,
    tie="rb_sign", seed=0, refit=None,
)

# (name, overrides): each stage switched off, or an alternative choice, one at a time
ABLATIONS: list[tuple[str, dict]] = [
    ("no_horizon_gate", {"horizon_row": None}),
    ("no_sat_floor", {"s_min": 0}),
    ("no_brightness_gate", {"v_min": 0}),
    ("no_table_prior", {"table_prior": False}),
    ("no_bg_prior", {"bg_prior": False}),
    ("no_priors", {"table_prior": False, "bg_prior": False}),
    ("box_only", {"horizon_row": None, "s_min": 0, "v_min": 0, "table_prior": False, "bg_prior": False}),
    ("prior_fit_all", {"prior_fit": "all"}),
    ("fit_before_gates", {"fit_after_gates": False}),
    ("no_per_image_cap", {"fit_max_px_per_image": None}),
    ("tie_orange", {"tie": "orange"}),
    ("tie_blue", {"tie": "blue"}),
]

# one-at-a-time sweep axes around the current best
SWEEP_AXES: dict[str, list] = {
    "s_min": [30, 40, 50, 60, 70],
    "s_min_blue": [20, 30, 40, 50, 60],
    "v_min": [0, 20, 40, 60, 80, 100],
    "box_pct": [(0.5, 99.5), (1.0, 99.0), (2.0, 98.0), (5.0, 95.0)],
    "k_table": [1.5, 2.0, 2.5, 3.0, 4.0, 6.0],
    "k_bg": [1.5, 2.0, 2.5, 3.0, 4.0, 6.0],
    "table_rows": [40, 80, 120],
    "horizon_row": [25, 50, 66, 90, None],
}

# the joint pair the data analysis said must be swept together
PAIR_AXES = (("s_min_blue", [20, 30, 40, 50]), ("k_bg", [1.5, 2.0, 3.0, 4.0]))
