"""Fixed train/dev/test splits (docs/EVAL.md). Stored in data/splits.json, append-only.

Assignment is stratified by condition (light_surface_scene) and seeded, so it is
reproducible. Stems already assigned are never moved; new stems get assigned when added.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from .io import PKG_ROOT, parse_name

SPLITS_PATH = PKG_ROOT / "data" / "splits.json"
SPLIT_NAMES = ("train", "dev", "test")


def load_splits(path: Path | str | None = None) -> dict[str, list[str]]:
    path = Path(path or SPLITS_PATH)
    if not path.exists():
        return {s: [] for s in SPLIT_NAMES}
    d = json.loads(path.read_text())
    return {s: list(d.get(s, [])) for s in SPLIT_NAMES}


def save_splits(splits: dict[str, list[str]], path: Path | str | None = None) -> Path:
    path = Path(path or SPLITS_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({s: sorted(splits[s]) for s in SPLIT_NAMES}, indent=2) + "\n")
    return path


def _condition(stem: str) -> str:
    try:
        t = parse_name(stem)
        return f"{t['light']}_{t['surface']}_{t['scene']}"
    except ValueError:
        return "unknown"


def _allocate(n: int, fractions: tuple[float, float, float]) -> tuple[int, int, int]:
    """How many of n go to (train, dev, test). Small groups: 1→train; 2→train,test; 3→one each."""
    if n <= 0:
        return 0, 0, 0
    if n == 1:
        return 1, 0, 0
    if n == 2:
        return 1, 0, 1
    if n == 3:
        return 1, 1, 1
    n_test = max(1, round(n * fractions[2]))
    n_dev = max(1, round(n * fractions[1]))
    return n - n_dev - n_test, n_dev, n_test


def assign(stems: list[str], splits: dict[str, list[str]] | None = None, seed: int = 0,
           fractions: tuple[float, float, float] = (0.6, 0.2, 0.2)) -> dict[str, list[str]]:
    """Return splits with every stem assigned; existing assignments are kept."""
    splits = {s: list(v) for s, v in (splits or load_splits()).items()}
    assigned = {x for v in splits.values() for x in v}
    new = sorted(set(stems) - assigned)
    groups: dict[str, list[str]] = {}
    for s in new:
        groups.setdefault(_condition(s), []).append(s)
    rng = random.Random(seed)
    for cond in sorted(groups):
        items = sorted(groups[cond])
        rng.shuffle(items)
        n_train, n_dev, n_test = _allocate(len(items), fractions)
        splits["test"] += items[:n_test]
        splits["dev"] += items[n_test:n_test + n_dev]
        splits["train"] += items[n_test + n_dev:]
    return splits


def split_of(stem: str, splits: dict[str, list[str]]) -> str | None:
    for s in SPLIT_NAMES:
        if stem in splits[s]:
            return s
    return None
