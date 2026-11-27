# The finder, every setting (in-sample; a measurement at known barrel locations, not a verdict)

`python barrels/experiments/2026-11-26_contrast/finder.py --grid`. Ordinary train frames: clean upright barrels and partly hidden ones (flag occluded or truncated) with a candidate of the right color on their stripe among the 5 / 20 strongest candidates of the frame; candidates on no barrel per frame and per empty frame (of at most 20). Extreme = the parked conditions; brightness 1 = excluded.

| setting | clean, top 5 | clean, top 20 | hidden, top 20 | extreme clean, top 20 | brightness 1 clean, top 20 | on no barrel, per ordinary frame | per empty frame | empty frames with any (of 22) |
|---|---|---|---|---|---|---|---|---|
| logrb o=1 margin=0.3 share=0.4 | 211 of 211 | 211 | 63 of 88 | 99 of 108 | 0 of 42 | 4.62 | 7.82 | 19 |
| logrb o=1 margin=0.3 share=0.5 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 3.60 | 6.32 | 19 |
| logrb o=1 margin=0.3 share=0.7 | 209 of 211 | 209 | 41 of 88 | 93 of 108 | 0 of 42 | 2.24 | 4.23 | 19 |
| logrb o=1 margin=0.5 share=0.4 | 211 of 211 | 211 | 61 of 88 | 99 of 108 | 0 of 42 | 2.01 | 4.59 | 18 |
| logrb o=1 margin=0.5 share=0.5 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 1.49 | 3.55 | 18 |
| logrb o=1 margin=0.5 share=0.7 | 209 of 211 | 209 | 39 of 88 | 93 of 108 | 0 of 42 | 0.95 | 2.45 | 18 |
| logrb o=1 margin=0.75 share=0.4 | 211 of 211 | 211 | 61 of 88 | 98 of 108 | 0 of 42 | 1.04 | 2.64 | 18 |
| logrb o=1 margin=0.75 share=0.5 | 211 of 211 | 211 | 59 of 88 | 98 of 108 | 0 of 42 | 0.71 | 1.91 | 16 |
| logrb o=1 margin=0.75 share=0.7 | 209 of 211 | 209 | 28 of 88 | 92 of 108 | 0 of 42 | 0.45 | 1.55 | 14 |
| logrb o=1 margin=1 share=0.4 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 0.56 | 1.50 | 12 |
| logrb o=1 margin=1 share=0.5 | 211 of 211 | 211 | 55 of 88 | 98 of 108 | 0 of 42 | 0.38 | 1.23 | 12 |
| logrb o=1 margin=1 share=0.7 | 209 of 211 | 209 | 23 of 88 | 89 of 108 | 0 of 42 | 0.21 | 0.82 | 11 |
| logrb o=8 margin=0.3 share=0.4 | 211 of 211 | 211 | 62 of 88 | 99 of 108 | 0 of 42 | 3.50 | 6.64 | 19 |
| logrb o=8 margin=0.3 share=0.5 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 2.66 | 4.82 | 19 |
| logrb o=8 margin=0.3 share=0.7 | 209 of 211 | 209 | 39 of 88 | 93 of 108 | 0 of 42 | 1.73 | 3.50 | 18 |
| logrb o=8 margin=0.5 share=0.4 | 211 of 211 | 211 | 61 of 88 | 98 of 108 | 0 of 42 | 1.31 | 3.36 | 18 |
| logrb o=8 margin=0.5 share=0.5 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 1.03 | 2.82 | 18 |
| logrb o=8 margin=0.5 share=0.7 | 209 of 211 | 209 | 36 of 88 | 93 of 108 | 0 of 42 | 0.68 | 2.00 | 18 |
| logrb o=8 margin=0.75 share=0.4 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 0.59 | 1.86 | 15 |
| logrb o=8 margin=0.75 share=0.5 | 211 of 211 | 211 | 58 of 88 | 98 of 108 | 0 of 42 | 0.43 | 1.45 | 13 |
| logrb o=8 margin=0.75 share=0.7 | 209 of 211 | 209 | 26 of 88 | 92 of 108 | 0 of 42 | 0.27 | 1.14 | 13 |
| logrb o=8 margin=1 share=0.4 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 0.26 | 1.00 | 10 |
| logrb o=8 margin=1 share=0.5 | 211 of 211 | 211 | 53 of 88 | 97 of 108 | 0 of 42 | 0.19 | 0.82 | 10 |
| logrb o=8 margin=1 share=0.7 | 209 of 211 | 209 | 22 of 88 | 86 of 108 | 0 of 42 | 0.09 | 0.41 | 5 |
| logrb o=16 margin=0.3 share=0.4 | 211 of 211 | 211 | 62 of 88 | 99 of 108 | 0 of 42 | 2.62 | 5.45 | 19 |
| logrb o=16 margin=0.3 share=0.5 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 2.01 | 4.05 | 19 |
| logrb o=16 margin=0.3 share=0.7 | 209 of 211 | 209 | 39 of 88 | 93 of 108 | 0 of 42 | 1.34 | 3.32 | 18 |
| logrb o=16 margin=0.5 share=0.4 | 211 of 211 | 211 | 61 of 88 | 98 of 108 | 0 of 42 | 0.99 | 3.05 | 18 |
| logrb o=16 margin=0.5 share=0.5 | 211 of 211 | 211 | 59 of 88 | 98 of 108 | 0 of 42 | 0.77 | 2.36 | 18 |
| logrb o=16 margin=0.5 share=0.7 | 209 of 211 | 209 | 35 of 88 | 93 of 108 | 0 of 42 | 0.50 | 1.77 | 18 |
| logrb o=16 margin=0.75 share=0.4 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 0.36 | 1.36 | 12 |
| logrb o=16 margin=0.75 share=0.5 | 211 of 211 | 211 | 57 of 88 | 97 of 108 | 0 of 42 | 0.29 | 1.14 | 12 |
| logrb o=16 margin=0.75 share=0.7 | 209 of 211 | 209 | 24 of 88 | 92 of 108 | 0 of 42 | 0.18 | 0.77 | 11 |
| logrb o=16 margin=1 share=0.4 | 211 of 211 | 211 | 58 of 88 | 94 of 108 | 0 of 42 | 0.15 | 0.64 | 8 |
| logrb o=16 margin=1 share=0.5 | 211 of 211 | 211 | 50 of 88 | 92 of 108 | 0 of 42 | 0.11 | 0.50 | 7 |
| logrb o=16 margin=1 share=0.7 | 209 of 211 | 209 | 21 of 88 | 82 of 108 | 0 of 42 | 0.02 | 0.09 | 1 |
| opp o=8 margin=0.08 share=0.4 | 211 of 211 | 211 | 63 of 88 | 99 of 108 | 0 of 42 | 4.54 | 8.36 | 19 |
| opp o=8 margin=0.08 share=0.5 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 3.56 | 6.64 | 19 |
| opp o=8 margin=0.08 share=0.7 | 209 of 211 | 209 | 41 of 88 | 93 of 108 | 0 of 42 | 2.21 | 4.41 | 19 |
| opp o=8 margin=0.12 share=0.4 | 211 of 211 | 211 | 62 of 88 | 99 of 108 | 0 of 42 | 2.43 | 5.64 | 19 |
| opp o=8 margin=0.12 share=0.5 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 1.87 | 4.23 | 19 |
| opp o=8 margin=0.12 share=0.7 | 209 of 211 | 209 | 39 of 88 | 93 of 108 | 0 of 42 | 1.28 | 3.23 | 18 |
| opp o=8 margin=0.2 share=0.4 | 211 of 211 | 211 | 61 of 88 | 98 of 108 | 0 of 42 | 0.97 | 3.09 | 18 |
| opp o=8 margin=0.2 share=0.5 | 211 of 211 | 211 | 59 of 88 | 98 of 108 | 0 of 42 | 0.70 | 2.32 | 18 |
| opp o=8 margin=0.2 share=0.7 | 209 of 211 | 209 | 35 of 88 | 93 of 108 | 0 of 42 | 0.47 | 1.68 | 15 |
| opp o=8 margin=0.3 share=0.4 | 211 of 211 | 211 | 60 of 88 | 98 of 108 | 0 of 42 | 0.33 | 1.18 | 12 |
| opp o=8 margin=0.3 share=0.5 | 211 of 211 | 211 | 53 of 88 | 97 of 108 | 0 of 42 | 0.29 | 1.05 | 12 |
| opp o=8 margin=0.3 share=0.7 | 209 of 211 | 209 | 25 of 88 | 89 of 108 | 0 of 42 | 0.15 | 0.68 | 9 |
