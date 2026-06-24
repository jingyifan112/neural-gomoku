# b4c96 Stage C failure forensics

## Scope

- Analysis only: read existing Stage C gate CSV.
- No training, no checkpoint write, no C export, no public benchmark, no promotion.
- Input gate CSV: `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.csv`

## Summary

| key | value |
|---|---:|
| rows | 25 |
| diagnosis | B4C96_STAGEC_FAILED_DUE_TO_PROTECTED_OR_OBJECTIVE_REGRESSION |

## Top-k movement

| key | value |
|---|---:|
| top3_a | 7 |
| top3_b | 7 |
| top3_delta | 0 |
| top5_a | 11 |
| top5_b | 9 |
| top5_delta | -2 |
| top10_a | 14 |
| top10_b | 15 |
| top10_delta | 1 |
| rank_gt50_a | 3 |
| rank_gt50_b | 4 |
| rank_gt50_delta | 1 |

## Mean deltas

| key | value |
|---|---:|
| target_rank_a | 17.320000 |
| target_rank_b | 19.520000 |
| target_rank_delta | 2.200000 |
| target_prob_delta | -0.006594 |
| primary_gap_delta | -0.193933 |
| worst_suppress_gap_delta | -0.485118 |
| multi_pair_hinge_delta | 0.273795 |

## Direction counts

### rank

| key | value |
|---|---:|
| improved | 8 |
| regressed | 11 |
| same | 6 |

### prob

| key | value |
|---|---:|
| improved | 11 |
| regressed | 14 |

### primary_gap

| key | value |
|---|---:|
| improved | 13 |
| regressed | 12 |

### worst_gap

| key | value |
|---|---:|
| improved | 12 |
| regressed | 13 |

### multi_pair_hinge

| key | value |
|---|---:|
| improved | 11 |
| regressed | 14 |

## Rank buckets

### Before Model B

| key | value |
|---|---:|
| protected_top10 | 3 |
| protected_top3 | 7 |
| protected_top5 | 4 |
| tail_rank_gt50 | 3 |
| trainable_rank_11_50 | 8 |

### After Model B

| key | value |
|---|---:|
| protected_top10 | 6 |
| protected_top3 | 7 |
| protected_top5 | 2 |
| tail_rank_gt50 | 4 |
| trainable_rank_11_50 | 6 |

## Forensics outcomes

| key | value |
|---|---:|
| directionally_useful | 9 |
| mixed_or_regressed | 5 |
| partial_tail_repair_unresolved | 1 |
| severe_core_regression | 10 |

## Failure tags

| key | value |
|---|---:|
| prob_regression | 14 |
| multi_pair_hinge_regression | 14 |
| worst_gap_regression | 13 |
| primary_gap_regression | 12 |
| rank_regression | 11 |
| core_improved | 10 |
| core_regressed | 10 |
| tail_rank_gt50_after_b | 4 |
| top5_lost | 3 |
| new_tail_rank_gt50 | 2 |
| protected_top10_regression | 1 |
| top10_lost | 1 |

## Hard fail reasons

- protected_top10_regression_nonzero
- target_top5_delta_negative
- rank_gt50_delta_positive
- mean_worst_suppress_gap_delta_negative
- mean_multi_pair_hinge_delta_positive

## Worst objective regressions

| case_id | rank_a | rank_b | prob_delta | worst_gap_delta | hinge_delta | outcome | tags |
|---|---:|---:|---:|---:|---:|---|---|
| legacy_g2_m5 | 4 | 8 | -0.013531 | -2.954720 | 1.405311 | severe_core_regression | top5_lost;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g5_m14 | 11 | 56 | -0.005814 | -2.449941 | 1.705355 | severe_core_regression | new_tail_rank_gt50;tail_rank_gt50_after_b;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g5_m8 | 2 | 5 | -0.081057 | -2.298124 | 1.506503 | severe_core_regression | rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g2_m21 | 39 | 51 | -0.000275 | -2.256331 | 1.477508 | severe_core_regression | new_tail_rank_gt50;tail_rank_gt50_after_b;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g4_m17 | 4 | 6 | -0.003598 | -2.165042 | 1.696744 | severe_core_regression | top5_lost;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g6_m19 | 6 | 6 | -0.028689 | -1.857393 | 1.111576 | mixed_or_regressed | prob_regression;worst_gap_regression;multi_pair_hinge_regression |
| legacy_g1_m40 | 3 | 3 | -0.130511 | -1.615253 | 0.617071 | mixed_or_regressed | prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression |
| legacy_g2_m11 | 12 | 20 | -0.000756 | -1.580258 | 1.715671 | severe_core_regression | rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g3_m4 | 11 | 16 | -0.004365 | -1.425894 | 0.220914 | severe_core_regression | rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g5_m12 | 69 | 106 | -0.000647 | -1.348132 | 1.639423 | severe_core_regression | tail_rank_gt50_after_b;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g3_m26 | 7 | 13 | -0.003749 | -1.279437 | 1.314304 | severe_core_regression | protected_top10_regression;top10_lost;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g5_m6 | 2 | 3 | -0.004857 | -0.848017 | 0.698181 | severe_core_regression | rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |

## Worst target ranks after Model B

| case_id | rank_a | rank_b | prob_a | prob_b | worst_gap_a | worst_gap_b | tags |
|---|---:|---:|---:|---:|---:|---:|---|
| legacy_g5_m12 | 69 | 106 | 0.00083295 | 0.00018624 | -6.156615 | -7.504747 | tail_rank_gt50_after_b;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g1_m8 | 102 | 75 | 0.00038893 | 0.00076429 | -6.780863 | -5.891213 | tail_rank_gt50_after_b;core_improved |
| legacy_g5_m14 | 11 | 56 | 0.00661942 | 0.00080527 | -4.123430 | -6.573371 | new_tail_rank_gt50;tail_rank_gt50_after_b;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g2_m21 | 39 | 51 | 0.00030841 | 0.00003364 | -7.981966 | -10.238297 | new_tail_rank_gt50;tail_rank_gt50_after_b;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g5_m30 | 53 | 48 | 0.00066022 | 0.00049970 | -6.481031 | -5.794907 | prob_regression |
| legacy_g2_m11 | 12 | 20 | 0.00094675 | 0.00019027 | -6.464814 | -8.045073 | rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g4_m13 | 28 | 18 | 0.00031777 | 0.00116715 | -7.411632 | -5.876796 | core_improved |
| legacy_g3_m4 | 11 | 16 | 0.00638845 | 0.00202391 | -4.635986 | -6.061881 | rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g6_m17 | 14 | 14 | 0.00403065 | 0.00565321 | -4.910375 | -3.790089 | core_improved |
| legacy_g3_m26 | 7 | 13 | 0.00514369 | 0.00139435 | -5.169128 | -6.448565 | protected_top10_regression;top10_lost;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g2_m5 | 4 | 8 | 0.01439602 | 0.00086503 | -4.068874 | -7.023594 | top5_lost;rank_regression;prob_regression;primary_gap_regression;worst_gap_regression;multi_pair_hinge_regression;core_regressed |
| legacy_g4_m23 | 21 | 8 | 0.00350194 | 0.00727156 | -4.536165 | -4.477715 | core_improved |

## Recommendation

Do not promote. Do not public benchmark. Next route should compare protected/anchor weighting, tail-row pruning, and objective weighting before any further b4c96 training.

## Final decision

`B4C96_STAGEC_FAILURE_FORENSICS_COMPLETE_NO_PROMOTION`
