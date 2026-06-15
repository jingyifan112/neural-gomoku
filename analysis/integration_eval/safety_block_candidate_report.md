# Safety-block candidate manifest report

This is a candidate manifest only. It does not train, export, benchmark, or modify model weights.

## Summary

- candidate rows: 36

### suggested split counts

| suggested_split | count |
|---|---:|
| train_candidate_candidate | 36 |

### role guess counts

| role_guess | count |
|---|---:|
| safety_block_teacher_candidate | 36 |

### eval family counts

| eval_family | count |
|---|---:|
| candidate_c_conservative | 12 |
| current_best | 12 |
| current_best_margin_3pair_b | 12 |

### snapshot family counts

| snapshot_family | count |
|---|---:|
| candidate_d_mcts32_nearend | 15 |
| b_mcts16 | 9 |
| candidate_c_mcts16 | 9 |
| candidate_d_move15_mcts16 | 3 |

## Source audit

| eval_path | rows | rows_with_expected_block | joined_candidates |
|---|---:|---:|---:|
| `analysis/integration_eval/current_best_rapfi_failure_eval.csv` | 7 | 5 | 12 |
| `analysis/integration_eval/candidate_c_conservative_rapfi_failure_eval.csv` | 7 | 5 | 12 |
| `analysis/integration_eval/current_best_margin_3pair_b_rapfi_failure_eval.csv` | 7 | 5 | 12 |

## Candidate rows

| split_guess | eval | snapshot | sample | side | target | expected | direct | final | direct_miss | top_miss | already_clean_v2 |
|---|---|---|---|---|---|---|---|---|---:|---:|---:|
| train_candidate_candidate | candidate_c_conservative | b_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_c_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_d_mcts32_nearend | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_d_move15_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | b_mcts16 | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_c_mcts16 | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_d_mcts32_nearend | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | b_mcts16 | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_c_mcts16 | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_d_mcts32_nearend | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_d_mcts32_nearend | `legacy_g2_m29` | white | `4,9` | `4,9` | `3,4` | `4,9` | True | True | False |
| train_candidate_candidate | candidate_c_conservative | candidate_d_mcts32_nearend | `legacy_g2_m33` | white | `9,6` | `9,11 9,6` | `10,8` | `9,6` | True | True | False |
| train_candidate_candidate | current_best | b_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | current_best | candidate_c_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | current_best | candidate_d_mcts32_nearend | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | current_best | candidate_d_move15_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | current_best | b_mcts16 | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | current_best | candidate_c_mcts16 | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | current_best | candidate_d_mcts32_nearend | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | current_best | b_mcts16 | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | current_best | candidate_c_mcts16 | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | current_best | candidate_d_mcts32_nearend | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | current_best | candidate_d_mcts32_nearend | `legacy_g2_m29` | white | `4,9` | `4,9` | `3,4` | `4,9` | True | True | False |
| train_candidate_candidate | current_best | candidate_d_mcts32_nearend | `legacy_g2_m33` | white | `9,6` | `9,11 9,6` | `10,8` | `9,6` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | b_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_c_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_d_mcts32_nearend | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_d_move15_mcts16 | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `2,10` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | b_mcts16 | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_c_mcts16 | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_d_mcts32_nearend | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `4,12` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | b_mcts16 | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_c_mcts16 | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_d_mcts32_nearend | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `8,11` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_d_mcts32_nearend | `legacy_g2_m29` | white | `4,9` | `4,9` | `3,4` | `4,9` | True | True | False |
| train_candidate_candidate | current_best_margin_3pair_b | candidate_d_mcts32_nearend | `legacy_g2_m33` | white | `9,6` | `9,11 9,6` | `10,8` | `9,6` | True | True | False |

## Interpretation

- `train_candidate_candidate`: candidate row where direct/top policy appears to miss an immediate-block target.
- `heldout_retention_candidate`: candidate row where logged final already matches the block; likely better as retention/probe unless policy target is separately justified.
- These rows should not be merged into clean v2 automatically. The next step is an acceptance filter for a narrow v3 candidate dataset.
