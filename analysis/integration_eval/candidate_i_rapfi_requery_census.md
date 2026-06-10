# Candidate I Rapfi re-query census

## Scope

- reconstructed positions: Candidate H mcts16 smoke losses from `eval_logs/integration_eval/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.engine_io.log`
- Rapfi re-query attempt plan: `2:10000,1:5000,2:5000`
- Candidate H C weights: `weights/15x15_candidate_h_value_ranking_weights.bin`
- measurement only; no training was run.
- Rapfi is queried per position in a fresh process. Persistent-process reuse was not used because the retry path needs clean per-board state and isolated stdout/stderr diagnostics; the failures are no-move replies after evaluation, not process startup failures.

## Summary

- total positions attempted: 25
- Rapfi returned concrete move: 11
- Rapfi timeout / no-move / NA: 14 (14 timeout, 0 no-move/NA)
- recovered concrete labels by retry/fallback: 0
- usable teacher labels: 11
- valid teacher disagreements with Candidate H: 1
- valid teacher agreements with low policy visibility: 1
- usable Rapfi moves with Candidate H policy rank > 10: 2
- Rapfi child-value higher than Candidate H move: 0
- safety failures in either Candidate H or Rapfi move: 0
- boards terminal before query: 0

## Priority Rows

| game | ply | priority | H move | Rapfi re-query | agree | rank | policy gap | value gap | safety H/R | Rapfi score | PV | classification |
|---:|---:|---|---:|---:|---|---:|---:|---:|---|---:|---|---|
| 1 | 14 | late_loss_window | 8,5 | NA | False | NA | NA | NA | True/NA | +M3 | NA | context |
| 1 | 16 | late_loss_window | 4,5 | 4,5 | True | 1 | 0.000000 | 0.000000 | True/True | NA | NA | matches_rapfi_teacher |
| 1 | 18 | game1_ply18_low_policy_prior;late_loss_window;low_policy_in_shallow_census | 5,2 | 5,2 | True | 37 | 0.000000 | 0.000000 | True/True | NA | NA | matches_rapfi_teacher;teacher_low_policy_visibility |
| 1 | 20 | late_loss_window | 7,1 | 7,1 | True | 1 | 0.000000 | 0.000000 | True/True | NA | NA | matches_rapfi_teacher |
| 2 | 13 | game2_focus_before_old_targets | 2,6 | 2,6 | True | 1 | 0.000000 | 0.000000 | True/True | NA | NA | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 15 | game2_focus_before_old_targets | 2,8 | 2,8 | True | 5 | 0.000000 | 0.000000 | True/True | NA | NA | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 17 | game2_focus_before_old_targets;late_loss_window | 4,10 | 4,10 | True | 4 | 0.000000 | 0.000000 | True/True | NA | NA | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 19 | late_loss_window | 3,10 | 3,10 | True | 1 | 0.000000 | 0.000000 | True/True | NA | NA | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 21 | late_loss_window | 3,5 | 3,5 | True | 1 | 0.000000 | 0.000000 | True/True | NA | NA | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 23 | late_loss_window | 2,5 | NA | False | NA | NA | NA | True/NA | +M3 | NA | already_losing_value |
| 2 | 25 | late_loss_window | 7,10 | 7,10 | True | 1 | 0.000000 | 0.000000 | True/True | NA | NA | matches_rapfi_teacher;opponent_forcing_reply_exists_before_move |
| 2 | 27 | late_loss_window | 7,9 | 2,9 | False | 146 | -0.457829 | -0.100804 | True/True | NA | NA | diverges_from_rapfi_teacher;value_supports_candidate;teacher_low_policy_visibility;opponent_forcing_reply_exists_before_move |

## Usable Teacher Labels

| game | ply | H move | Rapfi re-query | agree | rank | policy gap | value gap | safety H/R | classification |
|---:|---:|---:|---:|---|---:|---:|---:|---|---|
| 1 | 0 | 7,7 | 7,7 | True | 1 | 0.000000 | 0.000000 | True/True | matches_rapfi_teacher |
| 1 | 16 | 4,5 | 4,5 | True | 1 | 0.000000 | 0.000000 | True/True | matches_rapfi_teacher |
| 1 | 18 | 5,2 | 5,2 | True | 37 | 0.000000 | 0.000000 | True/True | matches_rapfi_teacher;teacher_low_policy_visibility |
| 1 | 20 | 7,1 | 7,1 | True | 1 | 0.000000 | 0.000000 | True/True | matches_rapfi_teacher |
| 2 | 13 | 2,6 | 2,6 | True | 1 | 0.000000 | 0.000000 | True/True | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 15 | 2,8 | 2,8 | True | 5 | 0.000000 | 0.000000 | True/True | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 17 | 4,10 | 4,10 | True | 4 | 0.000000 | 0.000000 | True/True | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 19 | 3,10 | 3,10 | True | 1 | 0.000000 | 0.000000 | True/True | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 21 | 3,5 | 3,5 | True | 1 | 0.000000 | 0.000000 | True/True | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 25 | 7,10 | 7,10 | True | 1 | 0.000000 | 0.000000 | True/True | matches_rapfi_teacher;opponent_forcing_reply_exists_before_move |
| 2 | 27 | 7,9 | 2,9 | False | 146 | -0.457829 | -0.100804 | True/True | diverges_from_rapfi_teacher;value_supports_candidate;teacher_low_policy_visibility;opponent_forcing_reply_exists_before_move |

## Valid Teacher Disagreements

| game | ply | H move | Rapfi re-query | rank | policy gap | value gap | score | PV |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 27 | 7,9 | 2,9 | 146 | -0.457829 | -0.100804 | NA | NA |

## Low Policy Visibility Agreements

| game | ply | H/Rapfi move | rank | policy prob | root value | child value | classification |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 18 | 5,2 | 37 | 0.000593 | -0.227468 | 0.801930 | matches_rapfi_teacher;teacher_low_policy_visibility |

## NA Diagnostics

| game | ply | H move | status | diagnosis | attempts | elapsed ms | terminal | legal moves | score | PV | stdout | stderr |
|---:|---:|---:|---|---|---:|---:|---|---:|---:|---|---|---|
| 1 | 2 | 4,6 | timeout_no_move | score_or_pv_without_move | 3 | 5061 | False | 223 | 89 | NA | OK || MESSAGE Speed 62000 | Depth 2-3 | Eval 89 | Node 62 | Time 0ms | NA |
| 1 | 4 | 6,4 | timeout_no_move | score_or_pv_without_move | 3 | 5064 | False | 221 | 189 | NA | OK || MESSAGE Speed 116K | Depth 2-5 | Eval 189 | Node 116 | Time 1ms | NA |
| 1 | 6 | 6,6 | timeout_no_move | score_or_pv_without_move | 3 | 5061 | False | 219 | 278 | NA | OK || MESSAGE Speed 100K | Depth 2-5 | Eval 278 | Node 100 | Time 1ms | NA |
| 1 | 8 | 5,7 | timeout_no_move | score_or_pv_without_move | 3 | 5064 | False | 217 | +M3 | NA | OK || MESSAGE Speed 2000 | Depth 2-2 | Eval +M3 | Node 2 | Time 0ms | NA |
| 1 | 10 | 6,7 | timeout_no_move | score_or_pv_without_move | 3 | 5064 | False | 215 | +M7 | NA | OK || MESSAGE Speed 267K | Depth 2-3 | Eval +M7 | Node 267 | Time 1ms | NA |
| 1 | 12 | 3,8 | timeout_no_move | score_or_pv_without_move | 3 | 5063 | False | 213 | +M3 | NA | OK || MESSAGE Speed 2000 | Depth 2-2 | Eval +M3 | Node 2 | Time 0ms | NA |
| 1 | 14 | 8,5 | timeout_no_move | score_or_pv_without_move | 3 | 5060 | False | 211 | +M3 | NA | OK || MESSAGE Speed 2000 | Depth 2-2 | Eval +M3 | Node 2 | Time 0ms | NA |
| 2 | 1 | 7,6 | timeout_no_move | score_or_pv_without_move | 3 | 5064 | False | 224 | -16 | NA | OK || MESSAGE Speed 26000 | Depth 2-3 | Eval -16 | Node 26 | Time 0ms | NA |
| 2 | 3 | 6,7 | timeout_no_move | score_or_pv_without_move | 3 | 5059 | False | 222 | -77 | NA | OK || MESSAGE Speed 70000 | Depth 2-3 | Eval -77 | Node 70 | Time 0ms | NA |
| 2 | 5 | 8,6 | timeout_no_move | score_or_pv_without_move | 3 | 5061 | False | 220 | 80 | NA | OK || MESSAGE Speed 6000 | Depth 2-4 | Eval 80 | Node 6 | Time 0ms | NA |
| 2 | 7 | 5,7 | timeout_no_move | score_or_pv_without_move | 3 | 5064 | False | 218 | -105 | NA | OK || MESSAGE Speed 98000 | Depth 2-3 | Eval -105 | Node 98 | Time 1ms | NA |
| 2 | 9 | 7,8 | timeout_no_move | score_or_pv_without_move | 3 | 5064 | False | 216 | -155 | NA | OK || MESSAGE Speed 10000 | Depth 2-6 | Eval -155 | Node 10 | Time 0ms | NA |
| 2 | 11 | 7,11 | timeout_no_move | score_or_pv_without_move | 3 | 5064 | False | 214 | -102 | NA | OK || MESSAGE Speed 10000 | Depth 2-6 | Eval -102 | Node 10 | Time 0ms | NA |
| 2 | 23 | 2,5 | timeout_no_move | score_or_pv_without_move | 3 | 5058 | False | 202 | +M3 | NA | OK || MESSAGE Speed 2000 | Depth 2-2 | Eval +M3 | Node 2 | Time 0ms | NA |

## Diagnosis

- Protocol color encoding is relative to the queried engine side, matching the smoke engine log where opponent stones are sent as `2`.
- Stderr is empty for the NA rows, so there is no evidence of a Rapfi crash or command-line failure.
- The depth-1 fallback also returns eval-only output on the unrecovered rows, so the remaining failures are not fixed by shorter depth or a longer per-turn wait.
- The NA rows are not caused by terminal reconstructed boards in this run.
- Remaining NA rows produced Rapfi eval output but no final coordinate before the retry deadline, so they are treated as no-move teacher failures rather than disagreements. This suggests Rapfi's `BOARD` response path for these arbitrary reconstructed positions is the limiting factor, not Candidate H safety or board reconstruction.

## Interpretation

- Direct re-query is stronger than the smoke log continuation and avoids treating stale PV tails as labels.
- Rows where Rapfi returns `NA` or no move are not usable teacher disagreements.
- Rows where Rapfi disagrees with Candidate H and has low Candidate H policy rank are teacher-policy candidates only after concrete-move and safety validation.
- Rows where Rapfi agrees but the move has low rank are policy-visibility anchors rather than disagreement pairs.
- Rows with positive child-value gap are potential value-ranking candidates, but only if the Rapfi PV remains stable under follow-up validation.

## Recommendation

Do not train Candidate J from this dataset. Retry/fallback did not recover enough concrete labels, and the validated disagreement set remains a single-row signal. NA/no-move rows remain excluded from training labels.

Do not train from this census until the selected teacher labels are reviewed.
