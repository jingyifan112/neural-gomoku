# 15x15 teacher-divergence next direct repair static patch apply

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-apply`

## Purpose

Apply the direct repair patch as a derived static artifact only.

This branch does not overwrite original manifest artifacts, train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, or overwrite current-best.

## Upstream

| Field | Value |
|---|---|
| upstream_preview_decision | `DIRECT_REPAIR_STATIC_PATCH_PREVIEW_READY_FOR_EXPLICIT_PATCH_BRANCH` |
| patch_apply_mode | `derived_artifact_only` |

## Source row identity

| Field | Value |
|---|---|
| repair_queue_id | `direct_repair_001` |
| source_repair_queue_id | `direct_repair_001` |
| source_manifest_row_id | `1` |
| source_eval_manifest_id | `run1_direct_probe_eval_001` |
| source_adapter_kind | `direct_model_eval_fixed_probe_candidate` |
| source_path | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` |

## Source row evidence

| Field | Value |
|---|---|
| source_path_exists | `1` |
| schema_status | `HAS_CONTEXT_BUT_NEEDS_REVIEW` |
| provenance_status | `CLEAN_HELDOUT_OR_DIRECT_SOURCE` |
| inspection_clean_source_tokens | `fixed_probe,direct_probe` |
| repair_review_decision | `REPAIR_ROW_MANUAL_REVIEW` |
| repair_review_bucket | `pending` |
| candidate_reasons | `` |
| pending_reasons | `` |
| quarantine_reasons | `` |

## Derived patch

| Field | Value |
|---|---|
| applied_to_original_manifest | `False` |
| applied_to_derived_artifact | `True` |
| patched_row_csv | `analysis/integration_eval/teacher_divergence_next_direct_repair_static_patch_apply_repaired_row.csv` |
| before_bucket | `pending` |
| after_bucket | `normalized_ready_static_repaired` |
| eval_allowed_after_patch | `0` |
| checkpoint_read_allowed_after_patch | `0` |
| training_allowed_after_patch | `0` |
| promotion_allowed_after_patch | `0` |

## Counts

| Bucket | Before | After derived patch |
|---|---:|---:|
| normalized_ready | 3 | 3 |
| normalized_ready_static_repaired | 0 | 1 |
| repair_queue | 1 | 0 |
| quarantine | 6 | 6 |

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
| original_manifest_overwrite_allowed_now | 0 |

## Acceptance checks

| Check | Result |
|---|---|
| upstream_preview_ready | PASS |
| exactly_one_repair_review_row | PASS |
| derived_patch_artifact_created | PASS |
| original_manifest_not_modified | PASS |
| does_not_train | PASS |
| does_not_run_model_eval | PASS |
| does_not_read_checkpoint_content | PASS |
| does_not_write_checkpoints | PASS |
| does_not_export_c | PASS |
| does_not_run_public_benchmark | PASS |
| does_not_promote | PASS |
| does_not_overwrite_current_best | PASS |

## Interpretation

The one repair-queue row is carried into a derived static-repaired bucket only. This does not mutate the original manifest and does not grant permission for training, model evaluation, checkpoint read, C export, public benchmark, promotion, or current-best overwrite.

## Apply decision

`DIRECT_REPAIR_STATIC_PATCH_APPLY_COMPLETE_DERIVED_ONLY`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-apply-closeout`

## Promotion decision

`NO_PROMOTION__STATIC_PATCH_DERIVED_ONLY`
