# The damage levels: found / barrels (false boxes)

git 74d03e9; v2 rule; the 16 HOME hand masks (29 barrels), train frames only. Arms: `experiments/2026-11-20_occl_combined/comb_arms.py`. PREREG clause (c): at the judged levels the false boxes may not be above `stack`'s, with 5 seeds and with 20.

## Seeds 0 to 4 (as every earlier test: 145 barrels per damaged level)

| level | `start` | `close` |
|---|---|---|
| perfect masks **(judged)** | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical **(judged)** | 145 / 145 (0) | 145 / 145 (0) |
| white tables, bad day (reported; not more than double) | 140 / 145 (0) | 140 / 145 (0) |
| bad day without the stripe patch **(judged)** | 144 / 145 (0) | 144 / 145 (0) |
| light **(judged)** | 143 / 145 (0) | 143 / 145 (0) |
| medium (reported; not more than double) | 112 / 145 (2) | 116 / 145 (2) |
| heavy (report only) | 25 / 145 (0) | 25 / 145 (0) |
| white tables, worst seen (report only) | 113 / 145 (1) | 116 / 145 (0) |

## Seeds 0 to 19 (580 barrels per damaged level)

| level | `start` | `close` |
|---|---|---|
| perfect masks **(judged)** | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical **(judged)** | 579 / 580 (0) | 579 / 580 (0) |
| white tables, bad day (reported; not more than double) | 563 / 580 (0) | 563 / 580 (0) |
| bad day without the stripe patch **(judged)** | 577 / 580 (0) | 577 / 580 (0) |
| light **(judged)** | 574 / 580 (0) | 574 / 580 (0) |
| medium (reported; not more than double) | 445 / 580 (4) | 455 / 580 (4) |
| heavy (report only) | 103 / 580 (0) | 103 / 580 (0) |
| white tables, worst seen (report only) | 440 / 580 (4) | 454 / 580 (4) |

## What each level is

- `perfect masks`: no damage
- `white tables, typical`: erode_px 1, speckle 6
- `white tables, bad day`: top_highlight (0.16, 0.09), stripe_highlight 0.06, erode_px 1, dropout 0.005, speckle 20
- `bad day without the stripe patch`: top_highlight (0.16, 0.09), erode_px 1, dropout 0.005, speckle 20
- `light`: top_highlight (0.3, 0.2), erode_px 1, dropout 0.02, speckle 5
- `medium`: top_highlight (0.5, 0.3), stripe_highlight 0.15, stripe_breaks (1, 0.06), erode_px 1, dropout 0.05, speckle 15
- `heavy`: top_highlight (0.7, 0.4), stripe_highlight 0.3, stripe_breaks (2, 0.08), erode_px 2, dropout 0.1, speckle 30
- `white tables, worst seen`: top_highlight (0.41, 0.3), stripe_highlight 0.4, stripe_breaks (1, 0.03), erode_px 1, dropout 0.014, speckle 37

## The false boxes, by the rule that drew them (seeds 0 to 19)

| level | arm | stripe step | caps_behind | post_pairs | slices_behind | half_stripes | stripeless piece |
|---|---|---|---|---|---|---|---|
| medium | `start` | 4 | 0 | 0 | 0 | 0 | 0 |
| medium | `close` | 4 | 0 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `start` | 3 | 1 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `close` | 4 | 0 | 0 | 0 | 0 | 0 |

## Which test refused the missed barrels (seeds 0 to 4; the detector's reason log)

- perfect masks, `start`: stripe_refused:height 1
- perfect masks, `close`: stripe_refused:height 1
- white tables, bad day, `start`: stripe_refused:height 5
- white tables, bad day, `close`: stripe_refused:height 5
- bad day without the stripe patch, `start`: stripe_refused:height 1
- bad day without the stripe patch, `close`: stripe_refused:height 1
- light, `start`: stripe_refused:height 2
- light, `close`: stripe_refused:height 2
- medium, `start`: stripe_refused:slice_not_full 10, stripe_refused:outline_unknown 6, stripe_refused:width 5, stripe_refused:area 4, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- medium, `close`: stripe_refused:slice_not_full 9, stripe_refused:outline_unknown 6, stripe_refused:width 5, stripe_refused:area 4, stripe_refused:side_unexplained 2, misplaced 2, stripe_refused:height 1
- heavy, `start`: stripe_not_sandwiched 32, stripe_refused:area 26, stripe_refused:width 22, stripe_refused:slice_not_full 18, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- heavy, `close`: stripe_not_sandwiched 32, stripe_refused:area 26, stripe_refused:width 22, stripe_refused:slice_not_full 18, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- white tables, worst seen, `start`: stripe_refused:slice_not_full 17, stripe_refused:width 5, stripe_refused:height 3, stripe_refused:outline_unknown 3, stripe_refused:area 3, misplaced 1
- white tables, worst seen, `close`: stripe_refused:slice_not_full 17, stripe_refused:width 5, stripe_refused:outline_unknown 3, stripe_refused:area 3, stripe_refused:height 1

## Every false box at the judged levels (seeds 0 to 19)

| level | arm | frame | seed | color | box | drawn by | width / a barrel's | best overlap with a true box of its color | that barrel also missed |
|---|---|---|---|---|---|---|---|---|---|
