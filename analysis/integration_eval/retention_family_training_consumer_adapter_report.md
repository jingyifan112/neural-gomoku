# Retention family training consumer adapter

Scope: consumer adapter dataset generation only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Inputs and outputs

- input dataset JSON: `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- input train manifest: `analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv`
- input eval manifest: `analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv`
- output train dataset JSON: `analysis/integration_eval/retention_family_training_consumer_adapter_train_dataset.json`
- output eval dataset JSON: `analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json`
- output adapter manifest CSV: `analysis/integration_eval/retention_family_training_consumer_adapter_manifest.csv`
- output summary JSON: `analysis/integration_eval/retention_family_training_consumer_adapter_summary.json`

## Summary

- source dataset rows: 44
- train manifest rows: 2
- eval manifest rows: 9
- adapted train rows: 2
- adapted eval rows: 9
- match counts: `{'yes': 11}`
- compat split counts: `{'heldout_retention': 9, 'train_candidate': 2}`
- validation errors: `[]`

## Critical family

- family_id: `bd:ea22cc14729b88fd`

| side | target | matched | compat_split | compat_role | gate_scope | only_sibling_gate_ok | risk_flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 7,10 | yes | train_candidate | nonheldout_retention_anchor | not_a_gate | no | critical_sibling_conflict_family |
| train | 10,7 | yes | train_candidate | nonheldout_retention_anchor | not_a_gate | no | critical_sibling_conflict_family |
| eval | 7,9 | yes | heldout_retention | heldout_retention_gate | external_or_family_level_only_not_sibling_only | no | critical_sibling_conflict_family;not_only_sibling_family_gate |

Interpretation:

- `7,10` and `10,7` are emitted on the train side as non-heldout retention anchor candidates.
- `7,9` is emitted on the eval side with restricted gate scope.
- The adapter preserves family metadata so the gated runner can enforce sibling-family restrictions.

## Adapter manifest

| side | family_id | source | target | matched | match_method | compat_split | compat_role | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | 7,10 | yes | source_target | train_candidate | nonheldout_retention_anchor | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| train | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | 10,7 | yes | source_target | train_candidate | nonheldout_retention_anchor | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| eval | bd:690e24eaa9cbf978 | b_mcts16_g1_m46_target_5_11_over_4_12 | 5,11 | yes | source_target | heldout_retention | heldout_retention_gate | neutral/unknown signal; keep as heldout gate review |
| eval | bd:9af3d20c637fd30d | v12l_g2_m15_target_8_6_over_6_6 | 8,6 | yes | source_target | heldout_retention | heldout_retention_gate | neutral/unknown signal; keep as heldout gate review |
| eval | bd:a2b4f843dfbb182a | v12l_g2_m13_target_8_6_over_9_4 | 8,6 | yes | source_target | heldout_retention | heldout_retention_gate | neutral/unknown signal; keep as heldout gate review |
| eval | bd:4e43e8574f31dd70 | b_mcts16_g2_m19_target_10_7_over_7_11 | 10,7 | yes | source_target | heldout_retention | heldout_retention_gate | neutral/unknown signal; keep as heldout gate review |
| eval | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10 | 7,9 | yes | source_target | heldout_retention | heldout_retention_gate | neutral/unknown signal; keep as heldout gate review |
| eval | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10 | 10,9 | yes | source_target | heldout_retention | heldout_retention_gate | neutral/unknown signal; keep as heldout gate review |
| eval | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10 | 8,10 | yes | source_target | heldout_retention | heldout_retention_gate | neutral/unknown signal; keep as heldout gate review |
| eval | bd:fa22a82f75e4b3c2 | candidate_e_g2_m13_white_target_5_8_over_8_8 | 5,8 | yes | source_target | heldout_retention | heldout_retention_gate | neutral/unknown signal; keep as heldout gate review |
| eval | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8 | 7,9 | yes | source_target | heldout_retention | heldout_retention_gate | stable top1 gain gate, but not valid as the only sibling-family heldout check |

## Consumer contract

- Future training commands may consume the train adapter JSON as train-side retention anchors.
- Future gate commands may consume the eval adapter JSON as eval/heldout gate rows.
- The eval adapter JSON alone does not make a promotion decision; gate results must still go through `scripts/run_retention_family_gated_training_probe.py`.
- `external_or_family_level_only_not_sibling_only` remains a hard restriction for critical-family gates.

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
