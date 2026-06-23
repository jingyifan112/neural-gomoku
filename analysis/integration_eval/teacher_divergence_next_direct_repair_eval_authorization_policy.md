# 15x15 teacher-divergence next direct repair eval authorization policy

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-eval-authorization-policy`

## Purpose

Define future explicit authorization requirements for direct repair eval execution without granting execution now.

This branch does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, overwrite current-best, or overwrite original manifest artifacts.

## Upstream closeout

| Field | Value |
|---|---|
| upstream_closeout_decision | `DIRECT_REPAIR_EVAL_PLAN_CLOSEOUT_COMPLETE_NO_EXECUTION` |
| upstream_recommended_next_branch | `exp/15x15-teacher-divergence-next-direct-repair-eval-authorization-policy` |
| upstream_promotion_decision | `NO_PROMOTION__EVAL_PLAN_CLOSEOUT_ONLY` |

## Planned inputs

| Field | Value |
|---|---|
| candidate_row | `direct_repair_001` |
| source_eval_manifest_id | `run1_direct_probe_eval_001` |
| source_adapter_kind | `direct_model_eval_fixed_probe_candidate` |
| source_path | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` |
| derived_status | `eligible_for_future_explicit_eval_plan_documentation_only` |

## Current authorization state

| Authorization | Granted now |
|---|---:|
| eval_execution_authorized_now | 0 |
| checkpoint_read_authorized_now | 0 |
| training_authorized_now | 0 |
| checkpoint_write_authorized_now | 0 |
| c_export_authorized_now | 0 |
| public_benchmark_authorized_now | 0 |
| promotion_authorized_now | 0 |
| current_best_overwrite_authorized_now | 0 |
| original_manifest_overwrite_authorized_now | 0 |

## Future authorization requirements before eval execution

| Requirement | Name | Required | Criterion |
|---|---|---|---|
| A1 | explicit_checkpoint_read_authorization | True | A later branch must explicitly authorize reading checkpoint contents and name the checkpoint path. |
| A2 | explicit_model_eval_authorization | True | A later branch must explicitly authorize model eval execution and distinguish it from planning/dryrun. |
| A3 | exact_eval_command_review | True | A later branch must replace placeholder script/output paths with exact tracked or generated paths before any execution. |
| A4 | input_row_scope_lock | True | Eval scope must remain limited to direct_repair_001 unless a later branch explicitly expands scope. |
| A5 | quarantine_exclusion_lock | True | The six quarantined rows remain excluded from any eval input. |
| A6 | no_promotion_guard | True | Eval execution, if later authorized, must not imply promotion, C export, benchmark, checkpoint write, current-best overwrite, or model replacement. |
| A7 | result_handling_policy_required | True | A later branch must define how eval output would be recorded and reviewed without automatic promotion. |

## Proposed future eval command documentation only

```bash
PYTHONPATH=src python scripts/<future_direct_repair_eval_script>.py \
  --input-row direct_repair_001 \
  --source-eval-manifest-id run1_direct_probe_eval_001 \
  --checkpoint checkpoints/15x15_current_best.pt \
  --output-dir analysis/integration_eval/<future_eval_output_dir>
```

This command is not executed in this branch.

## Authorization checks

| Check | Result |
|---|---|
| upstream_eval_plan_closeout_complete | PASS |
| upstream_no_execution_recorded | PASS |
| upstream_closeout_checks_pass | PASS |
| planned_input_present | PASS |
| checkpoint_identity_string_only | PASS |
| proposed_command_documented_only | PASS |
| current_eval_execution_not_authorized | PASS |
| current_checkpoint_read_not_authorized | PASS |
| promotion_not_authorized | PASS |
| current_best_overwrite_not_authorized | PASS |

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
| eval_authorization_policy_documentation_allowed_now | 1 |
| eval_execution_allowed_now | 0 |

## Interpretation

This branch defines the authorization boundary only. It does not grant permission to execute eval or read checkpoint contents. Any real eval remains blocked until a later branch explicitly grants checkpoint-read and model-eval execution authorization.

## Authorization decision

`DIRECT_REPAIR_EVAL_AUTHORIZATION_POLICY_DEFINED_NO_EXECUTION`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-eval-authorization-closeout`

## Promotion decision

`NO_PROMOTION__EVAL_AUTHORIZATION_POLICY_ONLY`
