# The damage levels: found / barrels (false boxes)

git a485ecf; v2 rule; the 16 HOME hand masks (29 barrels), train frames only. Arms: `experiments/2026-11-20_occl_combined/comb_arms.py`. PREREG clause (c): at the judged levels the false boxes may not be above `stack`'s, with 5 seeds and with 20.

## Seeds 0 to 4 (as every earlier test: 145 barrels per damaged level)

| level | `stack` | `vertical_alone` | `pin_alone` | `pin+thin_alone` | `combined` | `combined+thin` |
|---|---|---|---|---|---|---|
| perfect masks **(judged)** | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical **(judged)** | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) |
| white tables, bad day (reported; not more than double) | 135 / 145 (3) | 136 / 145 (3) | 135 / 145 (3) | 135 / 145 (3) | 136 / 145 (3) | 135 / 145 (3) |
| bad day without the stripe patch **(judged)** | 144 / 145 (0) | 144 / 145 (0) | 144 / 145 (0) | 144 / 145 (0) | 144 / 145 (0) | 144 / 145 (0) |
| light **(judged)** | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) |
| medium (reported; not more than double) | 99 / 145 (1) | 115 / 145 (1) | 99 / 145 (1) | 99 / 145 (1) | 115 / 145 (1) | 103 / 145 (1) |
| heavy (report only) | 21 / 145 (0) | 21 / 145 (0) | 21 / 145 (0) | 21 / 145 (0) | 21 / 145 (0) | 21 / 145 (0) |
| white tables, worst seen (report only) | 84 / 145 (2) | 105 / 145 (2) | 84 / 145 (2) | 84 / 145 (2) | 105 / 145 (2) | 98 / 145 (2) |

## Seeds 0 to 19 (580 barrels per damaged level)

| level | `stack` | `vertical_alone` | `pin_alone` | `pin+thin_alone` | `combined` | `combined+thin` |
|---|---|---|---|---|---|---|
| perfect masks **(judged)** | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical **(judged)** | 579 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) |
| white tables, bad day (reported; not more than double) | 547 / 580 (5) | 555 / 580 (6) | 547 / 580 (5) | 547 / 580 (5) | 555 / 580 (6) | 547 / 580 (5) |
| bad day without the stripe patch **(judged)** | 577 / 580 (0) | 577 / 580 (0) | 577 / 580 (0) | 577 / 580 (0) | 577 / 580 (0) | 577 / 580 (0) |
| light **(judged)** | 574 / 580 (0) | 574 / 580 (0) | 574 / 580 (0) | 574 / 580 (0) | 574 / 580 (0) | 574 / 580 (0) |
| medium (reported; not more than double) | 388 / 580 (3) | 444 / 580 (7) | 388 / 580 (3) | 389 / 580 (3) | 444 / 580 (7) | 404 / 580 (4) |
| heavy (report only) | 89 / 580 (0) | 89 / 580 (0) | 89 / 580 (0) | 89 / 580 (0) | 89 / 580 (0) | 89 / 580 (0) |
| white tables, worst seen (report only) | 337 / 580 (6) | 419 / 580 (10) | 337 / 580 (6) | 338 / 580 (6) | 419 / 580 (10) | 387 / 580 (6) |

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
| white tables, bad day | `stack` | 5 | 0 | 0 | 0 | 0 | 0 |
| white tables, bad day | `vertical_alone` | 5 | 0 | 0 | 1 | 0 | 0 |
| white tables, bad day | `pin_alone` | 5 | 0 | 0 | 0 | 0 | 0 |
| white tables, bad day | `pin+thin_alone` | 5 | 0 | 0 | 0 | 0 | 0 |
| white tables, bad day | `combined` | 5 | 0 | 0 | 1 | 0 | 0 |
| white tables, bad day | `combined+thin` | 5 | 0 | 0 | 0 | 0 | 0 |
| medium | `stack` | 3 | 0 | 0 | 0 | 0 | 0 |
| medium | `vertical_alone` | 3 | 0 | 0 | 4 | 0 | 0 |
| medium | `pin_alone` | 3 | 0 | 0 | 0 | 0 | 0 |
| medium | `pin+thin_alone` | 3 | 0 | 0 | 0 | 0 | 0 |
| medium | `combined` | 3 | 0 | 0 | 4 | 0 | 0 |
| medium | `combined+thin` | 3 | 0 | 0 | 1 | 0 | 0 |
| white tables, worst seen | `stack` | 5 | 1 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `vertical_alone` | 5 | 1 | 0 | 4 | 0 | 0 |
| white tables, worst seen | `pin_alone` | 5 | 1 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `pin+thin_alone` | 5 | 1 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `combined` | 5 | 1 | 0 | 4 | 0 | 0 |
| white tables, worst seen | `combined+thin` | 5 | 1 | 0 | 0 | 0 | 0 |

## Which test refused the missed barrels (seeds 0 to 4; the detector's reason log)

- perfect masks, `stack`: stripe_refused:height 1
- perfect masks, `vertical_alone`: stripe_refused:height 1
- perfect masks, `pin_alone`: stripe_refused:height 1
- perfect masks, `pin+thin_alone`: stripe_refused:height 1
- perfect masks, `combined`: stripe_refused:height 1
- perfect masks, `combined+thin`: stripe_refused:height 1
- white tables, bad day, `stack`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:width 1
- white tables, bad day, `vertical_alone`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1
- white tables, bad day, `pin_alone`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:width 1
- white tables, bad day, `pin+thin_alone`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:outline_unknown 1
- white tables, bad day, `combined`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1
- white tables, bad day, `combined+thin`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:outline_unknown 1
- bad day without the stripe patch, `stack`: stripe_refused:height 1
- bad day without the stripe patch, `vertical_alone`: stripe_refused:height 1
- bad day without the stripe patch, `pin_alone`: stripe_refused:height 1
- bad day without the stripe patch, `pin+thin_alone`: stripe_refused:height 1
- bad day without the stripe patch, `combined`: stripe_refused:height 1
- bad day without the stripe patch, `combined+thin`: stripe_refused:height 1
- light, `stack`: stripe_refused:height 2
- light, `vertical_alone`: stripe_refused:height 2
- light, `pin_alone`: stripe_refused:height 2
- light, `pin+thin_alone`: stripe_refused:height 2
- light, `combined`: stripe_refused:height 2
- light, `combined+thin`: stripe_refused:height 2
- medium, `stack`: stripe_refused:width 33, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- medium, `vertical_alone`: stripe_refused:width 20, stripe_refused:area 5, stripe_refused:side_unexplained 2, misplaced 2, stripe_refused:height 1
- medium, `pin_alone`: stripe_refused:width 33, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- medium, `pin+thin_alone`: stripe_refused:outline_unknown 17, stripe_refused:slice_not_full 10, stripe_refused:width 6, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- medium, `combined`: stripe_refused:width 20, stripe_refused:area 5, stripe_refused:side_unexplained 2, misplaced 2, stripe_refused:height 1
- medium, `combined+thin`: stripe_refused:outline_unknown 14, stripe_refused:slice_not_full 10, stripe_refused:width 5, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- heavy, `stack`: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- heavy, `vertical_alone`: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- heavy, `pin_alone`: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- heavy, `pin+thin_alone`: stripe_not_sandwiched 32, stripe_refused:area 26, stripe_refused:width 22, stripe_refused:slice_not_full 19, stripe_hidden 14, stripe_refused:height 7, stripe_refused:outline_unknown 3, not_segmented 1
- heavy, `combined`: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- heavy, `combined+thin`: stripe_not_sandwiched 32, stripe_refused:area 26, stripe_refused:width 22, stripe_refused:slice_not_full 19, stripe_hidden 14, stripe_refused:height 7, stripe_refused:outline_unknown 3, not_segmented 1
- white tables, worst seen, `stack`: stripe_refused:width 49, stripe_refused:area 5, stripe_refused:height 3, misplaced 3, stripe_refused:side_unexplained 1
- white tables, worst seen, `vertical_alone`: stripe_refused:width 29, stripe_refused:area 5, misplaced 3, stripe_refused:height 2, stripe_refused:side_unexplained 1
- white tables, worst seen, `pin_alone`: stripe_refused:width 49, stripe_refused:area 5, stripe_refused:height 3, misplaced 3, stripe_refused:side_unexplained 1
- white tables, worst seen, `pin+thin_alone`: stripe_refused:outline_unknown 26, stripe_refused:slice_not_full 17, stripe_refused:width 6, stripe_refused:area 5, stripe_refused:height 3, misplaced 3, stripe_refused:side_unexplained 1
- white tables, worst seen, `combined`: stripe_refused:width 29, stripe_refused:area 5, misplaced 3, stripe_refused:height 2, stripe_refused:side_unexplained 1
- white tables, worst seen, `combined+thin`: stripe_refused:slice_not_full 15, stripe_refused:outline_unknown 15, stripe_refused:width 5, stripe_refused:area 5, stripe_refused:height 3, misplaced 3, stripe_refused:side_unexplained 1

## Every false box at the judged levels (seeds 0 to 19)

| level | arm | frame | seed | color | box | drawn by | width / a barrel's | best overlap with a true box of its color | that barrel also missed |
|---|---|---|---|---|---|---|---|---|---|
