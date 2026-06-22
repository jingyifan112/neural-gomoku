# Teacher-divergence round2 trainable dry-run dataset export

## Branch

`exp/15x15-teacher-divergence-dryrun-dataset-export-round2`

## Scope

- Dry-run export only.
- Selects trainable `ready_full_schema` rows with `ready_bucket == trainable_rank_11_50`.
- Requires target rank/prob and suppress fields.
- Excludes protected top10 rows from training export.
- Excludes tail rank > 50 rows from training export.
- Excludes legacy trainable rows that need suppress schema normalization.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Input

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv`

## Summary

| metric | value |
|---|---:|
| total trainable ready rows | 44 |
| exportable dry-run samples | 35 |
| legacy rows needing schema normalization | 9 |

## Source counts in dry-run samples

| source | rows |
|---|---:|
| retention_candidate_dataset | 18 |
| retention_metadata_manifest | 10 |
| corpus8_teacher_candidate_csv | 7 |

## Round2 action counts in dry-run samples

| action | rows |
|---|---:|
| probe_and_suppress_built | 35 |

## Suppress candidate count distribution

| suppress candidate count | rows |
|---|---:|
| 5 | 35 |

## Target rank distribution

| target rank | rows |
|---|---:|
| 14 | 6 |
| 18 | 5 |
| 23 | 7 |
| 39 | 5 |
| 43 | 6 |
| 47 | 6 |

## Legacy trainable rows excluded from dry-run export

| manifest_id | source_class | case_id | reason |
|---|---|---|---|
| td_exp_00008 | canonical_full_schema_seed | legacy_g2_m11 | missing suppress fields in merged manifest |
| td_exp_00009 | canonical_full_schema_seed | legacy_g2_m21 | missing suppress fields in merged manifest |
| td_exp_00013 | canonical_full_schema_seed | legacy_g4_m13 | missing suppress fields in merged manifest |
| td_exp_00015 | canonical_full_schema_seed | legacy_g4_m23 | missing suppress fields in merged manifest |
| td_exp_00019 | canonical_full_schema_seed | legacy_g5_m14 | missing suppress fields in merged manifest |
| td_exp_00021 | canonical_full_schema_seed | legacy_g5_m28 | missing suppress fields in merged manifest |
| td_exp_00024 | canonical_full_schema_seed | legacy_g6_m17 | missing suppress fields in merged manifest |
| td_exp_00055 | retention_candidate_dataset | holdout_candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10 | missing suppress fields in merged manifest |
| td_exp_00058 | retention_candidate_dataset | holdout_candidate_e_g2_m13_white_target_5_8_over_8_8 | missing suppress fields in merged manifest |

## Output

- `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset.json`
- `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_report.md`

## Decision

This is a schema-validation dry run only.

Do not train yet.

Before training, either normalize the 9 legacy trainable rows or deliberately train only on the 35 round2 exportable samples.

No checkpoint.

No C export.

No public benchmark.

No promotion.
