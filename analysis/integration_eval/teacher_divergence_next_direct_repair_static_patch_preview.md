# 15x15 teacher-divergence next direct repair static patch preview

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-preview`

## Purpose

Create a static-only patch preview for the one direct repair-queue row.

This branch does not modify manifest data, train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, or overwrite current-best.

## Upstream

| Field | Value |
|---|---|
| upstream_plan_decision | `DIRECT_REPAIR_STATIC_PATCH_PLAN_READY` |
| specific_issue_candidate_count | `18` |
| top_static_candidate_count | `12` |

## Preview confidence counts

| Confidence | Count |
|---|---:|
| HIGH | 11 |
| MEDIUM | 3 |
| LOW | 4 |

## Selected candidate preview

| Field | Value |
|---|---|
| candidate_index | `4` |
| source_file | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` |
| location | `6` |
| patch_preview_confidence | `HIGH` |
| row_like_keys | `schema_keys` |
| field_like_keys | `schema_status, provenance_status, clean_source_tokens` |
| has_before_after_terms | `True` |
| has_missing_invalid_terms | `False` |

## Ranked candidate preview

| # | Source | Location | Confidence | Row-like keys | Field-like keys |
|---:|---|---|---|---|---|
| 4 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 6 | `HIGH` | schema_keys | schema_status, provenance_status, clean_source_tokens |
| 5 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 7 | `HIGH` | schema_keys | schema_status, provenance_status, clean_source_tokens |
| 6 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 8 | `HIGH` | schema_keys | schema_status, provenance_status, clean_source_tokens |
| 7 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 9 | `HIGH` | schema_keys | schema_status, provenance_status, clean_source_tokens |
| 8 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 10 | `HIGH` | schema_keys | schema_status, provenance_status, clean_source_tokens |
| 9 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 11 | `HIGH` | schema_keys | schema_status, provenance_status, clean_source_tokens |
| 14 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 6 | `HIGH` | quarantine_id, source_manifest_row_id, source_eval_manifest_id | source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, quarantine_reason |
| 15 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 7 | `HIGH` | quarantine_id, source_manifest_row_id, source_eval_manifest_id | source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, quarantine_reason |
| 16 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_repair_queue.csv` | 2 | `HIGH` | repair_queue_id, source_manifest_row_id, source_eval_manifest_id | repair_queue_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, repair_status |
| 17 | `analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_pending.csv` | 2 | `HIGH` | pending_id, source_repair_queue_id, source_manifest_row_id, source_eval_manifest_id | source_repair_queue_id, source_manifest_row_id, source_eval_manifest_id, source_path, schema_status, provenance_status, pending_reasons |
| 18 | `analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_rows.csv` | 2 | `HIGH` | repair_queue_id, source_manifest_row_id, source_eval_manifest_id, candidate_reasons | repair_queue_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, source_path_exists, schema_status, provenance_status, inspection_clean_source_tokens, repair_review_decision, repair_review_bucket, candidate_reasons, pending_reasons, quarantine_reasons |
| 1 | `analysis/integration_eval/teacher_divergence_next_direct_repair_materialization_dryrun.json` | $ | `MEDIUM` |  | source_state |
| 2 | `analysis/integration_eval/teacher_divergence_next_direct_repair_materialization_dryrun.json` | $.materialized_buckets[1] | `MEDIUM` |  | dryrun_status |
| 3 | `analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_decision.json` | $ | `MEDIUM` | row_counts | repair_queue_review_decision |
| 10 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 2 | `LOW` | quarantine_id, source_manifest_row_id, source_eval_manifest_id | source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, quarantine_reason |
| 11 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 3 | `LOW` | quarantine_id, source_manifest_row_id, source_eval_manifest_id | source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, quarantine_reason |
| 12 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 4 | `LOW` | quarantine_id, source_manifest_row_id, source_eval_manifest_id | source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, quarantine_reason |
| 13 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 5 | `LOW` | quarantine_id, source_manifest_row_id, source_eval_manifest_id | source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, quarantine_reason |

## Safety permissions

| Permission | Allowed now |
|---|---:|
| training_allowed_now | 0 |
| model_eval_allowed_now | 0 |
| checkpoint_read_allowed_now | 0 |
| checkpoint_write_allowed_now | 0 |
| c_export_allowed_now | 0 |
| public_benchmark_allowed_now | 0 |
| promotion_allowed_now | 0 |
| current_best_overwrite_allowed_now | 0 |
| manifest_patch_allowed_in_this_branch | 0 |

## Acceptance checks

| Check | Result |
|---|---|
| static_only_preview_created | PASS |
| does_not_modify_manifest_data | PASS |
| does_not_train | PASS |
| does_not_run_model_eval | PASS |
| does_not_read_checkpoint_content | PASS |
| does_not_write_checkpoints | PASS |
| does_not_export_c | PASS |
| does_not_run_public_benchmark | PASS |
| does_not_promote | PASS |
| does_not_overwrite_current_best | PASS |

## Interpretation

At least one candidate appears to contain row-like, field-like, and before/after evidence. A later explicit patch branch may apply a static metadata patch after reviewing the selected candidate.

## Preview decision

`DIRECT_REPAIR_STATIC_PATCH_PREVIEW_READY_FOR_EXPLICIT_PATCH_BRANCH`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-apply`

## Promotion decision

`NO_PROMOTION__STATIC_PATCH_PREVIEW_ONLY`
