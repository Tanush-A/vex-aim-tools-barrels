"""After the judged runs: which barrels the main candidate gains, by what, and which it still misses, and why.

    python barrels/experiments/2026-11-26_selfcal/misses.py [FAMILY]          # default AB; needs results/.../summary.json

Each place is run with the setting its own fold picked (read from summary.json, so nothing is chosen here). For every
true barrel of the ordinary and extreme train frames: its state under the fixed detector and under the candidate, what
the fixed colors paint of it (the share of the body bands and of the stripe band of its hand box), and what happened
to the seed candidates that sit on it. Writes ``misses.md`` and ``misses.json`` next to the summary.
"""
from __future__ import annotations

import collections
import dataclasses
import json
import sys

import candidates as cand
import common as cm
from barrels import conditions as cnd
from barrels import counting as ct
from barrels import judge as jg
from barrels import selfcal as sc

HIDDEN = {"occluded", "truncated", "held"}


def paint_state(mask, g) -> tuple[float, float, str]:
    b = sc.bands(g.bbox, mask.shape)
    if b is None:
        return 0.0, 0.0, "bands off the frame"
    body = float(sum((mask[r[1]:r[3], r[0]:r[2]] == g.color).sum() for r in (b["upper"], b["lower"])) /
                 max(1, sum((r[3] - r[1]) * (r[2] - r[0]) for r in (b["upper"], b["lower"]))))
    r = b["stripe"]
    stripe = float((mask[r[1]:r[3], r[0]:r[2]] == sc.OTHER_OF[g.color]).mean())
    state = ("both painted" if body >= 0.5 and stripe >= 0.5 else "body painted, stripe not" if body >= 0.5 else
             "stripe painted, body not" if stripe >= 0.5 else "neither painted")
    return body, stripe, state


def main(argv) -> int:
    family = argv[0] if argv else "AB"
    summary = json.loads((cm.RESULTS / "summary.json").read_text())
    chosen = {k.split("|")[1]: v["setting"] for k, v in summary["chosen"].items() if k.split("|")[0] == family}
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME]
    truth = jg.load_truth(stems)
    rows = []
    for place, ss in ct.group_stems(stems, "place").items():
        kw = chosen.get(place)
        cfg = dataclasses.replace(cand.BASE[family], **kw) if kw else dataclasses.replace(cand.BASE[family], seed_found=False, seed_body=False, seed_stripe=False)
        for s, r in cm.run_setting(cfg, ss, truth, keep_results=True).items():
            res = r["result"]
            for i, g in enumerate(truth.gts[s]):
                on = [x for x in res.seeds if x.why != "duplicate" and ct.on_share(x.bbox, g.bbox) >= 0.5]
                kept = [x for x in on if x.ok]
                body, stripe, state = paint_state(res.mask1, g)
                before, after = r["first"].gt[i], r["count"].gt[i]
                if kept:
                    seed = "kept: " + "+".join(sorted({x.kind for x in kept}))
                elif on:
                    seed = "refused: " + "+".join(sorted({f"{x.kind}:{x.why}" for x in on}))
                else:
                    seed = "no seed candidate"
                rows.append({"stem": s, "barrel": i + 1, "color": sc.NAME[g.color], "bbox": list(g.bbox), "flags": sorted(g.flags),
                             "condition": ct.condition_of(s), "class": cnd.info(ct.condition_of(s)).klass, "before": before, "after": after,
                             "body_painted": round(body, 2), "stripe_painted": round(stripe, 2), "paint": state, "seed": seed,
                             "hidden": bool(set(g.flags) & HIDDEN), "frame_moved": list(r["moved"]), "frame_has_seed": bool(r["kept"])})
    (cm.RESULTS / "misses.json").write_text(json.dumps(rows, indent=1) + "\n")

    def table(sel, keys, title):
        c = collections.Counter(tuple(r[k] if not isinstance(r[k], list) else ",".join(r[k]) for k in keys) for r in sel)
        out = [f"### {title} ({len(sel)})", "", "| " + " | ".join(keys) + " | n |", "|" + "---|" * (len(keys) + 1)]
        out += ["| " + " | ".join(str(v) for v in k) + f" | {n} |" for k, n in sorted(c.items(), key=lambda kv: -kv[1])]
        return out + [""]
    md = [f"# What {family} gains and what it still misses (each place with its own held-out setting)", "",
          "Counted per frame (a placement once per light). 'paint' = what the FIXED colors paint of the barrel's hand box: the body bands and the "
          "stripe band, painted when at least half. 'seed' = what happened to the seed candidates on the barrel.", ""]
    for klass in (cnd.ORDINARY, cnd.EXTREME):
        sel = [r for r in rows if r["class"] == klass]
        gained = [r for r in sel if r["after"] == ct.FOUND and r["before"] != ct.FOUND]
        missed = [r for r in sel if r["after"] != ct.FOUND]
        md += [f"## {klass} conditions: {len(sel)} barrels, {sum(r['before'] == ct.FOUND for r in sel)} found by the fixed detector, "
               f"{sum(r['after'] == ct.FOUND for r in sel)} by {family}", ""]
        md += table(gained, ["paint", "seed"], "gained, by what the fixed colors painted and by its seed")
        md += table([r for r in gained if not r["seed"].startswith("kept")], ["condition", "seed", "frame_moved"], "gained without a kept seed of its own (by the frame's ranges)")
        md += table(missed, ["hidden", "paint", "seed"], "still not found, by cause")
        md += table(missed, ["condition", "after"], "still not found, by condition")
        md += table([r for r in missed if not r["hidden"]], ["condition", "color", "paint", "seed"], "still not found and not hidden, in detail")
    (cm.RESULTS / "misses.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
