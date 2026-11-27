"""Shared by the scripts of experiment 2026-11-26_combined (TODO E8): the two winners' own experiment code, loaded
side by side, and the folders.

The two winners keep their code where it is (``experiments/2026-11-26_nearmiss``, ``experiments/2026-11-26_selfcal``).
Both folders hold a ``candidates.py``, so the two are loaded here under names of their own:

    nmc       nearmiss ``nm_common``: candidates by spec, the mask of a spec, ITS selection rule (``choose``)
    nm_cand   nearmiss ``candidates``: ``fit_partner`` (the judged winner), ``GRID_B``, ``FINAL_SPEC``
    scc       selfcal ``common``: the fixed model, the camera
    sc_cand   selfcal ``candidates``: ``fit_AB`` (the judged winner), ITS selection rule (``choose``), ``BASE``

TRAIN frames only: every image is read with ``judge.load_frame``, which refuses anything else.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))
NM_DIR = BARRELS / "experiments" / "2026-11-26_nearmiss"
SC_DIR = BARRELS / "experiments" / "2026-11-26_selfcal"
RESULTS = BARRELS / "results" / "2026-11-26_combined"
for _d in (NM_DIR, SC_DIR):
    if str(_d) not in sys.path:
        sys.path.append(str(_d))


def _load(name: str, path: Path):
    """A file as a module under a name of our choosing (two folders hold a ``candidates.py``)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


import barrels  # noqa: E402

if not str(Path(barrels.__file__).resolve()).startswith(str(BARRELS)):
    raise SystemExit(f"the barrels package is imported from {barrels.__file__}, not from this checkout ({BARRELS}): "
                     f"run with PYTHONPATH={BARRELS / 'src'}")

import nm_common as nmc  # noqa: E402
import common as scc  # noqa: E402

nm_cand = _load("nm_candidates", NM_DIR / "candidates.py")
sc_cand = _load("sc_candidates", SC_DIR / "candidates.py")

NM_REF = BARRELS / "results" / "2026-11-26_nearmiss" / "B_partner_fit"      # the judged pages of each winner, as committed on its branch
SC_REF = BARRELS / "results" / "2026-11-26_selfcal" / "AB"
