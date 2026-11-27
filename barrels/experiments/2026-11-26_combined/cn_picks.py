#!/usr/bin/env python3
"""ADDENDUM 2026-11-27 of experiment 2026-11-26_combined: the third winner (the stripe by color difference) on this
branch. Run in a process of its own: contrast's experiment folder has a ``common.py`` of its own, as self-calibration's
has, and its fold rule builds its table in a process pool.

    python barrels/experiments/2026-11-26_combined/cn_picks.py

1. **Reproduction.** Contrast's own judged candidate (``experiments/2026-11-26_contrast/table.py:fit``, the family
   C1) through the standard judge, leave one place out, on this branch; compared with the pages committed on its
   branch (``results/2026-11-26_contrast/judge_C1_add_guards/judge.json``): totals, places, conditions, report-only
   conditions, every changed barrel, every frame with changed boxes, and what each fold picked.
2. **Its picks per held-out place**, by its own rule (``table.choose`` over its 48 settings, on the ordinary train
   frames of the other places), and the pick on all ordinary places (for the report-only places): written to
   results/2026-11-26_combined/cn_chosen.json as the full ``contrast.Params`` of each pick. The combinations read
   them from there (``candidates.py``); nothing is chosen for a combination.

Train frames only (``judge.load_frame``). Exit 0 = identical.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
CN_DIR = BARRELS / "experiments" / "2026-11-26_contrast"
OUT = BARRELS / "results" / "2026-11-26_combined"
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(CN_DIR))
sys.path.insert(0, str(HERE))

import table as tb  # noqa: E402  (contrast's)
from jdiff import KEYS, diff, norm  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402

FAMILY = "C1_add_guards"
REF = BARRELS / "results" / "2026-11-26_contrast" / "judge_C1_add_guards"


def main() -> int:
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    truth = jg.load_truth(ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED])
    table = tb.build_table(ordinary, tb.FAMILIES[FAMILY])
    fitter = tb.Fitter(table, jg.load_truth(ordinary).placements)
    j = jg.judge(fit=fitter.fit(FAMILY), name="contrast", out_dir=OUT / "repro_contrast", frames=frames, truth=truth)
    now, old = norm(jg.to_json(j)), json.loads((REF / "judge.json").read_text())
    d = [x for k in KEYS for x in diff(now[k], old[k], k)]
    b, c = j.total
    picks_old = {p: v["spec"] for p, v in json.loads((REF.parent / "chosen.json").read_text())["folds"][FAMILY].items()}
    picks_now = {p: v["spec"] for p, v in fitter.chosen[FAMILY].items()}
    same = not d and now["verdict"] == old["verdict"] and picks_now == picks_old
    lines = ["# Addendum: the third winner (contrast) alone on this branch, against its own committed judge pages", "",
             "Made by `experiments/2026-11-26_combined/cn_picks.py`.", "",
             f"## contrast: {'IDENTICAL' if same else 'DIFFERENT'}", "",
             f"- verdict {now['verdict']} (committed {old['verdict']}); found {b.found_w:.2f} -> {c.found_w:.2f} of {b.placements} placements "
             f"(committed {old['total']['candidate']['found_w']:.2f}), per frame {b.found} -> {c.found} (committed {old['total']['candidate']['found']}); "
             f"boxes not on their barrel {b.extra_w:.2f} -> {c.extra_w:.2f} (committed {old['total']['candidate']['extra_w']:.2f}); "
             f"{sum(1 for x in j.changes if x.judged and x.kind == 'gained')} gained, {sum(1 for x in j.changes if x.judged and x.kind == 'lost')} lost.",
             f"- compared: {', '.join(KEYS)}: {len(d)} difference(s)."] + [f"  - {x}" for x in d[:20]]
    lines += ["", f"## what each fold picked: {'IDENTICAL' if picks_now == picks_old else 'DIFFERENT'}", ""]
    lines += [f"- {p}: `{picks_now.get(p)}`" + ("" if picks_now.get(p) == picks_old.get(p) else f" (committed `{picks_old.get(p)}`)") for p in sorted(set(picks_now) | set(picks_old))]
    # the picks the combinations use: per ordinary place (the other places), and on all ordinary places
    picks = {}
    for place in sorted({ct.place_of(s) for s in ordinary}):
        st, _ = fitter._pick(FAMILY, [s for s in ordinary if ct.place_of(s) != place])
        picks[place] = None if st is None else {"spec": st.spec, "params": dataclasses.asdict(st.params())}
    st, _ = fitter._pick(FAMILY, ordinary)
    picks["(any place that is not an ordinary one)"] = None if st is None else {"spec": st.spec, "params": dataclasses.asdict(st.params())}
    for p in picks_now:
        if p in picks and picks[p] is not None and picks[p]["spec"] != picks_now[p]:
            same = False
            lines.append(f"- MISMATCH at {p}: the pick for the combinations `{picks[p]['spec']}` is not the judged fold's `{picks_now[p]}`")
    (OUT / "cn_chosen.json").write_text(json.dumps(picks, indent=1) + "\n")
    lines += ["", f"RESULT: {'contrast reproduces exactly' if same else 'NOT identical: see above'}."]
    (OUT / "repro_contrast.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
