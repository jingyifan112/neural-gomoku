# Retention family split proposal

Scope: proposal builder only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Inputs

- dataset_json: `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- eval_csvs:
  - `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_eval.csv`
  - `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_eval.csv`
  - `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w005_gated_eval.csv`
  - `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit.csv`
  - `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv`
  - `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_eval.csv`

## Summary

- heldout rows: 11
- families: 7
- repeated blocker rows: 2
- stable top1 gain rows: 1
- families needing non-heldout retention anchor: 1
- families keeping heldout gate directly/review: 6

## High-priority sibling-conflict family

- `bd:ea22cc14729b88fd` has targets `10,7;7,10;7,9`; recommendation: `add_nonheldout_retention_anchor_for_family`; heldout_gate_policy: `family_level_or_external_only`.

## Family-level proposal

| family_id | rows | targets | repeated_blocker | sibling_conflict | mixed_signal | stable_top1_gain | needs_nonheldout_anchor | heldout_gate_policy | recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bd:ea22cc14729b88fd | 3 | 10,7;7,10;7,9 | yes | yes | yes | yes | yes | family_level_or_external_only | add_nonheldout_retention_anchor_for_family |
| bd:4e43e8574f31dd70 | 1 | 10,7 | no | no | no | no | no | keep_heldout_gate_review | manual_review_before_next_probe |
| bd:690e24eaa9cbf978 | 1 | 5,11 | no | no | no | no | no | keep_heldout_gate_review | manual_review_before_next_probe |
| bd:9af3d20c637fd30d | 1 | 8,6 | no | no | no | no | no | keep_heldout_gate_review | manual_review_before_next_probe |
| bd:a2b4f843dfbb182a | 1 | 8,6 | no | no | no | no | no | keep_heldout_gate_review | manual_review_before_next_probe |
| bd:fa22a82f75e4b3c2 | 1 | 5,8 | no | no | no | no | no | keep_heldout_gate_review | manual_review_before_next_probe |
| bd:fcfbf3a577067568 | 3 | 10,9;7,9;8,10 | no | no | no | no | no | keep_heldout_gate_review | manual_review_before_next_probe |

## Row-level proposal

| family_id | source | target | evals | outcomes | repeated_blocker | stable_top1_gain | split_proposal | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bd:690e24eaa9cbf978 | b_mcts16_g1_m46_target_5_11_over_4_12 | 5,11 | 8 | neutral_or_unknown:8 | no | no | heldout_gate_review | neutral or insufficient signal |
| bd:4e43e8574f31dd70 | b_mcts16_g2_m19_target_10_7_over_7_11 | 10,7 | 8 | neutral_or_unknown:8 | no | no | heldout_gate_review | neutral or insufficient signal |
| bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | 7,10 | 8 | regression:8 | yes | no | nonheldout_retention_anchor_candidate | row regressed/repeated as heldout blocker |
| bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | 10,7 | 8 | regression:8 | yes | no | nonheldout_retention_anchor_candidate | row regressed/repeated as heldout blocker |
| bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8 | 7,9 | 8 | top1_gain:8 | no | yes | heldout_gate_candidate | stable top1 gain without regression in available evals |
| bd:fa22a82f75e4b3c2 | candidate_e_g2_m13_white_target_5_8_over_8_8 | 5,8 | 8 | neutral_or_unknown:8 | no | no | heldout_gate_review | neutral or insufficient signal |
| bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10 | 7,9 | 8 | neutral_or_unknown:8 | no | no | heldout_gate_review | neutral or insufficient signal |
| bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10 | 10,9 | 8 | neutral_or_unknown:8 | no | no | heldout_gate_review | neutral or insufficient signal |
| bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10 | 8,10 | 8 | neutral_or_unknown:8 | no | no | heldout_gate_review | neutral or insufficient signal |
| bd:a2b4f843dfbb182a | v12l_g2_m13_target_8_6_over_9_4 | 8,6 | 8 | neutral_or_unknown:8 | no | no | heldout_gate_review | neutral or insufficient signal |
| bd:9af3d20c637fd30d | v12l_g2_m15_target_8_6_over_6_6 | 8,6 | 8 | neutral_or_unknown:8 | no | no | heldout_gate_review | neutral or insufficient signal |

## Interpretation rule

- Families with sibling or mixed-signal conflict should not use one sibling target as the only heldout check for another sibling target.
- Rows proposed as `nonheldout_retention_anchor_candidate` are candidates for the next dataset split, not training actions in this branch.
- Rows proposed as `heldout_gate_candidate` can remain heldout gates unless a later manual review finds hidden source-family leakage.
