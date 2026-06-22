# Teacher-divergence round2 readiness audit

## Branch

`exp/15x15-teacher-divergence-round2-readiness-audit`

## Scope

- Audits the manifest after current_best probe round2 and suppress build round2.
- Does not build a training dataset.
- Does not train.
- Does not save a checkpoint.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Input

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv`

## Core counts

| metric | value |
|---|---:|
| manifest rows | 362 |
| non-duplicate rows | 247 |
| ready_full_schema rows | 133 |
| trainable candidate rows | 44 |
| protected top10 rows | 23 |
| tail diagnostic rows | 66 |
| ready rows missing rank/prob | 0 |
| ready rows missing suppress fields | 36 |
| round2 ready rows missing suppress fields | 0 |
| pre-round2 ready rows missing suppress fields | 36 |

## Readiness interpretation

- `trainable_rank_11_50` rows are the only immediate candidates for a later dry-run dataset export.
- `protected_top10` rows should remain protection/eval rows unless a later design deliberately includes them.
- `tail_rank_gt50` rows should remain diagnostic-only for now because target visibility is too low.
- `needs_rapfi_requery` and `needs_board_join` remain unresolved and are not included in readiness.

## Non-duplicate status counts

| status | rows |
|---|---:|
| ready_full_schema | 133 |
| skipped_invalid | 51 |
| needs_board_join | 41 |
| needs_rapfi_requery | 22 |

## Ready bucket counts

| ready_bucket | rows | intended use |
|---|---:|---|
| trainable_rank_11_50 | 44 | dry-run export candidate |
| protected_top10 | 23 | protection/eval only |
| tail_rank_gt50 | 66 | diagnostic only |

## Expected count checks

| check | expected | actual |
|---|---:|---:|
| status:ready_full_schema | 133 | 133 |
| status:skipped_invalid | 51 | 51 |
| status:needs_rapfi_requery | 22 | 22 |
| status:needs_board_join | 41 | 41 |
| status:needs_current_best_probe | 0 | 0 |
| ready_bucket:protected_top10 | 23 | 23 |
| ready_bucket:trainable_rank_11_50 | 44 | 44 |
| ready_bucket:tail_rank_gt50 | 66 | 66 |

## Round2 merge action counts

| key | rows |
|---|---:|
| pre_round2_or_unchanged | 222 |
| probe_and_suppress_built | 97 |
| probe_target_illegal_skipped | 43 |

## Ready source counts

| key | rows |
|---|---:|
| retention_candidate_dataset | 63 |
| retention_metadata_manifest | 27 |
| canonical_full_schema_seed | 25 |
| corpus8_teacher_candidate_csv | 18 |

## Trainable candidate source counts

| key | rows |
|---|---:|
| retention_candidate_dataset | 20 |
| retention_metadata_manifest | 10 |
| canonical_full_schema_seed | 7 |
| corpus8_teacher_candidate_csv | 7 |

## Trainable candidate family counts

| key | rows |
|---|---:|
| legacy_game_family | 25 |
| teacher_divergence_retention_clean_v2_manifest | 7 |
| rapfi_teacher_policy_candidates_corpus8_selected | 7 |
| teacher_divergence_retention_manifest | 3 |
| candidate_family | 2 |

## Protected source counts

| key | rows |
|---|---:|
| canonical_full_schema_seed | 15 |
| retention_candidate_dataset | 6 |
| retention_metadata_manifest | 1 |
| corpus8_teacher_candidate_csv | 1 |

## Tail diagnostic source counts

| key | rows |
|---|---:|
| retention_candidate_dataset | 37 |
| retention_metadata_manifest | 16 |
| corpus8_teacher_candidate_csv | 10 |
| canonical_full_schema_seed | 3 |

## Recommended next step

Create a dry-run dataset export plan that selects only `ready_full_schema` rows with `ready_bucket == trainable_rank_11_50`, while keeping protected and tail rows out of training.

Before actual training, run one more dataset export dry-run and schema validation.

## Outputs

- `analysis/integration_eval/teacher_divergence_round2_readiness_audit.md`
- `analysis/integration_eval/teacher_divergence_round2_readiness_summary.csv`

## Decision

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
