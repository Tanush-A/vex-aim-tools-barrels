# v1_adaptive_shift: SYNTHETIC lighting shifts applied to held-out frames only (train frames untouched)

Not real data: a probe of which parts of the method depend on the lighting. gain g multiplies every pixel by g; a cast multiplies channels differently. Scores: primary = mean pooled IoU (orange, blue); neg FP.

| shift | config | primary | orange IoU (P/R) | blue IoU (P/R) | neg FP o/b |
|---|---|---|---|---|---|
| none | fixed floor (v1 final) | 0.810 | 0.829 (0.939/0.876) | 0.791 (0.988/0.799) | 0.000/0.000 |
| none | band floor | 0.809 | 0.825 (0.934/0.876) | 0.793 (0.988/0.800) | 0.000/0.000 |
| none | band floor + YUV chroma box | 0.814 | 0.842 (0.921/0.908) | 0.785 (0.947/0.821) | 0.000/0.000 |
| none | band floor + re-fit (margin 3) | 0.816 | 0.823 (0.933/0.874) | 0.810 (0.990/0.817) | 0.000/0.000 |
| none | band floor + YUV + re-fit | 0.820 | 0.842 (0.914/0.914) | 0.798 (0.957/0.828) | 0.000/0.000 |
| gain 0.5 | fixed floor (v1 final) | 0.534 | 0.561 (0.993/0.563) | 0.507 (0.998/0.507) | 0.000/0.000 |
| gain 0.5 | band floor | 0.630 | 0.582 (0.974/0.591) | 0.677 (0.965/0.695) | 0.000/0.000 |
| gain 0.5 | band floor + YUV chroma box | 0.770 | 0.845 (0.969/0.869) | 0.695 (0.945/0.724) | 0.000/0.000 |
| gain 0.5 | band floor + re-fit (margin 3) | 0.512 | 0.582 (0.974/0.591) | 0.443 (0.960/0.451) | 0.000/0.000 |
| gain 0.5 | band floor + YUV + re-fit | 0.577 | 0.529 (0.989/0.532) | 0.624 (0.982/0.632) | 0.000/0.000 |
| gain 0.75 | fixed floor (v1 final) | 0.760 | 0.796 (0.974/0.814) | 0.724 (0.985/0.732) | 0.000/0.000 |
| gain 0.75 | band floor | 0.786 | 0.801 (0.952/0.835) | 0.770 (0.964/0.793) | 0.000/0.000 |
| gain 0.75 | band floor + YUV chroma box | 0.824 | 0.861 (0.946/0.905) | 0.787 (0.954/0.818) | 0.000/0.000 |
| gain 0.75 | band floor + re-fit (margin 3) | 0.810 | 0.821 (0.957/0.852) | 0.799 (0.988/0.807) | 0.000/0.000 |
| gain 0.75 | band floor + YUV + re-fit | 0.825 | 0.857 (0.943/0.903) | 0.792 (0.962/0.818) | 0.000/0.000 |
| gain 1.25 | fixed floor (v1 final) | 0.558 | 0.465 (0.772/0.539) | 0.650 (0.980/0.659) | 0.000/0.000 |
| gain 1.25 | band floor | 0.564 | 0.492 (0.880/0.527) | 0.636 (0.987/0.641) | 0.000/0.000 |
| gain 1.25 | band floor + YUV chroma box | 0.491 | 0.423 (0.829/0.463) | 0.559 (0.931/0.583) | 0.000/0.000 |
| gain 1.25 | band floor + re-fit (margin 3) | 0.673 | 0.601 (0.902/0.643) | 0.745 (0.989/0.751) | 0.000/0.000 |
| gain 1.25 | band floor + YUV + re-fit | 0.590 | 0.514 (0.852/0.565) | 0.666 (0.945/0.693) | 0.000/0.000 |
| warm cast (R×1.2, B×0.8) | fixed floor (v1 final) | 0.443 | 0.171 (0.189/0.650) | 0.714 (0.997/0.716) | 0.031/0.000 |
| warm cast (R×1.2, B×0.8) | band floor | 0.421 | 0.208 (0.236/0.642) | 0.634 (0.998/0.635) | 0.013/0.000 |
| warm cast (R×1.2, B×0.8) | band floor + YUV chroma box | 0.158 | 0.015 (0.016/0.440) | 0.301 (0.364/0.636) | 0.199/0.004 |
| warm cast (R×1.2, B×0.8) | band floor + re-fit (margin 3) | 0.569 | 0.504 (0.573/0.808) | 0.634 (0.998/0.635) | 0.013/0.000 |
| warm cast (R×1.2, B×0.8) | band floor + YUV + re-fit | 0.283 | 0.017 (0.018/0.517) | 0.548 (0.798/0.637) | 0.199/0.004 |
| cool cast (R×0.8, B×1.2) | fixed floor (v1 final) | 0.417 | 0.784 (0.987/0.792) | 0.051 (0.052/0.767) | 0.000/0.077 |
| cool cast (R×0.8, B×1.2) | band floor | 0.564 | 0.551 (0.998/0.552) | 0.577 (0.990/0.580) | 0.000/0.000 |
| cool cast (R×0.8, B×1.2) | band floor + YUV chroma box | 0.422 | 0.557 (0.998/0.558) | 0.287 (0.505/0.398) | 0.000/0.003 |
| cool cast (R×0.8, B×1.2) | band floor + re-fit (margin 3) | 0.602 | 0.555 (0.998/0.555) | 0.650 (0.992/0.654) | 0.000/0.000 |
| cool cast (R×0.8, B×1.2) | band floor + YUV + re-fit | 0.457 | 0.557 (0.998/0.558) | 0.356 (0.560/0.495) | 0.000/0.003 |
