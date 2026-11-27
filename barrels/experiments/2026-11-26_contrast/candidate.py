"""The contrast path as a detector the judge can run (experiment C4; plan: PREREG.md).

    python barrels/tools/judge.py --cand-callable barrels/experiments/2026-11-26_contrast/candidate.py:detect_frame --no-save

A ``Setting`` is the handful of numbers of the contrast path and how its paint meets the fixed model:

- ``add``: the fixed model and today's detector run first and their boxes are kept as they are. Candidates whose
  stripe point lies in one of those boxes are left alone. The rest are painted into a copy of the fixed mask (only
  where the fixed model painted nothing, only inside the box the geometry predicts for the candidate), the detector
  runs again on that mask, and a box from the second run is added when it is on none of the first run's boxes. So a
  barrel that is found today cannot be lost.
- ``merge``: every candidate is painted into the fixed mask and the detector's answer on that mask is the answer.
- ``alone``: the fixed colors are switched off; the mask holds the contrast path's paint only.

In every mode the boxes come from ``detector.detect(mask)`` with ``DetConfig()``: the stripe proportions, the body
check, the size checks and the verify step of today's detector apply to every candidate.

``detect(frame, setting)`` is the detector of one setting; ``FrameWork`` is the same for many settings on one frame
(the response, the candidates and the fixed model's boxes are computed once). ``detect_frame`` is the judge's
callable for the setting this file names ``BEST`` (see ENTRY.md for how it was arrived at). ``table.py`` holds the
settings the folds choose among.
"""
from __future__ import annotations

import dataclasses
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import contrast_c4 as cn  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402

MODES = ("add", "merge", "alone")
_ROWS: dict = {}


@dataclass(frozen=True)
class Setting:
    mode: str = "add"
    margin: float = 0.5
    width_share: float = 0.5
    strength_min: float = 1.0
    d_min: float | None = None
    orange_min: float | None = None
    alike_rel: float | None = None
    alike_feat: float | None = None
    extent_top: float | None = None
    extent_bottom: float | None = None
    surround: float | None = None
    channel: str = "logrb"
    offset: float = 8.0

    def __post_init__(self):
        if self.mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got {self.mode!r}")

    def params(self) -> cn.Params:
        return cn.Params(channel=self.channel, offset=self.offset, margin=self.margin, width_share=self.width_share, strength_min=self.strength_min,
                         d_min=self.d_min, orange_min=self.orange_min, alike_rel=self.alike_rel, alike_feat=self.alike_feat,
                         extent_top=self.extent_top, extent_bottom=self.extent_bottom, surround=self.surround)

    @property
    def key(self) -> str:
        g = lambda v: "-" if v is None else f"{v:g}"      # noqa: E731
        return (f"{self.mode}|{self.channel}{self.offset:g}|m{self.margin:g}|q{self.width_share:g}|k{self.strength_min:g}|d{g(self.d_min)}|o{g(self.orange_min)}"
                f"|a{g(self.alike_rel)}|f{g(self.alike_feat)}|t{g(self.extent_top)}|b{g(self.extent_bottom)}|s{g(self.surround)}")

    @property
    def spec(self) -> str:
        """The setting as ``sheets.py --setting`` reads it."""
        return ",".join(f"{f.name}={getattr(self, f.name)}" for f in dataclasses.fields(self) if f.name == "mode" or getattr(self, f.name) != f.default)

    def describe(self) -> str:
        guards = [f"{n} {v:g}" for n, v in (("own colors apart >=", self.d_min), ("orange part reddish >=", self.orange_min), ("body bands alike in red-blue <=", self.alike_rel),
                                            ("body bands one color <=", self.alike_feat), ("top edge seen >=", self.extent_top),
                                            ("bottom edge seen >=", self.extent_bottom), ("a side differs >=", self.surround))
                  if v is not None]
        how = {"add": "added to today's boxes", "merge": "painted into the fixed mask", "alone": "alone, fixed colors off"}[self.mode]
        return (f"contrast path {how}: margin {self.margin:g}, share of the width {self.width_share:g}, mean difference >= {self.strength_min:g}, "
                f"guards: {', '.join(guards) or 'none'}")


def setting_from(spec: str) -> Setting:
    """``mode=add,strength_min=1.15,orange_min=0.8`` -> a Setting (the inverse of ``Setting.spec``)."""
    kw = {}
    for part in filter(None, spec.split(",")):
        k, v = part.split("=")
        kw[k] = v if k in ("mode", "channel") else (None if v in ("None", "-") else float(v))
    return Setting(**kw)


def _rows(shape, p: cn.Params):
    k = (shape[0], p.top_row, p.core, p.gap, p.body, p.window, p.min_stripe_px, p.min_width_px)
    if k not in _ROWS:
        _ROWS[k] = cn.row_bands(cm.CAM, shape[0], p)
    return _ROWS[k]


class FrameWork:
    """One frame, any number of settings. Computed once and kept: the fixed mask and today's boxes; the response
    per (channel, offset, margin); the candidates per (..., share, strength floor); the detector's answer per mask."""

    def __init__(self, frame):
        self.frame = frame
        self._base_mask = None
        self._base_boxes = None
        self._resp: dict = {}
        self._cands: dict = {}
        self._feat: dict = {}
        self._det: dict = {}

    @property
    def base_mask(self):
        if self._base_mask is None:
            self._base_mask = cm.fixed_mask(self.frame)
        return self._base_mask

    def _detect(self, mask) -> list:
        h = hashlib.blake2b(mask.tobytes(), digest_size=16).digest()
        if h not in self._det:
            self._det[h] = det.detect(mask, det.DetConfig(), cm.CAM)
        return self._det[h]

    @property
    def base_boxes(self) -> list:
        if self._base_boxes is None:
            self._base_boxes = self._detect(self.base_mask)
        return self._base_boxes

    def response(self, p: cn.Params) -> cn.Response:
        k = (p.channel, p.offset, p.margin)
        if k not in self._resp:
            self._resp[k] = cn.respond(self.frame.rgb, cm.CAM, p, _rows(self.frame.shape, p))
        return self._resp[k]

    def candidates(self, p: cn.Params) -> list[cn.Candidate]:
        k = (p.channel, p.offset, p.margin, p.width_share, p.strength_min)
        if k not in self._cands:
            self._cands[k] = cn.find(self.frame.rgb, cm.CAM, p, resp=self.response(p))
        return [dataclasses.replace(c, info={}) for c in self._cands[k]]

    def features(self, p: cn.Params):
        k = (p.feat_offset, p.bright)
        if k not in self._feat:
            self._feat[k] = cn.features(self.frame.rgb, p.feat_offset, p.bright)
        return self._feat[k]

    def masks(self, st: Setting):
        """(the mask the detector is run on, the candidates with their ``info``) for one setting."""
        p = st.params()
        base = None if st.mode == "alone" else self.base_mask
        skip = tuple(b.bbox for b in self.base_boxes) if st.mode == "add" else ()
        return cn.contrast_mask(self.frame.rgb, base, cm.CAM, p, skip_boxes=skip, resp=self.response(p), feat=self.features(p), cands=self.candidates(p))

    def detect(self, st: Setting | None) -> list:
        """The boxes of one setting (None = today's detector on the fixed mask)."""
        if st is None:
            return list(self.base_boxes)
        mask, cands = self.masks(st)
        if st.mode != "add":
            return list(self._detect(mask))
        if not any(c.info.get("painted") for c in cands):
            return list(self.base_boxes)
        new = self._detect(mask)
        out = list(self.base_boxes) + [b for b in new if not any(ct.is_on(b, o) for o in self.base_boxes)]
        return sorted(out, key=lambda b: b.bbox[0])


def detect(frame, st: Setting | None) -> list:
    """The boxes of one setting on one frame (``st`` None = today's detector on the fixed mask)."""
    return FrameWork(frame).detect(st)


# The setting on all eight places that the fold rule of PREREG.md picks in-sample for the primary family (C1). It is
# NOT what was judged: the judged candidate is ``table.fit_family("C1_add_guards")``, which picks a setting per
# held-out place. See ENTRY.md.
BEST = Setting(mode="add", strength_min=1.15, orange_min=0.8, extent_top=0.15, extent_bottom=0.15)


def detect_frame(stem: str, frame) -> list:
    """The judge's callable: the contrast path at ``BEST`` on top of today's detector."""
    return detect(frame, BEST)


detect_frame.describe = "today's default plus the " + BEST.describe()
