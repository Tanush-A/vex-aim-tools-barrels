"""Fit the camera model to the ruler set (TODO A4, 2026-11-19): one barrel on the vertical crosshair at known
distances, each with a hand-drawn box.

What is known and what is fit
-----------------------------
known (specification or tape measure, never fit by default):
    camera height 43.47 mm (aim_kin.py), principal point (320, 240), the barrel (24 mm tall, 18 mm ends,
    25.5 mm bulge; measured 2026-10-19).
fit:
    ``f``         focal length, px
    ``tilt_deg``  tilt below horizontal
    ``off_mm``    how far the camera sits behind the point the ruler distances were measured from (the robot's
                  front edge). aim_kin.py implies 3 mm (camera 27 mm ahead of the centre, body radius 30 mm);
                  it is not part of ``CameraModel``'s image geometry, only of "ruler distance -> camera distance".
    ``height_mm`` the camera height, when the frames do not fit at 43.47 (2026-11-19: they do not).
can be freed, for the record only (other single numbers that could absorb the same misfit):
    ``cy`` (the centre row) and ``barrel_h_mm`` (the barrel's height).

For a shot at ruler distance d (front edge -> near edge of the base, at table level):
    base near edge   d + off          from the camera, height 0      -> the box's bottom row
    barrel axis      d + off + 9
    lid far edge     d + off + 18,    height 24                      -> the box's top row
    silhouette       ``CameraModel.silhouette_width_px(axis)``       -> the box's width

The error model has two parts: the box edge is drawn to ``sigma_px`` pixels, and the barrel was placed by hand
to ``sigma_d_mm`` millimetres. Close to the robot one millimetre is many pixels (13 px/mm for the top row at
10 mm), so a near shot says little about the camera and a lot about the placement; each observation is weighted
by 1 / sqrt(sigma_px^2 + (d pred / d distance * sigma_d)^2).

Plain numpy (Levenberg-Marquardt with a numeric Jacobian); no scipy in the project's environment.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import geometry as geo
from . import io

PARAMS = ("f", "tilt_deg", "off_mm", "height_mm", "cy", "barrel_h_mm")
NOMINAL_OFF_MM = geo.FRONT_EDGE_FROM_ORIGIN_MM - geo.CAM_FROM_ORIGIN_MM      # 3 mm, from aim_kin.py
KINDS = ("top", "bottom", "width")
_END_R = geo.BARREL_END_DIAMETER_MM / 2


@dataclass(frozen=True)
class RulerShot:
    stem: str
    d_ruler_mm: float
    bbox: tuple[int, int, int, int]
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Obs:
    """One measured number of one shot: the top row, the bottom row or the width of the hand-drawn box."""
    stem: str
    d_ruler_mm: float
    kind: str
    value: float


def load_ruler_set(csv_path: Path | str | None = None, labels_dir: Path | str | None = None) -> list[RulerShot]:
    """``data/calib.csv`` (stem, distance_mm) joined with each stem's box label (exactly one box per frame)."""
    csv_path = Path(csv_path) if csv_path else io.PKG_ROOT / "data" / "calib.csv"
    shots = []
    with csv_path.open() as f:
        for row in csv.DictReader(f):
            label = io.load_boxes(row["stem"], labels_dir, check_image=False)
            if len(label["barrels"]) != 1:
                raise ValueError(f"{row['stem']}: a ruler frame must have exactly one box, found {len(label['barrels'])}")
            b = label["barrels"][0]
            shots.append(RulerShot(row["stem"], float(row["distance_mm"]), tuple(int(v) for v in b["bbox"]), tuple(b.get("flags", ()))))
    return shots


def observations(shots: list[RulerShot], frame_w: int = io.FRAME_W, frame_h: int = io.FRAME_H,
                 skip_flags: tuple[str, ...] = ("held",)) -> list[Obs]:
    """What each box measures. An edge on the frame border measures nothing (the barrel continues outside), so
    a box cut by the frame bottom gives no bottom row, and one cut at a side gives no width. Shots carrying a
    flag in ``skip_flags`` are left out entirely (``held``: seated in the kicker, the base is not on the table
    and its distance from the front edge is not the ruler's)."""
    out = []
    for s in shots:
        if any(f in s.flags for f in skip_flags):
            continue
        x0, y0, x1, y1 = s.bbox
        if y0 > 0:
            out.append(Obs(s.stem, s.d_ruler_mm, "top", float(y0)))
        if y1 < frame_h:
            out.append(Obs(s.stem, s.d_ruler_mm, "bottom", float(y1)))
        if x0 > 0 and x1 < frame_w:
            out.append(Obs(s.stem, s.d_ruler_mm, "width", float(x1 - x0)))
    return out


def camera_of(p: dict) -> geo.CameraModel:
    return geo.CameraModel(f=p["f"], tilt_deg=p["tilt_deg"], cy=p.get("cy", 240.0), height_mm=p.get("height_mm", geo.H_CAM_MM))


def params_of(cam: geo.CameraModel, off_mm: float = NOMINAL_OFF_MM) -> dict:
    return {"f": cam.f, "tilt_deg": cam.tilt_deg, "off_mm": off_mm, "height_mm": cam.height_mm, "cy": cam.cy,
            "barrel_h_mm": geo.BARREL_HEIGHT_MM}


def predict(p: dict, d_ruler_mm: float, kind: str) -> float:
    """The row or width the model expects for a shot at ruler distance d."""
    cam = camera_of(p)
    d_base = d_ruler_mm + p["off_mm"]
    if kind == "bottom":
        return cam.point_row(d_base, 0.0)
    if kind == "top":
        return cam.point_row(d_base + 2 * _END_R, p.get("barrel_h_mm", geo.BARREL_HEIGHT_MM))
    if kind == "width":
        return cam.silhouette_width_px(d_base + _END_R)
    raise ValueError(f"unknown observation kind {kind!r}")


def sigma(p: dict, o: Obs, sigma_px: float, sigma_d_mm: float) -> float:
    """Expected error of one observation in px: the drawn edge and the hand placement, added in quadrature."""
    if sigma_d_mm <= 0:
        return sigma_px
    h = 0.25
    try:
        slope = (predict(p, o.d_ruler_mm + h, o.kind) - predict(p, o.d_ruler_mm - h, o.kind)) / (2 * h)
    except ValueError:
        return sigma_px
    return math.hypot(sigma_px, slope * sigma_d_mm) if math.isfinite(slope) else sigma_px


def residuals_px(p: dict, obs: list[Obs]) -> np.ndarray:
    """measured - predicted, px, one per observation."""
    return np.array([o.value - predict(p, o.d_ruler_mm, o.kind) for o in obs])


@dataclass
class Fit:
    params: dict                      # every parameter, fitted or held
    free: tuple[str, ...]
    stderr: dict                      # 1-sigma of each free parameter from the fit's own scatter
    corr: np.ndarray                  # correlation matrix of the free parameters
    chi2: float                       # sum of (residual / sigma)^2
    dof: int
    obs: list[Obs] = field(default_factory=list, repr=False)
    res_px: np.ndarray = field(default=None, repr=False)
    sig_px: np.ndarray = field(default=None, repr=False)

    @property
    def camera(self) -> geo.CameraModel:
        return camera_of(self.params)

    @property
    def rms_px(self) -> float:
        return float(np.sqrt(np.mean(self.res_px ** 2)))

    @property
    def rms_weighted(self) -> float:
        """sqrt(chi2 / dof): 1 when the residuals are as large as the error model says."""
        return float(math.sqrt(self.chi2 / max(1, self.dof)))


def fit(obs: list[Obs], start: dict, free: tuple[str, ...] = ("f", "tilt_deg", "off_mm"), sigma_px: float = 1.5,
        sigma_d_mm: float = 1.0, n_reweight: int = 3, max_iter: int = 200) -> Fit:
    """Weighted least squares over the ``free`` parameters, the others held at ``start``. The weights depend
    (weakly) on the parameters through the placement term, so they are recomputed ``n_reweight`` times."""
    for k in free:
        if k not in PARAMS:
            raise ValueError(f"unknown parameter {k!r} (one of {PARAMS})")
    if len(obs) < len(free):
        raise ValueError(f"{len(obs)} observations cannot fit {len(free)} parameters")
    p = dict(start)
    steps = {"f": 0.05, "tilt_deg": 0.005, "off_mm": 0.01, "height_mm": 0.01, "cy": 0.05, "barrel_h_mm": 0.01}

    def unpack(x):
        q = dict(p)
        q.update(zip(free, x))
        return q

    def resid(x, sig):
        try:
            r = residuals_px(unpack(x), obs) / sig
        except ValueError:                       # a distance went non-positive: far outside any sensible camera
            return np.full(len(obs), 1e6)
        return np.where(np.isfinite(r), r, 1e6)  # the camera inside the barrel's outline: no finite width

    def jac(x, sig):
        J = np.empty((len(obs), len(free)))
        for j, k in enumerate(free):
            dx = np.zeros(len(free)); dx[j] = steps[k]
            J[:, j] = (resid(x + dx, sig) - resid(x - dx, sig)) / (2 * steps[k])
        return J

    x = np.array([p[k] for k in free], float)
    sig = np.ones(len(obs))
    for _ in range(max(1, n_reweight)):
        sig = np.array([sigma(unpack(x), o, sigma_px, sigma_d_mm) for o in obs])
        lam = 1e-3
        r = resid(x, sig); cost = float(r @ r)
        for _ in range(max_iter):
            J = jac(x, sig)
            A = J.T @ J
            g = J.T @ r
            step = np.linalg.solve(A + lam * np.diag(np.diag(A)), -g)
            r_new = resid(x + step, sig); cost_new = float(r_new @ r_new)
            if cost_new < cost:
                done = cost - cost_new < 1e-12 * max(1.0, cost)
                x, r, cost, lam = x + step, r_new, cost_new, lam * 0.3
                if done:
                    break
            else:
                lam *= 10
                if lam > 1e12:
                    break
    J = jac(x, sig)
    dof = len(obs) - len(free)
    cov = np.linalg.pinv(J.T @ J) * (cost / max(1, dof))
    sd = np.sqrt(np.clip(np.diag(cov), 0, None))
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = cov / np.outer(sd, sd)
    q = unpack(x)
    return Fit(params=q, free=tuple(free), stderr=dict(zip(free, sd.tolist())), corr=corr, chi2=cost, dof=dof,
               obs=list(obs), res_px=residuals_px(q, obs), sig_px=sig)


def leave_one_out(obs: list[Obs], start: dict, free: tuple[str, ...], **kw) -> dict[str, Fit]:
    """One fit per shot left out (all of that shot's observations): stem left out -> Fit."""
    out = {}
    for stem in sorted({o.stem for o in obs}):
        out[stem] = fit([o for o in obs if o.stem != stem], start, free, **kw)
    return out


def jitter(obs: list[Obs], start: dict, free: tuple[str, ...], n: int = 200, seed: int = 0, box_px: float = 1.5,
           place_mm: float = 1.0, **kw) -> np.ndarray:
    """Refit ``n`` times with the boxes and the placements disturbed by their assumed errors: every box edge by
    N(0, box_px) (a width gets two edges), every shot's distance by N(0, place_mm), one draw per shot. Returns an
    (n, len(free)) array: the spread says how well the data pins each parameter if the error model is right."""
    rng = np.random.default_rng(seed)
    stems = sorted({o.stem for o in obs})
    out = []
    for _ in range(n):
        dd = {s: rng.normal(0, place_mm) for s in stems}
        new = [Obs(o.stem, o.d_ruler_mm + dd[o.stem], o.kind,
                   o.value + rng.normal(0, box_px * (math.sqrt(2) if o.kind == "width" else 1.0))) for o in obs]
        fr = fit(new, start, free, **kw)
        out.append([fr.params[k] for k in free])
    return np.array(out)
