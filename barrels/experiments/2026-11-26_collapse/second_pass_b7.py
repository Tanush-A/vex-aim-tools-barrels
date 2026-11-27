"""Second pass, B7: would drop_single_reading decide the same if it read the span stage 3 measured (seen_span) instead of
measuring again? usage: second_pass_b7.py <barrels/src> <inputs.pkl>"""
import collections
import pickle
import sys

import cv2
import numpy as np

sys.path.insert(0, sys.argv[1])
from barrels import detector as det, geometry as geo  # noqa: E402

cam, cfg = geo.AIM_4A8B6118_BOXFIT, det.DetConfig()
enc = pickle.load(open(sys.argv[2], "rb"))
table = collections.Counter()
differ = []
numeric = collections.Counter()
for k in sorted(enc):
    mask = cv2.imdecode(np.frombuffer(enc[k], np.uint8), cv2.IMREAD_UNCHANGED)
    layers = det.sandwiches(mask, cam, cfg)
    pieces = det.find_pieces(mask, cam, cfg)
    stripes, leftover = det.find_stripes(mask, cam, cfg, None, layers)
    found, unplaced, lost = det.boxes_from_stripes(stripes, mask, cam, cfg)
    found = found + det.closeup_pieces(pieces, found, mask, cam, cfg)
    found = det.drop_seen_through(found, mask, cam, cfg)
    found = found + det.caps_behind(found, lost, mask, cam, cfg)
    found = found + det.post_pairs(leftover + unplaced, found, mask, cam, cfg)
    found = det.half_stripes(found, mask, cam, cfg, None, layers)
    found = det.drop_seen_through(found, mask, cam, cfg)
    group = k.split("/")[0]
    for f in found:
        b = f.barrel
        if not (b.source == "det2" and "occluded" in b.flags and {"top_inferred", "bottom_inferred"} <= b.flags):
            continue
        kept_old = bool(det.drop_single_reading([f], mask, cam, cfg))
        s = f.stripe
        if s is None:
            table[(group, f.rule, kept_old, "no stripe")] += 1
            continue
        at = det._at(s, cam)
        others = tuple((o.bbox[0], o.bbox[2]) for o in stripes if o is not s and not o.thin)
        seen = det.seen_span(s, mask, at.W, b.bbox[1], b.bbox[3], cfg, others)
        kept_new = seen.shows_width
        table[(group, f.rule, kept_old, kept_new)] += 1
        # the two measurements themselves
        x0, y0, x1, y1 = s.bbox
        at_mid = det.BarrelAt.from_stripe_row(cam, (y0 + y1) / 2)
        span_old = det._body_span(mask, b.color, x0, x1, b.bbox[1], b.bbox[3], y0, y1) if b.bbox[3] - b.bbox[1] >= 2 else None
        span_new = det._body_span(mask, b.color, x0, x1, b.bbox[1], b.bbox[3], y0, y1, others) if b.bbox[3] - b.bbox[1] >= 2 else None
        numeric[("same span" if span_old == span_new else "span differs", "same W" if at_mid is not None and at_mid.W == at.W else "W differs")] += 1
        if kept_old != kept_new:
            differ.append((k, f.rule, b.bbox, kept_old, kept_new))
print("asked boxes by (group, rule, kept today, kept if it read seen_span):")
for key in sorted(table):
    print("  ", key, table[key])
print("the two measurements:", dict(numeric))
print("verdicts that differ:", len(differ))
for d in differ[:30]:
    print("  ", d)
