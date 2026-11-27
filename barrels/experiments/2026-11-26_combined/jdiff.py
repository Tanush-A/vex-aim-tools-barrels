"""Comparing two judge pages (judge.json), value by value: used by repro.py and cn_picks.py. No imports from the
experiment folders, so it can be loaded next to any of them."""
from __future__ import annotations

import json

KEYS = ("total", "places", "conditions", "report_only", "changes", "box_changes")


def norm(x):
    return json.loads(json.dumps(x, default=str))


def diff(a, b, path="") -> list[str]:
    """Where two JSON values differ."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return [] if abs(a - b) < 1e-9 else [f"{path}: {a!r} != {b!r}"]
    if type(a) is not type(b):
        return [f"{path}: {a!r} != {b!r}"]
    if isinstance(a, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: only in {'now' if k in a else 'the committed page'}")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{path}: {len(a)} items now, {len(b)} committed"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in diff(x, y, f"{path}[{i}]")]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]
