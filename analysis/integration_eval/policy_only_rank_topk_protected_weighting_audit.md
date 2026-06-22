# Policy-only rank/top-k protected weighting audit

## Branch

`exp/15x15-policy-only-rank-topk-protected-weighting-audit`

## Scope

- Audit only.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`
- Optional run1 metrics: `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv`
- Output CSV: `analysis/integration_eval/policy_only_rank_topk_protected_weighting_audit.csv`

## Dataset summary

| metric | value |
|---|---:|
| rows | 25 |
| mean effective weight | 3.484279 |
| median effective weight | 3.000000 |
| max effective weight | 7.846130 |
| mean baseline target rank | 18.560000 |
| baseline top3 rows | 5 |
| baseline top5 rows | 11 |
| baseline top10 rows | 15 |
| baseline rank_gt50 rows | 3 |

## Rank bucket stats

| group | rows | mean_weight | median_weight | max_weight | mean_rank | top10_rows | rank_gt50_rows | mean_before_worst_gap | run1_mean_rank_delta | run1_mean_prob_delta | run1_mean_worst_gap_delta | run1_protected_top10_regressions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rank_001_003 | 5 | 2.128031 | 1.799092 | 3.042874 | 2.600000 | 5 | 0 | -2.463367 | 0.000000 | -0.000825 | -0.265755 | 0 |
| rank_004_005 | 6 | 3.744851 | 3.425482 | 5.547656 | 4.333333 | 6 | 0 | -4.268957 | 0.666667 | 0.005184 | -0.360444 | 0 |
| rank_006_010 | 4 | 3.973606 | 3.019850 | 7.846130 | 7.250000 | 4 | 0 | -4.711047 | -2.000000 | 0.001872 | 0.415457 | 0 |
| rank_011_050 | 7 | 3.564041 | 3.000000 | 6.990846 | 21.714286 | 0 | 0 | -6.369661 | -2.571429 | 0.000437 | -0.688426 | 0 |
| rank_051_plus | 3 | 4.385000 | 4.620000 | 5.535000 | 81.333333 | 0 | 3 | -7.496936 | 12.000000 | -0.000104 | -0.228456 | 0 |

## Weight bucket stats

| group | rows | mean_weight | median_weight | max_weight | mean_rank | top10_rows | rank_gt50_rows | mean_before_worst_gap | run1_mean_rank_delta | run1_mean_prob_delta | run1_mean_worst_gap_delta | run1_protected_top10_regressions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| weight_2_4 | 15 | 2.802836 | 2.667352 | 3.750000 | 16.666667 | 8 | 1 | -5.459236 | -1.400000 | -0.003153 | -0.606592 | 0 |
| weight_4_8 | 7 | 5.732799 | 5.535000 | 7.846130 | 29.571429 | 4 | 2 | -5.317905 | 4.857143 | 0.007464 | 0.202066 | 0 |
| weight_lt_2 | 3 | 1.644944 | 1.637685 | 1.799092 | 2.333333 | 3 | 0 | -1.579775 | 0.333333 | 0.010751 | 0.116818 | 0 |

## Suggested bucket stats

| group | rows | mean_weight | median_weight | max_weight | mean_rank | top10_rows | rank_gt50_rows | mean_before_worst_gap | run1_mean_rank_delta | run1_mean_prob_delta | run1_mean_worst_gap_delta | run1_protected_top10_regressions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| priority_policy_gap_unavailable | 13 | 2.353479 | 2.564858 | 3.000000 | 16.076923 | 8 | 1 | -4.586998 | -1.076923 | 0.001618 | -0.291831 | 0 |
| priority_policy_numeric_gap | 12 | 4.709312 | 4.436012 | 7.846130 | 21.250000 | 7 | 2 | -5.351852 | 2.333333 | 0.001348 | -0.295014 | 0 |

## Label type stats

| group | rows | mean_weight | median_weight | max_weight | mean_rank | top10_rows | rank_gt50_rows | mean_before_worst_gap | run1_mean_rank_delta | run1_mean_prob_delta | run1_mean_worst_gap_delta | run1_protected_top10_regressions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| first_direct_vs_mcts_divergence | 2 | 3.025557 | 3.025557 | 4.252023 | 3 | 2 | 0 | -2.619009 | 0.500000 | 0.015344 | 0.440120 | 0 |
| first_direct_vs_mcts_divergence;late_loss_window | 1 | 2.564858 | 2.564858 | 2.564858 | 15 | 0 | 0 | -5.259431 | -5.000000 | 0.003056 | 0.738967 | 0 |
| first_direct_vs_mcts_divergence;neighbor | 1 | 2.152983 | 2.152983 | 2.152983 | 4 | 1 | 0 | -3.611932 | 1.000000 | -0.009139 | -0.763392 | 0 |
| first_losing_value | 2 | 7.418488 | 7.418488 | 7.846130 | 11.500000 | 1 | 0 | -5.477166 | 2.000000 | 0.005132 | 0.562130 | 0 |
| first_losing_value;neighbor | 1 | 3.042874 | 3.042874 | 3.042874 | 3 | 1 | 0 | -2.212738 | 0.000000 | -0.034503 | -1.150988 | 0 |
| late_loss_window | 7 | 2.550351 | 2.667352 | 3.000000 | 25 | 3 | 1 | -5.522843 | -1.428571 | -0.004419 | 0.010897 | 0 |
| neighbor | 10 | 3.859712 | 3.656250 | 5.547656 | 23.100000 | 6 | 2 | -5.488248 | 2.400000 | 0.008786 | -0.637858 | 0 |
| neighbor;late_loss_window | 1 | 2.008593 | 2.008593 | 2.008593 | 7 | 1 | 0 | -3.034372 | -1.000000 | -0.020079 | -1.860752 | 0 |

## Highest effective weights

| case_id | rank | effective_weight | sample_weight | hardness_weight | before_worst_gap | suggested_bucket | label_type | run1_rank_delta | run1_prob_delta | run1_gap_delta |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| legacy_g6_m5 | 6 | 7.846130 | 3.000000 | 2.615377 | -5.461506 | priority_policy_numeric_gap | first_losing_value | -3 | 0.01095439214259386 | 1.4822158813476562 |
| legacy_g5_m14 | 17 | 6.990846 | 2.665000 | 2.623207 | -5.492826 | priority_policy_numeric_gap | first_losing_value | 7 | -0.0006912515964359045 | -0.3579559326171875 |
| legacy_g2_m5 | 5 | 5.547656 | 2.395000 | 2.316349 | -4.265397 | priority_policy_numeric_gap | neighbor | -2 | 0.0034610209986567497 | 0.22522878646850586 |
| legacy_g1_m8 | 102 | 5.535000 | 1.845000 | 3.000000 | -7.888449 | priority_policy_numeric_gap | neighbor | 9 | -6.819002737756819e-05 | 0.14369583129882812 |
| legacy_g1_m4 | 4 | 5.337941 | 2.377500 | 2.245191 | -3.980762 | priority_policy_numeric_gap | neighbor | 1 | -0.005915489513427019 | -0.6915302276611328 |
| legacy_g5_m12 | 69 | 4.620000 | 1.540000 | 3.000000 | -7.094744 | priority_policy_numeric_gap | neighbor | 22 | -0.00017866298730950803 | -0.4318819046020508 |
| legacy_g1_m6 | 4 | 4.252023 | 2.115000 | 2.010413 | -3.041652 | priority_policy_numeric_gap | first_direct_vs_mcts_divergence | 0 | 0.044687872752547264 | 1.0446863174438477 |
| legacy_g2_m11 | 12 | 3.750000 | 1.250000 | 3.000000 | -7.170754 | priority_policy_numeric_gap | neighbor | 3 | -0.0002963244951388333 | -3.178346633911133 |
| legacy_g4_m13 | 21 | 3.562500 | 1.187500 | 3.000000 | -7.601815 | priority_policy_numeric_gap | neighbor | -5 | 9.52481059357524e-06 | -0.08614635467529297 |
| legacy_g3_m4 | 9 | 3.364323 | 1.395000 | 2.411701 | -4.646803 | priority_policy_numeric_gap | neighbor | -3 | 0.000593880657106638 | -0.01090383529663086 |

## Worst run1 rank regressions

| case_id | rank | effective_weight | run1_rank_delta | run1_prob_delta | run1_gap_delta | run1_hinge_delta | protected_top10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_g5_m12 | 69 | 4.620000 | 22 | -0.00017866298730950803 | -0.4318819046020508 | 0.6612695693969721 | 0 |
| legacy_g1_m8 | 102 | 5.535000 | 9 | -6.819002737756819e-05 | 0.14369583129882812 | 0.855967330932617 | 0 |
| legacy_g5_m14 | 17 | 6.990846 | 7 | -0.0006912515964359045 | -0.3579559326171875 | 0.5685592651367184 | 0 |
| legacy_g5_m30 | 73 | 3.000000 | 5 | -6.605687667615712e-05 | -0.3971834182739258 | 0.23378276824951172 | 0 |
| legacy_g3_m26 | 5 | 2.598941 | 4 | 0.0024318331852555275 | 0.7097644805908203 | 0.6453264236450196 | 1 |
| legacy_g2_m11 | 12 | 3.750000 | 3 | -0.0002963244951388333 | -3.178346633911133 | 1.5708573341369636 | 0 |
| legacy_g1_m4 | 4 | 5.337941 | 1 | -0.005915489513427019 | -0.6915302276611328 | 0.4233070373535155 | 1 |
| legacy_g2_m7 | 4 | 2.152983 | 1 | -0.009138835594058037 | -0.763392448425293 | 0.8026884078979493 | 1 |
| legacy_g5_m8 | 2 | 1.799092 | 1 | -0.013999886810779572 | -0.1644458770751953 | 0.1756767272949219 | 1 |
| legacy_g1_m6 | 4 | 4.252023 | 0 | 0.044687872752547264 | 1.0446863174438477 | -0.6663097381591797 | 1 |

## Worst run1 target-probability regressions

| case_id | rank | effective_weight | run1_rank_delta | run1_prob_delta | run1_gap_delta | run1_hinge_delta | protected_top10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_g1_m40 | 3 | 1.498055 | 0 | -0.05030186474323273 | -0.3520660400390625 | 0.19598541259765623 | 1 |
| legacy_g2_m9 | 3 | 3.042874 | 0 | -0.03450305201113224 | -1.1509876251220703 | 0.034201622009277344 | 1 |
| legacy_g6_m19 | 7 | 2.008593 | -1 | -0.020079289563000202 | -1.8607521057128906 | 1.0069131851196287 | 1 |
| legacy_g5_m8 | 2 | 1.799092 | 1 | -0.013999886810779572 | -0.1644458770751953 | 0.1756767272949219 | 1 |
| legacy_g2_m7 | 4 | 2.152983 | 1 | -0.009138835594058037 | -0.763392448425293 | 0.8026884078979493 | 1 |
| legacy_g1_m4 | 4 | 5.337941 | 1 | -0.005915489513427019 | -0.6915302276611328 | 0.4233070373535155 | 1 |
| legacy_g4_m17 | 4 | 2.579559 | 0 | -0.00442304412717931 | -2.687422752380371 | 1.0632699966430665 | 1 |
| legacy_g5_m6 | 3 | 2.662452 | -1 | -0.0018748990260064602 | -0.5282399654388428 | 0.003387594223022594 | 1 |
| legacy_g5_m14 | 17 | 6.990846 | 7 | -0.0006912515964359045 | -0.3579559326171875 | 0.5685592651367184 | 0 |
| legacy_g2_m11 | 12 | 3.750000 | 3 | -0.0002963244951388333 | -3.178346633911133 | 1.5708573341369636 | 0 |

## Audit interpretation

Run1 and run2 showed that full-dataset policy-head updates are unstable under the current weighting scheme.

This audit separates rows by baseline rank, effective weight, suggested bucket, and label type. The purpose is to decide whether the next objective should protect already-good top10 rows, isolate extreme tail rows, or reduce high-hardness rows before another training attempt.

A safe next training probe should not save a checkpoint until a no-save or diagnostic pass shows:

- no protected top10 regressions;
- no increase in rank_gt50 rows;
- target probability does not collapse on already-top10 rows;
- useful top5/top10 movement appears before suppress-gap improvements are considered meaningful.

## Recommended next decision rule

Do not run another full 25-row training pass with the current effective weights.

Recommended next branch should implement a protected-row objective dry-run:

`exp/15x15-policy-only-rank-topk-protected-objective-dryrun`

Candidate protection rules:

1. Rows with baseline target_rank <= 10 should be evaluation/protection rows, not main training rows.
2. Rows with baseline target_rank > 50 should be isolated into a separate tail probe.
3. Main training rows should initially target only baseline rank 11-50, where top-k movement is plausible.
4. Cap effective_sample_weight before another training run.
5. Require no-save evidence before saving any checkpoint.

## Decision

Audit only.

No training, no checkpoint, no export, no public benchmark, no promotion.
