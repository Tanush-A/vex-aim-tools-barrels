# If thin stripe pieces were let in, where would the new boxes be? (a census; no acceptance number)

A thin piece = a stripe piece the lower floor lets in (0.45 of a stripe height wide) and today's floor refuses (narrower than a stripe is tall, or taller than wide). `full slice` = the body above and below it ends where its row predicts the top and the bottom. `outline knows` = the predicted outline fits the seen part at positions spanning no more than 0.3 W, with a cost of no more than 0.05 H (positions within 0.01 H of the best count as fitting). Train frames (HOME 16, CAMPUS 21, BLACK 10, WOOD 90) and the 337 frames of the recordings.

| frames | thin pieces | full slice | full slice and outline knows | of those: inside a drawn box | on a labeled barrel with no box | on nothing labeled / outside every drawn box |
|---|---|---|---|---|---|---|
| HOME (as in the eval table) | 7 | 1 | 0 | 0 | 0 | 0 |
| CAMPUS | 1 | 0 | 0 | 0 | 0 | 0 |
| BLACK (extreme) | 6 | 2 | 0 | 0 | 0 | 0 |
| WOOD (extreme) | 8 | 0 | 0 | 0 | 0 | 0 |
| recordings: black clip | 59 | 24 | 1 | 0 | 0 | 1 |
| recordings: campus clips | 24 | 1 | 1 | 0 | 0 | 1 |
| recordings: wood clip | 19 | 0 | 0 | 0 | 0 | 0 |

The same with the full slice alone (what the 2026-11-19 round asked for), for comparison:

| frames | full slice | of those: inside a drawn box | on a labeled barrel with no box | on nothing labeled / outside every drawn box |
|---|---|---|---|---|
| HOME (as in the eval table) | 1 | 1 | 0 | 0 |
| CAMPUS | 0 | 0 | 0 | 0 |
| BLACK (extreme) | 2 | 0 | 2 | 0 |
| WOOD (extreme) | 0 | 0 | 0 | 0 |
| recordings: black clip | 24 | 0 | 0 | 24 |
| recordings: campus clips | 1 | 0 | 0 | 1 |
| recordings: wood clip | 0 | 0 | 0 | 0 |

Every thin piece that is a full slice, where the outline knows, and that is not inside a drawn box:

| frames | frame | color | the piece | seen / W | the box the outline gives | overlap with the label | |
|---|---|---|---|---|---|---|---|
| recordings: campus clips | r3_enter_leave/frame_013 | orange | [624, 168, 640, 188] | 0.3 | [615, 133, 686, 209] |  | outside every drawn box |
| recordings: black clip | rec_2026-11-16_131933/frame_032 | blue | [120, 182, 129, 197] | 0.71 | [104, 137, 181, 220] |  | outside every drawn box |
