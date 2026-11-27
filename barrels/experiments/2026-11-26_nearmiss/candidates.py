"""The judged candidates of experiment 2026-11-26_nearmiss (TODO C2; plan: PREREG.md in this folder).

    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_nearmiss/candidates.py:fit_partner
    python barrels/tools/judge.py --cand-callable barrels/experiments/2026-11-26_nearmiss/candidates.py:detect_frame

Every candidate builds its own class mask (``barrels.nearmiss``) and then calls ``detector.detect(mask)`` with the
default ``DetConfig``. Nothing here changes what runs by default.

Candidates with a chosen number are ``fit(train_stems, held_place) -> detect_frame`` functions: the judge calls each
once per place with the ordinary train frames of the OTHER places, and the setting is chosen on those frames only
(``nm_common.choose``; the rule is written in PREREG.md). What was chosen for each held-out place is kept in
``CHOSEN``.

    fit_hyst            A   plain two-level thresholds, the loose level (1..5) chosen in the fold
    fit_hyst_guard      A'  the same, loose paint never below the lowest strict pixel of its piece
    fit_partner         B   partner-conditioned, both directions; stripe level and body level (0..5) and the edge
                            mode (strict | pred) chosen in the fold
    fit_partner_free    D   the same grid with the edges unprotected ("free"): what the protection is worth
    fit_wide            C   as B, but the levels may go past every color range: stripe 0..6 (6 = anything), body 0..7
                            (6 = darker than the ground, 7 = anything)
    fixed(spec)             a candidate with nothing chosen (the ladders of PREREG.md), e.g. fixed("pc:5,0,strict")
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nm_common as cm  # noqa: E402

JOBS = 8
CHOSEN: dict[str, dict[str, dict]] = {}         # candidate name -> held-out place -> {"spec", "rows"}


def grid(max_stripe: int, max_body: int, modes: tuple[str, ...]) -> list[str]:
    """Every (stripe level, body level, edge mode) but both-off, least loose first."""
    out = []
    for s in range(max_stripe + 1):
        for b in range(max_body + 1):
            if s == 0 and b == 0:
                continue
            for m in (modes if b else modes[:1]):
                out.append(cm.pc(s, b, m))
    return list(dict.fromkeys(out))


HYST = [f"hyst:{k}" for k in range(1, 6)]
HYST_GUARD = [f"hystg:{k}" for k in range(1, 6)]
GRID_B = grid(5, 5, ("strict", "pred"))             # 65 settings
GRID_FREE = grid(5, 5, ("free",))                   # 35
GRID_C = grid(6, 7, ("strict", "pred"))             # 104; holds GRID_B

# the ladders: nothing chosen
STRIPE_ONLY = [cm.pc(k, 0) for k in range(1, 7)]
BODY_ONLY = [cm.pc(0, k, "pred") for k in range(1, 8)]
BOTH = [cm.pc(k, k, "pred") for k in range(1, 6)] + [cm.pc(6, 6, "pred"), cm.pc(6, 7, "pred")]
HYST_FIXED = ["hyst:1", "hyst:2", "hyst:3"]


def all_specs() -> list[str]:
    """Every setting any candidate here can use (what run.py computes once, in parallel, before the judged runs)."""
    return list(dict.fromkeys(["fixed", *HYST, *HYST_GUARD, *GRID_C, *GRID_FREE, *STRIPE_ONLY, *BODY_ONLY, *BOTH]))


def _fit(name: str, specs: list[str], what: str):
    def fit(train_stems: list[str], held_place: str):
        spec, rows = cm.choose(specs, train_stems, jobs=JOBS)
        CHOSEN.setdefault(name, {})[held_place] = {"spec": spec, "rows": rows}
        d = cm.detector_of(spec)
        d.describe = f"{name}: {spec} ({cm.describe(spec)}), chosen without {held_place}"
        return d
    fit.describe = f"{name}: {what}; the setting is chosen in each fold on the other places (rule: PREREG.md)"
    fit.candidate_name = name
    fit.specs = specs
    return fit


fit_hyst = _fit("A_hyst_fit", HYST, "plain two-level thresholds, loose level 1..5")
fit_hyst_guard = _fit("A_hyst_guard_fit", HYST_GUARD, "two-level thresholds with the bottom guard, loose level 1..5")
fit_partner = _fit("B_partner_fit", GRID_B, "partner-conditioned, stripe and body level 0..5, edges strict or pred")
fit_partner_free = _fit("D_partner_free_fit", GRID_FREE, "partner-conditioned, stripe and body level 0..5, edges free (unprotected)")
fit_wide = _fit("C_wide_fit", GRID_C, "partner-conditioned, stripe level 0..6 and body level 0..7 (past every color range), edges strict or pred")


def fixed(spec: str):
    """A candidate with nothing chosen, as a ``detect_frame``."""
    return cm.detector_of(spec)


# The setting offered for the next experiment: what the selection rule gives on all eight ordinary places at once
# (written here after the judged runs; ``run.py --final`` checks it against the rule). Both directions at level 5
# (hue +-25, S -100, V >= 15), loose body paint never past the top and bottom the stripe's row predicts. Its own
# judged number (C_both5_5: 133.8 -> 152.8) is in-sample; the held-out number is B_partner_fit's (133.8 -> 147.5).
FINAL_SPEC = "pc:5,5,pred"
detect_frame = cm.detector_of(FINAL_SPEC)


def final_mask(frame):
    """The class mask of the offered setting on a ``pipeline.Frame`` (0 other, 1 orange, 2 blue), for a caller that
    wants the mask and not the boxes."""
    return cm.mask_of(FINAL_SPEC, frame)
