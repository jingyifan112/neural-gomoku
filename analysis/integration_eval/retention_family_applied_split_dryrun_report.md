# Retention family applied split dry-run

Scope: dry-run split application only. The input dataset was not modified. No training, checkpoint save, C export, benchmark, or promotion was run.

## Inputs and outputs

- input dataset JSON: `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- input materialized split manifest: `analysis/integration_eval/retention_family_materialized_split_manifest.csv`
- output dry-run manifest CSV: `analysis/integration_eval/retention_family_applied_split_dryrun_manifest.csv`
- output dry-run candidate JSON: `analysis/integration_eval/retention_family_applied_split_dryrun.json`

## Summary

- dataset rows: 44
- materialized split rows: 11
- matched materialized rows: 11
- unmatched materialized rows: 0
- proposed split counts: {'heldout_retention_gate': 1, 'heldout_retention_gate_review': 8, 'train_candidate': 8, 'train_retention_anchor': 2, 'train_teacher_divergence': 25}
- proposed role counts: {'heldout_retention_gate': 1, 'heldout_retention_gate_review': 8, 'nonheldout_retention_anchor': 2, 'teacher_divergence': 33}
- match method counts: {'row_key': 11, 'unmatched': 33}

## Critical sibling-conflict family application

| source | target | materialized_role | proposed_split | gate_scope | only_sibling_gate_ok | reason |
| --- | --- | --- | --- | --- | --- | --- |
| candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | 7,10 | nonheldout_retention_anchor | train_retention_anchor | not_a_gate | no | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | 10,7 | nonheldout_retention_anchor | train_retention_anchor | not_a_gate | no | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8 | 7,9 | heldout_retention_gate | heldout_retention_gate | external_or_family_level_only_not_sibling_only | no | stable top1 gain gate, but not valid as the only sibling-family heldout check |

## Family counts

| family_id | rows |
| --- | --- |
| bd:4e43e8574f31dd70 | 1 |
| bd:690e24eaa9cbf978 | 1 |
| bd:9af3d20c637fd30d | 1 |
| bd:a2b4f843dfbb182a | 1 |
| bd:ea22cc14729b88fd | 3 |
| bd:fa22a82f75e4b3c2 | 1 |
| bd:fcfbf3a577067568 | 3 |

## Applied row manifest

| idx | source | target | original_split | original_role | matched | family_id | materialized_role | proposed_split | gate_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | b_mcts16_g1_m46_target_5_11_over_4_12 | 5,11 | heldout_retention | heldout_retention_anchor | yes | bd:690e24eaa9cbf978 | heldout_retention_gate_review | heldout_retention_gate_review | review_before_use_as_gate |
| 2 | v12l_g2_m15_target_8_6_over_6_6 | 8,6 | heldout_retention | heldout_retention_anchor | yes | bd:9af3d20c637fd30d | heldout_retention_gate_review | heldout_retention_gate_review | review_before_use_as_gate |
| 3 | v12l_g2_m13_target_8_6_over_9_4 | 8,6 | heldout_retention | heldout_retention_anchor | yes | bd:a2b4f843dfbb182a | heldout_retention_gate_review | heldout_retention_gate_review | review_before_use_as_gate |
| 4 | b_mcts16_g2_m19_target_10_7_over_7_11 | 10,7 | heldout_retention | heldout_retention_anchor | yes | bd:4e43e8574f31dd70 | heldout_retention_gate_review | heldout_retention_gate_review | review_before_use_as_gate |
| 5 | candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10 | 7,9 | heldout_retention | heldout_retention_anchor | yes | bd:fcfbf3a577067568 | heldout_retention_gate_review | heldout_retention_gate_review | review_before_use_as_gate |
| 6 | candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10 | 10,9 | heldout_retention | heldout_retention_anchor | yes | bd:fcfbf3a577067568 | heldout_retention_gate_review | heldout_retention_gate_review | review_before_use_as_gate |
| 7 | candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10 | 8,10 | heldout_retention | heldout_retention_anchor | yes | bd:fcfbf3a577067568 | heldout_retention_gate_review | heldout_retention_gate_review | review_before_use_as_gate |
| 8 | candidate_e_g2_m13_white_target_5_8_over_8_8 | 5,8 | heldout_retention | heldout_retention_anchor | yes | bd:fa22a82f75e4b3c2 | heldout_retention_gate_review | heldout_retention_gate_review | review_before_use_as_gate |
| 9 | candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | 7,10 | heldout_retention | heldout_retention_anchor | yes | bd:ea22cc14729b88fd | nonheldout_retention_anchor | train_retention_anchor | not_a_gate |
| 10 | candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | 10,7 | heldout_retention | heldout_retention_anchor | yes | bd:ea22cc14729b88fd | nonheldout_retention_anchor | train_retention_anchor | not_a_gate |
| 11 | candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8 | 7,9 | heldout_retention | heldout_retention_anchor | yes | bd:ea22cc14729b88fd | heldout_retention_gate | heldout_retention_gate | external_or_family_level_only_not_sibling_only |
| 12 | g1_p22_black | 4,8 | train_candidate | teacher_divergence | no |  |  | train_candidate |  |
| 13 | g2_p15_white | 7,9 | train_candidate | teacher_divergence | no |  |  | train_candidate |  |
| 14 | g2_p17_white | 9,10 | train_candidate | teacher_divergence | no |  |  | train_candidate |  |
| 15 | safety_block_current_best_legacy_g1_m44 | 2,10 | train_candidate | teacher_divergence | no |  |  | train_candidate |  |
| 16 | safety_block_current_best_legacy_g1_m46 | 4,12 | train_candidate | teacher_divergence | no |  |  | train_candidate |  |
| 17 | safety_block_current_best_legacy_g1_m48 | 8,11 | train_candidate | teacher_divergence | no |  |  | train_candidate |  |
| 18 | safety_block_current_best_legacy_g2_m29 | 4,9 | train_candidate | teacher_divergence | no |  |  | train_candidate |  |
| 19 | safety_block_current_best_legacy_g2_m33 | 9,6 | train_candidate | teacher_divergence | no |  |  | train_candidate |  |
| 20 | legacy_g1_m40 | 12,6 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 21 | legacy_g2_m21 | 7,9 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 22 | legacy_g2_m7 | 5,6 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 23 | legacy_g3_m24 | 3,7 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 24 | legacy_g3_m26 | 6,3 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 25 | legacy_g4_m17 | 10,6 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 26 | legacy_g4_m23 | 7,9 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 27 | legacy_g5_m16 | 7,5 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 28 | legacy_g5_m28 | 5,11 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 29 | legacy_g5_m30 | 4,9 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 30 | legacy_g5_m8 | 8,5 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 31 | legacy_g6_m17 | 8,6 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 32 | legacy_g6_m19 | 9,5 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 33 | legacy_g1_m4 | 7,5 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 34 | legacy_g1_m6 | 7,8 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 35 | legacy_g1_m8 | 8,5 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 36 | legacy_g2_m11 | 9,7 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 37 | legacy_g2_m5 | 8,6 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 38 | legacy_g2_m9 | 10,5 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 39 | legacy_g3_m4 | 5,6 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 40 | legacy_g4_m13 | 9,6 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 41 | legacy_g5_m12 | 8,9 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 42 | legacy_g5_m14 | 7,9 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 43 | legacy_g5_m6 | 8,6 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |
| 44 | legacy_g6_m5 | 6,8 | train_teacher_divergence | teacher_divergence | no |  |  | train_teacher_divergence |  |

## Usage notes

- This dry-run file is a candidate split application artifact, not a training dataset approval.
- Rows with `proposed_split=train_retention_anchor` should be treated as non-heldout retention anchors in the next candidate split.
- Rows with `gate_scope=external_or_family_level_only_not_sibling_only` must not be used as the sole heldout evidence for a sibling target from the same family.
- Review unmatched materialized rows before using any generated split for training.
