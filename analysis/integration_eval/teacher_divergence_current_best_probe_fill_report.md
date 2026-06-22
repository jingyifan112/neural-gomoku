# Teacher-divergence current_best probe fill report

## Branch

`exp/15x15-teacher-divergence-current-best-probe-fill`

## Scope

- Fill current_best rank/prob/direct move only.
- Selected manifest rows with status `needs_current_best_probe`.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest.csv`
- checkpoint used for inference: `checkpoints/15x15_current_best.pt`
- selected rows: 14

## Summary

| metric | value |
|---|---:|
| rows selected | 14 |
| rows filled | 14 |
| target legal rows | 11 |

## Status after fill

| status_after | rows |
|---|---:|
| needs_suppress_build | 14 |

## Bucket after fill

| bucket_after | rows |
|---|---:|
| tail_rank_gt50 | 6 |
| protected_top10 | 3 |
| unknown_rank | 3 |
| trainable_rank_11_50 | 2 |

## Filled rows

| manifest_id | status_after | bucket_after | target_rc | rank | prob | direct_rc | notes |
|---|---|---|---|---:|---:|---|---|
| td_exp_00051 | needs_suppress_build | tail_rank_gt50 | `[5, 11]` | 101 | 8.819562935968861e-05 | `[7, 10]` | rank_prob_filled_but_suppress_missing |
| td_exp_00052 | needs_suppress_build | unknown_rank | `[8, 6]` | NA | 0.0 | `[6, 6]` | rank_prob_filled_but_suppress_missing |
| td_exp_00053 | needs_suppress_build | unknown_rank | `[8, 6]` | NA | 0.0 | `[4, 9]` | rank_prob_filled_but_suppress_missing |
| td_exp_00054 | needs_suppress_build | unknown_rank | `[10, 7]` | NA | 0.0 | `[10, 9]` | rank_prob_filled_but_suppress_missing |
| td_exp_00055 | needs_suppress_build | trainable_rank_11_50 | `[7, 9]` | 11 | 0.0021105546038597822 | `[10, 9]` | rank_prob_filled_but_suppress_missing |
| td_exp_00056 | needs_suppress_build | protected_top10 | `[10, 9]` | 1 | 0.37028923630714417 | `[10, 9]` | rank_prob_filled_but_suppress_missing |
| td_exp_00057 | needs_suppress_build | tail_rank_gt50 | `[8, 10]` | 56 | 7.451923011103645e-05 | `[10, 9]` | rank_prob_filled_but_suppress_missing |
| td_exp_00058 | needs_suppress_build | trainable_rank_11_50 | `[5, 8]` | 13 | 0.009368469938635826 | `[8, 8]` | rank_prob_filled_but_suppress_missing |
| td_exp_00059 | needs_suppress_build | protected_top10 | `[7, 10]` | 2 | 0.15224091708660126 | `[7, 4]` | rank_prob_filled_but_suppress_missing |
| td_exp_00060 | needs_suppress_build | protected_top10 | `[10, 7]` | 4 | 0.05512922629714012 | `[7, 4]` | rank_prob_filled_but_suppress_missing |
| td_exp_00061 | needs_suppress_build | tail_rank_gt50 | `[7, 9]` | 117 | 0.00024652446154505014 | `[7, 4]` | rank_prob_filled_but_suppress_missing |
| td_exp_00062 | needs_suppress_build | tail_rank_gt50 | `[4, 8]` | 147 | 4.618308139470173e-06 | `[7, 4]` | rank_prob_filled_but_suppress_missing |
| td_exp_00063 | needs_suppress_build | tail_rank_gt50 | `[7, 9]` | 96 | 0.0002625458873808384 | `[10, 7]` | rank_prob_filled_but_suppress_missing |
| td_exp_00064 | needs_suppress_build | tail_rank_gt50 | `[9, 10]` | 53 | 0.0014207102358341217 | `[5, 9]` | rank_prob_filled_but_suppress_missing |

## Interpretation

This branch only fills current_best policy diagnostics for rows that already had board, side, and target fields.

Rows that become `needs_suppress_build` are not ready for training yet. They need suppress candidates and suppress-gap diagnostics before any dataset build.

## Decision

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
