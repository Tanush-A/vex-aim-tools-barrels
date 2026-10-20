# v1_test: config ee36a1e9 fit on 16 pool frames, evaluated once on 5 test frames

Per-pixel micro-average per condition; IGNORE pixels excluded. `neg fp` = fraction of pixels flagged on frames with no barrels (target ≈ 0).

| condition | n pos | n neg | orange P | orange R | orange IoU | blue P | blue R | blue IoU | orange neg fp | blue neg fp |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 4 | 1 | 0.960 | 0.875 | 0.844 | 0.982 | 0.823 | 0.811 | 0.000 | 0.000 |
| window_light_core | 1 | 0 | 0.993 | 0.880 | 0.874 | 0.990 | 0.855 | 0.848 | — | — |
| window_light_edge | 1 | 0 | 0.971 | 0.810 | 0.791 | 0.983 | 0.929 | 0.915 | — | — |
| window_light_far | 1 | 0 | 0.910 | 0.835 | 0.771 | 0.948 | 0.763 | 0.732 | — | — |
| window_light_neg | 0 | 1 | — | — | — | — | — | — | 0.000 | 0.000 |
| window_light_touch | 1 | 0 | 0.972 | 0.898 | 0.875 | 0.993 | 0.780 | 0.776 | — | — |

Per-image numbers: `per_image.csv`.
