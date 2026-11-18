"""The never-regress rule as a check (TODO item I, 2026-11-18).

The rule (``docs/TODO.md``, "The goal"): no scenario row of the eval table on a protected data set (HOME and
CAMPUS) may get worse, and no box may appear on an empty frame of any data set. This module turns the rule into
a comparison of two sets of numbers; nothing here decides what a found barrel or a false box is, every count
comes from the one table (``report.py``, the v2 rule of ``docs/EVAL.md``).

In the order the data flows:

1. ``snapshot``   a ``report.Report`` -> the plain numbers of its candidate arm: for every data set and every
   scenario, frames / barrels / found / missed / false / boxes on empty frames, plus the git hash, the date and
   the arm they were made from. ``save_baseline`` writes it to ``results/baseline/baseline.json`` (committed).
2. ``load_protected``   the short list of protected sets, ``results/baseline/protected.json`` (HOME and CAMPUS).
   A new ordinary condition is protected by adding its name there and saving a new baseline.
3. ``compare``    stored baseline against this run, row by row -> one ``RowChange`` per scenario row:
   same / worse / better / new / gone / changed. Worse = fewer barrels found or more false boxes.
4. ``GateResult.passed``   false when a protected row is worse (or cannot be compared), or when any set, protected
   or not, has more boxes on empty frames than the baseline. Rows that are not in the baseline are "new" and
   never fail, so a new data set does not break the check.
5. ``format_gate``   the same as plain text, ending in RESULT: PASS or RESULT: FAIL.

The command is ``python barrels/tools/report.py --gate`` (and ``--save-baseline``).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .io import PKG_ROOT

BASELINE_DIR = PKG_ROOT / "results" / "baseline"
BASELINE_PATH = BASELINE_DIR / "baseline.json"        # the stored numbers (written by --save-baseline, committed)
PROTECTED_PATH = BASELINE_DIR / "protected.json"      # the protected sets: {"protected": ["HOME", "CAMPUS"]}
DEFAULT_PROTECTED = ("HOME", "CAMPUS")                # used when protected.json is missing
VERSION = 1
COUNTS = ("frames", "barrels", "found", "missed", "false", "neg_false")      # what is stored per row
ROW_KEYS = ("set", "label", "scene") + COUNTS


# ---------------------------------------------------------------- 1. the numbers of one run

def snapshot(rep, made: str = "") -> dict:
    """The candidate arm of a report as plain numbers: one row per data set x scenario, and one per data set
    (``scene`` = ""). The ALL row is left out (it is the sum of the others)."""
    from . import report as rp
    arm = rp.to_json(rep)["candidate"]
    rows = [{"set": r.set_key, "label": r.label, "scene": r.scene, **{k: int(getattr(r.cand, k)) for k in COUNTS}}
            for r in rep.rows if r.kind != "total"]
    return {"version": VERSION, "made": made, "git": rep.git, "arm": rep.candidate.describe(),
            "model_config_hash": arm.get("model_config_hash"), "det": arm.get("det"),
            "split": rep.selection.split, "home_protocol": rep.home_protocol, "rows": rows}


def validate(snap: dict) -> None:
    if not isinstance(snap, dict) or snap.get("version") != VERSION:
        raise ValueError(f"baseline version must be {VERSION}, got {snap.get('version') if isinstance(snap, dict) else snap!r}")
    if not isinstance(snap.get("rows"), list):
        raise ValueError("baseline needs a 'rows' list")
    for r in snap["rows"]:
        missing = [k for k in ROW_KEYS if k not in r]
        if missing:
            raise ValueError(f"baseline row {r!r} lacks {missing}")


def save_baseline(snap: dict, path: Path | str = BASELINE_PATH) -> Path:
    """Write the snapshot, one row per line so a change shows up as a one-line diff in git."""
    validate(snap)
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    head = {k: v for k, v in snap.items() if k != "rows"}
    text = json.dumps(head, indent=1)[:-2] + ',\n "rows": [\n' + ",\n".join("  " + json.dumps(r) for r in snap["rows"]) + "\n ]\n}\n"
    path.write_text(text)
    return path


def load_baseline(path: Path | str = BASELINE_PATH) -> dict:
    snap = json.loads(Path(path).read_text())
    validate(snap)
    return snap


# ---------------------------------------------------------------- 2. which sets are protected

def load_protected(path: Path | str = PROTECTED_PATH) -> tuple[str, ...]:
    """The protected set names (as the table prints them, e.g. HOME, or a full ``{robot}_{light}_{surface}`` key).
    ``DEFAULT_PROTECTED`` when the file is missing."""
    path = Path(path)
    if not path.exists():
        return DEFAULT_PROTECTED
    names = json.loads(path.read_text()).get("protected")
    if not (isinstance(names, list) and names and all(isinstance(n, str) and n for n in names)):
        raise ValueError(f"{path} must hold {{\"protected\": [set names]}}")
    return tuple(names)


def is_protected(row: dict, protected) -> bool:
    names = {n.strip().rstrip("*").upper() for n in protected}
    return row["label"].rstrip("*").upper() in names or row["set"].upper() in names


# ---------------------------------------------------------------- 3. row by row

@dataclass
class RowChange:
    """One row of the baseline next to the same row of this run."""
    set: str
    label: str
    scene: str                  # "" = the whole data set
    protected: bool
    status: str                 # same | worse | better | new (not in the baseline) | gone (not in this run) | changed (other frames or labels)
    base: dict | None
    cand: dict | None
    neg_gain: int = 0           # boxes on empty frames, this run minus baseline (a new row counts from 0); never below 0

    @property
    def name(self) -> str:
        return f"{self.label} {self.scene}" if self.scene else f"{self.label} (whole set)"

    @property
    def fails(self) -> bool:
        return self.neg_gain > 0 or (self.protected and self.status in ("worse", "gone", "changed"))

    def describe(self) -> str:
        b, c = self.base, self.cand
        if self.status == "new":
            text = f"found {c['found']} of {c['barrels']}, false boxes {c['false']}"
        elif self.status == "gone":
            text = f"was found {b['found']} of {b['barrels']}; the row is not in this run"
        elif self.status == "changed":
            text = (f"its frames or labels changed since the baseline ({b['frames']} frames, {b['barrels']} barrels -> "
                    f"{c['frames']} frames, {c['barrels']} barrels): cannot be compared")
        else:
            lost, more = b["found"] - c["found"], c["false"] - b["false"]
            text = f"found {b['found']} -> {c['found']} of {c['barrels']}" + (f" (lost {lost})" if lost > 0 else f" (gained {-lost})" if lost < 0 else "")
            text += f"; false boxes {b['false']} -> {c['false']}" + (f" ({more} more)" if more > 0 else f" ({-more} fewer)" if more < 0 else "")
        if self.neg_gain > 0:
            text += f"; {self.neg_gain} new box(es) on an empty frame"
        return text


def _change(b: dict | None, c: dict | None, protected) -> RowChange:
    ref = c or b
    if b is None:
        status, neg = "new", c["neg_false"]
    elif c is None:
        status, neg = "gone", 0
    else:
        neg = max(0, c["neg_false"] - b["neg_false"])
        if (b["frames"], b["barrels"]) != (c["frames"], c["barrels"]):
            status = "changed"
        else:
            lost, more = b["found"] - c["found"], c["false"] - b["false"]
            status = "worse" if lost > 0 or more > 0 else "better" if lost < 0 or more < 0 else "same"
    return RowChange(ref["set"], ref["label"], ref["scene"], is_protected(ref, protected), status, b, c, neg)


@dataclass
class GateResult:
    rows: list[RowChange]                   # the scenario rows: these decide
    totals: list[RowChange]                 # the whole-set rows: shown only
    protected: tuple[str, ...]
    baseline: dict                          # the stored snapshot's header (made, git, arm)
    current: dict
    notes: list[str] = field(default_factory=list)

    @property
    def failures(self) -> list[RowChange]:
        return [r for r in self.rows if r.fails]

    @property
    def passed(self) -> bool:
        return not self.failures


def compare(baseline: dict, current: dict, protected=DEFAULT_PROTECTED) -> GateResult:
    """Stored baseline against this run. Every scenario row of either side becomes a ``RowChange``; the rule is
    in ``RowChange.fails``: a protected row that is worse, gone or not comparable, or more boxes on empty frames
    than the baseline in any row of any set."""
    validate(baseline); validate(current)
    b = {(r["set"], r["scene"]): r for r in baseline["rows"]}
    c = {(r["set"], r["scene"]): r for r in current["rows"]}
    keys = list(c) + [k for k in b if k not in c]             # this run's order, then rows only the baseline has
    changes = [_change(b.get(k), c.get(k), protected) for k in keys]
    head = lambda s: {k: v for k, v in s.items() if k != "rows"}  # noqa: E731
    res = GateResult([x for x in changes if x.scene], [x for x in changes if not x.scene], tuple(protected), head(baseline), head(current))
    for name in protected:
        if not any(is_protected(r, [name]) for r in baseline["rows"]):
            res.notes.append(f"{name} is on the protected list but has no rows in the stored baseline: it is not protected until a new baseline is saved.")
    return res


# ---------------------------------------------------------------- 5. plain text

def format_gate(res: GateResult, title: str = "NEVER-REGRESS CHECK") -> str:
    prot = ", ".join(res.protected)
    out = [title,
           f"this run : {res.current.get('arm', '?')}; git {res.current.get('git', '?')}",
           f"baseline : saved {res.baseline.get('made', '?')} from git {res.baseline.get('git', '?')} ({res.baseline.get('arm', '?')})",
           f"Protected sets: {prot}. A scenario row of a protected set fails the check when it loses a found barrel or gains a false box.",
           "Every other set is listed for information and cannot fail it. A new box on an empty frame fails it in any set.", ""]

    def block(head: str, rows: list[RowChange], always: bool = True) -> None:
        if not rows and not always:
            return
        out.append(f"{head}: {len(rows)} row(s)" if rows else f"{head}: none")
        w = max([0] + [len(r.name) for r in rows])
        out.extend(f"  {r.name:{w}}  {r.describe()}" for r in rows)

    p = [r for r in res.rows if r.protected]
    o = [r for r in res.rows if not r.protected]
    block("GOT WORSE in a protected set", [r for r in p if r.status == "worse"])
    block("GOT BETTER in a protected set", [r for r in p if r.status == "better"])
    block("NEW BOX ON AN EMPTY FRAME (any set)", [r for r in res.rows if r.neg_gain > 0])
    block("CANNOT BE COMPARED in a protected set (check the table by eye, then save a new baseline)",
          [r for r in p if r.status in ("changed", "gone")], always=False)
    new_sets = [t for t in res.totals if t.status == "new"]
    new_rows = [r for r in res.rows if r.status == "new" and r.set not in {t.set for t in new_sets}]
    block("NEW since the baseline (not compared, cannot fail)", new_sets + new_rows, always=False)
    block("Other sets, for information only: got worse", [r for r in o if r.status == "worse"], always=False)
    block("Other sets, for information only: got better", [r for r in o if r.status == "better"], always=False)
    block("Other sets, for information only: frames changed or gone", [r for r in o if r.status in ("changed", "gone")], always=False)

    out += ["", "Set totals, baseline -> this run:"]
    w = max([0] + [len(t.label) for t in res.totals])
    for t in res.totals:
        tag = "protected" if t.protected else "information only"
        if t.status in ("new", "gone"):
            out.append(f"  {t.label:{w}}  {t.describe()}  [{tag}, {'new' if t.status == 'new' else 'not in this run'}]")
        else:
            b, c = t.base, t.cand
            out.append(f"  {t.label:{w}}  found {b['found']} -> {c['found']} of {c['barrels']}; false boxes {b['false']} -> {c['false']}; "
                       f"boxes on empty frames {b['neg_false']} -> {c['neg_false']}  [{tag}]")
    out += [""] + [f"Note: {n}" for n in res.notes]

    if res.passed:
        out.append(f"RESULT: PASS. No scenario row of {prot} lost a found barrel or gained a false box, and no set gained a box on an empty frame.")
    else:
        f = res.failures
        why = []
        worse = [r.name for r in f if r.protected and r.status == "worse"]
        neg = [r.name for r in f if r.neg_gain > 0]
        cannot = [r.name for r in f if r.protected and r.status in ("changed", "gone")]
        if worse:
            why.append(f"{len(worse)} protected row(s) got worse ({', '.join(worse)})")
        if neg:
            why.append(f"a new box on an empty frame in {len(neg)} row(s) ({', '.join(neg)})")
        if cannot:
            why.append(f"{len(cannot)} protected row(s) cannot be compared ({', '.join(cannot)})")
        out.append("RESULT: FAIL. " + "; ".join(why) + ". This change must not become the default as it is.")
    return "\n".join(out)
