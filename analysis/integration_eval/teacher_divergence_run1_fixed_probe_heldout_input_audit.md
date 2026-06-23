# Teacher-divergence run1 fixed-probe / heldout input audit

## Branch

`exp/15x15-teacher-divergence-run1-fixed-probe-heldout-input-audit`

## Scope

- Inventories local fixed-probe, heldout, tactical, anchor, dataset, and guard artifacts.
- Classifies which inputs are directly evaluable versus which need adapters.
- Does not train.
- Does not read or write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Decision

`READY_TO_IMPLEMENT_LOCAL_COMPARISON_ADAPTERS`

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| plan_decision | READY_TO_IMPLEMENT_LOCAL_COMPARISON_ADAPTERS | INFO | Input audit only. |
| inventory_rows | 783 | INFO |  |
| direct_model_eval_ready_files | 42 | INFO |  |
| already_compared_guard_output_files | 30 | INFO |  |
| needs_board_join_adapter_files | 73 | INFO |  |
| needs_target_adapter_files | 15 | INFO |  |
| run1_trainable_guard_rows | 44 | PASS |  |
| run1_bucket_guard_rows | 89 | PASS |  |
| run1_anchor_guard_rows | 32 | PASS |  |
| plan_summary_rows | 21 | INFO |  |

## Schema-ready counts

| schema_ready_kind | files |
|---|---:|
| not_directly_eval_ready | 623 |
| needs_board_join_adapter | 73 |
| direct_model_eval_ready | 42 |
| already_compared_guard_output | 30 |
| needs_target_adapter | 15 |

## Stage counts

| stage_class | files |
|---|---:|
| related | 544 |
| fixed_probe_candidate | 101 |
| benchmark_related | 47 |
| run1_output | 47 |
| dataset_related | 24 |
| anchor_candidate | 9 |
| heldout_candidate | 7 |
| guard_related | 4 |

## Suffix counts

| suffix | files |
|---|---:|
| .txt | 299 |
| .md | 235 |
| .csv | 165 |
| .json | 84 |

## Direct model-eval ready candidates

| path | stage | rows/count | schema_ready_kind |
|---|---|---:|---|
| `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | anchor_candidate | 8 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_dataset.json` | dataset_related | 8 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | anchor_candidate | 3 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_d_g2_m15_diagnostic_dataset.json` | dataset_related | 3 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | anchor_candidate | 1 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_e_g2_m13_diagnostic_dataset.json` | dataset_related | 1 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | anchor_candidate | 3 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_e_g2_m17_diagnostic_dataset.json` | dataset_related | 3 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_f_teacher_counterfactual_dataset.json` | dataset_related | 3 | direct_model_eval_ready |
| `analysis/integration_eval/candidate_g_teacher_seed_dataset.json` | dataset_related | 14 | direct_model_eval_ready |
| `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | anchor_candidate | 7 | direct_model_eval_ready |
| `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | anchor_candidate | 5 | direct_model_eval_ready |
| `analysis/integration_eval/current_best_margin_candidate_c_conservative_dataset.json` | dataset_related | 5 | direct_model_eval_ready |
| `analysis/integration_eval/current_best_margin_candidate_c_dataset.json` | dataset_related | 7 | direct_model_eval_ready |
| `analysis/integration_eval/current_best_margin_candidate_d_move15_lastmove_dataset.json` | dataset_related | 4 | direct_model_eval_ready |
| `analysis/integration_eval/debug_artifact_deep_schema_audit.md` | related | 0 | direct_model_eval_ready |
| `analysis/integration_eval/policy_only_multisuppress_dataset_trainer_audit.md` | dataset_related | 0 | direct_model_eval_ready |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` | fixed_probe_candidate | 0 | direct_model_eval_ready |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md` | fixed_probe_candidate | 0 | direct_model_eval_ready |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md` | fixed_probe_candidate | 0 | direct_model_eval_ready |
| `analysis/integration_eval/retention_family_applied_split_dryrun.json` | related | 44 | direct_model_eval_ready |
| `analysis/integration_eval/retention_family_run1_loss_source_diagnosis.json` | run1_output | 4 | direct_model_eval_ready |
| `analysis/integration_eval/retention_family_run1_nan_diagnosis.md` | run1_output | 0 | direct_model_eval_ready |
| `analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json` | dataset_related | 9 | direct_model_eval_ready |
| `analysis/integration_eval/retention_family_training_consumer_adapter_train_dataset.json` | dataset_related | 2 | direct_model_eval_ready |
| `analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json` | dataset_related | 2 | direct_model_eval_ready |
| `analysis/integration_eval/retention_family_wrapper_run1/train_plain_dataset.json` | run1_output | 2 | direct_model_eval_ready |
| `analysis/integration_eval/safety_block_candidate_manifest.json` | related | 0 | direct_model_eval_ready |
| `analysis/integration_eval/teacher_divergence_data_expansion_design.md` | related | 0 | direct_model_eval_ready |
| `analysis/integration_eval/teacher_divergence_expanded_manifest_design.md` | related | 0 | direct_model_eval_ready |

## Already compared guard outputs

| path | stage | rows/count | schema_ready_kind |
|---|---|---:|---|
| `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` | related | 3 | already_compared_guard_output |
| `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` | run1_output | 3 | already_compared_guard_output |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | fixed_probe_candidate | 0 | already_compared_guard_output |
| `analysis/integration_eval/policy_only_rank_topk_protected_weighting_audit.md` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/policy_only_rank_topk_training_run1_closeout.md` | run1_output | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_gate_evaluator_threshold_policy_gate_eval.json` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_gate_evaluator_threshold_policy_gate_eval.md` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_gate_evaluator_threshold_policy_strict_gate_eval.json` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_gate_evaluator_threshold_policy_strict_gate_eval.md` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_run2_eval_prob_regression_review.md` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_threshold_smoke_review.md` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_threshold_train_gate_smoke/gate_eval.json` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_threshold_train_gate_smoke/gate_eval.md` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_wrapper_threshold_gate_dryrun/gate_eval.json` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/retention_family_wrapper_threshold_gate_dryrun/gate_eval.md` | related | 0 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_guard_audit.md` | run1_output | 0 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv` | run1_output | 3 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv` | run1_output | 3 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit.csv` | heldout_candidate | 3 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_review.csv` | run1_output | 3 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_review.md` | run1_output | 0 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_run1_promotion_readiness_audit.md` | run1_output | 0 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_tiny_policy_margin_probe_e3_gap_summary.csv` | fixed_probe_candidate | 3 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_tiny_policy_margin_probe_e3_report.md` | fixed_probe_candidate | 0 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_tiny_posttrain_guard_audit.md` | guard_related | 0 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_tiny_posttrain_manifest_bucket_guard.csv` | guard_related | 3 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_tiny_posttrain_trainable_gap_guard.csv` | guard_related | 3 | already_compared_guard_output |
| `analysis/integration_eval/teacher_divergence_tiny_probe_guard_decision_closeout.md` | fixed_probe_candidate | 0 | already_compared_guard_output |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e10_lr5e6_report.md` | benchmark_related | 0 | already_compared_guard_output |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e40_lr1e5_report.md` | benchmark_related | 0 | already_compared_guard_output |

## Needs board-join adapter

| path | stage | rows/count | schema_ready_kind |
|---|---|---:|---|
| `analysis/integration_eval/candidate_d_teacher_disagreement_census.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/candidate_d_teacher_disagreement_census.md` | related | 0 | needs_board_join_adapter |
| `analysis/integration_eval/candidate_g_teacher_seed_manifest.json` | related | 14 | needs_board_join_adapter |
| `analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_applied_split_dryrun_manifest.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_gated_training_probe_runner_preflight.json` | fixed_probe_candidate | 0 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_materialized_split.json` | related | 11 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_materialized_split_manifest.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_split_proposal.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_threshold_train_gate_smoke/eval_after.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_threshold_train_gate_smoke/eval_before.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_threshold_train_gate_smoke/train_after.csv` | related | 2 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_threshold_train_gate_smoke/train_before.csv` | related | 2 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_threshold_train_gate_smoke/wrapper_train_gate.json` | related | 0 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_training_consumer_adapter_manifest.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_training_consumer_adapter_summary.json` | related | 0 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_training_input_dryrun_summary.json` | related | 0 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv` | related | 2 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run1/eval_after.csv` | run1_output | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run1/eval_before.csv` | run1_output | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run1/train_after.csv` | run1_output | 2 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run1/train_before.csv` | run1_output | 2 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run1/wrapper_result.json` | run1_output | 0 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run2_weighted/eval_after.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run2_weighted/eval_before.csv` | related | 3 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run2_weighted/train_after.csv` | related | 2 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run2_weighted/train_before.csv` | related | 2 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_run2_weighted/wrapper_result.json` | related | 0 | needs_board_join_adapter |
| `analysis/integration_eval/retention_family_wrapper_threshold_gate_dryrun/wrapper_gates_only.json` | related | 0 | needs_board_join_adapter |

## Needs target adapter

| path | stage | rows/count | schema_ready_kind |
|---|---|---:|---|
| `analysis/integration_eval/b_mcts16_debug_failure_snapshots.json` | related | 8 | needs_target_adapter |
| `analysis/integration_eval/b_mcts16_debug_failure_snapshots.md` | related | 0 | needs_target_adapter |
| `analysis/integration_eval/candidate_c_g2_m19_last_move_diagnosis.md` | related | 0 | needs_target_adapter |
| `analysis/integration_eval/candidate_c_mcts16_debug_failure_snapshots.json` | related | 8 | needs_target_adapter |
| `analysis/integration_eval/candidate_c_mcts16_debug_failure_snapshots.md` | related | 0 | needs_target_adapter |
| `analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json` | related | 5 | needs_target_adapter |
| `analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.md` | related | 0 | needs_target_adapter |
| `analysis/integration_eval/candidate_d_mcts32_nearend_failure_snapshots.json` | related | 16 | needs_target_adapter |
| `analysis/integration_eval/candidate_d_mcts32_nearend_failure_snapshots.md` | related | 0 | needs_target_adapter |
| `analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_snapshots.json` | related | 8 | needs_target_adapter |
| `analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_snapshots.md` | related | 0 | needs_target_adapter |
| `analysis/integration_eval/policy_only_objective_gate_next_design.md` | related | 0 | needs_target_adapter |
| `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json` | benchmark_related | 32 | needs_target_adapter |
| `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.md` | benchmark_related | 0 | needs_target_adapter |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json` | benchmark_related | 25 | needs_target_adapter |

## Recommended next implementation

Implement the local comparison executor in two layers:

1. Reuse run1 guard outputs as already-computed candidate-vs-current_best comparisons for trainable, protected/tail, and anchor rows.
2. Add adapters only for direct model-eval ready fixed-probe/heldout datasets discovered here.
3. Keep fixed-probe/heldout comparison local only; do not export C and do not run public benchmark.

## Outputs

- inventory CSV: `analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_inventory.csv`
- summary CSV: `analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_audit_summary.csv`
- report: `analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_audit.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
