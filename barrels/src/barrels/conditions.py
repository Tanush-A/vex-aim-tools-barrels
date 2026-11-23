"""Where and under what kind of light a condition was shot (2026-11-23): the small table
``data/conditions.json``, one entry per condition key ``{light}_{surface}``.

Two attributes per condition, both used by the adaptive-threshold analysis (``experiments/2026-11-24_adaptive``):

- ``place``: the table AND the room. The four ottoman conditions are one place (one table, one room, one lamp
  at four settings): their frames are not independent evidence about a new place, so the honest test of any
  rule fit across conditions holds out a whole place at a time.
- ``light``: the kind of source, ``window`` / ``overhead`` / ``lamp`` / ``mixed`` (two kinds at once, e.g. a
  lamp with some window light).

A condition that is not in the file is guessed from its tags (place = the surface tag; light from the light tag's
prefix: window / overhead / lamp, ``both`` or ``mix*`` = mixed, anything else ``unknown``) and marked
``guessed``; every summary that uses the table names the guessed ones, so the data session adds them.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .io import PKG_ROOT

TABLE_PATH = PKG_ROOT / "data" / "conditions.json"
LIGHT_KINDS = ("window", "overhead", "lamp", "mixed")
UNKNOWN = "unknown"


@dataclass(frozen=True)
class ConditionInfo:
    key: str
    place: str
    light: str          # one of LIGHT_KINDS, or "unknown" when guessed and the tag says nothing
    guessed: bool       # True: not in the table, read off the tags
    note: str = ""


def guess_light(light_tag: str) -> str:
    """The light kind a light tag suggests: ``window*``, ``overhead*``, ``lamp*``; ``both*`` / ``mix*`` = mixed."""
    t = light_tag.lower()
    if t.startswith(("both", "mix")):
        return "mixed"
    for kind in ("window", "overhead", "lamp"):
        if t.startswith(kind):
            return kind
    return UNKNOWN


def load_table(path: Path | str = TABLE_PATH) -> dict[str, dict]:
    """{condition key: {"place", "light", "note"}}; raises ValueError on a bad entry. A missing file = {}."""
    path = Path(path)
    if not path.exists():
        return {}
    d = json.loads(path.read_text())
    if d.get("version") != 1 or not isinstance(d.get("conditions"), dict):
        raise ValueError(f"{path}: expected version 1 with a 'conditions' object")
    for k, v in d["conditions"].items():
        if "_" not in k:
            raise ValueError(f"{path}: condition key {k!r} is not {{light}}_{{surface}}")
        if not isinstance(v, dict) or not v.get("place") or v.get("light") not in LIGHT_KINDS:
            raise ValueError(f"{path}: entry {k!r} needs a place and a light in {LIGHT_KINDS}, got {v!r}")
    return d["conditions"]


@lru_cache(maxsize=4)
def _cached(path: str) -> dict:
    return load_table(path)


def info(key: str, table: dict | None = None) -> ConditionInfo:
    """The place and light kind of a condition key, from the table (``data/conditions.json`` when ``table`` is
    None) or guessed from the tags."""
    table = _cached(str(TABLE_PATH)) if table is None else table
    if key in table:
        e = table[key]
        return ConditionInfo(key, e["place"], e["light"], False, e.get("note", ""))
    light, _, surface = key.partition("_")
    return ConditionInfo(key, surface or key, guess_light(light), True, "not in data/conditions.json: guessed from the tags")
