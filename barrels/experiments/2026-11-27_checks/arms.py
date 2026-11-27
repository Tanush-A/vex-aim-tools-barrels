"""The arms of this experiment (plan: PREREG.md): which switches of ``DetConfig`` are on, at which numbers.

P = the numbers the bluer_geom experiment's primary family (G1) picks on all eight places: solidity 0.40, a label
taller than 1.25 x a stripe height with body under 0.6 (its folds disagreed: the bathroom fold took 0.35 / 1.5).
M = the numbers its fixed-color family (G2) picks on all eight places: 0.35, 1.5, 0.6. Both are taken as they are;
nothing here is chosen on what this experiment measures."""
P = {"solid_min": 0.40, "label_stripe": 1.25, "label_body": 0.6}
M = {"solid_min": 0.35, "label_stripe": 1.5, "label_body": 0.6}

ARMS = {
    "S": {"check_solid": True, **P},
    "L": {"check_label": True, **P},
    "SL": {"check_solid": True, "check_label": True, **P},
    "Sm": {"check_solid": True, **M},
    "Lm": {"check_label": True, **M},
    "SLm": {"check_solid": True, "check_label": True, **M},
}
DESCRIBE = {
    "S": "solid paint only, solidity under 0.40 dropped (P)",
    "L": "label only, stripe over 1.25 x a stripe height with body under 0.6 dropped (P)",
    "SL": "both, at P (0.40; 1.25 / 0.6)",
    "Sm": "solid paint only, under 0.35 (M)",
    "Lm": "label only, over 1.5 x with body under 0.6 (M)",
    "SLm": "both, at M (0.35; 1.5 / 0.6)",
}
