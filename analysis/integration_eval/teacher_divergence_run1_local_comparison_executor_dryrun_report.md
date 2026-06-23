# Teacher-divergence run1 local comparison executor dry-run

## Branch

`exp/15x15-teacher-divergence-run1-local-comparison-executor-dryrun`

## Scope

- Implements a dry-run local comparison executor.
- Reuses already-computed run1 guard outputs.
- Does not run model eval.
- Does not train.
- Does not read or write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Executor decision

`LOCAL_COMPARISON_DRYRUN_BLOCKED`

## Safety flags

| flag | value |
|---|---:|
| mode | dry_run |
| execute_requested | 0 |
| would_train | 0 |
| would_eval_model | 0 |
| would_write_checkpoint | 0 |
| would_c_export | 0 |
| would_public_benchmark | 0 |
| would_promote | 0 |

## Combined reused guard summary

| section | rows | metric | value | status | notes |
|---|---:|---|---:|---|---|
| trainable_guard_reuse | 44 | gap_improved_rows | 44 | PASS |  |
| trainable_guard_reuse | 44 | target_prob_improved_rows | 44 | INFO |  |
| trainable_guard_reuse | 44 | target_rank_regressed_rows | 0 | PASS |  |
| trainable_guard_reuse | 44 | mean_gap_delta | 0.0086329092 | PASS |  |
| protected_tail_guard_reuse | 89 | evaluated_rows | 89 | PASS |  |
| protected_tail_guard_reuse | 23 | protected_top10_rank_regressed_rows | 0 | PASS |  |
| protected_tail_guard_reuse | 23 | protected_top10_prob_regressed_rows | 11 | WARN |  |
| protected_tail_guard_reuse | 66 | tail_rank_gt50_rank_regressed_rows | 0 | PASS |  |
| protected_tail_guard_reuse | 66 | tail_rank_gt50_prob_regressed_rows | 8 | WARN |  |
| anchor_drift_guard_reuse | 32 | anchor_top1_changed_rows | 0 | PASS |  |
| anchor_drift_guard_reuse | 32 | anchor_mean_kl | 0.0000018348 | INFO |  |
| anchor_drift_guard_reuse | 32 | anchor_max_kl | 0.0000060956 | PASS |  |

## Selected inputs

| adapter_kind | action | path | rows/count |
|---|---|---|---:|
| core_anchor_drift_guard_reuse | reuse_already_computed | `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_anchor_drift_guard.csv` | 3 |
| core_protected_tail_guard_reuse | reuse_already_computed | `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv` | 3 |
| core_trainable_guard_reuse | reuse_already_computed | `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv` | 3 |
| direct_model_eval_fixed_probe_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` | 0 |
| direct_model_eval_fixed_probe_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md` | 0 |
| direct_model_eval_fixed_probe_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md` | 0 |
| direct_model_eval_heldout_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md` | 0 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | 8 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | 3 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | 1 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | 3 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | 7 |
| direct_model_eval_anchor_candidate | candidate_vs_current_best_eval | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | 5 |

## Blockers

- adapter design is not ready: LOCAL_COMPARISON_ADAPTER_DESIGN_BLOCKED

## Warnings

- direct model-eval inputs selected but not executed in dry-run: 10
- combined reused guard output has WARN rows: 2

## Interpretation

This dry-run executor confirms that the already-computed run1 trainable, protected/tail, and anchor guard outputs can be reused as a local comparison baseline.

It does not yet perform additional fixed-probe model evaluation. A later branch may add controlled model-eval support only for selected direct-ready inputs.

## Outputs

- combined summary CSV: `analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv`
- decision JSON: `analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_decision.json`
- decision CSV: `analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_decision.csv`
- command plan: `analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_commands.txt`
- report: `analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_report.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
