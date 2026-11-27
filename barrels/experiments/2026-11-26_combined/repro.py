#!/usr/bin/env python3
"""STEP A of experiment 2026-11-26_combined: each winner ALONE, on this branch (the collapsed detector), must give
exactly the judged numbers it gave on its own branch (the detector before the collapse).

    python barrels/experiments/2026-11-26_combined/repro.py

For each winner its own ``fit`` function is run through the standard judge, leave one place out, and the judge's
pages are compared with the ones committed on the winner's branch: the totals, every place, every condition, the
report-only conditions, every barrel that changed state and every frame whose boxes changed. No combination is run
here. Writes results/2026-11-26_combined/repro_<winner>/ (the judge's pages) and repro.md. Exit 0 = both identical.
"""
from __future__ import annotations

import json
import sys

import cb_common as cb
from barrels import conditions as cnd
from barrels import judge as jg

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


def main() -> int:
    frames = jg.train_frames()
    truth = jg.load_truth(frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED])
    lines = ["# Step A: each winner alone on the collapsed detector, against its own committed judge pages", "",
             "Made by `experiments/2026-11-26_combined/repro.py`. The same `fit` functions, the same judge, leave one place out; "
             "the only thing that differs from the winners' own runs is `detector.py` (collapsed on 2026-11-26).", ""]
    ok = True
    for name, fit, ref in (("nearmiss", cb.nm_cand.fit_partner, cb.NM_REF), ("selfcal", cb.sc_cand.fit_AB, cb.SC_REF)):
        j = jg.judge(fit=fit, name=name, out_dir=cb.RESULTS / f"repro_{name}", frames=frames, truth=truth)
        now, old = norm(jg.to_json(j)), json.loads((ref / "judge.json").read_text())
        d = [x for k in KEYS for x in diff(now[k], old[k], k)]
        b, c = j.total
        gained = sum(1 for x in j.changes if x.judged and x.kind == "gained")
        lost = sum(1 for x in j.changes if x.judged and x.kind == "lost")
        same = not d and now["verdict"] == old["verdict"]
        ok &= same
        part = [f"## {name}: {'IDENTICAL' if same else 'DIFFERENT'}", "",
                f"- verdict {now['verdict']} (committed: {old['verdict']}); found {b.found_w:.2f} -> {c.found_w:.2f} of {b.placements} placements "
                f"(committed {old['total']['candidate']['found_w']:.2f}), per frame {b.found} -> {c.found} (committed {old['total']['candidate']['found']}); "
                f"boxes not on their barrel {b.extra_w:.2f} -> {c.extra_w:.2f} (committed {old['total']['candidate']['extra_w']:.2f}); "
                f"{gained} barrels gained, {lost} lost (committed {sum(1 for x in old['changes'] if x['judged'] and x['kind'] == 'gained')} and "
                f"{sum(1 for x in old['changes'] if x['judged'] and x['kind'] == 'lost')}).",
                f"- compared: {', '.join(KEYS)} ({len(now['changes'])} changed barrels, {len(now['box_changes'])} frames with changed boxes, "
                f"{len(now['conditions'])} conditions, {len(now['report_only'])} report-only conditions): {len(d)} difference(s)."]
        part += [f"  - {x}" for x in d[:20]] + [""]
        lines += part
        print("\n".join(part), flush=True)
    folds_nm = {p: v["spec"] for p, v in cb.nm_cand.CHOSEN.get("B_partner_fit", {}).items()}
    old_nm = {p: v["spec"] for p, v in json.loads((cb.NM_REF / "extras.json").read_text())["folds"].items()}
    folds_sc = {p: v["setting"] for (fam, p), v in cb.sc_cand.CHOSEN.items() if fam == "AB"}
    old_sc = {k.split("|")[1]: v["setting"] for k, v in json.loads((cb.SC_REF.parent / "summary.json").read_text())["chosen"].items() if k.startswith("AB|")}
    for name, a, b_ in (("nearmiss", folds_nm, old_nm), ("selfcal", folds_sc, old_sc)):
        same = norm(a) == norm(b_)
        ok &= same
        part = [f"## what each fold chose, {name}: {'IDENTICAL' if same else 'DIFFERENT'}", ""]
        part += [f"- {p}: {json.dumps(a.get(p))}" + ("" if norm(a.get(p)) == norm(b_.get(p)) else f"  (committed: {json.dumps(b_.get(p))})") for p in sorted(set(a) | set(b_))] + [""]
        lines += part
        print("\n".join(part), flush=True)
    lines.append(f"RESULT: {'both winners reproduce exactly' if ok else 'NOT identical: see above'}.")
    cb.RESULTS.mkdir(parents=True, exist_ok=True)
    (cb.RESULTS / "repro.md").write_text("\n".join(lines) + "\n")
    print(lines[-1])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
