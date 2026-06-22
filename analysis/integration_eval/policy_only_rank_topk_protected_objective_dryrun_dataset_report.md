# Policy-only rank/top-k protected objective dry-run dataset report

## Branch

`exp/15x15-policy-only-rank-topk-protected-objective-dryrun`

## Scope

- Dataset split only.
- Dry-run only.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Selection rule

- Train main rows: `11 <= before_target_rank <= 50`.
- Protected eval rows: `before_target_rank <= 10`.
- Tail eval rows: `before_target_rank > 50`.
- Effective sample weight cap: `3.0`.

## Summary

| metric | value |
|---|---:|
| source_rows | 25 |
| train_main_rows | 7 |
| protected_eval_rows | 15 |
| tail_eval_rows | 3 |
| train_weight_mean | 2.8064204965318953 |
| train_weight_median | 3.0 |
| train_weight_max | 3.0 |

## Train main rows

| case_id | rank | original_eff_weight | capped_eff_weight | before_prob | before_worst_gap | label_type | suggested_bucket |
|---|---:|---:|---:|---:|---:|---|---|
| legacy_g2_m11 | 12 | 3.750000 | 3.000000 | 0.00032455 | -7.170754 | neighbor | priority_policy_numeric_gap |
| legacy_g2_m21 | 47 | 3.000000 | 3.000000 | 0.00014416 | -8.742455 | late_loss_window | priority_policy_gap_unavailable |
| legacy_g4_m13 | 21 | 3.562500 | 3.000000 | 0.00024368 | -7.601815 | neighbor | priority_policy_numeric_gap |
| legacy_g4_m23 | 23 | 2.667352 | 2.667352 | 0.00152231 | -5.669407 | late_loss_window | priority_policy_gap_unavailable |
| legacy_g5_m14 | 17 | 6.990846 | 3.000000 | 0.00194023 | -5.492826 | first_losing_value | priority_policy_numeric_gap |
| legacy_g5_m28 | 17 | 2.412734 | 2.412734 | 0.00365030 | -4.650936 | late_loss_window | priority_policy_gap_unavailable |
| legacy_g6_m17 | 15 | 2.564858 | 2.564858 | 0.00270314 | -5.259431 | first_direct_vs_mcts_divergence;late_loss_window | priority_policy_gap_unavailable |

## Protected eval rows

| case_id | rank | original_eff_weight | capped_eff_weight | before_prob | before_worst_gap | label_type | suggested_bucket |
|---|---:|---:|---:|---:|---:|---|---|
| legacy_g1_m4 | 4 | 5.337941 | 3.000000 | 0.01358208 | -3.980762 | neighbor | priority_policy_numeric_gap |
| legacy_g1_m6 | 4 | 4.252023 | 3.000000 | 0.02087609 | -3.041652 | first_direct_vs_mcts_divergence | priority_policy_numeric_gap |
| legacy_g1_m40 | 3 | 1.498055 | 1.498055 | 0.15029132 | -0.992218 | late_loss_window | priority_policy_gap_unavailable |
| legacy_g2_m5 | 5 | 5.547656 | 3.000000 | 0.01223993 | -4.265397 | neighbor | priority_policy_numeric_gap |
| legacy_g2_m7 | 4 | 2.152983 | 2.152983 | 0.01570867 | -3.611932 | first_direct_vs_mcts_divergence;neighbor | priority_policy_gap_unavailable |
| legacy_g2_m9 | 3 | 3.042874 | 3.000000 | 0.06524349 | -2.212738 | first_losing_value;neighbor | priority_policy_numeric_gap |
| legacy_g3_m4 | 9 | 3.364323 | 3.000000 | 0.00723689 | -4.646803 | neighbor | priority_policy_numeric_gap |
| legacy_g3_m24 | 7 | 2.675377 | 2.675377 | 0.00318027 | -5.701507 | late_loss_window | priority_policy_gap_unavailable |
| legacy_g3_m26 | 5 | 2.598941 | 2.598941 | 0.00419021 | -5.395764 | late_loss_window | priority_policy_gap_unavailable |
| legacy_g4_m17 | 4 | 2.579559 | 2.579559 | 0.00475445 | -5.318236 | neighbor | priority_policy_gap_unavailable |
| legacy_g5_m6 | 3 | 2.662452 | 2.662452 | 0.00461780 | -5.364775 | neighbor | priority_policy_numeric_gap |
| legacy_g5_m8 | 2 | 1.799092 | 1.799092 | 0.08103481 | -2.196366 | first_direct_vs_mcts_divergence | priority_policy_gap_unavailable |
| legacy_g5_m16 | 2 | 1.637685 | 1.637685 | 0.10676790 | -1.550739 | neighbor | priority_policy_gap_unavailable |
| legacy_g6_m5 | 6 | 7.846130 | 3.000000 | 0.00362991 | -5.461506 | first_losing_value | priority_policy_numeric_gap |
| legacy_g6_m19 | 7 | 2.008593 | 2.008593 | 0.02625631 | -3.034372 | neighbor;late_loss_window | priority_policy_gap_unavailable |

## Tail eval rows

| case_id | rank | original_eff_weight | capped_eff_weight | before_prob | before_worst_gap | label_type | suggested_bucket |
|---|---:|---:|---:|---:|---:|---|---|
| legacy_g1_m8 | 102 | 5.535000 | 3.000000 | 0.00018429 | -7.888449 | neighbor | priority_policy_numeric_gap |
| legacy_g5_m12 | 69 | 4.620000 | 3.000000 | 0.00039491 | -7.094744 | neighbor | priority_policy_numeric_gap |
| legacy_g5_m30 | 73 | 3.000000 | 3.000000 | 0.00021954 | -7.507614 | late_loss_window | priority_policy_gap_unavailable |

## Decision

This branch should only verify whether the protected split can be loaded by the rank/top-k trainer in dry-run mode.

Do not run a saved checkpoint yet. A later no-save probe may train only the 7 main rows and evaluate protected/tail rows separately.
