# Retention family materialized split

Scope: split artifact generation only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Inputs and outputs

- input proposal CSV: `analysis/integration_eval/retention_family_split_proposal.csv`
- output manifest CSV: `analysis/integration_eval/retention_family_materialized_split_manifest.csv`
- output JSON: `analysis/integration_eval/retention_family_materialized_split.json`

## Summary

- rows: 11
- families: 7
- materialized role counts: {'heldout_retention_gate': 1, 'heldout_retention_gate_review': 8, 'nonheldout_retention_anchor': 2}
- gate scope counts: {'external_or_family_level_only_not_sibling_only': 1, 'not_a_gate': 2, 'review_before_use_as_gate': 8}
- families needing non-heldout retention anchor: 1

## Critical sibling-conflict family

- family_id: `bd:ea22cc14729b88fd`
- targets: `10,7;7,10;7,9`
- role_counts: `heldout_retention_gate:1;nonheldout_retention_anchor:2`
- family_action: `use_nonheldout_anchor_plus_external_gate`
- Interpretation: 7,10 and 10,7 move to non-heldout retention anchors; 7,9 can remain a heldout gate, but not as the only sibling-family gate.

## Family summary

| family_id | rows | targets | role_counts | needs_anchor | has_gate | sibling_conflict | mixed_signal | safe_sibling_gates | family_action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bd:4e43e8574f31dd70 | 1 | 10,7 | heldout_retention_gate_review:1 | no | yes | no | no | 0 | keep_heldout_gate_or_review |
| bd:690e24eaa9cbf978 | 1 | 5,11 | heldout_retention_gate_review:1 | no | yes | no | no | 0 | keep_heldout_gate_or_review |
| bd:9af3d20c637fd30d | 1 | 8,6 | heldout_retention_gate_review:1 | no | yes | no | no | 0 | keep_heldout_gate_or_review |
| bd:a2b4f843dfbb182a | 1 | 8,6 | heldout_retention_gate_review:1 | no | yes | no | no | 0 | keep_heldout_gate_or_review |
| bd:ea22cc14729b88fd | 3 | 10,7;7,10;7,9 | heldout_retention_gate:1;nonheldout_retention_anchor:2 | yes | yes | yes | yes | 0 | use_nonheldout_anchor_plus_external_gate |
| bd:fa22a82f75e4b3c2 | 1 | 5,8 | heldout_retention_gate_review:1 | no | yes | no | no | 0 | keep_heldout_gate_or_review |
| bd:fcfbf3a577067568 | 3 | 10,9;7,9;8,10 | heldout_retention_gate_review:3 | no | yes | no | no | 0 | keep_heldout_gate_or_review |

## Row manifest

| idx | family_id | source | target | role | gate_scope | only_sibling_gate_ok | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bd:690e24eaa9cbf978 | b_mcts16_g1_m46_target_5_11_over_4_12 | 5,11 | heldout_retention_gate_review | review_before_use_as_gate | no | neutral/unknown signal; keep as heldout gate review |
| 2 | bd:4e43e8574f31dd70 | b_mcts16_g2_m19_target_10_7_over_7_11 | 10,7 | heldout_retention_gate_review | review_before_use_as_gate | no | neutral/unknown signal; keep as heldout gate review |
| 3 | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | 7,10 | nonheldout_retention_anchor | not_a_gate | no | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| 4 | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | 10,7 | nonheldout_retention_anchor | not_a_gate | no | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| 5 | bd:ea22cc14729b88fd | candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8 | 7,9 | heldout_retention_gate | external_or_family_level_only_not_sibling_only | no | stable top1 gain gate, but not valid as the only sibling-family heldout check |
| 6 | bd:fa22a82f75e4b3c2 | candidate_e_g2_m13_white_target_5_8_over_8_8 | 5,8 | heldout_retention_gate_review | review_before_use_as_gate | no | neutral/unknown signal; keep as heldout gate review |
| 7 | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10 | 7,9 | heldout_retention_gate_review | review_before_use_as_gate | no | neutral/unknown signal; keep as heldout gate review |
| 8 | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10 | 10,9 | heldout_retention_gate_review | review_before_use_as_gate | no | neutral/unknown signal; keep as heldout gate review |
| 9 | bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10 | 8,10 | heldout_retention_gate_review | review_before_use_as_gate | no | neutral/unknown signal; keep as heldout gate review |
| 10 | bd:a2b4f843dfbb182a | v12l_g2_m13_target_8_6_over_9_4 | 8,6 | heldout_retention_gate_review | review_before_use_as_gate | no | neutral/unknown signal; keep as heldout gate review |
| 11 | bd:9af3d20c637fd30d | v12l_g2_m15_target_8_6_over_6_6 | 8,6 | heldout_retention_gate_review | review_before_use_as_gate | no | neutral/unknown signal; keep as heldout gate review |

## Usage notes

- `nonheldout_retention_anchor` rows are intended to remain in the training/anchor side of the next split, not as heldout gates.
- `heldout_retention_gate` rows may be used as heldout checks only according to `gate_scope`.
- `external_or_family_level_only_not_sibling_only` means the row must not be the sole heldout evidence for a sibling target from the same family.
- `heldout_retention_gate_review` rows are retained as review candidates because the available proposal signal is neutral or unknown.
