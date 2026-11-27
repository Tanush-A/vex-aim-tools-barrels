"""Compare two outputs of run_detect.py, box for box.

    python diff.py before.json after.json [--log]

Either file may be gzipped (.gz) and may hold the boxes only (as results/2026-11-26_collapse/before_boxes.json.gz
does): then the reason logs are not compared. Prints the inputs whose boxes differ and ends with
IDENTICAL BOXES ON EVERY INPUT or NOT IDENTICAL (exit code 0 or 1). Inputs with the same boxes and a different reason
log are counted (information, not a failure); --log says which reasons changed into which."""
import collections
import gzip
import json
import sys


def load(path):
    d = json.load(gzip.open(path, "rt") if path.endswith(".gz") else open(path))
    return {k: (v if isinstance(v, dict) else {"boxes": v}) for k, v in d.items()}


def notes(log):
    return collections.Counter((e[0], e[1], tuple(e[2] or ())) for e in log)


args = [a for a in sys.argv[1:] if not a.startswith("--")]
a, b = load(args[0]), load(args[1])
assert set(a) == set(b), "different input sets"
boxes_differ, log_differs, total, moved = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
shown = 0
for k in sorted(a):
    group = k.split("/")[0]
    total[group] += 1
    if a[k]["boxes"] != b[k]["boxes"]:
        boxes_differ[group] += 1
        if shown < 25:
            print("BOXES DIFFER", k, "\n   before", a[k]["boxes"], "\n   after ", b[k]["boxes"])
            shown += 1
    elif "log" in a[k] and "log" in b[k] and a[k]["log"] != b[k]["log"]:
        log_differs[group] += 1
        was, now = notes(a[k]["log"]), notes(b[k]["log"])
        gone, new = was - now, now - was
        new_at = {e[2]: e for e in new}
        gone_boxes = {e[2] for e in gone}
        for e, n in gone.items():
            other = new_at.get(e[2])
            moved[(f"{e[0]}:{e[1]}", f"{other[0]}:{other[1]}" if other else "(no note)")] += n
        for e, n in new.items():
            if e[2] not in gone_boxes:
                moved[("(no note)", f"{e[0]}:{e[1]}")] += n
        if not gone and not new:
            moved[("the same notes", "in another order")] += 1
print("inputs per group:", dict(total))
print("inputs whose BOXES differ:", dict(boxes_differ) or 0)
print("same boxes, reason log differs:", dict(log_differs) or 0)
if "--log" in sys.argv:
    for (was, now), n in sorted(moved.items(), key=lambda kv: -kv[1]):
        print(f"   {n:6d} x  {was}  ->  {now}")
print("IDENTICAL BOXES ON EVERY INPUT" if not boxes_differ else f"NOT IDENTICAL: {sum(boxes_differ.values())} inputs differ")
sys.exit(1 if boxes_differ else 0)
