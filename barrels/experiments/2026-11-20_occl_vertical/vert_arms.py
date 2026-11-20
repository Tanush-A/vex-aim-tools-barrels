"""The detector settings compared in this experiment (PREREG.md). ``base`` is the detector on `wip/detector-occl`
on 2026-11-19 (stripe_join, cap_behind, side_hidden, seam_height, cap_seen_bottom, edge_check, cap_same on; slice_box,
cover_unpinned, stripe_two off), spelled out so that a later change of defaults does not move it. The switches this
experiment adds are pinned off in ``base`` (``_known``: the baseline itself was run before they existed)."""
import dataclasses

from barrels import detector as det

_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}
NEW = ("half_stripe", "half_thin", "post_pair", "stripe_wide", "slice_behind", "cap_low")     # the switches this experiment adds (PREREG.md)
LATER = ("pin_outline", "pin_thin")       # switches of the parallel branch wip/occl-pin (merged 2026-11-20 on wip/occl-combined), pinned off so this experiment does not move


def _known(**kw) -> dict:
    """Only the fields this version of DetConfig has."""
    return {k: v for k, v in kw.items() if k in _FIELDS}


def _arm(**on) -> tuple[det.DetConfig, str]:
    """(DetConfig, the same as a report.py --cand-det string) for `base` with these fields changed."""
    kw = {"stripe_join": True, "cap_behind": True, "stripe_w_min": 0.4, "occl_body_side": False, "side_hidden": True, "seam_height": True,
          "cap_seen_bottom": True, "slice_box": False, "cover_unpinned": False, "stripe_two": False, "edge_check": True, "cap_same": True,
          **_known(**{k: False for k in NEW + LATER}), **on}
    text = ",".join(f"{k}={str(v).lower() if isinstance(v, bool) else v}" for k, v in kw.items())
    return dataclasses.replace(det.DetConfig(), **kw), text


_SPECS = {
    "base": {},
    "half": {"half_stripe": True},
    "half+thin": {"half_stripe": True, "half_thin": True},
    "post": {"post_pair": True},
    "wide": {"stripe_wide": True},
    "behind": {"slice_behind": True},
    "caplow": {"cap_low": True},
    "all": {k: True for k in NEW},
}
ARMS, OVERRIDES = {}, {}
for _name, _on in _SPECS.items():
    if set(_on) <= _FIELDS:                                  # an arm exists once the detector has its switches
        ARMS[_name], OVERRIDES[_name] = _arm(**_on)
BASE = ARMS["base"]
