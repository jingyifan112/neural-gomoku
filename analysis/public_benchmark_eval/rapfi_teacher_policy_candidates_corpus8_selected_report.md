# Rapfi Teacher Policy Candidate Rows: corpus8 selected

## Purpose

This file filters the Rapfi teacher score-gap benchmark into auditable candidate supervision rows.
No training or promotion is performed here.

## Source files

- `current_best`: `analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv`
- `candidate_g`: `analysis/public_benchmark_eval/rapfi_teacher_scoregap_candidate_g_corpus8_selected.csv`
- `candidate_h`: `analysis/public_benchmark_eval/rapfi_teacher_scoregap_candidate_h_corpus8_selected.csv`

## Summary

- total_rows: 32
- concrete_teacher_rows: 32
- stable_teacher_move_rows: 32
- policy_candidates: 32
- priority_candidates_current_best_mismatch: 25
- numeric_gap_candidates: 15
- priority_numeric_gap_candidates: 12
- priority_gap_unavailable_candidates: 13
- low_priority_already_matched_rows: 7
- mate_eval_rows: 8
- numeric_eval_rows: 16
- NA_eval_rows: 8
- other_eval_rows: 0

## Suggested bucket counts

| bucket | count |
|---|---:|
| priority_policy_gap_unavailable | 13 |
| priority_policy_numeric_gap | 12 |
| low_priority_policy_already_matched | 7 |

## Conservative usage recommendation

- Use `policy_candidate=true` rows only as teacher-policy candidates.
- Prioritize `priority_candidate=true` rows where current_best does not match Rapfi's re-query best move.
- Use `numeric_gap_candidate=true` only for weighting/ranking experiments, not direct value regression.
- Keep mate, NA, and other gap-unavailable rows as policy supervision candidates only; do not coerce them into numeric value targets.
- `value_regression_candidate` is intentionally false for all rows in this pass.

## Priority numeric-gap rows

| sample_id | side | teacher | current_best | gap | eval | eval_kind | failure_type |
|---|---|---|---|---:|---|---|---|
| legacy_g6_m5 | white | 6,8 | 8,8 | 801.0 | 440 | numeric | first_losing_value |
| legacy_g5_m14 | black | 7,9 | 6,6 | 666.0 | 410 | numeric | first_losing_value |
| legacy_g2_m5 | white | 8,6 | 7,8 | 558.0 | 440 | numeric | neighbor |
| legacy_g1_m4 | black | 7,5 | 7,6 | 551.0 | 120 | numeric | neighbor |
| legacy_g1_m6 | black | 7,8 | 6,6 | 446.0 | 87 | numeric | first_direct_vs_mcts_divergence |
| legacy_g1_m8 | black | 8,5 | 6,6 | 338.0 | 319 | numeric | neighbor |
| legacy_g2_m9 | white | 10,5 | 9,5 | 275.0 | 63 | numeric | first_losing_value;neighbor |
| legacy_g5_m12 | black | 8,9 | 6,6 | 216.0 | 198 | numeric | neighbor |
| legacy_g3_m4 | black | 5,6 | 8,8 | 158.0 | 134 | numeric | neighbor |
| legacy_g2_m11 | white | 9,7 | 6,5 | 100.0 | -92 | numeric | neighbor |
| legacy_g4_m13 | white | 9,6 | 6,4 | 75.0 | -42 | numeric | neighbor |
| legacy_g5_m6 | black | 8,6 | 9,8 | 11.0 | 1 | numeric | neighbor |

## Priority rows with unavailable numeric gap

| sample_id | side | teacher | current_best | eval | eval_kind | failure_type |
|---|---|---|---|---|---|---|
| legacy_g1_m40 | black | 12,6 | 5,8 | NA | NA | late_loss_window |
| legacy_g2_m7 | white | 5,6 | 6,5 | +M3 | mate | first_direct_vs_mcts_divergence;neighbor |
| legacy_g2_m21 | white | 7,9 | 2,4 | -M2 | mate | late_loss_window |
| legacy_g3_m24 | black | 3,7 | 7,6 | -M4 | mate | late_loss_window |
| legacy_g3_m26 | black | 6,3 | 7,6 | -M2 | mate | late_loss_window |
| legacy_g4_m17 | white | 10,6 | 9,9 | 353 | numeric | neighbor |
| legacy_g4_m23 | white | 7,9 | 7,3 | NA | NA | late_loss_window |
| legacy_g5_m8 | black | 8,5 | 6,6 | +M3 | mate | first_direct_vs_mcts_divergence |
| legacy_g5_m16 | black | 7,5 | 11,8 | +M3 | mate | neighbor |
| legacy_g5_m28 | black | 5,11 | 5,4 | NA | NA | late_loss_window |
| legacy_g5_m30 | black | 4,9 | 7,3 | NA | NA | late_loss_window |
| legacy_g6_m17 | white | 8,6 | 4,9 | +M3 | mate | first_direct_vs_mcts_divergence;late_loss_window |
| legacy_g6_m19 | white | 9,5 | 7,9 | NA | NA | neighbor;late_loss_window |

Candidate CSV: `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv`

