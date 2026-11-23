"""The detector settings compared in this experiment (PREREG.md, "Arms"). ``base`` is the detector on `barrels`
on 2026-11-18 evening (stripe_join and cap_behind on), spelled out so that a later change of defaults does not
move it. The two switches this experiment adds are pinned off in ``base`` (``_known``: the baseline itself was
run before they existed)."""
import dataclasses

from barrels import detector as det

_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}
SLIVER = ("stripe_bridge", "thin_frame", "own_close", "thin_span")   # switches of 2026-11-20 (occl_sliver), pinned off so this experiment does not move
SLIVER = SLIVER + ("closeup_side", "closeup_stripe")   # ... and of 2026-11-23 (closeup_shape), pinned off so this experiment does not move
NEW = ("side_hidden", "seam_height")                              # the switches this experiment adds (PREREG.md)
LATER = ("cap_seen_bottom", "slice_box", "cover_unpinned", "stripe_two", "edge_check", "cap_same",   # switches added after this experiment, pinned off so it does not move
         "half_stripe", "half_thin", "post_pair", "stripe_wide", "slice_behind", "cap_low",          # ... those of 2026-11-20 (occl_vertical)
         "pin_outline", "pin_thin")                                                                  # ... and of 2026-11-20 (occl_pin)


def _known(**kw) -> dict:
    """Only the fields this version of DetConfig has."""
    return {k: v for k, v in kw.items() if k in _FIELDS}


def _arm(**on) -> tuple[det.DetConfig, str]:
    """(DetConfig, the same as a report.py --cand-det string) for `base` with these fields changed."""
    kw = {"stripe_join": True, "cap_behind": True, "stripe_w_min": 0.4, "occl_body_side": False, **_known(**{k: False for k in NEW + LATER + SLIVER}), **on}
    text = ",".join(f"{k}={str(v).lower() if isinstance(v, bool) else v}" for k, v in kw.items())
    return dataclasses.replace(det.DetConfig(), **kw), text


_SPECS = {
    "base": {},
    "side": {"side_hidden": True},
    "seam": {"seam_height": True},
    "side+seam": {"side_hidden": True, "seam_height": True},
    "old_side": {"stripe_w_min": 0.25, "occl_body_side": True},      # report only: the 2026-11-11 fix
}
ARMS, OVERRIDES = {}, {}
for _name, _on in _SPECS.items():
    if set(_on) <= _FIELDS:
        ARMS[_name], OVERRIDES[_name] = _arm(**_on)
BASE = ARMS["base"]
