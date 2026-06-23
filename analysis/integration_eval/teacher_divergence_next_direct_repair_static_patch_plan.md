# 15x15 teacher-divergence next direct repair static patch plan

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-plan`

## Purpose

Create a static-only patch plan for the one direct repair-queue row.

This branch does not modify manifest data, train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, or overwrite current-best.

## Upstream route

| Field | Value |
|---|---|
| route_decision | `ROUTE_TO_STATIC_PATCH_PLAN` |
| selected_next_branch | `exp/15x15-teacher-divergence-next-direct-repair-static-patch-plan` |
| field_spec_decision | `DIRECT_REPAIR_FIELD_SPEC_STATIC_CANDIDATES_FOUND` |

## Field-spec scan summary

| Metric | Value |
|---|---:|
| tracked_files_scanned | 75 |
| json_marker_candidates | 33 |
| csv_marker_candidates | 33 |
| markdown_marker_hits | 65 |
| specific_issue_candidates | 18 |
| specific_issue_candidate_count | 18 |

## Static candidate evidence preview

| # | Source | Location | Evidence keys |
|---:|---|---|---|
| 1 | `analysis/integration_eval/teacher_divergence_next_direct_repair_materialization_dryrun.json` | $ | acceptance_checks, branch, dryrun_decision, execution_permissions, materialized_buckets, promotion_decision, purpose, recommended_next_branch, source_state, upstream_branch |
| 2 | `analysis/integration_eval/teacher_divergence_next_direct_repair_materialization_dryrun.json` | $.materialized_buckets[1] | allowed_next_handling, bucket, checkpoint_read_allowed_now, dryrun_status, eval_allowed_now |
| 3 | `analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_decision.json` | $ | normalization_decision, outputs, recommended_next, repair_queue_review_decision, row_counts, warnings |
| 4 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 6 | clean_source_tokens, provenance_status, recommended_action, schema_keys, schema_status |
| 5 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 7 | clean_source_tokens, provenance_status, recommended_action, schema_keys, schema_status |
| 6 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 8 | clean_source_tokens, provenance_status, recommended_action, schema_keys, schema_status |
| 7 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 9 | clean_source_tokens, provenance_status, recommended_action, schema_keys, schema_status |
| 8 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 10 | clean_source_tokens, provenance_status, recommended_action, schema_keys, schema_status |
| 9 | `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 11 | clean_source_tokens, provenance_status, recommended_action, schema_keys, schema_status |
| 10 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 2 | eval_allowed_now, provenance_status, quarantine_id, quarantine_reason, recommended_action, schema_status, source_adapter_kind, source_eval_manifest_id, source_manifest_row_id, source_path |
| 11 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 3 | eval_allowed_now, provenance_status, quarantine_id, quarantine_reason, recommended_action, schema_status, source_adapter_kind, source_eval_manifest_id, source_manifest_row_id, source_path |
| 12 | `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 4 | eval_allowed_now, provenance_status, quarantine_id, quarantine_reason, recommended_action, schema_status, source_adapter_kind, source_eval_manifest_id, source_manifest_row_id, source_path |

## Patch plan

| Step | Name | Allowed in this branch | Description |
|---:|---|---|---|
| 1 | Identify the repair row from static candidate evidence | YES | Use tracked static artifacts only to identify the one repair-queue row and its exact metadata inconsistency. |
| 2 | Name the exact field | YES | Record the field name, current value, proposed repaired value, and source artifact. |
| 3 | Create a patch preview artifact | YES | Create a dry-run patch preview showing before/after metadata without modifying training inputs or checkpoint files. |
| 4 | Apply static patch | NO | Do not apply the actual manifest/data patch in this branch. Reserve it for a later explicit static patch branch. |
| 5 | Evaluate or train | NO | No model evaluation, checkpoint reading, training, C export, benchmark, promotion, or current-best overwrite is allowed. |

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
| route_is_static_patch_plan | PASS |
| has_specific_issue_candidates | PASS |
| static_only_plan_created | PASS |
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

The safe next action is not to patch the manifest immediately. The safe next action is a static patch preview branch that names the exact row and field before any data mutation is allowed.

The repair path remains isolated from training, model evaluation, checkpoint reading, C export, public benchmark, promotion, and current-best overwrite.

## Decision

`DIRECT_REPAIR_STATIC_PATCH_PLAN_READY`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-preview`

## Promotion decision

`NO_PROMOTION__STATIC_PATCH_PLAN_ONLY`
