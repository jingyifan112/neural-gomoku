# Teacher-divergence legacy trainable suppress fill report

## Branch

`exp/15x15-teacher-divergence-legacy-trainable-probe-fill`

## Scope

- Builds suppress candidates only for legal legacy trainable probe rows.
- Input is legacy trainable current_best probe fill CSV.
- Does not process round2 already-exportable rows.
- Does not process protected top10 rows.
- Does not process tail rank > 50 rows.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- legacy probe fill CSV: `analysis/integration_eval/teacher_divergence_legacy_trainable_current_best_probe_fill.csv`
- selected legal rows: 9
- max suppress candidates per row: 5

## Summary

| metric | value |
|---|---:|
| selected needs_suppress_build rows | 9 |
| output rows | 9 |
| ready_full_schema rows | 9 |
| suppress repair rows | 0 |

## Status after suppress fill

| status_after | rows |
|---|---:|
| ready_full_schema | 9 |

## Bucket after suppress fill

| bucket_after | rows |
|---|---:|
| trainable_rank_11_50 | 9 |

## Suppress count distribution

| suppress_count | rows |
|---|---:|
| 5 | 9 |

## Notes distribution

| notes | rows |
|---|---:|
| suppress_candidates_built_trainable_rank_11_50 | 9 |

## Row preview

| manifest_id | bucket_after | target_rc | target_rank | target_prob | suppress_rc | suppress_rank | suppress_prob | status_after | notes |
|---|---|---|---:|---:|---|---:|---:|---|---|
| td_exp_00008 | trainable_rank_11_50 | `[7, 9]` | 12 | 0.00032454601023346186 | `[5, 6]` | 1 | 0.4221777617931366 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00009 | trainable_rank_11_50 | `[9, 7]` | 47 | 0.00014416118210647255 | `[4, 2]` | 1 | 0.9029175639152527 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00013 | trainable_rank_11_50 | `[6, 9]` | 21 | 0.00024367567675653845 | `[4, 6]` | 1 | 0.4877963662147522 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00015 | trainable_rank_11_50 | `[9, 7]` | 23 | 0.001522314501926303 | `[3, 7]` | 1 | 0.44126200675964355 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00019 | trainable_rank_11_50 | `[9, 7]` | 17 | 0.0019402344478294253 | `[6, 6]` | 1 | 0.47136619687080383 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00021 | trainable_rank_11_50 | `[11, 5]` | 17 | 0.0036502990406006575 | `[4, 5]` | 1 | 0.38212400674819946 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00024 | trainable_rank_11_50 | `[6, 8]` | 15 | 0.0027031409554183483 | `[9, 4]` | 1 | 0.5200085639953613 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00055 | trainable_rank_11_50 | `[7, 9]` | 11 | 0.0021105546038597822 | `[10, 9]` | 1 | 0.37028923630714417 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00058 | trainable_rank_11_50 | `[5, 8]` | 13 | 0.009368469938635826 | `[8, 8]` | 1 | 0.3607815206050873 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |

## Decision

Use these rows in a later manifest normalization update only if all selected rows are ready_full_schema.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
