# Teacher divergence / retention current-best probe

## Scope

Non-training probe only. This script loads current-best and computes policy rank/probability for each dataset target.

## Inputs

- Dataset: `analysis/integration_eval/teacher_divergence_retention_dataset.json`
- Checkpoint: `checkpoints/15x15_current_best.pt`
- Output CSV: `analysis/integration_eval/teacher_divergence_retention_probe.csv`

## Dataset summary

- Dataset rows: 36
- Split counts: `{'train_teacher_divergence': 25, 'heldout_retention': 11}`
- Role counts: `{'teacher_divergence': 25, 'heldout_retention_anchor': 11}`

## Probe summary

| split | rows | top1 | top3 | top5 | top10 | mean rank | median rank | mean target prob |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ALL` | 36 | 0/36 (0.000) | 7/36 (0.194) | 15/36 (0.417) | 22/36 (0.611) | 20.861 | 6.500 | 0.030492 |
| `heldout_retention` | 11 | 0/11 (0.000) | 2/11 (0.182) | 4/11 (0.364) | 7/11 (0.636) | 26.091 | 6.000 | 0.051526 |
| `train_teacher_divergence` | 25 | 0/25 (0.000) | 5/25 (0.200) | 11/25 (0.440) | 15/25 (0.600) | 18.560 | 7.000 | 0.021237 |

## Worst target ranks

| id | split | side | target | rank | prob | top move | top prob | reference move | reference kind | bucket |
|---|---|---|---|---:|---:|---|---:|---|---|---|
| `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10` | `heldout_retention` | white | `8,10` | 172 | 0.000001 | `9,10` | 0.370289 | `8,10` | `retention_anchor_target` | `diagnose game2 move17 earlier prevention of y=9 horizontal double threat` |
| `tdiv_legacy_g1_m8` | `train_teacher_divergence` | black | `8,5` | 102 | 0.000184 | `6,6` | 0.491384 | `6,6` | `current_best_direct_move` | `priority_policy_numeric_gap` |
| `tdiv_legacy_g5_m30` | `train_teacher_divergence` | black | `4,9` | 73 | 0.000220 | `7,3` | 0.399975 | `7,3` | `current_best_direct_move` | `priority_policy_gap_unavailable` |
| `tdiv_legacy_g5_m12` | `train_teacher_divergence` | black | `8,9` | 69 | 0.000395 | `6,6` | 0.476111 | `6,6` | `current_best_direct_move` | `priority_policy_numeric_gap` |
| `tdiv_legacy_g2_m21` | `train_teacher_divergence` | white | `7,9` | 47 | 0.000144 | `2,4` | 0.902918 | `2,4` | `current_best_direct_move` | `priority_policy_gap_unavailable` |
| `holdout_b_mcts16_g1_m46_target_5_11_over_4_12` | `heldout_retention` | black | `5,11` | 47 | 0.001009 | `10,7` | 0.374111 | `5,11` | `retention_anchor_target` | `Black should block/occupy 5,11 before White's lower horizontal threat becomes decisive; B final was 4,12.` |
| `tdiv_legacy_g4_m23` | `train_teacher_divergence` | white | `7,9` | 23 | 0.001522 | `7,3` | 0.441262 | `7,3` | `current_best_direct_move` | `priority_policy_gap_unavailable` |
| `holdout_v12l_g2_m15_target_8_6_over_6_6` | `heldout_retention` | white | `8,6` | 23 | 0.001043 | `6,6` | 0.588739 | `8,6` | `retention_anchor_target` | `CE-only v12k raised target rank/prob but live C final stayed 6,6` |
| `tdiv_legacy_g4_m13` | `train_teacher_divergence` | white | `9,6` | 21 | 0.000244 | `6,4` | 0.487796 | `6,4` | `current_best_direct_move` | `priority_policy_numeric_gap` |
| `tdiv_legacy_g5_m14` | `train_teacher_divergence` | black | `7,9` | 17 | 0.001940 | `6,6` | 0.471366 | `6,6` | `current_best_direct_move` | `priority_policy_numeric_gap` |
| `tdiv_legacy_g5_m28` | `train_teacher_divergence` | black | `5,11` | 17 | 0.003650 | `5,4` | 0.382124 | `5,4` | `current_best_direct_move` | `priority_policy_gap_unavailable` |
| `tdiv_legacy_g6_m17` | `train_teacher_divergence` | white | `8,6` | 15 | 0.002703 | `4,9` | 0.520009 | `4,9` | `current_best_direct_move` | `priority_policy_gap_unavailable` |
| `holdout_v12l_g2_m13_target_8_6_over_9_4` | `heldout_retention` | white | `8,6` | 13 | 0.000450 | `9,4` | 0.914306 | `8,6` | `retention_anchor_target` | `CE-only v12k raised target rank/prob but live C final stayed 9,4` |
| `tdiv_legacy_g2_m11` | `train_teacher_divergence` | white | `9,7` | 12 | 0.000325 | `6,5` | 0.422178 | `6,5` | `current_best_direct_move` | `priority_policy_numeric_gap` |
| `tdiv_legacy_g3_m4` | `train_teacher_divergence` | black | `5,6` | 9 | 0.007237 | `8,8` | 0.754454 | `8,8` | `current_best_direct_move` | `priority_policy_numeric_gap` |
| `tdiv_legacy_g3_m24` | `train_teacher_divergence` | black | `3,7` | 7 | 0.003180 | `7,6` | 0.951911 | `7,6` | `current_best_direct_move` | `priority_policy_gap_unavailable` |
| `tdiv_legacy_g6_m19` | `train_teacher_divergence` | white | `9,5` | 7 | 0.026256 | `7,9` | 0.545814 | `7,9` | `current_best_direct_move` | `priority_policy_gap_unavailable` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10` | `heldout_retention` | white | `10,9` | 7 | 0.007453 | `9,10` | 0.370289 | `10,9` | `retention_anchor_target` | `diagnose game2 move17 earlier prevention of y=9 horizontal double threat` |
| `tdiv_legacy_g6_m5` | `train_teacher_divergence` | white | `6,8` | 6 | 0.003630 | `8,8` | 0.854669 | `8,8` | `current_best_direct_move` | `priority_policy_numeric_gap` |
| `holdout_b_mcts16_g2_m19_target_10_7_over_7_11` | `heldout_retention` | white | `10,7` | 6 | 0.015358 | `9,10` | 0.433015 | `10,7` | `retention_anchor_target` | `White should block/occupy 10,7 before Black's diagonal threat becomes decisive; B final was 7,11.` |

## Held-out retention rows

| id | target | rank | prob | top move | top prob | top1 | top5 |
|---|---|---:|---:|---|---:|---|---|
| `holdout_v12l_g2_m13_target_8_6_over_9_4` | `8,6` | 13 | 0.000450 | `9,4` | 0.914306 | False | False |
| `holdout_v12l_g2_m15_target_8_6_over_6_6` | `8,6` | 23 | 0.001043 | `6,6` | 0.588739 | False | False |
| `holdout_b_mcts16_g2_m19_target_10_7_over_7_11` | `10,7` | 6 | 0.015358 | `9,10` | 0.433015 | False | False |
| `holdout_b_mcts16_g1_m46_target_5_11_over_4_12` | `5,11` | 47 | 0.001009 | `10,7` | 0.374111 | False | False |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8` | `7,10` | 4 | 0.055129 | `4,7` | 0.289357 | False | True |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8` | `10,7` | 2 | 0.152241 | `4,7` | 0.289357 | False | True |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8` | `7,9` | 5 | 0.046705 | `4,7` | 0.289357 | False | True |
| `holdout_candidate_e_g2_m13_white_target_5_8_over_8_8` | `5,8` | 6 | 0.025562 | `8,8` | 0.360782 | False | False |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10` | `7,9` | 2 | 0.261836 | `9,10` | 0.370289 | False | True |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10` | `10,9` | 7 | 0.007453 | `9,10` | 0.370289 | False | False |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10` | `8,10` | 172 | 0.000001 | `9,10` | 0.370289 | False | False |

## Interpretation guardrail

This report is descriptive only. It does not approve training. Held-out retention rows should remain excluded from train split.
