# Teacher-divergence next direct-probe input repair plan

## Branch

`exp/15x15-teacher-divergence-next-direct-probe-input-repair-plan`

## Scope

- Plans repair of direct-probe / heldout eval inputs after run1 conservative closeout.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Plan decision

`DIRECT_PROBE_INPUT_REPAIR_PLAN_READY`

## Recommended next

Create a follow-up branch to normalize/repair direct-probe and heldout input manifests. Keep all work report/input-only until a later explicitly guarded local-eval executor exists.

## Root causes

- direct_adapter_blocked
- probability_regression_warnings_remain
- direct_manifest_exists_but_route_not_safe
- prior_fixed_probe_heldout_audit_available

## Planned actions

| priority | action_id | type | proposed_output | guardrail |
|---:|---|---|---|---|
| 1 | inspect_direct_adapter_blockers | diagnostic | analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_blocker_notes.md | No model eval; text/CSV inspection only. |
| 2 | schema_normalize_direct_manifest | input_repair | analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_normalized_manifest.csv | Do not read checkpoints; validate only paths, row counts, split names, and source provenance. |
| 3 | build_clean_heldout_probe_source_plan | input_repair | analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_heldout_source_plan.csv | No training, no eval, no C export, no promotion. |
| 4 | dedupe_warning_propagation | routing_quality | analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_warning_dedupe_plan.md | Report-only patch plan; do not change gate thresholds in this branch. |
| 5 | keep_run1_candidate_isolated | governance | No checkpoint promotion; candidate stays local/isolated. | No current_best overwrite; no checkpoint artifacts in git. |
| 6 | reuse_prior_fixed_probe_audit_as_candidate_source | input_repair | analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_fixed_probe_source_review.csv | Review-only; no model eval. |

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| plan_decision | DIRECT_PROBE_INPUT_REPAIR_PLAN_READY | INFO | Plan only; no model eval. |
| recommended_next | Create a follow-up branch to normalize/repair direct-probe and heldout input manifests. Keep all work report/input-only until a later explicitly guarded local-eval executor exists. | INFO |  |
| final_closeout_decision | RUN1_CORE_REUSE_FINAL_CLOSEOUT_COMPLETE_WITH_WARNINGS | INFO |  |
| promotion_decision | NO_PROMOTION__KEEP_RUN1_CANDIDATE_ISOLATED | INFO |  |
| direct_adapter_decision | DIRECT_PROBE_EVAL_ADAPTER_BLOCKED | INFO |  |
| direct_adapter_blocker_count | 2 | WARN | controlled review is blocked; controlled review blockers present: 2 |
| direct_adapter_warning_count | 2 | WARN | controlled review warnings carried forward: 5; deferred adapter inputs remain: 88 |
| root_cause_count | 4 | INFO | direct_adapter_blocked; probability_regression_warnings_remain; direct_manifest_exists_but_route_not_safe; prior_fixed_probe_heldout_audit_available |
| planned_action_count | 6 | INFO |  |
| blocker_count | 0 | PASS |  |
| warning_count | 5 | WARN | combined WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8; direct adapter warnings carried forward: 2; controlled review warnings carried forward: 5; deferred adapter inputs remain: 88; direct adapter blocker notes need repair: controlled review is blocked; controlled review blockers present: 2 |
| candidate_checkpoint_exists_locally | 1 | INFO | Existence only; no checkpoint read. |
| current_best_exists | 1 | PASS |  |
| direct_manifest_rows | 10 | INFO |  |
| optional_fixed_audit_summary_rows | 10 | INFO |  |
| optional_fixed_audit_manifest_rows | 0 | INFO |  |
| combined_summary_rows | 12 | INFO |  |
| combined_fail_rows | 0 | PASS |  |
| combined_warn_rows | 2 | WARN |  |
| trainable_gap_improved | 44 | PASS |  |
| trainable_rank_regressed | 0 | PASS |  |
| protected_rank_regressed | 0 | PASS |  |
| tail_rank_regressed | 0 | PASS |  |
| protected_prob_regressed | 11 | WARN |  |
| tail_prob_regressed | 8 | WARN |  |
| anchor_top1_changed | 0 | PASS |  |
| anchor_max_kl | 0.0000060956 | PASS |  |
| would_train | 0 | PASS |  |
| would_eval_model_now | 0 | PASS |  |
| would_read_checkpoint_contents_now | 0 | PASS |  |
| would_write_checkpoint | 0 | PASS |  |
| would_c_export | 0 | PASS |  |
| would_public_benchmark | 0 | PASS |  |
| would_promote | 0 | PASS |  |

## Direct manifest preview

| row | keys |
|---:|---|
| 1 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 2 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 3 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 4 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 5 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 6 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 7 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 8 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 9 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |
| 10 | adapter_kind, comparison_action, dryrun_status, eval_manifest_id, future_execute_requires, future_executor_action, has_board, has_case_id, has_side, has_target, notes, path, sample_rows_or_count, schema_ready_kind, stage_class |

## Blockers

- None.

## Warnings

- combined WARN rows carried forward: 2
- protected raw probability regressions carried forward: 11
- tail raw probability regressions carried forward: 8
- direct adapter warnings carried forward: 2; controlled review warnings carried forward: 5; deferred adapter inputs remain: 88
- direct adapter blocker notes need repair: controlled review is blocked; controlled review blockers present: 2

## Final guardrails

- Keep the run1 candidate checkpoint isolated.
- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
