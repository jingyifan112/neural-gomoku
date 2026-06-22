# Teacher-divergence legacy trainable current_best probe fill

## Branch

`exp/15x15-teacher-divergence-legacy-trainable-probe-fill`

## Scope

- Runs current_best policy probe only for 9 legacy trainable rows missing suppress schema fields.
- Does not process round2 already-exportable rows.
- Does not process protected top10 rows.
- Does not process tail rank > 50 rows.
- Does not process needs_rapfi_requery rows.
- Does not process needs_board_join rows.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv`
- normalization plan CSV: `analysis/integration_eval/teacher_divergence_legacy_trainable_normalization_plan.csv`
- checkpoint used for inference: `checkpoints/15x15_current_best.pt`
- board source records indexed by hash: 196

## Summary

| metric | value |
|---|---:|
| selected legacy rows | 9 |
| legal target rows | 9 |
| illegal target rows | 0 |

## Status after probe

| status_after | rows |
|---|---:|
| needs_suppress_build | 9 |

## Bucket after probe

| bucket_after | rows |
|---|---:|
| trainable_rank_11_50 | 9 |

## Row preview

| manifest_id | status_after | bucket_after | target_rc | rank | prob | direct_rc | excluded | notes |
|---|---|---|---|---:|---:|---|---:|---|
| td_exp_00008 | needs_suppress_build | trainable_rank_11_50 | `[7, 9]` | 12 | 0.00032454601023346186 | `[5, 6]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |
| td_exp_00009 | needs_suppress_build | trainable_rank_11_50 | `[9, 7]` | 47 | 0.00014416118210647255 | `[4, 2]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |
| td_exp_00013 | needs_suppress_build | trainable_rank_11_50 | `[6, 9]` | 21 | 0.00024367567675653845 | `[4, 6]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |
| td_exp_00015 | needs_suppress_build | trainable_rank_11_50 | `[9, 7]` | 23 | 0.001522314501926303 | `[3, 7]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |
| td_exp_00019 | needs_suppress_build | trainable_rank_11_50 | `[9, 7]` | 17 | 0.0019402344478294253 | `[6, 6]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |
| td_exp_00021 | needs_suppress_build | trainable_rank_11_50 | `[11, 5]` | 17 | 0.0036502990406006575 | `[4, 5]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |
| td_exp_00024 | needs_suppress_build | trainable_rank_11_50 | `[6, 8]` | 15 | 0.0027031409554183483 | `[9, 4]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |
| td_exp_00055 | needs_suppress_build | trainable_rank_11_50 | `[7, 9]` | 11 | 0.0021105546038597822 | `[10, 9]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |
| td_exp_00058 | needs_suppress_build | trainable_rank_11_50 | `[5, 8]` | 13 | 0.009368469938635826 | `[8, 8]` | 0 | legacy_rank_prob_refilled_but_suppress_missing |

## Decision

Continue to suppress build only for legal rows from this CSV.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
