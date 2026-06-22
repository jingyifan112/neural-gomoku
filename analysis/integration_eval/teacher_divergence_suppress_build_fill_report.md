# Teacher-divergence suppress build fill report

## Branch

`exp/15x15-teacher-divergence-suppress-build-fill`

## Scope

- Build suppress candidates only.
- Input is current_best probe fill output.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- probe_fill_csv: `analysis/integration_eval/teacher_divergence_current_best_probe_fill.csv`
- max_suppress: 5
- min_suppress: 3
- input rows: 14

## Summary

| metric | value |
|---|---:|
| input rows | 14 |
| output rows | 14 |
| eligible non-excluded rows | 11 |
| excluded rows | 3 |
| ready_full_schema rows | 11 |

## Status after suppress build

| status_after | rows |
|---|---:|
| ready_full_schema | 11 |
| excluded_target_illegal | 3 |

## Bucket counts for ready rows

| bucket_after | rows |
|---|---:|
| tail_rank_gt50 | 6 |
| protected_top10 | 3 |
| trainable_rank_11_50 | 2 |

## Exclusion reasons

| exclude_reason | rows |
|---|---:|
| target_illegal_or_unknown_rank | 3 |

## Output rows

| manifest_id | status_after | bucket_after | target_rc | suppress_count | primary_suppress_rc | excluded | reason |
|---|---|---|---|---:|---|---:|---|
| td_exp_00051 | ready_full_schema | tail_rank_gt50 | `[5, 11]` | 5 | `[7, 10]` | 0 |  |
| td_exp_00052 | excluded_target_illegal | unknown_rank | `[8, 6]` | 5 | `[6, 6]` | 1 | target_illegal_or_unknown_rank |
| td_exp_00053 | excluded_target_illegal | unknown_rank | `[8, 6]` | 5 | `[4, 9]` | 1 | target_illegal_or_unknown_rank |
| td_exp_00054 | excluded_target_illegal | unknown_rank | `[10, 7]` | 5 | `[10, 9]` | 1 | target_illegal_or_unknown_rank |
| td_exp_00055 | ready_full_schema | trainable_rank_11_50 | `[7, 9]` | 5 | `[10, 9]` | 0 |  |
| td_exp_00056 | ready_full_schema | protected_top10 | `[10, 9]` | 5 | `[9, 7]` | 0 |  |
| td_exp_00057 | ready_full_schema | tail_rank_gt50 | `[8, 10]` | 5 | `[10, 9]` | 0 |  |
| td_exp_00058 | ready_full_schema | trainable_rank_11_50 | `[5, 8]` | 5 | `[8, 8]` | 0 |  |
| td_exp_00059 | ready_full_schema | protected_top10 | `[7, 10]` | 5 | `[7, 4]` | 0 |  |
| td_exp_00060 | ready_full_schema | protected_top10 | `[10, 7]` | 5 | `[7, 4]` | 0 |  |
| td_exp_00061 | ready_full_schema | tail_rank_gt50 | `[7, 9]` | 5 | `[7, 4]` | 0 |  |
| td_exp_00062 | ready_full_schema | tail_rank_gt50 | `[4, 8]` | 5 | `[7, 4]` | 0 |  |
| td_exp_00063 | ready_full_schema | tail_rank_gt50 | `[7, 9]` | 5 | `[10, 7]` | 0 |  |
| td_exp_00064 | ready_full_schema | tail_rank_gt50 | `[9, 10]` | 5 | `[5, 9]` | 0 |  |

## Interpretation

This branch only fills suppress candidates from current_best top policy moves.

Rows marked `ready_full_schema` are ready for diagnostics, not training. They should be merged into an updated manifest only after a separate manifest update branch.

Protected top10 rows remain eval/protection only. Tail rank_gt50 rows remain diagnostic-only. The trainable rank 11-50 bucket is still far below the minimum sample count for training.

## Decision

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
