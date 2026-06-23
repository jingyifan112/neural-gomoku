# 15x15 teacher-divergence next direct repair eval plan dryrun

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-eval-plan-dryrun`

## Purpose

Create a dry-run eval plan artifact for the derived direct repair row without executing eval or reading checkpoint contents.

This branch does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, overwrite current-best, or overwrite original manifest artifacts.

## Upstream

| Field | Value |
|---|---|
| upstream_planning_decision | `DIRECT_REPAIR_EVAL_PLANNING_POLICY_READY_NO_EXECUTION` |
| upstream_recommended_next_branch | `exp/15x15-teacher-divergence-next-direct-repair-eval-plan-dryrun` |
| upstream_promotion_decision | `NO_PROMOTION__EVAL_PLANNING_POLICY_ONLY` |

## Planned inputs

| Field | Value |
|---|---|
| candidate_row | `direct_repair_001` |
| source_eval_manifest_id | `run1_direct_probe_eval_001` |
| source_adapter_kind | `direct_model_eval_fixed_probe_candidate` |
| source_path | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` |
| derived_status | `eligible_for_future_explicit_eval_plan_documentation_only` |

## Future checkpoint identity

| Field | Value |
|---|---|
| checkpoint_path_string_only | `checkpoints/15x15_current_best.pt` |
| checkpoint_read_now | `False` |
| checkpoint_contents_inspected_now | `False` |
| note | `Checkpoint identity is recorded as a future planning string only. This branch does not load or inspect checkpoint contents.` |

## Proposed future eval command documentation only

```bash
PYTHONPATH=src python scripts/<future_direct_repair_eval_script>.py \
  --input-row direct_repair_001 \
  --source-eval-manifest-id run1_direct_probe_eval_001 \
  --checkpoint checkpoints/15x15_current_best.pt \
  --output-dir analysis/integration_eval/<future_eval_output_dir>
```

This command is not executed in this branch.

## Execution status

| Action | Executed now |
|---|---:|
| eval_command_executed | 0 |
| checkpoint_loaded | 0 |
| checkpoint_contents_read | 0 |
| training_executed | 0 |
| c_export_executed | 0 |
| public_benchmark_executed | 0 |
| promotion_executed | 0 |
| current_best_overwritten | 0 |
| original_manifest_modified | 0 |

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
| eval_plan_documentation_allowed_now | 1 |
| eval_execution_allowed_now | 0 |

## Dryrun checks

| Check | Result |
|---|---|
| upstream_policy_ready | PASS |
| eval_plan_documentation_allowed | PASS |
| eval_execution_disallowed | PASS |
| checkpoint_read_disallowed | PASS |
| training_disallowed | PASS |
| promotion_disallowed | PASS |
| current_best_overwrite_disallowed | PASS |
| original_manifest_overwrite_disallowed | PASS |

## Interpretation

The direct repair row has an eval-plan dryrun artifact only. The planned checkpoint is recorded only as a string, and no eval command is executed. Any future execution requires separate explicit authorization.

## Dryrun decision

`DIRECT_REPAIR_EVAL_PLAN_DRYRUN_COMPLETE_NO_EXECUTION`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-eval-plan-closeout`

## Promotion decision

`NO_PROMOTION__EVAL_PLAN_DRYRUN_ONLY`
