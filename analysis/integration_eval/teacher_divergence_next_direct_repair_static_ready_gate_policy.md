# 15x15 teacher-divergence next direct repair static ready gate policy

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-static-ready-gate-policy`

## Purpose

Define the static ready gate policy for derived static-repaired direct repair rows.

This branch does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, overwrite current-best, or overwrite original manifest artifacts.

## Upstream

| Field | Value |
|---|---|
| upstream_closeout_decision | `DIRECT_REPAIR_STATIC_PATCH_APPLY_CLOSEOUT_COMPLETE_DERIVED_ONLY` |
| upstream_promotion_decision | `NO_PROMOTION__STATIC_PATCH_APPLY_CLOSEOUT_ONLY` |

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

## Gate policy

| Field | Value |
|---|---|
| gate_name | `derived_static_repaired_to_eval_planning_gate` |
| input_bucket | `normalized_ready_static_repaired` |
| output_bucket_if_pass | `eligible_for_future_explicit_eval_planning` |
| output_bucket_if_fail | `remain_static_repaired_no_eval` |
| critical_boundary | This gate does not itself allow eval, checkpoint read, training, export, benchmark, or promotion. |

## Required preconditions

| Gate | Name | Required | Criterion | Current row result |
|---|---|---|---|---|
| G1 | derived_patch_closeout_complete | True | Upstream closeout decision must be DIRECT_REPAIR_STATIC_PATCH_APPLY_CLOSEOUT_COMPLETE_DERIVED_ONLY. | PASS |
| G2 | original_manifest_unchanged | True | Original normalization/review/manifest artifacts must remain unmodified. | PASS |
| G3 | row_identity_explicit | True | Row must carry repair_queue_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, and source_path. | PASS |
| G4 | source_path_tracked_and_exists | True | source_path_exists must be 1 and source_path must point to a tracked static artifact. | PASS |
| G5 | provenance_clean | True | provenance_status must remain CLEAN_HELDOUT_OR_DIRECT_SOURCE or another explicitly reviewed clean provenance label. | PASS |
| G6 | schema_review_resolved | True | schema_status must be resolved from HAS_CONTEXT_BUT_NEEDS_REVIEW to an explicitly accepted static schema status in a later branch. | FAIL |
| G7 | manual_review_resolved | True | repair_review_decision must be resolved from REPAIR_ROW_MANUAL_REVIEW to an explicit accepted decision in a later branch. | FAIL |
| G8 | permission_boundary_preserved | True | eval_allowed_now, checkpoint_read_allowed_now, training_allowed_now, and promotion_allowed_now must remain 0 until a separate explicit planning branch. | PASS |

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
| eval_planning_allowed_now | 0 |

## Interpretation

The current derived static-repaired row does not yet pass the static ready gate. It remains blocked because at least one future-review condition is unresolved. This is expected and conservative.

The next safe step is a static review-resolution branch, not eval, not checkpoint read, not training, and not promotion.

## Gate decision

`STATIC_READY_GATE_POLICY_DEFINED_CURRENT_ROW_REMAINS_BLOCKED`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-static-review-resolution`

## Promotion decision

`NO_PROMOTION__STATIC_READY_GATE_POLICY_ONLY`
