# A stripe cut through: one kind of damage at a time, found / barrels (false boxes)

The 16 HOME hand masks (29 barrels), seeds 0 to 19 (580 barrels per level; the perfect masks once). v2 rule. Train frames only.

| damage | `start` | `start+cover` |
|---|---|---|
| perfect masks | 28 / 29 (0) | 28 / 29 (0) |
| stripe patch 0.03 W | 545 / 580 (12) | 551 / 580 (9) |
| stripe patch 0.06 W | 544 / 580 (13) | 550 / 580 (12) |
| stripe patch 0.1 W | 543 / 580 (13) | 546 / 580 (12) |
| stripe patch 0.15 W | 538 / 580 (15) | 547 / 580 (11) |
| stripe patch 0.2 W | 543 / 580 (9) | 544 / 580 (16) |
| stripe patch 0.3 W | 547 / 580 (5) | 555 / 580 (5) |
| one stripe break 0.03 W | 560 / 580 (0) | 560 / 580 (0) |
| one stripe break 0.06 W | 553 / 580 (9) | 556 / 580 (8) |
| one stripe break 0.1 W | 536 / 580 (18) | 544 / 580 (16) |
| one stripe break 0.15 W | 539 / 580 (11) | 547 / 580 (11) |
| one stripe break 0.2 W | 545 / 580 (2) | 547 / 580 (3) |
| one stripe break 0.3 W | 535 / 580 (3) | 538 / 580 (3) |
| two stripe breaks 0.03 W | 560 / 580 (1) | 560 / 580 (0) |
| two stripe breaks 0.06 W | 553 / 580 (13) | 540 / 580 (23) |
| two stripe breaks 0.1 W | 541 / 580 (10) | 531 / 580 (25) |
| two stripe breaks 0.15 W | 535 / 580 (2) | 536 / 580 (10) |
| two stripe breaks 0.2 W | 530 / 580 (2) | 530 / 580 (2) |
| two stripe breaks 0.3 W | 465 / 580 (4) | 467 / 580 (4) |
| white tables, bad day | 547 / 580 (5) | 554 / 580 (2) |
| medium | 400 / 580 (3) | 400 / 580 (5) |

## `start`: which test refused the missed barrels

- perfect masks: stripe_refused:height 1
- stripe patch 0.03 W: stripe_refused:height 20, misplaced 7, stripe_refused:side_unexplained 4, stripe_refused:outline_unknown 4
- stripe patch 0.06 W: stripe_refused:height 20, misplaced 8, stripe_refused:side_unexplained 4, stripe_refused:outline_unknown 4
- stripe patch 0.1 W: stripe_refused:height 18, misplaced 9, stripe_refused:outline_unknown 6, stripe_refused:side_unexplained 4
- stripe patch 0.15 W: stripe_refused:height 20, misplaced 12, stripe_refused:side_unexplained 6, stripe_refused:outline_unknown 4
- stripe patch 0.2 W: stripe_refused:height 22, stripe_refused:side_unexplained 6, misplaced 6, stripe_refused:outline_unknown 3
- stripe patch 0.3 W: stripe_refused:height 17, stripe_refused:side_unexplained 8, stripe_refused:outline_unknown 7, misplaced 1
- one stripe break 0.03 W: stripe_refused:height 20
- one stripe break 0.06 W: stripe_refused:height 19, misplaced 8
- one stripe break 0.1 W: stripe_refused:height 18, misplaced 13, stripe_refused:outline_unknown 9, stripe_refused:side_unexplained 4
- one stripe break 0.15 W: stripe_refused:height 17, stripe_refused:outline_unknown 10, stripe_refused:side_unexplained 8, misplaced 6
- one stripe break 0.2 W: stripe_refused:height 15, stripe_refused:outline_unknown 8, stripe_refused:side_unexplained 8, stripe_refused:slice_not_full 3, misplaced 1
- one stripe break 0.3 W: stripe_refused:height 16, stripe_refused:outline_unknown 16, stripe_refused:side_unexplained 8, misplaced 3, stripe_refused:slice_not_full 2
- two stripe breaks 0.03 W: stripe_refused:height 20
- two stripe breaks 0.06 W: stripe_refused:height 18, misplaced 7, stripe_refused:side_unexplained 1, stripe_refused:outline_unknown 1
- two stripe breaks 0.1 W: stripe_refused:outline_unknown 16, stripe_refused:height 12, stripe_refused:side_unexplained 6, misplaced 5
- two stripe breaks 0.15 W: stripe_refused:outline_unknown 20, stripe_refused:height 13, stripe_refused:side_unexplained 7, stripe_refused:slice_not_full 4, misplaced 1
- two stripe breaks 0.2 W: stripe_refused:outline_unknown 20, stripe_refused:height 16, stripe_refused:slice_not_full 6, stripe_refused:side_unexplained 5, misplaced 3
- two stripe breaks 0.3 W: stripe_refused:outline_unknown 58, stripe_refused:height 18, stripe_refused:width 14, stripe_refused:slice_not_full 13, stripe_refused:side_unexplained 7, misplaced 5
- white tables, bad day: stripe_refused:height 15, stripe_refused:outline_unknown 7, misplaced 5, stripe_refused:side_unexplained 4, stripe_refused:slice_not_full 2
- medium: stripe_refused:outline_unknown 65, stripe_refused:slice_not_full 49, stripe_refused:height 21, stripe_refused:area 20, stripe_refused:width 17, stripe_refused:side_unexplained 4, misplaced 4

## `start`: which rule drew the false boxes

- stripe patch 0.03 W: stripe step (misplaced box of a missed barrel) 7, stripe step 4, caps_behind 1
- stripe patch 0.06 W: stripe step (misplaced box of a missed barrel) 8, stripe step 4, caps_behind 1
- stripe patch 0.1 W: stripe step (misplaced box of a missed barrel) 10, stripe step 2, caps_behind 1
- stripe patch 0.15 W: stripe step (misplaced box of a missed barrel) 13, stripe step 2
- stripe patch 0.2 W: stripe step (misplaced box of a missed barrel) 7, stripe step 2
- stripe patch 0.3 W: stripe step 4, stripe step (misplaced box of a missed barrel) 1
- one stripe break 0.06 W: stripe step (misplaced box of a missed barrel) 8, stripe step 1
- one stripe break 0.1 W: stripe step (misplaced box of a missed barrel) 15, stripe step 2, caps_behind 1
- one stripe break 0.15 W: stripe step (misplaced box of a missed barrel) 8, stripe step 3
- one stripe break 0.2 W: stripe step (misplaced box of a missed barrel) 2
- one stripe break 0.3 W: stripe step (misplaced box of a missed barrel) 3
- two stripe breaks 0.03 W: stripe step 1
- two stripe breaks 0.06 W: stripe step (misplaced box of a missed barrel) 8, stripe step 4, caps_behind 1
- two stripe breaks 0.1 W: stripe step (misplaced box of a missed barrel) 5, stripe step 5
- two stripe breaks 0.15 W: stripe step 1, stripe step (misplaced box of a missed barrel) 1
- two stripe breaks 0.2 W: stripe step (misplaced box of a missed barrel) 2
- two stripe breaks 0.3 W: stripe step (misplaced box of a missed barrel) 2, caps_behind (misplaced box of a missed barrel) 1, stripe step 1
- white tables, bad day: stripe step (misplaced box of a missed barrel) 5
- medium: stripe step (misplaced box of a missed barrel) 2, stripe step 1

## `start+cover`: which test refused the missed barrels

- perfect masks: stripe_refused:height 1
- stripe patch 0.03 W: stripe_refused:height 19, misplaced 6, stripe_refused:outline_unknown 4
- stripe patch 0.06 W: stripe_refused:height 18, misplaced 8, stripe_refused:outline_unknown 4
- stripe patch 0.1 W: stripe_refused:height 18, misplaced 10, stripe_refused:outline_unknown 6
- stripe patch 0.15 W: stripe_refused:height 20, misplaced 10, stripe_refused:outline_unknown 3
- stripe patch 0.2 W: stripe_refused:height 23, misplaced 10, stripe_refused:outline_unknown 3
- stripe patch 0.3 W: stripe_refused:height 16, stripe_refused:outline_unknown 7, misplaced 2
- one stripe break 0.03 W: stripe_refused:height 20
- one stripe break 0.06 W: stripe_refused:height 20, misplaced 4
- one stripe break 0.1 W: stripe_refused:height 19, stripe_refused:outline_unknown 9, misplaced 8
- one stripe break 0.15 W: stripe_refused:height 18, stripe_refused:outline_unknown 10, misplaced 5
- one stripe break 0.2 W: stripe_refused:height 21, stripe_refused:outline_unknown 8, stripe_refused:slice_not_full 3, misplaced 1
- one stripe break 0.3 W: stripe_refused:height 19, stripe_refused:outline_unknown 16, stripe_refused:slice_not_full 4, misplaced 3
- two stripe breaks 0.03 W: stripe_refused:height 20
- two stripe breaks 0.06 W: misplaced 21, stripe_refused:height 17, stripe_refused:outline_unknown 2
- two stripe breaks 0.1 W: misplaced 19, stripe_refused:outline_unknown 16, stripe_refused:height 14
- two stripe breaks 0.15 W: stripe_refused:outline_unknown 20, stripe_refused:height 13, misplaced 8, stripe_refused:slice_not_full 3
- two stripe breaks 0.2 W: stripe_refused:outline_unknown 23, stripe_refused:height 16, stripe_refused:slice_not_full 8, misplaced 3
- two stripe breaks 0.3 W: stripe_refused:outline_unknown 59, stripe_refused:height 19, stripe_refused:slice_not_full 16, stripe_refused:width 14, misplaced 5
- white tables, bad day: stripe_refused:height 15, stripe_refused:outline_unknown 7, stripe_refused:slice_not_full 2, misplaced 2
- medium: stripe_refused:outline_unknown 65, stripe_refused:slice_not_full 49, stripe_refused:height 21, stripe_refused:area 20, stripe_refused:width 17, misplaced 7, stripe_refused:side_unexplained 1

## `start+cover`: which rule drew the false boxes

- stripe patch 0.03 W: stripe step (misplaced box of a missed barrel) 6, stripe step 3
- stripe patch 0.06 W: stripe step (misplaced box of a missed barrel) 8, stripe step 4
- stripe patch 0.1 W: stripe step (misplaced box of a missed barrel) 11, stripe step 1
- stripe patch 0.15 W: stripe step (misplaced box of a missed barrel) 11
- stripe patch 0.2 W: stripe step (misplaced box of a missed barrel) 11, stripe step 5
- stripe patch 0.3 W: stripe step 3, stripe step (misplaced box of a missed barrel) 2
- one stripe break 0.06 W: stripe step (misplaced box of a missed barrel) 4, stripe step 4
- one stripe break 0.1 W: stripe step (misplaced box of a missed barrel) 9, stripe step 7
- one stripe break 0.15 W: stripe step (misplaced box of a missed barrel) 7, stripe step 4
- one stripe break 0.2 W: stripe step (misplaced box of a missed barrel) 2, caps_behind 1
- one stripe break 0.3 W: stripe step (misplaced box of a missed barrel) 3
- two stripe breaks 0.06 W: stripe step (misplaced box of a missed barrel) 21, stripe step 2
- two stripe breaks 0.1 W: stripe step (misplaced box of a missed barrel) 19, stripe step 6
- two stripe breaks 0.15 W: stripe step (misplaced box of a missed barrel) 8, caps_behind 1, stripe step 1
- two stripe breaks 0.2 W: stripe step (misplaced box of a missed barrel) 2
- two stripe breaks 0.3 W: stripe step (misplaced box of a missed barrel) 2, caps_behind (misplaced box of a missed barrel) 1, stripe step 1
- white tables, bad day: stripe step (misplaced box of a missed barrel) 2
- medium: stripe step (misplaced box of a missed barrel) 5
