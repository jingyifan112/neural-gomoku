# Teacher-divergence round2 trainable dry-run export after legacy normalization

## Branch

`exp/15x15-teacher-divergence-legacy-suppress-manifest-update`

## Scope

- Dry-run export only.
- Uses the legacy-normalized manifest.
- Selects `status == ready_full_schema` and `ready_bucket == trainable_rank_11_50`.
- Requires target rank/prob and suppress fields.
- Expects all 44 trainable rows to be export-schema-complete.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Input

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv`

## Summary

| metric | value |
|---|---:|
| ready trainable rows | 44 |
| exportable dry-run samples | 44 |
| excluded rows | 0 |

## Legacy normalization split

| group | rows |
|---|---:|
| round2_or_existing | 35 |
| legacy_normalized | 9 |

## Source counts

| source | rows |
|---|---:|
| retention_candidate_dataset | 20 |
| retention_metadata_manifest | 10 |
| canonical_full_schema_seed | 7 |
| corpus8_teacher_candidate_csv | 7 |

## Suppress candidate count distribution

| suppress candidate count | rows |
|---|---:|
| 5 | 44 |

## Target rank distribution

| target rank | rows |
|---|---:|
| 11 | 1 |
| 12 | 1 |
| 13 | 1 |
| 14 | 6 |
| 15 | 1 |
| 17 | 2 |
| 18 | 5 |
| 21 | 1 |
| 23 | 8 |
| 39 | 5 |
| 43 | 6 |
| 47 | 7 |

## Outputs

- `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset_legacy_normalized.json`
- `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_legacy_normalized_report.md`

## Decision

The 44-row trainable dry-run dataset validates after legacy normalization.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
