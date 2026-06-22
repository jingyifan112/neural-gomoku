# Teacher-divergence manifest update with suppress round2

## Branch

`exp/15x15-teacher-divergence-manifest-update-with-suppress-round2`

## Scope

- Merge current_best probe fill round2 into manifest.
- Merge suppress build fill round2 into manifest.
- Convert legal probed rows with suppress candidates to `ready_full_schema`.
- Convert illegal target rows to `skipped_invalid`.
- Does not process `needs_rapfi_requery` rows.
- Does not process `needs_board_join` rows.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins.csv`
- probe fill CSV: `analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2.csv`
- suppress fill CSV: `analysis/integration_eval/teacher_divergence_suppress_build_fill_round2.csv`

## Action counts

| action | rows |
|---|---:|
| unchanged | 222 |
| probe_and_suppress_built | 97 |
| probe_target_illegal_skipped | 43 |

## Non-duplicate status counts before

| status | rows |
|---|---:|
| needs_current_best_probe | 140 |
| needs_board_join | 41 |
| ready_full_schema | 36 |
| needs_rapfi_requery | 22 |
| skipped_invalid | 8 |

## Non-duplicate status counts after

| status | rows |
|---|---:|
| ready_full_schema | 133 |
| skipped_invalid | 51 |
| needs_board_join | 41 |
| needs_rapfi_requery | 22 |

## Ready bucket counts before

| ready_bucket | rows |
|---|---:|
| protected_top10 | 18 |
| tail_rank_gt50 | 9 |
| trainable_rank_11_50 | 9 |

## Ready bucket counts after

| ready_bucket | rows |
|---|---:|
| tail_rank_gt50 | 66 |
| trainable_rank_11_50 | 44 |
| protected_top10 | 23 |

## Expected after-checks

| status | expected | actual |
|---|---:|---:|
| ready_full_schema | 133 | 133 |
| skipped_invalid | 51 | 51 |
| needs_current_best_probe | 0 | 0 |
| needs_rapfi_requery | 22 | 22 |
| needs_board_join | 41 | 41 |

## Outputs

- `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv`
- `analysis/integration_eval/teacher_divergence_manifest_update_with_suppress_round2_report.md`

## Decision

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
