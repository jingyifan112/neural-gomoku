# Top3-sensitive manual decision audit

## Scope

- Branch: `exp/15x15-top3-sensitive-manual-decision-audit`
- Purpose: convert row-selection scores into explicit train/anchor/gate decisions.
- This is read-only decision/audit work.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Decision rule

- `protected_top3`, `top4_5`, and `top6_10` rows are protected rows: use as anchor/eval gate only.
- `trainable_rank_11_50` rows with `prior_regression_signal` and `train_side_candidate` are primary positive CE no-save probe candidates.
- `tail_rank_gt50` rows are tail eval guards only.
- `unknown` rows require schema review or exclusion.

## Summary

- total rows reviewed: `143`
- decision counts: `{'candidate_positive_ce_probe': 3, 'secondary_positive_ce_probe': 4, 'protect_as_anchor_or_gate': 60, 'tail_eval_guard_only': 15, 'hold_for_review': 28, 'exclude_or_schema_review': 33}`
- proposed use counts: `{'few_row_no_save_positive_ce': 3, 'backup_few_row_no_save_positive_ce': 4, 'anchor_or_eval_gate_only': 60, 'tail_eval_guard': 15, 'manual_review': 28, 'schema_review': 33}`

## Primary positive CE no-save candidates

| score | row_id | target | rank | bucket | role/label | reasons | source |
|---:|---|---|---:|---|---|---|---|
| 9 | `legacy_g2_m11` | `7,9` | 12 | `trainable_rank_11_50` | `neighbor` | `trainable_rank_11_50;prior_regression_signal;train_side_candidate;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g2_m21` | `9,7` | 47 | `trainable_rank_11_50` | `late_loss_window` | `trainable_rank_11_50;prior_regression_signal;train_side_candidate;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g5_m14` | `9,7` | 17 | `trainable_rank_11_50` | `first_losing_value` | `trainable_rank_11_50;prior_regression_signal;train_side_candidate;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |

## Protected anchor/gate rows

| score | row_id | target | rank | bucket | role/label | decision reason | source |
|---:|---|---|---:|---|---|---|---|
| 19 | `legacy_g5_m6` | `6,8` | 3 | `protected_top3` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; has prior regression signal, so it should be guarded explicitly; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 19 | `legacy_g5_m8` | `5,8` | 2 | `protected_top3` | `first_direct_vs_mcts_divergence` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; has prior regression signal, so it should be guarded explicitly; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 15 | `legacy_g1_m40` | `6,12` | 3 | `protected_top3` | `late_loss_window` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 15 | `legacy_g2_m9` | `5,10` | 3 | `protected_top3` | `first_losing_value;neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 15 | `legacy_g5_m16` | `5,7` | 2 | `protected_top3` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 13 | `legacy_g2_m5` | `6,8` | 5 | `top4_5` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; has prior regression signal, so it should be guarded explicitly; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 13 | `legacy_g3_m26` | `3,6` | 5 | `top4_5` | `late_loss_window` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; has prior regression signal, so it should be guarded explicitly; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 13 | `legacy_g4_m17` | `6,10` | 4 | `top4_5` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; has prior regression signal, so it should be guarded explicitly; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 12 | `legacy_g3_m4` | `6,5` | 9 | `top6_10` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; has prior regression signal, so it should be guarded explicitly; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 12 | `legacy_g6_m5` | `8,6` | 6 | `top6_10` | `first_losing_value` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage; has prior regression signal, so it should be guarded explicitly; high selection score confirms it is important, but not necessarily trainable` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g1_m4` | `5,7` | 4 | `top4_5` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g1_m6` | `8,7` | 4 | `top4_5` | `first_direct_vs_mcts_divergence` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g2_m7` | `6,5` | 4 | `top4_5` | `first_direct_vs_mcts_divergence;neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 8 | `legacy_g3_m24` | `7,3` | 7 | `top6_10` | `late_loss_window` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 8 | `legacy_g6_m19` | `5,9` | 7 | `top6_10` | `neighbor;late_loss_window` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 7 | `legacy_g1_m40` | `6,12` | 3 | `protected_top3` | `late_loss_window` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 7 | `legacy_g2_m9` | `5,10` | 3 | `protected_top3` | `first_losing_value;neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 7 | `legacy_g5_m16` | `5,7` | 2 | `protected_top3` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 7 | `legacy_g5_m6` | `6,8` | 3 | `protected_top3` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 7 | `legacy_g5_m8` | `5,8` | 2 | `protected_top3` | `first_direct_vs_mcts_divergence` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 6 | `legacy_g1_m4` | `5,7` | 4 | `top4_5` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 6 | `legacy_g1_m40` | `6,12` | 3 | `protected_top3` | `` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` |
| 6 | `legacy_g1_m40` | `6,12` | 3 | `protected_top3` | `` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` |
| 6 | `legacy_g1_m6` | `8,7` | 4 | `top4_5` | `first_direct_vs_mcts_divergence` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 6 | `legacy_g2_m5` | `6,8` | 5 | `top4_5` | `neighbor` | `already high-rank protected row; direct CE could overfit or destabilize protected coverage` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |

## Tail eval guards

| score | row_id | target | rank | bucket | role/label | source |
|---:|---|---|---:|---|---|---|
| 4 | `legacy_g5_m12` | `9,8` | 69 | `tail_rank_gt50` | `neighbor` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 0 | `legacy_g1_m8` | `5,8` | 102 | `tail_rank_gt50` | `neighbor` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 0 | `legacy_g1_m8` | `5,8` | 102 | `tail_rank_gt50` | `neighbor` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 0 | `legacy_g5_m12` | `9,8` | 69 | `tail_rank_gt50` | `neighbor` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 0 | `legacy_g5_m30` | `9,4` | 73 | `tail_rank_gt50` | `late_loss_window` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 0 | `legacy_g5_m30` | `9,4` | 73 | `tail_rank_gt50` | `late_loss_window` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| -1 | `legacy_g1_m8` | `5,8` | 102 | `tail_rank_gt50` | `` | `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` |
| -1 | `legacy_g1_m8` | `5,8` | 102 | `tail_rank_gt50` | `` | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` |
| -1 | `legacy_g5_m12` | `9,8` | 69 | `tail_rank_gt50` | `` | `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` |
| -1 | `legacy_g5_m12` | `9,8` | 69 | `tail_rank_gt50` | `` | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` |
| -1 | `legacy_g5_m30` | `9,4` | 73 | `tail_rank_gt50` | `` | `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` |
| -1 | `legacy_g5_m30` | `9,4` | 73 | `tail_rank_gt50` | `` | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` |
| -3 | `legacy_g1_m8` | `5,8` | 102 | `tail_rank_gt50` | `neighbor` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json` |
| -3 | `legacy_g5_m12` | `9,8` | 69 | `tail_rank_gt50` | `neighbor` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json` |
| -3 | `legacy_g5_m30` | `9,4` | 73 | `tail_rank_gt50` | `late_loss_window` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json` |

## Recommendation

The next executable step should be a tiny no-save probe, not a saved candidate. Use only the primary positive CE candidates as train rows, and require protected anchor/gate rows to have no top3/top5 regression. The recovered explicit-weight public baseline is `7.0/24`, so any later saved-candidate route must preserve or exceed that recovered baseline.

## Outputs

- `analysis/integration_eval/top3_sensitive_manual_decision_audit/manual_decision_report.md`
- `analysis/integration_eval/top3_sensitive_manual_decision_audit/manual_decision_manifest.csv`
- `analysis/integration_eval/top3_sensitive_manual_decision_audit/manual_decision_summary.json`
