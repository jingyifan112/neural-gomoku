# 15x15 teacher-divergence next direct repair static patch apply closeout

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-apply-closeout`

## Purpose

Close out the derived-only direct repair static patch apply branch.

This branch does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, overwrite current-best, or overwrite original manifest artifacts.

## Upstream apply result

| Field | Value |
|---|---|
| upstream_apply_decision | `DIRECT_REPAIR_STATIC_PATCH_APPLY_COMPLETE_DERIVED_ONLY` |
| patch_apply_mode | `derived_artifact_only` |
| promotion_decision | `NO_PROMOTION__STATIC_PATCH_DERIVED_ONLY` |

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

## Counts closeout

| Bucket | Before | After derived patch |
|---|---:|---:|
| normalized_ready | 3 | 3 |
| normalized_ready_static_repaired | 0 | 1 |
| repair_queue | 1 | 0 |
| quarantine | 6 | 6 |

## Closeout safety permissions

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
| eval_allowed_from_closeout | 0 |

## Closeout checks

| Check | Result |
|---|---|
| upstream_apply_complete | PASS |
| derived_patch_only | PASS |
| original_manifest_not_modified | PASS |
| repaired_row_csv_recorded | PASS |
| training_remains_disabled | PASS |
| model_eval_remains_disabled | PASS |
| checkpoint_read_remains_disabled | PASS |
| c_export_remains_disabled | PASS |
| public_benchmark_remains_disabled | PASS |
| promotion_remains_disabled | PASS |
| current_best_overwrite_remains_disabled | PASS |

## Interpretation

The repair queue row has been carried into a derived static-repaired artifact only. This is not a promotion, not an eval unlock, not a checkpoint-read unlock, and not a training input change.

The safe next step is a static ready-gate policy that defines what would be required before any derived static-repaired row could become eligible for future explicit eval planning.

## Closeout decision

`DIRECT_REPAIR_STATIC_PATCH_APPLY_CLOSEOUT_COMPLETE_DERIVED_ONLY`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-static-ready-gate-policy`

## Promotion decision

`NO_PROMOTION__STATIC_PATCH_APPLY_CLOSEOUT_ONLY`
