"""The detector settings compared in this experiment (PREREG.md, "Arms"). ``base`` is the detector on `barrels`
on 2026-11-18 evening (stripe_join and cap_behind on), spelled out so that a later change of defaults does not
move it. Fields added by this experiment are pinned off in ``base`` when they exist (``_known``): the baseline
was run before they existed."""
import dataclasses

from barrels import detector as det

_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}
NEW = ("side_hidden", "stripe_ends")                              # the switches this experiment adds (PREREG.md)


def _known(**kw) -> dict:
    """Only the fields this version of DetConfig has."""
    return {k: v for k, v in kw.items() if k in _FIELDS}


BASE = dataclasses.replace(det.DetConfig(), stripe_join=True, cap_behind=True, stripe_w_min=0.4, occl_body_side=False,
                           **_known(**{k: False for k in NEW}))
_BASE_STR = ",".join(["stripe_join=true", "cap_behind=true", "stripe_w_min=0.4", "occl_body_side=false"] + [f"{k}=false" for k in NEW if k in _FIELDS])

ARMS = {
    "base": BASE,
    "old_side": dataclasses.replace(BASE, stripe_w_min=0.25, occl_body_side=True),   # report only: the 2026-11-11 fix
}
# the same as report.py --cand-det strings
OVERRIDES = {
    "base": _BASE_STR,
    "old_side": _BASE_STR.replace("stripe_w_min=0.4", "stripe_w_min=0.25").replace("occl_body_side=false", "occl_body_side=true"),
}
if "side_hidden" in _FIELDS:
    ARMS["side"] = dataclasses.replace(BASE, side_hidden=True)
    OVERRIDES["side"] = _BASE_STR.replace("side_hidden=false", "side_hidden=true")
if "stripe_ends" in _FIELDS:
    ARMS["ends"] = dataclasses.replace(BASE, stripe_ends=True)
    OVERRIDES["ends"] = _BASE_STR.replace("stripe_ends=false", "stripe_ends=true")
if set(NEW) <= _FIELDS:
    ARMS["side+ends"] = dataclasses.replace(BASE, side_hidden=True, stripe_ends=True)
    OVERRIDES["side+ends"] = _BASE_STR.replace("side_hidden=false", "side_hidden=true").replace("stripe_ends=false", "stripe_ends=true")
