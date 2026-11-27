# In-sample exploration, version 4 (BEFORE the PREREG; not a judged run)

The output of experiments/2026-11-26_selfcal/explore2.py as the method stood when PREREG.md was written: fixed numbers on all eight places, no verdict. PREREG.md lists it under what was looked at. Columns as in summary.md.

```

=== A_found_frame: ordinary found 138.4 of 172 placements (217 of 307 per frame), boxes not on their barrel 1.9 (5 nothing, 0 second, 0 wrong), on empty frames 0 (clean 0)
condition              class       frm    brl    fix   cand    off   xtr1    xtr    emp   fr.b  fr.sd  s.fnd  s.bdy  s.str  s.off sd.emp  moved paint.out1 paint.out2
window_light           ordinary     16     29     28     28      0      0      0      0     14     11     18      0      0      0      0      6       3126       4823
campus_light           ordinary     21     35     35     35      0      0      0      0     17     10     20      0      0      0      0      8      27960      28310
both_abpgray           ordinary      8     16     10     14      1      0      0      0      7      3      5      0      0      0      0      3      34995      38307
lampcool6_bathtile     ordinary      7     15     13     14      0      0      0      0      6      3      4      0      0      0      0      3       9687       9953
lampcool6_glass        ordinary      7     15     15     15      0      0      0      0      6      4      9      0      0      0      0      2      30607      30744
lampcool6_ottoman      ordinary      7     15      3      3      0      0      0      0      6      0      0      0      0      0      0      0       8688       8688
lampmid3_bathtile      ordinary      7     15      1      1      0      0      0      0      6      0      0      0      0      0      0      0      18309      18309
lampmid3_glass         ordinary      7     15     15     15      0      1      1      0      6      4      8      0      0      0      0      1      29717      29717
lampmid6_bathtile      ordinary      7     15      1      1      0      0      0      0      6      0      0      0      0      0      0      0      31540      31540
lampmid6_glass         ordinary      7     15     15     15      0      1      1      0      6      4      8      0      0      0      0      1      27777      27777
lampmid6_ottoman       ordinary      7     15      6      7      0      0      0      0      6      1      1      0      0      0      0      1       7058       9118
lampwarm6_bathtile     ordinary      7     15      1      1      0      0      0      0      6      0      0      0      0      0      0      0      94435      94435
lampwarm6_glass        ordinary      7     15     15     15      0      1      1      0      6      4      8      0      0      0      0      1      23637      23637
lampwarm6_ottoman      ordinary      7     15      0      0      0      1      1      0      6      0      0      0      0      0      0      0       8135       8135
overheaddim_palewood   ordinary      7     15     13     13      0      1      1      0      6      2      3      0      0      0      0      1     155091     155547
window_abpwhite        ordinary     17     32     26     26      0      0      0      0     16     15     15      0      0      0      0     12      69519      70572
window_glass           ordinary      8     15     14     14      1      0      0      0      6      4      8      0      0      0      0      2      53935      53935
lampcool3_wood         extreme      10     21      2      2      0      0      0      0      9      0      0      0      0      0      0      0       6754       6754
lampcool6_wood         extreme      10     21      2      2      2      2      2      0      9      0      0      0      0      0      0      0       8825       8825
lampmid3_ottoman       extreme       7     15      1      1      1      0      0      0      6      0      0      0      0      0      0      0       4945       4945
lampmid3_wood          extreme      10     21      1      1      0      1      1      0      9      0      0      0      0      0      0      0      20352      20352
lampmid6_wood          extreme      10     21      1      1      0      0      0      0      9      0      0      0      0      0      0      0      40087      40087
lampwarm3_wood         extreme      10     21      1      1      0      0      0      0      9      0      0      0      0      0      0      0      50238      50238
lampwarm6_wood         extreme      10     21      0      0      0      1      1      0      9      0      0      0      0      0      0      0      63876      63876
window_black           extreme      10     26      5      5      1      0      0      0      9      0      0      0      0      0      0      0       4806       4806
ALL ORDINARY                       154    307    211    217      2      5      5      0    132     65    107      0      0      0      0     41     634216     643547
seed candidates by verdict: [(('found', 'ok'), 107), (('found', 'not_two_colors'), 1)]
kept seeds on a hand box: 107; rel min 1.52, lowest five [1.52, 1.61, 1.7, 1.96, 2.22]
kept seeds NOT on a hand box: []
floods over 3 %: []
frames that lost a barrel: []
frames with more boxes not on their barrel: []

=== B_local_rel1: ordinary found 146.0 of 172 placements (243 of 307 per frame), boxes not on their barrel 2.2 (5 nothing, 1 second, 0 wrong), on empty frames 0 (clean 0)
condition              class       frm    brl    fix   cand    off   xtr1    xtr    emp   fr.b  fr.sd  s.fnd  s.bdy  s.str  s.off sd.emp  moved paint.out1 paint.out2
window_light           ordinary     16     29     28     28      0      0      0      0     14     11      0     22      0      0      0      0       3126       3126
campus_light           ordinary     21     35     35     35      0      0      0      0     17     12      0     27      0      0      0      0      27960      27960
both_abpgray           ordinary      8     16     10     15      1      0      0      0      7      4      0      7      5      0      0      0      34995      34995
lampcool6_bathtile     ordinary      7     15     13     14      0      0      0      0      6      4      0      6      4      0      0      0       9687       9687
lampcool6_glass        ordinary      7     15     15     15      0      0      0      0      6      4      0     11      0      0      0      0      30607      30607
lampcool6_ottoman      ordinary      7     15      3      8      1      0      0      0      6      3      0      2      5      0      0      0       8688       8688
lampmid3_bathtile      ordinary      7     15      1     10      0      0      1      0      6      4      0      6      4      0      0      0      18309      18309
lampmid3_glass         ordinary      7     15     15     15      0      1      1      0      6      4      0     10      1      0      0      0      29717      30652
lampmid6_bathtile      ordinary      7     15      1      8      0      0      0      0      6      3      0      4      4      0      0      0      31540      31540
lampmid6_glass         ordinary      7     15     15     15      0      1      1      0      6      4      0     10      0      0      0      0      27777      27777
lampmid6_ottoman       ordinary      7     15      6      6      0      0      0      0      6      4      0      0      4      0      0      0       7058       7058
lampwarm6_bathtile     ordinary      7     15      1      6      0      0      0      0      6      3      0      4      2      0      0      0      94435      94435
lampwarm6_glass        ordinary      7     15     15     15      0      1      1      0      6      4      0      8      0      0      0      0      23637      23637
lampwarm6_ottoman      ordinary      7     15      0      0      0      1      1      0      6      0      0      0      0      0      0      0       8135       8135
overheaddim_palewood   ordinary      7     15     13     13      0      1      1      0      6      4      0      8      3      0      0      0     155091     155091
window_abpwhite        ordinary     17     32     26     26      0      0      0      0     16     15      0     17      0      0      0      0      69519      69519
window_glass           ordinary      8     15     14     14      1      0      0      0      6      4      0     10      0      0      0      0      53935      53935
lampcool3_wood         extreme      10     21      2     10      1      0      1      0      9      6      0      4      7      0      0      0       6754       6955
lampcool6_wood         extreme      10     21      2      7      2      2      2      0      9      4      0      3      5      0      0      0       8825       8825
lampmid3_ottoman       extreme       7     15      1      1      1      0      0      0      6      0      0      0      0      0      0      0       4945       4945
lampmid3_wood          extreme      10     21      1     10      1      1      1      0      9      6      0      3      8      0      0      0      20352      20378
lampmid6_wood          extreme      10     21      1      9      0      0      0      0      9      5      0      5      5      0      0      0      40087      40087
lampwarm3_wood         extreme      10     21      1      6      0      0      0      0      9      5      0      2      3      0      0      0      50238      50238
lampwarm6_wood         extreme      10     21      0      6      1      1      1      0      9      4      0      4      4      0      0      0      63876      63876
window_black           extreme      10     26      5      8      1      0      0      0      9      3      0      0      3      0      0      0       4806       4806
ALL ORDINARY                       154    307    211    243      3      5      6      0    132     87      0    152     32      0      0      0     634216     635151
seed candidates by verdict: [(('stripe', 'duplicate'), 290), (('body', 'ok'), 173), (('stripe', 'not_two_colors'), 147), (('stripe', 'ok'), 67), (('body', 'not_two_colors'), 56), (('stripe', 'stripe_not_painted'), 53), (('body', 'body_not_painted'), 52), (('stripe', 'body_like_surround'), 48), (('stripe', 'too_small'), 17), (('stripe', 'off_frame'), 14), (('body', 'too_small'), 9), (('body', 'body_like_surround'), 3), (('body', 'stripe_like_surround'), 2), (('body', 'duplicate'), 2), (('body', 'off_frame'), 1)]
kept seeds on a hand box: 240; rel min 1.07, lowest five [1.07, 1.12, 1.35, 1.38, 1.43]
kept seeds NOT on a hand box: []
floods over 3 %: []
frames that lost a barrel: []
frames with more boxes not on their barrel: [('lampmid3_bathtile_core_01', 0, 1), ('lampcool3_wood_clutter_01', 0, 1)]

=== B_frame: ordinary found 144.8 of 172 placements (236 of 307 per frame), boxes not on their barrel 1.9 (5 nothing, 0 second, 0 wrong), on empty frames 0 (clean 0)
condition              class       frm    brl    fix   cand    off   xtr1    xtr    emp   fr.b  fr.sd  s.fnd  s.bdy  s.str  s.off sd.emp  moved paint.out1 paint.out2
window_light           ordinary     16     29     28     28      0      0      0      0     14     11      0     22      0      0      0      6       3126       3126
campus_light           ordinary     21     35     35     35      0      0      0      0     17     12      0     27      0      0      0     10      27960      28545
both_abpgray           ordinary      8     16     10     15      1      0      0      0      7      4      0      7      5      0      0      4      34995      38824
lampcool6_bathtile     ordinary      7     15     13     14      0      0      0      0      6      4      0      7      4      1      1      4       9687      12060
lampcool6_glass        ordinary      7     15     15     15      0      0      0      0      6      4      0     11      0      0      0      2      30607      30607
lampcool6_ottoman      ordinary      7     15      3     11      0      0      0      0      6      3      0      2      5      0      0      3       8688       9426
lampmid3_bathtile      ordinary      7     15      1      1      0      0      0      0      6      4      0      7      4      0      0      2      18309      20529
lampmid3_glass         ordinary      7     15     15     15      0      1      1      0      6      4      0     10      1      0      0      1      29717      29717
lampmid6_bathtile      ordinary      7     15      1      8      2      0      0      0      6      3      0      4      4      0      0      3      31540      38079
lampmid6_glass         ordinary      7     15     15     15      0      1      1      0      6      4      0     10      0      0      0      1      27777      27777
lampmid6_ottoman       ordinary      7     15      6     10      1      0      0      0      6      4      0      0      4      0      0      4       7058      14098
lampwarm6_bathtile     ordinary      7     15      1      1      0      0      0      0      6      4      0      5      2      0      0      1      94435      97991
lampwarm6_glass        ordinary      7     15     15     15      0      1      1      0      6      4      0      8      0      0      0      2      23637      24252
lampwarm6_ottoman      ordinary      7     15      0      0      0      1      1      0      6      0      0      0      0      0      0      0       8135       8135
overheaddim_palewood   ordinary      7     15     13     13      0      1      1      0      6      4      0      8      3      0      0      4     155091     162798
window_abpwhite        ordinary     17     32     26     26      0      0      0      0     16     15      0     18      0      1      0     15      69519      71147
window_glass           ordinary      8     15     14     14      1      0      0      0      6      4      0     10      0      0      0      2      53935      53938
lampcool3_wood         extreme      10     21      2      3      0      0      0      0      9      6      0      4      7      0      0      4       6754       9665
lampcool6_wood         extreme      10     21      2      8      2      2      2      0      9      4      0      3      5      0      0      4       8825       8865
lampmid3_ottoman       extreme       7     15      1      1      1      0      0      0      6      0      0      0      1      1      1      1       4945       6046
lampmid3_wood          extreme      10     21      1      1      0      1      1      0      9      6      0      3      8      0      0      2      20352      27827
lampmid6_wood          extreme      10     21      1      1      0      0      0      0      9      5      0      5      5      0      0      1      40087      44482
lampwarm3_wood         extreme      10     21      1      1      0      0      0      0      9      5      0      2      3      0      0      0      50238      50238
lampwarm6_wood         extreme      10     21      0      0      0      1      1      0      9      4      0      4      4      0      0      3      63876      69330
window_black           extreme      10     26      5      6      1      0      0      0      9      3      0      0      3      0      0      3       4806       5559
ALL ORDINARY                       154    307    211    236      5      5      5      0    132     88      0    156     32      2      1     64     634216     671049
seed candidates by verdict: [(('stripe', 'duplicate'), 290), (('body', 'ok'), 177), (('stripe', 'not_two_colors'), 123), (('stripe', 'body_like_surround'), 71), (('stripe', 'ok'), 68), (('stripe', 'stripe_not_painted'), 53), (('body', 'body_not_painted'), 52), (('body', 'not_two_colors'), 50), (('stripe', 'too_small'), 17), (('stripe', 'off_frame'), 14), (('body', 'too_small'), 9), (('body', 'body_like_surround'), 5), (('body', 'stripe_like_surround'), 2), (('body', 'duplicate'), 2), (('body', 'off_frame'), 1)]
kept seeds on a hand box: 242; rel min 0.8, lowest five [0.8, 0.93, 1.07, 1.12, 1.35]
kept seeds NOT on a hand box: [('lampcool6_bathtile_neg_02', 'body', 'orange', (225, 116, 272, 167), 0.53), ('window_abpwhite_occlx_13', 'body', 'blue', (417, 131, 448, 165), 0.9), ('lampmid3_ottoman_neg_02', 'stripe', 'blue', (107, 140, 176, 214), 0.87)]
floods over 3 %: [('lampmid3_bathtile_core_01', {'orange': 0.047}), ('lampmid6_bathtile_core_01', {'orange': 0.043, 'blue': 0.001}), ('lampwarm6_bathtile_occl_02', {'orange': 0.213}), ('lampcool3_wood_cluster_01', {'orange': 0.049}), ('lampcool3_wood_clutter_01', {'orange': 0.063}), ('lampcool6_wood_cluster_01', {'orange': 0.095, 'blue': 0.0}), ('lampcool6_wood_core_01', {'orange': 0.077, 'blue': 0.005}), ('lampmid3_wood_cluster_01', {'orange': 0.576}), ('lampmid3_wood_clutter_01', {'orange': 0.176}), ('lampmid3_wood_core_01', {'orange': 0.554}), ('lampmid3_wood_occl_01', {'orange': 0.102}), ('lampmid6_wood_clutter_01', {'orange': 0.08}), ('lampmid6_wood_core_01', {'orange': 0.032}), ('lampwarm3_wood_cluster_01', {'orange': 0.403}), ('lampwarm3_wood_clutter_01', {'orange': 0.272}), ('lampwarm3_wood_core_01', {'orange': 0.252}), ('lampwarm3_wood_occl_02', {'orange': 0.132}), ('lampwarm3_wood_occl_04', {'orange': 0.034}), ('lampwarm6_wood_clutter_01', {'orange': 0.121}), ('window_black_close_02', {'orange': 0.112, 'blue': 0.0}), ('window_black_held_01', {'orange': 0.109, 'blue': 0.0})]
frames that lost a barrel: []
frames with more boxes not on their barrel: []

=== AB_both: ordinary found 148.6 of 172 placements (251 of 307 per frame), boxes not on their barrel 2.4 (6 nothing, 1 second, 0 wrong), on empty frames 1 (clean 0)
condition              class       frm    brl    fix   cand    off   xtr1    xtr    emp   fr.b  fr.sd  s.fnd  s.bdy  s.str  s.off sd.emp  moved paint.out1 paint.out2
window_light           ordinary     16     29     28     28      0      0      0      0     14     11     18      4      0      0      0      6       3126       4823
campus_light           ordinary     21     35     35     35      0      0      0      0     17     12     20      7      0      0      0     10      27960      28369
both_abpgray           ordinary      8     16     10     15      1      0      0      0      7      4      5      3      4      0      0      4      34995      39232
lampcool6_bathtile     ordinary      7     15     13     14      0      0      1      1      6      4      4      5      3      1      1      5       9687      12351
lampcool6_glass        ordinary      7     15     15     15      0      0      0      0      6      4      9      2      0      0      0      3      30607      30744
lampcool6_ottoman      ordinary      7     15      3     11      0      0      0      0      6      3      0      2      5      0      0      3       8688       9426
lampmid3_bathtile      ordinary      7     15      1     10      0      0      1      0      6      4      0      7      4      0      0      2      18309      20529
lampmid3_glass         ordinary      7     15     15     15      0      1      1      0      6      4      8      2      1      0      0      1      29717      30652
lampmid6_bathtile      ordinary      7     15      1      9      1      0      0      0      6      3      0      4      4      0      0      3      31540      38079
lampmid6_glass         ordinary      7     15     15     15      0      1      1      0      6      4      8      2      0      0      0      1      27777      27777
lampmid6_ottoman       ordinary      7     15      6     10      1      0      0      0      6      4      1      0      3      0      0      4       7058      14098
lampwarm6_bathtile     ordinary      7     15      1      6      1      0      0      0      6      4      0      5      2      0      0      1      94435      98012
lampwarm6_glass        ordinary      7     15     15     15      0      1      1      0      6      4      8      2      0      0      0      1      23637      23637
lampwarm6_ottoman      ordinary      7     15      0      0      0      1      1      0      6      0      0      0      0      0      0      0       8135       8135
overheaddim_palewood   ordinary      7     15     13     13      0      1      1      0      6      4      3      5      3      0      0      4     155091     162798
window_abpwhite        ordinary     17     32     26     26      0      0      0      0     16     15     15      3      0      1      0     13      69519      71199
window_glass           ordinary      8     15     14     14      1      0      0      0      6      4      8      2      0      0      0      2      53935      53938
lampcool3_wood         extreme      10     21      2     11      0      0      1      0      9      6      0      4      7      0      0      4       6754       9866
lampcool6_wood         extreme      10     21      2      8      2      2      2      0      9      4      0      3      5      0      0      4       8825       8865
lampmid3_ottoman       extreme       7     15      1      1      1      0      1      1      6      0      0      0      1      1      1      1       4945       8372
lampmid3_wood          extreme      10     21      1     11      1      1      1      0      9      6      0      3      8      0      0      2      20352      27853
lampmid6_wood          extreme      10     21      1      9      1      0      0      0      9      5      0      5      5      0      0      1      40087      44482
lampwarm3_wood         extreme      10     21      1      6      0      0      0      0      9      5      0      2      3      0      0      0      50238      50238
lampwarm6_wood         extreme      10     21      0      6      0      1      1      0      9      4      0      4      4      0      0      3      63876      69330
window_black           extreme      10     26      5      8      1      0      0      0      9      3      0      0      3      0      0      3       4806       5559
ALL ORDINARY                       154    307    211    251      5      5      7      1    132     88    107     55     29      2      1     63     634216     673799
seed candidates by verdict: [(('stripe', 'duplicate'), 295), (('stripe', 'not_two_colors'), 122), (('found', 'ok'), 107), (('body', 'duplicate'), 103), (('body', 'ok'), 76), (('stripe', 'body_like_surround'), 70), (('stripe', 'ok'), 65), (('stripe', 'stripe_not_painted'), 53), (('body', 'body_not_painted'), 52), (('body', 'not_two_colors'), 50), (('stripe', 'too_small'), 17), (('stripe', 'off_frame'), 14), (('body', 'too_small'), 9), (('body', 'body_like_surround'), 5), (('body', 'stripe_like_surround'), 2), (('found', 'not_two_colors'), 1), (('body', 'off_frame'), 1)]
kept seeds on a hand box: 245; rel min 0.8, lowest five [0.8, 0.93, 1.07, 1.12, 1.35]
kept seeds NOT on a hand box: [('lampcool6_bathtile_neg_02', 'body', 'orange', (225, 116, 272, 167), 0.53), ('window_abpwhite_occlx_13', 'body', 'blue', (417, 131, 448, 165), 0.9), ('lampmid3_ottoman_neg_02', 'stripe', 'blue', (107, 140, 176, 214), 0.87)]
floods over 3 %: [('lampmid3_bathtile_core_01', {'orange': 0.047}), ('lampmid6_bathtile_core_01', {'orange': 0.043, 'blue': 0.001}), ('lampwarm6_bathtile_occl_02', {'orange': 0.213}), ('lampcool3_wood_cluster_01', {'orange': 0.049}), ('lampcool3_wood_clutter_01', {'orange': 0.063}), ('lampcool6_wood_cluster_01', {'orange': 0.095, 'blue': 0.0}), ('lampcool6_wood_core_01', {'orange': 0.077, 'blue': 0.005}), ('lampmid3_wood_cluster_01', {'orange': 0.576}), ('lampmid3_wood_clutter_01', {'orange': 0.176}), ('lampmid3_wood_core_01', {'orange': 0.554}), ('lampmid3_wood_occl_01', {'orange': 0.102}), ('lampmid6_wood_clutter_01', {'orange': 0.08}), ('lampmid6_wood_core_01', {'orange': 0.032}), ('lampwarm3_wood_cluster_01', {'orange': 0.403}), ('lampwarm3_wood_clutter_01', {'orange': 0.272}), ('lampwarm3_wood_core_01', {'orange': 0.252}), ('lampwarm3_wood_occl_02', {'orange': 0.132}), ('lampwarm3_wood_occl_04', {'orange': 0.034}), ('lampwarm6_wood_clutter_01', {'orange': 0.121}), ('window_black_close_02', {'orange': 0.112, 'blue': 0.0}), ('window_black_held_01', {'orange': 0.109, 'blue': 0.0})]
frames that lost a barrel: []
frames with more boxes not on their barrel: [('lampcool6_bathtile_neg_02', 0, 1), ('lampmid3_bathtile_core_01', 0, 1), ('lampcool3_wood_clutter_01', 0, 1), ('lampmid3_ottoman_neg_02', 0, 1)]

=== AB_both_rel1: ordinary found 148.6 of 172 placements (251 of 307 per frame), boxes not on their barrel 2.2 (5 nothing, 1 second, 0 wrong), on empty frames 0 (clean 0)
condition              class       frm    brl    fix   cand    off   xtr1    xtr    emp   fr.b  fr.sd  s.fnd  s.bdy  s.str  s.off sd.emp  moved paint.out1 paint.out2
window_light           ordinary     16     29     28     28      0      0      0      0     14     11     18      4      0      0      0      6       3126       4823
campus_light           ordinary     21     35     35     35      0      0      0      0     17     12     20      7      0      0      0     10      27960      28369
both_abpgray           ordinary      8     16     10     15      1      0      0      0      7      4      5      3      4      0      0      4      34995      39232
lampcool6_bathtile     ordinary      7     15     13     14      0      0      0      0      6      4      4      4      3      0      0      4       9687      10904
lampcool6_glass        ordinary      7     15     15     15      0      0      0      0      6      4      9      2      0      0      0      3      30607      30744
lampcool6_ottoman      ordinary      7     15      3     11      0      0      0      0      6      3      0      2      5      0      0      3       8688       9426
lampmid3_bathtile      ordinary      7     15      1     10      0      0      1      0      6      4      0      6      4      0      0      2      18309      20529
lampmid3_glass         ordinary      7     15     15     15      0      1      1      0      6      4      8      2      1      0      0      1      29717      30652
lampmid6_bathtile      ordinary      7     15      1      9      1      0      0      0      6      3      0      4      4      0      0      3      31540      38079
lampmid6_glass         ordinary      7     15     15     15      0      1      1      0      6      4      8      2      0      0      0      1      27777      27777
lampmid6_ottoman       ordinary      7     15      6     10      1      0      0      0      6      4      1      0      3      0      0      4       7058      14098
lampwarm6_bathtile     ordinary      7     15      1      6      0      0      0      0      6      3      0      4      2      0      0      1      94435      97991
lampwarm6_glass        ordinary      7     15     15     15      0      1      1      0      6      4      8      2      0      0      0      1      23637      23637
lampwarm6_ottoman      ordinary      7     15      0      0      0      1      1      0      6      0      0      0      0      0      0      0       8135       8135
overheaddim_palewood   ordinary      7     15     13     13      0      1      1      0      6      4      3      5      3      0      0      4     155091     162798
window_abpwhite        ordinary     17     32     26     26      0      0      0      0     16     15     15      2      0      0      0     13      69519      71030
window_glass           ordinary      8     15     14     14      1      0      0      0      6      4      8      2      0      0      0      2      53935      53938
lampcool3_wood         extreme      10     21      2     11      0      0      1      0      9      6      0      4      7      0      0      4       6754       9866
lampcool6_wood         extreme      10     21      2      8      2      2      2      0      9      4      0      3      5      0      0      4       8825       8865
lampmid3_ottoman       extreme       7     15      1      1      1      0      0      0      6      0      0      0      0      0      0      0       4945       4945
lampmid3_wood          extreme      10     21      1     11      1      1      1      0      9      6      0      3      8      0      0      2      20352      27853
lampmid6_wood          extreme      10     21      1      9      1      0      0      0      9      5      0      5      5      0      0      1      40087      44482
lampwarm3_wood         extreme      10     21      1      6      0      0      0      0      9      5      0      2      3      0      0      0      50238      50238
lampwarm6_wood         extreme      10     21      0      6      0      1      1      0      9      4      0      4      4      0      0      3      63876      69330
window_black           extreme      10     26      5      8      1      0      0      0      9      3      0      0      3      0      0      3       4806       5559
ALL ORDINARY                       154    307    211    251      4      5      6      0    132     87    107     51     29      0      0     62     634216     672162
seed candidates by verdict: [(('stripe', 'duplicate'), 295), (('stripe', 'not_two_colors'), 146), (('found', 'ok'), 107), (('body', 'duplicate'), 103), (('body', 'ok'), 72), (('stripe', 'ok'), 64), (('body', 'not_two_colors'), 56), (('stripe', 'stripe_not_painted'), 53), (('body', 'body_not_painted'), 52), (('stripe', 'body_like_surround'), 47), (('stripe', 'too_small'), 17), (('stripe', 'off_frame'), 14), (('body', 'too_small'), 9), (('body', 'body_like_surround'), 3), (('body', 'stripe_like_surround'), 2), (('found', 'not_two_colors'), 1), (('body', 'off_frame'), 1)]
kept seeds on a hand box: 243; rel min 1.07, lowest five [1.07, 1.12, 1.35, 1.38, 1.43]
kept seeds NOT on a hand box: []
floods over 3 %: [('lampmid3_bathtile_core_01', {'orange': 0.043}), ('lampmid6_bathtile_core_01', {'orange': 0.043, 'blue': 0.001}), ('lampcool3_wood_cluster_01', {'orange': 0.049}), ('lampcool3_wood_clutter_01', {'orange': 0.063}), ('lampcool6_wood_cluster_01', {'orange': 0.095, 'blue': 0.0}), ('lampcool6_wood_core_01', {'orange': 0.077, 'blue': 0.005}), ('lampmid3_wood_cluster_01', {'orange': 0.576}), ('lampmid3_wood_clutter_01', {'orange': 0.176}), ('lampmid3_wood_core_01', {'orange': 0.554}), ('lampmid3_wood_occl_01', {'orange': 0.102}), ('lampmid6_wood_clutter_01', {'orange': 0.08}), ('lampmid6_wood_core_01', {'orange': 0.032}), ('lampwarm3_wood_cluster_01', {'orange': 0.403}), ('lampwarm3_wood_clutter_01', {'orange': 0.272}), ('lampwarm3_wood_core_01', {'orange': 0.252}), ('lampwarm3_wood_occl_02', {'orange': 0.132}), ('lampwarm3_wood_occl_04', {'orange': 0.034}), ('lampwarm6_wood_clutter_01', {'orange': 0.121}), ('window_black_close_02', {'orange': 0.112, 'blue': 0.0}), ('window_black_held_01', {'orange': 0.109, 'blue': 0.0})]
frames that lost a barrel: []
frames with more boxes not on their barrel: [('lampmid3_bathtile_core_01', 0, 1), ('lampcool3_wood_clutter_01', 0, 1)]
```
