# Clean v2 teacher-divergence / held-out retention dataset report

This step only builds dataset/manifest/report artifacts. It does not train, export, benchmark, or modify model weights.

## Summary

- dataset rows: 39
- manifest rows: 109
- manifest included rows: 39
- manifest skipped/audit rows: 70

## Dataset split counts

| split | count |
|---|---:|
| train_teacher_divergence | 25 |
| heldout_retention | 11 |
| train_candidate | 3 |

## Dataset role counts

| role | count |
|---|---:|
| teacher_divergence | 28 |
| heldout_retention_anchor | 11 |

## Dataset bucket counts

| bucket | count |
|---|---:|
| priority_policy_gap_unavailable | 13 |
| priority_policy_numeric_gap | 12 |
| game2 move15 earlier fork-prevention repair candidate; true last_move included | 3 |
| diagnose game2 move17 earlier prevention of y=9 horizontal double threat | 3 |
| candidate_g_seed_teacher_divergence | 3 |
| Black should block/occupy 5,11 before White's lower horizontal threat becomes decisive; B final was 4,12. | 1 |
| White should block/occupy 10,7 before Black's diagonal threat becomes decisive; B final was 7,11. | 1 |
| diagnose mcts16 final 5,8 versus mcts32/direct final 8,8 at game2 move13 | 1 |
| CE-only v12k raised target rank/prob but live C final stayed 9,4 | 1 |
| CE-only v12k raised target rank/prob but live C final stayed 6,6 | 1 |

## Dataset source counts

| clean_v2_source | count |
|---|---:|
| canonical_baseline_dataset | 36 |
| candidate_g_seed_dataset | 3 |

## Source audit

| source_group | path | exists | rows_seen | rows_included | error |
|---|---|---:|---:|---:|---|
| canonical_baseline_dataset | `analysis/integration_eval/teacher_divergence_retention_dataset.json` | True | 36 | 36 |  |
| candidate_g_seed_dataset | `analysis/integration_eval/candidate_g_teacher_seed_dataset.json` | True | 14 | 3 |  |
| rapfi_scoregap_current_best | `analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv` | True | 32 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | True | 8 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | True | 3 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | True | 1 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | True | 3 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | True | 7 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | True | 5 | 0 |  |

## Included train candidates

| id | source_id | bucket | side | teacher | model/current_best | gap/rank | weight |
|---|---|---|---|---|---|---:|---:|
| `tdiv_candidate_g_g1_p22_black` | `g1_p22_black` | candidate_g_seed_teacher_divergence | black | `4,8` | `4,7` | 54 | 2.0 |
| `tdiv_candidate_g_g2_p15_white` | `g2_p15_white` | candidate_g_seed_teacher_divergence | white | `7,9` | `7,10` | 5 | 1.5 |
| `tdiv_candidate_g_g2_p17_white` | `g2_p17_white` | candidate_g_seed_teacher_divergence | white | `9,10` | `9,5` | 18 | 2.0 |

## Skipped score-gap rows

| source_id | skip_reason | teacher | model | gap |
|---|---|---|---|---:|
| `legacy_g1_m38` | model_matches_teacher | `12,8` | `12,8` | NA |
| `legacy_g1_m4` | duplicate_source_id_already_in_baseline_or_seed | `7,5` | `7,6` | 551 |
| `legacy_g1_m40` | duplicate_source_id_already_in_baseline_or_seed | `12,6` | `5,8` | NA |
| `legacy_g1_m6` | duplicate_source_id_already_in_baseline_or_seed | `7,8` | `6,6` | 446 |
| `legacy_g1_m8` | duplicate_source_id_already_in_baseline_or_seed | `8,5` | `6,6` | 338 |
| `legacy_g2_m11` | duplicate_source_id_already_in_baseline_or_seed | `9,7` | `6,5` | 100 |
| `legacy_g2_m19` | model_matches_teacher | `5,6` | `5,6` | NA |
| `legacy_g2_m21` | duplicate_source_id_already_in_baseline_or_seed | `7,9` | `2,4` | NA |
| `legacy_g2_m5` | duplicate_source_id_already_in_baseline_or_seed | `8,6` | `7,8` | 558 |
| `legacy_g2_m7` | duplicate_source_id_already_in_baseline_or_seed | `5,6` | `6,5` | NA |
| `legacy_g2_m9` | duplicate_source_id_already_in_baseline_or_seed | `10,5` | `9,5` | 275 |
| `legacy_g3_m2` | model_matches_teacher | `7,6` | `7,6` | 57 |
| `legacy_g3_m24` | duplicate_source_id_already_in_baseline_or_seed | `3,7` | `7,6` | NA |
| `legacy_g3_m26` | duplicate_source_id_already_in_baseline_or_seed | `6,3` | `7,6` | NA |
| `legacy_g3_m4` | duplicate_source_id_already_in_baseline_or_seed | `5,6` | `8,8` | 158 |
| `legacy_g4_m13` | duplicate_source_id_already_in_baseline_or_seed | `9,6` | `6,4` | 75 |
| `legacy_g4_m15` | model_matches_teacher | `6,4` | `6,4` | 339 |
| `legacy_g4_m17` | duplicate_source_id_already_in_baseline_or_seed | `10,6` | `9,9` | NA |
| `legacy_g4_m21` | model_matches_teacher | `10,8` | `10,8` | NA |
| `legacy_g4_m23` | duplicate_source_id_already_in_baseline_or_seed | `7,9` | `7,3` | NA |
| `legacy_g5_m10` | model_matches_teacher | `10,7` | `10,7` | 101 |
| `legacy_g5_m12` | duplicate_source_id_already_in_baseline_or_seed | `8,9` | `6,6` | 216 |
| `legacy_g5_m14` | duplicate_source_id_already_in_baseline_or_seed | `7,9` | `6,6` | 666 |
| `legacy_g5_m16` | duplicate_source_id_already_in_baseline_or_seed | `7,5` | `11,8` | NA |
| `legacy_g5_m28` | duplicate_source_id_already_in_baseline_or_seed | `5,11` | `5,4` | NA |
| `legacy_g5_m30` | duplicate_source_id_already_in_baseline_or_seed | `4,9` | `7,3` | NA |
| `legacy_g5_m6` | duplicate_source_id_already_in_baseline_or_seed | `8,6` | `9,8` | 11 |
| `legacy_g5_m8` | duplicate_source_id_already_in_baseline_or_seed | `8,5` | `6,6` | NA |
| `legacy_g6_m15` | model_matches_teacher | `4,8` | `4,8` | NA |
| `legacy_g6_m17` | duplicate_source_id_already_in_baseline_or_seed | `8,6` | `4,9` | NA |
| `legacy_g6_m19` | duplicate_source_id_already_in_baseline_or_seed | `9,5` | `7,9` | NA |
| `legacy_g6_m5` | duplicate_source_id_already_in_baseline_or_seed | `6,8` | `8,8` | 801 |

## Interpretation

- Canonical baseline rows come only from `teacher_divergence_retention_dataset.json`.
- Old manifest/probe/validation files are no longer treated as sample sources, avoiding double-counting.
- Score-gap rows are added only when Rapfi has a concrete teacher move, current-best disagrees, and the before-board file is available.
- Retention anchors are held out and should not be mixed into the teacher-divergence training split.

