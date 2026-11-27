"""Which rule draws how many of the final boxes, per group of golden inputs (for docs/DETECTOR-MAP.md).

    python rule_counts.py <path to barrels/src> <inputs.pkl> [out.md]

Runs the collapsed detector with its reason log on every golden mask and gives each final box the rule that drew it:
a box of source "det1" is a stripeless piece, "det3" a cap; a "det2" box is matched to the newest "kept" note with the
same box (the stripe step's note names its rule; a pair and a half stripe have their own stage). It also counts every
refusal reason in the logs. Boxes are counted, not barrels found: no labels are read. Train frames only (the inputs)."""
import collections
import pickle
import sys

import cv2
import numpy as np

src, inputs = sys.argv[1], sys.argv[2]
sys.path.insert(0, src)
from barrels import detector as det  # noqa: E402

assert det.__file__.startswith(src), (det.__file__, src)
enc = pickle.load(open(inputs, "rb"))
rules = collections.defaultdict(collections.Counter)
whys = collections.defaultdict(collections.Counter)
n_masks = collections.Counter()
for k in sorted(enc):
    group = k.split("/")[0]
    m = cv2.imdecode(np.frombuffer(enc[k], np.uint8), cv2.IMREAD_UNCHANGED)
    log = []
    boxes = det.detect(m, log=log)
    n_masks[group] += 1
    for e in log:
        whys[group][f"{e['stage']}:{e['why']}"] += 1
    for b in boxes:
        if b.source == "det1":
            rule = "piece (close-up)"
        elif b.source == "det3":
            rule = "cap"
        else:
            note = next((e for e in reversed(log) if e["why"] == "kept" and tuple(e.get("box", ())) == tuple(b.bbox)), None)
            rule = "?" if note is None else {"barrel": note.get("rule", "stripe"), "pair": "pair", "half": "half_stripe"}[note["stage"]]
        rules[group][rule] += 1

ORDER = ["whole_stripe", "body_span", "hidden_side", "outline", "centred", "thin_span", "thin_frame", "thin_outline", "piece (close-up)", "cap", "pair",
         "half_stripe", "?"]
groups = sorted(n_masks)
lines = ["## Final boxes by the rule that drew them", "", "| rule | " + " | ".join(groups) + " |", "|---|" + "---:|" * len(groups),
         "| masks | " + " | ".join(str(n_masks[g]) for g in groups) + " |"]
for r in ORDER:
    if any(rules[g][r] for g in groups):
        lines.append(f"| {r} | " + " | ".join(str(rules[g][r]) for g in groups) + " |")
lines.append("| all boxes | " + " | ".join(str(sum(rules[g].values())) for g in groups) + " |")
lines += ["", "## Notes in the reason log (every refusal and every \"kept\")", "", "| stage:why | " + " | ".join(groups) + " |", "|---|" + "---:|" * len(groups)]
for w in sorted({w for g in groups for w in whys[g]}):
    lines.append(f"| {w} | " + " | ".join(str(whys[g][w]) for g in groups) + " |")
text = "\n".join(lines) + "\n"
print(text)
if len(sys.argv) > 3:
    open(sys.argv[3], "w").write(text)
