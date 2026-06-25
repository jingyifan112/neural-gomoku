# Teacher-divergence expansion source audit next

## Scope

- Source audit only.
- No dataset build.
- No training.
- No checkpoint read or write.
- No C export, no public benchmark, no promotion.

## Upstream decisions

- expansion targets: `TEACHER_DIVERGENCE_EXPANSION_TARGETS_READY`
- row-level guard review: `LEAVE_ONE_OUT_NO_GUARD_SAFE_SUBSET`

## Source status

| source | exists | loaded_rows |
|---|---:|---:|
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | True | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json` | True | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json` | True | 25 |
| `analysis/integration_eval/teacher_divergence_data_inventory_manifest.csv` | True | 289 |
| `analysis/integration_eval/teacher_divergence_data_inventory.json` | True | 0 |
| `analysis/integration_eval/teacher_divergence_expansion_candidate_manifest.csv` | True | 0 |
| `analysis/integration_eval/teacher_divergence_expansion_source_audit.csv` | True | 36 |
| `analysis/integration_eval/teacher_divergence_expansion_source_audit.json` | True | 0 |
| `analysis/integration_eval/teacher_divergence_retention_expanded_manifest.csv` | True | 233 |
| `analysis/integration_eval/teacher_divergence_retention_expanded_dataset.json` | True | 71 |
| `analysis/integration_eval/teacher_divergence_retention_expanded_source_audit.json` | True | 0 |
| `analysis/integration_eval/teacher_divergence_source_schema_audit.json` | True | 9 |

## Candidate buckets

| bucket | unique case_ids | minimum target | gap |
|---|---:|---:|---:|
| P0_tail_guard_candidate | 0 | 12 | 12 |
| P0_protected_guard_candidate | 13 | 12 | 0 |
| P1_train_candidate | 15 | 20 | 5 |

## Other buckets

| bucket | unique case_ids |
|---|---:|
| already_selected_or_guarded | 25 |
| quarantine_or_negative_example | 2 |
| unclassified_review | 599 |

## Decision

`EXPANSION_SOURCE_AUDIT_HAS_PARTIAL_CANDIDATES`

Available source artifacts contain some candidate rows but do not satisfy all minimum targets.

Next step should either expand source generation further or build a review manifest for the partial candidates while clearly tracking remaining gaps.

## Final note

This audit does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
