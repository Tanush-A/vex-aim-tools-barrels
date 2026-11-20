"""The detector settings compared in this experiment (PREREG.md, "Arms"). ``base`` is the detector on `barrels`
on 2026-11-18, spelled out so that a later change of defaults does not move it."""
import dataclasses

from barrels import detector as det

BASE = dataclasses.replace(det.DetConfig(), stripe_join=False, cap_behind=False, stripe_w_min=0.4, occl_body_side=False,
                           side_hidden=False, seam_height=False, cap_seen_bottom=False,   # switches of 2026-11-19, pinned off so this experiment does not move
                           slice_box=False, cover_unpinned=False, stripe_two=False, edge_check=False, cap_same=False,   # ... and those of the occlusion round
                           pin_outline=False, pin_thin=False)                                                          # ... and of 2026-11-20 (occl_pin)
SIDE = {"stripe_w_min": 0.25, "occl_body_side": True}

ARMS = {
    "base": BASE,
    "cap": dataclasses.replace(BASE, cap_behind=True),
    "join": dataclasses.replace(BASE, stripe_join=True),
    "cap+join": dataclasses.replace(BASE, cap_behind=True, stripe_join=True),
    "cap+join+side": dataclasses.replace(BASE, cap_behind=True, stripe_join=True, **SIDE),
    "side": dataclasses.replace(BASE, **SIDE),                    # report only
}
# the same as report.py --cand-det strings
OVERRIDES = {
    "cap": "cap_behind=true",
    "join": "stripe_join=true",
    "cap+join": "cap_behind=true,stripe_join=true",
    "cap+join+side": "cap_behind=true,stripe_join=true,stripe_w_min=0.25,occl_body_side=true",
    "side": "stripe_w_min=0.25,occl_body_side=true",
}
