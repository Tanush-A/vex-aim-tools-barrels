# The plain code against the detector before the paint checks

Every train frame (ordinary judged, extreme report only). Expected: the union of round 2's S (0.40) and Lm (1.5 / 0.6).

| color step | verdict | found, placements | gained / lost | boxes not on their barrel | frames whose boxes changed | same as expected (round 2 S ∪ Lm) |
|---|---|---|---|---|---|---|
| fixed | **NO CLEAR DIFFERENCE** | 133.80 → 133.80 | 0 / 0 | 1.93 → 1.93 (5 → 5) | 0: none | True (expected changes on 0 frames) |
| hand | **NO CLEAR DIFFERENCE** | 156.83 → 156.83 | 0 / 0 | 1.50 → 1.25 (3 → 2) | 1: 4A8B_lampmid6_bathtile_neg_02 | True (expected changes on 1 frames) |
| contrast | **NO CLEAR DIFFERENCE** | 156.97 → 156.97 | 0 / 0 | 2.43 → 2.43 (7 → 7) | 0: none | n/a (the contrast path re-runs the detector on a repainted mask) (expected changes on 0 frames) |
