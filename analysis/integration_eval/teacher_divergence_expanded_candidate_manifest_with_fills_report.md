# Teacher-divergence expanded manifest with fills report

## Branch

`exp/15x15-teacher-divergence-manifest-update-with-fills`

## Scope

- Manifest update only.
- Merges current_best probe fill and suppress build fill outputs.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- base manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest.csv`
- probe fill: `analysis/integration_eval/teacher_divergence_current_best_probe_fill.csv`
- suppress fill: `analysis/integration_eval/teacher_divergence_suppress_build_fill.csv`

## Update summary

| metric | value |
|---|---:|
| total manifest rows | 362 |
| non-duplicate rows | 247 |
| update actions | 14 |
| promoted ready_full_schema | 11 |
| excluded/skipped invalid | 3 |

## Status counts before

| status | rows |
|---|---:|
| needs_board_join | 203 |
| duplicate | 115 |
| ready_full_schema | 25 |
| needs_current_best_probe | 14 |
| skipped_invalid | 5 |

## Status counts after

| status | rows |
|---|---:|
| needs_board_join | 203 |
| duplicate | 115 |
| ready_full_schema | 36 |
| skipped_invalid | 8 |

## Bucket counts after for non-duplicate rows

| bucket | rows |
|---|---:|
| unknown_rank | 211 |
| protected_top10 | 18 |
| tail_rank_gt50 | 9 |
| trainable_rank_11_50 | 9 |

## Ready full-schema bucket counts after

| bucket | rows |
|---|---:|
| protected_top10 | 18 |
| tail_rank_gt50 | 9 |
| trainable_rank_11_50 | 9 |

## Update actions

| action | rows |
|---|---:|
| promoted_ready_full_schema | 11 |
| excluded_skipped_invalid | 3 |

## Interpretation

The current_best probe fill and suppress build fill have been merged into an updated manifest.

This increases ready_full_schema rows for diagnostics, but it does not create a training dataset.

Protected top10 rows remain eval/protection only. Tail rank_gt50 rows remain diagnostic-only. The trainable rank 11-50 bucket is still far below the minimum sample target for training.

## Decision

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
