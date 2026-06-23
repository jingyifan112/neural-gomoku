# Teacher-divergence run1 next-stage blocked review

## Branch

`exp/15x15-teacher-divergence-run1-next-stage-blocked-review`

## Scope

- Reviews why the route-aware next stage became blocked.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Review decision

`BLOCKED_REVIEW_RECOMMENDS_ROUTING_PATCH_OR_CORE_CLOSEOUT`

## Root causes

- direct_probe_adapter_blocked
- probability_regression_warnings_remain

## Recommended actions

- Inspect direct adapter blocker notes; likely direct-probe path is not ready.
- Carry warnings forward; do not promote without later fixed-probe/heldout evidence.

## Blocker source trace

- direct_adapter: blocker_count=2; controlled review is blocked; controlled review blockers present: 2
- post_adapter_route: blocker_count=2; adapter blockers present: 2; adapter decision is blocked
- route_aware_local: blocker_count=3; route blockers present: 2; adapter blockers present: 2; post-adapter route is blocked
- route_aware_next_stage: blocker_count=3; route-aware local decision blockers present: 3; direct adapter blockers present: 2; route-aware local decision is blocked
- dispatch: blocker_count=2; upstream next-stage blockers present: 3; upstream next-stage decision is blocked
- followup: blocker_count=2; dispatch blockers present: 2; dispatch decision is blocked
- dispatch_json: upstream next-stage blockers present: 3; upstream next-stage decision is blocked
- followup_json: dispatch blockers present: 2; dispatch decision is blocked
- route_next_spec: route-aware local decision blockers present: 3; direct adapter blockers present: 2; route-aware local decision is blocked

## Warning source trace

- direct_adapter: warning_count=2; controlled review warnings carried forward: 5; deferred adapter inputs remain: 88
- post_adapter_route: warning_count=1; adapter warnings carried forward: 2
- route_aware_local: warning_count=5; route warnings carried forward: 1; adapter warnings carried forward: 2; combined dry-run WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8
- route_aware_next_stage: warning_count=5; route-aware warnings carried forward: 5; adapter warnings carried forward: 2; combined local comparison WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8
- dispatch: warning_count=4; upstream next-stage warnings carried forward: 5; combined local comparison WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8
- followup: warning_count=4; dispatch warnings carried forward: 4; combined WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8
- dispatch_json: upstream next-stage warnings carried forward: 5; combined local comparison WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8
- followup_json: dispatch warnings carried forward: 4; combined WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8
- route_next_spec: route-aware warnings carried forward: 5; adapter warnings carried forward: 2; combined local comparison WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| review_decision | BLOCKED_REVIEW_RECOMMENDS_ROUTING_PATCH_OR_CORE_CLOSEOUT | INFO | Blocked review only; no model eval. |
| root_cause_count | 2 | INFO | direct_probe_adapter_blocked; probability_regression_warnings_remain |
| action_count | 2 | INFO | Inspect direct adapter blocker notes; likely direct-probe path is not ready.; Carry warnings forward; do not promote without later fixed-probe/heldout evidence. |
| candidate_checkpoint_exists_locally | 1 | PASS | Existence only; do not add to git. |
| current_best_exists | 1 | PASS |  |
| direct_manifest_rows | 10 | INFO |  |
| direct_ready_inputs_from_selection | 10 | INFO |  |
| direct_adapter_decision | DIRECT_PROBE_EVAL_ADAPTER_BLOCKED | INFO |  |
| post_adapter_final_route_decision | POST_ADAPTER_ROUTE_BLOCKED | INFO |  |
| route_aware_local_decision | ROUTE_AWARE_LOCAL_DECISION_BLOCKED | INFO |  |
| route_aware_next_stage_decision | NEXT_STAGE_BLOCKED | INFO |  |
| dispatch_decision | NEXT_STAGE_DISPATCH_BLOCKED | INFO |  |
| followup_decision | NEXT_STAGE_FOLLOWUP_BLOCKED | INFO |  |
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

## Interpretation

The route appears blocked without a clear hard metric failure. Consider either patching the routing logic or making a conservative core-reuse local decision closeout.

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
