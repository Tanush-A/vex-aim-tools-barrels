"""Per-barrel instance ground truth from the class masks (docs/DATA.md, "Instance labels").

A class mask says which pixels are barrel-orange / barrel-blue; it does not say which pixels
belong to which barrel, and touching barrels of the same color merge into one blob.
``split_instances`` splits the mask into barrels automatically; the pure edit functions
(``merge``, ``split_seeded``, ``delete``) and ``apply_edits`` let the instance tool fix the
mistakes with edits that are recorded by image point and can be replayed.

Auto-split, per connected blob of orange|blue|ignore pixels:
  1. the expected barrel width W and height Hpx at the blob's bottom row (barrels.geometry);
  2. stripe seeds: pixels of color B that have color A both a few rows above and below in the
     same column are a stripe sandwiched in a body of color A -> one seed per barrel, body color A;
     a stripe wider than 1.5 W is two touching same-colored barrels and is cut at the valleys of
     its column profile;
  3. distance-transform peaks add seeds for barrels without a visible stripe (far, occluded);
  4. a watershed on the inverted distance transform assigns every blob pixel to a seed.
Instance ids are uint8 1..N, left to right.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np

from . import geometry as geo
from .io import BLUE, IGNORE, ORANGE, OTHER, instance_records
from .labeling import _fill_boundaries

BARREL_CLASSES = (ORANGE, BLUE)
COLOR_NAME = {ORANGE: "orange", BLUE: "blue"}
HINT_OCCLUDED = "occluded"


@dataclass(frozen=True)
class SplitConfig:
    min_area_px: int = 20          # blobs smaller than this are label noise: dropped, counted in dropped_px
    stripe_frac: float = 0.25      # stripe height / barrel height (6 / 24)
    width_ratio_split: float = 1.5 # a stripe wider than this x W holds more than one barrel
    min_seed_sep: float = 0.5      # seeds closer than this x W are merged
    seed_erode_px: int = 2
    dt_peak_frac: float = 0.3      # distance-transform peaks >= this x W become seeds
    dt_min_sep: float = 0.6        # ... if farther than this x W from every existing seed
    no_stripe_frac: float = 0.02   # minority-color pixels below this fraction -> flag no_stripe
    occluded_height_frac: float = 0.6

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------- helpers

def _shift_rows(a: np.ndarray, k: int) -> np.ndarray:
    """out[y] = a[y - k] (k > 0 moves content down); zeros fill."""
    out = np.zeros_like(a)
    if k > 0:
        out[k:] = a[:-k]
    elif k < 0:
        out[:k] = a[-k:]
    else:
        out[:] = a
    return out


def _has_within_rows(a: np.ndarray, k: int, direction: int) -> np.ndarray:
    """True where ``a`` is True somewhere in the k rows above (direction -1) or below (+1), same column."""
    acc = np.zeros_like(a)
    for j in range(1, k + 1):
        acc |= _shift_rows(a, direction * j)
    return acc


def _components(binary: np.ndarray, min_area: int = 1) -> list[np.ndarray]:
    n, lab = cv2.connectedComponents(binary.astype(np.uint8), connectivity=8)
    out = []
    for i in range(1, n):
        c = lab == i
        if c.sum() >= min_area:
            out.append(c)
    return out


def _valley_cuts(colcount: np.ndarray, n_parts: int, min_sep: float) -> list[int]:
    """Column indices (relative) of the n_parts-1 deepest, well-separated valleys; equal spacing if none."""
    w = len(colcount)
    if n_parts <= 1 or w < 3:
        return []
    k = max(3, int(round(min_sep / 2)) * 2 + 1)
    sm = np.convolve(colcount.astype(float), np.ones(k) / k, mode="same")
    interior = range(1, w - 1)
    cands = [x for x in interior if sm[x] <= sm[x - 1] and sm[x] <= sm[x + 1]]
    cands.sort(key=lambda x: sm[x])
    cuts: list[int] = []
    for x in cands:
        if all(abs(x - c) >= min_sep for c in cuts) and min_sep <= x <= w - min_sep:
            cuts.append(x)
        if len(cuts) == n_parts - 1:
            break
    if len(cuts) < n_parts - 1:
        cuts = [int(round(w * (i + 1) / n_parts)) for i in range(n_parts - 1)]
    return sorted(cuts)


def _watershed_assign(region: np.ndarray, seeds: list[np.ndarray], erode_px: int) -> np.ndarray:
    """Assign every pixel of ``region`` to one of the seeds (1..n) by watershed on the inverted
    distance transform. Returns int32 labels (0 outside the region)."""
    n = len(seeds)
    if n == 0:
        return region.astype(np.int32)
    if n == 1:
        return region.astype(np.int32)
    dist = cv2.distanceTransform(region.astype(np.uint8), cv2.DIST_L2, 5)
    img = np.clip(255 - dist / max(dist.max(), 1e-6) * 255, 0, 255).astype(np.uint8)
    img3 = np.repeat(img[..., None], 3, axis=2)
    markers = np.zeros(region.shape, np.int32)
    kern = np.ones((2 * erode_px + 1, 2 * erode_px + 1), np.uint8)
    for i, s in enumerate(seeds, 1):
        core = cv2.erode(s.astype(np.uint8), kern) > 0 if erode_px > 0 else s
        if not core.any():
            core = s
        markers[core & region] = i
    markers[~region] = n + 1
    cv2.watershed(img3, markers)
    lab = markers.copy()
    lab[~region] = 0
    lab[(lab < 0) | (lab == n + 1)] = 0
    lab[~region] = -7                       # keep the outside out of the neighbour-majority fill
    filled = _fill_boundaries(np.where(region, lab, 0).astype(np.int32))
    filled[~region] = 0
    return filled


def _relabel(inst_int: np.ndarray) -> np.ndarray:
    """Compact labels to uint8 1..N ordered left to right by bbox x0 (ties: top to bottom)."""
    ids = [i for i in np.unique(inst_int) if i > 0]
    order = []
    for i in ids:
        ys, xs = np.where(inst_int == i)
        order.append((int(xs.min()), int(ys.min()), int(i)))
    out = np.zeros(inst_int.shape, np.uint8)
    for new, (_, _, old) in enumerate(sorted(order), 1):
        if new > 254:
            raise ValueError("more than 254 instances")
        out[inst_int == old] = new
    return out


# ---------------------------------------------------------------- auto-split

def split_instances(mask: np.ndarray, cam: geo.CameraModel = geo.NOMINAL, cfg: SplitConfig = SplitConfig()
                    ) -> tuple[np.ndarray, list[dict], int]:
    """(instance mask uint8, per-instance records, dropped class pixels). See the module docstring."""
    h, w = mask.shape
    union = np.isin(mask, (ORANGE, BLUE, IGNORE))
    inst = np.zeros((h, w), np.int32)
    seed_kind: dict[int, tuple[str, int | None]] = {}      # label -> (seed type, body color)
    dropped = 0
    next_id = 1
    for blob in _components(union):
        n_class = int(np.isin(mask[blob], BARREL_CLASSES).sum())
        if n_class == 0:
            continue                                        # ignore-only speck (glare off a barrel)
        if blob.sum() < cfg.min_area_px:
            dropped += n_class
            continue
        ys, xs = np.where(blob)
        y1 = int(ys.max()) + 1
        W = cam.expected_barrel_width_px(bottom_row=y1)
        Hpx = cam.expected_barrel_height_px(bottom_row=y1)
        if not np.isfinite(W) or W <= 0:
            W, Hpx = float(xs.max() - xs.min() + 1), float(y1 - ys.min())
        k = max(2, int(round(Hpx * cfg.stripe_frac)))
        seeds: list[np.ndarray] = []
        kinds: list[tuple[str, int | None]] = []
        cuts_between: list[tuple[int, int, int]] = []        # (x_cut, left seed index, right seed index): touching same-color barrels
        # 2. stripe seeds
        for body, stripe in ((ORANGE, BLUE), (BLUE, ORANGE)):
            is_a = (mask == body) & blob
            is_b = (mask == stripe) & blob
            sandwiched = is_b & _has_within_rows(is_a, k, -1) & _has_within_rows(is_a, k, +1)
            for comp in _components(sandwiched, min_area=max(4, int(0.1 * k * W))):
                cys, cxs = np.where(comp)
                cw = int(cxs.max() - cxs.min() + 1)
                if cw > cfg.width_ratio_split * W:
                    n_parts = max(2, int(round(cw / W)))
                    x0 = int(cxs.min())
                    colcount = comp[:, x0:x0 + cw].sum(axis=0)
                    cuts = [x0 + c for c in _valley_cuts(colcount, n_parts, cfg.min_seed_sep * W)]
                    bounds = [x0] + cuts + [x0 + cw]
                    prev_idx = None
                    for a, b in zip(bounds[:-1], bounds[1:]):
                        part = comp.copy(); part[:, :a] = False; part[:, b:] = False
                        if part.any():
                            seeds.append(part); kinds.append(("stripe", body))
                            if prev_idx is not None:
                                cuts_between.append((a, prev_idx, len(seeds) - 1))
                            prev_idx = len(seeds) - 1
                else:
                    seeds.append(comp); kinds.append(("stripe", body))
        # 3. distance-transform peaks for seedless barrels
        dist = cv2.distanceTransform(blob.astype(np.uint8), cv2.DIST_L2, 5)
        win = max(3, int(round(cfg.min_seed_sep * W)) | 1)
        peaks = (dist >= cv2.dilate(dist, np.ones((win, win), np.uint8))) & (dist >= cfg.dt_peak_frac * W) & blob
        seed_centers = [np.array([np.where(s)[1].mean(), np.where(s)[0].mean()]) for s in seeds]
        pys, pxs = np.where(peaks)
        for py, px in sorted(zip(pys, pxs), key=lambda t: -dist[t[0], t[1]]):
            c = np.array([px, py], float)
            if all(np.linalg.norm(c - sc) > cfg.dt_min_sep * W for sc in seed_centers):
                s = np.zeros((h, w), bool)
                r = max(1, int(round(0.15 * W)))
                cv2.circle(s.view(np.uint8), (int(px), int(py)), r, 1, -1)
                s &= blob
                if s.any():
                    seeds.append(s); kinds.append(("dt", None)); seed_centers.append(c)
        # 4. assign; upright barrels standing side by side meet along a vertical line, so between
        #    seeds that sit at the same height the watershed boundary is replaced by a vertical cut
        #    at the narrowest column of the blob between them (occluders, which sit higher, keep
        #    the watershed boundary)
        lab = _watershed_assign(blob, seeds, cfg.seed_erode_px)
        centers = [(float(np.where(sd)[1].mean()), float(np.where(sd)[0].mean())) for sd in seeds]
        colcount = blob.sum(axis=0)
        order = sorted(range(len(seeds)), key=lambda i: centers[i][0])
        known = {(li, ri) for _, li, ri in cuts_between}
        for a, b in zip(order[:-1], order[1:]):
            if (a, b) in known or abs(centers[a][1] - centers[b][1]) > 0.3 * Hpx:
                continue
            xa, xb = int(round(centers[a][0])), int(round(centers[b][0]))
            if xb - xa < 3:
                continue
            x_cut = xa + int(np.argmin(colcount[xa:xb]))
            cuts_between.append((x_cut, a, b))
        xs_grid = np.arange(w)[None, :]
        for x_cut, li, ri in sorted(cuts_between):
            left, right = li + 1, ri + 1
            lab[blob & (xs_grid < x_cut) & (lab == right)] = left
            lab[blob & (xs_grid >= x_cut) & (lab == left)] = right
        if len(seeds) <= 1:
            inst[blob] = next_id
            seed_kind[next_id] = kinds[0] if kinds else ("none", None)
            next_id += 1
        else:
            for i in range(1, len(seeds) + 1):
                sel = lab == i
                if not sel.any():
                    continue
                inst[sel] = next_id
                seed_kind[next_id] = kinds[i - 1]
                next_id += 1
    # compact ids left to right, carrying the seed info
    old_ids = [i for i in np.unique(inst) if i > 0]
    compact = _relabel(inst)
    kind_by_new: dict[int, tuple[str, int | None]] = {}
    for old in old_ids:
        new = int(compact[inst == old][0])
        kind_by_new[new] = seed_kind.get(int(old), ("none", None))
    records = records_from_inst(compact, mask, cam, kind_by_new, cfg)
    return compact, records, dropped


def records_from_inst(inst: np.ndarray, mask: np.ndarray, cam: geo.CameraModel = geo.NOMINAL,
                      seed_kind: dict[int, tuple[str, int | None]] | None = None,
                      cfg: SplitConfig = SplitConfig(), overrides: dict[int, dict] | None = None) -> list[dict]:
    """Per-instance records: geometry (io.instance_records) + color, seed, flags, hints."""
    h, w = mask.shape
    recs = instance_records(inst, mask)
    by_id = {r["id"]: r for r in recs}
    for r in recs:
        i = r["id"]
        kind, body = (seed_kind or {}).get(i, ("manual", None))
        n_o, n_b = r["px"]["orange"], r["px"]["blue"]
        color = body if body is not None else (ORANGE if n_o >= n_b else BLUE)
        r["color"] = COLOR_NAME[color]
        r["seed"] = kind
        x0, y0, x1, y1 = r["bbox"]
        flags = set()
        if x0 == 0 or x1 == w or y1 == h:
            flags.add("truncated")
        minority = min(n_o, n_b)
        if minority < cfg.no_stripe_frac * max(1, n_o + n_b):
            flags.add("no_stripe")
        if (x1 - x0) > 0.5 * w and y1 == h:
            flags.add("top_only")
        hints = []
        Hpx = cam.expected_barrel_height_px(bottom_row=y1)
        if np.isfinite(Hpx) and (y1 - y0) < cfg.occluded_height_frac * Hpx:
            sel = inst == i
            ring = cv2.dilate(sel.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
            if ((inst > 0) & ~sel & ring).any():
                hints.append(HINT_OCCLUDED)
        if overrides and i in overrides:
            ov = overrides[i]
            if "color" in ov:
                r["color"] = ov["color"]
            for f, v in ov.get("flags", {}).items():
                (flags.add if v else flags.discard)(f)
        r["flags"] = sorted(flags)
        r["hints"] = hints
    return [by_id[i] for i in sorted(by_id)]


# ---------------------------------------------------------------- edits (pure)

def _id_at(inst: np.ndarray, point) -> int:
    x, y = int(round(point[0])), int(round(point[1]))
    if not (0 <= y < inst.shape[0] and 0 <= x < inst.shape[1]):
        return 0
    return int(inst[y, x])


def merge(inst: np.ndarray, points) -> np.ndarray:
    ids = sorted({i for i in (_id_at(inst, p) for p in points) if i > 0})
    out = inst.copy()
    if len(ids) < 2:
        return out
    for i in ids[1:]:
        out[out == i] = ids[0]
    return out


def split_seeded(inst: np.ndarray, mask: np.ndarray, seeds, erode_px: int = 0) -> np.ndarray:
    """Re-split the instance(s) under ``seeds`` (image points) so each seed gets its own instance.
    The first seed's instance keeps the lowest id; the others get fresh ids."""
    ids = sorted({i for i in (_id_at(inst, p) for p in seeds) if i > 0})
    if not ids or len(seeds) < 2:
        return inst.copy()
    region = np.isin(inst, ids)
    seed_masks = []
    for p in seeds:
        s = np.zeros(inst.shape, bool)
        cv2.circle(s.view(np.uint8), (int(round(p[0])), int(round(p[1]))), 2, 1, -1)
        s &= region
        if s.any():
            seed_masks.append(s)
    if len(seed_masks) < 2:
        return inst.copy()
    lab = _watershed_assign(region, seed_masks, erode_px)
    out = inst.copy().astype(np.int32)
    new_ids = [ids[0]] + [int(inst.max()) + j for j in range(1, len(seed_masks))]
    for j in range(1, len(seed_masks) + 1):
        out[lab == j] = new_ids[j - 1]
    return _relabel(out) if out.max() > 254 else out.astype(np.uint8)


def delete(inst: np.ndarray, point) -> np.ndarray:
    i = _id_at(inst, point)
    out = inst.copy()
    if i > 0:
        out[out == i] = 0
    return out


def apply_edits(inst: np.ndarray, mask: np.ndarray, edits: list[dict]) -> tuple[np.ndarray, dict[int, dict], list[dict]]:
    """Replay recorded edits. Returns (inst, overrides {id: {color, flags{}}}, failed edits)."""
    out = inst.copy()
    overrides: dict[int, dict] = {}
    failed = []
    for e in edits:
        op = e.get("op")
        try:
            if op == "merge":
                ids = {_id_at(out, p) for p in e["points"]} - {0}
                if len(ids) < 2:
                    raise ValueError("fewer than two instances under the points")
                out = merge(out, e["points"])
            elif op == "split":
                before = int(len(np.unique(out)))
                out = split_seeded(out, mask, e["seeds"])
                if len(np.unique(out)) == before:
                    raise ValueError("split produced no new instance")
            elif op == "delete":
                if _id_at(out, e["point"]) == 0:
                    raise ValueError("no instance under the point")
                out = delete(out, e["point"])
            elif op in ("color", "flag"):
                i = _id_at(out, e["point"])
                if i == 0:
                    raise ValueError("no instance under the point")
                ov = overrides.setdefault(i, {"flags": {}})
                if op == "color":
                    ov["color"] = e["color"]
                else:
                    ov["flags"][e["flag"]] = bool(e.get("value", True))
            else:
                raise ValueError(f"unknown op {op!r}")
        except Exception as ex:   # noqa: BLE001 — report and continue; the tool shows failures
            failed.append(e | {"error": str(ex)})
    return out, overrides, failed


def check_consistency(mask: np.ndarray, inst: np.ndarray) -> dict:
    """Class pixels with no instance, instance pixels outside the class/ignore mask, id list."""
    barrel = np.isin(mask, BARREL_CLASSES)
    return {"unassigned_class_px": int((barrel & (inst == 0)).sum()),
            "outside_mask_px": int(((inst > 0) & ~np.isin(mask, (ORANGE, BLUE, IGNORE))).sum()),
            "ids": [int(i) for i in np.unique(inst) if i > 0]}
