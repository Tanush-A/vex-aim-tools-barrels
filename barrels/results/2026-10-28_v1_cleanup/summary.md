# v1_cleanup: cleanup flags on v1 final `afd85483` (LOSO CV, no test)

primary = mean pooled IoU (orange, blue) over in-scope positive pool frames; neg FP = fraction of pixels flagged on no-barrel frames (> 0.005 disqualifies); Δ vs base.

## base

| value | primary | Δ | orange IoU | blue IoU | blue P / R | neg FP o / b | fold std o / b | oos IoU o / b | guard | DQ |
|---|---|---|---|---|---|---|---|---|---|---|
| v1 final (no cleanup) | 0.809 | +0.000 | 0.825 | 0.793 | 0.988 / 0.800 | 0.000 / 0.000 | 0.122 / 0.044 | 0.918 / 0.335 | 0 |  |

## min_blob_px

| value | primary | Δ | orange IoU | blue IoU | blue P / R | neg FP o / b | fold std o / b | oos IoU o / b | guard | DQ |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 0.809 | +0.000 | 0.826 | 0.793 | 0.988 / 0.800 | 0.000 / 0.000 | 0.121 / 0.044 | 0.918 / 0.334 | 0 |  |
| 25 | 0.809 | +0.001 | 0.827 | 0.792 | 0.988 / 0.799 | 0.000 / 0.000 | 0.118 / 0.044 | 0.918 / 0.334 | 0 |  |
| 50 | 0.810 | +0.001 | 0.829 | 0.791 | 0.988 / 0.798 | 0.000 / 0.000 | 0.117 / 0.043 | 0.918 / 0.334 | 0 |  |
| 100 | 0.812 | +0.003 | 0.833 | 0.791 | 0.988 / 0.798 | 0.000 / 0.000 | 0.114 / 0.043 | 0.918 / 0.334 | 0 |  |

## open_px

| value | primary | Δ | orange IoU | blue IoU | blue P / R | neg FP o / b | fold std o / b | oos IoU o / b | guard | DQ |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0.803 | -0.006 | 0.822 | 0.784 | 0.990 / 0.790 | 0.000 / 0.000 | 0.117 / 0.044 | 0.918 / 0.334 | 0 |  |
| 5 | 0.785 | -0.024 | 0.801 | 0.770 | 0.991 / 0.775 | 0.000 / 0.000 | 0.115 / 0.047 | 0.917 / 0.329 | 0 |  |

## fill_holes

| value | primary | Δ | orange IoU | blue IoU | blue P / R | neg FP o / b | fold std o / b | oos IoU o / b | guard | DQ |
|---|---|---|---|---|---|---|---|---|---|---|
| True | 0.818 | +0.009 | 0.834 | 0.802 | 0.988 / 0.810 | 0.000 / 0.000 | 0.121 / 0.049 | 0.918 / 0.335 | 0 |  |

## pair

| value | primary | Δ | orange IoU | blue IoU | blue P / R | neg FP o / b | fold std o / b | oos IoU o / b | guard | DQ |
|---|---|---|---|---|---|---|---|---|---|---|
| min_blob_px=25,fill_holes | 0.819 | +0.010 | 0.836 | 0.802 | 0.988 / 0.810 | 0.000 / 0.000 | 0.117 / 0.049 | 0.918 / 0.334 | 0 |  |
| open_px=3,min_blob_px=25 | 0.803 | -0.006 | 0.822 | 0.783 | 0.990 / 0.790 | 0.000 / 0.000 | 0.116 / 0.044 | 0.917 / 0.334 | 0 |  |

## Selection (pre-registered rule)

- best primary 0.819 at pair=min_blob_px=25,fill_holes
- tied within 0.02: base=v1 final (no cleanup) (0.809), min_blob_px=10 (0.809), min_blob_px=25 (0.809), min_blob_px=50 (0.810), min_blob_px=100 (0.812), open_px=3 (0.803), fill_holes=True (0.818), pair=min_blob_px=25,fill_holes (0.819), pair=open_px=3,min_blob_px=25 (0.803)
- simplest among ties (4 active stages): base=v1 final (no cleanup)
- chosen: `afd85483` (base=v1 final (no cleanup)), primary 0.809
