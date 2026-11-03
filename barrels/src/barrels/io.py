"""Image/mask IO and the data-folder conventions from docs/DATA.md.

Mask values (single-channel PNG, same stem as the image + ``_mask``):
    0   other (table, background, anything non-barrel)
    1   barrel orange (orange body, or the orange stripe of a blue barrel)
    2   barrel blue   (blue body, or the blue stripe of an orange barrel)
    255 ignore (glare / uncertain) — excluded from eval
"""
from __future__ import annotations

import re
from pathlib import Path

import cv2
import numpy as np

OTHER, ORANGE, BLUE, IGNORE = 0, 1, 2, 255
MASK_VALUES = (OTHER, ORANGE, BLUE, IGNORE)
CLASS_NAMES = {OTHER: "other", ORANGE: "orange", BLUE: "blue", IGNORE: "ignore"}

PKG_ROOT = Path(__file__).resolve().parents[2]  # .../barrels
RAW_DIR = PKG_ROOT / "data" / "raw"
LABELS_DIR = PKG_ROOT / "data" / "labels"

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg")
_NAME_RE = re.compile(r"^(?P<robot>[^_]+)_(?P<light>[^_]+)_(?P<surface>[^_]+)_(?P<scene>[^_]+)_(?P<nn>\d{2})$")


INSTANCE_MAX_ID = 254
INSTANCE_JSON_VERSION = 1


def inst_path(image_path: Path | str, labels_dir: Path | str | None = None) -> Path:
    """``data/labels/<stem>_inst.png`` — uint8 per-barrel instance ids (0 = none)."""
    image_path = Path(image_path)
    return Path(labels_dir or LABELS_DIR) / f"{image_path.stem}_inst.png"


def inst_json_path(image_path: Path | str, labels_dir: Path | str | None = None) -> Path:
    image_path = Path(image_path)
    return Path(labels_dir or LABELS_DIR) / f"{image_path.stem}_inst.json"


def file_sha1(path: Path | str) -> str:
    import hashlib
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()


def mask_path(image_path: Path | str, labels_dir: Path | str | None = None) -> Path:
    """``data/labels/<stem>_mask.png`` for an image path."""
    image_path = Path(image_path)
    return Path(labels_dir or LABELS_DIR) / f"{image_path.stem}_mask.png"


def strokes_path(image_path: Path | str, labels_dir: Path | str | None = None) -> Path:
    """``data/labels/<stem>_strokes.png`` — the hand strokes a mask was grown from."""
    image_path = Path(image_path)
    return Path(labels_dir or LABELS_DIR) / f"{image_path.stem}_strokes.png"


# side files that may sit next to an image and are never images to label/evaluate
SIDE_SUFFIXES = ("_mask", "_strokes", "_inst", "_pred", "_overlay", "_orange", "_blue", "_boxes")


def list_images(raw_dir: Path | str | None = None) -> list[Path]:
    """Sorted image files in a folder, excluding mask/stroke/instance/prediction side files."""
    raw_dir = Path(raw_dir or RAW_DIR)
    return sorted(
        p for p in raw_dir.iterdir()
        if p.suffix.lower() in IMAGE_SUFFIXES
        and not p.stem.endswith(SIDE_SUFFIXES)
    )


def parse_name(stem: str) -> dict[str, str]:
    """Split ``{robot}_{light}_{surface}_{scene}_{nn}`` into its tags. Raises ValueError otherwise."""
    m = _NAME_RE.match(stem)
    if not m:
        raise ValueError(f"filename does not follow {{robot}}_{{light}}_{{surface}}_{{scene}}_{{nn}}: {stem!r}")
    return m.groupdict()


def load_image(path: Path | str) -> np.ndarray:
    """BGR uint8 HxWx3 (OpenCV order). Raises FileNotFoundError."""
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    return img


def validate_mask(mask: np.ndarray) -> None:
    if mask.ndim != 2 or mask.dtype != np.uint8:
        raise ValueError(f"mask must be a 2-D uint8 array, got {mask.dtype} shape {mask.shape}")
    bad = np.setdiff1d(np.unique(mask), MASK_VALUES)
    if bad.size:
        raise ValueError(f"mask contains values outside {MASK_VALUES}: {bad.tolist()}")


def load_mask(path: Path | str) -> np.ndarray:
    """Single-channel uint8 mask. Raises FileNotFoundError / ValueError on bad values."""
    mask = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if mask is None:
        raise FileNotFoundError(path)
    if mask.ndim == 3:  # tolerate a gray image saved as 3-channel
        if not (mask[..., 0] == mask[..., 1]).all() or not (mask[..., 0] == mask[..., 2]).all():
            raise ValueError(f"mask is a color image, expected single channel: {path}")
        mask = mask[..., 0]
    mask = mask.astype(np.uint8)
    validate_mask(mask)
    return mask


def save_mask(path: Path | str, mask: np.ndarray) -> Path:
    """Write a validated mask as a single-channel PNG, creating the folder if needed."""
    validate_mask(mask)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), mask):
        raise OSError(f"could not write {path}")
    return path


def load_strokes(path: Path | str) -> np.ndarray:
    """Single-channel uint8 strokes image (values 0–4; see labeling.py)."""
    s = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if s is None:
        raise FileNotFoundError(path)
    if s.ndim == 3:
        s = s[..., 0]
    return s.astype(np.uint8)


def save_strokes(path: Path | str, strokes: np.ndarray) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), strokes.astype(np.uint8)):
        raise OSError(f"could not write {path}")
    return path


# ---------------------------------------------------------------- instances

def validate_instances(inst: np.ndarray) -> None:
    if inst.ndim != 2 or inst.dtype != np.uint8:
        raise ValueError(f"instance mask must be a 2-D uint8 array, got {inst.dtype} shape {inst.shape}")
    if inst.max(initial=0) > INSTANCE_MAX_ID:
        raise ValueError(f"instance ids must be <= {INSTANCE_MAX_ID}")


def instance_records(inst: np.ndarray, mask: np.ndarray | None = None) -> list[dict]:
    """Geometry of every instance id present: bbox [x0, y0, x1, y1] half-open, area, bottom_mid,
    and per-class pixel counts when the class mask is given. Pure function of the arrays."""
    out = []
    for i in np.unique(inst):
        if i == 0:
            continue
        sel = inst == i
        ys, xs = np.where(sel)
        x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
        rec = {"id": int(i), "bbox": [x0, y0, x1, y1], "area": int(sel.sum()), "bottom_mid": [(x0 + x1) / 2, y1]}
        if mask is not None:
            rec["px"] = {"orange": int((mask[sel] == ORANGE).sum()), "blue": int((mask[sel] == BLUE).sum()),
                         "ignore": int((mask[sel] == IGNORE).sum())}
        out.append(rec)
    return out


def load_instances(image_or_stem: Path | str, labels_dir: Path | str | None = None,
                   check_mask: bool = True) -> tuple[np.ndarray, dict]:
    """(instance ids uint8 HxW, metadata dict). Raises if the JSON's cached geometry disagrees with
    the PNG, or (check_mask) if the class mask changed since the instances were made."""
    stem = Path(image_or_stem).stem
    png = Path(labels_dir or LABELS_DIR) / f"{stem}_inst.png"
    js = Path(labels_dir or LABELS_DIR) / f"{stem}_inst.json"
    inst = cv2.imread(str(png), cv2.IMREAD_UNCHANGED)
    if inst is None:
        raise FileNotFoundError(png)
    if inst.ndim == 3:
        inst = inst[..., 0]
    inst = inst.astype(np.uint8)
    validate_instances(inst)
    import json
    meta = json.loads(js.read_text())
    cached = {b["id"]: b for b in meta.get("barrels", [])}
    live = {r["id"]: r for r in instance_records(inst)}
    if set(cached) != set(live) or any(cached[i]["bbox"] != live[i]["bbox"] or cached[i]["area"] != live[i]["area"] for i in live):
        raise ValueError(f"{js.name} is stale: cached boxes/areas disagree with {png.name}")
    if check_mask and meta.get("mask_sha1"):
        mp = Path(labels_dir or LABELS_DIR) / f"{stem}_mask.png"
        if mp.exists() and file_sha1(mp) != meta["mask_sha1"]:
            raise ValueError(f"{js.name} is stale: {mp.name} changed since the instances were made")
    return inst, meta


def save_instances(image_or_stem: Path | str, inst: np.ndarray, meta: dict,
                   labels_dir: Path | str | None = None) -> tuple[Path, Path]:
    """Write <stem>_inst.png + <stem>_inst.json; the JSON's barrels[] geometry is refreshed from the array."""
    import json
    validate_instances(inst)
    stem = Path(image_or_stem).stem
    d = Path(labels_dir or LABELS_DIR); d.mkdir(parents=True, exist_ok=True)
    png, js = d / f"{stem}_inst.png", d / f"{stem}_inst.json"
    if not cv2.imwrite(str(png), inst):
        raise OSError(f"could not write {png}")
    meta = dict(meta); meta.setdefault("version", INSTANCE_JSON_VERSION); meta["stem"] = stem
    live = {r["id"]: r for r in instance_records(inst)}
    old = {b["id"]: b for b in meta.get("barrels", [])}
    meta["barrels"] = [old.get(i, {}) | live[i] for i in sorted(live)]
    js.write_text(json.dumps(meta, indent=1) + "\n")
    return png, js


# ---------------------------------------------------------------- box labels (v2, docs/DATA.md "Box labels")

BOXES_JSON_VERSION = 1
BOX_FLAGS = ("occluded", "truncated", "held", "bottom_estimated", "no_stripe")
FRAME_W, FRAME_H = 640, 480
# how the v1.5 instance flags map onto box flags (top_only = lid only, bottom below the frame -> truncated)
INST_TO_BOX_FLAGS = {"occluded": "occluded", "truncated": "truncated", "top_only": "truncated", "no_stripe": "no_stripe"}


def boxes_path(image_or_stem: Path | str, labels_dir: Path | str | None = None) -> Path:
    """``data/labels/<stem>_boxes.json`` — one box per barrel, the v2 detection ground truth."""
    return Path(labels_dir or LABELS_DIR) / f"{Path(image_or_stem).stem}_boxes.json"


def find_image(stem: str, raw_dir: Path | str | None = None) -> Path | None:
    """The raw image for a stem (png/jpg/jpeg), or None."""
    for suf in IMAGE_SUFFIXES:
        p = Path(raw_dir or RAW_DIR) / f"{stem}{suf}"
        if p.exists():
            return p
    return None


def touches_frame(bbox, shape: tuple[int, int] = (FRAME_H, FRAME_W)) -> bool:
    """True when a half-open box reaches any frame edge (the barrel may be cut by the frame)."""
    x0, y0, x1, y1 = bbox
    return x0 <= 0 or y0 <= 0 or x1 >= shape[1] or y1 >= shape[0]


def validate_boxes(meta: dict, shape: tuple[int, int] = (FRAME_H, FRAME_W)) -> None:
    """Raise ValueError unless ``meta`` is a well-formed box label: a 'barrels' list whose boxes are four
    ints, half-open, non-empty and inside the frame; colors orange|blue; flags from BOX_FLAGS; unique
    ids; and 'negative' true exactly when the list is empty."""
    h, w = shape
    if not isinstance(meta, dict) or not isinstance(meta.get("barrels"), list):
        raise ValueError("box label needs a 'barrels' list")
    ids: set = set()
    for b in meta["barrels"]:
        bb = b.get("bbox")
        if not (isinstance(bb, (list, tuple)) and len(bb) == 4 and all(isinstance(v, (int, np.integer)) and not isinstance(v, bool) for v in bb)):
            raise ValueError(f"bbox must be four ints [x0, y0, x1, y1], got {bb!r}")
        x0, y0, x1, y1 = (int(v) for v in bb)
        if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
            raise ValueError(f"bbox {bb} is empty or outside the {w}x{h} frame")
        if b.get("color") not in ("orange", "blue"):
            raise ValueError(f"color must be 'orange' or 'blue', got {b.get('color')!r}")
        bad = set(b.get("flags", ())) - set(BOX_FLAGS)
        if bad:
            raise ValueError(f"unknown flags {sorted(bad)}; allowed: {BOX_FLAGS}")
        if "id" in b:
            if b["id"] in ids:
                raise ValueError(f"duplicate barrel id {b['id']}")
            ids.add(b["id"])
    if bool(meta.get("negative", not meta["barrels"])) != (not meta["barrels"]):
        raise ValueError("'negative' must be true exactly when there are no barrels")


def load_boxes(image_or_stem: Path | str, labels_dir: Path | str | None = None, *,
               check_image: bool = True, raw_dir: Path | str | None = None) -> dict:
    """The box label dict for a stem. Raises FileNotFoundError, or ValueError when the content is bad or
    (check_image, image found in raw_dir) the image changed since the boxes were drawn."""
    import json
    stem = Path(image_or_stem).stem
    p = boxes_path(stem, labels_dir)
    if not p.exists():
        raise FileNotFoundError(p)
    meta = json.loads(p.read_text())
    validate_boxes(meta)
    if check_image and meta.get("image_sha1"):
        img = find_image(stem, raw_dir)
        if img is not None and file_sha1(img) != meta["image_sha1"]:
            raise ValueError(f"{p.name} is stale: {img.name} changed since the boxes were drawn")
    return meta


def save_boxes(image_or_stem: Path | str, meta: dict, labels_dir: Path | str | None = None) -> Path:
    """Validate and write ``<stem>_boxes.json``: barrels sorted left to right and renumbered 1..N, bbox as
    ints, flags in BOX_FLAGS order, 'negative' derived from the list, 'clean' default true."""
    import json
    validate_boxes(meta)
    stem = Path(image_or_stem).stem
    out = {"version": BOXES_JSON_VERSION, "stem": stem, "image_sha1": meta.get("image_sha1", ""),
           "reviewed": bool(meta.get("reviewed", False)), "negative": not meta["barrels"],
           "clean": bool(meta.get("clean", True)), "source": meta.get("source", "manual"), "barrels": []}
    for i, b in enumerate(sorted(meta["barrels"], key=lambda b: (b["bbox"][0], b["bbox"][1])), 1):
        out["barrels"].append({"id": i, "color": b["color"], "bbox": [int(v) for v in b["bbox"]],
                               "flags": [f for f in BOX_FLAGS if f in b.get("flags", ())], "note": b.get("note", "")})
    p = boxes_path(stem, labels_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1) + "\n")
    return p


def boxes_from_instances(inst_meta: dict, image_sha1: str = "", shape: tuple[int, int] = (FRAME_H, FRAME_W)) -> dict:
    """A provisional (reviewed=false) box label from a v1.5 instance JSON: one box per instance around its
    visible pixels (not yet the full barrel — the labeler fixes occluded ones), body color kept, flags
    mapped by INST_TO_BOX_FLAGS, 'truncated' added when the box touches the frame."""
    barrels = []
    for r in inst_meta.get("barrels", []):
        flags = {INST_TO_BOX_FLAGS[f] for f in r.get("flags", ()) if f in INST_TO_BOX_FLAGS}
        if touches_frame(r["bbox"], shape):
            flags.add("truncated")
        barrels.append({"id": r["id"], "color": r["color"], "bbox": [int(v) for v in r["bbox"]], "flags": sorted(flags), "note": ""})
    meta = {"version": BOXES_JSON_VERSION, "stem": inst_meta.get("stem", ""), "image_sha1": image_sha1, "reviewed": False,
            "negative": not barrels, "clean": True, "source": "from_inst", "barrels": barrels}
    validate_boxes(meta, shape)
    return meta
