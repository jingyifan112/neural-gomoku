# Teacher divergence / held-out retention dataset report

## Decision

Build dataset/manifest/report only. No training, no C export, and no public benchmark run was performed.

## Outputs

- Dataset: `analysis/integration_eval/teacher_divergence_retention_dataset.json`
- Manifest: `analysis/integration_eval/teacher_divergence_retention_manifest.csv`
- Report: `analysis/integration_eval/teacher_divergence_retention_report.md`

## Split rule

`heldout_retention` rows are regression/retention probes. They should be evaluated as held-out anchors, not consumed as train rows by default.

## Counts

- Included dataset rows: 36
- Manifest rows: 52
- Skipped rows: 16

### Split counts

| split | rows |
|---|---:|
| `train_teacher_divergence` | 25 |
| `heldout_retention` | 11 |

### Role counts

| role | rows |
|---|---:|
| `teacher_divergence` | 25 |
| `heldout_retention_anchor` | 11 |

### Bucket counts

| bucket | rows |
|---|---:|
| `priority_policy_gap_unavailable` | 13 |
| `priority_policy_numeric_gap` | 12 |
| `game2 move15 earlier fork-prevention repair candidate; true last_move included` | 3 |
| `diagnose game2 move17 earlier prevention of y=9 horizontal double threat` | 3 |
| `CE-only v12k raised target rank/prob but live C final stayed 9,4` | 1 |
| `CE-only v12k raised target rank/prob but live C final stayed 6,6` | 1 |
| `White should block/occupy 10,7 before Black's diagonal threat becomes decisive; B final was 7,11.` | 1 |
| `Black should block/occupy 5,11 before White's lower horizontal threat becomes decisive; B final was 4,12.` | 1 |
| `diagnose mcts16 final 5,8 versus mcts32/direct final 8,8 at game2 move13` | 1 |

## Included source counts

| source | rows |
|---|---:|
| `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json` | 25 |
| `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | 3 |
| `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | 3 |
| `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | 3 |
| `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | 1 |
| `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | 1 |

## Skipped rows

| reason | rows |
|---|---:|
| `duplicate_split_board_target` | 16 |

## Train teacher-divergence preview

| id | source_id | side | target | current_best | bucket | weight |
|---|---|---|---|---|---|---:|
| `tdiv_legacy_g1_m4` | `legacy_g1_m4` | black | `7,5` | `7,6` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g1_m6` | `legacy_g1_m6` | black | `7,8` | `6,6` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g1_m8` | `legacy_g1_m8` | black | `8,5` | `6,6` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g1_m40` | `legacy_g1_m40` | black | `12,6` | `5,8` | `priority_policy_gap_unavailable` | 1.5 |
| `tdiv_legacy_g2_m5` | `legacy_g2_m5` | white | `8,6` | `7,8` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g2_m7` | `legacy_g2_m7` | white | `5,6` | `6,5` | `priority_policy_gap_unavailable` | 1.5 |
| `tdiv_legacy_g2_m9` | `legacy_g2_m9` | white | `10,5` | `9,5` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g2_m11` | `legacy_g2_m11` | white | `9,7` | `6,5` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g2_m21` | `legacy_g2_m21` | white | `7,9` | `2,4` | `priority_policy_gap_unavailable` | 1.5 |
| `tdiv_legacy_g3_m4` | `legacy_g3_m4` | black | `5,6` | `8,8` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g3_m24` | `legacy_g3_m24` | black | `3,7` | `7,6` | `priority_policy_gap_unavailable` | 1.5 |
| `tdiv_legacy_g3_m26` | `legacy_g3_m26` | black | `6,3` | `7,6` | `priority_policy_gap_unavailable` | 1.5 |
| `tdiv_legacy_g4_m13` | `legacy_g4_m13` | white | `9,6` | `6,4` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g4_m17` | `legacy_g4_m17` | white | `10,6` | `9,9` | `priority_policy_gap_unavailable` | 1.5 |
| `tdiv_legacy_g4_m23` | `legacy_g4_m23` | white | `7,9` | `7,3` | `priority_policy_gap_unavailable` | 1.5 |
| `tdiv_legacy_g5_m6` | `legacy_g5_m6` | black | `8,6` | `9,8` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g5_m8` | `legacy_g5_m8` | black | `8,5` | `6,6` | `priority_policy_gap_unavailable` | 1.5 |
| `tdiv_legacy_g5_m12` | `legacy_g5_m12` | black | `8,9` | `6,6` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g5_m14` | `legacy_g5_m14` | black | `7,9` | `6,6` | `priority_policy_numeric_gap` | 2.0 |
| `tdiv_legacy_g5_m16` | `legacy_g5_m16` | black | `7,5` | `11,8` | `priority_policy_gap_unavailable` | 1.5 |

## Held-out retention preview

| id | source_id | side | target | bucket | source |
|---|---|---|---|---|---|
| `holdout_v12l_g2_m13_target_8_6_over_9_4` | `v12l_g2_m13_target_8_6_over_9_4` | white | `8,6` | `CE-only v12k raised target rank/prob but live C final stayed 9,4` | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` |
| `holdout_v12l_g2_m15_target_8_6_over_6_6` | `v12l_g2_m15_target_8_6_over_6_6` | white | `8,6` | `CE-only v12k raised target rank/prob but live C final stayed 6,6` | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` |
| `holdout_b_mcts16_g2_m19_target_10_7_over_7_11` | `b_mcts16_g2_m19_target_10_7_over_7_11` | white | `10,7` | `White should block/occupy 10,7 before Black's diagonal threat becomes decisive; B final was 7,11.` | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` |
| `holdout_b_mcts16_g1_m46_target_5_11_over_4_12` | `b_mcts16_g1_m46_target_5_11_over_4_12` | black | `5,11` | `Black should block/occupy 5,11 before White's lower horizontal threat becomes decisive; B final was 4,12.` | `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8` | `candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8` | white | `7,10` | `game2 move15 earlier fork-prevention repair candidate; true last_move included` | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8` | `candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8` | white | `10,7` | `game2 move15 earlier fork-prevention repair candidate; true last_move included` | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8` | `candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8` | white | `7,9` | `game2 move15 earlier fork-prevention repair candidate; true last_move included` | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` |
| `holdout_candidate_e_g2_m13_white_target_5_8_over_8_8` | `candidate_e_g2_m13_white_target_5_8_over_8_8` | white | `5,8` | `diagnose mcts16 final 5,8 versus mcts32/direct final 8,8 at game2 move13` | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10` | `candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10` | white | `7,9` | `diagnose game2 move17 earlier prevention of y=9 horizontal double threat` | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10` | `candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10` | white | `10,9` | `diagnose game2 move17 earlier prevention of y=9 horizontal double threat` | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10` | `candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10` | white | `8,10` | `diagnose game2 move17 earlier prevention of y=9 horizontal double threat` | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` |

## Next recommended gate before training

Before any training, run a small loader/probe that verifies every included row has a legal target, the side-to-move convention matches the current training code, and held-out rows remain excluded from train split.
