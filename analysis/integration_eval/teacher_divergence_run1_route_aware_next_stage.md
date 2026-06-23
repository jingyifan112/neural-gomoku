# Teacher-divergence run1 route-aware next-stage dry-run/report

## Branch

`exp/15x15-teacher-divergence-run1-route-aware-next-stage`

## Scope

- Reads route-aware local decision and prior local comparison outputs.
- Produces the next-stage plan/spec.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Next-stage decision

`NEXT_STAGE_BLOCKED`

## Recommended next branch

`none`

## Recommended action

Fix blockers before continuing.

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| next_stage_decision | NEXT_STAGE_BLOCKED | INFO | No model eval in this branch. |
| recommended_branch | none | INFO |  |
| recommended_action | Fix blockers before continuing. | INFO |  |
| local_decision | ROUTE_AWARE_LOCAL_DECISION_BLOCKED | INFO |  |
| recommended_branch_from_route | none | INFO |  |
| blocker_count | 3 | FAIL | route-aware local decision blockers present: 3; direct adapter blockers present: 2; route-aware local decision is blocked |
| warning_count | 5 | WARN | route-aware warnings carried forward: 5; adapter warnings carried forward: 2; combined local comparison WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8 |
| adapter_decision | DIRECT_PROBE_EVAL_ADAPTER_BLOCKED | INFO |  |
| route_blocker_count | 3 | FAIL |  |
| route_warning_count | 5 | WARN |  |
| adapter_blocker_count | 2 | FAIL |  |
| adapter_warning_count | 2 | WARN |  |
| candidate_checkpoint_exists_locally | 1 | PASS | Existence only; do not add to git. |
| current_best_exists | 1 | PASS |  |
| core_reuse_inputs | 3 | PASS |  |
| direct_ready_inputs | 10 | INFO |  |
| direct_manifest_rows | 10 | INFO |  |
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

## Direct manifest rows

| eval_manifest_id | adapter_kind | path | rows/count |
|---|---|---|---:|
| run1_direct_probe_eval_001 | direct_model_eval_fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` | 0 |
| run1_direct_probe_eval_002 | direct_model_eval_fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md` | 0 |
| run1_direct_probe_eval_003 | direct_model_eval_fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md` | 0 |
| run1_direct_probe_eval_004 | direct_model_eval_heldout_candidate | `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md` | 0 |
| run1_direct_probe_eval_005 | direct_model_eval_anchor_candidate | `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | 8 |
| run1_direct_probe_eval_006 | direct_model_eval_anchor_candidate | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | 3 |
| run1_direct_probe_eval_007 | direct_model_eval_anchor_candidate | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | 1 |
| run1_direct_probe_eval_008 | direct_model_eval_anchor_candidate | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | 3 |
| run1_direct_probe_eval_009 | direct_model_eval_anchor_candidate | `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | 7 |
| run1_direct_probe_eval_010 | direct_model_eval_anchor_candidate | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | 5 |

## Core reused comparison summary

| section | metric | value | status |
|---|---|---:|---|
| trainable_guard_reuse | gap_improved_rows | 44 | PASS |
| trainable_guard_reuse | target_prob_improved_rows | 44 | INFO |
| trainable_guard_reuse | target_rank_regressed_rows | 0 | PASS |
| trainable_guard_reuse | mean_gap_delta | 0.0086329092 | PASS |
| protected_tail_guard_reuse | evaluated_rows | 89 | PASS |
| protected_tail_guard_reuse | protected_top10_rank_regressed_rows | 0 | PASS |
| protected_tail_guard_reuse | protected_top10_prob_regressed_rows | 11 | WARN |
| protected_tail_guard_reuse | tail_rank_gt50_rank_regressed_rows | 0 | PASS |
| protected_tail_guard_reuse | tail_rank_gt50_prob_regressed_rows | 8 | WARN |
| anchor_drift_guard_reuse | anchor_top1_changed_rows | 0 | PASS |
| anchor_drift_guard_reuse | anchor_mean_kl | 0.0000018348 | INFO |
| anchor_drift_guard_reuse | anchor_max_kl | 0.0000060956 | PASS |

## Blockers

- route-aware local decision blockers present: 3
- direct adapter blockers present: 2
- route-aware local decision is blocked

## Warnings

- route-aware warnings carried forward: 5
- adapter warnings carried forward: 2
- combined local comparison WARN rows carried forward: 2
- protected raw probability regressions carried forward: 11
- tail raw probability regressions carried forward: 8

## Outputs

- summary CSV: `analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_summary.csv`
- spec JSON: `analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_spec.json`
- next plan: `analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_next_plan.txt`
- report: `analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
