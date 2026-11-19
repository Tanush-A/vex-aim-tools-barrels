"""The detector settings compared in this experiment (PREREG.md). ``base`` is the detector on `wip/detector-side`
on 2026-11-19 (stripe_join, cap_behind, side_hidden and seam_height on), spelled out so that a later change of
defaults does not move it. The switch this experiment adds is pinned off in ``base`` (``_known``: the baseline
itself was run before the switch existed)."""
import dataclasses

from barrels import detector as det

_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}
NEW = ("cap_seen_bottom",)                                        # the switch this experiment adds (PREREG.md)


def _known(**kw) -> dict:
    """Only the fields this version of DetConfig has."""
    return {k: v for k, v in kw.items() if k in _FIELDS}


def _arm(**on) -> tuple[det.DetConfig, str]:
    """(DetConfig, the same as a report.py --cand-det string) for `base` with these fields changed."""
    kw = {"stripe_join": True, "cap_behind": True, "stripe_w_min": 0.4, "occl_body_side": False, "side_hidden": True, "seam_height": True,
          **_known(**{k: False for k in NEW}), **on}
    text = ",".join(f"{k}={str(v).lower() if isinstance(v, bool) else v}" for k, v in kw.items())
    return dataclasses.replace(det.DetConfig(), **kw), text


_SPECS = {
    "base": {},
    "bottom": {"cap_seen_bottom": True},
}
ARMS, OVERRIDES = {}, {}
for _name, _on in _SPECS.items():
    if set(_on) <= _FIELDS:
        ARMS[_name], OVERRIDES[_name] = _arm(**_on)
BASE = ARMS["base"]
