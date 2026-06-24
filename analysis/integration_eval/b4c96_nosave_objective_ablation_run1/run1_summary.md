# b4c96 no-save objective ablation run1 summary

## Scope

- No-save objective ablation only.
- No checkpoint save, no C export, no public benchmark, no promotion.

## Variants

| variant | ce | pair | worst | anchor_kl | verdict |
|---|---:|---:|---:|---:|---|
| A1_stronger_anchor_balanced_hinge | 1.0 | 0.6 | 0.6 | 1.0 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |
| A2_light_worst_suppress | 1.0 | 0.6 | 0.2 | 0.8 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |
| A3_ce_dominant_rank_repair | 1.5 | 0.3 | 0.1 | 0.8 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |

## Group metrics

| variant | group | top5 Δ | top10 Δ | rank>50 Δ | mean_rank Δ | target_prob Δ | worst_gap Δ | hinge Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A1_stronger_anchor_balanced_hinge | train_main_rank_11_50 | 0.000000 | 1.000000 | -1.000000 | -6.714286 | 0.00312396 | 0.295766 | -0.318609 |
| A1_stronger_anchor_balanced_hinge | protected_eval_top10 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01157658 | 0.911788 | -0.108818 |
| A1_stronger_anchor_balanced_hinge | tail_eval_rank_gt50 | 0.000000 | -1.000000 | 2.000000 | 23.333333 | -0.00579524 | -1.014543 | 1.280915 |
| A2_light_worst_suppress | train_main_rank_11_50 | 0.000000 | 1.000000 | -1.000000 | -6.714286 | 0.00312402 | 0.295758 | -0.318614 |
| A2_light_worst_suppress | protected_eval_top10 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01157686 | 0.911791 | -0.108834 |
| A2_light_worst_suppress | tail_eval_rank_gt50 | 0.000000 | -1.000000 | 2.000000 | 23.333333 | -0.00579522 | -1.014530 | 1.280866 |
| A3_ce_dominant_rank_repair | train_main_rank_11_50 | 0.000000 | 1.000000 | -1.000000 | -6.714286 | 0.00312409 | 0.295759 | -0.318613 |
| A3_ce_dominant_rank_repair | protected_eval_top10 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01157822 | 0.911739 | -0.108866 |
| A3_ce_dominant_rank_repair | tail_eval_rank_gt50 | 0.000000 | -1.000000 | 2.000000 | 23.333333 | -0.00579517 | -1.014528 | 1.280806 |

## Preliminary decision rule

A variant is only directionally useful if train improves without protected top5/top10 loss and without tail rank>50 regression.

## Final note

This summary records no-save ablation metrics only. It does not authorize checkpoint save or promotion.
