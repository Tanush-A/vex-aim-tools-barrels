# v1_ablation (ablation) around config 5f1a692b

primary = mean pooled IoU (orange, blue) over in-scope positive pool frames; neg FP = fraction of pixels flagged on no-barrel frames (> 0.005 disqualifies); Δ vs base.

## base

| value | primary | Δ | orange IoU | blue IoU | blue P / R | neg FP o / b | fold std o / b | oos IoU o / b | guard | DQ |
|---|---|---|---|---|---|---|---|---|---|---|
| base | 0.775 | +0.000 | 0.766 | 0.785 | 0.989 / 0.792 | 0.000 / 0.000 | 0.175 / 0.049 | 0.000 / 0.000 | 0 |  |

## ablation

| value | primary | Δ | orange IoU | blue IoU | blue P / R | neg FP o / b | fold std o / b | oos IoU o / b | guard | DQ |
|---|---|---|---|---|---|---|---|---|---|---|
| no_horizon_gate | 0.773 | -0.002 | 0.762 | 0.784 | 0.988 / 0.792 | 0.000 / 0.000 | 0.175 / 0.050 | 0.000 / 0.000 | 0 |  |
| no_sat_floor | 0.046 | -0.729 | 0.050 | 0.043 | 0.043 / 0.920 | 0.252 / 0.120 | 0.027 / 0.016 | 0.631 / 0.217 | 32 | yes |
| no_brightness_gate | 0.775 | +0.000 | 0.766 | 0.785 | 0.989 / 0.792 | 0.000 / 0.000 | 0.175 / 0.049 | 0.000 / 0.000 | 0 |  |
| no_table_prior | 0.783 | +0.007 | 0.780 | 0.785 | 0.988 / 0.792 | 0.000 / 0.000 | 0.180 / 0.050 | 0.868 / 0.368 | 0 |  |
| no_bg_prior | 0.551 | -0.224 | 0.758 | 0.344 | 0.367 / 0.848 | 0.000 / 0.000 | 0.177 / 0.274 | 0.000 / 0.000 | 0 |  |
| no_priors | 0.444 | -0.331 | 0.771 | 0.117 | 0.119 / 0.864 | 0.001 / 0.025 | 0.183 / 0.055 | 0.868 / 0.368 | 0 | yes |
| box_only | 0.039 | -0.736 | 0.049 | 0.029 | 0.029 / 0.930 | 0.253 / 0.206 | 0.027 / 0.011 | 0.622 / 0.155 | 0 | yes |
| prior_fit_all | 0.781 | +0.005 | 0.761 | 0.801 | 0.984 / 0.811 | 0.000 / 0.000 | 0.175 / 0.029 | 0.000 / 0.000 | 0 |  |
| fit_before_gates | 0.769 | -0.006 | 0.747 | 0.791 | 0.984 / 0.801 | 0.000 / 0.000 | 0.188 / 0.054 | 0.000 / 0.000 | 0 |  |
| no_per_image_cap | 0.749 | -0.026 | 0.714 | 0.785 | 0.986 / 0.794 | 0.000 / 0.000 | 0.142 / 0.056 | 0.000 / 0.000 | 0 |  |
| tie_orange | 0.774 | -0.001 | 0.765 | 0.784 | 0.990 / 0.790 | 0.000 / 0.000 | 0.175 / 0.050 | 0.000 / 0.000 | 0 |  |
| tie_blue | 0.756 | -0.020 | 0.788 | 0.723 | 0.882 / 0.801 | 0.000 / 0.000 | 0.124 / 0.139 | 0.000 / 0.000 | 0 |  |

## Selection (pre-registered rule)

- best primary 0.783 at ablation=no_table_prior
- tied within 0.02: base=base (0.775), ablation=no_horizon_gate (0.773), ablation=no_brightness_gate (0.775), ablation=no_table_prior (0.783), ablation=prior_fit_all (0.781), ablation=fit_before_gates (0.769), ablation=tie_orange (0.774)
- simplest among ties (4 active stages): ablation=no_table_prior
- chosen: `6c993aa0` (ablation=no_table_prior), primary 0.783
