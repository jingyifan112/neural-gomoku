# 15x15 teacher-divergence next direct repair static review resolution

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-static-review-resolution`

## Purpose

Resolve the static schema/review blockers for the derived static-repaired direct repair row without unlocking eval or checkpoint reads.

This branch does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, overwrite current-best, or overwrite original manifest artifacts.

## Upstream

| Field | Value |
|---|---|
| upstream_gate_decision | `STATIC_READY_GATE_POLICY_DEFINED_CURRENT_ROW_REMAINS_BLOCKED` |
| upstream_recommended_next_branch | `exp/15x15-teacher-divergence-next-direct-repair-static-review-resolution` |

## Source row identity

| Field | Value |
|---|---|
| repair_queue_id | `direct_repair_001` |
| source_repair_queue_id | `direct_repair_001` |
| source_manifest_row_id | `1` |
| source_eval_manifest_id | `run1_direct_probe_eval_001` |
| source_adapter_kind | `direct_model_eval_fixed_probe_candidate` |
| source_path | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` |

## Static resolutions

| Field | Before | After |
|---|---|---|
| schema_status | `HAS_CONTEXT_BUT_NEEDS_REVIEW` | `STATIC_SCHEMA_ACCEPTED_CONTEXT_ONLY` |
| repair_review_decision | `REPAIR_ROW_MANUAL_REVIEW` | `STATIC_REVIEW_ACCEPTED_FOR_FUTURE_EXPLICIT_PLANNING_ONLY` |

## Resolution basis

### Schema resolution basis

- source_path_exists is 1
- source_path points to a tracked static analysis artifact
- provenance_status is CLEAN_HELDOUT_OR_DIRECT_SOURCE
- inspection_clean_source_tokens include fixed_probe and direct_probe

### Manual review resolution basis

- repair row identity is explicit
- derived patch apply closeout completed as derived-only
- original manifest artifacts remain unmodified
- the row remains outside eval and checkpoint-read permission

## Gate assessment before and after

| Gate | Before | After static resolution |
|---|---|---|
| G1 | PASS | PASS |
| G2 | PASS | PASS |
| G3 | PASS | PASS |
| G4 | PASS | PASS |
| G5 | PASS | PASS |
| G6 | FAIL | PASS |
| G7 | FAIL | PASS |
| G8 | PASS | PASS |

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
| eval_execution_allowed_now | 0 |

## Acceptance checks

| Check | Result |
|---|---|
| upstream_gate_row_blocked_as_expected | PASS |
| schema_status_was_review_needed | PASS |
| manual_review_was_pending | PASS |
| source_path_exists | PASS |
| provenance_clean | PASS |
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

The static blockers G6 and G7 are resolved only as metadata/static-review decisions. This does not unlock eval planning in this branch and does not permit eval execution, checkpoint reads, training, C export, benchmark, promotion, or current-best overwrite.

The next safe branch may define an eval-planning policy, still without running eval or reading checkpoint contents.

## Resolution decision

`STATIC_REVIEW_RESOLUTION_COMPLETE_FOR_FUTURE_EXPLICIT_PLANNING_POLICY`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-eval-planning-policy`

## Promotion decision

`NO_PROMOTION__STATIC_REVIEW_RESOLUTION_ONLY`
