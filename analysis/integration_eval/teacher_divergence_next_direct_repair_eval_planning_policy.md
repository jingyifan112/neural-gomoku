# 15x15 teacher-divergence next direct repair eval planning policy

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-eval-planning-policy`

## Purpose

Define future explicit eval-planning policy after static review resolution, without running eval or reading checkpoint contents.

This branch does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, overwrite current-best, or overwrite original manifest artifacts.

## Upstream

| Field | Value |
|---|---|
| upstream_resolution_decision | `STATIC_REVIEW_RESOLUTION_COMPLETE_FOR_FUTURE_EXPLICIT_PLANNING_POLICY` |
| upstream_recommended_next_branch | `exp/15x15-teacher-divergence-next-direct-repair-eval-planning-policy` |
| upstream_promotion_decision | `NO_PROMOTION__STATIC_REVIEW_RESOLUTION_ONLY` |

## Source row identity

| Field | Value |
|---|---|
| repair_queue_id | `direct_repair_001` |
| source_repair_queue_id | `direct_repair_001` |
| source_manifest_row_id | `1` |
| source_eval_manifest_id | `run1_direct_probe_eval_001` |
| source_adapter_kind | `direct_model_eval_fixed_probe_candidate` |
| source_path | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` |

## Gate assessment after static resolution

| Gate | Result |
|---|---|
| G1 | PASS |
| G2 | PASS |
| G3 | PASS |
| G4 | PASS |
| G5 | PASS |
| G6 | PASS |
| G7 | PASS |
| G8 | PASS |

## Eval planning policy boundary

This policy defines future eval-planning requirements only. It does not run model eval, read checkpoints, train, export C, benchmark, promote, or overwrite current-best.

## Future eval-planning requirements

| Requirement | Name | Required | Criterion |
|---|---|---|---|
| P1 | new_explicit_eval_planning_branch_required | True | Any future eval planning must happen in a separate branch and explicitly state that checkpoint reads and model eval are not run unless later separately authorized. |
| P2 | checkpoint_identity_must_be_named_but_not_read | True | A future planning branch may name intended checkpoint identity/path as a string only, but must not load or inspect checkpoint contents. |
| P3 | eval_command_must_be_dry_documented_only | True | A future planning branch may document a proposed eval command, but must not execute it. |
| P4 | manifest_input_must_be_derived_only | True | The repaired row must remain derived-only unless a later explicit branch authorizes a manifest mutation. |
| P5 | quarantine_boundary_must_remain_closed | True | The 6 quarantine rows remain excluded and cannot be carried into eval planning. |
| P6 | promotion_path_must_remain_disabled | True | No promotion, current-best overwrite, C export, public benchmark, or checkpoint write is allowed by planning. |

## Future explicit eval plan template

| Field | Value |
|---|---|
| candidate_row | `direct_repair_001` |
| source_eval_manifest_id | `run1_direct_probe_eval_001` |
| source_adapter_kind | `direct_model_eval_fixed_probe_candidate` |
| source_path | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` |
| allowed_now | `{"export_c": false, "overwrite_current_best": false, "promote": false, "public_benchmark": false, "read_checkpoint": false, "run_eval": false, "train": false, "write_eval_plan_artifact": true, "write_policy_artifact": true}` |
| required_later_authorizations_before_execution | `["explicit_checkpoint_read_authorization", "explicit_model_eval_authorization", "explicit_eval_command_review", "explicit_no_promotion_guard", "explicit_no_current_best_overwrite_guard"]` |

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

## Acceptance checks

| Check | Result |
|---|---|
| upstream_resolution_complete | PASS |
| all_static_ready_gates_passed_after_resolution | PASS |
| defines_policy_only | PASS |
| does_not_train | PASS |
| does_not_run_model_eval | PASS |
| does_not_read_checkpoint_content | PASS |
| does_not_write_checkpoints | PASS |
| does_not_export_c | PASS |
| does_not_run_public_benchmark | PASS |
| does_not_promote | PASS |
| does_not_overwrite_current_best | PASS |
| does_not_overwrite_original_manifest | PASS |

## Interpretation

The direct repair row is now eligible only for a future explicit eval-plan dry run artifact. This branch does not execute eval, read checkpoint contents, train, export C, benchmark, promote, or overwrite current-best.

## Planning decision

`DIRECT_REPAIR_EVAL_PLANNING_POLICY_READY_NO_EXECUTION`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-eval-plan-dryrun`

## Promotion decision

`NO_PROMOTION__EVAL_PLANNING_POLICY_ONLY`
