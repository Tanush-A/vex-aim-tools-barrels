# A stripe cut through: one kind of damage at a time, found / barrels (false boxes)

The 16 HOME hand masks (29 barrels), seeds 0 to 19 (580 barrels per level; the perfect masks once). v2 rule. Train frames only.

| damage | `start` | `bridge` | `sliver` |
|---|---|---|---|
| perfect masks | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| stripe patch 0.03 W | 545 / 580 (12) | 554 / 580 (8) | 554 / 580 (8) |
| stripe patch 0.06 W | 544 / 580 (13) | 555 / 580 (8) | 555 / 580 (8) |
| stripe patch 0.1 W | 543 / 580 (13) | 555 / 580 (8) | 555 / 580 (8) |
| stripe patch 0.15 W | 538 / 580 (15) | 555 / 580 (8) | 556 / 580 (7) |
| stripe patch 0.2 W | 543 / 580 (9) | 562 / 580 (1) | 562 / 580 (1) |
| stripe patch 0.3 W | 547 / 580 (5) | 557 / 580 (4) | 557 / 580 (3) |
| one stripe break 0.03 W | 560 / 580 (0) | 560 / 580 (0) | 560 / 580 (0) |
| one stripe break 0.06 W | 553 / 580 (9) | 555 / 580 (8) | 557 / 580 (7) |
| one stripe break 0.1 W | 536 / 580 (18) | 556 / 580 (7) | 558 / 580 (6) |
| one stripe break 0.15 W | 539 / 580 (11) | 559 / 580 (3) | 559 / 580 (3) |
| one stripe break 0.2 W | 545 / 580 (2) | 560 / 580 (0) | 560 / 580 (0) |
| one stripe break 0.3 W | 535 / 580 (3) | 553 / 580 (2) | 553 / 580 (2) |
| two stripe breaks 0.03 W | 560 / 580 (1) | 560 / 580 (0) | 560 / 580 (0) |
| two stripe breaks 0.06 W | 553 / 580 (13) | 559 / 580 (5) | 560 / 580 (4) |
| two stripe breaks 0.1 W | 541 / 580 (10) | 559 / 580 (5) | 561 / 580 (3) |
| two stripe breaks 0.15 W | 535 / 580 (2) | 558 / 580 (2) | 558 / 580 (2) |
| two stripe breaks 0.2 W | 530 / 580 (2) | 557 / 580 (0) | 558 / 580 (0) |
| two stripe breaks 0.3 W | 465 / 580 (4) | 481 / 580 (3) | 525 / 580 (3) |
| white tables, bad day | 547 / 580 (5) | 563 / 580 (0) | 563 / 580 (0) |
| medium | 400 / 580 (3) | 413 / 580 (4) | 455 / 580 (4) |

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

## `bridge`: which test refused the missed barrels

- perfect masks: stripe_refused:height 1
- stripe patch 0.03 W: stripe_refused:height 17, misplaced 7, stripe_refused:outline_unknown 1, stripe_refused:side_unexplained 1
- stripe patch 0.06 W: stripe_refused:height 16, misplaced 7, stripe_refused:outline_unknown 1, stripe_refused:side_unexplained 1
- stripe patch 0.1 W: stripe_refused:height 15, misplaced 7, stripe_refused:outline_unknown 3
- stripe patch 0.15 W: stripe_refused:height 17, misplaced 7, stripe_refused:outline_unknown 1
- stripe patch 0.2 W: stripe_refused:height 17, misplaced 1
- stripe patch 0.3 W: stripe_refused:height 17, stripe_refused:side_unexplained 4, stripe_refused:outline_unknown 2
- one stripe break 0.03 W: stripe_refused:height 20
- one stripe break 0.06 W: stripe_refused:height 17, misplaced 8
- one stripe break 0.1 W: stripe_refused:height 15, misplaced 7, stripe_refused:outline_unknown 2
- one stripe break 0.15 W: stripe_refused:height 14, misplaced 3, stripe_refused:outline_unknown 2, stripe_refused:side_unexplained 2
- one stripe break 0.2 W: stripe_refused:height 15, stripe_refused:side_unexplained 3, stripe_refused:outline_unknown 2
- one stripe break 0.3 W: stripe_refused:height 16, stripe_refused:side_unexplained 5, stripe_refused:outline_unknown 4, misplaced 2
- two stripe breaks 0.03 W: stripe_refused:height 20
- two stripe breaks 0.06 W: stripe_refused:height 17, misplaced 4
- two stripe breaks 0.1 W: stripe_refused:height 13, misplaced 4, stripe_refused:outline_unknown 4
- two stripe breaks 0.15 W: stripe_refused:height 14, stripe_refused:side_unexplained 4, stripe_refused:outline_unknown 3, misplaced 1
- two stripe breaks 0.2 W: stripe_refused:height 15, stripe_refused:side_unexplained 5, stripe_refused:outline_unknown 3
- two stripe breaks 0.3 W: stripe_refused:outline_unknown 44, stripe_refused:height 17, stripe_refused:width 12, stripe_refused:slice_not_full 12, stripe_refused:side_unexplained 11, misplaced 3
- white tables, bad day: stripe_refused:height 15, stripe_refused:slice_not_full 1, stripe_refused:side_unexplained 1
- medium: stripe_refused:outline_unknown 59, stripe_refused:slice_not_full 42, stripe_refused:height 21, stripe_refused:area 19, stripe_refused:width 14, stripe_refused:side_unexplained 9, misplaced 3

## `bridge`: which rule drew the false boxes

- stripe patch 0.03 W: stripe step (misplaced box of a missed barrel) 7, stripe step 1
- stripe patch 0.06 W: stripe step (misplaced box of a missed barrel) 7, stripe step 1
- stripe patch 0.1 W: stripe step (misplaced box of a missed barrel) 7, stripe step 1
- stripe patch 0.15 W: stripe step (misplaced box of a missed barrel) 7, stripe step 1
- stripe patch 0.2 W: stripe step (misplaced box of a missed barrel) 1
- stripe patch 0.3 W: stripe step 4
- one stripe break 0.06 W: stripe step (misplaced box of a missed barrel) 8
- one stripe break 0.1 W: stripe step (misplaced box of a missed barrel) 7
- one stripe break 0.15 W: stripe step (misplaced box of a missed barrel) 3
- one stripe break 0.3 W: stripe step (misplaced box of a missed barrel) 2
- two stripe breaks 0.06 W: stripe step (misplaced box of a missed barrel) 4, stripe step 1
- two stripe breaks 0.1 W: stripe step (misplaced box of a missed barrel) 4, stripe step 1
- two stripe breaks 0.15 W: stripe step (misplaced box of a missed barrel) 1, stripe step 1
- two stripe breaks 0.3 W: stripe step (misplaced box of a missed barrel) 1, caps_behind (misplaced box of a missed barrel) 1, stripe step 1
- medium: stripe step 2, stripe step (misplaced box of a missed barrel) 2

## `sliver`: which test refused the missed barrels

- perfect masks: stripe_refused:height 1
- stripe patch 0.03 W: stripe_refused:height 17, misplaced 7, stripe_refused:outline_unknown 1, stripe_refused:side_unexplained 1
- stripe patch 0.06 W: stripe_refused:height 16, misplaced 7, stripe_refused:outline_unknown 1, stripe_refused:side_unexplained 1
- stripe patch 0.1 W: stripe_refused:height 15, misplaced 7, stripe_refused:outline_unknown 3
- stripe patch 0.15 W: stripe_refused:height 17, misplaced 6, stripe_refused:outline_unknown 1
- stripe patch 0.2 W: stripe_refused:height 17, misplaced 1
- stripe patch 0.3 W: stripe_refused:height 17, stripe_refused:side_unexplained 4, stripe_refused:outline_unknown 2
- one stripe break 0.03 W: stripe_refused:height 20
- one stripe break 0.06 W: stripe_refused:height 17, misplaced 6
- one stripe break 0.1 W: stripe_refused:height 15, misplaced 5, stripe_refused:outline_unknown 2
- one stripe break 0.15 W: stripe_refused:height 14, misplaced 3, stripe_refused:outline_unknown 2, stripe_refused:side_unexplained 2
- one stripe break 0.2 W: stripe_refused:height 15, stripe_refused:side_unexplained 3, stripe_refused:outline_unknown 2
- one stripe break 0.3 W: stripe_refused:height 16, stripe_refused:side_unexplained 5, stripe_refused:outline_unknown 4, misplaced 2
- two stripe breaks 0.03 W: stripe_refused:height 20
- two stripe breaks 0.06 W: stripe_refused:height 17, misplaced 3
- two stripe breaks 0.1 W: stripe_refused:height 13, stripe_refused:outline_unknown 4, misplaced 2
- two stripe breaks 0.15 W: stripe_refused:height 14, stripe_refused:side_unexplained 4, stripe_refused:outline_unknown 3, misplaced 1
- two stripe breaks 0.2 W: stripe_refused:height 15, stripe_refused:side_unexplained 5, stripe_refused:outline_unknown 2
- two stripe breaks 0.3 W: stripe_refused:outline_unknown 13, stripe_refused:height 11, stripe_refused:side_unexplained 11, stripe_refused:width 9, stripe_refused:slice_not_full 8, misplaced 3
- white tables, bad day: stripe_refused:height 15, stripe_refused:slice_not_full 1, stripe_refused:side_unexplained 1
- medium: stripe_refused:slice_not_full 39, stripe_refused:outline_unknown 28, stripe_refused:area 19, stripe_refused:height 16, stripe_refused:width 12, stripe_refused:side_unexplained 8, misplaced 3

## `sliver`: which rule drew the false boxes

- stripe patch 0.03 W: stripe step (misplaced box of a missed barrel) 7, stripe step 1
- stripe patch 0.06 W: stripe step (misplaced box of a missed barrel) 7, stripe step 1
- stripe patch 0.1 W: stripe step (misplaced box of a missed barrel) 7, stripe step 1
- stripe patch 0.15 W: stripe step (misplaced box of a missed barrel) 6, stripe step 1
- stripe patch 0.2 W: stripe step (misplaced box of a missed barrel) 1
- stripe patch 0.3 W: stripe step 3
- one stripe break 0.06 W: stripe step (misplaced box of a missed barrel) 6, stripe step 1
- one stripe break 0.1 W: stripe step (misplaced box of a missed barrel) 5, stripe step 1
- one stripe break 0.15 W: stripe step (misplaced box of a missed barrel) 3
- one stripe break 0.3 W: stripe step (misplaced box of a missed barrel) 2
- two stripe breaks 0.06 W: stripe step (misplaced box of a missed barrel) 3, stripe step 1
- two stripe breaks 0.1 W: stripe step (misplaced box of a missed barrel) 2, stripe step 1
- two stripe breaks 0.15 W: stripe step (misplaced box of a missed barrel) 1, stripe step 1
- two stripe breaks 0.3 W: stripe step (misplaced box of a missed barrel) 1, caps_behind (misplaced box of a missed barrel) 1, stripe step 1
- medium: stripe step 2, stripe step (misplaced box of a missed barrel) 2
