# Teacher divergence / retention source audit

Purpose: inspect available source schemas before building a new dataset/manifest/report.

## Source summary

| path | kind | rows/length | notes |
|---|---:|---:|---|
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv` | csv | 32 | 32 columns |
| `analysis/public_benchmark_eval/rapfi_teacher_scoregap_model_comparison_corpus8_selected.csv` | csv | 32 | 44 columns |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv` | csv | 32 | 25 columns |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json` | json | 25 | first keys: id, source, board_size, win_length, game_number, move_count, side_to_move, board, policy_target, value_target, label_type, teacher_eval_before |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json` | json |  | top keys: name, description, source_dataset, samples, skipped |
| `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json` | json | 32 | first keys: game_number, move_count, side_to_move, value, direct, policy_safety, mcts_raw, mcts_safety, final, previous_rapfi_bestline, next_rapfi_bestline, board_snapshot_before_decision |
| `analysis/public_benchmark_eval/corpus8_selected_snapshot_targets.csv` | csv | 32 | 13 columns |
| `analysis/public_benchmark_eval/current_best_corpus8_selected_eval.csv` | csv | 32 | 24 columns |
| `analysis/public_benchmark_eval/current_best_failure_set_eval.csv` | csv | 7 | 24 columns |
| `analysis/integration_eval/candidate_i_rapfi_requery_census.csv` | csv | 25 | 48 columns |
| `analysis/integration_eval/candidate_i_smoke_failure_census.csv` | csv | 25 | 25 columns |
| `analysis/integration_eval/candidate_d_teacher_disagreement_census.csv` | csv | 44 | 31 columns |
| `analysis/integration_eval/candidate_g_teacher_seed_dataset.json` | json |  | top keys: name, purpose, source_manifest, source_debug_log, notes, summary, missing, side_mismatches, rows |
| `analysis/integration_eval/candidate_g_teacher_seed_manifest.json` | json |  | top keys: name, source_csv, purpose, notes, selection_counts, rows |
| `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | json | 5 | first keys: case_id, source, reason, game_number, move_count, board_size, win_length, side_to_move, current_player, target_xy, target_rc, suppress_xy |
| `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | json | 7 | first keys: case_id, source, reason, game_number, move_count, board_size, win_length, side_to_move, current_player, target_xy, target_rc, suppress_xy |
| `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | json | 8 | first keys: case_id, source, reason, game_number, move_count, board_size, win_length, side_to_move, current_player, target_xy, target_rc, suppress_xy |
| `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | json | 3 | first keys: case_id, source, reason, game_number, move_count, board_size, win_length, side_to_move, current_player, last_move_xy, last_move_rc, target_xy |
| `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | json | 1 | first keys: case_id, source, reason, game_number, move_count, board_size, win_length, side_to_move, current_player, last_move_xy, last_move_rc, target_xy |
| `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | json | 3 | first keys: case_id, source, reason, game_number, move_count, board_size, win_length, side_to_move, current_player, last_move_xy, last_move_rc, target_xy |

## CSV columns

### `analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `sample_id` | 32 | 32 | 'legacy_g1_m4' |
| `game_number` | 32 | 6 | '1' |
| `move_count` | 32 | 24 | '4' |
| `side_to_move` | 32 | 2 | 'black' |
| `labeled_failure_type` | 32 | 8 | 'neighbor' |
| `logged_final` | 32 | 25 | '7,6' |
| `model_direct_move` | 32 | 21 | '7,6' |
| `model_direct_prob` | 32 | 32 | '0.727427' |
| `model_value_estimate` | 32 | 32 | '0.398955' |
| `model_direct_apply_status` | 32 | 1 | 'ok' |
| `rapfi_best_move_before` | 32 | 24 | '7,5' |
| `rapfi_eval_before` | 24 | 18 | '120' |
| `rapfi_pv_before` | 24 | 23 | 'H6 J8' |
| `rapfi_query_status_before` | 32 | 1 | 'concrete_move' |
| `model_matches_rapfi_best_before` | 32 | 2 | 'False' |
| `rapfi_best_move_after_model` | 32 | 22 | '7,5' |
| `rapfi_eval_after_model_next_player_pov` | 24 | 19 | '431' |
| `rapfi_pv_after_model` | 24 | 23 | 'H6 H9' |
| `rapfi_query_status_after_model` | 32 | 1 | 'concrete_move' |
| `provisional_root_pov_gap_best_minus_model` | 15 | 15 | '551' |
| `rapfi_before_attempts` | 32 | 1 | '1' |
| `rapfi_after_attempts` | 32 | 1 | '1' |
| `rapfi_before_elapsed_ms` | 32 | 12 | '1061' |
| `rapfi_after_elapsed_ms` | 32 | 10 | '1062' |
| `rapfi_before_depth` | 32 | 1 | '2' |
| `rapfi_after_depth` | 32 | 1 | '2' |
| `rapfi_before_query_file` | 32 | 32 | 'analysis/public_benchmark_eval/rapfi_teacher_scoregap_boards/000_legacy_g1_m4_before.attempt1.board' |
| `rapfi_after_query_file` | 32 | 32 | 'analysis/public_benchmark_eval/rapfi_teacher_scoregap_boards/000_legacy_g1_m4_after_model.attempt1.board' |
| `rapfi_before_raw_output` | 32 | 32 | 'analysis/public_benchmark_eval/rapfi_teacher_scoregap_boards/000_legacy_g1_m4_before.rapfi.out' |
| `rapfi_after_raw_output` | 32 | 32 | 'analysis/public_benchmark_eval/rapfi_teacher_scoregap_boards/000_legacy_g1_m4_after_model.rapfi.out' |
| `rapfi_before_stdout_excerpt` | 32 | 32 | 'MESSAGE Speed 82000 \| Depth 2-3 \| Eval 120 \| Node 82 \| Time 0ms \|\| MESSAGE Bestline H6 J8 \|\| 7,5' |
| `rapfi_after_stdout_excerpt` | 32 | 31 | 'MESSAGE Speed 95000 \| Depth 2-5 \| Eval 431 \| Node 95 \| Time 0ms \|\| MESSAGE Bestline H6 H9 \|\| 7,5' |

### `analysis/public_benchmark_eval/rapfi_teacher_scoregap_model_comparison_corpus8_selected.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `sample_id` | 32 | 32 | 'legacy_g1_m38' |
| `game_number` | 32 | 6 | '1' |
| `move_count` | 32 | 24 | '38' |
| `side_to_move` | 32 | 2 | 'black' |
| `labeled_failure_type` | 32 | 8 | 'late_loss_window' |
| `current_best_logged_final` | 32 | 25 | '12,8' |
| `rapfi_best_move_before_current_best_query` | 32 | 24 | '12,8' |
| `rapfi_eval_before_current_best_query` | 24 | 18 | '120' |
| `rapfi_pv_before_current_best_query` | 24 | 23 | 'H6 J8' |
| `rapfi_query_status_before_current_best_query` | 32 | 1 | 'concrete_move' |
| `current_best_model_direct_move` | 32 | 21 | '12,8' |
| `current_best_model_direct_prob` | 32 | 32 | '0.386038' |
| `current_best_model_value_estimate` | 32 | 32 | '0.358879' |
| `current_best_model_matches_rapfi_best_before` | 32 | 2 | 'True' |
| `current_best_provisional_root_pov_gap_best_minus_model` | 15 | 15 | '551.0' |
| `current_best_rapfi_best_move_before` | 32 | 24 | '12,8' |
| `current_best_rapfi_eval_before` | 24 | 18 | '120' |
| `current_best_rapfi_eval_after_model_next_player_pov` | 24 | 19 | '+M3' |
| `current_best_rapfi_query_status_before` | 32 | 1 | 'concrete_move' |
| `current_best_rapfi_query_status_after_model` | 32 | 1 | 'concrete_move' |
| `candidate_g_model_direct_move` | 32 | 19 | '9,7' |
| `candidate_g_model_direct_prob` | 32 | 32 | '0.67541' |
| `candidate_g_model_value_estimate` | 32 | 32 | '-0.28636' |
| `candidate_g_model_matches_rapfi_best_before` | 32 | 2 | 'False' |
| `candidate_g_provisional_root_pov_gap_best_minus_model` | 13 | 13 | '551.0' |
| `candidate_g_rapfi_best_move_before` | 32 | 24 | '12,8' |
| `candidate_g_rapfi_eval_before` | 24 | 18 | '120' |
| `candidate_g_rapfi_eval_after_model_next_player_pov` | 23 | 18 | '431' |
| `candidate_g_rapfi_query_status_before` | 32 | 1 | 'concrete_move' |
| `candidate_g_rapfi_query_status_after_model` | 32 | 1 | 'concrete_move' |
| `candidate_h_model_direct_move` | 32 | 19 | '9,7' |
| `candidate_h_model_direct_prob` | 32 | 32 | '0.67541' |
| `candidate_h_model_value_estimate` | 32 | 32 | '-0.176947' |
| `candidate_h_model_matches_rapfi_best_before` | 32 | 2 | 'False' |
| `candidate_h_provisional_root_pov_gap_best_minus_model` | 13 | 13 | '551.0' |
| `candidate_h_rapfi_best_move_before` | 32 | 24 | '12,8' |
| `candidate_h_rapfi_eval_before` | 24 | 18 | '120' |
| `candidate_h_rapfi_eval_after_model_next_player_pov` | 23 | 18 | '431' |
| `candidate_h_rapfi_query_status_before` | 32 | 1 | 'concrete_move' |
| `candidate_h_rapfi_query_status_after_model` | 32 | 1 | 'concrete_move' |
| `candidate_g_match_delta_vs_current_best` | 32 | 3 | '-1' |
| `candidate_g_numeric_gap_delta_vs_current_best` | 13 | 7 | '0.0' |
| `candidate_h_match_delta_vs_current_best` | 32 | 3 | '-1' |
| `candidate_h_numeric_gap_delta_vs_current_best` | 13 | 7 | '0.0' |

### `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `sample_id` | 32 | 32 | 'legacy_g1_m4' |
| `game_number` | 32 | 6 | '1' |
| `move_count` | 32 | 24 | '4' |
| `side_to_move` | 32 | 2 | 'black' |
| `labeled_failure_type` | 32 | 8 | 'neighbor' |
| `teacher_move` | 32 | 24 | '7,5' |
| `teacher_eval_before` | 24 | 18 | '120' |
| `teacher_eval_kind` | 24 | 2 | 'numeric' |
| `teacher_pv_before` | 24 | 23 | 'H6 J8' |
| `teacher_query_status` | 32 | 1 | 'concrete_move' |
| `teacher_move_stable_across_runs` | 32 | 1 | 'True' |
| `current_best_direct_move` | 32 | 21 | '7,6' |
| `current_best_direct_prob` | 32 | 32 | '0.727427' |
| `current_best_value_estimate` | 32 | 32 | '0.398955' |
| `current_best_matches_teacher` | 32 | 2 | 'False' |
| `provisional_root_pov_gap_best_minus_model` | 15 | 15 | '551.0' |
| `numeric_gap_available` | 32 | 2 | 'True' |
| `numeric_gap_value` | 15 | 15 | '551.0' |
| `policy_candidate` | 32 | 1 | 'True' |
| `priority_candidate` | 32 | 2 | 'True' |
| `numeric_gap_candidate` | 32 | 2 | 'True' |
| `value_regression_candidate` | 32 | 1 | 'False' |
| `suggested_bucket` | 32 | 3 | 'priority_policy_numeric_gap' |
| `teacher_move_candidate_g_run` | 32 | 24 | '7,5' |
| `teacher_move_candidate_h_run` | 32 | 24 | '7,5' |

### `analysis/public_benchmark_eval/corpus8_selected_snapshot_targets.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `game_number` | 32 | 6 | '1' |
| `move_count` | 32 | 24 | '4' |
| `side_to_move` | 32 | 2 | 'black' |
| `value` | 32 | 32 | '0.319195' |
| `direct` | 32 | 19 | '7,6' |
| `policy_safety` | 32 | 26 | '7,6' |
| `mcts_raw` | 32 | 22 | '7,6' |
| `mcts_safety` | 32 | 25 | '7,6' |
| `final` | 32 | 25 | '7,6' |
| `previous_rapfi_bestline` | 31 | 27 | 'J6' |
| `next_rapfi_bestline` | 0 | 0 |  |
| `failure_type` | 32 | 8 | 'neighbor' |
| `notes` | 32 | 31 | 'neural_move=7,6; direct=7,6; policy_safety=7,6; mcts_raw=7,6; final=7,6; reason=neighbor' |

### `analysis/public_benchmark_eval/current_best_corpus8_selected_eval.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `sample_id` | 32 | 32 | 'legacy_g1_m4' |
| `game_number` | 32 | 6 | '1' |
| `move_count` | 32 | 24 | '4' |
| `side_to_move` | 32 | 2 | 'black' |
| `opponent` | 32 | 2 | 'white' |
| `label_type` | 0 | 0 |  |
| `value_target` | 0 | 0 |  |
| `policy_target` | 0 | 0 |  |
| `labeled_failure_type` | 32 | 8 | 'neighbor' |
| `logged_value` | 32 | 32 | '0.319195' |
| `model_value_estimate` | 32 | 32 | '0.398955' |
| `direct_policy_top_move` | 32 | 21 | '7,6' |
| `direct_policy_top_prob` | 32 | 32 | '0.727427' |
| `direct_blocks_opponent_immediate_win` | 32 | 2 | 'False' |
| `expected_blocking_moves` | 13 | 13 | '12,8' |
| `opponent_immediate_winning_moves` | 13 | 13 | '12,8' |
| `current_player_immediate_winning_moves` | 0 | 0 |  |
| `logged_direct` | 32 | 19 | '7,6' |
| `logged_policy_safety` | 32 | 26 | '7,6' |
| `logged_mcts_raw` | 32 | 22 | '7,6' |
| `logged_mcts_safety` | 32 | 25 | '7,6' |
| `logged_final` | 32 | 25 | '7,6' |
| `logged_final_blocks_immediate_win` | 1 | 1 | 'False' |
| `preliminary_failure_type` | 1 | 1 | 'needs_manual_review' |

### `analysis/public_benchmark_eval/current_best_failure_set_eval.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `sample_id` | 7 | 7 | 'legacy_g1_m38' |
| `game_number` | 7 | 2 | '1' |
| `move_count` | 7 | 7 | '38' |
| `side_to_move` | 7 | 2 | 'black' |
| `opponent` | 7 | 2 | 'white' |
| `label_type` | 0 | 0 |  |
| `value_target` | 0 | 0 |  |
| `policy_target` | 0 | 0 |  |
| `labeled_failure_type` | 7 | 5 | 'pre_threat_setup_review' |
| `logged_value` | 7 | 7 | '0.210098' |
| `model_value_estimate` | 7 | 7 | '0.242752' |
| `direct_policy_top_move` | 7 | 4 | '7,8' |
| `direct_policy_top_prob` | 7 | 7 | '0.168786' |
| `direct_blocks_opponent_immediate_win` | 7 | 1 | 'False' |
| `expected_blocking_moves` | 5 | 5 | '2,10' |
| `opponent_immediate_winning_moves` | 5 | 5 | '2,10' |
| `current_player_immediate_winning_moves` | 0 | 0 |  |
| `logged_direct` | 7 | 5 | '7,11' |
| `logged_policy_safety` | 7 | 7 | '3,8' |
| `logged_mcts_raw` | 7 | 7 | '8,6' |
| `logged_mcts_safety` | 7 | 7 | '3,8' |
| `logged_final` | 7 | 7 | '3,8' |
| `logged_final_blocks_immediate_win` | 7 | 2 | 'False' |
| `preliminary_failure_type` | 7 | 3 | 'needs_manual_review' |

### `analysis/integration_eval/candidate_i_rapfi_requery_census.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `game_id` | 25 | 2 | '1' |
| `ply` | 25 | 25 | '0' |
| `priority` | 25 | 5 | 'context' |
| `side_to_move` | 25 | 2 | 'black:neural' |
| `candidate_h_move` | 25 | 23 | '7,7' |
| `rapfi_requery_best_move` | 11 | 11 | '7,7' |
| `rapfi_return_status` | 25 | 2 | 'concrete_move' |
| `rapfi_returned_concrete_move` | 25 | 2 | 'True' |
| `rapfi_no_move_diagnosis` | 25 | 2 | 'concrete_move' |
| `rapfi_attempts` | 25 | 2 | '1' |
| `rapfi_attempt_plan` | 25 | 2 | 'd2:10000ms' |
| `rapfi_recovered_by_retry` | 25 | 1 | 'False' |
| `rapfi_elapsed_ms` | 25 | 12 | '108' |
| `rapfi_return_code` | 25 | 1 | '-15' |
| `agreement` | 25 | 2 | 'True' |
| `usable_teacher_label` | 25 | 2 | 'True' |
| `valid_teacher_disagreement` | 25 | 2 | 'False' |
| `low_policy_visibility_agreement` | 25 | 2 | 'False' |
| `board_reconstruction_valid` | 25 | 1 | 'True' |
| `board_terminal_before_query` | 25 | 1 | 'False' |
| `legal_moves_before_query` | 25 | 25 | '225' |
| `candidate_d_baseline_move` | 5 | 5 | '5,8' |
| `candidate_h_policy_rank` | 25 | 6 | '1' |
| `rapfi_move_policy_rank_under_h` | 11 | 5 | '1' |
| `candidate_h_policy_prob` | 25 | 25 | '0.894338' |
| `rapfi_move_policy_prob` | 11 | 11 | '0.894338' |
| `policy_probability_gap_teacher_minus_candidate` | 11 | 2 | '0.000000' |
| `root_value` | 25 | 25 | '0.028283' |
| `candidate_child_value` | 25 | 25 | '0.931547' |
| `rapfi_child_value` | 11 | 11 | '0.931547' |
| `child_value_gap_teacher_minus_candidate` | 11 | 2 | '0.000000' |
| `candidate_h_move_safety_pass` | 25 | 1 | 'True' |
| `rapfi_move_safety_pass` | 11 | 1 | 'True' |
| `rapfi_score` | 14 | 11 | '89' |
| `rapfi_pv` | 0 | 0 |  |
| `rapfi_timed_out` | 25 | 2 | 'False' |
| `rapfi_depth` | 25 | 1 | '2' |
| `rapfi_timeout_ms` | 25 | 2 | '10000' |
| `classification` | 25 | 7 | 'matches_rapfi_teacher' |
| `top_policy_moves` | 25 | 25 | '7,7:0.894338 8,4:0.009967 8,6:0.008876 6,7:0.006532 10,7:0.003965' |
| `board_query_file` | 25 | 25 | 'analysis/integration_eval/candidate_i_rapfi_requery_boards/g1_p0.attempt1.board' |
| `rapfi_raw_output` | 25 | 25 | 'analysis/integration_eval/candidate_i_rapfi_requery_boards/g1_p0.rapfi.out' |
| `rapfi_stderr_output` | 25 | 25 | 'analysis/integration_eval/candidate_i_rapfi_requery_boards/g1_p0.rapfi.err' |
| `rapfi_stdout_line_count` | 25 | 1 | '2' |
| `rapfi_stderr_line_count` | 25 | 1 | '0' |
| `rapfi_stdout_excerpt` | 25 | 22 | 'OK \|\| 7,7' |
| `rapfi_stderr_excerpt` | 0 | 0 |  |
| `notes` | 14 | 3 | 'game1 smoke loss' |

### `analysis/integration_eval/candidate_i_smoke_failure_census.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `game_id` | 25 | 2 | '1' |
| `ply` | 25 | 25 | '0' |
| `side_to_move` | 25 | 2 | 'black:neural' |
| `candidate_h_move` | 25 | 23 | '7,7' |
| `candidate_d_baseline_move` | 5 | 5 | '5,8' |
| `rapfi_teacher_move` | 10 | 10 | '4,5' |
| `teacher_source` | 25 | 2 | 'unavailable' |
| `candidate_h_policy_rank` | 25 | 6 | '1' |
| `teacher_policy_rank_under_h` | 10 | 4 | '1' |
| `candidate_h_policy_prob` | 25 | 25 | '0.894338' |
| `teacher_policy_prob` | 10 | 10 | '0.704813' |
| `policy_probability_gap_teacher_minus_candidate` | 10 | 1 | '0.000000' |
| `root_value` | 25 | 25 | '0.028283' |
| `logged_root_value` | 25 | 25 | '0.028283' |
| `candidate_child_value` | 25 | 25 | '0.931547' |
| `teacher_child_value` | 10 | 10 | '0.843044' |
| `child_value_gap_teacher_minus_candidate` | 10 | 1 | '0.000000' |
| `candidate_h_move_safety_pass` | 25 | 1 | 'True' |
| `teacher_move_safety_pass` | 10 | 1 | 'True' |
| `previous_rapfi_bestline` | 23 | 22 | 'E5' |
| `short_continuation_result` | 25 | 2 | 'White win by five connection' |
| `classification` | 25 | 6 | 'context' |
| `top_policy_moves` | 25 | 25 | '7,7:0.894338 8,4:0.009967 8,6:0.008876 6,7:0.006532 10,7:0.003965' |
| `board_position` | 25 | 25 | '.............../.............../.............../.............../.............../.............../.............../.............../.............../............... |
| `notes` | 14 | 3 | 'game1 smoke loss' |

### `analysis/integration_eval/candidate_d_teacher_disagreement_census.csv`

| column | nonempty | unique | example |
|---|---:|---:|---|
| `game` | 44 | 2 | '1' |
| `ply` | 44 | 44 | '0' |
| `side` | 44 | 2 | 'black' |
| `model_move` | 44 | 38 | '7,7' |
| `teacher_move` | 44 | 37 | '7,7' |
| `teacher_move_policy_rank` | 44 | 22 | '1' |
| `model_move_policy_rank` | 44 | 10 | '1' |
| `teacher_policy_prob` | 44 | 44 | '0.9767210483551025' |
| `model_policy_prob` | 44 | 44 | '0.9767210483551025' |
| `policy_probability_gap_teacher_minus_model` | 44 | 22 | '0.0' |
| `policy_logit_gap_teacher_minus_model` | 44 | 22 | '0.0' |
| `value_current_position` | 44 | 44 | '0.3196517527103424' |
| `value_original_move` | 44 | 44 | '0.8552002906799316' |
| `value_teacher_move` | 44 | 44 | '0.8552002906799316' |
| `teacher_value_disfavored` | 44 | 2 | 'False' |
| `teacher_top3_policy` | 44 | 2 | 'True' |
| `teacher_eval_current` | 32 | 19 | '84' |
| `teacher_bestline_current` | 32 | 30 | 'F5' |
| `rapfi_after_original_eval` | 42 | 30 | '-36' |
| `rapfi_after_original_move` | 44 | 37 | '4,4' |
| `rapfi_after_original_bestline` | 42 | 38 | 'E5' |
| `rapfi_after_teacher_eval` | 39 | 31 | '-36' |
| `rapfi_after_teacher_move` | 44 | 34 | '4,4' |
| `rapfi_after_teacher_bestline` | 39 | 33 | 'E5' |
| `strong_teacher_continuation_preference` | 44 | 2 | 'False' |
| `diverges` | 44 | 2 | 'False' |
| `logged_direct` | 44 | 28 | '7,7' |
| `logged_mcts_raw` | 44 | 36 | '7,7' |
| `logged_mcts_safety` | 44 | 38 | '7,7' |
| `logged_value` | 44 | 44 | '0.319652' |
| `loss_reason` | 44 | 2 | 'White win by five connection' |

## JSON structures

### `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json`

```json
{
  "kind": "json",
  "path": "analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json",
  "exists": true,
  "top_type": "list",
  "length": 25,
  "item_types": {
    "dict": 25
  },
  "first_keys": [
    "id",
    "source",
    "board_size",
    "win_length",
    "game_number",
    "move_count",
    "side_to_move",
    "board",
    "policy_target",
    "value_target",
    "label_type",
    "teacher_eval_before",
    "teacher_eval_kind",
    "teacher_pv_before",
    "current_best_direct_move",
    "numeric_gap_available",
    "numeric_gap_value",
    "suggested_bucket",
    "value_regression_candidate",
    "notes"
  ]
}
```

### `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json`

```json
{
  "kind": "json",
  "path": "analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json",
  "exists": true,
  "top_type": "dict",
  "top_keys": [
    "name",
    "description",
    "source_dataset",
    "samples",
    "skipped"
  ],
  "top_key_summaries": {
    "name": {
      "type": "str",
      "preview": "'rapfi_teacher_policy_margin_dataset_corpus8_selected'"
    },
    "description": {
      "type": "str",
      "preview": "'Pairwise policy-logit margin dataset: Rapfi teacher move should outrank current_best direct move.'"
    },
    "source_dataset": {
      "type": "str",
      "preview": "'analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json'"
    },
    "samples": {
      "type": "list",
      "length": 25,
      "first_keys": [
        "case_id",
        "source",
        "board_size",
        "win_length",
        "game_number",
        "move_count",
        "side_to_move",
        "current_player",
        "board",
        "target_xy",
        "target_rc",
        "suppress_xy",
        "suppress_rc",
        "teacher_move",
        "suppress_move",
        "old_final",
        "sample_weight",
        "label_type",
        "suggested_bucket",
        "teacher_eval_before",
        "teacher_eval_kind",
        "numeric_gap_available",
        "numeric_gap_value",
        "notes"
      ],
      "first_item_preview": {
        "case_id": "legacy_g1_m4",
        "source": "rapfi_teacher_policy_margin_dataset_corpus8_selected",
        "board_size": 15,
        "win_length": 5,
        "game_number": 1,
        "move_count": 4,
        "side_to_move": "black",
        "current_player": 1,
        "board": [
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            -1,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            -1,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
```

### `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`

```json
{
  "kind": "json",
  "path": "analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json",
  "exists": true,
  "top_type": "list",
  "length": 32,
  "item_types": {
    "dict": 32
  },
  "first_keys": [
    "game_number",
    "move_count",
    "side_to_move",
    "value",
    "direct",
    "policy_safety",
    "mcts_raw",
    "mcts_safety",
    "final",
    "previous_rapfi_bestline",
    "next_rapfi_bestline",
    "board_snapshot_before_decision",
    "board_snapshot_after_decision",
    "loss_reason",
    "failure_type",
    "notes"
  ]
}
```

### `analysis/integration_eval/candidate_g_teacher_seed_dataset.json`

```json
{
  "kind": "json",
  "path": "analysis/integration_eval/candidate_g_teacher_seed_dataset.json",
  "exists": true,
  "top_type": "dict",
  "top_keys": [
    "name",
    "purpose",
    "source_manifest",
    "source_debug_log",
    "notes",
    "summary",
    "missing",
    "side_mismatches",
    "rows"
  ],
  "top_key_summaries": {
    "name": {
      "type": "str",
      "preview": "'candidate_g_teacher_seed_dataset'"
    },
    "purpose": {
      "type": "str",
      "preview": "'board-state dry-run dataset for Candidate G teacher distillation; not trained yet'"
    },
    "source_manifest": {
      "type": "str",
      "preview": "'analysis/integration_eval/candidate_g_teacher_seed_manifest.json'"
    },
    "source_debug_log": {
      "type": "str",
      "preview": "'eval_logs/rapfi_smoke/candidate_d_move15_mcts32_debug_vs_rapfi_fast_g2.log'"
    },
    "notes": {
      "type": "list",
      "length": 5,
      "first_keys": [],
      "first_item_preview": "No training was run."
    },
    "summary": {
      "type": "dict",
      "keys": [
        "manifest_rows",
        "dataset_rows",
        "missing_replay_rows",
        "side_mismatches",
        "role_counts"
      ],
      "num_keys": 5
    },
    "missing": {
      "type": "list",
      "length": 0,
      "first_keys": [],
      "first_item_preview": null
    },
    "side_mismatches": {
      "type": "list",
      "length": 0,
      "first_keys": [],
      "first_item_preview": null
    },
    "rows": {
      "type": "list",
      "length": 14,
      "first_keys": [
        "id",
        "role",
        "reason",
        "weight",
        "game",
        "ply",
        "side_to_move",
        "manifest_side",
        "board_size",
        "board",
        "board_strings",
        "last_move_rc",
        "last_move_xy",
        "model_move",
        "teacher_move",
        "policy_target_move",
        "teacher_move_policy_rank",
        "model_move_policy_rank",
        "teacher_policy_prob",
        "model_policy_prob",
        "policy_probability_gap_teacher_minus_model",
        "policy_logit_gap_teacher_minus_model",
        "value_current_position",
        "value_original_move",
        "value_teacher_move",
        "teacher_value_disfavored",
        "teacher_top3_policy",
        "strong_teacher_continuation_preference",
        "diverges",
        "teacher_eval_current",
        "teacher_bestline_current",
        "rapfi_after_original_eval",
        "rapfi_after_original_move",
        "rapfi_after_original_bestline",
        "rapfi_after_teacher_eval",
        "rapfi_after_teacher_move",
        "rapfi_after_teacher_bestline",
        "stone_counts"
      ],
      "first_item_preview": {
        "id": "g1_p0_black",
        "role": "general_teacher_aligned_anchor",
        "reason": "teacher-aligned top-3 policy retention anchor",
        "weight": 0.75,
        "game": 1,
        "ply": 0,
        "side_to_move": "black",
        "manifest_side": "black",
        "board_size": 15,
        "board": [
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
```

### `analysis/integration_eval/candidate_g_teacher_seed_manifest.json`

```json
{
  "kind": "json",
  "path": "analysis/integration_eval/candidate_g_teacher_seed_manifest.json",
  "exists": true,
  "top_type": "dict",
  "top_keys": [
    "name",
    "source_csv",
    "purpose",
    "notes",
    "selection_counts",
    "rows"
  ],
  "top_key_summaries": {
    "name": {
      "type": "str",
      "preview": "'candidate_g_teacher_seed_manifest'"
    },
    "source_csv": {
      "type": "str",
      "preview": "'analysis/integration_eval/candidate_d_teacher_disagreement_census.csv'"
    },
    "purpose": {
      "type": "str",
      "preview": "'dry-run selection manifest for Candidate G teacher distillation; not a trainable tensor dataset'"
    },
    "notes": {
      "type": "list",
      "length": 3,
      "first_keys": [],
      "first_item_preview": "No training was run."
    },
    "selection_counts": {
      "type": "dict",
      "keys": [
        "total_selected",
        "seed_teacher_divergence",
        "retention_anchor",
        "nearby_nondivergent_anchor",
        "general_teacher_aligned_anchor"
      ],
      "num_keys": 5
    },
    "rows": {
      "type": "list",
      "length": 14,
      "first_keys": [
        "id",
        "role",
        "reason",
        "weight",
        "game",
        "ply",
        "side",
        "model_move",
        "teacher_move",
        "teacher_move_policy_rank",
        "model_move_policy_rank",
        "teacher_policy_prob",
        "model_policy_prob",
        "policy_probability_gap_teacher_minus_model",
        "policy_logit_gap_teacher_minus_model",
        "value_current_position",
        "value_original_move",
        "value_teacher_move",
        "teacher_value_disfavored",
        "teacher_top3_policy",
        "teacher_eval_current",
        "teacher_bestline_current",
        "rapfi_after_original_eval",
        "rapfi_after_original_move",
        "rapfi_after_original_bestline",
        "rapfi_after_teacher_eval",
        "rapfi_after_teacher_move",
        "rapfi_after_teacher_bestline",
        "strong_teacher_continuation_preference",
        "diverges",
        "logged_direct",
        "logged_mcts_raw",
        "logged_mcts_safety",
        "logged_value",
        "loss_reason"
      ],
      "first_item_preview": {
        "id": "g1_p0_black",
        "role": "general_teacher_aligned_anchor",
        "reason": "teacher-aligned top-3 policy retention anchor",
        "weight": 0.75,
        "game": 1,
        "ply": 0,
        "side": "black",
        "model_move": "7,7",
        "teacher_move": "7,7",
        "teacher_move_policy_rank": 1,
        "model_move_policy_rank": 1,
        "teacher_policy_prob": 0.9767210483551025,
        "model_policy_prob": 0.9767210483551025,
        "policy_probability_gap_teacher_minus_model": 0.0,
        "policy_logit_gap_teacher_minus_model": 0.0,
        "value_current_position": 0.3196517527103424,
        "value_original_move": 0.8552002906799316,
        "value_teacher_move": 0.8552002906799316,
        "teacher_value_disfavored": false,
        "teacher_top3_policy": true,
        "teacher_eval_current": "",
        "teacher_bestline_current": "",
        "rapfi_after_original_eval": "-36",
        "rapfi_after_original_move": "4,4",
        "rapfi_after_original_bestline": "E5",
        "rapfi_after_teacher_eval": "-36",
        "rapfi_after_teacher_move": "4,4",
        "rapfi_after_teacher_bestline": "E5",
        "strong_teacher_continuation_preference": false,
        "diverges": false,
        "logged_direct": "7,7",
        "logged_mcts_raw": "7,7",
        "logged_mcts_safety": "7,7",
        "logged_value": 0.319652,
        "loss_reason": "White win by five connection"
      }
    }
  }
}
```

### `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json`

```json
{
  "kind": "json",
  "path": "analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json",
  "exists": true,
  "top_type": "list",
  "length": 5,
  "item_types": {
    "dict": 5
  },
  "first_keys": [
    "case_id",
    "source",
    "reason",
    "game_number",
    "move_count",
    "board_size",
    "win_length",
    "side_to_move",
    "current_player",
    "target_xy",
    "target_rc",
    "suppress_xy",
    "suppress_rc",
    "old_final_xy",
    "old_final",
    "board",
    "board_snapshot_before_decision"
  ]
}
```

### `analysis/integration_eval/current_best_margin_candidate_c_anchors.json`

```json
{
  "kind": "json",
  "path": "analysis/integration_eval/current_best_margin_candidate_c_anchors.json",
  "exists": true,
  "top_type": "list",
  "length": 7,
  "item_types": {
    "dict": 7
  },
  "first_keys": [
    "case_id",
    "source",
    "reason",
    "game_number",
    "move_count",
    "board_size",
    "win_length",
    "side_to_move",
    "current_player",
    "target_xy",
    "target_rc",
    "suppress_xy",
    "suppress_rc",
    "old_final_xy",
    "old_final",
    "board",
    "board_snapshot_before_decision"
  ]
}
```

### `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json`

```json
{
  "kind": "json",
  "path": "analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json",
  "exists": true,
  "top_type": "list",
  "length": 8,
  "item_types": {
    "dict": 8
  },
  "first_keys": [
    "case_id",
    "source",
    "reason",
    "game_number",
    "move_count",
    "board_size",
    "win_length",
    "side_to_move",
    "current_player",
    "target_xy",
    "target_rc",
    "suppress_xy",
    "suppress_rc",
    "old_final_xy",
    "old_final",
    "direct",
    "policy_safety",
    "mcts_raw",
    "mcts_safety",
    "value",
    "board",
    "board_snapshot_before_decision",
    "last_move_xy",
    "last_move_rc"
  ]
}
```

### `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json`

```json
{
  "kind": "json",
  "path": "analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json",
  "exists": true,
  "top_type": "list",
  "length": 3,
  "item_types": {
    "dict": 3
  },
  "first_keys": [
    "case_id",
    "source",
    "reason",
    "game_number",
    "move_count",
    "board_size",
    "win_length",
    "side_to_move",
    "current_player",
    "last_move_xy",
    "last_move_rc",
    "target_xy",
    "target_rc",
    "suppress_xy",
    "suppress_rc",
    "old_final_xy",
    "old_final",
    "direct",
    "policy_safety",
    "mcts_raw",
    "mcts_safety",
    "value",
    "board",
    "board_snapshot_before_decision"
  ]
}
```

### `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json`

```json
{
  "kind": "json",
  "path": "analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json",
  "exists": true,
  "top_type": "list",
  "length": 1,
  "item_types": {
    "dict": 1
  },
  "first_keys": [
    "case_id",
    "source",
    "reason",
    "game_number",
    "move_count",
    "board_size",
    "win_length",
    "side_to_move",
    "current_player",
    "last_move_xy",
    "last_move_rc",
    "target_xy",
    "target_rc",
    "suppress_xy",
    "suppress_rc",
    "old_final_xy",
    "old_final",
    "direct",
    "policy_safety",
    "mcts_raw",
    "mcts_safety",
    "value",
    "board",
    "board_snapshot_before_decision"
  ]
}
```

### `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json`

```json
{
  "kind": "json",
  "path": "analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json",
  "exists": true,
  "top_type": "list",
  "length": 3,
  "item_types": {
    "dict": 3
  },
  "first_keys": [
    "case_id",
    "source",
    "reason",
    "game_number",
    "move_count",
    "board_size",
    "win_length",
    "side_to_move",
    "current_player",
    "last_move_xy",
    "last_move_rc",
    "target_xy",
    "target_rc",
    "suppress_xy",
    "suppress_rc",
    "old_final_xy",
    "old_final",
    "direct",
    "policy_safety",
    "mcts_raw",
    "mcts_safety",
    "value",
    "board",
    "board_snapshot_before_decision"
  ]
}
```
