"""Exploration 2 (IN-SAMPLE, before PREREG; listed there): a few settings of the two-pass detector on the ordinary
and extreme train frames, counted per condition. No verdict is computed here.

    python barrels/experiments/2026-11-26_selfcal/explore2.py [name ...]       # default: every setting below
"""
import sys

import common as cm
from barrels import conditions as cnd
from barrels import judge as jg
from barrels import selfcal as sc

C = sc.SelfCalConfig
SETTINGS = {
    "A_found_frame": C(seed_body=False, seed_stripe=False, local=False),
    "A_any_frame": C(seed_body=False, seed_stripe=False, local=False, found_flags="any"),
    "B_local": C(seed_found=False, frame=False),
    "B_local_rel1": C(seed_found=False, frame=False, rel_margin=1.0),
    "B_frame": C(seed_found=False, local=False),
    "AB_both": C(),
    "AB_both_rel1": C(rel_margin=1.0),
    "AB_both_r2": C(rounds=2),
    "AB_both_second": C(combine="second"),
}


def main(argv) -> int:
    names = argv or list(SETTINGS)
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME]
    truth = jg.load_truth(stems)
    for n in names:
        recs = cm.run_setting(SETTINGS[n], stems, truth)
        t = cm.tally_ordinary(recs, frames, truth)
        print(f"\n=== {n}: ordinary found {t.found_w:.1f} of {t.placements} placements ({t.found} of {t.barrels} per frame), "
              f"boxes not on their barrel {t.extra_w:.1f} ({t.nothing} nothing, {t.second} second, {t.wrong} wrong), on empty frames {t.empty} (clean {t.clean_empty})")
        print(cm.format_conditions(cm.per_condition(recs, truth)))
        print("seed candidates by verdict:", sorted(cm.refusals(recs).items(), key=lambda kv: -kv[1]))
        on, off = [], []
        for s, r in recs.items():
            for x in r["kept"]:
                (on if cm.seed_on_barrel(x.bbox, truth.gts[s]) else off).append((s.replace("4A8B_", ""), x.kind, sc.NAME[x.body], x.bbox, round(x.rel, 2)))
        rels = sorted(v[-1] for v in on)
        print(f"kept seeds on a hand box: {len(on)}; rel min {rels[0] if rels else None}, lowest five {rels[:5]}")
        print("kept seeds NOT on a hand box:", off)
        floods = [(s, r["flood"]) for s, r in recs.items() if any(v > 0.03 for v in r["flood"].values())]
        print("floods over 3 %:", [(s.replace("4A8B_", ""), {k: round(v, 3) for k, v in f.items()}) for s, f in floods])
        lost = [(s, r["first"].n_gt("found"), r["count"].n_gt("found")) for s, r in recs.items() if r["count"].n_gt("found") < r["first"].n_gt("found")]
        print("frames that lost a barrel:", lost)
        more = [(s.replace("4A8B_", ""), r["first"].extra, r["count"].extra) for s, r in recs.items() if r["count"].extra > r["first"].extra]
        print("frames with more boxes not on their barrel:", more)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
