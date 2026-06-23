# Teacher-divergence run1 local comparison adapter design

## Branch

`exp/15x15-teacher-divergence-run1-local-comparison-adapter-design`

## Scope

- Designs adapters for local candidate-vs-current_best comparison.
- Uses input inventory from fixed-probe/heldout input audit.
- Selects stable initial executor inputs.
- Does not train.
- Does not read or write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Decision

`LOCAL_COMPARISON_ADAPTER_DESIGN_BLOCKED`

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| design_decision | LOCAL_COMPARISON_ADAPTER_DESIGN_BLOCKED | INFO | Adapter design only; no model eval. |
| blocker_count | 1 | FAIL | fixed-probe/heldout plan decision is not ready: FIXED_PROBE_HELDOUT_PLAN_BLOCKED |
| warning_count | 2 | WARN | deferred adapter inputs present: 88; optional already-compared guard outputs present: 28 |
| input_audit_plan_decision | READY_TO_IMPLEMENT_LOCAL_COMPARISON_ADAPTERS | PASS |  |
| fixed_probe_heldout_plan_decision | FIXED_PROBE_HELDOUT_PLAN_BLOCKED | FAIL |  |
| candidate_checkpoint_exists_locally | 1 | PASS | Local artifact only; do not add to git. |
| current_best_exists | 1 | PASS |  |
| inventory_rows | 783 | INFO |  |
| selection_rows | 783 | INFO |  |
| selected_for_initial_executor | 13 | INFO |  |
| core_guard_outputs_selected | 3 | PASS |  |
| direct_model_eval_inputs_selected | 10 | INFO |  |
| deferred_adapter_inputs | 88 | WARN |  |
| optional_guard_reuse_inputs | 28 | INFO |  |
| adapter_kind:not_selected | 622 | INFO |  |
| adapter_kind:board_join_adapter_needed | 73 | INFO |  |
| adapter_kind:direct_model_eval_lower_priority | 32 | INFO |  |
| adapter_kind:guard_output_reuse_optional | 28 | INFO |  |
| adapter_kind:target_adapter_needed | 15 | INFO |  |
| adapter_kind:direct_model_eval_anchor_candidate | 6 | INFO |  |
| adapter_kind:direct_model_eval_fixed_probe_candidate | 3 | INFO |  |
| adapter_kind:core_anchor_drift_guard_reuse | 1 | INFO |  |
| adapter_kind:core_protected_tail_guard_reuse | 1 | INFO |  |
| adapter_kind:core_trainable_guard_reuse | 1 | INFO |  |
| adapter_kind:direct_model_eval_heldout_candidate | 1 | INFO |  |

## Selected initial executor inputs

| adapter_kind | action | stage | path | rows/count |
|---|---|---|---|---:|
| core_anchor_drift_guard_reuse | reuse_already_computed | run1_output | `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_anchor_drift_guard.csv` | 3 |
| core_protected_tail_guard_reuse | reuse_already_computed | run1_output | `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv` | 3 |
| core_trainable_guard_reuse | reuse_already_computed | run1_output | `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv` | 3 |
| direct_model_eval_fixed_probe_candidate | candidate_vs_current_best_eval | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` | 0 |
| direct_model_eval_fixed_probe_candidate | candidate_vs_current_best_eval | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md` | 0 |
| direct_model_eval_fixed_probe_candidate | candidate_vs_current_best_eval | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md` | 0 |
| direct_model_eval_heldout_candidate | candidate_vs_current_best_eval | heldout_candidate | `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md` | 0 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | anchor_candidate | `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | 8 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | anchor_candidate | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | 3 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | anchor_candidate | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | 1 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | anchor_candidate | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | 3 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | anchor_candidate | `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | 7 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | anchor_candidate | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | 5 |

## Adapter kind counts

| adapter_kind | files |
|---|---:|
| not_selected | 622 |
| board_join_adapter_needed | 73 |
| direct_model_eval_lower_priority | 32 |
| guard_output_reuse_optional | 28 |
| target_adapter_needed | 15 |
| direct_model_eval_anchor_candidate | 6 |
| direct_model_eval_fixed_probe_candidate | 3 |
| core_anchor_drift_guard_reuse | 1 |
| core_protected_tail_guard_reuse | 1 |
| core_trainable_guard_reuse | 1 |
| direct_model_eval_heldout_candidate | 1 |

## Action counts

| action | files |
|---|---:|
| not_directly_evaluable | 622 |
| defer_adapter | 88 |
| candidate_vs_current_best_eval_optional | 32 |
| reuse_already_computed | 31 |
| candidate_vs_current_best_eval | 10 |

## Selected stage counts

| stage | files |
|---|---:|
| anchor_candidate | 6 |
| run1_output | 3 |
| fixed_probe_candidate | 3 |
| heldout_candidate | 1 |

## Deferred adapter inputs

| adapter_kind | stage | path | reason |
|---|---|---|---|
| board_join_adapter_needed | fixed_probe_candidate | `analysis/integration_eval/retention_family_gated_training_probe_runner_preflight.json` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/integration_eval/teacher_divergence_current_best_probe_fill.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/integration_eval/teacher_divergence_current_best_probe_fill_report.md` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2_report.md` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/integration_eval/teacher_divergence_current_best_probe_round2_plan.md` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/integration_eval/teacher_divergence_legacy_trainable_current_best_probe_fill.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/integration_eval/teacher_divergence_legacy_trainable_current_best_probe_fill_report.md` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e10_lr5e6_teacher_rank_probe.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | fixed_probe_candidate | `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e40_lr1e5_teacher_rank_probe.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | heldout_candidate | `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | dataset_related | `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset.json` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | dataset_related | `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset_legacy_normalized.json` | Has target but needs board/source join before model eval. |
| target_adapter_needed | benchmark_related | `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json` | Has board/side but needs target extraction policy. |
| target_adapter_needed | benchmark_related | `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.md` | Has board/side but needs target extraction policy. |
| board_join_adapter_needed | benchmark_related | `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | benchmark_related | `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected_report.md` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | benchmark_related | `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected_report.md` | Has target but needs board/source join before model eval. |
| target_adapter_needed | benchmark_related | `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json` | Has board/side but needs target extraction policy. |
| board_join_adapter_needed | run1_output | `analysis/integration_eval/retention_family_wrapper_run1/eval_after.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | run1_output | `analysis/integration_eval/retention_family_wrapper_run1/eval_before.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | run1_output | `analysis/integration_eval/retention_family_wrapper_run1/train_after.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | run1_output | `analysis/integration_eval/retention_family_wrapper_run1/train_before.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | run1_output | `analysis/integration_eval/retention_family_wrapper_run1/wrapper_result.json` | Has target but needs board/source join before model eval. |
| target_adapter_needed | related | `analysis/integration_eval/b_mcts16_debug_failure_snapshots.json` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/b_mcts16_debug_failure_snapshots.md` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_c_g2_m19_last_move_diagnosis.md` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_c_mcts16_debug_failure_snapshots.json` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_c_mcts16_debug_failure_snapshots.md` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.md` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_d_mcts32_nearend_failure_snapshots.json` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_d_mcts32_nearend_failure_snapshots.md` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_snapshots.json` | Has board/side but needs target extraction policy. |
| target_adapter_needed | related | `analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_snapshots.md` | Has board/side but needs target extraction policy. |
| board_join_adapter_needed | related | `analysis/integration_eval/candidate_d_teacher_disagreement_census.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/candidate_d_teacher_disagreement_census.md` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/candidate_g_teacher_seed_manifest.json` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv` | Has target but needs board/source join before model eval. |
| target_adapter_needed | related | `analysis/integration_eval/policy_only_objective_gate_next_design.md` | Has board/side but needs target extraction policy. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_applied_split_dryrun_manifest.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_materialized_split.json` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_materialized_split_manifest.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_split_proposal.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_threshold_train_gate_smoke/eval_after.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_threshold_train_gate_smoke/eval_before.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_threshold_train_gate_smoke/train_after.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_threshold_train_gate_smoke/train_before.csv` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_threshold_train_gate_smoke/wrapper_train_gate.json` | Has target but needs board/source join before model eval. |
| board_join_adapter_needed | related | `analysis/integration_eval/retention_family_training_consumer_adapter_manifest.csv` | Has target but needs board/source join before model eval. |

## Recommended executor design

The next branch should implement a local-comparison executor with two input classes:

1. `reuse_already_computed`: load run1 guard CSVs and summarize candidate-vs-current_best results already computed by the wrapper.
2. `candidate_vs_current_best_eval`: evaluate selected direct model-eval-ready files if any are stable enough for immediate use.

The executor should produce:

- combined comparison CSV
- fixed-probe/heldout summary CSV
- decision report

Hard gates should remain local-only and should not trigger C export, public benchmark, or promotion.

## Blockers

- fixed-probe/heldout plan decision is not ready: FIXED_PROBE_HELDOUT_PLAN_BLOCKED

## Warnings

- deferred adapter inputs present: 88
- optional already-compared guard outputs present: 28

## Outputs

- selection CSV: `analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_selection.csv`
- summary CSV: `analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_design_summary.csv`
- command plan: `analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_design_commands.txt`
- report: `analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_design.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
