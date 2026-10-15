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


def mask_path(image_path: Path | str, labels_dir: Path | str | None = None) -> Path:
    """``data/labels/<stem>_mask.png`` for an image path."""
    image_path = Path(image_path)
    return Path(labels_dir or LABELS_DIR) / f"{image_path.stem}_mask.png"


def strokes_path(image_path: Path | str, labels_dir: Path | str | None = None) -> Path:
    """``data/labels/<stem>_strokes.png`` — the hand strokes a mask was grown from."""
    image_path = Path(image_path)
    return Path(labels_dir or LABELS_DIR) / f"{image_path.stem}_strokes.png"


def list_images(raw_dir: Path | str | None = None) -> list[Path]:
    """Sorted image files in a folder, excluding mask/stroke side files."""
    raw_dir = Path(raw_dir or RAW_DIR)
    return sorted(
        p for p in raw_dir.iterdir()
        if p.suffix.lower() in IMAGE_SUFFIXES
        and not p.stem.endswith(("_mask", "_strokes"))
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
