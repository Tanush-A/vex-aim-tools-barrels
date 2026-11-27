"""The boxes of a run_detect.py output, without the reason logs, gzipped (small enough to commit).

    python pack_boxes.py <before.json> <before_boxes.json.gz>

diff.py reads the packed file in place of the full one."""
import gzip
import json
import sys

d = json.load(open(sys.argv[1]))
boxes = {k: v["boxes"] for k, v in d.items()}
with gzip.GzipFile(sys.argv[2], "wb", mtime=0) as f:
    f.write(json.dumps(boxes, sort_keys=True, separators=(",", ":")).encode())
print("inputs", len(boxes), "boxes", sum(len(v) for v in boxes.values()), "->", sys.argv[2])
