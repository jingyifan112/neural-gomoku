# Top3-sensitive no-save supervision row-selection audit

## Scope

- Branch: `exp/15x15-top3-sensitive-nosave-supervision-audit`
- Purpose: identify candidate rows for targeted top3-sensitive no-save supervision.
- This is read-only selection/audit work.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Context

- Current-best tactical_mid provenance has been recovered at `7.0/24` using explicit C weights.
- Prior no-save routes reported broad improvements but retained a top3 regression signal.
- This audit ranks candidate rows for manual review before any new no-save probe.

## Source inventory

| source | exists | rows | kind |
|---|---:|---:|---|
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | True | 25 | json |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json` | True | 10 | json |
| `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` | True | 25 | csv |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_summary.csv` | True | 9 | csv |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_summary.csv` | True | 6 | csv |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_group_metrics.csv` | True | 3 | csv |
| `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` | True | 25 | csv |
| `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` | True | 25 | csv |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/A1_stronger_anchor_balanced_hinge_group_metrics.csv` | True | 3 | csv |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/A2_light_worst_suppress_group_metrics.csv` | True | 3 | csv |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/A3_ce_dominant_rank_repair_group_metrics.csv` | True | 3 | csv |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/A4_tail_guard_group_metrics.csv` | True | 3 | csv |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/A5_tail_guard_downweight_group_metrics.csv` | True | 3 | csv |

## Summary

- candidate rows scanned: `143`
- protected/top10-ish rows: `60`
- text hits from prior reports: `90`
- rank bucket counts: `{'top4_5': 24, 'tail_rank_gt50': 15, 'protected_top3': 20, 'trainable_rank_11_50': 35, 'top6_10': 16, 'unknown': 33}`

## Top candidate rows

| score | row_id | target | rank | bucket | split/stage | role/label | reasons | source |
|---:|---|---|---:|---|---|---|---|---|
| 19 | `legacy_g5_m6` | `6,8` | 3 | `protected_top3` | `protected_top3` | `neighbor` | `protected_top3;mentions_top3;protected_or_anchor;prior_regression_signal;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 19 | `legacy_g5_m8` | `5,8` | 2 | `protected_top3` | `protected_top3` | `first_direct_vs_mcts_divergence` | `protected_top3;mentions_top3;protected_or_anchor;prior_regression_signal;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 15 | `legacy_g1_m40` | `6,12` | 3 | `protected_top3` | `protected_top3` | `late_loss_window` | `protected_top3;mentions_top3;protected_or_anchor;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 15 | `legacy_g2_m9` | `5,10` | 3 | `protected_top3` | `protected_top3` | `first_losing_value;neighbor` | `protected_top3;mentions_top3;protected_or_anchor;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 15 | `legacy_g5_m16` | `5,7` | 2 | `protected_top3` | `protected_top3` | `neighbor` | `protected_top3;mentions_top3;protected_or_anchor;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 13 | `legacy_g2_m5` | `6,8` | 5 | `top4_5` | `protected_top5` | `neighbor` | `near_top3_top4_5;protected_or_anchor;prior_regression_signal;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 13 | `legacy_g3_m26` | `3,6` | 5 | `top4_5` | `protected_top5` | `late_loss_window` | `near_top3_top4_5;protected_or_anchor;prior_regression_signal;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 13 | `legacy_g4_m17` | `6,10` | 4 | `top4_5` | `protected_top5` | `neighbor` | `near_top3_top4_5;protected_or_anchor;prior_regression_signal;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 12 | `legacy_g3_m4` | `6,5` | 9 | `top6_10` | `protected_top10` | `neighbor` | `near_top10;protected_or_anchor;prior_regression_signal;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 12 | `legacy_g6_m5` | `8,6` | 6 | `top6_10` | `protected_top10` | `first_losing_value` | `near_top10;protected_or_anchor;prior_regression_signal;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g1_m4` | `5,7` | 4 | `top4_5` | `protected_top5` | `neighbor` | `near_top3_top4_5;protected_or_anchor;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g1_m6` | `8,7` | 4 | `top4_5` | `protected_top5` | `first_direct_vs_mcts_divergence` | `near_top3_top4_5;protected_or_anchor;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g2_m7` | `6,5` | 4 | `top4_5` | `protected_top5` | `first_direct_vs_mcts_divergence;neighbor` | `near_top3_top4_5;protected_or_anchor;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g2_m11` | `7,9` | 12 | `trainable_rank_11_50` | `trainable_rank_11_50` | `neighbor` | `trainable_rank_11_50;prior_regression_signal;train_side_candidate;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g2_m21` | `9,7` | 47 | `trainable_rank_11_50` | `trainable_rank_11_50` | `late_loss_window` | `trainable_rank_11_50;prior_regression_signal;train_side_candidate;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 9 | `legacy_g5_m14` | `9,7` | 17 | `trainable_rank_11_50` | `trainable_rank_11_50` | `first_losing_value` | `trainable_rank_11_50;prior_regression_signal;train_side_candidate;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 8 | `legacy_g3_m24` | `7,3` | 7 | `top6_10` | `protected_top10` | `late_loss_window` | `near_top10;protected_or_anchor;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 8 | `legacy_g6_m19` | `5,9` | 7 | `top6_10` | `protected_top10` | `neighbor;late_loss_window` | `near_top10;protected_or_anchor;has_target;has_suppress` | `analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv` |
| 7 | `legacy_g1_m40` | `6,12` | 3 | `protected_top3` | `samples` | `late_loss_window` | `protected_top3;has_target;has_suppress` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 7 | `legacy_g2_m9` | `5,10` | 3 | `protected_top3` | `samples` | `first_losing_value;neighbor` | `protected_top3;has_target;has_suppress` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 7 | `legacy_g5_m16` | `5,7` | 2 | `protected_top3` | `samples` | `neighbor` | `protected_top3;has_target;has_suppress` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 7 | `legacy_g5_m6` | `6,8` | 3 | `protected_top3` | `samples` | `neighbor` | `protected_top3;has_target;has_suppress` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 7 | `legacy_g5_m8` | `5,8` | 2 | `protected_top3` | `samples` | `first_direct_vs_mcts_divergence` | `protected_top3;has_target;has_suppress` | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| 6 | `legacy_g1_m40` | `6,12` | 3 | `protected_top3` | `` | `` | `protected_top3;has_target` | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` |
| 6 | `legacy_g1_m40` | `6,12` | 3 | `protected_top3` | `` | `` | `protected_top3;has_target` | `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` |
| 6 | `legacy_g2_m9` | `5,10` | 3 | `protected_top3` | `` | `` | `protected_top3;has_target` | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` |
| 6 | `legacy_g2_m9` | `5,10` | 3 | `protected_top3` | `` | `` | `protected_top3;has_target` | `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` |
| 6 | `legacy_g5_m16` | `5,7` | 2 | `protected_top3` | `` | `` | `protected_top3;has_target` | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` |
| 6 | `legacy_g5_m16` | `5,7` | 2 | `protected_top3` | `` | `` | `protected_top3;has_target` | `analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv` |
| 6 | `legacy_g5_m6` | `6,8` | 3 | `protected_top3` | `` | `` | `protected_top3;has_target` | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` |

## Top3/no-save report hits

| file | line | text |
|---|---:|---|
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 3 | - decision: `CLOSEOUT_NO_SAVED_CANDIDATE_TOP3_WARNING` |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 14 | \| archived current-best \| 7.0/24 \| aspirational recovery target \| |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 15 | \| current local b6c64 baseline \| 2.0/24 \| reproducible local no-regression gate \| |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 16 | \| expanded public candidate \| 2.0/24 \| actual candidate public benchmark result \| |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 18 | The current local b6c64 runner does not reproduce the archived `7.0/24` current-best score. The reproducible local b6c64 baseline is `2.0/24`, and the expanded public candidate also scored `2.0/24`. |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 26 | \| protected KL guard rows \| 15 \| |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 31 | ## No-save sweep result |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 39 | \| observed top3 deltas \| `[-1]` \| |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 44 | All tested configs were soft passes only. They improved broad metrics but retained `top3_delta = -1`, so this route does not qualify for saved candidate creation. |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 52 | - No no-save config achieved `PASS_HARD_NO_SAVE`. |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 53 | - Every no-save config retained top3 regression. |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 54 | - Current local b6c64 baseline is only `2.0/24`, so public-benchmark recovery remains unresolved. |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 55 | - The archived `7.0/24` current-best score is not currently reproduced by the local b6c64 runner. |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 61 | 1. Add targeted positive supervision for the top3-sensitive teacher-divergence row and repeat no-save only; or |
| `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout/closeout_report.md` | 62 | 2. Audit/recover the archived current-best runner that produced `7.0/24`, then restart benchmark-preserving training from that reproducible baseline. |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 1 | # b4c96 no-save objective ablation run1 closeout |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 5 | `exp/15x15-b4c96-nosave-objective-ablation-run1` |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 9 | Run b4c96-safe no-save objective ablations after the capacity-data paired b4c96 candidate failed Stage C due to protected/objective regressions. |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 11 | This route uses the b4c96-safe no-save wrapper created in: |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 13 | `exp/15x15-b4c96-safe-nosave-ablation-wrapper` |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 17 | No-save ablation only. |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 23 | - Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json` |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 48 | - protected group lost top-5 coverage and target probability |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 58 | \| A1 \| protected_eval_top10 \| -1 \| +2 \| 0 \| -0.666667 \| -0.01157658 \| +0.911788 \| -0.108818 \| |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 59 | \| A1 \| tail_eval_rank_gt50 \| 0 \| -1 \| +2 \| +23.333333 \| -0.00579524 \| -1.014543 \| +1.280915 \| |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 61 | \| A2 \| protected_eval_top10 \| -1 \| +2 \| 0 \| -0.666667 \| -0.01157686 \| +0.911791 \| -0.108834 \| |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 62 | \| A2 \| tail_eval_rank_gt50 \| 0 \| -1 \| +2 \| +23.333333 \| -0.00579522 \| -1.014530 \| +1.280866 \| |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 64 | \| A3 \| protected_eval_top10 \| -1 \| +2 \| 0 \| -0.666667 \| -0.01157822 \| +0.911739 \| -0.108866 \| |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 65 | \| A3 \| tail_eval_rank_gt50 \| 0 \| -1 \| +2 \| +23.333333 \| -0.00579517 \| -1.014528 \| +1.280806 \| |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 69 | The unlocked b4c96-safe no-save wrapper works, but simple objective reweighting is not enough. |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 73 | - protected group should not lose top-5/top-10 coverage |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 85 | `B4C96_NOSAVE_OBJECTIVE_ABLATION_RUN1_ALL_FAIL_NO_CHECKPOINT` |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 95 | Build an adapter for A4/A5-style ablations before further no-save training: |
| `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_closeout.md` | 100 | - protected/tail hard-guard reporting |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 1 | # b4c96 tail-aware no-save ablation run2 closeout |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 5 | `exp/15x15-b4c96-tail-aware-nosave-ablation-run2` |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 9 | Run A4/A5 tail-aware no-save ablations after A1/A2/A3 objective-only reweighting failed. |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 11 | This route tests whether adding tail guard rows and severe-regression downweighting can prevent the protected/tail regressions observed in run1. |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 15 | No-save ablation only. |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 21 | - Wrapper: `scripts/probe_policy_rank_topk_protected_nosave_b4c96.py` |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 47 | \| A4 \| protected_eval_top10 \| -1 \| +2 \| 0 \| -0.666667 \| -0.01150738 \| +0.890207 \| -0.098539 \| |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 48 | \| A4 \| tail_eval_rank_gt50 \| 0 \| -1 \| +2 \| +22.333333 \| -0.00576096 \| -1.041146 \| +1.266028 \| |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 50 | \| A5 \| protected_eval_top10 \| -1 \| +2 \| 0 \| -0.666667 \| -0.01150805 \| +0.890158 \| -0.098536 \| |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 51 | \| A5 \| tail_eval_rank_gt50 \| 0 \| -1 \| +2 \| +22.333333 \| -0.00576089 \| -1.041126 \| +1.266004 \| |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 59 | - protected group still loses top-5 coverage |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 60 | - protected target probability still regresses by about `-0.0115` |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 75 | `B4C96_TAIL_AWARE_NOSAVE_ABLATION_RUN2_ALL_FAIL_NO_CHECKPOINT` |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 89 | - failure forensics identified protected/objective regressions |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 90 | - no-save objective ablation run1 failed |
| `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_closeout.md` | 91 | - tail-aware no-save ablation run2 failed |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 1 | # Policy-only rank/top-k protected no-save probe closeout |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 5 | `exp/15x15-policy-only-rank-topk-protected-nosave-probe` |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 9 | This branch ran a protected no-save probe only. |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 19 | The protected dataset split was: |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 22 | - protected_eval_top10: 15 rows |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 23 | - tail_eval_rank_gt50: 3 rows |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 42 | \| group \| rows \| top3_delta \| top5_delta \| top10_delta \| rank_gt50_delta \| mean_rank_delta \| target_prob_delta \| mean_worst_gap_delta \| hinge_delta \| beats_worst_delta \| beats_all_delta \| |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 45 | \| protected_eval_top10 \| 15 \| 0.000000 \| 0.000000 \| 1.000000 \| 0.000000 \| -0.466667 \| -0.01282100 \| 0.735103 \| -0.185786 \| -1.000000 \| -1.000000 \| |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 46 | \| tail_eval_rank_gt50 \| 3 \| 0.000000 \| 0.000000 \| 0.000000 \| 1.000000 \| 37.333333 \| -0.00009595 \| 0.497262 \| 0.558160 \| 0.000000 \| 0.000000 \| |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md` | 50 | The protected split partially improved the intended training group: |

## Recommendation

Do not train yet. First inspect the top scored rows and decide whether the target should be a positive CE row, a protected anchor, or an eval-only gate row. Any later training must use `--no-save` first and must gate against recovered `7.0/24` current-best provenance.

## Outputs

- `analysis/integration_eval/top3_sensitive_nosave_supervision_audit/source_inventory.csv`
- `analysis/integration_eval/top3_sensitive_nosave_supervision_audit/top3_related_report_hits.csv`
- `analysis/integration_eval/top3_sensitive_nosave_supervision_audit/top3_sensitive_row_selection_manifest.csv`
- `analysis/integration_eval/top3_sensitive_nosave_supervision_audit/top3_sensitive_row_selection_summary.json`
