# b4c96 tail-aware no-save ablation run2 summary

## Scope

- Tail-aware no-save ablation only.
- No checkpoint save, no C export, no public benchmark, no promotion.

## Variants

| variant | dataset | ce | pair | worst | anchor_kl | verdict |
|---|---|---:|---:|---:|---:|---|
| A4_tail_guard | `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A4_tail_guard_dataset.json` | 1.0 | 0.5 | 0.3 | 1.0 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |
| A5_tail_guard_downweight | `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset.json` | 1.0 | 0.5 | 0.3 | 1.0 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |

## Group metrics

| variant | group | top5 Δ | top10 Δ | rank>50 Δ | mean_rank Δ | target_prob Δ | worst_gap Δ | hinge Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A4_tail_guard | train_main_rank_11_50 | 0.000000 | 0.000000 | 1.000000 | 2.300000 | 0.00037343 | -0.115352 | 0.157952 |
| A4_tail_guard | protected_eval_top10 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01150738 | 0.890207 | -0.098539 |
| A4_tail_guard | tail_eval_rank_gt50 | 0.000000 | -1.000000 | 2.000000 | 22.333333 | -0.00576096 | -1.041146 | 1.266028 |
| A5_tail_guard_downweight | train_main_rank_11_50 | 0.000000 | 0.000000 | 1.000000 | 2.300000 | 0.00037362 | -0.115340 | 0.157958 |
| A5_tail_guard_downweight | protected_eval_top10 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01150805 | 0.890158 | -0.098536 |
| A5_tail_guard_downweight | tail_eval_rank_gt50 | 0.000000 | -1.000000 | 2.000000 | 22.333333 | -0.00576089 | -1.041126 | 1.266004 |

## Directional decision rule

A variant is directionally useful only if it improves train while avoiding protected top5/top10 loss and avoiding tail rank>50 regression.

## Final note

This summary records no-save ablation metrics only. It does not authorize checkpoint save or promotion.
