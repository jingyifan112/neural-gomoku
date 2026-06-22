# Teacher-divergence expanded candidate manifest report

## Branch

`exp/15x15-teacher-divergence-expanded-manifest-builder`

## Scope

- Manifest builder only.
- Selected tracked sources only.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Source rows loaded

| source | rows_loaded |
|---|---:|
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json` | 25 |
| `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json` | 44 |
| `analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json` | 39 |
| `analysis/integration_eval/teacher_divergence_retention_dataset.json` | 36 |
| `analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv` | 109 |
| `analysis/integration_eval/teacher_divergence_retention_manifest.csv` | 52 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv` | 32 |

## Manifest summary

| metric | value |
|---|---:|
| total manifest rows | 362 |
| non-duplicate rows | 247 |
| duplicate rows | 115 |
| board_available rows | 39 |
| side_available rows | 247 |
| target_available rows | 242 |
| teacher_eval_available rows | 195 |
| rank_prob_available rows | 25 |
| suppress_available rows | 25 |

## Status counts

| status | rows |
|---|---:|
| needs_board_join | 203 |
| duplicate | 115 |
| ready_full_schema | 25 |
| needs_current_best_probe | 14 |
| skipped_invalid | 5 |

## Bucket counts for non-duplicate rows

| bucket | rows |
|---|---:|
| unknown_rank | 222 |
| protected_top10 | 15 |
| trainable_rank_11_50 | 7 |
| tail_rank_gt50 | 3 |

## Source class counts for non-duplicate rows

| source_class | rows |
|---|---:|
| retention_metadata_manifest | 96 |
| retention_candidate_dataset | 94 |
| corpus8_teacher_candidate_csv | 32 |
| canonical_full_schema_seed | 25 |

## Interpretation

This manifest is a candidate inventory, not a training dataset.

Rows marked `ready_full_schema` are immediately usable for diagnostics. Rows marked `needs_current_best_probe`, `needs_suppress_build`, `needs_rapfi_requery`, or `needs_board_join` require additional processing before they can feed any training dataset.

Duplicate rows are retained with `duplicate_of` pointers so source overlap remains auditable.

## Decision

No training should run from this branch.

The next branch should inspect the manifest and decide which missing-field fill step comes first.

Likely next step: current_best rank/prob probe for non-duplicate rows with board, side, and target but missing rank/prob.
