# Teacher-divergence run1 local comparison controlled review

## Branch

`exp/15x15-teacher-divergence-run1-local-comparison-controlled-review`

## Scope

- Reviews local comparison executor dry-run outputs.
- Confirms whether the dry-run is safe enough to proceed to a controlled direct-probe eval adapter.
- Does not train.
- Does not run model eval.
- Does not read or write checkpoint contents.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Review decision

`LOCAL_COMPARISON_CONTROLLED_REVIEW_BLOCKED`

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| review_decision | LOCAL_COMPARISON_CONTROLLED_REVIEW_BLOCKED | INFO | Controlled review only; no model eval. |
| review_blocker_count | 2 | FAIL | executor dry-run decision is not ready: LOCAL_COMPARISON_DRYRUN_BLOCKED; dry-run blockers present: 1 |
| review_warning_count | 5 | WARN | dry-run warnings carried forward: 2; combined dry-run WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8; direct model-eval inputs available for next adapter: 10 |
| executor_decision | LOCAL_COMPARISON_DRYRUN_BLOCKED | FAIL |  |
| dryrun_blocker_count | 1 | FAIL | adapter design is not ready: LOCAL_COMPARISON_ADAPTER_DESIGN_BLOCKED |
| dryrun_warning_count | 2 | WARN | direct model-eval inputs selected but not executed in dry-run: 10; combined reused guard output has WARN rows: 2 |
| combined_rows | 12 | INFO |  |
| combined_fail_rows | 0 | PASS |  |
| combined_warn_rows | 2 | WARN |  |
| selected_inputs | 13 | INFO |  |
| core_selected_inputs | 3 | PASS |  |
| direct_model_eval_inputs_selected | 10 | INFO |  |
| adapter_design_decision | LOCAL_COMPARISON_ADAPTER_DESIGN_BLOCKED | INFO |  |
| adapter_design_direct_model_eval_inputs_selected | 10 | INFO |  |
| adapter_design_deferred_adapter_inputs | 88 | INFO |  |
| would_train | 0 | PASS |  |
| would_eval_model | 0 | PASS |  |
| would_write_checkpoint | 0 | PASS |  |
| would_c_export | 0 | PASS |  |
| would_public_benchmark | 0 | PASS |  |
| would_promote | 0 | PASS |  |
| trainable_gap_improved | 44 | PASS |  |
| trainable_rank_regressed | 0 | PASS |  |
| protected_rank_regressed | 0 | PASS |  |
| tail_rank_regressed | 0 | PASS |  |
| protected_prob_regressed | 11 | WARN |  |
| tail_prob_regressed | 8 | WARN |  |
| anchor_top1_changed | 0 | PASS |  |
| anchor_max_kl | 0.0000060956 | PASS |  |

## Review blockers

- executor dry-run decision is not ready: LOCAL_COMPARISON_DRYRUN_BLOCKED
- dry-run blockers present: 1

## Review warnings

- dry-run warnings carried forward: 2
- combined dry-run WARN rows carried forward: 2
- protected raw probability regressions carried forward: 11
- tail raw probability regressions carried forward: 8
- direct model-eval inputs available for next adapter: 10

## Selected direct model-eval inputs

| adapter_kind | stage | path | rows/count |
|---|---|---|---:|
| direct_model_eval_fixed_probe_candidate | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` | 0 |
| direct_model_eval_fixed_probe_candidate | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md` | 0 |
| direct_model_eval_fixed_probe_candidate | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md` | 0 |
| direct_model_eval_heldout_candidate | heldout_candidate | `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md` | 0 |
| direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | 8 |
| direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | 3 |
| direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | 1 |
| direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | 3 |
| direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | 7 |
| direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | 5 |

## Interpretation

Do not proceed to direct-probe eval adapter until the blockers above are fixed.

## Outputs

- summary CSV: `analysis/integration_eval/teacher_divergence_run1_local_comparison_controlled_review_summary.csv`
- next plan: `analysis/integration_eval/teacher_divergence_run1_local_comparison_controlled_review_next_plan.txt`
- report: `analysis/integration_eval/teacher_divergence_run1_local_comparison_controlled_review.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
