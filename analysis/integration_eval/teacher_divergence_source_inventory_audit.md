# Teacher-divergence source inventory audit

## Branch

`exp/15x15-teacher-divergence-source-inventory-audit`

## Scope

- Inventory/audit only.
- Uses `git ls-files`, so it inventories tracked files only.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Summary

| metric | value |
|---|---:|
| candidate tracked files | 600 |
| json files | 32 |
| csv files | 81 |
| text/report/script files | 487 |
| json/csv files with rows | 109 |
| total parsed json/csv rows | 2838 |

## Field coverage across parsed JSON/CSV sources

| field group | files with coverage | total covered rows |
|---|---:|---:|
| board | 21 | 432 |
| side | 82 | 2433 |
| target | 30 | 700 |
| rank | 15 | 833 |
| prob | 15 | 833 |
| suppress | 12 | 134 |
| teacher_eval | 8 | 201 |
| source_trace | 80 | 1752 |
| bucket | 27 | 1222 |

## Parsed JSON/CSV source files

| path | kind | rows | sections | board | side | target | rank | prob | suppress | teacher_eval | source_trace | bucket |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `analysis/integration_eval/15x15_failure_corpus_census.csv` | csv | 34 | `` | 0 | 34 | 0 | 0 | 0 | 0 | 0 | 34 | 0 |
| `analysis/integration_eval/15x15_failure_corpus_corpus8_parseonly_census.csv` | csv | 105 | `` | 0 | 105 | 0 | 0 | 0 | 0 | 0 | 105 | 0 |
| `analysis/integration_eval/15x15_failure_corpus_corpus8_parseonly_summary.csv` | csv | 8 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| `analysis/integration_eval/15x15_failure_corpus_corpus8_selected_census.csv` | csv | 105 | `` | 0 | 105 | 0 | 0 | 0 | 0 | 0 | 105 | 0 |
| `analysis/integration_eval/15x15_failure_corpus_corpus8_selected_summary.csv` | csv | 8 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| `analysis/integration_eval/15x15_failure_corpus_summary.csv` | csv | 2 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | json | 8 | `{"top_level_list": 8}` | 8 | 8 | 8 | 0 | 0 | 8 | 0 | 8 | 0 |
| `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | json | 3 | `{"top_level_list": 3}` | 3 | 3 | 3 | 0 | 0 | 3 | 0 | 3 | 0 |
| `analysis/integration_eval/candidate_d_teacher_disagreement_census.csv` | csv | 44 | `` | 0 | 0 | 44 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | json | 1 | `{"top_level_list": 1}` | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 0 |
| `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | json | 3 | `{"top_level_list": 3}` | 3 | 3 | 3 | 0 | 0 | 3 | 0 | 3 | 0 |
| `analysis/integration_eval/candidate_f_teacher_counterfactual_dataset.json` | json | 3 | `{"samples": 3}` | 3 | 3 | 3 | 0 | 0 | 3 | 0 | 3 | 0 |
| `analysis/integration_eval/candidate_g_tactical_gate.csv` | csv | 14 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_g_teacher_policy_dataset.json` | json | 96 | `{"samples": 96}` | 96 | 96 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_g_teacher_rank_comparison.csv` | csv | 28 | `` | 0 | 0 | 28 | 28 | 28 | 0 | 0 | 28 | 0 |
| `analysis/integration_eval/candidate_g_teacher_seed_dataset.json` | json | 14 | `{"rows": 14}` | 14 | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_g_teacher_seed_manifest.json` | json | 14 | `{"rows": 14}` | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_h_c_decision_probes.csv` | csv | 8 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_h_c_parity.csv` | csv | 3 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_h_c_tactical_gate.csv` | csv | 7 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_h_child_value_comparison.csv` | csv | 8 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| `analysis/integration_eval/candidate_h_policy_rank_comparison.csv` | csv | 28 | `` | 0 | 0 | 28 | 28 | 28 | 0 | 0 | 28 | 0 |
| `analysis/integration_eval/candidate_h_rapfi_smoke_summary.csv` | csv | 3 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_h_tactical_gate.csv` | csv | 14 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_i_rapfi_requery_census.csv` | csv | 25 | `` | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/candidate_i_smoke_failure_census.csv` | csv | 25 | `` | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | json | 7 | `{"top_level_list": 7}` | 7 | 7 | 7 | 0 | 0 | 7 | 0 | 7 | 0 |
| `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | json | 5 | `{"top_level_list": 5}` | 5 | 5 | 5 | 0 | 0 | 5 | 0 | 5 | 0 |
| `analysis/integration_eval/current_best_margin_candidate_d_move15_lastmove_dataset.json` | json | 4 | `{"samples": 4}` | 4 | 4 | 4 | 0 | 0 | 4 | 0 | 4 | 0 |
| `analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv` | csv | 25 | `` | 0 | 0 | 25 | 25 | 25 | 25 | 0 | 25 | 0 |
| `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` | csv | 25 | `` | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 25 | 0 |
| `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` | csv | 25 | `` | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 25 | 0 |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_group_metrics.csv` | csv | 3 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/policy_only_rank_topk_protected_weighting_audit.csv` | csv | 25 | `` | 0 | 0 | 0 | 25 | 25 | 0 | 25 | 25 | 25 |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_train_metrics.csv` | csv | 25 | `` | 0 | 0 | 0 | 25 | 25 | 0 | 0 | 25 | 0 |
| `analysis/integration_eval/safety_block_candidate_manifest.csv` | csv | 36 | `` | 0 | 36 | 36 | 0 | 0 | 0 | 0 | 36 | 0 |
| `analysis/integration_eval/teacher_divergence_policy_anchor_probe_e40_kl075_eval.csv` | csv | 88 | `` | 0 | 88 | 0 | 88 | 88 | 0 | 0 | 0 | 88 |
| `analysis/integration_eval/teacher_divergence_policy_anchor_probe_eval.csv` | csv | 88 | `` | 0 | 88 | 0 | 88 | 88 | 0 | 0 | 0 | 88 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_eval.csv` | csv | 88 | `` | 0 | 88 | 0 | 88 | 88 | 0 | 0 | 0 | 88 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_eval.csv` | csv | 88 | `` | 0 | 88 | 0 | 88 | 88 | 0 | 0 | 0 | 88 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w005_gated_eval.csv` | csv | 88 | `` | 0 | 88 | 0 | 88 | 88 | 0 | 0 | 0 | 88 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.csv` | csv | 6 | `` | 0 | 6 | 6 | 0 | 0 | 0 | 0 | 6 | 6 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit.csv` | csv | 33 | `` | 0 | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 33 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv` | csv | 11 | `` | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 11 |
| `analysis/integration_eval/teacher_divergence_policy_probe_eval.csv` | csv | 88 | `` | 0 | 88 | 0 | 88 | 88 | 0 | 0 | 0 | 88 |
| `analysis/integration_eval/teacher_divergence_policy_probe_gate_summary.csv` | csv | 9 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_eval.csv` | csv | 88 | `` | 0 | 88 | 0 | 88 | 88 | 0 | 0 | 0 | 88 |
| `analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json` | json | 39 | `{"rows": 39}` | 39 | 39 | 39 | 0 | 0 | 0 | 0 | 39 | 39 |
| `analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv` | csv | 109 | `` | 0 | 109 | 82 | 0 | 0 | 0 | 32 | 109 | 109 |
| `analysis/integration_eval/teacher_divergence_retention_dataset.json` | json | 36 | `{"rows": 36}` | 36 | 36 | 36 | 0 | 0 | 0 | 0 | 36 | 36 |
| `analysis/integration_eval/teacher_divergence_retention_family_split_design_families.csv` | csv | 7 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/teacher_divergence_retention_family_split_design_rows.csv` | csv | 11 | `` | 0 | 11 | 11 | 0 | 0 | 0 | 0 | 11 | 11 |
| `analysis/integration_eval/teacher_divergence_retention_manifest.csv` | csv | 52 | `` | 0 | 52 | 52 | 0 | 0 | 0 | 12 | 52 | 52 |
| `analysis/integration_eval/teacher_divergence_retention_probe.csv` | csv | 36 | `` | 0 | 36 | 0 | 36 | 36 | 0 | 0 | 0 | 36 |
| `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json` | json | 44 | `{"rows": 44}` | 44 | 44 | 44 | 0 | 0 | 0 | 0 | 44 | 44 |
| `analysis/integration_eval/teacher_divergence_retention_safety_v3_manifest.csv` | csv | 36 | `` | 0 | 36 | 0 | 0 | 0 | 0 | 0 | 36 | 0 |
| `analysis/integration_eval/teacher_divergence_retention_source_audit.json` | json | 20 | `{"top_level_list": 20}` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/teacher_divergence_retention_validation.csv` | csv | 36 | `` | 0 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/public_benchmark_eval/candidate_g_corpus8_selected_eval.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/candidate_g_failure_set_eval.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/public_benchmark_eval/candidate_h_corpus8_selected_eval.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/candidate_h_failure_set_eval.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json` | json | 32 | `{"top_level_list": 32}` | 32 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/corpus8_selected_eval_source.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/corpus8_selected_snapshot_targets.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/current_best_corpus8_selected_eval.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/current_best_failure_set_eval.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv` | csv | 32 | `` | 0 | 32 | 32 | 0 | 0 | 0 | 32 | 32 | 32 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e10_lr5e6_corpus8_selected_eval.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e10_lr5e6_teacher_rank_probe.csv` | csv | 25 | `` | 0 | 25 | 25 | 0 | 0 | 0 | 0 | 25 | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e40_lr1e5_corpus8_selected_eval.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e40_lr1e5_teacher_rank_probe.csv` | csv | 25 | `` | 0 | 25 | 25 | 0 | 0 | 0 | 0 | 25 | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_bnfreeze_e40_lr5e6_corpus8_selected_eval.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json` | json | 25 | `{"samples": 25}` | 25 | 25 | 25 | 0 | 0 | 25 | 25 | 25 | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_e40_lr5e6_corpus8_selected_eval.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | json | 25 | `{"samples": 25}` | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json` | json | 25 | `{"protected_eval_samples": 15, "samples": 7, "tail_eval_samples": 3}` | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json` | json | 25 | `{"top_level_list": 25}` | 25 | 25 | 0 | 0 | 0 | 0 | 25 | 25 | 25 |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_candidate_g_corpus8_selected.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_candidate_h_corpus8_selected.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_model_comparison_corpus8_selected.csv` | csv | 32 | `` | 0 | 32 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| `analysis/public_benchmark_eval/tactical_mid_failure_categories.csv` | csv | 24 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/public_benchmark_eval/tactical_mid_failure_summary.csv` | csv | 24 | `` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `analysis/rapfi_failure_board_snapshots.json` | json | 7 | `{"top_level_list": 7}` | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_eval_v10.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_eval_v11.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_eval_v12_interp_a0.05.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_eval_v12_interp_a0.10.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_eval_v12_interp_a0.20.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_eval_v12_interp_a0.30.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_eval_v12_stage1.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_eval_v12_stage2.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_positions.csv` | csv | 42 | `` | 0 | 42 | 0 | 0 | 0 | 0 | 0 | 42 | 0 |
| `analysis/rapfi_failure_positions.json` | json | 2 | `{"top_level_list": 2}` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| `analysis/rapfi_failure_set.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_set.json` | json | 7 | `{"top_level_list": 7}` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_set_labeled.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_set_labeled.json` | json | 7 | `{"top_level_list": 7}` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/rapfi_failure_threat_analysis.csv` | csv | 7 | `` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `analysis/v12_candidate_failure_board_snapshots.json` | json | 8 | `{"top_level_list": 8}` | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| `analysis/v12_candidate_failure_threat_analysis.csv` | csv | 8 | `` | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| `analysis/v12_candidate_rapfi_failure_positions.csv` | csv | 27 | `` | 0 | 27 | 0 | 0 | 0 | 0 | 0 | 27 | 0 |
| `analysis/v12_candidate_rapfi_failure_positions.json` | json | 2 | `{"top_level_list": 2}` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| `analysis/v12_candidate_rapfi_failure_set.csv` | csv | 8 | `` | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| `analysis/v12_candidate_rapfi_failure_set.json` | json | 8 | `{"top_level_list": 8}` | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| `analysis/v12b_repair_eval_v12_candidate.csv` | csv | 11 | `` | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 11 | 11 |
| `analysis/v12b_repair_eval_v12b_candidate.csv` | csv | 11 | `` | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 11 | 11 |
| `analysis/v12i_failure_board_snapshots.json` | json | 22 | `{"top_level_list": 22}` | 22 | 22 | 0 | 0 | 0 | 0 | 0 | 22 | 0 |

## Candidate text/report/script files

| path | kind | lines |
|---|---|---:|
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00000_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p0/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00001_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p2/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00002_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p4/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00003_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p6/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00004_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p8/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00005_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p10/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00006_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p12/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00007_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p14/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00008_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p16/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00009_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p18/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00010_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p20/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00011_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p22/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00012_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p24/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00013_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p26/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00014_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p28/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00015_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p30/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00016_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p32/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00017_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p34/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00018_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p36/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00019_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p38/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00020_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p40/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00021_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p42/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00022_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g1_p44/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00023_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p1/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00024_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p3/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00025_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p5/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00026_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p7/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00027_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p9/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00028_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p11/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00029_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p13/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00030_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p15/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00031_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p17/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00032_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p19/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_c_cases/00033_candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2_g2_p21/top.txt` | text | 1 |
| `analysis/integration_eval/15x15_failure_corpus_corpus8_parseonly_report.md` | text | 74 |
| `analysis/integration_eval/15x15_failure_corpus_corpus8_selected_report.md` | text | 125 |
| `analysis/integration_eval/15x15_failure_corpus_report.md` | text | 66 |
| `analysis/integration_eval/candidate_c_g2_m19_last_move_diagnosis.md` | text | 42 |
| `analysis/integration_eval/candidate_d_mcts32_conclusion.md` | text | 134 |
| `analysis/integration_eval/candidate_d_rapfi_teacher_ledger.md` | text | 102 |
| `analysis/integration_eval/candidate_d_teacher_disagreement_census.md` | text | 64 |
| `analysis/integration_eval/candidate_e_teacher_counterfactual_validation.md` | text | 101 |
| `analysis/integration_eval/candidate_e_teacher_repair_dryrun.md` | text | 61 |
| `analysis/integration_eval/candidate_f_teacher_counterfactual_result.md` | text | 158 |
| `analysis/integration_eval/candidate_g_policy_first_dry_run_conclusion.md` | text | 68 |
| `analysis/integration_eval/candidate_g_policy_first_dry_run_report.md` | text | 53 |
| `analysis/integration_eval/candidate_g_teacher_distill_plan.md` | text | 77 |
| `analysis/integration_eval/candidate_g_teacher_policy_report.md` | text | 32 |
| `analysis/integration_eval/candidate_g_teacher_seed_dataset.md` | text | 49 |
| `analysis/integration_eval/candidate_g_teacher_seed_manifest.md` | text | 43 |
| `analysis/integration_eval/candidate_h_c_export_report.md` | text | 41 |
| `analysis/integration_eval/candidate_h_c_parity_cases/candidate_d_repair_anchor/c_top_legal_move.txt` | text | 1 |
| `analysis/integration_eval/candidate_h_c_parity_cases/candidate_d_repair_anchor/python_top_legal_move.txt` | text | 1 |
| `analysis/integration_eval/candidate_h_c_parity_cases/g2_ply15_teacher_disagreement/c_top_legal_move.txt` | text | 1 |
| `analysis/integration_eval/candidate_h_c_parity_cases/g2_ply15_teacher_disagreement/python_top_legal_move.txt` | text | 1 |
| `analysis/integration_eval/candidate_h_c_parity_cases/g2_ply17_teacher_disagreement/c_top_legal_move.txt` | text | 1 |
| `analysis/integration_eval/candidate_h_c_parity_cases/g2_ply17_teacher_disagreement/python_top_legal_move.txt` | text | 1 |
| `analysis/integration_eval/candidate_h_i_j_local_repair_closeout.md` | text | 105 |
| `analysis/integration_eval/candidate_h_rapfi_smoke_report.md` | text | 49 |
| `analysis/integration_eval/candidate_h_value_ranking_report.md` | text | 40 |
| `analysis/integration_eval/candidate_i_census_c_cases/0000_g1_p0/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0001_child_112/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0002_g1_p2/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0003_child_94/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0004_g1_p4/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0005_child_66/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0006_g1_p6/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0007_child_96/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0008_g1_p8/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0009_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0010_g1_p10/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0011_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0012_g1_p12/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0013_child_123/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0014_g1_p14/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0015_child_83/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0016_g1_p16/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0017_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0018_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0019_g1_p18/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0020_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0021_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0022_g1_p20/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0023_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0024_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0025_g2_p1/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0026_child_97/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0027_g2_p3/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0028_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0029_g2_p5/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0030_child_98/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0031_g2_p7/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0032_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0033_g2_p9/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0034_child_127/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0035_g2_p11/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0036_child_172/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0037_g2_p13/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0038_child_92/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0039_child_92/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0040_g2_p15/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0041_child_122/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0042_child_122/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0043_g2_p17/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0044_child_154/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0045_child_154/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0046_g2_p19/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0047_child_153/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0048_child_153/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0049_g2_p21/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0050_child_78/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0051_child_78/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0052_g2_p23/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0053_child_77/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0054_g2_p25/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0055_child_157/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0056_child_157/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0057_g2_p27/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0058_child_142/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_census_c_cases/0059_child_142/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0000_g1_p0/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0000_requery_g1_p0/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0001_child_112/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0002_child_112/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0002_g1_p2/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0003_child_94/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0003_requery_g1_p2/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0004_child_94/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0004_g1_p4/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0005_child_66/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0005_requery_g1_p4/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0006_child_66/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0006_g1_p6/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0007_child_96/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0007_requery_g1_p6/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0008_child_96/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0008_g1_p8/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0009_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0009_requery_g1_p8/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0010_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0010_g1_p10/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0011_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0011_requery_g1_p10/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0012_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0012_g1_p12/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0013_child_123/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0013_requery_g1_p12/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0014_child_123/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0014_g1_p14/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0015_child_83/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0015_requery_g1_p14/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0016_child_83/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0016_g1_p16/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0017_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0017_requery_g1_p16/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0018_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0019_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0019_g1_p18/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0020_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0020_requery_g1_p18/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0021_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0022_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0022_g1_p20/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0023_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0023_requery_g1_p20/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0024_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0025_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0025_g2_p1/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0026_child_97/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0026_requery_g2_p1/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0027_child_97/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0027_g2_p3/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0028_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0028_requery_g2_p3/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0029_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0029_g2_p5/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0030_child_98/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0030_requery_g2_p5/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0031_child_98/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0031_g2_p7/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0032_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0032_requery_g2_p7/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0033_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0033_g2_p9/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0034_child_127/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0034_requery_g2_p9/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0035_child_127/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0035_g2_p11/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0036_child_172/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0036_requery_g2_p11/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0037_child_172/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0037_g2_p13/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0038_child_92/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0038_requery_g2_p13/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0039_child_92/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0040_child_92/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0040_g2_p15/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0041_child_122/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0041_requery_g2_p15/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0042_child_122/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0043_child_122/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0043_g2_p17/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0044_child_154/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0044_requery_g2_p17/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0045_child_154/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0046_child_154/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0046_g2_p19/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0047_child_153/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0047_requery_g2_p19/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0048_child_153/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0049_child_153/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0049_g2_p21/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0050_child_78/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0050_requery_g2_p21/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0051_child_78/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0052_child_78/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0052_g2_p23/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0053_child_77/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0053_requery_g2_p23/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0054_child_77/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0054_g2_p25/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0055_child_157/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0055_requery_g2_p25/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0056_child_157/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0057_child_157/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0057_g2_p27/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0058_child_142/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0058_requery_g2_p27/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0059_child_142/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0060_child_137/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0060_requery_g1_p0/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0061_child_112/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0062_child_112/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0063_requery_g1_p2/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0064_child_94/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0065_child_50/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0065_requery_g1_p4/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0066_child_66/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0066_requery_g1_p4/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0067_child_66/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0067_requery_g1_p6/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0068_child_50/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0068_child_96/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0069_requery_g1_p6/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0069_requery_g1_p8/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0070_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0070_child_96/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0071_child_81/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0071_requery_g1_p10/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0072_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0072_requery_g1_p8/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0073_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0073_requery_g1_p12/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0074_child_123/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0074_child_50/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0075_requery_g1_p10/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0075_requery_g1_p14/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0076_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0076_child_83/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0077_child_50/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0077_requery_g1_p16/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0078_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0078_requery_g1_p12/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0079_child_123/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0079_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0080_child_67/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0080_requery_g1_p18/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0081_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0081_requery_g1_p14/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0082_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0082_child_83/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0083_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0083_requery_g1_p20/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0084_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0084_requery_g1_p16/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0085_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0085_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0086_child_79/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0086_requery_g2_p1/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0087_child_97/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0087_requery_g1_p18/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0088_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0088_requery_g2_p3/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0089_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0089_child_35/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0090_requery_g1_p20/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0090_requery_g2_p5/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0091_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0091_child_98/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0092_child_22/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0092_requery_g2_p7/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0093_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0093_requery_g2_p1/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0094_child_97/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0094_requery_g2_p9/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0095_child_127/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0095_child_82/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0096_requery_g2_p3/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0097_child_111/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0098_child_98/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0099_requery_g2_p5/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0100_child_98/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0101_child_98/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0102_requery_g2_p7/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_c_cases/0103_child_110/top.txt` | text | 1 |
| `analysis/integration_eval/candidate_i_rapfi_requery_census.md` | text | 109 |
| `analysis/integration_eval/candidate_i_smoke_failure_census.md` | text | 49 |
| `analysis/integration_eval/capacity_candidate_a_b6c64_init_report.md` | text | 90 |
| `analysis/integration_eval/capacity_candidate_a_b6c64_train_v1_probe.md` | text | 92 |
| `analysis/integration_eval/capacity_candidate_a_b6c64_train_v2_probe.md` | text | 63 |
| `analysis/integration_eval/capacity_candidate_b_b4c96_init_report.md` | text | 75 |
| `analysis/integration_eval/capacity_candidate_b_b4c96_train_v1_fixed_probe.md` | text | 89 |
| `analysis/integration_eval/capacity_candidate_b_b4c96_train_v2_fixed_probe.md` | text | 72 |
| `analysis/integration_eval/policy_only_multisuppress_dataset_build.log` | text | 16 |
| `analysis/integration_eval/policy_only_multisuppress_dataset_trainer_audit.md` | text | 97 |
| `analysis/integration_eval/policy_only_multisuppress_dryrun.log` | text | 16 |
| `analysis/integration_eval/policy_only_multisuppress_dryrun_closeout.md` | text | 59 |
| `analysis/integration_eval/policy_only_multisuppress_dryrun_report.md` | text | 73 |
| `analysis/integration_eval/policy_only_rank_topk_chain_closeout.md` | text | 389 |
| `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_report.md` | text | 70 |
| `analysis/integration_eval/policy_only_rank_topk_gate_run1_report.md` | text | 78 |
| `analysis/integration_eval/policy_only_rank_topk_objective_training_design.md` | text | 357 |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | text | 112 |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_report.md` | text | 51 |
| `analysis/integration_eval/policy_only_rank_topk_protected_objective_dryrun_dataset_report.md` | text | 80 |
| `analysis/integration_eval/policy_only_rank_topk_protected_objective_dryrun_report.md` | text | 59 |
| `analysis/integration_eval/policy_only_rank_topk_protected_weighting_audit.md` | text | 152 |
| `analysis/integration_eval/policy_only_rank_topk_training_probe_dryrun_report.md` | text | 59 |
| `analysis/integration_eval/policy_only_rank_topk_training_probe_nosave_smoke_report.md` | text | 71 |
| `analysis/integration_eval/policy_only_rank_topk_training_probe_run1_report.md` | text | 71 |
| `analysis/integration_eval/policy_only_rank_topk_training_probe_run2a_ce_only_nosave_report.md` | text | 71 |
| `analysis/integration_eval/policy_only_rank_topk_training_probe_run2b_weak_suppress_nosave_report.md` | text | 71 |
| `analysis/integration_eval/policy_only_rank_topk_training_run1_closeout.md` | text | 115 |
| `analysis/integration_eval/policy_only_rank_topk_training_run2_ablation_closeout.md` | text | 107 |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` | text | 49 |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md` | text | 891 |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_dryrun.log` | text | 114 |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md` | text | 1359 |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_train.log` | text | 232 |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_train_closeout.md` | text | 35 |
| `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_train_report.md` | text | 60 |
| `analysis/integration_eval/safety_block_candidate_report.md` | text | 91 |
| `analysis/integration_eval/teacher_divergence_data_expansion_design.md` | text | 318 |
| `analysis/integration_eval/teacher_divergence_policy_anchor_probe_closeout.md` | text | 107 |
| `analysis/integration_eval/teacher_divergence_policy_anchor_probe_e40_kl075_closeout.md` | text | 68 |
| `analysis/integration_eval/teacher_divergence_policy_anchor_probe_e40_kl075_report.md` | text | 73 |
| `analysis/integration_eval/teacher_divergence_policy_anchor_probe_report.md` | text | 73 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_closeout.md` | text | 95 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_gate_report.md` | text | 58 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_train_report.md` | text | 78 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_scale_sweep_closeout.md` | text | 133 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_gate_report.md` | text | 58 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_train_report.md` | text | 78 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w005_gated_gate_report.md` | text | 58 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w005_gated_train_report.md` | text | 78 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md` | text | 299 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review_closeout.md` | text | 130 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit.md` | text | 41 |
| `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_closeout.md` | text | 89 |
| `analysis/integration_eval/teacher_divergence_policy_next_steps.md` | text | 84 |
| `analysis/integration_eval/teacher_divergence_policy_probe_closeout.md` | text | 90 |
| `analysis/integration_eval/teacher_divergence_policy_probe_gate_report.md` | text | 52 |
| `analysis/integration_eval/teacher_divergence_policy_probe_report.md` | text | 70 |
| `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_gate_report.md` | text | 56 |
| `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_train_report.md` | text | 73 |
| `analysis/integration_eval/teacher_divergence_regression_gated_runner_closeout.md` | text | 76 |
| `analysis/integration_eval/teacher_divergence_retention_clean_v2_acceptance.md` | text | 98 |
| `analysis/integration_eval/teacher_divergence_retention_clean_v2_report.md` | text | 114 |
| `analysis/integration_eval/teacher_divergence_retention_data_closeout.md` | text | 95 |
| `analysis/integration_eval/teacher_divergence_retention_family_split_design_closeout.md` | text | 143 |
| `analysis/integration_eval/teacher_divergence_retention_family_split_design_report.md` | text | 94 |
| `analysis/integration_eval/teacher_divergence_retention_probe_report.md` | text | 70 |
| `analysis/integration_eval/teacher_divergence_retention_report.md` | text | 111 |
| `analysis/integration_eval/teacher_divergence_retention_safety_v3_acceptance.md` | text | 38 |
| `analysis/integration_eval/teacher_divergence_retention_safety_v3_report.md` | text | 65 |
| `analysis/integration_eval/teacher_divergence_retention_source_audit.md` | text | 1185 |
| `analysis/integration_eval/teacher_divergence_retention_validation.md` | text | 42 |
| `analysis/integration_eval/teacher_divergence_signal_audit.md` | text | 191 |
| `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.md` | text | 1889 |
| `analysis/public_benchmark_eval/corpus8_selected_eval_report.md` | text | 77 |
| `analysis/public_benchmark_eval/corpus8_selected_eval_source_summary.md` | text | 48 |
| `analysis/public_benchmark_eval/discovery_rapfi_paths.txt` | text | 29 |
| `analysis/public_benchmark_eval/failure_set_eval_report.md` | text | 59 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected_report.md` | text | 82 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e10_lr5e6_report.md` | text | 40 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_head_e40_lr1e5_report.md` | text | 50 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_bnfreeze_e40_lr5e6_report.md` | text | 46 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected_report.md` | text | 47 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_e40_lr5e6_report.md` | text | 46 |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected_report.md` | text | 53 |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_candidate_g_corpus8_selected_report.md` | text | 59 |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_candidate_h_corpus8_selected_report.md` | text | 59 |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected_report.md` | text | 59 |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_model_comparison_corpus8_selected_report.md` | text | 39 |
| `analysis/public_benchmark_eval/tactical_mid_failure_categories.md` | text | 56 |
| `analysis/public_benchmark_eval/tactical_mid_failure_summary.md` | text | 47 |
| `analysis/rapfi_failure_board_review_notes.md` | text | 57 |
| `analysis/rapfi_failure_board_snapshots.md` | text | 414 |
| `analysis/rapfi_failure_label_summary.md` | text | 62 |
| `analysis/rapfi_failure_set_preliminary_review.md` | text | 64 |
| `analysis/rapfi_failure_threat_analysis.md` | text | 99 |
| `analysis/v11_to_v12_failure_summary.md` | text | 49 |
| `analysis/v12_candidate_failure_board_snapshots.md` | text | 473 |
| `analysis/v12_candidate_failure_threat_analysis.md` | text | 113 |
| `analysis/v12_candidate_new_failure_analysis.md` | text | 79 |
| `analysis/v12_candidate_rapfi_smoke_summary.md` | text | 25 |
| `analysis/v12_candidate_robustness_summary.md` | text | 32 |
| `analysis/v12_interpolation_failure_set_summary.md` | text | 18 |
| `analysis/v12_stage1_failure_eval_summary.md` | text | 20 |
| `analysis/v12_stage2_failure_eval_summary.md` | text | 27 |
| `analysis/v12_training_plan_from_rapfi_failures.md` | text | 98 |
| `analysis/v12b_candidate_debug_comparison_summary.md` | text | 71 |
| `eval_logs/2026-06-02_v10_direct_debug_vs_rapfi_g2.log` | text | 662 |
| `eval_logs/2026-06-02_v10_mcts32_debug_vs_rapfi_g2.log` | text | 1661 |
| `eval_logs/2026-06-02_v10_mcts32_vs_rapfi_depth1_15x15_g10.log` | text | 7879 |
| `eval_logs/2026-06-02_v10_mcts32_vs_rapfi_depth1_15x15_smoke.log` | text | 1619 |
| `eval_logs/2026-06-02_v10_mcts_raw_debug_vs_rapfi_g2.log` | text | 995 |
| `eval_logs/2026-06-02_v10_vs_rapfi_depth1_15x15_g10.log` | text | 574 |
| `eval_logs/2026-06-02_v10_vs_rapfi_depth1_15x15_smoke.log` | text | 330 |
| `eval_logs/2026-06-02_v11_direct_debug_vs_rapfi_g2.log` | text | 736 |
| `eval_logs/2026-06-02_v11_mcts32_debug_vs_rapfi_g2.log` | text | 1661 |
| `eval_logs/2026-06-02_v11_mcts32_vs_rapfi_depth1_15x15_g10.log` | text | 7879 |
| `eval_logs/2026-06-02_v11_mcts32_vs_rapfi_depth1_15x15_smoke.log` | text | 1619 |
| `eval_logs/2026-06-02_v11_mcts_raw_debug_vs_rapfi_g2.log` | text | 995 |
| `eval_logs/2026-06-02_v11_vs_rapfi_depth1_15x15_g10.log` | text | 574 |
| `eval_logs/2026-06-02_v11_vs_rapfi_depth1_15x15_smoke.log` | text | 330 |
| `eval_logs/2026-06-03_v12_candidate_mcts32_debug_vs_rapfi_g2.log` | text | 1106 |
| `eval_logs/2026-06-03_v12_candidate_mcts32_vs_rapfi_depth1_15x15_smoke.log` | text | 1079 |
| `eval_logs/2026-06-03_v12_candidate_mcts32_vs_rapfi_depth1_15x15_smoke_rerun.log` | text | 1079 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_current_best_seed_3401.log` | text | 24 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_current_best_seed_3402.log` | text | 24 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_current_best_seed_3403.log` | text | 24 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_greedy_seed_3421.log` | text | 23 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_greedy_seed_3422.log` | text | 23 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_greedy_seed_3423.log` | text | 23 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_v10_seed_3411.log` | text | 24 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_v10_seed_3412.log` | text | 24 |
| `eval_logs/v12_candidate_robustness/v12_candidate_vs_v10_seed_3413.log` | text | 24 |
| `eval_logs/v12b_value_head_internal/v12_candidate_mcts16_debug_vs_rapfi_depth1_15x15_smoke.log` | text | 1106 |
| `eval_logs/v12b_value_head_internal/v12b_candidate_mcts16_debug_vs_rapfi_depth1_15x15_smoke.log` | text | 1106 |
| `eval_logs/v12b_value_head_internal/v12b_candidate_mcts16_vs_rapfi_depth1_15x15_smoke.log` | text | 1079 |
| `eval_logs/v12b_value_head_internal/value_head_stage1_vs_v12_candidate_seed1223.log` | text | 24 |
| `scripts/accept_teacher_divergence_retention_clean_v2_dataset.py` | text | 383 |
| `scripts/analyze_failure_threats.py` | text | 227 |
| `scripts/build_15x15_failure_corpus_census.py` | text | 804 |
| `scripts/build_candidate_g_teacher_policy_dataset.py` | text | 326 |
| `scripts/build_candidate_g_teacher_seed_dataset.py` | text | 288 |
| `scripts/build_candidate_g_teacher_seed_manifest.py` | text | 252 |
| `scripts/build_rapfi_failure_set.py` | text | 158 |
| `scripts/build_rapfi_teacher_policy_multisuppress_dataset.py` | text | 103 |
| `scripts/build_rapfi_teacher_scoregap.py` | text | 591 |
| `scripts/build_safety_block_candidate_manifest.py` | text | 434 |
| `scripts/build_teacher_divergence_retention_clean_v2_dataset.py` | text | 836 |
| `scripts/build_teacher_divergence_retention_dataset.py` | text | 579 |
| `scripts/build_teacher_divergence_retention_safety_v3_dataset.py` | text | 491 |
| `scripts/candidate_d_teacher_disagreement_census.py` | text | 703 |
| `scripts/candidate_i_rapfi_requery_census.py` | text | 694 |
| `scripts/candidate_i_smoke_failure_census.py` | text | 557 |
| `scripts/categorize_tactical_mid_failures.py` | text | 162 |
| `scripts/evaluate_candidate_g_policy.py` | text | 398 |
| `scripts/evaluate_candidate_h_value.py` | text | 295 |
| `scripts/evaluate_policy_rank_topk_gate.py` | text | 519 |
| `scripts/evaluate_rapfi_failure_set.py` | text | 363 |
| `scripts/evaluate_teacher_divergence_policy_probe_gates.py` | text | 345 |
| `scripts/extract_failure_board_snapshots.py` | text | 255 |
| `scripts/extract_rapfi_failure_positions.py` | text | 356 |
| `scripts/init_capacity_candidate_a_b6c64.py` | text | 112 |
| `scripts/init_capacity_candidate_b_b4c96.py` | text | 158 |
| `scripts/inspect_teacher_divergence_retention_sources.py` | text | 265 |
| `scripts/label_rapfi_failure_set.py` | text | 231 |
| `scripts/probe_policy_rank_topk_protected_nosave.py` | text | 319 |
| `scripts/probe_teacher_divergence_retention_dataset.py` | text | 358 |
| `scripts/run_15x15_rapfi_corpus.py` | text | 153 |
| `scripts/run_teacher_divergence_regression_gated_policy_probe.py` | text | 407 |
| `scripts/summarize_candidate_h_rapfi_smoke.py` | text | 196 |
| `scripts/train_candidate_g_policy_first_dry_run.py` | text | 824 |
| `scripts/train_candidate_g_teacher_policy.py` | text | 274 |
| `scripts/train_candidate_h_value_ranking.py` | text | 292 |
| `scripts/train_rapfi_failure_repair.py` | text | 453 |
| `scripts/train_rapfi_teacher_policy_margin.py` | text | 383 |
| `scripts/train_rapfi_teacher_policy_multisuppress_margin.py` | text | 125 |
| `scripts/train_rapfi_teacher_policy_rank_topk_probe.py` | text | 531 |
| `scripts/train_teacher_divergence_policy_anchor_probe.py` | text | 846 |
| `scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py` | text | 981 |
| `scripts/train_teacher_divergence_policy_probe.py` | text | 817 |
| `scripts/validate_teacher_divergence_retention_dataset.py` | text | 454 |
| `scripts/verify_candidate_h_c_export.py` | text | 367 |

## Interpretation

This audit is a first inventory pass. It does not decide final training eligibility.

The next step should inspect the parsed JSON/CSV sources with enough board, side, target, rank, suppress, teacher-eval, source-trace, and bucket coverage to decide which can feed an expanded teacher-divergence manifest.

Untracked local artifacts are intentionally excluded from this report so the committed audit remains reproducible from the repository state.

## Recommended next step

Open a manifest-design branch that selects concrete tracked sources from this inventory and defines deduplication keys.

Suggested branch:

`exp/15x15-teacher-divergence-expanded-manifest-design`

## Decision

Audit only.

No training, no checkpoint, no export, no public benchmark, no promotion.
