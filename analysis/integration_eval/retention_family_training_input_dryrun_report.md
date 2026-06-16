# Retention family training input dry-run

Scope: training-input manifest construction only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Inputs and outputs

- input applied split dry-run CSV: `analysis/integration_eval/retention_family_applied_split_dryrun_manifest.csv`
- output train manifest CSV: `analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv`
- output eval manifest CSV: `analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv`
- output summary JSON: `analysis/integration_eval/retention_family_training_input_dryrun_summary.json`

## Summary

- applied rows: 44
- train manifest rows: 2
- eval manifest rows: 9
- review/unmatched rows: 33
- bucket counts: `{'eval_gate_candidate': 1, 'eval_gate_review': 8, 'train_candidate': 2, 'unmatched_or_unchanged_review': 33}`
- train policy counts: `{'exclude_from_train_manifest': 42, 'include_as_nonheldout_retention_anchor_candidate': 2}`
- eval policy counts: `{'exclude_from_eval_manifest': 35, 'restricted_family_level_gate_candidate': 1, 'review_before_eval_gate_use': 8}`

## Critical sibling-conflict family validation

- family_id: `bd:ea22cc14729b88fd`
- validation: PASS

| target | bucket | train_policy | eval_policy | gate_scope | only_sibling_gate_ok | risk_flags |
| --- | --- | --- | --- | --- | --- | --- |
| 7,10 | train_candidate | include_as_nonheldout_retention_anchor_candidate | exclude_from_eval_manifest | not_a_gate | no | critical_sibling_conflict_family |
| 10,7 | train_candidate | include_as_nonheldout_retention_anchor_candidate | exclude_from_eval_manifest | not_a_gate | no | critical_sibling_conflict_family |
| 7,9 | eval_gate_candidate | exclude_from_train_manifest | restricted_family_level_gate_candidate | external_or_family_level_only_not_sibling_only | no | critical_sibling_conflict_family;not_only_sibling_family_gate |

Interpretation:

- `7,10` and `10,7` from the critical family are training-side retention anchor candidates.
- `7,9` remains eval-side only with restricted gate scope.
- The restricted `7,9` gate must not be the only sibling-family heldout check for `7,10` or `10,7`.

## Train manifest

| idx | family_id | source | target | train_policy | risk_flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| 9 | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | 7,10 | include_as_nonheldout_retention_anchor_candidate | critical_sibling_conflict_family | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| 10 | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | 10,7 | include_as_nonheldout_retention_anchor_candidate | critical_sibling_conflict_family | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |

## Eval manifest

| idx | family_id | source | target | eval_policy | gate_scope | only_sibling_gate_ok | risk_flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bd:690e24eaa9cbf978 | b_mcts16_g1_m46_target_5_11_over_4_12 | 5,11 | review_before_eval_gate_use | review_before_use_as_gate | no | review_required |
| 2 | bd:9af3d20c637fd30d | v12l_g2_m15_target_8_6_over_6_6 | 8,6 | review_before_eval_gate_use | review_before_use_as_gate | no | review_required |
| 3 | bd:a2b4f843dfbb182a | v12l_g2_m13_target_8_6_over_9_4 | 8,6 | review_before_eval_gate_use | review_before_use_as_gate | no | review_required |
| 4 | bd:4e43e8574f31dd70 | b_mcts16_g2_m19_target_10_7_over_7_11 | 10,7 | review_before_eval_gate_use | review_before_use_as_gate | no | review_required |
| 5 | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10 | 7,9 | review_before_eval_gate_use | review_before_use_as_gate | no | review_required |
| 6 | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10 | 10,9 | review_before_eval_gate_use | review_before_use_as_gate | no | review_required |
| 7 | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10 | 8,10 | review_before_eval_gate_use | review_before_use_as_gate | no | review_required |
| 8 | bd:fa22a82f75e4b3c2 | candidate_e_g2_m13_white_target_5_8_over_8_8 | 5,8 | review_before_eval_gate_use | review_before_use_as_gate | no | review_required |
| 11 | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8 | 7,9 | restricted_family_level_gate_candidate | external_or_family_level_only_not_sibling_only | no | critical_sibling_conflict_family;not_only_sibling_family_gate |

## Review / unmatched rows

| idx | family_id | source | target | bucket | risk_flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| 12 |  | g1_p22_black | 4,8 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 13 |  | g2_p15_white | 7,9 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 14 |  | g2_p17_white | 9,10 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 15 |  | safety_block_current_best_legacy_g1_m44 | 2,10 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 16 |  | safety_block_current_best_legacy_g1_m46 | 4,12 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 17 |  | safety_block_current_best_legacy_g1_m48 | 8,11 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 18 |  | safety_block_current_best_legacy_g2_m29 | 4,9 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 19 |  | safety_block_current_best_legacy_g2_m33 | 9,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 20 |  | legacy_g1_m40 | 12,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 21 |  | legacy_g2_m21 | 7,9 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 22 |  | legacy_g2_m7 | 5,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 23 |  | legacy_g3_m24 | 3,7 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 24 |  | legacy_g3_m26 | 6,3 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 25 |  | legacy_g4_m17 | 10,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 26 |  | legacy_g4_m23 | 7,9 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 27 |  | legacy_g5_m16 | 7,5 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 28 |  | legacy_g5_m28 | 5,11 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 29 |  | legacy_g5_m30 | 4,9 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 30 |  | legacy_g5_m8 | 8,5 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 31 |  | legacy_g6_m17 | 8,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 32 |  | legacy_g6_m19 | 9,5 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 33 |  | legacy_g1_m4 | 7,5 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 34 |  | legacy_g1_m6 | 7,8 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 35 |  | legacy_g1_m8 | 8,5 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 36 |  | legacy_g2_m11 | 9,7 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 37 |  | legacy_g2_m5 | 8,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 38 |  | legacy_g2_m9 | 10,5 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 39 |  | legacy_g3_m4 | 5,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 40 |  | legacy_g4_m13 | 9,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 41 |  | legacy_g5_m12 | 8,9 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 42 |  | legacy_g5_m14 | 7,9 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 43 |  | legacy_g5_m6 | 8,6 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |
| 44 |  | legacy_g6_m5 | 6,8 | unmatched_or_unchanged_review | unmatched_materialized_row;review_required | no materialized split row matched this dataset row |

## Consumer contract for future training script

- Only rows in `retention_family_training_input_dryrun_train_manifest.csv` may be considered training-side retention anchor candidates.
- Rows in `retention_family_training_input_dryrun_eval_manifest.csv` are eval/heldout candidates only according to `eval_use_policy` and `gate_scope`.
- `external_or_family_level_only_not_sibling_only` is a hard restriction: it must not be used as the sole heldout evidence for a sibling target in the same family.
- This artifact is not a training dataset approval; it is a dry-run contract for the next implementation step.

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
